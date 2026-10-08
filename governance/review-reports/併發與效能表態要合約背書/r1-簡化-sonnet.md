severity: major

**F1. 基數下整套機制沒有今天的使用證據,RETIRE-IF 量不出來**
severity: major
blocking: 是——機制規模與可觀測基數不成比例,且撤除門檻今天無法判定。
段落:〈緣起與現況〉與〈RETIRE-IF〉。
引句:「本 repo 沒有那份忽略清單、帳檔都被追蹤,但也只有 4 筆紀錄」
引句:「8 週總觸發少於 5 次——量太小,維護成本大於價值」
file: `docs/.kill-log.jsonl:1` 全檔 4 筆,同一 node、同一測試 t_canary_record_persist;3 筆 killed_unattributed、1 筆 killed。
file: `docs/.governance-log.jsonl` 56 筆 kind=dispositions,只涵蓋 py-eventloop/py-parallel/py-external/py-memory/py-hotpath 五題;被標八題觸發 0 次、satisfied 0 次。只查本 repo,消費專案未查,⚠ 交編排者。
問題:本 repo 是 Python CLI,八題永遠不觸發;只記 contract-evidence(warn 有問題時)量不出分母;條件③與「值得建」前提矛盾。

**F2. 背書過期判定(祖先+files 差異)在 1 筆強證據的基數下不值得建**
severity: major
blocking: 是——三個判定分支加兩條 git 指令,只為防沒有實例的失效情境。
段落:〈satisfied 要什麼證據〉第 2 點。
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動 → 「背書過期,要重跑破壞測試」。」
問題:files 只記配方改到的檔,不含測試本身;測試被改成永遠綠仍算未過期;「未過期」不代表仍咬得住。更小做法:只判帳上有沒有 killed,顯示 commit 給人看,砍 S5、S6。

**F3. off/warn/block 三模式加壞設定處理,block 沒有上線計劃**
severity: major
blocking: 是——三模式要 4 條驗收條款,block 沒有使用者且寫明升級另開計劃。
段落:〈擋不擋〉與〈不做〉。
引句:「`block`:同樣情況當成表態不完整,照表態閘既有路徑擋。」
引句:「不做 block 預設;升級另開計劃。」
問題:block 是「以後可能會用到」;最小版只做 warn/off 或只提醒;off 已由 stack_questions.gate 控制,並列開關邊際價值低。

**F4. 派工鏡頭註記與快取鍵變更成本高於效益**
severity: major
blocking: 是——全案最貴的附屬機制,對核心目的沒有直接貢獻。
段落:〈派工鏡頭多一行〉。
引句:「派工鏡頭的快取鍵(`_lens_cache_path`)要把背書狀態算進去,否則補跑破壞測試後舊快取不會失效。」
file: `scripts/lumos:35765` 到 `scripts/lumos:35782` 快取鍵 extra 是表態記錄 sha256,明寫 marker_only 不掃治理帳;暖機從 LUMOS_LENS_DISP_KEY 取 key(r1 併發席 f7)。
問題:要在 marker_only 路徑讀治理帳,與現行刻意設計衝突,spec 沒處理;code-loop check 已印提醒,派工單是第二條呈現路徑。可砍 S11 與整段。

**F5. guard-kill 事件欄位與 .kill-log.jsonl 重複**
severity: minor
blocking: 否——可精簡但不影響正確性。
段落:〈satisfied 要什麼證據〉第 1 點。
引句:「再用既有的治理帳寫入(`_gate_event_or_warn`,不改變呼叫端判定)為每條配方各寫一筆 `kind=guard-kill`」
問題:欄位幾乎重複;可只把 killed 那筆寫進治理帳;每條配方各寫一筆增加未上鎖帳的寫入次數,「不加重」論據不成立。

**F6. 只改技能文件可單獨達成核心目的,其餘可延後**
severity: minor
blocking: 否——取捨建議。
段落:〈教人怎麼寫測試〉。
引句:「技能文件(lumos-project-notes 寫合約那節、lumos-code-loop 表態那段)各加一小段」
問題:基數 0 時先做 S12;最小機械層是「satisfied 不收 path:line」(S3)。

**F7. 引用核對**
severity: minor
blocking: 否——僅記錄。
段落:〈實務隱患〉。
引句:「併發:治理帳多個寫入者同時寫的問題已有 [[Issues/治理帳多個寫入者都沒上鎖]]」
問題:只用片語 grep 到,未逐一核對檔名,⚠ 交編排者。

各節:其他表態照舊、回退、合約候選、審計修正紀錄:已讀,無 finding。
實務隱患:併發有風險(F5);效能有風險(F4);資源、相容、輸出純度、誤判:無新增。

最嚴重 severity:major;blocking 共 4 條(F1、F2、F3、F4)。
