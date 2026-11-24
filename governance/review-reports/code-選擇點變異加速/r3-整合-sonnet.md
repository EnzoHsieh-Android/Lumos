severity: minor

dispatch-lens 的鎖檔 `baf3be87….json.warming` 不存在(ls 與 cat 都回「No such file」),所以沒有鎖需要處理,也沒刪任何東西。

`lumos lint` 在 after 版(744f7b6d6)對兩篇都回 0 問題:`Projects/選擇點變異加速_計劃` 與 `Systems/guard-kill`。

## 發現

### 1. S20 新掛的 `t_choice_kill_merge_no_lane_chunk` 守的不是 S20 條款字面
severity: minor
blocking: 否
引句:「[test:t_choice_kill_merge_baseline_red][test:t_choice_kill_merge_no_lane_chunk]」
file: `scripts/test_lumos.py:147375`
- **問題**:S20 條款字面寫三件事:基準不綠的支不組進合併、快篩通過時那支交 abort 列、綠的不到 2 支不合併。新掛的測試守的是另一件事:壞法的配方一支都不在合併道時,不套壞法、不開快篩、`judged` 不記 merged。
- **行為出處**:這個行為只寫在計劃〈做法〉3(`Projects/選擇點變異加速_計劃.md:92`),沒有任何 S 條款寫它。
- **為什麼要報**:這支測試有人守,但守的行為沒有條款。條款文字也要同步補上這一句,才算綁對。
- **歸因**:未判定。我沒有跑修前版的對照;單看這個 patch,是修補把綁定掛到不相稱的條款上。
- **驗證**:`-k t_choice_kill_merge_no_lane_chunk` 在 after 版 2 passed。測試存在,行為本身成立。

### 2. 快篩上限受剩下總時限約束、基準中途重估兩條行為,沒有對應的條款句子
severity: minor
blocking: 否
引句:「[test:t_choice_kill_merge_unclean_goes_single][test:t_choice_kill_merge_screen_cap][test:t_choice_kill_merge_edges]」
引句:「[test:t_choice_kill_merge_baseline][test:t_choice_kill_merge_budget_reestimate][test:t_choice_kill_merge_budget_edge]」
file: `scripts/lumos:28819`
file: `scripts/lumos:28972`
- **screen_cap**:S4 字面只列失敗樣態(逾時、rc 非 0、結果檔異常等)。`t_choice_kill_merge_screen_cap` 守的是 `min(max(基準×5, 下限), max(剩下時限, 1))` 這條算式與端到端接線。S7 只管合併基準的上限,沒有任何條款寫快篩上限。
- **budget_edge / reestimate**:S6 字面沒提「量完一支就用實測平均重估」。`t_choice_kill_merge_budget_edge` 守的是這個卡線:剩 6.0 照量,剩 5.99 收手。這條規則只在〈做法〉2 第 1 步。
- **後果**:這幾支測試掛在最接近的條款下,行為本身成立。但要有人把條款當驗收清單讀,會漏掉這兩條行為。
- **歸因**:有證據的原有漏查(r1 加重估、快篩上限時就沒補條款)。修補只是把測試名掛上去,沒補條款句子。

