severity: minor

## F1 README 與 skill 寫「完整的結果不會被不完整的蓋掉」，程式其實是這次沒過一律蓋掉
severity: minor
blocking: 否
file: `README.md:388`（英文版同一段 `README.en.md:388`）、`skills/lumos-android-evidence/SKILL.md`〈端到端驗收〉表格第二列；對照 file: `scripts/lumos:41042`（`_e2e_keep_old`）
失敗場景：同一版已經有一筆完整的通過，AI 照表格第二列用 `--no-perf` 再跑一次，結果沒過。照 README 和 skill 的說法，AI 會以為這版紀錄還保留著那筆完整的通過，可以拿去推送前檢查。實際上程式會用這次的沒過蓋掉它。另外還有一條文件沒寫的規則：重判比既有那筆更早結束的 run 也不會蓋掉。計劃 S27 寫得對，三份文件說法不一樣。
引句:「同一版已有完整的結果不會被不完整的蓋掉」
歸因：有證據的原有漏查。修前（4b056532）和修後（7988107c）的 README 第 388 行文字一樣，`_e2e_keep_old` 也一樣，都有 `if new["result"] == "fail": return False`。兩版各跑 `python3.14 scripts/test_lumos.py -k feature_record_rules`：修前 9 過 0 紅，修後 15 過 0 紅。兩版測試檔都有「這次沒過一律蓋掉先前的通過(就算不完整)」這個檢查而且是綠的，可見程式就是會蓋掉，跟文件說的相反。

## F2 計劃〈查證紀錄長怎樣〉的 runs 與 history 欄沒跟上按功能跑，RETIRE-IF 的數法會被灌水
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:110-111`（RETIRE-IF 在第 26 行）；對照 file: `scripts/lumos:41080`
失敗場景：程式現在會在按功能跑時，往紀錄的 `history` 加一筆 `{"kind":"feature","cases":[…],"result":"pass",…}`，這時 `runs` 還是 null。計劃第 110 行仍寫 runs「每一次 judge 覆蓋這一欄」，第 111 行仍寫 history 每筆只有 result、run-id、結束時間；整段也沒提到 `feature_runs`。第 26 行的 RETIRE-IF 要從這裡數「歷次結果裡有過 pass 的指紋數」。照計劃去數的人（或寫第二批推送檢查的人）會把「只跑過一個情境的通過」算成那個指紋驗過，分母變大，降級條件就更不容易成立。
引句:「每次 judge 追加一筆(result、run-id、結束時間),只增不刪;RETIRE-IF 從這裡數。」
歸因：有證據的原有漏查。我寫了一支小探針，載入各版的 test_lumos 輔助函式，在乾淨的工作目錄跑 `--case login.ok`，兩版結果一樣：`rc 0 runs None history [{'kind': 'feature', 'cases': ['login.ok'], 'result': 'pass', …}]`。版本用 `git -C <clone> rev-parse --short HEAD` 確認是 4b056532 和 7988107c。

## F3 按功能跑的回傳碼和「通過」的說法漏了幾種情況
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Systems/android-e2e-acceptance.md`〈回傳碼〉、`skills/lumos-project-notes/commands/04-自檢與健康.md` 的 Android 那一列、`README.md`／`README.en.md`〈結果怎麼讀〉的「通過」那條；對照 file: `scripts/templates/android-e2e-run.sh:552`
失敗場景：
- 按功能跑被 INT、TERM 或 HUP 中斷時，腳本會回 2（`return 2 if st.data["interrupted"] else rc`）；steps.json 讀不懂時也回 2。筆記和手冊只寫了「2=挑不到或設定不合格」，AI 自動化收到 2 會去改對照表，修錯方向。
- README 的「通過：紀錄寫好了，提交它再推送」沒有區分跑法。按功能跑、開跑時有沒提交的改動時，回 0 但沒寫紀錄（測試 t_android_e2e_by_feature 的「工作目錄有改動時按功能跑不寫查證紀錄」檢查在兩版都是綠的），照這條做的人會找不到紀錄檔可以提交。
引句:「按功能跑是 0=挑到的都過、1=有沒過或沒判完(一個會判的項目都沒有也算)、2=挑不到或設定不合格」
歸因：有證據的原有漏查。修前修後的筆記都有這一行（grep 計數修前是 1），腳本第 552 行兩版相同；`-k t_android_e2e_by_feature` 兩版都是 22 過 0 紅。

