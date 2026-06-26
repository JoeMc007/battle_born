"""Research a validated YouTube idea — gather facts, stats, and sources."""

from .client import get_client, MODEL, MAX_TOKENS

SYSTEM_PROMPT = """You are a rigorous research journalist and fact-checker for YouTube creators.
Your job is to gather accurate, verifiable information so the creator never publishes false claims.

For every research session you will:
1. Search multiple angles of the topic (definitions, statistics, studies, expert opinions,
   counterarguments, common misconceptions)
2. Cross-reference claims across sources before including them
3. Flag anything that is disputed, outdated, or hard to verify
4. Organize findings into clearly labeled sections a scriptwriter can pull from directly
5. List every source with title, URL (if available), and date

Output format:
## KEY FACTS
Bullet list of the most important, verified facts with source citations inline [Source: ...]

## STATISTICS & DATA
Numbers, percentages, study results — always with source and date

## EXPERT OPINIONS
Quotes or paraphrased views from credible authorities in the field

## COMMON MISCONCEPTIONS
What people get wrong about this topic (important for credibility)

## COUNTERARGUMENTS
The other side of the argument — present these fairly

## SOURCES
Full list of all references used

Be thorough, be accurate, and flag uncertainty explicitly with ⚠️."""


def research_idea(idea: str, niche: str = "") -> None:
    """Stream a deep research report on a YouTube video idea using web search."""
    client = get_client()

    context = f"Channel niche: {niche}\n\n" if niche else ""
    user_message = f"""{context}YouTube video idea to research:

"{idea}"

Search the web thoroughly and compile every verifiable fact, statistic, expert opinion,
and source relevant to this topic. I need this research to be accurate — my audience
trusts me to get things right."""

    print("\n" + "=" * 60)
    print("RESEARCH REPORT")
    print("=" * 60 + "\n")

    tools = [
        {
            "type": "web_search_20260209",
            "name": "web_search",
        }
    ]

    messages = [{"role": "user", "content": user_message}]

    # Allow multiple tool-call rounds so Claude can search iteratively
    while True:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        ) as stream:
            tool_uses = []
            tool_results_needed = False
            current_tool_name = ""
            current_tool_id = ""
            current_tool_input_chunks: list[str] = []
            showing_response = False

            for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "thinking":
                        print("[Researching...]\n")
                        showing_response = False
                    elif block.type == "text":
                        showing_response = True
                    elif block.type == "tool_use":
                        showing_response = False
                        current_tool_id = block.id
                        current_tool_name = block.name
                        current_tool_input_chunks = []

                elif event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta" and showing_response:
                        print(delta.text, end="", flush=True)
                    elif delta.type == "input_json_delta":
                        current_tool_input_chunks.append(delta.partial_json)

                elif event.type == "content_block_stop":
                    if current_tool_id:
                        import json
                        raw = "".join(current_tool_input_chunks)
                        try:
                            tool_input = json.loads(raw) if raw else {}
                        except json.JSONDecodeError:
                            tool_input = {}
                        query = tool_input.get("query", "")
                        if query:
                            print(f"\n[Searching: {query}]")
                        tool_uses.append({
                            "id": current_tool_id,
                            "name": current_tool_name,
                            "input": tool_input,
                        })
                        tool_results_needed = True
                        current_tool_id = ""
                        current_tool_name = ""
                        current_tool_input_chunks = []

                elif event.type == "message_stop":
                    pass

            final = stream.get_final_message()

            if final.stop_reason != "tool_use" or not tool_uses:
                break

            # Build assistant turn with all content blocks
            messages.append({"role": "assistant", "content": final.content})

            # Return tool results so Claude can continue searching
            tool_result_content = []
            for tu in tool_uses:
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": "Search executed. Please incorporate the results above into your research.",
                })

            messages.append({"role": "user", "content": tool_result_content})

    print("\n")
