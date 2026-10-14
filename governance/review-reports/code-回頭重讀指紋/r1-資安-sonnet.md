severity: major

我找到 1 個擋得住推送的洞和 1 個不擋的次要點;其餘重點都試過,沒找到洞。

severity: major
blocking: 是 — 作者可把已被判定者看過的危險改動原封不動搬到同一支檔的別處,v2 指紋不變,舊紀錄照樣算「已對照」,而舊指紋(v1)會擋下。
引句:「headers=False:`@@` 後面的段落標頭(函式名)不算」
攻擊步驟(輸入→結果):
1. 一支 `app.py` 有兩個結構相同的處理函式 `public_list` 與 `admin_list`,各含 `trace(ctx)`、`check(user)`、`audit(req)` 這幾行。
2. 作者先在 `public_list` 做改動 `-check(user)/+allow(user)`,跑 prepare 與判定者並記下紀錄,檔名是 v2 指紋。
3. 作者再把這個改動改到 `admin_list`。此時 hunk 的增刪行與前後各 3 行上下文都一樣,只有 `@@` 後面的函式名和行號不同,這兩樣 v2 都不算。
4. 結果:v2 指紋與步驟 2 的紀錄相同,`_note_reread_hits` 判成 `"v2"` 命中,講「admin 要驗權」的舊句不會被擋。
5. 對照:舊口徑(headers 預設算)兩邊指紋不同,v1 也不同,因為 v1 含頂端 blob。放寬前這個搬動會被擋,現在不會。

實驗證據:
- 我在臨時 repo 實測。呼叫 `_patch_file_changes(..., headers=False, lf_only=True)`,x、y 兩份 diff 的結果 `==` 為 True。用預設參數(headers 算)則為 False。
- 我又建 `x`、`y` 兩條分支,分岔點同為 `b2`,把 `_note_reread_contrast_fp_v2` 對同一篇筆記路徑跑一次。兩邊都回 `76c127ef1b4b3ac8`。
- 這個洞不限於標頭:行號本來就不算,所以上下文相同的重複片段(樣板、設定表)換位置同樣中。
- file: `scripts/lumos:26098`(`_patch_file_changes` 的 `headers` 分支)。
- file: `scripts/lumos:36456`(`_note_reread_fp_file` 呼叫 `_patch_file_changes(..., headers=False, lf_only=True)`)。

severity: minor
blocking: 否 — 能偽造紀錄的人本來就能偽造 v1 紀錄,沒有新增能力;只是 v2 專屬的「分支自己新增」防線形同虛設。
引句:「範圍終點在本機找不到(rebase 前的舊頂端被」
攻擊步驟(輸入→結果):
1. `_note_reread_own_fps` 的三道檢查都看紀錄自己填的欄位:檔名不在分岔點樹裡、`contrast_fp` 等於檔名前 16 字、`tip` 欄不是分岔點的祖先。
2. 攻擊者複製主線上的舊紀錄,改檔名後綴,再把 `tip` 改成 40 個 0 或任一不存在的 sha。程式碼註解明說這種情況算「分支自己的」。
3. `provenance_ok` 也只是紀錄裡的一個欄位。
4. 結果:任何人能手寫一份 `provenance_ok: true`、`contrast_fp` 等於 v2 的紀錄就命中。
5. v1 本來就有同樣的偽造路徑,計算 v1 指紋不需任何秘密,所以不升級。這道檢查只擋「不小心沿用主線紀錄」,擋不住惡意。

實驗證據:純讀碼,沒另外執行。

這幾項試過,沒找到洞:
- git 選項注入:所有帶路徑的呼叫都有 `--` 加 `--literal-pathspecs`;sha 經 `_LENS_SHA_RE.fullmatch`(`$` 不會放過尾端換行),都不以 `-` 開頭。
- 事件欄位注入:`branch` 與 `v2_only.path` 走 `_note_reread_show`,`v1_why` 的鍵都是程式內的常數。長度由 `_gate_event_fit` 收斂,過長只丟 `v2_only`,不影響判定。
- 指紋算成常數:「全部未改」、「diff 空」、樹裡找不到都退回 v1,指紋混入筆記路徑與每支檔的 hunk 雜湊,攻擊者湊不出常數。
- 操縱遠端追蹤 ref:設成頂端會變「在主線上」而退回 v1;設得更早會讓 diff 變大、指紋對不上,都偏嚴格。把它設在分支中途理論上可排除前段改動,但這要改推送範圍閘共用的信任根,不是這次新增的洞,我沒做成。
- 逾時或截止:全部退回 v1,`_note_reread_own_fps` 逾時回空集合,偏嚴格。

最高等級 major,blocking 共 1 條(minor 1 條不擋)。
