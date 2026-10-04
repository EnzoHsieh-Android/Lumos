# r1 收貨(code-update預覽)

standard 分級:一位通才(正確性-sonnet)加架構對齊席(sonnet),收齊才動工作目錄。quote-check 全數錨定、report-normalize 不用改。

## 發現

| id | 來源席 | 一句話 |
|---|---|---|
| U1 | 正確性 F1(major) | 區塊差異把「刪掉的最後一行」與「新加的第一行」黏成一行,讀的人分不清刪了什麼、加了什麼 |
| U2 | 架構對齊 F1 | 預覽開頭標籤寫「專案:」,鄰居 deinit 預覽寫「root:」 |
| U3 | 架構對齊 F2 | 加 shell 引號另 import shlex,沒用既有的 `_sh_quote` |
| U4 | 架構對齊 F3 | 讀目標檔只接 UnicodeDecodeError/OSError,鄰居 deinit 寬接 Exception |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| U1 | t_update_dry_run_rule_diff_matches_apply 改成逐行比對(整行 `-舊版紀律:…`、整行 `+新版紀律:…` 各自存在) | HIT:舊程式兩個情境都翻紅 |
| U2 | 對照 cmd_deinit 預覽的開頭輸出 | 成立(純一致性) |
| U3 | 對照 `_sh_quote` 的 docstring | 成立(同一件事兩種寫法) |
| U4 | 讀 `_update_rule_plan` 與 deinit 那段 | 成立的只有「理由沒寫在接例外那一行」:窄接是刻意的,只把「讀不了這支檔」歸成 unreadable,其他錯誤照常往外丟,不會吞掉程式錯誤;席本身也寫「方向比鄰居好、不要求改」 |

## 處置

本輪有 major,不放行任何發現;U4 原本想駁回,但這輪不能放行,改成補註解折入。

- U1 折入:`_reinject_compute` 組差異時兩邊輸入補結尾換行;舊版套用時印的差異一併修好,寫回內容本來就不受影響。
- U2 折入:標籤改成 `root:`。
- U3 折入:改用 `_sh_quote`,拿掉區域 import。
- U4 折入:保留窄接(改成寬接反而會把程式錯誤藏成「讀不了」),在接例外那一行補註解寫明為什麼不學 deinit 寬接。
