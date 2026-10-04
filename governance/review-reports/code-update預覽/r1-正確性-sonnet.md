severity: major

## F1 預覽印的區塊差異把「最後一行被刪的內容」和「第一行被加的內容」黏成同一行
severity: major
blocking: 是
引句:「(old_start_line + "\n" + old_body).splitlines(keepends=True),」
file: `scripts/lumos:20337`(`_reinject_compute` 組 unified diff 的那段;`_preview_rule_target` 用 `it["diff"].splitlines()` 逐行印)
重現(已在臨時目錄跑過):
1. 照 `_upd_dry_fixture` 搭消費專案,CLAUDE.md 裡舊區塊是 `<START v0 -->\n舊\n<END>`(舊 body 一行,結尾沒有換行),來源範本是 `專案版:{{KG}}\n`。
2. 跑 `lumos update --dry-run --source <來源>`。
3. 輸出的「完整區塊差異」出現這兩行:`-舊+<!-- LUMOS:GRAPH-DISCIPLINE:START v1.2 ... -->` 與下一行 `+專案版:docs/p-knowledge/`。
原因:被拿去 diff 的兩串字(`old_start_line + "\n" + old_body` 與 `start_line + "\n" + new_body`)結尾都沒有換行。`difflib.unified_diff` 對沒換行的最後一行不補換行,也不印 `\ No newline`。只要「最後一行有差」,舊的最後一行(`-`)就跟新的第一個加入行(`+`)連在一起。這是最常見的情況,因為範本改動多半落在 body 尾端。
後果:計劃〈做法〉3 要「印區塊的完整差異」給使用者決定同不同意改規範檔,讀的人會看到一行被黏壞的 `-…+…`,分不清哪行被刪、哪行被加。套用時寫進檔的內容不受影響(新內容走 `new_text`),所以只是預覽的差異顯示壞掉。
測試為什麼沒抓到:`t_update_dry_run_rule_diff_matches_apply` 只用 `in r.stdout` 找 `-舊版紀律:docs/p-knowledge/` 與 `+新版紀律:docs/p-knowledge/`,黏壞的那行仍然含有這兩段子字串,所以是只驗字串長相的假綠。
舊程式的 diff 字串本來就是這樣組的(舊版套用時最多印 20 行摘要時同樣黏壞),但這次把它當成「完整差異」交給使用者核可,黏壞就變成這個功能的缺陷。

## 已走過沒問題的範圍
- 套用行為有沒有變:用舊版(基準提交)與新版的 `_reinject_claude_block` 各跑 1800 組輸入對照(CLAUDE.md、AGENTS.md、AGENTS.override.md;目標檔不存在、無區塊、有區塊且舊、有區塊且一樣、標記半壞;LF、CRLF、CR;有無 BOM;有無範本;範本有前導空行的標題與無標題檔),回傳狀態、差異字串、寫出的位元組完全一致,零差異。讀不了的檔(非 UTF-8、是資料夾)在套用端仍然往外丟例外,跟舊版一樣。
- 預覽與套用一致:在臨時專案搭 BOM+CRLF 的 CLAUDE.md、CRLF 的 AGENTS.override.md(同時存在 AGENTS.md,正確只選 override)、來源沒有範本只有專案有範本三種狀態,預覽算出的 `new_text` 與接著真的套用後的位元組一致;LUMOS_VERSION 兩邊是同一個程式程序,版本戳一致。
- 預覽不寫檔:前後比對整棵專案目錄位元組、家目錄、`core.hooksPath`、來源提交編號,全部不變。`_py314_upgrade_pending` 只讀檔;`_reinject_targets` 只做 exists 判斷;`_scaffold_project` 與 `_init_additive_setup` 不會寫工具檔清單內的檔,所以套用端結尾自癒清單跟預覽的 `_vendored_pending` 在套用前後算出來一致。
- 回傳碼:來源無效回 2、沒有 vault 回 3(跟套用同一條路)、目標檔是資料夾回 2 並印「讀不了」、`--allow-stale`、`--no-pull`、`--source` 相對路徑與在子資料夾執行都照常預覽且不寫檔。來源 repo 自身標記壞掉或沒範本回 2,跟套用一致。
- `LUMOS_PROBE=1` 下 `--dry-run` 也被擋成回 2。預覽本身唯讀,所以拒絕只是偏保守、不會造成錯誤寫入,計劃對此沒有規定,不列為問題。
- 圖譜鏡頭:派工尾端沒有附固定席筆記,也沒有備援段,無從逐條判斷;本案改動只新增唯讀旗標與兩支抽出來的函式,沒有看到破壞 doctor Check D 或 init 注入的路徑(兩者都仍呼叫 `_expected_claude_body` 與 `_reinject_claude_block`,行為經上面 1800 組對照確認不變)。
- 角色卡:派工沒有附卡,略過。
- 測試:另外五支(S1、S3、S4、S5、S6)在舊程式上因為 `--dry-run` 不認得、或 `_update_rule_plan` 不存在而翻紅;S1 只比對檔案不比對空資料夾,但預覽路徑沒有任何建資料夾的呼叫,不構成具體失敗場景。

一條會讓使用者看到壞掉的區塊差異的缺陷,其餘範圍沒找到問題。
