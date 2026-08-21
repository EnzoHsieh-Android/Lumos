# r2 S1 generalist 審查報告

審查對象:/tmp/檢核收緊五件-r2.md(v2,122 行)。範圍:全文一般性掃描——未定義詞、S1-S3 改寫段與保留段(緣起/PRIOR-ART/範圍刀/實務隱患/未決)之間的矛盾、無法落地的空隙、無 code 佐證的宣稱。

---

## finding 1(blocker)——S3 重用的 tier 判定機制是 fail-open,與「fail-closed」設計目標直接矛盾

引句:「pass 內自跑 `pitfalls --diff <range>` 判 tier,range 取 merge-base..HEAD,同 pre-push」

哪裡錯:S3 整節的標題與定位是「外家 fail-closed 綁在放行點」(第 68 行),核心賣點是把 fail-closed 判定釘死在真正擋 push 的 `code-loop pass`。但這句話講的 tier 判定機制,就是 `_codeloop_guard_verdict()` 目前已在用的同一條路(`pitfalls --diff ... --json` 取 `tier`)。這條路的既有行為在 code 裡白紙黑字寫死是 **fail-open**:

```
scripts/lumos:14052:    fail-open:pitfalls 出錯 / 非 git / 無 merge-base → tier 視作非 high(不 blocked)。
```

也就是說,只要 `pitfalls --diff` 那次呼叫失敗(逾時、非 git、無 merge-base、JSON 解析失敗——`_codeloop_guard_verdict` 第 14075-14085 行逐一 catch 並回傳 `tier: unknown`/`standard`),tier 就不會判成 `high`,S3 「tier=high 時必帶 `--loop` 或 `--no-loop`」的整條規則根本不會被觸發——外家 fail-closed 檢查被**靜默繞過**,而且沒有任何逃生門留痕(不是 waiver,是完全沒進判定式)。這與「fail-closed 的本意」(第 75 行原文自己講的)正面衝突:一個宣稱 fail-closed 的機制,其唯一的 tier 判準入口是 fail-open 的。文件全篇沒有一處提到這個既有 fail-open 行為,也沒有設計因應(例如 pitfalls 失敗時該 fail-closed 而非視為非 high)。

file:line:`scripts/lumos:14046-14085`(`_codeloop_guard_verdict`,尤其 14052/14075-14085);文件第 68、71 行。

正確做法:S3 若要真正 fail-closed,必須明講「pitfalls 判 tier 失敗時的行為」——至少要把「無法判定 tier」與「tier=high」同樣視為需要 `--loop`/`--no-loop` 的情況(即 tier 判定也要 fail-closed),否則整個 S3 機制存在一個文件未承認、code 已證實存在的繞過路徑。

---

## finding 2(blocker)——S2 棘輪要求鍵「非 stem」,但目前寫帳的全部 7 道 warned gate 都只寫 stem,不寫相對路徑

引句:「鍵=(gate, **節點相對路徑**,非 stem;r1 s2-F2)」

哪裡錯:S2 這句話是 r1 s2-F2 的修正結果,意在避免「同 stem 不同資料夾互撞」(對應測試 `t_ratchet_key_is_relpath`,第 98 行)。但棘輪讀的輸入是 `docs/.governance-log.jsonl` 裡既有的 `warned` 事件(第 60 行:「輸入:...中 `hard=false ∧ kind=warned` 的事件」),而目前**全部** 7 道會寫 `warned` 事件的既有 gate(check-r/check-s/check-e1/check-e2/check-e3/check-k/L3——與文件自己講的「現 7 道」數字一致)在寫入時一律只寫 `n.stem`,從未寫相對路徑:

