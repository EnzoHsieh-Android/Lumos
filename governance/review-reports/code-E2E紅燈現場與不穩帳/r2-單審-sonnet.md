severity: minor

兩條 finding 都是 minor,而且都出在 r2 新加的同 run_id 去重。範本腳本的 `after` 回呼、判定和回傳碼的「只提醒」保證、窗口 20 與門檻 3 的邊界,我都沒找到會壞的輸入。在複本 `/tmp/lumos-seat-work/code-E2E紅燈現場與不穩帳/單審-sonnet/repo` 切到 150ef621 跑 `-k android_e2e_flaky`、`-k android_e2e_judge_evidence`、`-k android_e2e_crash_log`,分別 22、5、8 條,全部通過。

### F1 history --flaky 的列級去重,會讓「重判被擋下」的空列蓋掉真正判出第二次才過的那一列
severity: minor
blocking: no
引句:「_e2e_window_put(rows, ids, r, r)   # 不穩帳:同一次執行重判的只算一次」
`scripts/lumos:41479`(`_e2e_history_cmd`)
歸因:有證據的修復回歸(去重是 r2 才加的)

1. 輸入:總表裡同一個 run_id 有兩行。
   - 第一行是正常判定,`items` 含 `f.yaml` 第二次才過(`"flaky": true`)。
   - 第二行是按功能跑卻沒帶 `--no-record` 重判被擋下的紀錄:`_e2e_judge_selected` 會寫一行 `_e2e_history_append(root, steps, None, ...)`,`items` 是 `[]`、`blocked` 有值、`cases` 照舊。
   - 走到的路徑:`history --flaky` 在列級用 run_id 去重,「留最後那行」,這一行就是空的。`f.yaml` 因此從分母和分子一起消失。
2. 同一份總表,點名那條路(`_e2e_flaky_counts`)是按 flow 各自去重,只在該 flow 有判出結果時才換掉舊的,所以仍算 1 次。兩條路對同一份資料結論不一致。計劃 S6 寫的是「跟點名同一套數法」,這裡沒做到。
3. 兩版重現,指令是 `lumos android-e2e history --repo <proj> --flaky`:
   - 修前 4e26f7bf 輸出:`f.yaml  1 次裡 1 次第二次才過  最近一次證據 .lumos/artifacts/android/R1`。
   - 修後 150ef621 輸出:`最近 1 筆紀錄裡沒有第二次才過的 flow`。
   - 修後 `_e2e_flaky_counts` 回 `{'f.yaml': (1, 1)}`,點名那邊沒丟。
4. 現有測試的重判案例只用 `--no-record` 重判,寫出的行有完整 `items`,所以抓不到這個分歧。
5. 影響:只提醒類的輸出被靜默弄丟,不改判定,所以我只給 minor。

### F2 重判多的總表搭配很大的 --last,去重的 `dq.remove` 掃窗口是平方級
severity: minor
blocking: no
引句:「for old in [x for x in dq if x[0] == rid]:」
`scripts/lumos:41413`(`_e2e_window_put`)
歸因:有證據的修復回歸(修前是直接 append,線性)

1. 輸入:`history --flaky --last 100000`,總表每個 run_id 連續兩行。
   - 走到的路徑:每個重判行都會掃一次整個窗口,窗口已經很大。
   - `ids` 計數只替「沒重判」的行省掉掃描,重判的行省不掉。
2. 實測 `_e2e_window_put` 逐行放入的耗時:

| 總表行數 | 窗口長度 | 耗時 |
|---|---|---|
| 5000 | 2500 | 0.11 秒 |
| 10000 | 5000 | 0.42 秒 |
| 20000 | 10000 | 1.7 秒 |

   耗時每翻倍行數約乘 4,外推十萬行約 40 秒。
