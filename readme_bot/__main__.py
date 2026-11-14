"""Entry point:  python -m readme_bot"""

import argparse
import sys
from pathlib import Path

import yaml

from .github_api import GitHubError, get_repos, get_user
from .render import render_readme
from .stats import build_stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a GitHub profile README.")
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--output", default="README.md", help="where to write the README")
    parser.add_argument("--dry-run", action="store_true", help="print instead of writing")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    try:
        user = get_user(config["username"])
        repos = get_repos(config["username"])
    except GitHubError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    stats = build_stats(user, repos, config)
    readme = render_readme(config, user, stats)

    if args.dry_run:
        print(readme)
    else:
        Path(args.output).write_text(readme, encoding="utf-8")
        print(f"Wrote {args.output} ({len(readme.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
