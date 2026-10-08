severity: major

# 筆記測試綁定要存在 設計審 r3:正確性-opus

實驗都在 `tb-r3-work-正確性-opus/repo`(對 negguard 的 `--shared` clone,HEAD 59087292)裡用 `/opt/homebrew/bin/python3` 載入 `scripts/lumos` 直接呼叫函式;另開一個只有一支 pytest 類別測試的小 repo `pyrepo`。沒有跑全套,也沒有改 repo 根。

## F1 1c 用 `_ns_text_key` 判「新寫」沒講要餵哪段文字;照這支函式現有的用法餵核心句,最主要的情境(既有條目這次才標作廢)永遠不擋

severity: major
blocking: 是
引句:「而且這一條用 `_ns_text_key` 正規化後在起點那一版整個知識庫找不到一樣的」
file: `scripts/lumos:28167`
file: `scripts/lumos:28183`
file: `scripts/lumos:28208`

1. `_ns_text_key(core)` 的參數名就是 core,唯一的既有呼叫端 `_ns_slot_key` 餵的是 `slot_parse(...)["core"]`,也就是**已經去掉所有欄位**的核心句。計劃 PRIOR-ART 寫「作廢條目比對 `_ns_text_key`」,照格子那邊的用法接,拿到的就是核心句的鍵。
2. 作廢幾乎都是改舊行做的:在既有的 `RULE: … [test:t_x]` 後面加 `[status:superseded] [被取代:[[…]]]`。加的全是欄位,核心句沒變,起點版本就有一樣的鍵,1c 判成「不是新寫」放行。rtb 那 12 條如果補上標記,走的也是這條路。
3. 實測(probe4.py):
   ```
   summary RULE
     core key equal : True '登入要擋重送'
     full key equal : False
   plan clause
     core key equal : True '- [S3]當重送時應擋下'
     full key equal : False
   rewrap full key equal: True
   ```
   用核心句當鍵,摘要條目與條款行兩種都被當成舊的;用含欄位的整條當鍵才會擋,而且只重排折行的照樣算一樣(S12 不受影響)。
4. 條款也抓不到這個錯:S11 的測試只要造一條起點完全沒有的作廢條目就會綠,S12 只測重排折行,沒有一條在測「既有條目這次加上 `[status:superseded]`」。
5. 改法:明寫鍵是「整條含欄位」的文字;或者直接借格子既有的判法,`_ns_is_old` 回的 `old_sup` 本來就在回答「對上的舊行有沒有標作廢」,1c 的條件寫成「現在標了作廢,而且起點對上的那一條沒標(或對不上)」。再補一條條款:起點有 `X [test:活測試]`、這次只加 `[status:superseded] [被取代:…]` → 回 1。

## F2 條款定義行寫成「那個編號第一次出現的行」,跟條款綁定實際的定義(第一次寫在行首的那行)不同;計劃裡先引用後定義的條款會被當成一般行,新計劃一推就擋

severity: major
blocking: 是
引句:「計劃(type: project)裡符合 `_CLAUSE_LEAD_RE`、且是那個編號第一次出現的行(`- [S1]` 也算)」
file: `scripts/lumos:6613`
file: `scripts/lumos:6645`

1. `clause_bindings` 的定義行是「這個編號第一次**在行首**出現的那一行」:前面的「見 [S1]」這種行內引用不算定義,只記成 fallback(`defined[cid] = (no, seg)` 只在 `_CLAUSE_LEAD_RE` 對上時寫)。計劃照字面寫的是「符合 LEAD 而且是那個編號第一次出現的行」,兩個條件要同時成立;只要〈做法〉先提到 [S1],後面〈條款〉的 `- [S1] … [test:…]` 就不是「第一次出現」,不算條款定義行。
2. 結果:那一行的 `[test:]` 改走「新加的測試名要指得到」。計劃都是在實作前推上去的(設計審折入就推),那時測試還沒寫,第②道一定找不到,推送被擋。doctor S20 也會把它們列成指不到。
3. 重現(probe9.py):
   ```
   line 8 LEAD matches S1 | literal 'first occurrence' line = 6 -> treated as clause def: False
   clause_bindings defined line: [('S1', 8)]
   ```
   本 repo 量(probe2.py、probe8.py):有條款帶 `[test:]` 的計劃 52 份、573 條,其中 **17 份、38 條**的定義行之前就有行內引用,例如 `Projects/審查有沒有用記帳_計劃.md` 的 [S1](第 66 行先提到,第 71 行才定義)、`Projects/探針判準對齊程式碼為主_計劃.md` 的 [S5](第 31 行、第 58 行)。
