"""Render the story in content/game.txt into portfolio/game/index.html (run by the Pages workflow).

Text format, one entry per line (blank lines are ignored):
  # Title                    game name
  > Text                     small line above the title
  Text                       paragraph: in the hero before the first chapter, in the chapter
                             before its first card, otherwise in the current card
  ## Heading                 story chapter, numbered automatically
  ## Heading | layers        chapter whose cards stack from the top of the world to the bottom
  ## Heading | progress      development progress (not numbered)
  ### Icon | Title           card in the current chapter (the icon is optional)
  - done: Title — details    progress step; the status is done, now or next
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content" / "game.txt"
PAGE = ROOT / "portfolio" / "game" / "index.html"
MARKERS = re.compile(r"(<!-- game:start -->).*?(<!-- game:end -->)", re.S)
KINDS = ("story", "layers", "progress")
STATUSES = {"done": "Done", "now": "In progress", "next": "Planned"}


def esc(text):
    return html.escape(text, quote=False)


def fail(message, number=None):
    where = f"{SOURCE.name}:{number}: " if number else ""
    sys.exit(f"build_game: {where}{message}")


def split_pipe(text):
    left, sep, right = text.partition(" | ")
    return (left.strip(), right.strip()) if sep else ("", text.strip())


def parse(text):
    page = {"title": "", "kicker": "", "intro": [], "chapters": []}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        chapter = page["chapters"][-1] if page["chapters"] else None
        if not line:
            continue
        if line.startswith("### "):
            if not chapter or chapter["kind"] == "progress":
                fail("a '### ' card needs a story or layers chapter above it", number)
            icon, title = split_pipe(line[4:])
            chapter["cards"].append({"icon": icon, "title": title, "text": []})
        elif line.startswith("## "):
            title, kind = line[3:].partition(" | ")[::2]
            kind = kind.strip() or "story"
            if kind not in KINDS:
                fail(f"unknown chapter type '{kind}' (use {', '.join(KINDS[1:])})", number)
            page["chapters"].append({"title": title.strip(), "kind": kind, "text": [], "cards": [], "steps": []})
        elif line.startswith("# "):
            page["title"] = line[2:]
        elif line.startswith("> "):
            page["kicker"] = line[2:]
        elif line.startswith("- "):
            status, sep, rest = line[2:].partition(": ")
            if not chapter or chapter["kind"] != "progress" or not sep or status not in STATUSES:
                fail("'- status: ...' steps belong in a progress chapter (status: done, now or next)", number)
            title, _, details = rest.partition(" — ")
            chapter["steps"].append({"status": status, "title": title, "text": details})
        elif not chapter:
            page["intro"].append(line)
        elif chapter["cards"]:
            chapter["cards"][-1]["text"].append(line)
        else:
            chapter["text"].append(line)
    if not page["title"] or not page["chapters"]:
        fail("needs a '# ' title and at least one '## ' chapter")
    return page


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def paragraphs(lines, indent):
    return [f"{indent}<p>{esc(line)}</p>" for line in lines]


def render_card(card, kind):
    icon = f'<span class="game-icon" aria-hidden="true">{esc(card["icon"])}</span>' if card["icon"] else ""
    if kind == "layers":
        return [
            f'        <li class="game-layer">{icon}<div>',
            f'          <h3>{esc(card["title"])}</h3>',
            *paragraphs(card["text"], "          "),
            "        </div></li>",
        ]
    return [
        f'        <article class="game-card">{icon}',
        f'          <h3>{esc(card["title"])}</h3>',
        *paragraphs(card["text"], "          "),
        "        </article>",
    ]


def render_step(step):
    return [
        f'        <li class="game-step is-{step["status"]}">',
        f'          <span class="game-step-status">{STATUSES[step["status"]]}</span>',
        f'          <h3>{esc(step["title"])}</h3>',
        *paragraphs([step["text"]] if step["text"] else [], "          "),
        "        </li>",
    ]


def render(page):
    chapters = page["chapters"]
    out = [
        '<header class="game-hero" id="top">',
        '  <div class="container">',
        f'    <p class="game-kicker">{esc(page["kicker"])}</p>' if page["kicker"] else "",
        f'    <h1 class="game-title">{esc(page["title"])}</h1>',
        *(f'    <p class="game-tagline">{esc(p)}</p>' for p in page["intro"]),
        '    <div class="hero-actions">',
        '      <a href="#story" class="btn btn-primary">Read the Story</a>',
        '      <a href="#support" class="btn btn-outline" data-support>Show Some Support</a>',
        "    </div>",
        "  </div>",
        "</header>",
        '<div id="story">',
    ]
    number = 0
    for i, chapter in enumerate(chapters):
        kind = chapter["kind"]
        if kind == "progress":
            label = "Where It Stands"
        else:
            number += 1
            label = f"Chapter {number}"
        # Alternate backgrounds, ending shaded so the plain support section after the story stands apart
        alt = " section-alt" if (len(chapters) - i) % 2 else ""
        anchor = "progress" if kind == "progress" else slug(chapter["title"])
        out += [
            f'<section class="section game-chapter{alt}" id="{anchor}">',
            '  <div class="container">',
            f'    <p class="game-chapter-label">{label}</p>',
            f'    <h2 class="game-chapter-title">{esc(chapter["title"])}</h2>',
            '    <div class="game-prose">',
            *paragraphs(chapter["text"], "      "),
            "    </div>",
        ]
        if kind == "progress":
            steps = chapter["steps"]
            if not steps:
                fail(f"progress chapter '{chapter['title']}' has no '- status: ...' steps")
            done = sum(step["status"] == "done" for step in steps)
            out += [
                f'    <div class="game-meter" role="img" aria-label="{done} of {len(steps)} milestones done">'
                f'<span style="width:{round(100 * done / len(steps))}%"></span></div>',
                f'    <p class="game-meter-label">{done} of {len(steps)} milestones done</p>',
                '    <ol class="game-progress">',
                *(line for step in steps for line in render_step(step)),
                "    </ol>",
            ]
        elif chapter["cards"]:
            tag = "ol" if kind == "layers" else "div"
            css = "game-layers" if kind == "layers" else "game-cards"
            out += [
                f'    <{tag} class="{css}">',
                *(line for card in chapter["cards"] for line in render_card(card, kind)),
                f"    </{tag}>",
            ]
        out += ["  </div>", "</section>"]
    out.append("</div>")
    return "\n".join(line for line in out if line)


def main():
    page = PAGE.read_text(encoding="utf-8")
    if not MARKERS.search(page):
        fail(f"{PAGE.relative_to(ROOT)} is missing the game:start / game:end markers")
    content = render(parse(SOURCE.read_text(encoding="utf-8")))
    PAGE.write_text(MARKERS.sub(lambda m: f"{m[1]}\n{content}\n{m[2]}", page), encoding="utf-8")
    print(f"build_game: rendered {SOURCE.relative_to(ROOT)} into {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
