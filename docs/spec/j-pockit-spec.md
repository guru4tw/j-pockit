# j-pockit 規格

日期:2026-10-20。詞彙見 `../../GLOSSARY.md`,架構決策見 `../adr/0001-flat-install-not-plugin.md`,查證事實見 `../research/upstream-facts.md`,逐題拍板見 `../decisions.md`。本檔是實作依據;與上述檔衝突時以本檔為準,並回頭修那份檔。

## Problem Statement

使用者在多台電腦用 Claude Code,想同時用 pstack(Lauren Tan)與 mattpocock-skills(Matt Pocock)兩套 skill set,而且要用 `/how`、`/grilling` 這種短名直接叫。官方 plugin 一律加 namespace(`/pstack:how`),調用變重;手動從 GitHub 複製又沒法追版本、沒法在另一台機器重現。本機既有的 15 個 Pocock flat skill 已落後 v1.3(還在用 CONTEXT.md),沒有可靠的更新方法。

## Solution

一個私人 GitHub repo `guru4tw/j-pockit`,裡面只有一支 `install.ps1`、一個 `versions.lock`、說明文件。跑一次 installer 就把兩套的 Claude Code 版扁平裝進 `~/.claude/skills/<name>/`,版本釘在 lock;`install.ps1 -Update` 把 lock 推到上游最新再裝。既有同名目錄先封存再覆蓋,不問。repo 不維護任何上游內容副本,也不維護 overlay。

## User Stories

1. As a Claude Code 使用者, I want 跑一支腳本就裝好兩套 skill set, so that 換機器不用手動複製。
2. As a 使用者, I want 用 `/how`、`/grilling` 短名叫 skill, so that 不用記 namespace。
3. As a 使用者, I want skill 名稱、內容與上游一致, so that 看上游文件就能用,不用對照另一套名字。
4. As a 使用者, I want 安裝版本釘在 repo 裡, so that 兩台機器裝出來一樣,出問題可對照。
5. As a 使用者, I want `-Update` 一個旗標就升到上游最新, so that 跟上 pstack 每日 bump 與 Pocock 新 tag。
6. As a 使用者, I want 更新後 lock 的變動能 commit, so that 其他機器下次 install 就拿到同版。
7. As a 使用者, I want 既有同名 skill 自動封存到 `~/.claude/skills/` 之外, so that 覆蓋不丟舊版、也不會被 Claude 掃到。
8. As a 使用者, I want 封存不要問我, so that 安裝一氣呵成。
9. As a 使用者, I want `/implement` 還是叫得到 `/tdd` 與 `/code-review`, so that Pocock 的 user-invoked → model-invoked 鏈不斷。
10. As a 使用者, I want `/tdd` 是 Pocock 版、`/teach` 是 pstack 版, so that 同名衝突有明確裁決。
11. As a 使用者, I want 我自己的 `/handoff`(`~/.claude/commands/handoff.md`)不被蓋掉, so that Stop hook 的接力流程照常。
12. As a 使用者, I want installer 不碰 `owl_check`、`plan-eng-review`、`writing-great-skills` 這些非兩套管的目錄, so that 我的其他 skill 安全。
13. As a 使用者, I want pstack 的 adapter(`docs/harness/claude-code.md`)裝到 SKILL.md 相對連結能解析的位置, so that 每個 pstack skill 開頭的「read the adapter」不斷鏈。
14. As a 使用者, I want pstack 的兩個 subagent 裝到 `~/.claude/agents/`, so that `/poteto-mode` 能 spawn `poteto-agent`。
15. As a 使用者, I want pstack 的 `docs/guide/` 也裝到本機, so that 離線也能看 10 頁指南。
16. As a 使用者, I want SKILL.md 一字不改, so that 更新時沒有 diff 要維護。
17. As a 使用者, I want 模型 slug(grok、gpt)在 Claude 下自動退回 session 模型, so that pstack 的模型選單不用改也能跑(adapter 已做)。
18. As a 使用者, I want installer 裝完列出裝了哪些、封存了哪些, so that 我知道發生什麼事。
19. As a 使用者, I want installer 裝完提醒「v1.3 改用 GLOSSARY.md,舊專案 CONTEXT.md 請自行改名」, so that 不會忘了 breaking rename。
20. As a 使用者, I want README 告訴我裝完後要跑 `/setup-pstack`(一機一次)與 `/setup-matt-pocock-skills`(一 repo 一次), so that 兩套的設定步驟不用去翻上游。
21. As a 使用者, I want README 有一節「兩套合用路線」, so that 知道哪個階段用哪套。
22. As a 使用者, I want 一份 `docs/workflow.htm` 開發流程圖, so that 一張圖看懂兩套怎麼接。
23. As a 使用者, I want `.ps1` 是 ASCII-only 且過 parse-check, so that 在任何 code page 的 Windows 都能跑。
24. As a 使用者, I want installer 只依賴 git 與 Windows PowerShell 5.1, so that 新機器不用先裝別的東西。
25. As a 使用者, I want installer 用 sparse clone 只拉需要的子目錄, so that 不用下載整個 cursor/plugins。
26. As a 使用者, I want 暫存 clone 用完就清, so that 不留垃圾。
27. As a 使用者, I want repo 有 MIT LICENSE 與致謝段, so that 上游作者的歸屬清楚。
28. As a 使用者, I want repo 的 push 前掃過金鑰, so that 符合 `H:\ALG_Joe` 的規則。
29. As a 使用者, I want `repos.txt` 有 j-pockit 一行, so that `sync_github.ps1` 會一起同步。
30. As a 使用者, I want 上游新增的 skill 在 `-Update` 後自動納入, so that 不用改 installer 名單。