## F4 S26 的條文跟綁定的測試對不上
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:265`（S26）、`scripts/test_lumos.py` 的 t_android_e2e_args_and_names
失敗場景：
- S26 點名 `/./` 不合格，但綁定的測試只測了 `//`、`.`、反斜線、萬用字元，沒有 `/./`。程式確實會擋（探針用 `app/./src` 跑 check-config，兩版都回 2），但把那段檢查拿掉，S26 的綁定測試也不會紅。
- 這次修補（40036673）在程式和測試裡新增了「反斜線與萬用字元也擋」，S26 的文字卻沒加上。照 S26 理解規則的人，會以為 `app/*.kt` 合格。
引句:「for desc, paths, cmd, word in (("paths 有 //", ["app//src"], None, "正規"), ("paths 只寫 .", ["."], None, "根本身"),」
歸因：分兩部分。
- 「`/./` 沒測到」：有證據的原有漏查。兩版測試檔用 grep 找 `app/./`，計數都是 0。
- 「S26 沒列反斜線與萬用字元」：有證據的修復回歸（文件落後）。這兩項是 4b056532 之後才加進程式與測試的，而 S26 那一行在修前修後的差異裡沒有變。

## F5 計劃把 stability_scenarios 講成在 stability 段裡面
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md`〈按功能與使用情境跑〉的記憶體那條
失敗場景：計劃寫「`stability` 段改成可以有多個情境(`stability_scenarios`…)」，但 README、skill 和程式都是把它放在最外層。照計劃把它塞進 `stability` 段的人，check-config 會回 2：「features.login.cases.ok.stability 的 player 不在 stability_scenarios 裡」（修後探針實測）。所以不會靜默放過，只是這句跟其他文件互相矛盾。
引句:「段改成可以有多個情境(」
歸因：未判定。這一行修前修後都有；擋下的探針只在修後跑過。

## F6 「終端最後那一行」兩處講的不是同一行
severity: minor
blocking: 否
file: 計劃〈檢測紀錄〉最後一條、`Systems/android-e2e-acceptance.md`〈回傳碼〉；對照 file: `scripts/lumos:41001-41002`
失敗場景：計劃說終端最後是照情境各列一行；筆記說要看有沒有寫進紀錄，就看「終端最後那行」。程式印完情境行之後，`_e2e_feature_record` 還會再印一行（「按功能的結果寫進查證紀錄…」或「這次只記進本機檢測總表…」）。所以計劃的說法不對，兩處自相矛盾。
引句:「終端最後照情境各列一行」
歸因：未判定。修補只改了這一行的範例內容，「最後」這個說法修前就有。這條我沒有另跑修前修後的對照。

## 圖譜鏡頭
- 這次沒有附固定席節點（LUMOS-LENS 寫明了），所以沒有固定席要逐條答。
- 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/08273ea6…json.warming` 不存在，沒有東西要處理。
- 這次牽連到四篇筆記：Systems/android-e2e-acceptance、Systems/android-stability-collector、Systems/README圖產生器、Projects/Android端到端驗收_計劃。在修後副本各跑 `lumos lint` 都是 0 問題。
- 新增的 WHY、PITFALL 行都有出處、因或根因，PITFALL 也都有 test。指到的測試名在修後測試檔裡都各有恰好一個定義，測試執行器會自動收所有 `t_` 開頭的函式。
- 我逐條對過的筆記內容：
  - 「捷徑」那條 PITFALL 寫的修法，跟 `_e2e_record_update` 檢查 `.lumos`、紀錄目錄、紀錄檔三處是不是捷徑一致。
  - collector 那條 WHY 說能蓋過的欄位跟 `E2E_SCENARIO_KEYS` 一樣：收集腳本第 130 行就是同一組四個欄位。
  - 效能方法名不收 `$` 的 WHY，跟 `E2E_BENCH_NAME_RE` 和範本腳本的同一條規則一致。

## 三問
1. **原問題修好的行為證據**：只驗了跟文件有關的捷徑那條。修後跑 `-k t_android_e2e_run_edges` 是 7 過 0 紅。修前（4b056532 換上修後的測試檔）是 0 過 2 紅，但在替身收集腳本那一格就先因為例外中斷，根本沒跑到捷徑那一段。所以「修前捷徑會寫到專案外」我判為未判定，binding 說是在 40036673 上紅的，我沒有重現。
2. **正常路徑還成立的證據**：
   - `generate.py --check` 修前修後都回 0（26 張圖都通過驗證、可重現）。
   - `-k t_android_e2e_by_feature` 兩版都是 22 過；`-k feature_record_rules` 修前 9 過、修後 15 過。
   - 文件裡這些說法我都逐一對過程式，對得上：參數名、`--changed` 對不到時回 2 並印改到的檔（沒改動時印「(沒有改動)」）、`{{TEST}}` 的換法、方法名規則、`stability_scenarios` 的欄位與 1 到 10000 的範圍、門檻條目要按情境、`--preflight` 帶挑法時不要求乾淨、`history` 的 `--feature`／`--case`／`--last`、總表路徑。
3. **新發現在修前修後各是什麼結果**：見每條的歸因。F1、F2、F3 兩版結果相同；F4 的前半兩版都沒測到，後半是修補後文件落後；F5、F6 未判定。

**沒驗的範圍**：真機實跑、整套 `test_lumos.py`、截圖的視覺檢查（只跑了 `--check`）。臨時目錄和測試留下的 gctl-run 現場都已經用字面絕對路徑刪掉了。

這一包導引大致跟程式對得上，照著做不會做出擋下推送的錯操作；要改的是 README 與 skill 的覆蓋規則、計劃的紀錄格式段落與 S26 條文、按功能跑的回傳碼說明這幾處跟程式不一致的地方。
