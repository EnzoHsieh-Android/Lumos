severity: major

F1 覆蓋輸出漏掉「已映射但不適用／未驗」入口，會讓機器消費者看不到安全缺口  
severity: major  
blocking: 是  
引句:「coverage含inventory來源、status（known_inventory或unknown）、unmapped、candidate_only及限制說明。」  
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:92`  
外部證據file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:278`  
具體輸入→錯誤：建立入口 `S1`，唯一映射控制項為 `lifecycle=active`、`concerns=["security"]`、`reported_status=not_applicable`。依現行算法，`S1` 既非 `unmapped` 也非 `candidate_only`；而 coverage 契約沒有「適用性待判／未驗」集合，機器只讀 coverage 時會得到零缺口，違反 d6 要求。  
最小重現：以上单一 surface、单一 active/not_applicable control 即可；预期 coverage 明列适用性缺口，稿面算法则不会列入两个既有缺口集合。  
最小修正：在 coverage 固定增加 `applicability_pending` 與 `unverified`（或等價的逐入口狀態），並規定僅有 `not_applicable`、`defect`、`untested`、`partial` 或不足證據的映射不能消除這兩類缺口；補一個只有 active/not_applicable 映射的 S5/S6 對照案例。

F2 現行讀取入口會跟隨符號連結，規格沒有釘住檢查到開檔間的置換競態  
severity: major  
blocking: 是  
引句:「引用只允許vault內正常檔案；拒絕絕對路徑、父目錄跳脫與符號連結，不讀其他專案、家目錄或外部檔案。」  
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:83`  
外部證據file: `scripts/lumos:608`  
外部證據file: `scripts/lumos:612`  
具體輸入→錯誤：若實作者用 `is_symlink()` 後再 `read_text()`，攻擊者可在兩者之間把正常 `Systems/x.md` 換成指向 vault 外的連結；S3 目前只描述固定 symlink，這種實作仍可通過驗收卻讀到外部內容。  
最小重現：已在規定的 `/tmp/lumos-seat-work/資安護欄唯讀盤點/integration/` 建立 `Systems/outside.md -> /etc/hosts`；現行 `rglob("*.md")` 會列出它，`read_text()` 成功讀到目標內容。  
最小修正：規格指定以目錄／檔案描述符開啟並禁跟隨連結（例如 `openat`/`O_NOFOLLOW` 或平台等價作法），開啟後以 `fstat` 驗證一般檔案且仍位於受信目錄；S3 增加「列舉後、開檔前置換為 symlink」測試，必須不洩露哨兵且退出 2。

合約、d5、d6、Q3／Q4：d5 的來源類型與關注面分離、逐條證據限制有保留；d6 的唯讀盤點、零條目不得通過與分離完整性有保留，但覆蓋輸出有 F1；Q3 仍只阻塞故障執行，Q4 仍阻塞正式交付接線，稿面未改其狀態。Invariant 仍沿用 `extract_contracts` 並精確匹配，未擴充既有合約語法。除 F1 外已讀，無 finding。

sources／contracts／decision／verification 生命週期：合法 Verification 狀態 `pass/stale/superseded/pending/abandoned` 與稿面映射一致；失效決策、撤除項、例外期限均保留，無 finding。

parse/load/main 整合：`parse_frontmatter`、`Env.from_texts`、`extract_contracts` 與 argparse 接點方向可落實；除 F2 的安全開檔缺口外，已讀無 finding。

實務隱患：守衛誤讀見 F1；輸入安全與併發見 F2；資源上限與超限退出 2 已明定；回退不改 contracts/query/enforcement；本案不付款、不連網、不部署。其餘已讀，無 finding。

refcheck：claims 0、missing 0、out_of_range 0。  
prose-lint：0；未以詞表結果取代語意審查。

總結最嚴重 severity: major；blocking: 2。
