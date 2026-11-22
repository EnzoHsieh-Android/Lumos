severity: minor

固定席說明:這次沒有附固定席節點,不必逐條答。我自己對照了這份 diff 動到的兩篇 Systems 節點(Systems/kotlin規則包、Systems/規格閘)和母計劃。判定都是「不影響」:這份 diff 只補文字,沒有改它們宣稱的行為或合約。

我在 `/Users/enzo/harness/lumos-choice-batch3` 實跑了下列測試,都綠:
- `-k batch3`:80 passed。
- `-k choice_scope_rule_output`:5 passed。
- `-k choice_samples_batch`:64 passed。
- `-k batch2_stable`:4 passed。
- `-k kt_catalog_api_decision`:38 passed。
- `check.py --catalog-only`:型錄問題 0 個。
- Verification 的 `lumos lint`:0 問題。

另外確認:
- 18 列的列號順序與計劃範圍 1 的順序一致。
- 型錄的「對應決策表」欄、規則、樣本標記對得上計劃。
- 計劃要求的測試名稱都存在。
- Verification 的 `valid_under` 指到 `1f2ae2d09`。該提交到審查頂端 `763081c0d` 之間只改了 3 個文件檔,沒動規則。

以下全是文件與現況對不上的 minor,沒有 major 或 blocker。

## i1 RETIRE-IF 與 Verification 對「上線日」互相推給對方
severity: minor
blocking: 否

引句:「上線日(寫進第三批的 Verification)起滿兩個月」
引句:「上線日以推上主線那天為準,寫進計劃的 REVISIT。」
引句:「REVISIT:2027-02-28 第三批上線滿兩個月前後(上線當天照範圍 6 把這個日期改成上線日加兩個月」

- 失敗場景:三個月後的人照 RETIRE-IF 去 Verification 找上線日,找不到。那篇只說「寫進計劃的 REVISIT」,而 REVISIT 要靠「上線當天手改」才會正確。
- 沒人手改的話,殘留的 `2027-02-28` 對應的上線日是 2026-12-28,不是實際推送日。以今天 2026-11-22 推送算,正確日期應該是 2027-01-22。
- 找上線日的路徑繞成一圈,又沒有機械檢查提醒人去改這個日期。
- 範圍 6 還寫「RETIRE-IF、REVISIT、〈回退〉要抄的數字都寫在這一篇」,但 Verification 裡沒有〈回退〉要抄的數字。

## i2 預期值表 S9 與實務隱患的輸出量數字跟現行規則實測對不上
severity: minor
blocking: 否

引句:「作用域規則輸出 ≤1MB(同一條 has 規則正面寫約 1.16MB)」
引句:「巢狀 500 層 72MB → 0.24MB、巢狀 100 層 3.1MB → 48KB」
引句:「作用域規則巢狀 100 層正寫 46MB、雙重否定 77KB」

file: `scripts/test_lumos.py:147017`(`t_choice_scope_rule_output`)

- 失敗場景:我實跑 S9。
  - 平鋪 300 個 `launch`:雙重否定寫法 544 位元組,拿掉雙重否定的正面寫法只有 60,435 位元組,不是 1.16MB。
  - 巢狀 100 層:76,548 位元組對 45,912,340 位元組。
- 同一份 diff 裡,PITFALL 的 46MB、77KB 是對的,計劃裡的 3.1MB、48KB 和 1.16MB 是設計稿那版規則的舊數字。
- 照預期值表 S9 第一列,有人拿掉雙重否定想看平鋪測資變紅,實際不會紅(60KB 小於 1MB)。真正會紅的只有巢狀那一列。
- 這不影響 S9 整體的偵測力,但表裡的證據欄寫錯了。

## i3 計劃仍寫「候選」與「暫定列號、實測後才定號」,Verification 已定案
severity: minor
blocking: 否

引句:「18 列暫定 C-38 到 C-55,範圍 7 實測後才定號。」
引句:「第三批(候選,設計審定案;每一列上線前還要過範圍 7 的實測門檻):」
引句:「18 列全部上線、列號照計劃範圍 1 的順序給 C-38 到 C-55」

- 失敗場景:後人讀計劃,會以為範圍 7 還沒量、列號還沒定。
- 其實同一份 diff 的 Verification 已寫三個門檻全過、18 列定號。
- 計劃沒有回寫「範圍 7 已過」,兩份在同一次提交裡互相矛盾。

## i4 PITFALL 承認第二批測試有同一個漏洞卻沒有回頭條件
severity: minor
blocking: 否

引句:「同族:t_choice_samples_batch2 的 _cb2_s6_filter 同樣沒收,這次沒改」

file: `scripts/test_lumos.py:146519`(`_cb2_s6_filter`,條件只收 `choice-batch2.kt` 與 C-32 到 C-37)

- 失敗場景:我對照 `_cb2_s6_filter`,條件確實不收列號是 `<choice-samples>` 的問題。
- 規則檔壞到 ast-grep 整批跑不起來時,`t_choice_samples_batch2` 會靜默綠。
- 母計劃寫明「承認風險要附回頭看的條件」。這句只有「這次沒改」,沒有 `REVISIT:` 或 `[when-file:]` 回頭條件。
- 計劃那一行〈實作時〉⑤也只說「記成 PITFALL」。
- 沒人會回頭補第二批這個洞。

## i5 S7 釘值其實是第二批常數的別名,不是計劃說的獨立常數
severity: minor
blocking: 否

引句:「加入前的結果在實作第一步先跑一次、釘成測試裡的常數」
引句:「第二批撤列時才不會讓第三批的測試紅」

file: `scripts/test_lumos.py:146960`(`_CB3_S7_PIN = tuple(_CB2_S7_PIN)`)

- 失敗場景:程式上方註解寫「另抄一份……這份照第三批加入前的結果釘死」,但它是載入時從 `_CB2_S7_PIN` 取的別名。
- 日後調整第二批釘值,第三批的 S7 會自動跟著變,偵測不到「第三批加入前後挑法不同」。
- 目前兩份值逐筆相同,沒有紅,所以只是計劃宣稱的獨立性與程式不符。

總結:最高嚴重度 minor,blocking 共 0 條
