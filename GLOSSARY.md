# j-pockit

guru4tw/j-pockit:一個 GitHub repo,用來在任何電腦上一次裝好 pstack 與 mattpocock-skills 的 Claude Code 版,並附兩套合用的說明。本檔是詞彙表,不放實作細節。

## Language

**j-pockit**:
GitHub repo 名,也是「一次性安裝 + 說明文件」這個東西本身。不是 skill 名,不是 plugin namespace。
_Avoid_: skill pool、j-pockit plugin、j-pockit skill

**Skill set(技能包)**:
一位作者維護、成套發布的一組 skill,代表一種工作方法。本 repo 處理兩套:pstack、mattpocock-skills。
_Avoid_: 方法、套件、skill 包、framework

**pstack**:
Lauren Tan(poteto)在 cursor/plugins 維護的 skill set。j-pockit 安裝的是它的 Claude Code 樹,名稱、skill 名一律沿用上游,不另取名。
_Avoid_: cstack(曾考慮的改名,2026-10-19 棄用,文件中不得出現)、gstack(Garry Tan 的另一套,與本案無關)、poteto stack

**Overlay(修補層)**:
曾規劃的 j-pockit 自維護修補檔,用來修 pstack 在 Claude 的毛邊。已定(2026-10-19)**縮成零檔**:上游 `docs/`(含 adapter)原樣複製到 `~/.claude/docs/`,相對連結自然接上;`agents/` 複製到 `~/.claude/agents/`;SKILL.md 一律不改;模型映射交給 adapter 執行期處理。j-pockit 自己的內容只剩 installer 與說明文件。
_Avoid_: patch、fork、客製版

**Installer(安裝腳本)**:
j-pockit 內的 `install.ps1`(ASCII-only;只此一支,`install.sh` 需要時再補;用 `git clone --depth 1 --filter=blob:none --sparse` 取上游),負責取上游、扁平複製、複製 docs/ 與 agents/、封存同名、略過排除名單(`handoff`、pstack `tdd`、Pocock `teach`)。更新也是重跑它。
_Avoid_: setup、bootstrap、安裝器

**versions.lock(版本鎖)**:
repo 根目錄的檔,釘住要裝的 pstack commit SHA 與 mattpocock-skills tag。平常 install 照 lock 裝;`install -Update` 先把 lock 改成上游最新(pstack main HEAD、Pocock 最新 tag)再裝,改動要 commit。已定(2026-10-19)。
_Avoid_: 追 main、latest

**Collision(同名衝突)**:
兩套 skill set 各自有同名 skill(目前:`tdd`、`teach`),扁平安裝後只能留一個。已裁決(2026-10-19):`tdd` 留 mattpocock-skills 版(`/implement` 依賴它);`teach` 留 pstack 版(無人依賴,學新概念改用 Pocock `research`)。對本機:mattpocock-skills 的 `handoff` **不裝**(會蓋掉 `~/.claude/commands/handoff.md`,那是 Stop hook 的接力流程),所以 Pocock 實裝 25 個(27 − `teach` − `handoff`),pstack 實裝 55 個(56 − `tdd`)。本機非兩套管的目錄(`owl_check`、`plan-eng-review`、孤兒 `writing-great-skills`)installer 一律不碰。
_Avoid_: 重疊、撞名、conflict

**Archive(封存)**:
Installer 要寫入 `~/.claude/skills/<name>/` 而該目錄已存在時,先把舊目錄整個搬到 `~/.claude/skills_archive/<yyyy-mm-dd>/<name>/`,再寫新版。不詢問、不刪、不留在 `~/.claude/skills/` 底下(避免被掃到)。已定(2026-10-19)。
_Avoid_: Reversion、backup、rollback、`_archive_<date>`(舊做法,放在 skills/ 內)

**mattpocock-skills**:
Matt Pocock 在 mattpocock/skills 維護的 skill set,官方 plugin 名即此。j-pockit 不改名。已定(2026-10-19):裝全 27 個;SKILL.md frontmatter 照上游,不加 `disable-model-invocation`、不寫 `skillOverrides`,因為 user-invoked skill 靠 Skill tool 叫 model-invoked skill(`/implement` → `/tdd`、`/code-review`),改旗標會斷鏈。
_Avoid_: mattpocock-skills-v1-3(那是文章 URL slug,不是版本 tag;真實 tag 是 v1.3.0 / v1.3.1)、pocock

**Upstream(上游)**:
兩個官方來源 repo:cursor/plugins、mattpocock/skills。j-pockit 能依賴就依賴,不自己維護副本。
_Avoid_: 原廠、source

**Official plugin(官方 plugin)**:
上游已發布到 Claude Code marketplace 的 plugin:`pstack@cursor-plugins`、`mattpocock-skills@claude-plugins-official`。
_Avoid_: 官方版、原版

**Flat skill(扁平 skill)**:
放在 `~/.claude/skills/<name>/` 的 skill,用 `/<name>` 叫,沒有 namespace。使用者本機現有的 15 個 Pocock skill 屬此類。
_Avoid_: 本機 skill、user skill、全域 skill

**Plugin skill**:
隨 plugin 安裝的 skill,一律帶 namespace,用 `/<plugin>:<name>` 叫。與同名 flat skill 可並存,不互相覆蓋。
_Avoid_: namespaced skill、plugin 內 skill
