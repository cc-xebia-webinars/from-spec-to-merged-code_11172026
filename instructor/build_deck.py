"""Build the webinar slide deck from the Xebia template.

This script is the only way the deck changes. The PPTX in `docs/` is generated from
the SLIDES list below and should never be edited by hand: change the data here,
rebuild, regenerate the PDF, and then update the matching heading in
PRESENTER_SCRIPT.md.

Run from the repository root:

    uv run --with python-pptx python instructor/build_deck.py
    uv run --with python-pptx python instructor/build_deck.py --inventory
    uv run --with python-pptx python instructor/build_deck.py --check-script

Then convert to PDF with LibreOffice, as described in the root CLAUDE.md.
"""

from __future__ import annotations

import argparse
import copy
import io
import re
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "instructor" / "Xebia PPT General Template.pptx"
OUTPUT = ROOT / "docs" / "spec-to-merged-code-slides.pptx"
SCRIPT = ROOT / "instructor" / "PRESENTER_SCRIPT.md"

# Diagrams are drawn with the diagram-builder MCP server. Each .svg in this folder is
# the editable source, and the .png next to it is the export the deck embeds.
DIAGRAMS = ROOT / "instructor" / "diagrams"

# Layout indexes in the Xebia template, named so the slide list below reads clearly.
COVER = 0          # Main-cover_light
BASIC = 6          # Content_Basic
# Content_3 Columns_Comparison. The _2 variant (8) sets white text on full-height color bands,
# and its third band is too pale to read on a shared screen, so the deck uses this one.
THREE_COL = 7
TWO_COL = 9        # Content_2 Columns
BREAK = 24         # 1_Photo_background
END = 27           # End-cover_light

# The template's own body default is 12 pt, which is unreadable on a shared screen,
# so every run gets an explicit size instead of inheriting one.
BULLET_PT = 20
CODE_PT = 18
COLUMN_CODE_PT = 16
COLUMN_BODY_PT = 16
COLUMN_HEADING_PT = 16
SUBTITLE_PT = 16
MONO = "Consolas"

# Density rules from CLAUDE.md, checked against this data before anything is built.
MAX_SLIDES = 20
MAX_BULLETS = 6
MAX_WORDS = 11     # "under a dozen words"
MAX_CODE_LINES = 12

# Column placeholders aren't in left-to-right index order, so each column is named by
# its (heading idx, body idx) pair, measured from the template.
THREE_COL_SLOTS = [(11, 1), (13, 12), (15, 14)]    # left, middle, right
TWO_COL_SLOTS = [(11, 1), (14, 13)]                # left, right

# The two-column layout reserves a band for icon pictures above each column. We don't
# use icons, and once those frames are removed the columns sit alone in the bottom half
# of the slide. Moving them up to the three-column layout's positions closes the gap.
TWO_COL_HEADING_TOP_IN = 2.16
TWO_COL_BODY_TOP_IN = 2.84
TWO_COL_BODY_HEIGHT_IN = 4.06

# Diagram slides fill the body area of the basic layout, under the title.
DIAGRAM_LEFT_IN = 0.61
DIAGRAM_TOP_IN = 1.85
DIAGRAM_MAX_HEIGHT_IN = 5.0
DIAGRAM_MAX_WIDTH_IN = 12.1


# ---------------------------------------------------------------------------- slides
#
# Text wrapped in backticks is set in a monospace font, so method names, file paths
# and code read as code. Everything else is set in the template's Arial.

