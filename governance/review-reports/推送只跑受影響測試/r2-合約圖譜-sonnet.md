severity: major

我沒有改任何判斷或等級,只補了引句。每句都用 grep 對過凍結快照,各出現一次。

**固定席逐條必答(合約與圖譜一致)**

- ★INVARIANT★ `Systems/bound-tests-gate`:這份設計沒有破壞它。那條合約管的是 `code-loop check` 對合約綁的測試逐支真跑,走獨立的閘。本計劃只動「全套測試分片」那一段,不碰合約測試真跑。
- `Systems/slim-install-安裝器` 的 CLAUDE.md 注入合約(sentinel 以外 byte-equal、冪等)、`lumos-cli-lifecycle` 的 re-inject 合約:沒有破壞。做法 5 只改範本,走既有的注入路徑。不過做法 5 沒說要跑哪個指令,見 finding 3。
- 範本大小:doctor Check D 的 150% 提醒線早已超過。範本現在 13320 bytes,基線 5256。那條只是警告,不影響這次改動。

---

severity: major
blocking: 是(照字面實作會讓「無法判定」的推送也跳過全套,漏掉現行的安全兜底)
段落:〈做法〉第 2 點。
引句:「這個 ref 原本判 `full` 時改判 `light`(沿用 `_SUITE_LIGHT`,不新增狀態)」
問題:現行 `_suite_this` 預設就是 `full`,有三種情況也會落在 `full`。
- 一是 `pitfalls --json` 失敗或回空。現行寫 `|| true`,所以算不出來時是 fail-closed,走全套。
- 二是 `light_ok` 為假,也就是範圍裡有測試檔、skills、workflow 這類既非文件也非程式的檔。這是 r1 資安席特別補的洞。
- 三是 spec-gate 沒判 light。

「原本判 full 就改判 light」會把這三種全部降級。
- `_SUITE_KEYS` 只在 `light_ok` 那段才從 `pf_json` 取。spec 說「照現行取」,但現行取的位置在被降級條件包住的區塊裡。
- 照字面做,pf_json 為空時 `affected_keys` 會是空的,掛鉤退成只跑文件子集,什麼都不比對。
- 改到測試檔本身(幾乎每個功能推送都會)、改到掛鉤或 `scripts/lumos` 這類守衛檔,也只剩「原始碼整字提到函式名」的小子集。守衛檔改壞了,本機測不到。

spec 沒寫保留哪些 fail-closed 條件。〈實務隱患〉也沒提到「算不出來」和 `light_ok` 這兩條現行安全兜底。
佐證:
file: `scripts/hooks/pre-push:488-497`
file: `scripts/hooks/pre-push:567-578`
file: `scripts/lumos:61914`

---

severity: major
blocking: 是(S1 沒覆蓋會變的既有行為,實作者會做出不同的結果)
段落:〈做法〉第 1、2 點與 [S1]、[S3]。
引句:「目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支」
問題:
- 這條判法的套用範圍比「推功能分支」大。
- release/hotfix/develop 這類長壽分支,或 git-flow 的整合分支,也會被降級。`_push_mainlines` 的註解就說這個 repo 要顧 git-flow 與 fork 兩種主線形狀。
- 這類分支不一定走 PR,也不一定有 CI。`ci.yml` 的 push 觸發只有 `branches: [main]`,PR 才跑全套。
- 於是「推功能分支 → 全套由 PR 的 CI 跑」這個前提,對「還沒開 PR」和「根本不開 PR」的分支都不成立。
- 訊息「全套由 PR 的 CI 跑」在開 PR 之前是不實的。
- 〈範圍〉和 Q2 只處理了「合併前要綠」,沒處理「沒有 PR 就沒有 CI」。

另一個缺口:S1 只列「功能分支、main、標籤」三種,沒有「其他長壽分支」「多 ref 混推時單一功能分支 ref 的訊息」。
佐證:
file: `.github/workflows/ci.yml:5-10`
file: `scripts/lumos:65263-65275`

---

