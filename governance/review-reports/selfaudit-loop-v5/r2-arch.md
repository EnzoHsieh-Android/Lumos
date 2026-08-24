# selfaudit-loop-v5 r2 架構對齊審查

角色:只判「跟本 repo 既有做法一不一樣」,不判設計對不對、也不重審 v1-v5 已經吵過的內容。
範圍:被審 `/tmp/selfaudit-loop-v5-r2.md`(即 `docs/lumos-toolchain-knowledge/Projects/自足性審計閉環_計劃.md`,204 行),
只看 v6 delta 七項——柵欄鐵則/sha 定形/started 預約+flock/沙盒刪除清單/網路誠實段/query 三刀/結局分流。
三問各自的對照物列在段落開頭。

---

## 問一:柵欄機制本身的雜湊選型(柵欄鐵則 + sha 定形)

**對照物①:本 repo 唯一既有的「拍雜湊、比對、不信任」機制——`about_code_stamp` 過期守衛。**
`note_body_hash`(`scripts/lumos:7700-7713`)算的是「frontmatter 之外正文(rstrip 後)」的 sha256 前 12 碼,
docstring 明講設計理由:「★必須 utf-8-sig★:BOM 檔否則 split_frontmatter 切不出 frontmatter、整檔算進雜湊,
『只改 frontmatter 不過期』就破」(`scripts/lumos:7706-7707`)——排除 frontmatter 是**刻意**設計,三輪審計才定形
(std-r3 arch+s1 兩席抓到)。`about_code_expired`(`scripts/lumos:7736-7740`)拿「現在雜湊」跟「標記當時雜湊」比對,
不等就判過期——這正是 v5-r1 arch 自己在 r1 審裡認證過的同構關係(「回寫柵欄被架構席驗出與 about_code 雜湊守衛同構」,
spec:200)。

v6 的「快照 sha 定形」卻改用整檔:「selfaudit.py 派工那一刻對主樹該篇 `hashlib.sha256(path.read_bytes())` 整檔計算並持有;
柵欄比對=同函式同演算法,兩邊永遠同空間」(spec:78-80)。這句話只論證了**內部一致性**(比對兩邊用同一函式、同一算法),
沒有論證**粒度選擇**——為什麼這次要包含 frontmatter,而全 repo 唯一的同類先例特地把 frontmatter 排除在外。
兩者目的確實不同(`about_code_expired` 判斷「about_code 的宣稱是否對正文仍成立」,frontmatter 改動語意上無關;
柵欄判斷「派工期間主樹這篇是否被任何人動過」,frontmatter 改動——例如 `lumos set` 改狀態欄——理論上也算「被動過」),
所以整檔雜湊未必是錯的選擇。但 spec 全文(用 `frontmatter\|正文\|整檔` 掃過)完全沒有一行提到「frontmatter 改動也算主樹變」
這個理由,也沒有引用 `note_body_hash` 這個既有先例並說明「這次故意不沿用」。對照 CLAUDE.md 自己要求的
「世界解過沒……一行 PRIOR-ART 記進計劃筆記」,這條 delta 沒有把「跟既有雜湊機制不同粒度」這件事講清楚,判 major。

引句:「`hashlib.sha256(path.read_bytes())` 整檔計算並持有」

---

## 問二:派工期資源隔離與並發保護(沙盒刪除清單 + started 預約 + flock)