## Implementation Decisions

### Repo 內容

- `install.ps1`:唯一的安裝 / 更新腳本。ASCII-only(含註解);動完必跑 `_Owlery/parse_ps1.ps1`。不寫 `install.sh`。
- `versions.lock`:純文字,兩行 `key=value`:`pstack=<commit SHA>`、`mattpocock-skills=<tag>`。初值 `pstack=d457567`(完整 SHA 以實作時 `git ls-remote` 為準)、`mattpocock-skills=v1.3.1`。
- `README.md`:繁中白話。章節:這是什麼 / 安裝 / 更新 / 裝完後兩步(`/setup-pstack`、`/setup-matt-pocock-skills`)/ 兩套合用路線 / 同名與排除清單 / 致謝(Lauren Tan、Matt Pocock、Dex Horthy,附上游連結)。
- `LICENSE`:MIT,Joe。不寫 THIRD_PARTY_NOTICES。
- `GLOSSARY.md`、`docs/adr/`、`docs/research/`、`docs/spec/`、`docs/decisions.md`:現有。
- `docs/workflow.htm`:用 `/gen_htm` 產的開發流程圖,README 連過去。
- 不放任何上游 skill 內容、不放 overlay。

### 上游來源與版本

- pstack:`https://github.com/cursor/plugins`,只取 `harness/pstack/claude-code/`(generator 產出的 Claude 樹),釘 lock 的 SHA。
- mattpocock-skills:`https://github.com/mattpocock/skills`,釘 lock 的 tag。
- 取法:`git init` → `config core.autocrlf false`(保持上游位元組)→ `remote add origin <url>` → `sparse-checkout set <subdir>` → `fetch --depth 1 --filter=blob:none origin <sha|refs/tags/tag>` → `checkout FETCH_HEAD`。原寫的 `clone --depth 1` 只拿得到預設分支頂端,釘舊 SHA / tag 會 checkout 失敗,實作時改掉(2026-10-20)。暫存目錄放 `$env:TEMP\j-pockit\<set>\`,裝完刪。
- lock 的 pstack 必須是 40 碼完整 SHA(依 SHA fetch 需要),installer 會檢查。
- `-Update`:先 `git ls-remote` 取 cursor/plugins `main` HEAD SHA、mattpocock/skills 最新 tag(`v*` 依 semver 排序取最大),寫回 `versions.lock`,再照 lock 裝。lock 的變動由使用者 commit;installer 不碰 git 歷史。
- 無 `-Update` 時嚴格照 lock,不連線查最新。

### 安裝集合

- pstack:`skills/` 下全部 56 個目錄,**排除** `tdd`。實裝 55。
- mattpocock-skills:`skills/engineering/` 20 + `skills/productivity/` 7,**排除** `teach`、`handoff`。實裝 25。`skills/in-progress/`、`skills/misc/` 不裝。
- 排除名單寫死在 installer 頂端,理由各一行註解。集合其餘部分由上游目錄即時列出,所以上游新增的 skill 會在 `-Update` 後自動納入。
- 上游**移除**的 skill 不從本機刪(installer 永不刪 `~/.claude/` 下任何東西);裝完若發現本機有兩套曾管但本次上游沒有的目錄,印一行提示請使用者自行處理。「曾管」的依據是 `~/.claude/j-pockit-installed.txt`(每次裝完寫入本次安裝名單,一行一名)。(推測,實作時自定,待拍板)
- 兩套排除後若仍有同名,installer 在複製前大聲失敗,要求補排除名單。

### 安裝目的地

- skill:`~/.claude/skills/<name>/`,目錄名 = 上游目錄名,內容整目錄複製(含 playbooks / references / scripts)。
- pstack `docs/`(含 `harness/claude-code.md`、`guide/`):整目錄複製到 `~/.claude/docs/`。只覆蓋同路徑檔,不刪 `~/.claude/docs/` 內其他東西。SKILL.md 的 `../../docs/harness/claude-code.md` 因此能解析。
- pstack `agents/`(`poteto-agent.md`、`comment-sicko.md`):複製到 `~/.claude/agents/`。
- 不裝:pstack `LICENSE`、`README.md`、`plugin.json`、`.claude-plugin/`;Pocock repo 根的任何檔。

### 封存(Archive)

- 目標 skill 目錄已存在 → 整目錄搬到 `~/.claude/skills_archive/<yyyy-mm-dd>/<name>/`,再複製新版。不詢問、不刪。
- 同日重跑且封存路徑已存在 → 在日期後加 `-2`、`-3`。
- `~/.claude/agents/` 同名檔同樣封存到 `~/.claude/skills_archive/<yyyy-mm-dd>/agents/<file>`。`~/.claude/docs/` 內檔案直接覆蓋不封存(全是上游文件,無使用者內容)。
- 新舊內容逐檔相同時仍封存(簡單、可預期)。

### 絕不碰的東西

- `~/.claude/skills/` 下不在本次安裝集合內的目錄(`owl_check`、`plan-eng-review`、`writing-great-skills`、使用者未來自建的任何 skill)。
- `~/.claude/commands/`(含 `handoff.md`)。
- 任何專案目錄(`CONTEXT.md` 改名由使用者或 Claude 另做)。
- SKILL.md 內容、frontmatter。不加 `disable-model-invocation`、不寫 `skillOverrides`、不改模型 slug。
- `~/.claude/settings.json`、`~/.claude/rules/`。

### 執行期行為

- 前置檢查:`git` 在 PATH;`~/.claude/` 存在;lock 可讀且兩個 key 都在。缺一即大聲失敗、退出碼非 0,不做半套。
- 結束輸出:每套裝了幾個、封存了哪些(路徑)、docs / agents 複製結果;接著固定兩行:
  - `v1.3 renamed CONTEXT.md to GLOSSARY.md; rename old project CONTEXT.md files yourself.`
  - `Next: run /setup-pstack once per machine, /setup-matt-pocock-skills once per repo.`
- 只有 `-Update` 一個旗標。

### GitHub

- 使用者在網頁建 `guru4tw/j-pockit` private,預設分支 `main`。
- Claude 做:`git -C H:/ALG_Joe/j-pockit init`、首次 push 前 `python -I H:/ALG_Joe/scan_secrets.py H:/ALG_Joe/j-pockit`、`H:/ALG_Joe/repos.txt` 加 `j-pockit https://github.com/guru4tw/j-pockit.git`。
- 本機無 `gh`,全走 `git` + HTTPS。

