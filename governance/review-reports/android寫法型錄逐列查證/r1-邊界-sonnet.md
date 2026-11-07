severity: minor

整體判斷:這次人裁落地的邊界行為站得住,沒有 major 以上的問題。我實跑了以下檢查,結果都符合快照的條款:

- 在 `/Users/enzo/orca/workspaces/lumos-toolchain/catalog-rulings` 跑 `check.py --sg <ast-grep>`:規則 211 條、問題 0 個、還沒逐列查證 0 列。
- `-k` 子集 `t_kt_catalog_unverified_rows`(10)、`t_kt_catalog_security_lint_ids`(5)、`t_kotlin_rulepack_unwired_dir`(11)、`t_kt_catalog_batch4_wiring`(18)、`t_kt_catalog`(48)全綠。
- 破壞性試驗一:在臨時複本把 `kt-async-await-immediately` 搬回 `rules/api.yml`。自檢報「引用出處不全的 API-14,只准放 rules-unwired/」,退出碼 1。
- 破壞性試驗二:把同一條規則複製一份放進 `rules-hints/testing.yml`。自檢報「id 重複」和「只准放 rules-unwired/」兩個問題。
- 統計節的數字(error 34、warning 115、info 12、hint 50、14 條在 unwired、出處不全 35 列、有查證紀錄 501 列)與程式重算一致。
- `sgconfig-hints.yml` 仍有 41 條規則,`SARIF_PROBES` 用的 `kt-value-assign-background` 沒被動到。宣告了提示級設定的消費專案只少一條 `kt-compose-test-node-by-literal-text`,不會載入失敗。
- DATA-12 的官方原文我對照了 androidx 原始碼 KDoc,字句吻合,KDoc 沒有重試的說法,拿掉「重試時副作用重複」沒有問題。
- 暫存目錄已刪。

### 1
severity: minor
blocking: 否

「出處不全只准放 unwired」的檢查只看規則訊息開頭的編號,不看型錄那一列「現成規則」欄列了哪些規則。實測:STATE-9 名稱標了(出處不全),通電批次寫「規則在 rules-unwired/」,但它列的 `kt-statein-lazily-or-no-timeout` 訊息開頭是 `[STATE-4]`,放在會擋的 `rules/state.yml`(warning 級)。自檢照樣 0 個問題。這是這次改動之前就有的缺口,不是這次造成的。快照的 S3 寫成「訊息引用那一列編號的規則」,所以這次的三條規則(訊息開頭是 `[API-14]`、`[TEST-31]`)被守住了。但「出處不全列的規則一律不擋」這個意圖,同一類的 STATE-9 就沒被守住。

引句:「型錄某列名稱標了(出處不全)時,訊息引用那一列編號的規則 應 全在 `rules-unwired/`」

證據在 `skills/kotlin-idioms/checks-catalog.md:249` 與 `configs/ast-grep/kotlin-android/rules/state.yml:257`。檢查寫在 `configs/ast-grep/kotlin-android/check.py:398-402`。

### 2
severity: minor
blocking: 否

情境決策表 D-1、D-2 的「對應檢查」仍列 API-14,而且 D-2 的標準寫法「不要包 async { }.await()」就是 API-14 那條沒有官方出處的主張。把規則搬進 unwired 後,推送前情境題的表態仍會以這個主張問作者(實跑只掃了對應表,沒實際跑表態閘)。表態閘本身只提醒不擋,所以不違反「推送前不再擋」。但「出處不全的主張不進推送前流程」這個意圖,在情境表這條路沒有對應的檢查。型錄自檢也沒有「情境決策表列只引用出處不全列」之類的檢查。查證時 D-1 對應 API-1、API-3、API-14,D-2 對應 API-1、API-14,其他對應列都已查證。計劃的〈守衛面〉只寫了規則包,沒提這條路。

引句:「推送前不再擋這兩種寫法(見〈待人裁〉)」

證據:`skills/kotlin-idioms/checks-catalog.md` 情境決策表的 D-1、D-2 兩列。

### 3
severity: minor
blocking: 否

「取捨提醒」只在計劃筆記定義,型錄的「接電方式五種」圖例沒有這一類,自檢也不認這個詞。DATA-12 實際靠 D-42 的「對應檢查」欄列了它(`check.py:394` 的「語意列要被情境表引用」檢查才放行),不是靠「取捨提醒」這個名字。另外 `samples/situation/D-42.kt.txt` 的反例只有 DATA-7,沒有 DATA-12 的 `updateData { api.call(); … }`。D-42 的主樣式 `\.updateData\s*\{` 對這種寫法也會對上,所以表態為「照標準寫法」時證據樣式放行。DATA-12 改成取捨提醒後,這在語意上本來就沒有對錯,這一條只是記錄:這列現在沒有任何機械判準,全靠盲判席讀懂 D-42 「不適用時」欄的新文字。

引句:「取捨提醒=不掛規則、不擋,型錄那一列寫清楚做法的代價,接電方式照舊是表態對程式與盲判席」

證據:`skills/kotlin-idioms/checks-catalog.md:756`(D-42)與 `configs/ast-grep/kotlin-android/samples/situation/D-42.kt.txt`。
