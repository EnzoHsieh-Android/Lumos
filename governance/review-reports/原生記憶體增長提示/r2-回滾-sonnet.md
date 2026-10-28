severity: major

我只讀了 spec 和對照的程式碼,沒有改檔,也沒有在 `/tmp` 另開實驗目錄,不需要清暫存。回滾這條線的結論是:〈回退〉節只寫了「拿掉」,沒寫「拿掉之後留下什麼、誰讀到舊或新形狀」。下面 F1 到 F4 是 major,F5 到 F8 是 minor。

## 逐節

- 檔頭 frontmatter 與 d1 到 d4:已讀,無 finding。
- 實驗室實測節:已讀,無 finding。
- 〈判法〉:已讀,無 finding。
- 〈打算怎麼做〉第 1 到 7 步:見 F1 到 F4、F6、F8。
- 〈跟舊否決的差別〉:已讀,無 finding。
- 〈實務隱患〉:「已排除:不可逆」見 F5,「已排除:對外送出」見 F6,「金流(不排除)」本身站得住,但與 F5 矛盾。
- 條款 S1 到 S11:S4、S8 的覆蓋範圍見 F3,S9 見 F2。
- 〈回退〉:見 F1、F2、F7。

`start_record`、`stop_record` 改簽名這件事,我查完沒發現不一致,理由有三:

- 兩個函式只在 `scripts/templates/android-stability-collect.sh` 內部被呼叫,`scripts/test_lumos.py` 沒有直接引用這兩個名字。
- 改簽名和回退是同一支檔、同一次 `git revert`,不會有舊簽名配新呼叫端的狀況。
- 第二段共用 `state["rec"]` 這個槽,而第一段在 `del state["rec"]` 之後才開第二段(收集腳本同一函式內),槽不會被兩段同時佔用。

## Findings

### F1 回退建議「請各專案刪掉 native_growth 鍵」會讓每個專案、每條分支整套重跑
severity: major
blocking: 是
引句:「要清乾淨就請各專案刪掉那個鍵」
file: `scripts/lumos:39542`(`_macrobench_stab_cfg_err`)、`scripts/lumos:41490`(`_e2e_mem_canon`)、`scripts/lumos:41567`(`_e2e_gate_need`)、`scripts/lumos:40747`

1. 舊版 lumos「不驗 stability 段未知鍵」這句宣稱屬實。
   - `_macrobench_stab_cfg_err` 與 `_macrobench_stab_optional_err` 只檢查已知鍵,沒有 extra-key 檢查。
   - `--check-config` 走 `_macrobench_stab_top_err`,同樣沒擋。
   - 收集腳本的 `load_config` 只取 `st` 裡認得的鍵。
   - 只有 `stability_scenarios` 才擋未知欄位(`scripts/lumos:40493`),spec 避開它是對的。
2. 問題在 e2e 的記憶體設定指紋。
   - `_e2e_mem_canon` 與 `_e2e_fingerprint` 都把整個 `stability` dict 做 `json.dumps` 後取雜湊,所以 `native_growth` 在指紋裡。
   - 回退後專案若保留該鍵,指紋不變,這條路是通的。
3. 照 spec 建議去刪鍵,會出事。
   - 指紋再變一次,`_e2e_gate_need` 回 `"full"`,原因是「記憶體設定(stability 段或 stability_scenarios)跟分岔點不一樣」。
   - 結果是推送前閘要求每條分支在實機上重跑整套。
   - 〈實務隱患〉的「遷移」那條只寫了「加鍵要重跑」,〈回退〉沒寫「刪鍵也要重跑」。
4. 應改成:回退時預設「留著那個鍵、舊版會忽略」,刪鍵要明寫「會讓所有分支整套重跑」並列為可選的最後一步。

### F2 舊新版本錯配時「沒有」與「沒跑」分不開,提示一路靜默
severity: major
blocking: 是
引句:「結果檔沒有這段(舊收集腳本)時不印」
file: `scripts/templates/android-stability-collect.sh:118`、`scripts/lumos:40255`(`_macrobench_without_results`)、`docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:39`

