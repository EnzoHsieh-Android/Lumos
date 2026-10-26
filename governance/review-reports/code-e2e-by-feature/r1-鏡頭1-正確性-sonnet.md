severity: major

沒有發現會寫壞紀錄或讓 judge 舊路徑退化的錯誤。judge 整套路徑重構後,髒樹、HEAD 換了、schema 不認得仍然回 2,錯誤訊息的優先序也和原本相同。主要問題有兩類:規格與實作對「按功能跑是否寫 `.lumos/e2e-records/`」說法互相矛盾;測試抓不到兩塊必要行為。

## F1 `--no-record` 的文字說不寫查證紀錄,實作乾淨時會寫
severity: major
blocking: 是
file: `scripts/lumos:40905`(`_e2e_judge_partial` docstring)、`scripts/lumos:67675`(`--no-record` 的 help)、`scripts/templates/android-e2e-run.sh:6`(用法說明)、計劃 S22、S24
失敗場景:
- 輸入:已提交、乾淨的工作目錄,跑 `sh android-e2e-run.sh --case login.ok run-k1`,等於 `judge --no-record`。
- 路徑:`_e2e_judge_partial` 最後呼叫 `_e2e_feature_record`,會用 `_e2e_record_update` 建立或改寫 `.lumos/e2e-records/<指紋>.json`。
- 這次新增的 `t_android_e2e_by_feature` 第二段也斷言這個行為。
- 矛盾的文字:
  - docstring 寫「不碰 `.lumos/e2e-records/`」。
  - help 寫「只判、只印,不寫查證紀錄」。
  - 範本腳本檔頭寫「不寫查證紀錄」。
  - S22 寫「不寫 `.lumos/e2e-records/`」,S24 寫「只判、只印」。
  - 只有 S27 與計劃〈檢測紀錄〉寫「名字沿用,意思是不寫整套的 runs」。
- 後果:照 S22 或 help 做事的人,會在不知情下產生一份要提交的紀錄檔。下一批的推送檢查若依 S22 設計,會讀到一份它以為不存在的紀錄。
引句:「selection 列的東西,不碰 .lumos/e2e-records/。rc 0=選到的都過」
能當場翻紅的重現:
- 照 `t_android_e2e_by_feature` 第二段(乾淨 tmp 專案)跑 `--case login.ok`,事後 `.lumos/e2e-records/*.json` 存在。
- 同一支檔的 docstring 與這個結果相反。

## F2 測試沒保護 `--changed` 對主線分岔點的差異
severity: major
blocking: 是
file: `scripts/lumos:40800` 附近的 `_e2e_changed_files`;測試 `scripts/test_lumos.py` 的 `t_android_e2e_by_feature` 與 `_e2e_feat_env`
失敗場景:
- S23 要求「HEAD 加工作目錄改動,對分岔點的差異」。
- 測試專案沒有 remote,`_secev_mainline` 回 `None`,`base` 永遠是空字串,只走「工作目錄髒檔」那條路。
- 我在乾淨的 git clone 裡把 `if base:` 的 `git diff base head` 區塊整段換成 `if False: pass`,`python3.14 scripts/test_lumos.py -k android_e2e_by_feature` 仍是 21 passed、0 failed。
- 這個功能實際上能用:我另建了有 origin/main 的分支專案,`android-e2e select --changed` 在已提交的分支改動上正確挑出 `login.ok`。
- 缺的是「分支上已提交的改動」這個典型開發情境(提交了 A.kt、工作目錄乾淨)沒有任何斷言。
引句:「raw = _nodehome_git(root, "diff", "--name-only", "-z", "--no-renames", base, head) or b""」
補法:測試用 bare repo 當 origin,在分支上提交 A.kt,工作目錄乾淨,斷言 `--changed` 挑到 login。

## F3 測試沒涵蓋按功能跑的記憶體情境判讀與 `--no-memory`
severity: major
blocking: 是
file: `scripts/lumos:40995` 附近的 `_e2e_evaluate_selected`、`_e2e_case_results` 的 stability 段;`scripts/templates/android-e2e-run.sh` 的 `stab_to_run` 與 preflight;測試 `_e2e_feat_env` 完全沒有 `stability`、`stability_scenarios`
失敗場景:
- 我在乾淨 clone 同時做三處改壞:
  - 把 `part` 改成 `{"steps": []}`,讓每個情境都判成「沒跑到」。
  - 把 `_e2e_case_results` 的 stability 項整段清空。
  - 把 preflight 的 `if stab_to_run(cfg):` 還原成 `if e2e.get("stability"):`,讓 `--no-memory` 仍查 trace_processor。
