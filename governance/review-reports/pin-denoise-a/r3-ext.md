# 外家否決席審查結果

## Findings

### f1 — blocker — 主案 §2、工具清單 #2b/#7：漏掉 `impact --diff` 這個正式的「非 pinned=free」消費點

引句:「★下游分流全站清單(工具清單 #2b,漏一處就重演舊坑)★」

問題：全 repo 查證後，清單漏了 `cmd_impact_diff`。單檔 `cmd_impact()` 最終仍把 `lane_items` 放進 JSON `results`，而 `cmd_impact_diff()` 會逐檔讀取全部 `results`，再以 `pinned` 布林重新合併成 pins/free；因此 `lane:"soft-guard", pinned:false` 會再次被吃進跨檔 free 桶、參與全域 top 截斷，完全重演 spec 自己宣稱已消滅的舊坑。

這不只是顯示問題：

- lane 會擠掉真正的 diff free 候選，破壞「free 集合與排序完全不動」。
- 超過跨檔 `top` 的 lane 會消失，失去「結構性保留」。
- 同一節點在不同檔案分別成為 lane、pinned 或普通 free 時，現行 merge 只合併 `pinned`，沒有定義 `lane` 的優先序；勝出 entry 可能留下錯誤的 `lane` 身分。
- `sync-check` 也沿用合併後的 pins/free，因此 lane 還會污染落成核對清單。
- 工具清單 #7 只要求修改 code-loop 的文件描述，沒有要求修正實際聚合程式。

查證：

- `scripts/lumos:14523-14528`：單檔 JSON 的 `results` 來源是 `final`；依 spec 將成 `pins + free + rescued + lane_items`。
- `scripts/lumos:14645-14648`：`cmd_impact_diff` 逐檔呼叫單檔 ranked JSON。
- `scripts/lumos:14662-14674`：遍歷所有 `results`，只合併 `pinned`，完全不識別 `lane`/`rescued`。
- `scripts/lumos:14675-14678`：所有 `pinned:false` 再次進 free 並受跨檔 `top` 截斷。
- `scripts/lumos:14691-14702`：`sync-check` 與 diff JSON 都消費這份重新二分的結果。
- `skills/lumos-code-loop/reference.md:93-95`、`:113`：`impact --diff` 是正式 code-loop 審計鏡頭，不是死路徑。

必須把 `cmd_impact_diff`、其人讀輸出及 `sync-check` 納入 #2b，定義跨檔 lane 去重、lane/pin/free 身分優先序、獨立 cap 與輸出位置，不能只改文件。

---

### f2 — major — 主案 §3、落地驗收、尺：`must_in_out` 同時被宣告「可能下降」與「不變」

引句:「must_in_out:不變(測試釘:被降節點仍在 JSON results)」

問題：這與 §3 的明文行為互相矛盾。§3 已承認 cap 砍掉的必看節點會離開 JSON、令 `must_in_out` 下降並由棘輪攔截；但落地驗收及〈尺〉又要求 `must_in_out` 不變、被降節點仍在 JSON。實作者無法判定驗收究竟是：

1. 所有被降節點都必須保留；
2. 只有 cap 內節點保留；
3. aggregate `must_in_out` 不退，但允許個別必看互換；
4. 允許下降，只要求棘輪變紅、禁止轉正。

這會直接造成測試選擇性實作：只做一個 lane 數量未超 cap 的 fixture，就能讓「被降節點仍在 JSON」通過，卻完全沒有驗證真實的 `lane_dropped > 0` 召回風險。

查證：

- spec §3 行 83：「被 cap 砍的必看會誠實掉數字、棘輪抓得到」。
- spec 落地驗收行 98：「must_in_out:不變」。
- spec〈尺〉行 129：「must_in_out:結構性不退(被降者仍在輸出)」。
- `governance/eval/retrieval_eval.py:353-357`：`must_in_out` 按完整 JSON `res` 的 node 集計數；被 cap 移除即確實下降。
- `governance/eval/retrieval_eval.py:473-505`：棘輪只負責比較最近同 rev PASS，並不提供「結構性不退」。
- `governance/eval/retrieval_eval.py:611-622`：下降會讓整體 gate FAIL，不是可接受但提示的狀態。

應將驗收拆成兩條精確合約：cap 內逐節點必存在；cap 外必誠實不存在且同 rev 棘輪必翻紅。若產品要求候選臂必須轉正，還需明說一旦真 goldset 必看超過 cap，候選臂就是失敗，而不是靠重立基線放行。

---

### f3 — major — 落地驗收、工具清單 #4b：`pin_noise` 棘輪沒有可實作的基線、split 與啟用協定

引句:「pin_noise 現況只印不閘——工具清單 #4b:進 verdict+gate「不准變多」,knob 轉正時啟用」

問題：「不准變多」沒有定義跟誰比，也沒有交代如何在 `LUMOS_IMPACT_HARD_PIN` 預設 0 的情況下保存候選臂證據。現行 history 沒有 `pin_noise` verdict 欄，現行棘輪只讀同 rev、同 split、最近 PASS 的 `must_in_out_count`。若照「`must_ratchet` 旁」仿作，至少仍有下列未決事項：

- 比較 knob=1 與同次 knob=0，還是跟歷史最近 PASS？
- gate 用 all、train、held，還是 per-split 全部不得增加？
- 預設 0 的一般週閘是否寫入舊制基線；何時才算「knob 轉正時啟用」？
- 候選臂若因其他既有 gate FAIL，能否成為下一輪 pin-noise 基線？
- 主目標是降低噪音，卻只規定「不准變多」；舊制持平也能通過，沒有候選臂勝出條件。

因此 #4b 目前不是可直接落地的工具項，且可能讓死碼臂在沒有有效對照的首輪自建基線後通過。

查證：

- `governance/eval/retrieval_eval.py:417-420`：現行 `pin_noise` 只加總並印出。
- `governance/eval/retrieval_eval.py:421-438`：verdict 未保存 `pin_noise`。
- `governance/eval/retrieval_eval.py:473-505`：現有 ratchet 的基線語意只為 `must_in_out_count`。
- `governance/eval/retrieval_eval.py:594-604`：現行 gates 使用 `all`，另只取 held 的 search lift。
- `governance/eval/retrieval_eval.py:611-618`：must 棘輪目前只選 `args.split or "all"`，不是 per-split 全比。
- `governance/eval/retrieval_eval.py:648-650`：只有整輪 gate 判定後才以該 `pass` 狀態寫 history。

必須在 spec 定義 pin-noise 的 history 欄位、基線資格、split、A/B 執行方式及轉正判準，而不只是給一個鄰近函式錨。

## 逐節結論

- 症狀：已讀，無 finding。
- 診斷：已讀，合約值域與字面條件核對相符；`_impact_contract` 的實際優先序為 `IRREVERSIBLE > INVARIANT > RISK·<tag值>`，見 `scripts/lumos:13872-13907`。
- 反事實：已讀，無 finding。
- 主案 §1：已讀，無 finding。現行 indirect 保送字面條件確為 `if contract and hop <= min(eff_depth, _pin_hop)`，見 `scripts/lumos:14457-14467`；direct 的 RISK 仍會固定，見 `scripts/lumos:14451-14456`，符合「direct 不動」。
- 主案 §2：有 f1。
- 主案 §3：有 f1、f2。
- 主案 §4–§5：已讀，無另立 finding。
- 落地驗收：有 f2、f3。
- 工具清單 #1–#6：有 f1、f3。
- 工具清單 #7–#9：#7 有 f1；#8/#9 的前案錨與範圍可定位，無另立 finding。
- 已試已殺、PRIOR-ART、審計紀錄 r1/r2、下一步：已讀，無另立 finding。

## 實務隱患

- 守衛面：有。f1 會讓 code-loop diff 鏡頭與 sync-check 重吃 lane，破壞本案宣稱的隔離保證。
- 回滾：無新增否決級問題；只要所有 lane 產生及下游行為確實包在同一 `LUMOS_IMPACT_HARD_PIN` 分支，knob=0 可回舊制。但 f1 所缺的 diff 聚合改動也必須受同一開關控制。
- 效能：無否決級問題。lane 在單檔產生端 cap=3，沒有新增讀盤；主要新增成本是少量排序與 JSON 欄位。
- 併發：無否決級問題。現行流程為行程內局部 list/dict 聚合，spec 未引入共享可變狀態或跨行程寫入。

最嚴重 severity：blocker
