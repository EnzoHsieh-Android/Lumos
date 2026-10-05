severity: major
findings: 1

ID: ORCH-R3-UTF8
severity: major
blocking: 是
引句:「candidates = [os.fsdecode(f) for f in r.stdout.split(b"\0") if f]」
file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:41342`

編排者真 Git 再現，不是獨立代理審查席。凍結來源 HEAD 9a6e21e49a96677db09286a63beaf38f381a0104、源碼 SHA-256 0eb04da07d1efbca592aa210819533cd35bbb4d17912fe184137204cc2bb169c。

用 Git index/blob 建 byte FF 檔名，不要求 macOS 工作目錄可表示該檔。NUL 列舉和 os.fsdecode 保留替身字元，但外層 JSON 沿 ensure_ascii=False 直接輸出；默认環境 rc0 卻有無效 UTF-8 位元組，json.loads(bytes) 拋 UnicodeDecodeError。嚴格 UTF-8 stdout 則拋 UnicodeEncodeError、rc1。人讀列出關聯檔案也在同一替身字元處報錯。

真實卷證：r3-parent-nonutf8-output.json；正式控制修前 r3-nonutf8-red-rerun.json 為1過7敗。首個 r3-repair-red.json 的此案缺 os 匯入、收集前失敗，不算產品反例；已保留，沒有覆寫。

最小修法：機器 JSON 沿標準 encoder 的 ASCII escaping 保留精確路徑；人讀呈現沿既有 _nodehome_show，不將顯示替字當索引鍵。控制要求 json.loads 可讀、os.fsencode 路徑位元組可逆、真事故仍命中，並驗嚴格 stdout 的兩個人讀消費者。

Python 官方 json 文件說明 ensure_ascii 預設會逃逸非 ASCII 字元、bytes 解析要求有效 UTF 編碼；os.fsdecode/os.fsencode 為既有檔案系統位元組轉換入口。官方文件支援修法的編碼判準，不替本案例證明 bug，bug 由上述真 Git 指令重現。

https://docs.python.org/3/library/json.html
https://docs.python.org/3/library/os.html#os.fsdecode

沒有宣稱任意跨語言客戶端能以相同方式還原原始路徑，也沒有扩充圖譜的既有家確認表示格式。兩個正式席均收齊後才動測試與源碼；這是第三輪追加的機械再現，不是新第四輪。
