severity: minor

我讀了被審的設計段(第 84 到 157 行)和 `scripts/lumos` 的鄰居程式。沒有 major:沒有第二套 diff 解析、第二套時間預算、第二套來源標記掃描,也沒有跨層直呼。有 5 條 minor。

**四問回答**

1. 分層與依賴方向:對齊。
   - 新掃描函式比照 `_contract_key_matches`(`scripts/lumos:39369`),全檔一支,鏡頭渲染去呼叫它。這和現況一致:合約行掃描也是 `_lens_contract_rows`(`scripts/lumos:39394`)呼叫它。
   - 改動行收集從 pitfalls 的 diff 迴圈抽成共用函式。現況是迴圈內聯收集,並以 `_stack_changed_ok`(`scripts/lumos:35692`)過濾(`scripts/lumos:35914`、`scripts/lumos:35923`)。抽出共用符合 `_stack_changed_ok` 注解寫的「別再各抄一份」原則。
   - 渲染共用 `_lens_render_listed`(`scripts/lumos:40007`),也對。
   - 第一項讀「FACT/FLOW/DEP 且帶外部來源標記」的行,沿用 `_CTX_SOURCE_RE`(`scripts/lumos:3373`)和 `_NOTE_SHAPE_PREFIX_RULES`(`scripts/lumos:3366`)那三種前綴。
2. 命名與錯誤處理:有 3 條 minor,見 finding 1、2、4。
3. 第二種做法:沒有 major。時間預算沿用 `_t0`、`_LENS_INNER_BUDGET`、`_LENS_FALLBACK_RESERVE`,與備援段一致(`scripts/lumos:40350`、`scripts/lumos:39473`)。逐篇讀檔夾剩餘秒數,現有的 `_lens_git(..., timeout=)` 參數(`scripts/lumos:39244`)本來就支援。「不寫快取」的做法有 1 條 minor,見 finding 3。
4. 落點:有 1 條 minor,見 finding 5。
   - 新開「派工鏡頭」節點合理。現有節點只是順帶提到鏡頭,沒有專管的家:`規格閘.md`、`棧別提問表態閘.md`、`每支檔有家.md` 等。
   - 「棧別提問表態閘」管題目表,放題目 id 總數與清單合適,`scripts/lumos:23394` 附近的題目表就在它的範圍。

**Findings**

**1. 新旗標沒有名字,也沒說要改哪幾處消費者**

severity: minor
blocking: 否
引句:「另在題目規格加一個旗標,讓這題:①不參與「某棧改動超過行數門檻就整組適用」的規則」
- 鄰居旗標叫 `needs_backing`:snake_case、布林、只在 `True` 時寫、缺省即假(`scripts/lumos:23415`、`scripts/lumos:23437`),消費處用 `spec.get("needs_backing")`(`scripts/lumos:14723`)。
- 設計該先定名。名字要說明「只看形狀、不吃行數門檻整組適用、不進舊語意清單」,別用會和 `needs_backing` 混淆的字。
- 設計也該列出要過濾的三處:`_STACK_PERF_QUESTIONS` 派生式(`scripts/lumos:23547`)、`_stack_applicability` 的 `over` 分支(`scripts/lumos:23897`)、`stack_questions` 取用處(`scripts/lumos:35945`、`scripts/lumos:38679`)。
- 同一個旗標管兩種語意,本身不算問題。

**2. 「共用形狀常數」和題目表的觸發欄格式對不上 ⚠**

severity: minor
blocking: 否
引句:「形狀定義成一組編譯好的正規式常數,放在題目表旁」
- 鄰居的題目表 `when` 和 `when_raw` 存的是字串清單,載入時才由 `_STACK_TRIGGERS` 以 `re.I` 編譯(`scripts/lumos:23551`)。
- 設計說放「編譯好的」常數,但題目表只收字串,兩邊要接起來,得先講清楚是哪一邊遷就哪一邊。
- A、C 組是「引號數字比較,且同行出現名稱片段」兩條件併用。`_stack_applicability`(`scripts/lumos:23884`)對每個 pattern 是獨立的「任一命中」,表達不了併用。
- 「單行超過 2000 字不比對」在 `_stack_applicability` 路徑也沒有對應步驟。
- 若實作時為此另寫一個判斷函式繞過題目表,就會變成第二套觸發路徑。建議設計先寫明:併用條件用單一 regex(先行斷言)還是多一道前置過濾,以及 2000 字門檻放在 `_stack_norm_line` 還是另處。
- 我判不準會不會走到第二套觸發路徑,所以標 ⚠。

**3. 「因時間不寫快取」是新的快取分支,沒說明和現況的關係**

severity: minor
blocking: 否
引句:「因時間停止時印一行「外部碼表補選因時間上限中止」,而且這次結果不寫進快取」
- 現況只有一個寫入點:`no_cache` 或環境變數為真才不寫,其餘一律寫(`scripts/lumos:40377`)。
- 現況備援段超時(`skipped-timeout`)的結果照樣寫進快取。
- 設計要新增「補選逾時就不寫快取」,但沒說明為何補選要和備援段規則不同。
- 設計也沒說明要在現有寫入點加一個條件,還是另開寫入路徑。
- 建議:標在同一個寫入點的條件上,並回頭決定備援段超時是否也該不寫。否則同一支鏡頭有兩種「超時是否快取」的做法。

**4. 新段落標題與狀態欄位沒有按鄰居的常數與命名慣例**

severity: minor
blocking: 否
引句:「段落標題固定寫「外部事實(筆記抄錄的官方或第三方來源,可能過期;有疑問查 [查:] 欄的原文)」」
- 鄰居的固定標題都是具名常數:`_LENS_HEADER`、`_LENS_FB_HEADER`、`_LENS_FB_FOOT`、`_LENS_FOOT_OK`(`scripts/lumos:39392`、`scripts/lumos:40370` 附近)。設計沒有給「外部事實」「外部碼表」兩個標題的常數名。
- 補選的狀態沒有對應 `fallback_status` 的輸出欄位(`scripts/lumos:40373`)。測試要斷言「補選因時間中止」時,缺少具名的狀態欄,只能比對文字。
- 建議照鄰居慣例補上 `_LENS_EXT_HEADER` 這類常數與一個 status 欄位。

**5. 非效能題放進效能檢核目錄 ⚠**

severity: minor
blocking: 否
引句:「`Systems/效能檢核目錄`(各棧題數那串數字;extcode 不是效能題,在目錄裡註明它住在題目表但不屬效能檢核)」
- 效能檢核目錄的定位是各平台「效能」問題的權威菜單。
- 題目表(`_STACK_QUESTION_SPECS`)在表態閘的範圍。extcode 題的總數與清單已經在「Systems/棧別提問表態閘」,再到效能目錄加一條「不屬效能」的註記,等於在一個效能目錄裡反向放例外說明。
- 比較自然的做法是:只動表態閘節點,效能目錄只在「各棧題數」數字確實因這八題而變時改數字。
- 這和 `Issues/架構對齊席與棧別檢核題可能相反` 提過的題目歸屬問題同源。
- 「目錄的題數會不會受影響」要看實作,我判不準,所以標 ⚠。
- 此外,表態閘節點現況「沒寫負責範圍」(`lumos new system --responsibility`),新題上線時順手補上較合規。

不對齊共 5 條,其中 major 0 條