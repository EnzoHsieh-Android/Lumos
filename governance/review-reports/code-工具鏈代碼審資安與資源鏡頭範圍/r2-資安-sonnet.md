severity: minor

## 總覽

上一輪的 major 已降到 minor。範圍那一行改成條件語氣後,照字面讀不會一步走到少審。剩下三條 minor,都不是 blocking。

### finding 1:`--json` 的 `lens_scope` 仍然無條件是 toolchain
severity: minor
blocking: 否 — 要在跨 repo 派工又只讀 JSON 欄位、不讀同段說明時才少審,偏離正常用法,而且說明與文字行都已帶但書。
引句:「`--json` 的 `lens_scope` 是 `toolchain`);那一行看的是帳本所在 repo,跨 repo 派工」
- 攻擊路徑(第 ③ 類,非刻意走過守衛)
  - 誰:使用者本人或照常操作的 AI 編排者。
  - 從哪:會談開在工具鏈 repo,審的卻是消費專案分支,編排者用 `lumos loop next <code-編號> --json` 取下一步。
  - 送什麼:只讀 JSON 的 `lens_scope` 欄位,沒看範本那段跨 repo 的但書。
  - 拿到什麼:欄位值是 `toolchain`,沒有任何條件限定。編排者照它貼〈工具鏈三類〉,消費專案被少審,而且是審登入、加密與行動端的那幾類被拿掉。
- 這次修補只改了文字行,沒改 JSON 欄位。
- 實驗(臨時 repo 已刪)
  1. 建一個只有空的 `skills/lumos-project-notes/SKILL.md` 加 `docs/x-knowledge/` 的 repo。
  2. 執行 `python3.14 scripts/lumos loop next code-consumerx --tier high --orchestrator codex --json`。
  3. 輸出 `lens_scope= toolchain`。
  4. 不帶 `--json` 時印出的是新的條件句。
  5. 欄位值與文字行的條件語氣不一致。
- 佐證:``file: `scripts/lumos:16432` ``(`out["lens_scope"] = "toolchain" if ... _is_toolchain_repo(_lens_root) else "default"`,沒有「被審分支也在這個 repo」的判斷)。
- 建議:欄位改成 `ledger_repo_is_toolchain`,或加一個 `applies_if_reviewed_branch_in_same_repo` 之類的但書欄位。

### finding 2:判別看被審分支的根,投稿者加一支空檔就能降級資安清單
severity: minor
blocking: 否 — 修補已把這個手法明文劃為刻意手法、範圍外,依派工圍欄只能標 minor。
引句:「任何 repo 根放一支空的同名檔就會被判成工具鏈,屬刻意手法、範圍外」
- 攻擊路徑
  - 誰:消費專案分支的投稿者。
  - 從哪:PR 或分支裡新增一支空的 `skills/lumos-project-notes/SKILL.md`。
  - 送什麼:那一支空檔。
  - 拿到什麼:編排者照〈工具鏈三類〉的判別規則,到被審 repo 的根看這支檔(多半就是被審分支的工作樹),把消費專案判成工具鏈本 repo。資安席拿到的清單從六類縮成三類,登入、加密、行動端被列入「接受不看」,範圍外那段還教席位把偽造類發現標 minor。
- 這是單檔就能做的事,不用偽造 git 內部。但新檔會出現在 diff 裡,席位或主審看得到。
- 實驗:finding 1 的臨時 repo 同樣用一支空檔就被判成 toolchain。
- 建議:判別時附一句「被審分支新增或修改這支檔,一律當消費專案」,或改看被審範圍的基底提交。

### finding 3:Issue 紀錄的「手法一句」只靠編排者自覺轉述
severity: minor
blocking: 否 — 紀錄寫法改成編排者轉述是進步,但沒有格式或跳脫規則,只是縱深防禦,沒有直接攻擊路徑。
引句:「手法一句由編排者自己轉述,不照抄席報告原文」
- 攻擊路徑(提示注入,推論)
  - 誰:能影響席報告文字的外部內容,例如被審 diff 裡的文字。
  - 從哪:席報告裡「看到刻意偽造」那一條。
  - 送什麼:夾帶指令、`[[連結]]`、`|`、換行或 `KEY:` 之類前綴的文字。
  - 拿到什麼:編排者轉述時若不慎帶進去,就寫進一篇只追加、清不掉的 Issue 筆記。後面的 AI 讀圖譜時會讀到它。
- 修補只給了原則,沒有長度上限,也沒有「去掉 `|`、換行與連結」的規則。
- 我只讀了這段文字,沒有實跑。

## 已讀,無 finding
- 範圍那一行的條件語氣:行動語句限定在被審分支同 repo 時。
- 〈工具鏈三類〉新增的判別說明(只看根目錄、不往上找、方向是多審)。
- 「DoS 歸資源席」搬進〈工具鏈三類〉。
- §3 的 manifest 併發題須知。
- §3.1 修補鏡頭與 §9 回顧起草者兩份派工詞新增的刪檔規則。這兩段只是固定字面的規則文字,沒有帶入作者可控文字。
- `scripts/test_lumos.py` 新增測試。我只掃了有沒有 `shell=True`、`rmtree`、網路、密鑰與信箱,只看到一處測試用的壞符號連結。
- `governance/anchor-baseline.json`:雜湊與備註更新,沒有新增密鑰或信箱。

最高等級 minor,blocking 0 條。