- `-k android_e2e_by_feature` 仍是 21 passed、0 failed。
- 這三處對應 S22(記憶體情境)、S23(`--no-memory` 不查工具)與 S27(`complete` 的 stability 分支)。
- `t_android_memstab_collect_scenario` 只測收集腳本,沒測範本腳本如何傳 `LUMOS_STABILITY_SCENARIO`、`<run-id>.<情境>` 目錄、`stability_judge` 的 `name` 過濾。
引句:「part = {"steps": [x for x in steps.get("steps", []) if x.get("block") not in ("stability", "stability_judge") or x.get("name") == name]}」
補法:fixture 加一個假的 stability 收集腳本與 `stability_scenarios`,斷言「情境 A 沒過、情境 B 過」會分開記,以及 `--no-memory` 在缺 trace_processor 時不被擋。

## F4 `stability_scenarios` 的 `cycles`、`warmup` 沒有上限
severity: minor
blocking: 否
file: `scripts/lumos:39470` 的 `_e2e_scenarios_err`;對照 `_macrobench_stab_cfg_err` 的 `MACROBENCH_MAX_CYCLES = 10000`
失敗場景:
- 輸入:`"stability_scenarios": {"p": {..., "cycles": 999999999}}`。
- `macrobench --check-config` 回 0。同樣的值寫在 `stability` 段會被擋(「cycles 要是 1 到 10000 的整數」)。
- 收集腳本用 `dict(st, **scen)` 蓋過後,驅動會一直跑到逾時上限。
引句:「return f"stability_scenarios.{name} 的 warmup、cycles 要是正整數"」

## F5 效能測試方法名到跑完前面所有塊才檢查
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `accept`
失敗場景:
- `macrobench: ["Bench scroll; rm x"]` 通過 `--check-config` 與 `android-e2e select`,我已實測 rc 都是 0。
- 範本腳本建置、安裝、跑 UI、跑記憶體之後,才在效能那步 `die` 離開。
- `die` 的 `SystemExit` 不是 `Terminated` 或 `KeyboardInterrupt`,不會走到 `judge`,前面跑完的結果沒人判、總表也沒有那一行。
引句:「die(f"效能測試方法名只收英數字、點、#、底線:{t!r}")」
建議:把同一條規則放進 `_e2e_case_err`。

## F6 整套跑只跑 `stability` 段本身,不跑 `stability_scenarios` 的情境
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `stab_to_run`;對照同檔 `tests_to_run`
失敗場景:
- 整套跑時效能會把所有 features 的測試方法都跑一遍,記憶體卻只回 `[None]`(基本情境)。
- 計劃寫「整套(推送前):全部跑」,`_e2e_thresholds_err` 也要求每個情境都有門檻,但整套寫進 `runs` 的結果從未判過 `player` 這類情境。
- 未能重現:要用假的 trace_processor 才跑得到,我是讀碼確認的。
引句:「return SEL["stability"] if SEL is not None else [None]」

## F7 judge 拒寫或設定壞掉時不記總表,與 S25「每一次」不符
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_judge_cmd`、`_e2e_judge_partial`
失敗場景:
- 整套跑完,但建置弄髒工作目錄,或 HEAD 換了:`return 2` 發生在 `_e2e_history_append` 之前,總表沒有這一行。
- 按功能跑時設定在跑的途中被改壞:`_e2e_judge_partial` 回 `(2, None)`,`_e2e_history_append` 看到 `runs is None` 直接 return。
- 這些回 2 的跑法,正是最需要查歷史的時候。
- 另外,S25 與計劃寫「每個情境每一項的結果(含這次沒跑)」,總表的 `items` 是各塊攤平的,沒有按情境分,也沒有「這次沒跑」。
引句:「_e2e_history_append(root, steps, runs, "full")」

## F8 `history --last 0` 或負數會列出全部
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_history_cmd`
失敗場景:我實測 3 行總表,`--last 0` 印出 3 行,`--last -1` 印出 2 行。
引句:「for r in rows[-last:]:」

