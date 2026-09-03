---
type: project
status: doing
created: 2026-09-03
updated: 2026-09-03
tags:
  - type/project
  - status/doing
  - scope/governance
summary: |-
  FLAG:DECISION
  KEY:主 session 動手前被 impact-hook 推到眼前的固定席節點,★有沒有被碰★今天零數字(只有反例:2026-09-03 編排者撤掉自己寫的硬約束兩次)。本案第一段★只量不加義務★:hook 記推了什麼、Stop hook 對帳「推 N 篇/動手前碰 M 篇」印一行;兩週(REVISIT:2026-09-17)後拿命中率裁第二段
  KEY:「利用到」定義=行為證據(同回合 Edit 前對推送節點做過 context/show 或 Read)或回答證據(第二段才有);量的是碰沒碰不是懂沒懂,跨回合早讀過的算沒碰=下限
  KEY:現況核過:impact-hook 只留 TTL 標記不記節點;usage-log 只記 context/show;check-graph-sync 只收 Edit/Bash 不收 Read——三處各加一小段,同帳同慣例
  KEY:第二段候選=必答落在 pre-commit 會讀的地方(LENS-ACK: <節點>=不影響,理由),先提醒只數遵守率;擋要等數字(2026-08-02 裁定:擋 standard 逼人繞);換措辭/多推不做(世界實證無效)
  KEY:姐妹題=[[Projects/派工鏡頭注入_計劃]](子代理側,裁不量成效);本案量的是行為不是成效,不牴觸
related:
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Projects/主動影響幅度偵測_計劃]]"
  - "[[Projects/指令索引與情境測試_計劃]]"
  - "[[Projects/收斂閘漏項敏感度v2_計劃]]"
  - "[[Systems/retrieval-ranking]]"
decisions:
  - content: 開案:第一段只量不加義務——impact-hook 記推送、Stop hook 對帳印一行、usage-log 多兩種事件;兩週後拿命中率裁第二段(必答/不做)
    id: d1
    context: Enzo 提「推到眼前不等於利用到」;同日派工鏡頭注入案裁子代理側不量成效;主 session 側今天零數字
    why_chosen: 成效量不出來、行為量得出來(碰沒碰);先量現況再建,避免同日五份計劃死在「想證明有用」的形態;三處都是既有機制各加一小段
    decided: 2026-09-03
    valid: true
---
# 主session鏡頭利用率_計劃

> 白話:主 session 動手改 code 前,hook 會把「這個檔牽連到哪些帶合約的筆記」推到眼前——但推了之後有沒有被看、被用,今天沒有任何數字,只有反例(2026-09-03 編排者自己把推到眼前的硬約束撤掉兩次)。本案★第一段只量現況、不加任何義務★:推了幾篇、動手前碰了幾篇,收工時報一行;兩週後拿數字裁第二段要不要「必答」。這跟同日的 [[Projects/派工鏡頭注入_計劃]] 是姐妹題——那邊是子代理、這邊是主 session;那邊裁「不量成效」是因為成效量不出來,這邊量的是「有沒有被碰」,是行為不是成效。

PRIOR-ART: ① 最小解層級——三塊都是既有的:`impact-hook.py`(PreToolUse Edit|Write,已把固定席推到眼前)、`docs/.usage-log.jsonl`(`context`/`show` 各記一筆 {ts,node,cmd},371 筆)、`check-graph-sync.py`(Stop hook,已解析本回合逐字稿的 Edit/Bash 動作)。本案改三處各加一小段:hook 記「推了什麼」、Stop hook 多抓 Read 並對帳、使用帳多一種事件。② 世界解過沒——「推到眼前的東西被忽略」是 2026 年 LLM judge 研究的主結論(清單在眼前仍漏六成,[[Projects/收斂閘漏項敏感度v2_計劃]] 轉引);對主 session 的處方世界只有「必答式提問」(structured elicitation)一種有量到效果,本案第二段候選就是它。③ 裁定=borrow-design,零依賴。

## 一句話

★先量「推了 N 篇、動手前碰了 M 篇」,兩週後拿數字裁要不要「必答」。★

## 「利用到」的定義(沒這個就做不了)

只認兩種看得見的證據:
1. **行為證據**:hook 在第 t 次 Edit 前推了節點集 P;同一回合裡、那次 Edit 之前,session 對 P 裡任一節點做過 `lumos context/show`(使用帳)、用 Read 工具開過那篇筆記、或 Bash 指令裡出現那篇筆記的路徑(`cat`/`sed`/`grep` 它;逐字稿)。★第三種不能少★:本 repo 的工作模式明文要 Claude 用 `cat`/`sed` 代替 Read,前掃抽最近一份逐字稿 Read 工具 0 筆——只算 Read 會量出假的零。命中率=|P∩碰過|/|P|。
2. **回答證據**(第二段才有):推的是問題,session 在固定位置留下答案(commit message 一行、或計劃筆記一行)。
「看過但沒理」量不到,誠實承認;本案量的是「碰沒碰」,不是「懂沒懂」。

