severity: major

## 範圍與結論
修補差異只動測試、計劃筆記、guard-kill 家筆記和簽章基準檔,沒有碰 `scripts/lumos` 的正式碼。所以只審測試是否抓得住錯,以及文件有沒有跟測試對上。

鎖檔 `…2fa.json.warming` 不存在(ls 與 cat 都回「No such file」),沒有東西可刪。

## 1. 重估測試分不出「平均」與「最小值/第一支」,卻宣稱守住平均
severity: major
blocking: 是
引句:「# r3 邊界 #2、正確性 #1:耗時不等(1 秒、3 秒、1 秒)才分得出「平均」跟總和、最後一筆、最大值。」
file: `scripts/lumos:28972`(`_kill_merge_singles`,重估式 `sum(measured) / len(measured) * left`)
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`(S23 條款寫「已量的平均耗時」)

失敗場景:耗時取 1、3、1 秒,剩 3.0 秒。量完第二支時,平均與第一支的門檻剛好都是 3.0(平均 2 × 1 × 1.5 = 3,第一支 1 × 1 × 1.5 × 2 = 3 在第一支後算過同值)。把平均換成最小值或第一支,結果都跟平均一樣。要分得出來,耗時要像 1、5、1、剩 3.0:真正的平均會收手,最小值或第一支會繼續量。這個改壞會讓重估偏樂觀,又把總時限吃光,正是 r1 正確性 #1 要擋的錯。

重現(在修後 worktree 裡改 `scripts/lumos`,清 pycache 後跑):
- 把 `sum(measured) / len(measured) * left` 換成 `min(measured) * left`:`python3.14 scripts/test_lumos.py -k choice_kill_merge_budget_edge` 回 `4 passed, 0 failed`(照綠)。
- 換成 `measured[0] * left`:同樣 `4 passed, 0 failed`。
- 對照:換成 `sum(measured) * left` 會紅(「耗時 1、3、1 秒、剩 3.0 秒 → 量了 3 支」那條),所以測試註解說得到的「總和」是守住的,只有「最小值」與「第一支」漏掉。
- 同一份改壞在修前版(744f7b6)跑同一指令:`2 passed, 0 failed`,也照綠,因為修前測試只有固定 2.0 秒。兩次各跑一遍,結果相同。

歸因:有證據的原有漏查。修前測試本來就分不出,修補把守得住的範圍擴大了(總和、最後一筆、最大值),但留下最小值與第一支的缺口。重大度因為被保護的是 S23 條款明寫的「平均」,所以標 major。

建議補一組 1、5、1 秒、剩 3.0 秒(預期只量 1 支)的案例。

## 已驗主張(三問的回答)

引句:「check(f"r3 邊界 #2 耗時 1、3、1 秒、剩 {rem} 秒 → 量了 {n} 支(重估用平均)", len(c.baselines) == n and got is (n == 3),」

1. 剩餘時限那組逾時上限(S22)修得到位:新測試 `t_choice_kill_merge_cap_wiring` 照修後版跑 `3 passed, 0 failed`。
   - 把快篩呼叫端改回 `max(m_el * 5, c.floor)`:紅,seen 為 `[59.3, 300.0, 300.0]`。
   - 把合併基準的剩餘時限改成 `1e9`:紅,seen 為 `[300.0, 58.6, 56.6]`。
   - 兩個呼叫端的改壞都抓得住,而且不靠真實睡眠,所以不會在負載下隨機紅。
2. 修補處的相鄰路徑仍成立:
   - `t_choice_kill_merge_screen_cap` 刪掉末段後剩 r1 邊界 #3 案例,跑 `5 passed, 0 failed`,函式前面沒有殘留對 `one`、`saved` 的引用。
   - `_ck_cleanup` 會略過 None,`root = fake = None` 後建 repo 失敗也不會在 finally 裡再崩。
   - 條款裡引用的測試名全部存在,各一份:`t_choice_kill_merge_cap_wiring`、`t_choice_kill_merge_screen_cap`、`t_choice_kill_merge_budget_edge`、`t_choice_kill_merge_budget_reestimate`、`t_choice_kill_merge_no_lane_chunk`、`t_choice_kill_merge_baseline`、`t_choice_kill_merge_baseline_red`、`t_choice_kill_merge_edges`、`t_choice_kill_merge_ledger_counts`。
3. 新發現(上面那條)的同一案例,修前、修後結果相同(都照綠),所以不是修補造成的回歸。

## 未驗範圍
- 沒讀 r4-behavior-cases.json 的配對案例,沒另補 repair/preserve 案例。
- 沒檢查 S22 在剩餘時限小於 1 秒、取 `max(R, 1)` 的邊角。
- 沒驗 `anchor-baseline.json` 的雜湊值是否跟 `test_lumos.py` 相符(這是簽章流程的事)。
- 沒跑全套測試。

## 八角度其餘項
被刪除的行為:S4、S6、S20 拿掉的綁定都轉到 S22、S23、S24,沒有掉出綁定。
效率:真實睡眠案例換成 spy 後,該測試跑約 9 秒。
慣例:找不到逐字違反 CLAUDE.md 的行。

worktree 已用 `git worktree remove --force` 移除。

總結:最高嚴重度 major
