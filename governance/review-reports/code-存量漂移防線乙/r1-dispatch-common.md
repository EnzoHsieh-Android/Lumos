你是外部第三方 code reviewer。這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找作者沒看到的洞。

Diff 檔(git diff -U10,凍結版,引句只准引這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/code-存量漂移防線乙/r1-snapshot.patch(1315 行,含 scripts/lumos、scripts/test_lumos.py、圖譜筆記)
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(可 Read/Grep 真代碼查證上下文;python3 零依賴單檔 CLI scripts/lumos,測試 scripts/test_lumos.py,單支跑法 `python3 scripts/test_lumos.py -k <測試名片段>`)。
設計(這份 diff 要兌現的規格):同 repo 的 docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md。本次只做「乙」:條件式回頭條件——〈做法〉第 0 節的條件文法、期限 [by:]、「這行是不是 REVISIT」共用判定、「同一條」、check 的候選篩選與判定、scan 與 doctor Z 的乙部分;第 2 節全部;第 3 節 probe 考法。「甲」(狀態一致檢查、settle 改寫)已經上線,不在這次範圍。
被考的 rtb repo 唯讀複本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/rtb-exam(只准 git -C 唯讀指令;考卷 governance/eval/drift-exam/rtb-2026-09-28.json、改寫檔 rtb-2026-09-28-probes.json)。

變更主題:
- 回頭條件可以寫 `REVISIT:[when-file|symbol|test|status:值][by:YYYY-MM-DD] 待辦`。新函式:_revisit_split(E5、筆記形狀擋、筆記內容審共用的判定)、_probe_parse、_probe_value_err、_probe_lines(只認正文與摘要的可見行;表格、圍欄、行內程式碼、開頭欄位其他欄不算)、_ProbeTree(在某個提交或工作目錄判四種鍵)、_probe_changes、_probe_is_candidate、_drift_probe_check、_probe_judge、_probe_prepare、_drift_probe_scan。
- drift check 在這次推送讓條件從不成立變成立時列進要處理;「同一條」只看條件標記(改名對回後);新寫而已成立的也擋。
- doctor E5 改用共用判定:條件式不算壞損、[by:] 當日期判到期。筆記內容審的待審行排除條件式回頭條件。筆記形狀擋加 _ns_revisit_violations,並讓共用的 _notelines_new 多一個 keep_other 選項收開頭欄位其他欄的新行。
- lumos set 收尾計劃時多列 when-status 因此成立的行;drift exam 加 --probes 的 probe 考法。

錨定紀律(硬性):
- 每條 finding 必附一段從凍結 diff 逐字複製的原文引句(≥10 字),寫成單獨一行「引句:「…」」,引句內不要再包「」、不要跨行。
- 審材外查證寫成單獨一行「file: `路徑:行號`」(反引號必加)。
- 你指出的 blocker/major 必須附能當場翻紅的最小重現(一條測試或一條指令+輸出);附不出就如實標「未能重現」,severity 自降一級。
- git 實驗一律 git -C <你自己 mktemp 的臨時目錄>;不准在任何 repo 根跑 commit/reset/restore/checkout/stash,不准改任何 repo 裡的檔;不要執行任何掛鉤腳本。

抑噪紀律:
- 低嚴重度疑慮,給不出具體失敗場景就不要標。但未定義的詞、壞引用、內部不一致一律要報。
- 不能從 diff 指出具體受影響的 file:line,就不准臆測「可能會壞別處」。
- 不要讀 governance/review-reports/ 底下任何席報告。

輸出格式(硬性,收貨端機械檢查):
- 檔首第一個非空行:severity: <整份最高 clean|minor|major|blocker>
- 每條 finding:標題行「## F<n> <一句話>」(標題裡不寫等級);接著獨立一行「severity: <值>」、獨立一行「blocking: 是|否 — 一句判準」(否↔minor;是↔major/blocker);一行「引句:「…」」;敘述編號條列,只寫到讓人能重現為止——哪個輸入、走到哪一行、壞在哪;不准用「可能/或許/建議考慮」收尾,判不準在敘述裡標 ⚠。
- 某塊沒問題也寫「已看,無 finding」。沒找到問題就交 severity: clean。
- 最後一行總結:最嚴重等級、blocking 共幾條(總結句裡不要寫 severity 字樣)。
- 報告只寫進指定的報告檔,不改任何其他檔;交回時只回一句「報告已寫到 <路徑>,最高 X,共 N 條」。