**對照物②:governance 簿記檔清單在本 repo 已經因「兩處分開寫會漂移」被收斂成單一源,v6 卻又開一份新的。**
`scripts/lumos:10868-10874` 的 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR` 前面掛的註解原文是:「簿記檔白名單(單一源,
兩個消費者:pitfalls --diff 掃描排除 + code-loop 留痕失效豁免)。兩處分開寫過會漂移」——這是本 repo 明文記錄過的
教訓:governance 記帳檔清單只要抄兩份就會走鐘。而 `scripts/lumos:11721-11726` 的 `_COCHANGE_DEFAULT_EXCLUDE`
已經是第二份獨立列舉(含 `.canary-log.jsonl`/`.rot-queue.jsonl`/`.kill-log.jsonl`/`.signoff-log.jsonl` 等,
跟 `_BOOKKEEPING_FILES` 不完全重疊)——即使有過「單一源」的教訓,repo 裡實際上已經在維護兩份不同形的清單。
v6 的沙盒刪除清單「建好後刪沙盒內全部審計脈絡:`governance/review-reports/`、`governance/pending/`、
`governance/l4-audit/`、`docs/.governance-log.jsonl`、`docs/.canary-log.jsonl`」(spec:68-69)是**第三份**,
且全文沒有一處提到 `_BOOKKEEPING_FILES` 或 `_COCHANGE_DEFAULT_EXCLUDE`,也沒有說明「這次為什麼不能沿用既有清單、
只能重新列舉」(兩份既有清單確實都不含目錄項,只收檔案,沿用不了是有道理的,但這道理 spec 沒寫)。
與本 repo 自己記錄過的漂移教訓正面撞上,判 major。

引句:「刪沙盒內全部審計脈絡(v5-r1 s2 抓到兩個漏)」

**對照物③:`fcntl.flock` 在 repo 有先例,但先例的鎖語意跟 v6 要的效果不完全對得上,而且沒被引用。**
grep 全 repo,`flock`/`fcntl` 只有兩處活代碼:`governance/eval/refresh_labels.py:52-73` 的 `_goldset_lock`
(goldset 寫入互斥鎖)與 `scripts/test_lumos.py:21280-21319` 對它的測試。既有先例的語意寫得很白:
「goldset 寫入互斥鎖(flock 非阻塞):apply/repin 讀改寫全程持有。搶不到=另一寫入進行中 → 快速失敗,
呼叫端 rc 非零、goldset 不動」(`refresh_labels.py:53-54`),鎖模式是 `fcntl.LOCK_EX | fcntl.LOCK_NB`
(`refresh_labels.py:62`)——非阻塞、搶不到就整個操作放棄,不等待。
v6 的用法是「整段『讀配額→派工→終局 append』用 `fcntl.flock` 鎖週帳檔(標準庫零依賴;同日兩進場不超額,
v5-r1 s2f9/Codex f4)」(spec:97)。要達成「同日兩進場不超額」,第二個進場者理論上要**等第一個放鎖後**
讀到更新後的配額,而非像既有先例那樣直接非阻塞失敗——如果 v6 也套用既有的 `LOCK_NB` 語意,第二個進場者
搶不到鎖時該怎麼處理(整段跳過今天?重試?)spec 沒寫;如果改用阻塞式 `LOCK_EX`(不帶 NB),那就是跟
repo 目前唯一先例不同的鎖策略,同樣沒有寫明、也沒有引用既有先例來說明沿用或不沿用的理由。
不管走哪一種,PRIOR-ART 段落(spec:121-124)完全沒提這個先例——本案 PRIOR-ART 已經很仔細地交代了
沙盒、週帳格式、判定邏輯各自借了誰的先例,唯獨 flock 這塊留白。判 major,鎖策略的具體選擇(阻塞或非阻塞)
標 ⚠(spec 文字不足以確定實作會怎麼選,可能只是我方推論)。

引句:「用 `fcntl.flock` 鎖週帳檔★(標準庫零依賴;同日兩進場不超額」

**對照物④:「started 預約」的耐久兩列寫法,在本 repo 現有的三個事件帳(governance-log/canary-log/ci-log)裡都找不到對應形狀。**
`_append_governance_log`(`scripts/lumos:434-454`)、`_ci_write`(`scripts/lumos:13234-13249`)寫的都是
「事情發生後才寫一行」的單次記錄——`docs/.governance-log.jsonl` 每一行是已完成的 gate 判定(`gate`+`kind`,
如 `{"gate": "check-s", "kind": "warned", ...}`,實例見 `docs/.governance-log.jsonl:1-3`),`.ci-log.jsonl`
用 `dedup_key` 防重寫、同樣是「結論出來才寫」(`_ci_write` 註解:「寫帳(去重鍵 run_id:attempt:conclusion;
helper 不 upsert 故應用層先掃)」)。全 repo grep `"kind":\s*"` 收集到的所有 kind 值(aggregate/approved/
blocked/bypassed/degraded/direct/incident/indirect/new_non_skippable/ran/second/shallow/signed/warned)
裡沒有一個是「started」或任何「預約中/進行中」的語意——canary-log 雖然同一個 loop id 會累積多行不同 kind
(ran/signed/approved 等,由 `lumos canary record` 陸續呼叫寫入),但那些都是**動作完成後**才記的階段結果,
不是「動手前先佔一行、失敗了靠『有列無終局』推斷」這種倒過來的耐久預約寫法。
v6:「派工前先 append kind=started(耐久預約,v5-r1 Codex f4:程序中斷在終局列前,下次不重複消耗配額;
有 started 無終局=視同 abort 補記)」(spec:94-95)是本案自己發明、repo 裡沒有先例的一種新記帳形狀——這件事
本身不是錯,但 spec 的 PRIOR-ART 段落(spec:121-124)只交代了「週帳=append-only jsonl(判別鍵照 governance-log
的 gate+kind 慣例)」,把 started 預約這個新形狀直接併進「既有慣例」的敘述裡,沒有把「這條是全新設計、
repo 沒有先例」講清楚。判 major。

