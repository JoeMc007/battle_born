"""Project management — save every stage of a video to a named project folder."""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = Path.home() / ".youtube_creator" / "projects"


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug[:60]


def _project_path(name: str) -> Path:
    return PROJECTS_DIR / _slug(name)


def _meta_path(project_dir: Path) -> Path:
    return project_dir / "meta.json"


def _load_meta(project_dir: Path) -> dict:
    p = _meta_path(project_dir)
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_meta(project_dir: Path, meta: dict) -> None:
    _meta_path(project_dir).write_text(json.dumps(meta, indent=2))


# ── Public API ────────────────────────────────────────────────────────────────

def create_project(idea: str, niche: str = "") -> Path:
    """Create a new project folder for a video idea."""
    project_dir = _project_path(idea)
    project_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "idea": idea,
        "niche": niche,
        "created": datetime.now().isoformat(),
        "stages_completed": [],
        "rating": None,
        "feedback": [],
    }
    _save_meta(project_dir, meta)
    return project_dir


def save_stage(idea: str, stage: str, content: str) -> Path:
    """Save output from a pipeline stage (validate/research/script/seo/titles)."""
    project_dir = _project_path(idea)
    project_dir.mkdir(parents=True, exist_ok=True)

    file_path = project_dir / f"{stage}.md"
    file_path.write_text(content)

    meta = _load_meta(project_dir)
    if stage not in meta.get("stages_completed", []):
        meta.setdefault("stages_completed", []).append(stage)
        meta[f"{stage}_at"] = datetime.now().isoformat()
    _save_meta(project_dir, meta)

    return file_path


def load_stage(idea: str, stage: str) -> str | None:
    """Load saved output from a previous stage."""
    p = _project_path(idea) / f"{stage}.md"
    return p.read_text() if p.exists() else None


def save_feedback(idea: str, rating: int, notes: str) -> None:
    """Record creator feedback on a completed script."""
    project_dir = _project_path(idea)
    meta = _load_meta(project_dir)
    meta["rating"] = rating
    meta["feedback"].append({
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "notes": notes,
    })
    _save_meta(project_dir, meta)


def list_projects() -> list[dict]:
    """Return all projects sorted by creation date, newest first."""
    if not PROJECTS_DIR.exists():
        return []
    projects = []
    for d in PROJECTS_DIR.iterdir():
        if d.is_dir():
            meta = _load_meta(d)
            if meta:
                projects.append(meta | {"slug": d.name})
    return sorted(projects, key=lambda m: m.get("created", ""), reverse=True)


def get_project(idea: str) -> dict | None:
    project_dir = _project_path(idea)
    if not project_dir.exists():
        return None
    return _load_meta(project_dir) | {"path": str(project_dir)}


def delete_project(idea: str) -> bool:
    project_dir = _project_path(idea)
    if project_dir.exists():
        shutil.rmtree(project_dir)
        return True
    return False


def print_project_list() -> None:
    projects = list_projects()
    if not projects:
        print("No projects yet. Run 'workflow' or 'validate' to start one.")
        return

    print(f"\n{'#':<4} {'IDEA':<45} {'STAGES':<30} {'RATING'}")
    print("-" * 90)
    for i, p in enumerate(projects, 1):
        stages = ", ".join(p.get("stages_completed", [])) or "—"
        rating = f"{p['rating']}/5" if p.get("rating") else "—"
        idea = p.get("idea", "")[:43]
        print(f"{i:<4} {idea:<45} {stages:<30} {rating}")
    print()
