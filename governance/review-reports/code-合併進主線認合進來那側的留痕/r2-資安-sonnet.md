severity: clean

本輪只靠讀碼與對照 `scripts/lumos` 現有輔助函式(_lens_git、_git_is_shallow、_codeloop_record_valid_ex)推演攻擊路徑,沒有另在臨時 repo 實作攻擊;下列各類都找不到可直接利用的繞法。

## 查過沒繞法的項目

1. 不可信輸入流到危險操作:帳本 head_sha 只會在 isinstance str、非空、且必須落在 `git rev-list --first-parent` 列出的 window 集合內才會往下傳;傳給 git 的 sha 因此都是 git 自己吐出的完整 sha,不是帳本字串,不能夾旗標。範圍字串先過 _lens_range_ok(拒 - 開頭、`...`、空白),再用 `--end-of-options` 的 _lens_full_sha 解析;全部用 list 形式、沒有 shell。
   引句:「if (isinstance(ev, dict) and ev.get("gate") == "code-loop" and ev.get("kind") in kinds」
2. 例外收成放行?沒有:merge-side 查詢整段包 try/except Exception,回的是 (None, 為什麼),呼叫端 _disp_record_for 與 _codeloop_review_block 都把 None 當「不認」;沒有任何分支把例外轉成放行。淺 clone 判斷逾時(TimeoutExpired)也被這層接住。
   引句:「return None, f"判不了合進來那一側({ex.__class__.__name__}),不認"」
3. 期限延後讓表態超時放行更容易觸發?沒有:延後量就是合併側實際花掉的時間,逐題核對拿到的預算跟原本一樣(_DISP_BUDGET),over_budget 放行的觸發窗沒有變寬;合併側自己的期限用盡只會得到「不認」。
   引句:「deadline = None if deadline is None else deadline + (_t.monotonic() - t0)」
4. cache 讓第二關沿用第一關放行?cache 只存「合併提交判定結果(母、是否只差簿記)」與帳本全文,不存放行結論;審查關(passed/skipped)與表態關(dispositions)各自用自己的 kinds 重新挑事件、各自重驗紀錄有效性,所以一關過不會讓另一關過。第一關失敗也是 fail-closed(side=None 被沿用,第二關同樣不認)。
   引句:「cache["side"] = _codeloop_merge_side(repo_root, marker_sha, raw_range, deadline)」
5. 權限繞過的前提鏈:第一母必須等於推送範圍起點、第一母是第二母祖先、合併結果只差簿記檔、紀錄那個提交包含第一母且對第二母有效、只認第二母那棵樹的帳本;淺 clone 與 octopus(非兩個母)都不認。唯一剩下的是「分支作者手寫帳本行」,已被上一輪列為既有天花板(同樣能手寫主線帳本),本輪沒有新增這條能力。
   引句:「if _git_is_shallow(repo_root, timeout=_merge_side_left(deadline) or 0.01):」
6. 密鑰與個資:reason 只含固定中文句、kind(僅 passed/skipped 兩值)、sha 前 8 碼、經 _esc_clean 截斷的分支名,不含帳本 detail/note;沒有秘密或個資進治理帳與 CI log。
   引句:「分支 {_esc_clean(ev.get('branch'), 80)}))")}, None」
7. 加密與傳輸:不適用,已看,無。
8. 執行邊界:兩份說明檔只描述「合併前先跟上主線、合併提交不手改、squash 不適用」,沒有教人關閘、跳過或貼上不安全指令;已看,無。
   引句:「壓成單一提交（squash）的合併不適用，主線那邊要補審或補記」
9. 行動端:不適用,已看,無。

總結:修正後「判不了一律不認」沒有反向變成放行的路徑,期限延後與 cache 也沒有放寬超時放行或跨關沿用,本輪未發現可直接利用的洞。
