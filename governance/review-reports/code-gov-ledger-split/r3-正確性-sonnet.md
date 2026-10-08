severity: minor

## F1 度量暖機取「第一筆」:帳首一筆壞時間(時鐘錯誤)就讓暖機護欄失效
severity: minor
blocking: 否
引句:「oldest = t if oldest is None else oldest」
file: `scripts/lumos:3942`
file: `scripts/lumos:3984`
失敗場景:
1. 某台機器 RTC 未設定(CI 容器、樹莓派常見),`_gov_ts` 對 `1970-01-01T00:00:00+00:00` 回有效時間,本機帳或版控帳的第一行就是這筆。
2. `_gov_metric_events` 把 oldest 固定成 1970;帳其實只有幾天歷史。
3. `_doctor_metric_lines` 走到 `first > cutoff` 判斷時為假,暖機護欄放行;帳裡這個閘+種類只有幾筆或零筆,`== 0 近4週` 型度量規則被判「這條限制該撤」,是誤報。
4. 帳是 append-only,但版控帳經 git 合併、兩台時鐘不一致的機器各自追加後,「第一行」不等於最舊,也不等於最可信。r2 為擋「中段壞時間」改成取第一筆,測試只涵蓋壞時間在後面的情況;壞時間在第一行時沒有覆蓋。
影響只在 doctor 軟提醒,不寫檔、不擋推送,所以是 minor。這是 r2 刻意的取捨,只標出它的反面輸入。

## F2 _ensure_docs_gitignore 以 docs_dir 當 vault 取鎖:鎖退路在 docs/ 不可寫時空轉 60 秒,並可能留下沒被忽略的鎖檔
severity: minor
blocking: 否
引句:「with _vault_write_lock(docs_dir):」
file: `scripts/lumos:17813`
file: `scripts/lumos:41936`
失敗場景(未能重現:本環境以 root 跑,唯讀權限擋不住;依程式碼路徑推):
1. `lumos update` 或 `lumos init` 在 `~/.cache/lumos/vault-lock` 建不起來或不可信的環境(唯讀 HOME 的 CI 容器)執行,docs/ 也唯讀。
2. `_vault_lock_where(docs_dir)` 走退路,鎖檔落在 `docs/.lumos-vault-<key>.lock`。
3. `_excl_lock_try` 的 `os.open` 丟 PermissionError,被 `except OSError: return False` 吞掉。`_vault_write_lock` 把它當「別人持鎖」,每 0.05 秒重試,滿 60 秒才拋 RuntimeError,被 `except (...RuntimeError)` 接住回 `[]`。結果是 init/update 平白卡 60 秒才跳過;原版讀後直接寫,不會卡。
4. 退路在 docs/ 可寫時,鎖檔存在期間是 docs/ 裡未被忽略的新檔。程序被 kill 後鎖檔殘留,可能被 `git add docs` 帶進版控。docs_dir 當 vault 傳入本身可行:鎖鍵由 realpath 算出,同一 docs 的兩個程序鍵一致;但這把鎖不跟真正 vault 的寫入鎖互斥,只擋 ensure 與 ensure 之間。這點可以接受,因為 .gitignore 只有這支函式在寫。

## F3 讀者改 is_file 之後,資料夾與壞捷徑從「出錯或讀不到」變成「靜默略過」(行為差,無資料損失)
severity: minor
blocking: 否
引句:「if not p.is_file():      # 跟捷徑讀,但只讀一般檔案」
file: `scripts/lumos:8268`
file: `scripts/lumos:2353`
失敗場景:
1. `docs/.governance-log.jsonl` 是資料夾(誤建)。cmd_gov 的 `load` 現在直接 return,連 `loaded` 都不記;舊版會記進 `loaded`,再因 read_bytes 的 IsADirectoryError 靜默 return。可見差別是 `--stats` 的「載入哪幾源」少列一項,數字不變。
2. doctor 帳增速那段(行 2353)先 `_gp.exists()` 為真,再呼叫 `_gov_tail_bytes`。資料夾或管線現在回 `(b"",0)`,`_from == 0` 被當成「整份讀到」,`_window_ok` 為真,以零筆資料往下比;舊版 stat 或 open 丟例外,被外層 broad except 跳過。實際效果是對這種帳,doctor 現在印的是「沒有加速」而不是「跳過」。這種帳不可能被 git 追蹤成管線,觸發條件只有手動建立,所以只是 minor。

## 已走過沒問題的範圍
- _ensure_docs_gitignore 各分支:
  - 鎖拿不到時拋 RuntimeError,被 except 接住回 `[]`;`Path.home()` 取不到也是 RuntimeError,同樣接住。
  - 新建走 O_EXCL。兩程序同時建時輸家得到 FileExistsError(OSError)回 `[]`,贏家寫入完整;鎖內本來也只有一個程序進來。
  - 建檔後崩潰留下空檔:下次 raw 為空,`have` 為空,補兩行,不重複。
  - 懸空捷徑:`not exists() and not is_symlink()` 為假,走到 `is_symlink()` 回 `[]`,不寫。
  - 硬連結(st_nlink>1)、資料夾、非 UTF-8(UnicodeDecodeError)都不動。
  - CRLF 沿用、無尾端換行先補;再跑一次不重複。
  - `missing` 在 with 之後引用,所有路徑上都已綁定。
  - `.gitignore` 帶 BOM 時第一行比對不到,會多補一次,無害。
- _gov_ts 加 `t.timestamp()` 擋出界:`0001-01-01T00:00:00+05:00` 這類帶時區值不拋(aware 減法不經 OS),naive 出界的捕成 None。sort key 不再需要二次 try。
- _gov_ledger_rows_by_time 整份讀:`is_file` 與 `read_bytes` 在同一個 try(OSError)裡,管線與裝置檔略過;版控帳在前、同時間保序。
- _usage_log、_gate_event、_append_governance_log 本機帳寫入前先 `is_symlink`,擋住指向 repo 外的捷徑。TOCTOU 要攻擊者在檢查與 open 之間換檔,需本機寫權限,不計。
- _gov_tail_bytes 回 `(b"",0)` 的呼叫端只有 doctor 帳增速與度量讀取,後者先 `is_file` 過;版控帳在檔尾被截時,取第一筆仍是「截後第一筆」,比 cutoff 新就不判,方向偏安全。
- _docs_ledger_path 的兩處改寫與原路徑相同,沒有語意變化。
- 圖譜鏡頭:派工尾端沒有固定席筆記附上,我沒有逐條核對固定席;就 diff 本身看,沒有碰到合約行或 ★INVARIANT★ 的跡象。判定類讀者(code-loop、fix-check、design-loop)只讀版控帳這點,不在這輪 delta 內,未重驗。

總結:未發現會讓資料損失或錯誤放行的缺陷,留下三條低風險的邊界行為差。
