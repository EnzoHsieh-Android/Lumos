## Findings

### f1 — blocker

Spec 段落：〈過期守衛〉std-r2、工具清單 #11、#6 doctor 提示、合約候選 3。

引句:「`lumos about-code restamp <節點>`(或 `--expired` 批次)重算第三段——這次重標真的會讓它不再過期」

`restamp` 只重算目前正文的雜湊，沒有重新判斷既有 `about_code` 是否仍符合目前正文，卻被 spec 稱為「重標」，並被 doctor 當成解除過期的標準動作。實際結果是：

1. 正文改動使標籤語意失效。
2. doctor 正確警告過期。
3. 使用者執行建議的 `restamp`。
4. 舊標籤未經雙評審或任何語意重驗便被蓋上新雜湊。
5. 後續 impact 永久信任這份可能錯誤的標籤。

這直接繞過〈存量與增量〉要求的雙評審寫入紀律，也讓「過期即不信」合約只保證字節同步，不能保證標記經重新驗證。`--expired` 批次模式尤其危險，會一次把全部已知可疑標籤重新宣告為新鮮。

應把恢復動作拆清楚：真正的 `relabel` 必須重新產生／審核 `about_code` 後才更新 stamp；若保留純 `restamp`，只能用於已人工核對標籤仍正確的情況，且 doctor 不得把它描述成「重標」。

程式碼查證：

- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:14976) 的 help registry 目前只登記 `about-code revert`。
- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:15082) 的二層 parser 目前也只有 `revert`；`restamp` 確屬本案待新增，因此 spec 必須完整定義其安全語義。
- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:7665) 的既有 `cmd_about_code_revert` 只負責撤回，沒有可供 `restamp` 重用的重新標註流程。

### f2 — blocker

Spec 段落：〈過期守衛〉std-r2 的 83 篇存量遷移。

引句:「標完到現在有改過正文的那幾篇,標記可能已經不對但雜湊會說「沒過期」——遷移時用 git 列出 08-23 之後改過正文的清單,人掃一眼。」

這個 bootstrap 程序仍使用剛被 std-r2 判定無法表達順序的日期／git 尺，而且漏掉最關鍵的兩類：

- 8 月 23 日標註完成後、同一天再次修改或 commit 的正文。
- 標註完成後尚未 commit 的工作樹修改。

直接以「現在正文」補第三段，會把這些可能已失效的舊標籤永久洗成新鮮；新雜湊守衛之後也無法再辨認它們。這正是 std-r1 的同日與 dirty 規則原本要處理、但 std-r2 沒有搬進遷移程序的仍有效要求。

由於 83 篇標註與遷移都發生在 `2026-08-23`，只列「08-23 之後」的 git 變更尤其可能得到空集合，不能作為一次性人工覆核母體。遷移必須使用能界定「每篇實際完成標註時點」的 provenance；若沒有這份資料，就應把 83 篇全數視為待覆核，而不能直接以現況正文 restamp。

程式碼查證：

- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:13564) 的既有 `git_last_change_dates` 只提供最後變更日期，沒有標註完成時點或同日先後資訊。
- Spec 指定的新 `note_body_hash` 尚不存在；一旦直接以目前工作樹內容建立初始 hash，歷史上的標註—修改順序即不可復原。

### f3 — major

Spec 段落：〈本案新增／修改工具清單〉#4，與〈過期守衛〉std-r2、工具清單 #5、#4 詳細規格的銜接。

引句:「總開關 `LUMOS_IMPACT_ABOUT`;懶觸發 git;計數切 `_impact_about_counts`」

這一列仍命令實作者在 `cmd_impact` 熱路徑「懶觸發 git」，但 std-r2 的核心裁決是「無 git、無子行程」，工具清單 #5 也說 `git_last_change_dates` 在本案暫無呼叫者。這不是單純背景留痕：它位於本案可執行工具清單 #4 的現行實作指示中，可能讓實作者重新接回已淘汰的 git 路徑，重生 std-r1 的約 0.2 秒 hook 成本及 dirty、rename、quotepath 問題。

應把 #4 的「懶觸發 git」改為「about 命中後才讀該筆記正文並計算 `note_body_hash`」，明確聲明不得呼叫 `git_last_change_dates`。

程式碼查證：

- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:13997) 的 `cmd_impact` 是實際 ranked 熱路徑。
- [impact-hook.py](/Users/enzo/harness/lumos-toolchain/scripts/hooks/claude/impact-hook.py:471) 每次窗外 PreToolUse 都以新 CLI 子行程執行 `impact --ranked`，所以行程內快取不能消除 git 子行程成本。
- [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:13564) 的 `git_last_change_dates` 已存在；錯誤照工具清單接線是可直接發生的，不是抽象措辭問題。

## 逐節覆核結果

- Frontmatter、定位段、症狀、訊號、被打掉方向：已讀，無否決級 finding。
- 實驗結果、現行 direct 算法、世界解、三層研判：已讀，無否決級 finding。
- 欄位設計與讀側規則：已讀；除上述過期／遷移銜接外，無否決級 finding。
- 存量與增量、巨檔門檻、回滾：已讀；`revert --batch` 與目前實碼契約相符，無其他否決級 finding。
- std-r1 留痕：未把被取代方案當現行規格重審；其仍有效的「同日與 dirty 變更不可漏」要求在 f2 指出。
- 離線驗證、成本與風險、三條線、A 層、下一步 impacts_code：已讀，無其他否決級 finding。
- 工具清單：✅ 項目未審；未完成項除 f1、f3 外無否決級 finding。
- #4、#6、#9、#10 詳細規格：已讀；`as_list`、四個 `results.append`、`.get` 慣例、`--incidents-only`、`fusion_p → _macro → verdict → history` 與 gates 現況均已開檔核對，無其他否決級 finding。
- 合約候選、誠實缺口、審計修正紀錄：已讀；除 f1 的「restamp 即恢復」合約外，無其他否決級 finding。
- 文件內 wikilink 與節名交叉引用：抽核目標均存在；未找到否決級壞引用。

## 實務風險鏡頭

- 併發：無否決級新問題。既有寫入採命令式更新；讀取正文可能遇到寫入競態，但雜湊最多產生一次保守過期。真正風險是 f1 的錯誤 restamp 會把競態結果重新宣告為新鮮。
- 效能：f3 是 major；若依工具清單誤接 git，PreToolUse 每個新 CLI 行程都付出子行程成本。純候選檔案讀取加 SHA-256 本身無否決級問題。
- 資源：無否決級問題；83 篇 doctor 掃描及候選級檔案讀取規模有限，沒有持久資源或無界集合。
- 回滾／恢復：f1、f2 是 blocker。`revert` 本身已有部分失敗保護，但 `restamp` 會把未重驗資料洗成新鮮，初次 83 篇遷移亦可能造成不可再偵測的假新鮮。

最嚴重 severity：blocker。
