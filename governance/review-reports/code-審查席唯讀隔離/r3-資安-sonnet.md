severity: minor

範圍說明:已先讀計劃的「誠實界線」(Bash 是完整 shell、repo 內改檔不擋不報、網路外洩不擋、有心繞不防),下列不當新洞報。本席只讀碼推演,未在 /tmp 複本跑實驗,所以三條都標推論。

逐類:
1. 不可信輸入流到危險操作:已看。路徑一律取真實路徑(跟連結、拒 . / .. / 空段)再比對;Grep/Glob 範圍判定、標記三段驗證、型別檢查皆到位,無可直接利用的洞。外掛不跑外部指令、不反序列化(只讀 $.state 並驗形狀)。
2. 權限邊界:已看。白名單未被放寬(MultiEdit、Skill 等仍擋);寫檔限工作資料夾;子代理型別與 isolation 有擋。僅下列縱深類(F1、F2、F3)。
3. 密鑰與個資進 log:已看,無。擋下訊息與 toast 只含使用者自己的路徑片段(截 200 字)與子代理編號;事件帳新增欄位只有 agent_type、model、child、denied。
4. 加密與隨機數:已看,無。
5. 執行邊界:已看,無新增。lumos-guard 只是加進既有的 user 範圍外掛清單,來源仍走 _lumos_src(),安裝/移除流程沿用既有逐支邏輯;外掛 TS 載入位置與 ledger、context 相同,沒有新的「執行不可信位置檔案」路徑。teardown 只改提示字串。
6. 行動端:無。新依賴:無(tsconfig 只 extends 外掛自帶型別檔)。

### F1 從 $.state 讀回的席位只驗型別、不驗路徑安全
severity: minor
blocking: 否 — 縱深防禦類,需要另一支外掛先改寫 state,推論未重現
誰:同一個 Claude Code 行程裡能寫 $.state 的別支外掛(程式註解自己承認「別的外掛可以掛 state 事件改寫它」)。入口:`lock` 無,入口是 state 鍵 lumos-guard/seats。送什麼:loop 或 name 欄位帶有路徑分隔或上層段落的席位物件(marker 的三段驗證在讀回路徑上被繞過)。拿到什麼:該席的 workDir 展開後跳出 /tmp/lumos-seat-work,寫檔限制被放寬到任意位置。推論:未重現,且已超出計劃「同一行程內外掛互信」的假設邊緣。
引句:「return !!o && typeof o === 'object' && ['loop', 'round', 'name', 'cwd'].every(k => typeof o[k] === 'string')」
建議方向:validSeat 對 loop、name 套同 parseMarker 的段落規則。

### F2 讀 $.state 失敗時,子代理派工與非 Bash 工具都 fail-open
severity: minor
blocking: 否 — 需引擎的 state 讀取先壞,且只影響熱重載後記憶體已空的窗口;推論
誰:被誘導的審查席。入口:外掛熱重載後模組記憶體清空、$.state 讀取丟錯的窗口。送什麼:正常的 Agent 派工(不帶標記)或 Write/Edit。拿到什麼:派工路徑 lookup 回 error 時 parent 被當成 undefined,子代理沒有標記就不被視為審查席,等於逃出白名單;工具路徑只有 Bash 會被擋,Write/Edit 放行,寫檔限制失效。計劃已寫「Bash 寧可擋」,但沒有涵蓋這兩條。推論:未重現。
引句:「const parent = found === 'error' ? undefined : found」
建議方向:lookup 出錯時派工路徑改為擋(或沿用已知的 parentAgentId 當席位),Write/Edit 也比照 Bash 擋。

### F3 工作資料夾比對折疊大小寫,在區分大小寫的檔案系統上不同席位會共用資料夾
severity: minor
blocking: 否 — 只讓同輪席位互相寫到對方工作資料夾,內容不進 repo,計劃已承認別席工作資料夾可讀;推論
誰:同一輪、席名只差大小寫的兩席(Linux 等區分大小寫的系統)。入口:Write/Edit 的 file_path。送什麼:指向另一席大小寫不同的工作資料夾的路徑。拿到什麼:能往另一席的工作資料夾放檔(例如放進它之後會讀的臨時腳本或資料),破壞席間獨立。推論:macOS 預設不區分大小寫不受影響;未重現。
引句:「return fold(`${root}/lumos-seat-work/${seat.loop}/${seat.name}`)」
建議方向:比對工作資料夾時只對暫存根折疊,loop 與 name 逐字比。

總結:最嚴重 minor,blocking 0 條
