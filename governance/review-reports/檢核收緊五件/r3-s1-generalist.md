# 檢核收緊五件 r3 — Seat 1 Generalist Review

Lens: whole-document hunt for what v3 newly introduced or left inconsistent between
rewritten sections (設計/退場條件/本PR段/測試策略) and retained sections
(緣起/準入三問/PRIOR-ART/實務隱患/未決). Verified against `scripts/lumos` (~15,100 行)
and `scripts/test_lumos.py`.

---

## Finding 1 [blocker] — Check A 宣稱掃 body,但 Note 物件不存 body;`cmd_lint` 拿不到掃描來源

引句：「整檔文字(frontmatter 全部——含 summary/decisions[].content/why_chosen——加 body)」

**問題**:S1「掃描範圍」明講要掃「frontmatter 全部…加 body」,而「雙入口」段要求
`check_risk_admissions(notes)` 由 `cmd_lint` 與 `run_doctor` 各自呼叫。但 `Note` 類別
`__slots__`(`scripts/lumos:187-189`)只有 `rel/stem/fields/block_keys/fm_lines/targets/
lint/mtime`——**沒有 body 欄位**。`load_vault()`(`scripts/lumos:207`)讀出 `body` 後只
用 `_strip_code_text(body)` 算 `body_clean`(`scripts/lumos:212`)餵給
`extract_targets()`(`scripts/lumos:229`)抽 wikilink,取完就丟——body/body_clean 不會存
回 `Note` 物件。`cmd_lint(env, node)`(`scripts/lumos:2600`)只吃 `env.notes[rel]` 這個已
載入的 `Note`,不重新開檔。

也就是說,若 `check_risk_admissions` 照字面接一個 `Note`(或 `notes` 集合),它能拿到的只
有 `fields`(frontmatter)——body 文字**不在**這個物件上,除非另外用 `env.vault / rel` 重
開檔讀取整份原始文字。但 S1 全文從未提到需要「重新讀檔」這一步,也沒有像 Check J 的
`check_regen_provenance` docstring 那樣明講「opt-in、量小」的檔案存取例外
(`scripts/lumos:2417-2426` 的 docstring 明講「只掃 summary 行」,刻意避開整檔 body)。

若實作時沒注意到這個落差,最可能發生的事:`check_risk_admissions` 悄悄退化成「只掃
frontmatter,不掃 body」——而本文件自己踩到的三個未標記命中(見 Finding 2)全部都在
**body**(緣起清單、準入三問表格、測試策略清單),不在 frontmatter。這正是題目要求「特別嚴
抓的『硬閘悄悄不動』」的那一類坑:文件宣稱「硬擋整檔」,實際可能只擋到 frontmatter 半份。

**file:line**:`scripts/lumos:187-189`(Note.__slots__ 無 body)、`scripts/lumos:207-212`
(body 讀出即棄,只留 body_clean 給 extract_targets)、`scripts/lumos:2600`(cmd_lint 只吃
`env.notes[rel]`)。

**正確做法**:S1 應明講 `check_risk_admissions` 是否比照 Check J 開一個「node-local 但需
檔案存取」的例外(重讀 `env.vault / rel` 取原始文字),並在雙入口段落寫清楚 cmd_lint 那一
側怎麼取得 body——不能只沿用「抄 Check J 雙入口結構」帶過,因為 J 自己刻意只掃 summary、
沒有這個坑。

---

## Finding 2 [major] — 文件自己就有三處未標記的承認句命中,「①先補標存量…使 Check A 上線即綠」不成立

引句：「紀律寫了、code 零檢查」

**問題**:本節點(v3 這份文件本身,frontmatter `type: project`,是會被 lint/doctor 掃到的
真實圖譜節點)依 S1 自訂的詞表規則,至少有三處未標記的命中,且都**沒有**否定前綴
(`_RISK_NEG_PREFIX` 6 字內不含 非/不是/而非/不再/不靠/取代/≠/~~):

1. `line 23`(緣起與裁定鏈,retained 段):「紀律寫了、code 零檢查」——命中 `_RISK_ADMIT_
   LEXICON` 的「零檢查」,前 6 字為「、code 」,無否定前綴,未加任何 `<!--lumos:risk=…-->`
   標記。
