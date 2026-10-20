"""Draw the j-pockit workflow diagrams (Git / SVN).

    python tools/docs/gen_flow.py          # writes docs/workflow.svg, docs/workflow-svn.svg

md2htm.py imports build() to inline the same diagrams into workflow.htm.
"""
import html, pathlib

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"

C = {
    "pocock": "#3a86c8", "pstack": "#c88a5a", "setup": "#4a9a6a",
    "svn": "#8a5ac8", "na": "#999999", "art": "#888888",
}

# skill names link to their row in appendix C (anchor s-<name>); a few non-skill boxes link elsewhere
LINK_OTHER = {"verify-<app>": "g-verify-app", "Opening a PR": "sec-5-2"}


def anchor_of(key):
    return LINK_OTHER.get(key) or "s-" + key.lstrip("/")


class SVG:
    def __init__(self, mode, w, h):
        self.mode, self.w, self.h, self.out = mode, w, h, []
        self.fg = "currentColor" if mode == "inline" else "#222"
        self.dim = "#888"

    def href(self, key):
        anchor = anchor_of(key)
        return ("#" if self.mode == "inline" else "workflow.htm#") + anchor

    def seg(self, text, key=None, mono=False, color=None, weight=None):
        attrs = []
        if mono:
            attrs.append('font-family="Consolas, monospace"')
        if color:
            attrs.append(f'fill="{color}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        t = f'<tspan {" ".join(attrs)}>{html.escape(text)}</tspan>'
        if key:
            t = (f'<a href="{self.href(key)}" class="flowlink">'
                 f'<tspan font-family="Consolas, monospace" fill="{C["pocock"] if self.mode=="file" else "#3a86c8"}" '
                 f'text-decoration="underline">{html.escape(text)}</tspan></a>')
        return t

    def text(self, x, y, parts, size=11, anchor="middle", color=None):
        body = "".join(p if p.startswith("<") else self.seg(p) for p in parts)
        self.out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
                        f'fill="{color or self.fg}">{body}</text>')

    def box(self, x, y, w, h, kind, lines, dashed=False):
        col = C[kind]
        if kind == "art":
            f = 12  # folded corner
            self.out.append(
                f'<path d="M{x} {y} H{x+w-f} L{x+w} {y+f} V{y+h} H{x} Z" fill="{col}14" '
                f'stroke="{col}" stroke-width="1.2"/>'
                f'<path d="M{x+w-f} {y} V{y+f} H{x+w}" fill="none" stroke="{col}" stroke-width="1"/>')
        else:
            dash = ' stroke-dasharray="5,3"' if dashed else ""
            self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{col}20" '
                            f'stroke="{col}" stroke-width="1.5"{dash}/>')
        n = len(lines)
        step = 16
        y0 = y + h / 2 - (n - 1) * step / 2 + 4
        for i, ln in enumerate(lines):
            size = 12.5 if (i == 0 and kind != "art") else 11
            self.text(x + w / 2, y0 + i * step, ln, size=size)

    def arrow(self, x1, y1, x2, y2, dashed=False, color="#999"):
        dash = ' stroke-dasharray="4,3"' if dashed else ""
        self.out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                        f'stroke-width="1.4"{dash} marker-end="url(#ah-{self.mode})"/>')

    def path(self, d, dashed=True, color="#999"):
        dash = ' stroke-dasharray="4,3"' if dashed else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.3"{dash} '
                        f'marker-end="url(#ah-{self.mode})"/>')

    def render(self):
        bg = '' if self.mode == "inline" else f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>'
        style = ('<style>.flowlink:hover tspan{fill:#d0602a}</style>')
        style_attr = ' style="max-width:100%;height:auto;background:transparent;"' if self.mode == "inline" else f' width="{self.w}" height="{self.h}"'
        return (f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg"{style_attr} '
                f'font-family="Segoe UI, Microsoft JhengHei, PingFang TC, Noto Sans CJK TC, sans-serif">\n'
                f'{style}{bg}<defs><marker id="ah-{self.mode}" markerWidth="10" markerHeight="10" refX="9" refY="3" '
                f'orient="auto"><polygon points="0 0, 10 3, 0 6" fill="#999"/></marker></defs>\n'
                + "\n".join(self.out) + "\n</svg>\n")


