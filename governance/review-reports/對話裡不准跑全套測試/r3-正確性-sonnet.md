severity: blocker

我讀完了 spec 全文,並對照 `scripts/test_lumos.py` 的 `main()`、`_fanout_wanted`、`_isolate_environment`、`_shard_by_duration`、`_load_durations_table`,以及 `scripts/hooks/pre-push`。只跑了 `--list` 取名單,算佔比的腳本在 `/tmp/lumos-seat-work/對話裡不准跑全套測試/正確性-sonnet/` 下,沒有跑任何測試本體。

## F1 `CLAUDECODE` 的「拿掉」時機自相矛盾,字面照做會讓擋下永遠不觸發,或讓對話裡的全套仍被切片
severity: blocker
blocking: 是(照 spec 字面實作會讓整個擋的機制失效,屬 blocker)
spec 段落:範圍/做 1,以及做 2、做 3 的 `_chat_full_suite_block(selected, all_tests, args, env)`。
問題:做 1 同時寫了兩個互斥的順序。
- 「判斷完才把 `CLAUDECODE` 從 `os.environ` 拿掉」。
- 「這一步在參數解析之後、`_fanout_wanted` 之前」。

照後一句做,`_fanout_wanted` 讀不到 `CLAUDECODE`,對話裡不帶條件的全套仍會預設切成 4 片。子程序沒有 `CLAUDECODE`,整個全套就繞過擋下。這正是 r2 的兩個 blocker。

照前一句做,`_fanout_wanted` 這一步是對的,但做 2 的擋下判斷在 `--list` 之後才跑,中間隔著整段分片與篩選。這時 `os.environ` 早就沒有 `CLAUDECODE`。spec 沒規定 `env` 參數是「拿掉之前的快照」,也沒規定快照要在哪裡取。如果實作者傳 `os.environ`,擋下永遠回 None,對話裡全套照跑。

佐證:
- `main()` 裡 `_fanout_wanted(_args)` 在 `_isolate_environment()` 之前呼叫,擋下判斷必須在其後。
- file: `scripts/test_lumos.py:49678` 是 `_fanout_wanted` 呼叫處,`:49680` 是 `_isolate_environment()`。
- S4 的前置斷言只驗「拿掉 `CLAUDECODE` 時回 None」。它抓不到「`os.environ` 被提前清掉」這種漏洞,因為子程序測試是從頭組環境。
- 修法要明寫:在 `main()` 取一次 `_chat = os.environ.get("CLAUDECODE") == "1"` 的快照,同時快照 `LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`、`LUMOS_ALLOW_FULL_SUITE`,之後 `_fanout_wanted` 與擋下判斷都吃快照,最後才 pop。
- S3 也要補一條「CLAUDECODE 被 pop 之後,擋下判斷仍擋」的紅燈釘。

引句:「這一步在參數解析之後、`_fanout_wanted` 之前,不跟清 `GIT_*` 同段」

## F2 計數檔寫在 `_isolate_environment()` 之後,`HOME` 已是拋棄式的,記錄既寫不到真家目錄、也會被收尾刪掉
severity: major
blocking: 是(RETIRE-IF 與 REVISIT 的唯一資料來源失效,且 S4 的斷言無法成立)
spec 段落:做 3(擋下在 `_isolate_environment()` 之後才判得了)、做 7(計數檔)、S4。
問題:`_isolate_environment()` 會把 `os.environ["HOME"]` 與 `USERPROFILE` 換成 `root/home`。`_mkdir_trusted_under_home` 與 `_home_cache_write` 用的都是當下的家目錄。在這之後寫 `~/.cache/lumos/full-suite-guard/events.jsonl`,寫的是拋棄式家目錄。擋下回 2 時 `finally` 會 `rmtree(_run_root)`,這份計數檔連同整個家目錄一起被刪,RETIRE-IF 的「八週內擋下與放行次數」永遠是 0。

S4 要求「私有 HOME 的計數檔多一行擋下」,但子程序跑了 `_isolate_environment()` 之後,私有 `HOME` 已被取代。這條條款字面做不出來,或者實作者會把檔寫進 root 內來湊過測試。

