severity: minor

審查範圍:修補鏡頭 787dd51b → 4b056532 的文件包。我在 `/tmp` 的乾淨 clone 裡各檢出修前、修後兩版。指令與環境:

- `python3.14 assets/readme-diagrams/generate.py --check`:兩版都是「26 bilingual SVGs: validated, reproducible…」。
- `python3.14 scripts/test_lumos.py -k android_e2e`:修後版 359 passed、0 failed。
- 四篇動到的筆記 `lumos lint` 全部 0 問題。

## F1 計劃寫的「終端最後一行」範例,跟程式實際印出的對不上
severity: minor
blocking: 否

- file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:228`、`scripts/lumos:40993`
- 失敗場景:
  - 照計劃範例,以為記憶體沒過時終端最後會印 `stability player:native_unreachable`,拿這串去對輸出或寫斷言。
  - 實際上 `bad = [f"{i['kind']} {i['name']}" ...]` 的項目名是情境名,只會印 `stability player`,不含 check 名。
  - 具體是哪個 check 失敗,要看上面的 `✗ 記憶體 player:exits` 那行。
- 引句:「- 終端最後照情境各列一行:「情境 player.open-close:沒過;沒過或沒判完:stability player:native_unreachable」;證據目錄看總表或 `history`。」(這行含「」,取不含「」的一段如下)
- 引句:「證據目錄看總表或 `history`。」
- 歸因:有證據的修復回歸。
  - 修前:計劃寫的是 `player.open-close:UI ✓、記憶體 ✗ native_unreachable(證據 …)`,程式 `情境 {fc}:…` 那行輸出格式相同(`scripts/lumos:40971`)。
  - 修後:文件改寫成上面這句,程式輸出沒變(`scripts/lumos:40995`),所以新寫的範例從一開始就跟程式不符。
  - 驗證方式:兩版都是讀程式碼比對;沒有另外重現終端輸出。

## F2 README「`--changed` 會列出的檔」的範圍,落後於修補後的程式
severity: minor
blocking: 否

- file: `README.md:172`(同段英文在 `README.en.md`)、`scripts/lumos:40880`
- 失敗場景:
  - README 寫「改到 App 程式目錄或流程清單裡、卻對不到任何功能的檔會列出來(文件、設定這類不列)」。
  - 修補後程式連 `.maestro` 底下任何檔、`.lumos/macrobench.json`、`.lumos/macrobench-thresholds.json` 對不到功能時也列出來。
  - 計劃 S23 寫的是「共用 flow、截圖素材、驗收設定或門檻…列出來提醒」。
  - 照 README 以為改門檻或設定檔不會被提醒,與 S23 和程式相反。
- 引句:「+- `--changed` 只認對照表裡寫了的程式路徑與情境列的流程檔；改到 App 程式目錄或流程清單裡、卻對不到任何功能的檔會列出來（文件、設定這類不列），推之前的整套跑照樣會驗到。」
- 歸因:有證據的修復回歸。
  - 修前程式只列 `all_flows` 與 `app_dirs` 的檔(`before/scripts/lumos:40866`),README 當時是對的。
  - 修後程式加了 `.maestro`、`macrobench.json`、門檻檔,README 這句沒跟著改(這句不在修補差異裡)。
  - 驗證方式:兩版都是讀程式碼比對;沒有另外重現 `--changed` 的輸出。

## F3 skill 的「先 `--preflight`」放在按功能跑的表格後面,但單獨的 `--preflight` 還要求工作目錄乾淨
severity: minor
blocking: 否

- file: `skills/lumos-android-evidence/SKILL.md:41`、`scripts/templates/android-e2e-run.sh:336`
- 失敗場景:
  - AI 在開發中(工作目錄有改動)照「先 `--preflight` 只驗裝置與工具」跑。
  - 沒帶挑法時,腳本在 `if not SELECTIVE:` 分支叫 `judge --precheck`,會以「工作目錄有沒提交的改動」回 2。
  - 要驗按功能跑的前置,得寫成 `--preflight --changed` 或 `--feature …`,但 skill 沒寫。
- 引句:「+- 先 `--preflight` 只驗裝置與工具;缺 Perfetto 工具會在動 App 之前擋。」
- 歸因:有證據的原有漏查。這句與 `scripts/templates/android-e2e-run.sh:336` 的行為在修前修後相同,README 修補前的註解「只檢查裝置、工具、工作目錄」才是準確的。
- 驗證方式:只讀程式碼,沒有實際以髒樹跑 `--preflight`。

## 已驗的正向主張
修前版 787dd51b 的檔我用 clone 的檢出逐項對過,沒有另跑修前的行為;下列主張在修後版成立:

- **參數與回傳碼**:
  - 腳本認的參數有 `--changed`、`--feature`、`--case`、`--no-perf`、`--no-memory`、`--preflight`,打錯的旗標回 2。
  - `--no-perf` 與 `--no-memory` 沒配挑法時回 2。
  - `--changed` 對不到功能時回 2,且在動 App 之前就停。
  - 按功能跑的回傳碼 0 / 1 / 2 與手冊一致。
- **紀錄寫入條件**:
  - 開跑時或判讀時髒、HEAD 換了、用了替身收集腳本,都只記本機總表。
  - 乾淨時按功能的結果寫進 `feature_runs`,整套跑才寫 `runs`。
  - `complete=false` 的條件(略過本來有的效能或記憶體、沒有會判過不過的項目)與 README、計劃、手冊一致。
  - 完整結果不被不完整的蓋掉、這次沒過一律蓋掉,與 `_e2e_keep_old` 一致。
- **效能與記憶體設定**:
  - `{{TEST}}`、方法名規則(不收 `$`、開頭不能是 `#`)、`stability_scenarios` 輪數上限 1 到 10000、`scenario` 與 `driver` 必填,都與 skill 和計劃寫的相同。
  - 整套跑只跑對照表列到的效能方法,與計劃一致。
