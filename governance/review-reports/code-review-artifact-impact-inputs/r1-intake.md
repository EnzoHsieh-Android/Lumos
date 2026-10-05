# R1 收貨與修復驗收

兩席均收齐後才修改來源；原報告未改。report-normalize、quote-check、seat-check 都 rc0。refcheck 兩席 rc1：報告以反引號寫了合成案例路徑，這些不是 repo 的持久檔；不宣稱 refcheck 全通過。引句本身已錨定凍結 snapshot。COR-1 另用真 Git／CLI 控制重現，不依不存在的案例路徑推論。

| ID | 重現 | 處置 | 證據 |
| --- | --- | --- | --- |
| COR-1 | HIT | folded | r1-code-control-red.json 5過10敗；r1-repair-impact-green.json 50過0敗；r1-repair-role-green.json 59過0敗 |
| ARCH-1 | HIT | folded | 兩處 WHY 加出處與因；圖譜 lint 核查。席位說機械 lint 會提醒不等於先前實測有提醒。 |

正確性觀察成立，但 run.sh 一定產生後端角色卡的擴張說法未採為判準；真正回歸為檔案從 impact 與角色來源清單消失。架構席把目錄內正式程式說成未來問題的判準與既有 _codeloop_bookkeeping_code／測試矛盾，依既有程式例外修正，不改其原報告。

未派辯方：COR-1 已機械重現，依先紅後綠規則折入；没有以低共識理由降級。此輪不是原 Python 結果修復換編號，原 major 仍待處理。
