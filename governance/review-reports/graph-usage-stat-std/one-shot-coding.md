# 一次性盤點編碼表(2026-08-30;編碼員=sonnet agent,主對話抽查 3 份全對)

判讀慣例:「引自審節點」=spec_path 那份不計實質;圖譜當搜尋語料(無節點名/內容進論證)→零〔語料〕;節點名當資料→表面;節點內容載重→實質。code 引註/治理帳/skill 檔不算圖譜。
樣本口徑:帳 812 列,ts≥2026-08-29 有 report_path 26 列=26 份(全 repo 內實存,無重複無淘汰);殘留線=2026-08-29T15:40:35。

| 報告 | 迴圈 | ts | 殘留 | 判定 | 證據引句 |
|---|---|---|---|---|---|
| impact-鏡頭機械化/r1-summary | impact(design) | 08-29T15:07 | 是 | 零(僅自審) | 「逐條去向見計劃節點」 |
| impact-鏡頭機械化/r2-summary | impact(design) | 08-29T15:25 | 是 | 實質 | 「摘要明寫「已排除:掛進pitfalls」」(送審前impact) |
| intake-guard/r1-summary | intake(design) | 08-30T12:08 | 否 | 實質 | 「計劃節點登記的是「連兩案缺席→升級」」(三修計劃:50) |
| intake-guard/r2-summary | intake(design) | 08-30T12:23 | 否 | 實質 | 「嚴重度綁定案實為外家否決advisory優先」 |
| intake-guard/r3-summary | intake(design) | 08-30T12:38 | 否 | 零 | 全篇 daily-governance.sh/skill/治理帳 |
| entry-latch/r1-external | entry-latch(design) | 08-30T16:32 | 否 | 實質 | 「既有裁定已明載…可能不跑的指令」(impact計劃:38-39) |
| entry-latch/r1-correctness | entry-latch(design) | 08-30T16:34 | 否 | 表面 | 「三個 [[]] 目標存在」〔語料〕 |
| entry-latch/r1-boundary | entry-latch(design) | 08-30T16:34 | 否 | 表面 | 「送審前…計劃 帶空白命中1篇」(名當測資) |
| entry-latch/r2-delta | entry-latch(design) | 08-30T16:48 | 否 | 拿不準 | 「行號抽驗…impact計劃:53✓」(核驗他人引句算不算) |
| entry-latch/r2-external | entry-latch(design) | 08-30T16:48 | 否 | 零 | 全篇對 spec 修訂條目 |
| code-entry-latch/r1-correctness | code | 08-30T17:49 | 否 | 零 | 「自建 vault 實測」(合成語料) |
| code-entry-latch/r1-resource | code | 08-30T17:49 | 否 | 實質★ | 「Verification 筆記宣稱 0.6s」(作者自寫驗證筆記) |
| code-entry-latch/r1-boundary | code | 08-30T17:49 | 否 | 零〔語料〕 | 「暫用 vault 實測 100% 召回」 |
| code-entry-latch/r1-contract | code | 08-30T17:49 | 否 | 實質★ | 「宣稱 3/4/2,實測 2/3/0」(同上) |
| code-entry-latch/r1-arch | code | 08-30T17:49 | 否 | 零 | 全篇 scripts/lumos 慣例比對 |
| code-entry-latch/r1-ext-finder | code | 08-30T17:49 | 否 | 零 | 全篇 code 行號 |
| code-entry-latch/r1-ext-veto | code | 08-30T17:49 | 否 | 零(僅自審) | 「…計劃.md:52…spec 明定的共同鐵則」 |
| code-entry-latch/r2-delta | code | 08-30T18:04 | 否 | 零〔語料〕 | 「詞只出現在 decisions:…的節點」(測試構造) |
| code-entry-latch/r2-ext-reverdict | code | 08-30T18:04 | 否 | 零 | 全篇測試/rc/JSON |
| code-entry-latch/r3-final | code | 08-30T18:11 | 否 | 表面 | 「首位=impact鏡頭機械化_計劃」(重放輸出) |
| graph-usage-stat/r1-generalist | gus(light) | 08-30T19:50 | 否 | 實質 | 「「d8」跨節點有三個互斥候選」(讀多節點錨定) |
| graph-usage-stat-std/r1-s1-mechanical | gus-std(design) | 08-30T20:06 | 否 | 表面 | 「`設計審收斂重定義_計劃.md`…抓不到」 |
| graph-usage-stat-std/r1-s3-contract | gus-std(design) | 08-30T20:06 | 否 | 實質 | 「E4 要分辨話多與真本事」(地基盤點:58) |
| graph-usage-stat-std/r1-arch | gus-std(design) | 08-30T20:06 | 否 | 零 | 全篇 mapper/link_target 對齊 |
| graph-usage-stat-std/r1-ext-veto | gus-std(design) | 08-30T20:06 | 否 | 實質 | 「與前案否決的「派工端機械強制」」(impact計劃:18-21) |
| graph-usage-stat-std/r1-s2-data-reality | gus-std(design) | 08-30T20:06 | 否 | 零 | 全篇重算帳列/git 時刻 |

匯總(24 正式):實質 8(嚴格 6★)/表面 4/零 11/拿不準 1;殘留 2:實質 1、零 1。
副觀察:8 實質中 4 出自外家或轉述外家;code 10 份嚴格 0 真使用。
