severity: major

## F1 decision 相關寫入(`_fmt_decision_value`)沒有跟著改走 `_yaml_plain_ok`/`_yaml_quote`,同一種壞法還在
severity: major
blocking: yes
引句:「return v if _yaml_plain_ok(v) else _yaml_quote(v, key)」

這次改動的重點正是上面這行(以及 `fmt_list_item` 改走的 `return v if _yaml_plain_ok(v) else _yaml_quote(v, "清單項")`)所代表的統一:`fmt_scalar` 與 `fmt_list_item` 共用同一支白名單,全寫入指令的引號規則統一。r2-snapshot 的圖譜筆記也寫了這句宣稱:「fmt_scalar 與 fmt_list_item 都改走它,所以 set 其他欄位與 append 一併修到」。但 `scripts/lumos:14312` 的 `_fmt_decision_value`(原文是「decision 子欄位值格式化(含 ': ' 或特殊字元 → 引號,避鐵則 3)」,供 `cmd_decision_add`、`cmd_decision_supersede` 寫 `content`/`context`/`why_chosen`/`superseded_by` 用)是另一支獨立手刻的舊版判準,沒有被這次改動碰到(不在這次凍結 patch 裡),而且是同一批人在改 `fmt_scalar` 時特別點名要修的那兩種壞法它都還在:

1. **結尾冒號不加引號**:`fmt_scalar` 已經加了 `not v.endswith(":")` 這條(因為 `key: 值:`  這種結尾裸冒號在標準 YAML 是非法的 mapping),但 `_fmt_decision_value` 的判準只有 `^[\[\{>|*&!#@\`"']|^\s|\s$`,不管結尾冒號。實測:

   ```
   lumos decision-add Systems/X "結尾冒號:" --decided 2026-09-26
   ```
   寫出 `content: 結尾冒號:`,用 `yaml.safe_load` 讀會直接炸:`yaml.scanner.ScannerError: mapping values are not allowed here`。本工具自己讀得回來,但 Obsidian/標準 YAML 讀不了——正是這次改動要堵的那個洞。

2. **加引號時用 `.replace('"', '\\"')` 硬塞反斜線跳脫**,而讀的一側(這支工具自己)不解跳脫,新程式碼的註解已經講明「讀的一側只剝掉頭尾一層引號、不解任何跳脫」。實測一個同時含 `: ` 與內嵌雙引號的決策內容:
   ```
   lumos decision-add Systems/X 'note: 他說 "好" 才對' --decided 2026-09-26
   ```
   結果是 `擋下:寫完讀回來檢查,decisions 的值跟要寫的不一樣,這次寫入不算成功`——自驗把它攔下來了(沒寫壞檔案),但功能整個炸掉,一般人合理的決策描述寫不進去。這正是 `_yaml_quote` 存在的理由(先試雙引號不解跳脫、再試單引號、兩者都不行才擋),但 `_fmt_decision_value` 沒有走這條路。

`_list_key_scalar_to_list`(13494 行)在同一輪已經改成呼叫 `fmt_list_item`,`cmd_new`/`cmd_set`/`cmd_append` 也都經過 `fmt_scalar`/`fmt_list_item`,只有 decision 這條路徑是漏網的第三套手刻引號邏輯。建議 `_fmt_decision_value` 直接委派給 `_yaml_plain_ok`/`_yaml_quote`(或呼叫 `fmt_scalar` 本身,只是要留意 decision 欄位沒有日期 bare 的特例)。

---

已看,無:
- `_yaml_plain_ok`/`_yaml_quote` 的白名單與加引號策略(先雙引號、不行換單引號、兩者都不行就擋)跟同批新增的錯誤訊息風格一致,句式都照「發生什麼→為何在意→要做什麼」寫(例如 `_yaml_quote` 的 ValueError:「同時有單引號、又有雙引號或反斜線,工具寫不出…,檔案沒動;把其中一種引號換掉再寫」)。
- `fmt_scalar`/`fmt_list_item` 改寫後行為與舊版在既有測試涵蓋的案例上等價,只是判準從「列舉要加引號的」換成「白名單放行、其餘一律加引號」,方向與圖譜筆記記載的動機(標準 YAML 相容)一致。
- `_set_conditions_locked` 拿掉專用的 `_fmt_cond`、改共用 `fmt_scalar`,插入新欄位位置的邏輯(`next(... kind in ("list","block") ...)`)跟既有 `edit_fm_scalar`(13434 行)「插在第一個 list/block key 之前,否則末尾」的規則等價,且註解直接點名對齊那支函式,沒有另起爐灶。
- `_list_key_scalar_to_list` 沒有被這次改動碰,但原本就是呼叫 `fmt_list_item`,沒有另一套手刻邏輯,符合這次要檢查的範圍。
- `cmd_new` 的欄位填值都經 `cmd_append`/`cmd_set`,沒有自己重刻引號規則。
- 新增測試 `t_set_condition_fields_standard_yaml_safe` 的命名、docstring 格式(`[S6]`、「出身:」段落、`check()` 呼叫方式)跟同檔鄰近的 `t_set_condition_fields_*` 系列一致,案例表格式(`(值, 期待寫出的那一行)`)清楚易讀,沒有另立風格。
