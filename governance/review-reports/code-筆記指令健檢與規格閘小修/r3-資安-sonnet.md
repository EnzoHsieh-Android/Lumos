severity: clean

這輪修補我逐 hunk 走過一遍,沒有發現能被利用的洞,也沒有守衛被意外繞過的路徑。

三類逐項如下。

**① 提示注入:已看,無。**
- `_dirty_non_bookkeeping` 只回傳路徑清單,結果拿去判斷真假,沒有拼進給 AI 的文字。
- 補跑紅步驟印出的 `git restore` 提示是固定字串,不含檔名或帳本欄位等外部可控的自由文字。
- 新增的 `_ns_neg_cond_paired` 和 `_ref_word_looks_like_path` 只做判斷,不輸出外部文字。

**② 讀寫與執行越界:已看,無。**
- `_spec_gate_status_at`:
  - `git_range` 以 `-` 開頭就回 None,也就是不當 done、照嚴的判。
  - `_range_base` 回來的 `base` 同樣會檢查是否以 `-` 開頭。
  - 呼叫的是 `git merge-base`,參數是 argv list,沒有 shell。
  - `merge-base` 沒有會寫檔的選項,所以不像 `diff --output` 那樣能寫任意檔,`...` 兩側帶選項字串也寫不出東西。
  - 路徑用 `resolve().relative_to(repo)` 限制在 repo 內。
  - `_note_text_at_rev` 失敗回 None,仍是 fail-closed。
- `_dirty_non_bookkeeping` 呼叫的 `git status --porcelain -z` 參數固定,沒有外部輸入。
- 補跑紅步驟提示:`git restore` 之前,`untracked=True` 的預警改成連沒追蹤的新檔也算,覆寫未提交改動的風險比修前小。
- 新寫進程式、測試和文件的內容沒有密鑰、信箱或下載網址,測試裡的 subprocess 是以 git 跑在臨時 repo。

**③ 非刻意一步繞過:已看,無。**
- 推送閘對 done 計劃的寬待,現在是「起點已 done」才給:
  - 新分支首推、起點讀不到、`..` 或 `...` 範圍解析失敗,`_spec_gate_status_at` 都回 None,等於不是 done,照 doing 一樣嚴。
  - 這個方向是 fail-closed,沒有錯判起點而繞過的路。
  - 新分支首推時遠端 sha 全零,這段本來就在 `git diff` 算不出範圍就放行,不是這次修補造成的。
- `_summary_write_shape_check`:
  - 非 git 專案只在 `isgit is False`(確定不是 git 目錄)時才讓 summary-line 跳過形狀檢查。
  - git 逾時或跑不起來(None)改成照擋,比修前嚴。
  - 非 git 目錄本來就沒有提交時檢查可繞,所以跳過不算新洞。
  - summary-add 在非 git 下仍擋。
- `_drift_fix_shape_err` 現在照 `note_shape` 總開關:`off` 不查、`warn` 只提醒、其他擋下。這是使用者自己設定的行為,不是意外繞過;舊版殘留環境變數也不影響它。
- `_spec_gate_latest_records` 去重與同秒取先列的改動:
  - 影響的是本機帳與治理帳同秒時哪一筆算數。
  - 兩筆都已讀入,要讓舊留痕贏得靠手填帳本欄位,屬範圍外。
- 其餘改動只涉及判斷邏輯,不碰守衛行為:
  - `_excluded_line` 的前置冒號檢查。
  - `_planned_ref_tokens` 的正規化。
  - `_ns_neg_*` 的子句判斷。
  - `_refcheck` 的指令判斷。
  - `--diff ""` 回 2。

最嚴重 severity:clean,blocking 共 0 條。
