C1 ✅ 7 個原語(set/append/self-audit/decision-add/decision-supersede/new/archive)全部存在,dispatcher 子指令與 cmd_* 函式一一對應 | 證據: scripts/lumos:14450(set),14454(append),14468(self-audit),14479(decision-supersede),14498(decision-add),14473(new),14508(archive);對應 cmd_set:7296,cmd_self_audit:7325,cmd_append:7343,cmd_decision_supersede:7401,cmd_decision_add:7501,cmd_new:7969,cmd_archive:8030

C2 ✅ remove 為第 8 個寫入原語,commit 93f990b(2026-08-11)新增,help 文字明寫「append 逆操作」/T1 list 項移除 | 證據: scripts/lumos:14463-14467(add_parser("remove", help="list 欄位移除(append 逆操作...")));git log -S 'def cmd_remove' -- scripts/lumos → 93f990b 2026-08-11

C3 ❌ 實際 SCALAR_KEYS 有 9 個鍵,比主張多 pitfall_ask、pitfall_source 兩個(主張只列 7 個) | 證據: scripts/lumos:7035 `SCALAR_KEYS = {"status", "updated", "created", "type", "self_audit", "signed_off", "regen", "pitfall_ask", "pitfall_source"}`

C4 ❌ 實際 LIST_KEYS 有 7 個鍵,比主張多 aliases、pitfall_when 兩個(主張只列 verified_by/plan_refs/related/tags + core_refs 共 5 個);core_refs 於 2026-08-11 加入屬實 | 證據: scripts/lumos:7036 `LIST_KEYS = {"verified_by", "plan_refs", "related", "tags", "aliases", "pitfall_when", "core_refs"}`;git log -S 'LIST_KEYS = {"verified_by"' 確認 core_refs 一筆即 2026-08-11 commit 93f990b 加入(前一版無 core_refs)

C5 ✅ set/append 對白名單外的 key 皆直接 return 2,測試 t_append_block_key_rejected 存在並覆蓋 | 證據: scripts/lumos:7297-7300(cmd_set)、7344-7346(cmd_append);test_lumos.py:1478 `def t_append_block_key_rejected()`

C6 ❌ 主張的四步順序(寫入 tmp → re-parse 驗證 → lint 比對 → os.replace)與實作不符:實作是「先在記憶體對 new_lines 解析出 fields/new_lint → expected_check 檢查(記憶體,非重讀 tmp)→ lint 指紋比對 → 全過才建立 tmp 並 _write_lf → os.replace」,tmp 檔案是在兩項檢查都通過「之後」才建立,不是驗證前就寫入;檢查失敗時根本沒建立過 tmp(tmp 變數尚未賦值),談不上「tmp 丟棄」——finally 區塊的 `if tmp.exists(): tmp.unlink()` 只在正常路徑走完後(os.replace 已把 tmp 換名成 path,tmp 已不存在)才會被跑到,是死代碼式保險而非主張描述的「失敗後丟棄暫存檔」語意 | 證據: scripts/lumos:7270-7294(atomic_write_verify 全函式,尤其 7276 expected_check 用的是本函式內解析自 new_lines 的 fields,不是重讀磁碟 tmp;7286 `tmp = path.with_suffix(...)` 在兩個 raise 之後才出現)

C7 ✅ load_raw_for_edit 讀 raw bytes 拒 BOM(ValueError)、拒 CRLF(ValueError),不靜默正規化,直接報錯 | 證據: scripts/lumos:7238-7239(BOM),7240-7244(CRLF),原函式 docstring 7236-7237 明寫「拒 BOM/CRLF...異常不靜默正規化」

C8 ✅ _write_lf 是以 write_bytes 強制輸出 UTF-8/LF/no-BOM,docstring 明寫不靠 text mode、不靠 Python 3.10 的 newline= 參數(因專案要求 ≥3.8);且被多處呼叫,docstring 自稱「vault 唯一寫入原語」 | 證據: scripts/lumos:7259-7267(_write_lf 函式,7265 write_bytes);呼叫點含 5219、7289、7997、8148、8569、8580、8601、8627、8962、8964

C9 ✅ append 的 dedup 比對用 link_target(),且新增項是逐次 `fm.insert(last+1, f"{indent}- {item}")` 單行插入,結構性保證一項一行,不會把多個 wikilink 併進同一值 | 證據: scripts/lumos:7134-7161(edit_fm_append),7144(link_target 用於 dedup),7155(單行 insert)

C10 ✅ remove 同樣用 link_target() 精確比對(非前綴/basename),未命中回傳 0 命中數,cmd_remove 轉為 rc=2,docstring 明白強調「不命中一律 rc=2」;測試 t_remove_not_found_rc2_file_untouched / t_remove_exact_target_not_prefix 存在 | 證據: scripts/lumos:7166-7192(edit_fm_remove,7168-7169 docstring「★不命中一律 rc=2★」,7182-7185 hits 判斷),7358-7377(cmd_remove,7368-7372 n==0 時 return 2);test_lumos.py:549、573

C11 ✅ remove 清空某 list key 最後一項後,會把整個 key 行區塊一併移除,不留裸鍵;測試 t_remove_last_item_drops_key 存在 | 證據: scripts/lumos:7188-7192(edit_fm_remove 尾段:清完檢查存活項,無則 `del fm[s2:e2+1]`,註解「空 list 不留裸鍵」);test_lumos.py:562 `def t_remove_last_item_drops_key()`

C12 ✅ decision-add 指派新 id 為 `d<max+1>`(_max_decision_id 掃現有最大號 +1),docstring/註解明寫「翻案後永不重用」的 ID 穩定性合約 | 證據: scripts/lumos:7488-7496(_max_decision_id,7489-7491 docstring「新號=max+1...不回收缺號——ID 穩定性合約:翻案後永不重用」),7501,7511(cmd_decision_add: `new_id = f"d{_max_decision_id(fm) + 1}"`)

C13 ✅ decision-supersede 用內容子字串比對(needle in content),多重命中時 raise ValueError 並列出候選(dispatcher 接住轉 rc=2),可用 `#dN` 精確定址;測試 t_decision_supersede_multimatch_rc2 / t_decision_supersede_dN_addressing 存在 | 證據: scripts/lumos:7420-7434(id_mode 的 #dN 分支與子字串比對分支,7429-7434 多重命中組候選字串並 raise),14995-15037(dispatcher 對 decision-supersede 的 except (ValueError,...) → return 2);test_lumos.py:754、766

C14 ✅ decision-supersede 對已有 superseded_by 的決策拒絕重插(raise ValueError「已翻盤過,不重複 supersede」) | 證據: scripts/lumos:7443-7446(迴圈檢查同 sub_indent 是否已有 `superseded_by:` 行,命中即 raise)

C15 ✅ decisions 區塊要求標準 2-space 縮排,遇到 0-indent/非標準縮排時 decisions_items 解析不到項目,cmd_decision_supersede 直接 raise ValueError 報錯,不自動轉換;cmd_decision_add 亦依 decisions_items 回傳結構(item_indent/sub)手術插入,同樣不做自動縮排轉換 | 證據: scripts/lumos:7414-7416(cmd_decision_supersede: `if not loc[2]: raise ValueError("decisions 區塊解析不到項目...不支援 0-indent/tab")`),7203-7226(decisions_items 解析邏輯:只認最淺層 dash 縮排為 item_indent)

✅12 ❌3 ❓0 ⏭0
