severity: clean

已逐 hunk 讀 r2-snapshot.patch(掛鉤篩選、_py_which、_py_probe/_py_uv_find/_pick_windows_launcher 改絕對路徑、shell 共用段 LUMOS_PYTHON 第一步、說明文字改動),對照 clone-314 內完整程式(_GLOBAL_CLAUDE_HOOKS、pre-push 的 _lumos_py314)判斷。

## 逐類結論
1. 不可信輸入流到危險操作:已看,無 finding。_hook_python_problems 現在要求「第二段檔名在 lumos 自家掛鉤清單且第一段像 python」才拿第一段去跑 -c 探針,別家工具的掛鉤不會再被執行;被執行的只有第一段(直譯器),不執行第二段腳本,找不到能由陌生 repo 控制的輸入。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看,無。新增的說明文字只印候選路徑與環境變數名。
4. 加密與傳輸:已看,無。本輪 diff 未動下載與 CI 依賴(ci.yml 不在本輪 diff,ruff 釘版本無法在此審)。
5. 執行邊界:
   - _py_which:POSIX 上 shutil.which 不搜目前目錄,repo 內同名檔不會被當候選;Windows 落在目前目錄底下者回 None,其餘一律用絕對路徑執行,堵住「陌生 repo 放 python3.14.exe」。已想過的繞法:cwd 內的符號連結因 realpath 被解到 cwd 外而放行,但攻擊者只控制 repo 內容,連結目標必在 repo 外、不受其控,取不到執行權,不成立。
   - Windows 上 which 命中 cwd 即回 None、不再往 PATH 續找,只會讓該候選被跳過(退到下一個候選),不是提權。
   - LUMOS_PYTHON:lumos 內要求絕對路徑;shell 共用段只判 -x,相對路徑也會被先用(與 lumos 內「不收相對路徑」不一致)。但環境變數要由使用者自己的 shell 環境設,能設它已能執行任意碼,無攻擊路徑,不標。
   - 掛鉤註冊、{python} 代入:本輪 diff 未改這兩處寫法,無新增。
最高 clean,blocking 共 0 條
