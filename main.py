#!/usr/bin/env python3
"""YouTube Creator App — AI-powered full video production pipeline."""

import argparse
import sys


# ── Shared helpers ────────────────────────────────────────────────────────────

def _prompt_continue(question: str, default: bool = True) -> bool:
    """Ask a yes/no question. Returns True to continue, False to skip."""
    hint = "[Y/n]" if default else "[y/N]"
    try:
        raw = input(f"\n{question} {hint}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if not raw:
        return default
    return raw in ("y", "yes")


def _step_banner(step: int, total: int, name: str) -> None:
    print(f"\n{'█' * 60}")
    print(f"  STEP {step}/{total} — {name}")
    print(f"{'█' * 60}")


# ── Individual command handlers ───────────────────────────────────────────────

def cmd_setup(args: argparse.Namespace) -> None:
    from youtube_creator.channel_dna import setup_dna_interactive
    setup_dna_interactive()


def cmd_validate(args: argparse.Namespace) -> None:
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.projects import create_project
    create_project(args.idea, args.niche or "")
    validate_and_improve(idea=args.idea, niche=args.niche or "")


def cmd_research(args: argparse.Namespace) -> None:
    from youtube_creator.research import research_idea
    research_idea(idea=args.idea, niche=args.niche or "")


def cmd_workflow(args: argparse.Namespace) -> None:
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.research import research_idea
    from youtube_creator.projects import create_project
    from youtube_creator.idea_vault import add_idea

    create_project(args.idea, args.niche or "")

    _step_banner(1, 2, "IDEA VALIDATION")
    validate_and_improve(idea=args.idea, niche=args.niche or "")

    _step_banner(2, 2, "RESEARCH")
    research_idea(idea=args.idea, niche=args.niche or "")

    add_idea(idea=args.idea, niche=args.niche or "", source="validated", tags=["workflow"])
    print(f"\n✓ Idea saved to vault.")
    print(f"  Next:  python main.py produce \"{args.idea}\"")


def cmd_script(args: argparse.Namespace) -> None:
    from youtube_creator.generate_script import generate_script
    from youtube_creator.projects import save_stage, load_stage
    from youtube_creator.idea_vault import _load as vault_load, update_idea
    from youtube_creator.learning import collect_feedback, regenerate_learning_profile

    key_points = [p.strip() for p in args.points.split(",")] if args.points else None

    research_notes = ""
    if args.research_file:
        try:
            with open(args.research_file) as f:
                research_notes = f.read()
        except FileNotFoundError:
            print(f"Warning: research file not found: {args.research_file}")
    elif not args.no_project:
        saved = load_stage(args.topic, "research")
        if saved:
            research_notes = saved
            print("[Loaded research from project]")

    script_text = generate_script(
        topic=args.topic,
        duration_minutes=args.duration,
        style=args.style,
        audience=args.audience or "",
        key_points=key_points,
        research_notes=research_notes,
    )

    if script_text and not args.no_project:
        path = save_stage(args.topic, "script", script_text)
        print(f"✓ Script saved → {path}")
        for entry in vault_load():
            if entry["idea"].lower() == args.topic.lower():
                update_idea(entry["id"], status="scripted")
                break

    if getattr(args, "export_elevenlabs", False) and script_text and not args.no_project:
        from youtube_creator.elevenlabs_export import export_for_elevenlabs
        print("\n" + "─" * 60)
        print("Auto-exporting for ElevenLabs...")
        export_for_elevenlabs(topic=args.topic, script_text=script_text)

    if not args.no_feedback and script_text:
        result = collect_feedback(args.topic)
        if result:
            regenerate_learning_profile()


def cmd_revise(args: argparse.Namespace) -> None:
    from youtube_creator.revise_script import revise_script
    revise_script(topic=args.topic)


def cmd_seo(args: argparse.Namespace) -> None:
    from youtube_creator.seo_package import generate_seo_package
    generate_seo_package(topic=args.topic)


def cmd_visuals(args: argparse.Namespace) -> None:
    from youtube_creator.visual_prompts import generate_visual_prompts
    generate_visual_prompts(
        topic=args.topic,
        visual_style=args.style,
        sentences_per_chunk=args.chunk,
        broll_count=args.broll,
        output_file=args.output or "",
    )


def cmd_export(args: argparse.Namespace) -> None:
    from youtube_creator.elevenlabs_export import export_for_elevenlabs
    export_for_elevenlabs(
        topic=args.topic,
        output_file=args.output or "",
        polish=not args.no_polish,
    )


def cmd_footage(args: argparse.Namespace) -> None:
    from youtube_creator.footage_finder import find_footage
    find_footage(topic=args.topic)


def cmd_description(args: argparse.Namespace) -> None:
    from youtube_creator.yt_description import generate_yt_description
    generate_yt_description(topic=args.topic)


def cmd_learn(args: argparse.Namespace) -> None:
    from youtube_creator.learning import regenerate_learning_profile, print_learning_summary
    regenerate_learning_profile()
    print_learning_summary()


def cmd_projects(args: argparse.Namespace) -> None:
    from youtube_creator.projects import print_project_list, get_project, delete_project
    action = args.project_action
    if action in ("list", None):
        print_project_list()
    elif action == "show":
        p = get_project(args.name)
        if p:
            import json
            print(json.dumps(p, indent=2))
        else:
            print(f"No project found for: {args.name}")
    elif action == "delete":
        if delete_project(args.name):
            print(f"✓ Deleted project: {args.name}")
        else:
            print(f"No project found for: {args.name}")


def cmd_vault(args: argparse.Namespace) -> None:
    from youtube_creator.idea_vault import (
        add_idea, _load as vault_load, print_vault, update_idea, advance_status
    )
    action = args.vault_action

    if action == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        entry = add_idea(idea=args.idea, niche=args.niche or "", tags=tags)
        print(f"\n✓ Idea #{entry['id']} added: {args.idea}")

    elif action in ("list", None):
        ideas = vault_load()
        if getattr(args, "status", ""):
            ideas = [i for i in ideas if i.get("status") == args.status]
        if getattr(args, "tag", ""):
            ideas = [i for i in ideas if args.tag in i.get("tags", [])]
        print_vault(ideas)

    elif action == "tag":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        if update_idea(args.id, tags=tags):
            print(f"✓ Tags updated on idea #{args.id}")
        else:
            print(f"No idea with id {args.id}")

    elif action == "advance":
        new_status = advance_status(args.id)
        if new_status:
            print(f"✓ Idea #{args.id} → {new_status}")
        else:
            print(f"Could not advance idea #{args.id}")

    elif action == "note":
        if update_idea(args.id, notes=args.text):
            print(f"✓ Note saved on idea #{args.id}")
        else:
            print(f"No idea with id {args.id}")


# ── PRODUCE — the full pipeline command ──────────────────────────────────────

def cmd_produce(args: argparse.Namespace) -> None:
    """
    Full interactive production pipeline — 9 steps:
      validate → research → script → revise → export → visuals → footage → seo → description

    Each step prompts before continuing. Pass --auto to run without prompts.
    Pass --from <stage> to resume mid-pipeline from a saved project.
    """
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.research import research_idea
    from youtube_creator.generate_script import generate_script
    from youtube_creator.revise_script import revise_script
    from youtube_creator.elevenlabs_export import export_for_elevenlabs
    from youtube_creator.visual_prompts import generate_visual_prompts
    from youtube_creator.footage_finder import find_footage
    from youtube_creator.seo_package import generate_seo_package
    from youtube_creator.yt_description import generate_yt_description
    from youtube_creator.projects import create_project, load_stage, save_stage
    from youtube_creator.idea_vault import add_idea
    from youtube_creator.learning import collect_feedback, regenerate_learning_profile

    topic = args.topic
    niche = args.niche or ""
    auto = args.auto
    start_from = args.from_stage or "validate"
    visual_style = args.visual_style

    STAGES = [
        "validate", "research", "script", "revise",
        "export", "visuals", "footage", "seo", "description",
    ]
    TOTAL = len(STAGES)

    def should_run(stage: str) -> bool:
        return STAGES.index(stage) >= STAGES.index(start_from)

    def ask(question: str, default: bool = True) -> bool:
        return True if auto else _prompt_continue(question, default)

    create_project(topic, niche)
    step = 0

    # ── Step 1: Validate ─────────────────────────────────────────────────────
    if should_run("validate"):
        step += 1
        _step_banner(step, TOTAL, "IDEA VALIDATION")
        validate_and_improve(idea=topic, niche=niche)
        add_idea(idea=topic, niche=niche, source="validated", tags=["produce"])

    # ── Step 2: Research ─────────────────────────────────────────────────────
    if should_run("research"):
        proceed = True
        if should_run("validate"):
            proceed = ask("Research this topic now?")
        if proceed:
            step += 1
            _step_banner(step, TOTAL, "RESEARCH")
            research_idea(idea=topic, niche=niche)
        else:
            print("  Skipped research.")

    # ── Step 3: Script ───────────────────────────────────────────────────────
    if should_run("script"):
        if not ask("Generate the script now?"):
            print(f"\nStopped at script stage.")
            print(f"Resume with:  python main.py produce \"{topic}\" --from script")
            return

        step += 1
        _step_banner(step, TOTAL, "SCRIPT GENERATION")

        research_notes = load_stage(topic, "research") or ""
        if research_notes:
            print("[Research loaded from project ✓]")

        script_text = generate_script(
            topic=topic,
            duration_minutes=args.duration,
            style=args.style,
            audience=niche,
            research_notes=research_notes,
        )
        if script_text:
            save_stage(topic, "script", script_text)
    else:
        script_text = load_stage(topic, "script") or ""

    if not script_text:
        print("\nNo script available — cannot continue pipeline.")
        print(f"Run:  python main.py script \"{topic}\"  then resume.")
        return

    # ── Step 4: Revise ───────────────────────────────────────────────────────
    if should_run("revise"):
        if ask("Revise the script before exporting?", default=False):
            step += 1
            _step_banner(step, TOTAL, "SCRIPT REVISION")
            revised = revise_script(topic=topic, script_text=script_text)
            if revised:
                script_text = revised

    # ── Step 5: ElevenLabs Export ────────────────────────────────────────────
    if should_run("export"):
        if ask("Export clean spoken script for ElevenLabs?"):
            step += 1
            _step_banner(step, TOTAL, "ELEVENLABS EXPORT")
            export_for_elevenlabs(topic=topic, script_text=script_text)

    # ── Step 6: Visual Prompts (AI-generated images + video) ─────────────────
    if should_run("visuals"):
        if ask("Generate AI image + video prompts for OpenArt?"):
            step += 1
            _step_banner(step, TOTAL, "VISUAL PROMPTS  (OpenArt)")
            generate_visual_prompts(
                topic=topic,
                visual_style=visual_style,
                script_text=script_text,
            )

    # ── Step 7: Footage Finder (real stock footage) ───────────────────────────
    if should_run("footage"):
        if ask("Search for real stock footage for your scenes?"):
            step += 1
            _step_banner(step, TOTAL, "FOOTAGE FINDER  (Stock Footage)")
            find_footage(topic=topic, script_text=script_text)

    # ── Step 8: SEO Package (titles + thumbnails) ─────────────────────────────
    if should_run("seo"):
        if ask("Generate SEO package (title options + thumbnail concepts)?"):
            step += 1
            _step_banner(step, TOTAL, "SEO PACKAGE  (Titles + Thumbnails)")
            generate_seo_package(topic=topic, script_text=script_text)

    # ── Step 9: YouTube Description ───────────────────────────────────────────
    if should_run("description"):
        if ask("Generate copy-paste YouTube description with chapters + keywords?"):
            step += 1
            _step_banner(step, TOTAL, "YOUTUBE DESCRIPTION  (Copy-Paste Ready)")
            seo_data = load_stage(topic, "seo") or ""
            generate_yt_description(
                topic=topic,
                script_text=script_text,
                seo_data=seo_data,
            )

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "█" * 60)
    print("  PRODUCTION COMPLETE")
    print("█" * 60)
    print(f"\nAll files saved to:  ~/.youtube_creator/projects/")
    print("")
    print("  script.md           → full script with all directions")
    print("  elevenlabs.txt      → clean spoken-only voice script")
    print("  visual_prompts.txt  → OpenArt AI image + video prompts")
    print("  footage.md          → real stock footage search results")
    print("  seo.md              → title options + thumbnail concepts")
    print("  description.md      → copy-paste YouTube description")
    print("")

    if not auto:
        result = collect_feedback(topic)
        if result:
            regenerate_learning_profile()


