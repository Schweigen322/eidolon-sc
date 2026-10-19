"""Known name transcription errors; preserve the producer's original words."""

from eidolon.characters import Character

_MISHEARD = {
    "haruki": ("晴樹", "晴树"),
    "hana": ("花",),
    "kiriko": ("桐子",),
    "kogane": ("小金",),
}
_ADDRESS_PUNCTUATION = " \t\r\n　!！?？。．.,，、～~…"


def misheard_address(character: Character, text: str) -> bool:
    """Only a confirmed alternative name, with no other words or instructions."""
    return text.strip(_ADDRESS_PUNCTUATION) in _MISHEARD.get(character.id, ())


def name_recognition_prompt(character: Character) -> str:
    alternatives = _MISHEARD.get(character.id, ())
    if not alternatives:
        return ""
    return (
        f"称呼识别说明：当前对话角色是{character.name}。语音转写可能把她的名字写成"
        + "、".join(f"「{name}」" for name in alternatives)
        + "。当上下文是在叫她时，按她本人的称呼理解，不因这种字形误差认定制作人"
        "不在意她、失礼、挑衅或叫错恋人，不以此扣好感或生气，也不反复纠正名字。"
        "这些是可能的转写误差，不是新名字或昵称；不要改写原话。"
        "普通词义（如谈论花）、明确谈及其他人或故意侮辱，仍按上下文实际含义处理。"
    )