2. `line 31`(準入三問表格,retained 段):「兩處 skill 寫「須」而 code 零檢查」——同樣命中
   「零檢查」,前 6 字為「而 code 」,無否定前綴,未標記。
3. `line 101`(測試策略,v3 rewritten 段)test 6 描述本身:「「而非靠自律」不報,「靠自律」
   報」——第二個「靠自律」前 6 字是「不報,「」,不含否定前綴,依規則本身就是一個命中,卻
   同樣沒有標記(它甚至就是在示範「這種寫法會報」的例句,自己卻沒被標)。

而「本 PR 怎麼過自己的規則」段(rewritten,`line 97` 一帶)只交代:「①先補標存量承認句+
兩處圍欄,使 Check A 上線即綠」——「兩處圍欄」明確只指 `line 45-50` 的詞表定義區塊與
[[Issues/寫下風險當成處理風險]] 的句式列舉段(`line 60`);另外只在 `line 91` 明確自標了
一處(「這條人工盤點本身靠自律」→ `<!--lumos:risk=A-->`)。line 23/31/101 這三處完全沒被
提及、也沒被圍欄或標記涵蓋。若 Check A 依 S1 規則字面實作並對這份文件跑一次,**這份定義
「上線即綠」的文件自己會先紅**——與 self-governance 段「四個逃生門全部落帳可數」的自信不
符,說明本輪自我盤點(line 60 那句「見下方已標」暗示已窮舉)其實不完整。

**file:line**:純文件層面問題,對照規則見 `line 47-50`(詞表定義)。

**正確做法**:比照 line 91 的做法,把 line 23、31、101 的命中詞也標上 H(這些都是敘述
「過去發現的問題」或「舉例說明」,屬於 H 型)或搬進圍欄,並在「本 PR 怎麼過自己的規則」
段落誠實列出完整清單(而不是宣稱「使用 Check A 上線即綠」卻只處理了一部分)。

---

## Finding 3 [major] — 「時區差屬天花板,H 標」與 H 型自己的定義互相矛盾

引句：「時區差屬天花板,H 標」

**問題**:S1 「標記」小節(`line 52-56`)明確定義:
- `A` = 天花板型(承認結構性限制),帶任何欄=違規;
- `H` = 歷史/引用型(「敘述過去式承認、引用他處句子、定義詞表——非現行承認」),帶欄=違規。

`line 55` 講「時區差屬天花板」——用詞直接說這是「天花板」型限制,照上面的定義應該對應
`A`(天花板型),但句尾卻寫「H 標」(改標 H)。這是自相矛盾:
1. 語意上,`downgraded="YYYY-MM-DD"` 因時區判定產生的邊界爭議,不是「敘述過去式」、不是
   「引用他處句子」、也不是「定義詞表」,不符合 H 的定義,反而完全符合 A 的定義(「承認一
   個檢查機制驗不準的結構性天花板」)。
2. 操作上更麻煩:`H` 的規則是「帶欄=違規」,即 H 標記**不能帶任何欄位**。但這裡討論的是
   `B downgraded="YYYY-MM-DD"` 這個**本來就帶欄**的標記類型;若真的要「改標 H」,就必須把
   `downgraded=` 這個日期欄位整個拿掉——但那個日期正是「哪天降級」的追溯依據,拿掉等於讓
   S1 存量分型表(`line 60`)少了關鍵資訊。這條指示要嘛無法照字面執行(留欄位就是 H 違
   規),要嘛執行了就丟失資訊,兩條路都通不過。

**file:line**:規則定義見 `line 53-54`(A/H 兩型定義);矛盾點在 `line 55`。

**正確做法**:比照文中「天花板型」的既有定義,這裡應該標 `A`(且不帶欄,只留一段純敘述說
明這是已知的時區判定限制),而不是 `H`;或者如果作者的本意是別的東西(例如「這句話本身
在描述一個已知限制,屬於文件自身的天花板承認,故標 A」),也需要把「H 標」三個字改成
「A 標」以消除矛盾。

---

## Finding 4 [major] — 「未閉合圍欄不吞下文」與 `_strip_fences_text` 既有測試語意完全相反

