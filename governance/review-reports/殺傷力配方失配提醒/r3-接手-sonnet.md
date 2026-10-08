severity: major

## F1 RETIRE-IF 要求的「配方數 10 條以上的其他消費專案」查無存在,條件永遠量不出來也沒有退路
severity: major
blocking: 是
引句:「與至少一個配方數 10 條以上的其他消費專案都是 0 條」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:27`
1. RETIRE-IF 是 AND:rtb 要連兩次(間隔至少 4 週)P2 為 0,而且還要有「配方數 10 條以上的其他消費專案」也連兩次為 0。
2. 實查 /Users/enzo/harness 下各專案(calc-ios、lumos-disposition、lumos-gvc、lumos-stack-verify、maestro-visual-toolkit、pos-api、pos-guest、pos-guest-flutter、pos-ios、remotes)docs/ 裡有 `kill_recipes:` 欄的筆記,除工具鏈自己的複本外都是 0 篇。計劃自己也只列出 rtb 73 條、工具鏈 1 條。看不到第二個符合門檻的專案(此機器範圍內;rtb 不在本機,其他機器未查)。
3. 下一個會談照字面量:第二個專案不存在 → 該 AND 項恆不成立 → 「撤 doctor 這一段」的路只剩另一條「推送時擋另案上線」,等於這段 RETIRE-IF 實質永不觸發;第 2 輪把「工具鏈恆成立」修掉,卻換成「另一專案可能不存在」的同類洞。
4. 折法:RETIRE-IF 補一句「若找不到配方 10 條以上的第二個消費專案,改以 rtb 單獨連兩次 0 條加上 REVISIT 到期時人裁」,或直接指名要驗的第二個專案;並在 REVISIT 回報時順便清點哪些專案真有 10 條以上配方。

## 其餘各節
- 做法 1(判斷函式、身分):已讀,無 finding(`_kill_recipe_key` 簽名、`load_platforms(cfg=)`、`env.find` 吃含 .md 相對路徑、guard kill 輸出 `invariant[:30]` 皆查證與 spec 相符)。
- 做法 2、3、4(設定、kill-add 提醒、kill-rm):已讀,無 finding(修法一行可貼、kill-rm 範本保留舊欄位;`_KNOWN_GATES`、HELP_WHEN、guard 子指令清單測試的連動點 spec 都有寫)。
- 做法 5(P2):已讀,無 blocking。minor(不計):P2 用 doctor 的 `repo_root`(無 docs/ 時為 None 直接跳過),guard kill 用 `_repo_root_from_env`(退回 vault.parent),standalone vault 兩邊會不一致;「平台不在設定裡/根找不到」的提醒沒有可貼的修法。
- REVISIT:日期、分支、只准延一次寫得可照字面執行,無 finding。

最高等級:major;blocking 共 1 條
