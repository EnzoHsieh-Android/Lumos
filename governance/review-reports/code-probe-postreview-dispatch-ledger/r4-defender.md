結論：A、B、D 都有反證；C 只成立為 minor 的 Markdown 呈現缺口，無具體安全攻擊鏈。四項共 0 條 blocking。

### A — evidence

severity: none  
blocking: false

`initialized_at = REAL -1.0` 不違反既有 v1 schema；現行時計錯誤只在 `now` 早於已記時間時成立。規格列出的壞帳是損壞、非一般檔、schema/version 不符或不可讀寫，未規定 `initialized_at >= 0`。

引句:「壞帳包含損壞、非一般檔、既有schema/version不符或不可讀寫；時計錯誤包含 now 小於 initialized_at 或已記 claimed_at。」

file: [探針持久用量帳_計劃.md:31](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Projects/探針持久用量帳_計劃.md:31)

引句:「CREATE TABLE ledger_meta (id INTEGER PRIMARY KEY CHECK(id=1), initialized_at REAL NOT NULL)」

file: [scenario_probe.py:745](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:745)

可執行結果：由 production helper 建立 v1 記憶體帳、再把唯一 `initialized_at` 改成 REAL `-1.0`；`now=20000, limit=1` 得 `remaining=1`、`claim=True`，意圖列成為 1。這符合 [scenario_probe.py:752](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:752) 至 [scenario_probe.py:765](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:765) 的既有判準。

before 沒有持久帳 helper，無同案例可比較。若要把負值定成壞帳，需新增 schema/政策，不能由現行 S3 推得。

### B — evidence

severity: none  
blocking: false

`calls=null` 與完全缺少 `calls` 欄，在 before、after 都是明確等價的 legacy 路徑：

引句:「calls = r.get("calls") or []」

file: [ablation_lumos_first.py:87](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:87)

型別閘也刻意只在 `calls is not None` 時要求 list；after 新增的是非 null list 內元素必須為兩個字串，沒有把 null 改判壞檔，見 [ablation_lumos_first.py:137](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:137) 及 [ablation_lumos_first.py:146](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:146)。

同案例實跑：

- before null：`invalid=[]`，M2=`0/1`
- before missing：`invalid=[]`，M2=`0/1`
- after null：`invalid=[]`，M2=`0/1`
- after missing：`invalid=[]`，M2=`0/1`

因此不是 after 回歸；S16 的「錯型 calls」由本輪新增的 malformed element 檢查承接，例如 `[42]`、`[["Bash"]]`、`[["Bash",42]]`，測試見 [test_lumos.py:38429](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/test_lumos.py:38429)。若要規定「欄位存在時 null 不合法」，需另寫與 legacy missing 的遷移政策。

### C — evidence

severity: minor（Markdown 文字呈現）；security severity: none  
blocking: false

實跑確認 before、after 都把 `![remote](https://example.invalid/pixel.png)` 原樣輸出 3 次。after 已處理 HTML、表格分隔符與換行，但沒有 literal Markdown escaping。

引句:「def text(x): return html.escape(str(x)).replace("|", "\\|").replace("\r", " ").replace("\n", " ")」

file: [ablation_lumos_first.py:416](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:416)

因此「在 Markdown renderer 中會成為 image」是實際格式缺口；但目前不足以成立 major 安全 finding：

- 實際 production 路徑只把內容寫進本機 `summary.md` 並印至 stdout，見 [ablation_lumos_first.py:506](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:506)。
- 該原始輸出目錄明確不進版控，見 [.gitignore:16](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/.gitignore:16)。
- repo 內找到的 `marked` renderer 只渲染知識圖譜 `Env.notes`，見 [scripts/lumos:651](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/lumos:651) 與 [scripts/lumos:14419](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/lumos:14419)；沒有接到消融 `summary.md`。
- S14 管的是純合併來源 meta 的 provenance，不是 Markdown literal escaping。

引句:「報表對來自題號的文字拒絕控制字元並轉義表格分隔符與 HTML 尖括號，但不聲稱這等於通用 HTML 消毒器，新增其他不可信欄位前須另驗呈現。」

file: [探針隔離與清理收斂_計劃.md:124](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md:124)

所以反證否定的是「當前 major／可利用安全鏈」；不否認 minor 的 Markdown 格式硬化缺口。repo 外有人手動開 Markdown preview 的網路行為未驗，不能冒稱絕對無風險。

### D — evidence

severity: none  
blocking: false

現行設計把 `limit` 當每次命令指定的窗口設定；帳內只存初始化時間與 launch intents，沒有永久上限欄位。每次交易用本次 `limit - used` 重算，見 [scenario_probe.py:761](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:761)。

引句:「`--max-per-window 0` 完全停用用量帳（不開帳、不查帳、不寫意圖），保留直跑相鄰路徑。」

file: [探針持久用量帳_計劃.md:28](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Projects/探針持久用量帳_計劃.md:28)

可執行結果：同一 helper-created 成熟帳，在五小時內依序 `limit=1` claim 成功、`limit=50` 再 claim 成功；帳內共兩筆，按 50 查詢剩 48。這是正常調額，與允許 `0` 完全停用的既有介面一致。

S1 要求的是同一個指定上限下競爭最後一筆時不能超額；S18 要求每次核對受管用量，兩者都未規定同帳永久鎖定首次上限。若要持久化唯一 cap、限制只能降額或設調額遷移，那是新政策，不是現行合約違反。before 尚無帳本 helper，無同案例可比較。

### 查證範圍

已執行：

- snapshot SHA-256 核對相符：`15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`
- 四個工作樹檔案 blob 均與 after 完全一致
- before/after 的 B、C 純函式同例執行
- A、D 使用 production helper 與共享記憶體 SQLite 執行
- 固定樹 `summary.md`、renderer、workflow/export 消費路徑檢索
- 依 AGENTS「查無」例外，由乾淨唯讀席獨立複核 C；結論同為 minor、非 blocking

未驗：

- 唯讀環境禁止建立 shell／檔案型暫存，因此未跑 file-backed SQLite 與整套測試；這是席位限制，不是產品失敗
- 未啟動真模型、付費探針、網路請求或 repo 外 Markdown preview
- 未宣稱四項以外的完整代碼審通過

閱讀僅限指定 snapshot 對應 hunks、必要 fixed source／測試、兩篇指定規格及 C 的必要 renderer 接線；未讀其他審查員報告、本輪 staging，未修改 repo 或圖譜。