severity: blocker

## 總覽:回退節這次仍然沒寫對

第二版把三類分發位置寫清楚了(比第一版進步),但「沒有其他殘留要清」這句話是假的——同一份文件自己前面就描述了一個現存、不受本案影響、但本案會讓它變多的狀態檔機制。另外,第 3 類位置(接入專案複本)沒有任何機械枚舉方式,跟第一版被打回的病灶是同一個,只是換了包裝。

---

## Finding 1: 「不寫任何狀態檔」自我矛盾,而且是假的

severity: blocker
blocking: 是 — 判準:回退章節據以宣稱「無殘留」的前提本身錯誤,任何依賴這句話收工的人都會漏清東西。

這支 hook 現在就在寫狀態檔:`~/.cache/lumos/stop-block/<session_id>`,用 `O_CREAT|O_EXCL` 佔名額、7 天才 lazy 清理。這個機制不是前一版的快照,是 2026-09-05 就有的「收工擋停只擋一次」機制,本計劃完全沒有要動它,但也完全沒有承認它存在於「回退/殘留」的語境裡。

引句:「已排除:不可逆:只讀不寫被檢查的檔,本方案不再寫任何狀態檔(這是相對前一版的主要簡化)。」

引句:「本方案不寫任何狀態檔,所以除了上述三份複本之外沒有其他殘留要清。」

而同一份文件自己在講新方案張力時已經寫過這個機制存在:

引句:「它會去建一個標記檔,建檔時要求「已經存在就失敗」,所以第一個建成的佔走名額、後面的一律擋不成」

file: `scripts/hooks/claude/check-graph-sync.py:621` `d = Path.home() / ".cache" / "lumos" / "stop-block"`,`:740-755` 的 `_stop_mark_write` 用 `os.O_CREAT | os.O_EXCL | os.O_WRONLY` 建檔、`:637-641` 7 天才清。

更嚴重的是「會不會變多」這題計劃根本沒問過自己:S1 把觸發判準從「認工具名」放寬成「這輪跑過任何 shell/編輯工具」,直接效果是**更多以前漏抓的 session 現在會第一次觸發「改了程式碼但筆記沒動」**——而每個第一次觸發的 session 都會在 `~/.cache/lumos/stop-block/` 多留一個檔(7 天內不會自己消失)。這是本方案自己造成的、可推導的殘留量變化,但「實務隱患」與「回退」兩節都沒提。

---

## Finding 2: 「使用者家目錄」其實是兩份複本,S5 的驗收沒講清楚要各自比對

severity: major
blocking: 是 — 判準:照計劃寫的驗收步驟去做,可能在只驗了一邊(通常是 Claude)的情況下就宣告回退完成,而 Codex 那份仍是舊版。

`_sync_global_hooks` 對 `claude` 與 `codex` 是兩個完全獨立的家目錄與檔案:`_HARNESS_HOME = {"claude": (".claude", "settings.json"), "codex": (".codex", "hooks.json")}`(`scripts/lumos:15992`),`_sync_global_from_project` 對兩家各跑一次(`scripts/lumos:16286-16287`:`for _h in ("claude", "codex")`),各自 copy 一份 `check-graph-sync.py` 到 `~/.claude/hooks/` 與 `~/.codex/hooks/`(`scripts/lumos:16077-16080`)。這是兩個實體檔案,不是同一份「全域複本」的兩個名字。

計劃把它們寫成一項:

引句:「使用者家目錄下的全域複本(要重跑一次安裝指令才會同步回去)」

而 S5 的人工驗收條款用的是配對語言,不是逐份語言:

引句:「再去已部署的位置對 sha256,兩邊要一致」

「兩邊」暗示一次 repo-vs-部署的二元比對,不是「repo vs N 份部署複本各比一次」。驗收條件第 6 項用「三類」修正了一點(對三類各比一次),但沒解決根本問題:如果一台機器同時裝了 Claude 與 Codex,「使用者家目錄」這一類要比對的其實是兩個檔案,不是一個;照「各比一次」的字面讀法很容易只做了一次就算過。

---

## Finding 3: 「每個接入專案的複本」沒有任何枚舉機制,跟第一版被打下來的病灶相同

severity: blocker
blocking: 是 — 判準:講不出「怎麼知道這台機器/這個人手上有哪些接入專案」,回退第 3 步就是一句沒有執行力的imperative,退不乾淨會沒人發現。

