"""Opt-in, bounded station-only messages. Attempts persist, including failures.

No fake user turns: a delivery is one ordinary character message. Reading it marks it
seen; only a later user message permits that character to initiate again.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import uuid
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from eidolon.characters import Character
from eidolon.clock import Clock
from eidolon.database import connect
from eidolon.llm import ChatMessage
from eidolon.own_keys import Deployer
from eidolon.producer import now_prompt, producer_prompt
from eidolon.reply_format import ReplyParser, Segment, format_instructions, format_reply
from eidolon.store import Conversation, Message, Store

log = logging.getLogger(__name__)
_SCHEMA = """
CREATE TABLE IF NOT EXISTS proactive_settings (
 user_id TEXT PRIMARY KEY REFERENCES users(id), value TEXT NOT NULL,
 version TEXT NOT NULL, next_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS proactive_attempts (
 id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), character_id TEXT NOT NULL,
 conversation_id TEXT REFERENCES conversations(id) ON DELETE SET NULL,
 version TEXT NOT NULL, day TEXT NOT NULL, created_at TEXT NOT NULL,
 message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
 seen INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS proactive_by_user ON proactive_attempts(user_id, created_at);
"""
DEFAULTS = dict(
    enabled=False,
    characters=[],
    interval_hours=6,
    daily_limit=2,
    quiet_start="23:00",
    quiet_end="08:00",
    timezone="Asia/Tokyo",
)
_INSTRUCTIONS = """# 这次由你主动发一条站内消息
制作人已允许你主动联系，现在没有新的用户发言。按自己的性格发一两句自然日语并附中文字幕。
可以接上有依据的旧话题、轻轻问后续、提出一个小话题或邀请练日语；选择一种就好。
不要虚构制作人说过的话、承诺、今天的行踪或尚未发生的共同经历，也不假装知道外界实时信息。
没有新的日语输入，不做纠错。不要追问为什么不回、催睡、卖惨、索取承诺或连续催促。
不要假定恋人关系，不把普通主动联系自动变成调情。保持原人设年龄和相处边界。
不要编造具体新工作、重大事件或照片，不输出工具调用。信息不足可以聊自己的已有兴趣或提出邀请。
"""


def quiet(settings: dict, now: datetime) -> bool:
    local = now.astimezone(ZoneInfo(settings["timezone"]))
    value = local.strftime("%H:%M")
    start, end = settings["quiet_start"], settings["quiet_end"]
    if start == end:
        return False
    return start <= value < end if start < end else value >= start or value < end


class Proactive:
    def __init__(
        self,
        store: Store,
        characters: dict[str, Character],
        deployer: Deployer,
        clock: Clock,
        cooling: Callable[[str, str], datetime | None],
        busy: Callable[[str], bool] = lambda _: False,
    ):
        self.store, self.characters, self.deployer = store, characters, deployer
        self.clock, self.cooling, self.busy = clock, cooling, busy
        # Same database as the store, independent connection and transactions.
        self.db = connect(store.path)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self.active: dict[str, int] = {}
        with self.db:
            self.db.executescript(_SCHEMA)
        self.task: asyncio.Task | None = None

    def is_busy(self, user: str) -> bool:
        return bool(self.active.get(user)) or self.busy(user)

    def hold(self, user: str) -> Callable[[], None]:
        """Suppress proactive delivery for the lifetime of a user-initiated text turn."""
        released = False
        with self.lock:
            self.active[user] = self.active.get(user, 0) + 1

        def release() -> None:
            nonlocal released
            with self.lock:
                if not released:
                    released = True
                    self.active[user] -= 1
                    if not self.active[user]:
                        del self.active[user]

        return release

    def settings(self, user: str) -> dict:
        with self.lock:
            row = self.db.execute(
                "SELECT value FROM proactive_settings WHERE user_id=?", (user,)
            ).fetchone()
        return json.loads(row[0]) if row else dict(DEFAULTS, characters=[])

    def save(self, user: str, settings: dict) -> dict:
        # Validation is also enforced here for callers outside HTTP.
        if type(settings.get("enabled")) is not bool:
            raise ValueError("开关无效")
        chars = settings.get("characters")
        if not isinstance(chars, list) or any(
            not isinstance(c, str) or c not in self.characters for c in chars
        ):
            raise ValueError("请选择有效角色")
        if len(chars) != len(set(chars)) or len(chars) > len(self.characters):
            raise ValueError("角色不能重复")
        if settings["enabled"] and not chars:
            raise ValueError("开启前请至少选择一位角色")
        for key, lo, hi in (("interval_hours", 2, 72), ("daily_limit", 1, 5)):
            if type(settings.get(key)) is not int or not lo <= settings[key] <= hi:
                raise ValueError(f"{key} 需要在 {lo} 到 {hi} 之间")
        import re

        for key in ("quiet_start", "quiet_end"):
            if not isinstance(settings.get(key), str) or not re.fullmatch(
                r"(?:[01]\d|2[0-3]):[0-5]\d", settings[key]
            ):
                raise ValueError("安静时段需要有效的时:分")
        try:
            ZoneInfo(settings["timezone"])
        except (KeyError, ValueError):
            raise ValueError("请选择有效时区") from None
        clean = {key: settings[key] for key in DEFAULTS}
        due = self.clock() + timedelta(hours=clean["interval_hours"])
        with self.lock, self.db:
            self.db.execute(
                "INSERT INTO proactive_settings VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET "
                "value=excluded.value,version=excluded.version,next_at=excluded.next_at",
                (user, json.dumps(clean), uuid.uuid4().hex, due.isoformat()),
            )
        return clean

    def unread(self, user: str) -> dict[str, int]:
        with self.lock:
            rows = self.db.execute(
                "SELECT character_id,COUNT(*) n FROM proactive_attempts "
                "WHERE user_id=? AND message_id IS NOT NULL AND seen=0 GROUP BY character_id",
                (user,),
            ).fetchall()
        return {r["character_id"]: r["n"] for r in rows}

    def seen(self, user: str, conversation: str) -> None:
        with self.lock, self.db:
            self.db.execute(
                "UPDATE proactive_attempts SET seen=1 WHERE user_id=? AND conversation_id=?",
                (user, conversation),
            )

    def start(self) -> None:
        if self.task is None:
            self.task = asyncio.create_task(self._run())

    async def aclose(self) -> None:
        if self.task:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
        self.db.close()

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(60)
            try:
                await self.tick()
            except Exception as exc:
                log.warning("proactive sweep failed: %s", type(exc).__name__)

    async def tick(self) -> None:
        with self.lock:
            rows = self.db.execute(
                "SELECT user_id FROM proactive_settings WHERE next_at<=?",
                (self.clock().isoformat(),),
            ).fetchall()
        for row in rows:
            user = row["user_id"]
            if self.is_busy(user):
                continue
            selected = self._claim(user)
            if selected:
                await self._generate(*selected)

    def _eligible(self, user: str, character: str, now: datetime) -> bool:
        account = self.db.execute(
            "SELECT banned_at,consented_at FROM users WHERE id=?", (user,)
        ).fetchone()
        if not account or account["banned_at"] or not account["consented_at"]:
            return False
        # Do not interrupt a recent user turn, even in another character's conversation.
        recent = self.db.execute(
            "SELECT MAX(m.created_at) FROM messages m JOIN conversations c "
            "ON c.id=m.conversation_id WHERE c.user_id=? AND m.role='user'",
            (user,),
        ).fetchone()[0]
        if recent and now - datetime.fromisoformat(recent) < timedelta(minutes=15):
            return False
        pending = self.db.execute(
            "SELECT 1 FROM proactive_attempts p WHERE p.user_id=? AND p.character_id=? "
            "AND p.message_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM messages m "
            "JOIN conversations c ON c.id=m.conversation_id WHERE c.user_id=p.user_id "
            "AND c.character_id=p.character_id AND m.role='user' AND m.id>p.message_id)",
            (user, character),
        ).fetchone()
        return not pending and self.cooling(user, character) is None

    def _claim(self, user: str) -> tuple[str, Conversation, int, dict, str] | None:
        now = self.clock()
        with self.lock, self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute(
                "SELECT * FROM proactive_settings WHERE user_id=?", (user,)
            ).fetchone()
            if not row or row["next_at"] > now.isoformat():
                return None
            settings = json.loads(row["value"])
            if not settings["enabled"] or quiet(settings, now):
                return None
            day = now.astimezone(ZoneInfo(settings["timezone"])).date().isoformat()
            count = self.db.execute(
                "SELECT COUNT(*) FROM proactive_attempts WHERE user_id=? AND day=?",
                (user, day),
            ).fetchone()[0]
            if count >= settings["daily_limit"]:
                return None
            # A crashed pending attempt is never retried. Also avoid overlapping slow generations.
            if self.db.execute(
                "SELECT 1 FROM proactive_attempts WHERE user_id=? AND status='pending' AND created_at>?",
                (user, (now - timedelta(minutes=5)).isoformat()),
            ).fetchone():
                return None
            ranked = sorted(
                settings["characters"],
                key=lambda c: self.db.execute(
                    "SELECT COALESCE(MAX(created_at),'') FROM proactive_attempts WHERE user_id=? AND character_id=?",
                    (user, c),
                ).fetchone()[0],
            )
            for character in ranked:
                if not self._eligible(user, character, now):
                    continue
                convo = self.db.execute(
                    "SELECT * FROM conversations WHERE user_id=? AND character_id=? "
                    "ORDER BY created_at DESC,rowid DESC LIMIT 1",
                    (user, character),
                ).fetchone()
                # Use an existing open conversation only. Never create conversations behind the user's back.
                if (
                    not convo
                    or self.db.execute(
                        "SELECT 1 FROM conversation_events WHERE conversation_id=? AND kind='ended'",
                        (convo["id"],),
                    ).fetchone()
                ):
                    continue
                last_id = self.db.execute(
                    "SELECT COALESCE(MAX(id),0) FROM messages WHERE conversation_id=?",
                    (convo["id"],),
                ).fetchone()[0]
                attempt = uuid.uuid4().hex
                self.db.execute(
                    "INSERT INTO proactive_attempts(id,user_id,character_id,conversation_id,version,day,created_at) VALUES(?,?,?,?,?,?,?)",
                    (
                        attempt,
                        user,
                        character,
                        convo["id"],
                        row["version"],
                        day,
                        now.isoformat(),
                    ),
                )
                self.db.execute(
                    "UPDATE proactive_settings SET next_at=? WHERE user_id=?",
                    (
                        (now + timedelta(hours=settings["interval_hours"])).isoformat(),
                        user,
                    ),
                )
                return (
                    attempt,
                    Conversation(**dict(convo)),
                    last_id,
                    settings,
                    row["version"],
                )
        return None

    async def _generate(
        self,
        attempt: str,
        conversation: Conversation,
        last_id: int,
        settings: dict,
        version: str,
    ) -> None:
        user, character = (
            conversation.user_id,
            self.characters[conversation.character_id],
        )
        lease = self.deployer.lease()
        try:
            profile = self.store.get_profile(user)
            prompt = [
                ChatMessage(
                    "system", character.sheet + "\n\n" + format_instructions(None)
                ),
                ChatMessage(
                    "system",
                    producer_prompt(profile)
                    + "\n\n"
                    + self.store.producer_context(user, character.id),
                ),
            ]
            history = [
                m for m in self.store.record(conversation.id) if isinstance(m, Message)
            ][-12:]
            for m in history:
                prompt.append(
                    ChatMessage(
                        "user" if m.role == "user" else "assistant",
                        (m.text or "")
                        if m.role == "user"
                        else format_reply(m.segments),
                    )
                )
            prompt.append(
                ChatMessage(
                    "system",
                    now_prompt(profile, self.clock(), settings["timezone"], False)
                    + "\n\n"
                    + _INSTRUCTIONS,
                )
            )
            parser = ReplyParser()
            async with asyncio.timeout(60):
                size = 0
                async for chunk in lease.keys.chat_llm.stream(prompt):
                    if isinstance(chunk, str):
                        size += len(chunk)
                        if size > 8000:
                            raise ValueError("oversized proactive reply")
                        list(parser.feed(chunk))
                list(parser.finish())
            if (
                not parser.complete
                or any(not s.ja or not s.zh for s in parser.complete)
                or len(parser.complete) > 4
            ):
                raise ValueError("invalid proactive reply")
            self._deliver(attempt, conversation, last_id, version, parser.complete)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Never include content, credentials or exception messages in logs.
            log.warning("proactive generation failed: %s", type(exc).__name__)
            with self.lock, self.db:
                self.db.execute(
                    "UPDATE proactive_attempts SET status='failed' WHERE id=?",
                    (attempt,),
                )
        finally:
            lease.release()

    def _deliver(
        self,
        attempt: str,
        convo: Conversation,
        expected: int,
        version: str,
        segments: list[Segment],
    ) -> bool:
        with self.lock, self.db:
            self.db.execute("BEGIN IMMEDIATE")
            setting = self.db.execute(
                "SELECT * FROM proactive_settings WHERE user_id=?", (convo.user_id,)
            ).fetchone()
            claimed = self.db.execute(
                "SELECT status FROM proactive_attempts WHERE id=?", (attempt,)
            ).fetchone()
            current = self.db.execute(
                "SELECT id FROM conversations WHERE user_id=? AND character_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1",
                (convo.user_id, convo.character_id),
            ).fetchone()
            last = self.db.execute(
                "SELECT COALESCE(MAX(id),0) FROM messages WHERE conversation_id=?",
                (convo.id,),
            ).fetchone()[0]
            ended = self.db.execute(
                "SELECT 1 FROM conversation_events WHERE conversation_id=? AND kind='ended'",
                (convo.id,),
            ).fetchone()
            valid = bool(
                setting
                and setting["version"] == version
                and claimed
                and claimed[0] == "pending"
                and current
                and current[0] == convo.id
                and last == expected
                and not ended
            )
            if valid:
                config = json.loads(setting["value"])
                valid = (
                    config["enabled"]
                    and convo.character_id in config["characters"]
                    and not quiet(config, self.clock())
                    and not self.is_busy(convo.user_id)
                    and self._eligible(convo.user_id, convo.character_id, self.clock())
                )
            if not valid:
                self.db.execute(
                    "UPDATE proactive_attempts SET status='discarded' WHERE id=? AND status='pending'",
                    (attempt,),
                )
                return False
            cursor = self.db.execute(
                "INSERT INTO messages(conversation_id,role,ja,zh,segments,created_at) VALUES(?,'character',?,?,?,?)",
                (
                    convo.id,
                    "".join(s.ja for s in segments),
                    "".join(s.zh for s in segments),
                    json.dumps([asdict(s) for s in segments], ensure_ascii=False),
                    self.clock().isoformat(),
                ),
            )
            self.db.execute(
                "UPDATE proactive_attempts SET message_id=?,status='sent' WHERE id=?",
                (cursor.lastrowid, attempt),
            )
            return True
