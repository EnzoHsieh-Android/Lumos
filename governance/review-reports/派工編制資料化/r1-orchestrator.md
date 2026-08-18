# 派工編制資料化 r1 編排者對帳報告(carrier)

四席(3 sonnet 分鏡頭+Gemini Flash 外家席,單發 REST)findings 去重 13 條,blocker×2/major×8/minor×3,**全折零放行**。兩條 blocker 均有可執行證據(s3 CLI 實測重現/s2 spec 文本自證+真帳對照),走機械證實通道免辯方;其餘 major 均為 spec 內部未定義行為,文本自證直接折。逐條處置與錨定引句(逐字取自 r1-snapshot.md):

## blocker(2,全折)

**f1 external 聚合零命中判準對「一席兼兩角」失明**(s2;正中立案動機事故③)
引句：「應派 external 席在實派 auditor 中零命中」
處置=folded:判準重訂為逐席分桶計數(required∪required-fail-closed 按 family 分桶逐桶比)+同名 auditor 佔多 external 席的兼任警示。

**f2 code/standard 列與既有 tier↔格式守衛正面衝突**(s3,CLI 實測重現:loop next 輸出自相矛盾+下輪 rc2;全庫零筆 code loop 錨定過 standard)
引句：「mode=single/sequential 條目(design/light、code/standard)佔 W 席數必須=1」
處置=folded:code/standard 列剔出 v1 編制表、範圍刀明文上游守衛缺陷另案;防雙真相段同步簡化。

## major(8,全折)

**f3 seat_shortfall 計數對象未定義(佔 W vs 總席)**(s4/g1+s2f3 合流)
引句：「`seat_shortfall`:實派席數 < 應派 required 席數。」
處置=folded:計數桶明文定義(required∪required-fail-closed 全數入桶,含不佔 W)。

**f4 conditional 席使 shortfall 分母不定**(s4/g2)
引句：「條件真值工具不可判,只印條件供編排者對」
處置=folded:conditional 明文不入任何機械計數桶。

**f5 unknown 分類與 external_missing 判準矛盾產生假警報**(s1f3+s4/g3 兩席獨立)
引句：「野字串→unknown 列出不判定(不誤喊 external_missing 的前提=分類 fail-open)」
處置=folded:unknown 桶非空→措辭降級「可能缺(另有 N 席家族無法辨識)」,不下定論。

**f6 --roster 觀測段會被既有互斥分支 early-return 吃掉**(s1,行號實證,編排者自核屬實)
引句：「帶 `--roster` 且帶 `--repo` 時啟用;逐輪掃 `governance/review-reports/」
處置=folded:落點明文=cmd_loop_status 入口、任何分支之前,四模式皆吃得到;測試補四模式各一案。

**f7 code/light 查表 miss 未定義行為**(s1)
引句：「以 (loop_kind, tier) 為鍵;loop_kind 由 loop id 前綴判」
處置=folded:查表 miss→fail-open 明講「無編制宣告,跳過」;loop next roster=null。

**f8 kind 前綴二值規則對歷史非慣例 id 載錯表噴無意義警告**(s4/g5)
引句：「code- 含連字號開頭=code,其餘=design」
處置=folded:升級三值——code 開頭無連字號=indeterminate,印「kind 無法判定,跳過對帳」。

**f9 requirement 值帶參數字串使比對落空**(s2f2)
引句：「| code/standard(sequential) | 單 reviewer×1(claude,required) | 外家否決×1(external,note-if-absent:standard 退同門+留痕) |」
處置=folded:requirement 恆四枚舉裸值、說明文字移 note 選配欄;該列本身隨 f2 剔除。

**f10 sequential 模式兩席吐法未定義**(s4/g4)
引句：「mode=single/sequential 條目(design/light、code/standard)佔 W 席數必」
處置=folded:隨 f2 剔除 sequential 條目,v1 mode 只剩 panel/single,無此歧義面。

## minor(3,全折)

**f11 雙家族關鍵字同時命中判序未定義**(s2f4)
引句：「codex`/`gemini`/`qwen`/`gpt`→external;`sonnet`/`opus`/`haiku」
處置=folded:判序寫死 external 表先比、先命中先贏,雙命中附 note。

**f12 合法 JSON 不符三形狀的處置兩讀法方向相反**(s2f5)
引句：「取不到 auditor 的元素計 unknown,壞損 JSON 印警告跳過該檔」
處置=folded:與壞損 JSON 同一處置(跳過不計),測試兩子案例各釘。

**f13 required-fail-closed 在 advisory 下語意矛盾**(s4/g6)
引句：「required-fail-closed(缺=喊 missing+提示 fail-closed 紀律)」
處置=folded:明文「觀測只轉述紀律措辭,不執行阻斷,advisory 本質不變」。

## 收貨三道紀錄

- quote-check:s1/s2/s3 全數錨定;s4(Gemini)12 條中 8 條格式病(全形冒號/省略號/表格列縮寫),機械正規化為快照逐字原文後全數錨定——內容一字未改,僅引句格式修復。
- refcheck:四席 0 missing/0 out_of_range(s3 引 docs/.canary-log.jsonl 實在)。
- seat-check:s1/s3 各 1 筆 unreported(報告內未貼快照路徑字串,協議格式面,非實質未讀——引句錨定已證讀過);out_of_scope 0(s4 正規化前 2 筆,正規化後 0)。

## 折入後衛生

散落漂移機械掃(sequential/零命中/code/standard/前綴 關鍵詞全文 grep)=殘留全在「已剔除/已訂正」敘述脈絡,無活規則變體。折入迷你核對 7 命中(訊息文字不一致×2、測試缺案×5)全修,記審計修正紀錄。fold-check 無 flag。
