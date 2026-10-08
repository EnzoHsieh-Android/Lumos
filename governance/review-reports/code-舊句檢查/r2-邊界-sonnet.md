severity: minor

# 邊界-sonnet 第 2 輪報告

實跑環境:`git clone --shared` 到自己的臨時目錄(HEAD 1d6e7289),用 `/opt/homebrew/bin/python3`(3.14)在行程內載入 scripts/lumos,對臨時 repo 直接呼叫判定本體與 CLI。git 一律用 fast-import 造(可放非 UTF-8 檔名),沒動 repo 根。

## F1 帳寫不進去的留痕檔:目錄放寬成 group 可寫後,被放進同名 FIFO 會讓推送前掛鉤卡死
severity: minor
blocking: 否
引句:「if hasattr(os, "getuid") and os.fstat(fd).st_uid != os.getuid():   # 目錄 group 可寫:檔要是自己的」
file: `scripts/lumos:29349`
1. 第 1 輪把 `~/.cache/lumos/drift-m1/` 改成 group 可寫也信(`group_ok=True`),並在 `os.open` 之後補「檔要是自己的」的 uid 檢查。
2. 問題是 `os.open(..., O_WRONLY | O_APPEND | O_CREAT | O_NOFOLLOW)` 沒有 `O_NONBLOCK`:同 group 的人在這個目錄(0775)放一個叫 `ledger-miss.jsonl` 的 FIFO,`os.open` 會在沒有讀端時一直等,uid 檢查根本輪不到。放寬之前 group 可寫的目錄一律不信、走不到這裡,所以是這個修正新帶進來的。
3. 重現:HOME 換成暫存目錄,建 `.cache/lumos/drift-m1`(chmod 775)、`os.mkfifo(".../ledger-miss.jsonl")`,呼叫 `m._drift_m1_ledger_miss(root, "a"*40, "done")`,設 alarm 8 秒 → 被 SIGALRM 殺掉(rc=142),沒有回傳。
4. 觸發條件苛刻:要有同 group 的惡意使用者、而且治理帳本身寫不進去(`_gate_event_or_warn` 回 False)才會走到留痕。所以只給 minor。快取檔那邊沒這個問題:`_lens_cache_read` 先 stat 檢查 uid、FIFO 是別人的就直接回 None,沒有先 open。

## 逐項實跑結果(沒有問題的,供收貨端對照)
- 單行長度上限:實測 19990 與 20000 字的行照掃(命中 1 筆、long_lines=0);20001 與 20030 字的行不掃、long_lines=1。上限用「字」算:20000 個中文字(約 6 萬位元組)照掃,行為跟計劃一致。
- `_DriftM1Clauses` 對 `_drift_m1_clause_hist`:30 萬組隨機字串(括號、全形括號、切句字、歷史字眼混排)逐位置比對,不一致 0 筆。
- 一行名稱索引 `_drift_m1_line_hits` 對「整份名稱一條正則」的舊做法:20 萬組隨機(名稱、行)(含旗標、路徑、`-v`、CJK、組合字元、全形字母、`ﬁ`),結果不一致 0 筆。單行 2200 個相異候選名稱、40 行,總共 1.3 秒。
- 名稱正規化:表態端實際擋掉 U+2028、U+200B、U+202E、控制字元(\x01、\x85、\x0c、\x7f)、開頭 NBSP、尾端全形空白、U+FEFF、tag 字元 U+E0041、201 字;放行 200 字、名稱中間有空白的 `ok name`、`é` 與 `é` 各自獨立。頭尾各差一個空白的名稱兩種都擋、不會靜默正規化成另一個名稱。含單引號、空白、`$` 的旗標名,提示行的 shell 引號寫法貼上去可以直接表態成功。
- 非 UTF-8:筆記檔名 `\xff\xfe.md`、程式檔名 `src/\xff.py`、`.py` 內容含 `\xff\xfe` 三種,warn 模式 rc=0 不當;`PYTHONIOENCODING=ascii:strict` 加 `LC_ALL=C` 也不當(輸出被逸出)。
- 無副檔名檔兩版一邊 Python 一邊不是:py→sh、py→無 shebang 的 def、py→刪除、py→空檔、CRLF shebang、BOM 開頭、含非 UTF-8 位元組的 Python、3MB 大檔,起點版的定義都有被算進消失名稱;sh→py 不誤報。第一行不是 `#!`(前面有空行)的 Python 腳本不認,跟原本 shebang 規矩一致,不算新洞。
- umask 002、077、022、000 與 `~/.cache` 事先不存在、0775、0755:快取都建得起來(2 個快取檔),新建的層是 0700。`~/.cache` 是 0777 時整個不用快取、照判完。
- `_drift_config` 二十幾種壞值組合(gate 壞 old_sentence 好、反過來、整份不是 JSON、BOM、`[]`、`null`、`"s"`、list/dict/false/大小寫錯的 old_sentence、重複鍵、十萬層巢狀):沒有例外,兩個開關各自解析,結果都合設計。

## 審材外的觀察(不算 finding,因為那幾行不在 r2-snapshot-code.patch 裡,無法錨定)
- doctor 開頭提醒(`scripts/lumos:29545` 那行把含 `old_sentence` 的提醒濾掉,只在 gate 不是預設時才多講 old_sentence 的值):實測 `{"drift_check":{"old_sentence":"off"}}`、`{"old_sentence":"Block"}`(大小寫寫錯,實際是 warn)、`{"gate":"old_sentence"}` 三種 doctor 都回空。推送時 `cmd_drift_check` 對寫錯的值還有印提醒,但 `off` 在推送與 doctor 都完全沒聲音。這是重定基底解衝突那一帶,若要處理請由架構或合約席在能引到 range-diff 的位置判。
- 非 UTF-8 檔名的筆記出現在提示行時,路徑印成字面的 `\udcff`,貼上去的 `drift ack` 找不到節點(名稱那半邊已保證貼得動,路徑這半邊沒有)。要處理層碰到這種筆記只能改筆記行,沒辦法表態;極少見,不標。

## 圖譜鏡頭逐條判定
- lumos-cli-read、bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-lifecycle、design-loop、pitfalls-code-loop 及「超出上限只列名」的節點:這批修正動到 m1 判定、`_drift_config`、`_drift_m1_*` 快取與留痕、`_gate_event` 讀側的 `check` 去重鍵、`_trusted_private_dir` 與 `_mkdir_trusted_under_home` 與 `_home_cache_write` 多一個預設關閉的 `group_ok`。沒有一條合約行講到這些:search 排除 superseded、bound-tests 逐支真跑、guard kill 的 rc 與 JSON 純度、授權檔不進 vendored、re-inject 保留 sentinel 外內容、處置閘第五步,都不在改動路徑上。判「不影響」。
- pitfalls-code-loop(★RISK★)與派工鏡頭快取:共用的 `_home_cache_write`、`_trusted_private_dir`、`_mkdir_trusted_under_home` 新參數預設 `group_ok=False`,原本的「group 或 other 可寫就不信」判準對 dispatch-lens 不變(讀碼確認 `_lens_cache_write` 仍不帶該參數)。判「不影響」。
- `gov` 去重鍵多帶 `check`:同一提交、同閘、同種類、同節點集合的 c 類與 m1 事件現在分得開,原有事件沒有 `check` 時補空字串,不改變舊事件的分組。判「不影響」既有 gov 行為;未另行實跑 `gov --stats`。

最高等級:minor
