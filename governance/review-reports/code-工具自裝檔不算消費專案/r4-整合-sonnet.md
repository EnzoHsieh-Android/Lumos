severity: minor

### F1 about_code_key 目錄不可讀時悄悄退回字面比對,跟 F23 擋下的精神不一致
severity: minor
blocking: 否 — 只造成 about_code 清單多出語意重複的項目,影響排序加分準確度,不影響資料完整性或寫入正確性
引句:「回 (真實拼法, None);某一層目錄讀不到檔名清單回 (None, 那一層目錄)——擋不擋由呼叫端決定」
1. `_about_code_path`(F23 的修法)目錄讀不到時回傳擋下理由、rc2 不寫入;但 append 去重與 remove 找項共用的比對鍵 `_about_code_key` 拿到同一個「讀不到」訊號時,直接丟棄那個訊號、退回純字面正規化(`real, _ = _disk_spelling(root, rel)` 把 `_disk_spelling` 回傳的第二個值──也就是「讀不到」標記──用 `_` 接掉)。
2. 場景:同一支檔已用兩種拼法(例如 `SRC/A.TS` 與 `src/a.ts`)寫進不同筆記,若該檔所在目錄暫時不可讀(防毒鎖檔、網路磁碟瞬斷),append 新增或 remove 移除時 `_about_code_key` 會把兩種拼法當成不同檔,既不會去重、也可能用另一拼法刪不掉。
3. file: `scripts/lumos:10980` `_disk_spelling` 明文說「擋不擋由呼叫端決定」,file: `scripts/lumos:11012` 這個呼叫端沒有接手這個決定,是 F23 修法唯一沒覆蓋到的第二入口。

## 第三輪修法驗收

F19:修到 — `_multi_link_value` 讀寫共用同一判斷,`t_multi_link_list_value_one_rule` 本機執行 14 條全過
F20:修到 — `_SEV_SUMMARY_LINE_RE` 改行首錨定、"0 條" 只剝計數語境;兩處分別還原後重跑 `t_report_normalize_cmd`,各自翻紅(1 條 / 3 條斷言失敗),已機械重現
F21:修到 — `_about_code_path` 先把反斜線轉斜線,子測試⑭「src\a.ts」存成 src/a.ts 通過
F22:修到 — `_about_code_key`+`_disk_spelling` 以磁碟真實拼法比對,子測試⑮b「SRC/A.TS 與 src/a.ts」判同檔通過
F23:修到(見上方 F1)——`_about_code_path` 端已擋下且子測試⑯通過;但同一責任在 `_about_code_key` 端沒有對稱覆蓋,算新洞不算沒修到
F24:修到 — `_vendored_state` 改內容指紋比對;還原成純路徑比對(`present, present`)後重跑 `t_pitfalls_diff_ignores_vendored_toolchain`,子案例③b 翻紅,已機械重現
F25:修到 — mkstemp 動態檔名 + `_vault_write_lock`;分別還原兩處後重跑 `t_concurrent_append_same_note`,①、②子案例翻紅,已機械重現
F26:修到 — symlink 別名納入同一比對鍵,子測試⑮「link/x.ts 與 real/x.ts」互通、remove 用別名刪得掉
F27:修到 — `[a]` 擋下訊息不再講「看不懂逗號」,對應子測試通過
F28:修到 — `_posix_norm` 單一函式,`_about_code_key`/`_about_code_path`/`_impact_about_counts`/`_impact_mark_about` 四處共用同一份(讀碼確認,無各寫一份的殘留)
F29:修到 — `_impact_mark_about` 改用 `_posix_norm`,`t_impact_about_hit` 子測試⑮「src/../src/svc.py」仍命中,本機執行通過
F30:修到 — cmd_new 回掛例外改抓 `(OSError, ValueError, RuntimeError)`,`t_new_verification_backlink_blocked_still_says_note_created` 三條斷言本機全過
F31:修到 — 帶引號的舊項照原樣搬移(`quoted` 分支);還原成一律 `fmt_list_item(sval)` 後重跑 `t_append_about_code_is_one_list_rule`,翻紅,已機械重現
F32:修到 — `_SINGLE_WIKILINK_RE.fullmatch` 判斷前先 `strip()`,QG(巢狀清單開頭像連結)、QH(引號內前導空白)兩種繞法測試通過
F33:修到 — remove 對 `_about_code_key` 相同的每一種既有拼法逐一呼叫 `edit_fm_remove`,子測試⑫「兩種寫法一次都拿掉」通過
F34:修到 — `_need_src("skills/lumos-project-notes/SKILL.md")` 只在工具鏈本體跑,本機執行 `t_vendored_file_list_matches_what_install_ships` 未被跳過且通過(證明本機是工具鏈本體、真的跑到比對邏輯)
F35:修到 — `_vendor_toolchain` 改成只複製 `_VENDORED_TOOLKIT + _VENDORED_TREE_FILES` 精確清單;`t_vendored_file_list_matches_what_install_ships` 本機執行,清單與 `git ls-files` 逐檔比對零落差

風險掃描清單(r4-manifest.json)2 條:
- `scripts/lumos:10902`(`_vault_write_lock` 內的 `open(...)`):誤報 — 整段被外層 `try/finally` 包住,即使逾時拋 `RuntimeError` 也會走到 `fh.close()`,沒有洩漏路徑
- `scripts/lumos:17884`(`_stack_changed_ok` 的 `open(`):誤報 — 命中處在 docstring 字面文字「命中 `open(...)`」裡,不是可執行程式碼,regex 掃描器誤判

總結:最高 severity minor,blocking 共 0 條
