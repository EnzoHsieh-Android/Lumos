severity: major

## F1 CLAUDECODE 的清除位置與判斷的先後矛盾
severity: major
blocking: 是(照字面做,判斷永遠看不到 CLAUDECODE,整道擋失效)
- spec 段落:範圍 4「跟清 `GIT_*` 同一段」,與範圍 2「參數解析完、`_isolate_environment()` 之前呼叫」。
- 問題:
  - 清 `GIT_*` 那段在 `main()` 最開頭,在 argparse 之前。
  - 照範圍 4 把 `CLAUDECODE` 放進同一段拿掉,等判斷在參數解析之後跑時,`env["CLAUDECODE"]` 已經不存在,永遠不擋。
  - 要成立,必須在最頂端先快照 `CLAUDECODE`(或延後清除),spec 沒寫。
  - 範圍 4 另寫「判斷完(不論擋不擋)」才清,與「同一段」互相矛盾。
- 佐證:file: `scripts/test_lumos.py:49596-49625` 的 `main()`,`GIT_*` 清除與 `PYTHON_COLORS` 設定都在 `argparse` 之前。

引句:「判斷完(不論擋不擋)把 `CLAUDECODE` 從 `os.environ` 拿掉,跟清 `GIT_*` 同一段」

## F2 判斷插入點若落在 `_fanout_wanted` 之後,預設切片母程序會繞過擋
severity: major
blocking: 是(對話裡無參數呼叫會真的切成四片跑滿全套)
- spec 段落:範圍 2。
- 問題:
  - 現況 `main()` 的順序是 `parse_args`、`if _fanout_wanted(_args): return _fanout_main(_args)`、`_isolate_environment()`。
  - 「參數解析完、`_isolate_environment()` 之前」同時涵蓋 `_fanout_wanted` 之前與之後兩個位置,spec 沒指定。
  - 放在 `_fanout_wanted` 之後時:對話裡無參數呼叫的母程序會先進 `_fanout_main`,並在子程序 env 設 `LUMOS_FANOUT_CHILD=1`。
  - 各片因此全部走豁免,擋下來的是零個。
  - 母程序與子程序的判斷必須明寫:擋只做在母程序(沒有 `LUMOS_FANOUT_CHILD`),且必須排在 `_fanout_wanted` 之前。
- 佐證:
  - file: `scripts/test_lumos.py:49587-49594` 的 `_fanout_wanted`。
  - file: `scripts/test_lumos.py:49706` 附近的 `if _fanout_wanted(_args): return _fanout_main(_args)`,在 `_isolate_environment()` 之前。
  - file: `scripts/test_lumos.py` 的 `_fanout_spawn` 設 `env = dict(os.environ, **{_FANOUT_CHILD_ENV: "1"})`。
  - S3 的「沒有建 `gctl-run-` 暫存目錄」只在順序放對時才綠(`_fanout_main` 會先 `mkdtemp("gctl-run-fanout-")`),但 spec 正文沒要求順序。

## F3 「沒帶 -k」對空字串的定義未寫,實作一偏就留下全套後門
severity: major
blocking: 是(spec 要擋的行為有一個等價輸入擋不到)
- spec 段落:範圍 1「沒帶 `-k` 或位置關鍵字」,預期值表。
- 問題:
  - 現況 `-k ""` 與位置參數 `""` 都得到 falsy 的關鍵字。
  - 篩選用 `if _args.keyword:`,`_fanout_wanted` 用 `not (args.keyword or ...)`,所以 `-k ""` 現在等同「無條件全套」,而且會切片。
  - 若實作寫 `args.keyword is None`,`python3.14 scripts/test_lumos.py -k ""` 在對話裡就不被擋、還會跑滿全套。
  - 預期值表沒有這列。spec 必須明寫「用真值判斷,跟 `_fanout_wanted` 同一口徑」,並補紅測試。
  - 注意 `-k " "` 不同:選中 0 支,回 1,不是全套。
- 佐證:
  - file: `scripts/test_lumos.py:49587-49594` 的 `_fanout_wanted`。
  - file: `scripts/test_lumos.py` 的 `if _args.keyword:`(關鍵字篩選)與 `if _args.keyword_pos:`。

