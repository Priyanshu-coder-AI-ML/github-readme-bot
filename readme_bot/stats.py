"""Turn raw GitHub API data into the numbers the README template needs."""

from collections import Counter


def build_stats(user: dict, repos: list[dict], config: dict) -> dict:
    exclude = {name.lower() for name in config.get("exclude_repos", [])}
    profile_repo = user["login"].lower()  # the special username/username repo

    own = [
        r
        for r in repos
        if not r["fork"]
        and not r["archived"]
        and r["name"].lower() not in exclude
        and r["name"].lower() != profile_repo
    ]

    # Language share, counted by each repo's main language.
    counts = Counter(r["language"] for r in own if r["language"])
    total = sum(counts.values()) or 1
    languages = [
        {"name": name, "count": count, "percent": round(count * 100 / total, 1)}
        for name, count in counts.most_common(config.get("top_languages", 6))
    ]

    top_n = config.get("top_repos", 6)
    top_repos = sorted(
        own, key=lambda r: (r["stargazers_count"], r["pushed_at"]), reverse=True
    )[:top_n]
    recent_repos = sorted(own, key=lambda r: r["pushed_at"], reverse=True)[:5]

    return {
        "repo_count": len(own),
        "total_stars": sum(r["stargazers_count"] for r in own),
        "followers": user["followers"],
        "languages": languages,
        "top_repos": top_repos,
        "recent_repos": recent_repos,
    }
