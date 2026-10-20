# j-pockit 開發流程:pstack + mattpocock-skills 合用指南

**日期**:2026-10-20    **目的**:讓第一次用的人直接接上兩套 skill。每一段該叫誰、重要 skill 實際在做什麼、pstack 怎麼解 AI 使用者的痛點、作者踩過的坑怎麼避開、兩套怎麼搭著用。

> 本檔是 [workflow.htm](workflow.htm) 的 GitHub 版,在 GitHub 網頁直接點開就能看;內容與 `workflow.htm` 相同。

---

<a id="sec-agenda"></a>
## Agenda(章節導覽)

全篇章節一覽,點任一標題直接跳到該節內容。

- [1. 一張圖看懂](#sec-1)
- [2. j-pockit 要解決什麼:兩套各補哪個缺口](#sec-2)
- [3. 設定(一次性)](#sec-3)
- [4. 規劃 / 規格 / 票:Pocock](#sec-4)
  - [4.1 主流程](#sec-4-1)
  - [4.2 /grill-with-docs:逼問加留紙本](#sec-4-2)
  - [4.3 /to-spec 與 /to-tickets](#sec-4-3)
  - [4.4 /implement 與 /implement-spec](#sec-4-4)
  - [4.5 模型自己叫的三個:/tdd、/code-review、pr](#sec-4-5)
  - [4.6 支線入口:修 bug、整理 issue、超大工作](#sec-4-6)
  - [4.7 其他 Pocock skill 速查](#sec-4-7)
  - [4.8 context 什麼時候清:階段邊界五選一](#sec-4-8)
- [5. 執行 / 驗證 / 審查:pstack](#sec-5)
  - [5.1 /poteto-mode 怎麼運作](#sec-5-1)
  - [5.2 23 個 playbook 速查](#sec-5-2)
  - [5.3 先看懂:/how、/why、/teach、/recall](#sec-5-3)
  - [5.4 設計:/architect、/arena、/swarm、/interrogate](#sec-5-4)
  - [5.5 寫與清:/unslop、/no-comments、/technical-writing](#sec-5-5)
  - [5.6 驗證:證明做對了](#sec-5-6)
  - [5.7 長跑與夜跑](#sec-5-7)
  - [5.8 換個說法、找路](#sec-5-8)
- [6. 回顧與改進環境](#sec-6)
- [7. pstack 怎麼解 AI 使用者的痛點](#sec-7)
- [8. 別重踩作者的坑](#sec-8)
  - [8.1 pstack 作者列的 14 個坑](#sec-8-1)
  - [8.2 Pocock 列的坑](#sec-8-2)
- [9. 善用技巧](#sec-9)
  - [9.1 prompt 五要素](#sec-9-1)
  - [9.2 用原則名當方向盤](#sec-9-2)
  - [9.3 兩套怎麼接,不打架](#sec-9-3)
  - [9.4 控制成本](#sec-9-4)
- [10. 在 Claude Code + j-pockit 扁平安裝下的差異](#sec-10)
- [11. 情境速查與單 session 捷徑](#sec-11)
- [附錄 A. 參考來源(References)](#appendix-a)
- [附錄 B. 技術關鍵字術語表(口語化說明)](#appendix-b)

---

<a id="sec-1"></a>
## 1. 一張圖看懂

分工原則一句話:**想清楚、寫下來、切成票**交給 [mattpocock-skills](#g-mattpocock-skills)(下稱 Pocock);**動手、驗證、審查、出 PR**交給 [pstack](#g-pstack)。pstack 自己的說明就寫明它沒有 planning skill<sup>[[5]](#ref-5)</sup>,所以規劃段用 Pocock<sup>[[2]](#ref-2)</sup>。

![j-pockit 開發流程圖](workflow.svg)

圖 1:四段流程加一次性設定。藍框用 Pocock、橘框以 pstack 為主;虛線框是 [`/poteto-mode`](#g-poteto-mode) 管的範圍(在 Claude Code 下它不會自己一直開著,換任務要重打,見第 10 節),虛線回頭箭號是做下一張票。

---

<a id="sec-2"></a>
## 2. j-pockit 要解決什麼:兩套各補哪個缺口

兩套 skill 各自完整,但重心不同。Pocock 強在**人和 AI 先對齊**:把模糊的想法逼問清楚、用同一套名詞、寫成 spec、切成每張都能單獨驗的票。pstack 強在**AI 動手時的紀律**:改之前先看懂、設計多做幾個比較、讓不同模型互相挑錯、做完拿證據、長時間跑留決策紀錄。

| 面向 | Pocock | pstack |
|---|---|---|
| 核心信念 | 先對齊理解;好的[回饋迴圈](#g-feedback-loop)就是 skill 本身 | 做完要能證明;第一個設計通常不是最好的 |
| 叫法 | 使用者叫的 orchestrator,內部再叫[模型自己叫的](#g-model-invoked) discipline | 幾乎全部設了 [`disable-model-invocation`](#g-disable-model-invocation),只能由你打指令,再由 `/poteto-mode` 統一調度 |
| 入口 | [`/ask-matt`](#g-ask-matt):只告訴你該叫哪個,不會替你執行 | `/poteto-mode`:挑一套 [playbook](#g-playbook) 照步驟做;[`/poteto-help`](#g-poteto-help):只回答該用哪個 |
| 規劃 | 逼問 → spec → 票 | 刻意沒有;用 prototype 回答問題,設計定了才寫 plan |
| 驗證 | 測試先行 + 兩軸 code review | 看真東西、專案自己的驗證 skill、效能數字七問、影響範圍檢查 |
| 回顧 | 改善 agent 的工作環境 | 把心得改進 skill;讓同一個錯在結構上不可能再犯 |

簡單說:**Pocock 回答「要做什麼、做到哪算完」,pstack 回答「怎麼做才不出包、怎麼證明做對了」。**

j-pockit 做的事很少:把兩套扁平裝進 `~/.claude/skills/`,用短名直接叫(`/how`,不是 [`/pstack:how`](#g-plugin-prefix)),版本釘死,並處理三個同名衝突<sup>[[4]](#ref-4)</sup>:

| 名稱 | 裝哪版 | 理由 |
|---|---|---|
| [`/tdd`](#g-tdd) | Pocock | Pocock 的 [`/implement`](#g-implement) 會自動叫 `/tdd`;換成 pstack 版這條鏈會斷 |
| [`/teach`](#g-teach) | pstack | pstack 版會串 [`/how`](#g-how)、[`/why`](#g-why) |
| [`/handoff`](#g-handoff) | 都不裝 Pocock 版 | 同名時 skill 會蓋掉本機的 `/handoff` 指令 |

為什麼不用官方 plugin 方式安裝,見 [ADR 0001](adr/0001-flat-install-not-plugin.md)<sup>[[9]](#ref-9)</sup>。

---

<a id="sec-3"></a>
## 3. 設定(一次性)

| 指令 | 頻率 | 做什麼 |
|---|---|---|
| [`/setup-pstack`](#g-setup-pstack) | 每台機器一次 | 依可用模型決定每個角色用哪個模型、多少 [reasoning budget](#g-reasoning-budget),寫成 [`~/.claude/rules/pstack-models.md`](#g-pstack-models-md)。最後會問要不要建專案的驗證 skill,**建議答應**(見 5.6)。 |
| [`/setup-matt-pocock-skills`](#g-setup-matt-pocock-skills) | 每個 repo 一次 | 一次問一題、每題附建議答案:(A) [issue tracker](#g-issue-tracker) 用 GitHub、GitLab 還是 repo 內的 markdown;(B) triage label 怎麼叫;(C) domain 文件放哪。結果寫進 [`docs/agents/`](#g-docs-agents),並在既有的 [`CLAUDE.md`](#g-claude-md) 加一段 `## Agent skills`。 |

兩者沒有先後,也不互斥。補充三點:

- `/setup-pstack` 是 pstack 裡唯一模型可以自己叫的 skill。沒跑過也能用,各角色會用 skill 內建的預設模型。
- 選 local markdown 當 issue tracker 時,spec 和票放在 [`.scratch/<feature>/`](#g-scratch),一張票一個檔,檔內有 `Status:`、`Blocked by:` 兩行。
- Pocock v1.3 起 `CONTEXT.md` 改名 [`GLOSSARY.md`](#g-glossary-md),沒有向下相容,舊專案要自己 `git mv`。

---

<a id="sec-4"></a>
## 4. 規劃 / 規格 / 票:Pocock

Pocock 的 skill 分兩種<sup>[[7]](#ref-7)</sup>:你打名字才會跑的 orchestrator,和模型判斷需要時自己叫的 discipline。規則是 orchestrator 可以叫 discipline,反過來不行。所以 [`/grill-with-docs`](#g-grill-with-docs) 本身很薄,真正做事的是它叫的 [`grilling`](#g-grilling) 和 [`domain-modeling`](#g-domain-modeling)。

<a id="sec-4-1"></a>
### 4.1 主流程

| 步驟 | 指令 | 什麼時候 | 產出 |
|---|---|---|---|
| 1 | `/grill-with-docs`(不在 repo 裡就用 [`/grill-me`](#g-grill-me)) | 有新想法、計畫還模糊 | 共同理解、[ADR](#g-adr)、`GLOSSARY.md` |
| 2(選用) | [`/prototype`](#g-prototype) | 有問題要跑一下才知道答案 | 丟棄式程式 + 結論 |
| 3 | [`/to-spec`](#g-to-spec) | 要跨多個 session 才做得完 | 一份 spec |
| 4 | [`/to-tickets`](#g-to-tickets) | spec 定了 | 一組 [tracer-bullet](#g-tracer-bullet) 票 |
| 5 | `/implement`(逐票)或 [`/implement-spec`](#g-implement-spec)(整份平行) | 開工 | commit |
| 6 | [`/retro`](#g-retro) | 做完,尤其做得不順時 | 環境改善建議 |

context 的規矩:步驟 1、3、4 留在同一段不中斷的 context 裡;prototype 另開 session 做,做完把結論帶回來;每個 `/implement` 開新的 context。

<a id="sec-4-2"></a>
### 4.2 /grill-with-docs:逼問加留紙本

這是整套最重要的一步。它的做法:

- 把計畫看成一棵決策樹。每一輪把**前置條件都已決定**的那一層問題([frontier](#g-frontier))一次列出來,每題附它建議的答案,你只要逐題回「同意」或改。
- **查事實是 AI 的事,做決定是你的事。**能從程式碼查到的,它派 [subagent](#g-subagent) 去查,不會拿來問你。
- 邊問邊由 `domain-modeling` 更新 `GLOSSARY.md`:挑戰跟術語表衝突的用詞、把含糊的詞說死(「account」到底是 Customer 還是 User)、編邊界情境來測、拿你說的去對程式碼。難回頭又有真實取捨的決定才寫 ADR。
- 問到沒有待決問題才停,而且**你確認理解一致之前不會動手**。

用法提示:用 `/grill-with-docs` 不要用 `/grill-me`,前者多留了紙本,下一個 session 讀得到。

<a id="sec-4-3"></a>
### 4.3 /to-spec 與 /to-tickets

`/to-spec` 只做彙整,不再問問題。它先用術語表的名詞讀 repo、遵守既有 ADR,再跟你確認測試要放在哪幾個 [seam](#g-seam)(「越高越少越好,理想是一個」),然後寫出:問題、解法、一長串 user story、實作決定、測試決定、不做什麼。spec 裡**不寫檔案路徑和程式碼**,因為那些很快就過時。

`/to-tickets` 把 spec 切成票。每張票是一條從頭打通到尾的細路徑(每一層都碰一點),做完就能展示、能驗,而且一個新 context 裝得下。需要先整理的「prefactoring」排最前面。大範圍重構例外,改用 [expand-contract](#g-expand-contract) 排序。它會跟你來回確認切法和誰擋誰,你點頭才發票,每張標 [`ready-for-agent`](#g-ready-for-agent)。

注意:`/to-spec` 和 `/to-tickets` 會直接發到 issue tracker,選 GitHub 就會開出真的 issue。沒跑過 `/setup-matt-pocock-skills` 時,多數 Pocock skill 會先停下來叫你去跑。

<a id="sec-4-4"></a>
### 4.4 /implement 與 /implement-spec

|  | `/implement` | `/implement-spec` |
|---|---|---|
| 範圍 | 一張票(或單 session 的整件事) | 整份 spec 的所有票 |
| 誰開車 | 你逐張叫,每張之間 [`/clear`](#g-clear) | AI 當調度者,把票當成任務圖 |
| 做法 | 在事先講好的 seam 用 `/tdd`;常跑 typecheck 和單一測試檔,最後跑全套;跑 [`/code-review`](#g-code-review);commit 到目前 branch | 開一條 [integration branch](#g-integration-branch);能做的票各派一個背景 subagent、各用一個 [worktree](#g-worktree);另有一個 merger 收合;全部做完跑 `/code-review` 再修 |
| 適合 | 想自己盯每一步 | 票多、彼此相依清楚,想讓 AI 平行做 |

<a id="sec-4-5"></a>
### 4.5 模型自己叫的三個:/tdd、/code-review、pr

- `/tdd`:先寫一個會失敗的測試,再寫剛好讓它過的程式,一個一個來,不先把測試全寫完。測試只放在事先講好的 seam,只在系統邊界(外部 API、時間、亂數)mock,**不 mock 自己的 module**。重構不在這個迴圈裡,交給 code review。介面形狀本身有疑問時會叫 [`codebase-design`](#g-codebase-design)。
- `/code-review`:對某個基準點以來的 diff,分兩條軸各派一個 subagent 平行審。**Standards** 軸看 repo 規範(加 12 個 Fowler code smell 當底線),**Spec** 軸看有沒有照原始 spec 做。兩軸結果分開列,不合併排序。基準點(`main` 或某個 SHA)沒給會問你;找不到 spec 就略過 Spec 軸。
- [`pr`](#g-pr):寫 PR 說明時自動套用。三段:最小的一張圖說重點、改前改後的證據(截圖最好,測試輸出次之)、合併風險(能不能回頭、影響多大)。

<a id="sec-4-6"></a>
### 4.6 支線入口:修 bug、整理 issue、超大工作

| 情況 | 指令 | 重點 |
|---|---|---|
| 東西壞了、很慢、測試失敗 | [`/diagnosing-bugs`](#g-diagnosing-bugs) | 第一步一定是建一個能穩定重現失敗、跑得快、AI 自己能跑的回饋迴圈。**沒有能變紅的指令,就不准開始猜原因。**再來是縮小重現、列 3 到 5 個可推翻的假設(測之前先給你看排序,你可以改;你不在就照它的排序)、一次只改一個變數加 log、有合適的 seam 就先寫回歸測試(沒有的話這本身就是發現,要記下來)、清掉 debug log。 |
| issue 堆積 | [`/triage`](#g-triage) | 每個 issue 一個類別(bug / enhancement)、一個狀態(五個標準 label)。先查是否重複、是否已被拒絕過,再重現。AI 發的留言一律加免責聲明。`/to-tickets` 產的票不要再 triage。 |
| 超大、霧很濃、一個 session 裝不下 | [`/wayfinder`](#g-wayfinder) | 畫一張由決策票組成的地圖,一個 session 只解一張票(研究票除外)。它只做規劃不做實作,最後回到主流程的 `/to-spec`。範圍清楚的功能不要用它。 |

<a id="sec-4-7"></a>
### 4.7 其他 Pocock skill 速查

| 指令 | 叫法 | 什麼時候用 |
|---|---|---|
| [`/improve-codebase-architecture`](#g-improve-codebase-architecture) | 你叫 | 有空檔時做架構健檢。產出一份 HTML 報告列出可「加深」的模組,你選一個再進逼問;結果回流 `/grill-with-docs`。 |
| `/prototype` | 模型叫 | 要驗證狀態邏輯(單一 HTML 檔 + 可點的按鈕)或 UI 長相(同一頁 3 到 5 個結構不同的變體,用 `?variant=` 切)。答案寫進正式程式碼並從 issue 指過去;原型程式碼本身留在 `prototype/<name>` branch 當一手資料。 |
| [`/research`](#g-research) | 模型叫 | 派背景 agent 只查一手來源,寫成一份附引用的 markdown。 |
| `codebase-design` | 模型叫 | [deep module](#g-deep-module) 的詞彙與原則:小介面藏大量行為、介面就是測試面。「Design it twice」會派 3 個以上 subagent 各用不同限制設計介面再比較。 |
| [`/to-questionnaire`](#g-to-questionnaire) | 你叫 | 答案在別人腦袋裡時,產一份問卷給對方填。 |
| [`/wait-what`](#g-wait-what) | 你叫 | AI 上一則沒講懂,要它用簡化英文加術語表的詞重講。 |
| [`wizard`](#g-wizard) | 模型叫 | 設 CI secret、第三方後台這類 AI 做不了的手動步驟,產一支一步一步帶你做的 bash 腳本。 |
| [`writing-for-agents`](#g-writing-for-agents) | 模型叫 | 寫給 agent 讀的文件(skill、`CLAUDE.md`)的寫法參考;`/retro` 會用到。 |

<a id="sec-4-8"></a>
### 4.8 context 什麼時候清:階段邊界五選一

Pocock 把 context 管理當成流程的一部分。只在[階段邊界](#g-phase-boundary)做決定,照順序問,第一個「是」就照做:

1. **繼續**:下一階段需要這段對話當一手資料,或 [smart zone](#g-smart-zone)(約 150k token)還夠。
2. `/clear`:目前的 context 跟下一步無關。
3. `/handoff`:換工具、換目錄、交給同事,或中途分出一條支線。
4. subagent:那件事 AI 自己做得完。
5. [`/compact`](#g-compact):預設選項,但不是第一個想到的。

理由:除了「繼續」,其他做法都會把一手資料變成有損的摘要。**階段中途 compact 最傷**,新 session 會很有自信地照著被壓扁的摘要做錯。

---

<a id="sec-5"></a>
## 5. 執行 / 驗證 / 審查:pstack

pstack 是 Lauren Tan(poteto)的工作方式<sup>[[1]](#ref-1)</sup><sup>[[5]](#ref-5)</sup>。幾乎每個 skill 都要你親手打指令;實務上你只要記住一個入口 `/poteto-mode`,其他 skill 由它在需要時拉進來。

<a id="sec-5-1"></a>
### 5.1 /poteto-mode 怎麼運作

1. 讀 Claude Code 的 [adapter](#g-adapter),把 Cursor 的工具名、模型名換成這裡的。
2. 把你的任務對到 23 套 playbook 之一,**把那套的步驟原樣抄成待辦清單**。跳過的步驟要寫 `skip: <理由>`,所以你看得到它省略了什麼。都對不上或範圍很大時,改走 [`/figure-it-out`](#g-figure-it-out) 現場設計一套。
3. 依觸發表自動拉其他 skill:非小改動先 `/how`;程式碼跨函式邊界就 [`/architect`](#g-architect);設計有爭議就 [`/interrogate`](#g-interrogate);寫文字套 [`/unslop`](#g-unslop);review 前跑 [`/no-comments`](#g-no-comments);有效能數字就 [`/benchmark-checklist`](#g-benchmark-checklist);長時間或無人看管就 [`/show-me-your-work`](#g-show-me-your-work)。
4. 套用到的每條 [principle](#g-principle),回覆裡要點名,並說它改變了哪個決定。
5. 可回頭的工作直接做不問你;只在 force-push 共用 branch、部署、刪資料、對客戶發訊息前停下來。要問你「選哪個做法」之前,跑一下就知道答案的先用 prototype 回答。它也被要求該反對時就反對。
6. 分派 subagent 用 [`poteto-agent`](#g-poteto-agent),每件事開新的,主 agent 要親自看過每個 diff。
7. 回覆風格:短句、不用破折號、每個說法標明是量到的、推論的還是猜的。

<a id="sec-5-2"></a>
### 5.2 23 個 playbook 速查

你不必背 playbook 名字,用平常的話描述任務,`/poteto-mode` 會自己對。下表方便你知道有哪些路可走,以及用什麼說法會被導到那裡。

| 類別 | playbook | 做什麼 / 觸發說法 |
|---|---|---|
| 弄清楚 | Investigation | 唯讀調查,附引用的答案。說「don't change any code yet」。 |
| 弄清楚 | Runtime forensics | 對活著的程式加量測,不靠讀原始碼猜。 |
| 弄清楚 | Trace forensics | 從已抓到的 profile、trace、heap snapshot 診斷。 |
| 弄清楚 | Session pickup | 接手別人(或上週的你)做到一半的 branch,讀決策紀錄,不重做已完成的。 |
| 改程式 | Bug fix | 先在真實介面重現,用執行期證據找根因,再修。說「repro first」。 |
| 改程式 | Feature | 從具名的資料形狀開始做新功能。 |
| 改程式 | Refactoring | 結構變、行為不變。說「zero behavior change」。 |
| 改程式 | Perf issue | 每個修正都要對到 baseline 量測。 |
| 改程式 | Hillclimb | 對一個指標持續改進:假設、改、量、記錄,每個進步一個 commit。 |
| 改程式 | Visual parity | 新舊畫面要一模一樣,用影像比對判定。 |
| 設計與規劃 | Prototype | 丟棄式草稿回答設計問題,附截圖或時間給你比。 |
| 設計與規劃 | Multi-phase plan | 設計定了之後寫 plan:一個 PR 一節,每節結尾是證明它有效的方法。只寫不做。 |
| 出貨 | Opening a PR | 每套 playbook 結尾都跑,開 PR。 |
| 出貨 | Babysit | 把 PR 顧到可合併(review thread、CI)。遇到衝突只回報哪條 branch 要 rebase,不自己解。 |
| 出貨 | Shipping | 每個 PR 單獨驗,只合從根算起連續驗過的那段。 |
| 出貨 | Autopilot-full | 一串互不相依的 PR,各有負責的 subagent 從建到合。 |
| 出貨 | Autopilot-stack | 一條線性堆疊的 PR,交給你審和合。 |
| 長跑 | Autonomous run | 給一個可檢查的完成條件,一路做到條件成立。 |
| 長跑 | Orchestrate | 跨好幾天、很多 PR 的大計畫,一個調度者管一群 subagent。 |
| 長跑 | Pause safely | 你說要暫停時,收尾或退回目前這步、存檔、寫接手說明。 |
| 維護 | Authoring a skill | 寫新 skill。「拿不準就刪」。 |
| 維護 | Eval | 改 skill 或 prompt 前先做盲測實驗,避免「知道在被測」影響結果。 |
| 維護 | Worktree cleanup | 清掉已合併或放棄的 worktree。 |

23 套都對不上時,`/poteto-mode` 改叫 `/figure-it-out` 現場設計一套。

<a id="sec-5-3"></a>
### 5.3 先看懂:/how、/why、/teach、/recall

AI 出錯通常是兩種:誤會你要什麼,或缺 context 就動手。這四個解第二種,而且都逼 AI 用你能檢查的話解釋自己<sup>[[5]](#ref-5)</sup>。

| 指令 | 回答什麼 | 做法 | prompt 範例 |
|---|---|---|---|
| `/how` | 程式現在怎麼跑、新東西該放哪 | 小問題直接讀;大子系統先派 2 到 4 個唯讀 explorer 分頭看,再由一個 explainer 整合。輸出:概觀、關鍵概念、流程、東西在哪、陷阱。 | `/how do we dedupe notifications?` |
| `/why` | 為什麼長這樣、這個數字哪來的 | 從 git blame / log 起頭,再依你接了哪些 [MCP](#g-mcp) 平行查 issue、文件、聊天、監控等 7 類證據。分開「直接證據」和「推論」,查無結果也照實報。 | `/why was the retry limit set to five?` |
| `/teach` | 讓你真的懂 | 跑 `/how` 和 `/why`,用白話加逐步長大的圖解釋。加一句「convince me」,解釋就變成你能檢驗的論證。 | `/teach me how this PR changes retries. convince me it fixes the cause.` |
| [`/recall`](#g-recall) | 你自己最近做到哪 | 翻你最近的對話紀錄、PR、branch,整理成現況、各線狀態、問題、下一步。 | `/recall catch me up on the export work from last week` |

坑:別因為「AI 反正會讀程式」就跳過這步。沒先建好心智模型就動手,常會在第一個看起來合理的地方修症狀。

<a id="sec-5-4"></a>
### 5.4 設計:/architect、/arena、/swarm、/interrogate

- `/architect`:先跑 `/how`(搬動擁有權時加 `/why`)打底,再用 [`/arena`](#g-arena) 產出至少兩個結構不同的設計草稿,每個都先寫「呼叫端怎麼用」,再寫型別與簽名。預設設計完直接實作;要先看設計就說「with checkpoint」。實作中如果到處出現同樣的繞路、只能靠 `any` 或強制轉型才編得過,它會當成設計錯了,砍掉重來。
- `/arena`:N 個 subagent 做同一份題目,各寫在自己的目錄或 worktree;一個唯讀評審(盡量用不同[模型家族](#g-model-family))照評分表打分;主 agent 選一個當底,再從每個落選者嫁接一兩個好點子(候選收斂時就不用嫁接),最後驗證。決定很貴時就要求更多候選。
- [`/swarm`](#g-swarm):把工作切成互不相干的片,一片一個 worker,各回 PASS / ISSUES / BLOCKED,最後一份報告。缺結果算缺口,不算通過。**要覆蓋面用 swarm,要比設計用 arena。**
- `/interrogate`:把同一個 diff 交給不同模型家族的 reviewer。重點是模型差異,不是角色扮演;兩個模型各自都抓到的問題最可信。主 agent 把結果分成 Act on / Consider / Noted / Dismissed,每個駁回都附理由,**不會自動套用**。駁回的也要看,你可以推翻。

多少設計工作才夠?pstack 給的[設計階梯](#g-design-ladder)<sup>[[5]](#ref-5)</sup>:

| 情況 | 用 |
|---|---|
| 小改動、做完了但不放心 | 只跑 `/interrogate` |
| 跨函式邊界或搬擁有權 | `/architect`(會帶上 `/arena`) |
| 單一決定:命名、格式、演算法 | 直接 `/arena` |
| 覆蓋矩陣、平行檢查、競速 | `/swarm` |
| 跑一下就知道答案的問題(版面、時間、做法) | prototype,不要辯論 |
| 有爭議、事後很難改的設計 | `/architect`,出貨前再 `/interrogate` |
| 跨好幾個 PR | 設計定了之後寫 plan |

`/poteto-mode` 已經會照這個階梯自動做。你直接叫它們,通常是想要比預設更多或更少的檢查。

<a id="sec-5-5"></a>
### 5.5 寫與清:/unslop、/no-comments、/technical-writing

- `/tdd`:j-pockit 裝的是 Pocock 版(見 4.5)。pstack 的 Bug fix playbook 說「用 tdd skill」時,拿到的就是這一版。
- `/unslop`:依一份編號清單刪掉 AI 腔,例如誇張詞彙、破折號、句中冒號、粗體開頭的條列、聊天機器人用語、抽象比喻名詞。`/poteto-mode` 每則回覆都會套。
- `/no-comments`:review 前派 [`comment-sicko`](#g-comment-sicko)(一個痛恨註解的 subagent)掃 diff。主 agent 會審它的判斷;描述限制的註解,會提議改成型別、執行期檢查、測試或 lint;你同意就改完再刪註解,不同意也照刪,並回報這個限制還沒有被保護。
- [`/technical-writing`](#g-technical-writing):文件、RFC、README、PR 說明、commit message。一份文件只選一種模式(教學、操作、參考、解說),目標是「累了的工程師第一遍就看懂」。

<a id="sec-5-6"></a>
### 5.6 驗證:證明做對了

pstack 最核心的一條原則是 [prove-it-works](#g-prove-it-works):看真正的東西,不看替代指標;「編得過」「測試綠了」都不算證明。驗證失敗時,先懷疑是觀察方法錯了。

| 指令 | 做什麼 | 結果 |
|---|---|---|
| [`/create-verification-skill`](#g-create-verification-skill) | 為專案產生 [`verify-<app>`](#g-verify-app) skill:怎麼啟動、怎麼自檢、怎麼操作、怎麼留證據、怎麼收拾,外加一份功能地圖。它會實際跑一遍確認證據留得下來。`/setup-pstack` 跑完會主動提議做這一步。 | 專案內的 skill 目錄 |
| [`/maintain-verification-skill`](#g-maintain-verification-skill) | App 改了,功能地圖就會過時。逐項重驗、補漏 | clean / changed / blocked 三選一 |
| [`/create-formal-verification-skill`](#g-create-formal-verification-skill) | 併發、重試、狀態機、parser 這類測試很難碰到的性質,用 [TLA+](#g-tla) 之類做形式驗證 | 形式模型 + 檢查腳本 |
| `/benchmark-checklist` | 回報或依效能數字行動前問 7 題:為什麼不是兩倍?有調過嗎?有超限嗎?有出錯嗎?能重現嗎(交替跑 5 次以上)?端到端有差嗎?工作真的有做嗎? | 變快 / 變慢 / 沒有可量測差異 / 無法判定,附數字、單位、次數、範圍、瓶頸 |
| [`/blast-radius`](#g-blast-radius) | 小 diff 不放心時,找它會在別處弄壞什麼。重點不是列呼叫者,而是 grep 找不到的那種(版本、時序、wire format、DB 欄位、feature flag),並找出「它安全是因為哪一個事實」,寫腳本跑真程式證明 | 風險清單(含 `file:line`)、已排除項、合併前要做的事 |

<a id="sec-5-7"></a>
### 5.7 長跑與夜跑

能自己驗證的 agent,才能放著讓它跑。放手前先確認四件事都成立<sup>[[5]](#ref-5)</sup>:

1. 你自己做過一次,或看 agent 做過一次,知道「好」長什麼樣。
2. agent 有你會用的工具和訊號:驗證 skill、profiler、log。
3. 每個階段都會證明自己的成果,不達標能讓整條線停下。
4. 你讀過幾份紀錄,並把重複出現的失敗做成工具、skill 或檢查。

還沒全成立就在旁邊看著跑。夜跑的交代要有:目標、可判定的完成條件(「done means ...」)、獨立的 worktree、事先給的權限(「don't ask me before committing」)、卡住時的出口(「truly stuck 就停下寫原因」),最後用 [`/loop`](#g-loop) 跑到條件成立。

- `/figure-it-out`:先寫出可推翻的完成條件,把工作切成最小單位、風險最高的先做,驗證工具和 baseline 先建。每圈:假設、最小改動、量、留或退。
- `/show-me-your-work`:每個決定記一列到 [`decisions.tsv`](#g-decisions-tsv)(時間、階段、決定、理由、證據、結果),只追加不改,預設只留在本機不 commit。結束時先對照紀錄自我稽核,再請不同模型的 reviewer 看。早上用 `/show-me-your-work catch me up on what you did last night` 驗收。
- 迴圈的節奏:一次改一個東西、驗一次、記一列。沒幫助的改動丟掉。完成條件不准偷偷放寬。

<a id="sec-5-8"></a>
### 5.8 換個說法、找路

| 指令 | 用途 |
|---|---|
| `/poteto-help` | 問「該用哪個 skill」,它只回答,不開工。 |
| [`/sharpen`](#g-sharpen) | 把你的 prompt 改得更深(頂尖專家會補什麼、最原始的資料、具體方法、外部檢查),只回 prompt,不做事。 |
| [`/in-your-own-words`](#g-in-your-own-words) | 開工前要 AI 用自己的話講一遍你的目標和問題,確認沒誤會。 |
| [`/bro`](#g-bro) | 把上一則用白話重講。 |
| [`/ketchup`](#g-ketchup) | 你離開一下回來:只整理這個對話自你上次發言後發生的事,並列出每件等你決定的事,附它的建議和風險。 |

---

<a id="sec-6"></a>
## 6. 回顧與改進環境

| 指令 | 哪套 | 改的對象 | 做法 |
|---|---|---|---|
| `/retro` | Pocock | agent 的工作環境 | 讀這次 session 的紀錄,從 7 類找改進:導航、自動檢查、coding standard、全域 `CLAUDE.md`、工具使用、沒作用的指示(寫了也不改變 agent 行為的規則)、資訊取得。依嚴重度排。 |
| [`/reflect`](#g-reflect) | pstack | skill 本身 | 派三個 reviewer 掃這次對話,整合成 Accepted / Rejected / Backlog,**等你批准**才改 skill。 |
| [`/correct`](#g-correct) | pstack | repo 結構 | 從 commit、revert、review 留言找 agent 一再犯的錯(發生兩次才算一類),在能擋住它的最高層修:架構 → 型別 → lint → 測試,文件最後。每類一個 commit,並證明新檢查能抓到過去真實的錯。 |
| [`/automate-me`](#g-automate-me) | pstack | 你的個人模式 | 從你的對話紀錄歸納工作習慣,產一個你自己的 `<handle>-mode` skill,照 `/poteto-mode` 的形狀。 |

建議用法:做完不順先 `/retro`;同一個錯第二次出現就 `/correct`;覺得某個 skill 本身寫得不好用 `/reflect`;用一陣子後跑 `/automate-me`。另外,**不要在任務做到一半時改 skill**,改了要用 Eval playbook 先測。

---

<a id="sec-7"></a>
## 7. pstack 怎麼解 AI 使用者的痛點

pstack 的做法是把「人得一直盯著的事」寫成 skill 裡固定會跑的步驟。下表左欄是用 AI 寫程式常見的痛,右兩欄是 pstack 的對應。

| 痛點 | pstack 的解法 | 機制 |
|---|---|---|
| AI 誤會你要什麼 | prompt 五要素(9.1)、`/in-your-own-words`、`/sharpen` | 開工前把目標和[完成條件](#g-done-check)說死,再讓 AI 複述 |
| 不懂既有程式就動手,修到症狀 | `/how`、`/why`;Investigation playbook | 非小改動一律先建心智模型;說「don't change any code yet」只出調查結果 |
| 第一個設計就定案 | `/architect`、`/arena`、prototype | 多個候選、交叉評審、選底再嫁接;能跑的問題用跑的回答 |
| 同一個模型自己審自己,盲點一樣 | `/interrogate` | 不同模型家族各審一次,兩邊都抓到才是強訊號;駁回要附理由 |
| 「build 綠了」就說完成 | prove-it-works、`verify-<app>` | 對真正的產物驗證,檢查寫成可重跑的腳本 |
| 效能數字不可信 | `/benchmark-checklist` | 七問找瓶頸、排除量錯東西 |
| 小改動在別處炸開 | `/blast-radius` | 找出「安全靠的那一個事實」並跑程式證明 |
| 文字一股 AI 腔、註解氾濫 | `/unslop`、`/no-comments` | 編號規則逐條掃;另派 subagent 專挑註解 |
| 長跑回來不知道 AI 做了什麼決定 | `/show-me-your-work` | 每個決定一列紀錄 + 異模型 review |
| 離開一下就跟不上 | `/ketchup`、`/recall`、Session pickup | 只整理你沒看到的部分,並列出等你決定的事 |
| 同一個錯一直手動糾正 | `/correct`、encode-lessons-in-structure 原則 | 重複的提醒改成 lint、型別、測試,而不是多寫一段說明 |
| 主對話被大量輸出塞爆 | guard-the-context-window 原則 | 大量讀檔交給 subagent,主對話只留結論 |
| AI 一直問「要繼續嗎?」 | never-block-on-the-human 原則 | 可回頭的事直接做完再給你看;只在不可逆的事前停 |
| 不知道該叫哪個 skill | `/poteto-mode`、`/poteto-help` | 由 playbook 決定步驟,你只描述任務 |

---

<a id="sec-8"></a>
## 8. 別重踩作者的坑

<a id="sec-8-1"></a>
### 8.1 pstack 作者列的 14 個坑

這些是 pstack 指南最後一頁整理的常見錯誤<sup>[[5]](#ref-5)</sup>,右欄是改法。

| # | 坑 | 為什麼會出事 | 改成這樣 |
|---|---|---|---|
| 1 | 在 prompt 裡列一堆 skill 名 | 打亂 playbook 已經排好的步驟順序 | 只講目標和完成條件,讓它挑 |
| 2 | 完成條件模糊(「弄好一點」) | 它不知道何時停,或隨便停 | 寫成能判 pass / fail 的條件 |
| 3 | 先講你對原因的猜測 | AI 被帶著走,去修你猜的地方 | 先請它複述問題,再說你的猜測 |
| 4 | 接受第一個設計 | 鎖死錯的形狀 | 要幾個方案;`/arena` 或 prototype |
| 5 | 打磨沒有程式支撐的 plan | reviewer 會發明永遠不會發生的風險 | prototype 先,plan 最後;`/interrogate` 用在 diff 上 |
| 6 | 多個平行 agent 共用一個 worktree | 互相覆蓋檔案 | 一個 worker 一個 worktree |
| 7 | 還沒信任就開 loop 跑一夜 | 錯的工作做得更快,越滾越大 | 四個條件(5.7)成立才放手 |
| 8 | 相信沒檢查過的數字 | 可能量到別的東西 | `/benchmark-checklist` |
| 9 | 同一個錯一直手動糾正 | 下次換個 session 照犯 | `/correct` |
| 10 | 拿 `/arena` 做覆蓋檢查 | 工具用錯,白花錢做選底嫁接 | 覆蓋用 `/swarm` |
| 11 | 每條 review 意見都接受 | reviewer 不是神,會誤判 | 看 `/interrogate` 的分類和駁回理由,自己判 |
| 12 | 把 [`auto`](#g-auto) 當成模型名 | 它不是某個模型 | 在 Claude Code 下等於不指定模型、用 session 的模型 |
| 13 | build 綠了就回報成功 | 沒看到真正的行為 | 對真產物驗證,附證據 |
| 14 | 憑手感寫 SKILL.md | 寫出 agent 不照做的 skill | 走 Authoring a skill playbook,改前用 Eval 測 |

<a id="sec-8-2"></a>
### 8.2 Pocock 列的坑

- 階段中途 `/compact`,新 session 會照被壓扁的摘要做錯。只在階段邊界決定(4.8)。
- 對 `/to-tickets` 產的票再跑 `/triage`。
- 範圍清楚的功能用 `/wayfinder`;或把地圖直接丟給 `/implement`,跳過 `/to-spec`。
- 沒有能變紅的回饋迴圈就開始猜 bug 原因。回歸測試放在太淺的 seam,只換來假的安心。
- mock 自己的 module、測實作細節、先把測試全寫完再寫程式。
- spec、票裡寫檔案路徑和程式碼;`GLOSSARY.md` 寫實作細節。
- 寫給 agent 的文件用否定句(「不要想大象」反而會想);用正面描述目標。

---

<a id="sec-9"></a>
## 9. 善用技巧

<a id="sec-9-1"></a>
### 9.1 prompt 五要素

| 要素 | 說明 | 例 |
|---|---|---|
| 目標 | 要達成什麼 | 背景工作每幾小時就 timeout,要找出原因 |
| 完成條件 | 能判 pass / fail | done means 連跑 24 小時零 timeout |
| 要看到的證明 | 你要什麼證據才信 | 給我用了哪些資料、各假設的證據 |
| 已知的事 | 你手上有的事實,不是猜測 | 上週升級 DB driver 後開始 |
| 真正的限制 | 不能違反的事 | repro first / don't change any code yet / zero behavior change / let me review before proceeding |

不要寫「怎麼做」和「你猜的原因」。換任務時說「new task」讓它重挑 playbook。後續追問用短句就好,例如「do it」「continue」。

<a id="sec-9-2"></a>
### 9.2 用原則名當方向盤

pstack 的 24 條原則各是一個 skill,`/poteto-mode` 每次會讀索引、套用、在回覆點名。你覺得它方向偏了,直接在 prompt 裡點原則名就能修正,比長篇解釋有效。

| 類別 | 原則(點名時用英文) | 一句話 |
|---|---|---|
| 核心 | Laziness Protocol | 偏向刪除和最小改動 |
| 核心 | Foundational Thinking | 先把核心型別和資料結構做對 |
| 核心 | Redesign from First Principles | 新需求要當成第一天就有來整合 |
| 核心 | Attack the Premise | 同一前提的修法連敗兩次,就去驗前提本身 |
| 核心 | Subtract Before You Add | 先刪死碼和多餘檢查,再往上加 |
| 核心 | Minimize Reader Load | 少層、少隱藏狀態 |
| 核心 | Outcome-Oriented Execution | 重寫時直奔目標架構,不留過渡相容層 |
| 核心 | Experience First | 使用者體驗優先於實作方便 |
| 核心 | Exhaust the Design Space | 沒前例的設計做 2 到 3 個原型比較 |
| 核心 | Build the Lever | 做工具(腳本、codemod)來完成或證明工作 |
| 架構 | Model the Domain | 分支多的邏輯用狀態機、表格等結構表達 |
| 架構 | Boundary Discipline | 在系統邊界檢查,內部信任型別 |
| 架構 | Type System Discipline | 讓不合法狀態無法表示 |
| 架構 | Make Operations Idempotent | 重跑、當掉後重試,結果都一樣 |
| 架構 | Migrate Callers Then Delete Legacy APIs | 一次搬完呼叫者並刪舊 API |
| 架構 | Separate Before Serializing Shared State | 多個寫入者先拆開,真的必要才排隊 |
| 驗證 | Prove It Works | 對真產物驗證 |
| 驗證 | Fix Root Causes | 追到第一個出錯的地方修 |
| 驗證 | Sequence Work into Verifiable Units | 切成小單位,每個結尾都有檢查 |
| 驗證 | Test Behavior Not Implementation | 測使用者看得到的行為 |
| 驗證 | Explain the Number | 信數字前先找出它的瓶頸 |
| 分派 | Guard the Context Window | 大量輸出交給 subagent |
| 分派 | Never Block on the Human | 可回頭的事不要停下來問 |
| 元 | Encode Lessons in Structure | 教訓寫成檢查,不寫成更多文字 |

<a id="sec-9-3"></a>
### 9.3 兩套怎麼接,不打架

- **逼問和 prototype 分工**:Pocock 的逼問處理只有人能回答的問題(意圖、名詞、取捨);pstack 的 prototype 處理跑一下就知道的問題。兩個都用,不要拿 prototype 問意圖,也不要逼問一個跑一下就知道的問題。
- **spec 不要 `/interrogate`**:pstack 作者明講抽象的 plan 不值得花 reviewer;它該用在 diff 上。spec 的品質靠逼問和 `/to-tickets` 的確認環節。
- **pstack 沒有 planning,Pocock 補上**:多 PR 的工作,先 Pocock 逼問 + spec + 票;每張票開工時打 `/poteto-mode 做票 #N`,讓 pstack 的 playbook 接手執行與驗證。
- **兩種 review 可以都跑**:Pocock `/code-review` 看「合不合規範、合不合 spec」;pstack `/interrogate` 看「不同模型能不能把它弄壞」。前者對齊意圖,後者找 bug。
- **修 bug 選一條**:`/diagnosing-bugs` 強在先建回饋迴圈、假設清單;`/poteto-mode` 的 Bug fix playbook 強在執行期證據和分派。推測:單機能重現的用前者,要在真實環境量測的用後者。
- **回顧兩個都有用**:`/retro` 改環境,`/reflect` 改 skill,`/correct` 改 repo。

<a id="sec-9-4"></a>
### 9.4 控制成本

- `/setup-pstack` 選小一點的 budget。
- 不重要的角色用 `auto` 或 [`inherit-parent`](#g-inherit-parent),也就是跟著 session 的模型。
- `/arena`、`/interrogate` 少開幾個候選或 reviewer。
- `/poteto-mode` 留給真的需要嚴謹的工作,小事直接講。

---

<a id="sec-10"></a>
## 10. 在 Claude Code + j-pockit 扁平安裝下的差異

pstack 原本寫給 Cursor,Claude Code 版靠 adapter 對應<sup>[[6]](#ref-6)</sup>。j-pockit 又改成扁平安裝,所以有些地方跟 pstack 文件寫的不一樣。標「推測」的是依檔案推論、尚未實測。

| 項目 | pstack 文件寫的 | 在這裡實際 |
|---|---|---|
| 叫 pstack skill | 打 `/name` | Claude Code 的 [Skill tool](#g-skill-tool) 會拒絕設了 `disable-model-invocation` 的 skill,所以 AI 不能自己叫,要你打。skill 之間靠「讀對方的 SKILL.md 照做」串起來<sup>[[3]](#ref-3)</sup>。 |
| 指令名 | adapter 叫 AI 告訴你打 `/pstack:<name>` | 扁平安裝下是短名 `/name`。AI 若叫你打 `/pstack:how`,改打 `/how`(推測)。 |
| subagent 名 | `pstack:poteto-agent`、`pstack:comment-sicko` | agent 檔裝在 `~/.claude/agents/`,名稱是 `poteto-agent`、`comment-sicko`(推測)。 |
| `/poteto-mode` 常駐 | Cursor 可設成 [Custom Mode](#g-custom-mode),每輪自動套用 | Claude Code 沒有這功能,每個新任務開頭都要打 `/poteto-mode`<sup>[[1]](#ref-1)</sup>。 |
| 模型 | `claude-opus-5-5-xhigh`、grok、gpt 等 | Claude 模型換成 `opus xhigh` 這種寫法;非 Claude 的模型名一律改用 session 模型。 |
| 「不同模型家族」 | `/interrogate`、`/arena` 評審、`/show-me-your-work` 都靠模型差異 | 只有 Claude 模型時差異變小。可在 `pstack-models.md` 讓 reviewer 用 sonnet、haiku 等不同模型拉開(推測)。 |
| cloud agent | `environment: cloud` | 改用 worktree 隔離。 |
| Cursor 專屬功能 | Automations、Bugbot、cloud agent 後台 | 跳過,回覆會出現一行 [`Skipped in Claude Code: ...`](#g-skipped-line)。[`/make-bot-ui`](#g-make-bot-ui) 幾乎整個不能用。 |
| 開 PR | 內建 PR 工具 | 改用 `[gh](#g-gh) pr create`。**本機沒裝 `gh`**,要先裝,或自己在網頁開 PR。 |
| [`create-skill`](#g-create-skill) | Cursor 內建,`/reflect`、`/automate-me`、Authoring a skill 會叫 | 不存在。改用 `writing-for-agents` 當寫法參考(推測)。 |
| [`/deslop`](#g-deslop) 等 | 屬 cursor-team-kit | 沒裝,相關步驟會跳過。 |
| `/loop` | Cursor 內建的喚醒機制 | Claude Code 也有 `/loop`,細節可能不同(推測)。 |
| tdd / teach / handoff | pstack 有自己的 `tdd`;Pocock 主流程會用 `/handoff` 把 prototype 分出去 | `/tdd` 是 Pocock 版;`/teach` 是 pstack 版;`/handoff` 是本機自己的指令,不是 Pocock 版。要跑 prototype 可直接在同一個 session 叫 `/prototype`(推測)。 |
| `/benchmark-checklist` 的工具 | `uptime`、`nproc` 等 Linux 指令 | Windows 上沒有,要換成對應的系統工具(推測)。 |

---

<a id="sec-11"></a>
## 11. 情境速查與單 session 捷徑

| 情境 | 建議路線 |
|---|---|
| 新功能,要好幾個 session | `/grill-with-docs` → `/to-spec` → `/to-tickets` → 每張票 `/poteto-mode`(或 `/implement`)→ `/interrogate` → PR → `/retro` |
| 小改動 | `/grill-with-docs` → `/implement`(Pocock 自己建議的短路線<sup>[[2]](#ref-2)</sup>),執行時照樣可以開 `/poteto-mode` |
| 修 bug | `/poteto-mode` + 「repro first」,或 `/diagnosing-bugs`(見 9.3) |
| 看不懂舊程式 | `/how`;想知道歷史加 `/why`;要真的懂用 `/teach` |
| 架構健檢 | `/improve-codebase-architecture` → 選一個候選 → `/grill-with-docs` |
| 效能問題 | `/poteto-mode`(Perf issue)+ `/benchmark-checklist` |
| 超大、還很模糊 | `/wayfinder` → 一個 session 解一張決策票 → `/to-spec` |
| 要睡了讓它跑 | 四條件成立後:`/poteto-mode` + 完成條件 + worktree + `/loop`;早上 `/show-me-your-work` |
| 離開一下回來 | 同一個對話用 `/ketchup`;跨對話用 `/recall` |
| 不知道用哪個 | 規劃類問 `/ask-matt`;執行類問 `/poteto-help` |

---

<a id="appendix-a"></a>
## 附錄 A. 參考來源(References)

| # | 主題 / 用途 | 來源 |
|---|---|---|
| <a id="ref-1"></a>#1 | pstack(Lauren Tan)本體與 `/poteto-help` 說明 | [cursor/plugins — pstack](https://github.com/cursor/plugins/tree/main/pstack) |
| <a id="ref-2"></a>#2 | mattpocock-skills(Matt Pocock) | [mattpocock/skills](https://github.com/mattpocock/skills) |
| <a id="ref-3"></a>#3 | Claude Code skill 機制(`disable-model-invocation` 等) | [Claude Code docs — Skills](https://code.claude.com/docs/en/skills) |
| <a id="ref-4"></a>#4 | 本 repo 安裝與排除清單 | [README.md](../README.md) |
| <a id="ref-5"></a>#5 | pstack 使用指南 10 頁(痛點、設計階梯、夜跑、14 個坑);本機副本在 `~/.claude/docs/guide/` | [pstack docs/guide](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/README.md) |
| <a id="ref-6"></a>#6 | pstack 的 Claude Code adapter;本機副本在 `~/.claude/docs/harness/claude-code.md` | [cursor/plugins — harness/pstack/claude-code](https://github.com/cursor/plugins/tree/main/harness/pstack/claude-code) |
| <a id="ref-7"></a>#7 | Pocock engineering skill(`ask-matt` 主流程、階段邊界、skill 叫法規則) | [mattpocock/skills — skills/engineering](https://github.com/mattpocock/skills/tree/main/skills/engineering) |
| <a id="ref-8"></a>#8 | 上游事實查證紀錄 | [research/upstream-facts.md](research/upstream-facts.md) |
| <a id="ref-9"></a>#9 | 為什麼扁平安裝而不用 plugin | [adr/0001-flat-install-not-plugin.md](adr/0001-flat-install-not-plugin.md) |

---

<a id="appendix-b"></a>
## 附錄 B. 技術關鍵字術語表(口語化說明)

| 關鍵字 | 類別 | 口語化說明 / 來源# |
|---|---|---|
| <a id="g-mattpocock-skills"></a>`mattpocock-skills` | skill set | Matt Pocock 的 skill 集,偏規劃、寫 spec、切票。j-pockit 裝 engineering + productivity 共 25 個。 [[2]](#ref-2) |
| <a id="g-pstack"></a>`pstack` | skill set | Lauren Tan(poteto)的 56 個 skill,偏執行、驗證、審查。j-pockit 裝其中 55 個(不裝 tdd)。 [[1]](#ref-1) |
| <a id="g-poteto-mode"></a>`/poteto-mode` | pstack skill | pstack 的總入口。把任務對到一套 playbook 照步驟做,需要時自動拉其他 skill。Claude Code 下每個新任務要重打。 [[1]](#ref-1) [[5]](#ref-5) |
| <a id="g-feedback-loop"></a>`回饋迴圈` | 概念 | 能快速告訴你「對了沒」的機制,例如一條會變紅變綠的測試指令。Pocock 認為多數 skill 的價值就在建這個。 [[7]](#ref-7) |
| <a id="g-model-invoked"></a>`model-invoked` | skill 類型 | 模型可以自己判斷要叫的 skill。Pocock 規定使用者叫的 skill 可以叫模型叫的,反向不行。 [[2]](#ref-2) [[3]](#ref-3) |
| <a id="g-disable-model-invocation"></a>`disable-model-invocation` | frontmatter 欄位 | 設成 true 的 skill 只能由使用者打 /名字 叫,模型不能自己叫。pstack 除 setup-pstack 外全設了。 [[3]](#ref-3) |
| <a id="g-ask-matt"></a>`/ask-matt` | Pocock skill | 問「現在該用哪個 Pocock skill」,它只指路不執行。 [[7]](#ref-7) |
| <a id="g-playbook"></a>`playbook` | pstack 概念 | /poteto-mode 底下的 23 套固定步驟,一種任務一套,例如 Bug fix、Refactoring。 [[5]](#ref-5) |
| <a id="g-poteto-help"></a>`/poteto-help` | pstack skill | 問該用哪個 pstack skill 或 playbook,只回答不開工。 [[1]](#ref-1) |
| <a id="g-plugin-prefix"></a>`/pstack:how` | 指令寫法 | 用 plugin 安裝時 skill 名前面會加 plugin 名。j-pockit 扁平安裝,直接打 /how。 [[9]](#ref-9) |
| <a id="g-tdd"></a>`/tdd` | Pocock skill | 先寫一個會失敗的測試,再寫剛好讓它過的程式,一次一個。只在系統邊界 mock。 [[7]](#ref-7) |
| <a id="g-implement"></a>`/implement` | Pocock skill | 實作一張票:在講好的 seam 用 /tdd、跑 typecheck 與測試、/code-review、commit。 [[7]](#ref-7) |
| <a id="g-teach"></a>`/teach` | pstack skill | 跑 /how 和 /why,用白話加逐步的圖讓你真的懂。j-pockit 裝這一版。 [[1]](#ref-1) |
| <a id="g-how"></a>`/how` | pstack skill | 解釋某個子系統怎麼運作、新東西該放哪。大問題會先派 2 到 4 個唯讀 explorer 分頭看。 [[1]](#ref-1) |
| <a id="g-why"></a>`/why` | pstack skill | 查某段程式或某個數字為什麼長這樣:從 git 歷史起頭,再查 issue、文件、聊天等證據,分開直接證據和推論。 [[1]](#ref-1) |
| <a id="g-handoff"></a>`/handoff` | 指令 | 把目前工作交給新 session 的接力指令。j-pockit 不裝 Pocock 版,以免蓋掉本機 ~/.claude/commands/handoff.md。 [[4]](#ref-4) |
| <a id="g-setup-pstack"></a>`/setup-pstack` | pstack skill | 一台機器跑一次,決定 pstack 各角色用哪個模型、多少推理預算,並提議建驗證 skill。pstack 唯一模型可自己叫的 skill。 [[1]](#ref-1) [[6]](#ref-6) |
| <a id="g-reasoning-budget"></a>`reasoning budget` | 設定值 | 模型每次可以花多少推理量。pstack 分 unlimited / large / medium / small 四檔,分別對到 max / xhigh / high / medium。 [[1]](#ref-1) |
| <a id="g-pstack-models-md"></a>`~/.claude/rules/pstack-models.md` | 檔案 | /setup-pstack 寫出的 rule 檔,每個新 session 自動載入,蓋過 skill 內建的模型預設。 [[6]](#ref-6) |
| <a id="g-setup-matt-pocock-skills"></a>`/setup-matt-pocock-skills` | Pocock skill | 每個 repo 跑一次,問 tracker、label、domain 文件三題,寫進 docs/agents/ 與 CLAUDE.md。 [[7]](#ref-7) |
| <a id="g-issue-tracker"></a>`issue tracker` | 概念 | 放 spec 與票的地方,可以是 GitHub Issues,也可以是 repo 裡一張票一個檔。 [[2]](#ref-2) |
| <a id="g-docs-agents"></a>`docs/agents/` | 目錄 | /setup-matt-pocock-skills 寫出的設定(tracker、label、domain 文件位置),其他 Pocock skill 開工前會讀。 [[7]](#ref-7) |
| <a id="g-claude-md"></a>`CLAUDE.md` | 檔案 | Claude Code 每個 session 自動讀的專案說明檔。 [[3]](#ref-3) |
| <a id="g-scratch"></a>`.scratch/<feature>/` | 目錄 | 選 local markdown tracker 時放 spec 與票的地方,一張票一個 NN-slug.md。 [[7]](#ref-7) |
| <a id="g-glossary-md"></a>`GLOSSARY.md` | 文件 | 專案術語表,每個詞附定義和「別這樣叫」清單。Pocock v1.3 起由 CONTEXT.md 改名而來。 [[2]](#ref-2) |
| <a id="g-grill-with-docs"></a>`/grill-with-docs` | Pocock skill | 逼問計畫到沒有模糊處,同時更新 GLOSSARY.md、必要時寫 ADR。內部用 grilling + domain-modeling。 [[7]](#ref-7) |
| <a id="g-grilling"></a>`grilling` | Pocock skill(模型叫) | 逼問的核心:一輪問完所有前提已定的問題、每題附建議答案;事實自己查,決定交給你。 [[7]](#ref-7) |
| <a id="g-domain-modeling"></a>`domain-modeling` | Pocock skill(模型叫) | 邊討論邊維護 GLOSSARY.md 和 ADR,挑戰含糊或互相衝突的用詞。 [[7]](#ref-7) |
| <a id="g-grill-me"></a>`/grill-me` | Pocock skill | 跟 /grill-with-docs 一樣逼問,但不留文件;不在 repo 裡時用。 [[7]](#ref-7) |
| <a id="g-adr"></a>`ADR` | 文件類型 | Architecture Decision Record,一個重要決定一份短文件:當時的情況、選了什麼、為什麼。 [[2]](#ref-2) |
| <a id="g-prototype"></a>`/prototype` | Pocock skill(模型叫) | 丟棄式原型:狀態邏輯用單一 HTML 檔,UI 用 ?variant= 切 3 到 5 個變體。 [[7]](#ref-7) |
| <a id="g-to-spec"></a>`/to-spec` | Pocock skill | 把目前對話整理成 spec 發到 issue tracker,只做彙整不再訪談,不寫檔案路徑。 [[7]](#ref-7) |
| <a id="g-to-tickets"></a>`/to-tickets` | Pocock skill | 把 spec 切成一組 tracer-bullet 票,每張寫明被哪幾張擋住。 [[7]](#ref-7) |
| <a id="g-tracer-bullet"></a>`tracer-bullet` | 切票方法 | 每張票都是從頭到尾打通的一條細路徑(每一層都碰一點),做完就能跑、能驗,而不是按層切。 [[2]](#ref-2) |
| <a id="g-implement-spec"></a>`/implement-spec` | Pocock skill | 把整份 spec 的票當任務圖,平行派 subagent 各用一個 worktree 做,merger 收合,最後 code review。 [[7]](#ref-7) |
| <a id="g-retro"></a>`/retro` | Pocock skill | 讀 session 紀錄,從 7 類找 agent 工作環境的改進點。 [[7]](#ref-7) |
| <a id="g-frontier"></a>`frontier` | 概念 | 決策樹裡前置條件都已決定、可以馬上問的那一層問題。 [[7]](#ref-7) |
| <a id="g-subagent"></a>`subagent` | Claude Code 機制 | 主對話派出去做一件事的子代理,有自己的 context,只把結論帶回來。 [[3]](#ref-3) |
| <a id="g-seam"></a>`seam` | 設計概念 | 不改內部就能換掉行為的介面位置,測試放在這裡。Pocock:只有一個 adapter 是假設的 seam,有兩個才是真的。 [[7]](#ref-7) |
| <a id="g-expand-contract"></a>`expand-contract` | 重構方法 | 先加新的、讓新舊並存(expand),搬完呼叫者再刪舊的(contract),每一步都能單獨合併。 [[7]](#ref-7) |
| <a id="g-ready-for-agent"></a>`ready-for-agent` | triage label | 這張票資訊夠了,AI 可以直接接手做。 [[7]](#ref-7) |
| <a id="g-clear"></a>`/clear` | Claude Code 指令 | 清空目前 context 重新開始。 [[3]](#ref-3) |
| <a id="g-code-review"></a>`/code-review` | Pocock skill(模型叫) | 對某個基準點以來的 diff,分 Standards(repo 規範 + Fowler code smell)與 Spec 兩軸,兩個 subagent 平行審。 [[7]](#ref-7) |
| <a id="g-integration-branch"></a>`integration branch` | git 概念 | /implement-spec 開的匯流 branch,各票做完先合到這裡,最後開一個 draft PR。 [[7]](#ref-7) |
| <a id="g-worktree"></a>`worktree` | git 概念 | 同一個 repo 的另一份工作目錄,有自己的 branch。平行 agent 各用一個才不會互相覆蓋檔案。 [[5]](#ref-5) |
| <a id="g-codebase-design"></a>`codebase-design` | Pocock skill(模型叫) | deep module 的詞彙與做法:刪除測試、介面即測試面、Design it twice。 [[7]](#ref-7) |
| <a id="g-pr"></a>`pr` | Pocock skill(模型叫) | 寫 PR 說明:最小的圖、改前改後證據、合併風險。取材自 Dex Horthy(HumanLayer)的 show-me。 [[2]](#ref-2) |
| <a id="g-diagnosing-bugs"></a>`/diagnosing-bugs` | Pocock skill | 修 bug 的六階段:先建能變紅的回饋迴圈、縮小重現、列假設、加標記 log、修 + 回歸測試、清理。 [[7]](#ref-7) |
| <a id="g-triage"></a>`/triage` | Pocock skill | 整理 issue:每個一個類別、一個狀態 label,先查重複再重現。 [[7]](#ref-7) |
| <a id="g-wayfinder"></a>`/wayfinder` | Pocock skill | 超大模糊工作的規劃地圖,一張決策票一個 session,最後接回 /to-spec。 [[7]](#ref-7) |
| <a id="g-improve-codebase-architecture"></a>`/improve-codebase-architecture` | Pocock skill | 掃 codebase 找可加深的模組,產 HTML 報告讓你挑一個再逼問。 [[7]](#ref-7) |
| <a id="g-research"></a>`/research` | Pocock skill(模型叫) | 背景 agent 只查一手來源,寫成附引用的 markdown。 [[7]](#ref-7) |
| <a id="g-deep-module"></a>`deep module` | 設計概念 | 介面小、背後藏很多行為的模組。呼叫者要學的少,能做的多。 [[7]](#ref-7) |
| <a id="g-to-questionnaire"></a>`/to-questionnaire` | Pocock skill | 答案在別人腦袋裡時,產一份問卷給對方填。 [[7]](#ref-7) |
| <a id="g-wait-what"></a>`/wait-what` | Pocock skill | 要 AI 用簡化英文加術語表的詞重講上一則。 [[7]](#ref-7) |
| <a id="g-wizard"></a>`wizard` | Pocock skill(模型叫) | 產一支 bash 腳本,一步一步帶人做 AI 做不了的手動設定。 [[7]](#ref-7) |
| <a id="g-writing-for-agents"></a>`writing-for-agents` | Pocock skill(模型叫) | 寫給 agent 讀的文件的原則,例如少用否定句、提防過早宣告完成。 [[7]](#ref-7) |
| <a id="g-phase-boundary"></a>`階段邊界` | Pocock 概念 | 一個階段做完、下一階段還沒開始的時點;只在這裡決定 context 要不要清。 [[7]](#ref-7) |
| <a id="g-smart-zone"></a>`smart zone` | 概念 | 模型還能好好推理的 context 長度,Pocock 估約 150k token,超過後品質下滑。 [[7]](#ref-7) |
| <a id="g-compact"></a>`/compact` | Claude Code 指令 | 把目前對話壓成摘要繼續。會丟細節,所以不要在階段中途用。 [[3]](#ref-3) |
| <a id="g-adapter"></a>`adapter` | pstack 文件 | ~/.claude/docs/harness/claude-code.md,把 pstack 給 Cursor 的寫法對到 Claude Code(工具名、模型名、路徑)。 [[6]](#ref-6) |
| <a id="g-figure-it-out"></a>`/figure-it-out` | pstack skill | 沒有現成 playbook 或範圍很大時現場設計做法:可推翻的完成條件、最小單位、風險高的先做、每圈驗證。 [[1]](#ref-1) |
| <a id="g-architect"></a>`/architect` | pstack skill | 跨邊界的設計:先 /how 打底,用 /arena 產至少兩個設計並先寫呼叫端用法;繞路太多就重來。 [[1]](#ref-1) |
| <a id="g-interrogate"></a>`/interrogate` | pstack skill | 把同一個 diff 交給不同模型家族的 reviewer,兩邊都抓到的最可信;結果分 Act on / Consider / Noted / Dismissed,不自動套用。 [[1]](#ref-1) |
| <a id="g-unslop"></a>`/unslop` | pstack skill | 依編號規則刪掉文字裡的 AI 腔,例如誇張詞彙、破折號、句中冒號。 [[1]](#ref-1) |
| <a id="g-no-comments"></a>`/no-comments` | pstack skill | review 前派 comment-sicko 挑多餘註解;描述限制的註解改成型別、檢查或測試。 [[1]](#ref-1) |
| <a id="g-benchmark-checklist"></a>`/benchmark-checklist` | pstack skill | 回報效能數字前問 7 題,判定變快、變慢、沒差或無法判定。 [[1]](#ref-1) |
| <a id="g-show-me-your-work"></a>`/show-me-your-work` | pstack skill | 長跑時每個決定記一列到 decisions.tsv,結束時異模型 review,回覆最後有 Attention 段。 [[1]](#ref-1) [[5]](#ref-5) |
| <a id="g-principle"></a>`principle` | pstack 概念 | pstack 的 24 條工程原則,每條是一個 skill;/poteto-mode 套用時會點名。 [[5]](#ref-5) |
| <a id="g-poteto-agent"></a>`poteto-agent` | subagent | /poteto-mode 分派工作用的 subagent,開工前會讀 poteto-mode 的 SKILL.md。 [[1]](#ref-1) |
| <a id="g-mcp"></a>`MCP` | 協定 | Model Context Protocol,讓 AI 連外部系統(issue、聊天、監控)的介面。/why 會用接上的 MCP 查證據。 [[3]](#ref-3) |
| <a id="g-recall"></a>`/recall` | pstack skill | 翻你最近的對話紀錄、PR、branch,重建你自己的工作現況。 [[1]](#ref-1) |
| <a id="g-arena"></a>`/arena` | pstack skill | 多個 subagent 做同一題,唯讀評審照評分表打分,選一個當底再嫁接別人的好點子。 [[1]](#ref-1) |
| <a id="g-model-family"></a>`模型家族` | 概念 | 同一家的模型,例如 Claude 各版。不同家族盲點不同,所以 pstack 拿來互審。 [[5]](#ref-5) |
| <a id="g-swarm"></a>`/swarm` | pstack skill | 把工作切成互不相干的片平行做,各回 PASS / ISSUES / BLOCKED,缺結果算缺口。 [[1]](#ref-1) |
| <a id="g-design-ladder"></a>`設計階梯` | pstack 概念 | 依改動大小決定做多少設計檢查的對照表,見 5.4。 [[5]](#ref-5) |
| <a id="g-comment-sicko"></a>`comment-sicko` | subagent | 專挑註解毛病的 subagent,/no-comments 用。 [[1]](#ref-1) |
| <a id="g-technical-writing"></a>`/technical-writing` | pstack skill | 寫文件、RFC、PR、commit message 的寫法規則,一份文件只選一種模式。 [[1]](#ref-1) |
| <a id="g-prove-it-works"></a>`prove-it-works` | pstack principle | 對真正的產物驗證,不拿 build 綠燈或替代指標當證明。 [[1]](#ref-1) |
| <a id="g-create-verification-skill"></a>`/create-verification-skill` | pstack skill | 為專案產 `verify-<app>` skill 並實跑一次。 [[1]](#ref-1) |
| <a id="g-verify-app"></a>`verify-<app>` | skill | 專案專屬的驗證 skill:啟動、自檢、操作、留證據、收拾,加一份功能地圖。 [[1]](#ref-1) |
| <a id="g-maintain-verification-skill"></a>`/maintain-verification-skill` | pstack skill | App 改了之後重驗 `verify-<app>` 的功能地圖。 [[1]](#ref-1) |
| <a id="g-create-formal-verification-skill"></a>`/create-formal-verification-skill` | pstack skill | 用形式方法驗併發、狀態機這類測試難碰到的性質。 [[1]](#ref-1) |
| <a id="g-tla"></a>`TLA+` | 形式語言 | 描述並自動檢查系統所有可能狀態的規格語言,適合找併發 bug。 [[1]](#ref-1) |
| <a id="g-blast-radius"></a>`/blast-radius` | pstack skill | 找小改動會在別處弄壞什麼,重點是 grep 找不到的依賴,並跑程式證明安全。 [[1]](#ref-1) |
| <a id="g-loop"></a>`/loop` | 指令 | 反覆喚醒 agent 直到條件成立;pstack 夜跑用它重檢完成條件。Cursor 和 Claude Code 各有一個。 [[5]](#ref-5) |
| <a id="g-decisions-tsv"></a>`decisions.tsv` | 檔案 | /show-me-your-work 的決策紀錄,一列一個決定,只追加不改。 [[5]](#ref-5) |
| <a id="g-sharpen"></a>`/sharpen` | pstack skill | 把你的 prompt 改得更深,只回 prompt 不做事。 [[1]](#ref-1) |
| <a id="g-in-your-own-words"></a>`/in-your-own-words` | pstack skill | 要 AI 用自己的話複述你的目標和問題。 [[1]](#ref-1) |
| <a id="g-bro"></a>`/bro` | pstack skill | 把上一則用白話重講。 [[1]](#ref-1) |
| <a id="g-ketchup"></a>`/ketchup` | pstack skill | 唯讀整理你上次發言後發生的事,列出等你決定的事。 [[5]](#ref-5) |
| <a id="g-reflect"></a>`/reflect` | pstack skill | 派三個 reviewer 掃本次對話,整合成 Accepted / Rejected / Backlog,你批准才改 skill。 [[1]](#ref-1) |
| <a id="g-correct"></a>`/correct` | pstack skill | 把 agent 一再犯的錯在最高層修掉(架構、型別、lint、測試,文件最後),並證明新檢查抓得到。 [[1]](#ref-1) |
| <a id="g-automate-me"></a>`/automate-me` | pstack skill | 從你的對話紀錄歸納習慣,產一個你自己的 `<handle>-mode` skill。 [[1]](#ref-1) |
| <a id="g-done-check"></a>`完成條件` | 概念 | 能判 pass / fail 的結束條件,例如「done means 連跑 24 小時零 timeout」。 [[5]](#ref-5) |
| <a id="g-auto"></a>`auto` | 模型設定值 | pstack 的模型值,意思是交給平台挑。Claude Code 下等於不指定 model。 [[6]](#ref-6) |
| <a id="g-inherit-parent"></a>`inherit-parent` | 模型設定值 | subagent 跟主 session 用同一個模型。Claude Code 下等於不指定 model。 [[6]](#ref-6) |
| <a id="g-skill-tool"></a>`Skill tool` | Claude Code 機制 | 模型用來叫 skill 的工具;會拒絕設了 disable-model-invocation 的 skill。 [[3]](#ref-3) [[6]](#ref-6) |
| <a id="g-custom-mode"></a>`Custom Mode` | Cursor 功能 | Cursor 可以把 /poteto-mode 設成每輪自動套用的模式;Claude Code 沒有。 [[1]](#ref-1) |
| <a id="g-skipped-line"></a>`Skipped in Claude Code: ...` | 回覆格式 | adapter 規定:步驟需要 Cursor 專屬功能時,印這一行後繼續下一步。 [[6]](#ref-6) |
| <a id="g-make-bot-ui"></a>`/make-bot-ui` | pstack skill | 依賴 Cursor 專屬功能,在 Claude Code 下幾乎不能用。 [[1]](#ref-1) |
| <a id="g-gh"></a>`gh` | CLI | GitHub 官方命令列工具;pstack 在 Claude Code 下用 gh pr create 開 PR。本機沒裝。 [[6]](#ref-6) |
| <a id="g-create-skill"></a>`create-skill` | Cursor skill | Cursor 內建的寫 skill 工具,Claude Code 沒有。 [[6]](#ref-6) |
| <a id="g-deslop"></a>`/deslop` | cursor-team-kit skill | Cursor 團隊套件裡的去 AI 腔工具,j-pockit 沒裝。 [[6]](#ref-6) |