四種組合照程式碼推演如下。

| 收集腳本 | lumos | 結果 |
|---|---|---|
| 舊 | 舊 | 無提示,屬預期 |
| 舊 | 新 | `--check-config` 通過;結果檔沒有 `native_growth`,按 S9 不印,使用者已打開該情境卻看不到任何東西 |
| 新 | 舊 | 收集腳本的 `--check-config` 通過(舊 lumos 不擋未知鍵),照樣多跑一整段 W+N 輪驅動(含 F5 的副作用)並留下 `heap-native.pftrace`,但舊 lumos 完全不讀,純成本 |
| 新 | 新 | 見下 |

新配新時有三個洞,舊配舊的靜默只是預期。

1. 收集腳本寫的 `failed` 與 `unsupported`(例如「沒錄到原生配置記帳」「沒宣告測試資料」)只留在 `stability.json`。
   - 第 6 步只把分類後的呼叫位置放進固定鍵,`failed` 與 `unsupported` 的原因沒有地方輸出。
   - 使用者打開了情境、錄失敗,看到的和「沒增長」一樣,都是空清單。
   - 這正是 r1 說要解掉的「錄不到被當沒事」,折完又在 lumos 輸出端漏掉。
2. skill 與 lumos 走不同的發佈管道,在多專案環境「skill 新、某專案 lumos 舊」是常態,不是例外。
   - skill 的 L0 條件和 L3 順序要讀 `--json` 的 `native_growth`。
   - 舊 lumos 的輸出沒有這個鍵,macrobench-adapter 筆記第 39 行明寫過「讀取端不用判斷鍵在不在」這個合約。
   - skill 若把缺鍵當空清單,會「先看提示」,於是跳過原本會手動錄的 L3 原生診斷。
3. 〈回退〉只講「新版 lumos 讀到沒有這段的結果檔不印」,沒講 skill 讀到缺鍵時該怎麼辦。

應補三件事:`native_growth` 要帶每個情境的 status(打開了但 failed 或 unsupported 時印原因),skill 要明寫「鍵不存在 = lumos 太舊,不可當作零筆」,〈回退〉要列出上表。

### F3 第二段中途崩潰、被中斷、或拖到 e2e 逾時,會丟掉已經量好的第一段結果
severity: major
blocking: 是
引句:「所以既有判定不受第二段影響」
file: `scripts/templates/android-stability-collect.sh:546`(`main`)、`scripts/templates/android-stability-collect.sh:556`、`scripts/templates/android-e2e-run.sh:477`

1. 結果檔只在 `measure()` 整個回傳之後才寫出。
   - 被中斷時印「沒寫結果檔」;
   - 其他例外是 `cleanup` 之後 `raise`,同樣沒有結果檔。
2. 第二段排在 `measure` 內、第一段之後,所以第二段發生這兩類事件時,剛量好的第一段整份丟掉:
   - 中斷:Ctrl-C、SIGHUP、e2e 逾時殺掉;
   - 新程式碼的意外例外:csv 解析函式簽名、查詢結果欄位缺失等。
3. 這和 d2「永遠只提醒、不影響判定」及「已排除:守衛面」互相打架。
   - 條款 S4 只驗「第二段期間 App 結束」,S8 只驗裝置端設定檔與錄檔被收掉,都沒有驗「第一段結果仍然寫出」。
   - e2e 的記憶體塊會因此變成 unjudged,推送前被擋。
4. e2e 逾時也是同一條路。
   - `android-e2e-run.sh:411` 的 `step` 預設 `timeout=T_LONG`,預設 3600 秒。
   - 第二段把驅動時間約再加 W+N 輪,逾時就回 None,`:477` 的處理是「剩下的情境與效能這次都不跑」。