## F4 推送前閘失敗時印的補救指令,在對話裡會被新擋擋下
severity: major
blocking: 是(與 spec 要保護的主要流程互相衝突)
- spec 段落:範圍 1(未豁免 `--ff -x`)。
- 問題:
  - `scripts/hooks/pre-push` 測試紅時印出兩次 `$PY scripts/test_lumos.py --ff -x` 當「下一步」。
  - 從對話裡推送的人(AI)照做,會是 `CLAUDECODE=1`、無 `LUMOS_PUSH_ATTEMPT`、無關鍵字、無 `--suite`。依 spec 一律回 2。
  - 實際行為:`--ff -x` 先跑上次紅過的,全綠時會續跑完整串行全套約 8 分鐘,所以擋是對的。
  - 但 spec 沒處理這個衝突:要嘛改 hook 的提示,要嘛讓 `--ff -x` 在有紅紀錄時改成只跑紅的。
  - 現況是推送被擋後給的唯一指令,被另一道擋反擋。
- 佐證:
  - file: `scripts/hooks/pre-push:1032` 與 `scripts/hooks/pre-push:1035`。
  - file: `scripts/test_lumos.py` 的 `--ff` 實作只重排、不篩(`tests = [紅的] + [其餘]`)。

## F5 S3 的「沒建 gctl-run- 暫存目錄」與子程序環境清理沒寫,會假紅甚至遞迴
severity: major
blocking: 是(新測試在推送前閘與分片平行下不穩;環境沒清乾淨時會遞迴開全套)
- spec 段落:驗收條款 S3、S4。
- 問題:
  - S3 要驗「沒有建任何 `gctl-run-` 暫存目錄」,但 `gctl-run-*` 建在共用的 `tempfile` 根目錄。
  - 推送前閘四片平行跑,別片與別的會談的執行器都會在同一個暫存根建這種目錄,斷言在 TMPDIR 全域列目錄會偶發紅。測試必須對子程序設私有 `TMPDIR`,spec 沒寫。
  - S3 的子程序環境必須明確清掉 `LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`、`LUMOS_ALLOW_FULL_SUITE`,並設 `CLAUDECODE=1`。
  - 這個測試跑在推送前閘裡時,外層 env 帶 `LUMOS_PUSH_ATTEMPT`;沒清掉時子程序不被擋,會 `_fanout_wanted` 起四片全套,片裡又有這支測試,形成遞迴(見記憶〈變異會炸程序〉的全套分裂先例)。
  - spec 只有「5 秒內」的超時當保險,沒有環境白名單與遞迴防護。
  - 現有 `_fan_run` 只剔除 `LUMOS_TEST_SHARDS` 與 `LUMOS_FANOUT_CHILD`,不剔除 `LUMOS_PUSH_ATTEMPT`,可見既有 helper 不能直接借用。
  - 另一個耗時因素:載入 `test_lumos.py` 約 1.3 秒,目前不構成 5 秒的風險,但四片平行加壓時餘裕不大,屬次要。
- 佐證:
  - file: `scripts/test_lumos.py:30778-30784` 的 `_fan_run`。
  - file: `scripts/hooks/pre-push:393` 的 `export LUMOS_PUSH_ATTEMPT`。
  - file: `scripts/test_lumos.py:49471` 的 `mkdtemp(prefix="gctl-run-fanout-")`。

## F6 逃生門「印放行一行」的觸發條件未定義
severity: minor
blocking: 否(語意模糊,不造成錯擋或漏擋)
- spec 段落:範圍 3、S2。
- 問題:範圍 3 沒說「只在本來會擋、因逃生門才放行」時才印,還是 `LUMOS_ALLOW_FULL_SUITE=1` 就印。
  - 若無條件印,帶 `-k foo` 時印「放行跑全套」是假話。
  - 若 `CLAUDECODE` 先被清,分片子程序已沒有 `CLAUDECODE`,不會重複印。
  - spec 該明寫只在「若沒有逃生門就會被擋」時印一次。
- 佐證:S2 預期值表只列「CLAUDECODE=1 + LUMOS_ALLOW_FULL_SUITE=1,印放行」,沒有「無 CLAUDECODE + ALLOW=1」和「`-k` + ALLOW=1」兩列。

