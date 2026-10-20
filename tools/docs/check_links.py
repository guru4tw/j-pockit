"""Link gate for docs/workflow.md and docs/workflow.htm.

    python tools/docs/check_links.py

Fails (exit 1) when:
- a #link has no matching anchor (dangling)
- a glossary (g-) or skill (s-) anchor is never linked (orphan)
- a relative file link points to a missing file
- workflow.htm is not pure ASCII, or its ids / #hrefs differ from the md
"""
import pathlib, re, sys

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"


def main():
    md = (DOCS / "workflow.md").read_text(encoding="utf-8")
    fences = re.compile(r"```.*?```", re.S)
    md_nocode = fences.sub("", md)
    ids = set(re.findall(r'<a id="([^"]+)"></a>', md_nocode))
    hrefs = set(re.findall(r"\]\(#([^)]+)\)", md_nocode))
    problems = []
    dangling = sorted(hrefs - ids)
    orphan = sorted(i for i in ids - hrefs if i.startswith(("g-", "s-")))
    if dangling:
        problems.append("md dangling: %s" % dangling)
    if orphan:
        problems.append("md orphan: %s" % orphan)
    for rel in re.findall(r"\]\(([^#)][^)]*)\)", md_nocode):
        if not rel.startswith("http") and not (DOCS / rel.split("#")[0]).exists():
            problems.append("md missing file: %s" % rel)

    raw = (DOCS / "workflow.htm").read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append("htm has BOM")
    if any(b > 127 for b in raw):
        problems.append("htm not pure ASCII")
    htm = raw.decode("ascii", "replace")
    hid = set(re.findall(r'\bid="([^"]+)"', htm))
    hhref = set(re.findall(r'href="#([^"]+)"', htm))
    if hhref - hid:
        problems.append("htm dangling: %s" % sorted(hhref - hid))
    if ids - hid:
        problems.append("htm missing md anchors: %s" % sorted(ids - hid))

    for p in problems:
        print("FAIL", p)
    if not problems:
        print("links ok: %d anchors, %d targets linked" % (len(ids), len(hrefs)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
