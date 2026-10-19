"""Offline proactive delivery, consent, timing, races, limits and lifecycle."""

from datetime import UTC, datetime

import pytest

from eidolon.config import Settings
from eidolon.proactive import DEFAULTS, quiet
from eidolon.llm import LLMError
from eidolon.reply_format import Segment
from tests.conftest import ClientFactory
from tests.fakes import FakeClock, FakeLLM, build_faked


@pytest.fixture
async def rig(settings: Settings):
    clock = FakeClock(datetime(2026, 10, 20, 3, tzinfo=UTC))
    llm = FakeLLM(*[["<ja>また話そう。</ja><zh>再聊聊吧。</zh>"] for _ in range(3)])
    backend = build_faked(settings, llm, clock=clock)
    user = backend.store.create_user("proactive-user")
    backend.store.consent(user.id, clock())
    convo = backend.store.create_conversation(user.id, "mano")
    yield backend, user, convo, clock, llm
    await backend.aclose()


def enabled(**changes):
    return dict(
        DEFAULTS, enabled=True, characters=["mano"], interval_hours=2, **changes
    )


async def test_opt_in_then_real_character_message_no_fake_user_and_no_followup_until_reply(
    rig,
):
    b, u, c, clock, llm = rig
    await b.proactive.tick()
    assert not llm.prompts
    b.proactive.save(u.id, enabled())
    await b.proactive.tick()
    assert not llm.prompts
    clock.advance(hours=2)
    await b.proactive.tick()
    record = b.store.record(c.id)
    assert len(record) == 1 and record[0].role == "character"
    assert b.proactive.unread(u.id) == {"mano": 1}
    b.proactive.seen(u.id, c.id)
    assert not b.proactive.unread(u.id)
    clock.advance(hours=2)
    await b.proactive.tick()
    assert len(llm.prompts) == 1
    b.store.add_turn(
        c.id, "你好", [Segment("はい", "好的")], said_at=clock().isoformat()
    )
    clock.advance(minutes=16)
    await b.proactive.tick()
    assert len(llm.prompts) == 2


async def test_quiet_hours_and_busy_calls_do_not_spend_attempts(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    clock.now = datetime(2026, 10, 20, 15, tzinfo=UTC)  # midnight Tokyo
    await b.proactive.tick()
    assert not llm.prompts
    clock.now = datetime(2026, 10, 21, 0, tzinfo=UTC)
    b.proactive.busy = lambda _: True
    await b.proactive.tick()
    assert not llm.prompts
    b.proactive.busy = lambda _: False
    await b.proactive.tick()
    assert len(llm.prompts) == 1


async def test_daily_attempt_cap_counts_failures_and_is_durable(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled(daily_limit=1))
    llm._replies = [LLMError("private content must not be logged")]
    clock.advance(hours=2)
    await b.proactive.tick()
    clock.advance(hours=3)
    await b.proactive.tick()
    assert len(llm.prompts) == 1
    assert (
        b.proactive.db.execute("SELECT COUNT(*) FROM proactive_attempts").fetchone()[0]
        == 1
    )


async def test_concurrent_claims_only_one_and_setting_change_discards_output(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    clock.advance(hours=2)
    claim = b.proactive._claim(u.id)
    assert claim is not None
    assert b.proactive._claim(u.id) is None
    attempt, convo, last, config, version = claim
    b.proactive.save(u.id, dict(config, enabled=False))
    assert not b.proactive._deliver(
        attempt, convo, last, version, [Segment("はい", "好的")]
    )
    assert not b.store.record(c.id)


async def test_new_user_turn_or_new_conversation_discards_stale_generation(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    clock.advance(hours=2)
    claim = b.proactive._claim(u.id)
    assert claim
    b.store.add_turn(
        c.id, "刚说的话", [Segment("はい", "好的")], said_at=clock().isoformat()
    )
    assert not b.proactive._deliver(
        claim[0], c, claim[2], claim[4], [Segment("old", "旧的")]
    )
    clock.advance(hours=2)
    claim = b.proactive._claim(u.id)
    assert claim
    b.store.create_conversation(u.id, "mano")
    assert not b.proactive._deliver(
        claim[0], c, claim[2], claim[4], [Segment("old", "旧的")]
    )


async def test_stops_for_banned_or_unconsented_user_and_delete_cleans_settings(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    with b.proactive.db:
        b.proactive.db.execute("UPDATE users SET consented_at=NULL WHERE id=?", (u.id,))
    clock.advance(hours=2)
    await b.proactive.tick()
    assert not llm.prompts
    b.store.consent(u.id, clock())
    await b.proactive.tick()
    b.store.delete_user(u.id)
    assert (
        b.proactive.db.execute("SELECT COUNT(*) FROM proactive_attempts").fetchone()[0]
        == 0
    )
    assert b.proactive.settings(u.id)["enabled"] is False


async def test_http_owner_isolation_validation_and_default_off(
    make_client: ClientFactory,
):
    client = make_client(FakeLLM())
    assert (await client.get("/api/proactive")).json()["enabled"] is False
    assert (await client.put("/api/proactive", json=enabled())).status_code == 200
    other = make_client(FakeLLM(), "other")
    assert (await other.get("/api/proactive")).json()["enabled"] is False
    for changes in (
        {"characters": []},
        {"characters": ["unknown"]},
        {"quiet_start": "24:00"},
        {"timezone": "bad/zone"},
        {"interval_hours": 0},
        {"daily_limit": 100},
    ):
        assert (
            await client.put("/api/proactive", json=dict(enabled(), **changes))
        ).status_code == 422


def test_quiet_interval_wrap_and_equal_means_no_quiet():
    now = datetime(2026, 10, 20, 15, tzinfo=UTC)
    assert quiet(DEFAULTS, now)
    assert not quiet(dict(DEFAULTS, quiet_start="00:00", quiet_end="00:00"), now)


async def test_first_user_reply_sees_the_unsolicited_message(rig):
    from eidolon.llm import TurnLLMs

    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    clock.advance(hours=2)
    await b.proactive.tick()
    events = [event async for event in b.engine.turn(c, "うん", TurnLLMs(llm, llm))]
    assert events
    assert any(
        m.role == "assistant" and "また話そう" in m.content for m in llm.prompts[-1]
    )


async def test_text_turn_busy_hold_prevents_claim_and_is_released_idempotently(rig):
    b, u, c, clock, llm = rig
    b.proactive.save(u.id, enabled())
    clock.advance(hours=2)
    release = b.proactive.hold(u.id)
    await b.proactive.tick()
    assert not llm.prompts
    release()
    release()
    await b.proactive.tick()
    assert len(llm.prompts) == 1
