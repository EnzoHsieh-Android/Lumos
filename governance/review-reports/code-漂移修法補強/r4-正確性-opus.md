severity: minor

# 正確性-opus 第 4 輪(驗收 43270394 的處置)

查證範圍與結論摘要:
- 刪除守衛撤回:`git diff 9cc20926 43270394 -- scripts/lumos` 裡沒有任何一行落在刪除守衛；把兩版 `_delguard_is_diff_header` 到 `cmd_delguard_check` 整段(9cc20926 第 29210–29620 行、43270394 第 29316–29726 行)抽出來 `diff`,輸出為空,**一字不差**。`_delguard_vendored_skips`、`_delguard_vendored_note`、`added_skip`、`vendored_skip` 參數、`_delguard_path_flags` 等三支小函式在 scripts/lumos、scripts/test_lumos.py、scripts/hooks、skills 全部 grep 不到。檔內還剩的 `_vendored_skip` 與 `vend_skip` 用在每支檔有家和 pitfalls,9cc20926 本來就有，不是殘留。commands/08 跟 9cc20926 相同。
- 殘留測試:test_lumos.py 在 9cc20926..43270394 之間跟刪除守衛有關的差異只有新加的 `t_delguard_scans_vendored_files_in_consumer`;前幾輪測跳過行為的測試都已經不在。`_DRIFT_C4_DIRS_MAX`、`_drift_c4_more_cmd` 在程式和測試裡都 grep 不到。
- 新測試還原後會不會翻紅(在 `git clone --shared` 出來的目錄裡做，換掉 scripts/lumos 並清掉 __pycache__):
  - 換成 b52d6f02(只比檔名)、b002ca4a(比指紋、讀工作目錄)、7b660203(改前改後兩態)三個版本:②③都翻紅(`"hits": []`、note 帶 `vendored-skip=1 files=scripts/lumos`),①前置斷言照綠。
  - 換成 9cc20926:3/3 綠。
  - 換成 5cb96d89(帶 20 個上限的版本):`t_drift_c4_lists_all_dirs` ②翻紅。
  - 把比對鍵改成只做 casefold:`t_drift_c4_code_review_r2` ②⑥翻紅。
  - 把比對鍵改成只做 NFC:`t_drift_c4_code_review_r3` ①②翻紅。
- 比對鍵實際輸出(直接在程式裡呼叫 `_drift_c4_same_commit`,git 那一步換成假的):

| git 裡的名字 → 現存目錄 | 印出 |
|---|---|
| NFC `code-卷證é` → 磁碟上 NFD 那一個 + other | NFD 那一個 |
| NFD `code-é` → NFC | NFC 那一個 |
| `Code-Review` → `code-review` | `code-review` |
| NFC `CODE-É` → NFD `code-é` | NFD 那一個 |
| `code-foo` → `Code-Foo`、`code-foo`、`CODE-FOO` | 三個都列 |
| NFC `é` → NFC 與 NFD 兩個都在 | 兩個都列 |
| `A`、`a`、NFD `é`、NFC `é` → `a`、NFC `é` | `a`、`é` 各一次(有去重) |
| 已刪的 `gone` | 不列 |
| 只有兩段路徑的散檔 | 不列 |

  在真的 macOS 磁碟上從頭跑一次:提交 `Code-Café`、`Plain` 後，只在磁碟上改名成 NFD 的 `code-café` 和 `plain`。證據頁印出的兩行都是磁碟上的名字、標「同提交」,回傳碼 0。
- 回歸子集:`-k delguard` 100/0、`guard_kill` 50/0、`guard_settle` 38/0、`set_condition` 88/0、`drift_fix` 146/0、`drift_c4` 26/0、`bound_tests_g` 16/0、`reinject_preserves_outside` 3/0。
- 筆記殘句:計劃(第 22、27、32–33、58–62、76、84、93、95、103、117、145–147 行)、Systems/delguard、Systems/存量漂移守衛、Issue、commands/03、04、08 都已經改成撤回後的說法。講舊行為的句子只剩在〈實作紀錄〉和〈審計修正紀錄〉裡，那是照時間記的歷史，後面都接了撤回紀錄，不算殘留。delguard 那行 REVISIT 改成縮排後，`_revisit_split` 會先去掉行首空白，照樣會被讀到。三篇 `lumos lint` 都是 0 問題。

