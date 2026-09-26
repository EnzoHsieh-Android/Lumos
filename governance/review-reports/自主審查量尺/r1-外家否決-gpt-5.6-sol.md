severity: blocker

## F1 三本帳沒有共同鍵，核心逃逸歸因無法實作
severity: blocker
blocking: 是；照字面實作無法可靠地把逃逸、審查分級與實際放行提交接成同一筆，第一把量尺的分類與分母都會錯。
引句:「同一個缺陷佐證(提交編號、CI 執行編號)只算一次,歸給最早放行、改動範圍碰到它的那個迴圈」
file: `scripts/lumos:8005` 代碼審產生逃逸時會把 `code-` 前綴剝掉，逃逸帳寫計劃 slug；分級卻留在 `.canary-log` 的 `code-<slug>` 迴圈。
file: `scripts/lumos:28320` code-loop 通過事件只帶 `branch/head_sha`，沒有 canary `loop` 或計劃欄位。
file: `docs/.escape-log.jsonl:15` 同一個 CI SHA 696709b 被寫到四個計劃；帳內沒有各迴圈的實作提交範圍，無法判定哪個「最早放行且範圍碰到缺陷」。
例如 `code-收工點名問版本控制` 的 high 分級、escape 的 `收工點名問版本控制`、code-loop passed 的 branch/head_sha 三者只能靠命名或自由文字猜接；歷史手寫列又可能直接以 `code-` 開頭。S1 需要先定義並落盤共同的 review/plan/commit ID，否則歸因結果不可重算。

## F2 分子是缺陷數、分母是迴圈數，Wilson 比例可超過一
severity: major
blocking: 是；照 spec 計算會產生超過 100% 的「逃逸率」，Wilson 區間甚至無合法輸入。
引句:「每類印:放行數、逃逸數、逃逸率、95% 信賴區間(比例的 Wilson 區間)、下一站接住數、歸因不明數」
同一個放行迴圈可以有多個不同缺陷；例如一個類別只有 1 個放行迴圈、後來記到 2 個不同逃逸，字面公式得到 2/1=200%。Wilson 區間要求每個分母單位只有成功/失敗一次。要嘛把分子改成「至少有一筆逃逸的放行迴圈數」，要嘛保留缺陷事件數但改稱事件率並使用相符的區間模型。

## F3 「下一站接住」依自由字串判斷，沒有可執行分類規則
severity: major
blocking: 是；同一筆逃逸可因實作者自行解讀站名而被算進逃逸或排除，S2 無法產生唯一答案。
引句:「若逃逸帳的站名表示是下一站審查接住的,則它應列在」
file: `scripts/lumos:30816` `--stage` 明定為自由字串，沒有列舉或 stage 次序。
file: `docs/.escape-log.jsonl:2` 現帳已有 `消費專案真推送(pos-ios)` 等非標準站名。
必須定義「被審站→發現站」的結構欄位或封閉映射；只看 `stage=="code-loop"` 也不夠，因為它對設計審是下一站，對代碼審本身則不是同一語意。

## F4 「指令跑紅」不是缺陷確認 oracle
severity: major
blocking: 是；照字面執行會把既有紅燈、環境故障或必敗指令當成確認缺陷，污染逃逸帳與所有後續統計。
引句:「每條發現要附一個能讓問題現形的做法(會紅的測試或指令),由編排者機械地跑一次」
例如抽查者交付 `python3 -c 'raise SystemExit(1)'`，或指定在父提交本來就紅的測試，編排者都會觀察到非零退出並記成確認。設計沒有規定在哪個提交/隔離環境執行，也沒有要求父版綠、被抽版紅或修正版轉綠的對照。S7 只擋「跑不出問題」，擋不住無鑑別力的紅燈。

## F5 現有處置帳無法計算盲席與配對席各自折入及單邊發現
severity: major
blocking: 是；即使新增 blind/pair 標籤，S12 要求的三個比較量仍算不出來。
引句:「累積 12 對之後比較:兩邊各抓到幾條、其中幾條被折(確認是真的)、有幾條只有其中一邊抓到」
file: `scripts/lumos:7653` `findings_set/folded_set/accepted_set` 是全輪載體的處置集合，不是每席各自的集合。
file: `scripts/lumos:7891` 非載體席只保留報告及 `reported` 數；沒有「此席的 finding 對應全輪哪個 canonical defect」的結構欄。
兩席可能用不同 ID 描述同一缺陷，也可能各報一半重疊內容。spec 必須定義 canonical finding ID、逐席 capture 關係與處置歸屬；只加「盲審、配對席」兩欄會把重複缺陷算成「只有一邊抓到」。

