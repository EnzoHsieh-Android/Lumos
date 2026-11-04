severity: minor

邊界席第 4 輪報告。我找到 4 條 minor,沒有 major 或 blocker。補充說明:實驗在 `git worktree add --detach` 的複本上做,沒動 `/Users/enzo/harness/lumos-green-scope` 的檔案。

1. SHA-256 repo、治理帳進版控(或判不了有沒有被忽略)、HEAD 在主線上或分離 HEAD 或沒有主線時,`_redbase_branch_rows` 仍走 SHA-1 空樹常數,整段判綠觀測與去重失效。
   - 修補只在帳被忽略的路徑繞開空樹,同族的另一條路沒掃。
   - 重現:`git init --object-format=sha256 -b main`,提交一次,把含 `spec-gate-green` 的帳 `git add` 並提交,留在 main 上呼叫 `m._redbase_branch_rows(d, "甲", "not", 30)`。
   - 結果:回 `[]`,stderr 印「讀不出起點那一版的治理帳」。換成 `--object-format=sha1` 的同樣操作回 2 筆。`"unknown"` 的結果相同。
   - 後果:這條路上判綠過的測試,之後判紅會存一份實作後的紅燈版。SHA-256 repo 罕見,而且有印訊息,所以只算 minor。
   - 引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」
   - file: `scripts/lumos:14444`
   - 歸因:有證據的原有漏查。修前 fe970227 與修後 ae9c4d82 跑同一支腳本,sha256 兩邊都回 0 筆並印同一句,sha1 兩邊都回 2 筆。
severity: minor
   blocking: 否

2. `_git_bool` 與 git 的布林規則在三處不符,文件也對不上。
   - 我拿 `git config --type=bool` 跟 `_git_partial_clone` 逐值對照,一共試了 39 個值。
   - `promisor = 0k`、`0K`、`0m`:git 算假,lumos 算真。git 的整數接受 k/m/g 字尾,`int(v, 0)` 不認,走 `ValueError` 回真。這個方向保守(多判成部分複製),但修前這三個值是判假(對的),所以是修補引入的差異。
   - `0_0`、`00_0`、`0b0`、`0o0`:Python 的整數寫法被 `int(v, 0)` 吃下判假,docstring 卻寫「git 認不得的寫法算真」。這幾個值 git 自己會 `fatal: bad boolean`,實際影響很小。
   - `t_git_partial_clone_keys` 只釘 false、0、空字串、2 和裸鍵,沒有釘 `0x`、八進位、單位字尾,也沒有釘 git 會拒絕的值。
   - 其餘結果與 git 一致:`TRUE`、`010`(八進位 8,真)、`00`、`0x0`、`-0`、前後空白,另有 17 個值一致。
   - 引句:「return int(v, 0) != 0」
   - file: `scripts/lumos:12035`
   - 歸因:`0k` 這類是有證據的修復回歸(保守方向);`0_0` 這類是修補新程式本來就有的缺口。
severity: minor
   blocking: 否

3. 驗收條款 S8 的文字與程式、測試矛盾。
   - 條款寫「HEAD 解不出…應整批照舊算進來(不過濾)」。
   - 程式與測試實際行為是 HEAD 沒有提交時,先照分支名丟:`_redbase_on_branch` 的 a 步在 b 步前面,`ref` 不同的列被丟。
   - 測試 `scripts/test_lumos.py:124046-124049` 斷言「分支名不同照丟」,我在修後樹跑是綠的。
   - 修前版本的條款是「照舊算進來並印一句說明」,沒有「不過濾」。這句是 r3→r4 的修補新加的,所以這處不一致是修補引入的。
   - 影響只在文件:照條款寫實作的人會把 ref 過濾也拿掉。
   - 引句:「HEAD 解不出或判不了治理帳有沒有被忽略時應整批照舊算進來(不過濾)」
   - 歸因:有證據的修復回歸。
severity: minor
   blocking: 否

4. 部分複製加帳進版控時,判綠觀測與去重整個停用,但使用者看得到的限制清單沒寫,fixture 在非 Linux 還有空轉。
   - 停用是本輪修補新加的:修前版本 `_redbase_branch_rows` 的非忽略路徑沒有部分複製檢查,直接讀分岔點那一版。這項取捨計劃天花板六有寫。
   - 但 `_TG_LIMITS`、`test-quality-standard.md`「抓不到」清單、`Systems/規格閘` 的 WHY 只寫帳被忽略的限制,漏了部分複製的情形。
   - 結果是 blobless clone 的使用者,判綠過的測試之後判紅也會存實作後的紅燈版,清單卻說「判綠過的不存」。
   - fixture 的問題有兩個:
     - Windows 上 `if sys.platform != "win32":` 把「查不到的提交會去連遠端」的前置跳過,`not mark.exists()` 兩條永遠成立,「沒有為了判祖先去連遠端」在 Windows 空轉變假綠。
     - `git init --object-format=sha256` 失敗時整段靜默略過,不會標記略過,舊 git 的 CI 上 K6 完全沒跑卻仍綠。
   - 在 TMPDIR 掛 noexec 或路徑含空白的 CI 上,留記號腳本跑不起來,前置會假紅。
   - 引句:「if sys.platform != "win32":   # 遠端抓取程式換成留記號就失敗的小腳本:有記號 = git 為了查不到的提交去連遠端了」
   - file: `scripts/test_lumos.py:124075`
   - 歸因:限制清單缺漏是有證據的修復回歸;fixture 的 Windows 與 SHA-256 略過是新測試本來的缺口(未判定先前版本)。
