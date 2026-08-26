# r1-intake(lint-wireup,2026-08-26)

## 外家席撈回紀錄
ext 報告引句用 markdown blockquote 非「引句:「…」」格式,quote-check 抽不到。依「可疑席先機械重現」紀律,編排者重現:
- ext-f1:scripts/hooks/pre-push:159-166 vault 缺席提前 exit 0(doctor 不執行)HIT——[S1] 掛 doctor --ci 對無 vault 消費 repo 不可達,blocker 成立。
- ext-f2:Systems/lint-declaration-health 存在且 FLOW 明定靜態校驗=格式層(_lintcheck_validate),工具/jar 存在性歸 smoke HIT——[S1] 的 PATH 檢查違反既有合約且雙向誤判,blocker 成立。
- ext-f3:同筆記記錄 /tmp jar 事故 07-17 後 07-27 重演、smoke 是唯一抓得到的守衛 HIT——「維持手動」無責任鏈=換名不接線,major 成立。
三條全撈回照折。

## 編排者自首
spec 動筆前沒對 lint-check 做圖譜進場(lumos search),漏掉 [[Systems/lint-declaration-health]] 這篇現成合約——外家用它打掉我半份 [S1]。圖譜先行破功一次,記入本輪誠實帳。
