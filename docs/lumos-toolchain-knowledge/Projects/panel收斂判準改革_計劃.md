---
type: project
status: done
created: 2026-08-05
updated: 2026-08-05
aliases:
  - K=1 改革
  - 收斂判準 A 案
related:
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/design-loop重設計]]"
tags:
  - type/project
  - status/done
summary: |-
  FLAG:DECISION
  KEY:★立案動機(r1 措辭校正)★——panel 是風險最高路徑(tier=high 專用)卻配最鬆判準(一個乾淨輪即收斂 K=1);convergence-evidence-gate 自認「未經檢驗的取捨」。★範圍(r1 收窄)★:design-loop 已改走 disposal 閘(2026-08-04),本案標的=★code-loop panel★。動機屬假設性風險非既遂觀測(r1 Codex F9:T8/RSNO 未收斂是三條合取全體作用,不能推「碰巧乾淨就會放行」)——但假設性風險有內部既遂實例支撐(見證據二 relmainnet)
  KEY:★證據一(外部主證,r1 全面校正措辭)★——AEGIS 迭代審計(arXiv 2605.12280,9 輪審 7152 行 spec):缺陷序列 15→8→12→2→8→1→4→1→0,★非單調★;r4(2)/r6(1) 是論文所稱 near-clean 非 clean(0 缺陷只有末輪)——正確宣稱=「若以 near-clean 當停止訊號會誤停兩次」,「兩個連續乾淨輪」是該文★前瞻建議★非既遂實驗;★同篇反面證據誠實併入★:severity 評審一致度僅 κ=0.46——「乾淨輪」訊號本身品質有限,支持組合訊號、不支持單靠 K
  KEY:★證據二(內部回放 v2,r1 s2 席打掉 v1 後重算;governance/eval/k1_stop_replay.py 可重算)★——v1「乾淨輪」漏算真 gate 第三條件(capture-recapture 殘餘,fail-closed),18 個「乾淨」panel 輪有 11 個真 gate 本不會放行→★v1 的 n=4/右截尾 14 全數作廢★。v2(真三條合取):panel 直接層=★1/1 觀測即反彈★(code-relmainnet r2 過全部三條→r3 冒 major)+右截尾 6;樣本極薄但唯一可觀測案例就是誤停,且截尾方向=低估。legacy 類比層(語意較鬆,標注)四組全列(r2 訂正:原只留最高組=重演選擇性引用):toolchain code 8/10、design 2/6;landmark design 3/9、code 1/12。★限制(Codex F3)★:v2 未覆蓋 M2 cluster 帳分層(該帳收斂=兩條合取),cluster loops 另計待補
  KEY:★證據三★——code-slim-handoff:minor→minor→clean→clean→★major(missed)→blocker★(legacy 層):連續兩乾淨輪後仍冒 blocker=★K=2 也非銀彈★;AEGIS 尾段(1→4)同構→設計空間必須含「收斂後」防線,不能只調 K
  KEY:★候選設計(r1 大改)★——(a) K=2 連續有效乾淨輪:★非只動參數★(r1 s4:現行 _loop_status_panel 只讀最後一輪,K=2=跨輪比對的結構性改動;且與 cap=3 相衝需同步定 cap 語意) (b) K=2+確認輪縮編(確認輪=K=2 中的第二個乾淨輪,審同一版材料的複審輪;縮編=席數 5→3,r2 補回定義——r1 折入時誤砍,R16 假折教訓):★r1 兩席打出自相矛盾★(縮編削弱 capture-recapture 統計力=拿 (c) 的否決理由打自己;W 又與 _TIER_PARAMS 單寬度表衝突)→降級為「僅當殘餘檢查在縮編寬度下仍具判別力才可選」,傾向不選 (c) K=1+殘餘上界:維持否決(小樣本 CI 寬) ~~(d) 衰減率規則~~:★r1 撤除★——撞 2026-07-09 既有裁決(G2 序列衰減明文排除於平行 panel 拓樸,見 convergence-evidence-gate)+可拆分/合併操縱+帳面語意未定義,三席獨立否定 (e') ★收斂後決定性抽查(r1 全面重寫)★:原「編排者擲 p」嚇阻模型不成立(擲骰人=被嚇阻人,s3+Codex 一致)→改★可稽核偽隨機★:抽樣函數=sha256(loop_id+收斂輪 result_sha256)%N==0(任何人可重算「該不該抽」,不靠誠實);記帳=eligibility/selection/completion 三事件 append-only(Codex F7 規格);狀態機=抽中輪 findings ≥major→撤銷 PASS 回 loop(補救輪計 cap,抽查輪自身不計;抽查上限 1 次/loop 防無界)
  KEY:✅★設計審收斂(2026-08-05,新制處置閘 r1+r2)★——r1 W5(15 組全折,carrier 引句 1 miss 被閘正確咬住)→r2 delta 確認(抓 1 假折+選擇性窄化自我重演+無餌輪 kind 缺口,3 組全折)→DISPOSAL GATE PASS。★方向=主推 (a)+(e') 組合,最終選型與實作啟動歸人裁★
  KEY:★r1 收斂傾向★——主推 (a)+(e') 組合:K=2 治單輪反彈、(e') 治 K=2 也擋不住的尾部+右截尾盲區;(b)(c)(d) 各有結構性否決
  KEY:★排除項★——SPRT(arXiv 2605.19193 作者自證判別型失效);(d) 見上
  PRIOR-ART:①最小解界線(r1 校正):(a) 是結構性改動非參數調整;(e')=d4 隨機化+G3 hash 慣例的組合(sha 決定抽樣=零新依賴) ②世界解(2026-08-05 真搜):AEGIS 非單調序列(措辭已校)/capture-recapture 十年回顧(Mh-jackknife 穩健但小樣本 CI 寬)/Dalal-Mallows 借思想/SPRT 排除;LLM 判官 3-5 runs 平台期降級為方向性引用(細節未能全查證,r1 s2) ③裁定=borrow-design(零依賴)
  KEY:★誠實天花板★——內部回放:panel 直接層 n=1(真 gate 語意)不足以獨立定案,主證在外部+截尾方向論證;severity=當時辯方後自報不可重審;cluster 帳分層未覆蓋;legacy 層語意較鬆只當方向佐證。★self-governance 循環★:改閘的 spec 由(design-loop 的)閘審——非同一個閘,但同族機制,r1 已照新制走完並被抓出 15 組 findings=循環至少在工作
  DEP:scripts/lumos(_loop_status_panel / _round_valid_m2 / _estimate_remaining_defects 三函式)｜governance/eval/k1_stop_replay.py｜skills/lumos-code-loop/SKILL.md｜skills/lumos-design-loop/SKILL.md(K=1 陳述連動,r1 s4)
---
# panel 收斂判準改革（A 案）

> 白話：現在的規則是「五個審查員一輪全醒著、沒挖到大洞、且統計上母體看似枯竭，就蓋章收工」。外部實測與我們唯一可觀測的內部案例都顯示：缺陷會回馬槍——這輪乾淨不代表挖完了。本案要用證據換一把更誠實的尺，方向是「多守一輪＋收工後可稽核的抽查」。

## 被翻紀錄(2026-08-08)
本計劃之 A 案收斂制(K=2+決定性抽查)與**防浮動條款**(「落地後不得論證型翻案;唯一通道=20 筆抽查帳」)已由 Enzo 具名推翻——見 [[Projects/驗證層去模型化_計劃]](S2b,signoff 留痕):條款前提「canary 閘可信」被非平穩性論證動搖,陷自我引用。code-loop 收斂改走 `--disposal`;**A 案機制碼與 `t_panel_k2_and_probe` 迴歸測試保留不刪**(舊帳重放/golden replay 消費)。

## 被翻紀錄二(2026-08-25,與上段是兩件不同的事)

上段(08-08)翻的是**閘切換**(canary 可信度前提動搖→code-loop 收斂改走 --disposal,當時實作只落到單席)。本段翻的是**多席路由+抽查機制**:Enzo 甲裁([[Projects/probe輪退場_計劃]] decisions d3)——多席 code-loop(含 high)亦統一走處置閘(d5 型彙總記帳),panel 閘轉純歷史回放(新迴圈 cutoff 拒判);probe 抽查輪義務退場(零觸發三週+三配套零實作);本計劃防浮動條款的「唯一翻案通道=攢滿 20 筆抽查帳」隨之正式作廢(具名),「判準凍結」句保留為回放語意。配套加嚴:code 迴圈處置閘輪內有 major 席則 accepted 必空(decisions d2),與本計劃 A 案「存活 max≤minor」同嚴度。

## 為什麼現在立案

K=1 是 convergence-evidence-gate 記錄在案的「未經檢驗的取捨」。本案動機為**假設性風險**（r1 校正：T8/RSNO 未收斂是三條合取共同作用的結果，不構成「碰巧乾淨就會放行」的觀測證據）——但 relmainnet 提供了一個**既遂實例**：r2 通過全部三條真合取，r3 冒出 major。範圍：**code-loop panel**（design-loop 已走 disposal 閘）。

## 實務隱患

- **併發**：只動收斂判準（讀側純函數）；(e') 抽查記錄走既有 `canary record` 原語＋新增三事件行（append＋讀回自驗），無新併發面。
- **效能**：gate 人工節奏呼叫，判準 O(帳面輪數)，無熱路徑。
- **資源**：無新連線/檔案生命週期；回放腳本唯讀、路徑已參數化。
- **self-governance 特有**：①改閘的 spec 必須過 design-loop 審（r1 已走完，15 組 findings 全處置）；落地測試需含「舊帳在新判準下的回放對照」防靜默放寬。②(e') 抽樣改為 sha256 決定性函數後**可稽核**（r1 重寫：原「編排者擲 p」不可稽核且無嚇阻力）；殘餘不可稽核面只剩「編排者假裝沒看到抽中」——由 eligibility 事件（PASS 時機械落帳）+canary-stats 曝光「應抽未抽」堵住。③抽查輪常態被跳過的偵測=canary-stats 新增「應抽/已抽/完成」三欄（Codex F7 規格）。

## 落地面（r1 折入，實作時逐項處理）

1. `_loop_status_panel` 結構改動：現只讀最後一輪（`next(reversed(groups))`），K=2 需跨輪比對——動的是判定迴圈不是參數（s4-F3）。
2. cap 語意：cap=3 與 K=2 的互動明定——收斂需要的第二個乾淨輪**計入** cap；cap 撞頂時未湊滿 K=2 照現行攤人（s4-F2）。
3. `_TIER_PARAMS`/`--min-seats` 單寬度表與任何縮編設計的衝突（s4-F4）——(b) 若不選則自然消滅。
4. 兩份 skill 的 K=1 權威陳述連動改寫（code-loop SKILL「panel K=1 唯一權威說法」段、design-loop SKILL 舊 panel 節；s4-F5）。
5. 舊帳相容：新判準**不回溯**——以「loop 首筆記錄日期 ≥ 落地日」定錨適用（借 T6 定錨慣例；s4-F6）；進行中 loop 沿舊判準收尾。
6. (e') 三事件記帳 schema＋`canary-stats` 抽查率欄＋抽查狀態機（撤銷 PASS→補救輪計 cap→再收斂需重新 K=2；抽查上限 1 次/loop）。
7. 回放腳本 v3：補 M2 cluster 帳分層（Codex F3）。
8. 未植入輪的記帳語意（r2 自抓）：新制「隨機決定植不植」落地時，`canary record` 的 kind
   仍是必填 caught|missed——無餌輪兩個值語意都是錯的（d4 下不進合取故無機械後果，
   但帳面誠實性缺口）。落地時補 `--planted` 欄或 kind 第三值；過渡期 note 明記 planted:false。

## 防浮動條款（2026-08-05 Enzo 裁定方向後定版）

1. **凍結**：本次落地後，panel 收斂判準凍結，不受理論證型翻案。
2. **唯一翻案通道＝抽查帳**：累積 **20 筆**抽查完成記錄（probe-* 輪）前不重開判準討論；
   攢滿後照預先規則調——抽查漏率≈0 → 可裁 K 降回 1 或抽查率調低；漏率高 → 加嚴。
   調鬆調緊都只走這條路。
3. 本條款自身可重算（抽查輪筆數＝帳面機械事實），非口頭承諾。

## 下一步

1. ~~r1 審~~（✅ 2026-08-05 走新制處置閘完成，見〈審計紀錄〉）。
2. ~~細部補完＋TDD 落地~~（✅ 2026-08-05 Enzo 裁「開工」後完成：K=2 跨輪窗
   [cutoff 2026-08-06 定錨不回溯，env 可覆寫]＋cluster 路同窗＋PASS 印決定性抽查判定
   [sha256(loop_id+rid+該輪 token 集)%2，帳面輸入、人人可重算]＋撤銷自動化
   [probe 輪冒 major → K=2 窗滑入髒輪 → gate 自然 FAIL，零新機制]；
   `t_panel_k2_and_probe` 6 斷言紅→綠＋突變釘精準（拔 K=2 窗→3 條翻紅無誤傷）；
   兩份 skill K 值段連動改寫；測試套件 pin 舊制防 cutoff 時間炸彈。全套 2344 綠。）
3. 待補（不擋收工）：canary-stats 抽查稽核欄（落地面 8 部分）、回放腳本 v3 cluster 分層（落地面 7）。

## 回放輸出（凍結）

- v1（已作廢，留檔供對照）：`governance/eval/k1-stop-replay-2026-08-05.txt`——「乾淨輪」漏第三條件，n 高估，r1 s2 席抓出。
- **v2（現行）**：`governance/eval/k1-stop-replay-2026-08-05-v2.txt`（腳本同目錄可重算；真 gate 三條合取；cluster 帳分層待 v3）。

## 審計紀錄

### r1（2026-08-05，design-loop 新制處置閘，W=5）

canary＝壞內部交叉引用（「抽查輪與 cap 互動規則已定於〈回放輸出〉節末」——該節無此內容；probe:pass 全文餵）。**caught 4/5**（s1 通才/s3 對抗面/s4 整合面/Codex），missed 1（s2 證據面）——★s2 雖 missed，其 blocker（回放定義漏第三條件）經機械重跑證實折入（d4：missed 不作廢 findings 的又一實證）★。

### r2（2026-08-05，delta 確認輪，W=1 縮編＋coin=0 未植入）

單席審折入忠實度：12/15 組抽驗，11 忠實、★1 假折抓到（R16 確認輪定義——宣稱處置實則砍掉，已補回）★；
另 R17（legacy 證據被我窄化成只留最高組——選擇性引用自我重演，已補全四組）、
R18（未植入輪 kind 語意缺口，自抓，入落地面 8）。r1 Codex 被拒引句的實質內容確認已隨 (d) 撤除解決。

### r1 處置

處置：15 組 findings **全折**（R1 回放 v2 重算/R2 AEGIS 措辭校正+κ=0.46 併入/R3 (d) 撤除/R4 範圍收窄 code-loop/R5 (b) 降級/R6 (e) 重寫為可稽核偽隨機+三事件+狀態機/R7-R10 落地面 1-5/R11 cluster 分層待 v3/R12 動機改假設性風險/R13 確認輪定義/R14 腳本參數化/R15 引文降級），accepted 0。留痕：`governance/review-reports/panel收斂判準改革/`。
