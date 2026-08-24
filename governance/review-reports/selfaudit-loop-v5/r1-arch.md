# selfaudit-loop-v5 r1 架構對齊審查

角色:只判「跟本 repo 既有做法一不一樣」,不判設計對不對、也不重審 v1-v4 已經吵過的內容。
範圍:被審 `/tmp/selfaudit-loop-v5-r1.md`(即 `docs/lumos-toolchain-knowledge/Projects/自足性審計閉環_計劃.md`,兩者內容逐行相同,172 行),
只看 v5 delta 五項——容器統一/回寫柵欄/query 出口/週帳判別鍵/PASS commit。三問各自的對照物列在下面段落開頭。

---

## 問一:隔離容器怎麼建、回寫前怎麼比

**對照物①:`make_sandbox` 的既有用法慣例。**
`scripts/scenario_probe.py:80-110` 定義 `make_sandbox`,而它唯一的既有呼叫者 `main()` 只在整批情境開跑前呼叫**一次**
(`scripts/scenario_probe.py:210` `work = make_sandbox(src)`),之後每個情境跑完用 `git checkout -q -- .` + `git clean -qfdx`
把同一個沙盒**復位**,不重建(`scripts/scenario_probe.py:228-229`)——貴的 `rsync` 全樹複製只付一次,情境之間用便宜的 git 復位攤提。
v5 的寫法是「每輪都重建」:`每輪 make_sandbox(repo) 建沙盒(rsync 現況+commit=派工快照;三層拆彈)`(spec:65)。
這跟既有慣例的「建一次、復位很多次」不是同一個用法模式——不過 spec 自己把理由寫在同一行:「rsync 現況」是要把
派工當下的主樹狀態**當場拍照**,這張照片正是後面回寫柵欄要拿來比對雜湊的基準,復位沿用舊沙盒做不到「重新對齊主樹現況」這件事。
既有慣例服務的是「情境之間互不干擾」,v5 服務的是「每輪都要一張新鮮快照」,兩者目的不同。頻率上 N=2/週,每週兩次全樹 rsync,
量體不大。判定:用法上確實跟既有呼叫者不同,但 spec 有把理由寫出來,不算典型的「抄了別人零件卻沒抄對用法」——標 ⚠。

引句:「每輪 `make_sandbox(repo)` 建沙盒(rsync 現況+commit=派工快照;三層拆彈)」

**同一段的另一個問題(直接在容器統一這條 delta 裡自相矛盾)**:§架構明講「worktree 全退場」——
「★隔離容器統一=探針沙盒(make_sandbox,三層拆彈)★——worktree 全退場」(spec:55)。
但 PRIOR-ART 段落(spec:103)仍寫「修復隔離=`git worktree`(pin_snapshot 先例)」,把已經死刑的 worktree
留在「本案抄的先例」清單裡,跟三行前才殺掉的架構決定直接打架。這不是「跟別的地方不一樣」,是**同一篇筆記自己內部前後不一致**、
而且剛好落在本次審的容器統一這條 delta 正中央,屬於 major。

引句:「修復隔離=`git worktree`(pin_snapshot 先例)」

**對照物②:回寫「比對 sha 再 copy」有沒有既有同構。**
有,而且對得很準。`about_code_stamp` 的過期守衛就是同一招:`note_body_hash`(`scripts/lumos:7700-7713`)算正文
`sha256` 前 12 碼,`about_code_expired`(`scripts/lumos:7736-7740`)拿「現在雜湊」跟「標記當時存的雜湊」比對,
不等就判過期、**不信這個標記**——跟 v5 回寫柵欄「copy 回主樹前比對『主樹該篇現況 sha256 == 派工快照 sha』——
不等=主樹已變,放棄回寫」(spec:76-77)是同一個精神:雜湊不等 = 保守、不信任、不覆蓋。這條是對齊的,不計入不對齊。

---

## 問二:對外介面長什麼樣——query 出口 + 週帳判別鍵