## F9 `steps.dirty` 有記錄卻沒拿來判斷;同情境重跑後沒有保留比較完整的那筆
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_feature_record`
失敗場景:
- 髒樹開跑:`dirty=True`,APK 含未提交的改動。
- 跑的途中把改動 `git stash`:判讀時工作目錄乾淨、HEAD 沒換。
- 結果:`feature_runs` 寫成「這一版 HEAD 通過」,但實際驗的是別的內容。
- 重跑同一情境時,`fr[fc] = ...` 直接覆蓋,先前 `complete: true` 的那筆會被 `--no-perf` 或 `--no-memory` 的 `complete: false` 換掉,也會被被中斷的 `unjudged` 換掉。
引句:「why = _e2e_precheck(root) or (None if head and steps.get("start_head") == head else "開跑後 HEAD 換了")」

## F10 `runs: null` 的記錄不再只代表放行
severity: minor
blocking: 否
file: `scripts/lumos:40551` 的 `_e2e_record_err` docstring 仍寫「只有放行的紀錄 runs 是 null」
失敗場景:
- 只做過按功能跑的記錄,是 `runs: null`、`waivers: []`、帶 `feature_runs`。
- S10 寫「只有放行、`runs` 是 null 的紀錄應放行」,下一批若照 `runs is None` 判放行,就會誤放行。
- 也要注意:S8 寫「最近一次」,`history` 末尾現在可能是 `kind: "feature"` 的條目,會蓋過整套的 fail。
- 目前 repo 還沒有推送檢查,所以是潛在風險。
引句:「fr = rec.get("feature_runs", {})」

## F11 沒做的規格:終端最後一段照情境列;整套跑時 `--no-perf` 被靜默忽略
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_print_runs`;`scripts/templates/android-e2e-run.sh` 的 `SELECTIVE`
失敗場景:
- 計劃寫「終端最後一段照情境列:player.open-close:UI ✓、記憶體 ✗」,實作仍按塊印。
- 只帶 `--no-memory`、沒帶 `--changed`、`--feature`、`--case` 時,`SELECTIVE` 為 False,旗標被吞掉,整套照跑並寫 `runs`。
引句:「SELECTIVE = bool(PICK["--feature"] or PICK["--case"] or "--changed" in FLAGS)」

## pitfalls manifest
內建只有一題,問 `scripts/lumos` 寫總表那段的 `open(` 有沒有 `with` 或確定關閉。`_e2e_history_append` 的 `with open(p, "a", encoding="utf-8") as fh:` 有 `with`,例外只接 `OSError`,handle 會關,判誤報。新增的 `open(` 沒有其他處。兩者都不是這次問題的重點:一行 `write` 被殺掉時可能留下沒有換行的殘行,下次 append 會黏在一起,而 `history` 讀端會略過壞行,這個機率很低,我沒標。併發類題目照規定標誤報。

## 圖譜鏡頭
固定席 `lumos-cli-read` 的 search 排除 superseded、`guard-kill` 的 rc 優先序與 `--json` 純淨、`lumos-cli-lifecycle` 的 re-inject 保留 sentinel 外內容,都不在這份 diff 的程式路徑上,沒有被破壞。`測試假綠形態` 的合約要求「還原翻紅釘要配前置斷言證明現場成立」:本次新測試對「按情境挑 flow」「--no-perf」有前置斷言,但如 F2、F3 所示,有三塊沒有任何會翻紅的斷言,與該合約精神相悖。`bound-tests-gate` 要求綁定測試能真跑:新測試都以 `-k` 跑得起來,全數通過。`pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 沒有行為被改。

## 角色卡
- be-api-compat:
  - 新增的 `feature_runs`、`history` 的 `kind: "feature"`、`steps.json` 的 `selection` 與 `dirty` 都是加欄位,舊版 lumos 讀新紀錄、新版讀沒有 `feature_runs` 的舊紀錄都不會崩。
  - 舊版整套 judge 對新紀錄是整份讀改寫,會保留 `feature_runs`。
  - 風險在語意:`--no-record` 的語意改變(F1),以及 `runs: null` 與 `history` 末尾的語意改變(F10)。
- be-authz:這份變更是本機命令列工具,沒有端點或授權面,不適用。

按功能跑的主流程大致正確,但規格自己對「寫不寫查證紀錄」說法不一(F1),且 `--changed` 的分岔點差異和記憶體情境判讀這兩塊必要行為,測試照綠地抓不到改壞(F2、F3)。