查過 `scripts/lumos` 全文,沒有任何全域登記檔記著「這台機器上有哪些專案跑過 `lumos init`」——`LUMOS_HOME` 只指向 toolchain 來源 repo 本身,`_vendored_manifest_write` 寫的是單一專案自己的 vendored 清單(給 `lumos update` 自癒用),不是「全部接入專案」的反向索引。`_vendor_toolchain` 覆寫 vendored 複本時也不留 `.bak`(純 `shutil.copy2` 覆蓋,`scripts/lumos:15470-15472`),不會製造第四種殘留,但同時也代表沒有任何機械線索告訴你「這份複本存在過」。

計劃只寫了指令性的話,沒有解法:

引句:「所以回退步驟必須三項都走完,並對每一份比對 sha256 確認一致」

引句:「這支檔會被分發到三類位置,每一份都要各自處理」

「每一份」「每個接入專案」全靠人記得自己在哪些 repo 跑過 `lumos init`。這正是第一版被回滾席打下來的同一種問題(分發出去的多份複本退不乾淨),第二版只是把它從「機制没考慮到」換成「機制考慮到了但沒有給枚舉工具」,退一半的風險原封不動。

---

## Finding 4: 版本控制查詢本身失敗時,計劃完全沒交代,且與既有慣例不一致(未查證)

severity: major
blocking: 是 — 判準:S1 與新的檔案清單查詢是兩條獨立訊號,一個成功一個失敗時會產生什麼輸出,六條條款一條都沒覆蓋,新增這條路徑等於新增一個未定義行為。

⚠ 這條是推導出的風險,不是重現出的 bug,交編排者判斷是否要求先補一條驗收條件。

本 repo 既有的「問版本控制」呼叫(`lumos impact --diff HEAD --sync-check`)遇到失敗時的既定慣例是靜默 fail-open:

file: `scripts/hooks/claude/check-graph-sync.py:600-606` — `r.returncode != 0 or not r.stdout.strip()` 時直接 `return []`,註解明寫「rc≠0 視為沒資料,fail-open 回 []」。

新方案的 S1(讀逐字稿判「這輪有沒有可能寫檔」)完全不依賴 git,而 S2/檔案清單(「工作樹上有哪些程式碼檔還沒提交」)依賴一次新的版本控制查詢。若 S1 判定「有」但這次版本控制查詢失敗(索引鎖、非 git 目錄、git 執行檔遺失、逾時),計劃六條條款、驗收條件、PRIOR-ART 段全部沒提這個情境會怎麼處理——印「0 個檔案」的荒謬訊息、比照既有慣例整段吞掉不開口、還是印錯誤?三種行為對應的後果差很多,計劃連要選哪一種都沒說。

---

## Finding 5(次要):`_hookevent.py` 的 `__pycache__` 沒被回退節提及

severity: minor
blocking: 否 — 判準:Python 的 bytecode cache 靠來源檔 mtime+size 自動失效,回退後不會讀到舊快取,不需要人手動清,只是文件宣稱「無殘留」時漏了這一類。

`check-graph-sync.py:895` 有 `from _hookevent import guard as _guard`,而 `_hookevent.py` 與 `check-graph-sync.py` 是同批被複製進 `~/.claude/hooks/`、`~/.codex/hooks/` 的檔案(`_GLOBAL_CLAUDE_HOOKS`,`scripts/lumos:15983-15989`)。以模組方式 import 會在該目錄下生出 `__pycache__/_hookevent.*.pyc`,是這次審查大綱建議查的「有沒有快取」那一類殘留,計劃完全沒提到。功能上無害(不影響 S1-S6 判定),但既然計劃在驗收條件第 5 項自己就寫了「還原前先清 `__pycache__`,否則…看到假的綠」(針對開發環境),卻沒有把同一風險意識延伸到「已部署位置」,是同一件事漏了一半。

---

## 條款逐條檢查(S1–S6)

已讀。S1–S4、S6 描述的是判定邏輯,跟回滾/殘局鏡頭無直接關聯,沒有額外 finding。

S5 是本輪重點,已在 Finding 2、Finding 3 詳細拆解:它標「靠人驗」本身可以接受(裝置分散、機械擋不了),但驗收步驟寫的「兩邊要一致」(manual 條款文字)與「對三類部署位置各比一次」(驗收條件第 6 項)兩處用詞不一致、且都沒解決「使用者家目錄其實是兩份」與「接入專案無法枚舉」這兩個具體缺口,實際擋不住「改了沒部署乾淨」的全部情境,只能擋住「完全沒跑安裝指令」這種最粗的漏法。

---

## 總結

最嚴重等級:blocker。blocking 共 4 條(Finding 1、2、3、4);non-blocking 1 條(Finding 5)。
