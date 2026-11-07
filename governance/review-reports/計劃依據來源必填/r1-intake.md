preflight-4: ran

# 計劃依據來源必填 — 設計審前掃收貨(r1 之前)

前掃四類:①未定義詞 3、②壞引用 2、③範圍自相矛盾 3、④機械宣稱驗語意 3。全部折進 `docs/lumos-toolchain-knowledge/Projects/計劃依據來源必填_計劃.md`,逐條去向如下。

## ① 未定義詞

1. 上線日沒定義
   - 前:〈用詞〉「新計劃:開頭欄位 `created` 在本案上線日(含)之後的計劃」,沒給日期、沒說用哪個常數。
   - 後:計劃日期沿用 `_plan_effective_day`(created 與第一次進 git 取較晚者);生效日另立常數 `_PLAN_SOURCES_SINCE`(值取實作合併隔天,同 `_HIGH_RISK_EVIDENCE_SINCE` 取法),讀法照 `_expected_since`(環境變數 `LUMOS_PLAN_SOURCES_SINCE` 覆寫,測試總檔預設 9999-12-31);寫明不共用 `_HIGH_RISK_EVIDENCE_SINCE` 的理由(值 2026-11-06 早於本案合併會追溯擋、測試開關會綁在一起);另補「舊計劃」定義。
2. 「逐列查證那份計劃」沒有節點
   - 前:〈不做〉與〈天花板〉寫「逐列查證那份計劃」,像是既有節點。
   - 後:範圍 4 寫明「後續另開一份計劃(暫名「Android寫法型錄逐列查證_計劃」,還沒建)」,〈不做〉〈天花板〉REVISIT 都改指這個暫名,不寫成 `[[連結]]`。
3. 「查證員結果」不可查
   - 前:依據來源表「實測 2026-11-06:查證員結果 /private/tmp 暫存」。
   - 後:刪掉查證員結果與「抽查 11 列,2 列相反、1 條誤報」(找不到可查出處);改成用 `check.py` 讀表的實數,出處指本檔〈型錄計數〉節的指令。

## ② 壞引用

1. `[[Projects/Android現成檢查接上CI與推送前_計劃]]` 本分支不存在
   - 前:`related` 與依據來源表各一處連結。
   - 後:兩處連結都拿掉(`related` 改放實際沿用的 `[[Projects/高風險測試證據加嚴_計劃]]`);範圍 4 改文字描述「分支 `EnzoHsieh-Android/android-lint-ci` 上的「Android現成檢查接上CI與推送前_計劃」(待合併進主線)也改同一支 `check.py` 的 `catalog_problems`,本案實作前先等它合併」。
2. `/private/tmp` 暫存出處
   - 前:同 ①3。
   - 後:同 ①3,出處改成本卷證檔路徑加指令。

## ③ 範圍自相矛盾

1. 實務隱患守衛面那一行
   - 前:「守衛面:規格閘多一道會擋的檢查,屬守衛面,走完整設計審」,規格閘判門時唸「實務隱患節缺已排除行:守衛面」。
   - 後:「守衛面:不排除——規格閘多一道會擋的檢查、健檢多一則提醒,動的是守衛面;判風險高,走完整設計審(lumos-design-loop),不寫成已排除」。本案確實動守衛面,不硬寫成已排除;規格閘那句提醒照舊會印,是預期的。
2. S2 沒測「有節但缺出處列」
   - 前:S2 只測缺節、done 不列、20 篇上限。
   - 後:S2 加「有節但有一列出處欄五種都不是 應 列出」「每列都合格 應 不列」,預期值表加一列。
3. 自己的依據來源不合自己的定義
   - 前:型錄那列出處是「查證員結果 /private/tmp 暫存」,既不是指令也不是卷證路徑。
   - 後:「實測 2026-11-06:`governance/review-reports/計劃依據來源必填/r1-intake.md` 〈型錄計數〉節的指令」——repo 內存在的卷證路徑,內含可重跑指令,符合〈用詞〉出處第⑤種。

## ④ 機械宣稱驗語意

1. 「跟預期值表同一個出口」實作會漏判
   - 前:範圍 1「跟預期值表同一個出口」,PRIOR-ART ③「沿用同一個做法與出口」。
   - 後:讀 `_spec_gate_front`、`_spec_gate_clause_part`(零條款且風險不是低直接回 0)、`_spec_gate_expected_part`、`_expected_requirement`(只查風險高、生效日後、至少一條新行為條款)後決定:新開 `_spec_gate_sources_part`,插在 `_spec_gate_pending` 之後、`_spec_gate_clause_part` 之前,形狀同 `_spec_gate_pending`(擋回 1、沒事回 None),不看門、不看條款,`--no-run` 也照查。S1 加零條款新計劃、風險低新計劃、`--no-run`、複製舊計劃四個案例,預期值表加三列;依據來源表加「插入點」一列。PRIOR-ART ③ 改成只沿用「規格閘、退出碼 1、生效日機制」,並註明不能掛在預期值表後面。
