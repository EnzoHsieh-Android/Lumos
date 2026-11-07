severity: blocker

## F1 `--lf` 沒進 `_fanout_wanted`,擋下訊息推薦的指令會跑成全套
severity: blocker
blocking: 是(照 spec 字面實作,擋下訊息叫人用的 `--lf` 會直接開出全套切片)
- spec 段落:做 1、做 3、做 5、S5。
引句:「第 1 條接在位置參數併進 `-k` 之後、`if _fanout_wanted(_args):` 之前」
- 問題:spec 只在新判斷函式的條件裡加了 `args.lf`,沒說要改 `_fanout_wanted`。現行 `_fanout_wanted` 的條件是 `not (keyword or shard or suite or list or serial or exitfirst) and _fanout_shards() > 1`,裡面沒有 `lf`。
  - 對話裡:`--lf` 通過新擋(`--lf` 算條件),接著 `_fanout_wanted` 回 True,`_fanout_main` 開 4 片各跑 `--shard i/4`。
  - `_fanout_main` 組子程序參數的 `extra` 只帶 `--seed`、`--keep-tmp`、`--ff`,不帶 `--lf`。每片因此都是全套的一片,整套約 4 分鐘照跑。
  - 一般終端機(沒有 `CLAUDECODE`)打 `--lf`,結果一樣。
  - S5 若用預設片數,「只跑那 2 支」會紅;若測試設 `LUMOS_TEST_SHARDS=1`,就蓋住這個洞。
- 佐證:file: `scripts/test_lumos.py:49391-49399`(`_fanout_wanted`)與 `scripts/test_lumos.py:49465-49470`(`_fanout_main` 的 `extra`)。
- 修法:`_fanout_wanted` 要把 `args.lf` 當條件。

## F2 `--lf` 讀的紀錄可能過期,紀錄全不對應時回綠、一支都不跑
severity: major
blocking: 是(`--lf` 重跑已修好的測試,或在沒驗任何東西時回 0,都會讓人誤判已修好)
- spec 段落:做 5、S5、預期值表。
引句:「沒有紀錄時印一行並回 2,不退成全套」
- 問題一,紀錄是誰寫的、全綠後清不清:
  - 現行紀錄在 `.lumos/test-cache.json`(不分片)與 `test-cache-shard{i}of{n}.json`(各片各一份)。
  - 每次跑完、只要是來源 repo,就把這次的 `_failed_names` 覆寫進「自己這個檔名」的那一份。
  - 讀的時候是 `glob("test-cache*.json")` 全部聯集。
  - 推送前閘紅了之後,紅名字寫在各片檔裡。`--lf -x` 不帶 `--shard`,只會覆寫 `test-cache.json`,各片檔不會被清。
  - 修好、`--lf` 全綠後,舊紅名字仍在各片檔裡,`--lf` 之後每次都再跑它們。
  - 對話裡用 `-k` 跑修好的那支,也只覆寫 `test-cache.json`,同樣清不掉各片檔。
  - 「全綠就清空」只對同檔名成立。spec 只說「沿用既有紀錄」,沒處理這個。
- 問題二,紀錄與現有測試對不上:
  - 紀錄裡的名字若已改名或刪除,`tests` 會變空。
  - 非 `--shard` 的路徑只有 `if _args.keyword and not tests` 這道零支檢查,`--lf` 不帶 `-k`,過不了這道。
  - 結果是「0 passed, 0 failed」、回 0。spec 的「沒有紀錄回 2」沒涵蓋「有紀錄但選中 0 支」。
- 問題三,消費專案:
  - 紀錄只在 `_is_src` 時寫,消費專案永遠沒有紀錄。
  - 推送前閘的提示改成 `--lf -x` 之後,消費專案照提示打,一律 rc 2。
  - 原本的 `--ff -x` 沒紀錄時會退回照原順序跑。
  - 這是 spec 沒提的行為退步。
- 佐證:file: `scripts/test_lumos.py:49742-49757`(讀聯集)、`scripts/test_lumos.py:49850-49855`(寫自己那份)、`scripts/test_lumos.py:49778-49792`(`-k` 零支才判紅)。

## F3 三成門檻的分母與分子沒定義,和 `--shard`、`--list`、`--lf` 的組合會錯
severity: major
blocking: 是(實作者無法照字面寫出條款 S3 能驗的行為,必須自己猜)
- spec 段落:做 2、做 3、S3。
引句:「選中支數超過全部測試的三成就擋,訊息印選中幾支、全部幾支」
- 問題一,`--shard`:
  - 現行 main 先分片再篩 `-k`,`tests` 在 `-k` 篩選時已經只剩這一片(約 1/4)。
  - 照做 3「接在測試清單篩選完」實作,分母變成「這一片的支數」,不是 spec 寫的「全部測試」。
  - `--shard 1/4 -k t_` 的 N/M 會印成片內數字,和訊息寫的「全部幾支」不符。
  - 分母要在分片前記下來。
- 問題二,`--suite keys`:
  - `tests` 在 keys 選完後被選中的子集覆寫,原總數已不在。
  - 實作要另存分母。
  - 現行 `cap` 是「單一關鍵字」命中超過三成就丟掉該關鍵字,spec 做 2 要的是「聯集選中支數」超過三成,量的東西不同。
  - 「沿用既有門檻」只沿用了 0.3 這個數字,而且那只是參數預設值,不是具名常數。多個各自不到三成的關鍵字聯集會超過,這正是做 2 要擋的情形,spec 沒說清。
