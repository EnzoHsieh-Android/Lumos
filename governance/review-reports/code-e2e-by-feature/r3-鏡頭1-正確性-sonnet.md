severity: major

## F1 測試沒守住「既有那筆必須是完整的才護住它」
severity: major
blocking: 是
file: `scripts/lumos:41029`(`_e2e_keep_old` 最後一行)
失敗場景:`feature_runs` 裡既有一筆 `{result: pass, complete: False}`(例如用 `--no-perf` 跑出來的)。
- 這次的結果是 `unjudged`,或不完整但通過。
- S27 的規則只保護「完整、判完」的既有結果,所以這次的應該蓋掉它。
- 把 `old.get("complete")` 改成 `True` 後,既有那筆不完整的結果就被當成完整的護住了。
- 這時紀錄會留著舊 run_id 和舊結果,而不是這次較新的 `unjudged`。

最小重現:我在 `after` 的複本裡把 `bool(old.get("complete") and ...` 換成 `bool(True and ...`,再跑 `python3.14 scripts/test_lumos.py -k android_e2e`,結果 359 過 0 紅,沒有任何測試翻紅。
- 載入的版本:複本的 `scripts/lumos`,HEAD 為 `4b056532`。
- 直接呼叫原函數:`_e2e_keep_old({"result":"pass","complete":False,...}, {"result":"unjudged","complete":False}, ...)`,修後版回 `False`(正確),被改壞的版本會回 `True`。
- 現有測試只涵蓋「既有是完整的」(`t_android_e2e_feature_record_rules`、`..._trust`)。

歸因:有證據的原有漏查。修補 `ef986b30` 新寫的 `_e2e_keep_old` 沒有對應的反向測試,修前沒有這個函式可比。
引句:「    return bool(old.get("complete") and old.get("result") in ("pass", "fail") and (new["result"] == "unjudged" or not new["complete"]))」

## F2 LUMOS_E2E_COLLECT 有設但記憶體塊沒用到,也擋下紀錄並誤說是記憶體的問題
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`(`Steps.__init__`),`scripts/lumos`(`_e2e_judge_target`、`_e2e_feature_record`)
失敗場景:環境裡有 `LUMOS_E2E_COLLECT=/bin/true`,專案沒開 stability(或按功能跑帶了 `--no-memory`)。
- 修前:`--case login.ok --no-memory` 照寫 `feature_runs`(記錄 1 份),整套跑 rc 0 並寫紀錄。
- 修後:按功能跑只印「這次只記進本機檢測總表,沒寫查證紀錄:記憶體收集腳本換成了 /bin/true」,紀錄 0 份;整套跑 rc 2 並寫「擋下:記憶體收集腳本換成了…」。
- 收集腳本根本沒被呼叫,理由不成立,而且擋下後整套驗收白跑。

歸因:有證據的修復回歸。兩版在同一個專案(`_e2e_feat_env`)、同一條環境變數下的結果不同,見上面兩行。
引句:「        if os.environ.get("LUMOS_E2E_COLLECT"):   # 換了收集腳本(測試用替身):judge 看到就不寫查證紀錄」

## F3 按功能的 judge 在記錄寫不進去時噴 traceback、回 1,而且漏記總表
severity: minor
blocking: 否
file: `scripts/lumos:41067`(`_put` 和 `_e2e_record_update` 的呼叫)
失敗場景:`.lumos/e2e-records` 不可寫(權限、磁碟滿都會走到)。
- 重現:先跑一次 `--case login.ok`,再 `chmod 555 .lumos/e2e-records`,第二次 `--case login.ok run-a2`。
- 結果是終端先印「情境 login.ok:通過」,接著 `PermissionError`(`_write_bytes_atomic`)traceback,rc 是 1,總表也沒有第二列(只有第一次的一列)。
- 這違反 `_e2e_feature_record` docstring 的承諾「寫不進去只提醒,不改這次的回傳碼」,也違反 S25「每一次都記」。
- `_e2e_record_update` 沒接 OSError。

歸因:有證據的原有漏查。修前 `787dd51b` 與修後 `4b056532` 用同一個重現,都是同一個 traceback 和 rc 1。
引句:「    p, werr = _e2e_record_update(root, fp, _put)」

## F4 判定擋下的按功能跑:總表標成「整套」,或根本不記
severity: minor
blocking: 否
file: `scripts/lumos`(`_e2e_history_append`、`_e2e_judge_selected`)
失敗場景一:`steps.json` 壞掉,跑 `judge <dir> --no-record --history`。
- 總表那一列是 `mode:"full"`、`cases:[]`。
- `history` 顯示「整套 … 擋下:讀不了 steps.json」,按功能跑被誤標成整套。
- 原因是 `mode` 只在 `selection` 讀得到時才用 `selection.mode`。

失敗場景二:對按功能跑的目錄跑 `judge <dir> --history`(沒帶 `--no-record`)。
- 回 2 並印「擋下」,但總表列數不變(實測前後都是 1 列)。
- S25 寫「judge 擋下沒寫紀錄的那次也記、附原因」,這條路沒記。

測試缺口:我把 `_e2e_judge_selected` 裡 `serr` 分支的 `_e2e_history_append(...)` 換成 `pass`,`-k android_e2e_history` 15 過 0 紅,沒有測試守住它。
歸因:有證據的原有漏查。修前修後兩版都是同樣的行為。
引句:「            "dirty": steps.get("dirty"), "mode": sel.get("mode", "full") if mode == "partial" else "full",」

## 三問的回答

**① 原問題的修復效果(我自己跑兩版,同一案例):**
- G1:`macrobench` 方法名 `B$X` 做 `--check-config`,修前 rc 0,修後 rc 2 並點名。
- G6:`paths` 寫 `app//src`,修前 rc 0,修後 rc 2。`macrobench_cmd` 是清單且 `macrobench` 沒開,修前 rc 0,修後 rc 2「要是字串」。
- G2:`--case perf.only`(只列效能),修前 rc 0,修後 rc 1。
- G3/G4:先有完整的 `login.ok` 通過,再跑 `--no-perf` 通過,兩版都不蓋掉。接著 `--no-perf` 且 flow 失敗,修前停在舊的 `run-g3a pass`,修後蓋成 `run-g3c fail`。
- G5:讓 `ls-files` 回 None,修前回 `([], '')`(當成沒改動),修後回錯誤「讀不到改動」。共用 flow `.maestro/shared/c.yaml` 在混合命中時,修前 `unmatched` 是 `[]`,修後會列出。
- G7:shell 殘留 `LUMOS_STABILITY_SCENARIO=cart`,修前 stability 段本身收集時還帶著 `cart`,修後是空。替身收集腳本,修前整套 judge rc 1 且寫了紀錄,修後 rc 2 且沒寫。
- G8:`history --case login.ok`,修前顯示「沒過 … ui .maestro/other.yaml」(別的情境失敗算到它頭上),修後顯示「通過」。

