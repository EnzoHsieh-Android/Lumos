你是外部第三方 code reviewer。這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找作者沒看到的洞。

Diff 檔(git diff -U10,凍結版,引句只准引這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/code-存量漂移防線乙/r4-snapshot.patch(1042 行,含 scripts/lumos、scripts/test_lumos.py、圖譜筆記)。
這份 diff 是「修正差異」:上一版(6400f52d)已審過三輪,這份是在它上面修掉第三輪 19 條發現後的差異(6400f52d..5ea8659c)。只審這份差異本身有沒有引入新問題、修法本身有沒有沒修到的形狀;上一版未改動的部分不是這輪的範圍,除非這份差異的改動讓它們壞掉。這是審查上限後、人裁定破例加開的一小輪。
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(HEAD=5ea8659c,可 Read/Grep 真代碼查證上下文;python3 零依賴單檔 CLI scripts/lumos,目前必須在 python3.9 能跑——/usr/bin/python3 就是 3.9;測試 scripts/test_lumos.py 要用 3.12 以上跑,單支跑法 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k <測試名片段>`)。
設計(這份 diff 要兌現的規格):同 repo 的 docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md 的〈做法〉第 0、2、3 節(「乙」:條件式回頭條件)。

這份修正差異做了什麼(作者自述,待你驗證,不是結論):
- 讀程式檔與筆記一律用內容編號:_nodehome_list 加可選輸出參數 oids(一般檔的 NFC 路徑 → 內容編號),_drift_list 順便記進 _DRIFT_OID_CACHE,_drift_cat 用編號讀、查不到編號才退回「版本:路徑」;r2 的 NFD 重讀(_drift_cat_nfc)拿掉。
- 3.12 以前,_drift_py_names 先呼叫 _drift_py_too_deep:不到 15 萬字元的檔直接解析,大檔用 tokenize 量最長邏輯行,超過 2 萬個詞就退回正則(系統 python3.9 的 ast.parse 碰到極長單一運算式會 SIGSEGV)。
- 候選篩選(_drift_probe_candidates)每一行之前看預算;不帶路徑的名稱改查 _DriftNames(終點全文的識別字集合,由 _DriftProbeTree.names_in 建一次);_drift_probe_is_candidate 改成任一確定受影響就是候選、判不了的不提前停;兩端測試資料夾版面不一樣也算形狀改變(_drift_with_layout / _drift_layout_changed)。
- 判不了的說明點名讀不出的檔(_drift_bad_note、_DriftProbeTree.bad_paths)。
- _probe_parse 回傳多一個 bad 旗標,check 與 scan 看旗標決定評不評估;驗文法前反斜線先轉斜線。
- scan 的 --budget 上限 86400;「像不像副檔名」改成 _drift_looks_like_ext;_shebang_line_is_python 搬到 _head_is_shebang 旁;scan 也走 _drift_probe_prefetch;_NotelinesNet 失敗當場停。
- 既有測試 t_drift_unknown_blocks_check_not_scan 的假讀取失敗改成認內容編號。

錨定紀律(硬性):
- 每條 finding 必附一段從凍結 diff 逐字複製的原文引句(≥10 字),寫成單獨一行「引句:「…」」,引句內不要再包「」、不要跨行。
- 審材外查證寫成單獨一行「file: `路徑:行號`」(反引號必加)。
- 你指出的 blocker/major 必須附能當場翻紅的最小重現(一條測試或一條指令+輸出);附不出就如實標「未能重現」,severity 自降一級。
- git 實驗一律 git -C <你自己 mktemp 的臨時目錄>;不准在任何 repo 根跑 commit/reset/restore/checkout/stash,不准改任何 repo 裡的檔;不要執行任何掛鉤腳本。

抑噪紀律:
- 低嚴重度疑慮,給不出具體失敗場景就不要標。但未定義的詞、壞引用、內部不一致一律要報。
- 不能從 diff 指出具體受影響的 file:line,就不准臆測「可能會壞別處」。
- 不要讀 governance/review-reports/ 底下任何席報告與收貨紀錄。

輸出格式(硬性,收貨端機械檢查):
- 檔首第一個非空行:severity: <整份最高 clean|minor|major|blocker>
- 每條 finding:標題行「## F<n> <一句話>」(標題裡不寫等級);接著獨立一行「severity: <值>」、獨立一行「blocking: 是|否 — 一句判準」(否↔minor;是↔major/blocker);一行「引句:「…」」;敘述編號條列,只寫到讓人能重現為止——哪個輸入、走到哪一行、壞在哪;不准用「可能/或許/建議考慮」收尾,判不準在敘述裡標 ⚠。
- 某塊沒問題也寫「已看,無 finding」。沒找到問題就交 severity: clean。
- 最後一行總結:最嚴重等級、blocking 共幾條(總結句裡不要寫 severity 字樣)。
- 報告只寫進指定的報告檔,不改任何其他檔;交回時只回一句「報告已寫到 <路徑>,最高 X,共 N 條」。
