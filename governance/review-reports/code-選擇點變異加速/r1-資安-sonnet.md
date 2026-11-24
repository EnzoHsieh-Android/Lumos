severity: clean

沒有可利用的洞(沒有 blocker 或 major)。鎖檔 `…2b4f.json.warming` 不存在(ls、cat 都回「No such file」),沒有東西要刪,照派工詞審。

## 三類逐項

①提示注入:已看,無。
- 合併路徑新增的對外輸出只有 stderr 的 `⚠ {_kill_esc(plat)}:…` 兩句,平台名經 `_kill_esc`。
- 合併分類的原因字串(`_choice_merge_classify` 的第二個回傳值)只用來數斷路器,沒有印出,也沒進治理帳。
- 進治理帳的新欄位 `judged` / `merged` / `single` / `base_secs` / `merge_tripped` 都是固定列舉或整數,型別經 `_GOV_FIELD_TYPES` 限制。測試輸出的自由文字沒有新增進入帳或給 AI 的路徑。`tail` 和 `fail_excerpt` 沿用逐支流程既有的 `_kill_fail_excerpt` 與 `_kill_res_excerpts`。

②讀寫與執行越界:已看,無。
- **合併指令的拼接**:每支測試名各自過 `_test_name_ok`(不收開頭減號、方括號、逗號、控制字元)。再各自過 `_run_cmd_expand`,用 `shlex.quote` 加引號,跟逐支流程完全同一支函式。用 ` --tests ` 接起來的每一段都已引號包好,測試名跑不出引號。
- **含 `{method}` 那一段**:`_choice_merge_shape` 要求單、雙引號各自成對。`--tests "foo {method}"` 這種引號跨空白的寫法,切出的那段引號不成對,直接回 None 不合併。
- **`run_cmd`**:仍是 `shell=True` 跑設定檔裡的字串,這是既有行為。`choice-kill` 是手動指令,這份 diff 沒把它接進 hook、安裝腳本或 CI。
- **`_choice_merge_clear` 會不會刪到工作樹外**:不會。`_choice_merge_results_dir` 用 `os.path.realpath` 解開符號連結和 `..`,再要求結果落在 `realpath(wt)+os.sep` 底下,否則回 None,`_kill_merge_ready` 就不合併。我走過三種情況:`-p` 給絕對路徑、`-p` 含 `..`、`build` 在 git 裡是指向外面的符號連結。三種都回 None。
- **`-p $HOME/x` 這類 shell 變數**:被算成工作樹內的路徑,實際 Gradle 寫到別處。後果只是刪到工作樹內不存在的路徑、讀不到結果檔而判 `unclean`,不會讀到別處的檔,也不會被誤判成存活。
- **讀結果檔**:只讀 `rdir` 下的 `TEST-*.xml`,只收 `is_file()`。大小上限單檔 8MB、合計 64MB,解析走既有的 `_secev_junit_facts`(DTD 拒收、過深拒收)。符號連結指到 FIFO 或 `/dev/zero` 的 `is_file()` 為假;指到一般檔的會被 XML 解析拒掉,內容不外洩。
- **密鑰與信箱**:在 diff 的新增行裡 grep 過,只有參考文件網址,沒有可用憑證、信箱或下載網址。這份 diff 沒碰安裝腳本。

③非刻意、一步就能繞過的守衛:已看,無。
- **`LUMOS_SKIP_CHOICE_MERGE`**:只認恰好是 `1`。殘留在 shell 裡也只會關掉合併快篩,回到原本逐支流程,守衛變慢,不會變鬆。
- **`--no-merge`**:同上。
- **合併把該被殺的判成存活**:合併只能得出「存活」,不能得出「殺掉」。存活不是放行,仍要人處置或 `lint-waive`,而且 `choice-points` 會標「存活(合併快篩判)」,所以不構成放行路徑。
- **「該失敗卻判通過」的路徑都被擋住了**:
  - 每次合併呼叫前先清結果資料夾。
  - 沒有結果檔記 `unclean`。
  - `rc != 0` 但結果檔全綠記 `unclean`。
  - 守衛測試名對不到結果檔的完整名,或對到不只一個,記 `unclean`。
  - 單支基準不綠的測試不進合併組,而是交 `abort`。
- **還原失敗**:記一列 `error` 並整組作廢。壞法只寫在隔離工作樹,使用者的工作樹不會被改。
- **第二個訊號的 `os._exit`**:沿用既有的 `_situation_rule_force_exit`,沒有新增殘留風險。

## 圖譜鏡頭
這次沒附固定席節點(LENS 說「沒附固定席節點」),不逐條答。

## 順手提一句(推論,不當 finding)
`_kill_merge_apply` 與 `_kill_merge_screen` 的 realpath 圍欄只在 `_kill_merge_ready` 檢查一次。理論上建置期間(也就是 repo 自己的 Gradle 腳本,本來就能執行任意碼)可以把 `build` 換成符號連結,再讓 `rmtree` 跟著走。攻擊者已經擁有的能力大於這個,所以不報。

## 引用的檔案
- 被審材料:`/Users/enzo/harness/lumos-choice-speed/governance/review-reports/code-選擇點變異加速/r1-snapshot.patch`
- 查證上下文:`/Users/enzo/harness/lumos-choice-speed/scripts/lumos`,涉及 `_test_name_ok`、`_run_cmd_expand`、`_under_root`、`_secev_junit_facts` 這幾個函式

總結:最高嚴重度 clean
