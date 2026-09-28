severity: minor

站在攻擊者角度逐 hunk 看過 scripts/lumos(存量漂移守衛:drift check/scan/ack/exam、guard plan/settle/abandon 加鎖、_note_audit_resolve/_notes_status_flipped 參數化)與 scripts/test_lumos.py + 圖譜筆記的改動。以下按六類分項記錄,找到一條縱深防禦級的觀察(F1),其餘沒有可利用的洞。

## 1 不可信輸入流到危險操作(命令/路徑/git 選項注入、cat-file --batch、寫檔路徑)

已看,無 blocking finding。逐一確認過的路徑:

1. `cmd_drift_exam` 的 `--repo <被考的 repo>` 會把整段 repo 交給 `_lens_git`/`_ns_git`/`_nodehome_cat_blobs` 跑 `rev-parse`/`diff --name-only`/`log --name-only`/`cat-file --batch`,全部是 subprocess 傳 list(不經 shell、不會被 shell 特殊字元注入),而且全是 git 的 read-only plumbing 指令(不會觸發目標 repo 的 hooks;plumbing 層級也不會跑 core.pager,因為輸出被 capture_output 接走、不是 tty)。
   引句:「r = _sp.run(cmd + list(args), capture_output=True, text=True, errors="replace", timeout=20)」
   file: `scripts/lumos:30139`
2. `_nodehome_cat_blobs`(這支雖非本次新增,但本次多了 `_drift_tree_env`/`_drift_exam_one` 兩個新呼叫點餵它 `where:path` 規格)已經擋掉規格字串裡有 `\n` 的情況,避免用換行在 `cat-file --batch` 的批次協定裡塞進第二筆假規格:
   引句:「if any("\n" in s_ for s_ in specs): return None」
   file: `scripts/lumos:23019`
   新呼叫點的 `paths` 來自 `_nodehome_list` 對 `git ls-tree` 的解析結果,不是外部字串直接拼進去,沒有繞過這道擋的路徑。
3. `_lens_range_ok`(既有函式,本次 `cmd_drift_check`/`cmd_note_audit_*` 共用同一支驗證 `--diff` 範圍)已經擋掉以 `-` 開頭、含 `...`、含空白的字串,新增的 `drift check --diff` 呼叫沒有繞過它另開一條路。
4. `cmd_drift_ack` 寫入 `governance/drift-acks.jsonl` 前,`text`/`reason`/`heading` 全部來自 `text.split("\n")` 之後單行 `.strip()` 或 argparse 給的字串,`_jsonl_append_verified` 用 `json.dumps` 序列化,控制字元(含換行)會被跳脫,不會有 JSONL 逐行解析被注入偽造第二筆紀錄的問題。
5. `env.find(node)` 只會解析到 vault 內既有筆記的相對路徑,`cmd_drift_ack` 沒有拿使用者輸入直接拼檔案路徑寫檔,`fp = Path(root) / _DRIFT_ACKS` 是常數相對路徑。

## 2 登入與權限

不適用。這批改動沒有引入任何認證/授權層,`lumos` 本身是本機 CLI,沒有使用者身份概念。已看,無。

## 3 密鑰與個資(進 log、治理帳、表態檔)

已看,無。新寫進治理帳/表態檔的欄位(`rel:line`、`kind`、`reason`、筆記原文片段)都是圖譜筆記內容本身或使用者當場輸入的理由,跟既有 note-audit/guard 家族寫治理帳的欄位形狀一致,沒有新增會蒐集密鑰或個資的欄位;`_drift_print_findings` 印的 `f['text'][:60]` 也只是筆記裡本來就公開的句子,不是憑證。

## 4 加密與傳輸

不適用。全部是本機檔案與本機 git 操作,沒有新增網路呼叫。已看,無。

## 5 執行邊界(推送前掛鉤/CI 會不會執行或讀取不可信位置;exam --repo 指向陌生 repo 會不會執行對方的東西;寫進使用者全域設定)

1. `exam --repo` 指向陌生 repo:見第 1 類第 1 點,確認只跑 git 唯讀 plumbing,不 checkout、不跑對方 hooks、也不寫回對方 repo。`_drift_doctor_lines` 印出的 CI 步驟建議只是字串印給人看,不會自動寫進任何 workflow 檔。已看,無 blocking finding。
2. F1(下方):`drift check` 的擋/放模式(block/warn/off)是從**被推送那個 tip 的 `.lumos/config.json`** 讀出來的,推的人自己這次提交就能決定這次推送查不查自己。

### F1 drift-check 的閘門開關可以被同一個要推送的提交自己改掉
severity: minor
blocking: 否 — 這是「防疏忽不防繞過」既有威脅模型下的縱深防禦缺口,不構成執行任意碼/資料外洩/權限提升/密鑰外露,推送者本來就對自己要推的提交有完整內容控制權
引句:「mode, warns = _drift_config(_nodehome_reader(root, tip)(".lumos/config.json"))」
1. 攻擊路徑(推論,已標記):誰——有推送權但不想讓自己這次的「轉正卻留著預告句」(c1)被擋下來的內部貢獻者;從哪裡——自己要推的分支;送什麼——同一個提交裡,一邊留著 c1 違規,一邊把 `.lumos/config.json` 的 `drift_check.gate` 改成 `warn` 或 `off`;拿到什麼——`cmd_drift_check` 讀的是 `tip`(也就是這次要推的頂端)的設定檔,`mode` 直接變成 `warn`/`off`,`_drift_report_must` 對 `warn` 只印不擋(rc0)、對 `off` 直接放行,推送前掛鉤與 CI(若 CI 也是對同一個 `github.sha` 跑 `lumos drift check`)都會用推送者自己剛設的寬鬆設定去判自己這次的內容。
2. file: `scripts/lumos:25508`(`cmd_drift_check` 讀 config 的位置)
3. file: `scripts/lumos:25460`(`_drift_config` docstring 自陳「照 `_note_audit_config` 的讀法(既有慣例)」——同樣的讀法在 `scripts/lumos:25023` 的 note-audit 閘已經先這樣做,這不是這批改動獨創的洞,是既有慣例被新閘沿用)
4. 未能在本地重現 rc 差異(需要一個帶 `pre-push` 上線標記且能跑 CI/推送前掛鉤的完整測試環境,凍結審材規則不准我在任何 repo 根跑 commit;純讀碼可確認邏輯路徑成立,故此條已依規定自降一級,標成 minor 而非拿掉)。
5. 這條之所以不算 blocking:PITFALL/RULE 在 `Systems/guard-kill.md`、本次新增的 `Systems/存量漂移守衛.md` 都明寫這整套機制的威脅模型是「防忘記不防繞過」——推送者本來就能用 `--no-verify` 或直接刪節點繞過,config 自我調寬只是同一類「已知且接受」的縱深防禦缺口,不是新引入的權限或資料邊界破口。列出來是給「以後要把 gate 預設改成 block」時參考——若那時希望這道閘變成真正擋得住惡意繞過(而不只是防疏忽),需要把 gate 設定挪到推送者拿不到的位置(例如只認主線上已提交過的設定,或伺服器端強制),而不是繼續讀 tip 自己的設定。

## 6 行動端

不適用。已看,無。

## 新依賴

已看,無。本次新增程式碼只用到標準庫(`json`/`re`/`datetime`/`secrets`/`time`/`subprocess`/`pathlib`),沒有引入新的第三方套件。

---
最嚴重等級為縱深防禦層級的觀察,blocking 共 0 條。
