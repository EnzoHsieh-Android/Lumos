你是外部第三方 code reviewer。這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找作者沒看到的洞。

Diff 檔(git diff -U10,凍結版,引句只准引這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/code-存量漂移防線乙/r3-snapshot.patch(982 行,含 scripts/lumos、scripts/test_lumos.py、圖譜筆記)。
這份 diff 是「修正差異」:上一版(123aaf47)已審過兩輪,這份是在它上面修掉第二輪 19 條發現後的差異(123aaf47..6400f52d)。只審這份差異本身有沒有引入新問題、修法本身有沒有沒修到的形狀;上一版未改動的部分不是這輪的範圍,除非這份差異的改動讓它們壞掉。
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(HEAD=6400f52d,可 Read/Grep 真代碼查證上下文;python3 零依賴單檔 CLI scripts/lumos,必須在 python3.9 能跑——/usr/bin/python3 就是 3.9;測試 scripts/test_lumos.py 要用 3.12 以上跑,單支跑法 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k <測試名片段>`)。
設計(這份 diff 要兌現的規格):同 repo 的 docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md 的〈做法〉第 0、2、3 節(「乙」:條件式回頭條件)。

這份修正差異做了什麼(作者自述,待你驗證,不是結論):
- 不帶路徑的 symbol/test 條件算不算候選:改看「這次推送改到的程式或測試檔在終點的全文」有沒有這個名稱(_drift_probe_is_candidate / _drift_probe_cond_candidate / _drift_probe_candidates,終點全文用 _DriftProbeTree.texts 讀一次);原本看新增行,抓不到只刪三引號、只加 #! 這種推送。_drift_probe_changes 因此不再跑算新增行的 diff,改回傳 code_touched。
- 樹上列得出、內容讀不出來的程式檔記成 None,帶路徑的條件碰到算判不了;不帶路徑的條件找到定義就成立,沒找到而語料裡有讀不出的檔算判不了(_DriftProbeTree._unread)。圖譜讀不出的筆記建成讀不出的筆記(_drift_tree_env)。讀到 None 時換成 NFD 路徑再讀一次(_drift_cat_nfc)。
- 程式檔用 utf-8-sig 解碼(_drift_decode);ast 解析丟 MemoryError / RecursionError 時退回正則。
- 工作目錄模式讀檔每支之前看預算;帶路徑的條件在評估前每一版一次讀完(_DriftProbeTree.prefetch、_drift_probe_prefetch;scan 與 check 都做)。
- 條件的路徑正規化之後再驗一次文法;「.」本身不合法。
- 第一層(_notelines_new keep_other)的範圍淨差異改成用到才算(_NotelinesNet),git 失敗時整次回 None。
- 考試重放的第③項用改之前的圖譜算(_drift_exam_replay);scan 的 --budget 要是大於 0 的有限數;drift check 的表態指令一種一行;「不像檔案路徑」的判法改成副檔名要字母開頭、提示講明還沒建的根目錄檔;語料的 #! 判定改呼叫 _head_is_shebang;首行是不是 python 的 #! 抽成 _shebang_line_is_python 與派工鏡頭共用。
- 這是審查上限的最後一輪。

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
