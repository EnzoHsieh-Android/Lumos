結論：此稿目前不可進 TDD。核心內部證據仍引用修正前數字；外部主證又把「非零 finding 輪」誤稱為「乾淨輪」。此外，候選方案與現行 cluster gate、cap、抽查記帳之間尚無可執行語意。

1. **blocker｜summary〈證據一〉：把非零 finding 輪誤稱為「乾淨輪」**

   問題：AEGIS 的逐輪缺陷數是 `15→8→12→2→8→1→4→1→0`；只有最後的 `0` 是 clean。`2→8`、`1→4` 證明的是「低 finding 數後反彈／非單調」，不是「單乾淨輪後反彈」。因此它可以反駁候選 (d) 的單調衰減假設，卻不能直接估計 K=1 clean-stop 的誤停率。論文摘要也把反彈歸因於 cascading edits 與 audit-scope expansion，與同材料隨機重審不同。[AEGIS 原文頁](https://arxiv.org/abs/2605.12280)

   查證：`r1-snapshot.md:19`；AEGIS abstract/per-round counts。

   引句：「單乾淨輪後反彈兩次(2→8、1→4);「一輪乾淨=枯竭」在該實測誤停兩次」

2. **blocker｜summary〈證據二〉＋〈回放輸出〉：snapshot 與凍結輸出仍是修腳本前的數字**

   問題：現場執行 `python3 governance/eval/k1_stop_replay.py` 後，panel 真 gate 層為：

   - toolchain code：有後續 `1`、反彈 `1/1`、右截尾 `3`
   - toolchain design：`0/0`、右截尾 `0`
   - Landmark code：`0/0`、右截尾 `3`
   - Landmark design：`0/0`、右截尾 `0`

   但 snapshot 仍宣稱「panel 直接層 n=4」及「右截尾 14」，而凍結檔仍列修正前的 `2+0+2+0=4` 個有後續觀測、`5+2+6+1=14` 個右截尾。凍結檔與現行腳本 `diff` 不一致，故「腳本同目錄可重算」現在是假的。這直接動搖內部主證的樣本量、截尾量與誤停分母。

   查證：`r1-snapshot.md:20,50`；`k1_stop_replay.py:28-43`；`k1-stop-replay-2026-08-05.txt:14-25`；實跑輸出。

   引句：「panel 直接層 n=4 觀測、反彈 1(code-relmainnet r2 乾淨→r3 major);右截尾 14≫4」

3. **major｜回放腳本分層：所稱「真 gate 三條合取」沒有覆蓋現行 cluster gate**

   問題：腳本對所有 panel 一律用「有效輪＋severity＋capture-recapture」三條件；但現行 `_loop_status_panel` 遇到首個有效輪含 `clusters` 時會轉 `_loop_status_panel_clusters`，真正判準是「最新輪有效＋跨有效輪 fold 後無 disputed-major」，capture-recapture 只是 advisory。兩本帳都已有 cluster 記錄。因此腳本不是現行 `_loop_status_panel` 的一般性回放器，最多是「無-cluster 舊帳」回放器。

   具體失敗場景：某 cluster loop 最新輪 `capture_counts` 顯示殘餘 ≥1，但所有 disputed-major 已 resolved；真 gate 可 PASS，腳本卻判非乾淨。反向地，若最新輪 severity 是 minor、capture 殘餘 <1，但歷史 fold 尚有 disputed-major，腳本會算乾淨，真 gate 會 FAIL。

   查證：`k1_stop_replay.py:28-43,76-77`；`scripts/lumos:3056-3061,3092-3115,3176-3208`；`docs/.canary-log.jsonl:128`；Landmark ledger `:150,155`。

   引句：「修:import 主檔 _estimate_remaining_defects(單一實作),panel 層乾淨輪補殘餘條件。」

4. **major｜summary〈候選設計 b〉：宣稱反彈發生在同材料，與所引證據不符**

   問題：AEGIS 明說反彈伴隨 cascading edits 和 expanded-scope rounds；內部唯一 panel 反彈案例的 round id 亦為 `r3-dref`、`r4-dref-delta`、`r5-recap`，顯示審查材料／範圍發生變化。據此不能推出「全量同材料確認輪有效、delta 無效」。相反地，現有反彈可能主要測到 material drift，而非同一 snapshot 上的審計隨機性。

   查證：`r1-snapshot.md:22`；`k1-stop-replay-2026-08-05.txt:15`；[AEGIS abstract](https://arxiv.org/abs/2605.12280)。

   引句：「★材料全量★——反彈發生在同材料上,delta 確認確不了枯竭」

5. **major｜summary〈候選設計 a/b〉＋ PRIOR-ART：不是「只動 need 參數」即可落地**

   問題：panel 路徑完全不消費 `need`；`cmd_loop_status` 直接把全部 records 交給 `_loop_status_panel`，後者只對最新 round 判 gate。故 K=2 必須新增「連續兩個 panel gate 狀態」的明確運算，而非調 `need`。

   尚未定義：

   - 每個歷史 round 的 clean 是否用當時 fold，還是用最終 fold 回看；
   - 中間無效輪是否重置 streak；
   - cluster 與無-cluster兩種模式各如何算 clean；
   - 確認輪 W=3 時，high tier 原 W=5／`--min-seats 5` 是否同步降為 3。

   查證：`r1-snapshot.md:22,24`；`scripts/lumos:3056-3062,3120,3181-3208,3719-3721`；`SKILL.md:164-168`。

   引句：「(a)/(b)只動 need 參數與席數表」

6. **major｜summary〈候選設計 d〉：帳面值與組合語意未定義，現況不能直接重算**

   問題：「存活折入數」不是明確的 round-level 欄位。panel 每輪 W 筆各有 `findings`，帳中常把同一輪總數重複寫在多席；不能直接 sum，也未說取 max、第一筆或唯一 carrier。cluster 模式的裁決真相又在 `clusters` fold，不在 findings 數。

   反例：兩輪各三席都記 `[3,3,3] → [1,1,1]`，取 max 得 `3→1` 可過，取 sum 得 `9→3` 不過；兩者消費同一本帳。另 `2→1` 雖符合嚴格遞減與末輪≤1，末輪那一條仍可能是 disputed-major，除非再與 severity／cluster fold 合取。稿中亦未裁定 (d) 是取代 K，還是 `K∧d`。

   查證：`r1-snapshot.md:21-22`；`k1_stop_replay.py:28-43`；`scripts/lumos:3192-3208`；`SKILL.md:123-126,166-168`。

   引句：「連續兩輪「存活折入數」帳面欄嚴格遞減且末輪≤1才准收斂——只消費既有 findings 欄,可重算」

7. **major｜實務隱患／候選設計 e：抽查記帳不足以稽核抽查率或形成嚇阻**

   問題：只記 `probed: true/false` 無法區分：

   - 哪些 K=1 PASS 事件進入抽樣母體；
   - 是否真的擲過；
   - 抽中但被跳過、未完成或工具失敗；
   - 使用的 p、抽樣時間、隨機來源；
   - 編排者是否在看到結果後才填值。

   因此 `canary-stats` 無法從帳本重算「應抽／已抽／完成率」，也無法偵測常態跳過。由被治理的編排者自行擲且不可稽核，對故意繞閘者沒有可信嚇阻。至少需 append-only 的 eligibility/selection/completion 三事件或等價狀態、記 p 與不可事後選擇的抽樣證據。

   查證：`r1-snapshot.md:22,38,41`；`scripts/lumos:12289` 附近現有 `canary-stats`；repo 搜尋無 `probed` 寫讀協定。

   引句：「記帳只能記 `probed: true/false`；③右截尾治理依賴 (e) 真的被執行」

8. **major｜下一步／候選設計 e：cap 與抽查失敗後的狀態機未定義，且交叉引用是壞的**

   問題：第 45 行聲稱 cap 規則「已定於〈回放輸出〉節末」，但該節只有一行凍結檔連結，沒有規則，屬硬壞引用。

   即使採用第 45 行括號內文字，仍缺：

   - 抽查發現 major 是否撤銷原 PASS；
   - 修完後要再跑 K=1、再抽一次，還是直接放行；
   - 抽查輪不計 cap，但其後補救輪是否計 cap；
   - 最多可觸發幾次抽查，避免 cap 外無界迴圈；
   - 抽查是 W=5 全量輪還是縮編輪，以及期望成本 `p×W`；
   - 使用者在 cap=3 已攤人後授權的確認輪，與隨機抽查是否為同一種例外。

   查證：`r1-snapshot.md:45,48-50`；`SKILL.md:167,191`。現有 skill 明定 panel `cap=3`，但沒有 post-convergence probe 狀態。

   引句：「抽查輪與 cap 的互動規則（抽中的覆核輪不計入 cap、其 findings 照常走處置帳）已定於〈回放輸出〉節末」

9. **minor｜為什麼現在立案：反事實案例沒有證明「明顯未枯竭時放行」**

   問題：T8／RSNO 三輪都出 ≥major，只能證明這兩次沒有收斂；「若任一輪碰巧乾淨」是未建模的反事實。現行無-cluster gate 還要求 capture-recapture 殘餘 <1，cluster gate則要求 fold 無 disputed-major，不能從「碰巧 severity clean」直接推出會放行。若保留此動機，需明確寫成假設性風險，不宜當觀測證據。

   查證：`r1-snapshot.md:34`；`scripts/lumos:3056-3061,3142-3163,3205-3208`；Landmark ledger 的 RSNO r1-r3。

   引句：「若任一輪碰巧乾淨，K=1 會在發現明顯未枯竭時放行」

逐節讀取結果：

- frontmatter／summary：已讀；findings 1–7。
- 〈為什麼現在立案〉：已讀；finding 9。
- 〈實務隱患〉：已讀；finding 7。
- 〈下一步〉：已讀；finding 8。
- 〈回放輸出（凍結）〉：已讀；findings 2、8。
- 交叉引用總查：`summary` 目標存在且含證據／候選；〈回放輸出〉目標存在但不含所稱 cap 規則，壞引用見 finding 8。

max severity: blocker
