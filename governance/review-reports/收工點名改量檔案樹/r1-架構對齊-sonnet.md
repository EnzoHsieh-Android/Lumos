severity: major

# 架構對齊審查:收工點名改量檔案樹_計劃

## finding 1 — 新造「跨輪雜湊快照比對」,把既有的「量版控索引」降級成備援

severity: major
blocking: 是
引句:「做法:每次收工存一份快照(工作樹相對上次提交的檔案清單與雜湊),下一次跟上一次比,差集就是這一輪。」

這份設計要解的問題(「改了哪些程式碼檔」)在這個 repo 已經有一種站得住的既有做法——**量版控索引/git diff**,而且不是只有一處:

- file: `scripts/hooks/pre-commit:43` — `STAGED="$(git -c core.quotePath=off diff --cached --name-only)"`(提交前:量 staged 索引)
- file: `scripts/hooks/pre-push:51` — `"$PY" "$GRAPHCTL" impact --diff "$1" --sync-check --json --repo "$REPO_ROOT"`(推送前:量 commit range)
- file: `scripts/hooks/claude/check-graph-sync.py:590` — `_impact_missing` 自己的註解寫著「跟 pre-commit/pre-push 同一條路:lumos impact --diff HEAD --sync-check --json(工作樹 vs HEAD)」,呼叫點在 `scripts/hooks/claude/check-graph-sync.py:600`
- file: `scripts/lumos:15345` 與 `scripts/lumos:28664` — 主程式裡也是 `git status --porcelain` 系列

這份設計自己也承認這件事:

引句:「本專案自己的 `pre-commit` / `pre-push` 兩道閘也早就是量 git 索引,跟用什麼工具改的無關」

但接下來設計選的**主要**機制不是延用這條路,而是自建一套沒有 git 語意、靠 hashlib 手算內容雜湊、寫進自訂狀態檔、下一輪讀回來取差集的「快照鏈」;git-diff 那條既有路(工作樹 vs 上次提交)反而被壓到「退回路徑」:

引句:「第一次跑、或快照讀不到時**沒有基準**:退回全量(工作樹 vs 上次提交)。」

也就是說:「量版控索引」在這份設計裡從「本來就夠用的主線做法」變成「降級才用的備胎」,真正的主線是一套本 repo 沒有先例的狀態機制(跨呼叫持久化的內容雜湊快照)。這正是題目要抓的第二種做法——之後有人要修「改了哪些檔怎麼算」這件事,得先搞懂兩套(git-diff 家族 vs 快照雜湊鏈)各管哪個分支,才知道要改哪邊。

(旁註,不算另一條 finding:設計要解的「共用工作目錄污染」問題確實是既有三種 git-diff 做法都沒處理過的——它們比對的基準永遠是「一個確定的 git 端點」staged/commit range/HEAD,不是「上一次 hook 執行的時刻」;這點是真問題,但不必然要靠自建雜湊狀態機解——例如 `git stash create`(不動 stash ref,純取一個 commit-ish)搭配 `git diff --name-only <上次快照的 commit-ish> <這次的 commit-ish>`,一樣能拿到「上一輪跑完後到這一輪」之間的差集,而且不必離開「量版控索引」這個既有典範、也不必手刻內容雜湊。設計沒有討論過為什麼不走這條、而要另起一套雜湊快照,這個缺口本身也支持「這是引入第二種做法」的判斷。)

## finding 2 — 沒說新邏輯放哪:抄一份進 hook,還是叫 lumos 子命令

severity: ⚠
blocking: 否
引句:「把「這一輪改了哪些程式碼檔」從**讀對話紀錄認工具名**,改成**量檔案樹**。」

Hook 檔頭與多處註解明講這條鐵則,而且有守衛測試盯著:

