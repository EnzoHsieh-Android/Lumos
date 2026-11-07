severity: major

**範圍說明**:我讀完整份補丁的 `scripts/lumos` 部分、型錄讀取與解析、情境段切分、表態形狀與對程式檢查、測試執行器的隔離段。測試檔假資料不報。用 grep 查過,目前工作樹裡 `LUMOS_KT_CATALOG` 只出現在補丁本身,沒有其他讀取點。

**F1 殘留的 `LUMOS_KT_CATALOG` 會讓推送前閘整題悄悄消失**
severity: major
blocking: 是
- 誰:使用者本人,或照常操作的 AI。
- 從哪:在 shell 裡 `export LUMOS_KT_CATALOG=…`(想測情境題時順手匯出,事後沒清),或把它寫進 shell 設定、工作階段環境。之後在同一個環境執行 `git push`、`lumos pitfalls --diff`、`lumos code-loop check`。
- 送什麼:一份觸發字寬鬆、或路徑不存在的型錄,例如測試用的永遠不亮的小表。
- 拿到什麼:`kt-situation` 這一題被悄悄拿掉,推送前閘不再要求逐段逐列的表態對程式。程式在模組載入時就讀環境變數,沒有任何只限測試的保護,生產路徑照樣讀。型錄讀不到或格式壞時,走的是印一行提醒到 stderr 後 `return []`,等於放行,不是擋下。環境變數覆蓋成功時也不印「正在用別份型錄」,所以使用者看不出守衛已經換掉。
- 補強方向:只在 `LUMOS_SKIP_` 這類明示開關存在、或測試執行器標記存在時才認這個變數;或覆蓋生效時固定印一行,並在 pitfalls 輸出裡標明用的是哪份型錄。
引句:「LUMOS_KT_CATALOG 可指到別份型錄(測試用)。」
引句:「env = os.environ.get("LUMOS_KT_CATALOG")」
引句:「print(f"提醒:Kotlin 型錄的情境決策表{_KT_DT_ERR},這次不出情境題(工具鏈安裝不完整?)", file=sys.stderr)」
file: `scripts/lumos`(同一個檔裡既有的 `LUMOS_SKIP_*` 隔離慣例,見 `_isolate_environment`)

**F2 git 錯誤時情境段算成空,題目被當成不適用**
severity: minor
blocking: 否
- 誰:使用者本人或照常操作的 AI。
- 從哪:`lumos pitfalls --diff <範圍>`,而 `git diff` 回傳非 0(例如範圍壞掉、物件暫時讀不到)。
- 送什麼:讓 `_kt_sit_hunks` 回 `None` 的範圍。
- 拿到什麼:`hunks = _kt_sit_hunks(...) or {}`,沒有區分「git 失敗」和「沒有改動」,情境段為空,`kt-situation` 判成不適用。推送前核對雖會重算,但同一個錯誤條件下可能重現同樣的空結果。這只是縱深防禦,是否真能走到這一步我是推論,沒實際重現。
引句:「hunks = _kt_sit_hunks(repo_root, diff_range) or {}」

**F3 被審分支可控的檔名進入問題句和模板時沒有統一跳脫**
severity: minor
blocking: 否
- 誰:能控制被審分支檔名的人(本專案是單人使用,這是推論)。
- 從哪:`.kt` 檔名含換行或控制字元。
- 送什麼:帶控制字元的檔名。
- 拿到什麼:`pitfalls` 人讀輸出有用 `_kill_esc`,但 `_kt_sit_check` 的「缺段 … sg['file']」問題句,以及模板的 `where` 欄位直接放檔名。JSON 輸出自帶跳脫,風險很低。若問題句會原樣印給 AI,檔名裡的文字理論上可以變成派工詞的一部分。我沒看到這些問題句最終怎麼印,所以標推論。
引句:「probs.append(f"缺段 {sg['seg']}({sg['file']}:{sg['start']}-{sg['end']},候選列」

**逐類結論**
- ① 提示注入:已看。程式碼的註解與字串在比對前先剝掉,`_mat`、`_code` 在輸出前由 `_kt_sit_public` 拿掉,不會印給 AI。印出的只有段身分(雜湊)、檔名、行範圍,以及型錄的寫法與樣式(型錄隨工具鏈、不在被審分支)。所以「程式碼文字變成給 AI 的指令」這條路不成立,除了上面 F3 的檔名推論。
- ② 型錄環境變數:見 F1。
- ③ 表態檔的 evidence 與段身分讀 repo 外檔案:已看,無。evidence 只拿來跟 `sg["file"]` 字串比對,再用行號查 `sg["_code"]`(由 `git show` 或 diff 路徑算出的內容),不會用表態裡的路徑開檔。`_kt_sit_read` 的路徑來自 `git diff` 輸出。工作樹分支(`at_sha=None`)讀 `Path(repo_root)/rel` 時理論上會跟過符號連結,但讀到的內容只用來比對和切段,不外送,只算縱深防禦,不另列。
- ④ 測試執行器以外是否讀 `LUMOS_KT_CATALOG`:有,模組載入時的 `_kt_catalog_path()` 無條件讀,所以才有 F1。
- 密鑰與信箱:已看,無。shell 插值與下載來源:已看,無(`git` 一律用 list 形式呼叫)。
- 照平常操作一步走過的守衛:除 F1、F2 外,已看,無。

總結:最嚴重是 F1(殘留環境變數讓推送前閘悄悄換成別份型錄、整題放行),會擋 1 條。
