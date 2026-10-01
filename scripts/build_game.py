"""Render content/game.txt into portfolio/game/index.html (run by the Pages workflow).

Text format, one entry per line (blank lines are ignored):
  # Title         page title
  > Text          intro paragraph
  ## Heading      section
  ### Heading     card inside the current section
  - Key: value    card item; the key before ": " is shown in bold (the "- " is optional)
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content" / "game.txt"
PAGE = ROOT / "portfolio" / "game" / "index.html"
MARKERS = re.compile(r"(<!-- game:start -->).*?(<!-- game:end -->)", re.S)

esc = html.escape


def fail(message):
    sys.exit(f"build_game: {message}")


def parse(text):
    title, intro, sections = "", [], []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("### "):
            if not sections:
                fail(f"{SOURCE.name}:{number}: card '{line}' needs a '## ' section above it")
            sections[-1]["cards"].append({"title": line[4:], "items": []})
        elif line.startswith("## "):
            sections.append({"title": line[3:], "cards": []})
        elif line.startswith("# "):
            title = line[2:]
        elif line.startswith("> "):
            intro.append(line[2:])
        elif sections and sections[-1]["cards"]:
            sections[-1]["cards"][-1]["items"].append(line.removeprefix("- "))
        else:
            fail(f"{SOURCE.name}:{number}: '{line}' must be inside a '### ' card")
    if not title:
        fail(f"{SOURCE.name}: missing '# ' title")
    return title, intro, sections


def item(text):
    key, sep, value = text.partition(": ")
    if sep and len(key) <= 40:
        return f"<li><strong>{esc(key)}:</strong> {esc(value)}</li>"
    return f"<li>{esc(text)}</li>"


def render(title, intro, sections):
    out = [
        '<header class="svc-hero" id="top">',
        '  <div class="container">',
        '    <p class="hero-greeting">Game in Development</p>',
        f'    <h1 class="hero-name">{esc(title)}</h1>',
        *(f'    <p class="svc-lead">{esc(p)}</p>' for p in intro),
        "  </div>",
        "</header>",
    ]
    for i, section in enumerate(sections):
        # Alternate backgrounds so the last section is plain and the support section after it is shaded
        alt = " section-alt" if (len(sections) - 1 - i) % 2 else ""
        slug = re.sub(r"[^a-z0-9]+", "-", section["title"].lower()).strip("-")
        out += [
            f'<section class="section{alt}" id="{slug}">',
            '  <div class="container">',
            f'    <h2 class="section-title">{esc(section["title"])}</h2>',
            '    <div class="projects-grid game-grid">',
        ]
        for card in section["cards"]:
            out += [
                '      <article class="project-card">',
                '        <div class="project-info">',
                f'          <h3 class="project-title">{esc(card["title"])}</h3>',
                '          <ul class="game-list">',
                *(f"            {item(text)}" for text in card["items"]),
                "          </ul>",
                "        </div>",
                "      </article>",
            ]
        out += ["    </div>", "  </div>", "</section>"]
    return "\n".join(out)


def main():
    page = PAGE.read_text(encoding="utf-8")
    if not MARKERS.search(page):
        fail(f"{PAGE.relative_to(ROOT)} is missing the game:start / game:end markers")
    content = render(*parse(SOURCE.read_text(encoding="utf-8")))
    PAGE.write_text(MARKERS.sub(lambda m: f"{m[1]}\n{content}\n{m[2]}", page), encoding="utf-8")
    print(f"build_game: rendered {SOURCE.relative_to(ROOT)} into {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