- **指令與總表**:
  - `lumos android-e2e select / history / judge --no-record` 都存在。
  - `--last` 預設 20。
  - 擋下的那次也記進總表。
- **計劃 S22–S28 的 `[test:]`**:列到的測試函式都存在、都通過。我讀了 by_feature、changed_pick、changed_edges、args_and_names、memory_by_case、feature_record_trust、full_scenarios_judged、history 系列的斷言,各自驗了條款說的行為。
- **圖產生器**:新圖的標題與文字跟 README 一致,`--check` 通過。
- **skill 與手冊是否互相矛盾**:skill〈端到端驗收〉、`reference.md` 完成判準、`04-自檢與健康.md` 三處對 `--changed`、整套跑、紀錄去向的說法沒有互相矛盾。
- **skill 對「對不到任何功能」的處理**:skill 寫「(沒有改動) 多半是直接在主線上提交」,與程式的錯誤訊息和 `merge-base` 行為相符。

## 未驗與未判定
- **perf-only 的情境**:skill 新增情境的步驟沒寫「只列效能的情境每次都會回 1、記成沒判完」。這點只在 README、計劃、手冊有寫。沒有能當場翻紅的失敗場景,所以不列為 finding。
- **`<run-id>/stability.json` 路徑**:README 的記憶體失敗路徑說明,按功能跑時不會有 `<run-id>/stability.json`(只有 `<run-id>.<情境>/`)。文字沒寫錯,但沒特別說,屬措辭精度,未列。
- **按功能跑被中斷時的回傳碼**:程式回 2,手冊「按功能跑 2=挑不到或設定不合格」沒提。純文字精度,未列。
- **實機行為**:沒有在真機或 Maestro 上跑,只用測試裡的替身驗證。

## 圖譜鏡頭
- 本次沒有附固定席筆記(`LUMOS-LENS` 寫「這次沒附固定席節點」),我改用 `lumos impact --diff` 找出牽連節點,逐篇讀了其中 4 篇:
  - `Systems/android-e2e-acceptance`
  - `Systems/android-stability-collector`
  - `Systems/README圖產生器`
  - `Projects/Android端到端驗收_計劃`
- 這 4 篇新增的 WHY 與 PITFALL 行格式齊全(出處、因、test、根因、修法),內容與程式一致:
  - `_e2e_keep_old` 的規則
  - `--changed` 用 `ls-files --others`
  - 方法名不收 `$`
  - 搭配 `E2E_SCENARIO_KEYS` 的守衛測試
- 受影響但沒有逐篇細讀的固定席節點(INVARIANT 與守衛面那些),這份文件包沒有改動它們宣稱的行為,也沒有碰到它們的合約。
- 計劃 S8–S14(推送前檢查、放行)的測試函式在此版本不存在(例如 `t_android_e2e_gate` 查無定義)。skill 寫的「目前推送前檢查還不會擋、也沒有放行指令」與程式相符,這批沒有碰到它們。

三條都是措辭或範例與程式不符,沒有發現會讓照文件做的人做出錯操作或讓測試與推送被擋的問題。

暫存目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭4-合約與圖譜一致-sonnet` 已用字面絕對路徑刪除。
