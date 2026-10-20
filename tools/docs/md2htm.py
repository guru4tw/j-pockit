"""Build docs/workflow.htm from docs/workflow.md (the md file is the source).

    python tools/docs/md2htm.py

- Supports only the markdown subset workflow.md uses: headings with a preceding
  <a id="..."></a>, paragraphs, > quotes, - / 1. lists (nested only in the Agenda),
  tables, ``` fences, --- rules, and ![..](x.svg) images.
- Images are replaced by the inline diagram from gen_flow.build(), so skill names
  in the figure link inside the page.
- Output is pure ASCII: every non-ASCII char becomes &#xNNNN; (ASCII armor),
  so the file survives any code page.
- Runs check_links.py at the end; a failed check exits non-zero.
"""
import html, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen_flow  # noqa: E402
import check_links  # noqa: E402

DOCS = HERE.parents[1] / "docs"

CSS = """body { font-family: -apple-system, "Segoe UI", "Microsoft JhengHei", sans-serif; max-width: 1100px; margin: 2em auto; padding: 0 1.5em; line-height: 1.65; color: #222; background: #fff; }
h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
h2 { border-bottom: 1px solid #aaa; padding-bottom: 0.2em; margin-top: 2em; }
h3 { color: #444; margin-top: 1.5em; }
a { color: #06c; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #bbb; padding: 0.5em 0.8em; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
code { background: #f4f4f4; padding: 0.1em 0.4em; border-radius: 3px; font-family: Consolas, monospace; font-size: 0.92em; }
pre { background: #f7f7f7; border-left: 3px solid #888; padding: 0.8em 1em; overflow-x: auto; }
blockquote { border-left: 4px solid #5b9; padding: 0.4em 1em; background: #f0f8f4; color: #335; margin: 1em 0; }
ul li { margin: 0.3em 0; }
a.gloss { border-bottom: 1px dotted #06c; text-decoration: none; }
a.skill { text-decoration: none; border-bottom: 1px solid #c88a5a; }
sup.cite { font-size: 0.75em; }
sup.cite a { color: #06c; text-decoration: none; font-weight: bold; }
tr:target, h2:target, h3:target { background: #fff3c4; }
@media (prefers-color-scheme: dark) {
  body { color: #e6e6e6; background: #1e1e1e; }
  h1 { border-bottom-color: #888; color: #f5f5f5; }
  h2 { border-bottom-color: #555; color: #f0f0f0; }
  h3 { color: #d0d0d0; }
  a { color: #6cb6ff; }
  th, td { border-color: #555; }
  th { background: #2d2d2d; color: #f0f0f0; }
  code { background: #2d2d2d; color: #f0e090; }
  pre { background: #252525; border-left-color: #888; color: #e6e6e6; }
  blockquote { background: #1e2a26; border-left-color: #5b9; color: #cfd8d4; }
  a.gloss { border-bottom-color: #6cb6ff; }
  sup.cite a { color: #6cb6ff; }
  tr:target, h2:target, h3:target { background: #4a3f10; }
}"""


def enc(s):
    return "".join(c if ord(c) < 128 else "&#x%X;" % ord(c) for c in s)


def link(text_html, href):
    cls = ""
    if href.startswith("#g-"):
        cls = ' class="gloss"'
    elif href.startswith("#s-"):
        cls = ' class="skill"'
    return '<a%s href="%s">%s</a>' % (cls, href, text_html)


INLINE = re.compile(
    r'<a id="([^"]+)"></a>'
    r'|<sup>\[\[(\d+)\]\]\(#ref-\d+\)</sup>'
    r'|\[`([^`]+)`\]\(([^)]+)\)'
    r'|\[([^\]]+)\]\(([^)]+)\)'
    r'|`([^`]+)`'
    r'|\*\*([^*]+)\*\*'
)


