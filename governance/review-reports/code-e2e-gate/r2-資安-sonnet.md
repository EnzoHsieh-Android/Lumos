severity: major

審查範圍是 r2-snapshot.patch 全份,含 scripts/lumos、開場掛鉤、pre-push、測試、筆記與 README。我沒有跑實機實驗,結論都來自讀碼。

## 發現

### 1. 殘留的 CI 或 GITHUB_ACTIONS 環境變數會讓本機推送整道不判,也不記治理帳
severity: major
blocking: 是
歸因:有證據的修復回歸。r2 把 CI 出口併進最後的 `_e2e_gate_escape() or out`,連「擋下」也會被它改寫成放行。
- 誰:使用者本人,或照常操作的 AI。
- 從哪:在 shell 殘留 `CI=true` 或 `GITHUB_ACTIONS` 的環境裡跑 `git push`。例如曾 `export CI=1`、IDE 終端或 devcontainer 預設帶 CI。
- 送什麼:一個改了 Android App 程式、沒有任何驗收紀錄的提交。
- 拿到什麼:判定回 `status: ci`,整道不跑,連「紀錄讀不懂」「逾時」這類本該擋的情況也被改成放行。
  - 治理帳的事件表只認 `skipped-env`、`pass-by-feature`、`blocked`,`ci` 不記帳。
  - 只剩一行「提醒」。
  - 計劃寫明 CI 也不跑這道,所以沒有第二道防線。
  - 對照 `LUMOS_SKIP_ANDROID_E2E=1`:它會留帳,CI 殘留變數不會。

引句:「if _in_ci():」
file: `scripts/lumos:41665`
file: `scripts/lumos:41663`

### 2. 擋下訊息把被推送提交的檔名原樣印給 AI(提示注入)
severity: minor
blocking: 否
歸因:有證據的原有漏查。這是新增程式的第一次出現,其他席沒機會先擋。
- 誰:被推送的提交的作者,也就是別人合進來或拉來的分支。
- 從哪:在 `app_dirs` 底下新增一個檔名含換行或 ESC 序列的檔。git 檔名允許換行。
- 送什麼:檔名帶「`\n` 加上假的工具指示」,例如要求 AI 用 `waive` 放行,或叫它關掉驗收。
- 拿到什麼:這個檔對不到任何功能,檔名被寫進 `reason`。`_cl_say_e2e_block` 和 pre-push 都原樣印到 stderr,等於一行看起來像工具自己寫的文字進了 AI 的視野。
  - 同檔的 `waive --list` 已經對 `who`、`note` 用 `_esc_clean`,這條路徑漏了。
  - 修法:`f` 進 `why` 前套 `_esc_clean`。
  - 分類:這是縱深防禦類。擋下訊息裡本來就有放行指令,注入多出來的能力有限。

引句:「why.append(f"{f}(對不到任何功能)")」
file: `scripts/lumos:41501`
file: `scripts/lumos:66766`

### 3. 擋下訊息印出現成的放行指令,AI 一步就能自己放行
severity: minor
blocking: 否
歸因:未判定。這是計劃明講的設計,審計軌跡也有做。
- 誰:照常操作的 AI(沒有互動終端)。
- 從哪:被擋下後,照訊息印的 `lumos android-e2e waive <指紋> --commit <sha> --note "<理由>"` 跑,理由湊滿 10 字,再提交紀錄、推送。
- 送什麼:沒有終端可答,`_confirm_tty` 回 None,於是記成 `by: ai`。
- 拿到什麼:`any(_e2e_waiver_ok(w))` 就放行,AI 單靠自己就能走過這道守衛。事後只有 doctor、開場掛鉤與 pre-push 的「待看」提醒。
  - 對照安全證據閘:它要使用者在核可鏈簽例外。
  - 這是設計,我只標縱深:`SKILL.md` 靠文字要求 AI「放行前先跟使用者講」,沒有機械把關。

引句:「print(f"    {_e2e_waive_hint(rep['fp'], rep.get('commit') or '')}", file=sys.stderr)」
file: `scripts/lumos:66784`

### 4. 範圍外順手提一句:被推送提交自帶的 `waivers` 與 `commit` 欄位不驗來源
severity: minor
blocking: 否
歸因:未判定。
- 紀錄是從被推送的提交樹讀的,而紀錄檔不在指紋範圍內。
- 有人在提交裡自填一筆 `by: human` 的放行就會過。這是刻意偽造帳本欄位,屬系統天花板。
- `waive --commit` 的值不驗,直接寫進紀錄和治理帳的 `head_sha`。只有本機使用者自己輸入,沒有攻擊路徑,因此標推論。

引句:「if any(_e2e_waiver_ok(w) for w in rec.get("waivers") or []):」
file: `scripts/lumos:41686`

## 三類逐項

**①提示注入**
- 發現 2。
- 開場掛鉤 `_e2e_ai_line` 只回傳筆數(整數)進 additionalContext,外來欄位不會進去。已看,無。
- `waive --list`、doctor、`--ack` 訊息已對 `at`、`who`、`note` 套 `_esc_clean`,指紋用 64 碼十六進位檔名限制。已看,無。
- 印成可複製 shell 指令的欄位都過了白名單:指紋、sha 是十六進位,功能名與情境名限英數字、底線與連字號。
- 紀錄路徑用 `shlex.quote`。已看,無。

**②讀寫與執行越界**
- 掛鉤與 `_e2e_record_files` 只讀 `.lumos/e2e-records/` 底下的一般檔(`lstat`,不跟捷徑),不執行專案內的任何碼。
- 寫入走 `_repo_path_unsafe` 與原子寫入,`waive`、`--ack` 的指紋要完整 64 碼十六進位。已看,無。
- 新增內容裡沒有密鑰、信箱、下載網址或 shell 插值。已看,無。

**③非刻意、一步就能繞過的守衛**
- 發現 1 和發現 3。
- 只改設定就想讓判定說不用驗:不行。
  - 分岔點的 e2e 段和記憶體設定都要比對,不同就要整套。
  - 流程、`flows`、`visual`、記憶體情境的要求取自主線版。
  - 被推送提交拿掉 e2e 段,或沒有 e2e 段而 App 程式有變,都是擋下。
- 判不清就擋:內部出錯、逾時、讀不懂、時間欄位不合格都是 `blocked`。唯一出口是環境變數,而且會記帳。
- `LUMOS_E2E_GATE_BUDGET` 只能把預算縮短,縮短只會更容易擋,不會放行。已看,無。
- 按 Ctrl-C 或 tty 答別的:`waive` 回 1 不寫放行,`--ack` 同理。已看,無。

最高等級 major,擋實作的 1 條(發現 1)。
