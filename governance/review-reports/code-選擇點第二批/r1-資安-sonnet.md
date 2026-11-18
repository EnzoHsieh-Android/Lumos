severity: clean

我讀了 `r1-snapshot.patch` 中 scripts/、configs/、skills/、docs/ 的全部改動。卷證散文只掃過。沒有找到可利用的洞,所以沒有重現可附。

dispatch-lens 的 `.warming` 鎖檔不存在(ls 與 cat 都回「No such file or directory」)。沒有鎖要處理,我沒刪任何東西。

## 逐類檢查

- **① 提示注入:已看,無。** 新增的程式只讀型錄的「已撤列號:」那一行、樣本檔的行尾標記,以及治理帳的 `row`、`label`、`file`、`fp` 欄位。這些都只用來比對列號或印在 `gov --stats`,沒有流進派工詞、hook 附加段或 AI 指令。印出時 `row` 與放行標籤都先過 `_kill_esc`。
  - 引句:「print(f"      {_kill_esc(row)[:20]}:壞法 {d['mut']}、殺掉 {d['killed']}、存活 {d['survived']}、跑不出結果 {d['no_result']};放行 {_kill_esc(w)}")」
- **② 讀寫與執行越界:已看,無。**
  - 新增的 scripts/lumos 與 check.py 程式沒有 `subprocess`、`shell=`、環境變數覆蓋下載來源或網址的寫法。
  - 唯一新的檔案讀取是 `_choice_sample_marks` 讀 `<rules_dir>/samples/*.kt`。`rules_dir` 預設是 `CHOICE`,由 `Path(__file__).resolve()` 算出,不接受外來路徑。
  - 壞法編輯 `_choice_anchor_edits` 只對記憶體裡的位元組做替換,不寫檔也不展開 shell。
  - 測試檔新增的 `subprocess.run([sg, "scan", ...])` 是 list 參數,沒有 shell 插值。測試的暫存目錄走 `mkdtemp`。
  - 新增的 ast-grep 規則、樣本與型錄列裡,沒有密鑰或信箱。網址都是 Kotlin、Android、論文的公開文件。
  - 型錄「需補的 import」那欄(例如 C-35 的 `kotlinx.coroutines.flow.zip`)仍受 `_CHOICE_IMPORT_RE` 限制成合法的點分識別字。
- **③ 非刻意一步繞過的守衛:已看,無。**
  - 「已撤列號」守衛的讀法是:沒有那一行視同空,寫「(無)」是空,其餘必須全是列號與分隔符,看不懂就報問題(`_choice_retired`)。
  - 這道守衛不會被 `LUMOS_SKIP_*`、`PYTHONPATH` 之類殘留環境略過。
  - 新增的 `choice_sample_mark_problems` 不依賴 ast-grep,沒裝 ast-grep 時照樣檢查,所以沒有「沒裝就靜默過關」的路徑。
  - 我推敲過「標題行打錯,撤列守衛就悄悄失效」這條路,但寫不出具體的攻擊路徑四件,依抑噪紀律不報。

## 圖譜鏡頭

這次沒有附固定席節點(`LUMOS-LENS` 寫「這次沒附固定席節點」),所以沒有逐條判的項目。範圍 `6857e3d60..eebb84593` 動到的檔,在資安面上都是本機規則包自檢與統計輸出。它們不碰登入、權限、付款、個資、上傳或對外呼叫,不影響任何已登記的資安護欄。

最嚴重:clean;blocking 共 0 條
