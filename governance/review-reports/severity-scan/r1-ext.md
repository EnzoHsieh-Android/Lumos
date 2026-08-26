### ext-f1

severity: blocker

引句:
「報告 parse 不到任何 severity 行=提醒「格式無法機械驗」(不紅,舊報告相容)」

佐證:file: `governance/review-reports/severity-scan/r1-snapshot.md:28`

說明: 最大逃逸路徑被明文設計成不紅。只要刪掉 severity 行，原本應被判定為 blocker/major 低報的案例便從「紅」退化成提醒；而 `--disposal` 又不改 rc，因此有意低報者可穩定繞過。這使 S1 只能攔截「保留 severity 行、但帳面抄錯」的非對抗性錯誤，不能支撐「嚴重度綁定機械守衛」的定位。作為 lint 仍可能有價值，但不值得以治理守衛名義過案；至少應把新報告的無 severity 行視同失敗，舊報告相容另以時間或版本邊界處理。

### ext-f2

severity: major

引句:
「綁定驗證現況=編排者自律;人工核僅一次(0/18);disposal 閘不驗此維度」

佐證:file: `governance/review-reports/severity-scan/r1-snapshot.md:24`

說明: spec 指出的問題是「編排者自律」，但方案仍由同一治理流程讀取其保存的報告，再核對其寫入的帳列；沒有獨立產生者、不可省略的結構化輸出，或不同權限邊界。若威脅是疏忽，掃描確實能抓轉錄錯誤；若威脅是有意低報，同一編排者可同時調整報告文字與帳面值，使兩者一致而通過。故「自我對帳沒有任何價值」的否決不成立，但把它當作對抗有意低報的控制則威脅模型不成立。

### ext-f3

severity: blocker

引句:
「邊界:不動記帳寫側、不動閘判定布林;報告格式不強制(掃不出=提醒非紅)」

佐證:file: `governance/review-reports/severity-scan/r1-snapshot.md:31`

說明: spec 主動排除了最接近資料入口、也最能封閉缺欄逃逸的控制點。應優先在 `record` 寫側要求帳列 severity 必須附報告中對應 severity 行號，並驗證該定位確實解析為合法 severity；無法提供便拒絕入帳。僅要求行號仍不足以證明它是報告最高嚴重度，所以最高值掃描可以保留為第二層校驗，但不能以 advisory 掃描取代寫側完整性約束。現案的層級選擇倒置，應退回重寫後再審。

### ext-f4

severity: major

引句:
「advisory 首版不動 rc(升級成硬閘=另案過審,本案在驗證紀錄掛回頭條件:若首驗或往後真抓到低報,硬閘案即立)」

佐證:file: `governance/review-reports/severity-scan/r1-snapshot.md:39`

說明: 升級條件只在掃描器「真抓到低報」時觸發，但有意規避者可以用缺 severity 行讓事件只成為提醒，或同步修改報告與帳面使其一致；兩種情況都不會滿足回頭條件。這形成循環盲點：最需要硬閘的逃逸，恰好不能觸發硬閘案。回頭條件至少必須納入「任何新報告無 severity 行」及「提醒累積達門檻」，否則 advisory 階段沒有可信的升級路徑。

結論：否決成立。否決的是目前「格式不強制、缺行不紅、disposal 不改 rc、寫側不動」的方案，不是否定 severity 對帳本身；合理重案應以寫側強制定位為第一層、最高 severity 對帳為第二層。
