severity: minor

## F1 挑到的「最小提交」是一行帳本檔,「真範圍證明真內容跑得通」的前提已經空了,註解與計劃沒跟著改
severity: minor
blocking: 否 只是敘述與驗證力道不一致,測試仍綠、仍驗認領機制本身。

位置:scripts/test_lumos.py t_codex_s1_lens_arm_claim 的 cheap 註解區(diff 未動它)與計劃筆記「不選」欄。
場景:在實際 repo 跑 `_lens_smallest_commit('.', 'Lumos/main')` 得到 0f9c4a11,內容是 `docs/.governance-log.jsonl | 1 +`(一行帳本)。於是 rng 是這種近乎空的範圍;但同函式上方未改的註解仍寫「只留第一次用真範圍(證明真內容跑得通)」,計劃筆記的「不選」也以「第一次武裝本來就要證明真內容跑得通」為由否決跳過鏡頭。換範圍後,這個宣稱實質上不再成立(跟 cheap 的空 diff 差別很小)。
引句:「# 真範圍取主線上改動最小的那一個提交(兩端都在主線上):用「主線..HEAD」的話範圍就是當下分支的改動,」
佐證:file: `scripts/test_lumos.py:37887` 附近原註解「只留第一次用真範圍(證明真內容跑得通)」未改;file: `docs/lumos-toolchain-knowledge/Projects/鏡頭測試範圍固定_計劃.md` 「不選」欄。
建議:改註解與計劃措辭為「小而真的提交範圍,內容不保證有鑑別力」。

## F2 計劃筆記對守衛判準與改動處數的描述與程式不符
severity: minor
blocking: 否 只是筆記敘述偏差。

場景:計劃「做法」第 3 點寫守衛找 `..HEAD"` 或 `..HEAD',`(多了一個逗號);程式實際 regex 是 `\.\.HEAD["']`,不含逗號。計劃「範圍」寫「三處 `{ml}..HEAD`」,diff 實際改了四個點(arm_claim 的 arm 與斷言、r1_fixes 的 arm 與 ⑤)。
引句:「if _re.search(r"""\.\.HEAD["']""", f):」
佐證:file: `docs/lumos-toolchain-knowledge/Projects/鏡頭測試範圍固定_計劃.md` 做法第 3 點與範圍第一項。

## F3 守衛的漏抓面:判準只認雙引號 "dispatch-lens" 與緊接引號的 ..HEAD
severity: minor
blocking: 否 計劃「天花板」只承認變數拼接,未涵蓋下列兩種更直接的繞法。

場景:實跑現有檔,守衛正確點名被還原的 `t_codex_s1_r1_fixes`(我在臨時 clone 把 `rng` 改回 `f"{ml}..HEAD"`,守衛紅並列出函式名),現有檔全綠。但 (a) 範圍寫成 `f"{ml}..HEAD --seats 2"` 或 `..HEAD~0` 之類 `..HEAD` 後面不是引號的形態;(b) 把 dispatch-lens 呼叫放進非 t_ 開頭的頂層輔助函式(切函式後 `re.match(r"def (t_\w+)\(")` 直接跳過)、再由測試傳入範圍;兩者都不會被抓。現有檔 grep 無單引號 'dispatch-lens',所以單引號不是現況缺口。切函式用 `(?m)^(?=def )`:巢狀函式與類別方法有縮排不會被誤切,裝飾器行會併到前一個函式尾巴,無害;現有檔沒有誤抓(輸出 22 支含鏡頭字樣者,只有被點名的才中 ..HEAD 引號判準)。
引句:「if '"dispatch-lens"' not in f or "Path(GRAPHCTL).resolve().parent.parent" not in f:」
佐證:file: `scripts/test_lumos.py:16799` 附近守衛本體。

## 其他逐項查證(無 finding)
- 邊界:`_lens_smallest_commit` 對淺複製 depth 1 的 %P 為空 → 回 "" → `_head` 為空 → 兩支測試丟 `_SrcOnly` 當 skip(我在臨時淺 clone 驗到 log 只有一個無父提交)。不會紅,但 CI 淺複製時這兩支會靜默跳過,覆蓋變少(舊寫法會跑)。ref 不存在時 git log 失敗、stdout 空,回 ""(實測)。根提交被函式本身排除(要求 >=2 個 token),故 `~1` 一定存在;`rev-parse --verify` 回空也已接。
- 例外與 None:`_head + "~1^{commit}"` 只在 `_head` 真時才跑,三元式無 None 問題;subprocess 不丟例外。
- 斷言有效性:`LUMOS-LENS range={rng} 第 1/2 席` 比對全長 sha,我實跑 `-k t_codex_s1`:31 通過 0 失敗,arm_claim 29.7 秒、r1_fixes 8.8 秒。過期(TTL)、claim 歸零、status、disarm 用的是 cheap 範圍,與本次改動無關,斷言仍驗同一件事;⑤ 互斥 rc2 與範圍內容無關,不會假綠。唯一弱化見 F1。
- 時鐘/分支狀態:主線最近 30 個非合併提交的最小者會隨主線前進而變,但兩端恆為主線祖先,不依賴當下分支;無時鐘相依新增。
- 筆記一致性:Issue 與計劃敘述與 diff 大致相符(34/11 秒等數字未重量);Issue 的 hook 只等 45 秒未查證。
- 圖譜鏡頭:派工詞說本次沒附固定席節點(鏡頭逾時),照規定不補算。僅就 diff 可見處判斷:改動只動測試與三篇筆記(測試假綠形態 PITFALL 新增同族與 [test:]、計劃、Issue),不改任何工具行為或合約行;對 `t_lens_timeout_keeps_warming_cache` 的 PITFALL 只是附加同族,不破壞其宣稱。
- 角色卡:未附,略過。

總結:max severity minor,blocking 共 0 條(3 條 minor)。
