severity: blocker

## F1 claim 含換行字元會打斷 summary 的 YAML block-scalar,讓既有已審計的真合約整段從圖譜消失

severity: blocker
blocking: yes

`cmd_guard_plan` 把使用者傳入的 `claim`(一句話合約,positional 參數)未做任何換行檢查就直接塞進插入行:

引句:「marker = f"  KEY:{PLANNED_MARK} {claim.strip()} [watch:{gref}] [due:{due.strip()}]"」

`claim.strip()` 只去頭尾空白,不會去掉字串中間的 `\n`。這行字串之後被整條塞進 `new_lines = lines[:ins] + [marker] + lines[ins:]`,寫檔時 `marker` 內含的真實換行符會變成檔案裡多一條物理行,但這條新增出來的物理行**沒有** `summary: |-` block-scalar 要求的兩格縮排。

**重現(在 /tmp 臨時 vault 跑,唯讀不動正式 repo)**:
先建一篇已經有「真合約」的功能節點:
```
Systems/Widget6.md:
summary: |-
  KEY:★INVARIANT★ 既有的真合約不能消失 [test:t_existing_real] [audit:sonnet/2026-09-01]
  FLOW:p→q
```
再對它 `guard plan` 一條 claim 用 `$'新預告第一行\n新預告第二行(含換行)'`(bash ANSI-C 換行字面量,argparse 完全接受,不需要引號逃逸)。跑完之後 `Systems/Widget6.md` 實際內容變成:
```
 5	summary: |-
 6	  KEY:★INVARIANT-PLANNED★ 新預告第一行
 7	新預告第二行(含換行) [watch:Verification/2026-09-22_新預告第一行-新預告第二行-含換行] [due:2099-12-31]
 8	  KEY:★INVARIANT★ 既有的真合約不能消失 [test:t_existing_real] [audit:sonnet/2026-09-01]
 9	  FLOW:p→q
```
第 7 行沒有縮排,破壞了 block-scalar 的連續性。實測後果:
- `lumos context Systems/Widget6` 印出的 `summary:` 只剩一行 `KEY:★INVARIANT-PLANNED★ 新預告第一行`——第 8、9 行(含既有真合約、FLOW)全部從 parsed frontmatter 消失,連 `[due:]`/`[watch:]` 也一起不見(context 顯示「★預告★ 新預告第一行 — 沒寫最遲日期」,但其實 `--due 2099-12-31` 有給)。
- `lumos doctor --ci` 的 `[T]` 段(專門抓「標成不能破壞的合約但沒綁測試/沒獨立審計」)完全沒有提到 `Systems/Widget6.md`——它既不出現在「裸合約」也不出現在「未審計」名單裡,因為它已經不在 parser 讀出來的 `summary` 字串裡了。
- `lumos lint Systems/Widget6` 同樣看不到這條合約,不會抱怨它缺審計。

**為什麼是 bug 不是風格**:這套機制的核心賣點就是「合約標成 ★INVARIANT★ 就會被閘守住,不會被忘記」(CLAUDE.md、guard-kill 節點都在講這件事)。`guard plan` 是這批新增的公開指令,任何呼叫方(人手打、腳本產生、之後接 CI 自動預告)都可能傳入含換行的 claim(例如從別的系統貼過來的多行需求敘述、或程式串接時字串模板沒清乾淨)。目前完全沒有驗證擋這個輸入,而後果不是「這條新預告寫壞」這麼輕——是**插入點之後、原本已經生效且已審計的舊合約會整段從機械可見的圖譜裡消失,而且沒有任何錯誤訊息**。doctor 的 `[1.5/4]`(「沒收尾整篇會被當成正文」)也沒抓到這個案例,因為 frontmatter 本身仍然有頭有尾地閉合,只是 block-scalar 內部斷裂,不在它的判定範圍內。

file: `scripts/lumos:10606`(marker 組字串那行,對應 patch 內同一段)

---