SLIDES = [
    {
        "kind": "Title",
        "layout": COVER,
        # The line break keeps the title clear of the cover's artwork.
        "title": "From Spec to\nMerged Code",
        "subtitle": ("Running AI Coding Agents as a\nCoordinated Engineering System\n"
                     "Eric Greene · Xebia · eric.greene@xebia.com"),
        "notes": (
            "Welcome and introductions. This is the follow-on to the first session on moving from "
            "autocomplete to agents. Ninety minutes: about twenty of slides and seventy of live "
            "demos, with Claude Code in VS Code's terminal and Copilot on GitHub. Questions are "
            "welcome at any time. Everything is in the webinar repo. Frame: generating code is no "
            "longer the hard part; keeping agents grounded, verified, and affordable is."
        ),
    },
    {
        "kind": "Agenda",
        "layout": BASIC,
        "title": "Agenda",
        "bullets": [
            "What changed in 2026",
            "Spec-driven development and context engineering",
            "Agent teams: coordinator, implementor, and verifier",
            "Autonomous loops and adversarial verification",
            "Closing the loop: review, fix pull requests, and merge",
            "Cost and governance takeaways",
        ],
        "notes": (
            "The README's eight agenda items, grouped into six. One feature, a weekly booking "
            "allowance for Roombook, the codebase from the first session, goes from spec to merged "
            "code across four demos. Demo 1 covers the spec and context, Demo 2 the agent team, "
            "Demo 3 loops, the cloud agent, and verification, and Demo 4 review, merge, and cost."
        ),
    },
    {
        "kind": "Content",
        "layout": BASIC,
        "title": "What changed in 2026",
        "bullets": [
            "Subagents nest, and fleets of them run in parallel",
            "Cloud agents turn issues into draft pull requests",
            "Code review is agentic, with one-click fix PRs",
            "Million-token context windows are the default",
            "Billing moved to tokens: AI Credits and API rates",
        ],
        "notes": (
            "Five shifts since the first session. Claude Code subagents can start subagents of "
            "their own, and Claude Code and Copilot CLI's /fleet run many in parallel. Copilot's "
            "cloud agent and Claude Code on the web turn a task into a PR. Copilot code review "
            "has run on an agentic architecture since March, with Fix with Copilot. Current models "
            "default to a million tokens of context. Copilot moved to AI Credits on 1 June, priced "
            "at token rates, so every agent now has a visible price."
        ),
    },
    {
        "kind": "Content",
        "layout": TWO_COL,
        "title": "The bottleneck moved",
        "columns": [
            ("Generating code", [
                "Cheap, fast, and parallel",
                "Rarely where projects get stuck",
            ]),
            ("What's scarce now", [
                "Grounding: agents working from the same facts",
                "Verification: proof it does what the spec says",
                "Affordability: knowing what each agent costs",
            ]),
        ],
        "notes": (
            "When you can run five agents at once, the limit isn't typing speed. It's whether they "
            "start from the same facts, whether anyone can show the result matches what was asked, "
            "and whether the run was worth what it cost. The rest of the session answers those "
            "three: specs and context for grounding, verifiers and review for verification, and "
            "ledgers and limits for cost."
        ),
    },
    {
        "kind": "Diagram",
        "layout": BASIC,
        "title": "From spec to merge",
        "image": "spec-to-merge.png",
        # Trims the diagram page's empty top and bottom margins, as fractions.
        "crop": (0.28, 0.29),
        "notes": (
            "The workflow for the whole session. A person writes the spec, a skill turns its "
            "criteria into failing tests, plan mode splits the work into slices, the agent team and "
            "a loop build it while a cloud agent works an issue, a verifier checks it and sends "
            "findings back, Copilot reviews it, and a person merges. The orange boxes are where "
            "people decide. The teal bar is the ground truth every agent shares."
        ),
    },
    {
        "kind": "Code",
        "layout": BASIC,
        "title": "An executable spec",
        "code": [
            "3. Ava booking Hudson on Sunday 1 November,",
            "   19:00 to 21:00, is rejected with 409.",
            "",
            "def test_criterion_3_the_week_is_the_offices_local_week(client):",
            "    response = book(client, 6,",
            '        "2026-11-01T19:00", "2026-11-01T21:00")',
            "    assert response.status_code == 409",
            '    assert response.json()["detail"] == ALLOWANCE_MESSAGE',
        ],
        "notes": (
            "Spec-driven development means the spec is the anchor every agent plans and checks "
            "against. It becomes executable when each numbered criterion is a test, written before "
            "the code, with expected values taken from the spec. This criterion is the trap: 19:00 "
            "on Sunday 1 November in New York is already Monday in UTC, so a UTC week gets it "
            "wrong. Once these tests are committed, a hook stops agents from editing them."
        ),
    },
    {
        "kind": "Content",
        "layout": THREE_COL,
        "title": "Context engineering",
        "columns": [
            ("Instruction files", [
                "AGENTS.md for every agent",
                "CLAUDE.md imports it, adds extras",
            ]),
            ("Skills", [
                "Workflows written once, run as commands",
                "Preloaded into the agents that need them",
            ]),
            ("MCP server", [
                "Read-only facts from one source",
                "Every agent asks instead of guessing",
            ]),
        ],
        "notes": (
            "Three ways to give every agent the same ground truth. AGENTS.md is read by Claude Code, "
            "Copilot's cloud agent, and most others. Skills package a workflow, such as turning a "
            "spec into tests, and can be preloaded into a subagent. A small, read-only MCP server "
            "answers questions about the data, the clock changes, and the spec's criteria, so no "
            "agent works facts out in its head. Each person approves a project's server once."
        ),
    },
    {
        "kind": "Demo",
        "layout": BREAK,
        "title": "Demo 1: Ground truth and an executable spec",
        "subtitle": "demos/01-ground-truth · about 15 minutes",
        "notes": (
            "Read AGENTS.md, CLAUDE.md, and the settings. Read facts/server.py and .mcp.json, start "
            "claude, approve the server, /mcp, and ask for Ava's hours: 4.5. Read the spec and point "
            "at criterion 3. Read the spec-to-tests skill and run it: 4 tests fail, 3 pass. Plan "
            "mode against the spec and review the slices. Don't save it; Demo 2 starts from a "
            "reviewed plan."
        ),
    },
    {
        "kind": "Diagram",
        "layout": BASIC,
        "title": "Coordinator, implementor, verifier",
        "image": "agent-team.png",
        "crop": (0.17, 0.24),
        "notes": (
            "The agent team for Demo 2. The coordinator runs on Opus with no edit tools, so all it "
            "can do is split the plan, brief each subagent, and decide when the work is done. "
            "Implementors run on Sonnet with edits accepted automatically, two of them in parallel "
            "on slices that share only a signature. The verifier is read-only. Every agent reads the "
            "same facts server, the same hooks protect the tests, and a ledger records each cost."
        ),
    },
    {
        "kind": "Code",
        "layout": BASIC,
        "title": "Scoping a role in frontmatter",
        "code": [
            "---",
            "name: verifier",
            "description: Checks a change against its spec. Read-only.",
            "tools: Read, Grep, Glob, Bash, mcp__roombook-facts__*",
            "disallowedTools: Edit, Write",
            "model: opus",
            "skills:",
            "  - verify-against-spec",
            "---",
        ],
        "notes": (
            "A subagent is a Markdown file. The frontmatter sets its scope: which tools, which MCP "
            "tools, which model, which skills it starts with, and its permission mode. The body "
            "becomes its instructions. The coordinator's tools line, Agent(implementor, verifier), "
            "is an allowlist of who it can start. For cost, a SubagentStop hook reads each agent's "
            "transcript, prices its tokens, and writes one ledger line per agent."
        ),
    },
    {
        "kind": "Demo",
        "layout": BREAK,
        "title": "Demo 2: An agent team builds the feature",
        "subtitle": "demos/02-agent-team · about 18 minutes",
        "notes": (
            "git init and commit. Read the three agent files, the verify-against-spec skill, the "
            "plan's three slices, and the ledger hook. claude --agent coordinator, then the build "
            "prompt. Watch slices A and B run in parallel, then C, then the verifier. Run the tests "
            "yourself, read the diff, then /usage and the ledger report per agent."
        ),
    },
    {
        "kind": "Content",
        "layout": TWO_COL,
        "title": "Autonomous loops, local and cloud",
        "columns": [
            ("On your machine", [
                "/goal runs until a stated condition holds",
                "Name the check, the limits, the turn cap",
                "Edits flow; most other commands still ask",
            ]),
            ("In the cloud", [
                "Assign an issue; get a draft pull request",
                "The issue is the whole brief",
                "Workflows wait for a person's approval",
            ]),
        ],
        "notes": (
            "Two kinds of unattended work running at once. Locally, /goal keeps Claude working until "
            "a small model judges the condition met. A good condition names the check, what mustn't "
            "change, and a turn limit. Accept-edits mode also lets simple file commands such as rm "
            "and mv through, so the condition checks the tests weren't touched. Stop hooks do the "
            "same with a script, and /loop repeats on a timer. In the cloud, assigning an issue to "
            "Copilot gets a draft PR, but it can't ask questions, so the issue carries everything."
        ),
    },
    {
        "kind": "Content",
        "layout": TWO_COL,
        "title": "What tests can't catch",
        "columns": [
            ("Tests miss", [
                "Scope creep: features nobody asked for",
                "Drift: rules with no acceptance criterion",
                "Broken constraints: a quiet new dependency",
            ]),
            ("A verifier needs", [
                "No stake in the build",
                "The whole spec, not just the criteria",
                "Evidence for every finding",
            ]),
        ],
        "notes": (
            "Tests only check what someone thought to test. Demo 3 starts from a team build where "
            "every test passes and three things are still wrong: an endpoint the spec ruled out, a "
            "rule implemented differently from how it's written, and a new dependency. A verifier "
            "that starts fresh, with a checklist that reads the whole spec, finds them. Each gap it "
            "finds becomes a new test, and each miss a new line in its checklist."
        ),
    },
    {
        "kind": "Demo",
        "layout": BREAK,
        "title": "Demo 3: Loops, a cloud agent, and a second opinion",
        "subtitle": "demos/03-loops-and-verification · about 18 minutes",
        "notes": (
            "git init, commit, gh repo create, create issue 1 and assign it to @copilot. Branch, "
            "copy team-build in, uv sync: 74 pass, 2 fail. Commit. claude in accept-edits mode, "
            "/goal until uv run pytest passes, or 15 turns. Commit. claude --agent verifier finds "
            "the endpoint, pending bookings, and dateutil. You git rm the test, Claude fixes the "
            "code, then you uv remove dateutil: 75 pass. Push, draft PR."
        ),
    },
    {
        "kind": "Content",
        "layout": BASIC,
        "title": "Closing the loop",
        "bullets": [
            "Agent pull requests get the same CI and review",
            "Agentic review reads the repo and your instructions",
            "Findings go back as small fix pull requests",
            "Agents can't approve or merge their own work",
            "A person merges, against a written checklist",
        ],
        "notes": (
            "The last mile is the same for every change. Copilot code review uses tools to read the "
            "repository, follows the review instructions in .github/instructions, and its comments "
            "are comments, not approvals, by default. Fix with Copilot turns a comment into a fix "
            "PR, so each change stays reviewable. GitHub keeps key steps with people: running "
            "workflows on agent pushes, marking ready, approving, and merging."
        ),
    },
    {
        "kind": "Demo",
        "layout": BREAK,
        "title": "Demo 4: Review, fix, merge, and the bill",
        "subtitle": "demos/04-review-and-merge · about 17 minutes",
        "notes": (
            "In the Demo 3 repo. Feature PR first: ready, add reviewer @copilot. While it reviews, "
            "Copilot's PR: View session, Approve and run workflows, checks, ready, merge. Read the "
            "review, Fix with Copilot as a new PR. While it runs, the ledger reports and the AI "
            "usage page. Merge the fix, walk the checklist, merge the feature, pull, test: 76+."
        ),
    },
    {
        "kind": "Content",
        "layout": BASIC,
        "title": "What the run cost",
        "bullets": [
            "Claude: per-agent tokens from transcripts, priced",
            "Copilot: AI Credits at each model's token rates",
            "The cheaper model goes where the most tokens go",
            "Bound every loop: turns, conditions, and budgets",
            "Compare the total with a person's time",
        ],
        "notes": (
            "Read out the totals from your own run: the ledger for Demos 2 and 3, the cloud agent's "
            "sessions, and the review. The implementors read and write the most tokens, so model "
            "choice there moves the bill most. Every loop needs a stopping rule. The useful "
            "comparison isn't zero; it's what the same feature costs in a person's time."
        ),
    },
    {
        "kind": "Content",
        "layout": THREE_COL,
        "title": "Where to draw the autonomy line",
        "columns": [
            ("Agents do alone", [
                "Read, plan, edit, test, iterate",
                "Draft pull requests and review comments",
            ]),
            ("A person approves", [
                "New dependencies and deleted tests",
                "Workflow runs on agents' pushes",
            ]),
            ("Only a person", [
                "Pushing and merging",
                "Changing the spec or the rules",
            ]),
        ],
        "notes": (
            "The demos drew the line this way, in settings, hooks, and platform rules rather than "
            "in prompts. Agents work freely inside the allow list. A new dependency asks first, and "
            "a hook blocks edits to tests; the hook can't see a file deleted from the shell, so CI "
            "is the backstop. Publishing and deciding what the software should do stay with "
            "people. Write your line down, check it in, and review it like code."
        ),
    },
    {
        "kind": "Wrap",
        "layout": BASIC,
        "title": "Next steps",
        "bullets": [
            "Clone the repo and run the four demos",
            "Write one spec with numbered, real-data criteria",
            "Add a read-only facts server for your data",
            "Set up a coordinator, implementors, and a verifier",
            "Start from the starter kit and the checklist",
        ],
        "notes": (
            "Point people to demos/README.md for setup, including the Copilot plan that Demos 3 and "
            "4 need. Suggest one small, real feature with a clear spec rather than a big one. The "
            "starter kit in docs/starter-kit has the agents, skills, hooks, settings, and GitHub "
            "files, and the checklist follows the session's order. Mention the Xebia Academy link."
        ),
    },
    {
        "kind": "Closing",
        "layout": END,
        "title": "Thank you",
        "subtitle": "Eric Greene · Xebia\neric.greene@xebia.com",
        "notes": (
            "Thank the audience. Leave this slide up while you answer any last questions, and "
            "remind them that the slides, demos, checklist, and starter kit are in the repo."
        ),
    },
]


