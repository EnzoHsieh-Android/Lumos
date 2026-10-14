severity: major

已讀 repair patch 全文,並在臨時目錄對 `_note_reread_hunk_chains` 做了實驗(用完已刪)。

### Finding 1:縮排鏈在「簽名收尾行或大括號頂格」的寫法下,所有函式拿到同一條鏈
severity: major
blocking: 是 — 這正是前兩輪被打穿的「同一段改動搬到同檔另一個結構相同的函式、指紋不變」,換了形狀後仍然存在。
引句:「從起點往上,縮排比起點淺的最近一行,空行、只有空白的行跳過,再從那行往上找比它更淺的,一路到縮排 0」
問題:鏈取的是「縮排比起點淺的最近一行」,而不是函式的定義行。以下兩種常見寫法下,最近的較淺行是收尾符號,不是函式名:
- 多行簽名(Python black 風格 `def f(\n    a,\n):`)。
- Allman 大括號(C#、C、C++、Java 部分風格)。
這些行的原文在整個檔案裡到處重複,於是不同函式的鏈完全相同。
失敗情境(對 `_note_reread_hunk_chains` 實測):
- 輸入 1:Python 檔有 `def f(\n    a,\n    b,\n):\n    x…` 和同樣形狀的 `def g(…)`。把同一段 hunk(起點在函式體第 4 行之後)從 f 搬到 g。輸出:f 的鏈是 `('):',)`。g 在函式體內的起點取到的鏈也是 `):`,與 f 完全一樣。我在 g 取了行 13,那行本身是 `):`,所以得到空鏈,這個取點不算數。同一個 g 函式體內更深的起點,依規則必然取到 `):`。
- 輸入 2:C# 的 `class A\n{\n    void F()\n    {\n        a();…}\n    void G()\n    {\n        a();…}\n}`。F 和 G 函式體內的 hunk 鏈都是 `('{', '{')`(實測)。整個類別裡所有方法共用同一個標籤。
- 結果:hunk 內容(增刪行加三行上下文)相同、標籤相同,指紋不變。「改動變了、指紋卻沒變」。
- 計劃點名的「大括號語言函式本體不縮排的寫法」不只是邊角案例,Allman 與 black 風格的多行簽名是常態寫法。
佐證:``file: `scripts/lumos`(patch 內 `_note_reread_hunk_nodes`:迴圈裡 `while stack and stack[-1][0] >= ind: stack.pop()`,Allman 的 `{` 縮排與外層相同,把外層的 `class A`、`void F()` 都彈掉)``
修法方向:鏈要能涵蓋被彈掉的行,例如保留「彈掉的最近一行」或把最近一個縮排 0 的簽名行並進鏈;或乾脆改用「起點往上到最近 N 個縮排非遞增的行都算」。

### Finding 2:逾時不擋可被「改很多檔」誘發
severity: minor
blocking: 否 — 單人、依序操作的威脅模型下是意外觸發,不是對抗;帳上會記 late。
引句:「因逾時沒算出新版指紋的篇不擋」
問題:`late` 只看 `why == "逾時"`。`_note_reread_v2_cut` 在 diff 階段逾時,也會被記成「逾時」。作者自己改的檔數與大小決定會不會逾時,等於讓他自己決定會不會被擋。注釋說「不會被拿來繞」,依據只有「要改到上千支被 about_code 列到的檔」,這只是門檻高,不是守衛。
失敗情境:一個分支同時動很多個被守檔筆記列到的大檔,指紋這一步用完 27 秒,所有篇變 late,第一層全部放行。第二層 must 仍擋,所以只是第一層失效。
佐證:``file: `scripts/lumos`(patch 內 `_note_reread_blocking`、`_note_reread_judge` 的 `late=[…]`)``
建議:late 篇數過多(例如超過候選一半)時仍擋,或在帳上標記後由 doctor 追蹤。

### 已讀,無 finding
- tab 與空白混用:`expandtabs(8)` 一致,內聯迴圈與 `_note_reread_indent` 行為相同。
- 空行與只有空白的行:一律跳過,不入堆疊。
- 起點取法的「範圍全是空白」分支:內聯迴圈裡 `inf` 節點用 `stack[-1]` 回傳,邏輯自洽。新側行數 0 的 hunk 沒有鏈,是因為帶 3 行上下文時只會出現在清空檔,論證成立。
- Python 裝飾器:函式體內的 hunk 鏈指向 `def` 行,裝飾器不影響。
- 批次讀超過總量時的退路:`_nodehome_cat_blobs_capped` 跳過超量的物件,`_note_reread_fp_blob` 退到單支讀,仍受 `_NOTE_REREAD_FP_MAX` 與 `deadline` 限制。`sizes=[None]` 時回 None,走「git 失敗」退回 v1,不會誤算。
- 資料狀態五問:無新增持久格式。帳上新增 `late` 欄位向下相容,舊讀者忽略它。

最高等級 major,blocking 1 條。
