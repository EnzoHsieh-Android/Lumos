---
type: project
status: doing
created: 2026-08-29
updated: 2026-08-29
tags:
  - type/project
  - status/doing
---
# intake守衛_計劃

> **★v3(2026-08-30)。r2 三席 24 條全折(1 blocker=編排者數字三犯;外家承認 r1 四條真解、但裁「升級迴路不機械接上就不做」)。★** v1/v2 快照與逐輪彙總在 `governance/review-reports/intake-guard/`。

PRIOR-ART: **借用既有樣板,不建新機制、不加依賴**——①宣告行照報告 `severity:` 行的行首錨定 fullmatch 型(`scripts/lumos:3750` `_report_severities`),並補「先剝 fenced 圍欄再掃」的前處理(r2 實測同款 parse 對圍欄內頂格行照計,模板照抄即偽造)②讀側驗證落處置閘(它本來就逐檔重驗留痕 sha)③**升級計數器落 doctor**(每天真的在跑、印給人看的既有通道——外家 r2 的裁定:計數靠散文=到第六案也不會發生,repo 有提醒被無視 546 次的帳)。
★引用訂正(r2 正確性 F1)★:v2 曾引嚴重度綁定案當「先 advisory 後硬擋」前例——**引反了**,該案實為外家否決 advisory 優先、反轉首日硬擋。v3 誠實承認:兩段式在本 repo 沒有完整前例;採它的理由是 r1 的實測(首日硬擋殺自主迴圈+大量測試),不是前例背書。**已排除**:自動化宣稱抽取工具(2026-08-25 明文,不翻);v1 首日硬擋與「$ 或反引號」判準;v2 的 claims 計數行(r2 b-F8:無任何讀者的死資料,砍)。

## 立案基礎(數法寫死,r2 b-F14/c-F2 折入)

**數法**(可重跑;CJK 目錄名須經 `core.quotepath=false` + python 切段,shell for 迴圈會炸):
`git -c core.quotepath=false log --diff-filter=A --since=2026-08-25 --name-only --pretty=format: -- governance/review-reports/` → 取路徑第三段為迴圈目錄 → 逐目錄查有無 `*intake*` 檔。
**結果(2026-08-30 實跑)**:27 個目錄、**16 個無 intake**(code 類 11 目錄 9 無;非 code 16 目錄 7 無)。任一切法皆遠超三修計劃:50 登記的「連兩案缺席→再議」門檻;**本設計審即該再議**。
★v1 引錯門檻(挑寬的)、v2 的 11/18 四種切法無一重現——同案數字三犯,故本節連數法一起釘死★。

## v3 設計(T1-T3 不擋 + T4 機械計數器)

### T1 · intake 宣告行(格式層,進模板正本)

`rN-intake.md` 首部一行(照 `severity:` 型,**先剝 fenced 圍欄再逐行 fullmatch**;示例不帶任何行尾註解——v2 的示例帶箭頭,過不了自己的 parser,r2 b-F7):

```
preflight-4: ran
```

- **值域封閉**:只有 `ran` 一值。前掃跑了(含「跑了但零命中」)都寫 `ran`;沒跑就沒有這行。claims 計數行**砍除**(r2 b-F8:無讀者的死資料)。
- **同檔多行=格式壞**,視同無宣告行(fail-closed,但後果只是 T2 的 ⚠,不擋)。
- **intake 綁迴圈不綁輪**(r2 b-F4/c-F5:實帳 11 份有 10 份在 r1、判定輪幾乎都是 r2+,綁輪必長噪):前掃是首輪一次,r2+ **不需**再產;規則=「迴圈目錄裡**至少一份** `*intake*.md` 含合法宣告行」即滿足。
- 落點:`skills/lumos-design-loop/templates.md` intake 慣例正本 + SKILL.md 步驟 2。**範圍刀撤除**(r2 b-F3/c-F2:code-batch2/3 實有 intake,「code-loop 無 intake 概念」與實帳相反)——慣例對所有審查迴圈開放,模板的 `[--intake]` 選配提示不分流。

### T2 · 處置閘 advisory 一行(讀側,不進合取不改 rc)

`loop status --disposal` 判定時多印一行觀測:
- 迴圈目錄含合法宣告行 → `[disposal] intake: ✓`
- 目錄存在但無 → `⚠ 迴圈目錄無帶 preflight-4 宣告行的 intake——首輪前掃第四類可能沒跑(慣例=skills/lumos-design-loop/SKILL.md 步驟 2)`
- **迴圈目錄不存在 → 跳過不印**(scratch 迴圈如自主迴圈的 /tmp 工作區;r2 b-F1:不跳會每天印進沒人讀的 log)。
- 讀 intake 檔的文字讀**帶 errors="replace"**(r2 c-F4:v2 把它掛在 T3——但 T3 四行為全走二進位無從解碼,真正要防炸的是這裡)。
- 誠實承認覆蓋邊界:panel/light/settle/legacy 不走 --disposal,T2 蓋不到(r2 b-F2)——它們是舊帳路徑,新迴圈一律處置閘,缺口隨舊帳退場自然收斂;不另建。

### T3 · 帳面選配欄 `--intake`(寫側,選配不必附)

