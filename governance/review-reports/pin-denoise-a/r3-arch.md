# pin-denoise-a r3 架構對齊審查

被審:`/tmp/pin-denoise-a-r3.md`(固定席降噪A層_計劃,172 行)。★只審 r2 折入 delta:主案 §2 參考道(獨立容器/產生端 cap/meta 欄/分流清單)、工具清單 1-9、落地驗收改寫★,只判「跟本專案既有做法一不一致」,不找 bug、不評風格。對照對象:`scripts/lumos` 的 `rescued` 第三桶(獨立容器/`_rescue_n` 產生端限量/meta 計數/三處輸出)、`LUMOS_IMPACT_LANE_N` 命名與轉正流程 vs `BASENAME_MATCH`/`RESCUE_N`、lane 排序鍵 vs `free.sort` 慣例、`lane_dropped` 未列出提示 vs 既有 `meta.truncated` 顯示慣例、eval 排除明文化(含 rescued)的風險。

背景:r2-arch(`governance/review-reports/pin-denoise-a/r2-arch.md`)曾對 v2 的參考道判過 major——cap 做在「顯示層」而非「產生階段」,且 `meta.lane` 計數缺席。r3 主案 §2 明文自稱已修:「★cap 在產生階段★(arch r2:rescued 的限量就在產生端,三處輸出同一份)」(`/tmp/pin-denoise-a-r3.md:66`)、補了 `meta["lane"]` 計數(`/tmp/pin-denoise-a-r3.md:70`)。本輪查證這個修法是否真的照著 rescued 的既有機制走,以及折入過程有沒有帶出新的不對齊。

---

## 問一:參考道的容器/cap/knob 命名,是否真的照 rescued 既有機制走

**容器位置與產生端 cap★對齊★。** rescued 現行機制:`_rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))`(`scripts/lumos:14510`)在產生階段算出缺口 `_need = max(0, _rescue_n - _free_direct)`(`scripts/lumos:14512`),只把 `dropped[:_need]` 塞進獨立 list `rescued`(`scripts/lumos:14507-14520`),再一次性併入 `final = pins + free + rescued`(`scripts/lumos:14523`)。JSON(`out_obj["results"] = final`)、CLI 人讀(`for r in final:` 迴圈)、hook(`build_ranked_context` 讀 `data["results"]`,即序列化後的同一個 `final`,見 `scripts/hooks/claude/impact-hook.py:339-341`)三處消費的是同一份算好的清單,沒有任何一處對 rescued 再做顯示層二次截斷。spec §2「收進獨立 `lane_items`;★cap 在產生階段★...`LUMOS_IMPACT_LANE_N`(預設 3,考卷網格轉正)...截斷後這一份=JSON=人讀=hook」(`/tmp/pin-denoise-a-r3.md:66-68`)與工具清單 #2「`final = pins + free + rescued + lane_items`」(`/tmp/pin-denoise-a-r3.md:109`)逐項對得上——r2-arch 抓到的「顯示層截斷」major 這輪確實改成了產生端一次性 cap,容器位置、產生時機、三處同源三個維度都對齊,r2 那條 major 不再成立。

**knob 命名慣例★對齊★。** `LUMOS_IMPACT_LANE_N` 沿用 `LUMOS_IMPACT_RESCUE_N` 同一組命名模式(`LUMOS_IMPACT_<桶名>_N`,整數上限旋鈕),不是另立新前綴,這一項沒有問題。

