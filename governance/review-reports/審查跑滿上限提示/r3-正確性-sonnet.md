severity: major

## F1 「findings 全是 0」規則沒排除「全部缺欄」,`all()` 空集合真值陷阱會把「沒人記」誤判成「折 0」
severity: major
blocking: 是(照字面實作會在真實帳本狀態下把「這輪根本沒人記 findings」算成「折 0」,提示可能因此給出「可以停」而不是「判不了」,誤導編排者提早收工)
引句:「各席帳的 `findings` 全是 0 → 算折 0(處置閘判空輪也看這個欄位)」
引句:「有人報了條數卻沒有彙總帳,則應印這輪沒記處置且提示是判不了」

規則只講兩種狀態:「全是 0」與「有人報了條數(非零)」,沒有處理第三種真實會出現的狀態——**整輪所有席位帳列都完全沒帶 `findings` 欄位**(不是 `--findings 0`,是根本沒給 `--findings`;`scripts/lumos:7552` `if findings is not None: rec["findings"] = findings` 證明不給旗標就不寫這個鍵)。

若照字面把「各席帳的 findings 全是 0」實作成「把有值的那些取出來、看是不是都等於 0」(例如 `all(int(r.get("findings")) == 0 for r in round_rows if r.get("findings") is not None)`),當這一輪**每一列都沒帶 findings**,篩出來的可迭代物件是空集合,而 Python 的 `all(空)` 恆真——這一輪就會被誤判成「全是 0 → 算折 0」,即「已記處置的空輪」,而不是應該印的「這輪沒記處置 → 判不了」。

這不是憑空推演:本專案自己的處置閘對「findings 缺欄 vs 明說 0」本來就有專門處理,而且態度相反——`scripts/lumos:7418-7422`、`18353-18360` 的 `_findings_zero`:
```
v = r.get("findings")
if v is None:
    return False       # 沒填 ≠ 明說 0(legacy 帳缺欄不放行,逐筆成輪加固測試釘的)
```
註解原文就是「沒填 ≠ 明說 0」,是刻意 fail-closed 的既有慣例。這份計劃的 S7/做法二卻只用「全是 0」一句話帶過,沒有明確排除「全部缺欄」這個子狀態,也沒有指名要沿用 `_findings_zero` 那種「None 不算 0」的判法——直接照字面寫最容易踩到 `all([])==True` 這個坑,得出跟既有慣例相反的結果。

真實帳本裡「整輪缺 findings 欄」的形狀確實會發生,不是杜撰:`docs/.canary-log.jsonl` 裡 `idioms-self-maint` 的 `r1`/`r2`/`r3`、`rel-layer-guard` 的 `r1`/`r2`/`r3`、迴圈 `L` 的 `r1`,每一輪都恰好只有一筆帳列、且該列完全沒有 `findings` 鍵(這些迴圈早於 2026-08-26 cutoff,所以目前不會被印,但它證明「一輪帳列集體缺 findings 欄」是這個帳本結構會產生的真實狀態,而 `--findings` 至今仍是選填旗標,2026-08-26 之後開的新迴圈一樣可能重現這個形狀,尤其在編排者還沒把處置帳補齊、只有幾席先留痕的中途狀態)。

## F2 「代碼審循序單審不印」若沿用鄰近既有的 loop_id 前綴判法,會連帶吃掉真正的多席代碼審 panel
severity: major
blocking: 是(照字面沿用鄰近既有的 `startswith("code")` 判法,會讓本該印的多席代碼審 panel 迴圈整段不印,漏掉合約 S9 只排除「循序單審」的範圍)
引句:「代碼審循序單審(沒有輪次記帳)」
引句:「若迴圈是 light 分級、代碼審循序單審,或 2026-08-26 以前開的」

