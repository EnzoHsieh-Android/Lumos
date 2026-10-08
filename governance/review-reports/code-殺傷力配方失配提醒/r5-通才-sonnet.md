severity: major

方法:在 `git clone --shared` 的 clone(HEAD 7a510e53)對 scripts/lumos 逐一突變(每次先清 __pycache__、各自一份拷貝),跑 `-k kill_recipe`(含 guard_kill_rm、doctor_kill_recipe_drift、guard_kill_add_warns 四組子集)。基準 116 passed / 0 failed。
共 21 個突變:翻紅的有 M2(冒號檢查拿掉)、M3(NFC 檢查拿掉)、M5(連結當正式路徑)、M8/M9(建議表鍵少 casefold 或少 normpath)、M10(替身字元檢查拿掉)、M12/M19(Check T 設定檔平台清單、測試名不跳脫)、M13(kill-add path 提醒字面改掉)、M14(path 前綴拿掉)、M16(P2 筆記名跳脫拿掉)。以下是改壞了照綠的。

## F1 100755(可執行檔)當正式路徑這條沒有任何對照格,拿掉照綠
severity: major
blocking: 是
引句:「    if mode in ("100644", "100755"):」
佐證行:file: `scripts/lumos:13141`(clone 內,`_kill_path_issue` 判一般檔那行)
1. 突變(唯一差異):`if mode in ("100644", "100755"):` 改成 `if mode in ("100644",):`。
2. 輸出:`-k kill_recipe` → `116 passed, 0 failed`;`-k doctor_kill_recipe_drift` → `30 passed, 0 failed`;`-k guard_kill_add_warns` → `31 passed, 0 failed`。四組全綠(`diff` 已確認 m-M7 拷貝只差這一行)。
3. 意義:計劃 S5 把「一般檔」列進正式路徑定義,可執行檔(shell 腳本、本 repo 的 `scripts/lumos` 自己就是 100755)是最常見的一類。被突變成 path 後,所有指向可執行檔的配方會被誤報「不是提交裡的正式路徑:提交裡沒有這個路徑」,而 guard kill 其實照常跑——這正是計劃 S5 說「正式路徑要對得上」的誤報方向。整張對照表(約 44 格)沒有一格把檔案存成 100755:`_krc_cell` 的 `files` 全是預設權限。修法:加一格 `files` 之後 `os.chmod(…, 0o755)` 再 commit 的 ok 格(在 Linux CI 與 macOS 都成立,git 看 mode 位元,不依賴檔案系統大小寫)。

## F2 「不含控制字元」是 S5 列的正式路徑條件,但沒有任何格子是「提交裡真的有這個含控制字元的檔」
severity: minor
blocking: 否
引句:「    if _path_special_chars(file):」
佐證行:file: `scripts/lumos:13134`(clone 內)
1. 突變:整個 `if _path_special_chars(file): return "含控制字元或無效字元"` 改成 `if False:`。`-k kill_recipe`、`guard_kill_rm`、`doctor_kill_recipe_drift`、`guard_kill_add_warns` 全綠(116/22/30/31 passed, 0 failed)。
2. 原因:kill-add 的 ⑦c 與 P2 ⑫ 用的是不在提交裡的假檔名,拿掉控制字元檢查後仍落到「提交裡沒有這個路徑」而判 path,狀態不變。要讓這個檢查獨立被測,需要一個 `git add` 進去的含換行檔名(Linux 與 macOS 都能建),期望 path 且原因帶「控制字元」。
3. 不是等效突變:被提交進去的怪檔名,拿掉檢查後會被判 ok 並照字面讀,跟條款「不含控制字元」不符;但實際風險低(要有人真提交怪檔名),所以 minor。

## F3 「Check T 三行全跳脫」只被守住一部分:rel 兩處、「出現但不是測試方法」整行拿掉跳脫照綠
severity: minor
blocking: 否
引句:「dangling.append(f"{_kill_esc(rel)}: [test:{_kill_esc(seg)}] 在程式碼中找不到")」
佐證行:file: `scripts/lumos:1681`(clone 內);同組另有 `scripts/lumos:1669`(平台前綴那行 rel)與 `scripts/lumos:1679`(fake 那行)
1. 突變 M20:1681 行把 `{_kill_esc(rel)}` 改成 `{rel}` → `-k doctor_kill_recipe_drift` 30 passed, 0 failed。
2. 突變 M11:1669 行同樣把 rel 的跳脫拿掉 → 30 passed, 0 failed。
3. 突變 M18:1679 行(`fake.append(f"{_kill_esc(rel)}: [test:{_kill_esc(seg)}] 在程式碼出現,但不是 {_kill_esc(_attr)} 測試方法")`)rel、seg、attr 三個跳脫全拿掉 → 30 passed, 0 failed。
4. 對照:同一格 ⑪b 對 seg(M19:拿掉 1681 行 seg 跳脫 → 翻紅)與設定檔平台名清單(M12 → 翻紅)有守。沒守到的是:筆記檔名 rel(整個 ⑪b 的筆記都叫 `Systems/Two.md`,沒有含控制字元的檔名)與「出現但不是測試方法」這條分支(沒有任何格子造出 fake 狀況)。修法:⑪b 補一篇檔名含 `\n` 的筆記、補一條指到「在程式碼出現但不是測試方法」的合約,斷言輸出沒有原始控制字元。
5. 這三處是第 4 輪「Check T 三行全跳脫」的字面承諾,風險方向是終端跳脫碼偽造行首(跟 ⑬ 同族),所以值得補。

