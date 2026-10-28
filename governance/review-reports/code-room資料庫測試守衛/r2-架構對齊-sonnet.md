severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/e61b41df…json.warming` 不存在(ls 與 cat 都回找不到),沒有鎖要處理,我沒刪任何東西。我沒讀上輪席報告。對照碼取自固定版本 680b7870 的 `scripts/lumos`,我另存一份在 `/tmp/lumos-seat-work/code-room資料庫測試守衛/架構對齊-sonnet/lumos.py`。

## 問 1 分層與依賴方向

大致對齊,另有一處不一致(F1)。

- `_rg_strip` 改成只轉呼叫 `_strip_c_comments(blank_strings=True, keep_newlines=True)`,不再自帶 `_C_STRIP_PAT` 掃描。
  - file: `scripts/lumos:6752` 共用剝註解已有 `blank_strings` 這個布林參數。新參數 `keep_newlines=False` 的命名和預設值同一種寫法。
  - 既有呼叫端(`scripts/lumos:6841` 的 `discover_test_methods` 剝註解、`scripts/lumos:37063` 的 `_kt_strip_comments`)不傳新參數,行為不變。
- `_rg_root` 改呼叫 `_note_audit_root(repo)`。
  - file: `scripts/lumos:48432` 這支函式的內文,就是被刪掉的那三行,而且 `scripts/lumos:48714`、`48776`、`62028` 等處都在用。
  - 這是對齊,而且去掉了重複寫法。
- `_rg_range` 改呼叫 `_note_audit_start(root, a, tip, push)`。
  - file: `scripts/lumos:48424` 這是筆記內容審與回頭重讀共用的入口,`scripts/lumos:48392` 也這樣用。
  - 對齊。會多印「起點——」前綴,跟那兩道閘同款。
- `_rg_fork_point` 改問 `_push_range_start(root, "0"*40, tip, *push)`。
  - file: `scripts/lumos:61746` 起點只在這一處算,說明裡寫「★起點只在這裡算一處★」。`_rg_fork_point` 之前自己用 `_push_mainlines` 加 `_push_pick_base` 算,所以這是收回既有入口,不是繞過。
  - 舊值給全 0 時,沒有主線會落到 `_EMPTY_TREE_SHA`(`scripts/lumos:62047` 的 `_push_no_mainline`),`_rg_fork_point` 再把它轉成 None。語意跟舊版一致。
  - 「用全 0 假舊值只問分岔點」在專案裡找不到先例,但它是共用函式文件明寫的合法輸入(「40/64 個 0=新分支首推」),所以不列為 finding。
- 手動跑(不帶 push 參數)的路徑仍走 `_lens_default_base(include_local=True)`,跟鄰居同(`scripts/lumos:62104`)。

## 問 2 命名與錯誤處理

- 新函式 `_rg_mock_re`、`_rg_const_value` 都用 `_rg_` 前綴,模組內命名一致。
- 新參數 `keep_newlines` 的形狀與預設值都跟 `blank_strings` 同款。
- 回傳形狀(`_rg_const_value` 回 `(值或 None, 檔的 tuple)`,找不到就 None)跟鄰居「查不到回 None 讓上層降級」同一種寫法。
- `_rg_check_sources` 新增的「整個專案沒有結構檔」走 `out["warns"]`,這和同函式原有的 `exportSchema = false` 提醒走同一條通道。
- 以下是不對齊的一條。

## F1 索引表同一格出現第二種列法
severity: minor
blocking: 否 因為只是子指令群組的列法跟同表其他列不同,結構沒壞(否 ↔ minor)
歸因：有證據的修復回歸(修前是 `reread-prepare·record·check`,同表其他列沒有大括號)
引句:「note-audit prepare·record·check·skip(筆記內容審)·reread-{prepare,record,check}(回頭重讀)」
file: `skills/lumos-project-notes/commands/INDEX.md:38` 在 680b7870 的整份 INDEX.md 與 skills 下,`-{a,b,c}` 大括號列法只剩這一處。其餘行(如同一格的 `code-loop pass·skip·check`、`guard list·scaffold·bind·…`)都是「前綴 空格 a·b·c」。同一格裡的 `note-audit prepare·record·check` 用的就是舊形狀。

## 問 3 第二種做法

- 剝註解:沒有第二套。Room 守衛原本自帶的那份掃描已刪,改走共用函式。測試 `t_strip_c_comments_keep_newlines` 也驗證 `_rg_strip` 的原始碼裡不再有 `_C_STRIP_PAT`。
- 讀常數:`_rg_const_value` 是專案裡第一支解析 Kotlin/Java 整數常數的函式。我在 680b7870 搜過 `_kt_`、`_testmap_`、`discover_test_methods` 和 `const val`,找不到現成可用的。`_kt_*` 系列只管建置檔判讀,不讀整數常數。所以不算重造輪子。
  - ⚠ 交編排者:`_rg_db_sources` 在 `_rg_triggered` 裡再被呼叫一次(`_rg_triggered` 用它的 `const_files` 判觸發)。我看不出專案有「一次解析、多處共用」的鄰居慣例可對照,不硬判。
- 「只判這次碰到的」:`_rg_check_sources` 用「原始碼、常數定義檔或結構檔目錄有改」過濾。專案裡其他閘(`cmd_note_shape` 與 `_nodehome_clamp_base` 那一帶)也是「只判碰到的」,但各自以自己的資料結構實作,沒有共用函式可直呼。
- 筆記行寫法:
  - 系統筆記新增的 WHY 與 REVISIT 都符合 CLAUDE.md 前綴表,`[出處:][因:][不選:][test:]` 俱全,日期格式 `REVISIT:YYYY-MM-DD 一句` 跟 `macrobenchmark-adapter.md:28`、`掛鉤存活事件.md:18` 同款。
  - 新 WHY 的 `[出處:]` 寫成純文字「代碼審 code-room資料庫測試守衛 r1 正確性席」,沒有 `[[…]]` 連結。同節點舊 WHY 有 `[[Projects/Room資料庫測試守衛_計劃]]` 連結。這是寫法細節的差異,不列為 finding。
  - 計劃的三條「實作偏離紀錄」跟既有兩條同一種「日期 + 實作:」寫法,每條帶 `[test:]`。

## 固定席筆記

這次沒有附固定席筆記,無項可判。

不對齊共 1 條,其中 major 0 條
