severity: major

## I1 上線會讓既有釘值測試紅,計劃沒列要改哪幾支、也沒交代怎麼改
severity: major
blocking: 是(實作時 `t_choice_points_batch2_stable` 與 `t_choice_points_batch3_stable` 必紅,計劃的驗收與落點都沒涵蓋)
引句:「只有同一級類別的行,打亂的清單跟改之前逐項相同(同一份清單、同一個種子),挑到同一個壞法。」
1. 我在 `/tmp` 的複本(已刪)照〈做法〉實作三級挑法,再跑既有測試。結果是 `t_choice_points_batch2_stable` 與 `t_choice_points_batch3_stable` 紅,`-k choice_points_stable` 和 `-k choice_samples` 綠。
2. 這兩支測試分別釘 `_CB2_S7_PIN`、`_CB3_S7_PIN`,各 82 行。釘的是「只含第一版語法的樣本行」加入新類別前後挑法不變。
3. 樣本 `choice.kt` 57 到 69 行與 `chain.kt` 9 行同時有 API 與 ROR、SBR、NUL。例如 58 行原釘 `C-1 false`,新順序挑出 `C-20 filter`;60 行原釘 `C-1 $A < $B`,新順序挑出 `C-22 any`。
4. 計劃只新增 S1 到 S7,〈做法〉與〈實務隱患〉都沒說這兩個既有釘值要重釘。〈做法〉只說「同級照舊」。
5. 第四批的 S7 照第三批只釘第一版樣本,同樣被牽連。
6. 計劃要改的 `scripts/test_lumos.py` 帶錨點簽章。這幾筆釘值是簽章內容,實作者不知道要改。
7. 這份計劃改的正是「混級行的挑法」,重釘本身合理。缺的是計劃裡一個條款加一句交代,例如 S8:重釘 82 行並說明改了哪幾行、為什麼。

file: `scripts/test_lumos.py:148731`(`_CB2_S7_PIN`)、`scripts/test_lumos.py:149129`(`_CB3_S7_PIN`)、`configs/ast-grep/kotlin-choice/samples/choice.kt:57`

## I2 〈白話〉說存活行會用新順序,但存活行的帳(判讀、reach、覆蓋指紋)綁壞法身分,挑法一換就作廢;消費專案第一次推送會發生什麼沒寫
severity: major
blocking: 是(會讓既有存活行的人工判讀白費、推送閘要求重新處置;計劃的量測 S7 又只在空帳本上做,量不到這件事)
引句:「新行與存活、跑不出結果要重跑的行才用新順序。」
1. 〈白話〉的有效處置只講 killed 與放行,把存活行說成「才用新順序」。實際上存活行分三種狀況,計劃沒分。
2. 依覆蓋判的存活(`via == cov`):`cov_sha` 的雜湊含 `new_sha`,挑法一換就對不上,一律重跑。
   - file: `scripts/lumos:80050` 到 `scripts/lumos:80075`、`scripts/lumos:80441`
3. 依 `tests_sha` 判的存活:測試沒變就不重跑,帳上留舊壞法的存活,但畫面印的是新壞法,兩邊不一致。
4. 判讀(layer)事件:`_choice_layer_state` 在 `ev["new_sha"] != new_sha` 時回 None,即判讀作廢。所以挑到別的壞法的存活行,既有判讀全部失效。
   - file: `scripts/lumos:81259` 到 `scripts/lumos:81265`
5. 後果:實驗專案上線後第一次推送,既有存活行中混級行會被改挑。這些行的 reach、判讀作廢,要重跑或重判,要付一次 choice-kill 的時間。
6. 計劃唯一的量測 S7 在「空帳本複本」上做,量得到改挑行數,量不到「帳上現有存活行有幾行被作廢」,也沒寫上線後第一次推送的處置步驟。〈回退〉說「帳不用動」只對 killed 與放行成立,對存活與判讀不成立。
7. 〈實務隱患〉第一條只講「舊放行會蓋住新順序」,漏了這條反方向的牽連。

