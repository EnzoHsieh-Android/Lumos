# code-codex-refine r2 intake(2026-09-05,2 席:delta回歸-sonnet / 外家finder-codex)
收貨:外家 1/1 錨定;delta 9 句 1 句錨不到(其餘 8 句錨定,refcheck 14/14)。
## 外家finder 1 條 major:標記目錄是 symlink → 先 chmod/清理目標才檢查 HIT(重現:symlink→victim,舊檔被刪):mkdir(0700) 後先過 _stop_dir_ok(symlink 直接 False)再 chmod/清理;測試⑲。
## delta回歸 5 條:1 blocker 1 major 2 minor 1 clean
- blocker 名額先佔後 print 失敗(ASCII locale UnicodeEncodeError)→ 名額白燒 HIT(重現 LANG=C):改 bytes 寫 stdout,寫不出去退回名額;測試㉑(LANG=C 仍送出 block)。
- major 檔名裡的反引號跳出 code span HIT:_safe_path 反引號→單引號,mentions 也包反引號;測試⑳。
- minor chmod 失敗靜默停用 HIT:stderr 一行(給 log;Codex 模型看不到,誠實界線)。minor 載入 scripts/lumos 失敗變儀器例外 HIT:try/except 退回同語意預設+stderr 一行。
辯方:兩席 findings 皆附翻紅重現,無低共識,未開庭。
