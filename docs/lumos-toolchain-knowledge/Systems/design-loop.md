---
type: system
status: done
created: 2026-06-26
updated: 2026-07-10
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-19_design-loop]]"
  - "[[Verification/2026-07-09_loop三輪壓縮]]"
  - "[[Verification/2026-07-10_審計loop研究硬化]]"
summary: |-
  KEY:[2026-07-10]reviewer 結構紀律明文化——禁互辯/編排者=meta-judge/關鍵單點判決≥3run多數決(EMNLP 2025 實證,見[[Projects/reviewer結構明文化_計劃]])
  FLOW:brainstorming產spec→[trivial?跳並註明]→每輪{複製spec→/tmp/<id>-rN(N=loop_status輪數+1)→植1canary(類型=清單[(N−1)mod4],只進工作副本)→派乾淨審計員(sonnet,連2missed升opus,不告知canary,refute framing)→判讀(canary抓到?+真finding max severity)→辯方refute(對≥major每條派獨立opus構造反證file:line)→該輪severity=辯方存活max→canary record caught|missed→抓到折真finding進真檔(commit前grep canary token須=0)/漏抓不折直接下輪}→loop status --need 2 exit0→收斂+天花板提醒→writing-plans
  KEY:Claude編排,lumos只出原語——Claude用Agent tool派審計員/判讀/修spec;lumos出 canary record/loop status 記錄與算收斂,lumos不spawn agent
  KEY:canary=test-the-tester——每輪偷植已知假錯驗審計員有沒有在認真抓;漏抓(missed)=該輪審計失靈,判決不採信、不折findings(防假陰性/審計員放水)
  KEY:辯方refute=對稱防假陽性——對審計員標≥major的每條finding派獨立opus(乾淨脈絡、不傳審計結論)強制拿file:line反證才能降;辯方只買code層假陽性,業務層留人
  KEY:硬閘是紀律非技術鎖——loop status未CONVERGED不得進實作,但lumos擋不住「不跑就實作」;靠Claude記得調用+誠實+cap/留痕兜底
  KEY:收斂判準K=2——連2輪 caught 且 severity∈{clean,minor};max cap=6筆record,到頂未收斂則停、攤給人
  KEY:實質收斂 early-exit(2026-07-07 Landmark 實戰調參)——連K輪 caught 無 blocker/major 且新 findings 全為文件精度級 minor → 編排者可提前攤牌請人裁「實質收斂」不跑滿 cap(「你一定找得到」framing 使 G2 數字枯竭壓不到底的誠實出口;僅手動 loop,自主 loop 走 unconverged requeue)
  KEY:派工模板權威=skills/lumos-design-loop/templates.md(6角色 dispatch prompt+編排者判讀規則,Landmark 實戰抽取;SKILL 內嵌 framing 是摘要,漂移以模板為準)
  KEY:平行 panel 模式(2026-07-09,≤3輪壓縮,見 [[loop三輪壓縮_計劃]])——買獨立廣度非相關深度:一輪平行 W 個多樣審計員(tier→panel_width);收斂判準改結構信號(輪有效∧存活max≤minor∧capture-recapture殘餘<門檻,無counts=fail-closed)取代 K-streak∧G2 序列;`loop status --gate --panel`;混用守衛防 None phantom 輪;legacy(無--panel)完全不變
  DEP:lumos canary record --loop/--severity｜lumos loop status --need(Component A 原語)｜skills/lumos-design-loop/SKILL.md
  TEST:Component A 原語有 test_lumos.py 覆蓋;B 是 skill 非 code,以 design-loop 自跑收斂為驗證
  VERIFY:[[Verification/2026-06-19_design-loop]]
