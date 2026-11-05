severity: major

我用 `scripts/hooks/pre-push`、`scripts/lumos`、`.github/workflows/ci.yml` 的現況對照 spec 字面。以下每條都寫了「照字面實作會怎樣」。

---

**F1**
severity: major
blocking: 是(照字面實作,基礎設施清單的「執行器本體函式」判準會失效,測試假綠的路徑沒被擋)
- 段落:做法 2「基礎設施清單」。
- 引句:「頂層函式名不是 `t_` 開頭、而且沒有任何一支 `t_` 測試的原始碼整字提到它」
- 問題:判準用「整字提到」,而 `main` 這種常見字會被測試字串提到。spec 自己舉的例子就是 `main`。
- 佐證:我用 `_keys_mentioned` 同一個整字規則掃 `scripts/test_lumos.py` 的 `t_` 函式,463 支提到 `main`,12 支提到 `shard`。
  - 照字面,執行器的 `main` 會被判成「被測試呼叫的輔助」,走關鍵字而不是強制全套。
  - 弄壞 `main`(分片、選測、計時)的改動只會選中提到 `main` 的那些測試。
  - 另有兩個沒定義的邊界:
    - 新增、尚未被任何 `t_` 提到的輔助,會被誤判成執行器,每次都全套。
    - 判準用新版檔還是舊版檔沒寫,被刪除的函式無從判斷。
  - 檔案:`scripts/test_lumos.py:1`
- 建議:改成明列常數(像 `_SELECTION_FUNCS`),或改成「test_lumos.py 裡非 `t_` 的改動一律全套」。

**F2**
severity: major
blocking: 是(這是少跑測試的核心保證,現有判定不認得非函式的改動)
- 段落:做法 1 關鍵字三條、做法 2。
- 引句:「檔名:頂層函式超過 200 個的大檔(`scripts/lumos`、`scripts/test_lumos.py`)不用檔名當關鍵字」
- 問題:`_affected_test_keys` 只認 hunk 標頭和 `+/-` 頂格的 `def` 行(`scripts/lumos:61758`)。
  - 改的若是模組層常數、正則表、元組(例如 `_DOCS_ONLY_PATHS`、`_PITFALL_DIFF_PATTERNS`、`_KEY_OK_RE`),不會產生任何關鍵字。
  - 現行 light 靠「檔名 `lumos`」當總兜底(量測表中一個字選中 876 支)。spec 拿掉這個兜底。
  - 這種改動只要同次再改一個小函式,就會 affected:只選中那個函式的測試,常數改動完全沒被測到。
  - 只改常數而沒別的關鍵字,才會落到「抽不出關鍵字 → 全套」。
- 同族:`scripts/test_lumos.py` 的模組層全域(例如分片常數)同理。
- 建議:diff 裡有任何不屬於某個頂層 `def` 的改動行(非函式區段、decorator、模組層賦值),直接判全套。

**F3**
severity: major
blocking: 是(選測的把關程式碼是被審對象本身)
- 段落:做法 2、做法 4 CI prep。
- 引句:「`scripts/lumos` 裡選測本身的函式(`_test_suite_for_range`、`_keys_mentioned`、`_affected_test_keys`、`_affected_test_keys_wide`、`_autoloop_full_for`,寫成常數 `_SELECTION_FUNCS`,新增選測函式要一起登記)」
- 問題:判斷「這次有沒有動到選測」的是 PR 自己那一版 `scripts/lumos`(CI prep 在 PR 頭 checkout 上跑,fork 來的也一樣)。
  - PR 若把 `_SELECTION_FUNCS` 或 `_test_suite_for_range` 改成永遠回 affected,新版程式碼自己放行,全套不跑。
  - 本機推送前掛鉤同理,跑的是工作樹那一版。
  - 全套要等合併進 main 才補,而且 notify 又用同一份已合併的程式重算。
  - 風險不只惡意,還有手滑。「新增選測函式要一起登記」靠人記得,沒有機械守衛。
- 建議:判定「是否動到選測」要拿基準版(main 上的 `_SELECTION_FUNCS`)來比,或把整個 `scripts/lumos` 的 `_test_suite_*`、`_keys_*`、`_affected_*` 前綴一律視為基礎設施。

**F4**
severity: major
blocking: 是(兩條條款互相矛盾,剛好一半時行為沒定義)
- 段落:做法 1 最後兩個條件、S1、S2。
- 引句:「關鍵字選中的測試數不超過全部的一半(超過就沒有省到,直接全套)。」
- 引句:「選中不到全部一半、沒設強制全套時」
- 引句:「選中超過一半」
- 問題:剛好等於一半時,做法 1 說可以 affected,S1 說要「不到」一半才 affected,S2 只說「超過」才退全套。三處口徑不同,測試也無從綁。
  - 「全部」的分母也沒定義:3202 支還是 3700 支案例?含不含被別的 suite 排掉的?
  - 數量從哪裡算也沒寫。spec 沒說誰去呼叫 `test_lumos.py --list`。
  - pitfalls 目前純看 git diff,不跑測試執行器。
  - 若執行器載入失敗(例如這次改動讓 `test_lumos.py` 語法錯),數量算不出來時的行為沒寫。fail-safe 應該是全套,但字面沒有。