3. 沒有重判的十萬行(`_e2e_flaky_counts`)是線性:0.86 秒,tracemalloc 峰值約 10MB。預設 `--last 20` 完全不受影響。
4. 這和 `_e2e_window_put` docstring 寫的「--last 給很大時不會變平方級」只對沒重判的情況成立。

### 修補鏡頭三問
同一個案例都用手工總表加 `_e2e_window_put` / `_e2e_flaky_counts` 跑。這一輪沒有重跑 r1-behavior-cases.json 的案例,也沒讀上輪報告。

- **① 原問題修復效果**:
  - claim:同一 run_id 重判不會把一次不穩湊成 3 筆。
  - input:1 筆舊 flaky 加本次,再重判 2 次。
  - expected:不點名。
  - case_source:`t_android_e2e_flaky_notice` 新案例,我另用手工總表補測。
  - before:未判定(沒跑修前版本的這個案例,修前沒有去重,依程式推得 4 筆)。
  - after:通過;手工總表 r59 重判 3 次得 `(3, 20)`;r42 在窗口內重判後得 `(3, 20)`,r42 被搬到最後,沒重複計。
  - comparison:去重在 flow 級成立,F1 是列級路徑的缺口。
  - 窗口邊界:60 筆分散的 id 封頂在 20,同一 run_id 全部重判時收斂成 `(0, 1)`,最後一行勝出,都正確。
- **② 修補處的正常、錯誤與相鄰路徑**:
  - 範本腳本的 `after`:
    - 回呼的 `rc` 是第一個位置參數,`ev` 和 `since` 靠預設值在每次迴圈綁定,綁定正確。
    - `rc` 為 None(逾時)時 `None != 0` 為真,會讀 crash 緩衝。
    - `since` 為 None 時 `crash_log` 回 None。
    - 殘留風險:`after` 若丟 `OSError`(例如寫 `crash.txt` 時磁碟滿),`rec` 還沒 `append`,這一步整筆不進 `steps.json`。修前是先存再收閃退紀錄。這個想不出非常合理的觸發場景,所以不單獨列 finding。
  - `case_results` 補回 flaky:用的是 `dict(i, flaky=True)` 複本,不會改到提交用的 `runs["cases"]`。`_e2e_history_append` 是唯一寫總表的函式,`feature_runs` 的內容不受影響。
  - 只提醒的保證:點名在 `_e2e_history_append` 末尾,不影響判定與回傳碼。
- **③ 新發現同一案例的修前與修後**:F1 修前顯示 1 次,修後顯示沒有;F2 修前沒有去重所以不存在這條平方級路徑。

### 圖譜鏡頭(固定席)
- **`guard-kill`、`design-loop`、`lumos-cli-lifecycle`、`lumos-cli-read`、`測試假綠形態`(五個 INVARIANT 節點)**:這份 diff 沒碰 guard kill 的 rc 優先序、JSON 純度、設計審處置閘、re-inject sentinel、search 預設排除、還原翻紅釘,不影響。
- **`loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger`(三個 RISK 節點)**:這份 diff 只動 `android-e2e` 子命令與範本腳本,沒碰審查帳、收斂記帳、可逆性帳,不影響。
- **其餘只列名的節點**:沒有逐條展開,未判定。
- **規格 S1–S6 與 d1**:
  - S1 到 S3 對得上,S2 的 `date` 格式有逐字相同的測試守著。
  - S4 補到 `case_results`。
  - S5 的去重成立,見 F1 的對照。
  - S6 的「沒判到的不算進分母」成立,但「同一次執行重判的只算一次」在列級與 flow 級有分歧,見 F1。
  - d1 守住:只讀 crash 緩衝、有 `since` 才讀、不清日誌。
- **未驗範圍**:
  - 真機與真 Maestro 沒跑,全靠假 maestro 與假 adb。
  - 角色卡沒附,略過。
  - 效能只量了 `_e2e_flaky_counts` 與 `_e2e_window_put` 在十萬行下的表現。

總結:整份最高嚴重度為 minor
