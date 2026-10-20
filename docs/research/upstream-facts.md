# 上游事實(2026-10-19 查證)

研究來源:sub-agent 直接 clone / GitHub API / 官方 docs。只記事實,不記決策。

## pstack(cursor/plugins)

- 路徑 https://github.com/cursor/plugins/tree/main/pstack;作者 Lauren Tan(poteto)。
- 版本 0.15.28;最後 commit d457567 2026-10-19T05:35Z,幾乎每天 bump。
- License:`pstack/LICENSE` MIT,`Copyright (c) 2026 Lauren Tan`。repo 根**沒有** LICENSE 檔(GitHub API `license: null`),根 README 只寫 `## License / MIT`。
- 內容:56 skills(24 個 `principle-*` 一段話)、23 playbooks(`skills/poteto-mode/playbooks/`)、2 subagents(`poteto-agent`、`comment-sicko`)、`docs/guide/` 10 頁、`automations/benny/`(Cursor only)。
- 全部 SKILL.md 都是 `disable-model-invocation: true`。
- 入口:`/setup-pstack`(寫模型路由 rule)→ `/poteto-mode`(常駐 agent style)。README 明言「沒有 planning skill」。
- **已有官方 Claude Code plugin**:`/plugin marketplace add cursor/plugins` → `/plugin install pstack@cursor-plugins`。安裝的是 generator 產出的 `harness/pstack/claude-code/` 樹(`scripts/generate-pstack-harness-trees.mjs`),略過 automations/assets/.cursor-plugin。
- Claude 移植毛邊(adapter `pstack/docs/harness/claude-code.md`):
  - Skill tool 拒絕互叫 pstack skill(因 disable-model-invocation),改用 `Read <pstack>/skills/<name>/SKILL.md`。
  - `setup-pstack` 改寫 `~/.claude/rules/pstack-models.md`;模型預算選項含 grok slug,在 Claude 無意義,adapter 規定 grok/gpt → 省略 model。
  - Task→Agent、AskQuestion→AskUserQuestion、todolist→TodoWrite、`readonly: true`→Explore、`environment: cloud`→`isolation: worktree`。
  - Automations / Bugbot / cloud agents / 內建 PR tool → 輸出 `Skipped in Claude Code: ...`。
  - `/deslop`、`control-cli`、`control-ui` 來自另一個 plugin `cursor-team-kit`,pstack 不含。
- 生成樹 `harness/pstack/claude-code/` 內容:`skills/`(56)、`agents/poteto-agent.md` + `comment-sicko.md`(frontmatter 只有 name / description / `is_background: true`,無 model / tools)、`docs/harness/claude-code.md`(5.7 KB adapter)、`docs/guide/`(10 頁 + 6 jpg)、`LICENSE`、`README.md`、`plugin.json`、`.claude-plugin/plugin.json`。
- 每個 SKILL.md 開頭都寫「read [the Claude Code adapter](../../docs/harness/claude-code.md) once per session」;skill 互叫用 `../<name>/SKILL.md`(poteto-mode 明寫此慣例);playbooks / references / scripts 都在 skill 目錄內。**扁平裝到 `~/.claude/skills/<name>/` 後,`../../docs/harness/claude-code.md` 會解析到 `~/.claude/docs/harness/claude-code.md`** —— 把上游 `docs/` 原樣複製到 `~/.claude/docs/` 即可,不用改任何 SKILL.md。
- adapter 已在執行期處理:`~/.cursor/rules/pstack-models.mdc` → `~/.claude/rules/pstack-models.md`;非 Claude 模型 slug(`grok-4.7-xhigh-fast`、gpt)→ 省略 model 用 session 模型;`.cursor` → `.claude`;`Task` → `Agent`。setup-pstack 的「選單」其實是 4 檔 reasoning budget(unlimited / large / medium / small),預設 slug 是 `claude-opus-5-5-xhigh` + `grok-4.7-xhigh-fast`;poteto-mode 寫「Defaults `grok-4.7-xhigh-fast` for code, `claude-opus-5-5-xhigh` for prose and judgment」。
- Cursor 專屬:`.cursor-plugin/plugin.json`、`assets/logo.png`、`automations/benny/`、agents frontmatter `is_background: true`、`~/.cursor/rules/*.mdc`。
- 本機 sparse clone(暫存,可能已清):`<scratchpad>/dl_plugins`。