## F2 同一功能節點預告多筆合約時,claim 前 12 字重複會讓 settle 誤配到別條、彼此互相覆蓋

severity: blocker
blocking: yes

`_guard_settle` 定位「要換成正式合約的那一行」用的是:

引句:「lines, idx, _e = _guard_planned_line(env, home_rel, claim[:12])」

而 `_guard_planned_line` 的比對邏輯是子字串包含,不是精確比對整行或比對 `[watch:{gref}]` 這個保證唯一的識別碼:

引句:「if PLANNED_RE.match(s) and claim_sub in s:」

由於只取 claim 前 12 個字元,當同一篇功能節點被預告了兩條「前 12 字相同、之後才分岔」的合約時,`claim_sub` 對兩行都會命中,而迴圈是 `for i in range(1, e)` 由上往下找**第一個**命中的行就回傳——新插入的行永遠排在最上面(`ins = summary 第一行之後`),所以後預告的那條會排在前面,先被找到。

**重現**:
```
lumos guard plan Systems/Pay "同一段開頭的合約敘述殊途A" --plan Projects/退款_計劃 --phase "Phase 1" --due 2099-12-31 --why 理由A --owner enzo
lumos guard plan Systems/Pay "同一段開頭的合約敘述殊途B" --plan Projects/退款_計劃 --phase "Phase 2" --due 2099-11-30 --why 理由B --owner alice
```
（"同一段開頭的合約敘述殊途" 這 12 個字兩條合約共用,只差最後一個 A/B 字)。此時 `Pay.md` 是:
```
  KEY:★INVARIANT-PLANNED★ 同一段開頭的合約敘述殊途B [watch:...B] [due:2099-11-30]
  KEY:★INVARIANT-PLANNED★ 同一段開頭的合約敘述殊途A [watch:...A] [due:2099-12-31]
```
接著 `lumos guard settle Verification/2026-09-22_同一段開頭的合約敘述殊途A --test t_contract_a`(轉正 A),實際結果:
```
  KEY:★INVARIANT★ 同一段開頭的合約敘述殊途A [test:t_contract_a]
  KEY:★INVARIANT-PLANNED★ 同一段開頭的合約敘述殊途A [watch:...A] [due:2099-12-31]
```
`settle A` 呼叫時傳入的 `claim_sub` 是 A 節點自己讀出來的 claim 前 12 字("同一段開頭的合約敘述殊途"),但迴圈由上而下第一個命中的卻是**B 的那一行**(因為 B 排在上面、也包含相同 12 字子字串),於是 `atomic_write_verify` 把 B 的預告行整條蓋成 A 的正式合約行。結果:
- B 的預告標記(含 `[watch:Verification/...B]`、`[due:2099-11-30]`)整條消失,`Pay.md` 裡再也看不到任何跟 B 有關的預告行——但 `Verification/2026-09-22_同一段開頭的合約敘述殊途B.md` 的 `status:` 仍然是 `pending`,`verified_by` 也仍指著它,doctor 的 S15 仍會照樣追蹤它逾期與否,但**人類透過 `lumos context Systems/Pay` 完全看不到「B 還沒做」這件事**——這正好打中這批設計文件自己強調的重點:「而且預告那一行就寫在節點裡……不必等到逾期被擋,也不必有人記得去翻守衛節點」,現在恰恰因為這個 bug 而失守。
- A 原本待轉正的那一行沒被動到,仍留在檔案裡,於是 `Pay.md` 同時出現「★INVARIANT★ A(已生效)」與「★INVARIANT-PLANNED★ A(還在預告)」兩行互相矛盾的敘述。

**為什麼是 bug 不是風格**:claim 前 12 字截斷 + 子字串包含比對,本來就不是可靠的唯一鍵;而系統其實已經有現成的唯一鍵可以用——`gref`(guard 節點自己的路徑,`[watch:{gref}]` 那段),`cmd_guard_plan` 建立守衛節點時已經做了同名擋(`if gpath.exists()`),保證每個 `gref` 全庫唯一。`settle`/`abandon` 卻繞過這個唯一鍵、改用不保證唯一的內容前綴去定位要改哪一行,才會在「同一功能節點預告多條」這個作者自己在鏡頭清單裡點名要測的情境下犯錯。