# ── Parser ────────────────────────────────────────────────────────────────────

def _add_idea_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("idea", help="Your video idea")
    p.add_argument("--niche", default="", help="Channel niche or focus area")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube-creator",
        description="AI-powered YouTube video production pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── produce (master workflow) ─────────────────────────────────────────────
    p_produce = sub.add_parser(
        "produce",
        help="★ Full pipeline: validate → research → script → revise → export → visuals → seo",
    )
    p_produce.add_argument("topic", help="Your video topic or idea")
    p_produce.add_argument("--niche", default="", help="Channel niche")
    p_produce.add_argument(
        "--from", dest="from_stage", default="validate",
        choices=["validate", "research", "script", "revise", "export",
                 "visuals", "footage", "seo", "description"],
        help="Resume pipeline from a specific stage (default: validate)",
    )
    p_produce.add_argument(
        "--auto", action="store_true",
        help="Run all stages without prompting",
    )
    p_produce.add_argument(
        "--duration", type=int, default=10,
        choices=[3, 5, 7, 10, 15, 20, 30],
        help="Script duration in minutes (default: 10)",
    )
    p_produce.add_argument(
        "--style", default="educational",
        choices=["educational", "entertainment", "tutorial", "storytime",
                 "review", "vlog", "documentary", "rant"],
        help="Script style (default: educational)",
    )
    p_produce.add_argument(
        "--visual-style",
        default="cinematic documentary, photorealistic, shallow depth of field",
        help="Visual aesthetic for OpenArt prompts",
    )
    p_produce.set_defaults(func=cmd_produce)

    # ── setup ────────────────────────────────────────────────────────────────
    p_setup = sub.add_parser("setup", help="Set up your Channel DNA (run once)")
    p_setup.set_defaults(func=cmd_setup)

    # ── workflow (validate + research only) ───────────────────────────────────
    p_workflow = sub.add_parser("workflow", help="Validate + research an idea")
    _add_idea_args(p_workflow)
    p_workflow.set_defaults(func=cmd_workflow)

    # ── validate ──────────────────────────────────────────────────────────────
    p_validate = sub.add_parser("validate", help="Validate and improve a video idea")
    _add_idea_args(p_validate)
    p_validate.set_defaults(func=cmd_validate)

    # ── research ─────────────────────────────────────────────────────────────
    p_research = sub.add_parser("research", help="Research facts and sources for an idea")
    _add_idea_args(p_research)
    p_research.set_defaults(func=cmd_research)

    # ── script ────────────────────────────────────────────────────────────────
    p_script = sub.add_parser(
        "script", help="Generate a video script with retention engineering"
    )
    p_script.add_argument("topic", help="Video topic")
    p_script.add_argument(
        "--duration", type=int, default=10, choices=[3, 5, 7, 10, 15, 20, 30]
    )
    p_script.add_argument(
        "--style", default="educational",
        choices=["educational", "entertainment", "tutorial", "storytime",
                 "review", "vlog", "documentary", "rant"],
    )
    p_script.add_argument("--audience", default="")
    p_script.add_argument("--points", default="", help="Key points, comma-separated")
    p_script.add_argument("--research-file", default="", metavar="FILE")
    p_script.add_argument("--no-feedback", action="store_true")
    p_script.add_argument("--no-project", action="store_true")
    p_script.add_argument("--export-elevenlabs", action="store_true")
    p_script.set_defaults(func=cmd_script)

    # ── revise ────────────────────────────────────────────────────────────────
    p_revise = sub.add_parser(
        "revise", help="Iteratively revise a saved script with targeted feedback"
    )
    p_revise.add_argument("topic", help="Video topic (must have a saved script)")
    p_revise.set_defaults(func=cmd_revise)

    # ── seo ───────────────────────────────────────────────────────────────────
    p_seo = sub.add_parser(
        "seo", help="Generate titles, thumbnail concepts, description, tags, chapters"
    )
    p_seo.add_argument("topic", help="Video topic (must have a saved script)")
    p_seo.set_defaults(func=cmd_seo)

    # ── visuals ───────────────────────────────────────────────────────────────
    p_visuals = sub.add_parser(
        "visuals", help="Generate image + video prompts for OpenArt"
    )
    p_visuals.add_argument("topic", help="Video topic (must have a saved script)")
    p_visuals.add_argument(
        "--style",
        default="cinematic documentary, photorealistic, shallow depth of field",
    )
    p_visuals.add_argument("--chunk", type=int, default=3, choices=[2, 3, 4])
    p_visuals.add_argument("--broll", type=int, default=8)
    p_visuals.add_argument("--output", default="", metavar="FILE")
    p_visuals.set_defaults(func=cmd_visuals)

    # ── export (ElevenLabs) ───────────────────────────────────────────────────
    p_export = sub.add_parser(
        "export", help="Export spoken-only script for ElevenLabs"
    )
    p_export.add_argument("topic", help="Video topic (must have a saved script)")
    p_export.add_argument("--output", default="", metavar="FILE")
    p_export.add_argument("--no-polish", action="store_true")
    p_export.set_defaults(func=cmd_export)

    # ── projects ──────────────────────────────────────────────────────────────
    p_projects = sub.add_parser("projects", help="View and manage video projects")
    proj_sub = p_projects.add_subparsers(dest="project_action")
    proj_sub.add_parser("list", help="List all projects")
    p_pshow = proj_sub.add_parser("show", help="Show project details")
    p_pshow.add_argument("name")
    p_pdel = proj_sub.add_parser("delete", help="Delete a project")
    p_pdel.add_argument("name")
    p_projects.set_defaults(func=cmd_projects, project_action="list")

    # ── vault ─────────────────────────────────────────────────────────────────
    p_vault = sub.add_parser("vault", help="Manage your idea vault")
    vault_sub = p_vault.add_subparsers(dest="vault_action")

    p_vadd = vault_sub.add_parser("add", help="Add an idea")
    p_vadd.add_argument("idea")
    p_vadd.add_argument("--niche", default="")
    p_vadd.add_argument("--tags", default="")

    p_vlist = vault_sub.add_parser("list", help="List vault ideas")
    p_vlist.add_argument("--status", default="")
    p_vlist.add_argument("--tag", default="")

    p_vtag = vault_sub.add_parser("tag", help="Tag an idea by ID")
    p_vtag.add_argument("id", type=int)
    p_vtag.add_argument("--tags", required=True)

    p_vadv = vault_sub.add_parser("advance", help="Advance idea to next pipeline stage")
    p_vadv.add_argument("id", type=int)

    p_vnote = vault_sub.add_parser("note", help="Add a note to a vault idea")
    p_vnote.add_argument("id", type=int)
    p_vnote.add_argument("text")

    p_vault.set_defaults(func=cmd_vault, vault_action="list")

    # ── footage ───────────────────────────────────────────────────────────────
    p_footage = sub.add_parser(
        "footage",
        help="Find real stock footage for your scenes (Pexels, Pixabay, Coverr, etc.)",
    )
    p_footage.add_argument("topic", help="Video topic (must have a saved script)")
    p_footage.set_defaults(func=cmd_footage)

    # ── description ───────────────────────────────────────────────────────────
    p_desc = sub.add_parser(
        "description",
        help="Generate copy-paste YouTube description with SEO, chapters, and keywords",
    )
    p_desc.add_argument("topic", help="Video topic (must have a saved script)")
    p_desc.set_defaults(func=cmd_description)

    # ── learn ─────────────────────────────────────────────────────────────────
    p_learn = sub.add_parser("learn", help="Rebuild learning profile from script feedback")
    p_learn.set_defaults(func=cmd_learn)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n[Interrupted]")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
