# edit面查詢品質閘 r1 編排者對帳報告(carrier)

四席(3 sonnet+Gemini 外家)去重 14 條全折(原評 max=blocker),1 條證偽出局。逐條處置與錨定引句(逐字取自 r1-snapshot.md):

**f1 閘作用域未明(blocker→折)**
引句：「impact ranked 融合塊(`query = (_payload.get("query") or "")` 之後、lex 計算之前)加 `_impact_query_junk(query)` 判準」
處置=S2 明文:只覆寫 lex 局部 query;事故探針 _delta_q 刻意不受閘,升格刻意不做條款。

**f2 shebang 前綴過寬誤殺新增檔案(major)**
引句：「`q.startswith("#!")` 或 `len(q) < MINLEN(預設 20)` → True」
處置=判準改「剝 shebang 首行後量壓縮殘餘」。

**f3 「僅 shebang 型觸發」被金標反證(major)**
引句：「考卷 train/held 16 案實測僅 shebang 型觸發;若未來出現真實短敘述誤傷」
處置=改「低資訊觸發族」如實列 E01/E15;案例數修 20。

**f4 gated 未初始化 NameError(major)**
引句：「`if _impact_query_junk(query): query = ""; gated=True`」
處置=S2 偽代碼補 gated=False 先行。

**f5 --diff 聚合丟棄觀測欄(major)**
引句：「`--diff` 聚合(query=hunk)與 hook 路徑(stdin payload)經同一塊,自然生效」
處置=S3 明文 per_file_meta 轉發+人讀加註。

**f6 stderr 被「人讀輸出」措辭鎖死(major)**
引句：「人讀輸出加一行 stderr 註記 `(query 品質閘:文本為檔頭雜訊/過短,L 臂靜默)`」
處置=改「觸發恆印不分 as_json」。

**f7 非字串 query 防呆缺(major)**
引句：「`_impact_query_junk(query: str) -> bool`」
處置=S1 第 1 步 isinstance 防呆。

**f8 驗收缺敗訴出口(major)**
引句：「考卷:重跑 held(釘 9fcb761)hook P@8 ≥0.70、train 不倒退」
處置=S4 ship 條件(淨提升∧無單案倒退>0.05)+旋鈕歸零出貨路徑。

**f9 稀疏空白繞過(minor)**
引句：「delta 文本為垃圾(首非空字元 `#!` 或去空白後 <20 字)」
處置=壓縮全空白量長度。

**f10 原生空 query 誤標 gated(minor)**
引句：「空字串本就走空查詢路徑,判 True 無害(冪等)」
處置=`if query and …` 不進判準不標欄。

**f11 incidents-only 白跑判準(minor)**
引句：「impact ranked 融合塊(`query = (_payload.get("query") or "")` 之後、lex 計算之前)加 `_impact_query_junk(query)` 判準」
處置=落點移入 `if not incidents_only:` 之內。

**f12 旋鈕負/NaN/Inf 語意不連續(minor)**
引句：「★0=整閘停用含 shebang 分支★」
處置=<=0/非有限一律停用。

**f13 空字串句與逃生門句衝突(minor)**
引句：「★MINLEN=0 → 直接 return False(整閘停用,含 shebang 分支——逃生門恆真)★」
處置=措辭重寫,空 query 不進判準。

**f14 stderr 自動鏈無人讀(minor)**
引句：「stderr 註記不進 stdout JSON。」
處置=誠實定位句:JSON 欄為主承載,stderr 僅互動式輔助。

**證偽出局(1)**:「diff 標頭使長度分支永不觸發」——謂詞席實測:標頭天生被 `l[:1] in "+-"` 濾掉,20 字邊界可觸發。

地基複驗:空查詢語意(lex 全 0/direct 基分/hop≥2 退場)、兩路徑共用融合塊、三消費端 .get() 相容——pre-flight+整合席逐行為真。
