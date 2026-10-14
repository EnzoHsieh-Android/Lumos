severity: major

我量到一個會超過外層預算的形狀,另有兩條 minor。

**1. 2 萬字內塞滿「落在暫存目錄的命中段」,hook 超過 5 秒外層預算**
severity: major
blocking: 是
引句:「timeout=_inner_budget(default=5.0))」

- **輸入**:一條 2 萬字內、約 260 段的指令。每段是 `git -C /tmp commit --no-verify;` 或 `git -C /tmp push --no-verify origin;` 這類,目錄存在且在暫存根底下。
- **走到哪**:`_Walker._command` 對每個命中段呼叫 `_exempt`。`commit` 走 `_not_real_repo`,`push` 走 `_push_target_temp`,兩者都會用 `_git_out` 各起一個 git 子程序。
- **出什麼錯**:`_inner_budget` 回「剩餘時間,下限 1 秒」,只限制單次子程序。沒有全域的子程序次數或總時間上限,段數也沒有上限(`MAX_LEN` 只擋字數)。預算用完後每次呼叫仍給 1 秒,所以 git 稍慢或卡住時,總時間 = 段數 × 1 秒。
- **失敗後果**:外層 5 秒一到,Claude Code 殺掉 hook,這條指令沒有跳「問人」就放行。這是「寧可漏問」的設計,但這個形狀正是繞閘會用的形狀(用重複段把命中埋進去),不是隨機壞輸入。
- **實測**(`bypass_reasons(cmd, "/tmp")`,git 正常、無卡住):
  - 262 段 `git -C <存在的暫存目錄> commit --no-verify;`:6.96 秒,回 `[]`。
  - 約 520 段 `git -C /tmp push --no-verify origin;`:11.55 秒,回 `['no-verify']`。
- **預算起點**:`_BUDGET_START` 在第一次呼叫 `_inner_budget` 才記,不是行程開始。這裡之前花掉的解析時間沒被扣。
- **應該是**:在 `bypass_reasons` 或 `_git_out` 層加總預算守衛,例如累計子程序數上限(約 3 次),超過就改用不查 git 的保守判斷(照命中算、寧可多問),或檢查整體 deadline。

file: `scripts/hooks/claude/bypass-ask-hook.py:306`(`_git_out`),子程序呼叫點在 `_not_real_repo` 與 `_push_target_temp`。

**2. 存活事件檔的修剪用固定暫存檔名,多個會談同時修剪會互相蓋掉**
severity: minor
blocking: 否
引句:「if not _go:」

- **說明**:這條不是新 diff 引入的程式,`_hookevent.py` 不在 diff 內,diff 只是讓它更常被觸發。引句取自 `bypass-ask-hook.py` 裡「預篩在 guard 之外」的接線,過了預篩的每條 Bash 都會記一筆。
- **走到哪**:`record()` 在檔案超過 512KB 時,讀整檔、取最後 2000 行、寫入固定名稱的 `hook-events.jsonl.tmp`,再 `os.replace`。
- **會出什麼錯**:兩個會談同時修剪時,會寫同一個 `.tmp`,後到的可能把另一方寫到一半的內容換上去。讀檔到改名之間別人 append 的行也會丟。
- **未能重現**:我沒有造出並行修剪的場景,所以沒有實測。
- **擠掉其他掛鉤紀錄**:預篩的 `-[a-z]*n[a-z]*` 只要原文同時含 `git`、`commit` 和任何含 n 的短旗標就過。我測到 `git log | grep commit; find . -name x` 這種純讀指令會過。過預篩的比例因此高於命中。修剪是留最後 2000 行,commit 密集的工作階段可能把 memory-sweep 這類低頻掛鉤的存活紀錄擠出去。我沒量到實際比例,所以只列 minor。

**3. `MAX_LEN` 的註解和實際最壞情形不符**
severity: minor
blocking: 否
引句:「MAX_LEN = 20000                     # 超過就不做結構分類,走字面判(shlex 對超長單詞是超線性)」

- 註解說慢在 shlex,但我實測的純解析形狀都不慢:
  - 括號、引號、反斜線、`$(` 這幾種形狀在 2 萬字內 ≤0.02 秒。
  - 5000 個 `<<A\n` 的未結束 heredoc 約 1.6 秒(`_drop_bodies` 每個換行都掃到結尾,是平方級)。
  - 1 萬個 `` `a `` 的反引號約 0.4 秒。
- 這些都在 5 秒內,所以不構成缺陷。真正的最壞路徑是 finding 1 的子程序累加,註解沒提。應該把註解改成指向子程序數量,或把 finding 1 的上限寫進去。

**其他項目,逐項判定(都沒找到問題)**

- **成本**:`echo '{}'` 空跑一次總計 0.053 秒;預篩只做子字串與一個正規式,不啟動 `_hookevent` 以外的子程序。
- **正規式**:`_PRE_SHORT_N`、`_ASSIGN`、`_expand` 都是線性,無回溯爆炸。
- **子程序釋放**:全用 `subprocess.run(timeout=)`,逾時會殺子程序。找不到 git 或權限問題都落入 `except` 回 `(None, "")`,不會拋出,也沒有開著沒關的檔案描述子。
- **`sys.path.insert(0, 本目錄)`**:放在 import `_hookevent` 前,只影響這支 hook 自己的行程,沒有副作用。
- **固定席節點**:這份 diff 不影響各節點宣稱的行為。
  - lumos-cli-lifecycle:`re-inject` 只覆蓋 sentinel 之間 body,diff 只動安裝名單、enforcement 列、錨點名單,沒碰這段邏輯。
  - lumos-cli-read:`search` 沒被碰。
  - guard-kill:`guard kill` 的 rc 優先序與 `--json` 純度沒被碰。
  - design-loop、測試假綠形態:diff 沒碰設計審處置閘,也沒改既有「還原翻紅釘」測試;新增測試是否帶前置斷言不在我的鏡頭內。

最嚴重 severity:major,blocking 共 1 條。