另一個不符:做 7 說「寫法照 `scripts/lumos` 既有的家目錄快取寫入」,而 `_home_cache_write` 是整檔 mkstemp 後 `os.replace`,不是追加。拿它寫 `events.jsonl` 每次都覆蓋整份,「追加一行」的計數意圖做不到,得另寫追加版,又違背「不手抄第三份」。

佐證:
- file: `scripts/test_lumos.py:49314-49320`,`os.environ["HOME"] = str(home)`。
- file: `scripts/lumos:69244-69265`,`_home_cache_write` 是 `os.replace` 整檔寫,且依賴 `_mkdir_trusted_under_home`。
- 修法:在 `_isolate_environment()` 之前快照真家目錄路徑並傳給計數寫入,或把擋下與計數拆成兩段。並改寫 S4 的斷言對象。

引句:「寫法照 `scripts/lumos` 既有的家目錄快取寫入那一套(子目錄、驗目錄可信、只攔 OSError,單次寫入一行)」

## F3 推送前閘紅燈提示改 `-k <紅的那支>`,但掛鉤手上沒有可直接用的紅測試名
severity: major
blocking: 是(S5 的前提不成立,依字面做出的提示會教出錯的指令)
spec 段落:範圍/做 5、S5。
問題:掛鉤彙總紅燈只做 `grep -h "✗ " "$_TESTS_LOG" | head -20`。`✗ ` 行有四種:
- `✗ <斷言說明>  <detail>`,這是 `check()` 印的,不是測試名。
- `✗ FAILED t_xxx(N 條斷言)`。
- `✗ TIMEOUT t_xxx:` 與 `✗ t_xxx EXCEPTION:`。
- 沒有測試名的紅,例如「✗ 判紅:…跳過基準線」。

此外:
- 一支紅測試通常先印多行斷言行,`head -20` 可能只列出幾支,其餘被截掉。
- 有些非零離開碼完全沒有 `✗ ` 行,例如耗時表換了 rc2、每片選中 0 支 rc3 被當紅、暫存目錄問題。這時提示裡的 `<紅的那支>` 是空的。
- 掛鉤是薄殼 bash,沒有「紅的測試名」這個變數可帶。實作者得新增從 log 解析 `FAILED t_…` 與 `EXCEPTION`、`TIMEOUT` 的邏輯。

spec 把它當「已有」,是沿用既有的假設。

佐證:
- file: `scripts/hooks/pre-push:1024`,`grep -h "✗ " "$_TESTS_LOG" | head -20`。
- file: `scripts/hooks/pre-push:1031-1035` 是兩處 `--ff -x`。
- file: `scripts/test_lumos.py:171-178`,`check` 失敗印 `✗ {name}  {detail}`。

引句:「紅的名字掛鉤上面已印出」

## F4 spec 漏列兩處仍教人跑 `--ff -x` 的地方,其中一處是既有測試的斷言
severity: minor
blocking: 否(只會讓使用者撞到擋下訊息、或讓既有測試翻紅,不會讓擋下失效)
spec 段落:做 5、驗收條款 S5。
問題:
- 執行器自己在 `-x` 停下時印「修完用 --ff -x 重跑,它會先跑這幾支」。`--ff` 只重排、不篩選,所以在對話裡 `--ff -x` 不帶 `-k` 就是 100% 全套,會被擋。這一處 spec 沒改。
- 既有測試 `t_prepush_blocked_last_line_is_next_step` 斷言最後一行含 `scripts/test_lumos.py --ff -x`。做 5 會讓它翻紅。spec 沒列「要改這支既有測試」。改它屬於改測試檔,要先簽名。

佐證:
- file: `scripts/test_lumos.py:49844`。
- file: `scripts/test_lumos.py:85831`。

引句:「原提示 `--ff -x` 在對話裡會被擋」

