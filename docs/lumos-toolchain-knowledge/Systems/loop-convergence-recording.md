---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-19_loop-convergence-recording]]"
summary: |-
  FLOW:每輪對抗審計 → canary record caught|missed --loop <id> --severity <max finding> 寫進 .canary-log.jsonl(+loop/+severity 兩選用鍵)→ loop status <id> 讀 append 序、篩 loop==id、tail-K 滑動窗算收斂 → exit 0/1/2 供編排 skill 讀
  KEY:把 loop 終止判準從「人含糊說看起來收斂了」換成「連 K(預設2)輪 caught 且 severity∈{clean,minor} 這個可重算條件」;留痕=那串 round 記錄本身
  KEY:CONVERGED ⟺ tail-K 滑動窗(append 序最後 K 筆)全為 caught+clean/minor;前面髒輪不影響、只看最後 K 筆[test:t_loop_status]
  KEY:missed 輪 ×tail-K 自然重置——一個 missed 落在窗內就擋收斂,直到隨新輪滑出;無需特例(dogfood R6 逼出)
  KEY:缺 severity 視同未收斂(逼明確宣告、不得當 clean);exit 0=CONVERGED｜1=未收斂(含無記錄=還沒開始)｜2=真錯誤(argparse/IO)
  KEY:誠實天花板——severity 自報無寫入端驗證,CONVERGED 是「忠實記錄、可重算的綠燈」非防竄改正確性證明;是可觀測性+摩擦+地板,非 oracle
  DEP:scripts/lumos cmd_canary(+loop/+severity)｜cmd_loop_status｜cmd_gov canary mapper(detail 附 loop/sev 放最前)｜.canary-log.jsonl(複用,不新增 log)
  TEST:t_loop_status + t_canary_loop_fields;258 passed
  VERIFY:[[Verification/2026-06-19_loop-convergence-recording]]
decisions:
  - content: 收斂用 tail-K 滑動窗(append 序最後 K 筆全 caught+clean/minor),非「每輪都得乾淨」;排序用檔案 append 序而非 ts
    context: 設計 loop r2 真 major(R2-MAJOR-1):「最後 K 輪」原文義含糊,可讀成全程乾淨;且 ts 只到秒、同秒兩輪會並列無法定序
    why_chosen: tail-K 讓前面髒輪(早期被審計揪出的 blocker)不永久汙染收斂,符合「修了就該往前」;append 序唯一且即時間序,免 ts 秒級碰撞
    decided: 2026-06-19
    valid: true
  - content: 機制定位誠實校正為「可觀測性+摩擦+一個地板」而非「機械自我終止 oracle」;severity 是忠實轉錄審計員 max finding、無寫入端驗證
    context: r1 深層 blocker(R1-BLOCKER-2):原宣稱「機械自我終止」過度;severity 自報、想早收工的編排者可記假 clean——這跟 canary「植入者忠實判定」是同一個沒閉合的迴歸
    why_chosen: 對「無人看顧的自動 loop」夠用(終止從不可查的人判→可查的條件);對「刻意作弊」本就不設防、不該假裝防竄改;誠實標清天花板免下游過度信任
    decided: 2026-06-19
    valid: true
  - content: missed 輪靠 tail-K 機制自然重置乾淨連續數(missed 必 kind!=caught 故落窗內即擋收斂),無需特例
    context: 第六輪 dogfood 實況逼出(R6):一次漏抓 canary 該讓乾淨連續數歸零,否則放水輪被忽略
    why_chosen: tail-K 已天然涵蓋——missed 在窗內就不收斂、隨新輪滑出才放行;加特例反增複雜度
    decided: 2026-06-19
    valid: true
---
# loop-convergence-recording

收斂留痕(Convergence Recording)—— lumos 治理朝 **loop engineering** 方向的 **Component A**(機械層):把對抗審計 loop 的終止判準從「人在判」變成「lumos 從紀錄機械算出、可查詢」。

源起:lumos 治理大方向 memory `lumos-governance-direction-loop-engineering`(朝自主/無人看顧的自我檢查 loop)。非由單日日報 gap 直接觸發——2026-06-19 日報的 gaps/loop_lens 聚焦記憶完整性(STALE/記憶污染/HEARTBEAT),與本功能相鄰但不同路;本設計稿明載其角色來自 loop-engineering 方向。reportProvenance 見回報。