**② 修補處的正常、相鄰路徑:**
- 我另外跑了 `-k android_e2e` 全部測試,修後版 359 過 0 紅。
- 我確認這些路徑仍成立:`--case` 正常通過寫入 `feature_runs`、`--feature` 失敗回 1、`--changed` 只跑改到的功能。
- 髒樹與 HEAD 換了不寫紀錄這兩條,我只靠 `t_android_e2e_feature_record_rules` 的斷言,沒有另外重跑(`旁證`)。
- 我只用 mutation 檢查了「測試能不能抓到改壞」:其中 6 個 mutant 被抓到,2 個沒被抓到(F1、F4)。
  - 被抓到:移除 judge 整次結果重算那行、移除 `.maestro` 和設定檔的 unmatched 擴充、移除 `skipped` 計算、移除 stability 的 name 篩選、移除總表補換行。
- 相鄰路徑出現新問題的是 F2。

**③ 新發現的同一案例修前修後:**
- F1:修前沒有 `_e2e_keep_old`(未判定,無可比版本);修後的函數回傳值如上。
- F2:有證據,修前寫紀錄、修後不寫。
- F3、F4:兩版相同,屬原有。

**未驗範圍:**
- 真機上 `adb` 和 `maestro` 的實跑(測試用 fake)。
- 與規格 S27/S22 一致性:`complete` 欄的語意(S27)在 F1 判為測試缺口,其餘與實作一致。
- 推送前檢查(下一批)。
- 併發和多機。

## 規格 S22、S24、S27 一致性(本案特定鏡頭)
- S22、S24:實作一致。沒帶 `--no-record` 但有 `selection` 時拒寫並回 2(實測 rc 2、紀錄 0 份),帶 `--no-record` 時不碰 `runs`。
- S27:寫入前提(開跑時乾淨、判讀時乾淨、HEAD 沒換)、「這次沒過一律蓋掉」、「重判較早的不蓋掉」都和實作一致。「完整」的保護條件缺反向測試,見 F1。
- judge 整套路徑:髒樹拒寫、HEAD 換了回 2 仍然成立,見 `_e2e_judge_target` 與 `_e2e_judge_cmd`。重構沒有弄壞它們。

## manifest 判定
`scripts/lumos 寫總表那段的 open(` 這一題,判誤報。總表寫入走 `_local_ledger_append`(`os.open` 的 fd 在 `finally` 裡 `os.close`)和 `_ledger_tail_needs_newline`(同樣在 `finally` 關)。diff 裡沒有新增裸 `open(`。收集腳本裡 `json.load(open(...))` 那行是既有的上下文,不在這次改動。

## 圖譜鏡頭
這次沒附固定席節點(`LUMOS-LENS` 寫「鎖狀態未知」),也沒有逐條要答的固定席筆記,依派工詞走備援,不逐條答。鎖檔 `…warming` 我讀不到(No such file),沒有動它。

## 角色卡
- be-api-compat:新增 `judge --no-record/--history` 和 `select/history` 子指令。舊呼叫(`judge <dir> --repo`)行為不變。新範本配舊 lumos 會因為不認得 `--history` 而 argparse 回 2,屬於範本與 lumos 同步發版的前提。記錄 schema 多了 `feature_runs`,`runs` 可為 null 的語意已寫進 `_e2e_record_err`;目前沒有讀 `runs is None` 當放行的消費者,我用 grep 確認過。
- be-authz:本地 CLI,不涉及登入或多人資料。方法名、情境名、run-id 都驗過字元集。

按功能跑的核心路徑大致可信,有一個測試缺口(F1)要補,另有一個修補造成的誤擋(F2)、兩個原有的小洞(F3、F4)。

我的臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭1-正確性-sonnet` 已用字面絕對路徑刪除。