- file: `scripts/hooks/claude/check-graph-sync.py:462-465` — 「單源說明在 Systems/hook信任邊界;這段在幾支 hook 裡是逐字相同的複本,有守衛測試盯著不准漂(hook 是獨立檔、複製到全域後彼此 import 不到,所以用「複製 + 守衛」而不是抽共用模組)」
- file: `scripts/hooks/claude/dispatch-lens-hook.py:159-162` — 同一段話的另一份複本

但這條鐵則目前在這支 hook 裡實際上分岔成兩種合法作法:①小型工具函式(`_trusted_lumos`、`_inner_budget`、`_mkdir_under_home`)是逐字複製進每支 hook,不呼叫 lumos;②較重的域邏輯(算「改了哪些筆記還沒動」)是 `subprocess` 呼叫 `lumos impact --diff HEAD --sync-check`(`check-graph-sync.py:600`),邏輯住在主程式裡。

這份設計完全沒交代新的「量檔案樹、存快照、取差集」邏輯要走哪一條——是像 ①一樣整段手刻進 `check-graph-sync.py`(那會是一段不小的邏輯:遍歷檔案樹、算雜湊、讀寫狀態檔,遠比現有複本重),還是像 ②一樣新開一個 `lumos` 子命令、hook 只 subprocess 呼叫。這兩種在本 repo 都有先例、也都不算違規,但設計沒表態,無法判斷這份設計本身有沒有踩到「該抄一份卻偷懶 import」或「該收進主程式卻散在 hook 裡自成一套」——判不準,交編排者裁,或要求設計補上這一段。

## finding 3 — 快照寫入失敗時怎麼辦,設計沒講

severity: minor
blocking: 否
引句:「基準檔不能放在 repo 的工作樹裡。」

S5 只講「放哪裡」,沒講「寫失敗（磁碟滿、權限、並發寫入衝突)時要怎樣」。鄰居檔在寫自己的狀態檔時都有明確的失敗語意:

- file: `scripts/hooks/claude/check-graph-sync.py:740-755` — `_stop_mark_write`:`O_EXCL` 原子建檔,任何 `OSError` 一律回 `False`(=不擋,寧可漏),且 fd 一定 close
- file: `scripts/hooks/claude/check-graph-sync.py:867-881` — 寫 stdout 失敗時「把名額退回」(`mp.unlink()`)再 raise,不留一個「以為佔到但其實沒佔到」的假狀態

這份設計對「快照寫失敗」完全沒提對應的降級語意(是靜默放棄這次寫入、下一輪照樣退回全量,還是怎樣)。不影響結構判斷,但跟鄰居的「錯誤處理要交代清楚」慣例比,這裡是缺一塊,補上就好。

---

## 四問逐答

### 1. 分層與依賴方向

**不對齊**,對應 finding 1、finding 2。

新機制(量檔案樹、存跨輪快照)要放的位置屬於 `check-graph-sync.py` 的第 2 道閘,這個定位本身沒問題(閘門結構見 `scripts/hooks/claude/check-graph-sync.py:14-19` 的四層閘門註解、`main()` 裡 `scripts/hooks/claude/check-graph-sync.py:802-824` 的實際順序)。但設計完全沒交代這段新邏輯要走「hook 內複製一份」還是「呼叫 lumos 子命令」——這正是本檔案反覆用★標出來、還有守衛測試盯著的鐵則(`scripts/hooks/claude/check-graph-sync.py:462-465`、`scripts/hooks/claude/dispatch-lens-hook.py:159-162`)。設計沒有違反它(沒寫出會違反的具體做法),但也沒有表態遵守——這塊是空白,不是對齊。

S5(基準檔寫在 repo 工作樹之外)這一條倒是跟既有慣例對得上:`_stop_block_dir()` 本來就是寫在 `Path.home() / ".cache" / "lumos" / "stop-block"`(`scripts/hooks/claude/check-graph-sync.py:618-621`),不進 repo 工作樹,跟 S5 要求的方向一致。

### 2. 命名與錯誤處理

