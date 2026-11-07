severity: major

## F1 擋的位置接在切片分流之後,預設全套根本擋不到
severity: major
blocking: 是(spec 設定的主要情境會直接失效)
- spec 段落:範圍 2,「參數解析完、`_isolate_environment()` 之前呼叫」。S1、S3 和預期值表第一列「CLAUDECODE=1,無參數 → 擋」。
- 問題:這份 spec 想擋的是沒帶任何條件的全套。程式現況裡,參數解析完之後先走切片分流,才輪到 `_isolate_environment()`。切片片數預設 4,不帶條件的呼叫在 `_fanout_wanted` 就回真,直接 `return _fanout_main(_args)`。`_isolate_environment()` 只有單一程序的路徑才會走到。
- 照字面把判斷插在 `_isolate_environment()` 前面,會落在 `_fanout_main` 那個 return 之後。不帶條件的呼叫早就進了切片,判斷不會執行。只有 `--serial`、`-x` 或 `LUMOS_TEST_SHARDS=1` 才擋得到。
- 後果:S3(真子程序、不帶條件、5 秒內回 2)會紅,使用者要擋的主要情境沒擋到。
- 切片母程序也會先建 `gctl-run-fanout-` 暫存目錄,再開出 4 個各載入整個測試檔的子程序,記憶體成本和被擋的目的相反。spec 沒講「擋要早於 `_fanout_wanted`」。
- 修法:判斷要放在 `_fanout_wanted` 之前,而且這個順序要有測試釘住。
- 佐證:file: `scripts/test_lumos.py:49678-49680`,`if _fanout_wanted(_args): return _fanout_main(_args)` 緊接著 `_run_root = _isolate_environment()`。

## F2 S3 的子程序測試沒寫清楚環境怎麼清,推送閘裡會被汙染
severity: major
blocking: 是(正確性條款的測試在它自己要服務的閘裡會紅)
- spec 段落:S3、S4(`t_runner_chat_full_suite_block_process`)。
- 問題:這支測試要起真的執行器子程序,在推送前閘和切片子程序裡跑。推送前閘跑測試時,環境已帶 `LUMOS_PUSH_ATTEMPT`;切片子程序則帶 `LUMOS_FANOUT_CHILD`。子程序若繼承其中任何一個,S3 預期的 rc 2 會變成實跑全套。
- spec 沒要求測試自己從子程序環境剝掉 `LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`、`LUMOS_ALLOW_FULL_SUITE`。現有的 `_fan_run` 就是這樣剝的,證明這個坑已經踩過。
- 缺口一:一旦沒剝,在推送閘裡 S3 要嘛紅,要嘛真的在測試裡起出全套。
- 缺口二:「沒有建任何 `gctl-run-` 暫存目錄」要是去數共用的系統暫存,會被同時跑的別的會談或別片的 `gctl-run-*` 騙到。測試要給子程序專屬的 `TMPDIR`。
- 缺口三:「5 秒內」要靠實測。本機只跑 `--help` 就要 1.35 秒,載入的是 5MB 以上的測試檔。四片同時載入的推送閘裡,5 秒是時間型易碎斷言。
- 佐證:file: `scripts/test_lumos.py:30985`(`_fan_run` 剝 `LUMOS_TEST_SHARDS`、`LUMOS_FANOUT_CHILD` 的做法)。

## F3 RETIRE-IF、REVISIT 的度量沒有資料來源,而且和「不寫治理帳」矛盾
severity: minor
blocking: 否(不影響守衛行為,影響撤除條件能不能機械判)
- spec 段落:RETIRE-IF 與 REVISIT:2026-12-08,對照「不做」第三條與範圍 3。
- 問題:RETIRE-IF 寫「連續八週治理帳與終端都沒有任何一次被擋下」,又寫「逃生門被用次數超過被擋次數 → 撤」。但 spec 明講「不寫治理帳」,逃生門「只印一行、不留帳」。
- 被擋次數和逃生門次數只剩對話終端的輸出,事後沒有機器可讀的來源。兩個撤除條件、一個回頭條件都量不到。
- 做法需要補一個計數來源,或把條件改成人工看終端回報。
- 引句:「連續八週治理帳與終端都沒有任何一次被擋下、而且記憶裡「對話裡跑全套」的事故也沒再發生」

