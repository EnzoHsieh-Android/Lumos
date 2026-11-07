severity: minor

**第六輪合約席 F1 的複核**

- 在 `git clone --shared` 的複本照當時重做,兄弟目錄刪除已修好。`t_r6del_sibling_e2e` 和 `t_r6del_status_entries_scope` 都綠。
- 我把狀態表出口的過濾整個拿掉(改成 `if p]`),`t_r6del*` 5 支裡 4 支紅。
- 這輪新測試 `t_r6*` 共 29 條,基準全綠。

**鏡頭 1:改壞實驗(都在前景跑完,複本與 repo 都沒動)**

`check-graph-sync.py` 的 `_git_status_entries` 與 `_rel_in_project`,改壞後 `-k t_r6del`:

| 改壞內容 | 結果 |
|---|---|
| 拿掉改名舊路徑那端 | 紅 |
| 只留舊路徑那端 | 紅 |
| 整個過濾拿掉 | 紅 |
| 拿掉 `resolve()` | 紅 |
| 前綴比對放寬成只比第一段 | 紅 |
| 前綴比對改成恆真 | 紅 |
| `top is None` 時不自己取根 | 紅 |
| 拿掉絕對路徑判斷 | 仍綠 |
| 拿掉 `..` 判斷 | 仍綠 |
| 拿掉反斜線轉換 | 仍綠 |
| 拿掉 `normpath` | 仍綠 |
| `except` 改回 True | 仍綠 |
| `except` 縮成只接 `ValueError` | 仍綠 |
| `main` 不傳 `top` | 仍綠(等價改壞,函式會自己取根) |

三支 shell 掛鉤改壞後 `-k t_r6sh`(各支單獨拿掉洗 PATH 段、三支一起改壞都試過):

| 改壞內容 | 結果 |
|---|---|
| `/*)` 改成 `*)` | 紅 6 |
| 拿掉退回 `/usr/bin:/bin` | 紅 3 |
| 拿掉結尾補的冒號 | 紅 2 |
| 只拿掉 pre-commit 的洗 PATH | 紅 11 |
| 只拿掉 pre-push 的洗 PATH | 紅 2 |
| 只拿掉 post-commit 的洗 PATH | 紅 2 |
| 找 python 段拿掉絕對路徑判斷 | 紅 1 |
| 找 python 段 `return 1` 改 `return 0` | 紅 1 |
| 找 python 段不清空 `_LUMOS_ANY_EXE` | 紅 1 |
| `${PATH:-}` 改 `${PATH}` | 仍綠(等價) |
| 拿掉 `export PATH` | 仍綠(等價,PATH 本來就已匯出) |

- 仍綠的非等價改壞,都是 `_rel_in_project` 裡 git 實際不會吐出的輸入:絕對路徑、`..`、含 `\` 的路徑、需要正規化的路徑。
- 所以沒有能讓錯誤行為上線的失敗場景,只算覆蓋不全。
- 作者說的「55 處翻 54 處」沒有逐一重做,只抽查了上面這些。

**鏡頭 2:** 這份 patch 沒有「恢復逐字比對加語法樹檢查」的改動,屬於前幾輪,這輪不套用。這輪的逐字守衛是 `t_r6sh_path_verbatim`,三支掛鉤各自拿掉洗 PATH 段都紅。

**鏡頭 3:** 計劃〈依據來源〉新列、天花板第 4 條與第 9 條、五篇家節點新加的行,跟程式行為對得上。〈審計修正紀錄〉只記到 r2,這輪沒補 r6 一行,但 r3 到 r5 也都沒補,是既有狀況,我沒標。

F1 改名出專案的檔,過濾後也不會被點名
引句:「改名的兩端任一端在專案內就留。路徑照舊從 repo 根算起」
- 場景:專案是 `sub/`,把 `sub/scripts/keep.py` 用 `git mv` 搬到 `other/keep.py`。
- 結果:`_git_status_entries(sub)` 回 `[('R ', 'other/keep.py')]`,但接著 `_entry_is_code('R ', 'other/keep.py', sub, top)` 回 False,專案少了一支程式檔卻不點名。
- 怪的地方:過濾那一步為了這種改名特地留下這一筆,下游又把它丟掉,留的這一筆等於白留。
- `t_r6del_status_entries_scope` 把 `other/tool` 當成該回的條目來斷言,只驗到出口,沒驗到有沒有被點名。
- 對照:這個行為在修補前就一樣,不是退步。
- 程式:`scripts/hooks/claude/check-graph-sync.py` 的 `_git_status_entries`、`_entry_is_code`。
severity: minor
blocking: 否

F2 `_rel_in_project` 的四道防禦沒有任何測試能讓它翻紅
引句:「if not parts or parts[0] in ("/", ".."):」
- 場景:拿掉 `parts[0] in ("/", "..")`、拿掉 `replace("\\", "/")`、拿掉 `posixpath.normpath`、把 `except` 改成 `return True`,`-k t_r6del` 都仍是 5 條全綠。
- 這些輸入 git 目前不會吐出,屬於防禦性程式碼,但新測試沒覆蓋。
- 若 git 或呼叫端日後吐出這類路徑,專案根是 repo 根時(前綴是空的)會全部判成專案內。
- 補一條直接餵 `_rel_in_project` 的單元案例即可。
severity: minor
blocking: 否

總結:最嚴重是 minor(改名出專案的檔不點名、`_rel_in_project` 四道防禦沒有測試翻紅),會擋 0 條;第六輪合約席 F1 已修好,三支掛鉤洗 PATH 的守衛抽查的改壞全部翻紅。

暫存清理:臨時目錄已用字面路徑刪除。測試紅沒有留下我能辨認的 `gctl-run-*`。