- 建議:統一成「選中數 ×2 > 全部數 → 全套」(剛好一半算 affected,或反過來),分母寫成執行器列出的 `t_` 總數,算不出來一律全套。

**F5**
severity: major
blocking: 是(字面實作會讓使用者漏跑,方向是少跑)
- 段落:做法 1 最後一條、做法 6、S2。
- 引句:「`LUMOS_PREPUSH_FULL=1 git push` 這次推送前跑全套」
- 問題:只定義了 `=1`。
  - `true`、`yes`、`TRUE`、`1 `(含空白)、`on` 這些使用者最自然的寫法,照字面都是「沒設成 1」,仍然走 affected。使用者要求全套卻被默默少跑。
  - `=0` 與 `=`(空字串)是「有設但不是全套」,字面也沒說。
  - 變數是誰讀:hook 傳給 `pitfalls`(子行程繼承)還是 hook 自己判?沒寫。
  - 若 hook 自己判,而 `pitfalls --json` 不知道,CI 與其他呼叫端就會不一致。
  - RETIRE-IF 還寫「設成 `LUMOS_PREPUSH_FULL` 預設開」,意思又和 `=1` 不同。
- 建議:非空且不是 `0` 一律視為要全套(偏向多跑),或沒認得的值直接報錯。

**F6**
severity: major
blocking: 是(多 ref 合併規則沒寫,hook 現有旗標結構不夠表達)
- 段落:做法 3、做法 1 第一條。
- 問題:一次 `git push` 帶多個 ref(例如 `main` 加一個功能分支),現況是任何一個 ref 判 full 就全套。
  - hook 現有 `_SUITE_FULL`、`_SUITE_LIGHT`、`_SUITE_KEYS`(`scripts/hooks/pre-push:464` 一帶,`538-578`)沒有 affected 狀態。spec 沒說新增旗標。
  - 多個 ref 都 affected 時,`_SUITE_KEYS` 是各 ref 關鍵字的併集,但「選中不超過一半」是逐 ref 算的。併集可能超過一半卻沒被擋住。
  - affected 加 docs 混合怎麼合,也沒寫。
  - 對 `refs/tags/*` 與其他遠端的 ref,不是 `refs/heads/*` 就不判 affected,這點有寫。但 `release/*`、`develop` 這類非 main 長期分支會被當功能分支,合併進它們時 CI 沒有「push 到 main 的全套」補回。
  - CI 只有 `push: branches: [main]`,所以那種分支沒有任何全套兜底(`.github/workflows/ci.yml:5-8`)。
- 建議:寫明 affected 的合併規則,併集後再套一次一半判斷,並說明非 main 長期分支怎麼處理。

**F7**
severity: major
blocking: 是(統計口徑會算錯,而撤除條件正是靠這個標籤)
- 段落:做法 5、S7、RETIRE-IF。
- 引句:「notify 工作拿合併提交的第一個父提交到合併提交這段(就是整個 PR 的改動)重算一次 `affected` 的選測清單」
- 問題:
  - squash merge:單一父提交,範圍正確。
  - 一般 merge commit:正確。
  - rebase merge:一次 push 帶多個提交,合併提交只是最後一個,第一父提交到它只有最後一個提交,前面的改動漏掉。重算的清單過窄,幾乎一定判成「子集漏抓」,會把假的算進 RETIRE-IF 的 3 次門檻。
  - 直推 main 的多個提交也一樣。而且直推 main 本來就是跑全套,根本沒有「子集」可言,卻會被標成 `subset-miss`。
  - 該用 `github.event.before..sha`(`ci.yml` 已有 `BEFORE`),force push 與首推時 before 是全零,要另寫。
  - 重算結果若是 full(例如 PR 改了基礎設施清單),此時 PR 的 CI 其實跑了全套,紅了不算「子集漏抓」,但 spec 沒說要不要標。
  - 紅的測試名怎麼從 16 份 shard 的輸出取出來、逾時被砍的片沒有測試名時怎麼判,都沒寫。
- 建議:範圍改用 `before..sha`,事件不是 PR 合併(直推)就不標,重算為 full 時明確不標,取不到測試名時另標而不算漏抓。

**F8**
severity: major
blocking: 是(通知機制本身有字面實作就會失敗的步驟)
- 段落:做法 4 最後一項、S5、實務隱患「對外送出」「併發」。
- 引句:「標籤 `main-red`」
- 問題:
  - `gh issue create --label main-red` 在標籤不存在時會失敗。spec 沒寫先建標籤(`subset-miss` 同理)。
  - 倉庫關閉 Issues 功能、`GITHUB_TOKEN` 權限被組織政策壓成唯讀、API 暫時失敗時,通知步驟紅了也沒有第二條路。結果主線紅了沒人知道,而這是這套設計「少跑測試」的唯一補償。
  - 「同標籤已有開著的 Issue 就改成留言」:一篇舊的、沒人關的 `main-red` Issue 會吃掉之後所有新的紅,新的壞不會有新標題。
  - 兩個 notify 同時跑(合併 run 與每晚 run),查詢與建立之間有競態,仍可能重開。spec 只說「改成留言」,沒有鎖。
  - 這個工作要不要 `if: failure()` 或 `always()`、依賴哪些工作(shards 被取消、被略過時),都沒寫。
