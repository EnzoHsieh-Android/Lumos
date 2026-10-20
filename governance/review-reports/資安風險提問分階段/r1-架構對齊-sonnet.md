severity: major

## 1. 分層與依賴方向

對得上的部分:
- 風險面表現在只有一處讀 `when`,就是 `_pitfalls_stage` 的篩選(`scripts/lumos:49099`)。〈三〉說「判斷收成一支函式」,在這裡成立。
- `pitfalls --stage` 不讀筆記庫(`scripts/lumos:49095`),計劃把筆記庫相關檢查放到 `security list` 與 `spec-gate`,分法正確。
- `security list` 在 `lumos-cli-read` 的 WHY 裡明寫不走 `load_vault` 或一般 Env,走自己的硬化快照。

不對齊有三條。

severity: major
blocking: 是
引句:「有資安登記時，印出那些護欄與 open 格子數，不擋。」
file: `scripts/lumos:7346`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:9`
說明:spec-gate 要算「護欄與 open 格子數」,就得讀 inventory 與 controls。
- 計劃只說「spec-gate 本來就讀筆記庫」,沒說走哪條讀法。
- spec-gate 手上的是一般 Env。盤點走的是自己的硬化讀取:`_secinv_snapshot` 加 `_secinv_build`,有容量上限和讀前讀後的變動偵測。
- 若 spec-gate 用 Env 自己解析 inventory,就多了第二套 inventory 解析器,繞過硬化讀取。
- 若 spec-gate 直呼 `_secinv_snapshot` 與 `_secinv_build`,就是 spec-gate 層跨進盤點層。每次跑規格閘還要多做一次最多 64MiB 的整庫讀取。
- 兩條路都沒寫進計劃,條款 S13 只驗輸出,不驗走哪條讀法。
- ⚠ 交編排者:我認定這是 major(跨層直呼或第二種解析),但實作者可能有第三條路,計劃沒寫就無從判斷。

severity: minor
blocking: 否
引句:在 verify-sec-evidence 或 deliver-sec-exceptions 觸發時，只多印一行指路
file: `scripts/lumos:49082`
說明:
- `_pitfalls_stage` 目前是通用迴圈,逐項印出 `[id] q`,沒有針對特定 id 的分支。
- 前端面是靠資料欄位 `role` 區分,不在程式裡寫死 id。計劃把指路行綁在兩個 facet id 上,等於在通用迴圈加了 id 特例。
- 同族做法是給表一個選填鍵(例如 `hint`),由迴圈通用地印。
- 指路行放進 `--json` 輸出的哪裡也沒寫。現有 JSON 只有 `stage`、`facets`、`questions`,條款 S13 沒蓋到這點。

severity: minor
blocking: 否
引句:它不寫在 surfaces 裡、作者不能自己宣告同名入口
file: `scripts/lumos:7160-7165`
file: `scripts/lumos:6770-6773`
說明:
- 現在 `_secinv_check_links` 對護欄的 `assets` 與 `surfaces` 會檢查是否都在 inventory 裡,不在就列 `reference_error`。
- 計劃要護欄寫 `@repo`,又不准 `@repo` 出現在 inventory,不改這段檢查的話,三類 repo 層護欄全會報錯。
- 計劃沒寫要特例這個檢查,也沒寫特例放在哪。
- 現行護欄 id 的格式限制是 `_SECINV_ID_RE`,只收字母、數字、`.`、`_`、`-`,`@` 不在其中。

## 2. 命名與錯誤處理

對得上的部分:
- 新問題種類 `insufficient_required_evidence` 與新輸出區 `applicability_pending_cells` 的形狀,和既有的 `missing_kind`、`applicability_pending_control_ids` 一致。
- 退出碼沿用 2。

不對齊有三條(第一條是 major)。

severity: major
blocking: 是
引句:或核可決策找不到、已作廢、缺補償措施或理由，這一列不算數、格子是 open。
file: `scripts/lumos:6841-6845`
file: `scripts/lumos:7140-7152`
file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:360`
說明:這裡引入第二種例外做法。
- 現有護欄例外的鍵是 `decision_ref`、`reason`、`expires_on`,由 `_secinv_check_exception` 判到期與決策失效。
- 姊妹計劃把它升成 v2:加補償措施、蓋住的證據種類、核可日,並規定「到期日減核可日超過 30 天」無效。30 天起算點是核可日欄位。
- 本篇 `considerations` 的 `risk_accepted` 另起一組,用中文描述的欄位(理由、補償措施、核可決策、到期日),沒給 JSON 鍵名。
- 30 天起算點改成核可決策的 `decided` 日,與姊妹計劃的核可日欄位不同。
- 結果是同一份盤點裡有兩種例外資料形狀、兩種 30 天算法,以及可能的兩支判斷函式。
- 母計劃 d9 的例外只有一條規則,這兩篇應共用鍵名與同一支檢查。
- 計劃沒寫共用。條款 S4 只描述行為,抓不到兩邊算法不同。

