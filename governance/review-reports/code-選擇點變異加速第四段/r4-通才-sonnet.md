severity: minor

審查範圍:`r4-repair.patch` 全部 517 行(文件、`scripts/lumos`、`scripts/test_lumos.py`),加上修補處在 `scripts/lumos` 裡的呼叫端。

**Finding 1**

severity: minor
blocking: 否
歸因:有證據的原有漏查(r3 補丁「同族」沒收乾淨,不是這輪修補才壞的)

引句:「if any(ch in seg for ch in "&;|<>"):   # 含 {method} 的那一段緊接殼層元字元」

- 場景:`run_cmd` 是 `(./gradlew :app:testDebugUnitTest --tests {method})`,`{method}` 後面緊接 `)`。
- 修前、修後結果相同:`_choice_merge_shape` 都回傳形狀,`seg` 是 `{method})`。
- 在 `/tmp` 副本實測,`_choice_merge_cmd(..., ["aCase","bCase"])` 組出 `(./gradlew :app:testDebugUnitTest --tests aCase) --tests bCase)`,有語法錯誤。
- 後果:合併基準白跑一次後不合併、照逐支跑,不會判錯也不會壞資料。反引號那案因為引號不成對已被擋。
- 判不準 ⚠:這個坑在實務上多常見(括號子殼層的 `run_cmd`)。
- 建議:改成只准一個白名單字元集,或把 `()` 也列進黑名單。這個新增守衛正文只列 `&;|<>`,而 `)` 同屬「切不出乾淨一段」的同一族。
- 因為只是白跑一次、不會判錯,不構成 blocking。

**三問**

① 修補處有沒有引入新問題:沒有。
- 逐段讀過 `_choice_merge_shape` 的新守衛。
- 也讀過 `_kill_merge_note_unclean` 抽出後的三個呼叫點,累計與 `last_unclean` 的寫法跟原本逐字相同。
- `_kill_merge_trip` 兩個計數歸零。
- 常數 `_CHOICE_MERGE_NO_RESULTS_WHY` 取代字面字串,值相同。

② 正常、錯誤與相鄰呼叫路徑是否仍成立:成立。
- `_choice_merge_shape` 只有一個呼叫者(`_kill_merge_ready`,`scripts/lumos:29035`),沒有被時限提示或別的指令用到。
- `_CHOICE_MERGE_BASE_WHY` 只用於印字(`scripts/lumos:29130`),記帳原因不經它換字,新增的「逾時(跑到測試後掛住)」鍵跟 S10 補述一致。
- `{method}` 後面空一格再接 `&&` 的對照案仍合併,實測 `'*{method}' && echo` 回非 None。
- 試探恢復、跳開、通過這幾條路徑的處理沒變。

③ 新發現在修前、修後各是什麼結果:
- Finding 1 修前、修後行為相同,是漏洞沒補完,不是回歸。
- `&&`、`;`、`|` 三案新測試翻紅:拿掉新守衛後 `{method}&&` 會回傳形狀。
- 這份 patch 裡的新測試鎖住原守衛要擋的三種情況,但沒有 `)` 案。

**已驗**
- 實測(副本在 `/tmp/lumos-seat-work/code-選擇點變異加速第四段/通才-sonnet/lumos.py`):
  - `{method}&& echo` 回 None。
  - `` `echo {method}` `` 回 None。
  - `{method})` 回形狀並組出壞指令。
- 讀碼確認:
  - `_choice_merge_events` 對 SKIPPED 的分層正確。
  - `_kill_merge_screen` 在沒跑乾淨時才用事件行,有失敗時用結果檔名單。
  - `hang_streak` 在恢復與跳開時歸零。

**未驗**
- 沒有重跑 `test_lumos.py` 的新增案例,也沒做變異翻紅。
- 沒讀完整的 1293 行快照,只讀修補差異與修補處的呼叫端。
- 沒有逐條跑固定席筆記,也沒看新增殘留段。表態記錄(py-* 都是 na)看起來與這輪純同步 CLI 修補相符,但沒有逐題驗。

最高 minor,blocking 0 條
