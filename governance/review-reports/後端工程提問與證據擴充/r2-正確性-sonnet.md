severity: major

**固定席逐條判(節點 `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md`)**:該節點摘要裡沒有 `KEY:★INVARIANT★` 合約行,也沒有 `RULE:`。只有 `FACT:本機容器環境選 Docker Desktop [來源:人工]`,這份設計不碰它。判「不影響」。節點宣稱的 WHY/決策 d1–d5 是這份設計自己的內容,不構成要保護的既有行為。

severity: major
blocking: 是,「最新一列」的過濾順序會讓真實的 FAIL 被濾掉,交付檢查照樣放行。
引句:「最新一列非作廢、非弱、非髒樹的證據是 PASS,且指紋等於現在的程式內容指紋」
照字面,過濾先於取最新:先濾掉髒樹列,再取最新。輸入是 clean 樹上 PASS,改程式不提交後重跑,得到髒樹 FAIL。這條 FAIL 被濾掉,舊 PASS 的指紋(HEAD 算的)仍等於現在,於是回 0。E 節的連續 FAIL 計數卻把這條列進去,D 和 E 對髒樹列的口徑不一致。

severity: major
blocking: 是,未提交的程式改動可以直接繞過新舊判定。
引句:「HEAD 的 `git ls-files -s`(檔案模式、內容雜湊、路徑)」
`git ls-files -s` 讀的是 index,不是 HEAD,讀 HEAD 要用 `ls-tree -r HEAD`。交付檢查的「現在」也沒說是 HEAD 還是工作樹。輸入是改了程式、未提交,然後 `lumos set <計劃> status done`:用 HEAD 算就與舊 PASS 的指紋相同而放行,用 index 算又會被 staged 狀態影響。「髒樹」也沒定義是否含 staged、untracked,或上一次 run 寫進 `docs/.evidence-log.jsonl` 的未提交改動。file: `scripts/lumos:13170` 已有「dirty_paths 排除簿記」的先例,spec 沒引用。

severity: major
blocking: 是,「內容一樣指紋就一樣」對消費專案不成立。
引句:「排除知識圖譜目錄、`governance/`、`.lumos/` 與簿記名單後算 sha256」
排除清單沒有排除 vendored 的 `scripts/lumos`、`scripts/hooks`、`scripts/templates`,也沒排除 CLAUDE.md 注入段。輸入是 `lumos update` 或改 `_BOOKKEEPING_FILES`(排除清單本身就在 `scripts/lumos`)。同一份業務程式的指紋會變,所有已記的 PASS 一次失效,而且列上沒存排除清單版本,無從分辨。file: `scripts/lumos:22487` `_VENDORED_TOOLKIT` 是被追蹤的檔,spec 沒排除。

severity: major
blocking: 是,S12/S13 日後改綁 `[evidence]` 時,證據和計劃在兩個 repo,指紋永遠對不上。
引句:「交付檢查上線後此條改綁證據標記」
示範 repo 是「另開 repo」,證據帳和程式內容指紋在示範 repo。計劃筆記和 `spec-trace --delivery` 在 lumos-toolchain。`--criterion <計劃>#S<n>` 在示範 repo 的圖譜裡找不到這份計劃。改綁後,這份計劃的 `set done` 要嘛永遠擋、要嘛比對錯 repo。

severity: major
blocking: 是,「解除只有一條路」其實 AI 自己就能走,停止狀態形同虛設。
引句:「解除只有一條路:人看過後跑」
`--human-ok "<4 字理由>"` 是普通旗標,沒有 tty 或人工確認的機制,AI 自己下指令就歸零。`evidence void` 也沒有任何限制(「追加一列作廢,不刪舊列」),作廢 3 條 FAIL 列也能讓計數歸零。作廢最新那條 FAIL 還會讓較舊的 PASS 重新變成「最新」,可繞過 D①。file: `scripts/lumos:21811` 顯示 repo 對需要人的操作有 `isatty` 確認先例,spec 沒用。

severity: major
blocking: 是,「單列保證小於 4KB」的保證不成立,取證會白跑。
引句:「單列保證小於 4KB(既有追加寫法 `_ledger_append` 的上限)」
指令截到「1000 字」,但 `json.dumps(ensure_ascii=False)` 的 CJK 每字 3 位元組,emoji 每字 4。1000 字就占 3000 到 4000 位元組。比對規則、工作目錄、條款、環境名都沒定上限。輸入是長 `--expect-match` 或很深的 cwd。file: `scripts/lumos:20557` 超過 4096 會丟 ValueError,指令已跑完卻 rc 2、沒有帳。