引句:「派工前先 append kind=started(耐久預約,v5-r1 Codex f4」

---

## 問三:對外介面與收尾分流(query 三刀 + 網路誠實段 + 結局分流)

**對照物⑤:query 輸出投影超集 vs `lane` 頂層鍵先例——這條是對齊的。**
`cmd_query`(`scripts/lumos:6649-6701`)的既有 JSON 投影固定是 `{"node", "status", "tags"}`
(`scripts/lumos:6690-6692`);r1-arch 曾經打過一次 major(`--self-audit-due` 換掉了整組欄名,
node→rel、丟了 status/tags,見 `governance/review-reports/selfaudit-loop-v5/r1-arch.md` 對照物③)。
v6 已經改成「輸出=既有投影★超集★:保留 node/status/tags 三欄、加 stem/repo_rel/self_audit_state——
舊消費者照樣找得到自己的鍵」(spec:65)——這跟 `lumos impact --json` 的 `lane` 精選臂加法完全同一招:
`meta["lane"]`/`out_obj["lane"]` 是獨立頂層鍵疊加上去,決策原文寫「JSON 用獨立頂層鍵『lane』(決策 d2:
沒學過 lane 的讀者結構性不受影響,diff 聚合/hook free 桶/守衛全免改)」(`scripts/lumos:14461-14463`)。
兩邊的精神一致:舊消費者的既有鍵不動、新資訊用加法掛上去。這條對齊,不計入不對齊。

**對照物⑥:網路誠實段用詞「誠實邊界」vs 本專案兩套並行的風險承認慣例——查證後也是對齊的。**
本 repo 其實有兩套平行的「誠實/天花板」寫作慣例:`docs/design/*.md`(自主 loop 產出的舊格式)用
「誠實天花板」作為固定小節標題,連 `orchestrator-prompt.md:35` 和 `docs/design/2026-07-03-risk-tiered-review.md:45`
的 `assess_spec` 黑名單都機械認這個詞;而 `docs/lumos-toolchain-knowledge/Projects/*_計劃.md`(這份筆記自己所屬的
語料,即 CLAUDE.md 規定的「設計、spec、計劃一律寫成 Projects/<主題>_計劃 筆記」)則普遍用「誠實邊界」
(如 `檢索PPR邊權_計劃.md`、`結清式收斂_計劃.md`、`關係層傳播守衛_計劃.md` 等多篇皆用此詞,本筆記自己
在 v5-r1 就已經用過)。v6 的「★誠實邊界(v5-r1 Codex f1)★:沙盒保證的是★主樹檔案零風險★……這與 orchestrator
每日跑的天花板完全相同」(spec:70-72)用詞跟它自己所屬的 Projects 語料一致,只是拿 orchestrator 的
「天花板」概念來類比、沒有混用成標題詞——這條對齊,不計入不對齊。

**對照物⑦:結局分流(柵欄擋下=時序巧合、不算失敗)vs 本 repo「良性未完成 ≠ 失敗」的既有哲學——對齊。**
「柵欄擋下(stale)=時序巧合非失敗→不落 pending、不鎖,記週帳後重新排隊」(spec:90-91)這個「區分良性
未完成與真失敗、前者不計入懲罰性狀態」的判準,在本 repo 有多處同精神先例:「★但無 remote 不算失敗★:
手動複製/slim 安裝出來的來源本就沒有 remote,那是合法的」(`scripts/lumos:9290`)、ci-log 的
「已記過,跳過(不算失敗)」(`scripts/lumos:13249`)、以及 `_run_lint`/SARIF 註解「rc≠0 不算失敗,
detekt 等工具有問題時仍輸出有效 SARIF」(`scripts/lumos:11069`)。三處都是同一個原則:某個信號雖然
「沒有正常收尾」,但只要能確認肇因是良性的(沒 remote 本來就合法、已經記過所以跳過、工具本身有已知限制),
就不算進失敗計數。柵欄擋下的肇因(主樹在派工期間被人正常改動)同樣是良性巧合而非鏈路壞掉,判定邏輯與既有
哲學一致。這條對齊,不計入不對齊。

---

## 不對齊清單

| # | 位置(spec) | 對照物 | 嚴重度 |
|---|---|---|---|
| 1 | spec:78-80 | 柵欄快照用整檔 `hashlib.sha256(path.read_bytes())`,未引用/未論證與既有 `note_body_hash`(排除 frontmatter,`scripts/lumos:7700-7713`)不同粒度的理由 | major |
| 2 | spec:68-69 | 沙盒刪除清單是第三份獨立列舉的 governance 簿記檔清單,未引用/未說明是否可沿用既有單一源 `_BOOKKEEPING_FILES`(`scripts/lumos:10868-10874`,repo 自己記錄過「兩處分開寫會漂移」) | major |
| 3 | spec:97 | 週帳 `fcntl.flock` 用法未引用 repo 唯一既有先例 `_goldset_lock`(`governance/eval/refresh_labels.py:52-73`,非阻塞快速失敗);鎖是否為阻塞式以達成「同日兩進場不超額」未寫明 | major(鎖策略推論部分 ⚠) |
| 4 | spec:94-95 | 「started 預約」耐久兩列寫法在 governance-log/ci-log/canary-log 三個既有事件帳裡都無對應形狀,PRIOR-ART 段落未點名這是全新設計 | major |

**不對齊共 4 條,其中 major 4 條。**
