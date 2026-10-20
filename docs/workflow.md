# j-pockit 開發流程:pstack + mattpocock-skills 合用路線

**日期**:2026-10-20  **目的**:一張圖看懂兩套 skill set 在開發流程裡怎麼分工、怎麼接。

> 本檔是 [workflow.htm](workflow.htm) 的 GitHub 版,在 GitHub 網頁直接點開就能看;內容與 `workflow.htm` 相同。

---

<a id="sec-agenda"></a>
## Agenda(章節導覽)

全篇章節一覽,點任一標題直接跳到該節內容。

- [1. 一張圖看懂](#sec-1)
- [2. 設定(一次性)](#sec-2)
- [3. 規劃 / 規格 / 票:Pocock](#sec-3)
- [4. 執行 / 驗證 / 審查 / PR:pstack 為主](#sec-4)
- [5. 回顧](#sec-5)
- [6. 單 session 捷徑](#sec-6)
- [附錄 A. 參考來源(References)](#appendix-a)
- [附錄 B. 技術關鍵字術語表(口語化說明)](#appendix-b)

---

<a id="sec-1"></a>
## 1. 一張圖看懂

分工原則一句話:**想清楚、寫下來、切成票**交給 [mattpocock-skills](#g-mattpocock-skills)(Pocock);**動手、驗證、審查、出 PR**交給 [pstack](#g-pstack)。pstack 自己的說明就寫明它沒有 planning skill<sup>[[1]](#ref-1)</sup>,所以規劃段只能用 Pocock<sup>[[2]](#ref-2)</sup>。

![j-pockit 開發流程圖](workflow.svg)

圖 1:四段流程加一次性設定。藍框用 Pocock、橘框以 pstack 為主;虛線框是全程常駐的 [`/poteto-mode`](#g-poteto-mode),虛線回頭箭號是做下一張票。

---

<a id="sec-2"></a>
## 2. 設定(一次性)

| 指令 | 頻率 | 做什麼 |
|---|---|---|
| [`/setup-pstack`](#g-setup-pstack) | 每台機器一次 | 依可用模型選每個角色用哪個模型、多少 [reasoning budget](#g-reasoning-budget),寫成 [`~/.claude/rules/pstack-models.md`](#g-pstack-models-md)。非 Claude 的模型名在 Claude Code 下由 [adapter](#g-adapter) 退回 session 模型。 |
| [`/setup-matt-pocock-skills`](#g-setup-matt-pocock-skills) | 每個 repo 一次 | 設定該 repo 的 [issue tracker](#g-issue-tracker)、triage label、domain 文件放哪。 |

兩者沒有先後,也不互斥。

---

<a id="sec-3"></a>
## 3. 規劃 / 規格 / 票:Pocock

| 步驟 | 指令 | 產出 |
|---|---|---|
| 1 | [`/grill-with-docs`](#g-grill-with-docs) | 一題一題逼問到計畫沒有模糊處,邊問邊寫 [ADR](#g-adr) 與 [`GLOSSARY.md`](#g-glossary-md)。 |
| 2 | [`/to-spec`](#g-to-spec) | 把剛才討論整理成一份 spec,發到 issue tracker。不再問問題。 |
| 3 | [`/to-tickets`](#g-to-tickets) | 把 spec 切成一組 [tracer-bullet](#g-tracer-bullet) 票,每張標明被哪張擋住。 |

---

<a id="sec-4"></a>
## 4. 執行 / 驗證 / 審查 / PR:pstack 為主

開工前先開 [`/poteto-mode`](#g-poteto-mode),整段都在這個工作風格下做:回覆精簡、刻意分派 [subagent](#g-subagent)、文字去 AI 腔、程式碼保持簡單、做完要驗證。

| 要做什麼 | 指令 | 哪套 |
|---|---|---|
| 改之前先看懂既有程式怎麼跑、東西該放哪層 | [`/how`](#g-how) | pstack |
| 工作量大、可拆:開 N 個平行 worker,收成一份報告 | [`/swarm`](#g-swarm) | pstack |
| 逐票實作 | [`/implement`](#g-implement)(內部叫 [`/tdd`](#g-tdd)、[`/code-review`](#g-code-review)) | Pocock |
| 多個 reviewer 從不同角度挑戰設計或改動 | [`/interrogate`](#g-interrogate) | pstack |
| 依 repo 規範與原始 spec 兩條軸審 diff | `/code-review` | Pocock |
| 寫 PR 說明 | [`pr`](#g-pr) | Pocock |
| 刪掉文字裡的 AI 腔 | [`/unslop`](#g-unslop) | pstack |

> 為什麼 `tdd` 裝 Pocock 版:Pocock 的 `/implement` 是使用者叫的 orchestrator,它會自動叫 [model-invoked](#g-model-invoked) 的 `/tdd`。換成 pstack 版,這條鏈就斷了。

---

<a id="sec-5"></a>
## 5. 回顧

- [`/retro`](#g-retro)(Pocock):對一段開發 session 做回顧。
- [`/reflect`](#g-reflect)(pstack):開三個 review subagent 掃本次對話,把學到的東西落成某個既有 skill 的具體修改。想直接改 skill 時用它。

---

<a id="sec-6"></a>
## 6. 單 session 捷徑

小改動不必走完整條。Pocock 自己建議的短路線是 `/grill-with-docs` → `/implement`<sup>[[2]](#ref-2)</sup>:問清楚就直接做,跳過 spec 與票。執行時照樣可以開 `/poteto-mode`。

---

<a id="appendix-a"></a>
## 附錄 A. 參考來源(References)

| # | 主題 / 用途 | 來源 |
|---|---|---|
| <a id="ref-1"></a>#1 | pstack(Lauren Tan) | [cursor/plugins — pstack](https://github.com/cursor/plugins/tree/main/pstack) |
| <a id="ref-2"></a>#2 | mattpocock-skills(Matt Pocock) | [mattpocock/skills](https://github.com/mattpocock/skills) |
| <a id="ref-3"></a>#3 | Claude Code skill 機制(`disable-model-invocation` 等) | [Claude Code docs — Skills](https://code.claude.com/docs/en/skills) |
| <a id="ref-4"></a>#4 | 本 repo 安裝與排除清單 | [README.md](../README.md) |

---

<a id="appendix-b"></a>
## 附錄 B. 技術關鍵字術語表(口語化說明)

| 關鍵字 | 類別 | 口語化說明 / 來源# |
|---|---|---|
| <a id="g-pstack"></a>`pstack` | skill set | Lauren Tan 的 56 個 skill,偏執行、驗證、審查。j-pockit 裝其中 55 個(不裝 `tdd`)。 [[1]](#ref-1) |
| <a id="g-mattpocock-skills"></a>`mattpocock-skills` | skill set | Matt Pocock 的 skill 集,偏規劃、寫 spec、切票。j-pockit 裝 engineering + productivity 共 25 個。 [[2]](#ref-2) |
| <a id="g-setup-pstack"></a>`/setup-pstack` | pstack skill | 一台機器跑一次,決定 pstack 各角色用哪個模型、給多少推理預算。 [[1]](#ref-1) |
| <a id="g-reasoning-budget"></a>`reasoning budget` | 設定值 | 模型每次可以花多少推理量。pstack 分 unlimited / large / medium / small 四檔。 [[1]](#ref-1) |
| <a id="g-pstack-models-md"></a>`~/.claude/rules/pstack-models.md` | 檔案 | `/setup-pstack` 寫出的 rule 檔,每個專案都會套用,蓋過 skill 內建的模型預設。 [[1]](#ref-1) |
| <a id="g-adapter"></a>`adapter` | pstack 文件 | `~/.claude/docs/harness/claude-code.md`,把 pstack 原本給 Cursor 的寫法對應到 Claude Code(工具名、模型名、檔案路徑)。每個 pstack skill 開頭都會叫你先讀它。 [[1]](#ref-1) |
| <a id="g-setup-matt-pocock-skills"></a>`/setup-matt-pocock-skills` | Pocock skill | 每個 repo 跑一次,告訴 Pocock 的 skill 這個 repo 的票開在哪、label 怎麼叫、文件放哪。 [[2]](#ref-2) |
| <a id="g-issue-tracker"></a>`issue tracker` | 概念 | 放 spec 與票的地方,可以是 GitHub Issues,也可以是 repo 裡一張票一個檔。 [[2]](#ref-2) |
| <a id="g-grill-with-docs"></a>`/grill-with-docs` | Pocock skill | 對計畫連續追問,問到沒有模糊處,同時把決定寫成 ADR 與術語表。 [[2]](#ref-2) |
| <a id="g-adr"></a>`ADR` | 文件類型 | Architecture Decision Record,一個重要決定一份短文件:當時的情況、選了什麼、為什麼。 [[2]](#ref-2) |
| <a id="g-glossary-md"></a>`GLOSSARY.md` | 文件 | 專案術語表。Pocock v1.3 起由 `CONTEXT.md` 改名而來,舊專案要自己改名。 [[2]](#ref-2) |
| <a id="g-to-spec"></a>`/to-spec` | Pocock skill | 把目前對話整理成 spec 發到 issue tracker,只做彙整不再訪談。 [[2]](#ref-2) |
| <a id="g-to-tickets"></a>`/to-tickets` | Pocock skill | 把計畫或 spec 切成一組票,每張寫明被哪幾張擋住。 [[2]](#ref-2) |
| <a id="g-tracer-bullet"></a>`tracer-bullet` | 切票方法 | 每張票都是從頭到尾打通的一條細路徑(UI 到資料都碰一點),做完就能跑、能驗,而不是按層切。 [[2]](#ref-2) |
| <a id="g-poteto-mode"></a>`/poteto-mode` | pstack skill | pstack 的常駐工作風格:回覆精簡、刻意用 subagent、文字去 AI 腔、程式簡單、做完要驗證。 [[1]](#ref-1) |
| <a id="g-subagent"></a>`subagent` | Claude Code 機制 | 主對話派出去做一件事的子代理,有自己的 context,只把結論帶回來。 [[3]](#ref-3) |
| <a id="g-how"></a>`/how` | pstack skill | 解釋某個子系統怎麼運作、資料怎麼流、東西該放哪個 package / 哪一層。改程式前先跑。 [[1]](#ref-1) |
| <a id="g-swarm"></a>`/swarm` | pstack skill | 同時開 N 個平行 worker 做同一類工作,全部收回後合成一份報告。 [[1]](#ref-1) |
| <a id="g-implement"></a>`/implement` | Pocock skill | 照 spec 或票實作一件工作;使用者手動叫,內部會叫 `/tdd`、`/code-review`。 [[2]](#ref-2) |
| <a id="g-tdd"></a>`/tdd` | Pocock skill | 測試先行:先寫會失敗的測試,再寫剛好讓它過的程式,再整理。 [[2]](#ref-2) |
| <a id="g-code-review"></a>`/code-review` | Pocock skill | 從某個基準點起的改動,分「是否符合 repo 規範」與「是否符合原始 spec」兩條軸審,兩個 subagent 平行跑。 [[2]](#ref-2) |
| <a id="g-interrogate"></a>`/interrogate` | pstack skill | 找多個 reviewer 各從一個角度挑戰改動,專找盲點。 [[1]](#ref-1) |
| <a id="g-pr"></a>`pr` | Pocock skill | 寫 PR 說明。取材自 Dex Horthy(HumanLayer)的 `show-me`。 [[2]](#ref-2) |
| <a id="g-unslop"></a>`/unslop` | pstack skill | 把文字裡一看就是 AI 寫的痕跡刪掉。 [[1]](#ref-1) |
| <a id="g-model-invoked"></a>`model-invoked` | skill 類型 | 模型可以自己判斷要叫的 skill。反過來,frontmatter 寫 `disable-model-invocation: true` 的只能由使用者打 `/名字` 叫。Pocock 規定使用者叫的可以叫模型叫的,反向不行。 [[2]](#ref-2) [[3]](#ref-3) |
| <a id="g-retro"></a>`/retro` | Pocock skill | 對一段開發 session 做回顧。 [[2]](#ref-2) |
| <a id="g-reflect"></a>`/reflect` | pstack skill | 開三個 review subagent 掃本次對話,把心得落成既有 skill 的具體修改。 [[1]](#ref-1) |
