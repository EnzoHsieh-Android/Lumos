# pin-denoise-a-v4 r1 架構對齊審查

被審:`/tmp/pin-denoise-a-v4-r1.md`(固定席降噪A層_計劃,204 行)。★只審獨立 JSON 鍵安置模型與 r3 折入 delta★(§2「JSON 輸出用獨立頂層鍵 `"lane"`,`results` 完全不含 lane」一段、工具清單 #2/#2b、PRIOR-ART、審計修正紀錄 r3 段),只判「跟本專案既有做法一不一致」,不找 bug、不評風格。對照對象:`scripts/lumos` 的 `impact --json` 既有頂層鍵模型(`out_obj`/`meta`)、`rescued` 第三桶的歷史決策紀錄、`scripts/hooks/claude/impact-hook.py` 與 `governance/eval/retrieval_eval.py` 對這份 JSON 的既有讀取慣例。

背景:本輪是三輪達上限後的裁甲delta審(決策 `d1`,`/tmp/pin-denoise-a-v4-r1.md:21-26`)——r3 把「獨立 JSON 頂層鍵」定為安置模型的修法,文件自己承認「★沒有任何審查員看過★」(`/tmp/pin-denoise-a-v4-r1.md:200`)。本輪補這隻眼睛。

---

## 問一:`out_obj`/`meta` 既有裝了什麼,開新頂層鍵有沒有先例

`cmd_impact` 的 JSON 基底只有三個鍵:`out_obj = {"file": rel_file, "results": final, "meta": meta}`(`scripts/lumos:14528`),`meta` 是計數字典 `{"candidates", "pinned", "truncated", "rescued", "safety_overflow"}`(`scripts/lumos:14524-14525`)。**開新頂層鍵確有先例,而且是同一支函式裡發生過兩次:** `out_obj["query_gated"] = True`(`scripts/lumos:14530`,查詢品質閘觸發時附加的觀測旗標)與 `out_obj["stack_questions"] = {...}`(`scripts/lumos:14536`,棧別效能追問附加payload)。兩者皆為**條件式存在**——不觸發就不出現在 JSON 裡,`scripts/test_lumos.py:20574/20583/20588/20592/20597` 逐一斷言「觸發時鍵在、不觸發時鍵不在」;`stack_questions` 同款測試在 `scripts/test_lumos.py:15042/15086`。`cmd_impact_diff` 自己的輸出層也有一個條件式頂層鍵先例:`**({"sync": sync} if sync is not None else {})`(`scripts/lumos:14698`)。所以「開新頂層鍵」本身,在這支程式的既有慣例裡不是禁區,是被反覆使用、且有測試釘住存在/不存在兩態的正常操作。

但這三個既有頂層鍵先例(`query_gated`/`stack_questions`/`sync`)裝的都不是「候選節點」——它們是整次查詢的旗標或另一種資料形狀(棧別問題表、touched/missing 節點的診斷附錄),跟 `results` 陣列裡每一項的欄位結構(`node`/`score`/`hop`/`contract`/`kind`)完全不同源。真正跟 `lane` 同形狀的既有先例只有一個:`rescued`。而 `rescued` 的既有慣例**不是**開新頂層鍵——見問二。這一層區分(旗標/附錄 vs. 節點候選)決定了「有沒有先例」要看你拿哪個當參照類別,判不準,標 ⚠(見結論)。

---

## 問二:`rescued` 當年為什麼「進 `results` 而非獨立鍵」,有沒有記錄

有明確、有日期的決策紀錄。`docs/lumos-toolchain-knowledge/Projects/hook必看召回修復_計劃.md:36`:「**席位模型=第三桶明文**(r2 折入,s3 blocker:現碼只有 pinned 布林二分桶,rescued 落錯桶則「被同一閾再砍」或「污染固定席語意」兩頭死):results 項帶 `rescued: true` **且 `pinned: false`**;...`final = pins + free[:min(top, quota)] + rescued(≤N)`...`meta` 加 `rescued` 計數鍵」。程式碼逐字對得上:`final = pins + free + rescued`(`scripts/lumos:14523`)、`out_obj["results"] = final`(`scripts/lumos:14528`)——rescued 從未被考慮放進獨立頂層鍵,「折入 results、用布林旗標分流」是唯一被討論過的方案,且有專屬測試釘住 `meta.rescued` 計數鍵(`scripts/test_lumos.py:21753`)。這一點回答了「有沒有記錄」:有,而且是清楚的、機械可核對的決策,不是含糊帶過。

但這份決策紀錄裡還有一段對本輪判定更關鍵、v4 spec 沒有引用到的話:「eval 端沿 pinned 二分讀取不受影響——rescued 天然落 free 桶、**計入 P@8 母體=誠實計噪**(護欄①正是在考這件事)」(`docs/lumos-toolchain-knowledge/Projects/hook必看召回修復_計劃.md:36`),對應的護欄①原文是「口徑如實:rescued 計入 P@8 母體,B 臂天然承壓,護欄考的就是誤救代價」(`docs/lumos-toolchain-knowledge/Projects/hook必看召回修復_計劃.md:94`)——也就是說,rescued 落入 P@8 母體**是刻意設計、由一個具名護欄機械把關的行為**,不是意外。而 v4 spec 工具清單 #2b④ 卻把同一件事講成:「free 讀 results 且★明文排除 rescued★(它現在被算進 P@8 母體只是僥倖沒進前 k,r2 s2f5;獨立回歸測試釘,arch ⚠)」(`/tmp/pin-denoise-a-v4-r1.md:88-89`,r2 審計摘要重複同一句見 `/tmp/pin-denoise-a-v4-r1.md:182`)——這句「僥倖」的措辭本身可回溯到本輪之前的一份 arch 審查:「rescued 從未在 eval 層被顯式排除在 P@8 母體之外,只是靠排序位置僥倖迴避」(`governance/review-reports/pin-denoise-a/r2-arch.md:41`,同份報告已自行標 ⚠「這件事本身未必是錯...但它確實不是『沿用既有做法』」)。v4 spec 把上一輪 arch 的「⚠、判不準」轉述成本輪工具清單裡的既定事實與行動項,且全文沒有一處提到 `hook必看召回修復_計劃.md:36/94` 這條原始「誠實計噪+護欄①」的設計紀錄——即將要推翻一個具名護欄的決策,卻沒有核對過那個護欄當初為什麼存在。

引句:「它現在被算進 P@8 母體只是僥倖沒進前 k」(`/tmp/pin-denoise-a-v4-r1.md:89`)

---

## 問三:hook 的 `data.get` 讀法、`edit_universe` 只抽 `results` 的慣例——lane 這個新鍵的消費端安全嗎

`build_ranked_context` 對現有三個鍵一律用容錯讀法:`res = data.get("results", [])`、`meta = data.get("meta", {})`(`scripts/hooks/claude/impact-hook.py:337-338`)、`for stk, qs in (data.get("stack_questions") or {}).items()`(`scripts/hooks/claude/impact-hook.py:364`);外層 gate `inject_ranked_context` 也是同款容錯:`if not data.get("results") and not data.get("stack_questions"): return`(`scripts/hooks/claude/impact-hook.py:378`)。`edit_universe` 同樣只抽一個鍵:`.get("results", [])`(`governance/eval/retrieval_eval.py:137`),`cmd_impact_diff` 聚合端讀 `data.get("meta", {})`/`data.get("query_gated")`/`data.get("results", [])`(`scripts/lumos:14658-14662`),`_bound_tests_for_diff`(spec 點名的另一個消費點)一樣讀 `data.get("results", [])`(`scripts/lumos:14887`)。**spec 在 §2「沒有學過 lane 的既有讀者結構性不受影響」這句話(`/tmp/pin-denoise-a-v4-r1.md:74-76`)查證屬實**——上述每一個既有消費點都是「不認得的鍵直接忽略」的寫法,不會因為 `out_obj` 多一個 `lane` 鍵而動作異常,這是本案技術論證裡少數完全站得住的部分。

但 spec 自己規劃的**第一個** lane 消費點,寫法卻背離了這個既有慣例:工具清單 #2b②「hook `build_ranked_context` 新小節讀 `data["lane"]`」(`/tmp/pin-denoise-a-v4-r1.md:86`)——用的是**方括號直接取值**,不是同一份工具清單 #2b①要求 `cmd_impact` 人讀分支「score 用 `.get`」的防禦寫法,也不是 `build_ranked_context` 自己既有的三個 `.get(...)` 讀法。這不只是風格不一致:`lane` 鍵本身是條件式的(§2 定義=knob `LUMOS_IMPACT_HARD_PIN` 預設 0、且「參考道整段包在 knob=1 分支內」`/tmp/pin-denoise-a-v4-r1.md:101-103`),也就是說在轉正之前的預設組態下 `lane` 鍵大概率整個不存在——這正是 `query_gated`/`stack_questions` 已經示範過、且被測試釘住「鍵可能不存在,讀取端必須用 `.get`」的既有模式。若真的照 spec 字面寫成 `data["lane"]`,knob=0(現行預設,也是 spec 自己標的「上線即死碼」臂)就會在每次 hook 呼叫時 KeyError。此外,工具清單 #2b 只提到要改 `build_ranked_context` 內部,完全沒提到外層 gate `inject_ranked_context` 的空集合判斷(`scripts/hooks/claude/impact-hook.py:378` 現在只看 `results`/`stack_questions`)——即使 `build_ranked_context` 改對了,若某次改動的候選**全部**被降入 lane(`results` 因此為空、也沒有 `stack_questions`),`inject_ranked_context` 仍會在看到 lane 小節之前就提前 return,守衛面參考小節不會被印出來,這正好是參考道這個機制原本要覆蓋的情境。

引句:「hook `build_ranked_context` 新小節讀 `data["lane"]`」(`/tmp/pin-denoise-a-v4-r1.md:86`)

---

## 綜合判定:獨立頂層鍵是「第二種做法」嗎;「未學讀者天然安全」夠格當刻意偏離的留痕嗎

是,相對於**唯一同形狀的既有先例**(rescued:候選節點,`node`/`score`/`hop`/`contract` 齊備),`lane` 選擇開新頂層鍵而非折入 `results`+旗標,確實是第二種安置法——問二已核對,rescued 當年沒有考慮過開獨立鍵這條路。但把參照類別放寬到「這支函式曾經開過的頂層鍵」(`query_gated`/`stack_questions`/`sync`),開新鍵本身不是破例。這個「該跟哪個先例比」的問題本身判不準,標 ⚠,不計入下方條數。

「未學讀者天然安全」這個理由本身,問三已逐點核對屬實——技術論證站得住,甚至間接修補了 rescued 折入模式暴露過的真實缺陷(rescued 靠 `pinned:False` 混進 `results`,被證實在 eval 端只靠排序位置僥倖沒有污染 P@8,見問二)。這部分夠格當一個「刻意偏離、講得出技術理由」的論證。但兩個具體問題壓低了它「留痕」的完整度:①同一節點內,較舊段落(`/tmp/pin-denoise-a-v4-r1.md:92-95`,標記為「arch r1 ⚠」的回應)仍宣稱「獨立容器、產生端限量、不過門檻名額、**append 輸出**、meta 計數,五個維度全照 rescued 慣例,不是第二種做法」——但 r3 折入後 lane **不再** append 進 `results`(`/tmp/pin-denoise-a-v4-r1.md:71`:「自始不進 `results` 共用清單」),「append 輸出」這一維度在 r3 之後已經不成立,段落沒有跟著改寫,讓讀者以為五個維度都還對得上;②推翻 rescued 的既有護欄(問二)時沒有引用護欄本身,讓「刻意偏離」看起來像是在填補一個「僥倖」的漏洞,而不是在推翻一個曾經被機械把關過的決定。

---

## 結論

不對齊共 **3** 條,其中 major **3** 條:

1.(問三)hook 消費點 `data["lane"]`(方括號直接取值)與 `build_ranked_context` 既有 `data.get("results", [])`/`data.get("meta", {})`/`data.get("stack_questions")` 三處一致的容錯讀法(`scripts/hooks/claude/impact-hook.py:337-338/364`)不符,且與「獨立頂層鍵」模型自身「鍵可能不存在」的前提(knob 預設 0 時 lane 鍵大概率整體缺席)相衝突,在最常見組態下會 KeyError;工具清單 #2b 也沒提到外層 gate `inject_ranked_context`(`scripts/hooks/claude/impact-hook.py:378`)要一併看 lane,候選全數降級時守衛面小節可能不會被印出。**major**。
2.(問二)工具清單 #2b④主張「rescued 現在算入 P@8 母體只是僥倖」並據此順手釘死排除,但原始設計紀錄明文把同一行為記成刻意的「誠實計噪」機制、由護欄①機械把關(`docs/lumos-toolchain-knowledge/Projects/hook必看召回修復_計劃.md:36/94`),spec 全文沒有引用或核對這條紀錄就要推翻它——這句「僥倖」的措辭其實承襲自上一輪一份自己標 ⚠、判不準的 arch 審查(`governance/review-reports/pin-denoise-a/r2-arch.md:41`),被本輪 spec 當成既定事實。**major**。
3.(綜合判定)節點內舊段落(`/tmp/pin-denoise-a-v4-r1.md:92-95`)宣稱的「五個維度全照 rescued 慣例,不是第二種做法」在 r3 折入獨立頂層鍵後,「append 輸出」這一維度已經不成立(`/tmp/pin-denoise-a-v4-r1.md:71` 明寫「自始不進 `results` 共用清單」),段落沒有隨 r3 修法更新,讓「不是第二種做法」這句結論式陳述失真。**major**。

另有 **1** 條 ⚠ 交編排者判準:
- 「開新頂層鍵有沒有先例」本身要看參照類別:窄看(跟 `lane` 同形狀的候選節點類)只有 `rescued`,而 `rescued` 的既有慣例是折入 `results`+旗標,不是開新鍵;寬看(這支函式曾經開過的頂層鍵)則 `query_gated`/`stack_questions`/`sync` 三個先例都成立,開新鍵不是破例。兩種參照類別哪個才是本案該比的對象,判不準。
