severity: major

這是 r1 的審稿,鏡頭是邊界可執行加資源併發。程式碼查證對象是 `scripts/lumos`。

## 各節

- 緣起與現況、PRIOR-ART、RETIRE-IF、REVISIT、D 七道關卡、F 示範 repo、分階段、不做、回退:已讀,無 finding。
- A 情境出題:見 F9、F10。
- B 工具能力:已讀,無 finding。
- C 證據擷取:見 F1 到 F8、F11。
- E 修復迴圈:見 F6。
- 驗收條款:見 F10、F12。
- 實務隱患:見 F2、F12。

## Findings

**F1(C「lumos evidence run」,證據列一行寫入)**
severity: major
blocking: 是
判準:證據列一超過 4KB 就整筆寫不進帳,而規格沒有定義這條路,所以會出現「跑完卻沒有證據」。
- 問題:規格說「沿用既有帳檔的追加寫法」,但既有寫法 `_ledger_append` 超過 4096 位元組就直接 `raise ValueError`,不截斷。證據列欄位有指令全文、環境、實際摘要、原始檔路徑,長指令(含 `-e` 參數的 k6 或 mvn)或長摘要很容易超過。
- 問題:`_ledger_append` 不帶 `O_CREAT`,帳檔不存在時第一列也寫不進去。證據帳是新檔,規格沒說誰建檔。
- 問題:規格沒說寫失敗時結果算什麼,是 BLOCKED 還是整個指令失敗。
- 佐證:file: `scripts/lumos:20557-20572`,4KB 上限與無 `O_CREAT` 的 `os.open`。
- 佐證:file: `scripts/lumos:1409`,另一種帶 `O_CREAT` 的寫法,規格沒說選哪種。

**F2(C「存檔前遮蔽」、S6、實務隱患「秘密」)**
severity: major
blocking: 是
判準:秘密放在 argv 時會原文寫進進版控的證據帳和事件帳,而且推出去就收不回。
- 問題:遮蔽只涵蓋「環境變數裡名字像 TOKEN/PASSWORD/SECRET/KEY 的值、連線字串裡的密碼」。證據列的「指令」欄存的是 argv 全文。像 `psql postgres://u:pw@host/db` 或 `curl -H "Authorization: Bearer xxx"` 這種形狀,規格沒說指令欄要不要遮蔽。
- 問題:規格自己要求證據帳進版控,秘密一旦進帳就進了 git 歷史。
- 問題:S6 只測「輸出或環境變數」,沒測 argv。
- 問題:規格已承認事件帳外掛不遮蔽敏感資訊,只記指令前 500 字。呼叫 `lumos evidence run -- <含秘密的指令>` 的那條 Bash 呼叫,會被事件帳整段記下,這條洩漏路徑規格沒提。
- 佐證:file: `scripts/lumos:23084`,既有 `.gitignore` 範本把本機帳忽略,證據帳反過來要進版控(見 C「證據帳要被追蹤」)。

**F3(C「lumos evidence run」,逾時、訊號、互動式、程序樹)**
severity: major
blocking: 是
判準:規格沒定義逾時值、stdin、程序樹清理、訊號中斷後的帳狀態,最壞時序下指令會卡住或留下孤兒程序。
- 問題:規格說「逾時判 BLOCKED」,但沒有 `--timeout` 旗標、預設值,也沒說 stdin 要不要接 `/dev/null`。互動式指令(例如 `psql` 不帶 `-c`)會一直等輸入。
- 問題:k6 或 Docker 起的子程序若不放進獨立 process group,逾時只殺父程序,孫程序繼續握著管線。
- 問題:對 `evidence run` 按 Ctrl-C 或收到 SIGTERM 時,可能原始檔寫了、帳沒寫,或反過來。規格沒有「中斷也要留一列 BLOCKED」的規則。
- 問題:被訊號殺掉(例如 OOM 的 SIGKILL)時 returncode 是負值。「退出碼非零」會把它算成 FAIL,算進 E 的計數,而不是 BLOCKED。
- 佐證:file: `scripts/lumos:17181-17198`,既有 `_kill_run` 用 `start_new_session=True` 加 `os.killpg`,但它不管 stdin(沒接 `/dev/null`)也不處理 SIGINT。規格沒說沿用。
- 佐證:file: `scripts/lumos:27679-27687`,同樣的 killpg 寫法在另一處。

