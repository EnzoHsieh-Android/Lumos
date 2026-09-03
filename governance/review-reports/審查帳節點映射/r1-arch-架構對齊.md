# r1 席報告:架構對齊(sonnet,不佔人數)

## 問1 分層
### ★capture-counts 的「自動路徑」撞上它自己的 vault-free 合約★
severity: major
blocking: 是
「自動算被幾席抓到」唯一講得通的讀法=讀同 loop+round 已記帳的多筆席記錄——否則「不靠編排者手數」是假的。
但 capture-counts 今天是「純機械原語(不碰圖譜):vault-free」,dispatch 在 vault 解析★之前★攔截、env=None
(`scripts/lumos:17699-17702`、`:17828`),輸入只吃 CLI 字串,從不碰 .canary-log.jsonl;
圖譜節點把這當合約記著(`Systems/heterogeneous-finder-ensemble.md:26,66`)。
★這正是本 repo 死過兩次的坑★:impact鏡頭機械化「pitfalls 明文 vault-free,掛 impact 即破約」(:70);
已知坑機械前置「破 vault-free 邊界…本輪不做」(:43)。材料完全沒提 vault-free。
引句:「`capture-counts` 加自動路徑:多席報告的 finding 若帶相同 `finding-nodes`,視為同一相異缺陷 → 直接算「被幾席抓到」」

### 新欄解析放內聯還是抽 helper,未表態
severity: minor
blocking: 否
既有兩層慣例:集合型走 `_ids` closure(:4128);id=value 字典型(finding_kinds/refute_verdicts)完全內聯各寫一份(:4173-4187、:4194-4231)。
`--finding-nodes` 是「id→多節點」全新形狀,兩種都不是現成套用;材料未說放哪——是未解三項之外的第四個洞。
引句:「`--finding-nodes <id=節點[,節點],…>`:每個 finding 對應到哪些節點(可多、可空)」

## 問2 命名/錯誤處理
### `--finding-nodes` 語法疊用逗號,兩種既有慣例都不是
severity: minor ⚠(貼近 major 邊界)
blocking: 是
既有:①一旗標一逗號串扁平列表(`_ids`)②旗標可重複每次一個 id=純量(`action="append"`,:17133-17137)。
材料的 `id=節點[,節點],…` 在同一字串疊用逗號當兩種分隔——第三種形狀、無先例可抽測試。
若改成旗標可重複、一次一個 id、節點內部另換分隔符,就落回既有慣例。
引句:「`--finding-nodes <id=節點[,節點],…>`:每個 finding 對應到哪些節點」

### 驗證方向有沿用,但沒點名重用既有 helper/訊息模板
severity: minor
blocking: 否
「節點不存在 rc2」與既有 `env.find(node)`→「擋下:圖譜裡找不到叫 {node} 的筆記…」(:3182-3184 等十餘處)方向一致、cmd_canary 拿得到 env 可直接複用;
但材料沒寫要不要重用、rc2 訊息文字也沒寫,無法核對白話三段式。
引句:「`finding-nodes` 的 id 必須 ⊆ `findings_set`;節點必須存在於圖譜(不存在 rc2 擋)」

## 問3 第二種做法
### ★recount.py 不是補空白,是第三個算「覆蓋率/重疊率」的地方★
severity: major
blocking: 是
`lumos loop canary-stats` 已直接開 .canary-log.jsonl(:4984)且已在算幾乎同一件事——`_print_overlap` 從 capture_counts 算「僅單席抓到 X/Y(Z%)」(:5035-5046);
recount.py 的 `rate()` 從同一欄算「獨家發現率」(recount.py:14-21)——本質同一個東西住兩個檔、各維護一份 parse 邏輯。
加上上一輪已判的 eval 腳本讀帳分裂(retrieval_eval 走 CLI vs k1/ledger_analysis 直開)未解決;
本案往「直接開檔」那邊再加讀法,讓「算覆蓋率的地方」變第三個維護點。材料沒討論「D1/D2 要不要進 canary-stats」。
引句:「`recount.py` 加兩個讀法(D1/D2 是母案〈派工時自動補清單〉預註冊的兩個指標名,本案只提供取數)」

不對齊共 5,major 2。
