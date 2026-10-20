---
status: accepted
date: 2026-10-19
---

# 以扁平複製安裝,不走 Claude Code plugin 機制

兩個上游(cursor/plugins 的 pstack、mattpocock/skills)都已經有官方 Claude Code plugin,照理直接 `claude plugin install` 最省事。但 plugin 機制下每個 skill 一律帶 namespace(`/mattpocock-skills:grilling`、`/pstack:how`),使用者認為這讓調用變麻煩、名單變重。我們決定 j-pockit 的安裝腳本在安裝時從上游取得 skill 目錄,**扁平複製**進 `~/.claude/skills/<name>/`,skill 名稱與上游一致、無 namespace。j-pockit 本身不維護 skill 內容副本,只維護安裝 / 更新腳本與說明文件。

## Considered Options

- **Plugin 模式**(依賴官方 plugin + `allowCrossMarketplaceDependenciesOn`):零維護、`claude plugin update` 可用,但 namespace 無法關掉。因調用便利性優先而棄。
- **全 fork**(83 個 skill 複製進 repo 自己維護):完全可控,但兩個上游幾乎每天更新,同步成本過高。棄。

## Consequences

- 更新不能用 `claude plugin update`,要重跑 j-pockit 安裝腳本。
- 同名 skill 會直接落在同一目錄:安裝腳本一律「既有同名 → 先封存到 `~/.claude/skills_archive/<yyyy-mm-dd>/<name>/` → 再覆蓋」,不詢問(封存無損,不需要人決定)。
- 兩套 skill set 自身的同名衝突(`tdd`、`teach`)必須在規格裡明定誰留誰讓。已定:`tdd` 留 Pocock(`/implement` 依賴),`teach` 留 pstack。
- pstack 的 Claude 樹是 generator 產物,SKILL.md 內指向 `../../docs/harness/claude-code.md`。扁平裝到 `~/.claude/skills/<name>/` 後該連結解析到 `~/.claude/docs/harness/claude-code.md`,所以安裝腳本把上游 `docs/` 原樣複製到 `~/.claude/docs/`、`agents/` 到 `~/.claude/agents/` 即可,不改任何 SKILL.md、不維護 overlay(2026-10-19 定,取代原本「兩檔 overlay」方案)。
- 不另取 cstack 之類的新名:使用者要無縫沿用 poteto 的名字與文件,避免混淆。
