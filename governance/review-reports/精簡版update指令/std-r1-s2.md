# std-r1 s2 更新機制邊界席審計報告

## Finding 1 [major] `--tool-only` 沒有向後相容合約,未來被拿掉/改名時已布署舊 CLI 靜默退回完整安裝

引句：「update=更新工具本身,永不碰專案層★」

_slim_update 生成期寫死呼叫 --tool-only;install.py 旗標判讀是寬鬆 `"--force" in argv` 型——未知旗標靜默忽略。未來重設計拿掉/改名該旗標,舊 CLI pull 到新 install.py 後 --tool-only 被無聲忽略,退回完整安裝(專案根守衛+CLAUDE.md 合併)=r1 blocker① 原封重演且靜默。合約候選未列此條、無測試守相容性。

## Finding 2 [major] `Path.home()` 無防護,HOME 未定義時裸 traceback 牴觸「全路徑 fail loud rc2」

引句：「緩解=全路徑 fail loud rc2+指路」

入口 `sys.exit(main())` 無外層 try/except;S1①定位固定落點是第一步、在所有 rc2 防護前。Path.home() 於 HOME 未設+passwd 無對應 uid 時拋 RuntimeError(容器/CI 常見),非 OSError、無人接→裸 traceback。

## Finding 3 [major] README 存在與「凍結」同義的殘留文字,機械文字釘字面比對抓不到

引句：「★範圍=`slim/` 全目錄(README+所有 .py/.sh/.ps1 的執行期輸出),非僅 README」

實測 grep:README 第 161 行「本包是凍結快照,不會有真正的新版本可拉,見下方〈凍結聲明〉」——(a)語意與 update 直接矛盾(b)〈凍結聲明〉改名後成懸空引用;測試 4 只釘「不會有更新」子字串,抓不到。

## Finding 4 [minor] 自我覆寫討論漏了 Windows 實際被執行的 `lumos.cmd` shim

引句：「Windows 自我覆寫(install.py copyfile 蓋住執行中的 lumos.py)理論上可行(python 編譯後不鎖檔)但**本輪無真機 Windows 驗證**」

_install_cli Windows 分支改寫 `lumos` 與 `lumos.cmd` 兩檔;cmd.exe 真正持有的是批次 shim,批次檔執行期覆寫語意與 python 原始碼不同(逐位元組續讀);spec 揭露只涵蓋一種檔且檔名寫錯。

max severity: major
