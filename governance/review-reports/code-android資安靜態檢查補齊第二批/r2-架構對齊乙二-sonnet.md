severity: major

三問全部對照過,共 3 條不對齊,其中 2 條 major。

## 1. 分層與依賴方向

新測試與輔助函式放在 `scripts/test_lumos.py`,型錄列放在主表。這點跟鄰居一樣:`t_kt_catalog_security_lint_ids` 也是把 `_ASL_README_IDS` 這類寫死的預期值放在測試檔,再用 `m.main_rows()` 讀表。

有兩處跨層或重抄。

**1. 批四標籤字面抄在測試裡,另立一套口徑(r2-repair 新增的迴圈)**

severity: major
blocking: 是

引句:
「        if "批四(CI 範本:Android Lint)" not in cell(rid, 9):」

- 這句把 `B4_TAG_LINT` 的值直接寫成字面。
- 鄰居 `t_kt_catalog_batch4_wiring` 一律用 `ck.B4_TAG_LINT` 和 `ck.batch4_expected_tags`。檔頭明寫「口徑住在 check.py(代碼審 r1 架構席:不在測試裡另立一套)」。
    - `scripts/test_lumos.py:129065` 起
    - `configs/ast-grep/kotlin-android/check.py:113`、`configs/ast-grep/kotlin-android/check.py:120`、`configs/ast-grep/kotlin-android/check.py:131`
- 這個迴圈判的是「現成規則欄登了 Android Lint 檢查的列,批四要寫對」。這個口徑 `batch4_expected_tags(cell(rid,5))` 就算得出來,不需要自己維護一串列表。
- 計劃筆記同批補的 REVISIT 也承認「check.py 不判這件事」。意思是測試在補 check.py 沒有的口徑,而不是把口徑放進 check.py。
- 正規的做法是先讓 `catalog_problems` 判,測試再去驗它。

**2. 〈統計〉與〈待查證〉的重數邏輯整套住在測試檔(`_kt_stats_problems`、`_kt_stats_extra_problems`、`_kt_pending_problems`)**

severity: major
blocking: 是

引句:
「    weak = ("未開頁核對", "搜尋摘要", "無網址")」

- 這句抄了一份 check.py 已有的常數。
    - `configs/ast-grep/kotlin-android/check.py:104` 有 `_WEAK_SRC = ("未開頁核對", "搜尋摘要", "無網址")`。
    - 同一批的 `_kt_pending_problems` 只寫了前兩個詞(「未開頁核對」「搜尋摘要」),所以這份抄本內部也已經不一致。
- 逐列查證的列數寫成 `"\u3014查證" in c[11]`。
    - check.py 已有 `_VERIFIED_RE` 和 `catalog_unverified`,判準不同:`_VERIFIED_RE` 要日期加網址,`catalog_unverified` 還認(出處不全)。
    - 位置:`configs/ast-grep/kotlin-android/check.py:565`、`configs/ast-grep/kotlin-android/check.py:569`
    - 兩邊對「逐列查證」可以各算出不同的數。
- 型錄自檢性質的不變量(數字能重數、不靠寫死預期值),鄰居都放 check.py 的 `catalog_problems`,測試只驗它。
    - 例如第四批口徑、`catalog_unverified`,以及 `check.py:373` 對 `_WEAK_SRC` 的使用。
- 〈待查證〉表目前 check.py 沒有讀取函式,所以測試裡自己寫解析不算重抄。
    - 但解析用的 `^\|\s*([A-Z]+-\d+)\s*\|` 是 `_MAIN_ROW_RE`(`check.py:98`)的複本。
    - 而且這批不改 check.py,`--catalog-only` 與推送閘看不到統計與待查證漂移,只有跑這支測試才看得到。

## 2. 命名與錯誤處理

- 測試命名 `t_kt_catalog_security_lint_batch2`、`t_kt_catalog_stats_consistent`、`_kt_batch2_*_problems` 對得上鄰居的 `t_kt_catalog_*`、`_kt_*_problems` 體例。
    - 位置:`scripts/test_lumos.py:129128`、`scripts/test_lumos.py:127379`、`scripts/test_lumos.py:127795`
- 輔助函式回「問題清單(空=通過)」,測試用 `check(...)` 帶訊息尾巴,這跟鄰居一致。
- 型錄列的欄位寫法照既有列:形狀類用「形狀:…」,通電批次用「告警帶寫法=…」,來源欄用〔查證 日期:網址〕。
- `WHY` 行是改既有那一行,沒另開新行,跟鄰居的慣例一致。
- 型錄兩節說明句改成「手寫(沒有程式產生…)」並指向測試名,跟既有〈待查證〉〈統計〉節說明句的口吻一致。

**3. docstring 條款標記不一致(r2-repair 把 `[S3]` 改成 `[第二批 S3]`)**

severity: minor
blocking: 否

引句:
「    """[第二批 S3] 第二批型錄([[Projects/Android資安靜態檢查補齊第二批_計劃]] 範圍 1~3):DATA-83 寫明 VulnerableCryptoAlgorithm 只看 Cipher、」

- 鄰居用裸的 `[S5]`、`[S1]`、`[S3][S4]`。
    - 位置:`scripts/test_lumos.py:129128`、`scripts/test_lumos.py:126936`
- 這次加「第二批」是為了避開跟第一批的 S 編號撞名,有理由。
- 但這是專案裡新的標記寫法。鄰居撞名時是用「[[計劃]] S5」把計劃連結放前面(`t_kt_catalog_unverified_rows`),不是在方括號裡塞前綴。
- 鄰居本身沒有統一寫法,所以標 ⚠ 交編排者定奪,我只給 minor。

## 3. 第二種做法

- 第 1、2 條已涵蓋引入第二種做法的部分,也就是測試裡另抄口徑與常數。
- 其餘對照下沒有新做法。
    - `_kt_batch2_misreg_problems` 用 `cell(rid, i)` 取欄位,走的是 `main_rows` 這個主表唯一讀法。
    - 搜尋 `內建:` 內建檢查 id 用的正則,跟 `t_kt_catalog_security_lint_ids` 的 `資安包:` 正則同形,是鄰居本來就有的做法。

不對齊共 3 條,其中 major 2 條(第 3 條是 minor,標 ⚠ 待編排者裁)。
