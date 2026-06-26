# YouTube Creator App

AI-powered CLI for YouTube creators — validate ideas, research facts, and generate scripts
using Claude Opus 4.8.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## Creator Workflow

The recommended path runs two steps automatically:

```
validate → research → (you review) → script
```

### Step 1 + 2 combined: `workflow` (recommended)

Runs idea validation and deep fact research back-to-back:

```bash
python main.py workflow "5 productivity hacks that actually work" --niche "self-improvement"
```

### Step 1 only: `validate`

Score your idea's potential and get 3 stronger hook variations:

```bash
python main.py validate "5 productivity hacks that actually work" --niche "self-improvement"
```

### Step 2 only: `research`

Deep-dive into facts, statistics, expert opinions, and sources for any topic:

```bash
python main.py research "5 productivity hacks that actually work" --niche "self-improvement"
```

Outputs organized sections:
- **Key Facts** — verified claims with inline citations
- **Statistics & Data** — numbers and study results with dates
- **Expert Opinions** — credible authority quotes
- **Common Misconceptions** — what people get wrong (protects your credibility)
- **Counterarguments** — the other side, presented fairly
- **Sources** — full reference list

### Step 3: `script`

Generate a ready-to-record script after reviewing your research:

```bash
python main.py script "5 productivity hacks that actually work" \
  --duration 10 \
  --style educational \
  --audience "busy professionals aged 25-40" \
  --points "time blocking,pomodoro,deep work,batching,weekly review"
```

### Script Styles

| Style | Best for |
|-------|----------|
| `educational` | Teach something (default) |
| `entertainment` | Entertaining/funny content |
| `tutorial` | Step-by-step how-tos |
| `storytime` | Personal narrative |
| `review` | Product/service reviews |
| `vlog` | Day-in-the-life content |

## How It Works

- **Idea Validator**: Claude Opus 4.8 + adaptive thinking + live web search scores your idea
  and generates stronger hook variations
- **Researcher**: Claude Opus 4.8 performs multiple web searches, cross-references sources,
  and flags disputed or uncertain claims with ⚠️ so your content stays honest
- **Script Generator**: Claude Opus 4.8 crafts a full professionally structured script with
  `[VISUAL CUE]`, `[PAUSE]`, and `[TITLE CARD]` markers ready to record

All features stream output in real time so you see results as Claude generates them.
