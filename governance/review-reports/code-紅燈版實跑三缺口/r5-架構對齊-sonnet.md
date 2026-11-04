severity: clean

**1. 分層與依賴方向:對齊**
- `_tg_ident` 加選填參數 `fold`,預設仍是 `_tg_ws_fold`。新的 `_tg_ws_collapse` 放在 `_tg_ws_keep_strings` 後面,跟 `_tg_ws_fold` 放在 `_tg_ident` 後面的排法一樣(`scripts/lumos:49400-49426`)。
- 呼叫方向沒變:`_tg_ws_keep_strings` 的兩處呼叫端(`scripts/lumos:49043`、`scripts/lumos:49056`)照舊,它現在往內呼叫 `_tg_ident`,在同一個 `_tg_` 區塊內,沒有跨層。
- 認字串的掃描迴圈仍只有 `_tg_ident` 一支。`_C_STRIP_PAT` 的三個使用處是 `scripts/lumos:6827`、`scripts/lumos:49112`、`scripts/lumos:49405`,數量沒增加,舊的重複迴圈已移除。
- `_TG_LIT_PAT` 的 5 個使用處(`scripts/lumos:49067`、`49174`、`49176`、`49194`、`49202`)都是一樣的 `_lazy_re(...)` 呼叫,補三引號只改樣式本身,呼叫端沒動。
- 擋下訊息仍在 `_spec_gate_push_one` 的 `cfg_gone` 段,回傳 `(訊息, None)`,跟 `bad_plat` 段一樣(`scripts/lumos:16003-16030`)。
- 測試補在原有的 `t_tq_guard_string_comma_args` 和 `t_spec_gate_record_keeps_platform` 裡,沒有另開測試函式。用到的 `_mp_head` 等輔助函式都已存在(`scripts/test_lumos.py:123211`)。已完成計劃的 `replace("status: doing", "status: done")` 寫法,在 `scripts/test_lumos.py:77493` 等多處都有。

**2. 命名與錯誤處理:對齊**
- `_tg_ws_collapse` 的名字跟 `_tg_ws_fold`、`_tg_ws_keep_strings` 同一組 `_tg_ws_` 前綴,也沒寫 docstring,跟 `_tg_ws_fold` 一樣(`scripts/lumos:49420-49425`)。
- 擋下訊息的句型對上「平台不在設定裡」那段:`{prel}:留痕記的… (…?)` 接 `;` 再講怎麼做,結尾帶 `lumos spec-gate {_sh_quote(Path(prel).stem)}`,錯誤路徑也同樣回 `(訊息, None)`(`scripts/lumos:16008-16012` 對 `16027-16029`)。
- 「實作後才跑」補法的描述,跟 `_spec_gate_low_not_red` 印的補法一致:先提交實作、換成只留介面的空殼讓測試紅、跑規格閘、再換回,最後可改 `plan_risk: high` 走設計審(`scripts/lumos:15222-15238`)。
- `done` 時降成 `notes` 提醒的分流沒動,仍是 `if cfg_gone and not done` 擋、`if cfg_gone` 降成提醒(`scripts/lumos:16013-16015`)。

**3. 第二種做法:沒有引入**
- 壓空白沒有另一套:`re.sub(r"\s+", " ", …)` 現在只是 `_tg_ident` 的一個 `fold` 參數值,不再有自己的掃描迴圈。
- 認字串沒有另一種樣式:`_TG_LIT_PAT` 的三引號段是照 `_C_STRIP_PAT` 的寫法補進原樣式,該樣式本來就是 `_C_STRIP_PAT` 之外另一份,這輪沒有新增第三份。
- 擋下訊息是現有 `bad_plat` 句型加上現有的補法,沒有新的訊息格式。

兩個小地方我認為不算不對齊,只提醒編排者:
- ⚠ `_tg_ident` 的 docstring 寫「傳 fold(_tg_ws_keep_strings)」,但實際傳進去的是 `_tg_ws_collapse`(`scripts/lumos:49402` 對 `49417`)。這是註解與實際不符,不是做法不一致。
- ⚠ `_TG_LIT_PAT` 的註解說「同 `_C_STRIP_PAT` 的三引號那段」,但少了 `(?:"""|\Z)` 裡的 `\Z`(沒收尾的三引號)和 `'''` 那一支(`scripts/lumos:6786` 對 `49072`)。屬於語意差異,另一位審查員那邊的範圍,我沒有判它是否有行為影響。

不對齊共 0 條
