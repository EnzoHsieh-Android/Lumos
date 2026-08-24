---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「開」)——held 固定席噪音 96 條(live 口徑;考卷 82)佔比過半,out_top3_must held 0.083 被它拖死。逐條分解:58 條=「間接一跳+RISK 類軟合約」樞紐筆記(pitfalls-code-loop 7x/lumos-cli-read 6x/lumos-refcheck 6x…)搭便車
  KEY:★v2(r1 五席打掉 v1 後改)★主案=間接保送只認 INVARIANT/IRREVERSIBLE;被降的 RISK 類 indirect 進**獨立參考道**(不佔固定席、不進自由席計分/門檻/名額、輸出尾端標「守衛面參考」上限 3 條)。★about/治標籤全退出本案★(v1 的豁免=翻前案已鎖決策+兩條測試機械擋+在震央 scripts/lumos 撞巨檔門檻必死;治標籤=把 impacts 語意塞進 about 欄)。參考道使 P@8 逐 byte 不變、must_in_out 結構性不退
  KEY:已試已殺留痕——扇出二元砍除(2026-08-23):P@8 +5 格但必看 26→23 被棘輪擋;勿憑直覺復活,重試須過同款考卷
  KEY:尺=固定席噪音數(主目標;★不押絕對值,以 knob=1 臂考卷實測為準★)+ P@8 逐 byte 不變(結構保證)+ must_in_out 不退(結構保證)+ out_top3_must 應升;★本案凍結 goldset 標籤★(Codex f4:改標籤→換 rev→棘輪重立基線,守衛蒸發);per-split 棘輪與 eval/hook top 口徑錯位(PPR 案舊坑)列工具清單;症狀指令見正文
  DEP:[[Projects/固定席扇出降權_計劃]]｜[[Systems/retrieval-ranking]]
plan_refs: []
related:
  - "[[Projects/固定席扇出降權_計劃]]"
  - "[[Systems/retrieval-ranking]]"
tags:
  - type/project
  - status/doing
decisions:
  - content: 三輪達上限後裁甲:開新編號 pin-denoise-a-v4 再審一輪 delta(獨立 JSON 鍵安置模型+r3 折入)
    id: d1
    context: r3 折入的核心修法(lane 用 JSON 獨立頂層鍵)是折入時新定、沒有審查員看過;動的是 hook 機械保證面;安置模型正是本案連續三輪被打的同一類洞
    why_chosen: 一輪成本低;新結構決定該有沒脈絡的眼睛看過再動手
    decided: 2026-08-24
    valid: true
---
# 固定席降噪A層_計劃

> 白話:改程式時 hook 會推「必看」筆記,其中一半以上是不相干的——因為有一批 CLI 樞紐筆記
> 掛著「守衛面」這種**軟**標記、又跟每支檔都只隔一跳,每一題都被無條件保送進固定席。
> 修法:保送只認「改了就壞」的硬合約;軟標記的要嘛有語意證據(about 命中)才留,要嘛下去排隊。

## 症狀(會翻紅的指令;2026-08-24 實測)

```
python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json --ablation
```
看「固定席裡不相干的筆記」:held **82 條**(live 口徑 96)、train 15;「輸出前 3 名是必看的比率」held **0.083**。
本案成功=held 固定席噪音顯著降、must_in_out 棘輪不退、out_top3_must held 上行。

## 診斷(2026-08-24,live 口徑逐條分解)

| 分解 | 數字 |
|---|---|
| 噪音 96 條按路徑 | incident 15 / direct 23 / **indirect 58(60%)** |
| 按合約 | **RISK·守衛面 56** / INVARIANT 22 / 無(事故)15 / RISK·不可逆 3 |
| 重複犯 | pitfalls-code-loop 7x、lumos-cli-read 6x、lumos-refcheck 6x、anchor-integrity 4x…(CLI 樞紐,圖上跟誰都一跳) |

**根因**:間接保送條件=「有合約且 hop≤1」——★任何類的合約都算★。「RISK·守衛面」是提醒級的軟標記
(掛在幾十篇 Systems 上),不是「改了就壞」的硬承諾;拿它保送=樞紐筆記全票通過。

## 反事實(2026-08-24 離線算,同一批題)

