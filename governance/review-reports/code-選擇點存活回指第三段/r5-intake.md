# r5 收貨紀錄(code-選擇點存活回指第三段,人裁第二次 extra-round 那一輪)

材料:r5-snapshot.patch(ce1b2bf48..667b346fb,4148 行,排除卷證與治理帳,檔清單跟 r4 同;資安席)、r5-repair.patch(09e720801..667b346fb,199 行,其餘六席主看)。r4 修正關卡全部通過(136.3 秒)。記帳全輪 --reviewed 填整份凍結快照的指紋。七席交回後才一次從逐字稿存檔,七份都已是正規化格式。資源、資安兩席 clean(沒有引句)。合約 #1、通才 #2 的引句錨不到(引句裡又包「」被截斷、或差字),改機械重現。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| c1 | 通才 #1(major)、正確性 #1、邊界 #1、架構對齊 #1、合約 #2 | major | 正文判段拿去掉結尾井號、只看第一層的標題去判,讀取器拿原始行判;`## 驗收條款 ##`(CommonMark 合法)與前面沒有二級標題的 `### 驗收條款` 那一節兩邊都看不到 | 折:換形狀,正文直接扣掉讀取器實際讀走的行(_choice_reader_lines),每一行恰好在一邊;_choice_layer_not_body 只剩審計修正紀錄判法;t_choice_plan_sections_reader_complement |
| k1 | 合約 #1(major)、通才 #2 | major | 判法上方註解與測試說明還在寫 r3 的「前綴記號、括號或冒號說明」比對,跟程式相反,照註解改會改回兩套 | 折:註解、測試說明、計劃〈用詞〉、Systems/規格閘兩行改成新判法 |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| c1 | 修前(667b346fb)_choice_plan_sections 對 `## 驗收條款 ##` 與 `### 驗收條款` 兩份計劃,另呼叫 _h2_section_lines(…, _KT_SIT_ACCEPT_H2_RE) | HIT:正文只有〈範圍〉、讀取器回 None,內容兩邊都沒有 |
| c1 歸因 | 同兩案在 09e720801(r4 修補前)與 64172d7ca(r3 修補前)各跑一次 | 兩版結果相同(兩邊都沒有):不是 r4 修補造成,是原有漏查 |
| k1 | grep scripts/lumos「整行比對:前面可帶一個不含空白的記號」:在 _choice_layer_not_body 上方;_choice_layer_not_body("驗收條款(全部有真測試、綠)") 回 False(註解字面說排除) | HIT |
| k1 歸因 | 09e720801 那版程式用的就是註解寫的比對(_CHOICE_LAYER_NOT_BODY_RE),r4 修補改了判法沒改註解 | 修補造成(regression) |

## 改壞驗翻紅(在 repo 根改 scripts/lumos、跑 -k choice_plan_sections、改完逐字還原並 cmp 確認)

| 改壞什麼 | 結果 |
|---|---|
| 不扣讀取器讀走的行 | 紅 |
| 讀取器行回空集合 | 紅 |
| 只扣驗收條款、不扣預期值表 | 紅 |
| 審計判法拿掉空標題退路 | 紅 |

(另拿掉一行沒有作用的「把讀取器標題行也記進讀走集合」:標題行本來就不進正文,改壞測不出來,留著是假守衛。)

## 先查世界

- PRIOR-ART:CommonMark 規格 ATX 標題一節:結尾那串 # 可有可無、長度不必跟開頭一樣、前面要空白(例 `# foo ##################################` 是一級標題)。來源 https://spec.commonmark.org/0.31.2/#atx-headings 、範例整理 https://ota-meshi.github.io/eslint-plugin-markdown-preferences/rules/atx-heading-closing-sequence.html 。採用:`## 驗收條款 ##` 是合法寫法,判段不能把它當成讀取器讀得到。不採:改讀取器認結尾井號(讀取器另有規格閘在用,範圍外;正文跟著讀取器走就不會兩邊漏)。
- PRIOR-ART:markdownlint 規則文件記載解析器跟作者對結構看法不同就會誤報(子清單縮排不夠被當成頂層清單)——兩支程式各自解析同一段文字會互相打架。來源 https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md 。採用:正文不再自己猜讀取器讀哪裡,直接拿讀取器的結果取補集。
- 方向:對 — 這一族(計劃標題判段)r3、r4、r5 連三輪有 major,每次都是判段跟讀取器各判一套;換成「正文 = 讀取器沒讀走的行」之後兩邊由構造保證互補,不再靠標題字面。依據上面兩個來源與本檔 _h2_section_lines「找節邏輯不准長出第三套」。