## 現況(三塊,2026-09-03 開檔核過)

- `impact-hook.py`:注入 additionalContext 後只留 TTL 冷卻標記(TTL=一段時間內同檔不重推的冷卻窗,鍵是 session+檔,存在家目錄),★沒記推了哪些節點★。它推的固定席=`pinned: true` 的節點(帶硬合約或出過事故),另有 top-8 自由席(分數排序、advisory)。
- `docs/.usage-log.jsonl`:`context`/`show` 才記;Read 工具直接開筆記不會記。
- `check-graph-sync.py`(Stop):`collect_turn_actions` 只收 EDIT_TOOLS 的 file_path 與 Bash 指令,不收 Read;逐字稿範圍=本回合;既有 `extract_bash_file_paths` 已能從 Bash 指令抽檔案路徑(第三種證據直接沿用)。
- `docs/.usage-log.jsonl` 在本 repo★被 git 追蹤★(不是 gitignored;`git ls-files` 有它),每次 commit 帶著走;append-only 行級合併,多機合併不衝突。

## 第一段:量(零義務,兩週)

1. **hook 記推送**:`impact-hook.py` 每次真的注入時,把 {ts, session_id, file, pinned 節點名} 追加到 `docs/.usage-log.jsonl`,`cmd: "pushed"`(同一份帳、同一慣例;best-effort 靜默)。只記固定席,不記 top-8 自由席(自由席本來就是 advisory)。
2. **Stop hook 對帳**:`collect_turn_actions` 多收 Read 的 file_path;收工時把本回合 pushed 事件對上「Edit 之前的 Read/Bash 路徑/context/show」(Bash 路徑用既有 `extract_bash_file_paths`),印一行白話:「這回合推了 N 篇固定席、動手前碰了 M 篇(碰=開過或查過)」,並追加一筆 `cmd: "lens-tally"` {pushed, touched}。★只印不擋★。
3. **兩週後**:一支唯讀腳本讀使用帳算總命中率與分佈(`lumos gov --stats` 只讀治理帳,不讀使用帳,不能拿來算);寫成 Verification。
4. **先驗門檻(暫用,裁定時可推翻)**:命中率 ≥50% → 鏡頭已在被用,第二段不做;<20% → 推到眼前幾乎無效,第二段走「必答」;之間→再量兩週或分檔型看。

## 第二段:候選(第一段數字出來才裁,本案不預作)

- **必答落在閘會讀的地方**:commit 時每個被推過的合約節點,要嘛動了那篇筆記,要嘛 commit message 帶一行「鏡頭確認」(候選格式 `LENS-ACK: <節點>=不影響,<一句理由>`,LENS-ACK 是本案新造的標記名,只是候選);pre-commit ★先只提醒、只數遵守率★,不擋。
- **擋**:2026-08-02 裁定在前(擋 standard 逼人繞、擋 high 抓不到 standard),沒有第一段+提醒期的數字不開這條。
- ★不做★:改 hook 措辭、加粗、重複推——世界實證「換措辭/多推」無效。

## 誠實界線

- 量的是「碰沒碰」,不是「用沒用」;Read 之後有沒有讀懂、有沒有據此改決策,量不到。
- 逐字稿只到本回合;跨回合早就讀過的節點會被算成「沒碰」(假陰性),命中率是下限。
- 使用帳是 best-effort 寫入(寫失敗靜默);本 repo 追蹤它、多機 append 會合併,但 hook 沒裝的機器不會有 pushed 事件。
- REVISIT:2026-09-17 第一段兩週到期,算數字、寫 Verification、裁第二段。
- 若兩週內 impact-hook 的推送次數 <30,樣本太小不裁,再延兩週。

## 實務隱患

- **self-governance**:改的是治理流程的觀測層。緩解=零義務、只印不擋、帳 append-only。
- **效能**:hook 多寫一行 jsonl;Stop hook 多解析 Read 條目;都是 O(回合大小)。
- **併發**:多 session 同時 append 同一份 jsonl——同既有 usage-log 慣例(單行 append,行級原子)。
- **回滾**:刪三段小改+帳裡兩種事件不影響任何閘;無持久狀態要清。
- **安全**:帳裡多記節點名(圖譜內部名),不含 diff 內容;無新注入面(本案不改任何注入文字)。
- ★沒有機械守衛的部分★:hook 沒真的 fire(專案未裝)就沒資料——REVISIT 那條會看樣本數。
