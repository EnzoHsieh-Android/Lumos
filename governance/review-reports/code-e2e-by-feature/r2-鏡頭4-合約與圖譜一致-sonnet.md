severity: major

派工詞要的鎖 `.warming` 檔不存在(cat 回「No such file」),所以沒有鎖要處理。我沒碰 `e2e-docs` 的 git 狀態。所有實驗都在我自己的臨時目錄裡做,做完已用字面路徑刪除。

## F1 文件說效能方法名可含 `$`,修後照寫會靜默跑錯測試
severity: major
blocking: 是
file: `scripts/lumos:40383`、`scripts/templates/android-e2e-run.sh` 的 macrobench 段(`cmd = e2e["macrobench_cmd"].replace("{{TEST}}", t)`,再交給 `["sh","-c",cmd]`)。文件側是 lumos-android-evidence SKILL 的「測試方法名,只收英數字、點、底線、`$` 與 `#`」,以及 Android端到端驗收_計劃 的 S26。

失敗場景:
- 照 skill 為 Kotlin 巢狀類別寫 `"macrobench": ["Outer$Inner#test"]`,`macrobench_cmd` 為 `echo {{TEST}} >> bench.log` 這類未加引號的寫法。
- `--check-config` 回 0。
- 腳本把名稱原樣換進 `sh -c`,`$Inner` 被 shell 展開成空字串,實際跑的是 `Outer#test`。
- 回傳碼 0,沒有任何警告,效能紀錄對應的是錯的測試。
- 測試 `t_android_e2e_args_and_names` 只驗「設定檢查回 0」,沒驗命令真的收到什麼。

