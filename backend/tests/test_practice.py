"""Japanese practice in a call (「日语练习」): she corrects the user's Japanese in her own
voice, writes a practice pause, and the rest of her voice is held until the user goes on."""

from pipecat.frames.frames import Frame
from pipecat.processors.frameworks.rtvi.frames import RTVIClientMessageFrame
from pipecat.tests.utils import SleepFrame

from eidolon.reply_format import PRACTICE_INSTRUCTIONS, PracticePause, ReplyParser, SegmentComplete
from tests.fakes import FakeLLM
from tests.test_call_turns import (  # noqa: F401  # the fixture
    CallUnderTest,
    mano_call,
    one_by_one,
    spoken,
)

CORRECTION = "<ja>あ、そこは「が」かな。</ja><zh>啊，那里用「が」吧。</zh><ja>猫が好きです。</ja><zh>我喜欢猫。</zh>"
REST = "<ja>私も好き！</ja><zh>我也喜欢！</zh>"
PRACTICE_REPLY = CORRECTION + "<pause/>" + REST


def parsed(*chunks: str) -> tuple[list[object], ReplyParser]:
    parser = ReplyParser()
    events = [e for chunk in chunks for e in parser.feed(chunk)] + parser.finish()
    return [e for e in events if isinstance(e, PracticePause | SegmentComplete)], parser


def test_a_pause_is_said_once_the_segments_before_it_are_complete():
    for size in (1, 3, 7, len(PRACTICE_REPLY)):
        chunks = [PRACTICE_REPLY[i : i + size] for i in range(0, len(PRACTICE_REPLY), size)]
        events, parser = parsed(*chunks)
        assert events == [SegmentComplete(0), SegmentComplete(1), PracticePause(2), SegmentComplete(2)]
        assert [s.ja for s in parser.segments] == ["あ、そこは「が」かな。", "猫が好きです。", "私も好き！"]


def test_a_pause_is_neither_shown_nor_voiced_even_in_the_middle_of_her_words():
    events, parser = parsed("<ja>あ<pause/>い</ja><zh>啊</zh>" + REST)
    assert PracticePause(1) in events
    assert parser.segments[0].ja == "あい"


def test_a_pause_before_her_first_segment_or_after_the_first_is_left_out():
    events, _ = parsed("<pause/>" + CORRECTION + "<pause/>" + REST + "<pause />" + REST)
    assert [e for e in events if isinstance(e, PracticePause)] == [PracticePause(2)]


def go_on() -> RTVIClientMessageFrame:
    return RTVIClientMessageFrame(msg_id="m3", type="practice-continue", data={})


def after_she_corrects(*frames: Frame) -> list[Frame]:
    return one_by_one(spoken("猫を好きです"), SleepFrame(0.3), *frames)


async def test_her_voice_is_held_at_the_pause(mano_call: CallUnderTest):
    llm = FakeLLM([PRACTICE_REPLY])

    spoken_text, messages = await mano_call.run(llm, after_she_corrects(), practice=True)

    assert "".join(spoken_text) == "あ、そこは「が」かな。猫が好きです。"
    assert {"type": "practice-pause", "reply": 1, "after": 2} in messages
    assert any(PRACTICE_INSTRUCTIONS in m.content for m in llm.prompts[0] if m.role == "system")


async def test_going_on_voices_the_rest(mano_call: CallUnderTest):
    spoken_text, _ = await mano_call.run(
        FakeLLM([PRACTICE_REPLY]), after_she_corrects(go_on()), practice=True
    )

    assert "".join(spoken_text) == "あ、そこは「が」かな。猫が好きです。私も好き！"


async def test_without_practice_nothing_is_held_nor_asked(mano_call: CallUnderTest):
    llm = FakeLLM([PRACTICE_REPLY])

    spoken_text, messages = await mano_call.run(llm, after_she_corrects())

    assert "".join(spoken_text) == "あ、そこは「が」かな。猫が好きです。私も好き！"
    assert not any(m["type"] == "practice-pause" for m in messages)
    assert not any(PRACTICE_INSTRUCTIONS in m.content for m in llm.prompts[0])