4. 改法:不要另寫判法,直接拿 `clause_bindings(text, …)` 回的 `defined: True` 那幾列的 `line` 當條款定義行(它也已經處理反引號、圍欄、`_strip_inline_markup`、重複定義)。

## F3 「新加的」用名稱扣起點集合,佔位字 `待補` 本 repo 起點就有 4 個,所以新寫的 `[test:待補]` 永遠不算新加,Enzo 裁的「不准」實際不會生效;空的 `[test:]` 也判不出新不新

severity: major
blocking: 是
引句:「新加的是佔位字、或 `[test:]` 方括號裡沒有名稱 → 一律違規,先於判存在」
file: `scripts/lumos:30601`

1. 〈做法〉3 先算「起點整個知識庫的名稱集合」,再把第 1 步的名稱扣掉這個集合;〈做法〉5 的佔位字規則只對「新加的」生效。佔位字是固定幾個字串,只要起點任何一篇寫過一次,之後所有新寫的同一個佔位字都會被扣掉。
2. 實測(probe10.py,照計劃的抽取:摘要用 `_ns_summary_logical`、正文用 `_visible_lines` 加 `slot_parse`,讀 HEAD 的整個知識庫):
   ```
   placeholder in base: Issues/rtb接上漂移檢查後回報的四個小改進.md 13
   placeholder in base: Issues/治理帳多個寫入者都沒上鎖.md 17
   placeholder in base: Issues/舊句檢查超長行判準偏寬與留痕殘行.md 16
   placeholder in base: Issues/舊句檢查超長行判準偏寬與留痕殘行.md 17
   Counter({'待補': 4}) empty [test:] in base: [...] 49
   ```
   這 4 個都是 PITFALL 摘要條目上真的寫著 `[test:待補]`(例:`Issues/治理帳多個寫入者都沒上鎖.md` 第 17 行)。這表示在本 repo 新寫一條 `PITFALL: … [test:待補]` 推上去會被放行,S4、S5 構造不出來。依據段落也說 rtb 有同類的佔位,消費專案一樣。
3. 空方括號沒有名稱可以扣:起點已有 49 個空的 `[test:]`。照字面實作,不是「永遠不算新加」(跟佔位字一樣失效),就是「所在條目有一行新寫就算」——那樣改舊行其他字也會被擋,跟名詞段「改舊行其他字…不算新加」矛盾。r2 邊界席 F5 問過「空方括號用名稱判不出新加」,這輪改成名稱集合以後這個問題還在。
4. S4、S5、S20 的測試多半在乾淨的小 repo 裡造,起點沒有佔位字也沒有空方括號,所以會綠,抓不到這個錯。
5. 改法:佔位字與空方括號不走名稱相減,改用條目層級判新舊(起點有沒有同一條,鍵照 F1 的含欄位整條或 `_ns_is_old`)。再補一條條款:起點已有別篇寫 `[test:待補]` 時,新寫的 `[test:待補]` 照擋。

## F4 單行寫法的 summary 那一行在 `_notelines_new` 裡算開頭欄位的「其他」區,照預設呼叫拿不到;計劃沒寫要帶 `keep_other`

severity: minor
blocking: 否
引句:「這組不靠格子的 `--slots` 容器,自己向 `_notelines_new` 要 rows」
file: `scripts/lumos:27429`
file: `scripts/lumos:28407`

