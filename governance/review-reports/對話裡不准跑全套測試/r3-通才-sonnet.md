severity: blocker

## F1 做 1 的「讀當下環境」與「先拿掉 CLAUDECODE」順序互相打架
severity: major
blocking: 是(照字面實作會讓整個功能失效,屬 blocking 級)
- 段落:做 1,連到做 3 的 S3 條款。
- 問題:做 1 一句話說「判斷讀的是當下環境變數」,下一句又說拿掉 `CLAUDECODE` 的位置在「參數解析之後、`_fanout_wanted` 之前」。照這個順序,`_fanout_wanted` 呼叫時 `os.environ` 已經沒有 `CLAUDECODE`,在對話裡不帶條件會回 True,於是 `_fanout_main` 開子程序。子程序環境也沒有 `CLAUDECODE`,全套就照常切片跑完,沒有任何一處擋住。
- 做 2 的 `_chat_full_suite_block(..., env)` 有一個 `env` 參數,但 spec 沒寫它是拿掉之前的快照。`_fanout_wanted(args)` 現行簽名只有 args,spec 也沒說要補快照參數。
- S3 直接呼叫 `_fanout_wanted`,測試會綠,看不出這個洞。只有 S4 的真子程序案例會逮到,而 S4 只驗不帶條件這一種。
- 佐證:`scripts/test_lumos.py` 的 `main()` 現況是參數解析之後直接 `if _fanout_wanted(_args): return _fanout_main(_args)`。`_fanout_wanted` 現行實作讀 `os.environ.get(_FANOUT_CHILD_ENV)`,沒有收快照的參數。
引句:「判斷讀的是當下環境變數;判斷完才把 `CLAUDECODE` 從 `os.environ` 拿掉」

## F2 計數檔會寫進被 `_isolate_environment()` 換掉的拋棄式 HOME,真家目錄永遠沒有計數
severity: blocker
blocking: 是(S4 在 spec 寫的設計下過不了,RETIRE-IF 和 REVISIT 依賴的資料也不會出現)
- 段落:做 3(擋下在 `_isolate_environment()` 之後才判)、做 7(計數)、S4、RETIRE-IF、REVISIT。
- 問題:做 3 自己承認擋下發生在 `_isolate_environment()` 之後。`_isolate_environment()` 會把 `os.environ["HOME"]` 和 `USERPROFILE` 換成 `<gctl-run-根>/home`。
- 計數寫入的 `Path.home()` 讀的就是這個 HOME。所以擋下和逃生門的計數行會落在拋棄式根目錄,收尾時整個被 `rmtree`。
- 結果有三個:
  - S4 說私有 HOME 的計數檔會多一行,但執行器內部看到的 HOME 已不是測試傳進去的那個,這條過不了。
  - 真正的 `~/.cache/lumos/...` 永遠沒有資料。
  - REVISIT 2026-12-08 和 RETIRE-IF 的「八週內放行次數超過擋下次數」永遠是零對零,守衛等於沒有退場判準。
- spec 沒寫「在 `_isolate_environment()` 之前記下真 HOME」。修法有兩種:判斷放在隔離之前(但選測試需要先載入清單),或隔離之前先存真 HOME。
- 佐證:`scripts/test_lumos.py` 的 `_isolate_environment`,內有 `os.environ["HOME"] = str(home)` 與 `os.environ["USERPROFILE"] = str(home)`。`scripts/lumos` 的 `_mkdir_trusted_under_home` 以 `cur = Path.home()` 起算。
引句:「私有 `HOME` 的計數檔 應 多一行擋下」

## F3 計數的「照既有寫法」是整檔覆蓋,不是追加一行;檔名也前後不一致
severity: major
blocking: 是(照做會丟掉先前的計數行,RETIRE-IF 的判準讀不到真值)
- 段落:做 7,以及 RETIRE-IF。
- 問題一:做 7 要「追加一行到 events.jsonl」,又說寫法照 `scripts/lumos` 既有的家目錄快取寫入。既有的 `_home_cache_write(subdir, path, data)` 是 mkstemp 之後 `os.replace`,而且寫的是單一 JSON 物件。它是整檔取代,不是追加,所以每次寫都會洗掉前面的行。
- 問題二:RETIRE-IF 指的檔是 `~/.cache/lumos/full-suite-guard.jsonl`,做 7 和 REVISIT 指的是 `~/.cache/lumos/full-suite-guard/events.jsonl`。兩個路徑不同,是第 3 版補丁與原文銜接處的新不一致。
- 另外,追加寫要自寫一套,但 spec 的「只攔 OSError、驗目錄可信」前提和「單次寫入一行」之間沒說怎麼在多片並行(推送閘跑多片)時避免互蓋。
- 佐證:`scripts/lumos` 的 `_home_cache_write` 內有 `os.replace(tmp, path)` 與 `_json.dumps(data, ...)`。
引句:「寫法照 `scripts/lumos` 既有的家目錄快取寫入那一套(子目錄、驗目錄可信、只攔 OSError,單次寫入一行)」

## F4 做 3 一句話內自相矛盾:擋下在隔離之前還是之後
severity: minor
blocking: 否(實作時看 ⚠ 那句即可判斷意圖,但文字需修)
- 段落:做 3。
- 問題:同一段先說「在 `_isolate_environment()` 之前不開任何子程序」,緊接著 ⚠ 說這條「在 `_isolate_environment()` 之後才判得了」。「不開子程序」本身在兩種順序下都成立,所以這句等於沒約束。
- 這一段實際該回答的是 F2 的真 HOME 問題,但文字沒碰。
- 佐證:同一檔 `main()`,`--list` 分支之後、迴圈之前已經是 `try:` 之內,`finally` 會清 `_run_root`。`--keep-tmp` 時那個 `finally` 會留下現場,spec 的「擋下要清暫存根」沒處理 `--keep-tmp`(只是邊角)。
引句:「⚠ 因為選測試要先載入測試清單,這一條在 `_isolate_environment()` 之後才判得了」