**F4(C「lumos evidence run」,超大輸出、二進位輸出、非 UTF-8)**
severity: major
blocking: 是
判準:截斷與解碼的規則不存在,會讓原始檔無法重判,或在多位元組字元中間被切壞。
- 問題:規格只說「原始檔有大小上限,超過只存頭尾並標截斷」,沒給上限數值,也沒說 `--expect` 判準是對完整輸出還是對截斷後的檔判。若對截斷後判,中段的錯誤訊息會漏判。若對完整輸出判,就得整份讀進記憶體,GB 級壓測輸出會吃光記憶體。
- 問題:RETIRE-IF ② 自己列了「原始檔不足以重判結果」,但規格沒說重判靠什麼,也沒保證判準關鍵行能留在頭尾。
- 問題:規格說「stdout/stderr 原樣存成原始檔」,卻沒說是存位元組還是文字。二進位輸出(例如 `pg_dump -Fc`)或 Latin-1/Big5 輸出,用 utf-8 解碼會拋例外或被取代字元弄壞,「原樣」就不成立。
- 問題:遮蔽是作用在文字上,頭尾截斷若切在秘密中間,殘片不會被遮蔽。
- 佐證:file: `scripts/lumos:17173-17200`,`_kill_run` 用暫存檔接輸出並以 `errors="replace"` 讀回,上限是 `_KILL_OUT_CAP = 256 * 1024`(`scripts/lumos:17204`)。這是既有的做法,規格沒說沿用,且它的取代字元做法違反「原樣」。

**F5(C「證據編號」、「原始檔位置」,兩程序同時寫)**
severity: major
blocking: 是
判準:證據編號與原始檔名的產生方式沒定義,兩個程序同秒跑同條款會撞名或編號重複。
- 問題:證據列有「證據編號」和「原始檔位置」,規格沒說怎麼產生。若用「讀帳取最大加一」,兩程序會拿到同一個號碼。若用條款加時間戳當檔名,同一秒同一條款的兩次執行會互相覆蓋原始檔。
- 問題:實務隱患節要求 S5 測試涵蓋兩程序同時寫,但 S5 的條款文字和測試名都沒提併發,條款與隱患節對不上。
- 佐證:file: `scripts/lumos:20578-20590`,既有 `rel_cascade_create` 用 `O_CREAT|O_EXCL` 加序號重試來避免同秒撞名。規格沒說照這個。
- 佐證:file: `scripts/lumos:20557`,`_ledger_append` 單次 `os.write` 只保證單列不交錯,不管編號唯一。

**F6(E 修復迴圈、S9、S13)**
severity: major
blocking: 是
判準:「累計三列 FAIL」沒有重置規則,修好之後仍會被擋,而且與 S13 自己的故意失敗互相衝突。
- 問題:規格說「同一條款累計三列 FAIL,不論原因都停」。修復後已經有 PASS 列,`lumos evidence check` 仍然回非零,因為歷史 FAIL 還在帳裡(規格也要求 FAIL 與之後的 PASS 都留在帳裡)。沒有「最後一列 PASS 就清零」或「只算最近一段」的規定。
- 問題:S13 要故意拿掉保護、留 FAIL 列,再還原留 PASS 列。反覆做破壞測試的同一條款,三次後就永遠被判「停」。
- 問題:連續兩列相同雜湊的判法依賴帳內順序,而兩程序同時寫時順序不代表時間順序。「去掉時間與路徑後的雜湊」沒定義正規化範圍,PID、port、UUID、k6 的毫秒數都會讓雜湊不同,連續規則實際不會觸發。
- 佐證:file: `scripts/lumos:20557`,帳是純追加、無重置機制。

**F7(C「lumos evidence run」,指令執行方式)**
severity: major
blocking: 是
判準:shell 執行和 argv 直接執行沒選定,「指令無法啟動」這條 BLOCKED 規則在 shell 模式下不會成立,誤差會進 FAIL 計數。
- 問題:規格寫 `-- <指令>`,沒說是 `shell=True` 還是 argv 直接 exec。用 shell 時指令不存在回 127,是非零退出碼,會被判 FAIL 而不是 BLOCKED。S7 的「無法啟動 → BLOCKED」測試只能在 argv 直接 exec 時成立。
- 問題:127 算 FAIL 就會進 F6 的累計三列計數,被當成程式修不好。
- 佐證:file: `scripts/lumos:17181`,`_kill_run` 用 `shell=True`,沿用的話 S7 的第一半不會成立。

