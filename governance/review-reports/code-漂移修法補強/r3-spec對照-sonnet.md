severity: minor

# 漂移修法補強 代碼審第 3 輪:spec 對照席(sonnet)

整體結論:[S1]–[S5] 每條的行為程式都照做了。我在 `--shared` clone 跑了 `-k t_drift_c4`(26 過)、`t_set_conditions_blocks`(32 過)、`t_drift_fix_c1_missing`(7 過)、`t_drift_fix_c3_reason`(10 過)、`t_delguard_vendored`(18 過)、`t_delguard_skips`(8 過),全綠。找到的都是計劃內部說法打架或測試少釘子句,沒有程式行為跟條款相反的。

## F1 計劃說「已列的加上 N 等於指令列出的數量」,但 N 含只靠計劃名對到的,兩句打架
severity: minor
blocking: 否
引句:「所以已列的加上 N 跟指令列出的數量對得上;查不到提交時不給指令」
file: `scripts/lumos:28063-28072`
1. 同一份〈做法〉第 1 節前一句寫「另有 N 個沒列出」的 N 含「只靠計劃名比對到的」,後一句卻說「已列的加上 N」等於指令列出的數量。指令只列同提交清單,所以只要沒列出的裡面有計劃名來源,兩句就不可能同時成立。
2. 重現:clone 裡對 `m._drift_c4_print_dirs` 餵 23 個「同提交」加 2 個「計劃名」,輸出「另有 5 個沒列出(其中 2 個只有計劃名對得上…)」與「同提交的完整清單(共 23 個…)」。20 加 5 是 25,指令列出 23。
3. 程式的行為(印「共 {同提交數} 個」)是合理的;錯在計劃句子。`t_drift_c4_dirs_capped_at_20` ③ 只在沒有計劃名來源時斷言「已列 + N == 指令數」,所以這個矛盾沒被測到。
4. 順帶:計劃寫「與一條列同提交完整清單的指令」沒有條件,程式在 `by_plan < len(rest)` 為假(沒列出的全是計劃名來源)時不印指令。行為合理,計劃沒寫這個條件。

## F2 〈回退〉節用的名字跟現在的程式對不上
severity: minor
blocking: 否
引句:「刪除守衛:呼叫端不傳 `skip`(預設空集合)即回到原行為;note 裡的 `vendored-skip=` 拿掉。」
file: `scripts/lumos:29393`
1. 〈做法〉第 5 節自己寫「加 `vendored_skip` 參數……函式裡已經有區域變數叫 `skip`,不能同名」,〈回退〉卻寫「不傳 `skip`」。現在參數是 `vendored_skip` 加 `added_skip`,呼叫端傳的是 `_delguard_vendored_skips` 算出的兩份。照〈回退〉字面找 `skip` 會找到函式內那個區域變數。
2. 同節另兩處也過期:「`_drift_c4_evidence` 與 `_drift_c4_print` 改回只用計劃名比對」,實際的同提交邏輯在 `_drift_c4_same_commit`、`_drift_c4_dirs`、`_drift_c4_print_dirs`、`_drift_c4_more_cmd`、`_drift_c4_show_name`;「`_drift_fix_c3` 的接法與佔位字呼叫拿掉」,佔位字呼叫在 `_drift_fix_c3_args`。
3. 功能上不傳(預設空集合)確實回到原行為,所以只是文件對不上;〈回退〉沒列 `_delguard_vendored_skips` 與 `added_skip`。
引句補充:「`_drift_c4_evidence` 與 `_drift_c4_print` 改回只用計劃名比對、範本自動填目錄。」

## F3 計劃與程式註解都說守衛的 deadline 涵蓋工具檔判斷,程式其實只在事後檢查
severity: minor
blocking: 否
引句:「讀 git 版本每支工具檔一次 git show(有逾時),時間算在這道守衛的 deadline 裡(下面 _over())。」
file: `scripts/lumos:33241-33252`
1. `_delguard_vendored_skips` 對每支工具檔跑兩次 `git show`(加兩次清單讀取,`_VENDORED_ALL` 共 17 支,約 36 次呼叫),走 `_lens_git`,每次逾時 20 秒,沒有吃守衛 deadline 的餘額。`_over()` 只在 `_delguard_parse_diff` 回來之後才第一次檢查。
2. 所以「算在 deadline 裡」只成立於事後判斷:慢了會降級,但不會提早停。deadline 預設 15 秒,理論上限遠高於它。
3. 正常情形約 0.6 秒沒差;git 卡住時守衛超過 deadline 才降級。⚠ 未能重現,沒造出會卡的 git;只從程式讀出上限。計劃〈實務隱患〉效能那段沒提。