decisions:
  - content: 收斂判準 K=2(連 2 輪 caught 且 severity∈{clean,minor}),寫進 spec 本體與 loop_status --need 預設;漏抓(missed)仍是一筆 record、仍算進 cap,判決不採信但不消失
    context: design-loop r2 canary 護審計揪出真 BLOCKER:K=2 未敘明於 spec 本體;MAJOR:「作廢」vs「算進 cap」矛盾——漏抓那輪到底算不算一輪定義不一致
    why_chosen: 「輪」「cap」「連續漏抓」全以 canary-log 記錄為準才定義一致,不存在「不記錄的 inline 重跑」;K=2 讓收斂=連 2 輪醒著的審計員沒找到 blocker/major,可觀測且有摩擦
    decided: 2026-06-19
    valid: true
  - content: canary 類型由輪序 N 決定 type=清單[(N−1) mod 4](a 壞§ref／b 未定義旗標／c 未定義欄位／d 未定義產物),無需 state 欄;missed 重跑時 N 已+1 故自動換新類型
    context: design-loop r2 MAJOR:rotation 無 state——若 type 要記憶/查 log 的 type 欄,植入者得自管狀態、易錯且不可審
    why_chosen: 由 N 機械推導 a→b→c→d→a 輪替,免狀態、可從 loop_status 輪歷史重現;canary 校準鐵則=「認真審抓得到但不一眼看穿」(太細不公平、太明顯訊號弱)
    decided: 2026-06-19
    valid: true
  - content: 加辯方 refute 階段(對 ≥major 每條 finding 派獨立 opus、不傳審計結論、強制 file:line 反證才能降),該輪 severity 取辯方裁決後存活 findings 的機械 max,取代編排者自剝誤判
    context: finding-refute 後續 spec(3 輪自動收斂):原 step4「編排者自剝審計員誤判」是沒閉合的迴歸、會放水;canary 防假陰性,但假陽性(審計員過度報警)無對稱守衛
    why_chosen: 辯方=canary 的對稱面(canary 防假陰性/防審計員放水,辯方防假陽性/防過度嚴重度);效力來源是「方向相反的對抗」+ 強制帶 code 證據,而非 code 證據本身;業務層假陽性留人裁
    decided: 2026-06-24
    valid: true
---
# design-loop

`skills/lumos-design-loop/SKILL.md` —— **canary-護的設計審計 loop**,進實作前的硬閘。對齊 lumos 治理的 loop-engineering 方向:讓「每個計畫都先進 loop 打磨、再進最終實作」成為標準路徑。

## 源起
日報 2026-06-18 gap:「內迴圈派 Sonnet 當審計員,卻從沒檢查它這一輪到底有沒有在認真抓。」suggestion 借 Codex『驗收要比迴圈本身可靠』:每輪審計先偷塞一個已知假錯(canary),看審計員抓不抓得到,抓不到代表這輪審計失靈、回報的「乾淨」作廢重跑。此 gap 直接催生 Component A(`canary record` 原語)與 Component B(本 skill,把 canary-護的對抗審計 loop 編排成標準路徑)。

## 定位:Component A / B 分工
- **Component A**(`docs/design/2026-06-19-convergence-recording.md`):lumos 出**原語** —— `lumos canary record --loop/--severity`(寫 `.canary-log.jsonl`)+ `lumos loop status --need`(讀 log 算收斂)。有 `test_lumos.py` 覆蓋。
- **Component B**(本節點 = 本 skill):Claude 的**編排層** —— 用 Agent tool 派審計員、判讀、修 spec。**lumos 不 spawn agent**;Claude 照 SKILL.md 跑程序。

