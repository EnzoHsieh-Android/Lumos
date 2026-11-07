severity: major

這份設計有兩處跟既有做法不一樣,一處是計數檔,一處是「重用權重」。理由判法和擋下訊息的形狀是一致的。

## 1. 分層與依賴方向

## F1 計數檔只說「照寫法」,沒說呼叫還是複製,會長出第二份寫入實作
severity: major
blocking: 否
引句:「寫法照 `scripts/lumos` 既有的家目錄快取寫入那一套(子目錄、驗目錄可信、只攔 OSError,單次寫入一行)」
file: `scripts/test_lumos.py:48948-48950`
- 既有慣例是:`test_lumos.py` 不抄 `scripts/lumos` 的規則,而是用 `_load_lumos_inproc()` 去讀活的函式。`_durations_table_path` 的註解寫明「路徑與讀表規則只在 scripts/lumos 一份,不抄第二份」(代碼審 r2 架構對齊席)。
- 計劃只說「寫法照那一套」,沒指定走 `_load_lumos_inproc()`。照字面實作會在 `test_lumos.py` 抄一份 `_mkdir_trusted_under_home`、`_trusted_private_dir` 和 O_APPEND 寫入。
- 要修的是補一句「呼叫 `_load_lumos_inproc()` 取 `_mkdir_trusted_under_home` 與 `_trusted_private_dir`」。

## F2 擋下判斷在 `_isolate_environment()` 之後,`Path.home()` 已是假家目錄
severity: major
blocking: 是
引句:「所以這條在 `_isolate_environment()` 之後才判得了;所以擋下時要照既有收尾把這一輪的暫存根目錄清掉」
file: `scripts/test_lumos.py:49597`(`main()` 入口),該函式在 `_isolate_environment()` 內把 `HOME` 設成假家目錄
- 既有程式在 `_isolate_environment()` 內把 `HOME` 與 `USERPROFILE` 換成 `gctl-run-*` 底下的假目錄。
- 計劃要寫 `~/.cache/lumos/full-suite-guard/events.jsonl`,而判斷點在隔離之後。照 `Path.home()` 寫,會寫進隨後被清掉的假家目錄,真機的 REVISIT 永遠讀不到計數。
- 既有先例的做法是先記下真 HOME,事後再還原(`test_lumos.py:28882`、`28901-28902`)。
- 計劃沒寫「進隔離前先記真 HOME」,S4 只驗了子程序的私有 HOME,這個缺口沒被覆蓋。

## 2. 命名與錯誤處理

## F3 「重用 `_shard_by_duration` 的權重」,但權重是函式內的區域算式,沒有可呼叫的單位
severity: minor
blocking: 否
引句:「估法重用 `_shard_by_duration` 的權重:耗時表秒數,表裡沒有的用全表中位數,下限 `_DURATION_FLOOR`」
file: `scripts/test_lumos.py:48987-48992`
- 權重只在 `_shard_by_duration` 內以 `w = {...}` 內聯算出,沒有獨立函式。
- `_chat_full_suite_block` 要用同一算式,不是抽出共用的權重函式,就是再寫一份。計劃沒講抽哪一支,等於預留第二份算式。
- 修法是在計劃寫明「抽出 `_duration_weights(names, table)`,`_shard_by_duration` 與擋下判斷共用」。

## F4 耗時表「讀不到」的處理跟既有分片分支不同,且用語含糊
severity: minor
blocking: 否
引句:「耗時表讀不到時改用支數比例。」
file: `scripts/test_lumos.py:49714-49720`
- 既有分片分支把兩種情況分開處理。`_load_durations_table()` 回 `None` 時照名字輪流分;丟 `ValueError`(格式壞)時印「擋下:耗時表讀不懂」並回 2。
- 計劃的「讀不到」沒分「沒有表」與「格式壞」。照字面把壞表也退成支數比例,就跟既有「壞表一律擋、不退回另一種分法」(`test_lumos.py:48953-48960` docstring)不一致。
- 要補的是寫明兩種情況各自怎麼處理。

## F5 計數檔路徑在同一份計劃裡寫了兩個
severity: minor
blocking: 否
引句:「計數檔(`~/.cache/lumos/full-suite-guard.jsonl`)八週內逃生門放行次數超過擋下次數」
file: `scripts/lumos:69211`(既有慣例:`~/.cache/lumos/<子目錄>/<檔>`)
- RETIRE-IF 寫 `~/.cache/lumos/full-suite-guard.jsonl`,做 7 與 REVISIT 寫 `~/.cache/lumos/full-suite-guard/events.jsonl`。
- 既有慣例是「子目錄/檔」,RETIRE-IF 那條跟既有不一致,要改成子目錄那一個。

## 3. 第二種做法

- 計數寫法只有一種做法跟既有對得上,就是 `_drift_m1_ledger_miss`(`scripts/lumos:62015-62043`):
  - 逐層建目錄並驗可信,`O_APPEND|O_NOFOLLOW|O_NONBLOCK` 開檔,`fstat` 確認是自己的一般檔,短寫算失敗,只攔 `OSError`。
  - 計劃的描述跟它吻合,所以「家目錄快取的 jsonl 追加」不算新做法。
  - `_home_cache_write` 是整檔原子取代,不是追加,不該拿它當 events.jsonl 的模板。計劃應指名 `_drift_m1_ledger_miss` 為模板,不要只寫「那一套」。成不成第二種做法,取決於 F1 的複製問題。
- 「理由照 lint-waive 判法」跟既有一致。`cmd_lint_waive`(`scripts/lumos:41861`)的判法是去空白後 ≥10 且 `re.search(r"[^\W_]", ...)`。計劃的「至少 10 字、至少一個文字或數字字元」描述相同,只要實作時共用或照抄同一條正則即可。
- 不過 `[^\W_]` 的判法目前內聯在 `cmd_lint_waive`,沒有獨立函式(`scripts/lumos:14101` 的 `_count_real_chars`之類另有近似函式)。計劃沒寫共用還是複製,風險同 F3,併入 F3 處理。
- 「對話裡不切片」的做法 `_fanout_wanted` 加條件,沿用既有的「環境標記當第二道」模式(`LUMOS_FANOUT_CHILD`,`test_lumos.py:49391-49400`),一致。
- 擋下訊息的形狀(stderr、「擋下:…」開頭、rc 2、指令各占一行)跟既有一致(`test_lumos.py:49670-49680`)。

## 4. 落點(lands_in)

- 落點是 `Systems/測試執行器`,理由與寫法合理,跟既有「執行器唯一進入點」的歸屬一致。
- 這篇在會談目錄還沒有,是計劃連結的新篇。實作時要用 `lumos new system 測試執行器 --code scripts/test_lumos.py --responsibility ...` 開,而且 `scripts/test_lumos.py` 屬 146 篇太泛的檔,要確認它在 `about_code` 裡有家。
- 計劃做 8 把逃生門與 `CLAUDECODE` 副作用寫進這一篇,對齊「每支檔有家」的規定。
- `scripts/hooks/pre-push` 與 `scripts/scenario_probe.py` 的家要另行確認,計劃的 lands_in 只列了一篇。若 pre-push 的家是別篇,「改到的每支檔都得先有家」的規則會要求寫進那一篇。⚠ 我沒有查 pre-push 的家節點是哪一篇。

不對齊共 5 條
