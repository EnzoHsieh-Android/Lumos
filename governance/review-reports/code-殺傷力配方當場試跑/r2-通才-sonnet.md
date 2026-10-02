severity: minor

# 殺傷力配方當場試跑 代碼審第 2 輪 通才-sonnet 席報告

四條修正逐項判定(臨時 clone 在 trc-r2-work-通才-sonnet/repo,HEAD fe722c3c,實跑過):

- g1 格式壞判定:修好了,漏同類路徑只剩已知的既有 Issue。我造了 test 是清單/整數/None、covers 是字串、note 是物件、platform 是 ""/清單/整數、file 是整數/空字串、old 是空字串、缺 new 等 14 種形狀,帶 `--id` 一律不當掉(格式壞的回 2 並指示 kill-rm,其餘照常跑出判定)。不帶 `--id` 時 platform 是清單、file 是整數仍會當掉,屬既有 Issue,計劃明講只管 `--id` 路徑。`--json` 下擋下訊息只走標準錯誤,標準輸出為空。`_kill_add_try` 傳的是剛寫進去的完整身分,走不到格式壞,同意 r1-fix 的 unaffected。
- a1 修正關卡讀提交裡的配方:修好了。`rr`、`env.vault` 都經過 resolve,`tree` 是 realpath,`relative_to` 在 macOS /tmp 符號連結下不會誤丟。實測工作目錄把筆記改掉沒提交,提醒仍照提交裡的配方;工作目錄新增的未追蹤筆記不會出提醒(符合「只看提交」,但全程沉默,見文末備註)。知識庫在 repo 外的情形,`loop fix-check` 的審查帳本身就綁在 repo 內,我試不出能走到這條 `except ValueError` 的真實場景(帶 `--repo` 加外部 vault 會先死在「找不到載體席」)。
- a2 提醒前綴:修好了。三條提醒都帶「⚠ 提醒:」,「試跑沒跑成」「drifted」「baseline 沒綠」屬錯誤說明,不加前綴合理。
- a3 同時間戳取先出現的:修好了。`_kill_log_latest` 改成嚴格大於,同 ts 保留先出現的;`_backing_judge_groups` 裡 `max(..., key=ts)` 在平手時也回先出現的,兩邊一致。

跑過的測試全綠:`-k guard_kill_only_ids`(11)、`fix_check_recipe_rerun`(6)、`doctor_p2_lists_survived`(13)、`guard_kill_add_try`(7)、`guard_kill_rc_precedence`(4)、`guard_kill_json_purity`(6)、`kill_recipe_check_matches`(92)、`kill_rm`(44)。

## F1 `--id` 把「不帶 --id 跑得動」的配方也擋成「跑不了」,訊息與實際不符
severity: minor
blocking: 否
引句:「擋下:第 {i} 條配方格式壞({why}),跑不了;先 lumos guard kill-rm」
佐證行:file: `scripts/lumos:15338`
1. 重現:筆記裡一條配方少了 `invariant`(或 `invariant: 3`),`lumos guard kill Systems/Limit` 不帶 `--id` 照常跑完(rc 1,印 `killed_unattributed`);同一條帶 `--id <它的 12 碼身分>` 回 rc 2、印「第 1 條配方格式壞(invariant 不是字串),跑不了」。`platform: 3` 同樣:不帶 `--id` 是 rc 2 的 `error` 列(平台 '3' 不在 config,沒當掉),帶 `--id` 變成「格式壞」。
2. 影響很小:這種配方的身分本來就走 `_kill_recipe_id` 的 malformed 分支,P2 與 kill-rm 也當它格式壞,所以擋它跟全系統口徑一致;錯的只是那句「跑不了」(實際跑得動、只是身分不是正規身分)。回傳碼同為 2 的 `error` 與擋下無法從碼分辨,只在 `invariant` 缺失/非字串、`platform` 非字串且不是清單這幾種形狀才有差別。
3. 若要收斂:把訊息改成「格式不合,先 kill-rm 再重加」之類不斷言「跑不了」的說法,或把 `invariant` 從 `_kill_recipe_shape_bad` 拿掉(它只影響 `--invariant` 片段過濾與顯示)。不改也不影響合約。

## 固定席(LUMOS-IMPACT)逐條判定
我自己跑了 `lumos impact --diff 1af7228f..fe722c3c`(派工尾端沒附固定席筆記)。固定席 26 篇、第一名直接家是 `Systems/guard-kill.md`。本輪修正差異只動四處:`_guard_kill_pick`/`_kill_recipe_shape_bad`、`_fix_recipe_rerun_notes`(及呼叫端)、`_kill_log_latest`、`_kill_add_try` 三行提示文字,加上測試與筆記。分組判定如下:

- `Systems/guard-kill.md` 兩條 ★INVARIANT★:(a) rc 優先序 survived→1、drifted/abort/error→2。新增的擋下是在跑任何配方之前回 2 的早退,沒有動到結果列的優先序判定,`t_guard_kill_rc_precedence` 4 項綠。(b) `--json` 成功跑完(rc 0/1)時 stdout 恰一行 JSON,rc 2 早退不印 JSON 是明文範圍外;新擋下訊息只走 stderr,`t_guard_kill_json_purity` 6 項綠。未破壞。
- `Systems/bound-tests-gate.md`(固定席綁定測試逐支真跑):我跑了它綁到的 guard kill 相關測試全綠;我沒有跑 `t_bound_tests_gate` 本身(耗時長,且本輪沒改該閘的程式)。未發現破壞。
- 其餘 `★INVARIANT★` 或 `★RISK·守衛面★` 的固定席(授權與歸屬、測試假綠形態、lumos-cli-read 的 search 排除 superseded、design-loop、canary-audit、slim 安裝/卸載、lumos-deinit、cochange-guard、check-r-guard、loop-convergence-recording、pitfalls-code-loop 等):它們只因 `scripts/lumos`、`scripts/test_lumos.py` 這兩支共用大檔被帶進來,合約內容(授權檔頭、deinit 白名單、搜尋隱藏規則、審查帳收斂等)與本輪四處修改的函式沒有任何交集,diff 不碰檔頭、白名單、搜尋、審查帳寫入。未破壞。
- `Systems/代碼審修正關卡.md`(本輪 a1 的家,沒登記合約):行為宣稱「只印、不影響過不過、不寫事件欄位」仍成立;`_fix_recipe_rerun_notes` 新增的 `return []` 與例外都在呼叫端 try 內,不會擋關卡。`t_fix_check_recipe_rerun_note` 6 項綠。

## 備註(未達標不列為 finding)
- a1 修正後,工作目錄新增(未追蹤)或改了沒提交的筆記裡的配方,提醒全程沉默;關卡的 dirty 提示只看有追蹤檔(`--untracked-files=no`)。這是「只看提交」的直接結果,設計上說得通,且只是提醒,我給不出會做出錯行為的場景,所以不立 finding。
- 計劃與 `guard-kill.md` 寫「同 ts 取先出現的,跟合約背書取最新那筆同一個規則」。背書端 `latest = max(..., key=ts)` 平手取先出現,而同一函式取 covers 用 `groups[rid][-1]`(最後一筆),所以「同一個規則」只對 head_sha 那一處成立。文字略寬,行為本身沒錯,未立 finding。

最高等級:minor,blocking 共 0 條
