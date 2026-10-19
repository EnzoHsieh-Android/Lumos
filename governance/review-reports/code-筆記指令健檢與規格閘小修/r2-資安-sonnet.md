severity: minor

已逐行讀三份修補 patch(lumos、tests、docs),並對照 `scripts/lumos` 修後的程式。

**①提示注入:已看,無。**
- 修補新增的文字只有固定提示句和 `_sh_quote(Path(rel).stem)`,外部可控文字沒有進到派工詞或 hook 附加段。
- `_summary_write_shape_check` 回傳的訊息只回給使用者。

**②讀寫與執行越界:已看,無實際洞。**
- `_spec_gate_status_at` 用 git 讀起點版本,走 `_lens_git` 的參數陣列(`subprocess.run` 列表式,沒有 shell)。`base` 若以 `-` 開頭就回 None,不會被當成 git 選項。
- `repo_rel` 由 `(env.vault/prel).resolve().relative_to(rr)` 算出,跑出 repo 外會擲 `ValueError` 並回 None。`rev:path` 是單一參數,`base` 裡有冒號也只會讓 git 找不到而失敗。
- 補跑紅的步驟提示:`git restore --source=HEAD -- <實作的檔>` 只是印出來的文字,工具不會執行它。
  - 這一版新增了工作目錄有未提交改動時的警告(`status --porcelain --untracked-files=no`)。
  - 警告只是印一行,不會停下步驟,所以照做仍可能覆寫未提交改動。放在 finding 1 當縱深防禦。
- 讀檔越界:`_nodehome_changed_vs_disk` 的新路徑加了 `fp.is_file() and not fp.is_symlink()`,捷徑檔不會被跟過去。
- 密鑰與信箱:新增行裡沒有。
- 安裝腳本、下載網址:這輪修補沒有碰。

**③非刻意走過守衛:**
- 推送閘對 done 計劃的寬待改成「起點已 done」。
  - 新分支首推:起點是全零或不存在的 sha,`git show` 非 0,回 None,照嚴的判。
  - rebase 與合併提交:起點仍是遠端舊 tip 的真實提交,讀到的是那一版的 status,沒有誤判。
  - `git_range` 沒有 `..` 時回 None,照嚴的判。
  - 結論:三種情形都往嚴的方向失敗,沒有繞過路徑。
- 唯一的非刻意放寬只剩下面 finding 1。

1.
severity: minor
blocking: 否
引句:「        if nongit_ok:」
說明:`summary-line` 的形狀檢查跳過條件是 `_nodehome_list(root,"index") is None`。這個條件同時涵蓋「不是 git 專案」和「在 git 專案裡 git 逾時或跑不起來」。後者是 `_lens_git` 的 20 秒逾時,或使用者環境暫時 git 壞掉。
- 誰:使用者本人或照常操作的 AI。
- 從哪:執行 `lumos summary-line`。
- 送什麼:會被提交時形狀檢查擋掉的行,例如程式行號引用,或沒寫來源的 FACT。
- 拿到什麼:寫入階段的形狀檢查被意外走過。
- 影響範圍:提交時的 pre-commit 仍會再擋一次,所以這只是縱深防禦的缺口。
- 判不出刻意與否,所以照③報,但因為有提交時的後備守衛,標 minor。

file: `scripts/lumos:22774`

最嚴重 severity:minor,blocking 共 0 條。