## F7 範圍的判準用 `-k` 子字串,廣字串可繞過
severity: minor
blocking: 否(spec 的天花板已承認環境變數逃生門,但沒承認這條)
- spec 段落:決策 d1「不管指令怎麼寫都會經過」,天花板。
- 問題:
  - `-k t_` 或 `-k _` 幾乎選中全部測試,在對話裡不被擋,實際等於全套串行。
  - d1 的理由是比對指令字樣可被繞過,但本案的「有帶 -k 就放行」也可被一個字元繞過。
  - 天花板只寫了逃生門,沒寫這條;至少該登記或改為選中數超過門檻(例如三成,同 `--suite keys` 的口徑)也擋。
- 佐證:file: `scripts/test_lumos.py` 的 `_keys_suite_select` 對太泛關鍵字有三成門檻,關鍵字篩選沒有。

## F8 CLAUDECODE 從 os.environ 拿掉的影響面
severity: minor
blocking: 否(查證後既有行為不變,只缺一個守衛測試)
- spec 段落:範圍 4、不汙染子執行器。
- 問題:
  - `scripts/` 下只有 `scripts/scenario_probe.py:1162` 讀寫 `CLAUDECODE`(本來就 pop),`test_lumos.py` 與 `scripts/lumos` 都沒有讀它,所以拿掉不改變既有測試或子程序的行為。
  - 同一處也 pop `CLAUDE_CODE_ENTRYPOINT`,本案沒清,但不影響擋的判斷。
  - spec 把「沙盒子執行器會被誤擋」當理由,事實上現有沙盒測試的環境繼承自 `os.environ`,若不清確實會被誤擋;既有 `_fan_run` 又沒剔除 `CLAUDECODE`,所以必須先清再測。
  - 這條假設成立,但依賴 F1 的順序解法。
- 佐證:`grep` 全 repo 的 `scripts/`,只有 `scripts/scenario_probe.py:1162`。

## 各節判讀
- 白話、PRIOR-ART、RETIRE-IF、跟舊決定的關係:已讀,無 finding。`[[Projects/測試總檔預設切片_計劃]]` 與 `[[Systems/測試執行器]]` 都存在,d1 描述與該節點一致。
- 做:範圍 1、2、4 見 F1 至 F3。範圍 3 見 F6。範圍 5 已讀,無 finding。
- 不做:已讀,無 finding。
- 實務隱患:「Claude Code 改了變數名」寫成了回頭條件;已讀,無 finding。
- 預期值表缺列:`-k ""`、`--ff -x`、`--list --shard`、`--suite keys --keys x`。
  - 後三者不擋是正確的:`--list` 與 `--suite` 都在豁免內,`--suite keys` 沒帶 `--keys` 在擋之前就回 2。
  - 前述 `-k ""` 列漏掉見 F3。

## 實務隱患鏡頭
- 金流、對外送出、不可逆:無,spec 已寫明排除理由,與程式碼一致。
- 守衛面:有,新擋停會造成誤擋。誤擋點是 F4(hook 提示)與 F5(測試自身的環境)。
- 併發:F5 的暫存目錄斷言在多片與多會談下不穩。
- 資源:F5 的遞迴風險。

## 固定席逐條判
- `bound-tests-gate`:不影響。
  - 該閘用 run_cmd 帶 `-k` 逐支真跑綁定測試,`-k` 在豁免內。
  - 但綁定測試的方法名是 `t_runner_chat_full_suite_block`,以 `-k` 子字串會同時選中 `..._process`,合約不受影響。
- `測試假綠形態`:不影響。
  - 新增的擋回 2,不是回 0,不製造假綠。
  - S3 的前置斷言要確認被測路徑真的被走到(子程序確實 `CLAUDECODE=1` 且被擋),F5 已涵蓋。
- `canary-audit`、`design-loop`、`lumos-cli-lifecycle`、`lumos-cli-read`、`guard-kill`:不影響,這些合約不經過 `test_lumos.py` 的 `main()` 參數判斷。
  - `guard-kill` 的子程序跑綁定測試帶 `-k`,仍在豁免內(⚠ 沒有逐個核對它的呼叫字串,`scripts/lumos` 沒有出現 `test_lumos` 字面,是以執行時組字串)。

總結:最高等級為 major,blocking 共 5 條
