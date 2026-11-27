severity: minor

我沒有動鎖,只照派工詞審查。逐個單獨編沒有造成逾時或吃光預算的場景。`cap()` 每次都用剩下的編譯預算、剩下的總時限、單支上限取最小。預算用完時 `compile()` 回 None,`probe` 的迴圈就收手。`apply_compile` 的寫入與還原都在 `try/finally` 裡。逐個單獨編只在整批紅且探針多於 1 個時才做。這比上一輪整批紅就一個都不記好,不會更慢。

severity: minor
blocking: 否
`scripts/lumos:29515`。逐個單獨編沒有隨機或輪替,永久編不過的探針每次都排在前面。
引句:「整批紅:逐個單獨編,能編的那一個才記補償(代碼審 r1 正確性 #2:一個永久編不過的探針不拖累同批)」
場景:有 K 個舊無效候選永遠編不過、排在字典序前面,後面還有真的能編的探針。每次執行編譯預算(`--max-seconds` 的 0.25)都先被前面 K 次紅編吃掉,後面的探針永遠輪不到,補償遲遲不記。結果只是多挑一次壞法、變慢,不會判錯。壞法數大時還會變成每次 run 固定多付 K 次編譯。
最小重現:探針 3 個,前 2 個永久紅,預算只夠編 2 次,第 3 個從不被記 cleared。建議把這一輪單獨編紅的探針記下,下輪排到後面,或限制單獨編次數。

severity: minor
blocking: 否
`scripts/lumos:80424`。檔頭只讀 32KB,但整份檔照樣整個讀進來、整個編碼。
引句:「head = text.encode("utf-8")[:_CHOICE_COV_SRC_HEAD].decode("utf-8", "replace")」
場景:`_choice_cov_req` 每個壞法行都先 `read_text` 整份檔,再 `text.split("\n")`,現在又對整份 `text.encode("utf-8")`。一支數 MB 的產生碼上有上千個選擇點時是 O(行數×檔大小)。這是舊有的問題,不是這次引入的。新程式碼反而比上一版的整檔正規式剝註解快。「只讀檔頭」只對剝註解那一步成立,所以速度上不會把正常操作擋下。若要改,先 `text[:_CHOICE_COV_SRC_HEAD]` 再編碼,或改成每個檔只讀一次。

其餘我看過的地方沒有問題:
- `_CHOICE_COMPILE_UNVERIFIED` 在 `one_batch`、`probe`、單獨確認三處都先於 `got[0]` 判斷。
- `_choice_task_swap`、`_choice_unit_variant` 的抽出只是搬位置,正規式沒變。
- `_choice_cov_pkg_of` 改用 `_strip_c_comments(kotlin=True)` 是線性掃描,沒有二次方。

總結:最高等級是 minor