### 兩套合用路線(README 與 workflow.htm 的內容)

- 規劃 / 規格 / 票:Pocock —— `/grill-with-docs` → `/to-spec` → `/to-tickets`。
- 執行 / 驗證 / 審查 / PR:pstack —— `/poteto-mode` 常駐,`/how` 理解、`/interrogate` 設計、`/swarm` 平行、`/unslop` 文字;Pocock `/implement` 逐票時仍可用。
- 回顧:Pocock `/retro`;pstack `/reflect` 為替代。
- 設定:`/setup-pstack`(一機一次)、`/setup-matt-pocock-skills`(一 repo 一次),無順序、不互斥。

## Testing Decisions

- 沒有自動化測試;installer 是一次性腳本,用本機實跑驗收。
- 驗收步驟(本機,依序):
  1. `parse_ps1.ps1` 回 PARSE_OK。
  2. 首次 install:`~/.claude/skills/` 下 pstack 55 + Pocock 25 個目錄存在;`~/.claude/skills_archive/<今天>/` 下有原本 14 個目錄(13 個 Pocock 同名 + 被 pstack 蓋的 `teach`;`writing-great-skills` 不碰所以不在內);`owl_check`、`plan-eng-review`、`writing-great-skills`、`commands/handoff.md` 原封不動;`~/.claude/docs/harness/claude-code.md` 與 `~/.claude/agents/poteto-agent.md` 存在。
  3. 開新 Claude session:`/how`、`/grilling`、`/implement` 都列在 skill 清單;`/doctor` 無警告;`claude plugin validate ~/.claude/skills` 通過。
  4. 再跑一次 install(不帶 `-Update`):結果與步驟 2 相同,只多一層封存。
  5. `-Update`:`versions.lock` 兩個值變成上游最新;`git diff` 只有那兩行。
