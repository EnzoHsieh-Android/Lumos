severity: major

我已逐節讀完整份 spec,並把 `scripts/lumos` 當模組載入做了實驗(暫存在 `/tmp/lumos-seat-work/紅燈版實跑三缺口/邊界-sonnet/`,沒有改 repo,`git status` 只剩原本就有的帳檔改動)。

## 各節結論

- 名詞、問題與最小解:已讀,無 finding。對照程式確認:
  - `_tg_strip` 與原文等長。
  - Room 守衛傳進來的是已剝字串的文字(`scripts/lumos:47944`)。
  - `_spec_gate_low_not_red` 的舊留痕不重寫條件屬實。
  - 孤兒紅燈版的 ident 預設用整句提醒(`scripts/lumos:49655-49658`)。
- 做法 1:finding 1、2、4。
- 做法 2:finding 3(多平台預設平台)、finding 5(裝置離線)、finding 9(效能)。
- 做法 3:finding 6、7。
- 做法 4:finding 8。
- 驗收條款與回退:finding 7、8。
- 實務隱患:finding 6、7、8。其中「金流、對外送出」的排除理由成立;「不可逆」的排除理由見 finding 8。

## Finding

### 1. 多平台專案的預設平台測試仍寫裸名,名字含冒號會讓推送前整個崩掉
- 位置:做法 2、S2。
引句:「預設平台照舊寫名字(舊讀者不受影響)」
- 問題:
  - 規格閘寫留痕時,預設平台的測試仍寫裸名。
  - 推送前每個裸名都會重新過 `_split_test_ref_ex`。多平台專案裡,名字含冒號就會被當成平台前綴。
  - Kotlin 反引號測試名很常帶冒號。例如預設平台 android 的測試 `` `fee: rounds up` ``,條款寫 `[test:android:fee: rounds up]` 能綁定,但留痕寫成 `fee: rounds up`。
  - 推送前讀回來,`_TestRefPrefixError` 沒有任何 try 包住,推送被擋。重跑規格閘又寫回同樣的裸名,使用者無解。
  - 名字長得像「已定義平台名加冒號」時更糟,會靜默跑到錯的平台。例如預設平台的測試叫 `device: shows total`,會被改派到 device。
- 佐證:
  - file: `scripts/lumos:6455-6477`。實跑結果:
    - `fee: rounds up` 丟 `_TestRefPrefixError`。
    - `device: shows total` 回 `('device', 'shows total', True)`。
    - `android:fee: rounds up` 正確回 `('android', 'fee: rounds up', True)`。
  - file: `scripts/lumos:15939-15940`。`_spec_gate_push_one` 的 `resolve_test_refs(f"[test:{t}]",...)` 沒有 try,`_spec_gate_push_scan`、`_spec_gate_push_check` 也沒攔。
  - 「舊讀者不受影響」不能當不全寫前綴的理由。現行推送前讀取就已經認前綴(同一行 `resolve_test_refs`)。多平台專案一律寫 `平台:名字`,只有舊制單平台(`split` 為空)才寫裸名。
  - 做法 2 的補平台那段也要先接住這個例外,spec 沒寫。
severity: major
blocking: 是——功能上線後會多出一條「推送被擋、重跑也解不掉」的路。

### 2. 字串內括號不成對時,漏報原樣保留,spec 沒有回頭條件;「只會少切字串裡的逗號」的說法也不成立
- 位置:做法 1。
引句:「後面真的分隔逗號照舊切不到,跟現況相同。」
- 問題:
  - 這個缺口修的是「字串預期值被改漏報」,而括號不成對的字串在同一類裡仍然漏報。
  - 實跑結果:`assertEquals("1) 項目", label(x))` 改成 `"2) 項目"`、`assertEquals("{", out)` 改成 `"["`。新舊切法都只切出 1 個參數,`_tg_split_expected` 回 None,`_tg_pairs` 回 `[]`,不列。
  - 這類字串在計數、JSON 片段、表情符號的斷言裡很常見。
  - spec 只寫「已知不處理」,沒有 `REVISIT:` 或回頭條件,違反專案鐵則 4。
  - 有便宜的做法:只讓「含 `${` 的字串」的括號進原文深度,其餘字串的括號不算。
  - 另一個反例,推翻「少掉的都是字串裡的逗號」(做法 1 原句:「兩邊都要求時,切點只會比現在少,少掉的都是字串裡的逗號」):
    - Kotlin 合法寫法 `assertEquals("""a"""", x)`。遮罩把收尾第 4 個引號當成未收尾字串,吃掉整行,真正的分隔逗號被遮掉。
    - 新切法只剩 1 個參數,舊切法有切開。
    - 這個例子少見,但說法應改成「遮罩誤判時會多漏」,S1 也要多一支遮罩誤判的測試。
