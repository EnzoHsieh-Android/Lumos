severity: major

## F1 複本守衛改成掃全部後,巢狀定義的複本會被完全跳過、guard 照樣全綠

severity: major
blocking: yes

守衛把偵測方式從走訪整棵 AST(`_ast.walk(tree)`)換成只看模組最外層陳述式(`for n in tree.body:`),用來找 `_ci_latest_attempts` 定義與 `_CI_RED`/`RED` 常數。只要有一份複本被包在任何一層區塊裡(`if`、`class`、另一個函式……),這個掃描完全看不到它,而且不是「看到了但比對失敗」,是**根本沒被列進 `bodies`**,連帶也不會被拿去跟主程式比對邏輯是否一致。

引句:「        for n in tree.body:」

引句:「    files = [base / "lumos"] + sorted((base / "hooks").rglob("*.py"))」

實測:把整個 repo 複製到 `/tmp/r2check/repo`(不動原 repo),在 `scripts/hooks/codex/fake-ci-hook.py` 塞一份**刻意寫錯**的 `_ci_latest_attempts`(退回 r1 之前 `att >= cur[0]` 的舊邏輯,同一次嘗試不會偏向紅),但包一層 `if True:`。跑 `python3 scripts/test_lumos.py -k ci_latest_attempts`:

```
✓ ① 現場成立:至少找到主程式與開場提醒 hook 兩份
✓ ② 找到的複本都比對了
✓ ③ 所有複本的程式一模一樣
✓ ④ 函式裡的紅燈集合跟各檔自己的常數一致
4 passed, 0 failed
```

四條全綠。接著把同一支檔案的函式改回**最外層**(不包 `if True:`,邏輯照樣錯)重跑,守衛立刻抓到:

```
✗ ③ 所有複本的程式一模一樣  跟主程式不一致的:['fake-ci-hook.py']
✗ ④ 函式裡的紅燈集合跟各檔自己的常數一致  ...
2 passed, 2 failed
```

兩次唯一差別是那份錯誤複本有沒有包一層區塊,證實問題就出在 `tree.body` 只看最外層。這正好是這輪攻擊清單點名的情境(巢狀定義會不會讓守衛安靜少比一份),而且不是假設——是這份 patch 自己在 r2 docstring 裡講的動機(「都踩過『寫死三支、漏了第四支』才改成掃全部」)沒有真正達成:掃描本身確實不寫死清單、會找到 `hooks/` 底下新加的檔案,但只要那份複本(或未來任何一份,包括萬一以後加的 Codex 專用子目錄那份)被包進任何一層區塊,就會從比對名單裡消失而不觸發任何斷言失敗。這輪 r2 的核心交付就是「守衛掃得到全部」,但掃描深度本身就有一個現在能重現的破口。

## F2 同一次嘗試兩筆結論都不是紅時,順序仍然決定結果,跟註解宣稱的「不看先後」不符

severity: minor
blocking: no

引句:「        # 嘗試次數大的贏;同一次嘗試有兩筆結論不同時留紅的(順序不定時往安全那邊倒)」

`red = (r.get("conclusion") or "") in ("failure", "timed_out", "startup_failure")`,同一次嘗試撞兩筆時只有「其中一筆是紅」才會蓋掉另一筆;若兩筆都不紅(例如 `cancelled` 對 `success`),誰先寫進帳誰就贏。實測(用 repo 現有 `scripts/lumos` 裡的函式本體,未修改):

```python
rows1=[{"run_id":5,"attempt":1,"conclusion":"cancelled"},{"run_id":5,"attempt":1,"conclusion":"success"}]
rows2=[{"run_id":5,"attempt":1,"conclusion":"success"},{"run_id":5,"attempt":1,"conclusion":"cancelled"}]
# order A → ['cancelled']    order B → ['success']
```
兩種順序給出不同答案。作者自己在說明裡把「同次嘗試撞兩筆」標成「不該發生」的異常情況,而且攻擊清單也點名了這個情境,所以降級為 minor:不影響「紅/綠」這個主要安全屬性(紅永遠贏),只有在資料本身已經異常、且兩邊剛好都不是紅/綠這種二元結論時,輸出才會不穩定。建議至少在 docstring 把「不看先後」的適用範圍收窄成「其中一筆是紅的時候」,避免以後有人照字面當成全稱命題來用。

## 已驗過、沒問題的部分

- `scripts/lumos` 與 `scripts/hooks/claude/ci-status-hook.py` 兩份 `_ci_latest_attempts`(patch 這兩處改動)目前都是模組最外層定義,`python3 scripts/test_lumos.py -k ci_latest_attempts`、`-k ci_rerun_latest_attempt_wins`、`-k ci_wait_rerun_records_latest_attempt` 三支全部實際跑過,7+2+4 條斷言全線 ✓,包括新增的端到端測試(`t_ci_wait_rerun_records_latest_attempt`,真的用假 `gh` 連跑兩次 `ci-wait` 再讀 `ci-status`)。
- `str(rid)` 轉型:確認 gh 回傳的 `run_id`/`databaseId` 一律是整數或整數字串,不會因為轉字串而把兩個本來不同的執行誤判成同一個(沒有 float 或帶前導零的路徑)。
- `~/.claude/hooks/ci-status-hook.py`(本機安裝的全域複本)目前確實落後、還沒有 `_ci_latest_attempts`——但這是 `scripts/lumos` 裡 `_vendor_toolchain`/`copy2` 全域同步機制(`lumos install`)負責的範圍,不是這支測試守衛的職責;守衛本來就只保證 repo 內原始碼互相一致,裝到全域是另一條路徑,不算這輪 patch 的缺陷。
- `files = [base / "lumos"] + sorted((base / "hooks").rglob("*.py"))` 對 `hooks/` 底下新增子目錄(用來模擬 Codex 專用子目錄)的偵測本身沒問題——`rglob` 是遞迴的,新檔案只要函式定義在最外層就抓得到、抓到後也真的會比對(F1 的對照組已證實抓到會噴 ③④)。破口只在「抓到檔案」之後、「找函式定義」那一步的巢狀盲區(即 F1)。
