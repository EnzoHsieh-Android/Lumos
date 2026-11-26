severity: minor

整體看修補都修到了。我讀了整份 repair.patch、追了 `_choice_cov_read` 和 `CODE_SKIP_DIRS` 的呼叫端,並實跑 `-k choice_cov_src_pkgs`、`-k choice_cov_base_read`,2 與 4 案都綠。`_KillPrep` 在測試裡沒有被直接建構,所以新增的 `_src_pkgs` 屬性不會讓用替身繞過 `__init__` 的測試出現 AttributeError。以下兩條都是小問題。

severity: minor
blocking: 否
`scripts/lumos:79795`、`scripts/lumos:6059`:跳過清單改成共用的 `CODE_SKIP_DIRS` 後,`bin`、`obj`、`dist`、`publish`、`vendor`、`.vs`、`__pycache__` 會在任何深度被跳過,包括 `src/main/java/com/x/vendor/` 這種正常主程式套件資料夾。
具體場景:電商或內容管理類的 app 若有 `com.x.vendor` 或 `com.x.publish` 套件,那裡的 package 不會被收進專案套件集合,只碰那個套件的測試會被算成「專案類別 0」。
後果有兩種:一是該測試被判成不明,多跑一次,方向安全。二是如果前三支 Robolectric 測試剛好都只碰這類套件,會誤觸斷路「覆蓋接不起來」,整個平台組的覆蓋被關掉。
引句:「_CHOICE_COV_SRC_SKIP = frozenset(CODE_SKIP_DIRS | {".gradle"})」
修法建議:build 與 .gradle 保留任意深度跳過;bin、obj、dist、publish、vendor、.vs 只在 root 下的第一層跳過,或只跳不在 `src/` 底下的。
我沒有實際跑出斷路,只確認了跳過邏輯,所以降為 minor。

severity: minor
blocking: 否
`scripts/test_lumos.py:150411`(`t_choice_cov_src_pkgs_edges`)和 `scripts/lumos:29145`:新增的兩個行為沒有測試守住,拿掉一樣全綠。
1. `_KillPrep._src_pkgs` 的快取:把 `if root not in self._src_pkgs` 改成每次都重掃,所有測試照綠。
2. `_CHOICE_COV_SRC_ENTRIES`(20 萬個檔)的上限和提醒:測試只用 `_CHOICE_COV_SRC_MAX = 1` 縮小原始碼數,這條分支整個沒走到。
3. 上限案的斷言 `len(cut) <= 1 and "上限" in ...` 偏弱,上限一到就回空集合也會過。
這些保護的只是效率和提醒,不是判定結果。
引句:「check("補修 看滿上限就停、印一行提醒", len(cut) <= 1 and "上限" in buf.getvalue(), f"{cut} {buf.getvalue()!r}")」

其他確認過沒問題的地方:
- `_choice_cov_base_read` 對超大整數、NaN、負數、超過上限都回 None;3.14 的 json 對六萬層巢狀只丟 `JSONDecodeError`,屬於 ValueError,有被接住。
- `store` 把基準檔另包 try,基準寫不下時覆蓋資料照存,邏輯正確。
- 符號連結檔和具名管道都被 `islink`/`isfile` 擋掉,符號連結資料夾因為 `followlinks=False` 不會被走進。

總結:最高等級是 minor