**R1:間接保送只認 INVARIANT/IRREVERSIBLE;RISK 類間接降自由席。**

| | 噪音會降 | 必看會降 | 有用會降 |
|---|---|---|---|
| train | 7/20 | **0/10** | 5/11 |
| held | **43/96(45%)** | **★3/5★** | 8/13 |

被誤降的必看 3 條:E06/E12 `anchor-integrity`(守**所有** hook,about_code 卻只標 pre-push)、
E08 `design-loop`(管自主迴圈測試,about 沒標 test_autonomous_loop)——★全是 about 漏標受害者★。

## 主案 v2:硬合約保送 + 參考道(r1 五席折入後版;v1 的 about 豁免/治標籤已整段作廢,見審計紀錄)

1. **間接保送收窄**:indirect 且 `hop ≤ min(depth, LUMOS_IMPACT_PIN_HOP)`(現行預設 1;★範圍隱性綁這顆旋鈕,動它要重跑考卷★,s2f4)的節點,
   `contract in ("INVARIANT", "IRREVERSIBLE")` 才保送固定席;`RISK·*` 類(值域=`_RISK_ENUM` 四值,錨:`def _impact_contract`)不再保送。
   direct 保送不動(direct 噪音 23 條另案;一次一刀可歸因)。
   ★併名陷阱(s2f2)★:`RISK·不可逆`(軟標籤)與 `IRREVERSIBLE`(硬合約)是兩個機制、中文撞名——實作用字串精確比對,文件裡兩者並列時必註明。
