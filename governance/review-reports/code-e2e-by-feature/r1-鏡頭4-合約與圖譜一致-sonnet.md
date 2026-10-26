severity: major

## F1 指令手冊說按功能跑不寫查證紀錄，跟程式、README、skill 三處相反
severity: major
blocking: 是
file: `skills/lumos-project-notes/commands/04-自檢與健康.md`（android-e2e 那一列）；對照 `scripts/lumos:40951`（`_e2e_feature_record`）
失敗場景：AI 查手冊這一列，讀到按功能跑「不寫查證紀錄」。但已提交、工作目錄乾淨時，按功能跑會把結果寫進 `.lumos/e2e-records/<指紋>.json` 的 `feature_runs`。手冊沒說這件事，所以 AI 不會把那份新檔 `git add` 提交，也不會把它當證據回報。README 與 skill 寫的是「寫進 feature_runs、要提交」，同一份 diff 裡兩套說法打架。
最小重現：
- `grep -n "不寫查證紀錄" skills/lumos-project-notes/commands/04-自檢與健康.md` 會命中手冊那一列。
- `python3.14 scripts/test_lumos.py -k android_e2e_by_feature` 的「乾淨時按情境的結果寫進查證紀錄」檢查證明程式確實會寫。
- `scripts/templates/android-e2e-run.sh` 檔頭註解（程式包）同樣寫著「不寫查證紀錄」，是同一個過時說法。
引句:「不要求工作目錄乾淨、不寫查證紀錄」

## F2 README 在「為什麼要先提交」一段把「只記總表」說成按功能跑的一律行為
severity: minor
blocking: 否
file: `README.en.md`、`README.md`（Why commit first／為什麼要先提交）
失敗場景：上一段「兩種紀錄」才說已提交且乾淨時按功能跑會寫 `feature_runs`。下一段卻寫成按功能跑一律只寫本機日誌，沒有「沒提交時」這個前提。照這段做的人會以為按功能跑永遠不會有查證紀錄，所以不去提交，或不去看 `feature_runs`。計劃的 S22 條款「不寫 `.lumos/e2e-records/`」也沒加「工作目錄有改動時」的前提，與 S27 讀起來互相衝突。
引句:「while a by-feature run still runs but only writes the local log」

## F3 「每一次跑都記進總表」在整套跑的兩種情況下不成立
severity: minor
blocking: 否
file: `scripts/lumos:41133-41152`（`_e2e_judge_cmd`）；README 與計劃 S25 的說法
失敗場景：整套跑在跑到一半時 HEAD 換了，或工作目錄冒出未提交改動，judge 會在 `why` 那一步直接回 2。這個提早回傳發生在 `_e2e_history_append` 之前，所以總表沒有那一行。README 與 S25 都寫「每一次（含被中斷）都記進 history.jsonl」，因此用 `lumos android-e2e history` 回頭看時，這類失敗的整套跑找不到。本項是讀程式得出，沒有實際跑出來。
引句:「adds a line to the local check log」

## F4 reference.md 說沒登記進 features 的 flow「整套驗收也不跑」，這句不實
severity: minor
blocking: 否
file: `skills/lumos-project-notes/reference.md`（完成判準第一條）；對照 `scripts/templates/android-e2e-run.sh` 的 `flows_to_run`
失敗場景：整套跑用的是 `e2e.flows` 整個清單，不經過 `features`。同一條前一句已要求把 flow 加進 `e2e.flows`，所以只要這樣做，整套跑一定會跑到它。README 寫的「整套跑照樣會驗到」才符合程式。AI 照 reference 的字面會以為每支 flow 都必須登記進某個 case，才能被整套驗收涵蓋，於是為了湊數亂建 case。
引句:「挑不到、整套驗收也不跑」

## F5 手冊教「單獨重判」，但對按功能跑的目錄這條指令會被拒
severity: minor
blocking: 否
file: `skills/lumos-project-notes/commands/04-自檢與健康.md`；`scripts/lumos:41080`（`_e2e_judge_selected`）
失敗場景：按功能跑的 `steps.json` 帶 `selection` 欄。AI 照手冊對那個目錄跑 `lumos android-e2e judge <結果目錄>`，會得到「這次是按功能跑…要留紀錄請整套跑」並回 2。要重判只能加 `--no-record`，這在手冊、README、skill 都沒提。另外 `reference.md` 的子命令全覽只列 `android-e2e` judge，沒有新增的 `history`、`select`，AI 查目錄時找不到。
引句:「判讀單獨重跑是 `lumos android-e2e judge <結果目錄>`」

