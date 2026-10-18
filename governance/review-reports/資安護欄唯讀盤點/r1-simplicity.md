severity: major

F1：無關筆記的 Markdown 圍欄錯字會讓整份資安盤點不可用

severity: major

blocking: 是

引句:「未閉合一般圍欄也列解析錯誤，避免其後登記被隱藏。」

規格要求列舉 vault 內所有 Markdown，連作廢筆記也讀；因此一篇完全沒有 `lumos-security-v1` 的舊 Project／Archive 筆記只要少了結尾圍欄，就會把本來完整的安全登記變成解析錯誤並退出 2。這不是 d6 要求的安全資料完整性，而是把整個 vault 的一般 Markdown 語法正確性升成新指令的硬前提，新增一套全庫 CommonMark 守衛且造成真實不可用。既有共用圍欄讀法對未閉合圍欄採寬鬆回退，並未把任意筆記的圍欄錯字當全庫硬錯。

file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:48`

file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:81`

file: `scripts/lumos:4936`

file: `scripts/lumos:4982`

最小翻紅（規格推演；CLI 尚未實作，未能實際執行）：建 `Systems/security.md`，放一筆完整合法登記；另建 `Projects/old.md`，內容只有普通 ```` ```text ```` 開頭、沒有專用標記且未閉合。依本規格執行 `lumos security list --json` 應因後者退出 2，令前者無法產生完整盤點。

最小修正：先以原始文字判定該篇是否含專用標記；只有含 `lumos-security-v1` 的篇章才把一般圍欄不閉合升成登記解析錯誤。完全沒有專用標記的篇章沿用既有可見行解析，不替本功能新增全庫 Markdown lint。

F2：必要證據種類與證據引用是兩張無關聯清單，算法無法得到自己規定的結論

severity: major

blocking: 是

引句:「required_evidence為空或證據種類對應未核對時，聚合至少incomplete。」

`required_evidence` 只列種類，`evidence_refs` 只列 Verification 路徑；schema 沒有任何欄位把某份 Verification 對應到 `behavior`、`review`、`deployment` 等種類。結果不是維護者被迫靠散文猜分類，就是所有實際有必要證據的控制項永久停在 `incomplete`。這讓新增的種類列舉、聚合規則與逐引用狀態成為無法使用的重複模型，不能滿足母計劃「必要證據與實際證據」的盤點需求。

file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:63`

file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:64`

file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:84`

file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:273`

最小翻紅（規格推演；CLI 尚未實作，未能實際執行）：一筆 control 宣告 `required_evidence=["behavior","review"]`，並引用兩篇 status=pass、前提欄位完整的 Verification；兩篇其實都是 behavior 測試。現有 schema 無法判斷 review 缺失，實作者只能誤給 `declared_only`，或保守地永遠給 `incomplete`。

最小修正：把兩張平行陣列合成一個最小對應，例如 `evidence_refs=[{"kind":"behavior","ref":"Verification/X"}, {"kind":"review","ref":"Verification/Y"}]`，移除獨立 `required_evidence`；若需求必須先宣告再收證，則至少新增明確的 kind→refs 對應並以同一結構產生缺項。

目的與授權、d5/d6、Q3/Q4界線：已讀，無 finding。

世界解、CLI契約與單一 vault：已讀，無 finding。

輸出契約、首案順序與 S1–S8：除 F1、F2 外，已讀，無 finding。

實務隱患—守衛誤讀：F1。

實務隱患—輸入安全：已讀，無 finding；路徑跳脫、符號連結、終端控制字元及壞資料洩漏均有明確守衛。

實務隱患—資源：已讀，無 finding；檔案、總量與數量上限均 fail-closed。

實務隱患—併發：已讀，無 finding；規格沒有宣稱跨檔原子快照，偵測到變動時退出 2。

實務隱患—回退：已讀，無 finding；只撤新命令與專用解析，未牽動既有讀指令語意。

金流、網路、部署：不涉及。

凍結快照核對：與 `ae54f89b0827bb5d216e9b930d58ee6047edec00` 指定檔案 SHA-256 相同；refcheck 為 0 claims／0 missing。

總結：最嚴重 severity: major；blocking: 2。