severity: minor
   blocking: 否

**已驗主張的證據**
- `_git_partial_clone`:
  - 真的 `git clone --filter=blob:none --no-local` 後,config 只有 `promisor=true` 加 `partialclonefilter=blob:none`,沒有 `extensions.partialclone`,函式回 True。
  - 遠端名含空白、裸鍵、`promisor = 2`、`promisor = false` 一律與 git 的結果一致。
- 分支名與 ref:`feat/功能一`、`功能`、80 字元加斜線加 80 字元、同名 tag,寫入的 `ref` 都等於讀取端的 `name`,自己的判綠都留得住。NFD 的 `éx` 會被 `_note_reread_show` 正規化成 NFC,但寫讀兩端一致。
- 模糊輸入:78 種 `ref`、`head_sha` 組合(含 None、整數、list、dict、大寫 hex、39 字元、尾端換行、`HEAD`)加壞 JSON 與 10 萬層 `[`,`_redbase_branch_rows` 與 `_redbase_branch_state` 都沒崩。
- `fullmatch` 不被尾端換行騙過。
- 改壞驗證:
  - 在複本上把 `_TitleIndex._join` 改成每次重算,`t_name_collision_scales` 的「同一份」檢查翻紅(1000 次拿到 515 個不同 id)。`id()` 在記憶體位址被重用時理論上可能誤判相同,但實測仍抓得到。
  - 把 `_TG_CONST_PAT` 的三引號段拿掉,S4 翻紅。
- 相關測試全綠:`t_spec_gate_redbase`(61 案)、`t_tq_guard_cli_contract`(99)、`t_name_collision`(22)、`t_drift_born`(27)。

**三問**
1. **原問題修復效果**:把修後的測試放到 fe970227 的程式上跑。
   - `t_git_partial_clone_keys`:修前紅 4 條(裸鍵、`promisor = 2`、含空白遠端判錯、判不了的回頭條件),修後 21 條全綠。
   - `t_redbase_branch_rows_fallback_keeps`:修前紅 2 條(S10 部分複製讀分岔點、SHA-256),修後 22 條全綠。
   - `t_tq_guard_string_comma_args` 與 `t_drift_born_unknown` 修前就綠:三引號與新式部分複製是 r2 之前的行為,r3 補的只是測試。
2. **修補處的正常、錯誤、相鄰路徑**:
   - 同一份計劃自己的判綠仍留得住,別條分支的仍丟,git 叫不起來、逾時、淺複製、部分複製仍照留,這些都成立。
   - 相鄰的非忽略路徑還在用 SHA-1 空樹(finding 1)。
   - `_drift_born_env_err` 的 `None → 判不了` 在本機行為正確。
3. **新發現同一案例的修前修後**:
   - finding 1 兩版相同。
   - finding 2 的 `0k`、`0K`、`0m` 修前判假,修後判真(方向保守)。`010` 修前判假、修後判真,與 git 一致,是改進。
   - finding 3 的條款文字是修補新加。
   - finding 4 的部分複製加帳進版控,修前會讀分岔點,修後整個不讀。

**圖譜鏡頭(逐條判)**
- `lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill`、`design-loop`、`pitfalls-code-loop`:這次改動沒碰到它們的 INVARIANT 或 RISK 行,無牴觸。
- `reversibility-governance-ledger`、`loop-convergence-recording`:新增的只是治理帳事件的既有欄位 `ref`。我 grep 過,沒有其他讀端把它當標記讀走,回退無害。
- `測試假綠形態`:新增的正向斷言多數有前置斷言。負向的 gb2 只驗 `"redbase" not in rec`,沒有驗原因是「曾判綠」,屬覆蓋可再補,講不出具體改壞,不另立條。
- 其餘「只列名」的節點,我沒有找到被這次改動寫錯的敘述。`docs/` 與 `skills/` 裡其他提到 partial clone 的句子,我看過沒有過期。

**未驗範圍**
- git 2.39(Apple Git-143)以外的版本,包括 `cat-file -e` 在較新 git 是否仍會觸發 lazy fetch。
- Windows、真正的 treeless 或 commit-less 遠端。
- 非 UTF-8 分支名(replace 後可能撞名)與超過 1000 字的分支名(`_esc_clean` 截斷)。
- 併發(範圍外)。

最嚴重等級是 minor,blocking 共 0 條。
