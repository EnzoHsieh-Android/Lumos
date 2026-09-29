severity: minor

# 架構對齊-sonnet 第 2 輪

## F1 刪除守衛讀工作目錄、且不含「起點原封不動」那一半,跟同用 _vendored_state 的另幾處口徑不同
severity: minor
blocking: 否
引句:「工具檔改名離開或整支刪掉時,來源已不在工作目錄 → 不算原封不動 → 照抽:寧可多掃,刻意的。」
佐證行 file: `scripts/lumos:17867`(_vendored_skip:終點原封不動的 ∪ 起點原封不動但終點已刪的,拆除工具鏈也跳)
佐證行 file: `scripts/lumos:24511`(每支檔有家 staged 側:`_vendored_state(root, "")[0]`,讀暫存區)
佐證行 file: `scripts/lumos:24643`(同上,staged 用 `""`、推送用 tip)
佐證行 file: `scripts/lumos:18399`(技術棧掃描:`_vendored_state(root)[0]`,讀工作目錄,無 diff 概念)
1. 修正後 cmd_delguard_check 呼叫 `_vendored_state(root)[0]`(ref=None,工作目錄),沒有任何 git 讀取。這條讀 staged diff,最近的同類(24511/24643)讀暫存區 `""`;18399 是純掃工作目錄,不算同類。
2. 分歧有寫理由(註解:純讀本機檔、不跑 git、無時間上限問題;暫存與工作目錄不一致只會少掃;來源刪除或改名離開照抽)。理由站得住,沒引進第二套解析,只是同一函式的第三種 ref 用法。
3. 唯一實質不一致:`_vendored_skip` 明講「終點刪了但起點原封不動的也跳」,刪除守衛對同一情境(消費專案拆除工具鏈、整支刪 scripts/lumos)反過來照抽,會把工具檔刪掉的名稱全丟去 grep 圖譜。註解和計劃都標了「刻意、寧可多掃」,且 RETIRE-IF 有量測條件,所以只列 minor;未做重現(是設計取捨,不是錯行為)。

## 逐項判定(無 finding)
- diff 檔頭解析:專案內解析 rename 的只有 `_patch_file_changes`(`scripts/lumos:19327`、19378,只取 rename to、有 `_git_unquote_path`、回指紋不回路徑),它自己的說明就寫「既有的 _delguard_parse_diff 只用 ` b/(.+)$` 抓、不處理引號,所以不能直接拿來用」;沒有可重用的 rename from 函式。新增的 `rename from ` 讀取跟 `_delguard_path_flags`(`scripts/lumos:29328`)同樣不做引號處理,與同函式家族一致;工具檔名固定是 ASCII,不會踩到引號。不算第二種做法。
- 佔位字變體:`_set_cond_slot_variant_re` 與 `_SET_COND_SLOT_VARIANTS` 就放在 `_SET_COND_SLOTS` 旁(`scripts/lumos:14632`~14644),字面從同一個 tuple 取;`_DRIFT_PLACEHOLDER_RE`(`scripts/lumos:27653`)擋 --reason、註解已明說「用途不同,不合併」。兩邊口徑仍不同(set 側擋變體、--reason 側只擋原樣),但 --reason 沒有「從證據頁整句照貼」的路徑,給不出失敗場景,不列。
- 證據頁截斷:具名常數 `_DRIFT_C4_DIRS_MAX` + 顯示層 `[:N]` + 「另有 N 個…」+ 指到完整清單,跟既有寫法同型(`scripts/lumos:29648` 的 DELGUARD_TOP_N「…另有 N 處…(--json 看全量)」、`scripts/lumos:33490` 的 _LENS_CAND_CAP)。措辭「另有 N 個沒列出」與 33442/33463/33509 的「另有 N 個未列」略異,屬措辭偏好。`_drift_c4_more_cmd` 另寫而不呼叫 `_drift_git_cmd`(`scripts/lumos:28172`,那支綁單一檔路徑 cx["repo_rel"],不適用)但沿用 `--literal-pathspecs` 與 core.quotePath=off,一致。
- c1 的 `one=True` 是同一支 `_guard_settle_missing_say` 的參數,兩處仍共用一支,沒有分叉。

最高等級:minor
