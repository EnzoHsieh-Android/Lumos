severity: major

（來源：代碼審 r1 外家獨立找洞席，codex-cli，2026-09-15；逐字稿切出的報告本體）


## 1. 綜合排序已經不一致，計分窗仍會漏標
severity: major
blocking: 是；未標檢查漏掉實際計分候選，直接違反本次修復目的。
上游按 `(-score, hop, node)` 排序，`eval_edit` 卻按 `(-score, node)` 重排，保留上游順序不等於涵蓋綜合計分窗。
記憶體內重現：k=1，依序放 B（direct、score=0.7、L=4/7）、A（hop=1、score=0.7、L=23/30）、C（hop=3、score=0.66、L=1），觸及集只有 B、C，綜合計分第一名卻是 A。
應讓計分與未標檢查共用排序函式，並加入此同分跨 hop 案例。
引句:「★三條排法要跟 eval_edit 的 orders 用同一組排序鍵,改一邊要改兩邊★。」
file: `governance/eval/retrieval_eval.py:202`
file: `governance/eval/retrieval_eval.py:474`
file: `scripts/lumos:23285`

## 2. 放寬恆等斷言後，切換輪仍用舊尺判決並記成新尺
severity: major
blocking: 是；歷史帳的尺版本與實際 gate 判決不一致，後續評測會在資料未變時翻轉結果。
三題舊 P 分別為 1、1、0，最後一題因候選不足被新尺排除時，新斷言通過，但舊平均為 0.6667、新平均為 1，兩者在 0.70 門檻下分別失敗與通過。
切換分支只更新 `args._metric_rev`，覆寫 gate 的分支仍判斷切換前的 `_cur_mrev`，因此當輪掛新尺版本卻使用舊尺，下一輪才真正改尺。
應在切換當輪同步套用新尺判決，並以此不等平均案例驗證版本與 gate 一致。
引句:「不是全題平均(_*_raw)——後者會讓兩組不同題目的平均互比,永遠不等。」
file: `governance/eval/retrieval_eval.py:694`
file: `governance/eval/retrieval_eval.py:818`
file: `governance/eval/retrieval_eval.py:826`

## 3. 新上界斷言的輸入不足以讓它失敗
severity: minor
blocking: 否；屬於回歸測試盲點，未直接造成執行錯誤。
fixture 只有 12 個 free 候選，卻斷言去重後數量不超過 24，即使錯誤納入全部 free，這條斷言仍會通過。
同段所稱「三臂同序」也不成立：文字與圖排序會把 F10、F11 排在 F2 前，只檢查 F9 不在無法證明集合恰為前八。
應使用超過 24 個候選，並逐臂計算預期聯集後比較完整集合。
引句:「check("★仍有上界:free 側至多 3 條窗×k★", len([x for x in te if x.startswith("F")]) <= 3 * 8, str(te))」
file: `scripts/test_lumos.py:27325`
file: `scripts/test_lumos.py:27330`
file: `scripts/test_lumos.py:27333`

總結：最嚴重 severity 為 major，blocking 共 2 條。
