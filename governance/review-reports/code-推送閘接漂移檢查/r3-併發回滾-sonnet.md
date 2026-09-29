severity: minor

# 併發回滾-sonnet 第 3 輪報告

## F1 舊值只是查詢失敗(逾時)時被當成「本機找不到」,範圍縮成只剩最後一個提交
severity: minor
blocking: 否
引句:「old_sha = None if zero else _lens_full_sha(repo_root, old)」
file: `scripts/lumos:33086`(patch 內 `_push_range_start`;`_lens_git` 逾時回 None、`_lens_full_sha` 對「不存在」與「git 逾時/失敗」都回 None)
1. 輸入:沒有可用主線(遠端沒有 HEAD/main/master、本機 main 沒設 upstream,或預設分支叫 develop/trunk 且 Actions 上沒有 origin/HEAD),遠端舊值其實在本機、只是 `rev-parse --verify` 那一次呼叫逾時或失敗。
2. 走到 `_no_mainline`:`old_sha` 是 None、`zero` 為假,落到「頂端的第一個父提交」那一支,起點變成 `tip^1`,說明還寫「遠端舊值在本機找不到」(不實)。
3. 重現(在暫存 repo 4 個提交,舊值=第 2 個、頂端=第 4 個,把 `_lens_git` 對舊值的 rev-parse 換成回 None 模擬逾時):
   正常:起點 c7cd51b4(舊值),範圍含提交 3、4;
   逾時:起點 7de04c7c(頂端父提交),範圍只剩提交 4,提交 3 的漂移不查。
4. 方向:git 呼叫失敗是往「少查」偏(把查不到當成沒有新東西的縮小版)。其他路徑(主線候選逾時、merge-base 逾時、is-ancestor 逾時、_push_pick_base 逾時)都是往「多查」偏,沒有這個問題,只有這一處。
5. 影響有限:要同時「沒有主線」加「單次 git 呼叫失敗」;放行後 CI 那步同樣走這條,兩邊可能同時漏。降為 minor。

## 其他鏡頭問題的核對結果(不是 finding)
- 新掛鉤配舊版工具:實測舊版 lumos(dca86f7d)對 `--push-remote --pushed-ref` 回 rc=2 印「擋下:不認得這幾個參數」。掛鉤只認 rc1 擋、≥128 停,rc2 走「漂移檢查沒能跑完…這次沒檢查;CI 會再檢查一次」放行並講一句,不是靜默放行;掛鉤註解與這句話已涵蓋「舊版工具」。CI 那邊工具與 workflow 同一個 checkout,不會不同版。消費專案若 CI 範本是新的、scripts/lumos 還是舊的,CI 會紅(rc2 原碼傳出),屬文件寫明的「寧可紅」。
- 舊掛鉤配新工具:舊掛鉤不帶兩個新旗標,`push=None`,走原本的 `_lens_push_base`,行為不變。
- 一次推多個 ref:每個 ref 跑一次 `drift check`,`_push_range_start` 最多約 10 次輕量 git 呼叫(每個候選 rev-parse 一次、`_push_mainline_branch` 至多 3 次、is-ancestor、merge-base --all、每個基底一次 is-ancestor);實測單次 drift check 約 0.54 秒(空 vs 全 help 0.38 秒)。最壞情形每次 git 逾時 20 秒 × 呼叫數,但各 ref 之間各有 60 秒預算,不是無界累加,不視為問題。
- 五道閘被中斷:`trap ... EXIT INT TERM` 在 INT 只清暫存目錄、不 exit,腳本會繼續;`pp_stop_if_signaled` 在 rc≥128 時 exit,再由 EXIT trap 清 `$_PP_TMP`,沒有殘留。`spec-gate` 用 `PIPESTATUS[0]` 取碼再判,正確。
- 照 revert 還原:在暫存 clone 對 fc25e1e4 與 dc89b491 兩個提交 `git revert`(唯一衝突是 append-only 的治理帳 jsonl,取現況即可),還原後掛鉤、CI、`_DRIFT_CI_STEP` 一起回到舊起點算法,`t_doctor_drift_ci_template_start_fallback` 等 `-k drift_ci` 4 個測試全綠,那篇新開的 Issue 也一併被 revert 刪除,沒有留下孤兒引用。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區:不影響。改動不動 code-loop check 的參數與 rc1 判定,只在其 rc≥128 時停下;rc1 擋、其他 fail-open 的慣例保留。
- Systems/存量漂移守衛、每支檔有家、筆記內容閘:不影響。掛鉤仍在 home/note-shape 後、code-loop 後跑,上線標記行 `# lumos drift check` 保留;只多了中斷停下。
- Systems/測試假綠形態(★INVARIANT★ 前置斷言):不影響。新增測試若是還原翻紅釘,本輪未見缺前置斷言的證據,本席未逐條審測試。
- anchor-integrity、bound-tests-gate、lumos-cli-lifecycle/read(合約:re-inject、search 排除 superseded):不影響,diff 不碰這些行為。
- 其餘「超出上限只列名」的節點:僅因牽連檔命中,本席未見與併發回滾相關的合約被動到。

最高等級:minor
