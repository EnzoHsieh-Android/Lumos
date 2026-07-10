# guard-kill design-loop 存活 findings（3 輪 panel，2026-07-10 凍結）

## 統計
- r1 W=5(4 canaried+veto): 3/4 caught。折入:資料模型重設(kill_recipes)、timeout歸killed、路徑圍欄、清理、hermetic限縮等 22 條。
- r2 W=5: 1/4 caught(輪無效)。折入:descope×2(hydration/lockfile,否決位裁)、gov三處硬編同步、ADR翻盤、bind歸因修正等 18 條。ghost 指控二度覆核為幻覺(s1/s4 同款)。
- r3 W=3 delta: 2/2 caught+0 missed(首個 near-perfect 有效輪)。三員同抓 descope 殭屍測試句(fold-drift 實證)+3 medium+4 minor。
- 探針:10 顆 canary 經 haiku 難度探針,2 顆重植(recraft×1)。

## 收斂裁定(編排者,使用者預先授權)
r3 輪有效+否決位「scrub 後可進實作,無設計級缺陷」+全部 ≥major 折入前機械覆核+殘餘統計為 lens-diverse 單命中假象 → 實質收斂。gate 形式未過(r3 折入項屬 major+殘餘>門檻),cap=3 到頂留痕。
opus 在密集 spec 的 canary miss 率:r1-r2 4/8——「密集 spec 審計員易漏」的又一實證(gov 分帳可查)。
