# r2 s4 — S1 Check A v2:詞表/豁免/掃描範圍/標記文法/存量回填

審查對象:`/tmp/檢核收緊五件-r2.md`(v2)§S1「Check A:承認句必須標型」(line 43-56、97、112-122)。
方法:把 v2 規則逐字實作成拋棄式 python 腳本,對 `docs/lumos-toolchain-knowledge/**/*.md`(311 檔)實掃,不是憑印象審。

**腳本位置**:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/fc47dab4-74db-4c20-9ccf-6c90d8bf7b79/scratchpad/check_a_v2.py`
**執行**:`python3 check_a_v2.py .`(於 repo root)
**結果**:311 檔全掃,詞表命中 **61 處**,套用否定前綴豁免+區段豁免+圍欄豁免後仍剩 **61 處**(當前全庫 0 個 `<!--lumos:risk=...-->` 標記,故 61 = 全部會被 `lumos lint` rc1 / `doctor --ci` 記 issue 的行)。

---

## Finding 1(blocker)——詞表定義本行自撞閘,而且是本設計即將寫入圖譜的那份文件

引句:「**詞表** `_RISK_ADMIT_LEXICON`(封閉常數):`靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`;`純靠`/`不驗` 僅在同行出現 `工具|code|程式|機制` 時算。」

實測:此行本身(單一行內連續列出全部 7 個詞,單反引號 inline code,非三反引號圍欄)已經以「Projects/檢核收緊五件_計劃」節點的型態存在圖譜裡:
`docs/lumos-toolchain-knowledge/Projects/檢核收緊五件_計劃.md:45`
```
**詞表** `_RISK_ADMIT_LEXICON`(封閉常數):`靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`;`純靠`/`不驗` 僅在同行出現 `工具|code|程式|機制` 時算。
```
掃描結果:此行同時命中 `靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`/`純靠`/`不驗` 共 7 個詞(`純靠`/`不驗` 因同行出現 `code|程式|機制` 而觸發 contextual gate)。三道豁免全部不適用:不是否定前綴(詞前 6 字是「):`」這類標點/反引號)、不在「審計修正紀錄」類標題底下(在「設計」節「S1 Check A」小節)、不在三反引號圍欄內(單反引號 inline code 不算圍欄)。**這代表:CLAUDE.md 要求「任何設計/spec/計劃產出一律寫成 `Projects/<主題>_計劃` 節點」,而這份 v2 spec 本身正是要進圖譜的那個節點——Check A 一上線,定義自己詞表的那一行會立刻讓 `lumos lint`/`doctor --ci` 對這個節點噴 7 個 finding。** r1 對這個「Issue 自撞」模式已經抓過一次(s3-F2,見 Finding 9),但只補了 Issues/寫下風險當成處理風險 一處,沒發現 spec 自己這行也中,說明修法不是通用規則而是逐案打補丁。

**正確規則**:詞表列舉/定義的自我豁免不能只靠「別讓詞表出現在非圍欄行」的人工紀律(那就是本案本身在打的「寫下風險當成處理風險」)。要嘛①強制詞表本身在原始碼常數之外只能以圍欄呈現(spec/skill 文件內),要嘛②新增「同行 backtick-delimited 詞表列舉(`/`分隔且每個 token 恰為詞表成員)」的結構性豁免,而非只靠 fence/section/negation 三件事。

---

## Finding 2(major)——掃描範圍排除 `decisions[].content`/`why_chosen`,但那裡已經有真實承認句

