# pin-denoise-a-v4 r2 架構對齊審查

被審:`/tmp/pin-denoise-a-v4-r2.md`(固定席降噪A層_計劃,225 行)。★只審 v4-r1 折入 delta★:hook `.get`+空判斷閘改法、rescued P@8 撤回(維持現狀)、edit_pool opt-in、混版協定、#7 綁定改綁 #6③、retrieval-ranking 帶日期 KEY、「四維度+刻意偏離留痕」句。只判「跟本專案既有做法一不一致」,不找 bug、不評風格。

背景:v4-r1 是對 `governance/review-reports/pin-denoise-a-v4/r1-arch.md` 三個 major 發現(`data["lane"]` 方括號直取值/空判斷閘漏 lane、rescued P@8 排除引用「僥倖」措辭其實是推翻具名護欄、「五維度」句在獨立頂層鍵模型下已失真)的折入回應,連同 s1/s2/Codex 抓到的第六個讀者(`build_goldset.edit_pool`)、混版相容協定、#7 綁定替換等一起收斂。本輪核對折入是否真的照專案既有寫法接上,不重複 r1 已核過的部分,只補未核到的角落。

---

## 問一:hook 讀取端的 `.get`/空判斷閘慣例,以及混版協定的退化寫法有沒有沿用既有模式

`impact-hook.py` 對 ranked JSON 的既有讀法一律走 `.get()`:`res = data.get("results", [])`、`meta = data.get("meta", {})`(`scripts/hooks/claude/impact-hook.py:335-336`),外層 gate `if not data.get("results") and not data.get("stack_questions"): return`(`scripts/hooks/claude/impact-hook.py:378`)。`scripts/lumos` 自己也有同款條件鍵先例:`out_obj["query_gated"] = True` 這個鍵只在觸發時才出現,消費端一律 `data.get("query_gated")` 判讀(`scripts/lumos:14659`)。v4-r1 折入後的寫法(`/tmp/pin-denoise-a-v4-r2.md:86-89`)——`build_ranked_context` 讀 `data.get("lane", [])`,且明文把空判斷閘擴成「要加看 lane」——逐字對得上這個既有模式,沒有另開一套讀法。r1-arch 抓到的兩個問題(方括號直取值會在 knob=0 常態下 KeyError、空判斷閘漏 lane 導致 lane-only 場景整段不注入)在這版都已改正,且改正的寫法就是抄既有 `.get`/條件鍵慣例,不是自造。**對齊**。

混版協定(`/tmp/pin-denoise-a-v4-r2.md:97-98`)的「新 hook 全 `.get` 讀舊 CLI=安全退化」是問一這條慣例的直接延伸,同樣對齊。「hooks 由 install 同步機制保底」這句有實在的機制可對:`docs/lumos-toolchain-knowledge/Projects/install全域hook同步_計劃.md` 記的正是 `~/.claude/hooks/*.py` 屬於「copy 類」更新——`git pull` 不會讓它自動生效,要跑 `install` 才同步(該節點 KEY:「symlink 類(skills/CLI)pull 即活,copy/merge 類要重跑安裝——後者在 install 缺席」)。這代表 hook 與 CLI 確實可能暫時不同版,`.get()` 退化不是憑空假設的風險,是這個專案已經記過一次的真實缺口。「落地 commit 註明『hook 與 CLI 同批更新』」這個提醒式作法,能找到的最接近先例是 `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:38`:「發現時還沒 push,已 amend 補一段『同批夾帶:…』載明來源」——同樣是用 commit message 記載「這批改動包含哪些互相依賴的部分」,但那個案例是既成事實後的補記,不是像本案這樣把它當成唯一的協調機制。這個對照成立但偏弱,判準見結論的 ⚠ 備註。

---

## 問二:rescued P@8 撤回的引用站不站得住;edit_pool 併入既有 opt-in 讀取模型是否走老路

