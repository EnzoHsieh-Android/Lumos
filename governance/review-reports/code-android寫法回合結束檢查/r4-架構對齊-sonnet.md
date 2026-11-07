severity: minor

第三輪架構對齊席 F1–F4 都照方向修了。F5 的放行理由站得住,我沒有退回。這輪沒有新的 major。以下 4 條是結構對、細節沒對齊的小項。我只讀了 patch,並用 grep 對照 `ffce2c71a` 的 repo,沒有重跑任何東西,也沒有改 repo。

## 第三輪 F1–F5 核對

- **F1(兩層預設相反)已修。**
  - 判定層不再補預設,`_lint_new_wt_verdict` 裡「沒寫種類就補 deliberate」那兩行拿掉了。
  - `"timeout"` 收成常數 `_LINT_WT_TIMEOUT`,JSON 層的寫法也跟著用常數。
  - 但「種類只在兩處寫」的說法不實,見下面 F3。
- **F2(`pre` 傳或不傳兩種形狀)已修。** `_nodehome_cat_blobs_capped` 兩處都改成一律 `pre=pre`,新增的呼叫端也都照這一種寫法。
- **F3(兩份清單)只算半修。** 主程式清單的過濾器列舉整段拿掉,剩固定三項。鉤子層 `_GIT_UNSAFE_CONFIG` 沒有 `core.hooksPath`、值也不同,仍是兩份,見 F4。
- **F4(門檻判斷兩份)已修。** 新的 `_lint_over_limit` 是唯一判斷,`_lint_new_oversize` 和 `_lint_wt_head_oversize` 都呼叫它。
- **F5(`_nodehome_cat_*` 沒帶 `GIT_OPTIONAL_LOCKS`)放行理由成立。** `cat-file` 不寫索引也不拿選用鎖。新的 `_impact_wt_nofilter` 走同一條讀法,沒有讓這個差異擴大。

## ① 模組邊界

- **`_wt_changed_nofilter` 在主程式與 `check-graph-sync.py` 各放一份逐字複本。**
  - 這跟 `Systems/hook信任邊界` 的做法一致:鉤子不能匯入主程式,安全邏輯走「逐字複本加守衛」。
  - 守衛 `t_lwt_r3_nofilter_verbatim` 在 `scripts/test_lumos.py:132250`,已存在。
  - 這個複本有多份實作的漂移風險,但沿用既有慣例,我不列為不對齊。
- **`_git_untrusted_c` 留在主程式,鉤子層不跟著用。**
  - 鉤子層本來就用自己的 `_hookshared._GIT_UNSAFE_CONFIG`(`scripts/hooks/claude/_hookshared.py:187`)。
  - 鉤子層現在找改動根本不跑 status,所以不再需要那份清單,邊界乾淨。
- **`unchecked_kind` 的欄位與事件對應仍和 `_hookevent` 合約一致。**
  - 鉤子的 `_unchecked_kind` 把 deliberate 記成 ok、timeout 記 timeout、其餘記 error,三種值都在 `KINDS` 內(`_hookevent.py:37`)。
  - 這輪多擋了非字串的值(清單、物件),一律記 error。

F1
引句:「def _impact_wt_nofilter(repo_root):」
引句:「texts[p] = " ".join(ln[1:].strip() for ln in lines)[:4000]」
引句:「modes[p] = ("100755" if st.st_mode & 0o111 else "100644", _head_is_shebang(new, lenient=True) if ok else None)」
- `cmd_impact_diff` 現在有兩條產生「改動段落文字」和「檔案模式」的路,各寫了自己的整形碼。
  - 既有路徑用 `git diff` 加 `_impact_diff_modes`(`scripts/lumos:67210`),整形是 `" ".join(l[1:].strip() ...)[:4000]`。
  - 新路徑用 difflib 加自算的模式,整形碼逐字重寫了一遍,模式判法也自己寫。
- 分兩條路的理由站得住:`git diff` 會經內容過濾器。
- 但「把 +/- 行接成查詢文字」沒抽成共用,兩處日後改一邊另一邊不會跟。
- 結構沒有跨層,所以標 minor。
- ⚠ 若編排者要與「宣告過唯一實作又多一份」同等對待,可升 major,判定權交編排者。
severity: minor
blocking: 否

## ② 命名與錯誤處理