## F6 skill 的「新增功能要補的東西」少了兩個會讓 check-config 擋下的地方
severity: minor
blocking: 否
file: `skills/lumos-android-evidence/SKILL.md`（新增功能或使用情境時一起補）；`scripts/lumos:40374`（`_e2e_scenarios_err`）、`scripts/lumos:40405`（`_e2e_case_err`）
失敗場景：
- 補記憶體情境時，skill 只說「`stability_scenarios` 裡的情境名」。README 與 skill 都沒寫 `stability_scenarios.<名>` 必須有 `scenario` 與 `driver`，也沒寫門檻檔要有 `scenario` 值（不是 key 名）對得上的條目。`scenario` 與 `driver` 只寫在收集腳本的筆記裡。
- 補截圖時，skill 只說「`visual`（有基準圖的畫面）」。程式要求那個畫面同時在 `e2e.visual` 清單裡，否則 check-config 擋下；skill 第 1 步只提到 `e2e.flows`。
- 使用前提沒講：專案有 `e2e` 段但還沒有 `features` 時，`--changed`、`--feature`、`--case` 一律回 2「e2e 段沒有 features」。skill 只描述「對不到任何功能」這一種 rc 2。
- skill 與手冊說「略過效能或記憶體就標不完整」，其實只有該情境本來有那一塊才標，措辭過頭。
- 以上都會被 check-config 的訊息帶回來，AI 多繞一圈就能修好，不會做出危險操作。
引句:「`stability`(`stability_scenarios` 裡的情境名)」

## F7 skill 把 `--changed` 回 2 只當成「補對照表」，沒講它比的是跟主線分岔點的差異
severity: minor
blocking: 否
file: `skills/lumos-android-evidence/SKILL.md`；`scripts/lumos:40804`（`_e2e_changed_files`）
失敗場景：README 與 skill 都寫「提交後再跑」。若 AI 直接在主線上提交後跑 `--changed`，HEAD 就是分岔點，沒有差異，結果回 2「（沒有改動）」。這時 skill 叫 AI 去補 `paths`，其實問題在另一頭。另外 README 說「改到的檔不在任何功能裡會被列出」，程式只列落在 `app_dirs` 裡卻對不到功能的檔，文件或設定檔不會列。
引句:「改到的檔不在 `e2e.features` 任何功能的 `paths` 裡」

## F8 計劃條款 S23、S25 的行為，綁定的測試沒有驗到
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md`（S23、S25、S22）；`scripts/test_lumos.py:19096`（`t_android_e2e_by_feature`）、`scripts/test_lumos.py:19182`（`t_android_e2e_history`）
失敗場景：
- S23 寫「`--no-memory` 時不跑那兩塊，也不查那兩塊要的工具」。整份測試裡沒有 `--no-memory`，也沒有「不查 Perfetto 工具」的斷言（`grep -n "no-memory" scripts/test_lumos.py` 無命中）。把 `stab_to_run` 改成不看 `SEL`，測試照綠。
- S23 說用「HEAD 加工作目錄改動」對分岔點的差異挑功能，測試只用工作目錄的未提交改動，沒有「已提交、與主線分岔」的情境。
- S25 的 `--last`、被中斷、沒判完都沒測。
- S22 的「沒判完時回 1」沒測。
- 其餘的 S24、S26、S27 對得上對應測試。
引句:「時不跑那兩塊,也不查那兩塊要的工具」

## F9 計劃的審計修正紀錄與圖的說明文字有小處對不上
severity: minor
blocking: 否
file: 計劃〈審計修正紀錄〉；`assets/readme-diagrams/generate.py` 的 `desc`
失敗場景：
- 計劃寫「改寫成…S22–S26」，但條款實際到 S27，條款範圍前後不一致。
- 圖的英文版 `desc` 說預檢查「working tree is clean」，沒有「整套才要」的限定。圖內文字已改為「whole app: clean tree」，兩處不一致。
- 英文圖的「By feature: committed runs count too」，容易被讀成會算進推送前檢查。README 與 skill 明說推送前檢查還不會擋，中文版是「也記進這一版紀錄」，意思不同。
- `python3 assets/readme-diagrams/generate.py --check` 在副本跑過：26 張圖驗證通過、可重現。
引句:「Whole app: commit the record, push」

## 圖譜鏡頭
- 固定席 INVARIANT 的節點：`lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`bound-tests-gate`。這份文件包沒有改它們宣稱的行為。`bound-tests-gate` 只牽連到 `generate.py`，沒有破壞。
- 新增的 WHY 行：`android-e2e-acceptance`（3 行）、`android-stability-collector`（1 行）、`README圖產生器`（1 行）、計劃（2 行）。出處、因、test 欄位都齊，內容與程式一致，且綁定的測試都存在。
- 新的子指令 `android-e2e select`、`history` 已補進 HELP_WHEN，`t_every_subcommand_has_when` 通過。
- 例外：筆記 PITFALL 提過「指令總數」要跟著改，但 `reference.md` 的子命令全覽沒列 `select`、`history`（見 F5）。
- 計劃狀態句寫著「已實作在 EnzoHsieh-Android/e2e-only 分支」，屬於過程紀錄，不該留在筆記裡，且分支名可能已過期。

文件包主要問題是指令手冊與程式、README、skill 對「按功能跑是否寫查證紀錄」說法相反（F1），其餘多為措辭精度與測試未涵蓋，圖產生器 `--check` 通過。
