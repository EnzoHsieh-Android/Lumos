severity: major

固定席節點:這次派工詞尾端沒有附任何固定席節點(我只看到派工詞和共用說明),所以沒有可逐條判的項目。

實驗放在 `/tmp/lumos-seat-work/改動與修補拆小/可執行性-sonnet-r2/`:一份 `--shared` clone,加幾支試算腳本。我用真實的 253 份 `code-*` 卷證試算:`snapshot_path` 全是相對路徑、沒有指到 repo 外,只有 `code-寫法規範/r1` 一份檔不在。對這份計劃,我找到兩條 blocking 和七條非 blocking。

### Findings

引句:「逐檔比較——這份 patch 每支檔的新增行,扣掉上一輪凍結 patch 同一支檔已有的同內容行」
severity: major
blocking: 是
1. 第 N 輪「這份 patch」是哪一份沒定義,照字面會印出誤導的數字,或在不該印的階段印。
   - 實測(clone 裡的 `code-合約測試閘並行`,帳上已有 r1、r2)有三種呼叫:
     - 帶新凍結的 r3 patch:phase 是 `plant-canary`,計劃的假設成立。
     - 帶 r2 patch(`gate-pending` 補完的指令、`loop status --disposal` 慣用的就是這種):phase 變 `converged`,輸出寫「這個編號沒有下一輪了」。
     - 帶 r1 patch:phase 仍是 `plant-canary`。
   - 帶 r2 patch 時,「上一輪」(帳上第 N-1 輪)的 `snapshot_path` 就是同一份檔,差集必為 0,會印「上一輪修補新增約 0 行」。
   - 計劃沒有規定:
     - 只在 `plant-canary` 印,`converged`、`cap-reached`、`gate-pending` 不印。
     - `--spec` 的 sha 等於帳上最後一輪的 `snapshot_path` sha 時不印。
   - 另外,SKILL.md 只教首輪帶 `--spec`;續輪該帶哪一份,計劃和手冊都沒講。
   - 應該是:明寫「只在 `plant-canary` 且 `--spec` 不是帳上已審過的那份時印」,並在 S3 加一條對應測試。

引句:「程式加測試超過 100 行時,再印一行」
severity: major
blocking: 是
2. 提示拿「程式加測試」去對一組不是用這個量算出來的百分比。
   - 回放腳本(`patch_lines`、difflib)算的是所有非簿記檔的 `+` 行,筆記也算,而且是整份 patch 的序列比對。計劃改成逐檔、多重集合相減,並排除筆記。
   - 304 對真實續輪的試算結果:
     - 259 對的數字不同。
     - 有 10 輪回放口徑超過 100,但計劃口徑不超過。
     - `code-ablation-probe` r3:回放 242,計劃 58。
   - 提示文字引用的「47 行以下約三成、226 行以上約八成」,在計劃量的這個量上沒有被量過。
   - 應該是:二選一。
     - 量法跟回放一致:含筆記、整份序列比對。
     - 或用計劃的量法重跑回放,換掉數字和門檻再寫進提示。
   - 首輪的「300 行附近四成對三分之二」我用 code+test 重算過,成立:112 個 ≤300 的迴圈跑滿比例 43%,93 個 >300 的 65%。
   - 但首輪 code+test 中位數是 256,有 110/248 個首輪超過 300,提示會常常響。

引句:「帳上第 N-1 輪有任一筆帶」
severity: minor
blocking: 否
3. 「任一筆」會選到錯的檔。
   - 有 19 個「輪」帶多份不同的 `snapshot_path`,例如 `code-delguard` 每席各一份 `r1-s1` 到 `r1-s5`。
   - 照字面取任一份,可能取到某個席的分片。
   - 另外 36 筆舊帳的 `round` 是 None(循序、不帶輪次),計劃沒說怎麼辦。
   - 應該是:取該輪 `snapshot_path` 去重後可解析的最後一份。多份且內容不同、或 `round` 為 None 時,明寫「不印」。

