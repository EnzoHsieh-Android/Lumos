severity: minor

## 資源席第八輪報告

實測用合成帳:366MB(約 14.7 萬筆,中文備註),Python 3.14,在 `/usr/bin/time -l` 下取峰值常駐記憶體。實驗目錄已刪。

### Finding 1

severity: minor
blocking: 否 — 只有帳大到數百 MB 且同一次推送碰到「帶 -std 紀錄」的計劃時才會耗時又吃記憶體;單人單機下每次推送只花幾秒,記憶體峰值短暫,不會洩漏或孤兒行程。
引句:「rc = cmd_loop_status(env, std_id, spec=str(env.vault / prel), disposal=True, readonly=True)」
問題:這輪把推送前的讀帳改成逐行串流,但 `_nogo_std_gate` 呼叫的 `cmd_loop_status` 沒跟著改。它仍用 `path.read_text(...)` 讀整本帳,再交給 `_ledger_lines` 切成行清單,並對每一行都跑 `json.loads`。`ctx["by_loop"]` 裡明明已有這份帳的列,卻沒傳進去。所以作者回報的「推送前 845→68MB」只涵蓋推送前自己的讀帳那一段。只要某份計劃走到出口 (b),就會多一次整本讀帳,沒有被這輪的串流修法涵蓋。
失敗情境:
- 實測 366MB 的帳用 `cmd_loop_status` 同一寫法(`read_text` + `_ledger_lines` + 逐行 `json.loads`),單次峰值 1,126MB、耗時 1.4 秒。
- 串流核心 `_canary_ledger_rows` 同帳峰值 131MB(只留 4 個欄位)、耗時 1.5 秒。
- 一次推送碰到 N 份「出口 (a) 沒過、帳上有 -std 紀錄」的計劃,就整本讀 N 次,耗時約 N×1.4 秒,每次峰值回到約 1.1GB。N=10 時約 14 秒。
- 這是同一個帳讀 N 次,記憶體不會累加;每次呼叫後即釋放。
- 處置閘其餘部分(讀快照、報告、治理帳)沒有跑測試,也沒有子行程。測試是在 `_spec_gate_push_one` 才跑,與 `cmd_loop_status` 無關。
- 串流版的耗時沒有比一次讀整本快,但記憶體少了約 8 倍。
- 修法方向:讓 `_nogo_std_gate` 傳入已讀好的列給 `cmd_loop_status`,或讓 `cmd_loop_status` 改走 `_canary_ledger_rows`。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9330`(`_nogo_std_gate`)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:13397`(`cmd_loop_status` 讀帳段,`read_text` 與 `_ledger_lines`)

### Finding 2

severity: minor
blocking: 否 — 只有手改成純 `\r` 行尾的帳才會觸發,正常寫入端只寫 `\n`,而且修補前的行為本來就是整本讀入。
引句:「真的串流——開檔逐行讀,不把整本帳讀成一份位元組、再切成一份行清單」
問題:`_canary_ledger_rows` 用 `for chunk in f` 取塊,二進位檔迭代只認 `\n`。帳若是純 `\r` 行尾(`_ledger_lines` 設計上要支援),整本就是一個塊,串流退化成整本讀入,與註解宣稱的「不整本讀進記憶體」不符。
失敗情境:100MB 的純 `\r` 帳,串流版峰值 473MB;同一份帳換成 `\n` 行尾只要 59MB。單行 200MB 的帳峰值約 1.06GB,這種情形本來就沒有解法,不列為缺陷。

### 已讀,無 finding
- `_canary_ledger_rows` 的 UTF-8 錯誤位移換算:多位元組字元不含 `\n` 位元組,逐塊解碼與整本解碼在同一個位元組出錯。
- 孤兒行程與訊號:這輪新增的程式沒有開子行程或執行緒,檔案用 `with` 開,生成器中途丟例外也會關檔。
- `_spec_gate_push_scan` 內帳只讀一次,`_nogo_ctx` 與 `_spec_gate_ledger_index` 保留欄位的篩法(串流版 131MB,作者回報的 68MB 方向一致)。
- 「表態記錄」的 `py-memory na`:本輪新增的串流核心確實沒有無上限的模組快取。但上述 Finding 1 的整本讀帳路徑它沒提到。

最高等級 minor,blocking 0 條。