1. 實測 `_notelines_regions`(probe5.py):`summary: "WHY: 單行 [test:t_one]"` 這一行的區塊是 `other`;區塊寫法的條目行才是 `summary`。
2. `_notelines_rows` 在 `keep_other=False`(預設)時直接丟掉 `other` 區的行。`_note_shape_eval` 之所以拿得到,是因為它呼叫時帶了 `keep_other=True`。計劃只說「自己向 `_notelines_new` 要 rows」,沒講帶什麼參數;照預設呼叫,單行 summary 永遠沒有新寫行,S21 的單行情境不會擋。S21 有測試,實作時會翻紅,所以列 minor。
3. 改法:明寫要帶 `keep_other=True`,再只留 `summary:` 那一行(其他開頭欄位不收)。另外,這樣等於推送時把逐提交的 diff 再跑一次;既然 eval 本來就算過,也可以讓 eval 一律把 notes 交出來(現在只有格子容器存在時才交)。

## F5 「類別.方法」補法只救得了 C#/JVM;Python profile 的方法集合錨在行首,pytest 類別裡的真測試補完照樣判指不到,實務隱患卻把「類別裡的方法」這一項刪掉了

severity: minor
blocking: 否
引句:「索引沒認出的寫法(參數化名稱)會被判指不到,`warn` 可退」
file: `scripts/lumos:4820`
file: `scripts/lumos:40263`
file: `scripts/lumos:41252`

1. r2 正確性席 F2 第 3 點指出 Python 類別方法會被誤擋。這輪的補法是第①道照 `_classify_test_refs` 的規則,取最後一段去比方法集合。可是 Python 的方法集合來自 `PYTHON_TEST_RE = (?m)^def …`,只收寫在行首的函式,類別裡縮排的 `def test_cap` 根本不在集合裡。
2. 實測(pyrepo:`class TestRetry(unittest.TestCase): def test_cap`,加一支頂層 `def test_top`):
   ```
   methods: ['test_top']
   test:TestRetry.test_cap -> (False, "測試 'TestRetry.test_cap' 在平台 'python' 的工作樹掃不到…")
   patched ① (classify rule): False
   classify: [('n', 'python', 'TestRetry.test_cap', 'dangling')]
   ```
3. 本 repo 自己用的就是 python profile。新寫 `[test:TestX.test_y]` 指向真的類別測試,推送時會被擋。這是 profile 本來的限制(Check T 也一樣),所以列 minor;但 r2 那條的處置不算做完,而且實務隱患把它從清單拿掉了,會讓人以為修好了。
4. 改法:實務隱患把「Python 類別裡的方法」寫回去,S23 註明只涵蓋不錨行首的 profile;或者 Python 的第①道改用 `loose_for`(不限縮排的宣告掃描)。

## F6 起點集合只讀範圍起點,合進來的主線新增的名稱不在集合裡;推送者碰到那一條、或合併時解衝突,主線的名稱就算到他頭上

severity: minor
blocking: 否
引句:「起點:提交時是 HEAD,推送時是 note-shape 算出的範圍起點」
file: `scripts/lumos:27268`
file: `scripts/lumos:38535`

1. 遠端已經有的分支,起點是舊的遠端頂端 `a`(`_lens_push_base` 直接回 `a`)。之後合進來的主線提交,`_notelines_new` 會排除,所以那些行不算新寫;但它們新增的名稱也不在「起點那一版」的集合裡。
2. 情境:主線新增 `WHY: … [test:t_m]`,分支合進主線後改了這一條的別的字(或合併時解衝突改到這行)。整條算新寫,`t_m` 不在起點集合裡,於是算成新加;如果 `t_m` 在終點指不到(主線是在上線前或用 --no-verify 寫進來的,或者測試後來在主線被刪),就擋分支推送者。名詞段說「改舊行其他字不算新加」,這裡卻不成立。
3. `_lens_push_base` 的說明已經登記同一類問題(Issues/推送前其他閘的範圍在合過主線時會多算)。改法:起點集合再併上被排除的主線提交的終點筆記,或改用 `_push_range_start`;至少把這個情境寫進〈實務隱患〉的誤擋。

## F7 `_dispositions_check_test` 其實有第三種結果(驗不了),計劃只分「指得到/指不到」;照字面接,git 出錯會擋推送,逾時會讓整道檢查丟例外

severity: minor
blocking: 否
引句:「兩道都過才算指得到;任一道不過算指不到」
file: `scripts/lumos:41275`
file: `scripts/lumos:41209`

