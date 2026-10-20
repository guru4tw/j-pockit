# j-pockit

把兩套 Claude Code skill set 扁平裝進 `~/.claude/skills/`,用短名直接叫(`/how`、`/grilling`,不是 `/pstack:how`),版本釘在 `versions.lock`,換機器跑一支腳本就裝出一樣的東西。

開發流程圖:[docs/workflow.htm](docs/workflow.htm)(下載後用瀏覽器開)。

## 這是什麼

| 套件 | 作者 | 上游 | 裝幾個 |
|---|---|---|---|
| pstack | Lauren Tan | [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack) 的 `harness/pstack/claude-code/` | 55(上游 56 扣 `tdd`) |
| mattpocock-skills | Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) 的 `skills/engineering/` + `skills/productivity/` | 25(上游 27 扣 `teach`、`handoff`) |

repo 裡只有:

- `install.ps1`:唯一的安裝 / 更新腳本
- `versions.lock`:兩行 `key=value`,pstack 釘 40 碼 commit SHA,mattpocock-skills 釘 tag
- 說明文件:`GLOSSARY.md`、`docs/`

不放任何上游 skill 內容,也不改任何 SKILL.md。為什麼不用官方 plugin:見 [docs/adr/0001-flat-install-not-plugin.md](docs/adr/0001-flat-install-not-plugin.md)。

## 安裝

需要:Windows、`git`、Windows PowerShell 5.1。

```
git clone https://github.com/guru4tw/j-pockit.git
cd j-pockit
powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1
```

腳本做的事:

1. 照 `versions.lock` 從兩個上游 sparse fetch 需要的子目錄到 `$env:TEMP\j-pockit\`,裝完刪掉
2. skill 整目錄複製到 `~/.claude/skills/<name>/`
3. pstack 的 `docs/`(adapter `harness/claude-code.md`、`guide/`)複製到 `~/.claude/docs/`,`agents/` 兩個 subagent 複製到 `~/.claude/agents/`
4. 同名目錄 / 檔案先整個搬到 `~/.claude/skills_archive/<yyyy-mm-dd>/`(同日重跑加 `-2`、`-3`),不問、不刪
5. 本次安裝名單寫進 `~/.claude/j-pockit-installed.txt`
6. 印出裝了幾個、封存了哪些

不碰的東西:`~/.claude/skills/` 下不屬於這兩套的目錄、`~/.claude/commands/`、`settings.json`、`rules/`、任何專案目錄。上游移除的 skill 不會從本機刪掉,腳本只印提示。

裝完要**開新 session** 才會讀到新 skill。

## 更新

```
powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Update
```

`-Update` 先查上游最新(cursor/plugins `main` HEAD、mattpocock/skills 最大的 `v*` tag),寫回 `versions.lock`,再照新 lock 安裝。lock 有變就自己 commit 並 push:

```
git add versions.lock
git commit -m "Bump versions.lock"
git push
```

其他機器 `git pull` 後跑不帶 `-Update` 的 install,就拿到同一版。不帶 `-Update` 時嚴格照 lock,不連線查最新。

## 裝完後兩步

| 指令 | 頻率 | 做什麼 |
|---|---|---|
| `/setup-pstack` | 一台機器一次 | 依可用模型與 reasoning budget 寫 `~/.claude/rules/pstack-models.md` |
| `/setup-matt-pocock-skills` | 一個 repo 一次 | 設定該 repo 的 issue tracker、triage label、domain doc 位置 |

兩者沒有先後,也不互斥。

v1.3 起 Pocock 把 `CONTEXT.md` 改名 `GLOSSARY.md`(`CONTEXT-MAP.md` → `GLOSSARY-MAP.md`),沒有向下相容。舊專案請自己 `git mv`。

## 兩套合用路線

| 階段 | 用哪套 | 指令 |
|---|---|---|
| 規劃 / 規格 / 票 | Pocock | `/grill-with-docs` → `/to-spec` → `/to-tickets` |
| 執行 | pstack 為主 | `/poteto-mode` 常駐;`/how` 理解既有程式、`/interrogate` 挑戰設計、`/swarm` 平行工作、`/unslop` 修文字。逐票做時 Pocock `/implement` 仍可用(它會叫 `/tdd`、`/code-review`) |
| 驗證 / 審查 / PR | pstack 為主 | 同上;Pocock `/code-review`、`pr` 可並用 |
| 回顧 | Pocock | `/retro`;pstack `/reflect` 可替代 |

圖解見 [docs/workflow.htm](docs/workflow.htm)。

## 同名與排除清單

| 名稱 | 衝突對象 | 裁決 | 理由 |
|---|---|---|---|
| `tdd` | pstack ↔ Pocock | 裝 Pocock 版 | Pocock `/implement` 會叫 `/tdd`,換掉會斷鏈 |
| `teach` | pstack ↔ Pocock | 裝 pstack 版 | pstack `teach` 會串 `how`、`why` |
| `handoff` | Pocock ↔ 本機 `~/.claude/commands/handoff.md` | 不裝 Pocock 版 | 同名時 skill 勝過 command,會蓋掉本機 Stop hook 用的 `/handoff` |

排除名單寫死在 `install.ps1` 頂端(`$PstackExclude`、`$PocockExclude`)。排除後若兩套還有同名,腳本在複製前直接失敗,要求補排除名單。

Pocock 的 `skills/in-progress/`、`skills/misc/` 不裝。

## 致謝

- **Lauren Tan**(poteto):pstack,MIT。<https://github.com/cursor/plugins/tree/main/pstack>
- **Matt Pocock**:mattpocock-skills,MIT。<https://github.com/mattpocock/skills>
- **Dex Horthy**(HumanLayer):Pocock `pr` skill 註明取材自他的 `show-me`。<https://github.com/humanlayer>

本 repo 只放安裝腳本與說明,不含上游內容。授權:[MIT](LICENSE)。