## F5 逃生門放行後反而被強制單程序,在對話裡跑 8 分鐘
severity: minor
blocking: 否(逃生門路徑本來就少用,但與設計目的相反)
- 段落:做 1、做 6。
- 問題:做 1 的 `_fanout_wanted` 條件只看「在對話裡且不是推送閘」,沒有排除逃生門有合格理由的情況。帶了合格理由放行的全套會變成單程序約 8 分鐘,而不是切片約 4 分鐘,對話工具更容易超時。
- spec 的天花板節也沒寫這一點。
- 佐證:`scripts/test_lumos.py` 的 `_fanout_wanted` 現況,切片是全套預設行為;做 1 加的條件會讓放行後同樣不切。
引句:「在對話裡(`CLAUDECODE` 是 `1`)而且不是推送前閘(沒有 `LUMOS_PUSH_ATTEMPT`)時回 False」

## F6 推送前閘提示只改了掛鉤兩處,執行器自己印的 `--ff -x` 與非測試紅燈沒處理
severity: minor
blocking: 否(不改也不會放行,只是提示會誤導)
- 段落:做 5、S5。
- 問題一:執行器的 `-x` 分支自己印「修完用 --ff -x 重跑」。在對話裡 `--ff -x` 不帶 `-k` 選中全套會被擋,提示反而教錯。做 5 只改掛鉤。
- 問題二:掛鉤印紅的名字靠 `grep -h "✗ "`。但紅燈也可能是沒有測試名的情況,例如耗時表在跑期間被換掉的 rc2,或跳過基準線判紅。這時「用 `-k <紅的那支>` 逐支重跑」沒有名字可代。
- 佐證:`scripts/test_lumos.py` 的 `-x` 分支有 `修完用 --ff -x 重跑,它會先跑這幾支`。`scripts/hooks/pre-push` 約第 1032、1035 行各印一次 `--ff -x`。
引句:「`scripts/hooks/pre-push` 兩處「下一步」從 `--ff -x` 改成「用 `-k <紅的那支測試名>` 逐支重跑」」

## F7 兩成線對 `--shard i/5` 恰好落在邊界,結果不穩定;耗時表只涵蓋約六成測試
severity: minor
blocking: 否(spec 已承認估計不準只移動那條線,但這裡有一個剛好貼線的合法輸入)
- 段落:做 2、預期值表。
- 問題一:實測本 repo 耗時表,`--shard i/5` 每片估計佔比都是 20.0%,門檻是「超過 0.2」,所以會因浮點尾數和估法細節而有的片擋、有的片不擋。預期值表只列了 1/4(25%)與 1/16(6%),沒列這個邊界。
- 問題二:耗時表有 2029 筆,現有測試約 3469 支,約 1442 支(約 41%)表裡沒有,要用中位數 1.879 秒補。表的平均約 5.25 秒,中位數遠低於平均,新測試被低估。spec 的「不齊」隱患節只說照中位數估。
- 佐證:
  - file: `governance/test-durations.json`,用 `scripts/test_lumos.py --list` 的名單對照算出缺 1442、過期 2。
  - 用 `_shard_by_duration` 同權重重算,分 4/5/6/16 片的佔比依序為 25.0/20.0/16.67/6.25。
引句:「估計耗時佔全部測試估計耗時超過 `_CHAT_SUITE_SHARE = 0.2` 就擋」

## 固定席判定:Systems 節點 INVARIANT
- canary-audit、design-loop、lumos-cli-lifecycle、測試假綠形態、bound-tests-gate、lumos-cli-read、guard-kill 的合約:不影響。這份設計只動 `test_lumos.py` 入口、`pre-push` 兩行提示與執行器的家目錄計數檔,不碰這些合約的標的(canary 落盤、re-inject 保留、搜尋濾網、guard kill 的 rc 優先序等)。
- bound-tests-gate 補充:code-loop check 與 guard kill 透過 `.lumos/config.json` 的 `run_cmd: "{python} scripts/test_lumos.py -k {method}"` 逐支跑,每次都帶 `-k <單支名>`。實測 `-k loop`、`-k gate` 等常用關鍵字佔比都在 20% 以內(最高 10.7% 以下),不會被新擋住,所以不影響。
- 測試假綠形態:S4 要求前置斷言證明擋是 `CLAUDECODE` 造成的,方向符合該合約。⚠ F2 解決前 S4 本身過不了,這點屬 F2,不是違反合約。

## 實務隱患鏡頭
- 守衛面(新擋停):有風險,見 F1(順序寫反會讓守衛整個失效)與 F2、F3(計數資料收不到,撤除判準失效)。
- 金流:無,不碰付款。
- 對外送出:無,不連網、不呼叫外部服務。
- 不可逆:無,只改入口判斷、切片條件和兩行提示;計數檔在工作目錄外(前提是 F2 解決後真的寫得到)。
- 效能:`-k` 小子集也要載入 `scripts/lumos` 模組(約 1.3 秒,實測 `--list -k zzz_nonexist`),在每次 `-k` 呼叫都付一次,可接受。
- 併發:推送閘多片同時寫計數檔,見 F3。

總結:最高等級為 blocker,blocking 共 3 條