**對照物③:`lumos query` 的旗標家族(--tag/--active/--linked)加 `--self-audit-due` 合不合形。**
`cmd_query` 的自我定位很清楚:「結構化查詢:WHERE over 標籤家族(旗標一律 AND 疊加,不發明查詢語言)」
(`scripts/lumos:6651`),`query` 子指令本身沒有 positional(`scripts/lumos:15563-15575`,對照 `set`/`append`
在 `scripts/lumos:15589-15596` 都有 `p.add_argument("note")`)。spec 說「query 無 positional、旗標切模式是它的既有
形狀」(spec:62)——這句話本身是對的,查過了確實如此。
但 `query` 家族還有一條沒寫進 spec 的隱性合約:**不管疊幾層旗標,輸出永遠是同一個投影**——`cmd_query` 收斂到
`hits.append((rel, st, sorted(...)))`(`scripts/lumos:6686`),JSON 輸出固定是
`{"results": [{"node", "status", "tags"}], "hidden_superseded"}`(`scripts/lumos:6690-6692`)。
`--active`/`--contract` 都只改「篩選哪些列」,不改「印出哪些欄」。
v5 的 `--self-audit-due` 卻宣告了一組全新的欄:「輸出欄:rel/stem/repo_rel」(spec:64)——沒有 `status`、沒有
`tags`,連欄名都換了(`node`→`rel`)。這等於在同一個子指令裡塞了第二種輸出投影,跟「同名多動作僅巢狀與動詞兩慣例,
都不合,故換家族」(spec:63)那句話想避開的問題(一個名字底下藏兩種動作)其實只是把界線從「子指令層」挪到了
「輸出投影層」,本質沒解決。任何假設 `query --json` 一定回 node/status/tags 的既有消費者(或未來寫的消費者)
碰到 `--self-audit-due` 會直接對不上格式。判 major。

引句:「輸出欄:rel/stem/repo_rel」

**對照物④:jsonl 判別鍵(`governance-log` 的 `gate`+`kind`)對不對得上。**
`docs/.governance-log.jsonl:1-3` 的每一行都是 `{"gate": "...", "kind": "...", ...}`——`gate` 定「哪個機制」,
`kind` 在同一個 `gate` 底下再分事件種類(例:`gate=check-s` 底下 `kind=warned`)。v5 週帳 schema
`{"week","stem","kind","ts"}`,`kind∈{done,fail,abort,stale,nag}`(spec:82)——因為整個檔案本來就只服務
selfaudit 這一個機制,不需要 `gate` 欄,`kind` 拿來分事件種類的用法跟 `governance-log` 精神上是同一招,這部分算對齊。
但 spec 的 PRIOR-ART 段落寫的引用是另一個檔:「週帳=append-only jsonl(covered.jsonl 同形,非 run_nags 單值戳)」
(spec:103)。查了 `governance/covered.jsonl:1-5`,每行只有 `{"weakness": "..."}` 一個欄位,完全沒有判別鍵、
沒有 `ts`、也不是多種事件類型共存一檔——跟 v5 「一檔五種 kind」的結構其實不同形。真正同形的先例是
`governance-log.jsonl` 的 `gate`+`kind`,而 spec 沒有引用它,反而引了一個結構對不上的檔案當先例。
設計本身沒問題,但先例引用引錯了對象,判 minor。

引句:「週帳=append-only jsonl(covered.jsonl 同形,非 run_nags 單值戳)」

---

## 問三:落地怎麼收——PASS commit 的先例 + 兩篇事故 Issue 的引用寫法

**對照物⑤:PASS commit 單行訊息 vs repo 唯一活著的自動 commit 先例(有嗎?)。**
查了全 repo(`scripts/`、`governance/`,排除 test 檔與 hook 檔名裡的 `pre-commit`/`post-commit` 字面比對雜訊),
唯一會真的下 `git commit` 的程式碼路徑是 `governance/autonomous-loop.sh:380`
(`git commit -m "auto-spec: $TOPIC(...)"`),但這條路徑掛在非 dry-run 分支底下,而非 dry-run 早在
`governance/autonomous-loop.sh:8` 和 `:12` 就被整段擋死:「非 dry-run 停用(2026-07-29 使用者裁定,Codex 外審
採納)」。也就是說 repo 裡**沒有活著的自動 commit 先例**——唯一一段是死碼。這件事 spec 自己也已經在 r3 修正過:
「commit 格式=單行訊息含三 model,★本案自定並測試釘——v4『照既有自動 commit 格式』引的是 07-29 起停用的死碼,
聲稱刪除(s2f6/arch)」(spec:73)。這句話查證後是準確的,自定格式、不假裝借了不存在的先例,是對的處理方式,
不計入不對齊。

