severity: major

## F1 light 模式的 --suite keys 沒有分片、也沒有選中比例的上限或退回機制,常見小改動可能把它悄悄變成「單行程跑幾乎全部測試」,比原本 4 片平行還慢

觀察:pre-push 對 light 改動多跑的那一趟

引句:「"$PY" "$REPO_ROOT/scripts/test_lumos.py" --suite keys --keys "$_SUITE_KEYS" > "$_sdir/s0-keys.log" 2>&1 || _krc=$?」

沒有帶 `--shard`,是單一行程、不分片執行。`_keys_suite_select` 選測試的方式是「原始碼整字提到任一關鍵字」(`scripts/test_lumos.py` 新增的 `_keys_suite_select`),而 `_affected_test_keys`(`scripts/lumos` 新增)抓的關鍵字來源是這次改動的 hunk 裡 `def 名字` 抓到的函式名——包含巢狀的區域函式,不分是不是通用名字。

重現(我在本機用真正的 `_keys_suite_select`/`_affected_test_keys` 邏輯,對現有 1021 支測試實測,不是臆測):
```
$ python3 -c "...import scripts/test_lumos.py 當模組..._keys_suite_select(tests, ['check'])..."
check -> 1021 tests, took 0.35 s
run -> 686 tests, took 0.37 s
```
`scripts/lumos` 現有的三個巢狀函式剛好都叫 `check`(`file: \`scripts/lumos:10364\``、`file: \`scripts/lumos:10486\``、`file: \`scripts/lumos:10884\``),而 `check` 正是 `scripts/test_lumos.py` 每一支測試都會呼叫的斷言函式名——所以只要這次「light」小改動剛好動到其中一個 `check(fields)` 閉包(完全是會被判成小改動、走 light 路徑的那種修法:改一行邏輯,不動架構),`_SUITE_KEYS` 就會含 `check`,`_keys_suite_select` 選中的就是全部 1021 支測試,而且是**單行程、不分片**地跑完它們。

為什麼是 bug:這條路徑的存在理由就是「light 改動不用等全套」(patch 裡的訊息也講「推送前先跑…全套約 8 分鐘」對照「文件子集」),但 keys 子集沒有上限檢查、沒有「選中比例太高就退回正常全套分片」的邏輯——結果同一個改動反而比什麼都不做(直接吃到分 4 片平行的全套)還慢,因為它是先跑完 docs 分片(平行)、再單行程跑近乎全部測試(serial、無分片)。這不是風格問題,是「本來要更快」的機制在可預期的輸入下變成更慢,而且沒有任何機械檢查會攔住它、使用者也不會得到警告(只有「關鍵字子集:N 支」這行,N=1021 也只是印出來,不會觸發任何 fallback)。

severity: major
blocking: yes

## F2 keys 那趟(light)跟 docs 分片是串行、不是平行,浪費本可重疊的等待時間

觀察:pre-push 裡,`_suite_mode == "light"` 的處理區塊出現在 shard 迴圈的 `wait` 全部完成**之後**:

引句:「for _p in "${_pids[@]}"; do wait "$_p" || _rc=1; done」
引句:「if [[ "$_suite_mode" == "light" ]]; then」

也就是「文件子集(平行分片)」跑完、所有分片 `wait` 收斂之後,才開始跑 `--suite keys`(單行程、序列)。這條路是 pre-push 的常見情境(light 對應「改到程式檔但判成小改動」,比純文件推送常見得多),但它從設計上就沒有讓 keys 那趟跟 docs 分片重疊——即使 keys 子集很小,也要等 docs 分片全部收斂才開始起算,總時間是「docs 分片時間」+「keys 序列時間」相加,而不是取兩者較大值。

為什麼是 bug 而不是風格:這正是整批改動要解決的問題(等待時間),而 keys 那趟跟 docs 分片彼此獨立(各自呼叫獨立的 `test_lumos.py` 行程、寫各自的 log),沒有資料相依性需要序列化,純粹是實作上少做了平行化,退化成「先平行跑一段、再序列跑一段」而不是「全部平行跑、取最晚完成者」。配合 F1(keys 常常選到大量測試),兩個問題疊加時 pre-push 總時間可能明顯超過「全套 4 片平行(4-5 分鐘)」這個原本要打敗的基準。

severity: minor
blocking: no

## F3 push-check 輸出從即時 stderr 改成先寫暫存檔、跑完才 cat,卡住時使用者完全看不到進度

觀察:

