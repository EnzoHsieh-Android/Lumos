severity: major

concurrency-F1  
severity: major  
blocking: 是

觀察：設計允許固定索引樹與既有起點共同供應額外路由證據，卻未定義兩者的優先序。現行流程又把 `N`、`B` 的結果直接合併進無來源標記的同一個集合；只把讀取來源換成固定樹，仍可能讓起點的合法證據掩蓋捕獲樹中的非法版本。

獨立判準：凡用來放行目前暫存內容的正向證據，只要相關檔案、宣告或設定存在於捕獲樹，就必須由捕獲樹版本裁決；起點只能協助判讀刪除或改名，不能覆蓋捕獲樹的非法結果。合併後仍須保留來源與失效原因。

具體場景：起點中的測試是普通檔且安家宣告合法；暫存版本把同一測試改成連結檔或移除宣告，同時修改受管程式。捕獲樹對該測試應拒收，但起點仍產生 route ID；目前的集合聯集保留該 ID，後續可能借到額外證據而放行，直接違反「非法來源仍拒收」。

引句:「額外路由的測試內容、設定、安家宣告與普通檔案模式均從捕獲樹核對，並可讀既有起點」

file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:975`  
file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:984`

resources-F2  
severity: major  
blocking: 是

觀察：規格要求記錄增量 bundle 的前置提交與取回入口，但沒有要求冷還原必須從空白物件庫、經由該入口實際取得前置版本。交付段又明定只提交增量 bundle 與收據，不提交完整 bundle／archive；因此收據可能只是證明準備者本機原本就有前置物件。

獨立判準：增量封存的可取回證據必須從無既有物件、無 alternates／共享物件庫的環境開始，完全透過收據所記入口取得精確前置 commit，核對其 tree 與完整必要物件，再套用增量 bundle。不得以原始 clone、環境中既有物件或未記錄的遠端補件完成還原。

具體場景：製作者在已有 `c4f2b0cf…` 完整物件的本機 clone 中驗證 bundle，還原成功並留下收據；但記錄的遠端入口實際不允許依 SHA 取得該舊提交，或只提供不含它的淺層歷史。交付者拿到已提交的增量 bundle 時缺少 prerequisite，無法還原；設計仍可能把原本受環境污染的收據判成來源已留存。

引句:「增量bundle明記前置commit與取回入口，核對指紋；bundle須實際還原commit/tree及必要blob」

file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:33`  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:74`  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:76`

覆蓋與未驗邊界：

- 已覆蓋索引捕獲、起點／終點證據合併、ABA 邊界、增量 bundle、前置版本取得及冷還原判準。
- 正式 index 資料面非原子化屬 spec 明示保留邊界，未另列 finding。
- 未執行任何程式、Git 實驗或外部取回，也未從既有綠筆記推導行為已驗。
- 未讀其他席、前輪報告或作者修復因果結論。

實際閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行；另 1 行行數輸出。
- 唯一真 spec：76 行。
- r2 凍結副本：76 行。
- r2 完整材料：1194 行完整讀畢；中途缺顯示的 20 行只作補讀，未重讀其他區段。
- 三檔行數輸出：4 行。
- 受控內容合計 1430 行；連同工具截斷提示計不超過 1432 行。無搜尋輸出。

最高級：major；blocking數：2