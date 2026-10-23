severity: minor

## 發現

### 1. 收據重跑腳本用 `python3 -` 讀 stdin,模組搜尋路徑第一項是目前工作目錄(推論,縱深防禦)
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'」
file: `scripts/templates/android-receipt-rerun.sh:11`
- 誰:使用者本人或照常操作的 AI,在一份別人給的收據目錄裡執行 `./rerun.sh`。
- 從哪:用 `cd` 進收據目錄(或任何含外來檔案的目錄)後執行重跑腳本。
- 送什麼:那個目錄裡有一個 `json.py`、`re.py` 或 `subprocess.py`。`python3 -` 從 stdin 讀程式,`sys.path[0]` 是空字串,也就是目前工作目錄,所以腳本開頭的 `import json, re, subprocess` 會先載入它。
- 拿到什麼:在使用者機器上以使用者權限執行外來程式碼。
- 為什麼只列 minor:
  - 這個行為在本輪修補前就有,修補只在前面加了 `env PYTHONUTF8=1`,沒有新增也沒有放大。
  - 收據目錄正常只放 `manifest.json`、`queries.sql` 和 `rerun.sh`,要塞檔案得刻意為之。
  - 另外 `PYTHONPATH` 殘留也會影響這支腳本。
- 若要補強:改成 `python3 -I -`(同時忽略 `PYTHONPATH`),或在 `exec` 前先 `cd` 到固定目錄。

## 逐類清單

**① 提示注入:已看,無可利用洞。**
- SKILL.md 新增的「分 XML / Compose」第 4 點,明寫查詢輸出的區段名與 `top_compose_fn` 來自被量的 App,是資料不是指令,只能當證據引用。這正好擋住 Trace 內容流入派工詞的路徑。
- `__PROCESS__` 是手動替換,放在 SQL 字串引號裡。SKILL.md 第 1 點要求先確認套件名只含英數字、底線與點,含別的字元就停下來問人。這道把關由 AI 照文件執行,不是機械擋,但沒有現成的注入路徑。
- 筆記與 Verification 文件裡沒有把外部自由文字拼進指令的地方。

**② 讀寫與執行越界:已看,無可利用洞。**
- `rerun.sh` 的執行對象是環境變數 `TP` 指的分析工具,或 PATH 上的 `trace_processor`。這是文件載明的設計,由使用者自己的環境決定。
- `subprocess.run` 用 list 傳參數,沒有 shell 插值。
- 新加的 `except OSError` 只印訊息並回 2,不會反過來執行別的東西。
- 暫存 `.sql` 檔用 `NamedTemporaryFile`,並在 `finally` 裡 `unlink`。
- 新範本 `android-ui-attribution.sql` 是純 SELECT,沒有 `ATTACH`、寫檔或載入擴充的語句,也已登進 `_VENDORED_TREE_FILES`,隨 `lumos update` 發給消費專案。
- 測試檔:
  - `tempfile.TemporaryDirectory` 都限定在自己的暫存目錄裡。
  - 假的分析工具是測試自己造的。
  - sqlite 測試執行的是範本,`__PROCESS__` 被換成測試常數。
  - 沒有真能用的憑證、密鑰或信箱。SPDX 抬頭裡的 Enzo Hsieh 是既有慣例。
- 新增文字裡沒有下載網址,也沒有可被環境變數覆蓋的下載來源。

**③ 非刻意、一步就能繞過的守衛:已看,有 1 條 minor。**
- 見發現 1。
- 本輪修補反而收緊了這類洞:
  - 檔頭帶 BOM 時,原本第一條標頭配不到,該條不符也照樣回 0。
  - 分析工具不存在時,現在回 2,不再被當成「比對不符」或誤判通過。
- `PYTHONUTF8=1` 只影響編碼,不會讓守衛提早回 0。

**程式規則對照:** python-idioms R15 邊界驗證已看,無。R16 秘密不進 log 已看,無,錯誤訊息只印工具路徑與 `strerror`。R18 反序列化與 shell 已看,無,`json.load` 只讀本地 manifest,也沒有 `shell=True`。SQL 範本與 Markdown 沒有對應條款:無。

總結:最高嚴重度 minor