## F4 path 原因文字(連結/子模組/冒號/拆開 Unicode)與 P2 的 path 措辭沒有任何斷言
severity: minor
blocking: 否
引句:「        return "是連結,寫它指向的那支檔"」
佐證行:file: `scripts/test_lumos.py:60426`(clone 內,唯一斷言建議字面的那格,只守「是不是 "prod.py"」)
1. 突變 M4:拿掉 `mode == "120000"` 分支 → 四組全綠;M6:拿掉 `if mode is not None: return "不是一般檔(子模組)"` → 全綠。狀態同為 path,只有原因字面不同,對照表的 path 格子只比 status。這兩個在狀態上是等效突變,所以只報文字沒守:使用者看到的「寫它指向的那支檔」這個建議沒有任何測試釘住,會被改成錯誤建議而不翻紅。
2. 另一條:突變 M15 把 P2 的 `detail = f"讀不到({res['detail']})" if code in ("missing", "undecodable") else res["detail"]` 的 else 拿掉(path 狀態也包成「讀不到(…)」)→ `-k doctor_kill_recipe_drift` 30 passed, 0 failed。原因是 ② 只檢查行內含「不是提交裡的正式路徑」。這會把 path 在 P2 印成「讀不到(不是提交裡的正式路徑:…)」,跟 kill-add 的措辭(不是讀不到)不一致。這一行不在 r5-delta.patch 內(沿用舊碼),引句改用 delta 內的 path 產出處:`"detail": f"不是提交裡的正式路徑:{why}"`。
3. 建議:在 ② 對 path 那格加 `"讀不到" not in line`,並在 `_krc_cell` 對 path 格補一個原因關鍵字欄位(連結:「是連結」;子模組:「子模組」;冒號:「冒號開頭」)。

## 未列為 finding 的觀察
- 突變 M17(把冒號開頭的 path 判斷搬到 test 名白名單之前)全綠。屬「判斷順序」,但目前沒有格子同時壞兩個欄位(冒號檔名加不合法 test 名),且 delta 沒新增順序依賴的斷言;若要釘順序,補一格「冒號檔名 + test 名不合法」期望 malformed(guard kill 先拒 test 名)。給不出會判錯的現實輸入,故不單獨標。
- 平台相依檢查:新格子(大小寫 `PROD.py`、拆開 Unicode、`./PROD.py`、冒號、`x?.py`)期望值都是固定的 path 或 ok,不再依賴本機檔案系統大小寫/Unicode 行為(舊版的 `ci`/`ni` 量測已拿掉),在 Linux CI 不會因檔案系統而恆綠或恆紅。「提交裡存的就是拆開寫法」那格先關再開 core.precomposeunicode,Linux 上兩個設定都無害、判斷走 `nfc(file) != file` 在兩邊同樣是 path(M3 突變在 macOS 翻紅;Linux 因 git 不轉寫法,翻紅路徑相同——判斷函式回 ok,所以也會紅)。
- 對照格 path 判得太多嗎:約 21 格 path、約 23 格非 path;path 格的「跟 guard kill 對得上」被 `"path": True` 恆真(`_krc_match`),等於只驗判斷函式本身,每格白跑一次真 guard kill(約 20 秒測試時間的主要來源)。這是作者刻意設計(不預測),不構成會做錯的行為,不標。
- 條款 S5 列的各題覆蓋:連結(檔案、資料夾、絕對、迴圈)、`..`、絕對路徑、大小寫、Unicode、冒號、不在提交裡(含被忽略)、資料夾、子模組、跑出 repo 都有格;缺的只有 F1(100755)與 F2(控制字元)。
- 以下翻紅確認有守:M2 冒號、M3 NFC、M5 連結當 ok、M8/M9 建議表鍵、M10 替身字元、M13 kill-add path 提醒字面、M14 path 前綴、M16 P2 筆記名跳脫、M12/M19 Check T 設定檔/seg 跳脫。

最高等級:major