計劃 PRIOR-ART/機制層沿用那段明講「機制層沿用……定錨分級 `_loop_anchor_tier`……舊閘退役判定 `_panel_retired_for`……」,而 S9 要在處置閘（`_loop_status_disposal`）判斷「是不是代碼審循序單審」時排除印出。但處置閘裡緊鄰、同語意脈絡的既有寫法就是純前綴判斷,不看有沒有輪次:

```
scripts/lumos:18541  if not readonly and not str(loop_id).startswith("code"):
```
這一行同時擋掉了 intake 觀測段跟緊接著的「審查有沒有用」段(`scripts/lumos:18550` `_review_yield_round(latest)`)——後者正是這份計劃打算直接呼叫、卻要求「不靠處置閘印出的那段」的同一個函式呼叫。既然計劃自己都承認要繞開這段是因為它「對 code 迴圈是跳過的」,就表示作者已經知道這個既有前綴判法會漏掉東西,但 S9 的排除條件本身卻只寫「代碼審循序單審(沒有輪次記帳)」一句話,沒有明講要用哪個判準去偵測——沒有明寫「要用 `_roster_kind(loop_id)=="code" and not panel_fmt`,不能只用 `loop_id.startswith("code")`」。

真正精準的判準已經在 `cmd_loop_next` 裡現成算好:
```
scripts/lumos:10402  seq = (eff_tier == "standard" and _roster_kind(loop_id) == "code" and not panel_fmt)
```
需要同時看 `_roster_kind(loop_id)=="code"`**和** `not panel_fmt`(有沒有輪次記帳)兩個條件;單看 `loop_id.startswith("code")`(`_roster_kind` 本身在 `scripts/lumos:9885` 就是靠這個前綴判"code")完全分不出「循序單審」跟「多席代碼審 panel」,因為兩者的 loop_id 都用 `code-` 開頭。

真實帳本可以直接證明這個混淆會發生:`docs/.canary-log.jsonl` 裡的迴圈 `code-記憶索引大小守衛`(在計劃自己引用的 r1-intake.md 裡被拿來當範例)是多席 panel 型,`r1`~`r4` 每輪都有 2–3 筆不同席位(`架構對齊-sonnet`、`通才-sonnet`)共用同一個 round-id,`panel_fmt` 明顯為真——但它的 loop_id 就是 `code-` 開頭。若實作直接照鄰近既有寫法只用 `loop_id.startswith("code")` 當 S9 的排除判準,這種真實存在、本該印(它是多席、有輪次記帳的迴圈,不是「循序單審」)的迴圈會被整段消音,漏掉 S9 只想排除「沒有輪次記帳」那個子集的合約意圖。

已看,無:
- 併發:計劃只讀帳,cap-hint 段本身不寫任何檔;跟 processed 閘既有的讀帳/壞行擋法路徑相同,沒有新的競態面。
- 金流 / 對外送出 / 不可逆:計劃本身已排除,程式碼走查沒發現額外接觸金流、外呼或不可逆動作的路徑,同意。
- 守衛面:`rounds_count >= cap`(`scripts/lumos:10676`)與既有 cap-reached 判定共用同一個比較式,cap-hint 只是在其後(或其他 phase 的 `emit`)追加輸出,沒有改動 `rc`/`phase` 本身的計算路徑,不影響既有退出碼與過關判定,認同「不改任何判定」的宣稱。
- 效能:`_review_yield_round` 是純函式、只掃單一 loop 已載入的帳列,逐輪呼叫一次的量級跟現有「審查有沒有用」段一致,沒有另開讀帳路徑,認同。
- 其餘章節(適用範圍、S1–S6、S8、S10–S11、回退、誠實界線、審計修正紀錄)逐條核對:交叉引用(`_TIER_PARAMS`、`_loop_anchor_tier`、`_panel_retired_for`、`_review_yield_round`)都在 `scripts/lumos` 裡存在且簽名相符;S1–S6、S8、S10–S11 的敘述跟程式碼現況(`rounds_count`/`cap`/`emit`/`--json` 輸出組裝方式)沒有發現額外矛盾。

最嚴重 severity: major;blocking 共 2 條。
