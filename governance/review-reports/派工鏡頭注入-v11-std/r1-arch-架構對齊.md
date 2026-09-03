# 架構對齊審查:v1.1「每篇固定席標綁定測試狀態」

審材:`governance/review-reports/派工鏡頭注入-v11-std/r1-snapshot.md`(與被審用的 scratchpad 副本逐字相同,已 diff 核對)「## v1.1」節,行 153–167。
範圍:只判這節設計跟本專案既有做法一不一樣,不找 bug、不評風格。

## 問題一:分層與依賴方向(分類邏輯復用方式)

本專案現行的依賴方向是:各個要「判斷某條 ★INVARIANT★ 綁的測試是不是真的」的呼叫點,都直接疊在共用的低階原語 `extract_contracts`(`scripts/lumos:2409`)、`resolve_test_refs`(`scripts/lumos:2744`)、`_platform_test_index`(`scripts/lumos:6344`)之上、各自寫自己的迴圈,沒有互相呼叫對方的高階函式——`_bound_tests_for_diff`(`scripts/lumos:16819`)、`cmd_archive` 的護欄迴圈(`scripts/lumos:10062`)、`classify_invariants`(`scripts/lumos:6393`)三處各自成一套。v1.1 寫「`resolve_test_refs`+`_platform_test_index` 的 real/fake/dangling/bad-name 分類=`_bound_tests_for_diff` 用的同一套」,選的是原語而不是直呼 `_bound_tests_for_diff` 本體,這個方向沒錯,跟既有慣例一致。

但問題在復用的目標選錯了:本專案已經有一支「單條合約行 → 綁定狀態」的既有共用 helper——`_classify_one(x, split, default, methods_for, hay_for)`(`scripts/lumos:6372-6390`),吃單條 ★INVARIANT★ 文字、回 naked/real/fake/dangling,而且已經內建「一行多個 [test:] ref 取最壞狀態」的聚合邏輯,正是 v1.1 需要的粒度(v1.1 只需要把 naked→「無」、real→「有」、fake 或 dangling→「懸空」三個標籤對映過去,不必新寫任何分類邏輯)。這支 helper 目前被 `classify_invariants`/`cmd_guard_list`(`scripts/lumos:6393`、`6410`,也就是「guard trace/list」既有呈現方式的來源)使用,v1.1 整節完全沒有提到它。

v1.1 反而錨定 `_bound_tests_for_diff`——它回的是 (node, plat, method, status) 每個測試參照一筆,不是「每條合約行一個狀態」,而且它多算一種 `_classify_one` 沒有的類別:`bad-name`(靠 `_KILL_METHOD_OK_RE` 對方法名格式做規則檢查,`scripts/lumos:6640` 定義、`scripts/lumos:16860` 使用)。照 v1.1 字面「同一套」去實作,若要把 bad-name 這條規則也搬進來,勢必要嘛跨層直接消費 `_bound_tests_for_diff` 的輸出再自己聚合(介面對不上,它不是 per 行的),要嘛把 `_KILL_METHOD_OK_RE`+real/fake/dangling/bad-name 那段邏輯原樣抄一份到 `_lens_*` 命名空間——這就是在既有的 `_classify_one`(guard 用)與 `_bound_tests_for_diff`(pre-push 閘用)之外,再造第三套「合約行綁定狀態」判定邏輯,而不是抽成閘與鏡頭共用的 helper。

### f1

severity: major
blocking: 是

引句:「`resolve_test_refs`+`_platform_test_index` 的 real/fake/dangling/bad-name 分類=`_bound_tests_for_diff` 用的同一套」

v1.1 把復用目標錨定在 `_bound_tests_for_diff`(per node/plat/method,`scripts/lumos:16819`),完全沒提已存在、粒度剛好對上(per 合約行)的既有共用 helper `_classify_one`(`scripts/lumos:6372`)。照字面實作會走向「自造第三套分類邏輯」而不是抽 helper 共用,見問題三。