## 定位
- 審計 loop 的終止(「審穩了沒」)原本人在判,無法自我終止、不留痕、無法事後查。
- 收斂留痕 = 每輪審計記下(canary caught/missed + severity)+ 由 lumos 從紀錄算收斂。
- **只做 Component A**(lumos 機械原語)。Component B(編排 skill,讓每個計畫自動進 loop、問 `lumos loop status` 決定停不停)另立子專案,消費 A。

## 資料模型(複用,不新增 log)
複用既有 `.canary-log.jsonl`。`lumos canary record` 加**兩個選用鍵**:
```
lumos canary record caught|missed --loop <id> --severity clean|minor|major|blocker [--auditor] [--token] [--note]
```
- `--loop <id>`:把這輪歸進某設計 loop(slug)。
- `--severity`:這輪審計員自己標的**最嚴重** finding(忠實轉錄其 max,非編排者獨立意見)。
- 寫入時 `if loop: rec["loop"]=loop` / `if severity: rec["severity"]=severity`(沒給就不寫鍵 → 舊 ad-hoc canary 行為不變)。

## 收斂計算(`lumos loop status <id> [--need K]`,K 預設 2,唯讀)
讀 `.canary-log.jsonl` 的 **append 序**(不 ts-sort)、篩 `rec.get("loop")==loop_id` 嚴格等值、tail-K 算收斂:
- **CONVERGED ⟺ tail-K 滑動窗(最後 K 筆)全為 `caught` 且 `severity∈{clean,minor}`**。canary 抓到=審計員醒著;無 blocker/major;**缺 severity 視同未收斂**。
- 否則「⏳ 還需 N 輪」,N = need − (從尾往回連續合格的輪數);最後一輪就髒 → N=need(髒輪不讓 N 虛低)。
- 記錄數 < K(含**無記錄=還沒開始審**)→ 未收斂 exit 1。
- `--need` 防呆:`need = max(1, need)`(< 1 夾到 1,不算參數錯)。
- 輸出:第一行 status,接著每輪一行 tab 分隔(`順位\tkind\tseverity\tts\tnote`)當留痕,讓 B skill 不必 screen-scrape。
- **exit code**(給 B 機器讀):`0`=CONVERGED、`1`=未收斂(含無記錄)、`2`=真錯誤(argparse 錯 / 檔讀不到)。「沒記錄」與「I/O 錯」分開 → B 能分辨「該起一輪」vs「基礎設施壞了」。

## missed × tail-K(無特例的自然重置)
`missed` 也算一輪、且 `kind!=caught` 必不合格 → 一個 missed 落在 tail-K 窗內就擋住收斂,直到它隨新輪滑出窗外。效果 = 一次漏抓 canary 自然重置乾淨連續數(dogfood 第六輪逼出)。

## gov 串接
`cmd_gov` 的第 4 源(canary mapper)`detail` 必附 loop/severity 且**放最前**(避 `[:50]` 截斷):
`f"loop={d['loop']} sev={d.get('severity','?')} · " if d.get("loop")` + auditor/note。舊記錄無 `loop` 鍵 → 前綴空、行為同現在。

## 已知限制(誠實天花板,兩層)
1. **完整性**:收斂只證明「連 K 輪醒著的審計員沒找到 blocker/major」,**不證明沒有更深問題**。完整性靠多輪+多視角的 loop 本身,不靠把門檻調嚴。
2. **整合性**:`severity` 自報、無寫入端驗證 → CONVERGED 是「忠實記錄下、可重算的綠燈」,非防竄改正確性證明。前提是「編排者忠實轉錄審計員判決」——跟 canary 同一個沒閉合的迴歸,較難自欺但**不是 tamper-proof**。
→ 定位:可觀測性+摩擦+一個地板,**不是 oracle**;對無人看顧 loop 夠用,對刻意作弊不設防(非目標)。

## 相關
- 設計稿:`docs/design/2026-06-19-convergence-recording.md`(canary-護審計 7 輪、用本設計自己的 K=2 判準收斂)。
- 實作落點:`scripts/lumos` `cmd_canary`(+loop/+severity threading)、`cmd_loop_status`、`cmd_gov` canary mapper、`loop` subparser。
- skill 串接:`skills/lumos-project-notes/SKILL.md` canary 協議節(記 round + `loop status` 看收斂)。
- 方向 memory:`lumos-governance-direction-loop-engineering`。