## F4 幾個條款子句沒有測試釘住
severity: minor
blocking: 否
引句:「在 `note` 裡加 `vendored-skip=<支數> files=<最多 20 支,逗號分隔>`」
file: `scripts/test_lumos.py:53988-53989`
1. [S5] 的「最多 20 支」:`t_delguard_skips_vendored_toolkit`、`t_delguard_vendored_two_states` 的 note 斷言只到 `vendored-skip=1 files=scripts/lumos`,沒有測支數大於 1 或超過 20 支被截。把 `vendored[:20]` 改成 `vendored` 或 `[:2]`,綁定測試照綠。
2. [S4] 的「長度……規則與 c2 相同」:`t_drift_fix_c3_reason` ③ 只測太短(`abc`)、多行、兩個佔位字,沒測超過 200 字被擋。把 `_drift_fix_reason_ok` 的上限拿掉,c2 的測試會紅、c3 的不會。
3. [S1] 的「git 失敗、逾時」:只測了「第一次提交查不到」(E2 未提交)。`_drift_c4_same_commit` 裡 `raw is None`(有 sha、git 失敗)那支沒被測;〈做法〉同節寫的「git 成功但那個提交沒加卷證目錄時不印這句」也沒測(`same == []` 且沒有「同提交:查不到」)。
4. [S3] 條款寫「兩處……字樣相同」;c1 好幾種都找不到時兩處字樣不同(c1 用 `one=True` 接成一句)。條款句尾已補「c1 好幾種都找不到時說明只接一次」,測試也釘了,沒有衝突,列在這裡是提醒條款首句沒限定單一種。

## 逐條對照結果(未列成 finding 的)
- [S1]:
  - 來源標示(兩者、同提交、計劃名)、排序(兩者、`code-`、其他)、範本句 `<卷證>`/`<sha>`、現存目錄名、NFC 鍵對應、格式字元跳脫、每目錄一行、超過 3 個提醒、20 上限與「另有 N 個」、最後一行先提交提醒,程式都照做。
  - 佔位字字面取自 `_SET_COND_SLOTS`。
  - 測試釘到這些子句。
- [S2]:
  - `_set_conditions_locked` 先擋任一整字面(點名、多個時全點名),再擋兩邊都有角括號的變體(全形、含 `　` 的內空白、sha 大小寫)。
  - 少一邊角括號那支已拿掉;`<sha256>`、`<git-sha>` 等照收(測試 ③ 釘住)。
  - 整字面訊息一字不差(test ③)。
- [S3]:
  - `_guard_settle_missing_say` 單一出口,c1 用 `say=False, one=True`,名稱取 `_GUARD_PROSE_NAMES`、不疊字。
  - 判定與回傳值不動。
- [S4]:
  - `_DRIFT_FIX_ALLOWED["c3"]` 含 `reason`;`_drift_fix_c3_args` 呼叫 `_drift_placeholder_err`;三種寫法都接「;理由:」,理由先 `.strip()`。
  - argparse 說明與 `_drift_fix_hint` 已更新。
- [S5]:
  - `_delguard_vendored_skips` 兩態都讀 git:刪除行 = 改前原封不動且(改後原封不動或不在暫存區),新增行 = 改後原封不動。
  - 無 HEAD 時改前為空;diff 沒出現工具檔路徑就不算;工具鏈 repo 為空。
  - `-` 行照 `rename from` 來源路徑,`vendored_skipped` 只數有 `-` 行的來源路徑,note 尾巴 `vendored-skip=N files=…` 沒碰到就不加。
  - commands/03、04、08 的文件同步也在。

## 圖譜鏡頭
此席專責 spec 對照,不另做圖譜鏡頭逐條判定。

最高等級:minor