- 只驗外部行為(目錄、檔案、輸出字串),不驗腳本內部函式。
- 驗收紀錄 2026-10-20(lock = pstack `d457567332aa6989e753ea289f30ea2bfbc80bc0`、Pocock `v1.3.1`):
  - 步驟 1 PASS。`_Owlery/parse_ps1.ps1` 只收 `H:\ALG_DevRepository`、`H:\ALG_GitDevRepository` 下的檔(回 ERR[4]),改用同邏輯(PSParser.Tokenize + Language.Parser)的 scratchpad 腳本驗,PARSE_OK;全檔 ASCII。
  - 步驟 2 PASS。`skills/` 共 83 個 SKILL.md = 55 + 25 + 3 個不碰的;封存 14 個到 `skills_archive/2026-10-20/`;`owl_check`、`plan-eng-review`、`writing-great-skills`、`commands/handoff.md` 的大小與 mtime 不變;docs 18 檔、agents 2 檔就位;`how/SKILL.md` 大小與上游 blob 相同(2839 bytes,LF 保留);`$env:TEMP\j-pockit` 已清。
  - 步驟 4 PASS。重跑封存 82 項(80 skill + 2 agent)到 `skills_archive/2026-10-20-2/`,結果同步驟 2。
  - 步驟 5 PASS。先 `git init -b main`,initial commit `948b218`(lock = d457567 / v1.3.1),再跑 `-Update`:pstack → `88d47514b82e7c44f00f2b2a72ff6dd12158038c`(main HEAD),Pocock 仍是最新 tag `v1.3.1`;`git diff` 只有 `versions.lock` 的 pstack 一行。照新 lock 重裝 55 + 25,封存 82 項到 `skills_archive/2026-10-20-3/`,不碰的 4 檔大小與 mtime 不變。
  - 步驟 3 部分 PASS(2026-10-20,新 session,lock = pstack `88d4751`、Pocock `v1.3.1`):
    - `claude plugin validate D:/Users/joe/.claude/skills` → `✔ Validation passed`。
    - 模型看得到的 skill 清單(system prompt)有 `grilling`,沒有 `how`、`implement`。這是設計如此:兩者 frontmatter 都是 `disable-model-invocation: true`,只進使用者的 `/` 選單,不進模型清單。模型清單共 14 個可自動叫的 skill,正好對上 83 個 SKILL.md 扣掉 69 個 `disable-model-invocation: true`(Pocock model-invoked 11 + `setup-pstack` + `owl_check` + `plan-eng-review`)。
    - 與規格出入:pstack @ `88d4751` 的 `setup-pstack` **沒有** `disable-model-invocation`,不是 Further Notes 寫的「56 個全是」。不影響安裝,只是它的 description 會進 context。
    - 待使用者補:互動 `claude` 終端打 `/` 確認 `/how`、`/implement` 在選單內;跑 `/doctor` 看有無警告。Claude Code 桌面 app 的 session 跑不了這兩項。

## Out of Scope

- `install.sh`、macOS / Linux。
- `plan-eng-review`(gstack)的納入或更新。
- 執行 `/setup-pstack`、`/setup-matt-pocock-skills`。
- 專案內 `CONTEXT.md` → `GLOSSARY.md` 改名(另做)。
- Overlay、改 SKILL.md、改模型 slug、`skillOverrides`。
- Plugin 模式、`cstack` 之類的改名。
- 刪除本機任何 skill。
- `-DryRun`、`-Uninstall` 之類的旗標。

## Further Notes

- pstack 的 `poteto-agent.md` frontmatter 帶 Cursor 專屬 `is_background: true`,Claude Code 不認得;照 adapter 規則忽略,不改檔。
- pstack 56 個 skill 除 `setup-pstack` 外都是 `disable-model-invocation: true`(@ `88d4751` 實查),description 不進 context;Pocock model-invoked 的那幾個會進,這是為了不斷鏈的代價。
- 接下來:`/handoff` 結算 → 下一 session 實作 installer + README + workflow.htm → 本機實跑驗收 → 改名兩個 CONTEXT.md。