2. **參考道(reference lane)——★r2 折入版:獨立容器+產生階段 cap★**:被 1 降的節點★自始不進 `results` 共用清單★
   (s1/s2 各自實測:`pinned:False` 會被四處既有「非 pinned=free」分流吃回自由席,把門檻拉高、真候選被擠光),
   收進獨立 `lane_items`;★r3 釘死安置模型(s2f1 blocker:「不進 results」與「final=...+lane_items」自相矛盾)★:
   **JSON 輸出用獨立頂層鍵 `"lane"`,`results` 完全不含 lane**——沒學過 lane 的既有讀者
   (★`cmd_impact_diff` 聚合(三席 r3 同抓的漏網消費點,code-loop 在用)、hook free 桶、`_bound_tests_for_diff`★)
   結構性不受影響;要用 lane 的地方**明文 opt-in**(名單見 #2b)。★diff 聚合明文:lane 不進 --diff 清單與 sync-check★
   (軟參考不屬代碼審波及口徑;測試釘)。
   ★cap 在產生階段★:`LUMOS_IMPACT_LANE_N`(預設 3,考卷網格轉正——轉正數字待跑,同 HARD_PIN 一起)內
   排序鍵 `(-score, hop, node)`(★同 free/rescued 三鍵慣例,arch r3:漏 hop 是漂移★),
   截斷後這一份=JSON `lane` 鍵=人讀=hook,兩個口徑合一——被 cap 砍掉的必看會真的掉 must_in_out,棘輪有效。
   欄位:`lane: "soft-guard"`、`pinned: False`;★score=indirect 自由席同款 R 公式(0.60L+0.40G)★
   (s1f2:原「保留原 score」=舊保送分支的常數 0.70,全員同分,cap 挑誰退化成字母序——改用 R 公式才有鑑別力,
   也才真的是「rescued 慣例」的分數精神);`meta["lane"]` 計數、`meta["lane_truncated"]` 被 cap 砍的條數
   (★命名沿既有 `meta.truncated` 慣例,arch r3★;hook 顯示「另有 N 條守衛面參考未列出」)。
   ★opt-in 名單(#2b;獨立鍵模型下「不改就不受影響」,要 lane 的才改)★:
   ①`cmd_impact` 人讀純文字分支加 lane 小節(★lane 項的 `kind` 保留原值 indirect,lane 是欄位不是 kind;人讀 kind 表不加 lane,由獨立小節顯示★,v4 s2f5;score 用 `.get`)
   ②hook `build_ranked_context` 新小節讀 ★`data.get("lane", [])`★(v4 arch/s1:條件鍵,`data["lane"]` 會在 knob=0 的常態下每次編輯 KeyError、打破 hook 永不擋人鐵則;
   照 `query_gated`/`stack_questions` 條件鍵慣例+兩態測試);★hook 的空判斷閘(現只看 results/stack_questions 全空就 return)要加看 lane★
   (v4 Codex f2:lane-only 的題會整個不注入)
   ③`retrieval_eval.py` `edit_universe`:★回傳形狀定死(v4 s1f3/s2f3)★——合併清單(lane 項保留 `lane` 欄位標記),
   下游一律用明文鍵過濾:`free` 排除 `lane`(★只排 lane;rescued 不排——v4 arch 考古:rescued 進 P@8 母體是 2026-08-07 決策紀錄裡
   具名護欄「誠實計噪」的刻意設計,r2 那句「僥倖」是把上輪 ⚠ 當事實,撤回★)
   ④`eval_edit`:★只動兩處★——`out_nodes`/`must_in_out` 讀 results ∪ lane(cap 內計入),`free` 明文排除 lane(不排 rescued,理由見③)——
   ★不准整段先濾 res★(順手全濾會讓 must_in_out 永久漏算 lane、棘輪失義;測試⑨釘)
   ⑤`_touched_edit`:lane 視同 pins 納入未標檢查——與 eval_edit 共用同一個分桶 helper(同檔一種 free 定義)
   ⑥★`build_goldset.py` `edit_pool`(v4 三席同抓的第六個讀者)★:未來出題的候選池要含 lane(人看得到的都該能被標),測試釘
   ⑦★混版相容協定(v4 Codex f4)★:新 hook 全 `.get` 讀舊 CLI=安全退化;舊 hook 配新 CLI 在 lane-only 情境=不注入(退化不炸,可接受);
   hooks 由 install 同步機制保底,落地 commit 註明「hook 與 CLI 同批更新」。
   ★為什麼不是降自由席★(r1 的血):有動態門檻+名額,被降的會被整個砍出輸出——前案「降級≠保留」舊坑;參考道=結構性保留。
   ★為什麼不是 about 豁免★:翻前案已鎖決策+兩條測試機械擋+巨檔門檻讓豁免在震央必死——r1 三票否決,v1 作廢。
   ★為什麼不擴 rescued★(arch r1 ⚠):語意不同(缺口補席 vs 整類降級保留),實作同家族——獨立容器、產生端限量、
   不過門檻名額、meta 計數四個維度照 rescued 慣例;★輸出位置刻意偏離(rescued 在 results 內帶布林旗標,lane 用獨立頂層鍵)★,
   理由=沒學過 lane 的讀者結構性安全(v4 arch:頂層鍵有 query_gated/stack_questions/sync 先例,但「候選節點陣列開頂層鍵」是首例——留痕,這是刻意的第二種做法)。
3. **結構保證(r2 誠實化)**:free 集合與排序完全不動 → P@8/nDCG 逐 byte 不變——★前提是 §2 的獨立容器與全站分流清單一處不漏★
   (s1 實測:漏任何一處,不是灌爆 free 就是 lane 消失);測試逐 byte 釘。
   must_in_out:cap 內結構性不退;★被 cap 砍的必看會誠實掉數字、棘輪抓得到★(這是口徑合一的代價與好處)。
   固定席噪音降幅:★「降誰」對 indirect 是決定論,但 incident/indirect 歸類會隨 delta 變(s1f3:同一節點不同改動下可能走事故路徑)——
   43/96 是無 query 口徑的近似,驗收不押絕對值★,以落地後考卷實測+pin_noise 棘輪為準(Codex r2 f3;82-43=39 的減法也不成立,s1f5)。
4. **總開關**:`LUMOS_IMPACT_HARD_PIN`,★預設 0(上線即死碼)★(s2f9:預設問號沒法審)——
   照 `LUMOS_IMPACT_BASENAME_MATCH` 轉正流程:train 網格、held 驗一次、gate 全過才轉預設 1;0=舊制逃生。
   參考道整段包在 knob=1 分支內(s2f13:單開關回滾逐 byte)。
5. **goldset 標籤本案凍結**(Codex f4):不補標、不改答案——改了 rev 就換、棘輪重立基線,守衛蒸發。
   E06/E08/E12 那 3 條(加 s1f2 抓的另外 12 處)的「必看但 about 不含」證據★不是 about 漏標★(Codex f1:
   anchor-integrity 的 about 只標 pre-push 是**對的**,它「影響」全部 hook 是另一個語意)——
   整批記進 [[Projects/固定席扇出降權_計劃]] 的 impacts_code 後案當語料,本案不動欄位。

## 落地驗收(照症狀指令)

- 固定席噪音:★驗收不押絕對值★(近似估計 held -40% 上下)——以 `LUMOS_IMPACT_HARD_PIN=1` 臂的考卷實測為準;
  ★pin_noise 棘輪協定(Codex r3 f3:「進閘」三個字不可實作)★:per-split、基線=knob 轉正那輪 PASS 的實測值、
  gate 只在轉正後啟用、方向「不准變多」——全部明寫進 #4b。
- ★must_in_out 一句話講死(Codex r3 f2:原文同時寫「不退」與「可能掉」)★:cap 內結構性不退;
  被 cap 砍的會誠實掉數字且棘輪抓——「可能掉」是 cap 的刻意代價,不是 bug;驗收看棘輪不看零變化。
- P@8/nDCG:**逐 byte 相同**(測試釘)。must_in_out:被降節點在 JSON 頂層 `lane` 鍵(cap 內),`must_in_out` 讀 results ∪ lane 計入
  (★v4-r1 五席同抓:原句「仍在 JSON results」是 r3 前殘句,與獨立鍵模型互斥——r3 審計帳宣稱「已統一」實未改,這次真改★)。
- out_top3_must held 0.083→應升(觀測)。
- ★eval/hook top 口徑錯位(r1 s2f12,PPR 案舊坑)★:參考道不受 `--top` 截斷(同 rescued;s2 查證屬實)→ 錯位不影響本案;
  per-split 棘輪列工具清單——★實作落點是 `main()` 呼叫端(現行只比 "all"),`must_ratchet` 函式本身已支援 split(s2 查證)★。
- **效能觀測**(s2 補充):lane JSON 全量會加大 `impact --json` payload(樞紐檔常態 >3 條被 cap 擋住,體積可控),落地時量一次留數字。

## 工具清單(草)

| # | 項目 | 錨 |
|---|---|---|
| 1 | indirect 保送條件加 contract 值過濾(knob=1 時);★被降者收進獨立 `lane_items`,不進 `results`★ | `if contract and hop <= min(` |
| 2 | lane 產生端 cap(`LUMOS_IMPACT_LANE_N` 預設 3,排序 `(-score, hop, node)`;score=R 公式)、`meta["lane"]`/`meta["lane_truncated"]`、★JSON 獨立頂層鍵 `"lane"`,`results`/`final` 不含 lane★ | `out_obj = {"file": rel_file, "results": final` |
| 2b | ★opt-in 名單(獨立鍵模型)★:人讀分支/hook 新小節/`edit_universe` 帶出 lane 鍵/`eval_edit`(free 排除 rescued 明文;out_nodes ∪ lane;★不准整段先濾★)/`_touched_edit` 共用分桶 helper;★diff 聚合與 sync-check 明文不含 lane(測試釘)★ | 各檔 grep `not x.get("pinned")` + `cmd_impact_diff` |
| 3 | hook 顯示新小節「守衛面參考(軟標記樞紐,未被本次改動直接證實相關)」+「另有 N 條未列出」 | `build_ranked_context` |
| 4 | eval:P@8 母體排除 lane(含 rescued 明文化) | `eval_edit` |
| 4b | pin_noise 棘輪(v4 s3f2:協定四項寫全)——★per-split;基線=knob 轉正那輪 PASS 實測值;gate 只在轉正後啟用;方向「不准變多」★;進 verdict(r3 Codex f3) | `must_ratchet` 旁 |
| 5 | per-split must 棘輪(呼叫端 `main()` 改,函式已支援) | `must_ratchet` |
| 6 | 測試:①knob=0 逐 byte(★含 JSON 無 `lane` 鍵——條件鍵兩態,照 query_gated 測試慣例★)②P@8 母體不含 lane ③被降者在 JSON `lane` 鍵且 cap 內 ④RISK indirect 不保送(行為測試,#7 改綁這顆)+事故/INVARIANT indirect 不受影響 ⑤翻紅釘:fixture 造「有 lane 候選」場景,斷言 lane 空時 must_in_out 掉(常設回歸寫法,v4 s3f5 定稿)⑥人讀分支不 KeyError ⑦hook 不重複顯示 ⑧lane_truncated>0 警告行 ⑨cap 內 lane 計入 must_in_out 即使不計 P@8 ⑩`cmd_impact_diff`/sync-check 不含 lane ⑪★rescued 仍在 P@8 母體(誠實計噪護欄的回歸,v4 撤回排除後改向)★ ⑫★hook lane-only 有注入、knob=0 不炸★ ⑬`edit_pool` 含 lane 候選 | test_lumos |
| 7 | 文件同步:`Systems/lumos-cli-read.md:14` 句改寫、★改綁 #6③(被降者出現在 JSON lane 鍵的**新行為**測試——v4 s2f2:替代綁定必須測「改了什麼」,#6①④測的是「什麼沒變」不合格)★,舊綁定解除、舊測試 docstring 同步(s1f5);`skills/lumos-code-loop/reference.md:94/113`;`Systems/retrieval-ranking.md`:★除修 `:11`/`:47` 兩句外,加一則帶日期的 KEY 落地紀錄(該節點對 rescued 的既有寫法,v4 s3f4)★ | — |
| 8 | 前案回寫:四處「扇出=A 層降噪主角」標「已由 pin-denoise-a 取代(硬合約+參考道);★扇出**二元砍除**已試已殺,分級降權未試★(s3f4:別把沒試過的設計空間一起封死)」 | 前案 summary/258/393/399-404(s1 r3 核過行號現況準確) |
| 9 | impacts_code 證據轉交(s3f3):E06/E08/E12+s1f2 的 12 處「必看但 about 不含」整批記進前案 impacts_code 後案節 | 前案「下一步:影響欄位」 |

## 已試已殺(留痕,勿復活)

- **扇出二元砍除**(2026-08-23):提到 ≥N 支檔的筆記直接踢出固定席——P@8 +5 格但必看 26→23,棘輪擋下。
  教訓:砍「量大」砍不準;本案改砍「軟合約搭便車」,且 v2 參考道=結構性保留(v1 的豁免/棘輪雙保險說法已作廢)。重試扇出須過同款考卷。

## 尺(v2)

- **固定席噪音數**:主目標;★不押絕對值(82→39 減法已在 §3 作廢,此處 r3 s1f4 抓到殘留)★;棘輪協定見落地驗收。
- **P@8/nDCG**:逐 byte 不變(結構保證+測試釘;v1「應零影響」的講法錯,s2f11)。
- **must_in_out**:結構性不退(被降者仍在輸出);棘輪當覆核。★棘輪現況只比全體、換 rev 重立基線(Codex f4)——per-split 版列工具清單★。
- **out_top3_must**:觀測,held 應升。
- ★數字口徑統一(s2f1)★:主基準=**考卷口徑**(`--ablation` 輸出的 82/15);live 口徑(96)只用於逐條診斷,兩者差=goldset 未收錄的題外 pins。

## PRIOR-ART

`PRIOR-ART: borrow-design`——★誠實版(arch r1 抓到 v1 誤標)★:合約**值域**(INVARIANT/IRREVERSIBLE/RISK·*)是既有語彙
(`_impact_contract`/`_RISK_ENUM`),但「硬/軟**分級**、且分級決定保送」是**本案新造的規則**,全庫無先例
(「軟」在專案裡既有意涵是 doctor 提醒那條軸,別混用)。借的是業界 alerting 的 page vs ticket 同構
(硬約束叫醒人、軟提醒進佇列);參考道借自家 rescued 第三桶模式(同家族第二成員)。零新依賴。

## 實務隱患

- **召回風險**:v2 結構性歸零(被降者不離開輸出;free 不動)。v1 的三層網逐層有洞(豁免死於巨檔、rescue 只救 direct、
  棘輪不分 split)——s2f10 點名的三個洞是 v1 作廢的直接原因,留痕。
- 守衛面:動的是 hook 的機械保證面;走完整 design-loop(前案明文:動 impact 排序 light 硬拒)。
- 回滾:總開關一顆;行為差異=固定席成員變化,測試逐 byte 釘。
- 併發/效能:無新讀盤(合約與 about 都是既有材料)。

## 審計修正紀錄

### r1(2026-08-24;s1/s2/s3 + arch + Codex,五席)
s1 5(2 blocker)/ s2 13(4 blocker)/ s3 8(1 blocker)/ arch 2 major+1 ⚠ / Codex 4(3 blocker)。
★v1 主案被三個承重點打穿,整段作廢改 v2★:
**A about 豁免**=翻前案已鎖乙選項+`about 不是第四條入口` docstring 與兩條測試機械擋(s2f5/s3f1/s3f2/arch)+巨檔門檻讓豁免在震央 scripts/lumos(56 篇>8)必死(s1f1/s2f6/s3f3/Codex f2)→ about 全退,參考道取代;
**B 治標籤**=把「影響」語意塞進 about 欄、汙染前案三輪審出的定義(Codex f1);範圍也錯(15 處非 3,s1f2)→ 退出本案,證據轉 impacts_code 後案;標籤凍結(Codex f4:改標籤→rev 換→棘輪基線蒸發);
**C「降自由席」與「P@8 零影響」**=降級後過不了動態門檻直接被砍出輸出(s1f3 帶真 query 實證;前案舊坑重踩),且降級改變 P@8 計分母體(s2f11/s3f5)→ 參考道:不進 free、不進計分、結構性保留;
其餘折入:hop 綁 PIN_HOP 明寫(s2f4,引句錨不到但自查屬實)、RISK·不可逆/IRREVERSIBLE 撞名註明(s2f2)、knob 預設 0 死碼上線(s2f9)、單開關包住參考道(s2f13)、eval/hook top 口徑錯位——參考道不受 top(s2f12)、per-split 棘輪列工具清單(Codex f4)、hook 文案(s3f4)、文件散落三處(s3f7)、PRIOR-ART 誤標既有語彙改誠實版(arch major1;s2 判值域既有——兩席各對一半)、口徑統一(s2f1)、restamp 連動(s2f8,隨治標籤退出而 moot)。
arch ⚠(要不要擴 rescued)已在主案 v2 §2 正面回答。放行:無。
★教訓:v1 用一小時寫的主案,三個承重點全是「沒對前案已鎖的決策與機械測試」——立案時 `lumos decisions <前案> `+grep 測試,比反事實跑得快更重要。★

### r2(2026-08-24;s1/s2/s3 + arch + Codex,五席)
s1 5(2 blocker,含 patch 副本實測)/ s2 8(3 blocker,含工具清單逐項可執行表)/ s3 3(2 major)/ arch 2+2⚠(1 major)/ ★Codex 4(1 blocker+3 major;r2 紀錄原誤記 3 條、f2/f4 折入時漏署名——r3 s3f1 抓到,此處更正★)。全折:
**A lane 會被「非 pinned=free」分流吃回自由席**(s1f1 實測灌爆門檻+s2f1 四處分流)→ 獨立容器 lane_items+全站分流清單 #2b;
**B JSON/人看口徑偷換**(Codex f1+s2f3 人讀分支 KeyError+arch cap 層級)→ cap 在產生階段、三處同一份、meta 計數+未列出提示、棘輪重新有效;
**C eval 側**(s1f4/s2f2 `_touched_edit` 消融閘覆蓋縮水;s2f5 rescued 被算進 P@8 母體「只是僥倖」——★此判 v4-r1 arch 考古翻案:是具名護欄的刻意設計,排除已撤回★)→ #2b/#4 明文;
**D 驗收數字**(Codex f3 死碼臂+s1f3 incident 歸類隨 delta 變+s1f5 減法不成立)→ 不押絕對值、明寫 knob=1 臂;
**E 文件清單 v2 重推**(s3f1:lumos-cli-read「risk 保送必看」句落地後變假+綁定測試恆綠)、**F 前案扇出框架回寫**(s3f2)、**G impacts_code 轉交進清單**(s3f3)、
meta 慣例(arch)、per-split 落點(s2)、pin_noise 拆句(s2f8)、payload 觀測(s2)。放行:無。
arch ⚠×2:lane 字串命名(kind 先例,採納不改)、eval 排除無先例(以 #2b 明文化+rescued 對稱處理回答)。

### r3(2026-08-24;上限輪;s1/s2/s3 + arch + Codex)
s1 6(2 blocker)/ s2 ★6★(2 blocker;原誤記 5,漏數 f1a——v4 s3f3 抓到,同款計數錯第二次)/ s3 4 major / arch 3+2⚠(1 major)/ Codex 3(1 blocker)。★達上限未收斂★。全折:
**A 安置模型講死**(s2f1 blocker「不進 results」vs「final+=lane」自相矛盾;Codex f1/s1f1/s2f2 三席同抓 `cmd_impact_diff` 這條三輪沒人看過的消費路徑)
→ JSON 獨立頂層鍵 `"lane"`,results 不含;沒學過的讀者結構性安全、要用的 opt-in;diff/sync-check 明文不含+測試⑩;
**B lane score 常數 0.70 無鑑別力**(s1f2)→ R 公式;排序鍵補 hop(arch);
**C eval 精度**(s1f3 順手全濾會讓棘輪失義→測試⑨;arch major 同檔兩種 free 定義→共用 helper;edit_universe 要帶 lane 鍵 s2f1a);
**D 假綠綁定**(s2f3 blocker:綁的測試只測分類函式永遠綠)→ 改綁行為測試+測試 docstring 一起改(s1f5);
**E 作廢數字殘留兩處**(s1f4 blocker:summary KEY 與尺節還寫 82→39)+ must_in_out 矛盾句(Codex f2)→ 統一;
**F pin_noise 棘輪協定明寫**(Codex f3);**G r2 帳 Codex 錯數與漏署名**(s3f1)→ 更正;
**H 扇出措辭**(s3f4:殺的是二元砍除,分級降權未試);文件錨補行號(s3f3);meta 命名沿 truncated 慣例、
LANE_N 轉正數字待跑(arch ⚠,與 HARD_PIN 同輪網格);`_RISK_ENUM` 錨兩點分開指(s1f6)。放行:無。
★三輪走勢:r1 打掉 about 豁免(方向)、r2 打掉降自由席與口徑偷換(機制)、r3 打掉安置模糊與漏網消費點(接線)。
r3 的修法(獨立 JSON 鍵)是折入時新定的,★沒有任何審查員看過★——這是攤給人裁的核心事實。★

### v4-r1(2026-08-24;新編號 pin-denoise-a-v4,人裁甲後;s1/s2/s3 + arch + Codex)
s1 4(2 blocker)/ s2 5(1 blocker)/ s3 5(1 blocker)/ arch 3 major+1⚠ / Codex 4(2 blocker)。全折:
**A 殘句 :116**(五席同抓:「被降節點仍在 results」與獨立鍵模型互斥;r3 帳宣稱已統一實未改)→ 真改;
**B hook 防禦**(arch/s1 `data["lane"]` KeyError 打破永不擋人 + Codex f2 空判斷閘漏 lane → lane-only 不注入)→ `.get`+閘加 lane+兩態測試⑫;
**C rescued 考古翻案**(arch:進 P@8 是 2026-08-07 具名護欄「誠實計噪」的刻意設計,r2「僥倖」是把 ⚠ 當事實)→ 撤回排除 rescued,測試⑪改向;
**D 第六個讀者**(s1/s2/Codex 三席同抓 `build_goldset.edit_pool`)→ opt-in ⑥+測試⑬;
**E edit_universe 形狀定死**(s1f3/s2f3)→ 合併清單+明文鍵過濾;**F 混版協定**(Codex f4)→ opt-in ⑦;
**G #7 替代綁定要綁行為測試**(s2f2)、**H #4b 協定四項寫全**(s3f2)、**I r3 帳 s2 條數 5→6**(s3f3,同款錯第二次)、
**J retrieval-ranking 加帶日期 KEY**(s3f4)、kind 欄不改值(s2f5)、「五維度」句更新+頂層鍵首例留痕(arch)、測試⑤定稿(s3f5)。放行:無。
★教訓兩條:①同一句殘句連三輪五席才真的改掉——「宣稱已統一」要 grep 驗,帳寫了不等於檔改了;
②審計帳條數錯第二次——記帳前逐份數報告檔,不抄上一輪summary。★

## 下一步

v4-r2:審 v4-r1 折入 delta(hook 防禦/rescued 翻案/edit_pool/混版協定)。乾淨即收斂進實作。
