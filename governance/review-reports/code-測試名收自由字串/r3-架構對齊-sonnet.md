severity: minor

## 1. 分層與依賴方向

- **`_clause_visible`**:現在只是呼叫 `_strip_inline_markup(line, keep_test_fields=True)` 的一層薄殼。欄位邊界改走 `_slot_scan`(`scripts/lumos:4489`)。這支掃描器的註解寫明「別另寫第二套掃描器」,所以這是從自寫掃描回到既有做法。
- **`_split_test_ref`**:現在是 `_split_test_ref_ex` 外面的薄殼(6087 到 6093)。`_kill_method_name`(18316)和 `_bind_name_problem`(18193)都改走 `_ex`。其餘呼叫點(2146、6060、20731、55412)仍用 `_split_test_ref`。我沒有找到任何呼叫端自己用 `split(":")` 切 `[test:]` 的值。
- **`_strip_test_comments`**:`c-style` 只有一條認得字串的路(6454),所有呼叫端共用,沒有新增第三套剝註解。`c-style+strings`(java,5811)的兩段式不是這次新增的,docstring 也講明它是例外。
- **`_raw_test_titles`**:它仍是第二條列舉標題的路,內建寫死呼叫形狀的 `_RAW_TITLE_RE`。不過它走的是同一個 `_walk_test_files` 和 `_strip_test_comments`。6463 到 6466 的註解寫明兩條並存是編排者裁定的,所以我不計入。
- **`regex_tail`**:不是第三種 name_filter 做法。`_REGEX_FILTERS` 和 `_TITLED_FILTERS` 兩個常數(54762、54763)統一了判斷,`_name_filter_escape` 也用 `_REGEX_FILTERS`(19498)。
- **`_ANCHOR_MAP_CACHE`**(6415):是模組層快取,和 `_DRIFT_LS_CACHE`、`_NODE_FLAVOR_CACHE` 同一種寫法。`scripts/test_lumos.py` 的 98626 行有 `.clear()`,和 `_DRIFT_LS_CACHE.clear()` 的做法一致。

## 2. 命名與錯誤處理

- **合法性訊息**:`_TEST_NAME_RULE_ZH` 現在只有一份(6118),擋下訊息有 4 處用它(18185、18582、19847、55416)。有兩處沒用它,見 finding 1。
- **常數裡的數字**:白話把 `200` 和 Windows 特殊字元手寫在文字裡,見 finding 2。
- **回傳碼與命名**:`_TestRefPrefixError` 仍是 ValueError 子類,舊呼叫端照接。`lenient=True` 的參數名和既有的 `_ex` 後綴風格一致。
- **docstring 殘留(只是備註,不算不對齊)**:`_name_filter_escape` 的 docstring(19495 到 19496)還寫著 `(?:^|\s)<名字>$`,實際碼已是 `\s…(?:\s@\S+)*$`。

## 3. 第二種做法

我搜過自己切冒號、自己掃反引號或 `[test:`、自己的剝註解正規式、重複的合法性文案,以及 name_filter 的字面比較,都沒找到新的第二套。要留意的只有兩處:
- `_name_collisions_across` 是 `_name_filter_collisions` 內部的新輔助,不是平行的另一條路。
- `_raw_test_titles` 是已裁定並存的例外。

## Findings

### Finding 1:合法性訊息沒有全部收成同一句

`scripts/lumos:15503` 印的是 `測試名不合法({method})`,只有名字、沒有規則。`scripts/lumos:54824` 是另一種措辭 `測試名不合法或平台前綴未定義`。這兩處在修補差異之外,不過 diff 裡的常數註解宣稱「擋下訊息全部用這一句」,與這兩處不符。結構沒錯,只是訊息形狀不一致。

severity: minor
blocking: 否
引句:「# _test_name_ok 的白話,擋下訊息全部用這一句(代碼審 r2 架構席)」
審材外佐證:`scripts/lumos:15503`、`scripts/lumos:54824`

### Finding 2:白話常數把數字手寫進文字

`200` 和 Windows 特殊字元在 `_TEST_NAME_MAX`、`_WIN_CMD_SPECIAL`(6065 到 6068)已有定義。白話裡又手寫一次,日後改常數時白話會失真,目前沒有守衛連動。這是維護性問題,不是結構問題。

severity: minor
blocking: 否
引句:「_TEST_NAME_RULE_ZH = ("不能是空的、不能超過 200 字、不能以減號開頭、不能含方括號或半形逗號、不能有控制字元;"」
審材外佐證:`scripts/lumos:6065`、`scripts/lumos:6068`

不對齊共 2 條,其中 major 0 條。
