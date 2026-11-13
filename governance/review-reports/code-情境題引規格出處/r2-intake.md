# code-情境題引規格出處 r2 收貨紀錄

## 派工與收貨
- 修補鏡頭:修前 6ccb7a462 → 修後 1d535b07b(來源 r2-repair-binding.json;r1 修正關卡全部通過,r1-fixcheck.txt)。
- 材料:r2-repair-code.patch(1138 行)、r2-repair-tests.patch(701 行)給程式席與合約席;資安席看全份 r2-snapshot.patch(6380 行,資安包不拆);配對案例 r2-behavior-cases.md。
- 7 席全新同門 sonnet,外家未派(單家族視角)。派工前暖過鏡頭快取,各席仍回報鏡頭逾時、沒附固定席。
- 7 份從逐字稿存檔;合約席總結句把等級與條數寫同一行,report-normalize --write 純格式搬移一處;其餘已正規化。quote-check:6 份全數錨定;正確性席 #1 引句內包了「」被截斷(見下方重現)。refcheck 全部 0 missing / 0 out_of_range。
- 收貨時 git status 只有編排者自己的帳本改動;審查席臨時目錄收齊後已刪。

## 機械重現(編排者)
| id | 做法 | 結果 |
|---|---|---|
| c1 | 引句被巢狀「」截斷;以完整原文 `進來前是「忽略」的(例:nohup 開的)照留忽略,不替人改掉。不在主執行緒(signal 丟 ValueError)就不裝。` grep r2-repair.patch | HIT:1 處逐字存在 |
| a1 | 讀碼對照 `_lint_wt_on_term`(處理器內收程序群組後 os._exit)與 `_situation_rule_signals`(轉 KeyboardInterrupt、存舊處理器還原) | HIT:兩套安裝與還原語意;docstring 寫「寫法照 _lint_wt_begin」與實際不符 |
| b1 | 席報告附兩版實跑(修前照插 S2、修後回已寫過 S1),讀碼 `test in refs` 與規格閘 `refs == {test}` 不一致 | HIT(讀碼) |
| 其餘 | 席報告附實跑或兩版讀碼,讀碼核對成立 | 採信 |

## 分組與處置(14 條全部折入)
1. **中斷收尾**(a1 major;z1 c1 c3 minor):
   - a1:`_situation_rule_signals` 的 docstring 改成實情(不是照 `_lint_wt_*` 的寫法),並在 Systems/guard-kill 加 WHY 說明為什麼不同:lint 工作樹的處理器在任何地方都要立即結束程序(os._exit),殺傷力要讓 `_isolated_worktree` 的 finally 收工作樹,只有轉成例外才會經過 finally;兩者語意不同是刻意的。
   - c1:第一個訊號到了之後,收尾期間把這兩個訊號暫時改成只記下、不再丟例外(收尾完照舊還原)。
   - z1:訊號保護延伸到寫計劃與記治理帳那段(鎖內寫入到 `_gate_event` 結束)。
   - c3:「已寫過」的拒絕訊息講清兩種情形:治理帳有對得上的 situation-rule → 什麼都不用做;沒有 → 先把計劃裡那一條刪掉再重跑(補記要的殺傷力結果拿不到)。
2. **「已寫過」判斷跟規格閘口徑不同**(b1 minor):改成那一行綁的測試恰好是 {--test},跟 `_spec_gate_ruled_ids` 一致。
3. **換行**(t1 c2 b2 minor;a2 minor):`_situation_rule_read` 改叫 `load_raw_for_edit`(同時拒 BOM 與 CRLF,訊息不另抄),再另擋單獨的 `\r`;計劃天花板若寫「只拒 CRLF」同步改。
4. **讀回比對不一致時的 rc**(t2 minor):計劃已被取代時回 1、訊息說計劃已動、治理帳沒記、照「已寫過」那條處理;docstring 的 rc 說明同步。
5. **保留標記**(z2 minor):工作樹沒建起來(wt.ok 為假)時不寫 .lumos-keep,照舊收掉暫存資料夾。
6. **--plan**(x1 b3 minor):包含檢查改拿 `env.vault.resolve()` 當基準,並拒 `vault/Projects` 本身是符號連結;大小寫以實際目錄列出的檔名比對,不同就拒絕並印實際檔名。
7. **AI 代跑的人裁條款**(x2 minor):規格閘認到 origin 為 ai 的人裁條款時多印一行提醒(帶 consent 原話),不擋;計劃天花板 7 補這一句。

regression-set:a1、a2、z2、t2、b1、c3 這幾條的程式是 r1 修補新寫的(席位歸因:z2、t2、b1、c3 有兩版證據;a1、a2 是修補新加的寫法)。z1、c1、c2、t1、b2、b3、x1 席位歸因為原有漏查;x2 是設計裁定的延伸。

## 先查世界
- PRIOR-ART:組 1 中斷收尾——查「python signal handler SIGTERM raise KeyboardInterrupt so finally cleanup runs, ignore second signal during cleanup」。Python 官方論壇討論把 SIGTERM 預設轉成例外,常見做法就是對 SIGTERM 裝處理器丟 KeyboardInterrupt 讓 finally 執行(https://discuss.python.org/t/convert-sigterm-to-an-exception-by-default/86283 );ActiveState 的 handle-exit 情境管理器同樣把訊號轉成例外再走收尾(https://code.activestate.com/recipes/577997-handle-exit-context-manager );pyterminate 套件提供同樣形狀(https://github.com/jeremyephron/pyterminate )。收尾期間第二個訊號:DelayedKeyboardInterrupt 做法是收尾時換處理器只記下、收完再處理,採用。
- 方向:對 — 「訊號轉例外、走同一條 finally 收尾」是官方論壇與兩個獨立實作的共同形狀(來源同上三個網址);跟 lint 工作樹 os._exit 的差異是需求不同(要不要經過 finally),寫明理由即可,不另抽共用。
- 組 2–7 是同一批函式內部的一致性與邊界補洞,照既有函式(`load_raw_for_edit`、`_spec_gate_ruled_ids` 的口徑)修,不另查。
