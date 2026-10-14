severity: minor

固定席節點:派工詞尾端沒有收到 hook 附的固定席節點,所以沒有逐條判的對象。要判的話請補貼。

我重算了帳本、抽樣了卷證。四個問題的結論:數字大致對,但分母要說清楚;d2 的解讀大方向對、字面過頭;判準寫法有一塊太窄;對收斂的預期效果沒有證據,計劃自己也沒量。沒有 blocker 或 major。

## ① 數字重算與分母

重算方法:從 `docs/.canary-log.jsonl` 取 `loop` 以 `code-` 開頭、恰一筆載體、載體有 `finding_severities`、同輪任一席 severity 是 major 或 blocker 的輪。

- 我算出 78 輪、176 條 minor、174 條折入、2 條放行。176 與 174 跟計劃一致,輪數是 78 不是 77(差一輪)。排除 blocker 輪後是 70 輪(只含 major 的是 55 輪)。
- 那 2 條放行是 `code-規格閘半套` r1 的 X4、X7,日期 2026-09-17。

severity: minor
blocking: 否
引句:「176 條 minor 有 174 條被折入」
說明如下:
- 這個比例是閘本身造成的:閘禁止放行,所以折入率幾乎必為 100%,它量的是規則,不是編排者的偏好。
- 78 輪裡有 23 輪含 blocker 席,共 29 條 minor。計劃明寫 blocker 規則不動,這 29 條改了也放行不了。
- 真正受益的是 55 輪、147 條 minor。
- 全部 461 個有 major 的代碼審輪裡,只有 78 輪(17%)的載體帶 `finding_severities`。`--finding-severity` 維持選填,所以另外 83% 的輪不會有任何改變,除非編排者開始標。
- 建議計劃改寫成「分母 78 輪,其中 55 輪可受益」,並說明 174/176 是規則的結果。

severity: minor
blocking: 否
引句:「卷證裡有「為了折一條 minor 新加了通道、下一輪因為新通道缺測試被判 major」的完整鏈條」
說明:引句內有「」,是我取了整句的一部分,鏈條本身屬實。
- 查證:r2 架構對齊席的 A1 是 minor,內容是改成印 MSG 行。r2 折入了它,新增了 MSG 通道。
- r3 的 K1 因此被判 major:「否」判定不印 MSG 沒有測試,改壞會變成每週都發 LINE。
- 但 `code-週評通知` 四輪的 `finding_severities` 全是空的,不在 78 輪的母體裡。
- 它是單一個案,不能當成「普遍」。

severity: minor
blocking: 否
引句:「有兩份凍結判定 `code-待決問題改存開頭欄位` r9、`code-審查跑滿回顧` r4 放行過」
說明:
- 凍結判定裡「major 輪加非空 accepted」其實有 4 個迴圈:另外兩個是 `code-純文件子集` r3 和 `code-prose-conv-impl` r1,這兩個的判定是 rc 0。
- 這 4 個載體都沒帶 `finding_severities`,所以「走照舊分支、判定不變」的結論成立,數字寫「兩份」不準。
- `code-規格閘半套` r1 就有「major 輪、帶逐條嚴重度、放行 minor」的反例,所以「舊帳都沒這樣做」這句話字面為假。
- 它的凍結判定在 r3,r3 判過 rc 0,所以不影響回放。
- 建議改寫成可驗證的說法:凍結判定所在輪的載體都沒帶 `finding_severities`。

## ② d2 與 panel 判準的解讀

severity: minor
blocking: 否 ⚠
引句:「major 修掉、minor 可以留著,現行規則比它更嚴」
說明:
- panel 的實作是 `_panel_round_conjuncts`。它的「存活 ≤minor」讀的是各席記的 severity,意思是這一輪不能還有 major,不是「修掉 major 之後 minor 可留」。
- panel 沒有 folded/accepted 這種處置帳,從來沒要求把 minor 折入。所以「panel 沒有強制折 minor」成立,方向對。
- 但「存活最高 ≤minor 代表 minor 可以留著」是推論,不是原文。
- d2 原文是「輪內任一席 ≥major 則 accepted 必空(major 一律折)」,動機是外家席指出 major 可附理由放行,是在補 major 的洞。「與 panel 同嚴度」是類比,不是條文。
- 計劃要推翻的是 d2 的字面。使用者 2026-10-14 的裁定有權這麼做,但計劃只在內文寫了 WHY,沒有走 decision-add 去記 d2 被部分取代。
- `probe輪退場_計劃` 的 KEY 行 d2 和 `scripts/lumos` 裡寫著 d2 的擋下訊息,都會變成過期描述。
- 建議:把「代表」改成「與之不衝突」,並補一筆翻案或取代 d2 的 decision。

## ③ 三類判準套到真實 major

我從 `governance/review-reports/code-*` 取得 1418 條 major,依字串分類:

| 類別 | 條數 | 備註 |
|---|---|---|
| 測試假綠類 | 182 | 約占全部 major 的 13% |
| 其中提到合約、驗收或 S 條款 | 122 | |
| 其中沒提到 | 60 | 最多這些會被判 minor,約占全部 major 的 4% |
| 架構對齊席的 major | 222 | 計劃不動 |
| 非架構席的第二種寫法 | 約 8 | |

「提到」不等於「綁定」,所以 60 是被改判的上界,實際會再少一些。