## mattpocock/skills

- https://github.com/mattpocock/skills;MIT,`Copyright (c) 2026 Matt Pocock`;`package.json` license MIT。
- Tags:v1.3.0(2026-09-29)、v1.3.1(2026-10-04)。**沒有** 叫 `skills-v1-3` 的 tag,那是 tenten 文章 URL slug。最後 commit 2026-10-09。
- **已有官方 Claude Code plugin**:`claude plugin install mattpocock-skills@claude-plugins-official`,27 skills(engineering 20 + productivity 7),自動更新。README:「Pick one per agent, because installing both gives you every skill twice.」
- 兩類 skill:user-invoked(`disable-model-invocation: true`,負責 orchestrate)/ model-invoked(可被模型自動叫,放可重用紀律)。規則:user-invoked 可叫 model-invoked,反向禁止。
- 主流程(`ask-matt` router):`/setup-matt-pocock-skills`(每 repo 一次)→ `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement`(逐票)或 `/implement-spec`(整份 spec 平行)→ `pr` → `/retro`。單 session:`/grill-with-docs` → `/implement`。
- v1.3 變更:graduate `implement-spec`、`pr`、`retro`;移除 `resolving-merge-conflicts`;**breaking rename** `CONTEXT.md`→`GLOSSARY.md`、`CONTEXT-MAP.md`→`GLOSSARY-MAP.md`,無向下相容,要 `git mv`。
- `pr` skill frontmatter 載明 credit:Dex Horthy / Humanlayer `show-me`。
- v1.3.1 tree 共 37 個 SKILL.md:`skills/engineering/` 20 + `skills/productivity/` 7 = 官方 plugin 的 27;另 `skills/in-progress/` 6(claude-handoff、loop-me、setup-ts-deep-modules、writing-beats、writing-fragments、writing-shape)、`skills/misc/` 4(git-guardrails-claude-code、migrate-to-shoehorn、scaffold-exercises、setup-pre-commit)不在 plugin 內。
- 27 個名單:engineering = ask-matt、code-review、codebase-design、diagnosing-bugs、domain-modeling、grill-with-docs、implement-spec、implement、improve-codebase-architecture、pr、prototype、research、retro、setup-matt-pocock-skills、tdd、to-spec、to-tickets、triage、wayfinder、wizard;productivity = grill-me、grilling、handoff、teach、to-questionnaire、wait-what、writing-for-agents。
- 本機 `writing-great-skills` **不在 v1.3.1 任何目錄**(已被上游移除或改名),升版後成孤兒。
- 與 pstack **無任何互相引用**;概念重疊:`/tdd`↔`tdd`、`/teach`↔`teach`、`/reflect`↔`/retro`、`/poteto-mode`↔`ask-matt`。

## 使用者本機現況

