severity: minor

# 合約圖譜-sonnet 第 3 輪

## F1 刪除守衛的筆記與註解說 git show 時間算在 deadline 裡,程式沒有綁
severity: minor
blocking: 否
引句:「讀 git 版本每支工具檔一次 git show(有逾時),時間算在這道守衛的 deadline 裡(下面 _over())。」
file: `scripts/lumos:29585`
file: `scripts/lumos:33241`
1. `_delguard_vendored_skips` 每次呼叫跑 `_vendored_state` 兩次,每次對 `_VENDORED_ALL` 全部 17 支各跑一次 `git show`(不只 diff 裡出現的那支)。
2. 這些 git 呼叫走 `_lens_git`,逾時固定 20 秒、跟守衛的 `LUMOS_DELGUARD_DEADLINE`(預設 15 秒)無關。`_over()` 只在 parse 完之後才看,沒辦法中途打斷。
3. 重現:在乾淨臨時 repo(`_is_toolchain_repo` 為 False)放一支 PATH 假 git,遇到 `show` 就 sleep 1 秒,然後呼叫 `_delguard_vendored_skips(root, "diff --git a/scripts/lumos b/scripts/lumos\n")`。實測 37.6 秒才回來,遠超 15 秒的 deadline。正常環境約 0.87 秒(本機實測)。
4. 影響:git 很慢的環境下 pre-commit 會被卡住,而不是降級放行。計劃、`_delguard_vendored_skips` 與 `cmd_delguard_check` 三處都寫「算在 deadline 裡」,跟行為不符。
5. 設計審 r2 抓過的「指紋判定沒有時間上限」是同一個問題。r1 用不跑 git 的判定避開,r2 改讀 git 又把它帶回來。

## F2 REVISIT 的處置辦法會讓這條機制整個失效
severity: minor
blocking: 否
引句:「是就在刪除守衛加「這次 diff 動到安裝清單就一支都不跳」」
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md:53`
1. 同一份筆記講的殘餘缺口,是同一個提交裡工具檔與安裝清單一起改成一致,並說「lumos update 就是這樣做」。
2. 「這次 diff 動到安裝清單就一支都不跳」照字面套用,連純工具更新也不跳,也就是這個 S5 要處理的主要情境(工具更新把自己的程式改掉)整個失效。
3. 這句 REVISIT 到期(2026-11-30)照著做,等於把 S5 撤掉。回頭條件應改成先量「工具更新以外的提交同時動了工具檔與清單」的佔比,或者說明只在什麼情形才這樣收緊。格式(獨立一行、帶日期)沒問題。

## F3 commands/08 的括號說明比程式行為窄
severity: minor
blocking: 否
引句:「消費專案裡改前改後都原封不動的工具自裝檔——內容跟那一版的安裝清單一致的——不抽被刪名稱」
file: `skills/lumos-project-notes/commands/08-自動跑的.md:5`
1. 程式(`p in after or p not in after_present`)在改之前原封不動、改之後已不在暫存區時也跳過:拆除、改名搬走、`git rm --cached`(`t_delguard_vendored_two_states` ④、`t_delguard_vendored_rename_and_count` ②)。
2. 這句只寫「改前改後都原封不動」,沒提「改之後不在也算」。計劃與 `Systems/delguard` 有寫,只有這份給使用者看的速查漏了。

## 圖譜鏡頭固定席逐條判定
- 授權與歸屬 ★INVARIANT★(`_VENDORED_TOOLKIT` 不含 LICENSE/COPYING/NOTICE;主程式檔頭 SPDX):diff 沒動 `_VENDORED_TOOLKIT`、`_VENDORED_ALL` 與任何檔頭,`_vendored_state` 本身沒改。不影響。
- 測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言):新測試 `t_delguard_vendored_two_states` 每個情境都有「前置」check(HEAD 版與暫存版的 `_vendored_state` 結果、diff 內含刪除行、還沒有 HEAD);`t_drift_c4_code_review_r2` ①前置確認 NFD 目錄與含格式字元目錄真的存在且同提交加入;⑤⑥雖沒有單獨前置,`a, b` 位元組確認不同(`code-Caf\xe9` 對 `code-Café`)。`t_drift_c4_dirs_capped_at_20` 前置改為確認散檔與已刪目錄真的進了該提交。未破壞。
- bound-tests-gate、guard-kill(rc 優先序、JSON 純度)、lumos-cli-read、lumos-cli-lifecycle、design-loop 的 INVARIANT:diff 沒碰 guard kill、search、re-inject、處置閘,只碰 `_set_conditions_locked`、c4 證據頁與刪除守衛。不影響。本輪新增的 `[test:]` 名稱(`t_drift_c4_code_review_r2`、`t_delguard_vendored_two_states`)在 `scripts/test_lumos.py` 各有一支同名函式。
- 筆記講的行為對不對得上新程式:計劃、Systems/delguard、存量漂移守衛、lumos-cli-write、commands/03 都已改成「改前改後兩態、讀 git」「只擋兩邊都有角括號」「印現存目錄名」「指令只列現存目錄、查不到提交不給」,repo 內 grep 沒有還在講「看工作目錄」「印 git 原名」「少一邊角括號也擋」的現行句(剩下的只出現在標註為歷史的審計修正紀錄與註解裡的「第一版」說明)。commands/08 見 F3。
- 新寫筆記行前綴:新增的都是 WHY 與計劃內文,沒有 FACT/FLOW/DEP 缺來源;`lumos lint` 對四篇改過的筆記 0 error(Systems/delguard 那條 REVISIT 未知鍵警告是 frontmatter 第 20 行既有的,不是本輪加的)。`lumos note-shape --diff 5e76222d..7b660203` 沒有輸出違規。REVISIT 兩處都是獨立一行、帶日期,格式合規(內容見 F2)。
- 家的歸屬:新增筆記文字用反引號寫的檔案路徑,都在計劃或該檔的家(`scripts/lumos`、`scripts/test_lumos.py` 的家)之內或既有寫法,沒有新增寫別人家檔案的反引號。

最高等級:minor
