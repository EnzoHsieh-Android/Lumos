# r1 收貨紀錄(代碼審:跑滿後查世界方向)

## 席位收貨

兩席報告從逐字稿存(完成通知把 `>=` 轉成跳脫字,不從通知存),兩份原本就是正規化格式,引句全數錨定、引用的 file:line 都對得上。席位臨時目錄 `/tmp/lumos-seat-work/code-跑滿後查世界方向/` 收齊後確認沒有程序開著,已刪。編號:正確性 F1、F2 記 c1、c2;架構對齊 A1–A4 記 a1–a4。正確性席另提「loop-retro 新 WHY 的 [test:] 只守生效判定」一句(沒編號,不是 finding):照實記在這裡,不改那行(那行講的生效判定確實由那支測試守,統計由 t_retro_record_world_verdict 守,兩支各守各的)。

## 先查世界

- G1(時間相關分支測不到):PRIOR-ART:查「testing time-dependent code inject clock」——Java 的 `java.time.Clock` 注入、Python clock-pattern、PHP PSR-20 都是把「現在」從邏輯裡抽出,測試給固定時鐘(https://kodejava.org/?p=18412、https://pypi.org/project/clock-pattern/0.10.0/)。採用同一個想法、但不另加時鐘參數:判情況改讀帳上已寫好的那筆人裁(它就是被持久化的「現在」),測試在同一個程序裡改生效常數,跟本 repo 既有的測試改 `LUMOS_PANEL_RETIRE_CUTOFF` 同一路(只是這個常數不給環境變數覆寫,設計審 r2 定的)。
- G2(新鮮度守衛看不到改值):PRIOR-ART:查「git log -S vs -G」——`-S` 比的是字串出現次數,原地改值次數不變會漏;`-G` 比的是增刪行是否符合正規式,git 手冊自己的例子就是這種(https://kitemetric.com/blogs/unlocking-git-log-s-power-mastering-g-and-s-options、https://public-inbox.org/git/7vfvxlw055.fsf@alter.siamese.dyndns.org/)。採用 `-G`。
- G3(命名與呼叫端一致):本 repo 既有慣例(`_body`/`_inner`/`_impl` 後綴、回傳 dict 開頭列齊鍵、唯一決定處的所有呼叫端都給同樣的輸入),不另查世界。

## 依根因分組與去向

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 記完人裁後另讀時鐘判情況:今天(生效前)測試走不到要求那一支,跨秒還可能跟帳上那筆不一致 | c1 a4 | 折:改成讀回帳上剛寫的那筆人裁判情況;新測試 t_cap_decision_world_fill_reads_ledger 在同一個程序裡把常數改到過去與未來,斷言提醒與否、且判情況用的是帳上事件本身(修正前 3 條紅) |
| G2 | 生效常數新鮮度守衛用 `-S` 看不到只改值的提交,比較用 `<=` 放過同日 | c2 | 折:守衛抽成 `_cap_since_last_change_day`(用 `-G`)與 `_cap_since_fresh`(嚴格早於);新測試 t_cap_since_last_change_sees_value_edit 自建倉庫驗「只改值看得到、同日不算」 |
| G3 | 命名與呼叫端跟鄰居不一致:本體後綴用 `_base`、回傳 dict 的 world_case 沒初始值、doctor 與 retro-stats 等呼叫端沒給情況值 | a1 a2 a3 | 折:改名 `_cap_retro_fix_cmd_body`;`res` 開頭列 `"world_case": None`;doctor、retro-stats、`--template --write` 兩處擋下都給情況值,說明改寫成「知道最新人裁的呼叫端都要給」;新測試 t_cap_retro_fix_cmd_world_fill_everywhere(修正前 2 條紅) |

## 重現

| 發現 | 怎麼試 | 結果 |
|---|---|---|
| c1 | 把 cmd_loop_cap_decision 的 `_cap_world_case({'decision': decision, 'ts': now})` 改成 `_cap_world_case(None)`,跑 `-k cap_hint_world` | HIT:9 passed 0 failed,改壞沒被抓到 |
| a3 | 修正前跑 t_cap_retro_fix_cmd_world_fill_everywhere | HIT:retro-stats 與 doctor 兩條都紅 |
| c2 | 讀碼:舊守衛 `git log -1 -S"_CAP_WORLD_CHECK_SINCE = "`、比較 `day <= since[:10]` | HIT(採信席位在 clone 的實測與 git 手冊說法) |

本輪沒有重現不到、沒折也沒放行的發現。
