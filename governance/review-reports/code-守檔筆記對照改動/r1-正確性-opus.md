severity: minor

# 代碼審 r1 正確性-opus(主審 r1-snapshot-code.patch)

實驗環境:`git clone --shared` 到 `hcc-r1-work-正確性-opus/repo`(HEAD 94e28375),另建小型 repo s1–s4 端到端跑 reread-check / reread-prepare / reread-record;`-k reread`(88 passed)、`-k notes_touched`(7 passed)。

## F1 reread-prepare 不排除已對照過的筆記:照提醒印的指令貼,會替已經有紀錄的筆記再產項目檔、再派判定者
severity: minor
blocking: 否
引句:「got, why = _note_reread_item(root, scan, rel, orchestrator, base, tip, codeish)」
佐證:file: `scripts/lumos:27060`(prepare 逐篇走 `scan["cands"]`,沒有對 `_note_reread_committed` 過濾)
佐證:file: `scripts/lumos:27228`(check 只列 `fps[rel] not in done` 的那幾篇)

1. check 列的是「候選裡還沒有同指紋已提交紀錄」的那幾篇,並叫人貼 reread-prepare;prepare 卻對全部候選產項目檔,不看已提交紀錄。兩邊的篇數對不上,已對照過的那幾篇會被重派(計劃〈實務隱患〉估每篇約 0.17 美元)。
2. 具體場景:一次推送有兩篇家筆記要對照,先把 A 對照完、記錄、提交;再推時提醒只列 B,照印的指令貼卻產出 A、B 兩份,訊息也說「這次要回頭重讀 2 篇」。
3. 重現(s4:A 管 src/a.py、B 管 src/b.py,兩支程式與兩篇筆記同一個提交改;先 prepare、只記 A、提交紀錄):
   ```
   === check
   回頭重讀提醒:這次改到的程式,有 1 篇守檔筆記這次也改了、還沒對照過這一版程式(已對照 1 篇)——…
     docs/p-knowledge/Systems/B.md  (對照指紋 9e23a4976388271a)
   === prepare (printed command)
   這次要回頭重讀 2 篇守檔筆記(…);每篇一份項目檔,各派一席 sonnet(…):
     Systems/A.md
     Systems/B.md
   ```
4. 不會做出錯的判定(只提醒、不擋),只會浪費判定者的費用、讓人搞不清楚要派幾席,所以列 minor。修法方向:prepare 也用 `_note_reread_committed(root, tip)` 與同一支 `_note_reread_contrast_fp` 濾掉已對照的(或至少印「其中 N 篇已對照過,可略過」);計劃〈做法〉1 的「每篇候選一份」要一起改寫。

## 其餘查過、沒有問題的(不列 finding)
- 兩個指紋:prepare 跟 check 都用 `_note_reread_about(scan, rel)`(只取頂端那邊)配 `scan["oids"]`(`_nodehome_list` 填的是 NFC 路徑),`_nodehome_key` 也是 NFC,所以 NFD 檔名(實測 `src/café.py` 存成 NFD)、`[id].py` 這類檔名都查得到 blob。record → 提交 → 照判定改筆記 → 再 check,都判成已對照(s1 實跑)。改動只在 bside 的 about_code 那一側、或只改補進來的測試檔時指紋不變,這在計劃〈誠實界線〉已經寫了,不當 bug 報。
- diff 組法:改名的新舊路徑都進 pathspec(`_nodehome_name_status` 的 paths 本來就收兩端),`--literal-pathspecs` 讓 `src/[id].py` 不會把別支檔帶進來,補測試檔(同層)有進 diff(s3 實跑)。截斷那段跟實驗的 `vcommon.truncated_diff` 逐行相同;分到的字數小於標記長度時會變成負數、`p[:負數]` 讓輸出超過上限(cap=200 時實測輸出 3375 字元),但要一篇筆記一次改到約 4000 支檔才會碰到,這個 repo 最大的 about_code 只有 23 項,所以不列。
- record:json 區塊取最後一段完整的、行號擋布林與超出範圍、重複只留第一次、原句從項目檔頭的 blob 讀、來源對不上照收並標 false,都照計劃;0 行也寫一份紀錄,提醒消得掉。
- check:開關在範圍解析之前、從頂端讀;全 0 終點記 none;結果只走標準輸出,最外層只接 Exception;`ls-tree <頂端> -- governance/reread-verdicts/` 在資料夾不存在時回空集合、不會被當成 git 失敗。在本 repo 做一個「改 scripts/lumos + 改 Systems/筆記內容審.md」的提交,帶推送參數與不帶都有列出,各約 1 秒。
- 設定讀取:四種壞設定、block 照 warn、off 不寫帳,都照計劃。
- 範圍解析新參數:`reasons` 不給時每個分支的印出與寫帳跟原本逐字相同(既有 5 個呼叫端都沒給);給了之後不印、不寫帳,種類分成 none/skipped/error,check 與 prepare 的處理都對。
- 抽出/改過的既有函式:`_notes_touched_in_range` 保留了截止時間檢查、git 失敗回 None、`.md` 篩選加排序去重,`_notes_status_flipped` 行為不變;`_note_audit_prompt` 改成一次掃描替換,判定範本只有 REPO_PATH/STACK/PROMPT_VERSION 三個佔位字,輸出相同;`_note_audit_judge_model` 預設用途還是回 opus/Codex 常數。
- 上線標記:改動前後推送前掛鉤與 ci.yml 裡「note-audit check」出現次數都是 0,筆記內容審找上線點不受影響。

最高等級:minor
