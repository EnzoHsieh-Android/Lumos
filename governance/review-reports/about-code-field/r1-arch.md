# about_code 欄位設計 — 架構對齊審查 r1

審查對象:`/tmp/about-code-field-r1.md`(固定席扇出降權_計劃,主案「語意『關於』欄位」段落)
審查範圍:僅判「跟本專案既有做法一不一致」,不判 bug、不評風格。

---

## Q1:分層與依賴方向

**問**:about_code 的讀(impact)與寫(預標/人放行)放的層、呼叫關係,跟既有 verified_by 那套一樣嗎?預標資料放 governance/eval/ 而不是進 frontmatter,這跟既有「圖譜是真相源」的賭注一致嗎?

**讀側:對齊。**
spec 設計「`impact` 的 direct 判定加一條:`about_code` 含目標檔 → direct 且 `hit="about"`,優先於 `body-inline-code`」(spec L188)。這跟既有 `_impact_direct_nodes` 對同一個 hit 欄位賦值 `"body-inline-code"` / `"basename-match"` 的機制(scripts/lumos:13499-13509)是同一個函式、同一種 hit 分類法的擴充,沒有新開一條平行路徑,也沒有跨層直呼——固定席的 `pinned = bool(x.get("contract"))`(scripts/lumos:14049)判定邏輯完全不動,只是 hit 的來源多一種。這跟既有 `verified_by` 之類欄位「寫在 frontmatter、讀側直接 `as_list(n.fields.get(...))`」的讀法一致。

**預標資料放哪裡:對齊。**
spec 沒有把模型預標結果放進 `governance/eval/` 當中間產物,而是「人抽驗後 `lumos set` 寫入」(spec L198)直接落進節點 frontmatter,跟既有「圖譜本身就是真相源」的賭注(docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:22「8個寫入原語…是專案層圖譜寫入的唯一安全路徑」)方向一致——不像 goldset 標註刻意留在 `governance/eval/goldset.json`(它是量測用的度量工具,不是系統行為依據,才需要跟圖譜分開)。

**寫側機制:不對齊(archf1,minor)。**
`about_code` 明文是「純清單,值=repo 相對路徑」(spec L173),依既有紀律清單型 frontmatter 一律走 `append`(LIST_KEYS 白名單),純量才走 `set`(SCALAR_KEYS 白名單)——這是 lumos-cli-write.md 決策 d2 明講的分工:「純量走 set(SCALAR_KEYS 白名單)、list 走 append(LIST_KEYS);白名單外 key 一律 rc2 拒絕」(docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:40-44),機械上由 `scripts/lumos:7243-7245`(SCALAR_KEYS/LIST_KEYS 常數)與 `cmd_set` 的白名單擋(scripts/lumos:7505-7508:「擋下:{key} 不能用 set 改…清單欄位用 lumos append」)雙重落實。但 spec 存量流程寫的是「人抽驗後 `lumos set` 寫入」——用 `set` 寫一個清單欄位,照現有工具字面上會被 `cmd_set` 直接 rc2 擋下(about_code 既不在 SCALAR_KEYS、內容又是 list)。層與呼叫方向本身沒錯(仍然透過 lumos 寫入原語、不是手改 frontmatter),只是指名的具體指令跟既有「verified_by 那套」的機制(append)不一致。

引句:「人抽驗後 `lumos set` 寫入」

---

## Q2:命名與錯誤處理

**問**:about_code / about_code_stamp 的命名跟既有慣例(snake_case、_refs 後綴、stamp 格式)一致嗎?過期降級的錯誤處理跟既有 degrade 慣例(delguard fail-open、E1 warn_soft)一致嗎?

**命名:大致對齊。**
`about_code` 是 snake_case,語意上是路徑清單而非連結,不強套 `_refs` 後綴(`_refs` 家族專指 wikilink/跨庫指針,如 `core_refs`——lumos-core-knowledge 明令 core_refs「值是純路徑非 wikilink」,scripts/lumos:7244 註解),這點沒有濫用既有後綴慣例,可以接受。

**about_code_stamp 格式:不對齊(archf2,minor)。**
本專案唯一的「標註時快照」stamp 慣例是 `self_audit`,格式固定兩段 `<model>/<date>`(`cmd_self_audit` 寫入 `f"{model}/{date}"`,scripts/lumos:7548;範例見 lumos-cli-read.md frontmatter `self_audit: sonnet/2026-08-16`)。spec 提出的 `about_code_stamp` 是三段格式且欄位性質不同——`<標註時本檔正文的 sha256 前 12 碼>/<誰標>/<日期>`(spec L179),第一段換成內容雜湊而非模型名。此外本專案唯一的「內容雜湊快照」前例是 `governance/anchor-baseline.json`,裡面每個檔案存的是完整 64 碼 sha256(如 `"scripts/lumos/hooks/pre-push": "7e62ba869b815e51307acb3f59ba779fcf0f5452a6f9d6d8e42f2653bff8c907"`),spec 卻選擇截斷成 12 碼,兩個既有 stamp 前例(self_audit 的兩段式、anchor-baseline 的全長雜湊)都沒有被沿用,是一個新格式。

引句:「本檔正文的 sha256 前 12 碼>/<誰標>/<日期>」

