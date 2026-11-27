severity: minor

整體修法成立:Linux 上的紅燈根因確實被消掉,沒有 major 以上的問題。我只找到兩條 minor。

## F1 倒序新測試比的是兩個空集合,「收到同一批」沒有真的被驗到
severity: minor
blocking: 否
引句:「check("看滿上限收到的套件跟檔案系統給的順序無關(資料夾倒過來給也收到同一批)", cut_rev == cut」

現象:我在拋棄式 clone(`/tmp/lumos-seat-work/code-主線CI/正確性/w`,已刪)的新測試斷言前插入 print,印出的 `cut` 與 `cut_rev` 都是 `set()`。

為什麼錯:`_CHOICE_COV_SRC_MAX=1` 時,排序後第一個走到的資料夾裡就有兩支以上原始碼。`seen > MAX` 在收第二支之前就停了,所以收到的套件是空集合。這條斷言實際上只是「兩邊都收不到東西」。同樣地,既有的 `len(cut) <= 1 and cut <= got`,在 `cut` 為空集合時也永遠成立。

我做的變異驗證(各自在拋棄式 clone 裡跑一次):
- 拿掉 `subs.sort()` 和 `sorted(files)`:倒序斷言紅,輸出 `{'org/b'} set()`。所以這條測試對「排序被拿掉」仍有殺傷力,但殺傷力來自一邊空、一邊非空的偶然差異。
- 拿掉測試裡的 `got = m._choice_cov_src_pkgs(tmp)` 重算:`t_choice_cov_src_pkgs_edges` 在 macOS 上仍然 7 條全綠(Linux 我沒跑)。重算這一步沒有任何測試守,是靠排序之後碰巧不紅。

怎麼重現:在該斷言前加 `print(cut, cut_rev, got)`,然後跑 `python3.14 scripts/test_lumos.py -k choice_cov_src_pkgs_edges`。

建議:把上限調到能收到至少一個非空套件(例如讓 `_CHOICE_COV_SRC_MAX` 剛好等於第一個資料夾的原始碼數),並加一句 `cut` 非空的前置斷言。

## F2 INDEX.md 只剩 4 字元餘裕,而且總目錄不再點名三個 choice 指令
severity: minor
blocking: 否
引句:「choice-*(改動選擇點與存活判讀) / room-guard·test-guard」

現象:`INDEX.md` 現在是 4496 字元(`python3.14 -c "print(len(open(...).read()))"` 實測),上限 4500。

影響:
- 下次任何一行增補都會讓 `t_command_index_complete` 再紅一次,這次的修法沒有留空間。
- 總目錄不再逐字列出 choice-points、choice-kill、choice-layer。完整性檢查是拿全部 `commands/*.md` 串起來比對,`lumos choice-points` 等字樣仍在 `06-代碼審與推送.md`(`grep -c` 命中 4 次),所以 `t_command_index_complete` 仍綠(我實跑 16 passed)。
- 「各子檔在總目錄被指到」只比子檔檔名,06 仍在。
- 代價是只看總目錄的人搜不到 choice-kill 這個詞,屬於可發現性的小退化,不是測試漏洞。

## 其餘鏡頭查證結果(沒問題)
1. 紅燈根因:真正的根因是 `got` 比舊全量。測試現在在 j/src 建好之後重算全量,上限子集必然是它的子集,與走訪順序無關。排序是額外的保險。在 `t_choice_cov_src_pkgs_edges` 裡 `cut <= got` 與 `cut2 <= got` 在任何檔案系統順序下都穩定(實跑 7 passed)。
2. 排序語意:`subs[:] = ...` 過濾後 `subs.sort()` 是同一個 list 物件原地排序,`os.walk` 的 topdown 裁剪仍有效。沒看滿上限時收到的是同一個集合,只有看滿上限時「收哪一批」從依檔案系統變成依名字,方向仍是「漏收只會被判不明、多跑」。排序成本可忽略。
3. 替換 walk:`_os_mod` 就是 `import os as _os_mod`(`scripts/test_lumos.py:157`),`_choice_cov_src_pkgs` 內用的 `os.walk` 在呼叫時才查找,所以替換有打到。`finally` 裡還原 `walk` 與 `_CHOICE_COV_SRC_MAX`。被包的 generator 傳回同一個 `subs` list,消費端的原地排序有作用。唯一會外溢的風險是,中途例外時才靠 `finally` 還原,目前寫法是對的。
4. 索引完整性:見 F2。
5. 資料狀態五問:無落盤資料、無不可逆操作、無新舊互讀問題。衍生資料(套件集合)只在看滿上限時內容不同,而且變成確定性的。知識圖譜 PITFALL 一行把根因寫成「Linux 先走到新建資料夾」,與實際「測試比舊全量」一致,但「修法」欄只寫排序,漏提重算全量,這是文件小不一致,併入 F1 即可。

附帶說明:我在拋棄式 clone 做變異測試時留下一個 `gctl-run-*` 現場,已用字面絕對路徑刪除,clone 也已刪。
