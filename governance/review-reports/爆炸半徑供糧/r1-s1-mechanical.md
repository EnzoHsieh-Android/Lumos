# 爆糧 r1 機械可行席(照字面走 B)
M-1|minor:CJK 檔名 octal 轉義 header 靜默漏抽(3/62 真 patch 實測)。引句:「從 patch 的 diff header 抽觸及檔案清單→跑既有 impact 計算」
M-2|major|blocking:是:in-process 呼叫 impact 不 redirect 會雙 JSON 破 ~20 處消費端;spec 稱對齊 A 鐵則卻沒提。引句:「advisory、fail-open,對齊入口栓 A 全部既有鐵則」
M-3|major|blocking:是:固定席層底層無上限——真 patch 實測 pinned 20+11=31,「top 3」在原語上不成立。引句:「B 印「帶合約/事故 tag 的 top N(暫 3)+其餘印名列表」」
M-4|blocker|blocking:是:守衛比既有 _IMPACT_DIFF_SKIP 窄;routine 同 commit 的 docs 筆記=污染源(實測 design-loop.md 出假事故命中)。引句:「B 只抽 patch 內文的 diff header 檔案路徑(真改動檔),且排除 governance/review-reports 自身」
M-5|minor:--spec 是否 patch 無機械判準,但誤觸發降級無害(0 匹配→fail-open no-op)。引句:「code-* 迴圈首輪、`--spec`=凍結 patch 在手時」
M-6|blocker|blocking:是:「其餘印名」重演 d8 前一天記錄的 free_total 少報陷阱(per-file meta 無此欄);名列表牴觸「貼內容」實測裁定。引句:「其餘印名列表」
severity: blocker
