# r1 正確性席(這份設計會出錯的假設者)

**F-1(裁 F-A:觸發時機與輸出形態)** — severity: major|blocking: 是(判準:兩句規格照字面互斥,不裁定無法動工)|spec 段落:提案A + PRIOR-ART
引句:「觸發:每次 `loop next`(文字模式印;--json 加 `related_nodes` 鍵)」/「比照 `record_cmd`/`scope_cap` 的 advisory 段」
佐證:scripts/lumos:5848,5879(兩鍵只在 plant-canary 分支組裝)、:5911(文字模式=五鍵單行白名單)、:5890-5894(cluster_hint 明文只在 N=1 印,註解直指逐輪重印=「噴無效噪音」)。
裁定:① 觸發收成 round 1(n_next==1;帳齡零必走 plant-canary,與事故時點「開迴圈」一致);② 文字模式開專屬多行段比照 roster 的輸出迴圈(:5905),不得塞進五鍵白名單;③ --json 把 related_nodes 放進 out;④ in-process 呼叫 cmd_search 必須 redirect stdout/stderr(同函式 :5927 對 cmd_loop_status 已有前例),不 redirect 則 --json 出現兩行 JSON;禁止另寫一份召回邏輯(:2085 「兩份實作分岔」事故)。

**F-2(裁 F-B:CJK 切詞規格)** — severity: major|blocking: 是(判準:spec 自訂的放行條件「切詞規則進 spec 且測試各給一例」未滿足)
引句:「切詞規則進 spec 且測試各給一例」
佐證:scripts/lumos:1871(_rank_tokenize:CJK 連續段→字元 bigram;全 repo 唯一 CJK 切詞實作)、:2138,2176(多詞回退)。
可實作規格:nfc().lower() 後重用 _rank_tokenize(不得另寫第二份),濾純數字 token 與長度 1 的 ASCII token、去重、空白 join 丟 cmd_search。實測:`search "圖譜 譜進 進迴 迴圈 圈入 入口 口栓"` 與人工斷詞 `"圖譜 迴圈 入口"` top-5 完全相同(垃圾 bigram 各僅 1 命中、高 IDF 反而精準)。測試例三枚:intake-guard→intake guard;圖譜進迴圈入口栓→bigram 串;auto-2026-08-23→auto(數字必濾:「2026」實測覆蓋 381/385 篇=全庫召回)。

**F-3(A 的查詢源在主要消費端上必產垃圾)** — severity: major|blocking: 是(判準:--json 首要消費端「自主迴圈」在現行編號慣例下必收零主題訊號結果)
引句:「查詢詞=迴圈編號去 `code-`/`-std`/`-v2` 等前後綴、按連字號與 CJK 切詞」
佐證:docs/.canary-log.jsonl(139 個真實 loop id 含 auto-2026-08-23…30 八枚日更編號)、scripts/lumos:16573(--spec 旗標已在 next 介面)。
auto-YYYY-MM-DD 清洗後只剩 auto(實測命中 68 篇、零主題相關),印 5 筆似是而非比 0 筆更毒(546 前例=雜訊教會人忽略)。修法:有 --spec 時以計劃節點檔名為查詢詞優先、編號僅 fallback;清洗後 token ≤1 且無 CJK 段→誠實印「編號無主題訊號,未查」。開放列舉前後綴黑名單由機械規則(濾純數字+單字 ASCII)取代。

**F-4(B 在 Verification 型別上必成背景噪音)** — severity: major|blocking: 是(判準:建檔最頻繁型別上線首日即高頻誤鳴;修法一行)
引句:「相似門檻收在檔名級,誤報成本=多讀一行」
佐證:vault 全量實測(Verification/ 156/385 篇):既有檔名 81% 有 ≥0.6 鄰居;模擬建兩個全新無關名各命中 12/3 個既有名,top 命中全靠「2026-08-xx_」前綴+「落地/驗證」通用尾詞。
修法:B 限 project/system/issue 三型,或比對前剝 YYYY-MM-DD_ 前綴。Projects 的 top pair 幾乎全是合法 計劃/實作計畫 變體,advisory 提醒先讀計劃反而是 feature。

**F-5(「同詞幹」未定義,照字面不可實作)** — severity: major|blocking: 是
引句:「檔名 difflib 比對 ≥0.6 或 search 前 2 名帶同詞幹」
佐證:全 repo 無 stemmer(grep 詞幹 0 命中)。
機械替代:用 _rank_score_candidates(:1953)的 hits 覆蓋判準;或刪掉此子句只留 difflib(單判準已可承載 advisory)。

**F-6(A 的誠實分支掛錯條件)** — severity: minor|blocking: 否
引句:「零命中印一行「圖譜這主題無既有節點」(誠實,不靜默)」
佐證:CJK bigram 經 OR 回退幾乎不可能 0 候選(「圖譜」命中 166 篇),0 筆分支對 CJK 編號實務永不觸發。
誠實行改掛:逐詞覆蓋全 ★0★ 或 top1 分數低於門檻。

已驗證站得住:cmd_new 完全同名會擋(:9581-9605);掛點 :9604→:9607 真實;多詞回退 :2138-2183;_search_index 0 出現;385 篇實數;--json 旗標 :16572;三個 [[]] 目標存在;決策數可機械數(:7225);B 同型別資料夾可實作(:9540+:2104);效能/併發/回滾「已排除」成立。

最嚴重 severity:major(無 blocker);blocking 共 5 條(F-1、F-2、F-3、F-4、F-5)。

severity: major