- 問題三,`--list`:
  - 做 2 說「同樣的豁免都不成立時」,`--list` 不是豁免。
  - 現行 `--list` 在篩完 `-k` 之後就印清單並 return,位置與第 2 條的插入點(「篩選完、開始跑之前」)相同。
  - 照字面實作會讓 `--list -k t_` 被擋。
  - 預期值表又說 `--list` 不擋。
  - spec 內部不一致。
- 問題四,`--lf`:
  - 做 2 只提「關鍵字篩選或 `--suite keys`」。
  - `--lf` 選中的支數(例:環境壞掉時紅了四成)是否套三成,沒寫。
  - 若套用,擋下訊息推薦的 `--lf` 會自己被擋。
- 佐證:file: `scripts/test_lumos.py:49720-49733`(分片後才篩)、`scripts/test_lumos.py:49766`(`-k` 篩選)、`scripts/test_lumos.py:58-76`(`_keys_suite_select`)。

## F4 逃生門理由「至少 10 字」的算法與既有 `_dispositions_reason_ok` 不一致
severity: minor
blocking: 否(自用框架、單人;不一致只是門檻比較鬆,不會算錯)
- spec 段落:做 6、S2。
引句:「理由去空白後至少 10 個字才算數(不夠照擋並講要寫理由)」
- 問題:
  - spec 寫「去空白後至少 10 個字」。
  - 專案既有的判法是 `_dispositions_reason_ok`:去掉空白與標點後,CJK 字數 ≥10,或總字數 ≥25。
  - 照 spec 字面做,`xxxxxxxxxx` 與 `run full suite` 都算數,既有判法會擋下。
  - spec 又寫「命名照鄰居」,卻沒說門檻照不照鄰居,也沒說不照的理由。
  - 該函式在 `scripts/lumos`,執行器要用得先走 `_load_lumos_inproc()`,spec 也沒提。
- 佐證:file: `scripts/lumos:73519-73525`(`_dispositions_reason_ok`)。

## F5 計數檔寫入沒涵蓋建目錄與家目錄失敗,也沒保證單行原子追加
severity: minor
blocking: 否(寫不進去只丟計數,不影響判斷,但會讓 RETIRE-IF 量不到)
- spec 段落:做 7、RETIRE-IF、REVISIT。
引句:「寫不進去就略過、不影響判斷」
- 問題:
  - spec 只說「寫不進去就略過」。
  - 沒說要先建 `~/.cache/lumos/`。不建的話,第一次寫入就失敗並被略過,計數永遠是 0。
  - 沒說只攔 `OSError`。家目錄解析失敗(例如 `HOME` 沒設時 `Path.home()` 丟的 `RuntimeError`)不是 `OSError`,會在擋下路徑上多出一個例外。
  - 沒說每筆用一次 `write` 追加。多片或多個會談同時寫一行 JSON,只有單次 `O_APPEND` 寫入才不會交錯,spec 只說「追加一行」。
  - 擋下與放行的計數寫在判斷時、`_isolate_environment` 之前,用的是真家目錄,這點與 S4 的私有 `HOME` 一致,沒問題。
- 佐證:file: `scripts/test_lumos.py:49596-49665`(`main()` 開頭到 `_fanout_wanted` 之間的順序);`lumos` 其他處已有 `~/.cache/lumos/` 的建目錄先例(`scripts/lumos:30547`)。

## 已讀無 finding 的條目
- 做 1 的豁免:`LUMOS_PUSH_ATTEMPT` 在 `scripts/hooks/pre-push:393` 先 export,各片帶 `--shard` 且無條件,被豁免,不會被擋。
- 做 3 的「先判再拿掉 `CLAUDECODE`」:現行 main 中,`_fanout_wanted` 之前沒有任何判斷,順序可行。`CLAUDECODE` 在 repo 內只有 `scenario_probe.py:1162` 讀,沒有測試依賴它。
- `scripts/hooks/pre-push:1032` 與 `:1035` 兩處提示確實存在,「兩處」的說法對得上。

## 固定席對照
- bound-tests-gate、lumos-cli-lifecycle、canary-audit、guard-kill、lumos-cli-read、測試假綠形態:都不影響,這份設計只動執行器入口、一個旗標與推送前閘的提示,不碰那些節點的合約行。
- design-loop 處置閘第五步:⚠ 本計劃的 S1–S5 帶 `[test:]` 但未見 `[綁定測試:有]` 標記,測試函式也還不存在(只在計劃裡),處置閘要不要判過,我看不到那個判定結果。
- 其餘節點:都是 scenario_probe 牽連來的間接節點,本計劃沒動 scenario_probe,不影響。

## 實務隱患鏡頭
- 金流:無,不碰付款。
- 對外送出:無,不連網。
- 不可逆:無,計數檔在工作目錄外、退提交即回原狀。
- 守衛面(新擋停):有,對應 F1、F2、F3。
- 併發多片同時寫計數檔:見 F5。

總結:最高等級為 blocker,blocking 共 3 條。
