severity: minor

**0. 範圍說明**
- 已讀:新掛鉤 `bypass-ask-hook.py` 全檔結構、`_hookevent.py` 修剪段、鄰居 `impact-hook.py`、`dispatch-lens-hook.py`、`ci-status-hook.py`、`memory-sweep.py`、`check-graph-sync.py`,以及 `scripts/lumos` 的暫存寫入函式。
- 沒有逐 hunk 讀 `/tmp/code-代理繞閘字樣問人-r2-code.patch` 全文,也沒有載入掛鉤跑任何指令,所以沒有行為重現。
- 以下行號都是 4e87b682 這版。
- 已知偏離(d1:分類邏輯放在掛鉤內;進入點預篩在 guard 之外)沒有重報。我只確認 `entry()` 的註解(約第 906 行)有交代理由,是真的。

**問 1:分層與依賴方向**
- 依賴方向跟鄰居一致:掛鉤只往下依賴共用的 `_hookevent`,沒有反向依賴,也沒有呼叫 `scripts/lumos`。
  - 對照:`scripts/hooks/claude/impact-hook.py:924-928`、`scripts/hooks/claude/dispatch-lens-hook.py:551-555`。
- 兩處接法跟鄰居不同,結構對、寫法不同,對應下面 1 與 2 兩條。

**問 2:命名與錯誤處理**
- `_GIT_STATE = {"calls": 0, "cache": {}}`(`bypass-ask-hook.py:467`)是模組層可變狀態,在 `bypass_reasons` 開頭(約第 845 行)重置。
  - 鄰居有同形寫法:`memory-sweep.py:202-203` 的 `_PUSH_CACHE = {}`、`_FETCHED = {}`,`_hookevent.py:119` 的 `_MARKED = {...}`。判一致。
- `_Normalizer`(第 258 行)、`_Walker`(第 700 行)是私有類別,命名一致。
  - 鄰居的類別是 `memory-sweep.py:536` 的 `_Clock` 和 `:595` 的 `Tally`。判一致。
- `_Sep(str)`(第 418 行)是 `str` 子類別,拿來標記切詞時就認定的分隔符。
  - 範圍:我只 grep 了 `scripts/lumos`、`scripts/hooks/*/*.py`、`scripts/*.py`,repo 內沒有先例,是新引入的寫法。但它只在這個檔案裡用,不外露,不影響結構,判 minor。
- 暫存寫入(`_hookevent.py:87-98`)共有三種做法,對照如下:
  - `scripts/lumos:20604` 的 `_write_lf`:自己用 `os.open(O_EXCL, 0o666)` 建檔、原檔在就 `copymode`。docstring 明寫「不用 mkstemp 再改權限」。
  - `scripts/lumos:50542` 的 `_codeloop_write_dispositions`:裸 `tempfile.mkstemp(dir=…)` 加 `os.replace`,沒有 `copymode`。
  - `scripts/lumos:47710` 的 `_home_cache_write`:函式內 `import tempfile as _tf`,`mkstemp` 加 `chmod 0600`。
  - `_hookevent.py` 用的是第二種(裸 `mkstemp`,函式內 `import tempfile`)。
  - 差異:`hook-events.jsonl` 原本由 `open(f, "a")` 建成一般權限(通常 0644),修剪後被 `mkstemp` 換成 0600,沒做 `copymode`。`_write_lf` 的 docstring 正是針對這個權限漂移而選了另一條路。

**問 3:第二種做法**
- 專案原本沒有「真的 shell 詞法分析器」。既有的是:
  - `check-graph-sync.py:439-445` 的 `_segment_command`:用 `re.split` 切 `&&`、`||`、`;`、`|`,自述「Quote-aware 不嚴格」。
  - 同檔的 `_tokens_of`:`shlex.split`。
  - `scripts/lumos:27048` 的 `shlex.split`。
- 新掛鉤自寫了一整套:`_Normalizer` 做引號遮罩和 heredoc 內文剝除,`shlex.shlex(punctuation_chars=…)` 做切詞,`_Walker` 追蹤 `cd`、`export`、變數、`mktemp` 目錄。這是第二套指令切段做法,而且規模大一個量級。
- 計劃 PRIOR-ART(第 35 行)為 d1「厚掛鉤」和「逐段解析、寧可漏問」(對照審查席粗擋 d3/d4)做了交代,但**沒有交代為何不沿用 `_segment_command` 加 `shlex.split`**。
- 這套切段只在這支掛鉤內部使用,沒有跨層直呼,所以不是 major。判成「引入第二種做法」是否該升 major,標 ⚠ 交編排者裁。

**不對齊清單**

1. 
   - 引句:「sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))」
   - 事項:共用模組的載入位置不同。鄰居的 `sys.path.insert` 和 `from _hookevent import guard` 放在 `if __name__ == "__main__":` 區塊內(`impact-hook.py:922-928`),新掛鉤放在模組頂層。
   - 差別:頂層寫法用 `try/except` 加自訂 `mark` 空殼,多了一種備援形狀。
   - 這一條跟已知偏離(預篩在 guard 之外)有重疊,但「載入位置」本身沒被那段註解涵蓋。
   - 歸因:未判定。

severity: minor
blocking: 否

2. 
   - 引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
   - 事項:裸 `mkstemp` 加 `replace`,修剪後 `hook-events.jsonl` 權限從建檔預設變成 0600。`scripts/lumos:20604` 的 `_write_lf` 為此特別用 `copymode`,同檔的 `_codeloop_write_dispositions`(`scripts/lumos:50542`)則跟新寫法一樣沒做。
   - 差別:repo 內有兩種慣例,新碼選了較弱的那種。
   - 這個權限變化只影響同機其他使用者能不能讀事件檔,單人情境下是否有害我判不準,標 ⚠。

severity: minor
blocking: 否

3. 
   - 引句:「class _Sep(str):」
   - 事項:新增 `str` 子類別當分隔符標記,repo 內沒有同形先例。結構上只在本檔使用。

severity: minor
blocking: 否

4. 
   - 引句:「lex = shlex.shlex(text, posix=True, punctuation_chars="();<>|&\n")」
   - 事項:見問 3,自寫完整指令切段器,與 `_segment_command` 加 `shlex.split` 並存。
   - 計劃有 d1 解釋「厚掛鉤」,但沒解釋不沿用既有切段器。
   - ⚠ 判不準:若認定這是「第二種做法」就該升 major,若認定這是規模自然成長就維持 minor。我暫標 minor,交編排者裁。

severity: minor
blocking: 否

**固定席節點判讀**
- `Issues/code-loop守衛main-direct盲區`、`lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger`,以及其餘只列名的節點,都不影響架構一致性判斷。
  - 理由:這份改動只加掛鉤、改 `_hookevent.py` 的修剪寫法、註冊進 `scripts/merge-claude-settings.py`。
  - 沒碰 search 排除邏輯、re-inject sentinel、設計審處置閘、guard kill 的 rc 優先序。

不對齊共 4 條,其中 major 0 條(第 4 條判不準,已標 ⚠ 交編排者裁)。