5. 中斷在 heapprofd 取樣中發生時,cleanup 只停錄製和刪暫存,不會 `force-stop` App。App 行程仍掛著 malloc hook(變慢),而 spec 自己也說「同一行程已有別的 heapprofd 工作階段」會錄不到。
6. 應改成:
   - 第二段整段包 try/except 降級成 `failed`;
   - 第一段結果在開第二段之前先落檔(或至少保證例外時仍寫出);
   - 補一條 S 條款驗證「第二段被中斷或崩潰時,第一段結果檔照寫」;
   - 〈回退〉補一句「中斷路徑要連 `force-stop` App 一起收」。

### F4 照 low_iterations 的形狀實作,只有 stability 的專案文字輸出不會印提示
severity: major
blocking: 是
引句:「沒東西時是空清單,文字與 `--json` 都有」
file: `scripts/lumos:39832`、`scripts/lumos:40255`(`_macrobench_without_results`)、`scripts/lumos:40312`

1. `low_iterations` 只在有結果目錄的路徑被填入並印出(`_macrobench_print` 與 `_macrobench_mode` 中段)。
2. 只做 stability 的專案(`only_other` 路徑,`results_dirs` 不填,e2e 驗收用的就是這類)走 `_macrobench_without_results`,文字輸出只印 `_macrobench_print_thresholds`,完全不印 `low_iterations`。
3. 照 spec 字面「照 `low_iterations` 的形狀」複製,`--json` 有鍵,但這類專案的文字輸出沒有提示。
4. 這也是 `native_growth` 最主要的使用者群,所以提示會在主要情境下印不出來。
5. 應明寫兩條輸出路徑都要印,並補一條涵蓋「無 results_dirs」文字輸出的 S 條款。

### F5 「已排除:不可逆」和同節「金流(不排除)」互相矛盾,回退也撤不掉副作用
severity: minor
blocking: 否
引句:「只寫被 git 忽略的 run 目錄、結果檔與測試裝置的暫存」

1. 〈實務隱患〉自己寫第二段會在測試後端多下 W+N 次單,這就是回退撤不掉的不可逆副作用。
2. 同一節又以「只寫被 git 忽略的檔」為由把「不可逆」標成已排除,分類和內文矛盾。
3. 這個理由只對「檔案」成立,對「後端資料」不成立。
4. 〈回退〉也沒有一句「已多下的單、已改的測試帳號資料不會因回退而還原」。
5. 應把「不可逆」改成不排除,理由寫成「後端副作用同金流條」,並在〈回退〉補這句。

### F6 新增檔名一律加進 ARTIFACTS,連沒打開 native_growth 的專案升級後也可能被擋下
severity: minor
blocking: 否
引句:「兩個都加進 ARTIFACTS」
file: `scripts/templates/android-stability-collect.sh:398`

1. `preflight` 的 `loose` 檢查對 `ARTIFACTS` 每個檔名各問一次 `git check-ignore`,對所有專案、所有執行一律生效。
2. 「已排除:對外送出」寫的 `.gitignore` 保護前提是專案忽略了 `.lumos/artifacts/`。
   - 筆記明記了 r2 資安席抓到的情境:`.gitignore` 若只寫個別檔名或 `*.json`,快照照樣進版控,所以才改成逐檔名檢查。
   - 這類專案升級後,`heap-native.pftrace` 與 `record-native.pbtxt` 沒被忽略,收集腳本會直接回 2 擋下,和預設關的承諾衝突。
3. 這道檢查本身是好的,但對沒打開的專案不應生效。
4. 應改成只在該情境真的打開時才把兩個新檔名加進檢查清單,或在升級說明裡寫明。

### F7 退回時消費專案和裝置上都會留下殘檔,〈回退〉沒列
severity: minor
blocking: 否
引句:「拿掉第二段、`android-stability-heapprofd.pbtxt` 與 ARTIFACTS 那兩項」
file: `scripts/lumos:32254`、`scripts/lumos:31959`、`skills/lumos-android-evidence/reference.md:120`