severity: minor
blocking: 否
引句:跨了哪道信任邊界，文字
file: `scripts/lumos:6395`
說明:
- 護欄已經有 `trust_boundary` 欄位(`_SECINV_NULLABLE`),值是可為空的文字。
- 計劃在 surfaces 上再加一個同名欄位,語意相近但層級不同。
- 讀者會分不清兩處的 `trust_boundary` 以誰為準。計劃沒說兩者關係,也沒說是否保留護欄上的欄位。

severity: minor
blocking: 否
引句:整條不分大小寫、前後不接英數字
file: `scripts/lumos:31056-31058`
說明:
- 計劃說詞界寫法照 `_REQ_FE_WHEN`,但實際上它的尾界不一致。
- 檔名副檔名與 e2e 那條用 `(?![a-z0-9])`。框架名那條用 `(?![a-z])`,刻意允許緊貼版本號(Vue3)。
- 另外 `(?i)` 是每條字串各自帶的。新的 `triggers.words` 每個元素各自 `re.search`,「整條」不分大小寫在這裡要變成每個元素都帶 `(?i)`。
- 計劃沒寫,實作時容易漏。

## 3. 第二種做法

- `triggers` 這個選填鍵本身站得住:`min_distinct` 的「不同詞數」用單一正規式表達不出,計劃也限定只有新項用、舊項的 JSON 逐字不變。
- 「鏡像常數加漂移測試」有先例:測試讀 `Systems/design-loop.md` 比對程式(`scripts/test_lumos.py:4873`),`_REQ_FE_WHEN` 與 `_NODE_FRONTEND_MARKERS` 也有同步測試。
- 但這張表的欄位是中文長句(如「既有單元與整合測試 runner、破壞測試與故障收證；動態掃描補充」)。逐欄比對的粒度與表格解析方式計劃沒寫。

這一問真正的第二種做法就是上面〈二〉的 `considerations` 例外,不再重列。

## 4. 落點

severity: minor
blocking: 是
引句:實作時這張表搬到 [[Systems/情境出題]] 這篇圖譜筆記
file: `docs/lumos-toolchain-knowledge/Systems/情境出題.md:6`
說明:`lands_in` 三篇裡,另兩篇都對得上:
- `Systems/pitfalls-code-loop` 管 `--stage`(該篇 225 行起)。
- `Systems/lumos-cli-read` 管 `security list`。

遺漏有兩處:
- `Systems/規格閘` 沒列進 `lands_in`,卻要改 spec-gate。
  - 該篇 responsibility 管規格閘的判門與擋法。
  - 鐵則 5 要求「改到的每支檔得先有家」,`lands_in` 也要寫現況落在哪幾篇。
- 威脅類別表放在 `情境出題`,是有疑義的落點。
  - 情境出題的負責範圍是「對照實驗的量測」加「需求風險面表的內容源」。
  - 威脅類別表的主要讀者是盤點與證據驗收(S5、S14),語意屬資安。
  - 計劃已承認要擴大它的 responsibility,但擴成「量測加風險面表加威脅分類正本加鏡像漂移測試」會變成一篇包多件事。
  - 判不準該擴既有那篇還是另開一篇。⚠ 交編排者,我只標出,不下結論。

## 結論

不對齊共 8 條,其中 major 2 條。

最需要編排者處理的是兩條:
- 例外資料形狀與 30 天起算點要跟姊妹計劃共用(〈二〉第一條)。
- spec-gate 讀 inventory 的路徑要選定(〈一〉第一條)。

我沒有建立臨時目錄,不需要清理。
