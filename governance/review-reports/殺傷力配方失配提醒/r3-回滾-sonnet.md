severity: minor

回滾與相容鏡頭第 3 輪。實查項目與結論:
- kill-rm 對背書計算:`_backing_note_recipes` 只認筆記現有配方的身分,kill-rm 移除後舊 kill-log 行自然略過;已存進表態記錄的背書不重算。與計劃「不刪 kill-log」一致,無 finding。
- 新身分函式對既有三處(kill-add 判重、guard kill 寫 recipe_id、背書分組):格式正常的配方仍走 `_kill_recipe_key`,節點字串 `str(rel)` 與 `Env.find` 回傳、doctor 的 `notes` 鍵同為帶 .md 的 posix 字串,三處一致,無 finding。
- 接走 `load_platforms` 警告:警告都用 `print(file=sys.stderr)` 呼叫當下取 `sys.stderr`,暫時接走有效;`cfg=` 給 dict 時不再讀檔,且 `load_test_profile` 也吃同一個 cfg;被吞的只有 root 不存在與未知 test_profile 等,這些在 P2 與 kill-add 各有自己的提醒,別處(guard kill、spec-gate)是各自呼叫、不受影響。無 finding。
- `_KNOWN_GATES` 登記、`[P2]` 與 `_section_of(out,"P")` 的 `[P]` 比對不互撞、HELP_WHEN 與 guard 子指令清單測試:已讀,無 finding。
- 回退節:已讀,無 finding。

## F1 寫進 guard-kill 節點的判斷函式狀態數,會撞到既有的「態數宣稱」測試
severity: minor
blocking: 否
引句:「程式說明寫進 [[Systems/guard-kill]](kill-rm 用法、P2 段、判斷函式跟 guard kill 的對照)」
file: `scripts/test_lumos.py:25200`
1. 既有測試在 `scripts/test_lumos.py:25200-25206` 對 `Systems/guard-kill.md` 全文掃 `(?<!舊)([一二三四五六七八九十])態`,要求每個「N態」都等於 guard kill 實際 verdict 數(現在是七)。
2. 新判斷函式有六個狀態(ok/hits/missing/undecodable/outside/malformed)。實作者照 spec 把「判斷函式跟 guard kill 的對照」寫進該節點時,若自然寫出「六態」,該測試翻紅(說明字面像是漂移)。
3. 同一測試 `scripts/test_lumos.py:25180` 用 `def cmd_guard_kill(` 到 `def cmd_guard_audit(` 之間的原始碼抽 verdict 值域;新函式若放在這兩個定義之間且寫了 `"verdict": "…"` 字面值,值域會被污染。
4. 為何放行:spec 並沒有要求寫「N態」,屬實作時的措辭與擺放注意事項;建議在〈實務隱患〉加一行:節點裡寫「六種狀態」不寫「六態」、新函式放在 `cmd_guard_audit` 之後或別處。

## F2 reference.md 插入位置有 2000 字元視窗限制
severity: minor
blocking: 否
引句:「skill 裡提到 kill-add 的三處(`skills/lumos-project-notes/reference.md` 的指令表、`commands/06-代碼審與推送.md`、`commands/INDEX.md`)各補 kill-rm」
file: `scripts/test_lumos.py:25189`
1. 測試 `scripts/test_lumos.py:25189` 取 `reference.md` 第一個「lumos guard kill-add」起的 2000 字元,要求七個 verdict 名都在裡面;現況最遠的 `error` 落在第 1494 字元,只剩約 500 字元餘裕。
2. 第一個「lumos guard kill-add」是 `reference.md:530` 那個程式碼區塊,不是 `reference.md:594` 的指令表。spec 說「指令表」,實作者若在 530 區塊後加超過約 500 字元的 kill-rm 說明段,測試翻紅。
3. 為何放行:spec 指的是 594 的指令表,字面實作不會出事;只是兩處都像「指令表」,建議實作紀錄寫明補在 594 行那一列、530 區塊最多補一行指令。

最高等級:minor;blocking 共 0 條
