severity: major

警示鎖 `…769b2e46….json.warming` 在 `/Users/enzo/.cache/lumos/dispatch-lens/` 下不存在,不需要處理。`e2e-docs` 的 HEAD 是 787dd51b。我只讀它,只在臨時目錄跑了重現,沒有對它做 checkout、reset 或 commit。

## F1 效能測試方法名收了 `$`,但交給 sh 後被展開,實際跑的是別的測試
severity: major
blocking: 是
file: `scripts/templates/android-e2e-run.sh`(`re.fullmatch(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*", t)` 與 `.replace("{{TEST}}", t)` 兩行);`scripts/lumos` 的 `E2E_BENCH_NAME_RE`
失敗場景:
- 修補把 `$` 加進允許字元,用意是收 Kotlin 巢狀類別。
- 方法名是原樣換進 `sh -c` 的指令字串,沒有加引號,所以 `Outer$Inner#test` 會變成 `Outer#test`(`$Inner` 被當成空變數)。
- 設定檢查回 0,驗收照常「通過」,但跑的不是被指名的測試。這比修前的行為更糟:修前遇到 `$` 會直接擋下。
- 允許字元裡沒有括號和大括號,所以沒有指令注入,只有被改名或被環境變數替換。
- 修補寫的測試只驗 `--check-config` 回 0,沒驗換進指令後的字串。

引句:「if t is not None and not re.fullmatch(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*", t):」

重現,同一個案例的修前與修後:
- 修前:在 9e21d491 的範本腳本第 476 行,規則是 `[A-Za-z0-9_.#]+`,`$` 會被 `die` 擋下。
- 修後:在 787dd51b 的臨時 repo 設定 `macrobench:["Outer$Inner#test"]`、`macrobench_cmd='echo {{TEST}} >> "$FAKE_DIR/bench.log"'`,用 `sh android-e2e-run.sh --case login.ok run-b1`。
  - 結果 `macrobench --check-config` 回 0,腳本回 0,`bench.log` 內容是 `Outer#test`。
  - 單純的 `sh -c 'echo Outer$Inner#test'` 也輸出 `Outer#test`。
- 我是用修後測試檔裡的 `_e2e_feat_env` 等輔助函式,載入修後版 `scripts/test_lumos.py` 跑的。

歸因:有證據的修復回歸。
- 修前被擋,修後被默默改名,兩邊都有跑或有程式碼對照。
- 修法方向有兩個:這條規則維持不收 `$`,或換進指令時用 `shlex.quote`。

## F2 同一版已有完整 pass 時,後來的不完整但真失敗的結果被丟掉,紀錄仍寫 pass
severity: major
blocking: 是
file: `scripts/lumos` 的 `_e2e_feature_record` 內 `_put`,即 `if (old.get("commit") == head and old.get("complete") and old.get("result") in ("pass", "fail")` 那段
失敗場景:
- 同一個提交先完整跑過 `login.ok`(pass,complete)。
- 再用 `--no-perf` 跑,flow 這次真的失敗,所以結果是 `fail`、`complete: False`。
- 條件 `not v["complete"]` 成立,舊的 pass 被留下,這次的 fail 沒進 `feature_runs`。
- 終端只印「這一版已有完整的結果,這次不完整或沒判完的沒蓋掉它」。這句寫的是「不完整或沒判完」,真失敗也被它蓋過去了。
- 結果是會提交進版控的查證紀錄寫著 pass,但同一版最後一次真實結果是 fail。
- 計劃第 116 行寫「同一個指紋重跑、這次沒過,會蓋掉先前的 pass(重跑出現的失敗就是真訊號)」,這個行為跟它相反。
- S27 的字面是「不拿這次不完整或沒判完的蓋掉」,可以讀成允許這樣做。所以規格有歧義,實作選了會遮住失敗的那一邊。
- 修法方向:只有「不完整且沒有 fail」或「unjudged」才保留舊結果;結果是 fail 的一律覆蓋。

引句:「and (not v["complete"] or v["result"] == "unjudged")):」

