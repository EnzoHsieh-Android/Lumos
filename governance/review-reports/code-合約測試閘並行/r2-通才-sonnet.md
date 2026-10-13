severity: minor

整體判斷:判紅綠、逾時、去重、tails 對應都跟改前一致,沒寫設定的消費專案行為不變。有一個修補只修了一半的問題:「出錯馬上往外丟」只在出錯的是第一項時成立。

## Finding

### 1. 「一支丟例外就馬上往外丟」只在失敗的是排序第一項時成立,且直譯器結束仍會等已開跑的執行緒
severity: minor
blocking: 否
引句:「# 一支丟例外(或按 Ctrl-C)就取消還沒開跑的、不等已開跑的跑完;已開跑的各自有逾時,會被 _kill_run 收掉」
file: `scripts/lumos:48191-48200`(`seen.update(ex.map(_one, list(jobs)))` 加 `except BaseException: ex.shutdown(wait=False, cancel_futures=True)`)

失敗場景(已在修後版本重現,在 `/tmp/lumos-seat-work/` 下的臨時目錄用 `_run_bound_tests` 直接跑):
- 設定 `parallel=2`,兩個平台,其中 `bad` 的 root 不存在,`good` 有一支睡 8 秒的測試。
- items 排成 `[bad, slow]`:0.0 秒丟出 `FileNotFoundError`,符合預期。
- items 排成 `[slow, bad]`:8.1 秒才丟出。
  - 原因:`ex.map` 依提交順序產出結果,迭代時先卡在第一支 slow 的 `result()`,後面 bad 的例外要等前面的跑完才浮上來。
  - 取消排隊的動作也跟著延後,排隊中的任務在這 8 秒內照樣開跑。
- 兩種排列的整個程序都是 8.17 秒才結束。
  - 原因:`ThreadPoolExecutor` 的工作者是非 daemon 執行緒,`shutdown(wait=False)` 之後,直譯器結束時 `concurrent.futures` 的結束掛鉤仍會 join 它們。
  - 所以計劃筆記「不會卡住前景」的說法不成立。最壞要等到那支測試的逾時(最長 180 秒,整套跑 600 秒)。
- Ctrl-C 同理:主執行緒拋出後,程序要等工作者收尾才退。循序模式的舊行為是 `communicate` 被中斷後程序立刻結束(子程序成為孤兒)。
- 測試 `t_bound_tests_parallel_error_stops_fast` 把失敗項排在第一位,所以抓不到這個缺口。把失敗項移到最後,它會紅。
- 它在 0.0 秒內結束,而 slow 子程序要睡 12 秒,測完臨時目錄被刪,事後會有孤兒程序。

歸因:有證據的原有漏查,屬於修補只修了一半。
- 修前(c9bd21d2,`with` 區塊):兩種排列都等約 8 秒。
- 修後(5b05034f):失敗項排第一位時 0 秒,排最後時仍 8.1 秒。
- 驗證命令:`python3.14 t.py first` 與 `python3.14 t.py last`,結果見上。
- 這不影響判定正確性(最壞退回循序行為),所以維持 minor。

建議修法:改用 `as_completed`,或在每個 future 上 `add_done_callback` 偵測例外。計劃筆記與 S5 條款的文字要改成實際行為。

## 其他核對(無 finding)
- **secs 與 secs_kind**:`secs_kind` 只在 `secs is not None` 時寫入。
  - 讀者端沒有依賴 secs 的程式。
  - `_GOV_FIELD_TYPES` 沒有白名單拒絕未知欄位,新舊混讀無礙。
  - `_wall` 包含 `_run_bound_tests` 全段(含 `load_platforms`),語意合理。
- **設定警告的觸發面**:
  - `parallel: null` 與沒寫都不出聲;`1`、`1.0` 不出聲;布林、字串、0、負數、17、2.5 會出聲。
  - 警告走 stderr,不污染 `--json`。
  - 次數:每次 `_run_bound_tests` 呼叫印一次。spec-gate 與相依回歸會多次呼叫(`scripts/lumos:7661`),同一次操作可能印多次。
  - 即使沒有項目要跑(jobs 為空)也會先讀設定並警告。
  - 以上為輕微噪音,沒有具體後果,不標 finding。
- **併發共用狀態**:`_kill_run` 每次用獨立的 `TemporaryFile` 與新的 session。
  - 治理帳與 tails 只在主執行緒寫,無競態。
- **測試穩定性**:`t_bound_tests_secs_is_wall_time` 的窗口是 `1.8 <= secs < 3.5`。
  - 舊實作的加總至少 4.0,翻紅有保證。
  - 極慢的機器上新實作可能超過 3.5 造成偶發紅,是穩定性的小風險。
  - 同步標記判法(最多等 2 秒)在正常 CI 穩定。
  - `config_values` 測試約 39 秒,偏慢。

## 修補核對三問
1. **原問題的修復效果有何行為證據?**
   - R1:跑 `python3.14 scripts/test_lumos.py -k bound_tests_parallel`,26 條全過,含 `secs_kind=wall` 的斷言。
   - R2:`t_bound_tests_parallel_config_values` 的九種值都符合預期(警告與否、循序或並行)。
   - R3:只有失敗項排第一位時,修補才有行為證據(0.0 秒對修前 8 秒)。
   - R4:同步標記取代計時重疊,方向正確。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立?**
   - 正常路徑(`matches_sequential`)逐項相同、順序相同,成立。
   - 錯誤路徑只部分成立,即 finding 1。
   - 相鄰路徑:spec-gate 與 fix-check 共用 `_run_bound_tests`,沒設定時行為不變。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 失敗項排最後:修前約 8 秒,修後 8.1 秒,沒有改善。
   - 失敗項排第一位:修前約 8 秒,修後 0 秒,有改善。
   - 兩者的整個程序都是約 8.17 秒才結束。

## 證據表
| claim | input | expected | case_source | 命令與結果 | 比較與歸因 |
|---|---|---|---|---|---|
| 出錯即停 | `parallel=2`,items `[bad, slow]` | 立即拋出 | 本席自造 | 修後 0.0 秒;修前(`with`)約 8 秒 | 修補有效,限第一位 |
| 出錯即停 | `parallel=2`,items `[slow, bad]` | 立即拋出 | 本席自造 | 修後 8.1 秒;修前約 8 秒 | 無改善,原有漏查 |
| 程序結束 | 同上 | 不卡前景 | 計劃筆記宣稱 | 兩種排列都是 8.17 秒結束 | 宣稱不成立 |
| 並行測試 | `-k bound_tests_parallel` | 全綠 | binding | 26 passed,0 failed | 通過不代表覆蓋失敗項在後的情況 |

## 圖譜鏡頭
- `bound-tests-gate`:★INVARIANT★ 的內容是「紅、懸空、偽證據、unfilterable 一律擋;沒算出來或沒綁則不擋但記帳」。這份 diff 沒有破壞它。
  - 判定邏輯不變。
  - 新增 `secs_kind` 只加欄位。
  - 程式只改排程。
- `lumos-cli-read`、`測試假綠形態`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`:這份 diff 不碰其行為或合約。
  - 測試假綠形態的前置斷言要求:`parallel_config_values` 以標記證明「現場確實並行」,符合。
- 其餘節點(`loop-convergence-recording`、`pitfalls-code-loop` 等 RISK 節點):未受影響。

未驗範圍:Ctrl-C 的實機互動行為、Windows 的 `killpg` 路徑、整套跑(whole-suite)逾時 600 秒路徑下的並行。

總結:最高等級 minor
