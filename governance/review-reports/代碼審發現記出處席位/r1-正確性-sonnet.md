severity: major

我把整份 spec 逐節讀完,並對照 `scripts/lumos` 與真帳 `docs/.canary-log.jsonl`(6596 行)查證。下面共 5 條 finding,2 條 blocking。

## 固定席

- **canary-audit 的 ★INVARIANT★ `canary record/second 回報成功 ⟺ 已落盤可讀回`**:不影響。新增的必填檢查都在寫帳前 rc 2 擋下,沒有碰落盤與 readback 那段。
- **canary-audit 的 ★INVARIANT★ `second 紀錄純 telemetry`**:不影響。`finding_seats` 掛在載體上,不是 second 列,處置閘也不讀它。
- **loop-convergence-recording**:不影響,spec 沒有改處置閘或收斂判定。不過它的 d4 決策見下面第 5 條。

## 各節判讀

- 白話、用詞、舊否決比對、範圍、做法:有 finding,見下。
- 驗收條款:S1 與 S3 有 finding(第 1 條)。
- 預期值表:S2、S5、S8 的數字我逐列手算,與 spec 一致,無 finding。S8 算出正確性 2 條沒用 0、架構對齊 2 條沒用 2、通才-opus 1 條沒用 0。
- 回退、實務隱患、依據來源:已讀,無 finding。

---

## Finding 1:「帶不帶 --round 都算」是死分支,S1 與 S3 的子句無法成立

severity: major
blocking: 是
判準:照 spec 字面實作並寫測試,有一半驗收子句根本觸發不到,測試會因別的原因紅或綠。

spec 在〈範圍〉②、〈做法〉必填條件、S1、S3 都主張「本筆沒帶 `--round` 的載體也算,且席名只能是本筆自己的 auditor」。

引句:「代碼審載體(帶 `--findings-set`,帶不帶 `--round` 都算)在「這條迴圈首筆帳不早於生效日」時必填」

現況是帶 `--loop` 與 `--findings-set` 卻沒 `--round` 的載體,更早就被擋了:

file: `scripts/lumos:19861`:`if loop and findings_set is not None and not (round_id and auditor)` 直接 rc 2,訊息是「處置帳必須綁 --round 和 --auditor」。

這道擋在 spec 說的檢查位置(讀同迴圈帳之後)之前。所以:

- 「沒帶 round 的載體必填」永遠走不到。
- S3 後半「本筆沒帶 `--round` 時,席名不是本筆 auditor 就擋」寫不出能驗證它的測試。實作者實際測到的是舊訊息,不是 `--finding-seat` 的訊息。
- 沒有 `--loop` 的載體不是 `code-` 開頭迴圈,本來就不適用。

建議:刪掉這個分支與「帶不帶 --round」的說法,或明講它是舊訊息先擋。

## Finding 2:統計「每個 (id, 席) 算一次」沒說範圍,真帳的 id 大量跨輪重用

severity: major
blocking: 是
判準:統計口徑不清楚,按字面做成全窗口去重,數字會系統性偏低。

引句:「每個 (id, 席) 算一次,id 在折入清單算有用,在放行清單或重現不到清單算沒用」

真帳顯示發現 id 是每輪重新編的(a1、c1 這類):

- 全帳 a1 出現 239 次、c1 出現 187 次。
- 同一迴圈內有 2921 個 id 在多輪重現(共 14970 個 (loop, id))。

「算一次」若以 `(id, 席)` 為鍵去重(全窗口、或按迴圈),跨輪、跨迴圈同名的 a1 會被併成一條。S8 的預期表剛好每個 id 都不同(c1、a1、a2、c2、c9),完全測不出這點。

建議:寫明去重鍵是 `(載體, id, 席)`,即每筆載體內各算一次。並在 S8 加一列「兩輪都有 a1」的案例。

## Finding 3:席名原樣分組,真帳的席名帶輪次後綴,同一席會被拆成多列

severity: minor
blocking: 否
判準:統計仍如 spec 所述運作,但會稀釋它自己宣稱的目的,也影響 REVISIT 的「每席至少 30 條」門檻。

引句:「席名照帳上原樣(含模型尾碼,例如 `正確性-sonnet` 與 `正確性-opus` 分開列),不合併不同模型」

真帳 code- 迴圈的 auditor 實際有:

- `架構對齊-sonnet` 628 筆
- `架構對齊r2-sonnet` 18 筆
- `架構對齊2-sonnet` 16 筆
- `架構對齊-r2-sonnet` 10 筆
- `正確性r2-sonnet` 15 筆
- `通才2-sonnet` 12 筆

必填生效後,若派工詞沒禁輪次或編號後綴,逐席沒用率會把同一席拆成多列,樣本分散。spec 的〈範圍〉③ 只要求席名等於帳上某筆的 auditor,沒有管命名形狀。

建議:至少在〈實務隱患〉記一句,或在派工詞規定席名不帶輪次。

## Finding 4:「一輪只准一筆載體」被當成寫側事實,其實寫側沒擋

severity: minor
blocking: 否
判準:口徑講錯,但影響限於舊帳或少數重記情境。

引句:「彙整全輪每條發現的去向;一輪只准一筆。」

查證:

- file: `scripts/lumos:37408`:一輪一筆是處置閘讀側才驗,`canary record` 沒有擋。
- file: `scripts/lumos:23035`:注釋明寫「一輪只准一筆是處置閘在驗,這裡取最後一筆」。
- 真帳 code- 迴圈有 11 個 (loop, round) 帶多筆載體。

後果:同輪若真有兩筆帶 `finding_seats` 的載體,統計會雙算。spec 把「一輪一筆」當成「欄位掛在唯一一筆」的理由(〈舊否決比對〉第二點),這個前提寫側不保證。

建議:統計段註明載體重複的處理,或改成「同輪取最後一筆」,與 `scripts/lumos:23035` 一致。

## Finding 5:翻案了 canary-audit d4,卻沒計畫記決策

severity: minor
blocking: 否
判準:筆記治理漏洞,不影響程式行為。

〈舊否決比對〉說使用者裁「這次不同,照做」。canary-audit 的 d4(`decided: 2026-08-08`,`valid: true`)寫著「否決跨期統計/席位信譽」。〈範圍〉⑦ 只列「手冊與筆記同步」,沒有 `lumos decision-add` 去標註 d4 的適用範圍或補一筆新決策。

下一個 session 讀到 d4 仍是 valid,會把這份功能當成違規。

## 其他小點

- 〈做法〉統計的「照它給的」前面那句「`gov --since-days` 給得比 56 小時」疑為「小」的筆誤(應為比 56 小)。
- 首筆帳時間的判法沒寫:
  - 字串比 `ts[:10]`,還是解析成日期。
  - `ts` 缺失或壞掉時怎麼辦。
  - 帳上有 `+00:00` 的列(95/6596),跨日邊界會差一天。
- 我確認過這兩點沒問題:
  - 結局帳與 spec-gate 列已被讀側濾掉(file: `scripts/lumos:22525`),「首筆」判法不會被它們汙染。
  - 席名比對用的 `_lrows` 已按 `round` 篩選,過濾做得到。

最嚴重 severity:major。blocking 共 2 條(Finding 1、2)。
