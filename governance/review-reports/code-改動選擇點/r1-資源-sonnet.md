severity: major

圖譜鏡頭:這次沒附固定席節點(鏡頭計算超時),沒有固定席可逐條判。

## r1 一支檔裡有長函式,整次推送的語法樹掃描就整個算不出來,所有檔一起放行
severity: major
blocking: 是(會讓推送閘在中等大小的輸入下整個失效,且放行的是所有檔,不只那一支)

輸入:一個改到的 .kt,裡面有一個約 1500 條呼叫陳述的函式(約 59KB,例如註冊表、DSL 清單)。
路徑:`_choice_scan` 對整個暫存目錄只跑一次 ast-grep。
壞在哪:規則 C-18(刪掉呼叫陳述)的每個命中,輸出裡都帶著整個外層區塊的 metaVariables 與 labels。我量到一個命中約 39KB。輸出大小因此約等於命中數乘上函式大小,是二次方成長。超過 `_lint_wt_fsize_cap` 設的 64MB 後,ast-grep 被 SIGXFSZ 殺掉,回傳碼是 -25。
後果:丟出 `_ChoiceUnverifiable`,`_choice_push_scan` 把它記成 unverified,只提醒不擋。同一次推送裡其他檔的選擇點也一起沒被檢查。
預期:只有那一支檔略過,或分檔掃描。實際:整次推送放行,提醒訊息只說「掃描回 -25」。

引句:「raise _ChoiceUnverifiable(f"ast-grep 掃描回 {rc}")」
file: `scripts/lumos:76983`

最小重現(臨時目錄裡用 importlib 載入 `scripts/lumos`):
- `_choice_scan(cwd, {"Big.kt": <1500 行 registry.add(Item(i, "name_i"))>, "Real.kt": <小檔>}, 300)`
- 400 與 800 行:正常。
- 1500 行:`_ChoiceUnverifiable ast-grep 掃描回 -25`,小檔 Real.kt 也一起算不出來。
- 另一個形狀:函式裡 1000 行 `Log.d(TAG,"v"); val x = a + b`,直接跑 ast-grep 得到 80MB 的 out.json,其中 C-18 佔 78.6MB。

## r2 每個選擇點都複製整份檔案,另有命中對 ERROR 與乾節點的雙層迴圈,推送閘的 30 秒預算管不到
severity: minor
blocking: 否(只是慢,結果是對的)

- `_choice_identity` 每個壞法都做 `nb` 重建、兩次 `split("\n")` 和最多五次 `text.count`。`_choice_ctx_safe` 每次又切 `b[:s]`。成本是選擇點數乘上檔案大小。
- 我量到的整檔都改過的情形:
  - 8000 行 / 380KB:6.6 秒。
  - 20000 行 / 490KB:27.5 秒,峰值 RSS 291MB。
  - 行數乘 2.5、時間乘 4。
- ⚠ 以掃描輸出上限(約 8 萬個命中)往上外推,單檔約 7 分鐘,我沒實測。
- `_choice_file_points` 內沒有任何 deadline 檢查,`_KT_SIT_BUDGET` 只管到掃描,算完才超時。
- `_choice_err_lines` 與乾節點的 `any(...)` 是命中數乘上 ERROR 或乾節點數。3000 個命中配 3000 個 ERROR,量到 1.37 秒。乾節點量到 0.33 秒。數量再放大,成長是二次方。

引句:「lines, nlines = text.split("\n"), nb.decode("utf-8").split("\n")」
file: `scripts/lumos:77182`(`_choice_identity`)

## r3 choice-kill 設 `st.defer = True`,第一個 SIGTERM 後最久還要等一條基準或壞法跑完,被工具逾時升級成 SIGKILL 時測試程序會殘留
severity: minor
blocking: 否(沒重現;設計取捨,文件有寫)

情境:對話工具逾時先送 SIGTERM、隔幾秒再送 SIGKILL。
- 走到:`_ChoiceKillRun.run` 設 `st.defer = True`,第一個訊號只記下、不丟 KeyboardInterrupt。
- 壞在哪:正在跑的那一條配方要等跑完才停,基準最長 600 秒。SIGKILL 殺不到用 `start_new_session` 開出去的測試程序群組(例如 Gradle),`/tmp/lumos-wt-*` 隔離工作樹也留著,只能等清殘骸。
- 對照:`_situation_rule_kill` 沒設 defer,第一個訊號就收程序群組。

引句:「st.defer = True」
file: `scripts/lumos:` 位於 `_ChoiceKillRun.run`(行號在 patch 3739 行附近)

## r4 `_choice_test_blobs` 在 `--max-seconds` 外對每支守的測試各跑一次整棵樹的 `git grep`
severity: minor
blocking: 否(沒在大 repo 量過)

- 路徑:`_choice_kill_report` 在總時限結束之後呼叫 `_choice_test_blobs`。
- 它對每個測試名跑 `git grep -l -F -e <名> <sha>`,單次 timeout 是 `_lens_git` 預設的 20 秒,沒有共用 deadline。
- 本 repo 約 2 萬檔,一次 0.27 秒;100K 檔以上的 Android repo 上,N 支守的測試會讓收尾多出 N 乘上數秒到 20 秒,而 1800 秒預算已用完。

引句:「r = _lens_git(rr, "grep", "-l", "-F", "-e", n, at_sha, "--")」

## 其他逐項判
- ①子程序收尾:`_choice_sg_run` 在逾時與例外都有 `_kill_proc_group`,並在 finally 取消登記;暫存目錄由 `TemporaryDirectory` 收掉。`_isolated_worktree` 新增的 `_KILL_WT_LIVE` 在 finally 拿掉。除 r3 外沒找到殘留點。
- ②預算:推送前讀帳與讀放行檔各有 30 秒;掃描逾時一律走 unverified 放行,是設計。除 r1 與 r2 外沒看到把正常推送擋下的路徑。
- ③記憶體:帳讀取沿用 `_gov_rows_at`(整本讀進記憶體再切行,約 2 到 3 倍帳大小),在作者自量範圍內。更糟的形狀是 r1 與 r2 兩條。

臨時目錄 `/private/tmp/lumos-seat-work/code-改動選擇點/資源-sonnet` 已刪。

最嚴重:major;blocking 共 1 條
