severity: minor

已讀全文並對照程式:`_note_audit_resolve`、`_push_range_start`、`_lens_push_base`、`_nodehome_name_status`、`_nodehome_list`、`_nodehome_side`、`_nodehome_golive`/`_nodehome_clamp_base`、`_notes_status_flipped`、`_write_lf`、`_note_audit_write_verdict`、`cmd_note_audit_record`、`_BOOKKEEPING_DIRS` 五個消費者、`scripts/hooks/pre-push` 的 drift 段與 `pp_stop_if_signaled`、CI 的 drift 步。空範圍、新分支首推、force push、合過主線、改名加刪檔、`[`/`*` 檔名、設定壞值、紀錄資料夾不存在、報告歪格式,在 spec 的算法下都走得通,沒找到照字面實作會做出錯行為的 blocking 級問題;前兩輪折法(指紋只看程式那一半、頂端無資料夾=沒紀錄、`--literal-pathspecs`、130 才停)對照程式現況也沒做錯或漏落實。以下三條都是 minor,附理由放行。

## F1 紀錄資料夾第一次寫入時沒交代要建
severity: minor
blocking: 否
引句:「自己的檔名正規式(`_write_lf` 中斷留下的 `.tmp-wlf` 不合、不算);用 `_write_lf` 原子寫入。」
file: `scripts/lumos:14978`
1. spec 把 `governance/reread-verdicts/` 說成「新資料夾」,又指定用 `_write_lf` 寫檔;`_write_lf` 只做暫存檔加 `os.replace`,不建父資料夾(讀 14978 行起的函式本體)。
2. 既有的判定檔寫入 `_note_audit_write_verdict`(26037 行前後)在寫之前明確 `d.mkdir(parents=True, exist_ok=True)`;spec 沒寫 reread-record 要照做。
3. 照字面實作,在沒有這個資料夾的專案第一次 record 會丟 FileNotFoundError。S5 的測試多半會在第一次跑就紅,所以只是提醒實作者補一句「先建資料夾」,不影響設計。

## F2 非 UTF-8 檔名的測試檔會讓 prepare 寫檔當掉
severity: minor
blocking: 否
引句:「另加同套件目錄裡沒有家的測試檔(<檔名用、分隔>)」
file: `scripts/lumos:23688`
1. 改動清單走 `_nodehome_name_status(norm=False)`,它用 `os.fsdecode` 解路徑;非 UTF-8 的檔名會變成含代理字元的字串(實測 `os.fsdecode(b"t\xff.py")` 再 `.encode("utf-8")` 丟 UnicodeEncodeError)。
2. 補測試檔判「是測試、同一層」不看檔名是否 UTF-8(`_nodehome_is_test` 不排除),所以檔名含 Latin-1 位元組的測試檔會被補進 `{{TRUNC}}` 與 `{{OTHERS}}` 的檔名清單。
3. 項目檔用 `_write_lf` 寫,內部 `text.encode("utf-8")` 遇到代理字元會丟例外;reread-prepare 不是 fail-open 的子指令,那一篇整個當掉。只有「範圍裡改到這種檔名的測試檔」才會發生,很少見;實作時檔名先過 `_nodehome_show` 之類的替代字元處理即可。

## F3 「頂端已在主線」與「刪除分支」在治理帳裡該記什麼,spec 兩處說法對不上
severity: minor
blocking: 否
引句:「reread-check 用這個參數,原因由自己印、事件由自己記一筆」
file: `scripts/lumos:26127`
1. 第 1 節把「刪除分支、頂端已在主線」列成範圍解析的提早結束原因、要 reread-check 自己記一筆;第 4 節與 S7 列舉「一律記 skipped」的情境裡沒有這兩項(S7 有刪除分支、沒有頂端已在主線)。
2. 既有程式對這兩種的處理不同:刪除分支只印不記帳(26115 行),頂端已在主線記 `skipped`(26127 行)。實作者要自己選。
3. 若一律記 `skipped`,〈做法〉第 5 節量「有候選的推送占比」時,「已經合過主線、沒有新東西」的推送會被算進 `skipped` 而不是 `none`,分母偏。只影響兩週量測的口徑,不影響行為;實作時在第 4 節補一句歸類即可。

最高等級:minor;blocking 共 0 條
