---
type: verification
status: pass
date: 2026-08-04
valid_under: scripts/lumos 單檔架構;.canary-log.jsonl 共用帳;_vault_repo_root 向上找 .git 的根判定;quote-check 引句樣式=「引句：「…」」
revalidate_when: canary-log 分帳(per-loop 檔)時;round 分組/內部鍵規則變更;_quote_norm 或引句抽取 regex 變更;留痕路徑落帳規則變更
self_audit: sonnet/2026-08-04
plan_refs:
  - "[[Projects/design-loop重設計_實作計畫]]"
  - "[[Projects/design-loop重設計]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:code-loop panel 終審(loop=code-dloop-redesign,tier=high,W=5+Codex 雙席+spec 席)三輪的 findings 修復驗證。新測試 4 支:t_disposal_gate_r1_panel_hardening(11 斷言)/t_disposal_gate_r2_panel_hardening(7)/t_disposal_gate_r3_panel_hardening(4)/t_calibration_readback_hardening(3)+quote-check 巢狀/下限 3 斷言;每支紅→綠+前置斷言;全套 2302 綠
  VERIFY:r1 修 7 major(壞行 fail-open 寫讀兩側/判定輪取錯/巢狀引句截斷/引句 10 字下限/只驗 carrier→全席/相對路徑落帳/UnicodeDecodeError);r2 修修復批自身回歸 3 條(__legacy 合組/全席缺欄跳過/vault.parent≠repo root→_vault_repo_root);r3 修 3 major(__ 保留字首撞鍵 3 席重疊/不成對引號格式 miss/--repo 顯式覆蓋)+校準帳 run_id 自驗與 --log 隔離。全部先機械 repro(可執行 falsification)才修
  KEY:★終審結論=達 cap(3 輪)未收斂,攤人裁★——r1(2 missed)/r2(1 missed)輪無效;r3 5/5 caught 輪有效但存活 major、capture-recapture 殘餘超門檻(發現未枯竭)。放行需人明示豁免 code-loop pass 留痕或加開 r4;殘留風險=r3 修復批未經獨立輪審
  KEY:accepted(留理由):n_badlines 全帳域 fail-closed(3 席異議)——誤擋方向+帳在 git 可修+settle 前例,配套=rc2 訊息附壞行行號;T6 定錨 check-then-act 竸態(minor,單機 CLI+讀側 gate 兜底)
  KEY:canary 生成觀察(進校準帳的教訓):資源類植入對 haiku 探針天生顯眼(兩席 recraft×2-fail,caught 記弱證據);r1 植入曾因 hunk 行數頭寫錯露機械破綻(r2 起改程式自算行數頭)
---
# design-loop 處置閘終審硬化（code-loop 三輪 findings 修復）

**loop**：`code-dloop-redesign`（tier=high panel，帳在 `docs/.canary-log.jsonl` r1-r3）
**計畫**：[[Projects/design-loop重設計_實作計畫]] T8；**spec**：[[Projects/design-loop重設計]]

## 三輪與修復對照（全部先機械 repro 才修）

| 輪 | canary | 存活 findings → 處置 |
|---|---|---|
| r1 | caught 3／missed 2（s2 席探針 recraft×2-fail＝弱證據；部分 caught 靠 hunk 行數頭破綻＝植入手藝瑕疵） | 壞行 fail-open（4 席重疊）→ 寫側逐行容錯＋讀側 rc2；判定輪取錯（round 重現）→ 守衛 rc2；巢狀『』截斷→同型閉引號；引句 10 字下限；只驗 carrier→全席重驗；相對路徑→root 相對落帳；UnicodeDecodeError→接住 |
| r2 | caught 4／missed 1 | r1 修復批自身回歸：__legacy 合組→逐筆 __seq；全席缺欄 continue→FAIL；vault.parent≠repo root→`_vault_repo_root`（向上找 .git，寫讀同根）；校準帳半行黏連/末行定位→run_id 全檔掃描 |
| r3 | caught 5／missed 0（輪有效） | __ 保留字首撞鍵（3 席重疊，偽 PASS repro）→ 寫側拒收＋讀側防守；round 混用→明確 rc2；不成對引號靜默丟棄→格式 miss 入列；--repo 顯式覆蓋解析根（git-less 邊角）；校準測試 --log 隔離（不碰生產帳） |

## 誠實天花板

- **終審未收斂**：cap=3 到頂，三輪每輪都還在出 major——發現未枯竭，capture-recapture 殘餘同判。放行歸人裁（明示豁免留痕或加開 r4）；殘留風險＝r3 修復批（保留字首/混用守衛/格式 miss/--log 隔離）未經獨立輪審，但各有紅→綠測試釘住。
- missed 席（r1 s1/s5、r2 s5）的 findings 未走席位信用，全部經機械 repro（通道 a：執行證據）才折入。
- accepted 兩條（n_badlines 全帳域、T6 竸態）理由見 summary，翻案條件＝canary-log 改 per-loop 分帳。