## F5 估佔比函式的輸入沒講清楚:權重函式沒有對外介面,耗時表讀不到的兩條路徑行為不一致
severity: minor
blocking: 否(實作者可自行補,不會讓擋下失效)
spec 段落:做 2、S2。
問題:
- 做 2 說「重用 `_shard_by_duration` 的權重」,但該函式回傳分桶、不是權重,權重 `w` 是函式內區域變數。要重用就得抽出函式,否則會手抄一份而產生漂移。
- 「耗時表讀不到時改用支數比例」有兩條路徑。帶 `--shard` 時,`main()` 在分片段遇到 `ValueError` 就已經回 2,不會走到擋下判斷。不帶 `--shard` 時,擋下判斷得自己呼叫 `_load_durations_table()` 並接 `ValueError`,spec 沒寫要接。S2 只測函式層,抓不到擋下判斷不接例外而直接崩潰。
- 佔比實測(以 `governance/test-durations.json` 與 `--list`):共 3469 支,其中 1442 支(約 42%)不在表裡,用中位數 1.879 秒補。`--shard 1/4` 與 `1/16` 的佔比確為 25.00% 與 6.25%,`_shard_by_duration` 是用同一份權重貪婪分配,不會偏。`--shard 1/5` 剛好落在 20% 邊界,「超過 0.2」是否擋下取決於浮點誤差,表裡預期值沒列這個邊界。
- 分子、分母:`tests` 在分片前就是全部 `t_`,擋下判斷放在 `-k` 之後,分子是分片加 `-k` 之後的清單,分母是全部。這與 spec 一致,沒問題。

佐證:
- file: `scripts/test_lumos.py:48987-49002`,`_shard_by_duration` 只回 buckets。
- file: `scripts/test_lumos.py:49711-49718`,分片段遇到表讀不懂回 2。

引句:「耗時表讀不到時改用支數比例」

## 逐項查證結果(沒有問題或不成 finding)
- 擋下時暫存根目錄會被清掉:擋下判斷放在 `--list` 之後,在 `try:` 內,既有 `finally` 會收尾。`FAIL` 為 0 且未帶 `--keep-tmp`,所以 `rmtree`。但 F2 的計數檔也在這棵樹裡,會一併被刪。
- 對話裡不切片後,推送前閘與 CI 的切片行為不會被誤改。掛鉤對每片明寫 `--shard i/N`,`LUMOS_TEST_SHARDS` 為 1 時不切。`_fanout_wanted` 新增的條件只在 `CLAUDECODE=1` 且沒有 `LUMOS_PUSH_ATTEMPT` 時才生效。
  - S3 的「推送前閘裡照舊切片」其實只在直接呼叫 `_fanout_wanted` 時才成立。掛鉤本身從不走這條路,所以這條條款抓不到掛鉤的退化。
- `-x`:`_fanout_wanted` 本來就在帶 `-x` 時回 False,新擋下判斷在 `-x` 之後。`--ff` 與 `--seed` 只改順序、不改集合,佔比不受影響。
- 對話裡逃生門放行後的全套變成單一程序約 8 分鐘,超過工具上限。spec 的 d1 已承認全套本就不該在對話裡跑,這屬預期。
- 空字串 `-k ""` 在 `main()` 中是 falsy,等於全套,佔 100%,會被擋。

## 固定席(圖譜節點宣稱的行為與合約)逐條判
- `lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間 body):不影響。這份設計只動 `scripts/test_lumos.py` 的 `main()` 入口與 `scripts/hooks/pre-push` 兩行提示,不碰 sentinel 與 re-inject。
- `canary-audit`、`guard-kill`、`design-loop`、`測試假綠形態`:不影響。它們的合約對象是 canary record、guard kill 的 rc 與 JSON、處置閘、還原翻紅釘,跟測試執行器的擋下路徑沒有交集。
- `bound-tests-gate`(逐支真跑合約綁的測試,紅或 unfilterable 就 blocked):大致不影響。⚠ 一個邊界:該閘用 `{method}` 做 `-k`,方法名是子字串比對。方法名太短(例如 `t_s`)時,選中超過兩成,在對話裡會被新擋下判斷擋成 rc2。閘會判成 blocked=True,而不是執行失敗。現有綁定的方法名夠長,實際風險低,但 spec 沒提這個互動。
- `lumos-cli-read`:不影響。

總結:最高等級為 blocker,blocking 共 3 條