同 v2,兩處修正:①**砍 errors="replace" 條款**(掛錯邊,見 T2)②**處置閘③的逐檔 sha 重驗補 intake 一項**——帳列有 `intake_path` 就重驗(照 report/snapshot 同迴圈),沒有就跳過;否則 `intake_sha256` 成為帳裡第一個讀側沒人驗的欄位,正是 v2 引來反對的形狀(r2 c-F3/b-F9)。互斥 tuple 照 v2 加(理由句訂正:不是「唯一」——`--scope-lines` 等本就不在 tuple——是「不加就再添一個」,r2 c-M3)。

### T4 · doctor 觀測段(★升級迴路的機械閉環,外家 r2 的裁定★)

doctor 新增一段 advisory(提醒不擋,照 [S]/[S2] 的形態):用〈立案基礎〉寫死的數法,數「慣例落地後迴圈目錄 vs 含宣告行的目錄」,印比率。**觸發句**:累積 ≥6 個新目錄後,若含宣告行比率 <5/6,且其中任一缺席迴圈的帳面有 blocker 輪(★嚴重度是帳面欄位,機械可讀——取代 v2 不可判定的「B 桶型」,r2 c-F6/b-F12★)→ 印「轉硬擋條件已達,去裁:Projects/intake守衛_計劃」。
- **數數和喊人的是機器(doctor 每天跑),決定升不升的仍是人**——這就是外家要的「自動計數、觸發、排程」,用 repo 現成通道,不建新排程。
- 落地時 Verification 節點的 `revalidate_when` 同步寫此條件(r2 b-F13:計數事件沒有關鍵字會命中 stale 掃描,doctor 段就是替代的回頭機制)。

## 實務隱患(逐類答;v2 各條結論不變者略,僅列變動)

- **自主迴圈**:T2 對不存在的目錄跳過 → 每日輪零噪音;T3 選配不擋。已排除。
- **測試/模板**:T3 選配 → 既有測試呼叫點不需改(★v2 的「87 個」數字撤回——r2 c-M4 數不出來,且結論不依賴該數★);模板加 `[--intake]` 選配段不分流(範圍刀已撤,r2 c-M5 的前提消失)。
- **★真隱患:宣告行可寫 ran 但沒跑★**:不變,靠席位覆核;T4 的重驗條件抓「宣告了仍出 blocker」的形態。
- **★真隱患:T4 又是一個 advisory,會不會重演 546 次無視★**:T4 與既有 advisory 的差別=它印的是**帶觸發句的裁決請求**(條件達成才出現,不是每天同一句);且條件寫進 revalidate_when 雙保險。誠實講:最後一步仍是人,無法再機械化——「放行永遠人手動」是本 repo 的定調(autonomous-iteration-loop d1),不是本案的缺陷。
- 其餘(併發/回滾/不可逆/零依賴/前置加重/應試化):同 v2,結論不變。

## 誠實天花板與重驗條件

- T1-T4 只把「前掃缺席」從靜默變**可見且可裁**,不證明前掃跑得對;「ran」真偽機械驗不了。
- 「前掃跑了仍漏」的召回問題不在本案。
- 重驗=T4 觸發句 + Verification `revalidate_when`(落地時寫);權威節點同步(三修計劃:50「無機械擋」、d4「純 skill 文件」在 T2-T4 落地後過期,**落地時一併更新**)。

## r1/r2 審計修正紀錄

**r1(五席,約 36 條、10 blocker 全折)**:首日硬擋殺自主迴圈+87 測試紅+模板跑不動+11 份 intake 全過不了 S2+S2 判準不可實作+code-loop 溢出 → v2 改 advisory+選配;F7 有檔≠有跑 → 宣告行;架構④寫側-only → 讀側落處置閘;立案門檻引錯(挑寬的)→ 改用機械數。
**r2(三席,24 條全折;外家承認 r1 四條真解)**:b-F14/c-F2 數字三犯 → 數法寫死進 spec;c-F1 PRIOR-ART 引反 → 誠實訂正;b-F4/c-F5 綁輪長噪 → 綁迴圈;b-F3/c-F2 範圍刀與實帳相反 → 撤除;b-F6/b-F7 圍欄假命中+示例壞 → 剝圍欄前處理+乾淨示例;b-F8 claims 死資料 → 砍;c-F4 errors="replace" 掛錯邊 → 移 T2;c-F3/b-F9 sha 無讀者 → 處置閘③補 intake;外家+b-F13+c-F6 升級迴路散文 → T4 doctor 機械計數;b-F12 B 桶不可判 → 改帳面 blocker 輪(機械可讀);c-M3「唯一」不實 → 訂正;c-M4 87 不可重現 → 撤回;b-F5/c-M1 非 rN 輪號 → 綁迴圈後不再需要輪映射;b-F10 /tmp 路徑爛帳 → 處置閘③重驗即兜底(讀不到照 report 慣例擋);b-F11 出現率分子分母 → T4 數法寫死+scratch 目錄天然不在母體。

## 相關

- 升級條件出處:[[Verification/2026-08-25_迴圈摩擦兩修落地]] + [[Projects/迴圈摩擦三修_計劃]](:50 門檻「連兩案→再議」,v3 以此為準)
- 宣告行樣板:`scripts/lumos:3750`;doctor advisory 形態:[S]/[S2] 各段
- 同軸:[[Projects/結清式收斂_計劃]];觸發事件:[[Projects/impact鏡頭機械化_計劃]]