- 佐證:
  - file: `scripts/lumos:47979-47996`。`_rg_split_args` 現況只看原文深度。
  - file: `scripts/lumos:6759-6762`。`_C_STRIP_PAT` 單行 `"` 未收尾會吃到行尾。
severity: major
blocking: 是——spec 要修的「預期值被改漏報」缺口在此留下一條可重現的漏報路徑,又沒有回頭條件。

### 3. 修好之後,平板沒接上時推送閘仍會擋下並自動記假逃逸
- 位置:做法 2、S2、實務隱患(沒有討論)。
引句:「推送前照前綴的平台指令跑那一支」
- 問題:
  - 修好之後,`device:` 的測試在每次推送前都要真的在平板上跑。
  - 平板沒接、模擬器沒開時,測試跑不到或是紅的,在推送前驗收裡都是「非綠」,於是推送被擋。
  - 同時 `_auto_escape(... "major" ...)` 會自動記一筆逃逸。這是環境失敗,不是程式缺陷,跟原缺口 2 造成的「假逃逸污染撤除條件分子」是同一種傷害,只是換了原因。
  - spec 只修平台派錯,沒有分辨環境失敗,也沒有在實務隱患的「資源」節提到對硬體的依賴。
- 佐證:
  - file: `scripts/lumos:15954-15966`。`v != "green"` 一律進 `reds`,接著 `_auto_escape`。
  - file: `scripts/lumos:14878-14879`。跑不到(`n == 0` 或 `unproven`)判成 weak,仍屬非綠。
  - file: `scripts/hooks/pre-push`。推送前驗收只在 pre-push 呼叫,每次推送都會經過這條路。
severity: major
blocking: 是——必須決定「裝置不可用」是擋、是略過、或不記逃逸,否則會重演缺口 2 的症狀。

### 4. 做法 1 沒說鏈上參數那處要不要遮罩,S1 也沒測
- 位置:做法 1、S1。
引句:「`_tg_call_parts` 已經用剝字串後的文字」
- 問題:
  - `_tg_call_parts` 有兩處切參數:呼叫本身(`scripts/lumos:48976`)和鏈上(`scripts/lumos:48983`)。
  - 鏈上那處現況先切後用 `,` 接回,會吞掉逗號後的空白。
  - 實跑結果:`assertThat(x).isEqualTo("a, b")` 改成 `"a,b"`,`_tg_expected_changed` 回 False,漏報。
  - S1 只測 `assertEquals`。
- 佐證:file: `scripts/lumos:48983`,以及 `_tg_split_chain` 的 `",".join(cargs)`(`scripts/lumos:49026`)。
severity: minor
blocking: 否——只影響空白差異的鏈式斷言,補一句「兩處都帶遮罩」加一支鏈式測試即可。

### 5. 忽略查詢:截止時間與失敗語意沒訂,S4 也沒有失敗情形的測試
- 位置:做法 3、實務隱患(效能)。
引句:「忽略查詢(兩到三次 git 呼叫)只在有孤兒、有還沒提交的紅燈版、或規格閘寫出紅燈版時才叫」
- 問題:
  - spec 寫借用 `_lens_git`,逾時固定 20 秒,三次最多 60 秒。
  - 但呼叫它的 `_tg_redbase_cands` 帶著截止時間 `deadline`,同函式族都用 `_lens_git_dl` 守預算。
  - 三次呼叫任一次回 None(逾時)或回傳碼 ≥ 2(例如 128:不在 git repo),spec 沒說結果。
  - 沒說的情形有:判不了算不算被忽略、是否照舊措辭、一次推送最多問一次的快取要不要記失敗。
  - S4 沒有「git 判不了」的測試。
  - 先例 `_local_ledger_doctor_msgs` 的做法是回 None 就略過,spec 沒說照抄。
- 佐證:
  - file: `scripts/lumos:49661-49690`(`deadline` 參數)。
  - file: `scripts/lumos:64496-64502`(`_lens_git_dl`)。
  - file: `scripts/lumos:1770-1776`(`_local_ledger_doctor_msgs` 的略過寫法)。
severity: minor
blocking: 否——可在實作時補,但要寫進做法與 S4。

### 6. 解析 `check-ignore -v` 輸出有兩個問題:格式與清洗
- 位置:做法 3、S5。
引句:「被忽略才用 `git check-ignore -v` 取出蓋到的規則來源與行號」
- 問題:
  - `-v` 的輸出是 `來源:行號:規則<TAB>路徑`,來源路徑含冒號就沒法用冒號切欄位。實跑:全域忽略檔放在 `a:b/ign` 時,輸出是 `".../a:b/ign":1:...`。
  - `-z` 只能配 `--stdin` 用,沒有現成的 NUL 分隔輸出。
  - 路徑含非 ASCII 字(例如家目錄是中文)時,git 預設會加引號並把字轉成八進位跳脫。要像 `_lens_git(..., quote=True)` 關掉 `core.quotePath`。spec 都沒提。
  - 規則文字、來源路徑是外來字串,S5 直接 `print` 一行。專案慣例是外來字串先過 `_out_clean`,`_tg_cand` 的 extra 會清,但 S5 的獨立印出沒有明說。