**大致對齊,一處缺口(finding 3)**。

S3「取不到基準就要明講,不准安靜印一個看起來精確的數字」——這正是本檔案家族近期定案的風格:`dispatch-lens-hook.py` 在 2026-09-05 第二輪審視後把「超時靜默放行」改成「附一行固定說明」(`scripts/hooks/claude/dispatch-lens-hook.py:323-342`,尤其 331-341 那段「吞掉逾時的地方要自己講一聲」);`check-graph-sync.py` 自己的 `_stop_block_dir()` 在判準不過時也一定印 `stderr` 訊息而不是悄悄跳過(`scripts/hooks/claude/check-graph-sync.py:630-634`)。S3 的「退回全量要明講」跟這個既有風格完全吻合。

寫失敗(存快照)這條路徑鄰居有先例但設計沒提,見 finding 3,算 minor 缺口不算結構不對。

### 3. 第二種做法

**不對齊**,即 finding 1。這個專案判斷「改了哪些檔」目前至少三處都是「量版控索引/git diff」這同一個典範:`pre-commit`(`scripts/hooks/pre-commit:43`,staged 索引)、`pre-push`(`scripts/hooks/pre-push:51`,commit range)、`check-graph-sync.py` 閘門 3 的 `_impact_missing`(`scripts/hooks/claude/check-graph-sync.py:590,600`,工作樹 vs HEAD)。這份設計要新增的「快照差集」(跨輪持久化的內容雜湊比對)是本 repo 沒有先例的第四種寫法,而且設計自己把既有那條(工作樹 vs 上次提交)降格成「退回路徑」而非主線——見引句「做法:每次收工存一份快照…下一次跟上一次比,差集就是這一輪」對照「第一次跑、或快照讀不到時…退回全量」。既有做法夠不夠用是可以討論的(共用工作目錄污染確實是既有三種都沒解過的真問題),但設計沒有交代「為什麼不能用 git 本身的機制(例如 `git stash create` 產生兩個時間點的 commit-ish 再 `git diff --name-only` 比對)去解決同一個問題」,就直接跳去手刻一套雜湊狀態機——這就是「有一種夠用的做法卻自己造了一種」的典型情況。

### 4. 落點合不合理

**對齊**。`Systems/graph-sync-coverage.md` 的 `about_code` 已經列了 `scripts/hooks/claude/check-graph-sync.py`(`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:32-33`),照「每支檔有家」規矩,這支檔的家本來就該收所有改到它的設計說明,不必為了「算改了哪些檔」這個子問題另開新節點。

這篇節點目前規模也不算大:frontmatter 到 `---` 結束約 34 行,正文一張三時機對照表加兩段說明(`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:35-51`),`decisions` 只有 1 筆(d1),`about_code` 管 2 支檔(`check-graph-sync.py`、`scripts/lumos`)。實際查了 repo 裡所有引用 `graph-sync-coverage` 的計劃筆記,目前只有這份被審的計劃把 `lands_in` 指過去,其餘(工具鏈補強十件、評測尺翻案、地基盤點、Codex行為精修、全repo審視、Spotify-shunt吸收)都只是 `related` 順路提到,不是落地——沒有「一篇包全部」的既有負擔,塞進去不會讓節點超出負責範圍。

節點現有摘要的白話語(`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:39`,「把原本只供人看的 `lumos impact --sync-check` 接到三個時機點名」)講的是「動過圖譜之後點名哪幾篇沒動」這個子機制,跟這次要塞的「怎麼算出這一輪改了哪些程式碼檔」是同一支檔裡的另一個子問題,寫回時建議在 KEY 行另起一條講清楚是閘門 2(算改了哪些檔)而不是閘門 3(sync-check 點名)的改動,避免以後有人把兩件事混成一件——但這是寫回時的細節,不影響「該不該落這篇」的判斷。

---

不對齊共 3 條,其中 major 1 條。