引句:「_sg_out="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-sg-XXXXXX")"」
引句:「"$PY" "$GRAPHCTL" spec-gate --push-check "$_range" --repo "$REPO_ROOT" > "$_sg_out" 2>&1 || sg_rc=$?」
引句:「cat "$_sg_out" >&2」

改動前是 `spec-gate --push-check ... >&2`,輸出直接、即時地流到終端機的 stderr;改動後整段輸出先被重導進暫存檔,`spec-gate --push-check` 這個子行程執行期間使用者在終端機上什麼都看不到,要等它完全結束(不論是正常結束還是跑很久)才會一次把暫存檔內容 `cat` 出來。

為什麼是 bug:`spec-gate --push-check` 會載入圖譜、算波及範圍、驗雙向門留痕測試,不是保證瞬間完成的操作(這個 repo 的其它地方也明確記錄過「單行程跑全套要 25–30 分鐘、pre-push 熱路徑對耗時很敏感」這種對「使用者在等待時看不到東西」的顧慮,例如 CI 那段新加的註解本身就強調「不然只看得到『有片紅了』」這種糟糕經驗要避免)。這裡的改法製造了同一類體驗:pre-push 在這一步若耗時較久,使用者只會看到終端機停在原地、沒有任何輸出,容易被誤判成掛住而中途 Ctrl-C(而 pre-push 這支腳本此時可能正處於 git push 的關鍵流程中),這是行為劣化,不是單純風格差異。

file: `scripts/hooks/pre-push:116-127`(以修改後的相對位置描述,行號以 patch context 為準)

severity: major
blocking: yes

## F4 _sg_out 暫存檔沒有用 trap 處理中斷,腳本被打斷時會在多 ref 迴圈裡逐次遺留在 TMPDIR

觀察:F3 引的同一段程式碼,`_sg_out` 是在 `for _ppl in ...` 這個「每個 ref 各判一次」的迴圈裡,每次迭代各自呼叫一次 `mktemp` 產生新檔案,執行完 `spec-gate --push-check`、`cat` 完之後才 `rm -f "$_sg_out"`：

引句:「rm -f "$_sg_out"」

正常路徑(命令跑完、無論 rc 是多少)都會清乾淨,但清除是寫在程式碼順序裡的一般指令,不是 `trap ... EXIT` 或 `trap ... INT TERM`。如果使用者在 `spec-gate --push-check` 執行期間(尤其是配合 F3——這段現在使用者完全看不到進度,更容易被誤判成卡住而動手中斷)按下 Ctrl-C,或這個子行程被系統訊號中止,`rm -f "$_sg_out"` 這一行就不會被執行,暫存檔會遺留在 `${TMPDIR:-/tmp}` 下。多 ref 一次推送(例如同時推多個分支或 tag)會讓每個 ref 各自留一份没人清的殘餘檔。

為什麼是 bug 而不是風格:這是新引入的資源(改動前這段完全沒有暫存檔),而且沒有沿用同一支腳本裡別的地方已經在用的 pattern——往下幾十行的 `_sdir="$(mktemp -d ...)"`用完後也只是命令順序裡的 `rm -rf`,同樣沒有 trap,可見這不是刻意的設計決定,只是這批改動延續了既有(未受保護)的暫存檔清理慣例,把暫存檔的使用面擴大了一處。單一檔案外洩不是嚴重問題,但屬於「併發與資源」鏡頭該點名的殘留風險,而且是這批 diff 新引入的。

severity: minor
blocking: no

---

驗過但沒發現問題的路徑:CI 裡 `$extra` 不加引號展開成 `--suite docs` 兩個字——這是刻意利用預設 IFS 做字詞分割(`extra` 只會是空字串或固定的 `"--suite docs"`,沒有動態內容會被誤切),跟 pre-push 那邊用陣列 `_suite_args` 的寫法相比較不嚴謹但沒有構造出真的會壞的輸入;`--suite docs` 的 0 選中情境已用真跑腳本驗過目前是 191/1021,不會觸發(而 keys 的 0 選中情境該退回全套是有處理的,pre-push 裡 `_krc -eq 3` 有印訊息、不擋);`_docs_suite_select`/`_keys_suite_select` 每次呼叫約 0.35–0.4 秒,分片各自重算一次是有 CPU 成本但量級不到會造成使用者可感知延遲的地步;`t_runner_suite_flags` 裡刻意把測試自身會用到的關鍵字拆成兩段字串常數以避免巢狀自選(`"zzz_" + "nope_at_all"`)這個修法本身是對的,只是沒有推廣成「keys 選中比例過高時退回全套」這種一般性保護(見 F1)。
