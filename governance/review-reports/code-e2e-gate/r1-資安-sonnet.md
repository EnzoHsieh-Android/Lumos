severity: major

**1. 推送前判定拿被推送提交自己的 e2e 設定算兩端指紋,同一個提交縮小範圍就能讓閘判「不用驗」**
severity: major
- blocking: 是
- 類別:③
- 引句:「sel_full, sel = pushed if pushed[1] else ml」
- 引句:「_e2e_gate_done("not-required", "App 程式與驗收素材跟分岔點一樣", fp=fp)」
- file: `scripts/lumos`(patch 內 `_e2e_gate_fps`,patch 第 1500 行前後;`_e2e_gate_need` 拿設定跟分岔點比對,只在指紋不同之後才跑)
- 攻擊路徑:
  - 誰:使用者本人,或照常改專案的 AI。
  - 從哪:一次提交,同時改 `.lumos/macrobench.json` 的 `e2e.app_dirs` 或 `exclude`(例如加一個排除項、把 app 目錄改名),又改到 App 程式。
  - 送什麼:`_e2e_gate_fps` 在兩端都用被推送提交的 e2e 段(`sel`)算指紋。分岔點那端用 `allow_missing=True`,所以新設定下兩端算出同一個指紋。
  - 拿到什麼:閘回 `not-required`,Android 端到端驗收整道沒擋,也沒走 `skipped-env`,不留帳。
  - 主線版設定只拿來判斷「有沒有要求」。設定被改弱這件事,要等指紋不同才會在 `_e2e_gate_need` 變成「要整套」,指紋相同時根本到不了那一步。
  - 設定與 App 程式一起改是日常動作(例如整理目錄),不必刻意偽造。
- 建議:指紋相等時,也要比對被推送提交與主線版(或分岔點)的 e2e 段。不一樣就視為要驗,或用主線版設定在兩端各算一次。

**2. `waive --list` 把紀錄的 who、note 原文印出,外來 repo 的紀錄能把文字塞進 AI 的上下文**
severity: major
- blocking: 是
- 類別:①
- 引句:「print(f"  {fp}  {w.get('at', '?')}  {w.get('who', '?')}({seen}):{w['note'][:80]}")」
- 引句:「看:lumos android-e2e waive --list;看過標記:lumos android-e2e waive --ack --all」
- file: `scripts/lumos`(patch 內 `_e2e_waive_list`,patch 第 1700 行前後),`scripts/hooks/claude/lumos-entry-hook.py`(`_e2e_ai_line`,patch 第 704 行起)
- 攻擊路徑:
  - 誰:陌生 repo 的作者。
  - 從哪:放一份檔名是 64 碼十六進位指紋的 `.lumos/e2e-records/<fp>.json`,內含 `by:"ai"`、`acked` 不是 true 的 waiver。
  - 送什麼:`who`(沒有長度上限)和 `note` 欄位裡放換行、ANSI 跳脫碼或假指令。紀錄用 `_e2e_load_json(scrub=False)` 讀,刻意保留換行與 tab,不清控制字元。
  - 拿到什麼:開場掛鉤看到這份紀錄,會在 additionalContext 叫 AI 去跑 `waive --list`。這個指令把攻擊者的 `who` 與前 80 字 `note` 原樣印進 AI 上下文,形成提示注入。同一段輸出也會讓終端被控制碼改寫。
  - 掛鉤那一行本身只印筆數與固定句,是乾淨的,洞在 `--list`。
- 建議:印出前把控制字元(含 `\n`、`\r`、`\x1b`)換掉,`who` 也要截長度。

**3. AI 放行與人放行在閘上效力相同(設計如此,只剩事後提醒)**
severity: minor
- blocking: 否
- 類別:③,縱深防禦
- 引句:「if any(_e2e_waiver_ok(w) for w in rec.get("waivers") or []):」
- file: `scripts/lumos`(patch 內 `_e2e_gate_body`)
- 說明:擋下訊息印出一行可複製的 `waive` 指令(指紋與提交都是十六進位,沒有 shell 注入)。AI 在沒有互動終端時照著跑,記成 `by: ai`,閘仍然放行,不需要人回應。計劃明講只靠 doctor 與開場提示事後提醒。這是已知設計,不是新洞,列為縱深防禦。

**逐類檢查**

- ① 提示注入:
  - 發現 2。
  - 開場掛鉤 `_e2e_ai_line` 只讀檔名是 64 碼十六進位的 JSON,有 500 份與 2MB 的上限,只輸出筆數和固定句子,異常靜默,不執行專案碼。這一段無洞。
  - `doctor` 只印指紋前 12 碼與筆數,無洞。
  - 派工詞與推送訊息沒有直接帶入紀錄的 `note` 或 `who`。`_gate_event_or_warn` 寫入的是自己放行時的 `note`,截到 200 字。
- ② 讀寫與執行越界:
  - 紀錄寫入前有 `_repo_path_unsafe` 逐層擋捷徑,補在 `_e2e_record_update`,已看,無洞。
  - 鎖檔固定在 `~/.cache/lumos/e2e-record-lock/`,名稱是路徑的雜湊,`O_EXCL` 加 0600 建立。pid 判活用 `os.kill(pid, 0)`,不執行任何外部碼,已看,無。
  - 判定讀的是被推送提交的樹(`ls-tree`、`cat-file`,帶 `--literal-pathspecs`),不讀工作目錄。這一段已看,無。
  - 沒有新的下載來源或環境變數覆蓋網址,沒有新密鑰或信箱。
  - `LUMOS_E2E_LOCK_WAIT`、`LUMOS_E2E_GATE_BUDGET`、`LUMOS_TTY` 都只是測試接縫,縮短逾時只會讓判定變成擋下。
- ③ 非刻意繞過:
  - 發現 1。
  - 判不清的路徑(git 失敗、逾時、紀錄讀不懂、時間沒帶時差、內部例外)都回 `blocked`,沒有 fail-open。
  - Ctrl-C 在 `waive` 回 1、不寫帳。
  - 檔名含空白或中文的檔案,`diff -z` 與 `ls-tree -z` 的切法正確。
  - 殘留的 `LUMOS_SKIP_ANDROID_E2E=1` 會讓整道略過,但有 `skipped-env` 提醒行並留帳,屬已知出口。

最高嚴重度 major,blocking 共 2 條(發現 1、發現 2)。