# ---------------------------------------------------------------------- validation

def words(text: str) -> int:
    """Count words the way a reader would: tokens containing a letter or digit."""
    return sum(1 for t in text.replace("`", "").split() if re.search(r"[A-Za-z0-9]", t))


def validate_data(slides: list[dict]) -> list[str]:
    problems = []
    if len(slides) > MAX_SLIDES:
        problems.append(f"{len(slides)} slides, limit is {MAX_SLIDES}")
    for n, s in enumerate(slides, start=1):
        groups = []
        if "bullets" in s:
            groups.append(s["bullets"])
        for _, items in s.get("columns", []):
            groups.append(items)
        total = sum(len(g) for g in groups)
        if total > MAX_BULLETS:
            problems.append(f"slide {n}: {total} bullets, limit is {MAX_BULLETS}")
        for g in groups:
            for b in g:
                if words(b) > MAX_WORDS:
                    problems.append(f"slide {n}: {words(b)} words in {b!r}")
        code_blocks = [s.get("code", [])] + [lines for _, lines in s.get("code_columns", [])]
        for block in code_blocks:
            if len(block) > MAX_CODE_LINES:
                problems.append(f"slide {n}: {len(block)} code lines, limit is {MAX_CODE_LINES}")
        if "image" in s and not (DIAGRAMS / s["image"]).is_file():
            problems.append(f"slide {n}: diagram {s['image']} is missing; export it first")
        if not s.get("notes", "").strip():
            problems.append(f"slide {n}: speaker notes are empty")
    for n in (1, len(slides)):
        if "eric.greene@xebia.com" not in slides[n - 1].get("subtitle", ""):
            problems.append(f"slide {n}: the presenter's email must be on the first and last slides")
    return problems


