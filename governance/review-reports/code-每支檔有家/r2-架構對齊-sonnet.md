severity: clean

## 三問逐答

1. 分層與依賴方向:兩支 hook(`scripts/hooks/pre-commit:124`、`scripts/hooks/pre-push:181-192` 的 `_hrange`)仍只呼叫 `lumos home check`、判 rc,不重寫判定邏輯;`scripts/lumos` 內新增/修改的程式碼都留在既有的 cmd/_helper 分層裡,沒有新的跨層直呼。這輪修法沒有改變分層。
2. 命名與錯誤處理:F5(`scripts/lumos:26187-26193`)的訊息與判斷順序逐句對齊 `cmd_loop_status` 的 `--light`/`--panel`(`scripts/lumos:7403-7404`,先判「同給」再判「都沒給」,訊息句型一致);F7(`scripts/lumos:12496-12533`)的 try/except 逐句對齊同一支函式裡 `plan_rels`/`sys_rels` 回掛的既有寫法(捕 `OSError, ValueError, RuntimeError`、失敗印「筆記建好了,但…」、其餘項目照做完、最後彙總 `return 2`)。
3. 第二種做法:F4(`scripts/lumos:22959`)不再自寫正規式,改呼叫派工鏡頭既有的 `_lens_contract_lines`(`scripts/lumos:22052`)——這正是這輪 prompt 自己點名的對照物;F5 拿掉了整支工具唯一一處 `add_mutually_exclusive_group`,回到跟鄰居一致的手動判斷;F8 沒有把 `_hrange` 併回 `_range`,但這是判讀階段裁定的「刻意保留兩套、不合併」,並已把理由寫進 hook 註解(`scripts/hooks/pre-push:181-182`)與節點 KEY 行(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`),不是疏漏。這四類之外重新掃過整份 delta(config 讀法、`--diff` 範圍解析改呼叫既有 `_lens_range_ok`、doctor S8/S9/S10 之間補 `print()` 對齊 S7/S8 既有間距),沒有再發現新的第二種做法。

## 第一輪修法驗收
F4:修到 — `_nodehome_landing_sizes` 改呼叫既有 `_lens_contract_lines(summ, cap=10**6)`,不再自寫正規式;新增測試釘住帶括號說明的 KEY 行(如 `KEY:(2026-09-11 補)★CHECKPOINT★…`)也算進合約數,r1 的漏算場景已被測試覆蓋。
F5:修到 — 拿掉整支工具唯一的 `add_mutually_exclusive_group`,改成跟 `loop status` 的 `--light`/`--panel` 同一套手動判斷(先判同給、訊息中文、判斷順序一致);新增測試斷言錯誤訊息不含 argparse 的英文 `not allowed`。
F7:修到 — `--code`/`--responsibility` 寫回加上跟 `plan_rels`/`sys_rels` 同款的 try/except,例外不再直接穿出去,失敗項目印提醒後繼續處理其餘項目,最後用 `rc_own` 彙總回傳,結構跟鄰居一致。
F8:修到 — 沒有合併 `_range`/`_hrange` 兩套範圍演算法(此為判讀階段裁定保留,非疏漏),但把「為什麼刻意不同」寫進了 `pre-push` 掛鉤註解與 `每支檔有家.md` 節點 KEY 行,滿足「不合併就要留痕」的收斂條件。

總結:最高 severity clean,blocking 共 0 條
