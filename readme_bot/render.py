"""Render the README from a Jinja2 template."""

from datetime import date
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _bar(percent: float, width: int = 20) -> str:
    """Text progress bar, e.g. ████████░░░░░░░░░░░░"""
    filled = round(percent / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _badge(skill: dict) -> str:
    """Markdown image for a shields.io skill badge."""
    label = quote(skill["name"].replace("-", "--").replace("_", "__"))
    color = skill.get("color", "555555").lstrip("#")
    url = f"https://img.shields.io/badge/{label}-{color}?style=for-the-badge"
    if skill.get("logo"):
        url += f"&logo={quote(skill['logo'])}&logoColor=white"
    return f"![{skill['name']}]({url})"


def render_readme(config: dict, user: dict, stats: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["bar"] = _bar
    env.filters["badge"] = _badge
    template = env.get_template("profile.md.j2")
    return template.render(
        config=config,
        user=user,
        stats=stats,
        # Date only (no time) so the file changes at most once a day.
        updated=date.today().isoformat(),
    )
