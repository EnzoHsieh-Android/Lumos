severity: major

## 問 1 分層與依賴方向
不一致。專案現況是兩層各算一份:掛鉤層 bash 的 `_hrange` 供每支檔有家與筆記形狀擋用(`scripts/hooks/pre-push:332-343`),lumos 層 `_push_range_start` 供漂移檢查等用,而且該函式自己的說明寫「★起點只在這裡算一處★……掛鉤的 bash、CI 的 shell 補法、工具端各算一份,三份各有洞」(`scripts/lumos:41864` 起的說明)。材料把更多會擋的閘接到掛鉤層 bash 推導上,方向跟那條已定的收斂方向相反。材料引句:「推送前掛鉤的所有閘改走 lumos 的 `_push_range_start`」——材料自己承認那是收斂路,卻放在 RETIRE-IF 而不是做法。

## 問 2 命名與錯誤處理
結構大致對得上、命名小差異。既有慣例:`pp_range_for`、`pp_touched_file` 以 `pp_` 開頭(`scripts/hooks/pre-push:39,63`),新名 `pp_block_range_for` 符合前綴。空字串語意:既有 `_hrange` 空字串=跳過該閘(`scripts/hooks/pre-push:345` 的 `-n` 判斷);材料卻把空字串改成頂端..頂端空範圍讓閘照跑,跟 `_hrange` 現行的「空=不查」不同,抽函式後同一函式兩種呼叫端處理。材料引句:「它輸出空字串(這次沒有新提交)時,這幾道用「頂端..頂端」的空範圍跑」。

## 問 3 第二種做法
是第三套。專案已有 `_lens_push_base`(`scripts/lumos:41772`)與 `_push_range_start`(`scripts/lumos:41864`)兩套並存且記有收斂路,掛鉤層另有 `_hrange` 的 bash 版與 `pp_range_for`。材料名為「抽出 `_hrange`」,但把它的適用範圍從兩道擴大到七八道,等於把一份已被審查指出「shell 補法在合過主線、新分支首推一次帶多個提交時算錯」的 bash 算法(`scripts/lumos:37086`)擴散,而不是收斂進 `_push_range_start`。材料引句:「跟同一支掛鉤裡每支檔有家與筆記形狀擋已經在用的算法同一套」。另外 `scripts/hooks/pre-push:327-330` 與 `Systems/每支檔有家.md` 的 KEY 行(第 33 行)明寫「兩套刻意不同……別合併」,材料第 4 步直接改寫該註解,是推翻既有明文,而非沿用。

## 問 4 落點
大致對。`scripts/hooks/pre-push` 在 `Systems/每支檔有家.md` 的 about_code 列內(第 11 行),lands_in 寫它合規;該篇第 33 行 KEY 需同步改寫。⚠ `impact_once` 與受波及合約測試閘的描述在 `Systems/bound-tests-gate.md`(也列了 pre-push),只寫進每支檔有家可能漏掉那篇;另 `Systems/存量漂移守衛.md` 講起點由 lumos 算,與本案「兩處算法並存」的說法也要互相指到。建議 lands_in 補列 bound-tests-gate,或在其內放 SEE 連結。材料引句:「寫回 [[Systems/每支檔有家]](它是推送前掛鉤這段起點推導的家)」。

## F1 在掛鉤層把 bash 起點推導擴大套用到會擋的七道,而非收斂進 `_push_range_start`
severity: major
blocking: 是
引句:「把 `_hrange` 的推導抽成一支函式 `pp_block_range_for <遠端舊值> <本地頂端>`」
對照:`scripts/lumos:41864`(起點只在 lumos 算一處、bash 算法三份各有洞)、`scripts/lumos:37086`(shell 補法在合過主線時算錯)、`scripts/hooks/pre-push:332`。建議:會擋的閘改帶 --push-remote/--pushed-ref 由 lumos 算,或至少先證明 `_hrange` 的 bash 版在合過主線、一次多提交的新分支上不會算錯(材料天花板只提到「基在別人未合併分支」,沒提合過主線這個已知洞)。

## F2 空字串語意在同一函式被兩種呼叫端解讀
severity: minor
blocking: 否
引句:「空字串時設成 `"$_lsha..$_lsha"`」
對照:`scripts/hooks/pre-push:345` 空字串=跳過該閘。建議:函式輸出保持空=沒有新提交,每個呼叫端自行決定;或統一都跳過,不要只有部分閘改走空範圍。

## F3 推翻既有「兩套刻意不同、別合併」註解與 KEY 行,但沒列入同步改寫
severity: minor
blocking: 否
引句:「註解:`_range` 那段原本寫「給波及計算與風險掃描用,只提醒」」
對照:`scripts/hooks/pre-push:327-330`、`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:33`。材料第 6 步只說寫回「會擋的閘共用同一支起點函式」,沒明講那條 KEY 行與其 test 綁定(t_prepush_runs_home_check)要連動改。

不對齊共 3 條,其中 major 1 條
