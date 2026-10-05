severity: major

## Findings

ID: DESIGN-COST-1  
severity: major  
blocking: 是  
標題：批次只有單檔上限，整批仍可能在保守退路生效前耗盡記憶體

引句:「單一物件缺失／超限、路徑特殊字元使首行不可安全批次讀取；這些狀態不當作排除證據，保守保留。」

觀察：`_impact_diff_modes` 會把所有需要判斷首行的物件加入同一批，沒有物件數或累計位元組上限。底層先逐一檢查單檔大小，但之後仍把所有未超過 1 MiB 的物件一次交給 `git cat-file --batch`，並以 `capture_output=True` 將完整輸出收進記憶體後才解析。

佐證：

- file: `scripts/lumos:41050`：建立無總量上限的 `ask`。
- file: `scripts/lumos:41058`：整批送入 `_nodehome_cat_blobs_capped`。
- file: `scripts/lumos:27103`：只檢查各物件是否低於單檔上限。
- file: `scripts/lumos:27106`：所有合格物件均進入同一讀取批次。
- file: `scripts/lumos:27128`：`capture_output=True` 會先累積完整批次輸出。
- file: `scripts/test_lumos.py:23092`：現有控制組只有少量固定檔案，沒有覆蓋批次總量邊界。

具體錯行為：若差異含大量各自小於 1 MiB 的無副檔名簿記檔，父程序可能先累積數百 MiB 乃至數 GiB 的 Git 輸出，遭記憶體壓力或終止。此時不會走設計所述「讀取失敗後保守保留」；整個 impact／角色鏡頭可能直接失敗，混合差異中的真正程式、家與事故也無法產出。逾時只限制等待時間，不是記憶體上限。

判準：加入累計物件數或累計宣告大小超限案例，證明入口會在啟動內容批次前停止擴張；未讀項目須以未知處理並保守保留，同時仍能完成整體結果。具體上限及分批方式可由作者選擇，不要求另建分類機制。

## 逐節核對

- 「目的／PRIOR-ART」：無 finding。沿用既有簿記分類，且沒有用 gitignore 取代已追蹤檔案的輸入分類。
- 「最小改法／S1」：除 DESIGN-COST-1 外，已確認已刪檔取舊模式、staged 取索引模式、未知狀態保守保留；程式副檔名與可執行檔會優先保留。
- 「證據與範圍」：無 finding。文件明確承認這是實作後補審、高風險放行已失效，也沒有重編或重設代碼審輪次。
- 「實務隱患」：無額外 finding。共享 raw parser 確實觸及守衛面，文件沒有以「閘判準未改」掩蓋風險。
- 「回退」：無 finding。回退會恢復已知誤觸，因此明確標成不當通過版本；控制測試名稱存在。
- 「終審揭露的分類例外」：無 finding。程式副檔名、可執行文字副檔名、無副檔名腳本與刪檔控制均有對應源碼分支及測試。
- 「第二輪完整例外核對」：無 finding。`_codeloop_raw_changes` 提供四欄，`_codeloop_raw_modes` 仍只投影原有模式對，舊消費者介面未被擴張。
- 「修復驗證的時間前提」：無 finding。`budget <= 0` 在任何設定或 Git 讀取前直接返回，探針也檢查 `_lens_git` 與選檔均未被呼叫。正預算路徑並非完整期限保證，但凍結副本最後一句已明確承認「不冒稱已收緊所有正預算 Git 查詢」，因此沒有把局部修復冒稱完整保證。
- 活計劃與凍結副本：逐位元組相同。
- 指定六個函式：均存在；呼叫關係及回傳語意已開碼核對。

## 實際設計鏡頭逐條判定

- `Systems/retrieval-ranking`：受影響。它承接 impact 種子分類；分類正確性大致維持，但 DESIGN-COST-1 的批次總成本缺口會使其在大量輸入下無法產出結果。
- `Systems/測試假綠形態`：不破壞既有合約。現有唯一合約是修 bug 翻紅釘須帶現場前置斷言；本次測試有真入口控制，但尚未覆蓋批次累計資源邊界。
- `Systems/pitfalls-code-loop`：受影響但相容。共享 raw parser 對舊消費者仍投影模式對；零預算提前返回成立。正預算 Git 查詢仍可能超過名義預算，文件已如實限縮宣稱，故不另列 finding。

## 已讀材料

完整閱讀：

- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`

核對源碼、測試與相關圖譜：

- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`

未讀取其他輪審查報告或結果。唯讀 sandbox 下未建立臨時 Git 實驗，因此沒有把未執行的壓力量測算成通過證據。

最嚴重 severity：major  
blocking 總數：1