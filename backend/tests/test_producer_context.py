"""Imported producer context persists per user and is injected without retrieval."""

import sqlite3
from pathlib import Path

from eidolon.config import Settings
from eidolon.producer import ProducerProfile
from eidolon.store import Store
from tests.conftest import ClientFactory
from tests.fakes import FakeLLM, system_of
from tests.test_text_turn import send_turn, start_conversation


def test_context_is_scoped_to_user_and_character_and_survives_profile_edits(tmp_path: Path):
    path = tmp_path / "context.db"
    store = Store(path)
    owner = store.create_user("owner")
    other = store.create_user("other")
    store.save_profile(owner.id, ProducerProfile(timezone="Asia/Tokyo"))
    store.save_producer_context(owner.id, "shared fact", {"mano": "specific guidance"})
    assert store.get_profile(owner.id).timezone == "Asia/Tokyo"
    assert store.producer_context(owner.id, "mano") == "shared fact\n\nspecific guidance"
    assert store.producer_context(owner.id, "kogane") == "shared fact"
    assert store.producer_context(other.id, "mano") == ""
    store.save_profile(owner.id, ProducerProfile(gender="male"))
    store.close()
    store = Store(path)
    assert "specific guidance" in store.producer_context(owner.id, "mano")
    store.delete_user(owner.id)
    assert store.producer_context(owner.id, "mano") == ""
    store.close()


def test_existing_profile_migrates_without_losing_fields(tmp_path: Path):
    path = tmp_path / "old.db"
    store = Store(path)
    owner = store.create_user("owner")
    store.save_profile(owner.id, ProducerProfile(gender="male", timezone="Asia/Tokyo"))
    store.close()
    with sqlite3.connect(path) as db:
        db.execute("ALTER TABLE producer_profiles DROP COLUMN context")
    store = Store(path)
    assert store.producer_context(owner.id, "mano") == ""
    assert store.get_profile(owner.id).timezone == "Asia/Tokyo"
    store.close()


async def test_context_enters_every_characters_prompt_only_for_its_owner(
    make_client: ClientFactory, settings: Settings,
):
    llm = FakeLLM(["<ja>はい</ja><zh>好的</zh>"])
    client = make_client(llm)
    store = Store(settings.database_path)
    owner = store.first_user_named("producer")
    assert owner is not None
    store.save_producer_context(owner.id, "shared marker", {"mano": "mano marker"})
    for character in ("mano", "kogane"):
        conversation = await start_conversation(client, character)
        await send_turn(client, conversation, "你好")
        prompt = system_of(llm.prompts[-1])
        assert "shared marker" in prompt
        assert ("mano marker" in prompt) == (character == "mano")
    other_llm = FakeLLM(["<ja>はい</ja><zh>好的</zh>"])
    other = make_client(other_llm, "other")
    conversation = await start_conversation(other)
    await send_turn(other, conversation, "你好")
    assert "shared marker" not in system_of(other_llm.prompts[-1])
    store.close()