severity: major
blocking: 是(做法 5 的文件同步沒列全,條款 S4 也無法證明規則沒有半新半舊)
段落:〈做法〉第 5 點,以及 [S4]。
引句:「用安裝程式重新注入 `CLAUDE.md` 與 `AGENTS.md`」
補充引句:「不再出現「全套留給推送前的閘」」(此句出自 S4 條款,因含「」故不單列為引句行)
問題:
- **注入指令沒寫**:spec 只說「用安裝程式重新注入」,沒給指令。目標清單由 `_reinject_targets` 決定,doctor Check D 只會警告漂移,不擋。S4 因此要自己驗兩檔。
- **「不再出現」的斷言不成立**:S4 說兩檔的紀律區塊不再出現那句話。但專案 `CLAUDE.md` 紀律區塊外第 98 行也有「全套…留給推送前的閘」。S4 要限定在 sentinel 區塊內才不會誤判,spec 沒有限定。
- **現有守衛測試**:`scripts/test_lumos.py:54911` 的測試只查「相關的測試子集」在範本裡,不查「留給推送前」。改寫後它仍綠,但也守不住新句子。S4 的新測試要自己讀範本和兩檔。
- **其他沒列進去的同步點**:
  - `skills/lumos-project-notes/commands/08-自動跑的.md:7` 寫「pre-push:…全套測試」,仍是舊行為。
  - `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md` 第 47 行寫「其餘全套」「CI 對 light 照跑全套當後盾」。spec 只說「補一句」,但整行的邏輯是「light 才少跑」,功能分支現在也少跑,要改的是那一行的結論。
  - 掛鉤本身的訊息:`_suite_word` 寫「這次沒改到程式、或改動判成 light」,功能分支降級的情況不屬於這兩種,會誤導。做法 3 只加一行,沒改這句。
- **父計劃連結**:做法 5 要在父計劃 `Projects/推送與CI提速_計劃` 的 REVISIT 加 `[closed:]`。我查了,該檔第 76 行確實有那條。spec 沒說 `[closed:]` 的寫法,可對照 `Projects/漂移防治路線圖_計劃.md:31`。
- **全域規則**:Q1 說的 `~/.claude/CLAUDE.md`「不要只跑針對性測試或守衛測試就推」在這個 repo 之外。上線後這句與新規則會互相矛盾,而 Q1 還是「待查」。

佐證:
file: `scripts/test_lumos.py:54911`
file: `CLAUDE.md:98`
file: `skills/lumos-project-notes/commands/08-自動跑的.md:7`
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:47`
file: `/Users/enzo/.claude/CLAUDE.md:13`

---

severity: minor
blocking: 否(文件精度)
段落:〈做法〉第 4 點(`run_group` 回 3 的判法),與 [S2]。
引句:「改成每片都回 3 才算一支都沒選到」
問題:
- 現行函式說明寫「回傳 3=每片都選中 0 支」,程式實際是「任一片 rc3 就回 3」。spec 把問題描述對了,修法也合理。
- spec 說 `_krc_all3` 宣告了沒用到,我查到它在掛鉤第 897 行宣告,陳述屬實,不是錯誤。
- 修的位置在 `run_group` 內,「每片都 rc3 才回 3」要把 `_any3` 改成計數,spec 沒寫具體改法。
- 既有測試 `t_prepush_docs_and_light_run_subset` 用 `FAKE_KEYS_RC` 假執行器,所有片回同一個值。要驗證「部分片 rc3、部分片 rc0」需要新的假執行器。S2 沒說這點。

佐證:
file: `scripts/hooks/pre-push:897`
file: `scripts/hooks/pre-push:914-945`

---

severity: minor
blocking: 否(措辭與可執行性)
段落:`RETIRE-IF` 的數法。
引句:「對照同提交的推送前檢查紀錄」
問題:
- PR 常被 rebase 或 squash,提交編號會變。
- 推送前掛鉤是否留下「本機綠」的紀錄也沒寫。我查過掛鉤,測試套件閘通過後的紀錄看起來只有訊息,沒看到進治理帳。

這條撤除條件目前機器數不出來。
佐證:
file: `scripts/hooks/pre-push:960-990`

---

**實務隱患逐類**
- 守衛面:見 finding 1,fail-closed 條件被降級是這份設計最大的洞。
- 併發:已讀,無 finding。
- 金流、對外送出、不可逆:已讀,無 finding。

**已讀,無 finding 的段落**:〈舊否決對照〉、〈現況〉(`ci.yml` PR 事件確實全套;`main` 保護 FACT 未驗,屬外部事實)、〈回退〉、〈審計修正紀錄〉。

最嚴重等級是 major,會擋的問題共 3 條(finding 1、2、3),另有 2 條 minor 不擋。