2. 只用 `created` 判新舊
   - 前:〈用詞〉與實務隱患「用 `created` 判新舊」。
   - 後:改沿用 `_plan_effective_day`(見 ①1);實務隱患逐一寫複製、搬檔改名、regen、淺複製四種情形的結果,淺複製只看 created 會漏判複製來的舊計劃,同預期值表既有限制。依據來源表加「新舊計劃怎麼判」一列。
3. 「139 列」對不上
   - 前:「型錄 473 列只有 139 列有逐列查證紀錄」。
   - 後:用 `check.py` 的讀表重算(見下節):主表 473、來源欄有 `〔查證 YYYY-MM-DD` 140、名稱標(出處不全)29(其中 20 列同時有查證紀錄)、照範圍 4 口徑還沒逐列查證 324。139 是誤數,改成 140 並寫出口徑。

## 型錄計數

口徑:主表 = `skills/kotlin-idioms/checks-catalog.md` 在「## 情境決策表」之前、`_MAIN_ROW_RE` 認得的列;欄位用 `_cells` 切,第 12 欄是來源、第 2 欄是名稱。「有查證」= 來源欄有 `〔查證 YYYY-MM-DD`;「還沒逐列查證」= 來源欄沒有網址、沒有 `〔查證 YYYY-MM-DD`、名稱沒標(出處不全)。

指令(在 repo 根執行,2026-11-06 跑出 473 / 140 / 29 / 140 / 324):

```
cd configs/ast-grep/kotlin-android && python3.14 -c '
import re, check
t = check.CATALOG.read_text(encoding="utf-8")
rows = [check._cells(l) for l in t[:t.find("\n## 情境決策表")].splitlines() if check._MAIN_ROW_RE.match(l)]
ver = lambda s: re.search(r"〔查證\s*\d{4}-\d{2}-\d{2}", s)
print("主表", len(rows))
print("有查證", sum(bool(ver(c[11])) for c in rows))
print("出處不全", sum("(出處不全)" in c[1] for c in rows))
print("來源有網址", sum(bool(re.search(r"https?://", c[11])) for c in rows))
print("還沒逐列查證", sum(not re.search(r"https?://", c[11]) and not ver(c[11]) and "(出處不全)" not in c[1] for c in rows))
'
```

# r1 收貨(2026-11-06,四席:通才、可行性、依據、架構對齊,皆 sonnet)

## 收貨三道

- 正規化:四份已是正規化格式。
- quote-check:第一次交件依據席只認得 F1(F2 引句少結尾 」、F3–F10 沒用「」包),架構對齊席 F3 引句內含「」被截斷;兩席退回原席只重寫引句(內容、條數、等級不動),重交後四份全數錨定。
- refcheck:通才 9/9、架構對齊 18/18、依據 6/6 對得上;可行性沒有 file:line 佐證。
- seat-check:派工單是按席位分的 `seats[]`,工具只讀頂層 `materials`,直接跑會判「沒東西可對」(之前各輪都是這樣);改成逐席另造單席派工單副本(scratchpad)再跑。四席都標 unreported(報告沒寫出快照路徑),但引句全錨進快照,判定有讀;只觀測不擋。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 可行性-F1 | 讀 `_plan_effective_day`:兩個日期都讀不到回 None,計劃寫「讀不到當新計劃」→ 不看生效日一律新;席位實跑 `-k spec_gate_expected` 2 條斷言紅 | HIT |
| 通才-F4 | 臨時 repo 實驗(git 2.39.2):rebase 後加檔那筆 作者日 2026-10-01、提交日 2026-11-06;soft reset 壓提交與 `merge --squash` 兩個日期都變今天;`_plan_first_day` 用 `%cs`(提交日) | HIT |
| 通才-F2、可行性-F2 | 讀 android-situation-evidence 的 `check.py` `dt_sources`:縮寫照〈來源縮寫〉表展開成網址,所以拿得到網址,但多半是工具或文件首頁層級,不是逐列查證過的那頁;範圍 5 要的讀表函式已由盲判那條線實作 | HIT(部分:「拿不到網址」不成立,「不是逐列查證過的出處、計劃沒交代」成立) |
| 依據-F10 | 在 Systems 開頭欄位 about_code 找:`scripts/templates/graph-discipline.md` 的家是 `Systems/lumos-cli-lifecycle`(計劃 lands_in 已列,席位說家在診斷迴圈先行不成立);`skills/lumos-design-loop/SKILL.md` 的家是 `Systems/convergence-evidence-gate`、`Systems/lumos-refcheck`;`skills/lumos-code-loop/SKILL.md` 的家是 `Systems/每輪修補差異派工`(本案折入要改這兩份,lands_in 沒列) | HIT(部分) |
| 通才-F3、依據-F4 | 讀 `_spec_gate_pending` 等各道:擋下只印與回 1,不寫治理帳 | HIT |
| 其餘 | 讀計劃快照原文即可確認(缺定義、缺交代、缺接口) | HIT |

