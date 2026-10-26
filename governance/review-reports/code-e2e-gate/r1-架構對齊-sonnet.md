severity: major

三問都對照過 `scripts/lumos` 的鄰居。判定本體的分層和呼叫方向跟安全證據閘一致,只有查證紀錄的鎖另起一套。

## 1. 分層與依賴方向:大致對齊
- **本體放哪、誰呼叫它**:`_e2e_gate_evaluate`(`scripts/lumos:41660`)是判定本體。`_codeloop_e2e_step`(`scripts/lumos:66129`)包它,`android-e2e check` 也呼叫它。這跟 `_codeloop_security_step` 包 `_secev_evaluate`(`scripts/lumos:66140`、`scripts/lumos:10948`)是同一個形狀。
- **接進 code-loop 的方式**:`_codeloop_guard_verdict.last_e2e` 對應 `last_security`。擋下訊息 `_cl_say_e2e_block` 對應 `_cl_say_sec_block`。`_codeloop_kg_finish` 的明細鍵表和 `pre-push` 的 `pp_cl_reason` 表也都照加。
- **用到安全證據閘的工具**:`_secev_git_left`、`_SecevTimeout`、`_secev_mainline` 這幾個,基準版的 e2e 碼就在用(基準版 `scripts/lumos:40860`),所以是重用,不算新跨層。
- **沒看到跨層直呼**。

## 2. 命名與錯誤處理:大致對齊,有 2 條差異
對齊的部分:
- `_E2eGateStop` 帶結果提早結束,有先例:`_DriftM1Stop(state)`(`scripts/lumos:53935`)、`_NoteRereadStop(why)`(`scripts/lumos:47810`)。
- 判不清就擋、`except Exception` 轉成擋下,跟 `_secev_evaluate` 同一做法。
- 治理帳走 `_gate_event_or_warn`;事件種類 `blocked`、`skipped-env`、`waived` 和 `lint-new`、`code-loop` 同一寫法;閘名 `android-e2e` 已加進 `_KNOWN_GATES`。

差異見下面發現 2 和 4。

## 3. 第二種做法:鎖是,其他是重用或比照
- **`_E2eRecordLock`(發現 1)**:另起一套。
- **`_confirm_tty` 的 `stdin_timeout`(⚠ 交編排者)**:它延伸既有函式,沿用 `LUMOS_TTY_TIMEOUT` 和同樣的 select 逾時寫法,屬於重用。但第 ① 階現在有「阻塞 `input()`」和「帶逾時」兩種並存,靠旗標切(`scripts/lumos:33576`)。這是設計審 r3 明講的取捨,我沒有判成另一套。
- **`_E2eGateStop` 帶結果**:有先例,見上。
- **測試接縫環境變數 `LUMOS_E2E_GATE_BUDGET`、`LUMOS_E2E_LOCK_WAIT`**:比照 `LUMOS_TTY_TIMEOUT`(`scripts/lumos:33590`)和 `LUMOS_DISP_GIT_TIMEOUT`(`scripts/lumos:65498`)。安全證據閘自己的預算接縫是函式參數 `budget`,這點不同,但鄰居已有環境變數接縫,所以不列。
- **開場掛鉤自己讀 JSON(發現 3)**:有先例,`ci-status-hook.py` 就自己讀檔。但先例有一致性守衛,這裡沒有。

## 發現

1. 查證紀錄的讀改寫鎖另起一套,而且做了專案明文否決過的事。
引句:「不改 _vault_write_lock 本身:別的寫入也在用它。」
file: `scripts/lumos:41690`(`_E2eRecordLock`)、`scripts/lumos:40892`(`_e2e_record_update` 原本用 `_vault_write_lock(p)`)
- **鄰居的做法**:`_vault_write_lock` 收的是路徑,lint-waive 就用它鎖單一檔案(基準版 `scripts/lumos:38624`、`scripts/lumos:40823`)。它底下是 `_excl_lock_try`,明文寫著「更不能依鎖內 PID 接手」(基準版 `scripts/lumos:61526`),因為接手會有 ABA:後到者可以搬走前到者的新鎖,兩邊都以為自己拿到。
- **新鎖和鄰居的差異**:
  - 新鎖偏偏就是依鎖內 PID 判斷程序已不在、然後 `unlink` 接手(`_stale_or_wait`)。
  - 鎖資料夾是直接 `mkdir`,沒走 `_mkdir_trusted_under_home` 與 `_trusted_private_dir` 的信任檢查和退路(`_vault_lock_where`)。
  - 沒有巢狀可重入表(`_VAULT_LOCK_HELD`)。
  - 逾時有 `LUMOS_E2E_LOCK_WAIT` 接縫,鄰居是寫死的 60 秒。
