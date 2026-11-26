severity: clean

我找了一輪,沒有找到會做出錯行為的輸入。`q.py` 和 `w` 不是我建的,我沒碰。我自己的暫存已用字面絕對路徑刪掉。

**已驗主張**(都是在 c5be145a 的乾淨 clone 上跑的)
- 主張:`python3.14 scripts/test_lumos.py -k choice_kill_merge` 全綠。結果:307 passed、0 failed,其中包含新增的 `t_choice_kill_merge_events_cmd`、`events_order`、`hang_breaker`。
- 主張:事件行解析是線性的,沒有回溯。輸入:1500 個名字、約 52 萬字元的事件輸出,先過 `_kill_cap` 截斷。結果:1.76 秒。這是每個沒跑乾淨的壞法一次,而且需要上千支守衛測試才會到這個量級,不到值得標的程度。
- 主張:`{method}` 那段緊接殼層元字元才判形狀不支援,正常指令不被誤擋。輸入與結果如下。
  - `--tests {method}`:仍可合併。
  - `--tests '*{method}' 2>&1`:仍可合併。
  - `--tests=*{method} --info`:仍可合併。
  - `--tests {method})`:不支援。我沒有跑修前版本,所以沒有對照。
- 主張:共用的 `_cmd_arg_quote` 沒有改變 `{python}`、`{method}` 的引號行為。依據:程式讀碼,`_run_cmd_expand` 刪掉的兩個區域 import 在函式內沒有別處用到;Windows 雙引號寫法由既有測試 `[S80]` 守著,這次全綠。
- 主張:斷路器的兩個計數互相獨立,沒有新漏洞。檢查過的路徑如下。
  - 恢復時兩個計數都歸零。
  - `_kill_merge_trip` 共用,兩種計數跳開時行為一致。
  - 停用中試探逾時有事件行,不恢復。
  - 「編不過」不動任何計數(修前就是這樣)。
- 主張:`merge_failed`、`merge_back` 每個壞法開頭都清空,不會沿用上一個壞法的名單。依據:程式讀碼,清空在 `_kill_merge_screen` 開頭,套不上壞法提早回 single 的路徑也在清空之後。
- 主張:重試的上限、重試後快篩不帶腳本、`merge_init_off` 寫入與缺欄舊帳讀成空字典,測試都釘住了。
- 主張:Gradle 拒收初始化腳本(`Could not compile initialization script`)不會被 `_KILL_COMPILE_RE` 誤判成「編不過」而擋掉重試。依據:該正規式只比對 `e: …kt`、`Compilation error`、`Execution failed for task …compileKotlin`,不含這句。
- 圖譜鏡頭:改動沒有破壞固定席那些 INVARIANT(bound-tests-gate、guard-kill 的 rc 優先序與 `--json` 純度、lumos-cli-read 的 search 濾網),因為沒有改到相關的行為路徑。

**未驗範圍**
- 沒有用真的 Gradle 跑。事件行格式靠假 Gradle 與計劃裡的探針實測紀錄。
- Windows 上初始化腳本路徑含空白的實際引號行為沒有真跑。
- 巢狀類別(JUnit5 `@Nested`)的事件行,名字會對不到而落在未知層,只影響逐支順序(計劃〈實務隱患〉已寫)。
- 殼層元字元判斷只擋 `& ; | < >`。`{method}` 後面緊接 `)` 或 `` ` `` 之類不在此列,修前也沒擋,不算修補引入。
- 沒有逐項做破壞測試(沒有各改壞一次再看測試翻紅)。

**三問**
1. 修補有沒有引入新問題:沒有找到。歸因:無新 finding。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立:成立。證據是上面的 307 案全綠,以及 `--no-merge`、舊帳缺欄這些相鄰路徑的案例。
3. 新發現在修前、修後各是什麼結果:沒有新發現。

最高 clean,blocking 0 條
