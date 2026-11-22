severity: clean

我完整讀了 r3-snapshot.patch。scripts/lumos 與測試的部分逐行看,規則、樣本、型錄、筆記、計劃只掃過。r3-repair.patch 沒有另外讀,對照上輪修補時只看了與下面三類有關的內容。

**①提示注入:已看,無。**
- 新增的 `整個呼叫` 錨點(`_choice_anchor`、`_choice_err_start`、`_choice_anchor_edits`、`_choice_also`)只處理 Kotlin 原始碼的位元組位移。
- 它產生的壞法放進既有的 old/new 身分結構。
- 沒有新增把筆記、檔名、分支名或帳本欄位的自由文字帶進派工詞或 hook 附加段的路徑。

**②讀寫與執行越界:已看,無。**
- 新程式沒有 shell 插值、`eval`、`exec` 或下載。
- 沒有新增環境變數去覆蓋來源或路徑。
- 沒有新寫進去的密鑰或信箱。
- 測試改用 `tempfile.TemporaryDirectory(prefix="gctl-cb-")`。
  - 檔案只寫進自己的暫存目錄,子程序參數是清單形式,`cwd` 是那個暫存目錄。
  - ast-grep 的設定檔是測試自己現場寫的,不是從待審的 repo 讀來的。
  - 這個改動還把原本不會自動清掉的 `mkdtemp` 現場改成自動清除。
- 型錄與計劃裡的 URL 只是文件引用,不會被程式拿去下載。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 新程式裡的 `整個呼叫` 錨點,沒有「沒有 `$A` 卻往下走」的路徑:`_choice_anchor` 和 `_choice_anchor_edits` 遇到沒有 `$A` 都回 `None`,該命中被略過,不會變成誤放行。
- ERROR 覆蓋改成從錨點行起算,只影響 `整個呼叫` 這一列。其他錨點維持原行為,所以沒有讓原本被擋的情況悄悄走過去。
- 乾節點覆蓋沒有改動,判定仍照整個命中範圍。
- `_choice_also` 的 import 補寫條件改看那一列的「需補的 import」欄位,不看命中形狀。條件不成立就回 `None`,不會多補或錯補 import。
- 我沒有看到「檔名帶空白或中文、Ctrl-C、殘留環境變數」會讓這些新路徑意外繞過守衛的輸入。

總結:最高嚴重度 clean,blocking 共 0 條