**F8(C「pass 要有證據」、「繞過 lumos set 的寫法」)**
severity: major
blocking: 是
判準:新舊分界靠人可手改的 `created` 欄位,守衛可以被一個欄位值整個繞過。
- 問題:規格說「2026-10-19 之後新建的驗證筆記」才適用,又說 lint 對「2026-10-19 之後新建」的 pass 筆記報錯。判定「新建」靠 frontmatter 的 `created`,這個欄位可以手改。把 `created: 2026-10-01` 寫進去,就整個落在舊筆記豁免區。
- 問題:規格已經承認手改開頭欄位能繞 `lumos set`,卻用同樣可手改的欄位當分界,守衛沒有堵住自己指出的洞。
- 佐證:file: `scripts/lumos:18475-18480`,`_STATUS_ENUM` 的 verification 只是值域檢查,不看日期。
- 佐證:規格內「舊的驗證筆記(2026-10-12 機械數…)不追溯」。分界用 git 首次提交日或固定的筆記清單比較不會被手改,規格沒提。

**F9(A「題目住哪」,〈待決問題〉一行解析)**
severity: major
blocking: 是
判準:一行的文法沒給,S1、S2 的判定與 `--answers Q3` 都會在邊界上各讀各的。
- 問題:規格只給一個範例行。重複編號(兩行 `[Q3]`)、欄位順序顛倒、一行多個連結、`→` 後面為空、一題跨多行、小節為空、題目內文含 `[...]`,都沒說怎麼處理。
- 問題:已決要連「`#dN`」,但決策 id 是各節點自己的 `decisions:` 欄位內編號。本篇的 d1 和別篇的 d1 同名,規格沒說連到哪一篇的 d1。
- 問題:`--answers Q3` 要寫進決策,但 `cmd_decision_add` 只收單一節點 `rel`,沒有指定哪份計劃。重複編號時無法判定回答的是哪一題。
- 問題:延後「必附理由」,但 Q5 的理由是行尾自由文字,沒定義格式,S2 沒法機械判。
- 佐證:file: `scripts/lumos:20434`,`cmd_decision_add(env, rel, content, decided, context=None, why=None)`,沒有計劃或題號參數。
- 佐證:file: `scripts/lumos:6900`,現有 `SPEC_CLAUSE_RE = \[S(\d+)\]`,新增 `[Q3]` 行與條款行共存時不衝突,但規格沒測。

**F10(S12、S13,Docker 不可用時)**
severity: minor
blocking: 否
判準:Docker 不可用時 S12、S13 的狀態沒有定義,不過兩者本來就是 `[manual:]`,後果是無法機械驗收而不是誤放行。
- 問題:S12 和 S13 都標 `[manual:]`,`spec-trace` 只看有沒有綁定,不看有沒有證據列。Docker 缺失時 `evidence run` 回 BLOCKED,但沒有任何機制阻止人在沒有 PASS 列的情況下把這兩條視為滿足。
- 佐證:file: `scripts/lumos:5483-5491`,`MANUAL_REF_RE` 與 `_MANUAL_MIN_CHARS = 4`,只要求 manual 文字不短於 4 字。
- 佐證:S10 的 `[evidence:]` 綁定可以補這個洞,但規格沒要求 S12、S13 改用它。

**F11(C「存檔前遮蔽」,漏網形狀)**
severity: minor
blocking: 否
判準:遮蔽用名稱包含 KEY 等子字串比對,會同時漏抓與誤殺,誤殺會破壞原始檔的可信度。
- 問題:短值或常見值當秘密會把輸出弄壞。例如環境變數 `TOKEN_TTL=60`,輸出裡所有的「60」都被換成遮罩,k6 的數字證據就毀了。
- 問題:漏網形狀有 URL 編碼的密碼、JSON 轉義的值、Base64、分行輸出。規格只承認「抓不到自訂名稱」,沒提值本身被轉形的情況。
- 佐證:無程式碼可對照,這是規格尚未實作的規則,依規格文字推出。⚠ 實際誤殺範圍取決於比對寫法,規格沒給。

**F12(實務隱患「對外送出」,k6 只打 localhost)**
severity: minor
blocking: 否
判準:「k6 目標限定 localhost」只寫在示範 repo 的設定檔,沒有任何機制擋住別的目標。
- 問題:`lumos evidence run` 接任意指令,規格明說「只記錄、不替指令背書安全」。`BASE_URL` 之類的環境變數被改成外部位址,k6 就打出去。
- 問題:「localhost」本身也沒保證。Docker Compose 發佈埠預設綁 0.0.0.0,別台機器能打進來。
- 問題:這條是 pitfalls 的 external-send 類,規格把它標成「已排除」,前提卻不是機械保證的。
- 佐證:規格內「k6 目標限定 localhost 寫進示範 repo 的壓測設定」。示範 repo 還不存在,無對應程式碼。

