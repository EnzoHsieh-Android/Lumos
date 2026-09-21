severity: blocker

## F1 兩支「已修好」的漂移守衛,實測都還能繞——SKILL.md 用矛盾段落塞在正文繞過整段比對
severity: blocker
blocking: yes

`t_note_convention_synced_to_skill`(`scripts/test_lumos.py:17757`)的判準只是「範本〈寫筆記時〉那一節的逐字內容,有沒有原封不動出現在 SKILL.md / 03-寫回圖譜.md 的『非 HTML 註解』區域裡」。它只堵死了上一輪抓到的那個洞(把正確內容整段藏進 `<!-- -->`),但完全沒檢查「這段文字有沒有被別的、矛盾的段落搶先蓋過」。

引句:「改成整段逐字比對,兩種都擋得住。」

重現(在 `/tmp/seat-通才-審計折入-sonnet` worktree,對照組先跑一次確認乾淨):
```
python3 scripts/test_lumos.py -k note_convention_synced   # 乾淨 checkout:10 passed, 0 failed
```
接著在 `skills/lumos-project-notes/SKILL.md` 的「摘要區塊」段落**前面**插入一段矛盾內容(保留後面完整逐字複本不動):
```python
p = "skills/lumos-project-notes/SKILL.md"
txt = open(p, encoding="utf-8").read()
marker = "**摘要區塊**(Systems/Issues 必有)——分類規則的唯一來源是紀律範本"
idx = txt.index(marker)
decoy = ("**摘要區塊快速版(讀這段就好,不用往下翻)**:其實只有一種前綴 `KEY:`,"
         "其他四個前綴(WHY/RULE/PITFALL/FACT)已經棄用,寫哪個都一樣,不需要出處也不需要退場條件。\n\n")
open(p, "w", encoding="utf-8").write(txt[:idx] + decoy + txt[idx:])
```
再跑一次:
```
python3 scripts/test_lumos.py -k note_convention_synced
```
輸出仍是 **10 passed, 0 failed**——包含那條「skills/lumos-project-notes/SKILL.md 逐字帶著範本那一節(且不在註解裡)」照樣綠,即使檔案開頭多了一段公然唱反調、叫人不用管出處和退場條件的「快速版」。

為什麼是問題:這支守衛的存在理由就是「兩邊分岔會紅」,但它驗的是「文字存在」不是「文字是唯一/優先被讀到的規則」。一個不知道脈絡的人(或另一個 AI)接手改 SKILL.md 時,很可能只在檔案前段加一句「懶人包」而不動後面那段逐字複本——測試照樣全綠,實際上先被讀到的規則卻是錯的。這正是這一批工作(F2 折入)聲稱已經解決、外家審計原本抓到的同一類洞,只是換了個位置繞過去。

（收工已 `cp /tmp/skill_backup.md skills/lumos-project-notes/SKILL.md` 還原,worktree 現在乾淨。）

## F2 進場守衛新版判準是「整份範本任何位置有沒有出現這串字」,不分區塊也不去除 HTML 註解
severity: blocker
blocking: yes

`t_entry_points_agree_with_code_first`(`scripts/test_lumos.py:17672`)這次的修法把「範本不含『先讀程式碼』就 skip」改成 `check(..., "先讀程式碼" in body, ...)`——確實不再靜默跳過,但 `body` 是整份範本檔案的原始文字,**沒有先用 `t_note_convention_synced_to_skill` 剛學到的 `_strip_html_comments` 去掉註解**,判準也沒有限定在〈怎麼用〉第一步那一句,只要全檔任何角落出現這四個字就算過。

引句:「連同這支守衛與 _OLD_POSITION_PHRASES 一起改,不要靠改措辭讓守衛靜音」

重現:
```
sed -i '' 's/1\. \*\*先讀程式碼\*\*/1. **先看原始碼**/' scripts/templates/graph-discipline.md
python3 -c "
txt = open('scripts/templates/graph-discipline.md', encoding='utf-8').read()
txt = txt.rstrip('\n') + '\n\n<!-- 不是真的指令,只是為了不要忘記以前的說法:先讀程式碼 -->\n'
open('scripts/templates/graph-discipline.md', 'w', encoding='utf-8').write(txt)
"
python3 scripts/test_lumos.py -k entry_points_agree
```
輸出 **9 passed, 0 failed**——連「entry_points_agree: 範本仍是程式碼為主定位」那條新斷言都是綠的,即使〈怎麼用〉第一步實際上已經改成「先看原始碼」,規範只是被我塞進一行沒人會讀的 HTML 註解裡。