def inline(s):
    out, pos = [], 0
    for m in INLINE.finditer(s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        g = m.groups()
        if g[0]:
            out.append('<a id="%s"></a>' % g[0])
        elif g[1]:
            out.append('<sup class="cite">[<a href="#ref-%s">%s</a>]</sup>' % (g[1], g[1]))
        elif g[2]:
            out.append("<code>%s</code>" % link(html.escape(g[2]), g[3]))
        elif g[4]:
            out.append(link(inline(g[4]), g[5]))
        elif g[6]:
            out.append("<code>%s</code>" % html.escape(g[6]))
        else:
            out.append("<strong>%s</strong>" % inline(g[7]))
        pos = m.end()
    out.append(html.escape(s[pos:], quote=False))
    return "".join(out).replace("    ", " &nbsp;&nbsp; ")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


def nested_list(lines):
    """Agenda: '- x' with two-space indent per level."""
    out, depth = [], -1
    for ln in lines:
        d = (len(ln) - len(ln.lstrip(" "))) // 2
        item = inline(ln.strip()[2:])
        if d > depth:
            out.append("<ul>" if depth >= 0 else '<ul style="line-height:1.9;">')
        else:
            out.append("</li>")
            while depth > d:
                out.append("</ul></li>")
                depth -= 1
        out.append("<li>" + item)
        depth = d
    out.append("</li>")
    while depth > 0:
        out.append("</ul></li>")
        depth -= 1
    out.append("</ul>")
    return "\n".join(out)


def convert(lines, svgs):
    out, i, pending_id, fig_open, in_agenda = [], 0, None, False, False
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r'<a id="([^"]+)"></a>$', s)
        if m:
            pending_id = m.group(1); i += 1; continue
        if not s:
            i += 1; continue
        if fig_open and not s.startswith("圖 "):
            out.append("</figure>"); fig_open = False
        h = re.match(r"(#{1,4}) (.*)", s)
        if h:
            lv = len(h.group(1))
            idattr = ' id="%s"' % pending_id if pending_id else ""
            in_agenda = pending_id == "sec-agenda"
            out.append("<h%d%s>%s</h%d>" % (lv, idattr, inline(h.group(2)), lv))
            pending_id = None; i += 1; continue
        if s == "---":
            out.append("<hr>"); i += 1; continue
        im = re.match(r"!\[[^\]]*\]\(([^)]+)\)$", s)
        if im:
            out.append('<figure style="margin: 1.2em 0; text-align: center;">')
            out.append(svgs[im.group(1)].strip())
            fig_open = True; i += 1; continue
        if fig_open:
            out.append("<figcaption>%s</figcaption>" % inline(s))
            out.append("</figure>"); fig_open = False; i += 1; continue
        if s.startswith("```"):
            j, body = i + 1, []
            while not lines[j].strip().startswith("```"):
                body.append(lines[j]); j += 1
            out.append("<pre>%s</pre>" % html.escape("\n".join(body), quote=False))
            i = j + 1; continue
        if s.startswith(">"):
            body = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                body.append(lines[i].strip()[1:].strip()); i += 1
            text = " ".join(body)
            if "(workflow.htm)" not in text:  # the md-only "this is the GitHub copy" note
                out.append("<blockquote>%s</blockquote>" % inline(text))
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            out.append("<table>")
            out.append("<tr>" + "".join("<th>%s</th>" % inline(c) for c in cells(rows[0])) + "</tr>")
            for r in rows[2:]:
                cs = cells(r)
                rid = re.match(r'<a id="(s-[^"]+)"></a>', cs[0])
                if rid:  # skill rows: put the anchor on the row so :target highlights it
                    cs[0] = cs[0][rid.end():]
                    out.append('<tr id="%s">' % rid.group(1) + "".join("<td>%s</td>" % inline(c) for c in cs) + "</tr>")
                else:
                    out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in cs) + "</tr>")
            out.append("</table>")
            continue
        if s.startswith("- "):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                block.append(lines[i].rstrip()); i += 1
            if in_agenda:
                out.append("<nav>\n" + nested_list(block) + "\n</nav>")
            else:
                out.append("<ul>\n" + "\n".join("<li>%s</li>" % inline(b.strip()[2:]) for b in block) + "\n</ul>")
            continue
        if re.match(r"\d+\. ", s):
            out.append("<ol>")
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                out.append("<li>%s</li>" % inline(re.sub(r"^\d+\. ", "", lines[i].strip()))); i += 1
            out.append("</ol>")
            continue
        out.append("<p>%s</p>" % inline(s)); i += 1
    if fig_open:
        out.append("</figure>")
    return "\n".join(out)


def main():
    md = (DOCS / "workflow.md").read_text(encoding="utf-8").splitlines()
    title = md[0][2:].strip()
    svgs = {
        "workflow.svg": gen_flow.build("inline", "git"),
        "workflow-svn.svg": gen_flow.build("inline", "svn").replace("ah-inline", "ah-inline-svn"),
    }
    body = convert(md, svgs)
    page = ('<!DOCTYPE html>\n<html lang="zh-Hant">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>%s</title>\n<style>\n%s\n</style>\n</head>\n<body>\n\n%s\n\n</body>\n</html>\n"
            % (html.escape(title, quote=False), CSS, body))
    out = enc(page)
    (DOCS / "workflow.htm").write_bytes(out.encode("ascii"))
    print("ok: workflow.htm", len(out), "bytes")
    sys.exit(check_links.main())


if __name__ == "__main__":
    main()