我手抽 12 條測試類:
- 維持 major:推送與CI提速 r2 的 S3、殺傷力配方失配提醒 r5 的 S5(100755 突變)、probe-postreview 的 S11。這三條都有 S 條款綁定。
- 該維持卻可能被改判:`code-test-quality-r4-repair` r3。
  - 測試名稱宣稱「worker 被停掉」,但把 `terminate_group` 換成 `break` 後 worker 洩漏、測試仍綠。
  - 這是修補本身的核心主張,不是「一般完整度」。
- 可改判 minor:`code-codex-s0` r1 的恆真斷言,審查員自己標了 blocking 否。
- 待確認:`code-batch3` r1-s3 的唯讀守衛、`code-batch2` r2-delta。拔掉守衛 15 條仍綠,若屬守衛類應維持。

文件類:
- `code-筆記格子第3步` 的過期註解,審查員並列了「條款字面與測試相反」的證據,屬於跟合約衝突,維持 major。
- `code-審查收斂規則` 手冊跟工具順序走不通,照文件做會出錯,維持 major。
- `code-否決提案收齊查重` 的指令數 84 寫成 85 會讓 `t_docs_command_count` 紅,不屬於計劃列的三類。照字面會被判成「歷史數字」的 minor,但它會擋推送,實害小。

severity: minor
blocking: 否 ⚠
引句:「受影響的是合約行(★INVARIANT★ 等)或計劃驗收條款綁的測試、而且能舉出一個合理的改壞照綠 → major」
說明:
- 「能舉出改壞照綠」在這批樣本裡全部成立(審查員本來就要附重現),所以實際只剩「綁定」一個判準。
- 計劃沒說「綁」是指 `[test:]` 綁定,還是只要在條款裡被提到。
- 守衛類(程序清理、唯讀守衛)的測試沒有條款綁定,但失效會直接破壞功能,這類應明列為 major。
- 建議補一條:測試是修補核心主張或安全、唯讀、清理類守衛的唯一驗證時,維持 major。

## ⑤ 防放水檢查的實際強度

severity: minor
blocking: 否
引句:「放行 minor 必須標逐條嚴重度,且記帳時數量檢查擋住把 major 標成 minor」
說明:
- 我在 55 輪(只含 major、無 blocker)上重算「報告裡 minor 加 clean 的宣告數」,分布是:0 條 12 輪、1 條 13 輪、2 條 13 輪、3 條 2 輪、4 條 2 輪、5 條以上 13 輪。
- 只有 0 條的 12 輪會被這個檢查完全擋住。其餘 43 輪都留有空間,把一個 major 標成 minor 後放行仍然過關。
- 檢查擋得住的是「標的數量超過報告宣稱」,擋不住「對應錯」。計劃內文自己也承認這點,但「實務隱患」那段寫成「擋住把 major 標成 minor」,說過頭了。
- 同一段還說「記帳時」,與「做法」段「放在處置閘而不在記帳時」自相矛盾。
- 好消息:78 輪中只有 1 輪(`code-小改動閘` r2)的標記 minor 數多於報告宣告的 minor 數,誤擋風險低。
- 建議改成「只防數量灌水,對應正確靠收貨審查」,並把「記帳時」改成「處置閘」。

## ④ 對收斂的預期效果

severity: minor
blocking: 否 ⚠
引句:「帳本顯示這讓 minor 大量進入修補」
說明:
- 「大量進入」屬實,但 minor 修補導致下一輪出現 major,證據只有 `code-週評通知` 那一個個案。
- 計劃引用的 `Verification/2026-10-14_修補大小與下一輪major回放` 的 REVISIT 自己寫「推測它讓修補變大,今天沒量」。
- 我在 78 輪母體裡,把非最後一輪(共 60 輪)依載體內 minor 與 major 的多寡分兩組,看下一輪是否仍有 major:
  - minor 較多的輪:11 輪,下一輪有 major 的 10 輪。
  - major 較多的輪:49 輪,下一輪有 major 的 43 輪。
  - 兩組的比率沒有差別,也就是這份資料看不出「折 minor 讓下一輪更容易有 major」。
- 另外,major 仍照舊必折,下一輪的審查也照舊;跑滿三輪且第三輪仍有 major 的 72/110(65%)不會因這個改動變少。
- 預期的好處最多是「修補縮小、折入條數變少」。以修補大小回放的分層看,修補小一級下一輪有 major 的比率約降 10 個百分點,效果有限。
- 計劃沒有收斂的量測指標。REVISIT 只看放行件數、去向比例和逃逸帳,看不出收斂有沒有改善。
- 建議加一個指標:「有 major 的輪,下一輪仍有 major 的比率」和「跑滿三輪仍有 major 的比率」。

總結:整體最高等級是 minor,blocking 0 條。沒有發現字面實作會做錯的洞。重點是把數字分母與防放水檢查的實際強度寫準,補 d2 的取代紀錄與「核心主張類測試維持高嚴重度」的例外,並加收斂量測指標。

相關檔案:
- `/tmp/代碼審minor解綁-r1.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/docs/.canary-log.jsonl`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/governance/review-reports/code-週評通知/`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/governance/replay/code-規格閘半套/verdict.json`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/docs/lumos-toolchain-knowledge/Projects/probe輪退場_計劃.md`