# ---------------------------------------------------------------------------- build

def add_runs(paragraph, text: str, size: int) -> None:
    """Split on backticks so `code` segments get the monospace font."""
    for i, part in enumerate(text.split("`")):
        if not part:
            continue
        run = paragraph.add_run()
        run.text = part
        run.font.size = Pt(size)
        if i % 2 == 1:
            run.font.name = MONO


def fill_lines(placeholder, lines: list[str], size: int) -> None:
    """Write one paragraph per line, without leaving a stray empty first paragraph."""
    tf = placeholder.text_frame
    tf.clear()
    first = True
    for line in lines:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        add_runs(para, line, size)


def fill_code(placeholder, lines: list[str], size: int) -> None:
    """Write code as unbulleted monospace lines.

    The body placeholder bullets every paragraph, which would put a dot in front of
    each line of code, so each paragraph gets an explicit buNone and no indent.
    """
    tf = placeholder.text_frame
    tf.clear()
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p_pr = para._p.get_or_add_pPr()
        p_pr.set("marL", "0")
        p_pr.set("indent", "0")
        p_pr.insert(0, p_pr.makeelement(qn("a:buNone"), {}))
        run = para.add_run()
        # A non-breaking space keeps blank lines and leading indentation intact.
        run.text = line.replace(" ", " ") if line else " "
        run.font.size = Pt(size)
        run.font.name = MONO