## F4 擋下訊息把繞過指令直接印給 AI,且判斷邊界漏列 `--serial`、`-x`、`--ff`、`--seed`
severity: minor
blocking: 否(spec 的「天花板」第 2 條已承認逃生門可被 AI 自己設)
- spec 段落:範圍 2 訊息的「怎麼辦」、範圍 1、S1。
- 問題一:使用者原話是「你可以不斷繞過這個規則」。訊息第三行直接印出 `LUMOS_ALLOW_FULL_SUITE=1`,等於把繞法交給被擋的那方。
- 問題二:實務隱患寫「訊息裡印逃生門」,是為了人手跑;而 AI 看到就會設。spec 卻拿它當依據,沒有量這個風險。
- 建議把逃生門改成需要人才給得出的東西,或訊息只印子集用法、逃生門寫進文件;至少 spec 要明講取捨。
- 問題三:S1 只列了不帶條件和 `--shard`。依現行程式,`--serial`、`-x`、`--ff`、`--seed N` 也都是不帶關鍵字的全套,同樣被這道判斷擋下。預期值表沒有這幾列,判斷函式的簽名(`args`)也沒說這幾個旗標算不算「有條件」。
- 佐證:file: `scripts/test_lumos.py:49391-49399`,`_fanout_wanted` 的條件含 `args.serial`、`args.exitfirst`。

## F5 清掉 `CLAUDECODE` 的範圍與副作用沒盤點
severity: minor
blocking: 否
- spec 段落:範圍 4。
- 問題:`os.environ.pop("CLAUDECODE")` 放在 main 內,對 `-k` 的子集也生效。這之後起的所有子程序都看不到 `CLAUDECODE`,包括測試裡呼叫 `scenario_probe` 或別的工具、讀 `CLAUDECODE` 的路徑。
- 我查到 `test_lumos.py` 和 `scripts/lumos` 目前都不讀 `CLAUDECODE`。只有 `scenario_probe.py` 在開子程序前自己拿掉它,所以現況無衝突。
- spec 把「沒有測試讀它」當前提,卻沒寫成守衛:之後有人加讀 `CLAUDECODE` 的測試,會拿不到值。
- 這個副作用需要在 `Systems/測試執行器` 註明。
- 佐證:file: `scripts/scenario_probe.py:1162`。

## 其他段落
- 前言、決策 d1、「跟舊決定的關係」、「依據來源」:已讀,無 finding。交叉引用 `[[Systems/測試執行器]]` 與 `[[Projects/測試總檔預設切片_計劃]]` 在本 repo 的 docs 底下都存在。
- 引用的 `LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD` 都存在。前者在 `scripts/hooks/pre-push:393` export,早於跑測試的 981、985 行。後者在 `scripts/test_lumos.py:49388`、`49552`。
- `LUMOS_ALLOW_FULL_SUITE`、`_chat_full_suite_block` 是 spec 要新增的,尚未存在,屬正常。
- 對 `CLAUDECODE=1` 的說法:本機實測環境確實為 1。
- 「CI 沒有 `CLAUDECODE`」:我只看了 CI 的 workflow,它沒用 Claude Code 動作,但這屬部署事實。程式碼答不了,⚠ 無法證實 runner 環境不會被注入。

## 實務隱患鏡頭
- 守衛面(新擋停):有隱患,見 F1(位置)、F4(繞法外露)。
- 平行路徑:`.lumos/config.json` 的 `run_cmd` 是 `{python} scripts/test_lumos.py -k {method}`,帶關鍵字,所以 bound-tests、fix-check、guard kill 在對話裡不會被擋。
- 推送前閘一律帶 `--shard` 且已有 `LUMOS_PUSH_ATTEMPT`,不受影響。
- 消費專案:測試檔會被複製進去,那邊沒有推送閘標記。在 Claude Code 對話裡,消費專案的 `test_lumos.py` 全套也會被擋;spec 沒提範圍。⚠ 判不準是否有意。
- 金流、對外送出、不可逆:無,理由同 spec,只改入口判斷。
- 併發、記憶體:F1 的後果之一是被擋之前就已經建了暫存並開出 4 個程序。

## 固定席逐條判
- `lumos-cli-read` 的 INVARIANT(search 預設排除 superseded):不影響,這份設計不碰 search。
- `lumos-cli-lifecycle` 的 INVARIANT(re-inject 保留 sentinel 之外內容):不影響,不碰 re-inject。
- `design-loop` 的 INVARIANT(處置閘第五步,審材必須是 .md 計劃):不影響,只改執行器入口。
- `測試假綠形態` 的 INVARIANT(還原翻紅釘必須配前置斷言):間接相關。F2 指出 S3 缺少證明現場成立的前置條件。補上前置後就符合,不補就違反。
- `bound-tests-gate` 的 INVARIANT(合約綁定測試逐支真跑,任一紅或證不出跑過就擋):不影響。run_cmd 帶 `-k`,不會被擋。但如果某個平台的 run_cmd 缺關鍵字,在對話裡會變成 rc 2 並被判紅。
- `canary-audit` 與 `guard-kill` 的 INVARIANT:不影響,它們只讀執行器的 rc 與輸出。

總結:最高等級為 major,blocking 共 2 條。