對照組(只改步驟一,不補註解)會正確翻紅:
```
✗ entry_points_agree: 範本仍是程式碼為主定位  範本的〈怎麼用〉第 1 步不再寫「先讀程式碼」…
8 passed, 1 failed
```
但只要多加一行看不見的註解就能讓它閉嘴。這支守衛跟 `t_note_convention_synced_to_skill` 是同一批、同一天折入,後者已經因為同樣的「HTML 註解藏字」被抓到過一次並修好,前者卻沒套用同一個教訓——兩支「防漂移」守衛裡,一支學會了去註解化,另一支沒學到,而且兩支檢查的是同一份範本檔案。

（收工已 `cp /tmp/tpl_backup.md scripts/templates/graph-discipline.md` 還原,`git diff --stat` 確認乾淨、`-k entry_points_agree` 重跑為 9 passed, 0 failed。）

## F3 RULE 的 [retire:] 欄位遇到內容含右中括號(典型情況:退場條件引用 `[[wikilink]]`)會被靜默截斷,截斷後仍判定「欄位齊全」而拿到挑戰程式碼的權力
severity: major
blocking: yes

引句:「_RULE_FIELD_RE = re.compile(r"\[(since|until|confirmed|status|retire|applies):([^\]]*)\]")」

`[^\]]*` 一路吃到「第一個」`]` 就停。本 repo 的退場條件常常需要指回另一篇節點(`RETIRE-IF:`/`decisions:` 的既有慣例都用 `[[節點]]` 這種雙中括號),但只要 `[retire:...]` 裡面出現任何一個 `]`(最常見就是 `[[Systems/X]]` 裡的收尾括號),欄位值就會在第一個 `]` 處被腰斬,後面的文字變成裸露在外的雜訊,**而且 `rule_lifecycle_warnings` 完全看不出異狀,因為截斷後的字串仍然非空,通過 `not f.get("retire")` 的檢查**。

重現:
```python
import importlib.machinery, importlib.util, sys
loader = importlib.machinery.SourceFileLoader('lumos', 'scripts/lumos')
spec = importlib.util.spec_from_loader('lumos', loader)
lumos = importlib.util.module_from_spec(spec); sys.modules['lumos'] = lumos
loader.exec_module(lumos)

line = 'RULE:[since:2026-09-21][retire:參照 [[Systems/固定席扇出降權]] 決策撤銷後撤]大額退費要人工核可'
rest = line[len('RULE:'):]
print(lumos.parse_rule_fields(rest))
print(lumos.rule_lifecycle_warnings(rest))
print(lumos.context_marker_warnings(line))
```
輸出:
```
{'since': '2026-09-21', 'retire': '參照 [[Systems/固定席扇出降權'}
[]
[]
```
`retire` 實際存到的內容是斷頭的 `參照 [[Systems/固定席扇出降權`(少了收尾的 `]]` 和後面「決策撤銷後撤」這句真正的退場條件),但 `lint` 零警告,判定這條 RULE 欄位齊全。依這批修法自己定的新規則(AGENTS.md/CLAUDE.md 第 3 條:「寫齊出處、有效期與退場條件的 `RULE:` 行」才能挑戰程式碼),這條退場條件其實沒寫齊、甚至可以說是壞掉的,卻照樣拿到跟「真的寫齊」一樣的裁決權——這正是派工詞點名要查的「`[retire:]` 內容含 `]`」,而且後果不是「格式醜」,是「機制本身用來把關授權的那個欄位被靜默吃掉一截」。

## F4 同一摘要行塞進兩條 RULE: 時,`[since:]`/`[retire:]` 用「後蓋前」合併,沒填欄位的那條會借用旁邊完整的欄位而被判過關
severity: major
blocking: yes

引句:「return {m.group(1): m.group(2).strip() for m in _RULE_FIELD_RE.finditer(rest)}」