引句:「E2E_BENCH_NAME_RE = re.compile(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*")」

歸因:有證據的修復回歸。
- 修後 `787dd51b`:用 `_e2e_feat_env` 起暫存專案,同一案例,`--check-config` rc 0,跑 `--case login.ok` rc 0,`bench.log` 內容是 `Outer#test`。
- 修前 `9e21d491`(換上修後的測試檔):同一案例,run rc 2,訊息「擋下:效能測試方法名只收英數字、點、#、底線:'Outer$Inner#test'」,`bench.log` 不存在。
- 修前是擋下,修後是放行並跑錯。
- 純 shell 對照:`sh -c 'echo Outer$Inner#test'` 印出 `Outer#test`。

## F2 S28「整套跑各情境各判一次」的綁定測試沒有驗到整套判讀路徑
severity: major
blocking: 否
file: `scripts/lumos:40777`(`_e2e_evaluate` 裡 `_e2e_stab_by_name(e2e, steps, [None, *scen], notices) if e2e.get("stability") and scen`);測試 `t_android_e2e_memory_by_case`(`scripts/test_lumos.py`)。

失敗場景:
- 條款 S28 說整套跑時 `stability` 段本身加每個 `stability_scenarios` 情境「各判一次」。
- 測試對整套跑只檢查 `collect.log`,也就是收集腳本被叫了幾次。
- 「各判一次」只在 `--no-record` 的按功能判讀路徑上驗過。
- 我把整套判讀那個分支換成只判 `stability` 段本身(模擬回歸),再跑 `-k android_e2e_memory_by_case`(7 過 0 紅)、`-k android_e2e_judge`(122 過 0 紅)、`-k android_e2e_by_feature`(21 過 0 紅)。
- 全綠,守衛被拿掉測試沒紅。
- 這會讓整套紀錄在其他情境沒判到時仍寫成「整套驗過」。
- 這違反圖譜〈測試假綠形態〉的 ★INVARIANT★:拔掉被測守衛要翻紅。

引句:「stab = (_e2e_stab_by_name(e2e, steps, [None, *scen], notices) if e2e.get("stability") and scen」(取自 `scripts/lumos`,審材外查證,見下)

file: `scripts/lumos:40777-40782`

歸因:有證據的修補自帶測試缺口。修前 `_e2e_evaluate(e2e, steps, run_dir)` 沒有 `scen` 參數,此行為是修補新增的;修前沒有 `t_android_e2e_memory_by_case`(`git show 9e21d491:scripts/test_lumos.py` 計數為 0)。

## F3 README「記憶體沒過時的 stability.json 路徑」對情境跑是錯的
severity: minor
blocking: 否
file: `README.md:395`、`README.en.md` 對應句。這句是 diff 的上下文行,不是新增行,但這次改動讓按情境收集成為主要路徑。

失敗場景:
- 按功能或整套跑的記憶體情境,收集腳本寫到 `.lumos/artifacts/android/<run-id>.<情境>/stability.json`,是兄弟目錄,不在 `<run-id>/` 裡。
- 照 README 去 `<run-id>/stability.json` 找會找不到。
- 總表 `history.jsonl` 的 `evidence` 也只指 `<run-id>`。
- 腳本有 `sid = run_id if scn is None else f"{run_id}.{scn}"`;測試裡 `collected(fake) == [["run-c1.player","player"]]`。

引句:「記憶體沒過時原始數字在這次的產物目錄（`.lumos/artifacts/android/<run-id>/stability.json`），照上面的分層查證往下找。」

歸因:有證據的原有漏查。`9e21d491` 與 `787dd51b` 的 README 該行逐字相同;`9e21d491` 的腳本已有 `<run-id>.<情境>` 目錄。

## F4 README 與 manual 把回傳碼、紀錄寫入說成只有整套的行為
severity: minor
blocking: 否
file: `skills/lumos-project-notes/commands/04-自檢與健康.md` 那一列的結果欄;`docs/lumos-toolchain-knowledge/Systems/android-e2e-acceptance.md` 的〈怎麼跑〉與〈回傳碼〉段(正文未改,只動了 `updated`);README「Passed: the record is written」。

失敗場景:
- 這些地方寫「0=寫了紀錄且通過」「2=沒寫紀錄(…工作目錄有未提交改動…)」「改動要先提交再跑」。
- 按功能跑在有改動的工作目錄會回 0,只寫總表、不寫紀錄。
- 按功能跑選不到時才回 2。
- AI 若用回傳碼判斷「紀錄有沒有寫」,會誤判。
- 系統節點〈怎麼跑〉也完全沒列 `--changed`、`--feature`、`--case`。

引句:「0=通過、1=有一段沒過、2=沒寫紀錄(設定不合格、工作目錄有未提交改動、跑到一半 HEAD 變了);改動要先提交再跑」

歸因:未判定。這是文字沒隨 `9e21d491` 與 `787dd51b` 的行為更新,兩版都沒改正文。

## F5 圖產生器筆記的 WHY 與條款、圖本身互相矛盾
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Systems/README圖產生器.md` 新增的 WHY 行。

失敗場景:
- 該行寫「查證紀錄(只有整套跑寫)」。
- S27 與同一張圖的文字都說按功能跑在乾淨時也寫 `feature_runs`(圖上「按功能跑:從頭到尾都乾淨也記進紀錄」)。
- 讀筆記的下一個 AI 會以為按功能跑從不寫查證紀錄。

引句:「結果與底下兩行分開講本機檢測總表(每次都記)與查證紀錄(只有整套跑寫)」

歸因:有證據的原有漏查。計劃的 r1 紀錄寫明這是第一輪「不寫紀錄」說法與實作相反的那類,README 與計劃已改,這行筆記沒跟上。

## F6 README 引用已改名的小節
severity: minor
blocking: 否
file: `README.md:357`、`README.en.md` 對應句。

失敗場景:
- 效能小節仍指向下面的「推送前整套驗收」(英文版是 "full check before pushing")。
- 該小節標題這次改成「實機驗收：開發中按功能跑，推之前整套跑」,英文是 "Device acceptance: …"。
- 這是壞引用。

引句:「效能、記憶體已經接進下面的「推送前整套驗收」；單獨跑 `lumos macrobench` 時照舊只提醒。」

歸因:有證據的修復回歸,但屬於 `9e21d491` 那個提交就已改標題。`git grep` 可見舊詞只剩這兩處加治理帳。

## F7 計劃內部與實作對不上的幾處說法
severity: minor
blocking: 否
file: `Projects/Android端到端驗收_計劃.md` 的「功能對照表」「檢測紀錄」兩節。

三處對不上:
- 「沒帶 `{{TEST}}` 時按功能跑不能選效能,開跑前說明」。實作是設定檢查直接擋(S26),沒有「開跑前說明」這一步。
- 總表欄位寫「每個情境每一項的結果(…這次沒跑)」。實作的 `items` 是不分情境的平鋪清單,沒有「這次沒跑」值,效能放在另一個 `perf` 欄。
- 終端範例寫「player.open-close:UI ✓、記憶體 ✗ native_unreachable(證據 …)」。實際印的是 `情境 login.ok:沒過;沒過或沒判完:stability player:…`,沒有證據路徑。

引句:「`macrobench_cmd` 可以帶 `{{TEST}}`,按功能跑時換成選到的測試方法、一個方法跑一次(例如 `sh scripts/run-bench.sh {{TEST}}`);沒帶 `{{TEST}}` 時按功能跑不能選效能,開跑前說明。」

歸因:未判定,只比對了修後版本的實作。

## F8 文件沒講「用了 `{{TEST}}` 之後整套跑只跑對照表列到的效能方法」,README 另外把 `history` 說成「每一次」
severity: minor
blocking: 否
file: `skills/lumos-android-evidence/SKILL.md` 新增段;README 的 `lumos android-e2e history   # every check you ran`。

失敗場景:
- 整套跑的 `tests_to_run` 在 `macrobench_cmd` 帶 `{{TEST}}` 時,只跑 `features` 各情境列出的方法。
- 沒列進對照表的 Macrobenchmark 方法在整套跑裡靜默不跑。
- AI 為了按功能跑而加 `{{TEST}}`,可能不知道整套跑的效能範圍因此縮小。
- README 的 history 指令預設 `--last 20`,只列最後 20 筆,不是「每一次」。

引句:「lumos android-e2e history                                          # every check you ran (filter with --feature, --case)」

歸因:未判定。這是 `9e21d491` 設計上就有的行為,文件兩版都沒講。

## 回答三問

①原問題的修復效果,行為證據:
- 修後 `-k android_e2e` 全跑 332 過 0 紅(約 4 分 37 秒)。
- binding 說修前有 22 紅,我沒有重跑修前全套,所以修前的對照只有 F1 那一例。
- `python3.14 assets/readme-diagrams/generate.py --check` 在修前與修後兩版都回「26 bilingual SVGs: validated…」,圖本身可重現。
- 按功能跑的紀錄可信度(開跑時髒就不寫 `feature_runs`)、`--changed` 漏挑、總表半行,我只讀程式碼與測試確認了對應關係,沒另造修前修後案例。這幾組請以「未判定」看待。

②修補處的正常、錯誤與相鄰呼叫路徑:
- 相鄰路徑裡 F1(`$` 名稱)修後變壞,已有修前修後同一案例的證據。
- 整套跑的 `_e2e_evaluate` 新分支(F2)沒有測試把守。
- 文件側的使用者表述(`--changed` 對不到時的訊息、`complete` 的條件、不覆蓋完整結果的規則)與程式一致,我逐句對過 `_e2e_changed_features`、`_e2e_case_results`、`_e2e_feature_record`。
- S22–S28 的 `[test:]` 指到的測試全都存在。除 S28 的「整套各判一次」外,條款說的行為都有斷言。

③新發現的同一案例在修前、修後各是什麼:
- F1:修前擋下(rc 2),修後放行並跑錯(rc 0)。
- F2:修前沒有該行為,修後行為存在但測試缺口(模擬回歸,三組測試全綠)。
- F3、F4、F5、F6、F7、F8:兩版文字相同或修前沒有,歸因見各條。

## 圖譜鏡頭
- 本次掛鉤沒有附固定席筆記(LUMOS-LENS 寫「這次沒附固定席節點」)。我改用 `lumos impact --diff 8f613342…787dd51b` 自己查,它列出 38 個固定席加 top 8。
- 逐條判斷後,真正牽連的只有這幾篇:
  - `Systems/測試假綠形態`:★INVARIANT★「拔掉守衛要翻紅」,被 F2 觸及,條款綁定的測試沒有鑑別力。
  - `Systems/README圖產生器`:WHY 與 S27 矛盾,即 F5。
  - `Systems/android-e2e-acceptance`:正文沒更新,即 F4。
  - `Systems/android-stability-collector`:新 WHY 與程式(`LUMOS_STABILITY_SCENARIO`、欄位清單與 `E2E_SCENARIO_KEYS`)一致,無矛盾。
- 其餘固定席(`bound-tests-gate`、`lumos-cli-read`、`guard-kill` 等)這份 diff 沒有破壞它們宣稱的行為。我讀了 `bound-tests-gate` 與 `lumos-cli-read` 的 KEY/★INVARIANT★ 行,新增的 `android-e2e select` 與 `history` 子命令都是唯讀。
- 新增筆記的 WHY/PITFALL 行格式檢查:
  - 出處、因、`[test:]` 齊全。
  - `[根因:]` 與 `[修法:]` 與 `_e2e_feature_record` 的 `steps.get("dirty") is not False` 一致。
  - 不能機器證明的是 `--changed` 挑不到主線時「說明」那一句,測試只斷言 rc 2 與「對不到任何功能」字樣。
- 沒做的範圍:沒重跑修前全套測試,沒在真機跑腳本,沒審 `scripts/lumos` 其餘程式邏輯(其他席負責)。

這份文件包的主要問題是 F1(`$` 名稱修後靜默跑錯)和 F2(S28 的整套判讀沒有測試把守),其餘是文件與實作對不上的措辭問題。
