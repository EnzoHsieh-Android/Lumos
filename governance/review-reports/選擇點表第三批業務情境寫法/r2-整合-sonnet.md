severity: minor

我逐節讀完 r2 稿,對照 scripts/lumos、check.py、型錄、兩篇 Systems 筆記、母計劃、第二批計劃、既有測試。這份稿大多數交叉引用都對得上,例如 CHOICE_ANCHORS、`_choice_also` 只限 `方法名` 錨點、err_hit 用 `line..end_line`、`t_choice_samples_batch2` 的 `C-1..C-31` 篩法、about_code 與樣本列舉段都和稿中描述一致。照做後會自己紅的地方(列數、HIT 缺漏、`不收(` 行)稿中已有 S5/S6 擋住。找到的洞全是同步與宣稱面的,沒有 blocker。

## i1 乾節點覆蓋判斷的修改指示講錯層級
severity: minor
blocking: 否。這處是文字指示與程式簽章對不上,實作者會自行讀程式修正,不會產生錯誤行為。
- 稿的位置:範圍 3 第三個子彈。
- 失敗場景:稿說 `_choice_iv_cover` 要「照錨點行到 `end_line` 判」。實際上這支函式吃的是位元組位移 `cover(s, e)`,不是行號;只有 `_choice_err_cover` 吃行範圍。
- 照字面做不出來,只能自行猜成「`arid_cover(anchor, h["e"])`」。
- 稿給的理由(接收者含 `delay(…)` 會讓整段被當乾節點)也不成立:現行判法要求整個命中落在同一個乾節點內,接收者裡有乾節點不會讓整段變乾。
- 驗收條款只有 S2 測 ERROR 那半,乾節點這半沒有任何條款或測試綁定,實作了也無從驗證。
- 佐證:file: `scripts/lumos:77774`(`arid_cover = _choice_iv_cover(scan["arid"])`、呼叫 `arid_cover(h["s"], h["e"])`)與 file: `scripts/test_lumos.py:145518`(用位移測 `cover(s0, e0)`)。
引句:「整個命中落在某個乾節點內才算乾」

## i2 「其餘八組沒有範本」與 test-templates.md 現況不符
severity: minor
blocking: 否。錯的是文字宣稱,不會讓任何機械檢查變紅,但會誤導接手者補範本的判斷。
- 稿的位置:REVISIT 第二條與〈實務隱患〉測試成本。
- 稿說作用域以外的八組都沒有守門測試範本,只有 API-4 有。
- 實際上 skills/kotlin-idioms/test-templates.md 的同一組範本已有三支對得上的測試:
  - `missing_user_returns_null`(FLOW-23):空流用 `first()` 與回 null,正好對應 `firstOrNull` → `first` 那一列。
  - `late_collector_still_gets_welcome`(FLOW-24):對應晚到訂閱者與 `replay`。
  - `latest_query_wins`(API-8):對應 `flatMapLatest`,與 `mapLatest` 同概念。
- 三個月後的人依這句話會替這三組重寫範本,或把這三組「不是需求」放行偏高誤判成「沒範本所致」。
- 佐證:file: `skills/kotlin-idioms/test-templates.md:1697`(該組〈測試〉節,含上述三個函式名)。
引句:「作用域以外的八組現在都沒有範本」

## i3 同步清單漏了母計劃的不收清單與統計括號
severity: minor
blocking: 否。只是文件前後說法打架,沒有機械檢查綁在上面。
- 稿的位置:範圍 1 說明段同步、範圍 6 母計劃那條。
- 母計劃〈範圍〉API 條目裡有一條逐字相同的「不收(…`coroutineScope`/`supervisorScope`…)」。稿只規定母計劃〈天花板〉第 1 條補指向,這條不動。
- S6 只釘型錄那一行,翻案後母計劃仍寫著不收,三個月後 grep `supervisorScope` 的人會看到兩份互相矛盾的說法。
- 型錄〈統計〉現有括號「2026-11-14 第一版 31 列,2026-11-17 第二批加 6 列」。稿只說把列數改成「37 加實際上線列數」,沒要求括號補上第三批加幾列。數字改了,來由留在舊括號裡,下一個重數的人會對不上。
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:67`;file: `skills/kotlin-idioms/checks-catalog.md:1651`。
引句:「〈天花板〉第 1 條補指向這份」
引句:「〈統計〉的選擇點表列數改成 37 加實際上線列數」

## i4 作用域規則採用 kotlin規則包 已記為踩坑的正面 inside 寫法,稿沒引用該筆也沒採其修法
severity: minor
blocking: 否。稿自己要求實作第一步重量,爆量時落成「驗不了」只提醒、不誤擋,後果有界。
- 稿的位置:範圍 2 作用域規則、〈實務隱患〉深層巢狀。
- Systems/kotlin規則包 已有 PITFALL:正面寫 `inside` 會把整段 lambda 當次要標記塞進每個命中,巢狀 300 層 444MB、撞 64MB 上限整檔記驗不了。
- 該筆的修法是改寫成 `not inside not X` 的雙重否定,命中集合不變。同族清單還列了 C-18。
- 稿的作用域規則同樣是正面 `inside` 加 `stopBy`,自己實測 100 層就 34MB、200 層 263MB,但全文沒提這筆 PITFALL,實作者看不到既有修法。
- 我另做了實驗:一個 6 行的 `supervisorScope` 樣本,每個命中的 JSON 就約 2KB,可見次要標記確實帶出了整段本文。
- 稿也沒有要求實作後回頭更新該 PITFALL 的同族清單。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:102`。
引句:「新規則在實作第一步用同一組巢狀輸入重量」

