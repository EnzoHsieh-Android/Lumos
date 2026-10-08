severity: minor

回滾與相容鏡頭逐項核對(已對 negguard repo 的程式與測試查證):
- `_notes_touched_in_range` 抽取:既有測試換 `_ns_git` 的做法只看 `"log" in args`/`"--follow" in args`,抽共用函式且照走模組全域 `_ns_git` 不會壞;已讀,無 finding。
- 範本載入抽共用、`_note_audit_judge_model` 加參數、`_note_audit_resolve` 加選配參數:既有呼叫端都靠預設值不變;`_note_audit_prompt` 現況是鏈式 replace,改一次掃描對正常輸入逐字相同;已讀,無 finding。
- `_BOOKKEEPING_DIRS` 加一項:實際五個消費者(小改動閘、風險掃描、風險分級、推送前測試範圍、留痕有效性)都吃同一個 tuple,spec 的「五個」屬實(程式註解寫「三個」是舊註解);其他地方沒有另抄一份目錄清單;已讀,無 finding。
- `_VENDORED_TREE_FILES` 與 `lumos update`:更新迴圈只複製表上的檔、逐檔比對測試要求「表=受版控檔」,新範本須同提交 git add;已讀,無 finding。
- 回退:revert 同提交 git rm 紀錄資料夾的做法對得上豁免撤掉後的留痕檢查;已讀,無 finding。
- 掛鉤與 lumos 版本偏斜:新掛鉤配舊 lumos 為 argparse rc2 放行,舊掛鉤配新 lumos 沒人呼叫;已讀,無 finding。
- 上線點標記 `note-audit reread-check` 不含 `note-audit check` 子串,`-S` 與 doctor 的子字串判斷互不干擾;已讀,無 finding。

## F1 「跟筆記內容審無相依」的先後順序講錯,改筆記會讓筆記內容審的判定失效
severity: minor
blocking: 否
引句:「先後順序:跟筆記內容審、存量漂移表態無相依,建議放在代碼審留痕之前(改筆記會讓留痕失效)」
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:53`
1. reread 的收尾動作是「照點出的行改筆記」。既有筆記內容審流程第 4 步寫明「改了就是新的一行,要再 prepare 判」,而它的輕判定要「那行的上下文沒變」才收(`_note_audit_check_evidence` 旁的 `cur_ctx` 比對)。
2. 所以作者若先完成筆記內容審 record、再做 reread 並改筆記,被改到的行與鄰行在筆記內容審那邊變成未判或判定失效;筆記內容審一旦接線(掛鉤裡出現 `note-audit check`),推送會被擋。存量漂移表態(`drift ack <節點> <行號>`)綁行號,改筆記行數也可能讓它對不上。
3. 照字面寫進 skill 第 6 小節(S14 只驗有提到 reread-prepare/record/提交),作者會被教成「無相依」。目前筆記內容審沒接線(掛鉤與 CI 都沒有 `note-audit check`),所以現在不出事,屬 minor;放行理由:提醒版只提醒、且接線另案,但該句應改成「reread 先做,再做筆記內容審與表態,最後代碼審留痕」,或至少不寫「無相依」。

## F2 既有測試 `t_prepush_gates_stop_on_signal` 寫死掛鉤裡恰有五行 pp_stop_if_signaled,spec 沒列要一起改
severity: minor
blocking: 否
引句:「這是掛鉤裡唯一不照「128 以上一律停」的一段」
file: `scripts/test_lumos.py:51282`
1. 該測試用 `^[ \t]*pp_stop_if_signaled "\$[a-z]+_rc".*\n` 數掛鉤裡的停下行,並斷言 `n == 5`(前置)。spec S9 要求 reread 那段「只在回傳碼 130 時交給 `pp_stop_if_signaled`」。
2. 若實作寫成多行 `if [[ "$rr_rc" -eq 130 ]]; then` 換行後獨立一行 `pp_stop_if_signaled "$rr_rc" ...`,正規式就多命中一行,n 變 6,既有測試前置翻紅;寫成單行 `&&` 則不命中。兩種寫法 spec 都沒指定,也沒把這支測試列入要更新的清單(純新增踩到計數測試的典型)。
3. 影響小:實作者跑掛鉤相關測試子集即知,放行理由如此;建議 S9 或〈實作紀錄〉註明「該測試的計數與註解(五道)同步改」,並保證新段的寫法不被該正規式誤數或一併改測試。

最高等級:minor;blocking 共 0 條
