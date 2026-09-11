severity: major

## 逐節覆蓋

1. frontmatter／決策 d1–d5：已讀，無 finding。
2. 為什麼：已讀，無 finding。
3. 世界上怎麼做的：已讀，無 finding；CODEOWNERS、notowned、Nx 邊界規則的描述與其[官方文件](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)、[專案說明](https://github.com/mszostok/codeowners-validator)、[Nx 文件](https://nx.dev/docs/kb/enforce-module-boundaries)一致。
4. 名詞：已讀，finding 見 F1、F2、F5、F9、F10。
5. 規則一：已讀，finding 見 F1。
6. 規則二：已讀，finding 見 F3。
7. 規則三：已讀，finding 見 F4、F5。
8. 規則四：已讀，無 finding。
9. 規則五：已讀，finding 見 F8。
10. 在哪裡檢查：已讀，finding 見 F1、F2、F6、F12。
11. 舊帳：已讀，finding 見 F7、F10。
12. 讓規則被看見：已讀，無 finding。
13. 邊界：已讀，finding 見 F2、F4、F10。
14. 範圍外：已讀，無 finding。
15. 落點：已讀，無 finding。
16. 實務隱患：已讀，finding 見 F9、F11。
17. 驗收怎麼跑：已讀；所有 `[test:]` 目標均存在，finding 見 F9。
18. 回頭條件：已讀，finding 見 F11。
19. 實作時對計劃的修訂：已讀，finding 見 F9。
20. 合約候選：已讀，無 finding。
21. 審計修正紀錄：已讀，第一輪處置核對見末節。
22. 交叉引用：四個 `[[...]]` 目標與全部內部 `[S…]` 目標均存在，無壞引用。

### F1 `--staged` 仍受未暫存設定與工具內容控制

severity: major
blocking: 是 — 不改的話，未暫存的 `gate=off` 可以關掉提交索引的守衛，工具自裝檔的未暫存內容也能反轉是否納管。
引句:「提交前一律讀提交索引裡的版本（節點與程式檔都是），不讀工作目錄」
file: `scripts/lumos:17943` `--staged` 與 `--diff` 都先用工作樹讀取 `_nodehome_config(root)`。
file: `scripts/lumos:17380` 設定直接從工作樹 `.lumos/config.json` 讀取。
file: `scripts/lumos:17980` staged 模式以 `ref=None` 呼叫 `_vendored_state`。
file: `scripts/lumos:13502` `ref=None` 明定讀工作目錄，而不是提交索引。
1. 暫存一份違規提交，再只於工作樹把 `node_home.gate` 改成 off，Gate H 會直接 rc0。
2. 暫存版與工作樹版的 vendored 檔內容不同時，內容指紋也會依錯誤版本決定排除或納管。

### F2 推送非目前分支時，端點快照會混入目前工作樹

severity: major
blocking: 是 — 不改的話，推送另一個 local ref 會用目前 checkout 的設定、vault 與路徑拼法判斷，產生誤擋或漏擋。
引句:「推送前讀範圍兩端的提交」
file: `scripts/lumos:17938` vault 由目前工作樹的 `_vault_in(root)` 決定。
file: `scripts/lumos:17943` `node_home` 設定同樣取目前工作樹。
file: `scripts/lumos:11071` about_code 比對鍵透過目前磁碟解析 symlink、大小寫與 Unicode 拼法，沒有端點參數。
file: `scripts/hooks/pre-push:188` 掛鉤允許檢查 stdin 指定的任意 local SHA，不保證它就是目前 checkout。
1. 非目前分支若有不同 vault 名、ignore、max_files 或路徑大小寫，檢查結果就不是範圍兩端的狀態。
2. 這也使 [S38] 的推送前隔離承諾在平行分支情境下不成立。

### F3 新增程式檔可喚醒既有外家引用而不觸發 S9

severity: major
blocking: 是 — 不改的話，節點不用改字也能因新增程式檔而新成為「別人的檔入口」，守衛會漏擋。
引句:「擋：這篇之後比之前多出來的別人的檔（這次新開的節點＝全部都算新）」
file: `scripts/lumos:17723` 規則二只迭代 `changed_new` 裡被修改的 Systems 節點。
file: `scripts/lumos:17735` foreign-before／foreign-now 差集位於該迴圈內，未修改的節點完全不會比較。
1. 既有節點若早已寫著尚不存在的 `src/new.py`，之後新增該檔並把家設為另一篇，這篇會新成為 foreign ref。
2. 因舊節點沒有進 `changed_new`，S9 仍會放行，之後 impact 反而開始把錯節點推出來。

### F4 刪除程式檔不算規則三的「改了需要家的檔」

severity: major
blocking: 是 — 不改的話，刪程式檔時可以把刪除理由寫進任意 Systems 節點，寫回落點閘完全不執行。
引句:「只在這次改了需要家的檔時生效；純圖譜提交（整理節點、補家）不受這條管」
file: `scripts/lumos:17708` change 的 `new` 為空時立即跳過，刪除路徑不會進 `changed_new`。
file: `scripts/lumos:17715` `code_changed` 只取變更後仍存在且屬於 `reqN` 的路徑。
file: `scripts/lumos:17757` 規則三只有 `code_changed` 非空才執行。
1. 刪除 `src/a.py` 並更新不相關的 `Systems/B` 時，home check 把它當成沒有程式變更。
2. Spec 未把刪除排除於「改了需要家的檔」，實作卻靜默排除。

### F5 決策以 YAML 原文而非解析值比較

severity: major
blocking: 是 — 不改的話，只調整 decisions 的引號或等價 YAML 表示也會被判定為內容寫回，造成錯誤擋下。
引句:「兩個版本之間，摘要、決策、正文三者任一不同（逐欄比對兩個版本解析後的值）」
file: `scripts/lumos:17549` 實作另存 `dec_raw`，沒有取解析後的 decisions 值。
file: `scripts/lumos:17565` 內容簽名直接包含 `dec_raw.strip()`。
1. `content: a` 改成 `content: "a"` 的解析值相同，實作簽名卻不同。
2. 同提交若改了別支程式檔，這種純格式整理會觸發 S13 誤擋。

### F6 治理帳的 `nodes` 欄會混入節點路徑且缺少部分配對

severity: major
blocking: 是 — 不改的話，統計與撤回清理會把節點路徑當程式檔，無法可靠重建哪些 about_code 是被閘逼出的。
引句:「事件裡記的是檔案路徑與（檔，節點）配對，所以也登記進『這個來源記的不是節點名』那張統計語意表」
file: `scripts/lumos:17739` foreign finding 的 tuple 順序是 `(節點, 程式檔, 家)`。
file: `scripts/lumos:17989` 治理帳一律取 tuple 的第零項當檔案路徑。
file: `scripts/lumos:17994` `pairs` 只寫入另外累積的部分類別，foreign finding 沒有加入。
file: `scripts/lumos:4700` 統計語意卻宣告 `nodehome-check` 的 nodes 全是程式檔路徑。
1. foreign 違規會把 `Systems/A.md` 寫入 nodes，而真正的程式檔不在 nodes 或 pairs。
2. [S27]、規則撤回段與 REVISIT 使用的證據形狀因此互相對不上。

### F7 健檢把繞過守衛的改名誤列成上線前舊帳

severity: major
blocking: 是 — 不改的話，透過 `--no-verify` 進入的改名違規會失去「守衛被繞過」警示。
引句:「守衛上線之後才新增的（該被擋卻進來了＝有人繞過或開關被關，放在最前面、講明）」
file: `scripts/lumos:17909` 上線後路徑只以 `git log --diff-filter=A` 收集。
file: `scripts/lumos:17711` 即時檢查明確把 `R` 與 `C` 都視為新增路徑。
1. S3 會擋 `git mv src/a.py src/b.py` 後沒有家的 `src/b.py`。
2. 同一改名若繞過 hook，doctor 不收 `R` 路徑，會把 `src/b.py` 歸到 legacy，與 S39 的判準不一致。

### F8 處置閘沒有驗證 spec 真在圖譜內

severity: major
blocking: 是 — 不改的話，任意名為 Projects 的外部目錄都能冒充圖譜計劃並通過 lands_in 檢查。
引句:「審材是圖譜裡 Projects 底下、type 為 project 的 .md 計劃才看」
file: `scripts/lumos:15017` 實作直接接受呼叫方傳入的任意 `spec` 路徑。
file: `scripts/lumos:15018` 路徑判定只驗副檔名與父目錄 basename 是否為 `Projects`。
file: `scripts/lumos:15040` 後續更直接把該外部檔的祖父目錄當成 vault。
1. `/tmp/Projects/fake.md` 只要寫 `type: project` 與格式正確的 lands_in，就會被當成適用計劃。
2. 程式沒有驗證它位於 repo 的 `docs/*-knowledge/Projects/`。

### F9 批次讀取修訂仍與 S38、效能處置及實作矛盾

severity: major
blocking: 是 — 不改的話，實作者無法判斷應採批次讀取還是逐檔 git show，且現有實作沒有落實其餘縮讀承諾。
引句:「讀版本：從『一次批次讀取』改成『跟磁碟一樣的直接讀、不一樣的用既有 git show 包裝讀』」
file: `scripts/lumos:17536` 現有 reader 對每支不同版本的檔各跑一次 `git show`。
file: `scripts/lumos:17579` `_nodehome_side` 仍遍歷快照裡全部 Systems 節點。
file: `scripts/lumos:17584` 每篇 Systems 節點都讀完整內容並解析，不是全圖只讀 about_code 與狀態。
1. [S38] 與實務隱患段仍逐字要求「一次批次讀取」，跟修訂段正面相反。
2. 名詞段承諾起點只讀有變節點、其餘與終點共用，現有兩側 `_nodehome_side` 也各自完整讀取，S32 的效能策略尚未實現。

### F10 非 UTF-8 檔名沒有出現在 doctor 健檢

severity: minor
blocking: 否 — 這是明訂提醒的漏接，不會讓硬閘做出相反裁定。
引句:「這種檔永遠不算需要家的檔，只在健檢提醒『建議改名或加進 ignore』」
file: `scripts/lumos:17924` `_nodehome_ledger` 有回傳 `bad_names`。
file: `scripts/lumos:2109` doctor 的 S8 只輸出 bypassed 與 legacy。
file: `scripts/lumos:2145` S8–S10 結束前也只補設定警告，從未消費 `bad_names`。
1. home check 只提醒這次改到的壞檔名，既有或繞過後留下的壞檔名不會在 doctor 出現。
2. 測試只覆蓋 home check，沒有驗 doctor 的這條承諾。

### F11 無鎖治理帳風險沒有接電的回頭條件

severity: major
blocking: 是 — 不改的話，平行檢查造成的 JSONL 損壞或遺失會直接破壞撤回與誤擋分析證據，且永遠沒有重驗入口。
引句:「跟其他閘同一條沒有鎖的附加路徑，是既有天花板，不另外處理」
file: `scripts/lumos:922` 治理帳以無鎖的 append/open/write 寫入。
1. 這是明文承認的併發風險，但相鄰段落及「回頭條件」都沒有日期或事件型 REVISIT。
2. S27、撤回段與 2026-10-11 誤擋分析都依賴這本帳，不能把其完整性風險列成永久不處理的散文。

### F12 `--staged` 與 `--diff` 同給時的語意未定義

severity: minor
blocking: 否 — 正常掛鉤不會同時傳入兩者，但公開 CLI 對矛盾輸入會靜默選邊。
引句:「新指令 `lumos home check`：`--staged`（提交前，看這次要提交的內容）或 `--diff <範圍>`」
file: `scripts/lumos:25427` 兩個參數不是互斥群組。
file: `scripts/lumos:25618` 同給時實作靜默讓 `--diff` 優先。
1. Spec 沒定義同給應拒絕、哪個優先或如何出聲。
2. CLI 應把這個組合寫死，避免呼叫方以為檢查的是索引。

## 第一輪處置核對

1. G1／G2：修到；[S13b] 與 [S35] 已補上原核心漏洞。
2. G3：修出新洞；已改成整段端點比，但批次／逐檔及縮讀敘述互相衝突，見 F9。
3. G7／G14：修出新洞；值域與 glob 已定義，但 staged 設定與 vendored 指紋仍讀工作樹，見 F1。
4. G12：沒完全修到；無損路徑判定已補，doctor 的非 UTF-8 提醒沒接上，見 F10。
5. G19：修出新洞；摘要與決策納入了，但決策比較的是 YAML 原文而非解析值，見 F5。
6. G21：沒完全修到；type 與 Projects basename 有驗，圖譜／repo containment 沒驗，見 F8。
7. G23：修到；文字已誠實改為不改節點、會附加治理帳。
8. G24：修出新洞；on／warn／off 已有，但未暫存的 off 可關掉 staged 閘，見 F1。
9. G25：沒完全修到；新增檔能分流，繞過後的改名路徑仍被列成舊帳，見 F7。
10. G26／G29：修出新洞；事件與語意表已新增，但 payload 會把節點當檔案且缺配對，見 F6。
11. G35：修到；多家檔的天花板、lands_in 與 REVISIT 都已明列。

## 實務隱患鏡頭

1. 誤擋：有，F1、F2、F5。
2. 漏擋：有，F1、F2、F3、F4、F7、F8。
3. 設定與升級：有，F1；未暫存設定可改變 staged 判定。
4. 平行分支與非目前 ref：有，F2。
5. 併發與治理帳完整性：有，F11。
6. 回滾與可觀測性：有，F6、F7、F11。
7. 效能與大圖譜：有，F9。
8. 路徑、改名與編碼：有，F2、F7、F10。
9. 合併、改基底、新分支：新分支端點算法已讀；除 F2 的非目前 ref 污染外，無新增 finding。
10. CLI 邊界：有，F12。
11. 新依賴與供應鏈：無；實作只使用 Python 標準庫與既有 git 包裝。
12. 金流、不可逆、正式環境、對外寄送、認證與 PII：無；功能只讀本機 repo／圖譜並附加本機治理事件。

總結:最高 severity major,blocking 共 10 條