def transparent_png(path: Path) -> io.BytesIO:
    """Make the diagram's white page background transparent.

    The diagram tool exports on solid white, which would cover the template's light
    background artwork. Pillow comes with python-pptx, so no extra dependency is needed.
    """
    img = Image.open(path).convert("RGBA")
    img.putdata([(r, g, b, 0) if min(r, g, b) >= 250 else (r, g, b, a)
                 for r, g, b, a in img.get_flattened_data()])
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out


def add_diagram(slide, image: str, crop: tuple[float, float]) -> None:
    """Place a diagram under the title, scaled to the body area and cropped.

    The diagram tool always exports a full landscape page, so the empty margins above
    and below the drawing are cropped off before the picture is sized.
    """
    top_crop, bottom_crop = crop
    pic = slide.shapes.add_picture(transparent_png(DIAGRAMS / image), Inches(DIAGRAM_LEFT_IN),
                                   Inches(DIAGRAM_TOP_IN))
    pic.crop_top, pic.crop_bottom = top_crop, bottom_crop
    aspect = pic.image.size[0] / (pic.image.size[1] * (1 - top_crop - bottom_crop))
    height = min(DIAGRAM_MAX_HEIGHT_IN, DIAGRAM_MAX_WIDTH_IN / aspect)
    pic.height, pic.width = Inches(height), Inches(height * aspect)