- 沿用既有前綴:`_wt_changed_nofilter`、`_lint_wt_*`、`_LINT_WT_TIMEOUT` 都和 `_LINT_WT_DELIBERATE`、`_LINT_WT_FAILED` 同風格。
- git 出錯的判法更一致了:`rev-parse --verify -q HEAD` 只有回 1 才算沒有 HEAD,其餘非零記 failed。
- 工具解析失敗用 `fail_info["unresolved"]` 回報,和既有的 `too_long` 同一種手法。

F2
引句:「def _git_untrusted_c(repo_root=None):」
- 這個函式現在不用 `repo_root`,卻保留參數「讓呼叫端寫法不變」。
- 結果同一個函式有兩種呼叫形狀:
  - `_git_untrusted_c(repo_root)`,在 `_lint_wt_blobs` 和 `cmd_spec_freeze`。
  - `_git_untrusted_c()`,在 `_lint_wt_git` 和 `_impact_wt_nofilter`。
- 這是死參數加不一致的呼叫,不是結構問題。
- 對照:`scripts/lumos:40215` 一帶的呼叫端。
severity: minor
blocking: 否

F3
引句:「# ★種類只在兩處寫★(代碼審 r3 通才席 F2、架構對齊席 F1):判定層每條 not-checked 路徑自己明寫種類,不補預設;」
引句:「out["status"], out["unchecked_kind"] = "not-checked", _LINT_WT_DELIBERATE   # 宣告形狀不讓跑,照設計判完了」
- 註解宣稱種類只在判定層和 JSON 層兩處寫,實際判定層本身分散在三處:
  - `_lint_wt_unready` 回 `(種類, 原因)`。
  - `_lint_new_wt_verdict` 寫 `_LINT_WT_TIMEOUT`。
  - `_lint_new_classify` 寫 `_LINT_WT_DELIBERATE`,有兩處。
- `_lint_new_classify` 是通用函式,不只工作樹模式用,卻開始寫帶 `_LINT_WT_` 前綴的欄位。
- 前一輪「判定層預設相反」的根因確實拿掉了,但「每條出口明寫種類」的守住靠的是人記得每條路徑都要寫。
- 以後新增一條 not-checked 路徑漏寫,會落到 JSON 層的 failed,這是安全方向,所以只標 minor。
- 對照:`scripts/lumos:42103`(`_lint_new_classify`)。
severity: minor
blocking: 否

## ③ 第二種做法

- **大小上限**:`_impact_wt_nofilter` 和 `_lint_wt_blobs` 都走既有的 `_nodehome_cat_sizes` 加 `_nodehome_cat_blobs_capped`,上限用既有的 `_CODELOOP_BOOKKEEPING_HEAD_CAP`,沒有另起讀法。
- **門檻判斷**:收成 `_lint_over_limit`,沒有第二份。
- **暫存清掃**:這輪沒有新增暫存清掃,工具寫檔上限(`RLIMIT_FSIZE`)重用既有的 `_LINT_SARIF_MAX_BYTES` 加餘量。
- **改檔前推播的入口**:`_impact_missing` 是鉤子取「該動卻沒動」的唯一入口,加了 `--worktree-nofilter`,沒有第二條路。
- **工作樹找改動**:除了 `git status` 被換掉,主程式還剩兩處 `_porcelain_v1_entries`,在 `scripts/lumos:52762` 和 `:75539`。它們讀的是推送前閘的 status 輸出,不是工作樹模式,不構成第二條路。

F4
引句:「_GIT_UNTRUSTED_FIXED = ("core.fsmonitor=false", "core.hooksPath=/dev/null", "diff.external=")」
- 註解仍寫「對齊鉤子那份 `_hookshared._GIT_UNSAFE_CONFIG`」,實際是兩份清單,值和項目都不同。
  - 鉤子那份是 `core.fsmonitor`、`diff.external` 兩項,值是空字串。
  - 主程式這份多了 `core.hooksPath`,且 fsmonitor 的值用 `false`。
- 守衛(`scripts/test_lumos.py:131602`)只驗單向:鉤子清單上的每一項主程式都關掉。
- 現在兩邊都不再靠清單擋內容過濾器,差異不構成缺口,只是第三輪 F3 的註解與守衛沒再收緊。
- 對照:`scripts/hooks/claude/_hookshared.py:187`。
severity: minor
blocking: 否

不對齊共 4 條,其中會擋的 0 條