file: `scripts/lumos:10698-10699`(`_guard_planned_line` 的比對式)、`scripts/lumos:10736`(`cmd_guard_settle` 呼叫處)

---

## F3 claim 沒有做非空白驗證:純空白 claim 能建立成功,轉正永久卡死,棄置時又靜默留下無法清除的殘行

severity: blocker
blocking: yes

`cmd_guard_plan` 的必填檢查只涵蓋 `plan`/`phase`/`due`/`why`/`owner` 五個具名旗標,唯獨不驗 `claim` 本身:

引句:「missing = [(v, lbl) for v, lbl in ((plan, "計劃參照"), (phase, "階段"), (due, "最遲日期"),」

**重現**:`lumos guard plan Systems/Pay "   " --plan Projects/退款_計劃 --phase P1 --due 2099-12-31 --why 理由 --owner enzo`(claim 純空白)——指令**成功**(rc=0),建出 `Verification/2026-09-22_guard.md`(因為 `_guard_plan_slug` 對空字串 fallback 成 `"guard"`),`Pay.md` 多出一行:
```
  KEY:★INVARIANT-PLANNED★  [watch:Verification/2026-09-22_guard] [due:2099-12-31]
```
(合約敘述整段是空的,兩個空格之間什麼都沒有)。寫入自驗那段:
```
if "status: pending" not in _back or claim.strip() not in _back:
    raise RuntimeError("寫完讀回來對不上")
```
對空字串失效——`"" not in _back` 恆為 False,自驗永遠通過,不會攔下這個壞資料。

之後這個節點**永久卡死,兩條出路都壞**:
1. `settle`:`m = re.search(r"^預告的合約:(.+)$", body, re.M)` 要求冒號後至少一個字元,空 claim 的 body 是「預告的合約:」(冒號後面沒東西),`m` 為 `None` → `claim=""` → 直接擋下「讀不出預告的合約是哪一條」,永遠無法轉正。
2. `abandon`:雖然能簽核成功並把節點狀態改成 `abandoned`,但因為 `claim` 是空字串,清除家節點預告行那段被整段跳過且**不印任何警告**:

引句:「if home_rel and claim:」

實測 `lumos signoff ... --ref ...` 之後 `lumos guard abandon ...`,指令回報成功(`✓ 已棄置`,rc=0),但 `Pay.md` 裡那行空白預告 `KEY:★INVARIANT-PLANNED★  [watch:Verification/2026-09-22_guard] [due:2099-12-31]` 永久留著,沒有任何指令能清掉它——`abandon` 已經跑過且不會再跑第二次,而 `settle` 對這個空 claim 節點恆擋。

**為什麼是 bug 不是風格**:這批設計文件在〈誠實界線〉裡列了四條「刻意不補」的繞法(改日期/改 type/刪節點檔/偽造簽核),但**沒有一條提到「claim 給空白」**——這不是威脅模型裡「防忘記不防繞過」已經裁定要放棄的情境,是輸入驗證本身有缺口。而且它和文件反覆強調的原則矛盾:「防忘記的機制如果不告訴人怎麼解,就變成防做事」——這裡是反過來,程式完全不告訴人「你的 claim 是空的、這篇永遠卡死」,靜靜地製造一個誰都清不掉的孤兒資料。

file: `scripts/lumos:10559-10560`(missing 檢查未含 claim)、`scripts/lumos:10609-10610`(`_back` 自驗對空字串失效)、`scripts/lumos:10795`(abandon 靜默跳過)

---

## F4 guards 欄位被改指到另一篇存在的節點時,abandon 靜默成功、真正的家節點永久留著矛盾的預告行

severity: major
blocking: yes

`cmd_guard_abandon` 完全信任守衛節點自己 frontmatter 裡的 `guards` 欄位所指的家節點,拿它去找要清除的預告行,找不到就整段跳過、不印任何訊息(與 F3 共用同一段程式碼,但觸發方式不同,這裡示範探針⑦「guards 欄位被改成別篇」的情況):

引句:「home = _guard_home_of(n)」

**重現**:正常 `guard plan` 建出 `Systems/Widget3.md`(真正的家)與其守衛節點,再手改守衛節點 frontmatter 的 `guards: - Systems/Widget3` 改成 `guards: - Systems/Pay`(指向另一篇**存在**但完全不相干的節點)。接著 `signoff --ref` + `guard abandon`,指令回報成功(`✓ 已棄置`,rc=0),但:
- `Systems/Widget3.md`(真正曾經預告過這條合約的家節點)裡的 `KEY:★INVARIANT-PLANNED★ 第三號小工具合約 [watch:...] [due:...]` **原封不動留著**,因為程式跑去 `Systems/Pay.md` 找對應行,找不到(`lines is None`)就靜默放棄,不印警告。
- `Systems/Pay.md` 沒有被誤改(這點是對的),但 `Systems/Widget3.md` 從此永久顯示「這條合約還在預告中、還沒有測試在守」,而實際上守衛節點早已 `status: abandoned`——查 `Widget3` 的人會被誤導以為這條合約還活著、還要追蹤最遲日期,但其實已經沒人在管了。

**為什麼是 bug 不是風格**:計畫文件的〈誠實界線〉列的四條已知繞法裡,「把守衛節點的 type 改掉」有明講會怎樣(「連結還在,自檢不會叫」),但這裡討論的是 `guards` 欄位(不是 `type`)被改到**另一個真實存在的節點**——這不在已公開承認的四條繞法名單裡,而且和程式碼裡其他地方(例如 `cmd_guard_plan` 寫失敗時每一步都印 `⚠` 警告)的一貫作法不一致:同一支檔案在別處對「連結沒寫成功」都會警告,唯獨 `cmd_guard_abandon` 在「連結找不到對應行」時完全沉默。這會讓棄置動作看起來乾淨成功,實際上圖譜留下一則假訊息。

file: `scripts/lumos:10791-10802`(`cmd_guard_abandon` 找家節點與清行邏輯,無 else 分支)

---

## 已驗過、沒有問題的路徑(避免只報壞消息)

- 探針①部分:claim 含中括號、冒號(`"含 [中括號] 與冒號: 的合約"`)——plan/context/settle 全程正常,`DUE_REF_RE`/`WATCH_REF_RE` 沒被裡面的 `[中括號]` 誤觸發。
- 探針②「兩篇節點預告同一句完全相同的合約」——`gname` 用日期+slug 命名,第二次會撞檔名,正確擋下(`擋下:守衛節點 ... 已經存在,換一句話或改名再試`),不會靜默覆蓋。
- 探針③ 最遲日期 `2026-02-30`、`99999-1-1`——兩者都被 `datetime.date.fromisoformat` 的 `ValueError` 正確攔下(`擋下:最遲日期『...』不是 YYYY-MM-DD`),不會建出壞節點。
- 探針⑤ `--ref` 帶 `.md` 路徑(`--ref Verification/xxx.md`)——`_guard_signoff_refs` 有把 `.md` 去尾存進 set,`abandon` 比對時正確吃到,不受影響。
- 探針⑥ 功能節點完全沒有 `summary:` 欄位——`guard plan` 正確地不回滾、只印警告並保留已建好的守衛節點(`⚠ 守衛節點已建好(...),但功能節點沒有摘要區塊,標記沒寫進去`),行為與設計文件 S2 的敘述一致。
- 探針⑦「guards 指向不存在的節點」——`settle` 正確擋下(`擋下:守衛節點指名的功能節點 ... 找不到`);但「guards 指向存在但不相干的節點」這個變體會出問題,見 F4。