def move(placeholder, *, top: float, height: float | None = None) -> None:
    """Reposition a placeholder vertically, keeping its inherited left and width.

    A slide placeholder inherits its geometry from the layout until it's given its own,
    and python-pptx needs all four values set to write one, so the current left and
    width are carried over explicitly.
    """
    left, width = placeholder.left, placeholder.width
    new_height = Inches(height) if height is not None else placeholder.height
    placeholder.left, placeholder.width = left, width
    placeholder.top, placeholder.height = Inches(top), new_height


def restore_slide_number(slide) -> None:
    """python-pptx skips slide-number placeholders when cloning a layout, but the
    template's own slides carry them, so copy the layout's one across."""
    for lp in slide.slide_layout.placeholders:
        if lp.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER:
            slide.shapes._spTree.append(copy.deepcopy(lp._element))


def remove_unfilled(slide, filled: set[int]) -> None:
    """An unfilled picture placeholder renders as an empty frame, so anything we
    didn't write to is removed rather than left behind."""
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx not in filled:
            ph._element.getparent().remove(ph._element)


def build(output: Path) -> None:
    prs = Presentation(TEMPLATE)
    layouts = prs.slide_masters[0].slide_layouts
    assert len(layouts) == 29, f"template has {len(layouts)} layouts, expected 29"

    # Remove the template's example slides. Layouts, the master and the notes master
    # survive, which is all the deck needs.
    rel_id = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    id_list = prs.slides._sldIdLst
    for sld in list(id_list):
        prs.part.drop_rel(sld.get(rel_id))
        id_list.remove(sld)
    assert len(prs.slides) == 0

    for s in SLIDES:
        slide = prs.slides.add_slide(layouts[s["layout"]])
        ph = {p.placeholder_format.idx: p for p in slide.placeholders}
        filled = {0}
        ph[0].text_frame.text = s["title"]

        if s["layout"] in (COVER, BREAK, END):
            fill_lines(ph[1], s["subtitle"].split("\n"), SUBTITLE_PT)
            filled.add(1)
        elif "columns" in s:
            slots = THREE_COL_SLOTS if s["layout"] == THREE_COL else TWO_COL_SLOTS
            for (head_idx, body_idx), (heading, items) in zip(slots, s["columns"]):
                fill_lines(ph[head_idx], [heading], COLUMN_HEADING_PT)
                fill_lines(ph[body_idx], items, COLUMN_BODY_PT)
                filled.update({head_idx, body_idx})
                if s["layout"] == TWO_COL:
                    move(ph[head_idx], top=TWO_COL_HEADING_TOP_IN)
                    move(ph[body_idx], top=TWO_COL_BODY_TOP_IN,
                         height=TWO_COL_BODY_HEIGHT_IN)
        elif "code_columns" in s:
            for (head_idx, body_idx), (heading, lines) in zip(TWO_COL_SLOTS, s["code_columns"]):
                fill_lines(ph[head_idx], [heading], COLUMN_HEADING_PT)
                fill_code(ph[body_idx], lines, COLUMN_CODE_PT)
                filled.update({head_idx, body_idx})
                move(ph[head_idx], top=TWO_COL_HEADING_TOP_IN)
                move(ph[body_idx], top=TWO_COL_BODY_TOP_IN, height=TWO_COL_BODY_HEIGHT_IN)
        elif "code" in s:
            fill_code(ph[1], s["code"], CODE_PT)
            filled.add(1)
        elif "image" in s:
            add_diagram(slide, s["image"], s["crop"])
        else:
            fill_lines(ph[1], s["bullets"], BULLET_PT)
            filled.add(1)

        remove_unfilled(slide, filled)
        if s["layout"] not in (COVER, END):
            restore_slide_number(slide)
        slide.notes_slide.notes_text_frame.text = s["notes"]

    assert len(prs.slides) == len(SLIDES)
    for n, slide in enumerate(prs.slides, start=1):
        assert slide.notes_slide.notes_text_frame.text.strip(), f"slide {n} has no notes"

    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output)