## F1 比對鍵加上 casefold 後，分大小寫的檔案系統上，只差大小寫的另一個目錄也被標成「同提交」

severity: minor
blocking: 否
引句:「比對鍵對到好幾個現存目錄(分正規化或分大小寫的檔案系統才會有)才每個都列。」
file: `scripts/lumos:27997`
file: `scripts/lumos:28001`
file: `scripts/lumos:28016`
file: `scripts/test_lumos.py:53795`

1. 情境:Linux 這類分大小寫的檔案系統(例如 CI)。那篇驗證紀錄第一次被提交的那個提交加了 `governance/review-reports/code-foo/`;另外有一個跟這次無關的現存目錄 `Code-Foo`(別的計劃的卷證)。
2. 走到 `_drift_c4_same_commit`:git 裡的 `code-foo` 算出比對鍵 `code-foo`,對到 `by_key` 裡的兩個現存目錄，兩個都放進同提交清單。接著 `_drift_c4_dirs` 把兩個都標成「同提交」(如果計劃名也對得上，就標「兩者」)。
3. 重現(假 git，只換 `_nodehome_git`):
   `m._nodehome_git = lambda _r, *a: b"governance/review-reports/code-foo/r1.md\0"; m._drift_c4_same_commit(".", "abc", {"code-foo", "Code-Foo"})`
   - 43270394 → `['Code-Foo', 'code-foo']`
   - 5cb96d89(第二輪只用 NFC 當鍵)→ `['code-foo']`
4. 壞在哪:證據頁的說明寫「同提交=這篇第一次提交時一起加進來的」,是一句肯定的說法(「可能漏或多」只掛在計劃名那一種)。`Code-Foo` 並不是那個提交加的，卻被標成同提交。這個誤標是這次加 casefold 才帶進來的：原本要解的是「不分大小寫的檔案系統上只有一個現存目錄」,在分大小寫、而且字面完全相符的目錄就在那裡時，不需要再放寬。測試 ② 把「兩個都列」釘成預期行為。
5. 影響有限：範本不自動填，人還是要自己從清單挑；兩個卷證目錄只差大小寫也很少見。所以列為 minor。有字面完全相符(NFC 後相同)的現存目錄時只取它，沒有才退到 casefold 鍵，兩種檔案系統就都對。

## 圖譜鏡頭固定席逐條判定

- Systems/存量漂移守衛(家):c4 證據頁的說法跟程式一致(全部列出、NFC 再 casefold、印現存名字)。唯一的偏差見 F1(說明寫一個現存目錄一行，實際上一個 git 名字可能對到好幾個現存目錄都標同提交),不破壞它的 WHY 行。
- Systems/bound-tests-gate ★INVARIANT★:這次沒改 code-loop check 或綁定測試的邏輯。`-k bound_tests_g` 16/0。不影響。
- Systems/guard-kill ★INVARIANT★ ×2(rc 優先序、--json 純度):這次只動到 settle 的訊息函式(前幾輪已審),沒碰 guard kill。`-k guard_kill` 50/0。不影響。
- Systems/授權與歸屬 ★INVARIANT★ ×2:`_VENDORED_TOOLKIT` 和 `_VENDORED_ALL` 都沒改(新測試只是讀 `_VENDORED_ALL`),檔頭沒動。不影響。
- Systems/測試假綠形態 ★INVARIANT★(翻紅釘要附前置斷言):新測試 ① 證明現場成立(消費專案、確實有刪除行、scripts/lumos 在工具檔清單裡)。上面換成三個歷史版本時 ① 照綠、②③翻紅，所以不是走不到被測那條路的假綠。符合。
- Systems/lumos-cli-read ★INVARIANT★(search 排除 superseded):沒碰。不影響。
- Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 保留 sentinel 以外的內容):沒碰。`-k reinject_preserves_outside` 3/0。不影響。
- Systems/design-loop ★INVARIANT★(處置閘第五步):沒碰。不影響。
- 只列名、超出上限的那些節點(pitfalls-code-loop、lumos-deinit、delguard 等):刪除守衛的程式跟 9cc20926 一字不差，只多一條 WHY 行和一支測試。其他節點牽涉到的函式在 9cc20926..43270394 的差異裡沒有出現。不影響。

最高等級:minor