**「考卷網格轉正」標籤本身缺證據,跟既有轉正慣例對不上,⚠判不準。** 兩個既有旋鈕轉正時都附具體數字:`LUMOS_IMPACT_BASENAME_MATCH` 明文「2026-08-07 轉正預設 1;0=逃生/A 臂」(`scripts/lumos:13815`,呼叫點 `scripts/lumos:13830` 再註一次「2026-08-07 考卷轉正預設 1」);`LUMOS_IMPACT_RESCUE_N` 附完整 train/held 數字:「train 網格 {1,2,3} recall 軸選出;held 確認 Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠」(`scripts/lumos:14502-14509`)。而 spec 對 `LUMOS_IMPACT_LANE_N` 只寫「預設 3,考卷網格轉正」(`/tmp/pin-denoise-a-r3.md:67`),沒有附任何 train/held 數字。更矛盾的是同一份文件的落地驗收段明寫「★驗收不押絕對值★...以 `LUMOS_IMPACT_HARD_PIN=1` 臂的考卷實測為準(Codex r2 f3:預設 0 是死碼,驗收必須明寫在候選臂上跑)」(`/tmp/pin-denoise-a-r3.md:96`)——總開關 `LUMOS_IMPACT_HARD_PIN` 本身還是「預設 0、上線即死碼、驗收未跑」的階段(`/tmp/pin-denoise-a-r3.md:86-87`),參考道整段又包在這個開關裡(`/tmp/pin-denoise-a-r3.md:88`),邏輯上不可能已經跑出 held 驗證數字來把 `LANE_N=3` 標成「轉正」。不能排除 spec 外部真的存在一份離線網格記錄只是沒抄進來,故標 ⚠,不計入下方對齊條數。

引句:「`LUMOS_IMPACT_LANE_N`(預設 3,考卷網格轉正)」(`/tmp/pin-denoise-a-r3.md:67`)

---

## 問二:lane 排序鍵 `(-score, node)` 少了 hop,是刻意還是漂移

**不對齊,minor。** `free.sort` 的既有 tie-break 鍵是三元:`free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))`(`scripts/lumos:14487`)。rescued 自己的 `dropped.sort` 完全複製這個三元鍵:`dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))`(`scripts/lumos:14517`),旁邊註解也明寫「tie-break 沿 free.sort 慣例 (-score, hop, node)」(`scripts/lumos:14501`)——這是本專案唯一一條被兩處獨立實作重申過的排序慣例。spec §2 卻把 lane 的排序鍵寫成二元:「內排序鍵 `(-score, node)`(同 free tie-break 慣例)」(`/tmp/pin-denoise-a-r3.md:67`)——字面上少了中間的 `hop`,但又自稱「同 free tie-break 慣例」,這句引用跟既有慣例的實際內容對不上,是可以直接核對出來的事實錯位,不是猜測。

至於是刻意化簡還是單純漏抄,判不準,標 ⚠:lane 目前的候選來源被 §1 收窄在「indirect 且 `hop ≤ min(depth, LUMOS_IMPACT_PIN_HOP)`(現行預設 1)」(`/tmp/pin-denoise-a-r3.md:60`)才會被降入 lane,若這個上限維持在 1,實務上 lane 內節點的 hop 值可能天生同質、第三鍵恆平手可省;但 spec 自己在同一段標了「★範圍隱性綁這顆旋鈕,動它要重跑考卷★」(`/tmp/pin-denoise-a-r3.md:60`),也就是承認 `PIN_HOP` 未來可能變動——一旦變動,lane 內就會出現 hop 不同的節點,屆時少了 hop 這一鍵會讓同分節點的排序跟 free/rescued 的既有慣例不一致。文件裡沒有任何一句話對「為什麼省略 hop」做解釋,跟這份 spec 對其他每個設計選擇幾乎都附理由的風格不符,較像是漏抄而非刻意化簡,但不能排除是刻意的,故仍標 ⚠。

引句:「排序鍵 `(-score, node)`(同 free tie-break 慣例)」(`/tmp/pin-denoise-a-r3.md:67`)

---

## 問三:`lane_dropped` 顯示慣例 + eval 排除明文化(含 rescued),有沒有動到既有行為

