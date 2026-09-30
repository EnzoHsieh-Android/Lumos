severity: minor

# 代碼審 r2 正確性-opus(審 r2-snapshot.patch,94e28375..94c1e82f)

實驗環境:`git clone --shared` 到 `hcc-r2-work-正確性-opus/repo`(HEAD 94c1e82f);子集 `-k note_audit` 285 passed、`-k code_loop` 31 passed、`-k nodehome_side` 3 passed、`-k bookkeeping` 41 passed。另寫兩支小腳本(借 test_lumos 的 `_rr_*` 輔助函式)端到端跑 prepare/record/check,並把新舊兩版 `_codeloop_record_valid` 拿真的提交歷史逐對比較。

## F1 prepare 預設只略過「已提交」的紀錄:check 明講「工作目錄有紀錄、還沒提交」的那幾篇,照它印的指令貼 prepare 會整批重產、一句都沒提
severity: minor
blocking: 否
引句:「todo = [rel for rel in scan["cands"] if fps[rel] not in done]」
file: `scripts/lumos:27139`(prepare 的 `done` 只來自 `_note_reread_committed(root, tip)`,也就是頂端提交樹)
file: `scripts/lumos:27340`(check 另用 `_note_reread_uncommitted` 找出工作目錄裡已有紀錄的篇數並印出來)

1. 第 1 輪正確性 F1 要解決的是「照 check 印的指令貼 prepare,已對照過的篇又被派一次、白花判定者的錢」。這次修法只看已提交的紀錄。還有一種同樣常見的情況沒蓋到:記完紀錄、忘了提交就推。
2. 這時 check 把那幾篇照樣列成「還沒對照」(這沒錯,它本來就只認已提交的),另外多印一行「其中 N 篇在工作目錄有對照紀錄、還沒提交:git add … && git commit」,接著又印「對照一次:lumos note-audit reread-prepare …」。人照最後那行貼,prepare 會把工作目錄裡已經有紀錄的每一篇重新產項目檔,輸出也沒提到其實已經有紀錄、只差提交。結果就是重派判定者,正是第 1 輪要堵的浪費。
3. 重現(兩篇 A、B,兩支程式與兩篇筆記在同一個提交裡改;prepare → 兩份都 record → 不提交 → check → 再 prepare):
   ```
   === check (records written, not committed)
   回頭重讀提醒:這次改到的程式,有 2 篇守檔筆記這次也改了、還沒對照過這一版程式(已對照 0 篇)——…
     docs/kg-knowledge/Systems/A.md  (對照指紋 d3b8da5c06eaea46)
     docs/kg-knowledge/Systems/B.md  (對照指紋 18055c7b660a769d)
     其中 2 篇在工作目錄有對照紀錄、還沒提交:git add governance/reread-verdicts && git commit
   對照一次(…):
       lumos note-audit reread-prepare --diff 6296f0c6…..HEAD --orchestrator <claude 或 codex>
   === prepare again (pasting the printed command)
   0 這次要回頭重讀 2 篇守檔筆記(…);每篇一份項目檔,各派一席 sonnet(…):
     Systems/A.md
       項目檔:…/reread-66ec9e72f4ebd22b-claude.md
     Systems/B.md
       項目檔:…/reread-d5ac3fa2c8512648-claude.md
   ```
4. 這不會讓判定出錯(整條路只提醒、不擋),只會多花錢、讓人搞不清楚要不要重派,所以列 minor。修法方向有兩種:讓 prepare 也用 `_note_reread_uncommitted(root)` 和同一份 `fps` 過濾,碰到只差提交的篇就不產、改印「N 篇已有紀錄、還沒提交:git add … && git commit」(`--all` 照舊全產);或者至少在 check 裡,工作目錄的紀錄已經涵蓋全部 `left` 時,不要再印「對照一次」那行 prepare 指令。

## 其餘照派工詞逐項查過、沒有問題的(不列 finding)
- **資料夾守衛接進筆記內容審的 prepare/record/skip 之後**:三處都只多了「守衛拒用 → 印『擋下:<原因>』、rc2」這一條分支,插在原本 mkdir/寫檔的位置;守衛放行時,建資料夾、檔名、內容、.gitignore 都跟原本一樣(`.gitignore` 從「第一次建或不存在就寫」改成「不存在就寫」,兩者等價)。`_note_audit_write_verdict` 與 `_note_audit_work_dir` 全 repo 只有 patch 裡改到的這些呼叫端(另有兩支測試),回傳值改成二元組之後沒有漏改的呼叫端。工具自己不會把 `.lumos` 或 `governance` 建成符號連結(全檔 `symlink_to` 只出現在 skill 安裝與 lint 快照的依賴目錄),正常專案不會被誤擋。`--repo` 會先 resolve,不帶時 git 給的 toplevel 也是實體路徑;守衛兩邊都 resolve 後再比,所以根目錄在 /tmp 這類系統層連結底下也不會誤判。
- **`_nodehome_side` 不傳截止時間**:新加的只有 `if deadline is not None and time.monotonic() > deadline: return None` 這一行,`time` 是模組層就 import 的。不傳時逐行等同原本;既有四個呼叫端(`home check` 兩處、`_nodehome_*` 兩處)都沒傳。回頭重讀的掃描拿到 None 時,由 `_note_reread_fail` 依截止時間判斷是逾時還是 git 失敗,訊息也對。
- **`_note_audit_write_verdict` 不給新參數**:`dirname or _NOTE_AUDIT_VERDICT_DIR`、`prefix=""`,檔名格式 `<UTC 時間>-<32 位亂數>.json` 與內容序列化照舊,只多回一個 `why`。既有的原子寫入測試(中途被殺不留合格式檔名的半殘檔)照綠。
- **留痕有效性(關掉改名偵測、`-z`、簿記資料夾裡的程式副檔名不算簿記)**:把新舊兩版 `_codeloop_record_valid` 在工具鏈主 repo 最近 400 個「父提交 → 子提交」上逐對比較(只做唯讀 git),結果**舊版判有效的,新版全部仍判有效**;兩版不同的 11 對全是「舊版判失效 → 新版判有效」,原因都是簿記資料夾底下的中文檔名(例如 `governance/replay/筆記內容審/verdict.json`)舊版被 core.quotepath 加了引號、比不到前綴。檢查歷來「記錄代碼審通過」的帳本提交,動到的只有 `docs/.*-log.jsonl`、`governance/anchor-baseline.json`、`.lumos/lint-waivers.json`(最後這支本來就不在簿記名單裡,不是這次改出來的);`governance/code-loop/` 的留痕與表態檔都是 `.json`。所以合法的留痕情境沒有被新判法誤判失效。
- **prepare 預設略過**:比對用的指紋走 `_note_reread_fps`,跟 check 同一支,也跟 `_note_reread_item` 算 cfp 的口徑一致(都只看頂端的 about_code 配頂端 blob),帶或不帶推送參數得到同一個指紋。`_note_reread_committed` 回 None 時退回全部照產並講一句;全部都對照過時在範本檢查、建工作目錄之前就 rc0 返回,不會多產檔。實跑非 UTF-8 檔名的筆記:prepare → record → 提交 → check 判「都對照過」→ 再 prepare 判「已對照 1 篇,略過」,整串都不會當掉。
- **控制字元與路徑清洗**:`_NOTE_REREAD_CTRL_RE` 的範圍和 `_esc_clean` 相同。項目檔頭只有「筆記路徑」一個欄位來自外部,已經過清洗;重複欄位整份不收,不會誤傷合法的項目檔,因為檔頭是固定行、本文在「---本文---」之後,解析也只讀前段。

最高等級:minor
