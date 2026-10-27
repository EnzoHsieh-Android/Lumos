severity: major

審查範圍是整份 diff,重點在 `_e2e_gate_*`、`_e2e_tree_*`、`_e2e_fingerprint`、`_e2e_scope_hit`、`_e2e_owners`、`_e2e_shared_paths_err` 與 waive 的參數處理。重現都在 `/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/` 的臨時 repo 用 python3.14 跑過,目錄已刪。

## Findings

**1. 逃生出口 `LUMOS_SKIP_ANDROID_E2E=1` 排在讀設定之後,設定讀不懂或逾時時關不掉**
severity: major
blocking: 是
file: `scripts/lumos:41636` 與 `scripts/lumos:41640`(`_e2e_gate_body`)
引句:「return _e2e_gate_out("skipped-env", "LUMOS_SKIP_ANDROID_E2E=1:這一次整道不跑")」
- 失敗場景:`_e2e_gate_body` 先呼叫 `_e2e_gate_uses`,才檢查 `_in_ci()` 和 skip 環境變數。`_e2e_gate_uses` 讀不到或讀不懂被推送提交的 `.lumos/macrobench.json`(BOM、壞 JSON)就直接 `_e2e_gate_block`。
- 影響一:擋下訊息和 pre-push 都叫人設 `LUMOS_SKIP_ANDROID_E2E=1`,設了照擋。
- 影響二:CI 裡同樣照擋,和「CI 不跑這道」不符。
- 影響三:預算耗盡的逾時訊息也叫人設這個變數。逾時多半發生在這些 git 呼叫上,所以設了也沒用。
- 受害範圍:任何有壞掉 `macrobench.json` 的專案,不限 Android E2E 專案。
- 重現:
  - `LUMOS_SKIP_ANDROID_E2E=1 python3.14 scripts/lumos android-e2e check --repo .`
  - 提交的 `macrobench.json` 加 BOM,輸出 `{"status": "blocked", "reason": "被推送提交的 macrobench.json … 讀不懂(不是合格的 UTF-8 JSON 物件)"}`。
  - 改成內容 `not json` 結果相同。
  - 加 `CI=true` 結果相同。
  - `LUMOS_SKIP_ANDROID_E2E=1 LUMOS_E2E_GATE_BUDGET=0.000001` 輸出 `code: timeout` 的 blocked。
  - `code-loop check` 同環境也印「擋下:Android 端到端驗收」。
- 測試缺口:`t_android_e2e_gate_unclear_blocks` 的 skip 案例只用正常設定,沒有「設定讀不懂加 skip」的案例。

**2. 開場掛鉤與 doctor 讀紀錄檔不限型別,符號連結指到 `/dev/zero` 就卡死並吃光記憶體**
severity: major
blocking: 是
file: `scripts/hooks/claude/lumos-entry-hook.py:287-289`;佐證 file: `scripts/lumos:41771-41779`(`_e2e_records_all`)
引句:「or p.stat().st_size > 2 * 1024 * 1024:」
- 失敗場景:被打開的 repo 有 `.lumos/e2e-records/<64 個 a>.json -> /dev/zero`。git 能存符號連結,檔名也符合 64 碼十六進位。
- 為什麼擋不住:`stat()` 跟著連結走,字元裝置的 `st_size` 是 0,過得了 2MB 上限,接著 `read_text` 無限讀。
- 違反的宣稱:函式 docstring 寫「單檔大小有上限,任何異常靜默」,又說在信任邊界內只當資料讀。
- doctor 的 `_e2e_records_all` 沒有大小上限,也不擋非一般檔。
- 重現:對該 repo 跑掛鉤(repo 內要有 `docs/x-knowledge`),12 秒逾時,子程序 maxrss 約 5GB 且還在漲。
  - `echo '{"cwd":"<repo>"}' | python3.14 scripts/hooks/claude/lumos-entry-hook.py`
- 測試缺口:掛鉤的測試只有正常紀錄。

**3. 只改了「只列效能」的功能,判定仍擋推送,訊息還是空的**
severity: major
blocking: 是
file: `scripts/lumos:41593-41605`(`_e2e_gate_load`)
引句:「_e2e_gate_block(f"這一版沒有查證紀錄(沒驗收過、或驗收時的版本不是這一版);{want}", **info)」
- 失敗場景:所有被改的檔都只屬於 `bench` 這種只有 macrobench 的功能,`need[1]` 為空,`perf_only=["bench.scroll"]`。計劃〈推送前怎麼按功能判〉第 4 步說這種情境「不用驗」。
- 實際行為:`_e2e_gate_load` 對 `rec is None` 一律擋,訊息變成「按功能跑這幾個情境就夠:」後面空白。`_cl_say_e2e_block` 因為 `cases` 為空,改叫人整套跑。
- 後果:`_cl_say_e2e_notes` 裡「(沒有要驗的情境)」只有在已有紀錄時才走得到。沒有任何要驗的東西,卻要人先造一份紀錄,或者放行。
- 重現(bench 功能的 `paths` 是 `app/src/main/C.kt`,只改它):
  - `python3.14 scripts/lumos android-e2e check --repo . --branch feat2`
  - 輸出 `{"status": "blocked", "reason": "…按功能跑這幾個情境就夠:", …, "need": "cases", "cases": [], "perf_only": ["bench.scroll"]}`