### 3. guard-kill 拆 PITFALL 時掉了「配方一支都不在合併道不開快篩」與「判法只算一份」兩個修法片段
severity: minor
blocking: 否
引句:「PITFALL:合併快篩開跑量齊單支基準時,單支實際比「支數 × 10 秒 × 1.5」那道門的單價貴,會把總時限吃光、一個壞法都不判(--no-merge 同情境至少判 1 個)」
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:111`
- **舊版**:舊的合併 PITFALL 修法欄收了 `_kill_merge_in_lane`(配方一支都不在合併道的壞法不開快篩)與「判法只在 `_ChoiceKillRun` 算一份,on_row 不帶」。我用 `git show 02fd3bdf5:…guard-kill.md | grep -c _kill_merge_in_lane` 確認舊版有 1 筆。
- **新版**:這兩段在 after 版 guard-kill 裡 grep 不到(`_kill_merge_in_lane`、`on_row 不帶` 皆 0 筆)。
- **影響**:`_kill_merge_in_lane` 的行為在計劃〈做法〉3 第 92 行還有,只是 guard-kill 這個「家」不再記它的出處與對應測試 `t_choice_kill_merge_no_lane_chunk`。重大規則沒掉,掉的是 guard-kill 內的回溯線索。
- **歸因**:有證據的修復回歸(拆分時漏帶)。影響只在知識同步,不影響行為。

## 已驗主張

- **`_gradle_module_parts` 存在,說法成立。**
  - 引句:「`_gradle_test_module` 只跟它共用模組各段的檢查(`_gradle_module_parts`),回傳不變」
  - file: `scripts/lumos:77436`、`scripts/lumos:28745`、`scripts/lumos:77444`
  - `_gradle_test_module` 回傳 `_gradle_module_parts(task[:-len(":test")])`;`_gradle_unit_test_task` 也呼叫它。兩處共用,`_gradle_test_module` 的回傳沒變。
- **做法 4 的總時限說法成立。**
  - 引句:「合併快篩與合併基準的上限都不超過剩下的總時限(最少 1 秒),所以一次呼叫最多超出 `--max-seconds` 約 1 秒加一支逐支的時間」
  - file: `scripts/lumos:28814`、`scripts/lumos:28819`、`scripts/lumos:28957`
  - 兩個上限函式都受 `max(remaining, 1.0)` 約束,與筆記一致。
  - 〈預期效益〉與風險段落(約第 141、150、153、228 行)仍寫「快篩逾時上限約 2.5–5 分鐘」。那是預算寬裕時的估算,與新說法沒有打架。
- **`_kill_merge_singles` 的卡線與筆記一致。**
  - 程式:`mg.remaining() < 平均 × left × 1.5` 才收手,所以剩 6.0 照量、剩 5.99 收手。
  - 筆記:「超過剩下的總時限 → 不量了」。
  - 測試:`t_choice_kill_merge_budget_edge` 的兩個案例剛好是 6.0 與 5.99。
- **新掛的 `[test:]` 名字都存在。** 13 個名字各 1 支定義,含 `t_choice_kill_merge_budget_edge`、`_screen_cap`、`_signal_race`、`_no_lane_chunk`。
- **`governance/anchor-baseline.json` 的指紋對得上。** `shasum -a 256 scripts/test_lumos.py` 是 `b72ebebc…`,與 baseline 一致。這一輪對測試檔的淨改動只有新增(`git diff 02fd3bdf5 744f7b6d6 -- scripts/test_lumos.py` 的減行只有檔頭那一行),所以 note 寫「換回原版」與淨差異不衝突。
- **after 版實跑:** `-k t_choice_kill_merge_budget_edge` 2 passed、`-k t_choice_kill_merge_screen_cap` 6 passed、`-k t_choice_kill_merge_no_lane_chunk` 2 passed。只跑一次、沒有重跑。

## 三問回答

1. **原問題的修復效果有何行為證據?** 這個鏡頭只看知識同步:上面那些測試名與說法在 after 版對得上,三支關鍵測試在 after 版通過。修前版的對照我沒跑,修復效果本身(重估與快篩上限是否真的擋住)留給正確性與資源席。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 兩篇筆記沒有新舊打架。結論限於我讀到的 patch 範圍與上面三支測試。
3. **新發現的同一案例在修前、修後各是什麼結果?** 三條都是文件綁定或內容問題,沒有可比較的行為案例。發現 3 的修前證據是上面的 grep,修後同一 grep 為 0。其餘兩條只有修後證據,未判定。

未驗範圍:沒跑修前版測試、沒驗行為正確性、沒跑不帶 -k 的全套。

收工時已移除我建的 worktree 與臨時目錄。

總結:最高嚴重度 minor
