# code r1 合約圖譜席(spec 逐條核驗;patch 與 main 現檔逐字元比對一致)

**G-1**|major|blocking:否
引句(spec):「有 `--spec` → **計劃節點檔名優先**;編號僅 fallback」
code-loop 的 --spec 慣用值=凍結 patch:Path("r1-snapshot.patch").stem → ['snapshot'] → 無訊號分支,把更有訊號的 loop_id 整個丟棄——code loop 帶 --spec 比不帶更糟。

**G-2**|minor:JSON 合約寫 query str|null,實作恆回 str,null 分支無任何路徑產生。
引句(spec):「"query": str|null, "queried": bool」
**G-3**|minor:spec 對 B 訊息只描述單筆,實作印最多 3 筆(紅釘測資實印 2 行);測試未斷筆數。
引句:「for _r, _stem, _rel in sorted(_el_near_sibs, reverse=True)[:3]:」
**G-4**|major|blocking:否(治理帳失真,牴觸「數字必機械數」)
引句(驗證筆記):「advisory 移出首輪守衛 → 2 條紅(抑噪失效)」
三支突變數字全錯:宣稱 3/4/2,實測 2/3/0。第三支 0 紅=測試第二輪呼叫落 gate-pending 而非 plant-canary,首輪守衛沒被釘。
**G-5**|major|blocking:否
引句(spec):「B 比對集必須寫檔前收集(EL-13 自比坑;紅釘已釘)」
把收集段搬到寫檔後照樣 14/14 綠——防自比的是 env.notes 啟動快照這個結構性事實,非程式碼順序;「已釘」過度宣稱。
**G-6**|minor:spec 三例具名切詞測資(intake-guard/圖譜進迴圈入口栓/auto-2026-08-23)未以可重放形式進 suite;手動驗全對但無紅釘保護。

兌現清單:A 觸發/出口/切詞三步/召回不經 cmd_search/superseded 納入/三分支/五鍵白名單未擾動/B 時序與範圍與判準/fail-open 無 SystemExit 可達路徑(巧合式安全,記一筆)/d1 偏離描述與現檔一致/全套 3379x2 乾淨。

severity: major