- 測試缺口:S31 的測試同時改了 login 檔,從沒測過「要驗清單為空」。

**4. 掛鉤裡一份壞紀錄會讓整個「AI 放行待看」提醒消失**
severity: minor
blocking: 否
file: `scripts/hooks/claude/lumos-entry-hook.py:289`
引句:「rec = json.loads(p.read_text(encoding="utf-8"))」
- 失敗場景:迴圈裡沒有逐檔 try,任一份紀錄壞掉(合併衝突標記,或內容是 `[]` 導致 `.get` 丟 AttributeError)就跳到外層 `except` 回 None,前面已累計的筆數也丟掉。
- 實際影響:AI 放行是沒人看過的權限逃生口,這個提醒是開場唯一的通知。
- 對比:doctor 的 `_e2e_records_all` 是逐檔容錯、標「讀不懂」。
- 重現:放一份有 `by:ai` 未看過的紀錄,輸出含「AI 放行」。再加一份內容為 `<<<<<<< HEAD` 的 `<64 個 b>.json` 後輸出變 0。內容為 `[]` 的紀錄同樣讓輸出變 0。

**5. `LUMOS_TTY_TIMEOUT` 設成負數或 NaN,waive 與 `--ack` 在終端機下直接炸 traceback**
severity: minor
blocking: 否
file: `scripts/lumos:33612`(`_confirm_tty_stdin`)
引句:「readable, _, _ = select.select([sys.stdin], [], [], timeout)」
- 失敗場景:`select` 對負數或 NaN 丟 ValueError,新路徑沒接,而 `_confirm_tty` 只接 EOFError。原本走 `input()` 的路徑不會碰 `select`,所以這是這次新增的崩潰面。
- 重現:用 pty 跑 `LUMOS_TTY_TIMEOUT=-1 lumos android-e2e waive <64 碼> --note …`,輸出 `ValueError: timeout must be non-negative`,rc 1。設成 `nan` 同樣輸出 `ValueError: Invalid value NaN (not a number)`,rc 1。
- 補充:設成 `0` 時,真人在終端也來不及答,直接記成 AI 放行(rc 0)。

## 逐項極端輸入(程式走過沒問題的)

- 只刪檔:`git diff --name-only` 會列出被刪的檔,刪掉在範圍內的 flow 時會判為要整套,擋下。
- 改名:用 `--no-renames`,新舊路徑都算。
- 一支檔屬於兩個功能:`_e2e_owners` 回傳兩個,都要驗。
- `shared_paths` 空清單:無影響。`shared_paths` 與 `paths` 重疊:`shared_paths` 先判,走整套。
- `waivers` 元素是字串:`_e2e_waiver_ok` 不算放行,也不算讀不懂。
- 中文檔名:ls-tree 與 diff 都帶 `-z`。
- `app_dirs` 在被推送端被刪光:擋並說原因。
- `--at-sha` 縮寫:解成完整 sha。`--at-sha` 不存在:rc 2。
- detached HEAD:`branch` 為 None,照常判。
- 主線本身:無 `range_start` 時視為新 repo 而不要求,有 `range_start` 時正確判。
- 全零 `range_start`:視為首推主線。
- tag 推送:計劃明寫不跑這道。

另外確認一點:只改 e2e 設定(例如換 package 或 build 指令)、App 檔不動時,判定是 `not-required`。兩端指紋用同一份設定算,所以設定本身的改動不會觸發。這符合計劃字面,不列為缺陷。`_e2e_gate_need` 的「設定不同要整套」只有在檔案也有變時才走得到。

## 圖譜鏡頭

固定席節點逐條判不影響:

- `Issues/code-loop守衛main-direct盲區`:diff 只在 pre-push 加一句原因對照,沒碰 main 直推的判定邏輯。`_e2e_gate_mainline` 對「推主線本身」沿用 `_secev_mainline_pushed`。
- `Systems/存量漂移守衛`、`每支檔有家`、`筆記內容閘`、`pitfalls-code-loop`:diff 不動這些守衛的判定,只在 `_codeloop_guard_verdict` 多接一道。
- `lumos-cli-lifecycle`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間):diff 沒有碰 re-inject 與 CLAUDE.md 寫入。
- `lumos-cli-read`(★INVARIANT★ search 預設排除 superseded):diff 沒碰 `search`。
- `guard-kill`(★INVARIANT★ rc 優先序、`--json` 純度):diff 沒碰 `guard kill`。`code-loop check --json` 只多一個 `android_e2e` 鍵,而且只在有 e2e 時才加。
- 其餘「超出上限只列名」的節點沒有牽連到可見的行為宣稱。

pitfalls manifest 裡 `pitfalls-builtin` 落在新增行的兩條都是誤報:`scripts/lumos:41707` 的 `os.open` 在 `finally` 內 `os.close`,`scripts/lumos:41733` 的 `time.sleep(0.2)` 被 `wait` 秒上限約束。

總結:max severity = major,共 5 條,blocking 3 條(第 1、2、3 條)。