def build(mode, vcs):
    git = vcs == "git"
    s = SVG(mode, 980, 1290)
    sg = s.seg
    MX, MW = 290, 400          # main column
    CX = MX + MW / 2
    RX, RW = 730, 240          # right side column
    LX, LW = 10, 240           # left side column

    # ---- row 0: setup ----
    setups = [
        (10, ["0a. ", sg("/setup-pstack", "/setup-pstack")], "每台電腦 × 每個使用者帳號一次",
         ["~/.claude/rules/pstack-models.md"], "全機共用,跨專案、跨 repo、Git/SVN 都吃"),
        (340, ["0b. ", sg("/setup-matt-pocock-skills", "/setup-matt-pocock-skills")],
         "每個 repo 一次" if git else "每個 working copy 一次;tracker 選 Local markdown",
         ["docs/agents/*.md + CLAUDE.md"], "tracker、label、GLOSSARY / ADR 位置" if git else "+ 自寫 VCS: SVN 指令對照段"),
        (670, ["0c. ", sg("/create-verification-skill", "/create-verification-skill")], "每個專案一次(選用)",
         [".claude/skills/verify-<app>/"], "這個專案怎麼啟動、怎麼驗"),
    ]
    for x, title, sub, art, artsub in setups:
        s.box(x, 10, 300, 54, "setup", [title, [sg(sub, color=s.dim)]])
        s.arrow(x + 150, 64, x + 150, 82)
        s.box(x, 84, 300, 48, "art", [[sg(art[0], mono=True)], [sg(artsub, color=s.dim)]])
    s.text(490, 156, [sg("↓ 三個設定產出不在主流程裡傳遞;之後每個階段開工時由 skill 自己去讀(模型 / tracker 位置 / 驗證方法)",
                         color=s.dim)], size=11)

    # ---- main chain ----
    y = 172
    def main(h, kind, lines, gap=18, dashed=False):
        nonlocal y
        top = y
        s.box(MX, y, MW, h, kind, lines, dashed=dashed)
        y += h + gap
        if gap:
            s.arrow(CX, y - gap, CX, y - 2)
        return top, top + h

    a0 = main(36, "art", [[sg("輸入:需求 / 想法(口述或既有 issue)")]])
    s1 = main(66, "pocock", [["1. 對齊 · ", sg("/grill-with-docs", "/grill-with-docs")],
                             ["內部叫 ", sg("grilling", "grilling"), " + ", sg("domain-modeling", "domain-modeling")],
                             [sg("讀:需求、程式碼、既有 GLOSSARY.md / ADR", color=s.dim)]])
    # side: prototype
    s.box(RX, s1[0] - 4, RW, 40, "pocock", [[sg("/prototype", "/prototype"), "(選用)"], [sg("跑一下才知道的問題", color=s.dim)]], dashed=True)
    s.box(RX, s1[0] + 44, RW, 30, "art", [[sg("結論帶回對話;原型另存" + ("一條 branch" if git else "一個資料夾"))]])
    s.arrow(MX + MW, s1[0] + 16, RX - 2, s1[0] + 16)
    s.arrow(RX, s1[0] + 59, MX + MW + 2, s1[0] + 50)
    s.box(LX, s1[0] + 8, LW, 40, "pocock", [[sg("/grill-me", "/grill-me"), " 替代"], [sg("不在 repo 裡時用,不留檔", color=s.dim)]], dashed=True)

    a1 = main(52, "art", [[sg("GLOSSARY.md、docs/adr/NNNN-*.md", mono=True)],
                          [sg("+ 對話裡的共同理解(1→2→3 同一段 context,不清)", color=s.dim)]])
    s2 = main(54, "pocock", [["2. 規格 · ", sg("/to-spec", "/to-spec")],
                             [sg("讀:上一步的檔 + 對話 + repo;只彙整,不再問", color=s.dim)]])
    a2 = main(40, "art", [[sg("spec:GitHub issue" if git else "spec:.scratch/<feature>/spec.md", mono=not git)]] if git else
              [[sg(".scratch/<feature>/spec.md", mono=True)]])
    s3 = main(54, "pocock", [["3. 切票 · ", sg("/to-tickets", "/to-tickets")],
                             [sg("讀:spec;切法和相依先跟你確認", color=s.dim)]])
    a3 = main(40, "art", [[sg("票 × N:ready-for-agent,寫明 Blocked by" if git else
                              "票 × N:.scratch/<feature>/issues/NN-*.md(Status / Blocked by)")]])

    # stage 4
    poteto_top = y - 8
    s4 = main(78, "pstack", [["4. 執行 · 每張票開新 context"],
                             [sg("/poteto-mode", "/poteto-mode"), " 做票 #N  或  ", sg("/implement", "/implement")],
                             [sg("讀:一張票 + GLOSSARY + 程式碼", color=s.dim)]])
    sides = [
        [sg("/how", "/how"), " 讀程式 → 心智模型(只在對話)"],
        [sg("/architect", "/architect"), "(跨函式邊界時)"],
        [sg("/tdd", "/tdd"), " 紅 → 綠,一次一個測試"],
    ]
    for i, ln in enumerate(sides):
        yy = s4[0] - 6 + i * 30
        s.box(RX, yy, RW, 26, "pstack" if i < 2 else "pocock", [ln])
        s.arrow(MX + MW, s4[0] + 14 + i * 24, RX - 2, yy + 13)
    if git:
        s.box(LX, s4[0] + 34, LW, 46, "pocock", [[sg("/implement-spec", "/implement-spec"), " 替代"],
                                                [sg("整份 spec 平行做(worktree)", color=s.dim)]], dashed=True)
    else:
        s.box(LX, s4[0] + 34, LW, 46, "na", [[sg("/implement-spec", "/implement-spec"), " 不建議"],
                                            [sg("要 worktree + branch + merge", color=s.dim)]], dashed=True)

    a4 = main(42, "art", [[sg("feature branch 上的 commit + 測試" if git else
                              "working copy 修改 + 測試(svn commit 到 trunk 或 svn copy 的 branch)")]])
    s5 = main(66, "pstack", [["5. 驗證 / 審查"],
                             [sg("/code-review", "/code-review"), sg("(基準 SHA..HEAD)" if git else "(基準 rN:svn diff -r rN)"),
                              " · ", sg("/interrogate", "/interrogate")],
                             [sg("/blast-radius", "/blast-radius"), " · ", sg("verify-<app>", "verify-<app>"), sg("(讀 0c)", color=s.dim)]])
    s.box(RX, s5[0] + 4, RW, 26, "pstack", [[sg("/no-comments", "/no-comments"), " · ", sg("/unslop", "/unslop")]])
    s.arrow(MX + MW, s5[0] + 17, RX - 2, s5[0] + 17)
    a5 = main(40, "art", [[sg("review 結論:Act on / Consider / Dismissed + 修正 " + ("commit" if git else "修改"))]])
    # fix loop back to stage 4
    s.path(f"M {MX} {a5[0]+20} H {MX-26} V {s4[0]+40} H {MX-2}")
    s.text(MX - 30, (a5[0] + s4[0]) / 2 + 40, [sg("有 Act on → 回 4 修", color=s.dim)], size=10.5, anchor="end")

    if git:
        s6 = main(56, "pstack", [["6. 出貨 · ", sg("Opening a PR", "Opening a PR"), " playbook"],
                                 [sg("gh pr create;PR 說明套 ", color=s.dim), sg("pr", "pr"), sg(" skill", color=s.dim)]])
        a6 = main(40, "art", [[sg("PR(Summary / Evidence / Merge Danger)→ merge 進 main")]])
    else:
        s6 = main(56, "svn", [["6. 送審 / 提交(沒有 PR)"],
                              [sg("說明照 ", color=s.dim), sg("pr", "pr"), sg(" skill 格式寫;附 svn diff patch", color=s.dim)]])
        s.box(RX, s6[0] + 6, RW, 44, "na", [[sg("Opening a PR / Babysit /")], [sg("Shipping / Autopilot:不適用")]], dashed=True)
        a6 = main(40, "art", [[sg("patch + review 說明 → 審過後 svn commit -m")]])
    poteto_bot = a6[1] + 8
    s.out.insert(0, f'<rect x="{MX-14}" y="{poteto_top}" width="{MW+28}" height="{poteto_bot-poteto_top}" rx="8" '
                    f'fill="none" stroke="{C["pstack"]}" stroke-width="1.2" stroke-dasharray="6,4"/>')
    s.text(MX - 18, poteto_top + 14, [sg("/poteto-mode", "/poteto-mode"), sg(" 管的範圍", color=s.dim)], size=10.5, anchor="end")
    s.text(MX - 18, poteto_top + 28, [sg("(每個任務重打)", color=s.dim)], size=10.5, anchor="end")

    # next ticket loop: from a6 left back to s4
    s.path(f"M {MX+MW} {a6[0]+20} H {MX+MW+20} V {s4[1]-10} H {MX+MW+2}")
    s.text(MX + MW + 24, a6[0] + 4, [sg("下一張票 → 回 4", color=s.dim)], size=10.5, anchor="start")

    s7 = main(56, "pocock", [["7. 回顧 · ", sg("/retro", "/retro")],
                             [sg("/reflect", "/reflect"), " 改 skill · ", sg("/correct", "/correct"), " 改 repo"]])
    a7 = main(40, "art", [[sg("CLAUDE.md、lint / 測試、skill 修正 → 下一輪開工時讀到")]], gap=0)
    # retro feeds environment (setup row) -- right edge up
    s.path(f"M {MX+MW} {a7[0]+20} H 975 V 108 H 972")
    s.text(970, a7[0] + 36, [sg("回饋到環境(第 0 列的檔)", color=s.dim)], size=10.5, anchor="end")

    # legend
    ly = a7[1] + 26
    items = [("pocock", "Pocock"), ("pstack", "pstack"), ("setup", "設定")] + ([("svn", "SVN 改法"), ("na", "SVN 不適用")] if not git else [])
    lx = 200 if git else 40
    for kind, label in items:
        s.out.append(f'<rect x="{lx}" y="{ly-10}" width="14" height="12" fill="{C[kind]}20" stroke="{C[kind]}"/>')
        s.text(lx + 20, ly, [label], size=11, anchor="start")
        lx += 110 if git else 100
    s.out.append(f'<path d="M{lx} {ly-10} H{lx+12} L{lx+16} {ly-6} V{ly+2} H{lx} Z" fill="#88888814" stroke="#888"/>')
    s.text(lx + 22, ly, ["產出物(下一階段的輸入)"], size=11, anchor="start")
    s.text(lx + 200, ly, [sg("虛線框 = 選用 / 替代", color=s.dim)], size=11, anchor="start")
    s.h = ly + 14
    return s.render()


def main():
    for vcs, fname in (("git", "workflow.svg"), ("svn", "workflow-svn.svg")):
        (DOCS / fname).write_text(build("file", vcs), encoding="utf-8", newline="\n")
    print("ok: workflow.svg, workflow-svn.svg")


if __name__ == "__main__":
    main()