1. 第②道遇到 git grep 回傳碼不是 0 也不是 1 時,回的是 `(False, "無法對推送版本的樹驗證…")`;單次 git 超過 `LUMOS_DISP_GIT_TIMEOUT`(預設 8 秒)會往上拋 `TimeoutExpired`。表態閘那邊靠「每題外面包例外處理」把它判成擋。
2. 計劃照「任一道不過算指不到」接:git 出錯 → 新加的名稱算指不到 → 推送被擋,跟 S14「索引建不起來就跳過」的 fail-open 方向相反;`[test-gone:]` 那邊則反過來,驗不了被當成「現在指不到」→ 放行。逾時的例外如果沒人接,整支 note-shape 會丟 traceback 結束,回傳碼非 0,掛鉤擋下。
3. 改法:明寫第三種結果(git 失敗或逾時)跟 S14 一樣「這個名稱跳過、印一行原因」,而且這組的判定整段包在例外處理裡(照 `_ns_slots_collected` 的做法)。

## F8 1c 的改法「拿掉」套在計劃條款定義行上,那條條款就變成「沒標」,`spec-trace` 會回 1、規格閘判不過

severity: minor
blocking: 否
引句:「改法是把綁定移到接手的那一條(`[被取代:]` 指的那裡),或拿掉」
file: `scripts/lumos:6591`
file: `scripts/lumos:7489`

1. S24 讓 1c 也查條款定義行。照擋下訊息把 `[test:]` 從作廢的條款行拿掉以後,`clause_bindings` 判那條是 `untagged`。`clause_bindings` 不認 `[status:superseded]`,`_clause_check` 碰到 untagged 會 fail(「每條要嘛綁 [test:],要嘛寫 [manual:]」),`spec-trace` 也會回 1。
2. 改法:擋下訊息對條款行另給一句,例如改寫 `[manual:已撤除,見 …]`;或者讓 `clause_bindings` 把標了作廢的條款排出分母。至少在〈實務隱患〉講清楚這兩道會互相打架。

## F9 decisions 區裡的 `[test:]` 不在「一條」的定義裡,新寫的不驗,doctor S20 也不列,〈不做〉卻沒寫

severity: minor
blocking: 否
引句:「摘要裡一個前綴條目接回續行後的整條(單行寫法的 summary 整個值算一條);正文裡一個實體行」
file: `scripts/lumos:27152`

1. `_notelines_new` 會交出 decisions 區的新寫行(區塊值是 `decisions`),但計劃的抽取只處理摘要條目與正文行。本 repo 量(probe6.py):decisions 區有 14 行帶 `[test:`。
2. 照字面實作,這些行上新寫的壞名字既不擋也不列,而〈範圍〉的「不做」沒有這一項,讀者會以為全覆蓋。改法:二選一,把 decisions 欄位納進「一條」,或寫進〈不做〉。

## r2 改法驗收(照派工詞逐項)