- `D:\Users\joe\.claude\skills\` 有 15 個 Pocock flat skill:grilling、grill-me、grill-with-docs、domain-modeling、to-spec、to-tickets、implement、tdd、code-review、codebase-design、teach、research、writing-great-skills、improve-codebase-architecture、setup-matt-pocock-skills。版本 **早於 v1.3**(domain-modeling 仍寫 CONTEXT.md)。
- 另有 `plan-eng-review`(來源 gstack,Garry Tan,與本案兩套無關)。gstack = github.com/garrytan/gstack,repo 根有 ~120 個項目(約 60 個 skill 目錄平鋪在根、`lib/`、`bin/`、`setup` / `setup.ps1`、`VERSION`、`LICENSE` + `NOTICE.md` + `licenses/`);本機 `plan-eng-review/SKILL.md` 檔頭寫 `AUTO-GENERATED from SKILL.md.tmpl — do not edit directly`,frontmatter `benefits-from: [office-hours]`。它有自己的安裝 / 升級機制(`setup.ps1`、`gstack-upgrade/`),單抽一個目錄沒有保證能獨立運作。
- 本機無 pstack、無 `gh` CLI。
- 既有專案用舊名:`H:\ALG_Joe\Freelance\CONTEXT.md`、`H:\ALG_Joe\REA\CONTEXT.md`(升 v1.3 會受 rename 影響)。

## Claude Code plugin 機制(官方 docs)

- plugin.json 只有 `name` 必填;元件目錄 `skills/`、`commands/`(仍支援但建議用 skills)、`agents/`、`hooks/hooks.json`、`.mcp.json`、`bin/`。plugin 內 CLAUDE.md 不會載入。
- marketplace.json 最小:`name`、`owner.name`、`plugins[{name, source}]`;相對 source 須 `./` 開頭。一個 repo 可同時是 marketplace 並放多個 plugin。source 類型:相對路徑、github、url、git-subdir、npm、archive、command。
- CLI:`claude plugin marketplace add owner/repo`、`claude plugin install name@marketplace`(2.1.292+ 可加 `--marketplace owner/repo` 一步到位)、`claude plugin update name@marketplace`、`claude plugin validate <path>`。
- Private repo 可行,靠本機既有 git 認證(SSH 無 passphrase 或 HTTPS 已存 credential);無 token 欄位;背景更新失敗會靜默。
- Plugin skill 一律 namespace `/plugin:skill`;與 `~/.claude/skills/<同名>` 並存,`/<name>` 叫到 flat 那個。
- 版本:plugin.json 有 `version` 就釘版,沒有則追 commit SHA。非官方 marketplace 預設**不自動更新**。
- Claude Code 不讀 Cursor `.mdc` / `.cursor-plugin`。
- `~/.claude/rules/*.md` 是官方支援的 user-level rules(docs/en/memory「Personal rules in `~/.claude/rules/` apply to every project on your machine」),所以 adapter 讓 `setup-pstack` 寫 `~/.claude/rules/pstack-models.md` 是有效的。
- 同名解析(docs/en/skills「Resolve skills that share a name」):skill 與 `.claude/commands/<name>.md` 同名 → **skill 勝**;personal(`~/.claude/skills`)勝 project;personal/project skill 會取代同名內建 command(alias 不取代)。

## 同名盤點(2026-10-19,pstack 56 + Pocock 27 vs 本機)

- pstack ↔ Pocock:只有 `tdd`、`teach`。
- 兩套 ↔ 本機 `~/.claude/skills/`(owl_check、plan-eng-review):無。
- 兩套 ↔ 本機 `~/.claude/commands/`(28 個):**只有 Pocock `handoff` ↔ `commands/handoff.md`**。user 的 `/handoff` 是 Stop hook 強制接力流程,user CLAUDE.md 直接引用該檔;依上條規則裝了 Pocock `handoff` 會蓋掉它。
- 兩套 ↔ 內建 command:pstack 無;Pocock 無(`loop-me` 在 in-progress,不裝)。
- 磁碟:`~/.claude/plugins/{cache,marketplaces,data,installed_plugins.json,known_marketplaces.json}`;settings `enabledPlugins`、`extraKnownMarketplaces`。
- Marketplace entry name 與 plugin.json name 不同時:安裝 id 用 entry name,skill namespace 用 manifest name,無警告。`git-subdir` source 支援 `ref` / `sha` 釘版。
- Cross-marketplace `dependencies` 預設不自動安裝;root marketplace 要加 `allowCrossMarketplaceDependenciesOn: [...]`。

## Skill 載入成本(官方 docs/en/skills)

- `disable-model-invocation: true`:description **不進 context**,只列名字,`/name` 時才載入全文。pstack 56 個全是此類。
- `user-invocable: false`:description 常駐 context,只有模型能叫。
- 清單預算 = 模型 context 的 1%;超出時先砍最少用的 skill 的 description,名字一律保留;每筆上限 1536 字元。可調 `skillListingBudgetFraction`、env `SLASH_COMMAND_TOOL_CHAR_BUDGET`、`skillOverrides` 設 `name-only`。
- `~/.claude/skills/` 底下巢狀目錄(如 `_archive_x/foo/SKILL.md`)會不會被掃:**官方未載明**。封存應放到 `~/.claude/skills/` 之外。
- 診斷:`/doctor` 估清單成本、`/skill-doctor` 找沒用的 skill、`claude plugin validate ~/.claude/skills`(2.1.233+)。