file: `scripts/lumos:6372`(既有的正確復用目標,未被引用)
file: `scripts/lumos:16819`(v1.1 錨定的目標,粒度不對)
file: `scripts/lumos:16860`(bad-name 這條 `_classify_one` 沒有,v1.1 若原樣搬會複製這段邏輯)

## 問題二:命名與錯誤處理

fail-open 寫法:v1.1 明寫「多平台專案沒填 `default_platform` 時 `_platform_test_index` 會拋例外……既有閘用 try/except 包成 no-config——本案同樣包住」,這條是明確承諾沿用 `_bound_tests_for_diff` 同款 try/except 包法(`scripts/lumos:16843-16845` 那段 `except Exception as e: return [], f"no-config:…"`),跟既有做法一致,沒有不對齊。

固定字彙的方括號格式:CLAUDE.md 記的既有標記家族是 `[test:]`/`[audit:]`/`[kill:]`/`[rollback:]`/`[guard:]`——全部「英文小寫詞+冒號」;`dispatch-lens` 自己現有的方括號用法(`_LENS_KIND`,`scripts/lumos:16496`)是純中文詞、不帶冒號,如 `[直接相依]`、`[事故]`。v1.1 新造的 `[綁定測試:有]`/`[綁定測試:懸空]` 是「中文詞+冒號+值」,兩種既有格式都不是這個形狀,是第三種寫法。

### f2

severity: minor
blocking: 否

引句:「解得出但方法不存在/只出現在文字裡/名字不合法 → `[綁定測試:懸空]`」

方括號格式跟本檔既有的兩種慣例(guard 家族的英文冒號式、`_LENS_KIND` 的純中文無冒號式)都不一致,結構本身(印固定字彙、不印自由文字)沒問題。

file: `scripts/lumos:16496`(`_LENS_KIND` 的既有中文無冒號格式)
file: `scripts/lumos:6419`(guard 既有的 `[test:…]`/`(未綁)` 英文冒號格式)

### f3

severity: minor
blocking: 否

引句:「★無綁定測試——閘守不到,只剩你讀★」

本專案既有詞彙把「懸空」(dangling,方法找不到)、「偽證據」(fake,方法名出現在程式碼文字裡但不是真測試)、「裸合約/未綁」(naked,根本沒綁)當三個語義不同、圖示也不同的狀態(`GUARD_ICON`,`scripts/lumos:6333-6334`:❌懸空 / ⚠偽證據 / ❌裸合約)。v1.1 把 dangling/fake/bad-name 三種都印成同一個「懸空」,是借用既有術語但擴大了它的既有語意(讀過 `guard list`/`doctor` 輸出的人會預期「懸空」不含「偽證據」這種更嚴重的狀態);「無 [test:] 綁定」這個既有已有專有名詞「裸合約」的概念,v1.1 另造「無綁定測試」新詞,沒有沿用既有詞彙。

file: `scripts/lumos:6333`(`GUARD_ICON` 既有的四態分詞)
file: `scripts/lumos:6419`(既有「(未綁)」一詞,對應「裸合約」概念)

## 問題三:第二種做法(自創一套 per-line 分類 vs 抽 helper 讓閘與鏡頭共用)

直接回答:是自創一套的風險,不是抽 helper 共用。證據見 f1——本專案已經有粒度對得上的既有共用 helper `_classify_one`(`scripts/lumos:6372`,已被 guard 家族用),v1.1 整節不提它,反而錨定粒度不對、且多一條 `_classify_one` 沒有的 bad-name 規則的 `_bound_tests_for_diff`。順著 v1.1 字面走,實作端要嘛得跨層硬湊 `_bound_tests_for_diff` 的輸出(node/plat/method → per 行,介面不合),要嘛把它的分類迴圈原樣複製一份進 `_lens_*`——兩條路都是「引入第二種做法」,不是「抽 helper 讓閘與鏡頭共用」。真正對齊既有做法的路徑是:呼叫或視需要小幅擴充 `_classify_one`(例如讓它可選擇性回報 bad-name),讓 guard 與鏡頭共用同一支分類函式,而不是各自維護一套。

不對齊共 3 條,其中 major 1 條