重現,同一個案例的修前與修後:
- 步驟:`login.ok` 帶一個效能方法,先 `--case login.ok run-k1`(通過),再把假 maestro 的 `rcs` 設成 `1 1 1 1`,跑 `--case login.ok --no-perf run-k2`。
- 修前(9e21d491 的臨時 clone):`feature_runs["login.ok"]` 是 `{result: fail, complete: False, run_id: run-k2}`。
- 修後(787dd51b):`feature_runs["login.ok"]` 是 `{result: pass, complete: True, run_id: run-k1}`。
  - 本機總表 `history.jsonl` 的 run-k2 那行是 fail,所以兩份紀錄互相矛盾。

歸因:有證據的修復回歸。`kept` 邏輯是這次修補新增的,修前無條件覆蓋。

## 三問的答案

① 原問題的修復效果:
- 我只對兩個題目做了行為驗證:`$` 方法名(F1),以及 `kept` 保留邏輯(F2)。兩者都是修補本身出問題。
- 其他修補(`--changed` 對沒追蹤目錄與 flow 檔、總表記擋下、`--last` 檢查、旗標檢查、`stability_scenarios` 輪數上限)我只讀了程式碼並對照修補附的測試,沒有逐項做修前修後對跑,所以這些的修復效果是未判定。

② 修補處的正常、錯誤與相鄰路徑:
- 正常路徑:完整通過後 `feature_runs` 照寫,`kept` 在「新結果不完整且是 pass」或「unjudged」時保留舊的,這部分行為成立。這是在 F2 重現過程中對照確認的。
- 錯誤路徑:真失敗被舊 pass 吞掉(F2)。
- 相鄰路徑:`$` 進了 `sh -c`(F1)。

③ 新發現的同一案例在修前與修後各是什麼結果:見 F1、F2 各自的重現。

## 已驗與未驗範圍
- 已驗:F1、F2 的修前修後;`_local_ledger_append`、`_ledger_tail_needs_newline`、`_canary_ledger_rows` 的簽名與行為,和總表新寫法相容;`_dirty_non_bookkeeping` 預設不含沒追蹤的檔,所以新加的 `ls-files --others` 沒有重複;`_BOOKKEEPING_DIRS` 是 tuple,`startswith` 用法正確。
- 沒逐項跑:`--changed` 與歷史總表的其餘路徑,只讀了程式碼,不另下保證。
- 一個觀察,未升為 finding:整套 judge 現在會要求 `stability_scenarios` 每個情境都跑過,但指紋只算 `e2e` 段,計劃 S2 明寫 `macrobench.json` 其他段不影響指紋。新增情境不會讓舊的 pass 失效。這是計劃寫明的取捨,歸因未判定。
- 沒跑全套測試。

## manifest 判定
- 內建的 `open(` handle 題:這次差異新增的程式碼沒有裸 `open(`。總表追加走 `_local_ledger_append`(`os.open` 加 `os.close` 在 finally);測試裡的 `open(p, "a")` 都在 `with` 內。判定為誤報,不是真隱患。
- 併發類題目依規定算範圍外。

## 圖譜鏡頭
`lumos impact --diff` 列出 38 條固定席加 top 8,沒有固定席節點被附加到本席。我只對和這次改動直接相關的三篇做了判讀;其餘條目(`lumos-cli-*`、`guard-kill`、`design-loop` 等)是因為 `scripts/lumos` 與 `scripts/test_lumos.py` 的檔案牽連才被推上來,本席判斷其內容與這次改動無關,不逐條答。
- `Projects/Android端到端驗收_計劃.md`:
  - 第 116 行(重跑沒過會蓋掉先前的 pass)與 S27(不拿不完整的蓋掉)互相拉扯,是 F2 的規格來源歧義。
  - S26 要求方法名「開頭 #、含空白」要擋,沒說要收 `$`;`$` 是修補多收的,F1 的來源。
  - S2 寫明 `macrobench.json` 其他段不影響指紋。
- `Systems/android-stability-collector.md` 與 `Systems/android-e2e-acceptance.md`:收集腳本的欄位清單與 `E2E_SCENARIO_KEYS`、驗收腳本與 `E2E_BENCH_NAME_RE` 各留一份,由 `t_android_e2e_lists_match_templates` 比對相等,這一點成立。但規則相等不等於規則安全,F1 就是兩邊一起放行了 `$`。

兩處放行或計劃文字與實作的落差各造成一條會誤導驗收結論的行為,是這次審查的重點。
