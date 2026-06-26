import anthropic

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client
