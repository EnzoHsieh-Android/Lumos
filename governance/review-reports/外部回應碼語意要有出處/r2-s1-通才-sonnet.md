severity: major

審查範圍:「## 設計(三項)」到「## 回退」。每個對程式碼的宣稱都對照 `scripts/lumos` 開檔驗過語意。

## Finding 1:共用形狀常數「編譯好」,題目表卻會再編譯一次
- spec 段落:設計(三項)/共用:「外部碼比對」形狀、第三項
severity: major
- blocking: 是(實作照寫會在載入時直接炸,屬 major)
- 問題:spec 要求形狀是「一組編譯好的正規式常數」,同時要讓題目表的 `when` / `when_raw` 欄引用它。題目表欄位目前放的是字串,載入時才統一用 `re.compile(_p, re.I)` 編譯。把已編譯的 Pattern 放進去,載入時會丟 `ValueError: cannot process flags argument with a compiled pattern`(已在 Python 實測),整支 lumos 啟動即錯。另外 `triggered_by` 記的是 `pat.pattern` 字串。
- 還有一個銜接缺口:鏡頭端要拿 Pattern 直接比,表端要字串。spec 沒有寫「單一來源是字串清單,兩邊各自編譯」。S4 的「同一組形狀常數」因此沒有明確的型別。
- 引句:「形狀定義成一組編譯好的正規式常數,放在題目表旁;第二項的鏡頭補選與第三項的八題觸發都只引用這組常數,不各寫一份。」
- 佐證:file: `scripts/lumos:23551`(`_STACK_TRIGGERS` 對 `_s["when"]` 一律 `re.compile(_p, re.I)`)

## Finding 2:「因時間中止就不寫快取」會讓背景暖機的等待路徑永遠超時
- spec 段落:第二項(時間);實務隱患/併發
severity: major
- blocking: 是
- 問題:hook 帶 `--deadline` 時,`_dispatch_lens_graph` 不直接算,而是派脫離的背景行程去算,自己只等快取檔出現。背景行程跑的是同一支函式。
  - 補選因時間中止,結果不寫快取,等待端到時只會印「還在算」,鏡頭整段(固定席也包含在內)都拿不到。
  - 下一席派工會再次派背景行程、再次因同樣原因中止、再次不寫。最慢的範圍(spec 自己引用的實測是 137 秒)等於永久失效。
  - 現況是慢範圍至少算完一次就有快取。spec 的做法讓「補選」這個附加功能把既有功能變成永遠不可用。
- spec 的「併發:已排除」只考慮了寫入競態,沒考慮「不寫就永遠重算」。
- 引句:「因時間停止時印一行「外部碼表補選因時間上限中止」,而且這次結果不寫進快取。」
- 佐證:file: `scripts/lumos:40350`、`scripts/lumos:40091`(等待端只認快取出現)、`scripts/lumos:40370`(寫快取的位置)
- 建議:截斷版本照寫快取,但在快取鍵或內容標明「已截斷」。或者截斷版本只寫短 TTL,這部分 spec 要自己定。

## Finding 3:固定席為 0 篇時整段沒有注入框,補選段接在後面等於把筆記自由文字印在框外
- spec 段落:第二項(備援段);第一項
severity: major
- blocking: 是
- 問題:`_dispatch_lens_graph` 只在 `listed` 非空時才執行 `_frame_injected`。固定席為 0 時,備援段直接輸出,沒有框。spec 說「補選段接在備援段之後」,而且這種情況正是補選最有價值的場景。那麼印出的是 base 筆記的自由文字(每行最多 300 字、每篇最多 10 行、最多 3 篇),在「不是指令」的框之外。
- 第一項同樣沒說這個情形。「都在注入框內」的宣稱在 0 篇時不成立。
- 引句:「固定席為 0 篇時,code 層備援段照現行規則照印(判斷只看固定席,不看補選);補選段接在備援段之後。」
- 佐證:file: `scripts/lumos:40351`-`scripts/lumos:40369`(框只包在 `if listed:` 內)
- 另外 `_frame_injected` 會刪掉含「─────」的行,這個處理還在,但前提是進得了框。

