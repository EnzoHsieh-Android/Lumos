severity: major

## F1 「回退」三招都寫成本機切關,但消費專案跑的是拷貝定版的工具鏈,不會自動吃到回退
severity: major
blocking: yes

spec 的回退段把三個改動的退路都寫成在來源 repo(lumos-toolchain)這邊動一刀就好:
引句:「健檢新段落是一個獨立的段,回退=拔掉那段呼叫與 CI 的清單參數。」
引句:「新欄位規則都走「新違規才擋」」

（第二句因規則要求逐字引用、原文本身含括號但無巢狀「」，附帶說明：完整句為「三、新欄位規則都走『新違規才擋』:回退=把新違規判定改成一律回『舊違規』即全部降成提醒,不必拔程式。」)

但消費專案裝的不是「跟著來源即時變」的東西:`scripts/lumos:16368` 的 `_vendor_toolchain` 用 `shutil.copy2` 把 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push` 等逐檔複製進消費專案(清單見 `scripts/lumos:16121-16139` 的 `_VENDORED_TREE_FILES`),只有消費專案的人自己跑 `scripts/lumos:16418` 的 `cmd_update`(= `lumos update`)才會重新 pull 來源、重新複製這些檔。也就是說:上線第一天某消費專案已經 `lumos update` 吃到這批新規則,pre-push 在它那邊誤擋——這時就算 Enzo 這邊立刻照回退段的三招之一改 revert,消費專案本機那份 `scripts/lumos`/`pre-push` 內容完全沒變,誤擋照樣發生,因為它讀的是自己硬碟上那份拷貝,不是來源 repo 現在的內容。回退要生效,消費專案的人必須自己知道要再跑一次 `lumos update` 把新的(已回退的)版本拉回去——spec 全篇沒有一處提到這一步,「實務隱患」段也只講「拿不到碰到清單就全部只提醒」這種上線瞬間的保護,沒講已經裝上舊版工具鏈之後要怎麼退。

## F2 S11 的「讀不到上一版就從嚴」在消費專案自帶的 shallow-clone CI 上會把舊帳當新違規擋下
severity: major
blocking: yes

引句:「若讀不到上一版(新建的筆記、改名、或上一版讀取失敗),則這一版的違規應全部當成新違規(從嚴)」

引句:「當 CI 由推送事件觸發且有推送前的起點,CI 應以起點到本次提交的改動算出碰到的筆記清單並交給健檢」

S11 判斷「讀不到上一版」的情境包含「上一版讀取失敗」,而 S3 要求 CI 用推送前的起點與本次提交去算清單、交給健檢做新舊違規判斷——這兩條合起來依賴 CI checkout 有完整歷史才拿得到「上一版」的內容。lumos-toolchain 自己的 `.github/workflows/ci.yml:16` 特別設了 `fetch-depth: 0`(註解寫著是給 code-loop 算 diff 用的),但 `.github/workflows/ci.yml` 不在 `_VENDORED_ALL`/`_VENDORED_TREE_FILES`(`scripts/lumos:16121-16139`)清單裡,不會被 `lumos update` 複製到消費專案——每個消費專案的 CI workflow 是自己寫的,`actions/checkout@v4` 預設 `fetch-depth: 1`(shallow)。一旦消費專案的 CI 沒有主動設 `fetch-depth: 0`,S11 就會對這次推送觸碰到的每一篇筆記都判「讀不到上一版」,把該筆記裡任何既有(舊)違規(例如早就沒有 `lands_in` 的舊 `_計劃` 筆記、早就寫錯格式的日期)一律升級成「新違規」擋下——即使那篇筆記這次只是被順手碰到、規則設計上明明想讓它只提醒。spec 的做法三與 S3 都沒提到「上一版讀不到」對 shallow clone 的依賴,也沒有要求或檢查消費專案 CI 的 fetch-depth。

## F3 doctor --ci 的 gate findings 寫進 append-only 治理帳,誤擋事後沒有訂正機制
severity: minor
blocking: no

引句:「有碰到清單時(推送前掛鉤本來就傳;CI 改成用推送前的起點算出同一份清單):清單裡的筆記有錯誤 → 擋;其他筆記有錯誤 → 只提醒並列出篇名。」

`run_doctor`(`scripts/lumos:989-1002`)本身就有 `gov_events = []` 這個「本輪 gate findings → governance-log(--ci 才寫)」的既有管道,寫入端是 `scripts/lumos:949` 的 `_append_governance_log`,直接 append 進 `docs/.governance-log.jsonl`,函式註解自己寫明「dedup 留給讀時(lumos gov)」——也就是寫進去的錯誤事件不會被修改或刪除,只能在讀的時候被動去重。spec 做法一把新段落直接掛在健檢裡("健檢新增一段"),沒有講清楚這段的 findings 會不會跟其他 gate 一樣落進 `gov_events`;如果會(既有其他段落都這樣做),那麼 F1/F2 講的日誤擋一旦發生,除了當下擋下推送以外,還會在 `.governance-log.jsonl` 留一筆永久記錄,事後 revert 規則或修好筆記都不會回頭訂正那筆帳,下游讀治理帳的人(`lumos gov`、代碼審流程)看到的仍是「這篇筆記/這次推送被擋」而查不到那是規則本身的 bug。spec 的回退與誠實界線兩段都沒提到這筆帳要不要標註、要不要補一筆訂正事件。

最嚴重 severity: major,blocking 共 2 條(major×2、minor×1)。