**F13(C「驗證筆記狀態」)**
severity: minor
blocking: 否
判準:`_STATUS_ENUM` 的 verification 加值會連動到另一個衍生常數,規格只提了前者。
- 問題:`_DRIFT_C3_STATUSES` 直接由 `_STATUS_ENUM["verification"] - {"pending"}` 推出,加了 `fail` 與 `blocked` 後,`lumos drift fix --kind c3 --status fail` 會變合法。規格沒提這個連動,也沒說是否要保留。
- 佐證:file: `scripts/lumos:38475`,`_DRIFT_C3_STATUSES = frozenset(_STATUS_ENUM["verification"] - {"pending"})`,錯誤訊息在 `scripts/lumos:38514`。
- 佐證:`QUERY_CLOSED_STATUSES`(`scripts/lumos:18470`)沒有 `fail`、`blocked`,所以 `--active` 查詢會把它們當未結案,規格也沒提。

**F14(C「程式版本(HEAD)」)**
severity: minor
blocking: 否
判準:證據列只記 HEAD,沒記工作樹是否有未提交改動,同一個 HEAD 的 PASS 可能來自髒樹。
- 問題:在髒樹上跑出 PASS 後把改動丟掉,PASS 列的 HEAD 仍等於當時 HEAD,看起來有效。規格沒要求記 dirty 旗標或拒絕在髒樹上取證。
- 佐證:file: `scripts/lumos:48870-48935`,`_codeloop_record_valid_ex` 只比 sha 與簿記增量,不看工作樹狀態。規格的有效性判法沿用它,所以同樣看不到。

## 實務隱患鏡頭

- payment:無。規格說不含付款流程,訂單只到建立與扣庫存,查證無相關程式路徑。
- external-send:有,見 F12。k6 只打 localhost 沒有機械保證。F2 也屬此類,因為秘密進版控後可能被推出去。
- prod-irreversible:有,見 F2、F3。`evidence run` 能對任何系統執行任何指令,規格靠 Claude Code 原生權限確認擋,但 argv 秘密一旦寫進進版控的帳就不可逆。

## 固定席:節點行為與合約

不影響既有合約。

- 理由:對照節點就是本計劃自己,查到的影響都落在新增的指令和判定,沒有改到既有節點宣稱的行為。
- 唯一碰到既有合約的是 `_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS` 加名單。規格已說明三個使用者要跑對照測試。
- ⚠ 我沒有逐一讀那三個使用者的合約筆記,這裡只確認程式碼層(`scripts/lumos:7071`、`13170`、`42214`、`42227`)確有這幾處消費者。

最嚴重 severity: major,blocking 共 8 條(F1 到 F9 中除 F10 外,即 F1、F2、F3、F4、F5、F6、F7、F8、F9 共 9 條)。

更正:blocking 為「是」的是 F1 到 F9,共 9 條;F10 到 F14 為 minor、blocking 為「否」,共 5 條。

最嚴重 severity: major,blocking 共 9 條。

## 補引句(編排者續談請同席補,只補不改判)

- F1 引句:「沿用既有帳檔的追加寫法與原子寫入慣例」
- F2 引句:「存檔前遮蔽:環境變數裡名字像 TOKEN/PASSWORD/SECRET/KEY 的值」
- F3 引句:「指令跑不起來或逾時判 BLOCKED」
- F4 引句:「原始檔有大小上限,超過只存頭尾並標截斷。」
- F5 引句:「證據編號、需求(計劃條款)、驗證節點」
- F6 引句:「同一條款累計三列 FAIL,不論原因都停。」
- F7 引句:「結果只由退出碼與 `--expect` 判準機械決定(PASS/FAIL)」
- F8 引句:「2026-10-19 之後新建的驗證筆記,狀態要設成 pass」
- F9 引句:「`狀態` 取 待查/自答/待人/延後/已決/已驗」
- F10 引句:「[manual: 第 4 階段在示範 repo 執行併發測試並以證據帳列為憑]」
- F11 引句:「遮蔽規則只抓常見命名,抓不到自訂名稱的秘密」
- F12 引句:「k6 目標限定 localhost 寫進示範 repo 的壓測設定」
- F13 引句:「`_STATUS_ENUM` 的 verification 加 `fail` 與 `blocked`」
- F14 引句:「程式版本(HEAD)」