## Finding 4:「只從 base 版讀」對設計審鏡頭不成立,而設計審是第一項刻意共用的另一半
- spec 段落:第一項最後一條(註解改寫);「diff 與設計審兩種鏡頭都印」
severity: major
- blocking: 是
- 問題:spec 要把消毒原則註解改成「都只從 base 版讀」。設計審鏡頭(`cmd_dispatch_lens_spec`)用的是 `_read_wt`,讀工作樹,而且 spec 本身就在被審的分支上。
  - 分支作者可以在自己改過的筆記裡寫一行 `FACT: … [來源:外部]`,這行會原樣印進審查員的派工詞。這等於把「base 才可信」的防注入原則在設計審這一側整個放掉。
  - spec 的已知限制說「鏡頭只信 base 版,這是既有的防注入原則」,在設計審模式也不成立。
  - 設計審模式沒有改動行,第一項的「含這次改動碼的行排前面」只在 diff 模式有意義,spec 沒有寫設計審模式的排序。
- 引句:「鏡頭程式碼開頭那段「自由文字零輸出」的消毒原則註解改寫成:合約行與帶外部來源標記的事實行兩種例外,都只從 base 版讀、都在注入框內。」
- 佐證:file: `scripts/lumos:40563`-`scripts/lumos:40564`(`_read_wt` 讀工作樹)、`scripts/lumos:39028`(現行消毒原則註解)
- 另外現行合約行也是這樣從工作樹讀。但合約行是固定三個正規式抓的結構化行,事實行是任意自由文字。威脅面不同,spec 要明講取捨,或讓設計審模式不印第一項。

## Finding 5:「抽成共用函式」低估了改動行收集現況,鏡頭端也沒有改動行可用
- spec 段落:共用:「外部碼比對」形狀 / 輸入
severity: major
- blocking: 是
- 問題:現行改動行收集不是獨立函式,而是 `_pitfall_diff_collect` 解析迴圈的一部分,與 claims、行號推進、`vend_skip`(工具自裝檔豁免,依 repo 與範圍算)交錯。
  - 它跑的是 `git diff --no-ext-diff --no-textconv -U3 <原始範圍字串>`。鏡頭端目前完全不跑 git diff:它只拿 `cmd_impact_diff` 的結果,而且範圍只信 `_lens_range_ok` 驗過、解成完整 sha 的 base/head。
  - 抽函式時必須定下三件事,spec 都沒寫:
    1. 鏡頭要用 `base_sha..head_sha`,不能用原始字串(`-` 開頭選項注入已被 `_lens_range_ok` 擋過)。
    2. 要不要 `vend_skip`。鏡頭沒有它,消費專案的工具自裝檔改動會被當 code 比對。
    3. 這支額外 `git diff` 在 45 秒預算裡由誰扣。spec 的時間段只算了讀筆記,沒算 diff 本身(大範圍 diff 可能很慢,而且 `_lens_git` 預設 timeout 20 秒)。
  - S4 要求「同一支改動行收集函式」,但現況沒有可原地抽出的單元,是一個要拆的重構,風險不小。
- 引句:「把 pitfalls --diff 現有的改動行收集(增刪行都算,經 `_stack_changed_ok` 過濾,排除測試檔、非程式副檔名、審計證物、簿記檔、工具自裝檔)抽成一支共用函式」
- 佐證:file: `scripts/lumos:35838`-`scripts/lumos:35851`、`scripts/lumos:35877`-`scripts/lumos:35920`(`_pitfall_diff_collect` 內聯收集)、`scripts/lumos:35692`(`_stack_changed_ok` 的 skip 參數)

## Finding 6:B 組(分支)不要求名稱片段,與「刻意不認」清單和誤觸發防線的說法不一致
- spec 段落:認的四組形狀 B;刻意不認;實務隱患/守衛面
severity: minor
- blocking: 否(S6 的人判量測會抓,屬可調參數,所以是 minor)
- 問題:守衛面宣稱「A 組要求名稱片段」是誤觸發的防線,但 B 組刻意不要求。`case "2026"`、`case "10001"`、Kotlin `"500" ->` 這類尺寸、年份、郵遞區號分支會命中。「刻意不認」只列了比較式的 `year == "2026"`,沒列分支式,兩者同一類語意卻處理不同。
- 引句:「這組不要求名稱片段,因為分支行本身看不到被比較的變數。」
- 建議:S1 補一條 `case "2026"` 的不命中或命中預期,或給 B 組一個替代防線,例如要求 3-4 位且相鄰行有名稱片段。