severity: major
blocking: 是,規格只寫逾時才殺程序群組,Ctrl-C 時子程序變孤兒。
引句:「Lumos 自己被 Ctrl-C 中斷——一律記一列 BLOCKED」
照 `_kill_run` 用 `start_new_session=True`,終端的 SIGINT 不會送到子程序。只有 `TimeoutExpired` 才 `killpg`。輸入是跑 k6 或 docker 時按 Ctrl-C:帳上寫 BLOCKED、以 130 結束,壓測卻繼續打資料庫。S5 只測了逾時要連子程序一起結束。file: `scripts/lumos:17169`

severity: major
blocking: 是,沒有證據帳的專案,只有〈待決問題〉的計劃會被 `set done` 永久擋住。
引句:「全過回 0,有沒過的回 1 並逐條列出,證據帳讀不了回 2」
`lumos set done` 在「有〈待決問題〉一節」時就跑交付檢查,不需要有 `[evidence]` 條款。大多數消費專案根本沒有 `docs/.evidence-log.jsonl`(帳檔只在 `evidence run` 時建立)。這種專案若把「帳檔不存在」當「讀不了」就是 rc 2,S11 也沒測這個情況。

severity: major
blocking: 是,不更新 `_KNOWN_GATES`,事件會被靜默丟掉,RETIRE-IF ③ 的量測永遠是 0。
引句:「交付檢查每次擋下或放行都寫一筆治理帳事件(沿用 `_gate_event`)」
file: `scripts/lumos:1533` 閘名不在 `_KNOWN_GATES` 就只印警告、不寫帳。file: `scripts/lumos:1522` 沒有 `docs/` 目錄時回 None。spec 的「要同步改的有…」清單沒列 `_KNOWN_GATES`。S1–S13 也沒有任何一條測治理帳事件或 `gov --stats` 接線。

severity: minor
blocking: 否,「未結」的定義有洞。
引句:「有標阻塞、階段是需求或架構、狀態是待查或待人的題,不放行」
輸入是 `[阻塞]` 加 `[狀態:延後] 理由:先放著吧`:只有「不可逆不得自答」被擋,阻塞加延後不受限。依 S1 字面不擋規格閘,D③ 的「還沒結」也沒定義延後算不算結。

severity: minor
blocking: 否,「有效」的定義指向了一個不存在的段落。
引句:「已驗=已決的連結再加 `證據:` 一個有效證據編號(有效的定義見 C)」
C 節沒有「有效」的定義,定義只在 D①。D② 的「符合①」又是以條款的「最新一列」為準,題目引的舊編號是否算數不明。lint 若檢查已驗,結果會隨程式內容指紋變動,成了時變規則;S2 也沒列這項。

severity: minor
blocking: 否,規格引用的現有結構形狀不對。
引句:「形狀照棧別題庫 `_STACK_QUESTION_SPECS` 的條目寫法(`{id, stage, ask, when[]}`」
file: `scripts/lumos:26519` 實際鍵是 `id`、`q`、`when`(另有 `needs_backing`、`shape_only`),沒有 `stage`、`ask`。file: `scripts/lumos:51379` `pitfalls` 的位置參數是 vault-free 的 spec md 路徑,不是計劃節點名,`lumos pitfalls <計劃> --stage` 要寫清是路徑。

severity: minor
blocking: 否,「逐行比對」遇到沒有換行的大串流會把整串吃進記憶體。
引句:「比對在串流時逐行做,判定先於截斷」
輸入是 2GB 沒有換行的二進位輸出,`readline` 式的逐行讀會整串緩衝,抵消「50MB 只留頭尾」的資源保證。

severity: minor
blocking: 否,計數規則有永遠不觸發的路徑。
引句:「連續 3 列非作廢的 FAIL 或連續 3 列 BLOCKED」
FAIL、BLOCKED 交替(F,B,F,B…)永遠湊不到 3 連續。一列 weak PASS(`-- true` 不給比對)也會當成 PASS 把計數歸零。所以沒有 PASS 資格的弱證據也能重置停止狀態。

總結:最嚴重 major;blocking 共 9 條