`/tmp/pin-denoise-a-v4-r2.md:91-92` 主張「`free` 只排 lane;rescued 不排——rescued 進 P@8 母體是 2026-08-07 決策紀錄裡具名護欄『誠實計噪』的刻意設計,r2 那句『僥倖』是把上輪 ⚠ 當事實,撤回」。查 `docs/lumos-toolchain-knowledge/Projects/hook必看召回修復_計劃.md`:「eval 端沿 pinned 二分讀取不受影響——rescued 天然落 free 桶、**計入 P@8 母體=誠實計噪**(護欄①正是在考這件事)」(該節點「### R1 直連保底席」段);對應護欄①原文「口徑如實:rescued 計入 P@8 母體,B 臂天然承壓,護欄考的就是誤救代價」也在同節點的驗收線段落。**引得對**——rescued 落入 P@8 母體從一開始就是被機械把關過的刻意設計,不是漏標。實際碼也印證這是現行行為而非要新引入的東西:`free = [x["node"] for x in res if not x.get("pinned")]`(`governance/eval/retrieval_eval.py:161`,`_touched_edit` 用)與 `free = [x for x in res if not x.get("pinned")]`(`governance/eval/retrieval_eval.py:336`,`eval_edit` 用)兩處都只用 `pinned` 分桶,rescued 項的 `pinned:False` 讓它自然落入 `free`、自然計入母體——v4-r1 這條折入是把 delta 拉回現行程式碼與現行決策紀錄的原貌,不是引入新做法。**對齊**。

`edit_pool` 是 s1/s2/Codex 三席同抓的「第六個讀者」(`governance/eval/build_goldset.py:157-160`):`ranked = lum_json("impact", ..., "--json", stdin=payload).get("results", [])`——一樣是 `.get("results", [])` 這個既有讀法,只讀 `results` 不讀 `lane`。v4-r1 把它併入 opt-in 名單(工具清單 ⑥,`/tmp/pin-denoise-a-v4-r2.md:96`)的處理方式,跟 §2 opt-in 名單裡另外五個既有讀者(人讀分支/hook/`edit_universe`/`eval_edit`/`_touched_edit`)走的是同一套「獨立鍵模型下不改就不受影響,要用的才改」規則,沒有為這第六個讀者另開特例或另一套併入方式。**對齊**。

---

## 問三:retrieval-ranking 帶日期 KEY 的加註寫法;#7 綁定改綁 #6③ 是否符合測試假綠形態紀律;「四維度+刻意偏離留痕」句對頂層鍵先例的核對站不站得住

`Systems/retrieval-ranking.md` 現有的四則 KEY 行全走同一種格式:`KEY:[YYYY-MM-DD 主題,plan:[[Projects/…]]]內容……[test:…] | VERIFY:[[Verification/…]]`(`docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:13-16`,以 `:15` 那則 2026-08-07 hook必看召回修復落地為例)。工具清單 #7(`/tmp/pin-denoise-a-v4-r2.md:143`)規劃「除修 `:11`/`:47` 兩句外,加一則帶日期的 KEY 落地紀錄」——這正是同一節點既有四則 KEY 行反覆使用的格式,不是另立寫法。**對齊**。

#7 綁定改綁 #6③(`/tmp/pin-denoise-a-v4-r2.md:143`:「替代綁定必須測『改了什麼』,#6①④測的是『什麼沒變』不合格」)直接對應本專案「測試假綠形態」清單第⑨型——「合約文字寬於測試覆蓋(宣稱的行為從未被執行過)」:「合約/文件宣稱一個行為,也綁了測試……但綁的測試只走過宣稱的**子集**,宣稱的其餘部分**從來沒有被任何測試……真的執行過**」(`docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:121-125`)。`Systems/lumos-cli-read.md:14` 那句新宣稱「被降者出現在 JSON `lane` 鍵」,若只綁 #6①(knob=0 逐 byte 不變)與 #6④(RISK indirect 不保送),兩條測完全不會執行到「lane 鍵真的出現」這件事——這正是第⑨型的教科書案例。`skills/lumos-project-notes/reference.md:666`「綁 `[test:]` 前對照 `Systems/測試假綠形態`……綁上去的測試若中了其中一型,合約鏈看起來完整、實際什麼都沒守住」與 `SKILL.md:52` 是同一條紀律的兩處重申。v4-r1 這條折入是把既有紀律套用到一個新綁定上,沒有另造判準。**對齊**。

「四維度+刻意偏離留痕」句(`/tmp/pin-denoise-a-v4-r2.md:101-103`)是本輪唯一一處真正的架構分歧,但寫法本身值得肯定:它先核過四個維度(獨立容器/產生端限量/不過門檻名額/meta 計數)跟 rescued 的既有實作逐一對得上——`rescued = []` 獨立容器、`LUMOS_IMPACT_RESCUE_N` 產生端限量、「threshold/quota 不作用其上」、`meta["rescued"] = len(rescued)` 計數(`scripts/lumos:14502-14524`),四項全部屬實;然後才把第五個維度(輸出位置)明確拉出來單獨承認是偏離。查頂層鍵先例:`out_obj = {"file": rel_file, "results": final, "meta": meta}`(`scripts/lumos:14528`)、條件式追加 `out_obj["query_gated"] = True`(`scripts/lumos:14530`)、`out_obj["stack_questions"] = {...}`(`scripts/lumos:14536`),以及 `cmd_impact_diff` 的 `**({"sync": sync} if sync is not None else {})`(`scripts/lumos:14698`)——這四個先例都成立,但它們裝的都不是「候選節點陣列」:`query_gated` 是布林旗標,`stack_questions` 是問題表,`sync` 底下的 `missing` 陣列雖然形狀像候選節點,卻是巢狀在 `sync` 這個頂層鍵**之下**,不是它自己就是頂層鍵。目前唯一「頂層鍵直接裝候選節點陣列」的是 `results`,`lane` 會是第二個——spec 自己的結論「候選節點陣列開頂層鍵是首例」查證屬實。跟 rescued 唯一同形狀的既有做法(折入 `results`、用 `rescued: true` 布林旗標分流)相比,`lane` 選擇不折入、改開獨立頂層鍵,確實是本專案裡候選節點資料的第二種安置法。**不對齊,major**——這不是疏漏,而是 spec 自己標記、自己核對過先例、且在 arch r1 的 ⚠ 已經被正面回答過的刻意決定;但按「架構對齊」的判準,刻意與否不改變它在結構上是不是第二種做法,只改變它該不該被接受,那是留給人裁的事。

引句:「這是刻意的第二種做法」(`/tmp/pin-denoise-a-v4-r2.md:103`)

---

## 結論

不對齊共 **1** 條,其中 major **1** 條:

1.(問三)`lane` 用獨立頂層鍵裝候選節點陣列,是本專案「候選節點資料」目前唯一的第二種安置法(既有做法=折入 `results`+布林旗標,`scripts/lumos:14523-14528`);四個維度(容器/限量/門檻/計數)照 rescued 慣例、僅第五個維度(輸出位置)刻意偏離,且已核對頂層鍵先例(`query_gated`/`stack_questions`/`sync`,`scripts/lumos:14530/14536/14698`)只支持「開新頂層鍵」本身不算破例,不支持「候選節點陣列」這個資料形狀有先例。**major**,但屬已留痕、已在 arch r1 被正面回答過的刻意選擇。

另有 **1** 條 ⚠ 備註,不計入上方條數:混版協定裡「落地 commit 註明『hook 與 CLI 同批更新』」這個提醒式作法,本專案能找到的最接近先例(`docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:38` 的「同批夾帶」commit 註記)是既成事實後的事後補記,不是像本案這樣把 commit message 當成唯一協調機制事先講好——這個對照成立但偏弱,判不準,交編排者。