## I3 〈落點〉漏列同樣寫了「類別用行指紋洗牌」的現有文字,三個月後會跟程式對不上
severity: minor
blocking: 否(文件落差,不影響行為)
引句:「改寫行指紋那條 WHY 的「挑壞法的種子也用它;論文整次呼叫洗一次類別」,補「各級各自洗、依級串接」。」
1. 〈落點〉要改的那句確實在 `Systems/規格閘.md:68`,說法對得上。
2. 同檔 `Systems/規格閘.md:67` 的 choice-points WHY 也寫「每行最多一個壞法照論文 4.1 Listing 2 的迴圈(類別用行指紋當種子洗牌、取第一個產得出的)」,沒列入落點,改完會變成過時的說法。
3. `Projects/改動選擇點都要有需求守住_計劃.md:95` 〈用詞〉的「①把那一行有選擇點的類別用『行指紋』當種子打亂」確實存在,〈落點〉列了。
4. `Projects/選擇點表第二批常見誤用寫法_計劃.md:111` 的「類別變多後洗牌結果可能挑到別的壞法…只含第一版語法的行挑法不變(S7)」,在新挑法下兩半都不成立:混級行挑法會變,而這正是 I1 的釘值。計劃沒列它,也沒說它是歷史描述、不用改。
5. 第四批計劃 `選擇點表第四批常用語法_計劃.md:91` 已補「`CHOICE_TIERS` 同時加 `"RET": 2`」,與本計劃一致。
6. 型錄〈選擇點表〉說明段存在(`skills/kotlin-idioms/checks-catalog.md:1668` 附近有已撤列號行),補一句沒有衝突。

## I4 PRIOR-ART 與〈依據來源〉的「11%」在論文原文找不到,且「代碼審 r1 核對了」的說法不實
severity: minor
blocking: 否(論文數字只是佐證,不影響設計與驗收)
引句:「用回饋做的抑制規則讓沒用的壞法從 85% 降到 11% https://arxiv.org/pdf/2102.11378 (代碼審 r1 整合席取回原文核對了 4.1、Listing 2 與 85%、11% 兩個數字)」
1. 我下載 arXiv 2102.11378 v2 的 PDF,用 `pdftotext` 全文搜尋。出現的是「developers at Google initially classified 85% of reported mutants as unproductive」,而且是在抽樣之後,屬 Introduction。
2. 全文沒有「11%」。與 11% 相近的是 3.2.5:早期三個抑制啟發式(logging、時間類、設定旗標)讓生產力「from about 15% to 80%」,後續啟發式再把它推到 89%。11% 是讀者自己從 100% 減 89% 算出來的,論文沒寫,也不是只靠「開發者回饋做的抑制規則」。
3. Listing 2 在 4.1 Random Selection 屬實,且寫明整次呼叫洗一次 `{UOI, ROR, SBR, LCR, AOR}`。Listing 3 在 4.2 Targeted Selection,不在 4.1。
   - WHY 與〈依據來源〉把 Listing 3 與「同篇」並列,沒寫錯節。
   - PRIOR-ART 寫「4.1、Listing 2 與 85%、11%」,沒把 Listing 3 說成 4.1。
4. 結論:「85%」屬實,「11%」該改寫成「生產力提升到 89%(即沒用的剩 11%,為換算值)」,並把「核對了兩個數字」那句改成實情。

## I5 〈白話〉的「toInt↔toLong 這類轉型」跟型錄實際的轉型列不符
severity: minor
blocking: 否(只是舉例用語不準)
引句:「toInt↔toLong 這類轉型、拿掉 retry 這類呼叫等」
1. 型錄 C-43 到 C-45 是 `toIntOrNull→toInt`、`toLongOrNull→toLong`、`toDoubleOrNull→toDouble`(失敗時從回 null 變丟例外),不是 Int 與 Long 互換。
2. 〈白話〉表的 API 列數 35、NUL 2、SBR 1、AOR 5、ROR 8、LCR 2、UOI 2 我用腳本逐列數過,與型錄全部吻合。S7 點名的列號 C-19、C-27、C-31、C-37、C-43 到 C-45、C-54、C-55 全是 API 類,吻合。
3. 〈做法〉裡 `CHOICE_CATEGORIES` 的位置與「`choice_tables` 交出的表多一個鍵」都對得上現況。`scripts/lumos` 只有 `_choice_file_points` 一處呼叫 `_choice_pick`,partial 傳 `tiers` 的改法完整。
   - file: `scripts/lumos:79494`、`configs/ast-grep/kotlin-android/check.py:1393`、`configs/ast-grep/kotlin-android/check.py:1491`

## 已讀,無 finding 的節
- 〈不做〉:與〈白話〉、〈做法〉一致。
- 〈回退〉:改回洗牌與拿掉 `CHOICE_TIERS` 的步驟可行,但「帳不用動」只涵蓋 killed 與放行,見 I2。
- 〈驗收條款〉S1 到 S6 及〈預期值表〉:句式與對應關係自洽,但沒涵蓋 I1 的既有釘值。
- 風險類:效能、記憶體與巢狀深度只多一個 3 組分組的洗牌,不構成問題。有效處置引用的 WHY 原文「型錄改了、挑到的壞法換了,同一行的需求證據不該作廢」在 `Systems/規格閘.md:72` 逐字吻合,killed 與放行行不重跑的宣稱成立。

總結:最嚴重 severity 為 major,blocking 共 2 條(I1、I2);minor 3 條(I3、I4、I5)。