- **`_notelines_new` 不帶 `--slots` 拿不拿得到新寫行**:拿得到。rows 是它自己的回傳值,跟格子容器無關,`per_commit`、上線點、排除主線、合併只算自己多寫的,都跟 eval 同一條路。缺的是 `keep_other`(F4),以及推送時多跑一次逐提交的 diff。
- **摘要條目「一行新寫就整條算」**:對新加的名稱沒有副作用,整條裡的舊名稱本來就會被起點集合扣掉。但這條讓「碰到主線那一條」的機會變大(F6)。對 1c,整條算新寫以後是靠文字鍵把只重排折行的排掉;鍵餵哪段文字是 F1。佔位字與空方括號不能靠名稱相減(F3)。
- **`_drift_tree_env` 的範圍與時間**:只讀 `vault_rel` 底下的 `.md`;`where=None`(首推從空樹算、或還沒有 HEAD 的第一個提交)時 `_nodehome_list` 回空,起點集合是空的、名稱全算新加,這是對的。`deadline` 不給時批次讀預設 60 秒;時間上限只管批次讀,不管列檔與 `Env.from_texts`。本 repo 實測:630 篇讀取 0.28 秒,照計劃抽完 892 個名稱 0.37 秒,在可接受範圍。計劃沒寫上限是幾秒(minor,不另列)。
- **`_dispositions_check_test` 第②道**:對終點用 `at_sha=tip`;平台根是子資料夾時,glob 是 `<根>/**/*<副檔名>`,跟第①道掃的根一致;根在 repo 外時只做第①道。多平台預設平台由 `load_platforms` 決定:平台超過一個又沒寫 `default_platform` 會拋 ValueError,剛好落在「索引建不起來」那條路,沒問題。類別.方法補完以後,C#/JVM 兩道一致(第①道取最後一段比集合、第②道用方法名 grep);Python 例外(F5)。另外,舊式單平台設定下名稱帶冒號時,`_dispositions_split_test` 回的原因是「沒開多平台」,跟名詞段「整串當名稱」說法不同,但兩邊都判指不到,行為一樣(不另列)。
- **`slot_parse` 實際輸出**(probe1.py):正文行照樣解析,`- [S1]` 留在核心句;整段放在成對反引號裡的 `[test:…]` 不算欄位;值本身用反引號包時會保留反引號(``[test:`t_bt`]`` → `` `t_bt` ``,跟 Check T 的 `TEST_REF_RE` 一樣,行為一致);`[TEST：a，b, c]` → `test` 欄的值是 `a，b, c`;`[test:]` → 空值;`[test:t_b` 沒收尾 → 照樣抽到 `t_b`,另帶錯誤;`[test-gone:t_old@abc1234]` 目前不在 `_SLOT_CANON`,整串留在核心句,要等〈做法〉9 登記成鍵才抽得到(`_SLOT_KEY_RE` 鍵名上限 12 字,`test-gone` 9 字,放得下)。
- **推送時「測試檔有差異就只提醒」的範圍**:防的是「第①道讀工作目錄、第②道讀終點」兩邊不一致造成的誤擋,條件用「終點對工作目錄的已追蹤檔有沒有差異」是對的。沒追蹤的新測試檔不算差異,會被第②道判指不到,這正是計劃的本意。計劃沒寫差異要不要限在平台根底下;照字面掃整個 repo 只會更常降成提醒,不會擋錯,所以不列。

## 逐節

- 開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,交叉引用的節點都在(`Projects/漂移防治路線圖_計劃`、`Projects/筆記格子寫法與過期檢查_計劃`、`Systems/筆記內容閘`、`Systems/check-t-sentinel`、`Systems/bound-tests-gate`、`Systems/lumos-cli-read`)。PRIOR-ART 裡「作廢條目比對 `_ns_text_key`」見 F1,其餘無 finding。
- 名詞:F2、F3、F9。
- 範圍:已讀,無 finding(decisions 沒列進〈不做〉併在 F9)。
- 做法 1–4:F1、F3、F4、F6、F7。
- 做法 5:F1、F3、F8。
- 做法 6–9:已讀,無 finding(帳本 `extra` 的合併方式照 `_ns_slot_extra` 的形狀做得出來;推送時跳過在讀範圍前就返回,這點屬實)。
- 做法 10–11:S20 的抽取跟 F2 同一個條款定義行判法,改法一樣;其餘無 finding。
- 條款:S4、S5、S11、S20 測不到 F1、F3 的情境,改法裡已寫要補的條款。
- 回退:已讀,無 finding。
- 實務隱患:F5(漏寫一項)、F6(漏寫一項)、F8。

## 實務隱患鏡頭

- 誤擋:F2(新計劃先引用後定義的條款)、F5、F6、F7(git 出錯被當成指不到)。
- 漏擋:F1(標作廢不擋)、F3(佔位字與空方括號不擋)、F9。
- 錯誤處理與 fail-open:F7。
- 效能:實測起點讀取加抽取在 1 秒內;推送時多跑一次 `_notelines_new` 的逐提交 diff 沒量,寫在 F4。
- 金流、對外送出、不可逆:無。這組只讀筆記和測試檔、只擋推送,計劃的排除理由成立。
- 跟其他閘的接點:F8(規格閘、spec-trace)。

最高等級:major,blocking 共 3 條
