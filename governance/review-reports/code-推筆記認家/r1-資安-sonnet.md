severity: major

1. `governance/eval/home_audit.py` 把圖譜筆記 `about_code` 的字面值直接拼進要讀取的檔案路徑,沒有重做「repo 相對路徑、不可跑出 repo」的驗證,可被誘導讀 repo 外任意檔並把內容寫進會被提交進版控的 JSON。
   誰:能讓一篇 `type: system`、`status` 為 doing/done/stale 的 `.md` 筆記進到某個圖譜(例如惡意 PR、或別人分享/複製過來的圖譜資料夾)裡的人——不需要透過 `lumos append`,直接手改 `.md` 的 frontmatter 就能寫入,寫入時的路徑校驗只在 CLI 那條入口(`_about_code_path`),讀取端(`_nodehome_key`)只做字面正規化。
   從哪裡:那篇筆記的 `about_code:` 欄位,值填成 `../../../../../../.env` 或 `/Users/<user>/.ssh/id_rsa` 這種絕對路徑/跳出路徑。
   送什麼:審查員對這個圖譜跑 `governance/eval/home_audit.py sample --vault <該圖譜> --out out.json` 這個文件裡教的標準抽查流程。
   拿到什麼:`head_of` 讀到那支檔的開頭 40 行,原樣塞進輸出 JSON——本次 diff 裡已經看到同類輸出(`home-audit-sample.json`)被直接提交進 `governance/review-reports/`,等於把 repo 外任意檔(含私鑰、`.env` 之類機密)的內容外洩進版本控制。
   引句:「repo = Path(args.repo) if args.repo else Path(args.vault).resolve().parents[1]」
   引句:「"head": head_of(repo / p["file"]),」
   佐證(舊制在寫入端有做、讀取端沒做同一驗證,確認繞法真的存在):
   file: `scripts/lumos:11157`
   file: `scripts/lumos:18105`
severity: major
   blocking: 是

2. `_nodehome_key`/`_home_map_from_notes`(供 `home_audit.py` 與主程式共用)明文寫著只做字面路徑正規化、不查磁碟,把「寫入時已驗證」當成永遠成立的前提,但這個前提在「直接手改 .md」或「讀外部/不可信圖譜」的情境下不成立——這是上一條漏洞的根因,獨立列出以便修法(應在 `home_audit.py` 讀出 `file` 後,對照 repo 根重新跑一次 `_about_code_path` 同款驗證,而不是只信任字面值)。
   引句:「about_code 一項的比對鍵(字面):路徑正規化+NFC。★不讀磁碟★」
severity: major
   blocking: 是

3. `home_audit.py` 把「那支檔開頭 40 行」原樣寫進要人工審查、且依現有作業習慣會被提交進版控的 JSON,即便 `about_code` 沒被惡意操弄,只要合法程式檔第一段剛好帶了機密(測試 fixture 的假 token 除外,現實中常見寫死的 API base/內部主機名等),照樣原樣外流進 git 歷史;沒有任何遮罩/黑名單機制。屬縱深防禦缺口,沒有獨立可構造的攻擊路徑,列為 minor。
   引句:「"head": head_of(repo / p["file"]),」
severity: minor
   blocking: 否

4. `load_lumos` 用 `SourceFileLoader` 動態執行 `--lumos`(或預設 `scripts/lumos`)整支程式——這是「執行任意路徑程式碼」沒錯,但 `--lumos` 是本機使用者自己在命令列打的參數,文件也寫明「測試用」,攻擊者若已經能控制這個命令列參數,代表他已經能在同一台機器用同一權限直接跑任意指令,沒有額外的權限邊界被跨越。推論:不構成可獨立利用的漏洞。
   引句:「s.add_argument("--lumos", default=None, help="lumos 主程式路徑(測試用)")」
severity: minor
   blocking: 否

六類逐項判定:
1. 不可信輸入流到危險操作:見發現 1、2——`about_code` 路徑穿越是真的、可利用;`--lumos` 動態載入已看,無(本機自控參數,無權限跨越)。
2. 正規表示式:新加的 `_PATH_IN_TEXT_RE = re.compile(r"[A-Za-z0-9_.@+\-]+(?:/[A-Za-z0-9_.@+\-]+)+")` 是線性字元類交錯,無巢狀量詞、無回溯放大結構,對抗惡意長字串不會 ReDoS;已看,無。
3. 密鑰與個資:見發現 1、3(檔案內容被寫進會提交的 JSON);沒看到把密鑰寫進一般 log 或錯誤訊息的地方。
4. 執行邊界:`home_audit.py` 不是 hook、沒有任何 CI/掛鉤自動呼叫它(已用 grep 確認全 repo 沒有其他地方引用 `home_audit`),要人手動跑才會觸發;掛鉤(`check-graph-sync.py`、`impact-hook.py`)這次只改顯示文字,沒放寬任何執行邊界;已看,無新增的自動化執行面。
5. 加密與傳輸、行動端:這次沒碰,已看,無。
6. 新依賴:`home_audit.py` 只 import 標準庫(`argparse`/`importlib.util`/`importlib.machinery`/`json`/`random`/`sys`/`pathlib`),零依賴,符合本專案零依賴家規;已看,無。
