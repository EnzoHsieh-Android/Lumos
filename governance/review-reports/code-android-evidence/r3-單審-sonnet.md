severity: major

## 1 新範本沒登記進「工具自裝檔」清單,守衛測試在修後版本翻紅
severity: major
blocking: 是
引句:「+  - scripts/templates/android-receipt-rerun.sh」
歸因:有證據的修復回歸。修前版本(49283648)的 `scripts/templates/` 只有 3 個檔,腳本當時寫在 reference.md 裡。修後版本(d3a17c71)新增這支檔,但 `_VENDORED_TREE_FILES` 沒跟著登記。
失敗場景:
- `scripts/lumos:31914-31927` 的 `_VENDORED_TREE_FILES` 只列 graph-discipline.md、note-audit-judge.md、note-audit-reread.md。
- 安裝器用 rglob 把整個 `scripts/templates` 複製進消費專案,所以 `android-receipt-rerun.sh` 會被裝進去。
- 但它不在 `_VENDORED_ALL`,消費專案會把它當專案自己的程式:推送閘的風險分級被撐高,「每支檔有家」也會擋它。
- 這跟 SKILL.md 與 reference.md 的說法衝突。SKILL.md 說這是工具鏈的檔,reference.md 說「接上 Lumos 的專案裡同一個路徑也有一份」。
- 這個守衛本來就有逐檔比對的測試(`scripts/test_lumos.py:15300` 的 `t_vendored_file_list_matches_what_install_ships`)。這次修補完全沒跑過它。

file: `scripts/lumos:31914`
重現(修後版本,當場翻紅):
- 命令:`cd /Users/enzo/orca/workspaces/lumos-toolchain/android-receipt-trial && python3.14 scripts/test_lumos.py -k vendored`
- 結果:`✗ 跳過清單 = 工具鏈 repo 裡那兩個目錄底下受版控的每一支檔  少登記:['scripts/templates/android-receipt-rerun.sh'] 多登記:[]`,`86 passed, 1 failed`。
- 修前版本:`git ls-tree -r --name-only 49283648 scripts/templates` 只列三個檔,沒有這支腳本,該測試在那時不可能紅。我沒把修前版本 checkout 下來實跑這個測試,所以修前結果是由檔案清單推出來的,不是實測。

## 2 重跑腳本遇到「收據寫錯」的兩種情況會噴 KeyError 回 1,不是文件說的 2
severity: major
blocking: 是
引句:「+    trace = paths[kv['trace']]」
歸因:有證據的原有漏查。這段程式碼從修前的 reference.md 原樣搬到範本,沒有被修補改動。但三處文件(範本標頭、reference.md、計劃節點)都把回 2 說成「收據本身寫錯」,而這個角落沒被涵蓋。
失敗場景:
- (a)queries.sql 標頭 `trace=zzz` 指到 manifest 沒有的 artifact id。
- (b)標頭 `requires=Q7`,但 Q7 不存在。
- 兩種情況的標頭數和解析數相同、也有 expect、manifest 列的 Q 都在,所以三道防空轉檢查全過。
- 之後走到 `paths[kv['trace']]`(範本第 36 行)或 `chain()` 內的 `qs[...]`(第 25 行),噴 `KeyError` traceback,exit code 是 1。
- 呼叫端會把它當成「量測不符」。這跟 SKILL.md 的「回 2 是收據本身寫錯,照它印的原因修」衝突,也沒印出可讀的原因。
- 測試只涵蓋三種回 2 的情況,沒涵蓋這兩種。

file: `scripts/templates/android-receipt-rerun.sh:36`、`scripts/templates/android-receipt-rerun.sh:25`
重現:
- 在 `/tmp/lumos-seat-work/code-android-evidence/單審-sonnet/t1/.lumos/receipts/r` 下放 manifest.json(artifact id 為 `t`)和 queries.sql(`-- [Q1] session=a trace=zzz requires=- expect=a:n=1` 加一行 `select 1;`)。
- 執行 `sh rerun.sh`:輸出 `KeyError: 'zzz'`,rc=1。
- 改成 `requires=Q7`:輸出 `KeyError: 'Q7'`,rc=1。
- 修前版本的同一段程式碼是同樣結果,所以不是修補造成的。我是用範本在修後版本的複本跑的,修前沒另外實跑。

## 三問
1. 原問題的修復效果:
   - 原問題是「腳本寫在 markdown 裡、測試得抽出來跑」,以及「超大整數讓 `_macrobench_num` 溢位」。
   - 範本現在是真檔,測試直接讀 `scripts/templates/android-receipt-rerun.sh`。
   - 我實跑 `-k macrobench` 得 166 通過 0 失敗,`-k android_evidence` 得 5 通過 0 失敗。
   - 這只證明測試通過,沒做改壞驗證:我沒有去拿掉某道防空轉檢查或 `try/except OverflowError` 看測試會不會紅。
2. 修補處的相鄰路徑:
   - 正常路徑(假 trace_processor 比對相符回 0)和三種回 2 的路徑,測試都有涵蓋。
   - 相鄰路徑有兩個破口。一個是 finding 1:範本進了安裝流程,卻沒進自裝檔清單。另一個是 finding 2:trace 或 requires 指到不存在的東西,會噴例外回 1。
3. 新發現同一案例的修前、修後:
   - finding 1:修前沒有這支檔,守衛測試不會紅;修後紅。這是修補引入的。
   - finding 2:修前(reference.md 內嵌版)與修後(範本版)的程式碼相同,行為相同。這是原有的,不是修補引入的。

## 已驗與未驗
已驗:
- 範本的 rc 0、1、2 在 SKILL.md、reference.md、範本標頭三處說法一致。
- `-k macrobench` 與 `-k android_evidence` 全綠。
- `-k vendored` 有一支紅(finding 1)。
- SKILL.md 的複製指令與 reference.md 的 `cp scripts/templates/... .lumos/receipts/<run-id>/rerun.sh` 都以專案根目錄為前提。這要靠安裝器把範本放進消費專案,而 finding 1 顯示該檔沒被登記進自裝檔清單,所以消費專案能不能照做,取決於安裝器實際有沒有複製它。我沒實裝一個消費專案驗證。

未驗:
- 圖譜鏡頭:範圍 `1c6c0add..d3a17c71` 在本專案算不出來,我沒有逐條判固定席節點。
- 沒有對 macrobench 的各個讀數入口逐一做超大整數的改壞實驗。
- 沒有對修前版本實際 checkout 跑任何測試。

總結:這份報告最高嚴重度是 major