引句:「檔案讀不到、上一輪沒有凍結 patch」
severity: minor
blocking: 否
4. 路徑解析沒說清楚。
   - 帳上路徑是相對 repo 根(`prov_path`、`reviewed_spec` 都是 `_root / sp`),`--spec` 是照 cwd 讀。
   - 我實測過從 `governance/` 和 `docs/` 帶 `--spec` 都能跑。
   - 實作若直接 `open(snapshot_path)` 會在子目錄讀不到,然後靜默不印。
   - 應該是:帳上路徑用 `--repo` 或 `_vault_repo_root(env)` 解析,`--spec` 照 cwd。
   - 圖譜資料夾的相對路徑取法:`env.vault.relative_to(_vault_repo_root(env))`。

引句:「每支檔先看是不是簿記」
severity: minor
blocking: 否
5. 「其餘算程式」會把資料檔當程式算。
   - 我對 248 個首輪 patch 用計劃的分類算過:`.txt` 累計 14.5 萬行、`.json` 2.6 萬行,進了「程式」格。
   - 大宗是 `governance/eval/results/...`,單一目錄就有 8980 行,不在 `_BOOKKEEPING_DIRS`。
   - 這類 fixture 和輸出會讓「超過 300 行」誤響。有 8 個首輪因此超標。
   - 應該是:把 `governance/eval/` 之類生成物排除,或明說這是已知誤差。
   - `_nodehome_is_test` 用預設 layout 即可,沒有昂貴掃描。但消費專案的 Xcode `Tests/`、`androidTest` 會被算成程式,可寫成已知限制。

引句:「給了一個 dict 時,在既有的檔頭狀態機裡,把 hunk 內以」
severity: minor
blocking: 否
6. 狀態機的實作細節計劃沒寫,可以直接補進〈做法〉。
   - 檔名要到 `_flush` 才定案(`plus`、`rename`、`minus`、`hdr` 的優先序),但 `+` 行是在 hunk 內收集的。
   - 實作要先暫存在 `cur["added"]`,`_flush` 時才依最終 name 寫進 `added_out`。
   - 同名檔出現兩段(`files[name]` 目前是覆寫)時,`added_out` 該覆寫還是累加沒有規定。
   - 預設的 `splitlines()` 會在 `\x0c` 之類字元處切行。我對 570 份真實 patch 比過,`+` 行數沒有差異,但行內容會被截短。計數時建議明寫 `lf_only` 取向。
   - `\ No newline`、二進位、刪檔、改名:這套狀態機都不會讓它們混進 `+` 行。`in_hunk` 只在下一個 `diff --git` 才結束,所以 S4 的 `+++` 內容行成立。
   - 61MB、一百萬行的最大 patch 解析 0.6 秒,沒有效能問題。

引句:「回傳 應 與改動前逐位元相同」
severity: minor
blocking: 否
7. S6 只能對固定預期值比,沒有舊實作可對照,測試怎麼寫計劃沒說。
   - 建議用既有 `test_lumos.py` 約第 54354 行那組輸入,先釘改動前的 `files` dict,之後比對。
   - 改 `scripts/test_lumos.py` 會碰錨點檔(`ANCHOR_FILES`),要先 `anchor approve`。這點計劃沒提,屬於過程提醒。

### 已確認不成問題的假設

- `--json` 加 `change_size` 欄位:`test_lumos.py` 裡沒有用鍵集合斷言 `loop next --json` 的測試。實測現有輸出是逐步加欄位(`reviewed_spec`、`fix_check` 等)的做法。
- `_patch_file_changes` 加可選參數且預設為 None,不影響現有 5 個以上的呼叫處(`_patch_files_from_text`、資安席、回頭重讀)。
- 計劃對 `find_vault` 的描述準確。回放的總趨勢也成立:續輪 100 行以上的比例,回放口徑 154/304、計劃口徑 144/304。

最嚴重等級 major,共 2 條 blocking(#1、#2),其餘 5 條 minor(非 blocking)。