## F6 每週上限的判斷與追加沒有原子交易
severity: major
blocking: 是；兩個會談同時看到本週已有 2 筆時都會排第 3 筆，實際得到 4 筆，直接違反 S9。
引句:「每週 3 個的上限要在同一週被兩個會談同時抽中時也守得住」
file: `scripts/lumos:8017` 既有 `_jsonl_append_verified` 只做 append 與讀回自驗，沒有包住「先數再寫」。
file: `scripts/lumos:9340` 現有逃逸去重已明載正確模式：讀取、判斷、append 必須整段放在同一把 `_vault_write_lock`。
「以帳上已記筆數判」不能解決 TOCTOU；抽查帳需要在同一把跨程序鎖內完成週界線計算、容量判斷、延期入列與 append，並定義週的時區及延期佇列順序。

## F7 私有 repo 外送只有散文預設，沒有設定鍵與驗收條款
severity: major
blocking: 是；實作者漏做或預設值反轉時，消費專案私有程式碼會被送往外部服務。
引句:「預設只在本 repo 抽查,消費專案要自己在專案設定明寫打開」
file: `.lumos/config.json:1` 現有設定沒有抽查、外送或 opt-in 欄位。
S1–S12 沒有任何條款驗證「消費專案缺設定時不派外家席」、壞設定 fail-closed、或本 repo 的辨識方式。這是對外資料揭露邊界，不能只靠實務隱患段的散文承諾。

## F8 逃逸帳不可撤，但 spec 宣稱可人工撤回
severity: major
blocking: 是；抽查誤確認一旦入帳，統計會永久把它當真缺陷，回退說法無法執行。
引句:「抽查確認的缺陷寫進逃逸帳是追加一列、可以人工標註撤回;盲審席的記帳跟一般席相同」
file: `scripts/lumos:9406` 逃逸帳的既有合約是 append-only。
file: `scripts/lumos:7397` 讀側會回傳所有合法列，沒有 `retracted/status/supersedes` 排除語意。
spec 沒定義撤回事件 schema、誰能撤、統計如何抵銷原列，也沒有條款測試。人工再加一列若仍按「逃逸筆數」計數，反而會多算一次。

## F9 「已推上遠端」不是現有通過留痕能證明的母體
severity: major
blocking: 是；抽樣會混入只在本機通過但未推送、後來又改版或永遠未發布的提交。
引句:「母體:已推上遠端、有代碼審通過留痕的提交,加上風險低計劃直接放行的提交」
file: `scripts/lumos:29835` `code-loop pass` 在本機當下立即寫入通過事件，發生在 push 之前。
file: `scripts/lumos:29842` 留痕只保證綁目前 HEAD；沒有遠端名稱、push 成功事件或遠端可達性快照。
以今天的 remote refs 回查也無法還原已刪分支的歷史狀態。母體需要持久的 push-success/remote/sha 留痕，或把宣稱收窄成「有通過留痕的本機提交」。

實務隱患逐類：統計與量測有效性見 F1–F5、F9；併發見 F6；對外送出見 F7；不可逆見 F8。金流無：所有既定動作只讀本地帳本或派審，未碰付款。效能無：指令定位為手動或週報路徑，不進提交/推送閘，現有帳量不足以構成 blocking 場景。守衛面無新增破壞：設計未改 `loop status --disposal` 的合取或退出碼，盲席發現仍走既有處置閘。

已看,無: 一句話、動機、成本、誠實界線與回退其餘敘述；S3–S5、S8、S10–S11 單看條款語意無額外洞；所有文件內本地路徑與 wikilink 目標存在，intake 已修的分級缺值、696709b 次數及風險低提交無放行紀錄未重報；PRIOR-ART 的 [Meta RADAR 論文](https://arxiv.org/abs/2605.30208)與 [openedclaude EP07 索引](https://github.com/openedclaude/claude-reviews-claude/blob/main/architecture/00-overview.md)可定位。對照節點 `Systems/loop-convergence-recording` 宣稱的 append 序、kind/severity 與 disposal 判定本身不受新增唯讀統計及選填盲席欄位影響；真正衝突是 F8 對 append-only 逃逸帳的可撤回宣稱。

最嚴重 severity: blocker，blocking 共 9 條。