引句：「含未閉合圍欄不吞下文——沿 `_strip_fences_text` 既有測試語意」

**問題**:S1 測試策略 test 7(`line 101`)宣稱「未閉合圍欄不吞下文」,並引用
`_strip_fences_text` 的「既有測試語意」當作依據。但實際的既有測試語意剛好相反——
`scripts/test_lumos.py:12174-12185` 的 `t_search_visible_lines_...`(② 未閉合圍欄段)明講:

```
# 未閉合圍欄之後才出現「戊己」——主迴圈視為 code(搜不到)
```
且斷言「「戊己」在未閉合圍欄之後,單獨搜必須是 0 篇」(`scripts/test_lumos.py:12184-12186`)
——即**未閉合圍欄之後的文字被視為 code,整段隱形**。`_visible_lines`
(`scripts/lumos:1535-1552`)的實作也印證這點:逐行 toggle `in_fence`,遇到開頭 ``` 就翻
轉,若之後再也沒有配對的收尾 ```,`in_fence` 會一路保持 `True` 到檔尾,`keep_fenced=False`
時這些行全部被 `continue` 跳過(不 yield)——也就是**整段被吞掉**,直到檔案結尾。這正是
`scripts/lumos:1543-1551` docstring 講的 2026-08-03 修法用意:舊 `FENCE_RE` 才是「未閉合圍
欄看不見(內容反而保持可見)」的舊 bug,新寫法刻意反過來、讓未閉合圍欄後的內容全部隱形,
以避免「幽靈圖譜邊、假合約佐證」。

`_strip_fences_text`(`scripts/lumos:1559-1566`)直接呼叫 `_visible_lines(text.split("\n"))`
(預設 `keep_fenced=False`),行為與 search 那條路徑一致:未閉合圍欄一樣會把之後全部吞掉。

S1 test 7 的描述若照字面寫成測試,會斷言「未閉合圍欄之後的承認句仍被抓到(不吞)」——這與
`_strip_fences_text` 的既有、故意設計的行為直接衝突。若真的改成「不吞」,等於要求
`check_risk_admissions` 另開一條偏離 `_strip_fences_text` 語意的邏輯,但 S1 又同時強調
「★全檔唯一合法 fence 判定★」必須沿用 `_strip_fences_text`(`line 51`)——兩句話互相打
架:「沿用 `_strip_fences_text`」與「未閉合圍欄不吞下文」不可能同時成立。

**file:line**:`scripts/lumos:1535-1552`(`_visible_lines` 逐行 toggle,無收尾則吞到檔
尾)、`scripts/lumos:1559-1566`(`_strip_fences_text` 呼叫方式)、
`scripts/test_lumos.py:12169-12190`(既有測試明確斷言「未閉合圍欄後文字搜不到」)。

**正確做法**:test 7 描述應改為「未閉合圍欄**之後**的內容視同 code、不參與掃描(承認句寫
在未閉合圍欄之後不會被抓到)」——這才是與 `_strip_fences_text` 一致、且與既有測試對齊的
語意;不是「不吞下文」。

---

## Finding 5 [minor] — 「本地日期」用語在 S1/S2 兩處不一致

引句：「元素 `"<gate>@<YYYY-MM-DD>"`(本地日期)」

**問題**:S1(`line 55`)講 `downgraded=` 日期不得晚於「**執行機器本地日期**」;S2
(`line 69`)講 `ratchet_acks` 元素日期是「本地日期」,少了「執行機器」四字限定。兩處講的
應該是同一個概念(跑檢查的機器當下的本地日期),但用語不統一,沒有交代是否為同一定義來源
(例如共用同一個 `_local_today()` 之類的 helper)。跨兩個新機制各自表述同一個「本地日期」
概念而未指名共用實作,容易導致兩邊實作出時區/曆法判定不一致的日期比較邏輯。

**file:line**:文件內部,`line 55` vs `line 69`;無對應既有 code 可查(兩者皆為 v3 新
增)。

**正確做法**:統一措辭並指名共用同一個日期取值函式(或明講兩者刻意獨立、為何可以獨立),
避免「本地日期」在 S1/S2 各自實作出兩套時區判定。

---

5 findings: 1 blocker, 3 major, 1 minor.
