severity: major

審查範圍:r1-pkgA.patch,逐 hunk 讀完。最後一行有總結。其他確認結果放在文末。

## 1. 開跑先量齊全部單支基準,時限不夠時整次零進度,跟 `--no-merge` 的行為不一致
severity: major
blocking: 是
引句:「b_rc, b_tail, b_el, b_to = _kill_run(cmd_of[m], c.run_dir, min(max(600.0, c.floor), max(mg.remaining(), 1.0)))」
引句:「if mg.remaining() < len(uniq) * _CHOICE_MERGE_UNIT_SECS * _CHOICE_MERGE_BUDGET_K:」
file: `/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28912`、`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28954`

失敗場景:
- 能不能量齊,只靠「剩下時限 ≥ 支數 × 10 秒 × 1.5」這個固定單價判斷。
- 真實單支基準只要比 15 秒貴,這個判斷就放行,但量齊會把整個時限吃光。
- 時限一到,下一支基準前的 `hk.between()` 丟 `_KillHalt`,連一個壞法都沒判完就收尾,rc 2、「還有 N 個沒跑」。
- 再跑一次是同樣結果,因為基準沒有跨次快取,所以永遠沒有進度。
- `--no-merge` 逐支流程是邊跑邊量:第一個壞法只需要第一批測試的基準,時限內會有進度。
- 被時限截斷的那一支基準還會以 `b_to=True` 寫進 `c.baselines`。退回逐支時它會被記成 `abort`「baseline 非綠」,而 `--no-merge` 會讓它跑完。
- 這跟「有疑慮就退回逐支、跟 `--no-merge` 行為一字不差」的宣稱衝突。

重現(3 支測試、2 個壞法、`--max-seconds 50`;ready 檢查要 45 秒所以放行;假 Gradle 讓每支單支基準睡 20 秒):
- 腳本:`/tmp/lumos-seat-work/code-選擇點變異加速/正確性-sonnet/budget.py`,指令 `python3.14 budget.py`。
- 腳本把 `test_lumos._CKM_GRADLE` 換成「單支基準睡 20 秒」的版本,其餘沿用既有 `_ckm_repo` / `_ck_run`。

```
merge    rc 2 secs 54 judged mutants: 0 run: [(0, 0, 0, False)]
  calls: [('alphaCase','base'), ('bravoCase','base'), ('charlieCase','base')]
no-merge rc 2 secs 70 judged mutants: 1 run: [(1, 0, 1, False)]
```

⚠ 編排者判斷用:
- 這個重現是人造的(20 秒對 10 秒單價)。
- 實驗專案實測約 5 到 6 秒,Android 真實專案暖機單支多半更貴,但我沒有實測數字。
- 方向上,量基準的成本只要超過單價假設,時限小的跑法就會中招。
- 修法方向(我沒驗證,供參考):量基準那段別被剩餘時限截斷、改成量不完就整組不合併,或把已量到的基準留給逐支使用。

## 2. 第一個訊號落在「停止旗標檢查」之後、程序登記之前,合併呼叫照跑完整段
severity: minor
blocking: 否
引句:「_choice_merge_clear(c.sh["rdir"])」
引句:「if c.hk.should_stop is not None and c.hk.should_stop():   # 套完壞法、開快篩之前已收到第一個訊號或時限到了:還原、不開快篩、不交列」
file: `/Users/enzo/harness/lumos-choice-speed/scripts/lumos:29052`、`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:29055`

失敗場景:
- 停止旗標檢查之後,先 `rmtree` 結果資料夾,再 `_kill_run` 開程序並登記。
- 訊號若落在這段(rmtree 加 Popen,約幾十到幾百毫秒),`on_signal` 找不到帶標記的程序,只設 `interrupted`。
- 之後快篩照樣開跑到結束,結束後才 `raise _KillHalt`。這就是設計要避免的「拖過對話工具寬限期」。
- 合併基準那一段(`c.hk.between()` 到 `_kill_run` 之間)同樣有這個窗口。
- 窗口很窄,機率低,所以只標 minor。

