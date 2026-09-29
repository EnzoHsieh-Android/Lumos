severity: clean

已看,無 finding。逐類結論:

1. 不可信輸入流到危險操作:已看,無。掛鉤新增的驗證只對 lumos python-path 的輸出用 case 比對,再以雙引號執行 "$LUMOS_PY" -c 固定探針字串,無 eval、無字串拼進 shell。get.sh、install.sh 與另兩支安裝腳本新增的提示一律用 printf '%s' 印變數,沒有格式字串注入。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看,無。uv 失敗時把 stderr 最後一行截 160 字進訊息,內容是 uv 自己的錯誤文字,不含秘密。
4. 加密與傳輸:已看,無新增下載。CI 的 ruff==0.16.7 有釘版本、來源是 pip 預設索引、沒有雜湊鎖,屬供應鏈縱深但不在這份修正差異內,不報。
5. 執行邊界:已看,無可利用路徑。
   - _py_which 在 Windows 比對所在目錄的絕對與真實兩種寫法、檔案本身不解析符號連結,目前目錄本身放的檔仍被拒,POSIX 不搜目前目錄。
   - 掛鉤驗證路徑必須是絕對路徑且執行後為 3.14 以上才拿來跑閘。能偽造 python-path 輸出的人,要嘛控制 PATH 上的 python、要嘛控制 repo 內 scripts/lumos,兩者本來就已能執行任意碼,計劃〈誠實界線〉已寫明,沒有新增權限。
   - doctor 的自家掛鉤目錄改成兩家分開精確比對,只把 lumos 自己寫的目錄視為自家,縮小了「被執行的第一個字」範圍。攻擊者要能寫 ~/.claude/settings.json 才能塞入,那已是使用者層級的控制。
   - uv 錯誤分辨只改回報文字,不改執行對象。
   - LUMOS_PYTHON 由使用者環境控制,被略過時只多印說明。
   - LUMOS_PYTHON_SEARCH_DIRS 與 LUMOS_REEXEC_PYTHON 不在這份差異裡被改動,未見放寬。

最嚴重等級為 clean,blocking 共 0 條。