`context_marker_warnings` 是逐「行」處理(`SYMBOL_RE.match(line)` 用 `^` 錨點),但一行裡如果不小心(例如少打一個換行、合併衝突沒清乾淨)黏了兩條邏輯上獨立的 RULE 敘述,`parse_rule_fields` 是對整行 `finditer`,重複的 key 用字典推導式「取最後一個」,等於後面那條 RULE 的 `[since:]`/`[retire:]` 會蓋掉/借給前面那條。

重現:
```python
line = 'RULE:舊限制沒填欄位 是否還算數不知道 RULE:[since:2026-09-21][retire:新閘上線後撤]新限制'
rest = line[len('RULE:'):]
print(lumos.parse_rule_fields(rest))   # {'since': '2026-09-21', 'retire': '新閘上線後撤'}
print(lumos.rule_lifecycle_warnings(rest))   # []
```
「舊限制沒填欄位 是否還算數不知道」——這句話本身就承認自己沒有把握,照理該被「缺 [since:]/[retire:]」擋下來要求補欄位,結果因為後面剛好緊接著一條欄位齊全的新 RULE,兩者的欄位被合併成一份,lint 判定零警告、視為齊全。這不是「風格問題」:合併後的假象直接關係到這批修法新賦予 RULE 的裁決權——一條連作者自己都不確定還算不算數的規則,靠著跟別的規則擠在同一行,拿到了「可以挑戰程式碼」的資格。

## F5 WHY: 的「出處」偵測正則,對任意 ≥7 位數字會誤判為有出處(漏報),對純「對話」出處(表格明文允許的三種之一)會誤判為缺出處(誤報)
severity: minor
blocking: no

引句:「出處（提交／決策編號／對話）」

分類表白紙黑字寫 WHY: 的出處可以是「提交／決策編號／對話」三選一,但 `_CTX_SRC_RE`(`scripts/lumos:2767`)只認 ISO 日期、`#d\d+`、`[[`、裸 `d\d+`、或 7–40 碼的 `[0-9a-f]` 十六進位字串,完全沒有「對話」這個管道的等價判準。

重現(誤報:合法的「對話」出處被打回票):
```python
print(lumos.context_marker_warnings('WHY:跟 Enzo 口頭討論後決定砍掉這個功能'))
# ['脈絡標記『WHY:』缺出處——行內補一個日期、決策編號(#d3)、提交 sha 或 [[節點]],…']
```
重現(漏報:任何 ≥7 位數字,不管是不是提交 sha,都會被當成「有出處」放行,因為 `[0-9a-f]{7,40}` 這個字元類本身就包含全部 0–9):
```python
print(lumos.context_marker_warnings('WHY:因為預算有 1234567 元所以砍掉這個功能'))   # []
print(lumos.context_marker_warnings('WHY:因為使用者投訴電話 0912345678 打來抱怨'))   # []
```
兩個方向都不會擋任何東西(lint 只警告),但這條規則存在的目的就是「逼人留下可查證的出處」,現在它既會冤枉照著文件寫「跟誰討論過」的人,又會被一個剛好 7 位數以上的無關數字唬過去——對「會不會誤報或漏報」這題,答案是兩者都會。

## F6 探針題目新加的 `note` 欄位,`scripts/scenario_probe.py` 完全不讀,純粹是人看的註解
severity: minor
blocking: no

引句:「換成現在真的存在的常數。挑目標的條件:①現在真的存在」

`governance/scenarios/discipline.jsonl` 的 d01 這行加了 `"note": "2026-09-21 換目標:…"`。查過 `scripts/scenario_probe.py` 全檔,讀取 scenario 欄位只用到 `id` / `prompt` / `expect` / `forbid_before` / `cat` / `answer_expect`,沒有任何地方 `.get("note")` 或引用這個 key——它不影響判分、不影響是否被選中執行,單純是給人看的沿革記錄,格式驗證(`sc.get("id")`/`sc.get("prompt")`/`sc.get("expect")` 那段,`scripts/scenario_probe.py:224-228`)也不會因為多了這個 key 而拒絕。這符合派工詞背景段自己講的「換掉一題腐爛的探針題目」的性質(只是加註解,不是加邏輯),但既然派工詞明確問「note 欄位是不是探針程式認得的欄位」,机械查證的結論就是:**不是**,它是死欄位,如果以後有人以為改這個欄位能影響判分或篩選,會是誤解。

