severity: clean

**1. 分層與依賴方向:對齊**
- 這份 diff 沒有新增函式、模組或呼叫關係,只擴充 Room 守衛原有的正規式和提醒字串。
- `_RG_TRIGGER_RE`(`scripts/lumos:46903`)仍是常數加 `re.compile`。前綴 `@(?:androidx\.room3?\.)?` 沿用原寫法,只把 `TypeConverter` 換成 `(?:Column)?TypeConverter`。
- `_rg_spans`(`scripts/lumos:47359`)仍回 `(dao, ms, cs)`。它的 DAO 分支(`:47362`、`:47363`)原本就帶 `(?:androidx\.room3?\.)?`,轉換器分支現在用同一前綴。
- 轉換器第二個分支原本寫 `@TypeConverter\b`,沒有套件前綴。新版補上前綴,反而跟 DAO 分支和第一個分支更一致。
- `_rg_check_sources` 只改了提醒字串,結構沒動。
- 沒有跨層直呼,也沒有新的呼叫方向。

引句:「_RG_TRIGGER_RE = re.compile(r"@(?:androidx\.room3?\.)?(?:Database|Dao|(?:Column)?TypeConverter)\b|(?<![\w.])(?:Auto)?Migration\s*\(")」

**2. 命名與錯誤處理:對齊**
- 新測試 `t_room_column_typeconverter_warns` 和 `t_room_mig_never_exported_hint_room3` 沿用 `t_room_` 前綴。
- 測試開頭的 `print("t_...")`、`_rg_repo()`、`_nh_file`、`_nh_commit`、`_rg(root)`、`check(...)` 跟 `t_room_typeconverter_warns` 逐項一樣。
- 第二支測試的建庫流程(`_nh_repo`、`checkout -b main`、`_rg_db`、`_rg_dao`、`_rg_daotest`、`checkout -b feat`)跟 `t_room_mig_never_exported_warns_not_blocks` 一致。
- 兩支測試的 docstring 都以 `[S43]`、`[S44]` 開頭,跟既有的 `[S29]` 同形。
- 提醒字串仍進 `out["warns"]`,沒有新增錯誤回傳或日誌方式。

引句:「check("Room 3 轉換器只改它也觸發、只提醒", rc == 0 and "提醒" in out, out[-600:])」

**3. 第二種做法:沒有**
- 沒有自創工具函式。剝註解、讀檔、解析差異都沒動。
- 轉換器沒有另外拆一支新正規式,只是在原本的兩個分支裡擴充註記名,維持「一個地方認註記名」的做法。
- 筆記一側(`Systems/room-guard.md` 的 PITFALL 行、`verified_by`、計劃的 S43、S44 和偏離紀錄)沿用既有的欄位與寫法。
- 這次沒有適用的檢核題。

引句:「for m in re.finditer(r"@(?:androidx\.room3?\.)?(?:Column)?TypeConverter\b[\s\S]*?\bfun\s+(\w+)"」

⚠ 一處交編排者判斷:`_RG_TRIGGER_RE` 和 `_rg_spans` 兩處各自重複寫了 `(?:Column)?TypeConverter`。這是原本就有的重複,鄰居沒有共用常數可對,所以不判不一致。

不對齊共 0 條,其中 major 0 條