```
scripts/lumos:792:  gov_events.append({"gate": "check-r", "kind": "warned", "hard": False, "nodes": [nnote.stem]})
scripts/lumos:819:  gov_events.append({"gate": "check-s", "kind": "warned", "hard": False, "nodes": [n.stem]})
scripts/lumos:825:  gov_events.append({"gate": "check-s", "kind": "warned", "hard": False, "nodes": [n.stem]})
scripts/lumos:866:  gov_events.append({"gate": "check-e1", "kind": "warned", "hard": False, "nodes": [n.stem]})
scripts/lumos:948-949: gov_events.append({"gate": "check-e2", "kind": "warned", "hard": False, "nodes": [notes[arel].stem]})
scripts/lumos:989:  gov_events.append({"gate": "check-e3", "kind": "warned", "hard": False, "nodes": [n.stem]})
scripts/lumos:1030: gov_events.append({"gate": "check-k", "kind": "warned", "hard": False, "nodes": [n.stem]})
scripts/lumos:2990: "nodes": [stem(d.get("verification", ""))]   # L3
```

也就是說,r1 s2-F2 只修到「棘輪聚合器自己怎麼算鍵」這一層,但它讀的原始資料(`nodes` 欄)在寫入端根本沒有相對路徑可用——只有 stem。「同 stem 不同資料夾不互撞」這個 r1 認定的 blocker,在資料源頭仍未解決:兩個不同資料夾但同 stem 的節點,寫進治理帳的 `nodes` 值本來就是同一個字串,棘輪不管怎麼「以相對路徑為鍵」都聚合不出兩個不同的鍵,因為輸入資料裡兩者本就無法區分。文件的「範圍刀」(第 79-83 行)明講「不改 `_TIER_ROSTER` 內容;不改 pre-push;不改 loop status 判定式」,但完全沒提「要不要改這 7 個既有 warned 事件的寫入」,也沒有任何測試涵蓋寫入端。測試 13 `t_ratchet_key_is_relpath` 極可能是直接餵合成的 `nodes: [rel]` 資料進棘輪聚合函式測,測得過但不反映真實整合行為——這是「測著假裝的輸入」。

file:line:`scripts/lumos:792,819,825,866,948-949,989,1030,2990`;文件第 60-62 行。

正確做法:要嘛明講這 7 個既有 gate 的 `nodes` 欄要同步改成寫 `rel`(並補對應漂移測試釘死格式),要嘛承認棘輪鍵目前仍等同 stem-based、r1 s2-F2 並未真正解決,退回原判準或另案處理既有 gate 的寫入面。

---

## finding 3(major)——S3 用「canary-log 依 ts 排序」推導輪序,與既有 codebase 明文的「讀 append 序、不 ts-sort」慣例矛盾

引句:「輪序取 `canary-log` 同 loop 各 round 首筆 ts 排序」

哪裡錯:同一份 `.canary-log.jsonl` 在既有 `cmd_loop_status`(消費同一檔案、判斷同一種「輪」語意)的 docstring 裡明講理由拒絕 ts 排序:

```
scripts/lumos:4324:  讀 .canary-log.jsonl 的 **append 序**(不 ts-sort:ts 只到秒、同秒會並列),篩 loop==id。
```

另一處(rel-cascade 帳本)也重申同一慣例:

```
scripts/lumos:7608:  canary-log 慣例:讀 append 序、不 ts-sort);torn 行(壞 JSON)=未提交,跳過。
```

理由很具體:ts 只到秒級精度,同一秒內的多筆記錄(panel 模式下 W 個審計席「同一輪」常常在同一秒內各自寫入)排序後會並列/不確定,所以整個 codebase 對這份檔案的既定慣例是「不 ts-sort,只信 append 序」。S3 卻反其道而行,把「輪序」的判定基礎明確定義成「依 canary-log 首筆 ts 排序」——這正是 codebase 已知會出問題的排序方式,而且用在一個會決定「取最後 min(K=2,輪數)輪」→「該輪 external 席數夠不夠」→「放行 push 與否」的硬閘判定上。若兩輪在同一秒內都有記錄(panel 模式常見),ts 排序無法穩定分出先後,S3 判定式讀到的「最後 K 輪」可能與實際輪序不一致,導致該過的擋、該擋的過。

`standard` 檔那句「`loop next` 印「外家連續 N 輪缺席」(跨 loop,依 canary-log ts)」(第 76 行)是同一問題的第二個實例——同一份日誌、同一個已知有並列風險的排序基礎,拿來做跨 loop 連續缺席的計數。

file:line:`scripts/lumos:4324,7608`;文件第 72、76 行。

