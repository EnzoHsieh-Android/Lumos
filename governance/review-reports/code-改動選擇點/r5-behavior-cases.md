# code-改動選擇點 r5 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 04b21d1ff80fbbd37a3917cfd86fd90c4cc23e7e(第四輪派工單 base_commit)、修後見 r5-repair-binding.json 的 after_commit。來源:計劃 docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md 的條款與〈用詞〉。本輪是人裁再破例加開的第 5 輪(第二筆 cap-decision extra-round,使用者親裁)。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| K1 | repair | 被改檔名含 `$(touch PWNED)` 與空白,某行前後各 2 行都相同(不唯一)→ choice-kill 印的照貼 lint-waive 指令用 shlex.split 解回來,第二個參數等於 `choice:<原檔名>:<行>`;貼進 shell 不執行、不切開 | 〈存活的處置〉 | t_choice_kill_waive_hint_shell_quote |
| K1 | preserve | 一般 ASCII 檔名的不唯一行 → 印出的指令照舊可貼、放行鍵與 lint-waive 認得的 choice: 鍵相同 | 〈存活的處置〉、S22 | t_choice_kill_waive_hint_shell_quote、t_lint_waive_choice_ai_summary |
| K2 | repair | 推送前那一圈判定:碰到的計劃只算一次,後段 `_choice_guard` 拿到同一份快取;拿掉傳快取 → 測試紅 | 〈範圍〉4 | t_spec_gate_push_choice_guard_cache |
| K2 | preserve | 推送前判定的擋與放(有效處置、上限、生效日、看被推送版本)結果與第四輪相同 | S19–S22 | t_spec_gate_push_choice* |
| K3 | repair | 綁名 `FooTest.bar`,`bar` 只定義在不含類別名的測試檔 → 找得到該檔、改它雜湊變;改成取第一段 → 紅 | S11 | t_choice_test_blobs_name_shape |
| K3 | repair(文件) | 計劃〈範圍〉寫明點號名取最後一段、整批掃描關掉忽略規則;Systems/規格閘 引用 t_choice_scan_batch_share、t_choice_kill_partial_unverified_rc | 〈範圍〉2、〈範圍〉4 | 文件 |

未覆蓋:真 Android 專案的端到端耗時(S26 手動驗收);整批輸出超過 64MB 退逐檔時,約 450 支以上的大檔改動會超出推送前時限(只提醒不擋)。
