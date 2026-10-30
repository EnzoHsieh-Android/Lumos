severity: minor

## 一、分層與依賴方向

對齊。這份 diff 只動使用說明、測試與圖譜筆記,沒有執行期程式碼,所以沒有跨層直呼。
- 範本檔放在 `skills/lumos-project-notes/commands/target-arch-*.md`,跟 DDD、前端兩份同層。
- 06 的 `arch_targets` 那一列和技能首頁各加一句指路,跟前端範本當年的接法一致(`06-代碼審與推送.md`、`SKILL.md`)。
- 測試仍是 `scripts/test_lumos.py` 裡的 `t_arch_target_*`,讀範本檔的方式沿用 `_need_src` 加 `GRAPHCTL` 路徑(對照 `scripts/test_lumos.py:15449`、`:109151`)。
- 圖譜面:新計劃筆記的區段(問題與最小解、做法、驗收條款、回退、實務隱患、審計修正紀錄)與 `Projects/DDD目標架構範本_計劃.md` 的區段順序相同。`Systems/arch-alignment-lens.md` 也照前端那節的寫法,加一節帶日期與計劃連結的段落。

## 二、命名與錯誤處理

大致對齊,有兩處小不一致。
- 對齊的部分:
  - 測試名 `t_arch_target_android_template_{valid,linked_from_usage,konsist_names_match}` 照前端的 `t_arch_target_frontend_template_*`。
  - 常數 `_ANDROID_TEMPLATE` 對應 `_FE_TEMPLATE`。
  - 節點名 `Android目標架構` 與 `DDD目標架構`、`前端分層目標架構` 同形。
  - RULE 行的必有鍵都齊,格式與 DDD、前端兩份範本相同。
  - 測試檢查式用 `check(...)`,跟鄰居一樣。
  - 測試尾端沒有 `print("  ✓ …")`,跟前端那兩支一樣(DDD 那三支有),所以不算新分歧。
- 不對齊的見 ARC-1、ARC-2。

## 三、第二種做法

- 取範本區塊的小工具:鄰居是「一份範本一支 `_xxx_template_block()` 函式」,Android 改成另一種簽名的 `_android_template_section(title)`,而且 `valid` 測試裡又手寫一次圍欄切法。見 ARC-1,結構上等價,只算 minor。
- Konsist 的 Kotlin 骨架:前面兩份範本都沒有「可執行程式骨架加對照表」這種內容。DDD 範本只在 `target-arch-ddd-template.md:63` 順帶提到 Konsist 這個名字,所以專案裡沒有既有做法可對。見下面 ⚠。

ARC-1
引句:「def _android_template_section(title):」
``file: `scripts/test_lumos.py:15449` ``(`_ddd_template_block()`),``file: `scripts/test_lumos.py:109151` ``(`_fe_template_block()`)
說明:前兩份都是無參數、專抓「## 範本」那一節裡 markdown 圍欄的函式,函式裡順手做「前置:有圍欄」的檢查。Android 新寫了參數化的切節函式,圍欄的切法在 `t_arch_target_android_template_valid` 裡又寫了一遍。功能相同、形狀不同,結構沒壞,後來的人要在兩種寫法間選。
severity: minor
blocking: 否

ARC-2
引句:「在那一行加 `[test:<平台>:<測試名>]`,讓機器守、審查席補看」
``file: `skills/lumos-project-notes/commands/target-arch-ddd-template.md:63` ``(寫 `[test:<測試名>]`),``file: `skills/lumos-project-notes/commands/target-arch-frontend-template.md:58` ``(同樣寫 `[test:<測試名>]`)
說明:兩份兄弟範本教人寫不帶平台的 `[test:<測試名>]`,Android 範本改教帶平台前綴。圖譜裡有帶前綴的寫法(`Projects/測試名收自由字串_計劃.md:67`、`Projects/Macrobenchmark驗收門檻_計劃.md:55`),但那份計劃寫明:不是專案已定義的平台時,冒號前的片段會被判成壞名。單平台專案照抄可能被擋。
severity: minor
blocking: 否

⚠ 交編排者:Konsist 骨架與「規則與測試名對照表」(`target-arch-android-template.md` 的「Konsist 骨架」一節,以及對應的 `t_arch_target_android_template_konsist_names_match`)是專案裡沒有先例的內容類型。我判不準這算「新增能力」還是「第二種做法」,不硬判。計劃的 PRIOR-ART 與 REVISIT 已交代來源與回頭條件。

不對齊共 2 條,其中 major 0 條
