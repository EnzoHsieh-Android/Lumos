severity: minor

我看了修補差異、讀了 `lens-repo` 的程式,也實測了管線與逾時。最高等級是 minor,只有一條 finding。

**實測結果**
- 死鎖:`cat-file --batch-check` 的寫入與讀取沒有死鎖。`subprocess.run(input=..., capture_output=True)` 走 `communicate()`,會同時寫 stdin、讀 stdout 與 stderr。我送過 40 萬個候選(輸入約 30MB),正常返回,沒有卡住。
- 逾時收子行程:`TimeoutExpired` 時 `run` 會先殺子行程並等它結束。逾時後我查過沒有殘留的 `cat-file` 行程,函式約 20.7 秒回 None,呼叫端走「算到一半」。
- 作者數字:我用 `git fast-import` 造了 50 萬檔的 repo。新路徑 0.05 秒、約 32MB,舊的 `ls-tree -r` 本身就要 0.17 秒、輸出 46MB。方向與作者一致(我沒有重跑他完整的 0.68 秒/236MB 對照,不能逐字確認這兩個數字)。
- 預算順序:`_LENS_SPEC_BUDGET` 是 30 秒,在 hook 的 45 秒總帳之內。落點先算、`impact` 最後吃剩的預算,每次 `impact` 都帶剩餘秒數當逾時。`impact` 的 `max(1.0, remain)` 最多讓單次多出不到 1 秒,迴圈入口有擋,不會連續超支。

severity: minor
blocking: 否 — 只有計劃文字含數萬個不同的程式檔候選時才觸發,觸發後是降級成「算到一半」、不會當掉或卡住,單人使用的威脅模型下不會遇到。
引句:「只查候選、不列整棵樹」
問題:成本從隨 repo 檔數增長,變成隨候選數線性增長,而且沒有候選數上限。`cat-file --batch-check` 查提交裡不存在的路徑,每個約 0.2 毫秒,不是便宜的記憶體比對。實測:5000 個 1.1 秒,2 萬個 4.4 秒,5 萬個 11.3 秒。
具體失敗情境:計劃上限 1MB,理論上能塞進約 10 萬個以上的不同程式檔名。實測 10 萬個就撞到 20 秒的單次上限,函式回 None。接著 `_lens_spec_code_files`、`_lens_spec_linked`、落點與只在提交裡的清單全部當成查不到,等於整份提交寫法的固定席資訊消失。這 20 秒也吃掉 30 秒預算的三分之二,後面的 `impact` 只剩約 10 秒。呼叫端會印出「程式檔、連結節點與落點只算到一半」的警示,所以不是靜默錯誤。一般計劃只有幾十個候選,耗時在毫秒級。
佐證:file: `scripts/lumos:49358`(`_spec_commit_present`,候選一次全送進 `cat-file`)

**已讀,無 finding**
- 管線大小:input 一次性交給 `communicate`,沒有自己寫 stdin 的迴圈。
- 輸出對位:輸出按行對應 `q` 的索引。`missing` 與 `ambiguous` 都是單行,所以不會錯位。
- `ls-tree` 分批:200 個一批,每批前都檢查剩餘預算,命令列長度沒問題。
- 輸入正規化:換行、NUL、`.`、`..`、空段、絕對路徑都先在 Python 端濾掉。
- 編碼:`surrogateescape` 對非法代理字元會丟 ValueError,已被 except 接住,回 None。
- 暫存檔:這段沒有產生暫存檔。實驗用的目錄已刪除。

最高等級 minor,blocking 0 條。
