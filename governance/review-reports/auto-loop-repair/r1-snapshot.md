---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:地基盤點第 1 批案 A——自主迴圈三症修理:①NO_JSON 中止真的丟 gap(log 說「自然重抽」是假話,08-24/25 兩筆實丟)②選題退化 FIFO(decay_and_prune 寫了沒人呼叫,153/160 筆凍在 0.5 分,靠穩定排序挑兩個月前舊題)③近三天燒 $156 落地 0 件,帳有成本欄但無產出行
  KEY:[S1] 失敗不丟件 [S2] 選題接上衰減+再現回血+同分新者先+淘汰歸檔 [S3] 死因分類落帳+連兩天管線死喊人 [S4] 七天產出一行(跑幾次/燒多少/落地幾件)
  DEP:[[Systems/autonomous-iteration-loop]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# 自主迴圈修理_計劃

> 白話:每天早上自動選一個治理缺口、寫成 spec、自審到收斂、停在放行閘等人的那條迴圈,最近三天燒了 156 美金、一件都沒落地。查下來是三個具體的洞,不是「整條迴圈爛了」——修這三個洞,不動放行閘等既有裁定。

PRIOR-ART: 全部借用,零依賴自寫幾行——「失敗的件不丟、進死信重排」是訊息佇列教科書做法(SQS/RabbitMQ 的 DLQ);「排隊太久的題目分數要動、防餓死/防殭屍」是 OS 排程器 aging;「被重複點名=價值信號、回血」是 LFU 快取;「每週一行花費對產出」是 SRE 成本儀表。沒有一樣需要新輪子。

## 現況事實(2026-08-26 實查,含收據)

1. **NO_JSON 丟件**:`gap_select.select()` 會把選中的 gap 從 backlog **拿走**(`backlog.py` `pop_top` 是 pop+存檔);orchestrator 輸出解析失敗時 `autonomous-loop.sh:254` 直接 `exit 1`,沒有任何 requeue,而且 log 訊息寫「gap 留在 backlog 下輪自然重抽」——**假話**。實查:08-24(API 529 過載)、08-25(輸出被截斷)兩天選中的 gap 都已不在 backlog,也不在 covered,就是消失了。
2. **選題退化 FIFO**:`backlog.py:28` 的 `decay_and_prune`(每天九五折、低於 0.2 淘汰)**全 repo 沒有任何生產呼叫點**(只有測試);live backlog 160 筆裡 153 筆凍在初始 0.5 分,`pop_top` 用穩定排序取最高分→同分時永遠是最早插入的贏→ 08-23 選中的是 2026-06-29 的舊題。日報重複點名一個 gap 只更新 `last_seen`,分數不動,`last_seen` 是死資料沒人讀。
3. **成本已記、產出沒帳**:08-23 起每輪成本已落 canary 帳(第一筆 08-23 15:16)(`auto-<日期>` 迴圈、--tokens/--wallclock-min 既有欄),這塊是好的。缺的是**結局**:帳上看不出這輪是收斂、未收斂、還是管線死掉;也沒有任何地方把「七天燒多少、落地幾件」放在一行給人看。近三輪:08-23 $68.7 跑滿 6 輪未收斂(正常路徑,有 requeue)、08-24 $33.9 NO_JSON(529)、08-25 $53.3 NO_JSON(輸出截斷;信封=「claude -p --output-format json」回傳的頂層 JSON(含 total_cost_usd/num_turns/duration_ms 等)——這輪信封異常:1 turn/0.1 分鐘卻報 $53,原因未查明,先當「死因待分類」記帳不建理論)。

## 條款

- **[S1] 失敗不丟件**:orchestrator 輸出解析失敗(PARSE_FAIL/NO_JSON/空)時,中止前把選中的 gap **原分數放回 backlog**(不是它的錯,不降分),另在該筆累計 `pipeline_failures` 欄;log 訊息改成真話(「gap 已放回 backlog」)。行為斷言:模擬 NO_JSON 一輪後,該 gap 仍在 backlog 且分數不變、`pipeline_failures` +1。
- **[S2] 選題修理**:①每日進場呼叫既有 `decay_and_prune`(原設計參數不動:×0.95/日、<0.2 淘汰);②日報再次點名已在 backlog 的 gap 時分數回血到初始 0.5(再現=世界重複投票),不只碰 `last_seen`;③ `pop_top` 同分時改「`last_seen` 新者優先」;④被淘汰的列**歸檔到 `governance/backlog-archive.jsonl`(新檔,本案新增;跟 live 的 `governance/backlog.jsonl` 同目錄)** 而不是靜默刪(現況 153 筆會在接上衰減後 ~17 天內大批淘汰,屬原設計意圖,但要留痕可回收)。行為斷言:兩筆同分 gap,`last_seen` 較新者先被選;跑衰減後低於 0.2 的筆出現在 archive 檔而非人間蒸發。
- **[S3] 死因分類落帳+連續失敗喊人**:成本落帳那筆的 `--note` 帶上結局分類與美元(`outcome=converged|unconverged|skipped|pipeline_fail:<死因> usd=<金額>`;canary 帳的成本欄當初刻意只收 tokens/分鐘兩欄不發明新欄,美元走 note 自由文字,不動欄位)(死因取信封 is_error 與 NO_JSON 標記帶出的 result 殘文(autonomous-loop.sh:213 那段)分類:api_error/truncated/parse_fail);連續 2 天 `pipeline_fail` → 復用既有 `line_notify` 喊人(管線連死兩天不是天氣,是要人看)。行為斷言:NO_JSON 輪的 canary 帳 note 含 `pipeline_fail:api_error` 字樣;連兩天注入失敗 fixture 觸發 LINE 呼叫(測試打樁驗參數,不真發)。
- **[S4] 七天產出一行**:每輪收尾在 autonomous.log 印一行七天彙總:「過去 7 天:跑 N 次、燒 $X、收斂 Y、放行 Z、管線死 W」,資料源=canary 帳的 `auto-*` 迴圈(tokens/分鐘走既有欄;美元與結局分類走 [S3] 落在 note 的 `usd=`/`outcome=`),不建新帳本、不發明新欄。行為斷言:給定 fixture 帳,彙總行數字與逐筆加總一致。

## 不做(邊界)

- 不加自動 retry(529 重試一次=最壞情況成本翻倍,無人看顧下不敢);止血靠 [S3] 喊人。
- 不動放行閘、N=1 閘、tier 收檔守衛、dry-run 紀律等既有裁定。
- 不查 08-25 信封異常的根因(單一樣本,先靠 [S3] 分類累積證據;連續出現再立案)。
- 不給 orchestrator 加 turn/成本上限:08-23 $69 那輪是**正常跑滿 6 輪**,上限會腰斬合法長跑;等 [S4] 產出帳累積數據再判要不要管。

## 實務隱患

- **金流/對外送出**:LINE 通知是對外送出,但復用既有 `line_notify` 傳輸層(token 環境變數傳遞,08-18 已硬化),不新增通道;測試一律打樁不真發。已排除:不碰金流。
- **正式環境不可逆**:backlog 淘汰改「歸檔」正是為了可逆;archive 檔 append-only。已排除:無不可逆操作。
- **守衛面**:本案改的就是守衛面(自主迴圈是治理守衛的一環),故走完整設計審(standard),不走 light。
- **併發/資源**:backlog.jsonl 單寫者(每天一次 launchd 串行),無併發;archive append 同。已排除。
- **相容性**:backlog 列新增 `pipeline_failures` 欄——會讀分數類欄位的路徑都用 `.get()` 容錯(`weakness` 是必有鍵、直索引,不受新欄影響),舊列無此欄照舊;covered.jsonl 格式不動。

## 驗證計劃

test_autonomous_loop.py 加測(先紅後綠):S1 失敗不丟件、S2 同分新者先+淘汰進 archive+再現回血、S3 note 分類+連兩天喊人(打樁)、S4 彙總一致。真機驗收:修完後下一次 launchd 真跑的 log 要看得到七天產出行。
