severity: minor

本輪補修沒有發現破壞合約的問題。`t_docs_command_count` 綠,`-k t_choice_layer` 55 支全過。差異裡新寫的 `[test:]` 名稱在 `scripts/test_lumos.py` 都找得到。判讀檔的讀者和 `_note_audit_write_verdict` 呼叫端都沒漏:

- **`cite` 欄的讀者**:只有 `_choice_layer_text`,缺 `cite` 時退成「(出處讀不到)」,不會崩。
- **`_note_audit_write_verdict` 的四個呼叫端**:都沒被補修動到。
- **`_CHOICE_LAYER_DIR`**:已在 `_BOOKKEEPING_DIRS`。
- **層值範圍**:`_gov_choice_count_layer` 與 `_choice_ledger_aux` 都收 0 到 4,一致。
- **指令總數 103**:`ARCHITECTURE.md`、`reference.md`、`INDEX.md` 都已是 103,沒有殘留的 102。
- **drift scan**:輸出沒有點到這次改動的筆記。

以下兩條是文件措辭不一致,都不會讓照做的人做錯。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:75` 與 `:77`:合批編譯的 WHY 與 PITFALL 仍寫「每個嫌疑單獨再編一次、單獨也紅才算無效」,沒提一批最多確認 8 個。這個上限只寫在 `Systems/規格閘.md:127`,程式在 `scripts/lumos:29391`(`_CHOICE_COMPILE_SOLO_MAX`)。三個月後從 guard-kill 這個家讀,會以為嫌疑全部確認。
引句:「修法:錯誤所在檔有壞法就把那支檔的壞法都列成嫌疑、逐個單獨確認(受編譯預算管),錯誤落在沒有壞法的檔才算對不回」

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Issues/選擇點存活回指第一段末輪小問題第二段先修.md:57` 與 frontmatter 第 15 行:r2 補了第 15 條且仍未修,但「什麼條件算修好」與 summary 仍只寫「剩第 8、9 條」,沒有把第 15 條列進去。議題狀態是 open,別人照這兩處會以為只剩兩條。
引句:「第 15 條(第三段代碼審 r1 資源 #1 放行):推送閘對範圍內全部有壞法的行算判讀狀態(讀判讀檔、算 deps_sha),大專案可能逼近 30 秒預算」

總結:最高等級是 minor
