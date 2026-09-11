severity: major

### F1 驗證紀錄的新增測試數與機械重數對不上
severity: major
blocking: 是 — 這是 status:pass 的 Verification 記錄,數字錯會誤導三個月後的人以為只需盯 34 支,牴觸本專案自己的「審計紀錄數字必機械數」鐵則,合入前該重數更正。
引句:「新增 t_nodehome_* 等 34 支（計劃 39 條驗收條款綁了 36 條測試、3 條靠人）；每支檔有家相關 146 項檢查全過」
1. 機械重現:`git diff d26fd9b3..5d9eae74 -- scripts/test_lumos.py | grep -c "^+def t_nodehome_"` 輸出 `40`,不是文件宣稱的 34;若把同批新增的 `t_precommit_runs_home_check`/`t_prepush_runs_home_check`/`t_new_system_with_code_and_responsibility`/`t_lands_in_field_format`/`t_disposal_gate_requires_landing`/`t_design_dispatch_shows_landing_sizes`/`t_disposal_landing_requires_spec_in_vault` 也算進「每支檔有家相關」,總共是 52 支新測試函式。
2. 「146 項檢查全過」也對不上:在 `/tmp` 乾淨複製的 scripts 上跑 `python3 scripts/test_lumos.py -k nodehome` 得到 `136 passed, 0 failed, 1 skipped`,再逐一補跑上述 7 支不含 "nodehome" 字串的測試名共 `29 passed, 0 failed`,合計 165 通過,不是 146。
3. 佐證:file: `scripts/test_lumos.py:7595` 起是新增測試區塊起點(`t_code_exts_four_lists_agree`,同批修改),`scripts/test_lumos.py` 內 `^def t_nodehome_` 開頭的函式現有 40 支(`grep -c` 可重跑核對)。

### F2 節點正文說「五份」一致性測試,綁定的測試名卻還叫「four_lists_agree」
severity: minor
blocking: 否 — 只是測試函式名沒跟著語意更新,不影響擋不擋,但會讓讀者以為只有四份清單在比對。
引句:「同一份清單,五份由一致性測試釘住」
1. 同一行緊接著標的綁定測試是 `[test:t_code_exts_four_lists_agree]`,函式名裡的「four」與正文剛講完的「五份」字面互相矛盾。
2. 佐證:file: `scripts/test_lumos.py:7595` 該測試函式目前確實比對五份清單(含新增的 `_NODEHOME_CODE_EXTS`,見 `scripts/lumos:17385`),只是函式名沿用了改動前「四份」的舊名,沒有跟著這次擴充改名。

總結:最高 severity major,blocking 共 1 條
