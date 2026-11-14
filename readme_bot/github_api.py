"""Thin wrapper around the GitHub REST API (only what we need)."""

import os

import requests

API = "https://api.github.com"


class GitHubError(RuntimeError):
    """Raised for API problems we can explain in plain words."""


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-readme-bot",
        }
    )
    # A token is optional: unauthenticated calls allow 60 requests/hour,
    # which is plenty for this script. GitHub Actions provides one for free.
    token = os.getenv("GITHUB_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def _get(session: requests.Session, url: str, params: dict | None = None):
    response = session.get(url, params=params, timeout=20)
    if response.status_code == 404:
        raise GitHubError(f"Not found: {url} (check the username in config.yaml)")
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        raise GitHubError("GitHub rate limit reached. Set GITHUB_TOKEN or try again later.")
    if not response.ok:
        raise GitHubError(f"GitHub returned HTTP {response.status_code} for {url}")
    return response.json()


def get_user(username: str) -> dict:
    return _get(_session(), f"{API}/users/{username}")


def get_repos(username: str) -> list[dict]:
    """Return all public repos owned by the user (handles pagination)."""
    session = _session()
    repos: list[dict] = []
    page = 1
    while True:
        batch = _get(
            session,
            f"{API}/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "owner", "sort": "pushed"},
        )
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1