引句:「**掃描範圍**(r1 s1-F3):整檔文字=frontmatter `summary` 區塊 + body(」

分析:`scripts/lumos` 的 `parse_frontmatter()`(scripts/lumos:112-175)只把 `summary: |` 這類 **block scalar** 存進 `fields["summary"]`;`decisions:` 是巢狀 list-of-dict(`id/decided/content/context/why/why_chosen/rollback/guard`),其子鍵值**完全不會**被解析進 `fields`(`LIST_ITEM_RE` 只吃 `- ` 開頭那一行,子鍵行被迴圈吃掉但未存)。v2 明講掃描範圍「整檔文字=frontmatter `summary` 區塊 + body」——這是**只點名兩塊**,`decisions[]` 不在其中任一塊,是結構性排除,不是含糊。

實測:`decisions[]` 裡現在就有承認句,例如
`docs/lumos-toolchain-knowledge/Projects/Android側UI測試綁圖譜工作流_計劃.md:42`
```
      綁 name: 而非路徑,代價=flow 檔改名/搬家時 name 與檔名可能不一致(靠命名慣例自律,無機械守衛);
```
此行是某條 ADR 決策的 `why_chosen:`/`content:` 子欄內文(frontmatter `decisions:` 巢狀鍵下),含 `無機械守衛`(貨真價實、非引用、非定義)。因為它既不在 `summary` block scalar 裡、也不在 body,Check A 依 spec 字面規則**永遠掃不到它**——不是「豁免掉了」,是根本不在掃描域內。

**回答上級指定的檢查點**:frontmatter `decisions[].content` 文字**不在**「summary 區塊」內——`summary` 是專指 `summary: |` 那個獨立 block scalar 鍵,`decisions` 是另一個 top-level list 鍵,parse_frontmatter 對兩者的處理路徑完全不同。這是一個真實的掃描盲區,而非模糊地帶。

**正確規則**:若 Check A 的目的是「防止宣稱有守衛、實際沒有」的承認句逃過標記,掃描範圍至少要包含 `decisions[].content`/`why_chosen`/`context`(ADR 決策文本是這類承認句的高頻棲息地——上面的例子即是),否則存量回填(§存量)只會抓到 summary/body 兩處,`decisions[]` 裡的承認句永久計不到、也永久不會出現在退場條件的分子分母裡。

---

## Finding 3(blocker)——「圍欄豁免沿用 Check N」抄的是專案自己明令禁止重新加回的 pattern

引句:「圍欄內不掃(沿用 Check N)。」

實測:`scripts/lumos` 裡有兩個不同的「Check N」(命名本身有歧義,見 Finding 3b),但唯一在 doctor 裡真的做「圍欄內文字抹空」的是「可重算數字宣稱」檢查,其實作在 `scripts/lumos:1246-1247`:
```python
_fence_re = re.compile(r"```.*?```", re.S)
text = _fence_re.sub(lambda fm: " " * len(fm.group(0)), text)
```
但 `scripts/lumos:61-64` 有一段明文警告:
```
# ★FENCE_RE 已於 2026-08-03 移除,不要再加回來★——它有兩個致命假設:
#   ①圍欄成對(未閉合就看不見) ②標記在第 0 欄(收尾縮排會與下一個區塊錯配、
#   把中間的真散文整段吞掉)。這兩個假設在 code-loop r2/r4 各造成實測的靜默錯答:
#   幽靈圖譜邊、假合約佐證、G1 硬閘對壞引用放行、impact hook 漏掉合約節點。
# ★一律改用 `_visible_lines`(全檔唯一的 fence 判定)★:
```
即 Check N 那段 `_fence_re = re.compile(r"```.*?```", re.S)` 本身就是被 2026-08-03 全域移除、之後又在 Check N 局部重新加回的 `FENCE_RE`(該行上方 2026-08-21 的註解自己也承認是為了防「Check N 自家範例被當真標記掃」而臨時補的——見 `scripts/lumos:1244`)。它不是本專案「全檔唯一的 fence 判定」(`_visible_lines`,`scripts/lumos:1534`起),而是一個已知帶兩個「致命假設」缺陷、只在 Check N 這個局部復發的偏差實作。v2「沿用 Check N」等於把這個已知瑕疵的圍欄判定原樣抄進 Check A——未閉合圍欄會吞掉後面全部真散文(把之後所有承認句都豁免掉,反而製造漏抓)、縮排的圍欄會與下一段錯位。

**正確規則**:S1 的圍欄豁免應該抄 `_visible_lines(keep_fenced=False)`(scripts/lumos:1534,「全檔唯一的 fence 判定」),不是抄 Check N 局部的 `_fence_re` regex——後者正是專案自己在 61-64 行寫下教訓要求不准再犯的模式。

### Finding 3b(minor,附掛同一引句)——「Check N」在 scripts/lumos 裡不是單一指涉

`scripts/lumos` 裡有兩個 section 都叫「Check N」:一個是「可重算數字宣稱」(scripts/lumos:1231,`section("N", "可重算數字宣稱 ...")`),另一個是「版本更新提示」(scripts/lumos:1318,`# Check N: 版本 nudge`)。v2「沿用 Check N」字面上有歧義,只能靠讀者猜是指前者(因為只有它做圍欄抹空);若照抄進實作 docstring/注解,一字不改地寫「沿用 Check N」會延續這個指代不清。

---

## Finding 4(major)——區段豁免對 frontmatter 完全不成立,而「審計紀錄」的實際承載位置多半就是 frontmatter 的 `KEY:` 行

引句:「**區段豁免**(r1 s3-F3):標題為 `審計修正紀錄|審計紀錄|歷史|變更紀錄` 的 section 內不掃(敘述過去式承認)」

分析:「section」是 markdown heading(`^#{1,6}\s+...`)語法;frontmatter 的 `summary: |` block scalar 裡只有 `FLAG:`/`KEY:`/`FLOW:`/`DEP:`/`DECISION:` 這類符號行,**沒有 heading 語法**,region-title 豁免結構上不可能在 summary 區塊內成立。這不是「沒寫清楚」,是規則的作用域天生只覆蓋 body。

但實測顯示,本庫大量節點把「審計紀錄」寫成 `summary` 裡的 `KEY:` 一行,而非 body 底下的獨立 section,例如:
- `docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md:19`(KEY 行內以 `★(2026-08-21 程式碼實證)這三個參數**程式碼零實作**...★` 記錄「已查清、已如實揭露」的過去式審計事實)——含 `零實作`,且不在任何 body 的「審計修正紀錄」標題下,section 豁免完全用不上。
- `docs/lumos-toolchain-knowledge/Systems/design-loop.md:33`(`KEY:...M0 honor-system、M1 機械化...本 KEY 早期「須新增單席謂詞」的未來式已兌現...`)——同樣是敘述「這件事以前是 honor-system、後來補上機械化」的過去式/已改善紀錄,寫在 summary 的 KEY 行,不是 body section。
- `docs/lumos-toolchain-knowledge/Issues/probe輪三參數只在散文.md:14`(KEY 行:`scripts/lumos 零實作:cap 計數含全部 distinct round、無次數上限、無席數檢查`)。

這三個都被本次實掃判定為「命中且無標記」(見腳本輸出 summary 區塊那幾行)。它們是否算「敘述過去式承認」見仁見智,但至少 `convergence-evidence-gate.md:19`/`design-loop.md:33` 明顯是「已查清、已改善」的審計紀錄語意,跟 v2 想用 section 豁免放過的東西是同一類——只是承載媒介是 `KEY:` 行不是 markdown heading,規則完全接不到。

**正確規則**:region-title 豁免要嘛明講「只對 body 生效,frontmatter summary 內的審計紀錄一律必須標記」(這樣才是自洽規則,但要在 spec 裡把這條後果寫出來,因為它意味著大量 KEY 行都要補標),要嘛另外定義 summary 專用的「KEY: 行內以 `已查清/已改善/已兌現/程式碼實證` 等字樣起頭視為歷史敘述」豁免——目前 spec 對這個岔路完全沒表態。

---

## Finding 5(major)——`why=`/`revisit=`/`issue=` 是無引號的空白分隔 key=value,承載中文自由文的 `why=` 必然撞文法

引句:「`<!--lumos:risk=C why=<非空> revisit=<非空>-->`。」

分析:整份 spec 沒有定義這個 HTML 註解內部的 tokenizer,只給了範例。若比照本庫既有的同類標記——Check N 的 `<!--lumos:count=7 re=某正則 in=**/*.cs-->`(`scripts/lumos:1236`,`_CNT_RE = re.compile(r"<!--\s*lumos:count=(\d+)\s+re=(.+?)\s+in=(\S+?)\s*-->")`)——那是**目前唯一的同類先例**,它靠"下一個 key= 一定緊接在 `\s+` 後面"這個假設用 lazy regex 卡住 `re=` 的邊界,對 `re=` 這種通常無空白的技術字串還算堪用。

`why=`/`revisit=` 語意上要裝的是**中文自然語言理由**(C 型的「已接受」理由,例如「理由=測試仍跑、改了不會壞只會白做」這種本庫既有寫法,見 `docs/lumos-toolchain-knowledge/Issues/寫下風險當成處理風險.md:66`)——這種文字必然含空白、常含全形/半形 `=`(本庫行文習慣大量用 `X=Y` 簡寫,例如這份 v2 文件自己就寫了幾十次 `詞表=`/`掃描範圍=`/`退場=` 這種结构)。若沿用 Check N 那套「空白分隔 token,每個 token 各自 split 一次 `=`」的天真實作:
- `why=已知限制,測試仍跑=可接受風險 revisit=...` → `why=已知限制,測試仍跑=可接受風險` 這個 token 本身含第二個 `=`,`partition("=")` 只會切第一個,值變成 `已知限制,測試仍跑=可接受風險`(還算能接受,因為 partition 是切第一個不是報錯);但若改成貪婪匹配到下一個已知 key(`revisit=`)前的所有文字,一旦 `why=` 的中文理由裡本身就出現空白後接似 key 的字("...原因是 revisit 這件事成本太高 revisit=2026-12-01"),`revisit=` 這個字面詞出現在理由文字裡會被誤判成真正的欄位邊界,把 `why` 值攔腰截斷。
- 若改用貪婪一路吃到 `-->` 再切,則 `why=` 值裡如果恰好包含子字串 `-->`(理論上少見但 markdown 裡箭頭符號常寫成 `-->`/`->`)會讓整個 HTML 註解提前結束,後面 `revisit=...-->` 變成裸露文字。

**正確規則**:spec 至少要指定一種逃逸/引號機制(例如整段值用 `"..."` 包住、或規定值不得含空白與 `=`,把「理由」改成一個查證用的短代碼+另外存長文在 body),否則「why=<非空>」在真實填寫時大機率不是一段乾淨無空白短字串,標記文法在還沒開始用就已經不穩。TDD 測試清單(`t_checka_C_fields`)只驗「缺欄」,完全沒有一條測 `why=` 含空白/`=`/`-->` 時的解析行為——這正是本欄位最可能出錯的地方,卻沒有測試覆蓋。

---

## Finding 6(minor/major 邊界)——`issue=Issues/<stem>` 走 `env.find()` 時,「路徑」其實只是「stem 的裝飾」,回退會跨資料夾誤配

引句:「`<!--lumos:risk=B issue=Issues/<stem>-->`(resolve 到存在且 `type: issue`)」

分析:本庫既有的節點解析邏輯 `Env.find()`(`scripts/lumos:293-305`)是這樣運作的:
```python
if "/" in a and (a + ".md") in self.notes:
    return a + ".md"
hits = self.by_stem.get(a.rsplit("/", 1)[-1].lower())
```
只有當 `Issues/<stem>.md` **真的存在**時,`Issues/` 這個前綴才有作用;一旦不存在(打錯字、節點被搬到別的資料夾但沒改標記),它會**丟掉 `Issues/` 前綴**,退回全庫按 stem(檔名去掉副檔名)查——若剛好某個 `Systems/`/`Projects/` 節點有相同 stem,`env.find()` 會回傳那個完全不同資料夾的節點(且會印一行 `⚠ 同名筆記 N 個` 到 stderr,但函式仍回傳命中結果而非 None)。Check A 的判定邏輯若照抄這個 `find()`(v2 沒有另外定義解析函式,只寫「resolve 到存在」),後續的 `type: issue` 檢查雖然還能擋掉「誤配到非 issue 節點」的情況,但**擋不掉「誤配到另一個資料夾裡剛好也是 type: issue 的同名節點」**這種情況——B 標記會被判「合法」,但其實指向了錯誤的 Issue。

**正確規則**:`issue=` 若要求前綴 `Issues/`,判定時應該直接檢查 `rel == "Issues/" + stem + ".md"`(嚴格路徑相等),而不是把值丟給寬鬆的 `env.find()`;否則「path vs stem」這兩種語意混在一起,`Issues/` 前綴形同虛設。

---

## Finding 7(major)——`downgraded=YYYY-MM-DD ... 不晚於今日` 沒說「今日」是哪台機器的哪個時區

引句:「`<!--lumos:risk=B downgraded=YYYY-MM-DD-->`(合法日期、不晚於今日)。」

分析:`scripts/lumos` 全庫的「今日」一律是 `datetime.date.today()`(裸呼叫,例如 `scripts/lumos:2863`/`5752`/`6379`/`7015`/`7337`/`7463`,無任何 `timezone.utc`/`.astimezone()` 正規化)——即**執行機器的本地掛鐘日期**,無時區錨定。`downgraded=` 若沿用這個既有慣例,同一個標記在不同時區/不同機器上跑 `lumos lint`/`doctor --ci` 會有一天的判定落差:例如作者在 UTC+8 深夜寫下 `downgraded=2026-08-22`(對他是「今天」),若 pre-push hook 或 CI runner 在 UTC(比 UTC+8 慢 8 小時)執行、且執行當下 UTC 時間仍是 08-21,`date.today()` 回傳 08-21,`2026-08-22 > 08-21` 就會被判「未來日」而報錯——**同一份提交在作者本機通過、在 CI 上失敗**。這類問題本庫並非沒意識到(例如 `LUMOS_PANEL_K2_CUTOFF` 用 env 變數覆寫日期基準做測試錨定,`docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md:19`),但 S1 spec 對 `downgraded=` 的「今日」完全沒有比照處理。

**正確規則**:要嘛明講「今日=執行環境本地日期,contributors 需注意時區,不做 UTC 正規化」(接受既有慣例、但寫清楚以免誤判是 bug),要嘛統一走 UTC 或 git commit 時間戳定義「今日」(更適合 CI 場景)。目前留白。

---

## Finding 8(major)——「雙入口抄 `check_regen_provenance()`」的函式簽名結構性放不進 body 文字

引句:「雙入口抄 `check_regen_provenance()`。」

分析:`check_regen_provenance(note, repo_root)`(`scripts/lumos:2416`)的簽名只吃 `note`(`Note` 物件)與 `repo_root`,函式內唯一讀到的文字來源是 `note.fields.get("summary")`(`scripts/lumos:2429`)——**它從不讀 body**,因為 Check J 的稽核範圍本來就只限 regen 節點的 summary block(docstring 明講「只掃 summary 行」)。`Note.__slots__`(`scripts/lumos:188-189`)是 `rel, stem, fields, block_keys, fm_lines, targets, lint, mtime`——**沒有任何欄位存 body 原文**;`fields` 只由 `parse_frontmatter()` 產生,只覆蓋 frontmatter。

但 S1 的掃描範圍明講「summary 區塊 + body(兩者都掃)」(見 Finding 2 引的同一句)——`check_regen_provenance(note, repo_root)` 這個簽名結構上**沒有管道拿到 body 文字**。要嘛擴充簽名(例如 `check_risk_admission(note, body_text, repo_root)`,呼叫端額外做一次 `(env.vault / rel).read_text(...)` 把 body 傳進去——這在本檔案並非首例,`cmd_lint` 自己在別處已經這樣重讀原始檔:`scripts/lumos:2673`(`_fm_lines, _ = split_frontmatter((env.vault / rel).read_text(...))`),`run_doctor` 對 Check N/Check Y 也各自重讀原始檔:`scripts/lumos:1203`/`1241`),要嘛把「抄 check_regen_provenance()」改成「抄它的雙入口**呼叫模式**(同一函式被 run_doctor 與 cmd_lint 各呼叫一次、errs/warns/gov 三分流映射同一套)」,而不是抄它的**參數簽名**——這兩件事目前在 spec 裡沒有分清楚,若實作者真的把 `check_regen_provenance` 的簽名原樣複製,第一步就會發現拿不到 body、被迫另開一套,等於「抄」這個詞在這裡是誤導性的。

`errs/warns/gov` 三分流映射本身(`scripts/lumos:2419-2422` docstring 那張表)倒是可以照搬,這部分「同一套模式」的說法成立;純粹是簽名層級(拿不到 body)這一點對不上。

---

## Finding 9(blocker)——r1 s3-F2「改放圍欄」的修法沒有真的落地到現實檔案,存量回填會立刻自撞

引句:「[[Issues/寫下風險當成處理風險]] 內列舉句式的那段改放圍欄(r1 s3-F2)。」

分析:v2 §審計修正紀錄(line 114)聲稱 r1 blocker s3-F2「Issue 節點自撞→例句入圍欄」已折入修正;§設計 line 56 再次確認「那段改放圍欄」。但實際檔案 `docs/lumos-toolchain-knowledge/Issues/寫下風險當成處理風險.md` 的「## 現象」段(line 22-29)**現在仍是純 markdown bullet list,不是三反引號圍欄**:
```
## 現象

以下句式在圖譜與 skills 中反覆出現,已成慣用語:

- 「★這是觀測不是強制★」「恆 rc0,不擋」
- 「無機械守衛,靠自律」「純靠 honor-system」
- 「這個數字是拍的,無根據」
- 「本工具不碰 GitHub 設定,要擋得自己去設分支保護」
```
(`docs/lumos-toolchain-knowledge/Issues/寫下風險當成處理風險.md:24-29`)

本次實掃這段命中 3 個詞(`靠自律`/`honor-system`/`無機械守衛`,見腳本輸出 body:10 那行),而且同一份文件下面的判準表格(line 47-70)還有 6 處類似命中(`body:16/32/32/37/49/50/51`)——包括「把全庫 38 處『靠自律／honor-system』讀完」(line 32,這句在描述**這篇文件自己做過的統計工作**,語意上是這篇 Issue 的核心方法論陳述,不是引用),以及分類表格裡多個**表格儲存格**(「| 「pass --note 須含效能檢核答案」code 零檢查 | **B→降級** | ... |」等,line 50/51),这些都是在「實例」欄位裡引用**其他系統**(skill/probe/slim)的承認句作為分類對象,不是本文件自身對其宣稱的守衛狀態做出承認。

**這代表兩件事**:①r1 審計修正紀錄聲稱已修的東西,實測**沒有真的動過那個檔案**——這是「審計紀錄寫了修正、實際檔案沒同步」的活生生案例,恰好正是本案 S1 想解決的那類問題,出現在本案自己的修正紀錄裡。②即使照 v2 規則字面實作,這個 Issue 節點在存量回填當天至少有 9 處會被判「命中」,其中至少 3 處(line 24-29 的例句 bullet list)按 spec 自己的意圖應該被圍欄豁免掉但目前沒有,另外多處是表格儲存格裡引用「其他系統」的承認句,不是這篇文件自身的承認——詞表+三豁免規則對「這是在講別人」跟「這是在講我自己」完全沒有分辨能力,只能靠人工在存量回填時逐條判斷,跟現有「28~51 句零分類」的起點沒有本質差異,只是換了一個新標記語法去人工分類同一批句子。

**正確規則**:①先把 §審計修正紀錄聲稱已完成的圍欄化實際套用到 `寫下風險當成處理風險.md`(否則「審計修正紀錄」這欄位本身就示範了它想防的漂移);②詞表/三豁免規則需要額外一種「這是在描述/分類別的系統的承認句,不是本節點自身的承認」的判斷依據(例如:表格欄位標題含「型」「分類」「實例」等 meta 詞、或整段被「以下句式...」這類 meta-narration 開場——目前規則完全沒有這條,存量回填會把大量方法論陳述誤判為需要標記的承認句)。

---

## 綜合:Check J 雙入口模式是否「同一套模式」適用於 S1?

`check_regen_provenance()` 的**呼叫慣例**(`run_doctor` 與 `cmd_lint` 各呼叫一次、`errs→硬/warns→軟/gov→僅--ci`三分流)可以照搬,這部分成立。但**函式簽名**(只吃 `note`,靠 `fields["summary"]` 拿文字)結構上不覆蓋 S1 需要的 body 文字,詳見 Finding 8——「抄」這個字在 spec 裡沒有區分「抄模式」還是「抄簽名」,是本次審查發現的落差,不是無中生有的挑剔:兩函式的資料需求集合(J 只要 summary;A 要 summary+body)本來就不一樣,呼叫端勢必要多做一次檔案讀取。

---

## 總結

實掃 311 個節點,v2 字面規則命中 **61 處**、目前全部無標記(0 個現存 `<!--lumos:risk=...-->`)。其中至少 9 處(`Issues/寫下風險當成處理風險.md` 的例句 bullet list 與判準表格儲存格、`Projects/檢核收緊五件_計劃.md` 自己的詞表定義行)是明顯的「在講別人/在定義詞表/在做分類」而非本節點自身的承認句,規則對此沒有分辨力;至少 1 處(`Projects/Android側UI測試綁圖譜工作流_計劃.md` 的 `decisions[].content`)是規則掃描範圍結構性排除、但明明是真承認句的盲區。核心結構性問題(Finding 1、3、8、9)足以在實作第一天就讓這份 spec 即將寫入圖譜的自己撞閘、圍欄豁免抄到一個已知有缺陷且被專案明令禁止的 pattern、雙入口簽名對不上資料需求。

---

**命中數:61**
