severity: major

1. refcheck 對帶空白的路徑只拿第一個詞,缺檔會誤判成存在(rc 0)
severity: major
   blocking: 是
   - diff 段:`_ref_cmdline_token` 與 `_node_code_ref_tokens(cmdline=True)`,`_refcheck_scan` 開了這個旗標。
   - 問題:反引號裡有空白、整串又不存在,就被當成「路徑加參數」,只留第一個詞。檔名或目錄名帶空白的缺檔會被截成一個存在的前綴,refcheck 回 ✓ ok、rc 0。
   - 重現:repo 內有 `src/app/m.py`,文件寫
     ```
     `src/app v2/gone.py`
     `src/app v2/other.py`
     ```
     跑 `lumos refcheck d2.md --repo <repo>`。
   - 改前(0beb6d7d 版):`✗ missing src/app v2/gone.py`、`✗ missing src/app v2/other.py`,rc 1。
   - 改後(55da596f):只印 `✓ ok src/app`、missing 0,rc 0。兩條缺檔都被吞掉,兩條還併成同一個 token。
   - 後果:`loop status --gate` 的 G1 錨共用 `_refcheck_scan`,所以設計審的引用檢查會把幻覺路徑放行。
   - 另一種表現:`src/中文 目錄/不存在.py` 與 `src/中文 目錄/ig 檔.py` 都變成 `missing src/中文`。被 gitignore 的帶空白檔名因此認不出 `ignored`。
   - 佐證:`_ref_cmdline_token` 判斷「是指令」只看有沒有空白,沒有看第一個詞之後是不是旗標(`-` 開頭)。
   引句:「if any(ch.isspace() for ch in s) and not exists(s):」

2. summary-line 與 summary-add 在非 git 專案一律 rc 2
severity: minor
   blocking: 否
   - diff 段:`_summary_write_shape_check` 先呼叫 `_drift_fix_shape_err`。
   - 重現:把有 `.lumos` 的 vault 複製到沒有 `.git` 的目錄,跑 `lumos summary-line 中文節點 "FACT: 空白" "FACT: 空白格 "`。
   - 改前:改好、rc 0。改後:`git 列不出檔案清單,沒辦法先跑筆記形狀擋`,rc 2。
   - 這是 summary-line 的行為倒退。doctor 的 S8 段對非 git 專案是「跳過」,可見工具認為非 git 專案存在。
   - 在剛 `git init`、還沒有任何提交的專案,兩個指令都正常。
   引句:「return "git 列不出檔案清單,沒辦法先跑筆記形狀擋"」

3. 否定句提醒的條件開頭詞沒有詞界,會誤吞現況句
severity: minor
   blocking: 否
   - diff 段:`_NS_NEG_COND_OPEN` 加 `_ns_neg_cond_open`,只用 `startswith`。
   - 重現(`_ns_negation_hits`):
     - 「只要求尚未上線」:改前列,改後不列。
     - 「等到期尚未付款」:改前列,改後不列。
     - 「如果然尚未」同理。
   - 「若干」「若是」靠 `_TRIGGER_STOPWORDS` 擋住了,但「只要求」「等到期」這類以條件詞當前綴的普通詞沒有擋。
   - 這是靜默漏報,不是誤報。
   引句:「return any(h.startswith(w) for w in _NS_NEG_COND_OPEN)」

4. `_ns_neg_clause_break` 把任何標點當子句記號,斜線與連字號也算
severity: minor
   blocking: 否
   - diff 段:`unicodedata.category(nxt).startswith("P")`。
   - 重現:「尚未上線前/後都一樣」「尚未部署前-測」改前列,改後不列。
   - `/`、`-`、`_` 都是 P 類。「前/後」只是並列詞,不是時序子句。
   - 實際影響偏小,因為「前」「時」緊接斜線的寫法少見。
   引句:「or unicodedata.category(nxt).startswith("P"))」

5. doctor 的 S8 段會同時印「都有家」的綠勾與「家還沒提交」的警告
severity: minor
   blocking: 否
   - diff 段:`_nodehome_ledger` 把 pending 從 homeless 移出,但 `if not (bypassed or legacy): ok(...)` 沒看 pending。
   - 重現:`src/新 檔.py` 的家只在工作目錄、未提交時,輸出為
     ```
     ✓ 每支需要家的程式檔都有家
     ⚠ 有 1 支的家還在工作目錄…
     ```
   - 兩行互相矛盾。
   - 中文節點名與帶空白的檔名本身都能正確認出,只是這個 ok 行該排除 pending。
   引句:「warn_soft([f"{f}(家:{'、'.join(h[:-3] for h in hs)})" for f, hs in sorted(_nhl["pending"].items())],」

6. summary-add 的 `--nth` 在沒給 `--after` 時被靜默忽略
severity: minor
   blocking: 否
   - 重現:`summary-add 節點 "WHY:x [出處:a] [因:b]" --nth -3` 照常寫入,rc 0。
   - 有給 `--after` 時,範圍外的 `--nth`(-1、99)都正確擋下。
   引句:「return (real[-1] + 1 if real else head + 1), indent, None」

7. 驗收條款 S32 的字面與實作對不上
severity: minor
   blocking: 否
   - 條款寫「doctor 一次跑多篇時提交索引清單應只讀一次」。
   - 實作快取的是 `_drift_probe_tree(root, "disk")`,是工作目錄樹,不是提交索引。
   - 照字面寫的測試(數提交索引的讀取次數)會對錯東西。
   - 另外 `_LINT_BORN_TREES` 是行程內全域快取,同一行程裡先建檔再 lint 會讀到舊樹。
   引句:「_LINT_BORN_TREES[str(root)] = _drift_probe_tree(root, "disk")」

固定席(圖譜鏡頭)對照:
- `lumos-cli-read` 的 search 合約、`guard-kill` 的 rc 優先序與 JSON 純度、`design-loop` 的處置閘第五步、`測試假綠形態`:這份 diff 沒碰 search、guard kill、處置閘或還原翻紅釘,判不影響。
- `筆記內容閘`:有碰(否定句提醒),見第 3、4 條。
- `pitfalls-code-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`:規格閘推送前檢查新增讀治理帳。
  - 治理帳壞或路徑不合時,只要有 doing 或被改到的 done 計劃,推送就會被擋。
  - 這是設計內的 fail-closed。
  - `_gov_vc_gate_events` 對壞行跳過,所以壞一行不擋。

沒找到問題的邊界:
- 中文節點名、帶空白檔名、新 repo 沒有提交、`--after` 空字串或找不到,summary-add 與 S8 都正確。
- 行分隔字元 U+2028 在 summary-add 被擋。
- lint 的「已排除」行對 U+2028、全形冒號、引用塊、圍欄內、散文都符合 S15。
- `_git_ignored` 先剔除含 `..` 的路徑,文件裡的 `src/../../etc/passwd` 照回 missing,git 沒有中止。

臨時目錄 `/private/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/邊界-sonnet` 已刪。

最嚴重 severity:major;blocking 共 1 條(第 1 條)。
