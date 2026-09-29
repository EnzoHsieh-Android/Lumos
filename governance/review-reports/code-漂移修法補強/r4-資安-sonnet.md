severity: minor

## F1 casefold 比對鍵讓 Unicode 大小寫折疊等價(ß 與 SS)的另一個目錄被標成「同提交」
severity: minor
blocking: 否
引句:「return nfc(d).casefold()」
佐證行:file: `scripts/lumos:28001`
1. 輸入:提交只加了 `governance/review-reports/STRASSE/`;磁碟(分大小寫的檔案系統,例如 Linux/CI)上另有沒被該提交碰過的 `straße`、`Straße`。
2. 走到 `_drift_c4_same_commit`:`by_key` 用 `nfc(x).casefold()` 分桶,`"STRASSE"`、`"straße"`、`"Straße"` 折成同一個鍵。
3. 實測(直接呼叫函式,existing 集合給那四個名):輸出 `['STRASSE', 'Straße', 'straße']`,沒被提交碰過的兩個也被當成「同提交」印出、標來源。macOS 預設檔案系統下無法同時建立這些目錄,未能在真檔案系統重現,只在函式層重現。
4. 影響僅止於證據頁多列一行誤標來源的現存目錄(只列出、不寫檔、由人挑),不能指到不存在或目錄外的路徑;docstring 只說「不分大小寫的檔案系統才會有」,對分大小寫的檔案系統其實也會發生,措辭不準。要精確只需改用 `casefold` 前先 `lower`(ß 不折)或只在鍵相等且 `os.path.samefile` 時併入;此列不擋。

## 其餘查過、無 finding
- 終端跳脫:`_drift_c4_show_name` 對類別 Cf(RLO/LRI/RLI/PDI/ZWJ/ZWSP/BOM/tag 字元)逐字換成 `\uXXXX`,`_esc_clean` 再把 C0(含 ESC、換行)與 DEL、C1(0x7f-0x9f)換空格。實測輸入 `x y‮z\u0085\x1b[2Jq` 輸出 `x y‮z  [2Jq`(只有 U+2028/2029 行分隔符原樣通過,類別 Zl/Zp,終端不當換行、證據頁也沒有被機器逐行解析,不算洞)。非 UTF-8 位元組由 `_nodehome_show` 換替代字元。範本句與指令行同樣過 `_esc_clean`。
- casefold 拿來當指向別目錄的手段:鍵只用來從「現存目錄」挑要列的名字,印的是磁碟實際名、不印 git 名,不能造出不在 `existing` 裡的路徑或跳出 `governance/review-reports/`(`parts[:2]` 與 `len>=4` 已限制),`<卷證>` 也仍由人手填。
- 刪除守衛撤回:`git diff 9cc20926 43270394 -- scripts/lumos` 的 hunk 完全沒碰 `_delguard_*`/`cmd_delguard_check`,回到基準原文;`_VENDORED_ALL`、`vendored-skip` 在 delguard 區(scripts/lumos 29300-29760)零殘留;patch 內殘留的 `vendored-skip=` 字樣全在被刪的 `-` 行或註明「已撤」的筆記句。撤回不新增可繞過的縫,退回的是原本「工具更新造成誤報」的已知狀態(已有 Issue),不是新繞過。

## 圖譜鏡頭逐條判定
- 存量漂移守衛(家):只動 c4 證據頁顯示與比對鍵,不動寫檔路徑;不影響其合約。
- bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-read、lumos-cli-lifecycle、design-loop 的 ★INVARIANT★:此次改動不觸及各自綁的行為(閘的 rc 判定、kill 優先序、授權白名單、re-inject sentinel、search 過濾、處置閘),判不影響;授權白名單未動、`_VENDORED_TOOLKIT` 未動。
- 其餘「超出上限只列名」的節點:資安面沒有牽連。

最高等級:minor
