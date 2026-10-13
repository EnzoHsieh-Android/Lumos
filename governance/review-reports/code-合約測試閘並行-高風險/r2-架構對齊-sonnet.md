severity: minor

我對照了 `scripts/lumos` 周邊的既有寫法,有一個結構上的小不一致;`_kill_run` 的接法、`secs_kind` 的記帳寫法都對得上。

## 1. 設定看不懂時的出聲方式與去重寫法,跟同類設定讀取函式不同
severity: minor
blocking: 否
引句:「有寫但不合法時講一句用了 1(跟 note_lint、note_shape 看不懂時出聲同一個慣例)」
file: `scripts/lumos:26996`(`_stack_questions_config`)、`scripts/lumos:29067`(`_nodehome_config`)、`scripts/lumos:30562`(`_note_shape_config`)、`scripts/lumos:5842`(`load_platforms`)、`scripts/lumos:19525`(`_VAULT_LOCK_WARNED`)

1. 引句宣稱的慣例對不上。`_stack_questions_config`、`_nodehome_config`、`_note_shape_config` 是把警告收進 `warnings` 回傳,由呼叫端決定印不印。新函式 `_bound_tests_parallel` 卻在函式裡直接 `print(..., file=sys.stderr)`。
2. 直接 print 在專案裡有先例,就是 `load_platforms:5842`,所以結構上說得過去。但這個 docstring 把慣例講錯了,容易誤導後人。
3. 設定檔讀不了或 JSON 壞掉時,新函式靜默回 1。同類函式(`_nodehome_config:5842` 附近、`_stack_questions_config`)讀不了都會留一句警告。這裡不吭聲,是跟同類不一致的地方。
   - 補充:同一次呼叫中 `_run_bound_tests` 先跑 `load_platforms`,它會替壞設定檔出聲,所以實際使用者看得到提醒。這個落差在行為上被遮住,只是寫法不一致,所以維持 minor。
4. 去重用 `set` 加獨立的 `_bt_parallel_warn` 小函式。專案既有的「只提醒一次」寫法是模組層字典加 `.get` 判斷(`_VAULT_LOCK_WARNED`,19525、19600),或函式內旗標(`mt_warned`,17367)。屬於同一類做法的小變體,不算第二種機制。
5. 歸因:未判定。這是新增的函式,沒有修前版本可比。

## 三問

**1. 分層與依賴方向**
- 並行排程放在 `_run_bound_tests` 裡,每支仍呼叫既有的 `_kill_run`(`scripts/lumos:17175`)。
- `_bound_tests_check` 與 `_spec_gate_judge_items`(`scripts/lumos:7661`)兩個呼叫端都不用改。
- 設定讀取走 `Path(repo_root)/.lumos/config.json` 直讀,跟 `_stack_questions_config`、`_config_has_top_run_cmd` 同層同做法,沒有跨層直呼。
- `_bound_tests_parallel` 的位置在 `_run_bound_tests` 之後、`_config_has_top_run_cmd` 之前,就在同一組函式旁邊,對齊。

**2. 命名與錯誤處理**
- `_BT_PARALLEL_WARNED` 大寫加 `_WARNED` 尾碼,跟 `_VAULT_LOCK_WARNED` 一致。
- 鍵名 `parallel` 沒有踩到「鍵叫 gate 會被治理閘名漂移掃描抓」的雷。
- `secs_kind` 沒有進 `_GOV_FIELD_TYPES`(`scripts/lumos:8627`),這點跟 `calc_secs` 一致。該表註解說「mapper 用到的欄位才補」,而 `secs_kind` 沒有 mapper 讀它,所以不用補。
- 時鐘混用:同一個 `_bound_tests_check` 裡,`_calc` 仍用 `time.time()`(`scripts/lumos:48381`),新的牆上時間用 `monotonic`(48421)。`_kill_run` 內部的 `elapsed` 也是 `time.time()`(17175 以下)。
  - 專案裡量期限與預算的地方本來就偏好 `monotonic`(148、174、16555、23805 等),新寫法站在主流這邊。
  - 同函式兩種時鐘是被刻意區隔的(程式碼註解有寫理由),我不列為不對齊。

**3. 第二種做法(Grep 實查)**
- `scripts/lumos` 裡沒有任何既有的 threading、`queue`、`ThreadPoolExecutor`、`concurrent.futures` 或 `multiprocessing` 實作,命中的都是審查規則的正規表示式字串。所以「手刻 daemon 執行緒加 queue」沒有同族的第二種做法可比對。
- 專案裡唯一的並行先例是測試 runner 的 `--shard`(`scripts/test_lumos.py:18891` 一帶),那是外層多程序切片。本 diff 的 PRIOR-ART 也承認是「照搬外層多工作者」,但實作選了執行緒而不是子程序切片。
  - ⚠ 這算不算「第二種並行做法」,我判不準。因為專案內沒有第二個執行緒版本,所以不標 major。
  - 日後若有別處也要並行,應該收斂到這個 worker 寫法。
- 計時、`_kill_run` 的接法、記帳多帶欄位的寫法,都沒有出現新的平行機制。

不對齊共 1 條,其中 major 0 條