## Finding 7:C 組只認括號與方括號,漏掉集合字面值
- spec 段落:認的四組形狀 C
severity: minor
- blocking: 否
- 問題:Python 和 Kotlin 最常見的寫法是 `code in {"0000", "2000"}`,Dart、Swift 的 `const {…}`、`setOf(...)` 也一樣。只認 `(`、`[` 會漏掉最典型的寫法。這是覆蓋面問題,不是正確性問題。
- 引句:「in 後接括號或方括號、第一個元素是引號 3 到 6 位數字」

## Finding 8:「含這次改動行裡出現的那些數字碼」沒定義數字碼從哪一組形狀抽
- spec 段落:第一項(每篇最多印 10 行)
severity: minor
- blocking: 否
- 問題:排序要的是「改動行裡出現的數字碼」,但 spec 沒說抽取規則。
  - 是只抽命中形狀那幾行裡的引號數字,還是抽整個改動的所有 3 到 6 位數字?後者會把行號、版本號、金額都當碼。
  - 刪除行的碼算不算,也沒寫。
  - 沒有抽取規則就沒辦法寫出 S2 的測試。
- 引句:「先印含有這次改動行裡出現的那些數字碼的行,其餘照檔案順序補滿」

## Finding 9:自由席的描述與 impact 現況不完全一致
- spec 段落:第二項(第一條)
severity: minor
- blocking: 否
- 問題:spec 寫「impact 現行截到前 8 名」。實際是 `min(top, 10)` 名額(`top` 預設 8),另外加上「直連保底席」(rescued,最多補到 3 個直接相依),所以回傳數可能多於 8。自由席還要先過 `max(min_score, 0.65×最高分)` 的動態閾值,同閾值下一篇不含查詢字面相似度的碼表筆記很難進榜。spec 的已知限制有承認「沒進自由席就選不到」。但「第二項補選」的價值要靠這個前提成立,沒有給出預期命中率。這點與第三項「靠作者把碼表寫進家」互補,但 spec 沒有把「補選預期有多少機會真的選到」記進來。
- 引句:「鏡頭從 impact --diff 結果的自由席(impact 現行截到前 8 名)挑出 base 版裡掃描函式找得到外部事實行的筆記」
- 佐證:file: `scripts/lumos:38612`-`scripts/lumos:38630`

## 已讀,無 finding
- 第三項(旗標①②、不設 `needs_backing`):`_STACK_PERF_QUESTIONS` 確實由所有 spec 的 `q` 派生,所以需要旗標才能排除。排除方向對。此外 impact hook 路徑(`scripts/lumos:38685`)用 `_stack_applicability` 的結果,extcode 命中時會在編輯時也被問到。spec 沒提這個副作用,但屬於「新題上線的一般行為」,不構成缺陷。
- 同步點、回退節:`_LENS_SCHEMA` 升版與釘版本斷言(`scripts/test_lumos.py:36450`)、題數斷言等,與程式碼現況相符。回退後表態寫入檢查會擋未知題目 id(`scripts/lumos:42491`),與 spec 描述相符。
- `_stack_norm_line(keep_strings=True)`、`_stack_applicability` 的「`when` 剝字串、`when_raw` 保留字串」都與 spec 描述相符。

## 固定席(LUMOS-SPEC)判斷
- Systems/棧別提問表態閘:參考資料顯示 0 條合約、沒寫負責範圍,沒有可對照的合約行。本案新增八題與旗標不破壞既有題目 id 集合的「穩定代號」語意,因為只新增 id,沒有改既有 id。
- Systems/pitfalls-code-loop:我沒有逐條核對它的內容,這一席判不準 ⚠。就本審查看,本案不改 pitfalls 的 tier 判定(extcode 不產生 claims),所以不影響風險分級。

最嚴重等級:major;blocking 條數:5(Finding 1、2、3、4、5)。