def inventory() -> str:
    rows = [f"{'#':>2}  {'kind':<8} title"]
    for n, s in enumerate(SLIDES, start=1):
        title = s["title"].replace("\n", " ")
        rows.append(f"{n:>2}  {s['kind']:<8} {title}")
    return "\n".join(rows)


def check_script() -> list[str]:
    """Compare the presenter script's slide headings with the deck, line for line.

    Each slide in PRESENTER_SCRIPT.md has a heading of the form "## Slide N: Title",
    and the titles drift whenever a slide is renamed without updating the script.
    """
    expected = [f"## Slide {n}: {s['title'].replace(chr(10), ' ')}"
                for n, s in enumerate(SLIDES, start=1)]
    text = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
    found = [line.rstrip() for line in text.splitlines() if line.startswith("## Slide ")]
    problems = []
    for i in range(max(len(expected), len(found))):
        want = expected[i] if i < len(expected) else "(no slide)"
        got = found[i] if i < len(found) else "(missing)"
        if want != got:
            problems.append(f"expected {want!r}, found {got!r}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inventory", action="store_true",
                        help="print the slide list and exit, for checking the script against it")
    parser.add_argument("--check-script", action="store_true",
                        help="check PRESENTER_SCRIPT.md's slide headings against the deck and exit")
    args = parser.parse_args()

    if args.inventory:
        print(inventory())
        return 0

    if args.check_script:
        problems = check_script()
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("presenter script matches the deck" if not problems
              else f"{len(problems)} heading(s) don't match", file=sys.stderr if problems else sys.stdout)
        return 1 if problems else 0

    problems = validate_data(SLIDES)
    if problems:
        print("Slide data breaks the rules in CLAUDE.md:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    build(OUTPUT)
    print(f"built {OUTPUT.relative_to(ROOT)} with {len(SLIDES)} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
