severity: major

在 `/Users/enzo/orca/workspaces/lumos-toolchain/qo-frontmatter` 讀完 `r9-repair-review-甲.patch`,用修前 `d705e3d7` 與修後 `75620ccf` 兩份 `scripts/lumos`(存在我的臨時目錄 `lumos_before.py`、`lumos_after.py`)逐條對跑。ground truth 用 PyYAML 6.0.3。`-k t_qfm_r8` 76 條全綠,全 repo 1259 篇筆記前後的 `pq_parse` 結果沒有差異。

1. `? pending_questions` 這種用複雜鍵寫出的清單頭,讀不到、也不報錯,阻塞題從規格閘靜默消失(題號 甲)
severity: major
blocking: 是
引句:「return bool(errs), items, errs」
file: `scripts/lumos:7427`(`_pq_scan` 找不到頂格 `pending_questions:` 就提早返回,清單外規則根本沒跑)
- 最小重現(`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-正確性-sonnet/` 下 `python3.14 gate.py`):
  ```
  ? pending_questions
  :
    - id: Q1
      text: 阻塞題
      class: 需求
      stage: 需求
      status: 待查
      blocking: true
  ```
  PyYAML 讀到 1 題。`pq_parse` 回 `(False, [], [])`。
- `_spec_gate_pending` 回 `None`,規格閘放行。同一份題目寫成一般 `pending_questions:` 時回 1,規格閘擋下。
- `lumos lint` 對這份筆記沒有任何警告。
- 同類寫法也靜默:頂格 flow `{pending_questions: [...]}`,以及 `<<: {pending_questions: [...]}` 的 merge key。
- `question-add` 的寫後自驗有擋下(rc2 且檔案沒動),所以只有讀端漏。
- 這一輪新增的「`? ` 複雜鍵清單外整個不收」只在已找到頂格 `pending_questions:` 時才運作。清單頭本身用 `? ` 寫,正好繞過。
- 歸因:有證據的原有漏查。修前修後都是 `(False, [])`。
- 修前查證:`run(B, 上列文字)` 回 `(False, [], [])`。
- 修後查證:`run(A, 上列文字)` 回 `(False, [], [])`。
- 建議修法:沒找到 head 時,對整份開頭欄位也跑一次「`? ` 複雜鍵、頂格 flow、`<<`」的存在檢查,看到就判讀不懂。
- 測試缺口:`t_qfm_r8_outside_key_rule` 沒有任何「清單頭本身用複雜鍵寫」的案例。

2. 簽核寫帳時被 Ctrl-C,筆記還原了,帳卻留下一行
severity: minor
blocking: 否
引句:「# Ctrl-C 這類程序內中斷落在筆記已寫、帳還沒寫完之間:先還原筆記再往外丟(代碼審 r8 後 Codex 反方);」
file: `scripts/lumos:9225`、`scripts/lumos:9172`
- `_signoff_append` 只接 `OSError`、`UnicodeError`、`WriteBlocked`,`KeyboardInterrupt` 穿過去時沒有 `os.ftruncate`。最可能的中斷點是 `os.fsync`,此時整行已寫入。
- 重現:`python3.14 sig.py A`,在帳描述子的 `fsync` 丟 `KeyboardInterrupt`。修後結果:筆記逐位元還原,`.signoff-log.jsonl` 仍留著那一行。
- 這一行會被 `guard abandon` 的簽核核對(`_guard_signoff_refs`)當成有人點頭過。
- 計劃 `Projects/待決問題改存開頭欄位_計劃.md` 與 `Systems/lumos-cli-write.md` 只說「Ctrl-C 都會還原筆記」,沒提帳會留行。
- ⚠ 筆記寫完到進入 `try` 之間(`_cmd_set_locked` 收尾)的中斷窗口很小,我沒重現。
- 歸因:有證據的原有漏查,修補只補了一半。
- 修前查證:`python3.14 sig.py B`,筆記沒還原(`note restored: False`)且帳留一行。
- 修後查證:`python3.14 sig.py A`,筆記還原(`True`)但帳仍留一行。
- 測試缺口:`t_qfm_r8_signoff_and_write_refusal ③e` 把整個 `_signoff_append` 換成直接丟 `KeyboardInterrupt`,只驗筆記,碰不到帳這一側。

3. `decision-supersede --ended` 的尾端換行沒有跟著 `decision-add` 一起修
severity: minor
blocking: 否
引句:「會放過尾端換行,寫進一個空行」
file: `scripts/lumos:21403`(`DATE_RE.match`),`scripts/lumos:21452`(`ended: {ended}` 原樣寫入)
- 重現:`python3.14 sup.py`,`--ended "2026-10-13\n"`。修前修後都 rc0,筆記的決策項裡多一個空行(`ended: 2026-10-13\n\n---`)。
- 歸因:有證據的原有漏查,與 R5 同一類,只修了 `decision-add`。
- 修前查證:`lumos_before.py decision-supersede Systems/S "#d1" --by 乙 --ended "2026-10-13\n"` rc0,有空行。
- 修後查證:同一命令 rc0,有空行。

4. 縮排的 `pending_questions:` 判讀不懂,也套到 block scalar 內文,沒有這個欄位的筆記被擋
severity: minor
blocking: 否
引句:「縮排掉的 pending_questions: 整段會被當成別的欄位的內容,題目跟著不見」
file: `scripts/lumos:7415`(第一輪掃描沒有跳過 block scalar 內容)
- 重現:`python3.14 g4.py`。`summary: |-` 裡有一行 `  pending_questions: 見計劃,尚未立任何題`。
- 修前 `pq_parse` 回 `(False, [], [])`,規格閘 `None`。修後回 `(True, [], [錯誤])`,規格閘回 1。
- 實際機率低,因為摘要行通常有 `KEY:`、`WHY:` 前綴。
- 歸因:有證據的修復回歸。
- 修前查證:`run(B, text)` 回 `(False, [], [])`。
- 修後查證:`run(A, text)` 回 `(True, [], [(6, ...要頂格寫...)])`。

