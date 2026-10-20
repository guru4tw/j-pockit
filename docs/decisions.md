# 已拍板事項(grilling 紀錄,2026-10-19)

一行一題,user 原話為準。術語定義見 `../GLOSSARY.md`,架構理由見 `adr/`。規格寫完後本檔只當追溯用。

| # | 題 | 結論 |
|---|---|---|
| Q1 | 內容範圍 | 最簡;能依賴上游就不維護副本 |
| Q2 | 安裝模式 | flat:`~/.claude/skills/<name>/`,無 namespace |
| Q3 | tdd / teach | `tdd` 留 Pocock;`teach` 留 pstack |
| Q4→Q7 | Overlay | 零檔。上游 `docs/` → `~/.claude/docs/`、`agents/` → `~/.claude/agents/`;SKILL.md 不改;模型映射交 adapter |
| — | 同名既有 | 先封存到 `~/.claude/skills_archive/<yyyy-mm-dd>/<name>/` 再覆蓋,不詢問 |
| Q5 | Pocock 範圍 | 全 27 個(engineering 20 + productivity 7);frontmatter 照上游,不加 `disable-model-invocation`、不寫 `skillOverrides` |
| Q6 | 其他同名 | Pocock `handoff` 不裝(保留 `~/.claude/commands/handoff.md`),連同 Q3 的 `teach` 共排除 2 個,Pocock 實裝 25、pstack 實裝 55;`owl_check`、`plan-eng-review`、孤兒 `writing-great-skills` 不碰 |
| Q8 | 版本 | `versions.lock` 釘 pstack SHA + Pocock tag;`install -Update` 先更新 lock 再裝 |
| Q9 | Installer | 只 `install.ps1`,ASCII-only,git sparse clone;`install.sh` 需要時再補 |
| Q11 | 文件 | `README.md` 繁中白話(what / 安裝 / 更新 / 兩套合用路線 / 致謝);`docs/workflow.htm` 開發流程圖**用 `/gen_htm` 產**(不是 `/gen_html`),README 連過去 |
| Q12 | GitHub | `guru4tw/j-pockit` private,main;user 網頁建 repo;Claude 做 `git -C H:/ALG_Joe/j-pockit init`、push 前 `python -I H:/ALG_Joe/scan_secrets.py H:/ALG_Joe/j-pockit`、`repos.txt` 加 `j-pockit https://github.com/guru4tw/j-pockit.git` |
| Q13 | v1.3 rename | installer 裝完印一行提醒「v1.3 改用 GLOSSARY.md,舊專案 CONTEXT.md 請自行改名」,不碰專案檔;`Freelance/CONTEXT.md`、`REA/CONTEXT.md` 裝完後由 Claude 改名 |
| Q14 | 兩個 setup | installer 不跑;README 寫裝完後兩步:`/setup-pstack` 一機一次(寫 `~/.claude/rules/pstack-models.md`),`/setup-matt-pocock-skills` 一 repo 一次(改該 repo CLAUDE.md);無順序、不互斥 |
| Q15 | plan-eng-review | 不納入 j-pockit,installer 不碰;更新走 gstack 自家 `setup.ps1` / `gstack-upgrade`,不在本案範圍 |
| 補 | 上游移除 | 上游不再有的 skill 本機不刪,installer 只印一行提示 |
| 補 | 相同仍封存 | 新舊內容逐檔相同時仍照常封存 |
| Q10 | License | repo MIT(Joe);README 一段致謝 Lauren Tan / Matt Pocock / Dex Horthy 附上游連結;不寫 THIRD_PARTY_NOTICES,不搬上游 LICENSE |
