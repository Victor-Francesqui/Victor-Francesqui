#!/usr/bin/env python3
"""Coloca a animação gerada pelo Platane/snk num painel com o tema Matrix."""
import argparse
import pathlib
import random
import re

WIDTH = 1200
GRID_WIDTH = 1100
GRID_TOP = 58
SLOWDOWN = 1.5
BG, LINE, NEON, DEEP, INK, MUTED = "#020805", "#14432A", "#39FF6A", "#12A63F", "#EFFFF4", "#A5D0B2"
PALETTE = {
    "--cb": LINE,
    "--cs": NEON,
    "--ce": "#07180D",
    "--c0": "#07180D",
    "--c1": "#0F5A26",
    "--c2": DEEP,
    "--c3": "#25D457",
    "--c4": NEON,
}
FONT = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Consolas,'DejaVu Sans Mono',monospace"


def rain(height):
    rng = random.Random(1999)
    alphabet = "0123456789ABCDEFXZ:.=*+|"
    columns = []
    for x in range(14, WIDTH, 46):
        chars = "".join(rng.choice(alphabet) for _ in range(12))
        ys = " ".join(str(n * 14) for n in range(12))
        xs = " ".join("0" for _ in range(12))
        duration = rng.uniform(12, 24)
        columns.append(
            f'<g transform="translate({x} {rng.randrange(0, 60)})"><text x="{xs}" y="{ys}" font-size="12" fill="url(#rainFade)" class="rain" '
            f'style="animation-duration:{duration:.1f}s;animation-delay:-{rng.uniform(0, duration):.1f}s">{chars}</text></g>'
        )
    return "".join(columns)


def legend(height):
    x = WIDTH - 262
    y = 32
    squares = "".join(
        f'<rect x="{x + 48 + i * 18}" y="{y - 11}" width="13" height="13" rx="2" fill="{color}" stroke="{LINE}"/>'
        for i, color in enumerate((PALETTE["--c0"], PALETTE["--c1"], PALETTE["--c2"], PALETTE["--c3"], PALETTE["--c4"]))
    )
    return (
        f'<text x="{x}" y="{y}" font-size="13" fill="{MUTED}">menos</text>{squares}'
        f'<text x="{x + 146}" y="{y}" font-size="13" fill="{MUTED}">mais</text>'
    )


def theme(source):
    root = re.search(r'<svg viewBox="([-\d. ]+)" width="([\d.]+)" height="([\d.]+)"[^>]*>', source)
    if not root or not source.rstrip().endswith("</svg>"):
        raise ValueError("formato inesperado do SVG do snk")
    if ":root{" not in source:
        raise ValueError("o SVG do snk não define a paleta em :root")
    view_box, width, height = root.group(1), float(root.group(2)), float(root.group(3))
    inner = source[root.end(): source.rstrip().rfind("</svg>")]
    colors = ";".join(f"{name}:{value}" for name, value in PALETTE.items())
    inner = re.sub(r":root\{[^}]*\}", ":root{" + colors + "}", inner, count=1)
    inner = re.sub(r"(\d+)ms", lambda m: f"{round(int(m.group(1)) * SLOWDOWN)}ms", inner)
    grid_height = GRID_WIDTH * height / width
    total = round(GRID_TOP + grid_height + 14)
    corners = (
        f"M8 44V24L24 8H80M{WIDTH - 80} 8H{WIDTH - 24}L{WIDTH - 8} 24V44"
        f"M{WIDTH - 8} {total - 36}V{total - 24}L{WIDTH - 24} {total - 8}H{WIDTH - 80}"
        f"M80 {total - 8}H24L8 {total - 24}V{total - 36}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {total}" width="{WIDTH}" height="{total}" role="img" '
        'aria-label="Painel com tema Matrix: uma cobrinha verde neon percorre o gráfico de contribuições do GitHub e come as contribuições.">'
        f'<defs><linearGradient id="rainFade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{NEON}" stop-opacity="0"/><stop offset="1" stop-color="{NEON}" stop-opacity=".32"/></linearGradient>'
        f'<clipPath id="panel"><rect width="{WIDTH}" height="{total}" rx="14"/></clipPath></defs>'
        f"<style>text{{font-family:{FONT}}}"
        ".rain{animation:rain 18s linear infinite}@keyframes rain{from{transform:translateY(-240px)}to{transform:translateY(420px)}}"
        ".edge{animation:edge 3.6s ease-in-out infinite}@keyframes edge{50%{opacity:.5}}"
        ".cursor{animation:cur 1s step-end infinite}@keyframes cur{50%{opacity:0}}"
        f".s{{filter:drop-shadow(0 0 3px {NEON})}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>"
        f'<g clip-path="url(#panel)"><rect width="{WIDTH}" height="{total}" fill="{BG}"/>{rain(total)}'
        f'<text x="40" y="32" font-size="15" fill="{INK}"><tspan fill="{NEON}">$</tspan><tspan dx="9">./snake --contribuicoes</tspan><tspan fill="{NEON}" dx="5" class="cursor">_</tspan></text>'
        f"{legend(total)}"
        f'<svg x="{(WIDTH - GRID_WIDTH) / 2:g}" y="{GRID_TOP}" width="{GRID_WIDTH}" height="{grid_height:g}" viewBox="{view_box}">{inner}</svg>'
        f'<path d="M1 1H{WIDTH - 1}V{total - 1}H1Z" fill="none" stroke="{LINE}" stroke-width="2"/>'
        f'<path d="{corners}" fill="none" stroke="{NEON}" stroke-width="3" class="edge"/></g></svg>\n'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    args.output.write_text(theme(args.input.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
