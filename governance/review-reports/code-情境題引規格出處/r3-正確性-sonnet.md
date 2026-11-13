severity: minor

## c1 治理帳讀不出來時,「已寫過」會誤判成帳沒記,叫人刪條款重跑
severity: minor
blocking: 否
歸因:有證據的修復回歸(「已寫過」分帳已記與沒記兩種救法是本輪新加的。修前版本是一律叫人照補記方法補,沒有判帳的步驟)
引句:「帳讀不到或沒有這種事件回空集合(少認一條只會更嚴,不會放寬)。」
file: `scripts/lumos`(`_spec_gate_ruled_ids`,修後的 `_situation_rule_already`)

失敗場景:
1. 前一輪人裁已完整跑完,計劃和治理帳都寫了,但這次讀治理帳的檢查失敗(例:帳檔是符號連結)。讀帳的 `_gov_vc_gate_events` 回 `gerr`,`_spec_gate_ruled_ids` 因此回空集合。
2. 重跑同一條時,`_situation_rule_already` 看到 `ruled()` 不含 S 號。它走「治理帳沒有對得上的 situation-rule」那一邊,rc 2,叫人「先把計劃裡 S 那一行刪掉並提交,再重跑」。
3. 照做會在計劃再插一條新號,並再寫一筆帳。訊息沒分「帳沒記」和「帳讀不到」。
4. 實際影響不大:舊條款本來就要刪,舊帳事件只會讓規格閘少認一條,不會放寬。
5. 缺口是:帳讀不到時該走第三條路(提示先修帳路徑),現在只有兩條路。

兩版查證:
- 修後:我用 `python3.14` 載入修後的 `scripts/lumos`,呼叫 `_situation_rule_insert(t, "當甲,系統 應 乙", "t_a", ruled=lambda: set())`。輸出是「治理帳沒有對得上的 situation-rule…先把計劃裡 S1 那一行刪掉」。`_spec_gate_ruled_ids` 在 `gerr` 時回 `set()`,這一點是讀程式碼確認的,沒另外造壞帳實測。
- 修前:`git -C /Users/enzo/harness/lumos-spec-cite show 1d535b07b:scripts/lumos | grep -n "照補記方法補"` 命中那一句。同一輸入走到一律「照補記方法補」的訊息,沒有判帳這一步。

## 附:三問、圖譜鏡頭

**①原問題的修復效果(行為證據)**
- **`--plan` 路徑與大小寫(G8):已驗。** 我用 `python3.14` 載入修後的 `scripts/lumos`,在暫存圖譜上呼叫 `_situation_rule_plan_path_problem`。
  - `projects/搜尋_計劃` 和 `Projects/foo_計劃` 都被拒,並印出實際檔名。
  - `Projects//x` 和 `Projects/sub/../x` 被拒。
  - 圖譜的 `Projects` 是符號連結時,即使連結指向圖譜內也被拒。
  - 正常的 `Projects/Foo_計劃` 通過,`.md` 後綴也照收。
- **`load_raw_for_edit` 多出的拒絕(G5):未見回歸。**
  - 沒有欄位區塊的計劃會被拒,訊息是「沒辦法改欄位」(用語稍偏,不影響行為)。
  - 我掃過 `docs/lumos-toolchain-knowledge/Projects/*.md`,全都以 `---` 開頭、沒有 CR。
  - `load_raw_for_edit` 只用 `split("\n")` 切行,所以 `"\n".join(lines)` 會保留結尾換行,也不會把 `\x0b`、`\x0c` 悄悄改成換行。實測有 `\x0b`、`\x0c` 的檔,讀回後原樣保留。
- **訊號狀態機(G1、G2):未驗。** 只讀程式碼,沒真的對程序送訊號。
  - 殺傷力段:第一個訊號丟 `KeyboardInterrupt`,之後的只記下;指令一律回 rc 2,記下的訊號不會讓程序卡住不結束。
  - 寫回段:三個出口的 rc 與 `_situation_rule_commit` 的檢查點一致:寫前 2、寫後記帳前 1(印補記事件)、記帳當中等記完回 0。
  - 沒做變異驗證,新測試守不守得住,未判定。
  - 小缺點:寫回段拿鎖最久可能等 60 秒,期間 SIGTERM、SIGINT 只被記下,不會中斷等待。這是已知取捨,沒有造成資料損壞。
  - 另一個取捨:殺傷力段裡第二次 Ctrl-C 也只被記下,所以收尾卡住時不能再用 Ctrl-C 中止。
- **讀回對不上回 1(G6)、建樹失敗不留保留標記(G7)、規格閘對 origin=ai 的提醒(G9):** 只讀了程式碼與測試,沒有實跑。邏輯與計劃文字一致,沒找到反例。

**②相鄰呼叫路徑**
- **試插時的「已完成」(rc 0):** `cmd_situation_rule` 的試插階段回 0,在殺傷力和終端確認之前就結束。`_situation_rule_locked_write` 的 `done` 路徑也用 `rc is not None`,0 能正確短路。
- **鎖內重讀:** 重讀時也一律先過 `_situation_rule_read`,不會繞過 BOM、CR 的檢查。
- **`_isolated_worktree` 的 `on_keep` 路徑:** 建樹失敗時 `on_keep` 照舊叫,guard kill 輸出不變。
- **規格閘提醒:** 低風險走 `_spec_gate_twoway_gate`,高風險走 `_spec_gate_expected_part`,兩條互斥,不會重複印。

**「已寫過」兩種情形的判定,帳讀不到時走哪邊:** 見 c1。帳讀不到時歸入「帳沒記」那邊。

**其他觀察,沒有升為 finding**
- 計劃裡有兩條同文、同測試的定義行時,`_situation_rule_already` 取第一條比對 `ruled`。帳上認的是後一條時,訊息會指到第一條。我用 `python3.14` 實測過:S1、S3 同文,`ruled={S3}` 會誤說「治理帳沒有」並叫人刪 S1。要手寫出同文重複條款才會發生,我不標 finding。
- 修補與降 C901 的拆函式混在同一個提交,binding 已註明歸因拆不開。我看到的行為變化只能追溯到本輪新增的邏輯。

**圖譜鏡頭:** 派工附的固定席筆記因鏡頭計算逾時沒附上,這一項未判定。我只看了 patch 裡改到的 `Projects/情境題答案要引規格出處與回寫循環_計劃.md` 和 `Systems/guard-kill.md`,兩者與程式行為一致,沒有可確認的錯誤。這次也沒有跑 `lumos lint`、`lumos doctor` 或任何測試。

最嚴重:minor;blocking 共 0 條
