severity: clean

沒有找到能讓本該被擋的推送放行、或讓全套測試沒跑就推出去的洞。實驗用 `/bin/bash` 3.2 跑真的掛鉤,搭配假的 `scripts/lumos`。實驗目錄已刪。

**1. `_PP_BLOCKED` 沒被設**
- 每個 `pp_record_block` 呼叫都在頂層,不在 `$(...)`、管線或 `while read` 子 shell 裡,旗標不會因此丟失。
- 實驗證據:八道閘各回 rc 1 都以 1 結束、全套 0 次;`anchor` 與 `doctor` 回 2 到 127 照舊記成擋下。
- 掛鉤內只有開頭「沒有 `scripts/lumos`」和最後一行有 `exit 0`,迴圈內沒有 `break`,所以記下之後沒有提前放行的路。
- 環境變數預設 `_PP_BLOCKED=0 _PP_NBLK=-5 _PP_NREFS=0 _CL_KG=0` 都在掛鉤內無條件重設,doctor 擋下時仍 rc 1。反過來預設 `_PP_BLOCKED=1` 也沒有用,沒擋時照樣放行,這是無害的。
- 暫存目錄在擋下之後被刪掉:旗標與筆數在記憶體裡,仍然 rc 1,只是少了彙總明細。
- file: `scripts/hooks/pre-push:100-106`,`scripts/hooks/pre-push:677-682`

**2. `LUMOS-BLOCKS:` 偽造或被蓋掉**
- 這一行只決定記幾筆、記什麼原因,rc 1 時至少記一筆,所以偽造最多改彙總文字,改不了放行與否。
- 實驗證據:空值、只有逗號、重複種類、`$(touch /tmp/pwn-ppc)`、整行不存在,都以 rc 1 結束、全套 0 次,`/tmp/pwn-ppc` 沒被建出來。原因字串是寫死的對照表,不會把輸出展開或執行。
- 這一行出現在 stdout 最後,stderr 先寫,所以 `tail -n 1` 取到的是真的那一行。
- file: `scripts/hooks/pre-push:566-594`

**3. 版本探測誤判**
- 舊版 lumos 沒有 `--keep-going`,探測得 0,掛鉤不帶旗標,rc 1 時照舊記一筆,仍 rc 1。
- 探測自己回 rc 2 時,同樣不帶旗標,仍 rc 1。
- 探測被訊號殺掉(rc 130)時,掛鉤以 130 停下。
- 假的 help 說有 `--keep-going` 但實際拒絕(`check` 回 2)時,走既有的「其他非零放行」,這是舊行為,而且要先控制 `scripts/lumos` 才做得到,不算新洞。
- 真的 lumos 的 `code-loop check --help` 回 0,內含 `--keep-going`。
- file: `scripts/hooks/pre-push:563-571`

**4. 中斷變成放行**
- 掛鉤收到 SIGINT 時,在 `drift` 內以 130 結束、全套 0 次,即使代碼審已經記了擋下。
- 在 `impact` 內收到 SIGINT 也以 130 結束。
- 收到 SIGTERM(在 `test-layers`)以 143 結束。
- 收到 SIGHUP 以 129 結束,git 都視為失敗。
- 各道閘 rc 255 都被 `pp_stop_if_signaled` 接住,以 255 結束。
- file: `scripts/hooks/pre-push:300-303`

**5. `push-summary` 回 0 改變結果**
- 實驗證據:回 0、2、137 或舊版不認得,最後都是 `exit 1`。回非零時會印簡版彙總,不會多印第二次。
- file: `scripts/hooks/pre-push:677-682`

**6. `blocks` 檔被換掉**
- 檔案在 `mktemp -d` 建的暫存目錄裡,只用來印彙總,不影響擋不擋。
- 欄位把 tab 與換行換成空白,原因是寫死的字串,ref 名不能含控制字元,沒有注入面。

**7. 一件不構成 finding、但留給主審知道的事**
- 因為 `anchor` 擋下後不再停,測試檔被竄改(沒簽名)時,後面的 `spec-gate --push-check` 與 `code-loop check` 的合約測試會跑到那份被改過的測試。
- 我查了 `_spec_gate_push_check`,它沒有寫帳;`_bound_tests_check` 沒有留下可被後續推送沿用的綠燈快取。
- 這次推送一定被擋,而且能改測試檔的人本來就能直接跑程式碼,所以我不列成 finding。
- 簡版彙總文字也已明講「綠燈不算數」。

最高等級 clean,blocking 0 條。
