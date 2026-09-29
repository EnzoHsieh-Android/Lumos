你是外部第三方 code reviewer。這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找作者沒看到的洞。

Diff 檔(git diff -U10,凍結版,引句只准引這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/code-存量漂移防線乙/r2-snapshot.patch(1500 行,含 scripts/lumos、scripts/test_lumos.py、圖譜筆記、考卷改寫檔)。
這份 diff 是「修正差異」:上一版(e8f17913)已審過一輪,這份是在它上面修掉 30 條發現後的差異(e8f17913..123aaf47)。只審這份差異本身有沒有引入新問題、修法本身有沒有沒修到的形狀;上一版未改動的部分不是這輪的範圍,除非這份差異的改動讓它們壞掉。
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(HEAD=123aaf47,可 Read/Grep 真代碼查證上下文;python3 零依賴單檔 CLI scripts/lumos,必須在 python3.9 能跑;測試 scripts/test_lumos.py,單支跑法 `python3 scripts/test_lumos.py -k <測試名片段>`)。
設計(這份 diff 要兌現的規格):同 repo 的 docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md 的〈做法〉第 0、2、3 節(「乙」:條件式回頭條件)。

這份修正差異做了什麼(作者自述,待你驗證,不是結論):
- 判 file/symbol/test 的樹快照改成 _DriftProbeTree,由 _drift_probe_tree 在列得出路徑時才建(列不出回 None);status 條件搬到 _drift_probe_one,只看筆記、不需要 git;指到的筆記讀不出來算判不了。
- 語料與候選篩選共用 _drift_probe_code_path:副檔名清單裡的檔或沒副檔名的檔(語料裡要開頭 #! 才算),不含 docs/、governance/。帶路徑的條件只讀那一支檔、不管它算哪一類。
- Python 定義改用 ast(_drift_py_names;字串與 docstring 裡的不算),語法壞掉的檔退回逐行正則 _drift_py_def_re。
- 條件裡的路徑在 _probe_parse 就正規化(_probe_norm_value:_posix_norm 加 NFC)。
- 範圍改動只算一次:_drift_probe_changes 用共用的 _nodehome_name_status(新增可選 codes 參數回狀態字母),筆記改名對照也從這一次拿;新增行的 diff 帶 --text(-diff 屬性的檔也看得到)。
- 同一個提交的樹清單加記憶(_drift_list,只記完整 40 字提交編號,上限 8 筆);列樹、起點圖譜、每條候選前都看預算。
- scan 加 --budget(預設 60 秒)、工作目錄模式看磁碟(_drift_disk_list:index 加未追蹤、扣掉磁碟上不在的)、列「型別::方法」這種不像檔案路徑的寫法(_drift_probe_path_warn)。
- 推送範圍的第一層(_notelines_new keep_other)對開頭欄位其他欄的行另對一次範圍淨差異的行號(拆出 _notelines_range_cand、_notelines_rows)。
- doctor E5 餵 _strip_inline_markup 剝過的那一版給共用判定;lumos set 第③項收尾前就成立的不列;drift check 的修法提示分預告句與條件式兩種;exam 先用第一層那套文法驗改寫檔、不合的回 2;改寫檔補期限。

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