- 佐證:
  - 實跑兩條指令的輸出差異(同上)。
  - file: `scripts/lumos:49336-49340`(`_tg_cand` 內的 `_out_clean`)。
  - file: `scripts/lumos:64953-64960`(`quote` 參數)。
severity: minor
blocking: 否——實作層級的坑,補上解析規則與清洗即可。

### 7. 做法 4 與 S6 的撤回指令缺必要參數
- 位置:做法 4、S6。
引句:「修完重跑考場時用 `lumos loop escape --withdraw` 撤回並附理由」
- 問題:
  - 指令需要 `--withdraw <token>`、`--reason`、`--withdrawn-by <誰>`,缺 `--withdrawn-by` 直接回 2。
  - 兩筆假逃逸要先用 `--list` 查出 token。
  - spec 沒寫這些,人工驗收照著做會卡住。
- 佐證:file: `scripts/lumos:19886-19898`(`--withdrawn-by` 缺就擋;reason 要夠長)。
severity: minor
blocking: 否——補一行完整指令即可。

### 8. 「換身分字不影響放行」與「回退就回來」互相矛盾
- 位置:做法 3、回退、實務隱患(不可逆)。
引句:「所以換身分字不會讓既有放行失效」
- 問題:
  - 治理帳被忽略的專案裡,每份紅燈版推送時都是孤兒,必然被擋,使用者必然去放行。
  - 新身分字 `孤兒`、`還沒提交` 一上線,這些放行就記在新指紋上。
  - 回退節寫「兩句提醒的措辭與身分字改回原樣」,回退後這批放行全部失效。這跟實務隱患的「改壞了回退就回來」衝突。
  - 另外,「沒有專案存過這兩句的放行」是部署事實。我只能確認:紅燈版功能提交 `08b4ce74f` 在本 repo 只出現在 `spec-snapshot-guard` 分支(`git branch -a --contains 08b4ce74f`),沒有上主線。考場分支的本機放行紀錄從程式碼無法證實。
  - 需要一句回頭條件,或在回退節註明回退身分字會讓期間的放行失效。
- 佐證:
  - file: `scripts/lumos:49340`(指紋由 rule、file、ident 組成)。
  - file: `scripts/lumos:49655-49658`(`ident or reason`)。
severity: minor
blocking: 否——是文字與回退節的一致性問題,不影響主功能。

### 9. 舊留痕補平台那一步要重新綁定一次條款,效能節沒算 ⚠
- 位置:做法 2。
引句:「留痕沒過期(條款指紋相符,現在的條款就是當時記的那份)才看現在計劃條款裡同名的引用」
- 問題:
  - `_spec_gate_push_stale` 只回 `(原因, 重判結果)`,不回條款資料。
  - 要「看現在計劃條款裡同名的引用」,得再呼叫一次 `_clause_bindings_for`,它會建測試索引(`discover_test_methods`)。
  - 每份有裸名的留痕各重做一次,跟推送前逐計劃跑的次數成正比。
  - 新寫的留痕預設平台也是裸名,所以每份留痕都會走這條。
  - 實務隱患的效能節沒有提這筆,應回傳 `rows_b` 或快取。
  - 我沒有實測耗時,所以標 ⚠。
- 佐證:file: `scripts/lumos:15550-15563`(`_spec_gate_push_stale` 內已算過 `rows_b` 但沒回傳)。
severity: minor
blocking: 否——是實作層級的優化,影響範圍小。

## 固定席節點
派工尾端沒有附合約或事故固定席,不適用。

## 實務隱患逐類
- 併發:無新風險。忽略查詢是唯讀的 git 呼叫,留痕寫入走既有 `_vault_write_lock`。
- 效能:切參數仍是單趟線性,不用多算;深層巢狀由 `_rg_bracket_map` 迭代處理。忽略查詢見 finding 5,補平台見 finding 9。
- 資源:git 逾時見 finding 5;裝置離線見 finding 3。
- 回滾:見 finding 8。
- 相容:
  - 舊留痕補平台那段方向正確。
  - 「讀留痕 tests 欄的只有推送前驗收」屬實,我 grep 過所有 `"tests"` 的讀取點(`spec-gate-green` 事件讀的是自己事件的 `items`,不是留痕)。
  - 新舊 `tests` 欄在裸名、帶前綴兩邊都解析得過。唯一的洞是 finding 1。

最嚴重 severity: major,blocking 共 3 條(finding 1、2、3)。