- **來源推測**:這套寫法照抄 `scripts/templates/android-e2e-run.sh` 的裝置鎖(`take_lock`、`lock_holder`)。那份是範本腳本,一次一台裝置,不是 `scripts/lumos` 內建的做法。
- **後果**:之後接手的人要在兩套鎖裡猜,而且新鎖的接手路徑有已知競態:兩個等待者同時看到程序已死,A 刪鎖並重建,B 隨後把 A 的新鎖刪掉。
severity: major
blocking: 是

2. `_codeloop_e2e_step` 在取不到要推的提交編號時直接放行,跟安全證據閘的處理不同。
引句:「不看 tier、排在所有放行早退之前(判定本體是 _e2e_gate_evaluate」
file: `scripts/lumos:66129`
- **新碼**:`if not marker_sha: return None`。
- **鄰居**:`_codeloop_security_step` 不先擋,直接交給 `_secev_evaluate`。後者在提交解不出來時,會看工作目錄有沒有登記痕跡,有就擋(`_secev_worktree_trace`,`scripts/lumos:9938`)。
- **e2e 這邊**:`_e2e_gate_resolve` 其實有同樣的「工作目錄有 e2e 段才擋」邏輯,卻被前面的早退擋住,走不到。
- **後果**:前面的文字說「判不清就擋」,取不到提交這一條卻是放行。
severity: minor
blocking: 否

3. 開場掛鉤複製了「AI 放行待看」的判定規則,沒有跟 `scripts/lumos` 對齊的守衛。
引句:「只讀 .lumos/e2e-records/ 底下檔名是 64 碼指紋的 JSON,當資料數筆數,不執行專案裡的任何碼」
file: `scripts/hooks/claude/lumos-entry-hook.py:276`(`_e2e_ai_line`)、`scripts/lumos`(`_e2e_ai_pending`、`_e2e_waiver_ok`、`_e2e_record_err`)
- **先例**:`ci-status-hook.py` 的 `_ci_latest_attempts` 也是 `scripts/lumos` 的複本,但它的說明寫「有測試盯著兩份一致」,測試是 `t_ci_latest_attempts_copies_identical`(`scripts/test_lumos.py:36660`)。
- **新碼**:`_e2e_ai_line` 沒有這種盯複本的測試。
  - 它也沒套 `_e2e_record_err` 與 `by` 的白名單,doctor 那邊的 `_e2e_records_all` 有套。紀錄壞了時,兩處的筆數可能對不上。
  - `t_android_e2e_ai_waiver_notice` 只驗字串有沒有出現,不驗兩處筆數一致。
- 同層的 `_enforcement_line` 則是呼叫 CLI,所以鄰居本身兩種都有。這條只在「複本有沒有守衛」上判不一致。
severity: minor
blocking: 否

4. 判定逾時與內部出錯的代碼命名、訊息內容,跟安全證據閘的寫法不同。
引句:「判定超過 {b:g} 秒還沒算完(git 太慢或檔案樹太大)」
file: `scripts/lumos:41660`(`_e2e_gate_evaluate`),對照 `scripts/lumos:10948`(`_secev_evaluate`)
- **代碼名**:新碼用 `code="timeout"`、`code="internal"`;鄰居是 `evaluation_timeout`、`evaluation_error`,並由 `_secev_gate` 配對照表 `_SECEV_GATE_WHY`。
- **訊息**:鄰居的逾時訊息會說判到哪一階段(`stage["name"]`),e2e 沒有。
- **影響**:結構是對的,只是之後要讀治理帳的人得認兩套詞。
severity: minor
blocking: 否

不對齊共 4 條,其中 major 1 條

臨時檔只有 `/tmp/lumos-seat-work/code-e2e-gate/架構對齊-sonnet/lumos.base`(基準版 `scripts/lumos`),我沒有刪,留給編排者在這一輪席報告收齊後依暫存清理規則處理。
