#!/usr/bin/env python3
"""Gera o card de atividade do perfil a partir da API GraphQL do GitHub."""
import argparse
import json
import os
import pathlib
import urllib.request

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
"""

THEMES = {
    "dark": {"bg": "#071521", "line": "#1B3040", "ink": "#F3F6F8", "muted": "#9BA6AE", "accent": "#31D4CE"},
    "light": {"bg": "#F6F9FB", "line": "#D5DEE6", "ink": "#071521", "muted": "#4F6070", "accent": "#0F7F7B"},
}


def summarize(user):
    calendar = user["contributionsCollection"]["contributionCalendar"]
    counts = [day["contributionCount"] for week in calendar["weeks"] for day in week["contributionDays"]]
    longest = current = 0
    for count in counts:
        current = current + 1 if count else 0
        longest = max(longest, current)
    return [
        (calendar["totalContributions"], "contribuições em 12 meses"),
        (sum(1 for count in counts if count), "dias ativos em 12 meses"),
        (longest, "maior sequência em dias"),
        (user["repositories"]["totalCount"], "repositórios públicos"),
    ]


def render_card(stats, theme):
    colors = THEMES[theme]
    tile_width = 1200 / len(stats)
    tiles = []
    for index, (value, label) in enumerate(stats):
        x = tile_width * index + 40
        tiles.append(
            f'<text x="{x:g}" y="84" font-size="46" font-weight="700" fill="{colors["ink"]}">{value}</text>'
            f'<text x="{x:g}" y="120" font-size="15" fill="{colors["muted"]}">{label}</text>'
        )
        if index:
            tiles.append(
                f'<path d="M{tile_width * index:g} 36V124" stroke="{colors["line"]}"/>'
            )
    description = "; ".join(f"{label}: {value}" for value, label in stats)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 160" width="1200" height="160" '
        f'role="img" aria-label="{description}">'
        "<style>text{font-family:'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,"
        "Consolas,'DejaVu Sans Mono',monospace}</style>"
        f'<rect x=".5" y=".5" width="1199" height="159" rx="15.5" fill="{colors["bg"]}" stroke="{colors["line"]}"/>'
        f'<rect x="40" y="0" width="64" height="3" fill="{colors["accent"]}"/>'
        + "".join(tiles)
        + "</svg>\n"
    )


def fetch_user(login, token):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", required=True)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    stats = summarize(fetch_user(args.login, os.environ["GITHUB_TOKEN"]))
    args.out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (args.out / f"activity-{theme}.svg").write_text(render_card(stats, theme), encoding="utf-8")


if __name__ == "__main__":
    main()
