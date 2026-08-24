# pin-denoise-a r2 架構對齊審查

被審:`/tmp/pin-denoise-a-r2.md`(固定席降噪A層_計劃,146 行)。★只審 v2 delta:主案 v2、參考道、工具清單、尺 v2、PRIOR-ART 誠實版★,只判「跟本專案既有做法一不一致」,不找 bug、不評風格。對照對象:`scripts/lumos` 的 `rescued` 第三桶(R1 直連保底席)。

---

## 問一:參考道自稱「同一家族第二個成員,不是第二種做法」,這個宣稱成立嗎

宣稱出處:spec §2「★為什麼不擴 rescued★(arch ⚠ 的回答):rescued 解的是「direct 被門檻砍」的缺口補席;本案是「整類降級後的保留」,語意不同;但實作**共用同一種輸出位置**(free 之後、pinned False、豁免門檻名額),是同一家族的第二個成員,不是第二種做法。」(`/tmp/pin-denoise-a-r2.md:71-72`,同一句在 PRIOR-ART 段重申:`/tmp/pin-denoise-a-r2.md:122`)。逐項核對四個維度:

**輸出位置★對齊★。** rescued 現行機制是把算好的補救名單外掛在 `free` 之後:`final = pins + free + rescued`(`scripts/lumos:14523`)。工具清單 #2 把參考道接在同一條拼接式的再下一節——「參考道:降級節點 append 到 rescued 之後」(`/tmp/pin-denoise-a-r2.md:97`),即 `pins + free + rescued + lane` 的自然延伸,沒有另立新的輸出通道,這一項確實是同家族的做法。

