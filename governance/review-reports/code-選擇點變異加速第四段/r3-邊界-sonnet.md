severity: minor

我的立場是替極端輸入發聲。整份 1197 行 diff 逐 hunk 讀完,在 `/tmp/lumos-seat-work/` 底下用 python3.14 載入 `scripts/lumos`,對函式餵極端輸入實測。找到 1 條 minor,不擋推送;其餘極端輸入都撐得住。實測用的暫存目錄已刪。

**Finding 1**
severity: minor
blocking: 否
歸因:有證據的原有漏查(`_choice_merge_shape` 與 `--tests` 段的拆法本輪沒動,本輪新增的 `--init-script` 只是照樣插在同一個位置)
引句:「extra = "" if not init else " --init-script " + _cmd_arg_quote(str(init))」
file: `scripts/lumos:28810`(`_choice_merge_cmd`)與 `scripts/lumos:28793-28802`(`_choice_merge_shape`)
輸入:run_cmd 的 `{method}` 後面不留空白,直接接 `&&` 或 `;`,例如 `./gradlew :app:testDebugUnitTest --tests {method}&& echo`。
後果:`_choice_merge_shape` 把 `{method}&&` 當成同一段,合併指令變成 `--tests a.B.t1&& --tests a.B.t2&& --init-script X echo`。實測印出的字串就是這樣。shell 跑完第一支後會把 `--tests` 當指令執行(推論 rc 127,我沒真的跑 shell)。合併基準於是不會通過,這個平台組整組不合併,只影響速度,不改判定。
最小重現:`_choice_merge_shape("./gradlew :app:testDebugUnitTest --tests {method}&& echo")` 回傳非 None,再交給 `_choice_merge_cmd(..., init="/x")` 即可看到壞字串。
修前、修後:兩版 `scripts/` 完全相同,結果一樣。
建議:`{method}` 那一段含 shell 元字元(`&`、`;`、`|`)就讓 shape 回 None。

**三問**

1. **文件有沒有跟程式對不上、條款數字照程式跑得出來嗎**
   - 驗過、對得上:
     - S1:`--init-script` 插在 `--tests` 段之後、原字串其餘部分之前。實測 `&& echo done`、`-q`、`| tee`、`-p 'my dir'` 都符合;路徑含空白與單引號時由 `shlex.quote` 包好。
     - S2 預期值表:順序 b、d、c、a(截斷時 b、c、d、a)與程式一致。六萬個 ` > ` 的長行 0.00 秒解完。`\r` 結尾認得。
     - 〈用詞〉寫 `\xa0` 與全形空白算事件行尾,實測成立。
     - S3 與 S6 的計數、重試上限 `min(cap, max(remaining, 1.0))` 寫法跟程式一致。
     - PITFALL 行的 repro `_choice_merge_events("x.V > foo (bar) FAILED", ["foo (bar)"])` 實測 `failed` 為空,跟說法一致。
   - 我另外跑了 `-k choice_kill_merge_events`(32 支)與 `-k choice_kill_merge_hang`(21 支),全過。
   - 沒有發現條款、預期值表、用詞與程式對不上的地方。

2. **整份快照有沒有上一輪沒人看的角落**
   - 看了 `_gov` 欄位型別表與 `merge_init_off` 缺欄讀成空字典的路徑、`_isolated_worktree.scratch`、`_choice_merge_init_path` / `init_write` 的寫入失敗與 Windows 路徑、`_kill_merge_base_run` 的重試、`_kill_merge_trip` 與恢復歸零、`_kill_merge_failed_first` 的四層排序。
   - 結論:除了 Finding 1 沒有新問題。
   - 規模實測:1000 支測試乘上 1000 筆事件,事件解析 0.33 秒,不構成效能問題。

3. **新發現在修前、修後各是什麼結果**
   - 修前、修後的 `scripts/` 逐字相同,Finding 1 兩版行為一致。
   - 本輪 repair 只改計劃與守檔筆記,沒有改程式碼路徑,沒有修復回歸。

**已驗主張**
- 空輸出或 `None`:不炸,回傳全空。
- 只有 STARTED、輸出被截斷:不判掛住,落入未知層。
- `\r\n`:認得。
- 行首空白、頂格但缺類別或測試名的行:不算事件行。
- 剩餘時限 0 或負數:重試上限夾在 1.0 秒,且重試前先過 `hk.between()` 的停止檢查。
- 舊帳缺 `merge_init_off`:讀成空字典。
- `\u2028` 等會被 `splitlines()` 拆開的字元只影響順序,不改判定;我沒標。

**未驗範圍**
- 沒有真的跑 Gradle,所以 `--init-script` 的位置是否被 Gradle 接受、Gradle 拒收腳本的輸出是否真的觸發重試,都只憑計劃的探針實測紀錄。
- Windows 沒有實機,只看了 `list2cmdline` 與 `_WIN_CMD_SPECIAL` 的程式碼路徑。
- 沒有驗證 shell 在 `{method}&&` 情境下真的回 rc 127。
- 沒有逐支審 `test_lumos.py` 其餘新增案例的殺傷力。

最高 minor,blocking 0 條
