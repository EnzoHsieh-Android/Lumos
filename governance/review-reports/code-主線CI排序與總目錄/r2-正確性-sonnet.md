severity: minor

## G1 檔案排序拿掉後這組斷言照綠,「檔案照名字排序」沒有任何測試守
severity: minor
blocking: 否
引句:「files.reverse()」
現象:我在拋棄式 clone 裡把 `_choice_cov_src_pkgs` 的 `for f in sorted(files):` 改成 `for f in files:`,再跑 `python3.14 scripts/test_lumos.py -k choice_cov_src_pkgs`,8 條全綠。
為什麼錯:`_rev_walk` 雖然也把 `files` 倒序,但測試樹裡「看滿上限切點上有兩支以上、會被收進去的原始碼」的資料夾不存在。唯一一個同資料夾有兩支檔的是 `app/src/main/java` 的 `pipe.kt` 和 `sym.kt`,兩支都被跳過。所以檔案層的排序從來沒被碰到。這個缺口修正前就有,r2 沒補上。PITFALL 的「修法」寫「資料夾與檔案照名字排序」,檔案那一半沒有守衛。
怎麼重現:在 clone 裡改掉 `sorted(files)`,跑上面的 `-k`。要補的話,在某個資料夾放兩支套件不同的 `.kt`,並讓切點落在它們中間。

## 查證摘要(1~4 都沒找到問題)

1. **穩定性與 k 的上限:沒問題。**
   - 測試樹約 16 支檔,k 在 1 到 59 之間一定有解。
   - k 夠大時 `_cut_at` 會收到全量,`!= got` 為假,所以搜尋會停在「第一個收得到東西又沒收全」的 k。
   - 切點會卡在 `pipe.kt` 和 `sym.kt` 這兩支被跳過的檔(它們仍計入 seen),所以 k=1 收到空集合;這跟註解說的一致,而且 k 的搜尋就是為此而生。
   - 找不到 k 時 `part=set()`,「★前置★」那條 `bool(part) and part < got` 會紅,不會靜默通過。退路是對的。
   - k 在不同檔案系統順序下可能不同,但斷言的是同一個 k 下正序和倒序結果相同。這等同於斷言排序存在,跟 k 是多少無關。
2. **try/finally 殘留:沒問題。**
   - `_cut_at` 的 finally 把 `_os_mod.walk` 還原成 `real_walk`、把 `_CHOICE_COV_SRC_MAX` 還原成 old,兩個狀態都會還原,函式在 `return` 之前也會走 finally。
   - `_rev_walk` 內部呼叫的是 `real_walk` 而不是 `os.walk`,所以不會遞迴。
   - 被 `return out` 中途丟掉的 generator 沒有副作用。
3. **拿掉排序會不會紅:資料夾排序會紅。**
   - 拿掉 `subs.sort()`(連同只拿掉 `subs.sort()` 兩種都試過),「順序無關」那條都紅,訊息為 `{'testapp','org/b'} {'bom/x'}`。
   - 「★前置★」那條仍綠,代表紅燈確實來自順序斷言本身。
   - 檔案排序見 G1。
4. **既有斷言:沒被削弱。**
   - 「補修 看滿上限就停、印一行提醒」(`len(cut)<=1`)和 ENTRIES 那條都原封不動。
   - 它們在上限 1 時本來就偏弱,但那是修正前就有的,不是這次造成的。
   - r2 只刪掉舊的順序斷言並替換成兩條新的,`real_walk` 與 `_rev_walk` 的定義位置與前後斷言都沒動。

我在 `/tmp/lumos-seat-work/code-主線CI/r2正確性/` 建的 clone 與紅燈殘留的 `gctl-run-s7imx6ra`、`gctl-run-e_o3j08c` 都已刪掉。系統暫存目錄裡還有一批 `gctl-run-*`,不是這一輪全建的,我沒動,只留下 `mutA.py`、`mutB.py`、`mutC.py` 三份變異檔。

我跑第一次變異(拿掉 `subs.sort()`)時,還有一份紅燈現場沒記下目錄名,可能仍留在上述目錄裡;那份我無法確認是哪一個,沒有刪。

相關程式位置:`scripts/lumos:80356`(`_choice_cov_src_pkgs`),`scripts/test_lumos.py:150482`(`t_choice_cov_src_pkgs_edges`)。
