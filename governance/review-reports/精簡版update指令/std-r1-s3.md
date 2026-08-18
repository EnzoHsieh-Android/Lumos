# std-r1 s3 整合席審計報告

## Finding 1 [blocker→編排者以遠端現況降級] hooks 回填 premise 質疑——「刻意不裝」裁定衝突

引句：「`slim/` 新增 `hooks/`(內容=Citrus_Lumos 現行兩支,含 2026-08-18 檔頭修真——發行 repo 是它們目前唯一真身,搬回工廠)」

證據鏈:install.py docstring「不設 core.hooksPath、不裝任何 Claude hook」;~/Citrus_Lumos README 227 行「本精簡版刻意不裝任何 hook」;該 clone 的 hooks/pre-commit 檔頭「由 install.py 複製進 scripts/hooks/」與 install.py 宣告矛盾;install.py 零 hooks 相關 code。判 hooks 為被裁定砍掉未清乾淨的殘餘。
(編排者裁決註:席位查的 ~/Citrus_Lumos 為 stale clone(停在 08-14);GitHub main 6e249eb(08-18)已含調和後 README(「安裝器刻意不裝…opt-in 接法」)與修真後 hook 檔頭——矛盾原文均已不存在。降級,但衍生要求(決策脈絡明文/回填來源釘遠端/mode bit 斷言/同步前先 pull)全採。)

附帶:slim-gen chmod 清單只列三支 .sh,hooks 兩支無副檔名 script 不在列——copytree copy2 保留來源 mode bit 屬隱含假設,spec 無一語、無測試斷言,靜默死門型態。

## Finding 2 [major] slim-scan 白名單/舊豁免對新增「lumos update」文字失能——不誤翻紅但也永不驗證

引句：「`lumos update` 一行(限一行安裝的固定落點;手動 clone 者指路)或重跑一行安裝」

removed 集合=完整版 help−白名單,"update" 在其中;t_slim_readme_assertions 的 `("update","prefixed")` 豁免為舊「本包沒有 update」誠實聲明而設,不分語境——新〈更新方式〉段被同一豁免吃掉,守衛對新內容徹底失能且 spec 未提。

## Finding 3 [major] 兩處拼接與既有 `ast.parse(new_text)` 語法自檢的先後順序未定

引句：「模板檔不存在→生成硬失敗(fail loud,防靜默漏拼)。」

slim-gen 寫檔前有 ast.parse 自檢(手術語法洞防線);拼接若在自檢後=模板縮排/語法錯直接出貨 chmod 755,使用者端才炸 SyntaxError。spec 對「模板存在但拼接後語法壞」零檢查點。

## Finding 4 [minor] 兩處「2026-08-18」引註與 ~/Citrus_Lumos git 歷史不符

引句：「②2026-08-18 README hooks 章同型(直接推在發行 repo)」

該 clone log:hooks 最後 08-11、README 最後 08-14。(編排者裁決註:遠端 6e249eb 確為 08-18,席位讀 stale clone 所致——日期屬實,教訓轉化為 S4「先 pull 再查證」硬步驟。)

## Finding 5 [minor] 「Citrus_Lumos clone」未釘實體路徑

引句：「內容同步進 Citrus_Lumos clone(hooks/README 此後由管線攜帶)→ push」

Verification 對後人不可執行;建議釘 ~/Citrus_Lumos。

## 查證無問題項(摘)
兩拼接錨點源檔/產物皆唯一;argv 長度守衛邏輯正確;WINDOWS-NOTES.md 確為真漏檔(dist 缺);t_slim_gen dangling-handler 檢查不會誤紅;install.py 443 行凍結訊息實存(r1 major 屬真)。

max severity: blocker(編排者裁決後有效存活 max=major)