**對照物⑥:兩篇事故 Issue 的引用寫法合不合圖譜慣例。**
用 `[[Issues/X]]:摘要` 這種行內 wikilink 引證本身沒問題——`scripts/lumos:13987` 明確把 `body-wikilink` 列為和
`related`/`verified_by`/`plan_refs` 並列的合法邊型,不需要額外進 `related:` frontmatter 才算數(spec 的
`related:` 只列了 `Systems/autonomous-iteration-loop`,spec:13-14,兩篇 Issue 都沒進去,這點不算違規)。
問題出在引用內容本身兌不兌得上來源:

- `[[Issues/同工作區多session並行改動]]`(`docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md`)
  正文寫的是「有症狀(**三次,兩次有實害**)」(該檔:61,事件列表本身在 :20-48 也是三例中第三例「結果是好的」)。
  spec 引成「同日**三次實害**的開放事故」(spec:77-78),把「三次事件、兩次有害」壓縮成「三次都有害」,
  跟來源對不上。判 minor(用詞誇大,不影響設計本身)。

引句:「同日三次實害的開放事故」

- `[[Issues/探針沙盒能推到真遠端]]`(`docs/lumos-toolchain-knowledge/Issues/探針沙盒能推到真遠端.md`)
  的「誠實缺口」明寫重驗條件是:「★重驗條件:**下次探針題**有『對外送東西』的情境,先確認 gh auth 在沙盒內是否
  可用。★」(該檔:48-49)——這條件鎖定的是 `scenario_probe.py` 自己**下一次新增的情境題**,要去驗 gh auth 會不會
  在沙盒裡外洩。spec 卻寫「該 Issue 的重驗條件由本案首跑兌現」(spec:103),但本案的做法是「本案 agent 無網路
  需求,派工 prompt 明禁對外」(同行)——也就是**主動避開**去觸碰 gh/curl,而不是去驗證 gh auth 到底可不可用。
  避開風險跟驗證風險是兩件事,不是同一件事被做掉了。這條 Issue 的重驗條件既沒有被本案的射程涵蓋(本案不是探針題),
  也沒有被本案的做法實際檢驗(本案刻意不去戳這個路徑)。宣稱「兌現」查證後站不住,判 major。

引句:「該 Issue 的重驗條件由本案首跑兌現」

---

## 不對齊清單

| # | 位置(spec) | 對照物 | 嚴重度 |
|---|---|---|---|
| 1 | spec:65 | make_sandbox 每輪重建 vs probe 建一次+checkout/clean 復位 | minor ⚠ |
| 2 | spec:103 vs spec:55 | PRIOR-ART 仍留「修復隔離=git worktree」,跟同篇「worktree 全退場」自相矛盾 | major |
| 3 | spec:64 | `--self-audit-due` 換了 query 家族固定的輸出投影(node/status/tags → rel/stem/repo_rel) | major |
| 4 | spec:103 | PRIOR-ART 引「covered.jsonl 同形」不準確,真正同形的判別鍵先例是 governance-log 的 gate+kind,未引 | minor |
| 5 | spec:77-78 | 引 [[Issues/同工作區多session並行改動]] 把「三次,兩次有實害」誇大成「三次實害」 | minor |
| 6 | spec:103 | 宣稱 [[Issues/探針沙盒能推到真遠端]] 的重驗條件「由本案首跑兌現」,但本案既非該條件鎖定的射程、也刻意迴避而非驗證 | major |

**不對齊共 6 條,其中 major 3 條。**
