#!/usr/bin/env python3
"""Keep one SKILL.md router in sync with a graph of Markdown modules.

Every Markdown file below ``skill/`` is a node and every relative Markdown
link is a directed edge. Only the marked catalog in SKILL.md is regenerated;
hand-written instructions outside the markers remain untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


START = "<!-- BEGIN AUTO-GENERATED SKILL GRAPH -->"
END = "<!-- END AUTO-GENERATED SKILL GRAPH -->"
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
SUMMARY_RE = re.compile(r"<!--\s*graph-summary:\s*(.*?)\s*-->", re.I)


@dataclass(frozen=True)
class Node:
    path: Path
    relative: Path
    title: str
    summary: str


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if end >= 0 else text


def plain_text(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def infer_summary(text: str, title: str) -> str:
    override = SUMMARY_RE.search(text)
    if override:
        return plain_text(override.group(1))

    body = TITLE_RE.sub("", strip_frontmatter(text), count=1)
    for paragraph in re.split(r"\n\s*\n", body):
        lines = [line.strip() for line in paragraph.splitlines()]
        first = next((line for line in lines if line), "")
        if not first or first.startswith(("```", "|", "#", "*Production prompt")):
            continue
        summary = plain_text(" ".join(lines))
        if summary:
            return summary[:177] + "..." if len(summary) > 180 else summary
    return f"Detailed guidance for {plain_text(title)}."


def discover(module_dir: Path) -> list[Node]:
    nodes: list[Node] = []
    for path in sorted(module_dir.rglob("*.md"), key=lambda item: item.as_posix().lower()):
        text = path.read_text(encoding="utf-8")
        match = TITLE_RE.search(strip_frontmatter(text))
        title = plain_text(match.group(1)) if match else path.stem.replace("-", " ").title()
        nodes.append(Node(path, path.relative_to(module_dir), title, infer_summary(text, title)))
    return nodes


def group_name(relative: Path) -> str:
    if len(relative.parts) == 1:
        return "Core operations"
    return relative.parts[0].replace("-", " ").title()


def render_catalog(nodes: list[Node], skill_file: Path) -> str:
    grouped: dict[str, list[Node]] = {}
    for node in nodes:
        grouped.setdefault(group_name(node.relative), []).append(node)

    lines = [START, "", "Every linked file is a graph node. Follow links inside a node only when relevant."]
    priority = {"Core operations": 0, "Voice Agents": 1, "Simulations": 2}
    for group in sorted(grouped, key=lambda name: (priority.get(name, 99), name.lower())):
        members = grouped[group]
        lines.extend(("", f"### {group}", ""))
        for node in members:
            target = node.path.relative_to(skill_file.parent).as_posix()
            lines.append(f"- [{node.title}]({target}) — {node.summary}")
    lines.extend(("", END))
    return "\n".join(lines)


def replace_catalog(text: str, catalog: str) -> str:
    if START not in text or END not in text:
        raise ValueError(f"SKILL.md must contain graph markers {START!r} and {END!r}")
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    return before.rstrip() + "\n\n" + catalog + "\n" + after.lstrip("\n")


def local_link_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    candidate = (source.parent / unquote(parsed.path)).resolve()
    if candidate.is_dir():
        for index in ("SKILL.md", "README.md"):
            if (candidate / index).exists():
                return (candidate / index).resolve()
    return candidate


def validate_links(files: list[Path], allowed_root: Path) -> list[str]:
    errors: list[str] = []
    root = allowed_root.resolve()
    for source in files:
        for raw_target in LINK_RE.findall(source.read_text(encoding="utf-8")):
            target = local_link_target(source, raw_target)
            if target is None:
                continue
            try:
                target.relative_to(root)
            except ValueError:
                continue  # A link outside the pack is not a graph edge.
            if not target.exists():
                errors.append(f"{source}: broken local link {raw_target!r}")
    return errors


def run(skill_root: Path, check: bool) -> int:
    skill_root = skill_root.resolve()
    skill_file = skill_root / "SKILL.md"
    module_dir = skill_root / "skill"
    if not skill_file.is_file() or not module_dir.is_dir():
        print(f"error: expected {skill_file} and directory {module_dir}", file=sys.stderr)
        return 2

    nodes = discover(module_dir)
    if not nodes:
        print(f"error: no Markdown nodes found below {module_dir}", file=sys.stderr)
        return 2

    current = skill_file.read_text(encoding="utf-8")
    expected = replace_catalog(current, render_catalog(nodes, skill_file))
    errors = validate_links([skill_file, *(node.path for node in nodes)], skill_root)

    if check:
        if current != expected:
            errors.append(f"{skill_file}: generated graph catalog is out of date")
    elif current != expected:
        skill_file.write_text(expected, encoding="utf-8")
        print(f"updated {skill_file} with {len(nodes)} nodes")
    else:
        print(f"already up to date: {len(nodes)} nodes")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"validated {len(nodes)} nodes and their local Markdown links")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", nargs="?", type=Path, default=Path("skills/callkaro"))
    parser.add_argument("--check", action="store_true", help="fail instead of updating an out-of-date catalog")
    args = parser.parse_args()
    return run(args.skill_root, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