**過期降級處理:部分不對齊(archf3,minor)。**
既有兩種 degrade 慣例:delguard 是「超時/內部錯誤→整段檢查失效直接放行,行為契約自動成立,只記治理帳」的 fail-open(scripts/lumos:424 註解「fail-open:寫不進去不影響判定輸出」;cmd_delguard_check 恆 rc0,scripts/lumos:11827-11901);E1 是「不擋、只列出來提醒,資料照舊使用」的 warn_soft(scripts/lumos:872-892)。spec 的做法是兩段混合:doctor 端印 warn_soft 提示(「sha 不符→列『這篇改過、關於欄位可能過期』」,spec L209-210,跟 E1 精神一致),但 `impact` 端不是「不擋照舊使用」也不是「整段失效放行」,而是靜默把命中等級由 `about` 換成 `body-inline-code`——一種既有兩種模式都沒有的「不告知、直接打折可信度」處理。方向可以理解(不信任過期語意標、退回舊行為),但沒有精確對上任何一個既有 degrade 慣例,算是新組合。

引句:「降回 `body-inline-code` 等級」

---

## Q3:第二種做法

**問**:spec 有沒有引入本專案原本沒有的做法——尤其「過期守衛」會不會變成第三套「宣稱 vs 事實」檢查、「模型離線預標」會不會變成第二套「模型標→人放行」流程?

**過期守衛:不對齊,major(archf4)。**
本專案現有「宣稱 vs 事實」家族目前兩種:Check N 比對「文字宣稱的數字 vs 重新掃描 repo 算出的數字」(正則計數,scripts/lumos:1170-1181 起,`<!--lumos:count=…-->` 標記);Check E1 比對「筆記引用的驗證背書 vs 那條驗證現在的 status」(狀態欄位比對,scripts/lumos:872-892)。spec 提出的 `about_code_stamp` 守衛比的是第三種材料——內容 sha256 雜湊,而且 spec 自己承認「檢查邏輯與 Check N 同族(宣稱 vs 重算),但比的是雜湊不是計數——**要另寫,不能直接借**」(spec L213-214)。這正是題目問的情況:一個接手的人以後要在「數字重算 / 狀態比對 / 內容雜湊」三套判準之間猜哪個場合用哪套,而 spec 也沒有交代為什麼不能延伸既有兩套之一(例如比對 `updated` 日期,像 self_audit 那樣)、非要引進雜湊比對不可。

引句:「檢查邏輯與 Check N 同族(宣稱 vs 重算),但比的是雜湊不是計數——要另寫,不能直接借」

**模型離線預標:不對齊,major(archf5)。**
本專案現有「模型標 → 人放行 → 寫入」的唯一流程是 `governance/eval/refresh_labels.py` 的 delta/merge/apply:merge 要求雙評審(A 席 + B 席),同值才 `agreed`,不一致進 `disputed`,B 席缺席整批降級 `degraded` 全部進人裁(refresh_labels.py:213-226);apply 端對每一筆 `disputed` 強制要求 adjudication 檔給出 `final`,缺了就整批擋下不准寫(「⛔ apply 擋下:{len(missing)} 筆人裁缺 final」,refresh_labels.py:275-278),還有跨進程寫入鎖防併發破壞(`_goldset_lock`,refresh_labels.py:44-60)。spec 的存量流程只有單一模型(Codex)「讀全文,依判準產 `about_code`」後「人抽驗」(抽樣核對,不是逐筆判定,更不是雙評審+disputed 機制)就直接寫入(spec L198)。`about_code` 判準明講「跟 goldset 標註表『必看』同一把」(spec L184),等於拿一套比 goldset 本身寫入紀律更薄的流程,去產生跟 goldset 語意等重的資料——這是題目點名的「兩套模型標→人放行」,且新的這套比既有那套鬆。

引句:「模型讀全文,依上面判準產 `about_code`,人抽驗後」

---

## 總結

不對齊共 5 條,其中 major 2 條(archf4、archf5)。

| id | 問題 | 嚴重度 |
|---|---|---|
| archf1 | 存量寫入用 `lumos set` 寫清單欄位,跟既有 set/append 分工(scalar/list)不符 | minor |
| archf2 | `about_code_stamp` 三段格式(雜湊/誰/日期)跟 self_audit 兩段格式、anchor-baseline 全長雜湊兩個既有前例都不同 | minor |
| archf3 | impact 端「降回 body-inline-code 等級」是靜默值替換,不精確對應 fail-open 或 warn_soft 任一既有 degrade 慣例 | minor |
| archf4 | 過期守衛引入第三套「宣稱 vs 事實」機制(內容雜湊),spec 自承不能直接借 Check N/E1 | **major** |
| archf5 | 存量預標(單模型+抽驗)是第二套「模型標→人放行」流程,比 refresh_labels 的雙評審+disputed+鎖薄 | **major** |

⚠ 判不準之處:spec 沒有明說存量批次腳本(讀模型輸出、跑 `lumos set/append`)實際會放在哪個目錄。若放進 `governance/eval/`,會多一層「eval 層腳本直接寫回 project 層 frontmatter」的跨層呼叫,目前既有的 `governance/eval/` 腳本(如 refresh_labels.py)只寫 eval 自己的產物(goldset.json/history.json),從不碰 frontmatter——這點留給編排者依實際落地位置判斷,本審查不因未定案的執行位置強判。
