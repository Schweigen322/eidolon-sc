"""Relationship guidance reaches roleplay and judgement without rewriting speech."""

from eidolon.characters import load_characters
from eidolon.config import Settings
from eidolon.judge import SAID, turn_state
from eidolon.relationship import RELATIONSHIP_GUIDANCE
from tests.conftest import ClientFactory
from tests.fakes import FakeLLM, system_of
from tests.test_text_turn import send_turn, start_conversation


async def test_relationship_guidance_reaches_both_models(
    make_client: ClientFactory, settings: Settings,
):
    llm = FakeLLM(["<ja>三人で、どこに行こうか？</ja><zh>三个人去哪里呢？</zh>"])
    client = make_client(llm)
    conversation = await start_conversation(client)
    said = "いや、ルカはいないよ。私、あなた、そしてはるき。私たち3人だ。"
    await send_turn(client, conversation, said)
    assert RELATIONSHIP_GUIDANCE in system_of(llm.prompts[0])
    character = load_characters(settings.characters_path)["mano"]
    state = turn_state(character, [], said)
    assert state["关系沟通说明"] == RELATIONSHIP_GUIDANCE
    assert state[SAID] == said