**cap 做法★不對齊,major★。** rescued 的名額限制完全發生在「產生階段」:`_rescue_n` 這個 knob(預設 3)減去 `free` 裡已有的 direct 數,算出缺口 `_need`,只把 `dropped[:_need]` 塞進 `rescued` list(`scripts/lumos:14510-14520`),且明文「threshold/quota 不作用其上」(`scripts/lumos:14500`)——也就是說 JSON、人讀、hook 三處看到的都已經是這個算好的最終列表,沒有任何一處對 rescued 再做「顯示層」二次截斷,`impact-hook.py:356-361` 印出 `rescued` 整個 list,沒有任何 slicing。參考道規劃的卻是「不過門檻、不佔名額」(產生階段完全不設上限)+「JSON 全量、人讀/hook 顯示上限 3(顯示層截斷)」(`/tmp/pin-denoise-a-r2.md:66`,同款文字見工具清單 #2`/tmp/pin-denoise-a-r2.md:97`)——把「要不要限量」這個問題從 rescued 既有的「產生階段算好再輸出」搬到「顯示層另砍一刀」,是同一個問題的第二種解法,不是複用 rescued 的機制。

引句:「上限 3 條(顯示層截斷,JSON 全量)」(`/tmp/pin-denoise-a-r2.md:66`)

**JSON/人讀/hook 三處顯示——與上一條同源,一併不對齊。** rescued 目前只有兩處有專屬呈現:JSON(逐筆 `rescued:true` 欄位 + `meta.rescued` 計數,`scripts/lumos:14520/14525`)、hook(獨立小節「另外 N 篇分數不高但直接提到這個檔」,`impact-hook.py:356-361`)。`scripts/lumos` 自己的人讀 CLI 分支(`scripts/lumos:14539-14548`)完全沒有替 rescued 開專屬小節,是跟 pins/free 混在同一個 `for r in final:` 迴圈裡印(`scripts/lumos:14540`),只靠既有的 `pin = " [固定]" if r["pinned"] else ""` 欄位分辨,rescued 本身沒有可視標籤——即 rescued 從未觸碰「人讀 CLI」這一層的差異化顯示。工具清單 #2 卻要求「人讀/hook 顯示上限 3」(`/tmp/pin-denoise-a-r2.md:97`),把差異化顯示擴大到 rescued 從無先例的第三個位置。這不是複製既有兩處,是新增一處。

**欄位命名(lane 字串 vs rescued 布林)⚠判不準。** rescued 用專屬布林旗標:`rr["rescued"] = True`(`scripts/lumos:14520`);參考道用字串值:「加 `lane: "soft-guard"`、`pinned: False`」(`/tmp/pin-denoise-a-r2.md:64`)。單看跟 rescued 本身比,這是不同的欄位慣例;但 `results` dict 裡本來就有 `kind`(`"incident"`/`"direct"`/`"indirect"`,`scripts/lumos:14428` 起)這個既有的字串列舉欄位,所以「用字串值分類」在同一個 dict 結構裡並非首見。是否構成「第二種做法」要看審查者把參照對象定在 rescued(不對齊)還是整個 results schema(有 `kind` 先例、對齊)——判不準,標 ⚠。

引句:「加 `lane: "soft-guard"`、`pinned: False`」(`/tmp/pin-denoise-a-r2.md:64`)

---

## 問二:`meta` 欄慣例——rescued 有 `meta.rescued` 計數,lane 要不要

**不對齊(非 major,是遺漏)。** rescued 的 `meta` 字典明文包含計數鍵:`meta = {"candidates": ..., "pinned": ..., "truncated": ..., "rescued": len(rescued), "safety_overflow": ...}`(`scripts/lumos:14524-14525`),且這個鍵是被測試釘住的合約,不是可有可無的裝飾:`test_lumos.py:21753` 直接斷言 `check("★meta.rescued 計數鍵★", d["meta"].get("rescued") == 1, str(d["meta"]))`。也就是說 rescued 家族的既有慣例是「每個外掛桶都同時有 (a) 逐筆布林旗標 + (b) `meta.<桶名>` 計數鍵」兩件事一起出現,且計數鍵有專屬測試。

通篇檢索 `/tmp/pin-denoise-a-r2.md`,參考道的欄位規格只出現在工具清單 #2:「參考道:降級節點 append 到 rescued 之後,`lane`/`pinned:False`,JSON 全量、人讀/hook 顯示上限 3」(`/tmp/pin-denoise-a-r2.md:97`)——全文沒有任何一處提到 `meta.lane`(或等義的計數鍵)。工具清單 #6 的測試計劃「①knob=0 逐 byte ②P@8 母體不含 lane ③被降者仍在 results ④事故/INVARIANT indirect 不受影響 ⑤翻紅釘:拿掉參考道→must_in_out 掉」(`/tmp/pin-denoise-a-r2.md:101`)也沒有對應 rescued 那條「★meta.rescued 計數鍵★」的姐妹測試。這是「同一家族第二個成員」宣稱裡一個具體、可核對的缺口:v2 複製了 rescued 的欄位命名精神(`pinned:False` + 專屬旗標)的一半,但沒有複製另一半(meta 計數鍵 + 對應測試)。

引句:「`lane`/`pinned:False`,JSON 全量、人讀/hook 顯示上限 3」(`/tmp/pin-denoise-a-r2.md:97`)

---

## 問三:knob 轉正流程文字對照;eval 口徑改動(pin_noise 排除 lane)有沒有先例可循

**knob 轉正流程★對齊★。** spec:「★總開關★:`LUMOS_IMPACT_HARD_PIN`,★預設 0(上線即死碼)★(s2f9:預設問號沒法審)——照 `LUMOS_IMPACT_BASENAME_MATCH` 轉正流程:train 網格、held 驗一次、gate 全過才轉預設 1;0=舊制逃生。」(`/tmp/pin-denoise-a-r2.md:76-77`)。這跟兩個既有 knob 的實際轉正史逐字對得上:`LUMOS_IMPACT_BASENAME_MATCH` 明文「2026-08-07 轉正預設 1;0=逃生/A 臂」(`scripts/lumos:13815`,`13830`);`LUMOS_IMPACT_RESCUE_N` 明文「2026-08-07 水位案考卷轉正 N=3(train 網格 {1,2,3} recall 軸選出;held 確認 Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠;knob 留逃生)」(`scripts/lumos:14502-14509`)。「train 網格→held 驗一次→gate 全過才轉正→0 留逃生」這套流程跟兩個既有 knob 的實際做法一致,沒有另立新的轉正判準,這一項不列入不對齊。

`--top` 豁免的引用也查證屬實:spec「參考道不受 `--top` 截斷(同 rescued 慣例)」(`/tmp/pin-denoise-a-r2.md:89`),對照 rescued 明文「外掛於 free 之後(--top 例外, 同 pins safety_overflow 精神)」(`scripts/lumos:14500`)——這句引用精確,不列入不對齊。

**eval 口徑改動(pin_noise/P@8 排除 lane)查無 rescued 先例,且與 rescued 現況不對稱⚠判不準。** 工具清單 #4:「eval:pin_noise 口徑=真固定席(參考道不算噪音也不算固定席);P@8 母體不含 lane」(`/tmp/pin-denoise-a-r2.md:99`)。查 `governance/eval/retrieval_eval.py` 全部歷史(`git log -p` 過濾 `rescued`),從未出現過任何一次對 rescued 的顯式排除邏輯——目前 `pin_noise` 天然不含 rescued,純粹是因為 rescued 恆 `pinned:False`、而 `pin_noise = sum(1 for x in pins if ...)` 只掃 `pinned` 為真的項目(`governance/eval/retrieval_eval.py:335/361`),不是有人特地寫過濾;但 `_touched_edit()` 算 P@8/nDCG 觸及集用的「free 前 k」是 `free = [x["node"] for x in res if not x.get("pinned")]`(`governance/eval/retrieval_eval.py:161`,`_touched_edit` 版見 `governance/eval/retrieval_eval.py:154-161` 段)——這個過濾條件同樣把 rescued 算進「free」候選,只是因為 rescued 在 `res` 排序裡永遠殿後(`final = pins + free + rescued`),才「結構上通常」不會擠進前 k;一旦 free 本身少於 k,rescued 就會滲入計分母體。也就是說,rescued 從未在 eval 層被顯式排除在 P@8 母體之外,只是靠排序位置僥倖迴避。

參考道規劃要新增一段程式碼明確把 lane 從 P@8 母體剔除(`eval_edit`,`/tmp/pin-denoise-a-r2.md:99`)——這比 rescued 現有的保護更強、更明確,不是「照抄 rescued 的先例」(沒有先例可抄),也沒有回頭補一致的保護給 rescued(兩個「同家族成員」在 eval 層待遇不對稱)。這件事本身未必是錯——比 rescued 更嚴謹地保護 P@8 母體可能是合理的加固,不是壞的設計——但它確實不是「沿用既有做法」,是新造判準,而且 spec 沒有交代為什麼只給 lane 而不給 rescued 同等待遇。判不準是否構成「另立新法」,標 ⚠。

引句:「P@8 母體不含 lane」(`/tmp/pin-denoise-a-r2.md:99`)

---

## 結論

不對齊共 **2** 條,其中 major **1** 條:
1.(問一)cap 做法+顯示範圍:rescued 的限量全在「產生階段」算完(`_rescue_n` 缺口計算,`scripts/lumos:14510-14520`),三處輸出(JSON/人讀/hook)都印同一份算好的清單,`impact-hook.py:356-361` 無二次截斷;參考道規劃「JSON 全量+顯示層另砍到 3」(`/tmp/pin-denoise-a-r2.md:66/97`),把限量邏輯搬到顯示層,且把差異化顯示擴大到 rescued 從未觸及的人讀 CLI 這一層,是同一問題的第二種解法。**major**。
2.(問二)`meta` 欄慣例缺口:rescued 家族的既有合約是「逐筆旗標 + `meta.<桶名>` 計數鍵」一起出現,且計數鍵有專屬測試釘住(`test_lumos.py:21753`);參考道的欄位規格(`/tmp/pin-denoise-a-r2.md:97`)與工具清單 #6 的測試計劃(`/tmp/pin-denoise-a-r2.md:101`)全文都沒有 `meta.lane` 或對應測試,只複製了 rescued 慣例的一半。

另有 **2** 條 ⚠ 交編排者判準:
- 欄位命名(lane 字串 vs rescued 布林,`/tmp/pin-denoise-a-r2.md:64`)——若參照對象是 rescued 本身則不對齊,若參照對象是 `results` dict 既有的 `kind` 字串列舉(`scripts/lumos:14428`)則有先例、對齊,判不準。
- eval 口徑改動(`/tmp/pin-denoise-a-r2.md:99`)排除 lane 於 P@8 母體之外——查證 `retrieval_eval.py` 歷史與現況,rescued 從未被顯式排除、只是結構性殿後僥倖迴避,參考道這個改動查無先例可循,且未同步補給 rescued 對稱待遇,是否構成「另立新法」判不準。

（輸出位置、knob 轉正流程文字、`--top` 豁免引用三項查證屬實對齊,不列入不對齊條數。）