重現:`/tmp/lumos-seat-work/code-選擇點變異加速/正確性-sonnet/race.py`。
- 腳本在第 2 次 `_choice_merge_clear` 內呼叫 `mg.on_signal()`,模擬訊號正落在檢查之後。
- 輸出的 calls 最後一筆是 `('alphaCase,bravoCase,charlieCase','1')`,表示壞法 1 的合併呼叫在 interrupted 為 True 之後仍然開跑並跑完,`interrupted: True`、rows 空。
- 修法方向:`_kill_run(merge=True)` 登記程序後、或 `_choice_merge_clear` 之後,再看一次 `mg.interrupted`。

## 3. pitfalls manifest 2 條
兩條都判誤報。
- `scripts/lumos:28996` 的 `open(target, encoding="utf-8")`,在 `with open(...) as fh:` 內,離開區塊必關。
- `scripts/lumos:29007` 的 `open(target, "w", ...)`,同樣是 `with open(...) as fh:`,寫完必關。

## 4. 正確性追案例結果
以下逐項走過,沒找到會把會被殺的壞法記成存活的輸入,只留下上面兩條。

- **合併判全部存活的條件**:要同時滿足 rc 為 0、結果檔無 failure/error、lane 每支名字恰好對到 1 個完整名。
  - 比「單支 rc 0」更嚴,不會多放行。
  - 有 failure 但 rc 0(例如 ignoreFailures)走 `fail`。
  - 多個 `--tests` 只命中其中一個、Gradle 仍 rc 0 的情況,被「對不到名字」擋成 `unclean`。
  - lane 是所有壞法測試的聯集,是每個壞法測試集的超集。超集裡不相關的測試紅了,只會退回逐支,方向安全。
- **合併永遠不判殺掉**:`_kill_merge_emit` 只會交 `survived` 或 `abort`。壞法編不過或測試程序崩潰時,都退回逐支,由逐支流程判殺掉或編不過。
- **退回逐支**:跑 `t_choice_kill_merge_*` 共 109 項全綠。
  - 除了上面第 1 點(基準量法不同),我找不到退回逐支與 `--no-merge` 的其他差異。
- **多平台**:`survived`、`plats`、`streak` 都以平台為鍵。`finish` 要所有有配方的平台都判存活才記 merged,沒有發現混記。
- **`--only`**:壞法數少於 2 就不合併,行為符合文件。
- **斷路器**:只有 `pass` 歸零、`fail` 與 `compile` 不計不歸零,跟文件一致。
- **新舊帳互讀**:缺 `judged` 的舊帳讀成 `single`,未知欄位舊程式忽略。`_choice_ledger_status` 取 `evs_k[-1]`,與 `_choice_disposition` 看的是同一筆。

## 5. 圖譜鏡頭、角色卡與鎖
- 派工詞明講沒附固定席節點,所以沒有逐條要答的筆記。
- 我只核對了 diff 內兩篇筆記(`guard-kill`、`規格閘`)的宣稱,與程式一致:
  - `on_first` 不設回呼時,人裁與 guard kill 行為不變。
  - `judged` 缺值讀成 `single`。
  - `merged + single` 等於判定數。
  - `base_secs` 無條件進位。
  - `--only` 已放行行的提示。
- 兩篇筆記有一處沒講到:`guard-kill` 的合併段沒提「量基準被剩餘時限截斷」。這點與第 1 點相關,不另列。
- 角色卡:沒附前端或後端卡,略過。
- 鎖:`/Users/enzo/.cache/lumos/dispatch-lens/99f6fb48490f070f03634f0f7fa53515af8d17065b27bb18781c91a3986c2b4f.json.warming` 不存在,沒有要處理的鎖。

臨時檔留在 `/tmp/lumos-seat-work/code-選擇點變異加速/正確性-sonnet/`(`budget.py`、`race.py`、`race.log`),由編排者收貨後刪。

總結:最高嚴重度 major
