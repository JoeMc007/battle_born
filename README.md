# YouTube Creator App

AI-powered CLI for YouTube creators — validate ideas and generate scripts using Claude Opus 4.8.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

### Validate & Improve a Video Idea

Analyze your idea's potential and get 3 improved versions with stronger hooks:

```bash
python main.py validate "5 productivity hacks that actually work" --niche "self-improvement"
```

### Generate a Full Script

Get a ready-to-record script with visual cues, pacing notes, and chapter markers:

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

- **Idea Validator**: Uses Claude Opus 4.8 with adaptive thinking + live web search to assess
  your idea against current trends, competition, and audience demand
- **Script Generator**: Uses Claude Opus 4.8 with adaptive thinking to craft a full
  professionally structured script optimized for viewer retention

Both features stream output in real time so you see results as Claude generates them.
