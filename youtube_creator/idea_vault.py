"""Idea Vault — capture, tag, score, and manage your video ideas."""

import json
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path.home() / ".youtube_creator" / "idea_vault.json"

STATUS_OPTIONS = ["raw", "validated", "researched", "scripted", "filmed", "published", "archived"]


def _load() -> list[dict]:
    if not VAULT_PATH.exists():
        return []
    return json.loads(VAULT_PATH.read_text())


def _save(ideas: list[dict]) -> None:
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VAULT_PATH.write_text(json.dumps(ideas, indent=2))


# ── Public API ────────────────────────────────────────────────────────────────

def add_idea(
    idea: str,
    niche: str = "",
    tags: list[str] | None = None,
    source: str = "manual",
    viability_score: int | None = None,
    notes: str = "",
) -> dict:
    """Add a new idea to the vault."""
    ideas = _load()

    entry = {
        "id": len(ideas) + 1,
        "idea": idea,
        "niche": niche,
        "tags": tags or [],
        "source": source,          # manual / validated / researched / ai-suggested
        "status": "raw",
        "viability_score": viability_score,
        "notes": notes,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }
    ideas.append(entry)
    _save(ideas)
    return entry


def update_idea(idea_id: int, **kwargs) -> dict | None:
    """Update fields on an existing vault entry."""
    ideas = _load()
    for entry in ideas:
        if entry["id"] == idea_id:
            for k, v in kwargs.items():
                entry[k] = v
            entry["updated"] = datetime.now().isoformat()
            _save(ideas)
            return entry
    return None


def get_ideas(
    status: str | None = None,
    niche: str | None = None,
    tag: str | None = None,
    min_score: int | None = None,
) -> list[dict]:  # noqa: E501
    """Filter vault by status, niche, tag, or minimum viability score."""
    ideas = _load()
    if status:
        ideas = [i for i in ideas if i.get("status") == status]
    if niche:
        ideas = [i for i in ideas if niche.lower() in i.get("niche", "").lower()]
    if tag:
        ideas = [i for i in ideas if tag.lower() in [t.lower() for t in i.get("tags", [])]]
    if min_score is not None:
        ideas = [i for i in ideas if (i.get("viability_score") or 0) >= min_score]
    return ideas


def get_all() -> list[dict]:
    return _load()


def advance_status(idea_id: int) -> str | None:
    """Move an idea to the next status in the pipeline."""
    ideas = _load()
    for entry in ideas:
        if entry["id"] == idea_id:
            current = entry.get("status", "raw")
            if current in STATUS_OPTIONS:
                idx = STATUS_OPTIONS.index(current)
                if idx < len(STATUS_OPTIONS) - 1:
                    entry["status"] = STATUS_OPTIONS[idx + 1]
                    entry["updated"] = datetime.now().isoformat()
                    _save(ideas)
                    return entry["status"]
    return None


def print_vault(ideas: list[dict] | None = None) -> None:
    if ideas is None:
        ideas = _load()
    if not ideas:
        print("\nIdea vault is empty. Add ideas with: python main.py vault add \"your idea\"")
        return

    print(f"\n{'ID':<5} {'SCORE':<7} {'STATUS':<12} {'IDEA':<50} {'TAGS'}")
    print("-" * 100)
    for entry in ideas:
        score = f"{entry['viability_score']}/10" if entry.get("viability_score") else "—"
        tags = ", ".join(entry.get("tags", [])) or "—"
        idea_text = entry["idea"][:48]
        status = entry.get("status", "raw")
        print(f"{entry['id']:<5} {score:<7} {status:<12} {idea_text:<50} {tags}")
    print()