正確做法:比照既有慣例改用 append 序(或明講為何這裡跟既有慣例不同、且說明同秒並列時的 tie-break 規則),否則這是把已知會踩雷的排序法重新引進一個新的硬閘。

---

## finding 4(major)——S3 要求 `loop next` 寫治理帳事件,違反該指令自己文件化的「唯讀指針」契約,且無去重機制

引句:「`loop next` 印「外家連續 N 輪缺席」(跨 loop,依 canary-log ts),N≥3 印」

哪裡錯:`loop next` 現有 docstring 與 help 文字明講它是**唯讀**:

```
scripts/lumos:4783:  """M1包 #1(loop機械脊椎M1包_計劃):帳本吐唯一下一動作。唯讀指針——lumos 不 spawn agent,
scripts/lumos:14319:  ln = lsub.add_parser("next", help="M1包 機械脊椎:帳本吐唯一下一動作(...);唯讀指針,不 spawn agent")
```

「唯讀指針」不只是命名——這是自主迭代 loop(每天自動選 gap→brainstorm→design-loop)之類編排者會頻繁、機械式呼叫的查詢點,呼叫方合理假設它沒有副作用。S3 卻要求它在 N≥3 時「寫 `gate: external-absent, nodes:[<loop-id>]`」——這是一次真正的寫入副作用,直接打破「唯讀」這個既有契約。而且文件沒有講任何去重/節流邏輯:如果一個外家缺席已連續 5 輪、`loop next` 在這 5 輪期間被呼叫多次(编排者每輪至少呼叫一次是常態用法),會不會每次呼叫都各寫一筆 `external-absent`?文件的退場條件與治理帳兩節都強調「三件的分子分母全部是已寫帳...的 gate,`gov --stats` 現有欄位即可印」(第 93 行)——如果 `external-absent` 因重複呼叫而膨脹計數,這個「可信賴的分母」本身就失真,而這正是文件自己在批判 v1 五件時最在意的「檢核越來越寬鬆/數字失真」問題。

file:line:`scripts/lumos:4783,14319`;文件第 76 行。

正確做法:要嘛把寫帳動作移到一個明確有副作用語意的指令(而不是動既有的「唯讀指針」),要嘛在 `loop next` 補上明確的去重鍵(例如同一 streak 只在首次跨過 N≥3 時寫一筆)並同步更新其「唯讀」的文件化定位。

---

## finding 5(minor)——「## 未決」標題在文件裡重複出現兩次,內容部分重疊卻不一致,保留段被 v2 編輯過程弄亂

引句:「S2 N=20 run 仍是拍的;上線後以 `ratchet`/`ratchet-ack` 筆數回看。」

哪裡錯:這句話出現在第 107-111 行的「## 未決」段(2 條:S2 N=20、S3 外家家族計算)。但文件在「## 審計修正紀錄」之後(第 118-122 行)又出現第二個一字不差同名的「## 未決」標題,內容是另外 3 條(S2 門檻/ack 窗、S1 詞表初版 7 詞、存量 38 處分型)。兩段標題完全相同、內容不互斥卻各講各的——第一段講「S2 N=20 run 仍是拍的」,第二段講「S2 門檻 20 與 ack 窗 30 天是拍的」,是同一個未決事項(S2 的門檻拍板)被拆成兩處、用不同措辭各講一半,任何只讀到第一個「## 未決」就停下的人會漏掉 S1 詞表初版與存量 38 處分型這兩條(尤其是「存量 38 處補標由實作者(本 session)分型」這條——這是 Verification 要收的內容,漏看等於漏了交付項)。這是 v2 把 v1 保留段與新增內容合併時沒有去重/合併的痕跡,對照 CLAUDE.md「多個 wikilink 必須...」等寫入紀律的精神,這種結構性重複本該在 `lumos lint` 或人工複核時被抓到。

file:line:文件第 107、118 行(兩個「## 未決」標題本身無法對應到 code,是文件結構問題,不涉及 scripts/lumos)。

正確做法:合併成單一「## 未決」段,5 條開放問題去重後放在一起,避免讀者漏看其中任一半。

---

count: 5
