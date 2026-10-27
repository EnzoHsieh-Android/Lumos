severity: minor

## F1 新說明的「沒被任何情境列到」會讓人誤以為被情境用到的畫面,它的基準圖不用整套
severity: minor
blocking: 否
引句:「驗收素材不列,但改到沒被任何情境列到的素材(例如重錄的基準圖、門檻檔),推送前判定照樣要求整套跑」
歸因：有證據的修復回歸

1. 輸入:只改 `.maestro/` 底下一張基準圖,該圖對應的畫面名已被某情境的 `visual` 列到。
2. 走法:`_e2e_gate_need` 先用 `_e2e_scope_hit` 把這張圖算進範圍(`E2E_MATERIAL_DIRS = (".maestro",)`)。接著 `_e2e_gate_owners` 呼叫 `_e2e_file_owner`,再呼叫 `_e2e_owners`。`_e2e_owners` 只認兩條路:功能的 `paths` 包住它,或某情境的 `flows` 列了這個檔。
3. 結果:`visual` 裡的是畫面名,不是檔案,所以基準圖永遠對不到歸屬,一律回 `none`,判成「對不到任何功能」,推送前要求整套。
4. 壞在哪:新說明用「沒被任何情境列到」當條件,讀的人會以為畫面已被情境用到的基準圖屬於「被列到」、不在此限。實際上除非那個檔被 flows 列到,或剛好在某功能 `paths` 底下,`.maestro/` 底下的檔(基準圖、`config.yaml`、共用 flow、toolkit 腳本)改到都要整套。
5. 說明講對的部分:被 flows 列到的流程檔屬「不在此限」,門檻檔屬「要整套」,這兩個我讀程式核對過,講得對。
6. 限制:我沒有實際跑 `check`,只讀 `_e2e_scope_hit`、`_e2e_file_owner`、`_e2e_owners`、`_e2e_owner_index` 的程式。

## F2 技能文件那句仍把「改到的檔都歸屬」當成推送前不會被要求整套的判準
severity: minor
blocking: 否
引句:「看這次改到的檔是不是都歸屬到功能(沒歸屬的,推送時會被要求整套跑)」
歸因：有證據的原有漏查

file: `skills/lumos-android-evidence/SKILL.md:52`

1. 輸入:只改基準圖或門檻檔。`coverage --changed` 列 0 支沒歸屬,但推送前判定要整套(計劃的 r2 例子自己也這麼寫)。
2. 壞在哪:這句沒有說「只看程式檔」。整句只提到基準圖只准人錄,沒講它改到時會讓推送要求整套。
3. 這是前輪沒涵蓋的相鄰說明,這次修補沒動它,所以屬原有漏查。照做的後果是被推送前檢查擋下後補跑,不會做出破壞性的錯誤操作,故列 minor。

## 修補三問

**①原問題修好了沒?** 大致修好。
- 原問題是說明宣稱「沒歸屬+共用程式」等於推送前要整套的全集。
- 新說明在三處講明限於「程式檔」並另述素材:`_e2e_coverage_report` 的說明字串、計劃的第 1 項、計劃的 `--changed` 一行。
- 證據一:`_e2e_coverage_report` 在 `if app is None or not inside` 之外另有 `_e2e_scope_hit`,而它把 `.maestro/` 與門檻檔判成在範圍內,所以這些素材會進報告的迴圈。
- 證據二:報告迴圈內 `app is None` 時 `continue`。素材路徑不在 `app_dirs` 底下,所以 `app` 為 `None`,被略過,報告確實不列素材。
- 證據三:`_e2e_gate_need` 不做這個篩選,素材進 `_e2e_gate_owners`,對不到歸屬就要整套。
- 「被列到的不在此限」限於 flows 列到的流程檔,這一點成立;見 F1 對措辭的保留。

**②相鄰說明有沒有矛盾?**
- README 中英版:只說列出程式檔、另印共用程式幾支,沒有宣稱是推送判定的全集,不矛盾。
- 系統筆記 `Systems/android-e2e-acceptance.md:73`:只說沒歸屬的程式檔與共用程式,不矛盾。
- 技能文件 `skills/lumos-android-evidence/SKILL.md:52`:見 F2,語意上不完整,但不算直接矛盾。
- 文字版輸出「沒歸屬的程式檔…(改到它們時,推送前檢查會要求整套跑)」已限定程式檔。

**③修前修後的結果:** 新發現是 F1、F2。F1 是新措辭引入的歧義,修前說明沒提素材,所以修前沒有這條。F2 修前、修後都有。

## 固定席逐條答
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`(RISK):這輪只改了一段說明字串和計劃筆記,沒有改動風險路徑,判不影響。
- `lumos-cli-read`(search 預設排除 superseded):未動 search,判不影響。
- `guard-kill`(rc 優先序、`--json` 輸出):未動,判不影響。
- `測試假綠形態`、`lumos-cli-lifecycle`(re-inject)、`design-loop`(處置閘):這輪修補沒有改行為,只改說明,判不影響。
- 超出上限只列名的節點:未逐條核對,判不影響(本輪只改說明字串)。

總結:本報告最高等級為 minor
