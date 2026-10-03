severity: major

先說結論:這份設計能做,但「純加法、快取不變、只動幾處」的說法不成立。快取版本、既有測試、三處文件的同步點,計劃都沒列。

**Codex 武裝與領取通道:不受影響**
- 武裝(`cmd_dispatch_lens_arm`)也是呼叫 `cmd_dispatch_lens`,拿同一支圖譜文字存進 `meta.json`,領取時整段吐出。
- Claude 掛鉤走同一支 `_dispatch_lens_graph`。兩邊都拿得到新段落,不需要另外接線。
- 唯一副作用:武裝當下算出的文字會被固定十分鐘。如果裡面有「時間上限中止」那行,十分鐘內每一席都收到(見 #1)。

**固定席合約:不破壞**
- design-loop 那條 INVARIANT 管的是處置閘第五步(條款綁測試)。這份計劃的 S1 到 S5 都有綁 `[test:]`,不受影響。
- pitfalls-code-loop 掛 0 條合約,不受影響。

---

**#1 快取:格式一改,舊快取照吐舊格式,而且「快取鍵不變」不成立**
- 計劃段落:實務隱患/併發
- 引句:「快取鍵不變(輸出內容依 base 與 head 決定)」
- 問題 A:快取鍵含 `_LENS_SCHEMA`,現在是 2。快取的 TTL 是 1200 秒。輸出多了新段落卻不 bump 版本,二十分鐘內同範圍的派工會拿到舊格式。
- 問題 B:現有測試把版本釘死為 2,bump 時要一起改。計劃沒列這件事。
- 問題 C:輸出若含「外部碼表補選因時間上限中止」,就依賴當時機器速度,不再只由 base 與 head 決定。這行會被寫進快取,之後每席都收到,機器已經變快也一樣。
- 佐證:
  - file: `scripts/lumos:39322`
  - file: `scripts/lumos:39400`
  - file: `scripts/lumos:39326`
  - file: `scripts/test_lumos.py:36450`
severity: major
- blocking: 是。輸出格式變了卻有舊快取吐舊格式,而且釘版本的測試會紅。

**#2 第三項會讓一批既有測試翻紅,計劃只列了一支**
- 計劃段落:第三項/條款 S5
- 引句:「題目表除 sql 外的八個棧應各多一題 `<棧>-extcode`」
- 問題:既有測試把每棧題數寫死。
  - `kt` 七問、`cs` 五問、`vue` 五問、`sql` 四問。
  - `py` 五題、`dart` 六題、`java` 七題。
  - `stack_questions_meta["kt"]` 長度等於 7。
  - id 集合釘死(只有 `t_stack_question_triggers` 在 S5 列了)。
- 計劃只寫了 S5 一支測試。這些被動到的測試要全列進去,否則推送閘會紅,下一個人只看到一堆莫名紅燈。
- 佐證:
  - file: `scripts/test_lumos.py:23256`
  - file: `scripts/test_lumos.py:23306`
  - file: `scripts/test_lumos.py:23478`
  - file: `scripts/test_lumos.py:23536`
  - file: `scripts/test_lumos.py:41319`
  - file: `scripts/test_lumos.py:41234`
severity: major
- blocking: 是。守衛測試會翻紅,而且計劃漏列。

**#3 誤觸發成本被低估:題目會在沒有外部碼的情況下出現**
- 計劃段落:實務隱患/守衛面
- 引句:「第三項加題會讓更多改動要作者表態,誤觸發會增加摩擦」
- 問題 A:某棧增刪行超過 300(`ask_all_over_lines`)時,該棧全表適用。大改動就算沒有一個外部碼,八個棧的 extcode 都會要求表態。
- 問題 B:`pitfalls` 的 manifest 和 `stack_questions` 是「命中棧整組」附上。extcode 會在每次改該棧檔案時無條件進清單,觸發形狀擋不住這一條。
- 問題 C:`impact-hook` 動手前注入的是原始內容命中的題,同樣會多出這題。
- 計劃只用「形狀排除無引號數字」來擋,沒處理這兩條路。
- 佐證:
  - file: `scripts/lumos:23897`(`over` 時 `hits=["行數>門檻"]`)
  - file: `scripts/lumos:23552`(`_STACK_PERF_QUESTIONS` 整組派生)
severity: major
- blocking: 是。「只在命中形狀時才問」這個賣點在兩條路徑上不成立,會變成固定噪音。

**#4 同步點漏列,而且 `lands_in` 管轄不對**
- 計劃段落:front matter 的 `lands_in`
- 引句:「Systems/pitfalls-code-loop」
- 問題:題目表和鏡頭格式還寫在以下地方,計劃全沒列:
  - `Systems/棧別提問表態閘`:有「全表 id 集合 37→44 題」的敘述。它是 `scripts/lumos` 題目表的家。
  - `Systems/效能檢核目錄`:有「全表 kt=7/cs=5/…/dart=6」的數字串,註明「★這串數字每次加棧都要跟著改★」。另外還有「題目 id 對照」表。這份目錄是效能題的內容源,extcode 是正確性題,放進去語意也對不上。
  - `skills/lumos-code-loop/SKILL.md:29`、`skills/lumos-design-loop/templates.md:99`:都描述鏡頭貼什麼(合約行加綁定測試徽章),新增的外部事實行與「外部碼表」種類沒寫。
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md:28`:寫「內容從 base 讀、零自由文字」,第一項之後就不真了。
- `lands_in` 只列 `pitfalls-code-loop` 和 `design-loop`。真正管題目表的是 `棧別提問表態閘`,這篇沒進 `lands_in`。
- 這兩篇都被「改到的檔必須先有家」的規則管。
- 計劃也沒寫任何漂移守衛來盯「數字串」。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:42`
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:198`
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:204`
  - file: `skills/lumos-code-loop/SKILL.md:29`
  - file: `skills/lumos-design-loop/templates.md:99`
  - file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:28`
severity: major
- blocking: 是。三個月後有人讀手冊或對照表,拿到的是舊數字和舊說法。

**#5 第二項補選的筆記會被擠到「只列名」**
- 計劃段落:第二項
- 引句:「鏡頭從 impact --diff 結果裡「沒被固定」的候選(自由席;impact 現行已截到前 8 名)挑出」
- 問題 A:補選進清單的筆記加在固定席之後。渲染只有前 `cap=8` 篇才展開內容,其餘寫「超出上限,只列名」。固定席滿 8 篇時,補選的碼表筆記只有名字,根本印不出外部事實行,補選形同白做。
- 問題 B:固定席為 0 時,備援段先算完才進清單。補選後 `listed` 變成非空,但備援段已經印了「圖譜沒有釘到節點」那段,兩段並存,語意打架。
- 佐證:
  - file: `scripts/lumos:40010`(`_lens_render_listed` 的 `if i < cap`)
  - file: `scripts/lumos:40348`(`if not listed` 才算備援)
severity: major
- blocking: 是。補選的結果有一種常見情境會拿不到內容。

**#6 第一項無條件印外部事實行,取前 10 行會漏掉真正要的碼**
- 計劃段落:第一項
- 引句:「每篇最多 10 行、每行截 200 字」
- 問題 A:每篇列出的筆記都印,不管這次改動有沒有碰外部碼,也不管這行跟改動有沒有關。現存就有一行外部 FACT:`Projects/代碼審鏡頭對照DDIA_調研.md` 的 DDIA 出版資訊。它的來源是調研網搜,不是「官方原文」,標題卻固定寫「官方或第三方來源…以原文為準」。
- 問題 B:一篇真正的碼表可能列幾十個碼,只取檔案順序的前 10 行。要抓的 2000 和 1005 不一定在裡面。
- 問題 C:`[查:網址]` 放在行尾,截 200 字時網址先被砍,出處就沒了。
- 問題 D:計劃沒說外部事實行是在 `summary:` 還是正文找。現行合約行只掃摘要區塊,這裡不定義就會各寫各的。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Projects/代碼審鏡頭對照DDIA_調研.md`(摘要區的 `FACT:` 加 `[來源:外部]`)
  - file: `scripts/lumos:3367`(`_CTX_SOURCE_RE` 允許 `\s*`,比計劃說的寬)
  - file: `scripts/lumos:39370`(合約行掃描只認摘要)
severity: major
- blocking: 是。實驗成功是因為碼表就是那一篇,放進生產後取樣方式會讓它失效。

**#7 預算:渲染段沒有可用的剩餘時間,而且 20 秒逾時沒受剩餘時間約束**
- 計劃段落:第二項、實務隱患/效能
- 引句:「每篇沿用既有讀檔函式的 20 秒逾時,並受內層 45 秒總帳的剩餘時間約束」
- 問題 A:45 秒的 `_t0` 只在固定席為 0 的備援路徑才換算成 `deadline`。固定席非空時渲染段完全沒有這個變數,要自己接。
- 問題 B:`_lens_git` 的逾時預設 20 秒,不看剩餘時間。剩 3 秒時讀一篇,最壞可超出 17 秒,算不到「約束」。
- 佐證:
  - file: `scripts/lumos:40350`
  - file: `scripts/lumos:39244`
severity: minor
- blocking: 否。超時只是補選慢,不會讓鏡頭整個失敗;但規格寫成「受約束」是假宣稱,實作時要自己拉線。

**#8 兩種鏡頭共用渲染,第一項也會改設計審的輸出**
- 計劃段落:設計/PRIOR-ART
- 引句:「派工鏡頭的節點渲染(兩種鏡頭共用一支)」
- 問題:`_lens_render_listed` 同時服務 diff 與 spec(設計審)。第一項會讓設計審那份附件也多出外部事實行。
  - spec 模式讀的是工作樹,不是 base。
  - S2 只寫「派工鏡頭」,沒說兩種都印,也沒有測試覆蓋 spec 模式。
- 佐證:
  - file: `scripts/lumos:40007`
severity: minor
- blocking: 否。先寫明意圖與測試範圍即可。

**#9 形狀的輸入範圍沒定義**
- 計劃段落:共用形狀
- 引句:「刻意不認:沒有引號的數字比較(`== 200`,HTTP 狀態碼語意公開周知,認了會誤傷大量程式);測試檔(沿用既有的測試檔判斷)」
- 問題 A:鏡頭目前沒有「改動行」的取得函式。
- 問題 B:題目表走 `_stack_changed_ok` 與棧鍵,鏡頭補選看不到棧。沒說用不用 `_stack_changed_ok`,非程式副檔名(`.md`、`.json`)裡的 `== "0000"` 範例會誤命中。
- 佐證:
  - file: `scripts/lumos:35692`
  - file: `scripts/lumos:38776`
severity: minor
- blocking: 否。要在實作前補一句來源與過濾條件,否則 S1 的測試不知道要釘哪一條路徑。

**#10 注入面擴大,與既有消毒原則不一致**
- 計劃段落:第一項
- 引句:「這段標題固定寫「外部事實(官方或第三方來源,程式碼看不到;以原文為準)」」
- 問題 A:鏡頭程式碼註解寫「來自圖譜或 diff 的自由文字零輸出——只印固定字彙、路徑、base 版合約行」。新段落把任意一行 FACT 自由文字推到審查員眼前。
- 問題 B:雖然從 base 版(主線)讀、外面有注入框,但「以原文為準」是工具自己寫的話,等於替筆記內容背書。
- 問題 C:計劃沒寫這次是刻意放寬,也沒更新該註解。
- 佐證:
  - file: `scripts/lumos:39028`
  - file: `scripts/lumos:40344`
severity: minor
- blocking: 否。信任邊界是承認過、有框的,但要改註解並避免「以原文為準」這種過度背書。

**#11 題目表的性質**
- 計劃段落:第三項
- 引句:「題目表裡除了 sql 以外的每個棧」
- 問題 A:沒說 extcode 要不要 `needs_backing`。這是正確性題不是併發題,應明寫「不要」。
- 問題 B:題目文字括號不成對(「(FACT 行帶 [來源:外部],附官方網址)網址寫在 [查:] 欄,不要寫進來源標記)」)。
- 佐證:
  - file: `scripts/lumos:23397`(id 的 `needs_backing` 欄位用法)
severity: minor
- blocking: 否。

---

blocking 5 條(#1 到 #6 中的 #1、#2、#3、#4、#5、#6 共 6 條為 blocking),最嚴重等級 major。

更正上面這句:blocking 是 6 條(#1、#2、#3、#4、#5、#6),minor 5 條(#7 到 #11),最嚴重等級 major。