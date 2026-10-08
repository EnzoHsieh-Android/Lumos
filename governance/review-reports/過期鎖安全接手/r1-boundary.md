severity: major

# 邊界席

## b1：半寫入鎖永久阻斷

severity: major
blocking: 是
引句:「保留 `O_CREAT|O_EXCL` 的正常取鎖」
file: `scripts/lumos:33843`
`os.write` 只寫 PID 首位元組時，函式回 `True`，釋放端無法以完整 PID 認回，留下半成品鎖。審查席實測 `got=True`、鎖內容 `b'3'`、第二次 `False`。需驗完整寫入、失敗關 fd 並只清自己剛建的檔。

## b2：建檔錯誤被誤認已有持有者

severity: major
blocking: 是
引句:「已存在的鎖一律回未取得，不因 mtime 或 PID 推論可刪」
file: `scripts/lumos:33849`
`FileExistsError` 與其他 `OSError` 都回 `False`；無權限建鎖時 vault 白等 60 秒，lens 誤報可能有人在算。審查席以不可寫目錄實測 `got=False, lock_exists=False`。設計需給建檔失敗獨立診斷。

## b3：S1 修後假紅

severity: major
blocking: 是
引句:「跨程序屏障先證明舊碼回 `True/True`」
file: `scripts/test_lumos.py:54397`
file: `scripts/test_lumos.py:54429`
正確刪掉過期 rename 分支後，子程序不會建立 `ready`，前置斷言必紅。歷史重現與修後驗收須分開。

## b4：Windows 符號連結測試可能無法執行

severity: minor
blocking: 否
引句:「應保留活 PID、死 PID 或符號連結的舊鎖且回未取得」
file: `scripts/test_lumos.py:54456`
無建立 symlink 權限的 Windows 會在測試準備階段拋 OSError；需按既有跨平台測試做受控跳過或替代驗法。

## b5：背景工作身份不足以安全人工復原

severity: major
blocking: 是
引句:「確認全部停止後才人工移除」
file: `scripts/lumos:33904`
file: `scripts/lumos:33907`
派工者退出後鎖內 PID 已死，背景工作仍可能活著；鎖沒有背景 PID，按鎖 PID 刪除可再派第二支。需有可操作的跨平台核對方法，或保留鎖直到能確認。

問題、驗收其餘、PRIOR-ART、RETIRE-IF、回退其餘、實務隱患已讀，無 finding。

總結：最嚴重 severity: major；blocking 4 條。