- 建議:加建立標籤步驟,notify 失敗時要讓整個 workflow 顯示紅並留 run 上的醒目註記(退而求其次也要寄信)。

**F9**
severity: minor
blocking: 否(執行時代價與行為,影響速度但不影響正確性)
- 段落:做法 1「擴一層」與 `_keys_mentioned`。
- 問題:關鍵字可能極多。spec 量測的最大案例是 56–139 個函式,再加直接呼叫者一層可能到上千個關鍵字。
  - 選測是每個 key 對每支測試各跑一次 `re.search` 加 `re.escape`。我試跑 1000 個關鍵字對 463 支以上 `t_` 原始碼,超過兩分鐘沒跑完,我手動停掉了。
  - Python `re` 的快取上限約 512,也會抖動。
  - 這步要在 pitfalls 裡算「選中數是否過半」。pitfalls 沒有時限(hook 裡 `|| true`),所以關鍵字多的改動會讓推送卡很久。
  - 另外 `_KEY_OK_RE` 要求至少 3 字,2 字的函式名(如 `fn`)被丟掉,改到它不會產生關鍵字。這屬於 F2 的同族,但至少 spec 也沒提。
- 建議:關鍵字超過某個上限(例如 150)就直接全套,或把全部關鍵字合成一條交替正則,每個測試只掃一次。

**F10**
severity: minor
blocking: 否(逃生口有,但字面沒說兩條路徑一致)
- 段落:做法 1 第一條、做法 3、做法 4。
- 問題:
  - 呼叫端傳 `--target-ref`,但 hook 與 `pitfalls` 版本錯開時(`scripts/hooks/pre-push` 本來就有讀檔探旗標字樣的先例)的行為沒寫。舊版 `pitfalls` 不認得 `--target-ref`,argparse 報錯 → `pf_json` 空 → 判成 full。這是安全方向,但字面沒說,測試也沒綁。
  - PR 事件「以 PR 的頭分支為目的」:fork 來的 PR 頭分支叫 `main` 時,字面規則視為直推 main,走全套(保守,可接受)。
  - base 不是 main 的 PR(堆疊式 PR)範圍從 `origin/main` 分岔點算起,會把下層 PR 的提交一起算進來,選中偏多、可能更常退回全套。合併進那個非 main 的 base 之後沒有 main 上的 push 全套(同 F6)。
  - 新分支首推:hook 現有 `pp_block_range_for`(分岔點),沒寫 affected 判定該用 `_range`(空樹)還是 `_brange`。若誤用空樹,整段歷史都當改動,必然超過一半而全套,省不到。

**F11**
severity: minor
blocking: 否(正確性影響小,是定義遺漏)
- 段落:做法 1 測試檔條、做法 2。
- 問題:只改測試檔或只改簽名基準。
  - 只刪除測試(`t_` 函式被刪):被刪的函式名會產生關鍵字,但沒有測試提到它,選中 0 支,hook 輸出「沒有測試提到」,實際只跑了文件子集。可接受,但字面沒說這樣算 affected 還是「抽不出關鍵字」。
  - 函式改名:舊名在 `-` 行、新名在 `+` 行,兩個都是關鍵字,仍會選到寫死舊名的測試,這條沒問題。
  - 只改 `governance/anchor-baseline.json` 而沒改測試檔:S1 說「只多改了簽名基準 應 照樣是 affected」,但「多改」暗示同時有測試檔。單獨只改簽名基準時沒有程式檔也沒有關鍵字,走哪條沒定義(現行是守衛檔 → 全套)。
- 建議:S1 補一句「只改簽名基準,沒有測試檔的改動」的結果。

**F12**
severity: minor
blocking: 否(每晚全套的可靠度問題,不影響閘本身)
- 段落:做法 4 schedule。
- 問題:GitHub 的 `schedule` 只在預設分支執行,公開倉庫 60 天沒活動會被自動停用,排程可能延遲或被丟。
  - 全套本來就在每次 push 到 main 時跑,每晚這支只多補「時間相關、外部相依」的紅。
  - 而 spec 又寫排程「沒有對應的合併,不標」漏抓,所以它對 RETIRE-IF 完全沒貢獻。
  - 排程被停用時沒有任何訊號。REVISIT 只約了 2026-12-31 看標籤筆數,沒有「排程確實有跑」的檢查。

---

**已讀,無 finding 的節**:PRIOR-ART、舊否決對照、現況(量測表)、範圍(做 / 不做)、回退。

**實務隱患逐類:**
- 併發:已列為 F8 與 F7。
- 時好時壞的測試:spec 已有段落,notify 開 Issue 不回退,可接受。
- 資安:已列為 F3。
- 金流:已排除,與 spec 一致。
- 不可逆:無。設定都可回退,Issue 可關。

**總結:最嚴重等級 major,共 8 條 blocking(F1 至 F8),其餘 4 條 minor。**