## i5 REVISIT 日期寫死成計劃日期,不是上線日
severity: minor
blocking: 否。只是回頭看的時點可能比資料成熟時早,不影響閘的行為。
- 稿的位置:REVISIT 兩條,對照 RETIRE-IF。
- RETIRE-IF 以「上線日(寫進第三批的 Verification)起滿兩個月」計。REVISIT 卻固定寫 2027-01-21,剛好是 2026-11-21 計劃日加兩個月。
- 計劃仍是 doing,上線日要等範圍 7 實測過門檻之後才定。上線若晚於 11-21,doctor 到期唸的那天兩個月還沒滿,依列號的 5 筆門檻讀不到足夠樣本。
- 第二批的 REVISIT 是上線當天已知日期才寫成 2027-01-17。這份沒有「上線時回頭改這兩條日期」的步驟,範圍 6 的 Verification 只抄數字。
引句:「REVISIT:2027-01-21 第三批上線滿兩個月前後」

## i6 S6 與〈回退〉要求「命中的原寫法名稱」,型錄沒有可供讀取的欄位
severity: minor
blocking: 否。實作者可由候選欄反推,不會失敗,但這是 S6 能否機械實作的缺口。
- 稿的位置:S6、〈回退〉第 1 項。
- 型錄表頭是列號、類別、ast-grep 規則、錨點、候選壞法、型別前提、需補的 import、對應決策表、為什麼行為不同、出處,沒有「原寫法」欄。
- S6 的測試要從表裡推出作用域列的原寫法名稱,才能核對 `不收(` 那一行。〈回退〉單列撤掉時也要靠它決定加回哪個名稱。
- 稿沒說從哪欄取。合理做法是取候選欄的反方向(`supervisorScope` 列候選是 `coroutineScope`),或解析 `ast-grep 規則` 欄的自由文字。兩種結果在欄位寫法微調時會不同。
- 稿應寫明取法,否則 S6 可能對自由文字做脆弱解析。
引句:「以 `不收(` 開頭的那一行 應 不列那一列命中的原寫法名稱」

## i7 作用域兩列的 ERROR 保護只看識別字那一行,漏了與 retry 同理的結構不可信問題
severity: minor
blocking: 否。後果是多出一個放行或漏一個選擇點,屬於可由放行理由承接的雜訊。
- 稿的位置:範圍 3 ERROR 節點與乾節點覆蓋判斷;S2 只為 retry 寫了 ERROR 條款。
- 現行保護是「命中的 line..end_line 與 ERROR 節點有交集就略過」。稿只把 `整個呼叫` 錨點改成錨點行到 end_line。
- 作用域兩列的命中只是 `supervisorScope`/`coroutineScope` 這個識別字,範圍是單一行。「兩個以上子協程」「最近一層 lambda」是靠整段大括號本文的樹結構判斷,而 `_choice_err_cover` 的註解明寫「文法錯誤恢復讓同幾行其他節點的結構不可信」。
- 失敗場景:作用域大括號裡有一行文法不認得(例如中文識別字讓 `> 上限` 變 ERROR)。ERROR 節點離識別字那一行很遠,不會被略過,但 `async` 的歸屬可能被判錯,造成誤判「兩個以上」而挑出壞法。
- S5 樣本沒有「作用域本文含 ERROR 行」這一型。
- 佐證:file: `scripts/lumos:77737`(`_choice_err_cover` docstring)。
引句:「接收者裡任何一行文法不認得都會讓 `.retry` 靜默消失」

## 圖譜節點固定席

- Systems/kotlin規則包:不影響,理由有三。
  - 沒有合約行也沒有 KEY。
  - 稿只動 about_code、補一條 WHY、改兩句列舉(api.yml 命中形狀與逐檔樣本)。這些位置我都查到了。
  - 綁在 WHY 上的 `t_choice_table_missing`、`t_choice_points_interview` 不碰第三批新增的東西。
  - 該節點已記的 PITFALL 與稿的衝突見 i4。
- Systems/規格閘:不影響。
  - 20 行 KEY 全是條款判定、門規則、推送前查簽、小改動閘,稿只動 `_choice_*` 與「依列號」那條 WHY。
  - 判門與條款句式沒動,稿的 WHY 補句位置(約 66 與 80 行)也確實存在。
  - 稿自己的「守衛面:不排除」會讓計劃判風險高走半套門,這是預期行為。

## 實務隱患鏡頭

我逐類核對了稿列的隱患,沒有再補到新類別。

- 編不過與等價存活:稿已逐項列出,我另核對 `_choice_also`、`_choice_api_edits` 的 import 與換名路徑,對得上。
- 同一行重疊:`_choice_pick` 以類別洗牌加錨點排序決定,新列只影響含新語法的行;既有樣本無第三批語法(grep 已確認),S7 可行。
- 資源:見 i4。實測 CI 釘的 ast-grep 0.51.1 與本機 0.51.2,`$A.retry` 規則與 `inside` 加 `stopBy` 規則物件的命中結果相同。
- 併發:無,單人單機依序操作,稿已排除。
- 金流:無,只改型錄、規則與產壞法程式。
- 對外送出:無,掃描與殺傷力都在本機。
- 不可逆:無,治理帳只追加,撤列後處置照 `(檔, 行指紋)` 續用,〈回退〉第 3 項已承認。

總結:最高嚴重度 minor,blocking 共 0 條
