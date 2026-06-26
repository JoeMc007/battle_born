"""Validate and improve a YouTube video idea using Claude with web search."""

from .client import get_client, MODEL, MAX_TOKENS

SYSTEM_PROMPT = """You are an expert YouTube strategist with deep knowledge of content trends,
audience psychology, and what makes videos go viral. You analyze video ideas critically and
provide actionable improvements.

When given a YouTube video idea, you will:
1. Assess the idea's potential (hook strength, search demand, competition level, audience appeal)
2. Identify weaknesses and missed opportunities
3. Suggest 3 improved versions of the idea with stronger hooks and angles
4. Recommend the best title format (question, how-to, listicle, controversy, story)
5. Give an overall viability score (1-10) with clear reasoning

Be direct, specific, and data-driven. Reference current trends when relevant."""


def validate_and_improve(idea: str, niche: str = "") -> None:
    """Stream a validation and improvement analysis for a YouTube video idea."""
    client = get_client()

    context = f"Niche/channel focus: {niche}\n\n" if niche else ""
    user_message = f"""{context}YouTube video idea to validate and improve:

"{idea}"

Please analyze this idea thoroughly and provide your expert assessment."""

    print("\n" + "=" * 60)
    print("IDEA VALIDATION & IMPROVEMENT")
    print("=" * 60 + "\n")

    tools = [
        {
            "type": "web_search_20260209",
            "name": "web_search",
        }
    ]

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        showing_thinking = False
        showing_response = False

        for event in stream:
            if event.type == "content_block_start":
                block = event.content_block
                if block.type == "thinking":
                    print("[Analyzing your idea...]\n")
                    showing_thinking = True
                    showing_response = False
                elif block.type == "text":
                    if showing_thinking:
                        print()
                    showing_thinking = False
                    showing_response = True
                elif block.type == "tool_use":
                    showing_thinking = False
                    showing_response = False
                    print(f"\n[Searching: {getattr(block, 'input', {}).get('query', '')}...]")

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta" and showing_response:
                    print(delta.text, end="", flush=True)

            elif event.type == "content_block_stop":
                if showing_response:
                    pass

    print("\n")