1. `lumos update` 只做「來源有、專案沒有或內容不同就複製」(`_vendored_pending`),不會刪除來源已經不存在的檔。
2. 退回後,消費專案的 `scripts/templates/android-stability-heapprofd.pbtxt` 永遠留著,而且它已不在 `_VENDORED_ALL`。依 `scripts/lumos:32854` 的設計,風險掃描會當作專案自己的程式。
3. 〈回退〉的「裝置上」那條叫人去查 `lumos-stability-*-native.*`,但 `reference.md:120` 現行寫的是「收集腳本只清自己的 `lumos-stability-<run-id>.*`」,`-native` 後綴不被這個說法涵蓋。
4. 回退時 `reference.md` 一起還原,那句查殘留的指引也跟著消失;舊收集腳本的 `abort_record` 也不認識這個名字。
5. 應在〈回退〉補:提供一道手動刪消費專案範本檔的指令,裝置殘留的確切刪除指令(字面絕對路徑),並說明舊版不會自動清它。

### F8 「default」是保留字,但現行的情境名規則允許同名的 stability_scenarios 鍵
severity: minor
blocking: 否
引句:「代表沒指定情境的那一段(沒設 LUMOS_STABILITY_SCENARIO)」
file: `scripts/lumos:40483`(`_e2e_scenarios_err`)

1. `_e2e_scenarios_err` 的名字規則是 `[A-Za-z0-9_-]+`,`default` 合法。
2. 專案真有一個叫 `default` 的情境時,`native_growth` 裡的 `"default"` 同時指兩件事。
3. 第 1 步要求 lumos 驗「名字要在 `stability_scenarios` 裡」,但沒有說撞名時怎麼辦。
4. 應補:`stability_scenarios` 不准用 `default` 這個名字(新舊版行為要一致,舊版沒有此限制,所以只能加在新鍵的檢查上),或改用不會撞名的保留字。

## 固定席逐篇判

- `Systems/android-stability-collector.md`:會被影響,要同步修改。
  - 合約「開跑前對每一種會寫出的檔名各問一次 git check-ignore」會被 F6 的無條件加入改變。
  - 「收到 SIGTERM … 最後才停裝置上的錄製」「日誌串流與錄製先從待收清單拿掉才開始停」這兩條,在第二段共用 `state["rec"]` 槽時都不被破壞。
  - 「同一個 run-id 已有結果檔回 2」與第二段無關。
  - `about_code` 要加新範本檔;第二段中斷的資料遺失見 F3。
- `Systems/macrobenchmark-adapter.md`:會被影響。「固定鍵一開始就放好、讀取端不用判斷鍵在不在」的合約要遵守,所以 F2 的缺鍵語意要先定義。「只提醒不擋」「回傳碼」沒被破壞,輸出路徑見 F4。
- `Systems/android-e2e-acceptance.md`:會被影響,是 F1 與 F3 的來源。
  - 指紋合約(記憶體設定另算一段雜湊接進去)本身沒被破壞,只是加鍵、刪鍵都會觸發整套重跑。
  - `steps.json`、`stability_judge` 的消費端 `_e2e_judge_stability` 只取已知鍵,加一個鍵不影響;`_e2e_load_json` 限深 20 層,`native_growth` 約 4 層,夠用。
  - e2e 逾時沒被評估,見 F3。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:不破壞宣稱的行為。
  - 它的 S27(結果檔欄位對得上)新增 `native_growth` 段不改既有欄位。
  - 「Native Heap 前後兩個數字只回報」那句需要在實作後同步,spec 第 7 步已列。
  - 「否決只看 Native Heap 趨勢」的區分已寫在〈跟舊否決的差別〉。
- `Projects/Android逐層診斷_計劃.md`:不破壞。d4 已按「不每次都錄」把否決理由守住,「記憶體 check 沒過時從 L0 直達 L3」的例外不受影響。

總結:整份最高嚴重度為 major,blocking 共 4 條。
