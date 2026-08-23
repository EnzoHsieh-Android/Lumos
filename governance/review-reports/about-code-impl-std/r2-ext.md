# 外家否決席重審

## Findings

### f1 — blocker

Spec 段落：`★過期守衛` std-r1 改寫、`#4`、合約候選第 3 條。

引句:「標記當天若先改兩次 commit 才標,會被誤判過期——方向是「不加分」,安全;doctor 會列出來,人看一眼 `lumos set about_code_stamp` 就好。」

問題：這個誤判無法用 spec 所寫的方式解除。判定只保存日期與「最後改動日當天的 commit 總數」；若同一天先有兩次 commit、之後才完成標記，`n_same_day ≥ 2` 會永久成立。人重新標註並執行 `lumos set about_code_stamp`，stamp 仍是同一天，commit 計數也不變，所以讀側依然永遠不信該欄位、doctor 依然永遠報過期。更嚴重的是，目前 83 篇批次標記都使用同一天日期；只要某篇在當日標記前已有兩次 commit，功能上線當刻即可能被靜默停用。

這不是單純「方向安全」的偽陽性：它破壞了明文提供的恢復動作與合約可操作性。日期加計數無法表達標記位於同日 commit 序列的哪個位置。必須保存可比較的 commit OID／時間戳，或提供能真正清除基線的獨立狀態；單純重設同日日期不成立。

程式碼證據：

- `scripts/lumos:13564-13599` 現有 helper 只回傳 `YYYY-MM-DD`，沒有標記時 commit 邊界。
- `scripts/lumos:13583-13595` 從 git log 取得的材料雖逐 commit 掃描，現行輸出仍只保存日期。
- Spec `:314-318` 擬議的新 helper 也只回 `(date, n_same_day)`，仍不足以判斷那些 commit 發生在標記之前或之後。

### f2 — major

Spec 段落：`★過期守衛` std-r1 改寫、工具清單 #5、`#4` 與 `#6`。

引句:「再一次批次 `git status --porcelain -- <vault>` 抓沒 commit 的:`git_dirty_notes(repo_root, vault)` 回 set,同款行程內快取。」

問題：新增的 dirty-set 路徑缺少可執行的輸出解析契約。普通 `--porcelain` 會對特殊／非 ASCII 路徑套用 quoting，rename/copy 更會輸出兩個路徑；spec 沒要求 `-z`，也沒要求 `-c core.quotepath=false`，更沒定義 rename、刪除、未追蹤檔與 quoted path 如何轉成 vault-relative `rel`。因此中文筆記或 rename 狀態可能無法加入 dirty set，直接造成過期守衛的安全方向偽陰性。

這尤其與同節已確認的 git-log 中文路徑事故不一致：工具清單 #5 明知不關 `core.quotepath` 會讓中文路徑「整張表是空的」，卻沒有把同一要求套到新補的 `git status` 路徑，也沒有相應測試。

程式碼證據：

- `scripts/lumos:13572-13584` 現有 git-log helper 特別使用 `-c core.quotepath=false`，註解明載中文路徑否則無法對回。
- `scripts/test_lumos.py:579-608` 現有測試明確覆蓋中文檔名，但 std-r1 新列的測試只測 dirty 結果，沒有中文、空格、rename/copy 或 `-z` 解析。
- `git_dirty_notes` 目前不存在，屬本案要新建；spec 尚未給足它的資料格式與解析規格。

### f3 — major

Spec 段落：工具清單 #4、`#4 impact 讀 about_code`、審計修正紀錄 std-r1 的「讀側三條路徑行號」。

引句:「四處 `results.append`(incident `:14178` / direct `:14203` / indirect pinned `:14214` / indirect free `:14223`)」

問題：這批宣稱已經由 std-r1 校正的行號仍全部指錯，且多數落在不相關敘述或變數上，不是 `results.append`：

- `:14178` 是 incident dict 的結尾；真正 append ranked incident 是 `:14193`。
- `:14203` 是 query-quality gate 的 stderr；真正 direct append 是 `:14218`。
- `:14214` 是 direct-base knob；真正 indirect pinned append 是 `:14229`。
- `:14223` 是 `L` 賦值；真正 indirect free append 是 `:14238`。
- 同段宣稱 `pins :14226`，實際在 `:14241`。
- `_impact_knob :13883` 實際定義在 `:13898`。
- `LUMOS_IMPACT_BASENAME_MATCH :13609` 的說明／使用實際在 `:13624`、`:13639`。

本 repo 雖允許知識圖譜導航行號近似，但這份是交付實作者的具體接線 spec，且修正紀錄明確宣稱這些行號已被校正。整批偏移並落到錯誤語句，會使逐字開工與審查定位失真，亦表示 std-r1 的「全改」宣稱未經當前 code 驗證。

## 逐節覆核

- Frontmatter、決策與定位段：已讀；除既有摘要仍殘留「噪音剔除改由巨檔門檻」而正文後段承認巨檔門檻不剔噪音外，屬歷史摘要銜接瑕疵，未另報 ≥major。
- 症狀、扇出訊號、兩個否決方向、二元砍除實驗：已讀，無新增 ≥major finding。
- 現行 direct 算法、世界解、三層研判：已讀，無新增 ≥major finding。
- 主案、欄位設計、讀側三路：已讀；行號錯誤見 f3。
- 存量／增量、巨檔門檻、回滾：已讀；已標 ✅ 的落地項目未重審。
- 過期守衛：已讀；不可解除的同日誤判見 f1，dirty path 解析缺口見 f2。
- 離線驗證、成本與風險、三條線、A 層、`impacts_code` 後案：已讀，無新增 ≥major finding。
- 工具清單 #4/#5/#6/#7：已讀；#4 引用錯誤見 f3，#5 新增 dirty helper 缺口見 f2；標 ✅ 項目依要求不審。
- `#4`：已讀；同日基線問題見 f1，行號見 f3。
- `#6`：已讀；`repo_root` 確實由 `run_doctor` Check C 建立並可供後段複用，無另 finding。
- `#9`：已讀；hook 的 pins 顯示迴圈確在 `impact-hook.py:342-348`，無 finding。
- `#10`：已讀；`_macro()` 會排除 `None`，history 實際保存 `reports[*].verdict`，接線方向成立，無 finding。
- Tier、合約候選、誠實缺口、審計修正紀錄：已讀；合約候選第 3 條的恢復動作不成立，見 f1。
- 文件內 wikilink 交叉引用：已逐項核對，未發現達 major 的斷鏈。

## 實務隱患

- 併發：無新增否決級問題。擬議快取皆為行程內、hook 每次新 process，不共享可變狀態；主要問題是資料基線語意而非跨 process race。
- 效能：有風險。命中時新增 git log 加 git status 兩個子行程；spec 只量到 git log 約 0.215 秒，未量 git status，且 hook 是 PreToolUse 熱路徑、行程內快取對下一次 hook 無效。這是需驗證的成本，但在已有懶觸發與 30 秒 hook timeout 下，單獨不足以再列 major。
- 資源：無獨立否決級問題。全 vault 計數與 git 輸出規模受 repo 大小約束，未見持久資源洩漏。
- 回滾：有 blocker；同日誤判無法靠文件指定的重設 stamp 恢復，見 f1。批次 revert 已標 ✅，依要求未重審其主體。

最嚴重 severity 是 blocker。