**`meta["lane_dropped"]` 命名跟既有 `meta["truncated"]` 顯示慣例分裂,minor。** 既有慣例裡,「自己這個桶因為上限被砍掉幾條、要不要告訴使用者」只有一種命名與呈現方式:`truncated = max(0, len(free) - min(int(top), _quota))`(`scripts/lumos:14496`,free 名額截斷),CLI 人讀分支印「`(+{meta['truncated']} 條低分截斷;--json 全量)`」,hook 印「`(+{meta['truncated']} 條低分截斷,沒列出來)`」(`scripts/hooks/claude/impact-hook.py:362-363`)——欄位名固定叫 `truncated`。rescued 反而完全沒有這種「未列出提示」:rescued 被 `_need` 砍掉的候選(`dropped[_need:]`)既不進 `meta`,也不在 hook 的 rescued 小節(`scripts/hooks/claude/impact-hook.py:356-359`)留下任何「還有 N 條沒列出」的字樣,是靜默捨棄。spec 對 lane 選的是第三種寫法:新開一個欄位名 `meta["lane_dropped"]`,搭配 hook 新提示「另有 N 條守衛面參考未列出」(`/tmp/pin-denoise-a-r3.md:70-71`,工具清單 #3 錨定 `build_ranked_context`,`/tmp/pin-denoise-a-r3.md:111`)——語意上跟 `truncated`(自己這桶被 cap 砍掉的計數,曝光給使用者)是同一件事,卻換了個新詞彙 `dropped`,沒有沿用 `truncated` 這個唯一的既有命名。這不是功能上的分歧(呈現風格、觸發時機都學 `truncated` 那一套,不是學 rescued 的靜默捨棄),純粹是詞彙沒對齊,列為不對齊但不到 major。

引句:「`meta["lane_dropped"]` 被 cap 砍的條數」(`/tmp/pin-denoise-a-r3.md:70`)

**`eval_edit` 與 `_touched_edit` 對 rescued 的排除不同步,同一模組內「free」被拆成兩種定義,major。** 現狀:`governance/eval/retrieval_eval.py` 裡兩個函式對「free」的計算目前是同一行字重複兩次——`eval_edit` 用 `free = [x for x in res if not x.get("pinned")]`(`governance/eval/retrieval_eval.py:336`),`_touched_edit` 用一模一樣的 `free = [x["node"] for x in res if not x.get("pinned")]`(`governance/eval/retrieval_eval.py:161`)。因為 rescued 的 `pinned` 恆為 `False`,這兩處目前都把 rescued 隱性算進「free」——`eval_edit` 拿它進 P@8/nDCG 母體,`_touched_edit` 拿它進消融閘的觸及集(只取 `free[:k]`)。

spec 的工具清單 #2b 對這兩個函式分開下了兩條不同的修法:「`retrieval_eval.py` `eval_edit` free 分流(★排除 lane,並順手把 rescued 的排除釘成明文——它現在被算進 P@8 母體只是僥倖沒進前 k,s2f5★)」對 `_touched_edit` 只說「`retrieval_eval.py` `_touched_edit`(消融閘的觸及集:lane 視同 pins 無條件納入未標檢查,否則安全網覆蓋縮水,s1f4/s2f2)」(`/tmp/pin-denoise-a-r3.md:75-76`);工具清單本表同一列再確認一次:「eval `eval_edit` 排除 lane★並把 rescued 排除釘明文★/`_touched_edit` lane 視同 pins 納入」(`/tmp/pin-denoise-a-r3.md:110`)。兩處文字都只在 `eval_edit` 這一側明文把 rescued 一併排除,`_touched_edit` 那一側只提到 lane、完全沒提 rescued。改完之後,`eval_edit` 的 free = 「非 pinned、非 lane、非 rescued」,`_touched_edit` 的 free 卻還是「非 pinned、非 lane」(rescued 仍隱性算入)——本來靠一行相同程式碼機械維持同步的兩個函式,這次改動後對「free」產生兩套不同定義,是同一個概念在同一個檔案裡的第二種做法,不是延續既有的單一定義。

**eval 排除明文化本身是否需要自己的獨立驗證,⚠判不準。** `eval_edit` 這處改動不只影響本案新造的 lane 分支,還會改變 rescued 這個既有、已上線功能在既有 goldset 全部題目上的 P@8/nDCG 計分母體(`n_free`/`n_rel_free`/`kk = min(k, len(labels))`),不是本案新功能的局部改動。spec 自己也承認這件事目前只是「僥倖」不出事:「它現在被算進 P@8 母體只是僥倖沒進前 k」(`/tmp/pin-denoise-a-r3.md:75`)。工具清單 #6 的測試計劃①-⑧(`/tmp/pin-denoise-a-r3.md:115`)裡,唯一沾到這件事的是②「P@8 母體不含 lane(含 `_touched_edit` 口徑,s2f2)」,沒有任何一項專門驗「純 rescued、不含 lane 的既有案例,P@8/nDCG 數字改動前後一致」。落地驗收段的「P@8/nDCG:逐 byte 相同(測試釘)」(`/tmp/pin-denoise-a-r3.md:98`)理論上會把任何回歸一併攔下,但那是全案整體對照,不是針對「單獨把 rescued 排除這一刀」的隔離驗證——若真的翻紅,不容易單獨歸因是 lane 邏輯的問題還是 rescued 排除的問題。這算不算需要自己單獨一張考卷,還是既有的整體逐 byte 閘已經夠用,判不準,標 ⚠,不計入下方對齊條數。

引句:「`eval_edit` 排除 lane★並把 rescued 排除釘明文★/`_touched_edit` lane 視同 pins 納入」(`/tmp/pin-denoise-a-r3.md:110`)

---

## 結論

不對齊共 **3** 條,其中 major **1** 條:

1.(問三)`eval_edit` 與 `_touched_edit` 對 rescued 的排除處理不同步:改動後同一檔案裡「free」出現兩種定義(`governance/eval/retrieval_eval.py:161` vs `:336`),是同一概念的第二種做法。**major**。
2.(問二)lane 排序鍵 `(-score, node)` 少了 `hop`,跟自稱的「同 free tie-break 慣例」(`scripts/lumos:14487`/`14501`/`14517` 皆為三元鍵)字面對不上。
3.(問三)`meta["lane_dropped"]` + hook「另有 N 條...未列出」用了新詞彙,沒有沿用既有的 `meta["truncated"]` 命名(`scripts/lumos` 的 truncated 欄位與 `impact-hook.py:362-363` 的顯示行是本專案唯一一套「自己這桶被砍幾條、要不要告訴使用者」的既有寫法)。

另有 **2** 條 ⚠ 交編排者判準:
- `LUMOS_IMPACT_LANE_N`「考卷網格轉正」標籤沒附 train/held 具體數字,跟 `BASENAME_MATCH`/`RESCUE_N` 的轉正慣例(兩者皆附實測數字,`scripts/lumos:13815`/`14502-14509`)對不上,且總開關 `LUMOS_IMPACT_HARD_PIN` 本身仍在「預設 0、驗收未跑」階段(`/tmp/pin-denoise-a-r3.md:86-87`/`96`),邏輯上難以已經跑出轉正證據——但不能排除 spec 外部確有離線網格紀錄。
- `eval_edit` 排除 rescued 這個改動,實質上改變了既有已上線功能(rescued)在全部既有 goldset 案例上的 P@8/nDCG 計分母體,工具清單 #6 的 8 項測試裡沒有專門隔離驗證這一刀是否真的無影響,只能靠全案整體的「逐 byte 相同」大閘覆蓋——這算不算行為變更、要不要自己單獨一張考卷,判不準。

(容器位置、產生端 cap 時機、三處輸出同源、knob 命名模式四項查證屬實對齊,r2-arch 抓到的 major 這輪確認已修,不列入不對齊條數。)