## 先查世界

PRIOR-ART:出處合格判法——查 Wikipedia 可查證性政策(https://en.wikipedia.org/wiki/Wikipedia:Verifiability ):要求引用「明確支持」那段內容,且沒有出處的內容可被移除;但「支持」靠人判,機器只做得到「有沒有可查的出處」。採用:機器只判格子裡有沒有一個可查的出處(含即可,不看開頭),「支持不支持」明寫交給審查席;排除:想用字面規則判支持與否。
PRIOR-ART:擋下要留帳、誤判率要量——查 Google Tricorder(Sadowski 等 ICSE 2015,https://research.google/pubs/pub43477/ 一系;ICSE SEIP 2021 https://lup.lub.lu.se/search/files/91080778/ICSE_SEIP_2021_MEAN_final.pdf ):把「使用者不想看到的報告」定義為誤報、持續量「not useful」比例並要求低於約 10%。採用:擋下時寫治理帳事件(帶被擋的格子原文),REVISIT 時抽樣判誤報;排除:不做「標成沒用」按鈕(規格閘是命令列,沒有回饋介面,抽樣比較便宜)。
PRIOR-ART:作者日期與提交日期——git 官方對 rebase 的 `--committer-date-is-author-date`、`--ignore-date` 兩個選項說明(https://git-scm.com/docs/git-rebase )加本機實驗(上表通才-F4):rebase 保留作者日、壓提交兩個都換。採用:不改共用的 `_plan_first_day`(會連帶改預期值表的判定),被 rebase 或壓提交後判成新計劃的舊計劃,代價是補寫這一節,跟使用者「所有機制的依據來源最後都要補回計劃」方向一致,寫進實務隱患與天花板。
PRIOR-ART:「機制」的粒度——查架構決策紀錄的「重大決策」定義(Fowler「希望一開始就做對的決定」、Booch「改起來代價高的設計決定」,https://ozimmer.ch/practices/2021/04/23/AnyDecisionRecords.html ;一份紀錄只記一個決定):採用「一個可以被單獨質疑為什麼是這樣的選擇=一列」;排除:用改動代價當門檻(本案要的是每個機制都有出處,不只重大的)。

## 分組與去向(全數折入)

- 甲 出處判法:通才-F1、架構對齊-F1(major);架構對齊-F2、通才-F6、依據-F6、依據-F7、依據-F8(minor)→ 一支共用函式、格子裡「含」一個合格出處即可、使用者原話與實測後面要有實字、日期要合法;寫明跟預期值表來源格、型錄來源欄、筆記 `[出處:]` 是不同物件不同門檻;節與表的找法重用預期值表那組;定義依據欄與出處欄分工;改本計劃自己的表。
- 乙 擋下留帳:通才-F3、依據-F4(major)→ 擋下寫治理帳;RETIRE-IF 改成量得到的條件。
- 丙 新舊判斷:可行性-F1、通才-F4(major)→ 讀不到日期當今天;rebase/壓提交寫進隱患與天花板。
- 丁 型錄與盲判:通才-F2、可行性-F2、依據-F5(major);架構對齊-F4(minor)→ 範圍 5 改「已由盲判那條線實作」、撤 S4;逐列查證紀錄只認〔查證〕;寫明兩層口徑與期間怎麼守既有 WHY;計數另開函式不進 problems。
- 戊 推送前覆查:依據-F1(major)→ 推送前小改動閘對範圍內新計劃重查同一支函式。
- 己 跟先查世界的關係:依據-F2(major)→ 寫明三處分工;兩份審查手冊各加一句;lands_in 補家。
- 庚 機制定義:依據-F3(major)→ 〈用詞〉加定義與粒度;補本計劃自己漏的列;天花板保留「判不出每個機制都有一行」。
- 辛 健檢只列新計劃:通才-F5、依據-F9、可行性-F3(minor)→ 跟規格閘同一個新舊判斷;範圍定義;不算進健檢問題數。
- 壬 訊息與家:架構對齊-F3、依據-F10(minor)→ 擋下訊息照預期值表三塊;lands_in 補手冊的家。