5. 沒被分派接住的 `WriteBlocked`,程式內直接呼叫 `main()` 現在丟例外,不再回 2
severity: minor
blocking: 否
引句:「不用裝飾器、也不讓各分派重新拋出(代碼審 r8 架構席:那是第二、三種接法);」
file: `scripts/lumos:53755`(`_cli`,即 patch 末段新增處)
- 重現:`python3.14 mainraise.py`。`signoff` 對符號連結筆記,修前 `main()` 回 rc2,修後 `main()` 丟 `WriteBlocked`。
- 命令列走 `_cli()`,實測仍是 rc2、訊息已清洗,這點是對的。
- 受影響的只有程式內直接 `import` 後呼叫 `main()` 的人,以及沒有自己 try 的分派(`signoff`、`loop` 部分子指令等)。我沒有逐一查現有測試是否有這種呼叫。
- 這是計劃明寫的取捨,只是合約變了。
- 歸因:有證據的修復回歸,屬設計取捨。
- 修前查證:`B.main()` 回 2。
- 修後查證:`A.main()` 丟 `WriteBlocked`。

6. ⚠ 簽核帳的 `os.open` 沒帶 `O_BINARY`,Windows 上可能把換行寫成 `\r\n`
severity: minor
blocking: 否
引句:「fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)」
file: `scripts/lumos:9183`
- 修前用 `open(log, "ab")`(二進位),修後 `os.open` 在 Windows 預設文字模式。
- 讀端 `json.loads` 對尾端 `\r` 寬容,影響大概只是外觀,所以只標 ⚠。
- 同檔其他 `os.open` 追加(`scripts/lumos:21809`、`scripts/lumos:41656`)也沒帶,屬一致的既有慣例。
- 歸因:未判定。我沒有 Windows 可驗。

**甲、乙、丙三條單一規則的核對**
- 甲:引號鍵後空白、JSON 風格冒號緊接值、雙引號 `\x` 跳脫、flow 跨多行、`-<tab>`、連串 `- `、巢狀 status、`"pending\x5fquestions"`、帶 anchor 或 tag 的清單頭,修後都被攔下或判讀不懂。例外只有上面第 1 條。
- 乙:各語系長句(法文 NBSP、德、泰、阿拉伯、希伯來、印地語 ZWJ、韓、日、越)和 emoji 組合(四人家庭、`❤️‍🔥`、旗、鍵帽)都放行。
- 乙:IVS、`FE00`、RLM 被擋,符合 DICP 全擋的設計,計劃已有 2026-11-13 的回頭條件。
- 乙:波斯文數字後接 ZWNJ(如 `۱۰‌ام`)被擋。
- 乙:emoji 連接符「一串最多 3 個」只限制相連的串,中間隔兩個 emoji 後可以重新計數。整份上限 64 仍有效,我視為設計範圍內。
- 效能:連串 `- `、20 萬段 flow、百萬字元、60 萬字元 ZWJ 輸入都在 3 秒內,無平方級。
- 測試:`t_qfm_r8_unicode_scripts_and_budget` 的 expected 是手寫的,把 emoji 串長上限放寬到 4,或把 32 天花板放寬到 40 以上,測試會翻紅。`t_qfm_r8_outside_key_rule ③` 對 block scalar 界線有行為斷言。
- 測試:`④` 的標籤與註解還寫 `min(8,…)`,實際是 32。
- 圖譜:`Systems/lumos-cli-write.md`、`lumos-cli-read.md`、`Projects/待決問題改存開頭欄位_計劃.md` 的規則描述與程式一致。唯一對不上的是第 2 條,筆記沒有說帳會留行。`規格閘.md` 的描述與程式一致。

**三問**
- ① 原問題的行為證據:
  - 清單頭寫成 `"pending\x5fquestions":` 修前靜默 `(False, [])`,修後報錯。
  - `decision-add` 的 tab、ESC、DEL、C1、尾端換行日期修前 rc0,修後 rc2。
  - `decision-supersede --by "a\x1bb"` 修前 rc0,修後 rc2。
  - 簽核 ENOSPC 截回、新建帳刪掉、帳是目錄、guard 子指令的檔名控制字元,r8 測試都綠。
  - `slim-gen` 產出的精簡版保留 `_cli`,對符號連結 `set` 回 rc2。
- ② 相鄰路徑:
  - 命令列的 `WriteBlocked` 一律 rc2,訊息已清洗,含 guard。
  - `decision-add` 與 `decision-supersede --by` 的換行及控制字元回 rc2,沒有 traceback。
  - `drift fix` 載入時 `WriteBlocked` 會被當成 ValueError 接住。
  - 1259 篇既有筆記前後無差異。
  - 退步或沒補到的是第 1、3、4、5 條。
- ③ 新發現案例的前後結果:
  - 第 1 條:修前、修後都是靜默(`(False, [])`,規格閘放行)。
  - 第 2 條:修前筆記沒還原、帳留一行,修後筆記還原、帳仍留一行。
  - 第 3 條:修前、修後都寫入空行。
  - 第 4 條:修前沒問題,修後規格閘被擋。
  - 第 5 條:修前 `main()` 回 2,修後丟例外。

總結:這一輪的修補大多站得住腳,但清單頭用複雜鍵寫就會繞過所有守衛,讓阻塞題從規格閘消失,合併前建議先補這個洞。

臨時檔都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-正確性-sonnet/` 下。
