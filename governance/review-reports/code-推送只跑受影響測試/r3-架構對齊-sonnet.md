severity: minor

**1. 分層與依賴方向**
- 這輪修補沒有跨層直呼,也沒有新的依賴方向。掛鉤仍只靠 `pitfalls --json` 的欄位和對 lumos 原始碼的字樣探測,不 import 任何東西。對照 `scripts/hooks/pre-push:588-591` 與既有的 `_SUITE_*` 旗標、`:912` 的消費端,結構一致。
- 測試端 `_ppfb_harness` 仍然建在 `_sc_setup` 上(`scripts/test_lumos.py:125819`),方向沒變。
- 這輪把測試場景改成回傳圖譜根 `kg`,取代原本的 `d.rglob("Systems/Home.md")`。這是往既有做法靠攏:鄰居(`scripts/test_lumos.py:77556`、`:80508`、`:109837`)都是拿 `_sc_setup` 的 `kg` 直接組路徑。
- 沒有發現不對齊。

**2. 命名與錯誤處理**
- `_down` 的新值 `spec_light` / `feature_branch`:對照 `scripts/hooks/pre-push:552`,`_suite_this` 的值都是單一小寫詞(full、light、docs)。這兩個值是 snake_case 複合詞。
- 對照 `scripts/hooks/pre-push:470`,狀態旗標是大寫 `_SUITE_*` 的 0/1,這條降級原因變數則是小寫字串。
- `_down` 的值除了 `-n` 判斷(`scripts/hooks/pre-push:595`)沒有別處讀。真正驅動印降級那行的是 `_SUITE_BRANCH_DOWN`(`:591`、`:912`)。所以「原因」這一格資訊其實跟旗標重複,只有註解(`:580-581`)在用。
- 這是命名與記法的小落差,結構沒壞,所以只列 minor。
- 錯誤處理仍是 fail-closed:舊 lumos 沒有欄位、`pf_json` 空,都不降級。與鄰居的「算不出就照全套」一致。
- `_ppfb_harness` 回五元組,拆包命名是 `d, push, g, alog, kg`,不用的位置寫 `_alog` / `_kg` / `_a2`(`scripts/test_lumos.py:125866-125951`)。這跟鄰居慣例對得上:`_sc_setup` 的 `d, kg, _p`(`:109837`、`:125752`),以及前綴底線表示不用的欄位。
- 五元組本身在檔內有先例(`:15437`、`:20544`、`:49599`、`:62113` 都回五元組),所以不算第二種做法。
- 唯一的小不一致:`t_prepush_feature_branch_failclosed` 裡第二組用 `_a2, _kg`,第一組用 `_alog, _kg`(`:125877`、`:125885`)。同一個函式內不同名,但都是丟棄值,無實質差別,不列 finding。

**3. 第二種做法**
- 這輪沒有引入新做法。
  - 新增的 `feat:main` 與 `main:feat` 案例沿用同一個 `push([...])` 與 `check(...)` 寫法(`scripts/test_lumos.py:237-241`),與同函式的混推案例一樣。
  - `_down` 的兩條降級路徑共用同一段取關鍵字與自主迴圈旗標(`scripts/hooks/pre-push:595-599`),沒有複製出第二份。
  - `.lumos/lint-waivers.json` 的放行與文件同步沿用既有慣例。

### finding

severity: minor
blocking: 否
標題:降級原因變數 `_down` 與 `_SUITE_BRANCH_DOWN` 重複記同一件事,值的命名風格也跟鄰居不同
引句:「      _down="feature_branch"; _SUITE_BRANCH_DOWN=1」
file:line:`scripts/hooks/pre-push:588-591`,對照 `scripts/hooks/pre-push:470` 與 `:552`
歸因:有證據的修復造成(只是改名)。修補前是 `_down="light"` / `"branch"`,修補後改成 `spec_light` / `feature_branch`。結構在修補前就是這樣,所以不是回歸。
失敗場景:沒有行為上的壞處。`_down` 只被 `-n` 判斷讀到,沒有分支依賴它的具體值,所以這兩個字串值是純註解用途。要拿它當原因就該被讀,要拿它當旗標就該跟 `_SUITE_*` 一樣用 0/1。

不對齊共 1 條,其中會擋的 0 條。