## 每一輪的程序(SKILL.md §「每一輪」)
1. 複製 `docs/design/<id>.md` → `/tmp/<id>-rN.md`;**N = `lumos loop status <id>` 已有輪數 + 1**(不靠記憶)。
2. 植 1 個 **canary**(additive、只進工作副本、**真檔永不含**):類型由 N 機械決定 `清單[(N−1) mod 4]`(a 壞§ref／b 未定義旗標／c 未定義欄位／d 未定義產物),嵌唯一 token 定位。
3. 派**乾淨審計員**(Agent tool、`model: sonnet`、不告知有 canary、refute framing 逐節找洞)。連 2 次 missed 後升 opus。
4. **判讀**:① canary 是否被清楚且正確點出性質(光 token 出現不算);② 排掉 canary 後最嚴重真 finding(clean/minor/major/blocker);③ **辯方 refute**(對 ≥major 每條派獨立 opus 構造 file:line 反證);④ 該輪 severity = 辯方裁決後存活 findings 的機械 max。
5. `lumos canary record caught|missed --loop <id> --severity <存活max> --auditor <model> --note "r<N> type=<a-d> …"`。
6. **漏抓** → 判決不採信、**不折** findings、直接下一輪(仍是一筆 missed record、仍算 cap、自動換 canary 類型 + framing 加碼)。
7. **抓到** → 只折辯方存活的真 finding 進 `docs/design/<id>.md`;**commit 前 `grep -c '<canary token>' docs/design/<id>.md` 必須為 0** 再 commit。
8. `lumos loop status <id> --need 2` → exit 0 出 loop;exit 1 → 回 step 1。

## 收斂演算法(Component A `cmd_loop_status`)
讀 `.canary-log.jsonl` 的 **append 序**(不 ts-sort:ts 只到秒、同秒並列),篩 `loop==id`。tail-K 滑動窗:`converged = len(rounds)≥need 且 last-K 筆皆 good`,`good = kind==caught 且 severity∈{clean,minor}`。missed/缺 severity 視同未收斂。exit 0=CONVERGED／1=未收斂(含無記錄)／2=真錯誤。

## 護欄與誠實天花板(SKILL.md)
- **連 2 次漏抓**(canary-log 最近 2 筆都 missed;中間一筆 caught 即重置)→ 升級:sonnet→opus +(soft、人工)切小 spec 各自開 loop。
- **max cap = 6 筆 record**:到頂未收斂 → 停、攤給人、記「達 cap 未收斂」,別無限燒。
- **硬閘是紀律非技術鎖**:lumos 擋不住「不跑就實作」(同 pre-commit `--no-verify` 後門),靠 Claude 記得調用 + 誠實 + cap/留痕事後可查。**trivial 改動**(typo/一行/純機械)可跳,但寫一句為什麼跳。
- **誠實天花板**(收斂後務必向人提醒):① 完整性 —— 收斂只證「連 2 輪醒著的審計員沒找到 blocker/major」,不證沒更深問題;② 整合性 —— canary-caught／severity／誤判判定皆由植入者自判、無外部檢查,是**沒閉合的迴歸**,loop 是可觀測+摩擦+地板,**不是 oracle**。

## 已知限制(v1 YAGNI)
- 不做:lumos spawn agent、圖譜自足性審計 loop(v1 只設計/spec)、自動 canary 生成、改 brainstorming/writing-plans skill 本體。
- 三重自判(canary 抓到沒／severity／誤判)根本上不 tamper-proof;辯方 refute 收窄了假陽性那一面、canary 收窄假陰性那一面,但都不是 oracle。

## 相關
- 設計稿(B):`docs/design/2026-06-19-design-loop-skill.md`(design-loop 收斂,5 輪、0 漏抓,severity 單調 blocker→blocker→major→minor→clean)。
- 設計稿(A 原語):`docs/design/2026-06-19-convergence-recording.md`。
- 設計稿(辯方 refute 後續):`docs/design/` finding-refute(3 輪自動收斂)。
- 實作落點:`skills/lumos-design-loop/SKILL.md`(B);`scripts/lumos` `cmd_canary` + `cmd_loop_status`(A 原語)。
- 衍生:`docs/superpowers/plans/2026-06-20-autonomous-iteration-loop.md`(自主迭代 loop 跨輪 headless 跑 design-loop)。