新題本身的兩個事實我也核過:`governance/autonomous_loop/replay_weekly.py:22` 確實有 `FULL_SWEEP_SECONDS = 180`,且在 `:145` 真的用來判斷「單包耗時×存量是否 ≤ 這個門檻就全跑」,改了會動到行為;`docs/lumos-toolchain-knowledge/Systems/autonomous-iteration-loop.md` 確實提到這支檔和這個常數,滿足「它的家有筆記在講它」。舊題引用的 `sync_nudge` 也核過:`scripts/hooks/pre-commit` 裡確實已經沒有這個名字,`scripts/hooks/pre-push:40` 留了一句「2026-09-11 起同步點名改由每支檔有家照家算,不再讀這一份」佐證舊題目已腐爛的說法。這部分背景陳述查證屬實,不是這次要折的問題。

## F7 舊版 RULE 判準用的兩個正則(`_CTX_DATE_RE`/`_CTX_RETIRE_RE`)欄位化之後變成死碼,留著容易讓人誤以為 RULE 還在用「日期字樣+退場字樣」判斷
severity: minor
blocking: no

引句:「_CTX_RETIRE_RE = re.compile(r"退場|撤掉|失效|RETIRE-IF")」

`grep -n "_CTX_RETIRE_RE\|_CTX_DATE_RE" scripts/lumos scripts/test_lumos.py` 只各命中一次(定義那一行),沒有任何函式呼叫它們——`context_marker_warnings` 對 `RULE` 前綴已經改成整段走 `rule_lifecycle_warnings`(欄位式),不再落到 `_CONTEXT_MARKER_RULES` 那個通用字典、也就用不到這兩個舊正則。這不影響任何行為(死碼不會被執行),但下一個接手的人如果照著這段附近的註解(`# 之前不在表內…`)去讀,可能會誤以為 RULE 的舊判準(日期字樣+退場字樣)還跟欄位判準並存、彼此互補,實際上舊判準已經完全沒人呼叫。建議收尾時順手刪掉,或至少留一句「已由 rule_lifecycle_warnings 取代,不再使用」的註記。

---

## 驗過但沒發現問題的路徑
- `rule_lifecycle_warnings` 的空值 / 重複欄位:`[since:][retire:]`(空字串)、`[since:2020][since:2026-09-21]`(重複取最後一個)都如預期被判定或正確合併,沒有崩潰或誤判。
- `_rule_date` 對非法日期格式(`2026/09/21`)正確報「不是合法日期」,不會拋例外中斷 lint。
- 極長字串(10 萬字元塞進 `[retire:]`)沒有 ReDoS 或效能問題,微秒級跑完。
- `date.today()` 沒有做時區處理,但這是全庫既有慣例(`grep -n "date.today()" scripts/lumos` 命中十幾處,都沒有時區參數),不是這批新增的問題,不單獨列為發現。
- 「決策裁決權」層級的新舊落差:比對 `decisions:` 欄位本身(`cmd_decision_add`,`scripts/lumos:13330`)也只是「有填就寫、沒填就不寫」,沒有機械檢查 alternatives≥2 / trade_offs 是否真的寫了——跟這次給 RULE 的欄位式弱把關屬於同一等級,不是這批修法新引入的落差。
- AGENTS.md 與 CLAUDE.md 兩份文件的第 3 條、分類表、鐵則六改動逐字比對一致,沒有發現兩份文件之間的新分岔。
- 真實出貨的兩篇節點(`Systems/codex-harness.md`、`Systems/lumos-cli-read.md`)與新節點(`Projects/按需檢索_計劃.md`)實際跑 `lumos lint` 都是 0 問題,新規則沒有誤傷這批自己新寫的內容。
- `t_lint_context_marker_requirements`、`t_rule_lifecycle_fields`、`t_note_convention_synced_to_skill`、`t_entry_points_agree_with_code_first` 四支測試在乾淨 checkout 上實跑全線,結果與程式碼行為一致(20 顆斷言全綠)。
