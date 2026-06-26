---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-23_check-t-sentinel]]"
summary: |-
  FLOW:doctor 掃節點 Check 段尾(T→R→S→K)→Check K 對每 note 取 extract_contracts→過濾 inv 含 ★COMBO★→數該 inv 的 [test:] 標記個數(TEST_REF_RE.findall)==1→收進 combo_thin 經 _soft_list warn_soft 提醒補組合+gov_events check-k warned hard:False→無 ★COMBO★ 則 ok 靜默
  KEY:★COMBO★ 是 invariant 鐵則的子修飾(第 5 個 Tag),標在最重鐵則上,觸發軟 Check K 提醒「別只綁 1 個 happy-path [test:]」;不擋、不計 issues、不執行測試(同 Check S)[test:t_check_k]
  KEY:判據數「[test:] 標記個數」非展開測試名數——[test:a,b] 算 1 個標記,免單逗號 tag 繞過提醒(F1,正中動機要防的反向優化)[test:t_check_k]
  KEY:★COMBO★ 必寫在 invariant marker 之後(末尾);寫在前會讓 INVARIANT_RE 不匹配、整條 invariant 從 Check T/K 雙雙消失
  KEY:★COMBO★ 無 invariant marker = 已知盲區——純 ★COMBO★ 行進不了 extract_contracts、Check K 看不到、誤標靜默忽略(YAGNI 不另掃)
  KEY:本機制不重複 CI——CI 跑測試綠才部署是確定性錨點;Check K 只補「不提醒你漏寫組合情境」這道縫,是摩擦地板非神諭
  DEP:scripts/lumos cmd_doctor section("K")｜extract_contracts｜TEST_REF_RE｜_soft_list/warn_soft(沿用 Check S 模板)
  TEST:258 passed(macOS);t_check_k 4 案(綁1提醒/綁2不提醒/無COMBO靜默/F1逗號仍提醒)
  VERIFY:[[Verification/2026-06-23_check-t-sentinel]]
decisions:
  - content: 判據改「數 [test:] 標記個數」(TEST_REF_RE.findall(inv) 長度),非 strip_test_refs 展開的測試名數;[test:a,b] 算 1 個標記
    context: design-loop r6 canary 排掉後揪出的真 major(F1):原判據 len(refs)(展開測試名數)可被 [test:a,b] 單逗號 tag(=2 名)繞過提醒——正中本機制動機要防的反向優化(maker 寫剛好過的 happy-path 刷掉提醒)
    why_chosen: 機制動機正是防「綁了幾條測試」被反向優化刷掉;若用展開名數,單行多名即可規避提醒,機制自我瓦解;數標記個數才逼真的多個 [test:] 標記
    decided: 2026-06-23
    valid: true
  - content: ★COMBO★ 必寫在 ★INVARIANT★ 之後;★COMBO★ 無 ★INVARIANT★ 標為已知盲區、誤標靜默忽略、YAGNI 不另掃
    context: design-loop r3 canary 排掉後揪出真 major(F3):原 spec §「★COMBO★ 無 ★INVARIANT★ 也軟提醒」與 extract_contracts 路徑互斥不可實作——extract_contracts 只收 INVARIANT_RE 命中行,純 ★COMBO★ 行進不了
    why_chosen: ★COMBO★ 本就設計為 ★INVARIANT★ 子修飾,單獨用屬罕見誤用;與其加一條撐不住的掃描路徑,不如誠實標盲區、留痕、YAGNI
    decided: 2026-06-23
    valid: true
  - content: Check K 自己重掃(extract_contracts + strip_test_refs/TEST_REF_RE),不複用 Check T 的 bound/refs 局部變數;接在 Check S 之後(段尾 T→R→S→K),用未占用的 section("K")
    context: design-loop r1 揪出 blocker(section("C") 已被 core_refs 占用)+ major(複用 Check T bound/refs 不成立:局部變數出作用域且違反「不改 Check T」)
    why_chosen: Check K 為純新增軟 Check、不得動 Check T;自己重掃才作用域乾淨;照 Check S 模板(warn_soft + _soft_list + gov_events warned/hard:False)複用既有結構
    decided: 2026-06-23
    valid: true
---
# check-t-sentinel

`scripts/lumos` `cmd_doctor` 的 **Check K** —— `★COMBO★` 組合覆蓋軟提醒。`★INVARIANT★` 的第 5 個 Tag 子修飾。

> 源起:日報 2026-06-23 主軸「驗證正確性 > AI 審計 / 地面事實查證能用死板比對(grep/diff/測試存在性)就別交給 AI」+ 設計者引申的 gap「Check T 賭『綁一個會跑的測試=合約為真』,但測試只是 proxy、會被反向優化刷掉」。(該 gap 文字非 06-23 報原句逐字,係 06-23「確定性比對 vs LLM 判斷」主題的引申。)

## 是什麼 / 解決什麼
- **Check T 現狀**:doctor 靜態驗每條 `★INVARIANT★` 綁了真實存在 + 經審計的 `[test:名]`,但只驗「綁了測試」。測試是 proxy——maker 看得到綁的 happy-path,可寫「剛好過這條」的實作而不真守規格,CI 照樣綠。「綁了幾條」≠「測夠了組合情境」。
- **Check K 補的縫**:在最重的 `★INVARIANT★` 上加 `★COMBO★` 標記,doctor 軟提醒「這條最重鐵則只綁 1 個 happy-path `[test:]`,建議補組合情境測試(多條件交叉)」。養成「最重的地方測組合」的習慣。
- **CI 才是錨點**:bound 測試在 CI 跑、綠才部署——已確定性驗「測試跑了 + 綠了」。Check K **不重複** CI(不執行測試、不驗有效),只補「不提醒你漏寫組合情境」這一道縫,是摩擦地板、非神諭。

## 關鍵機制
- **軟 Check(照 Check S 模板)**:`warn_soft` 印出但不動 issues、不影響 rc;`gov_events.append({"gate":"check-k","kind":"warned","hard":False,"nodes":[n.stem]})`。觸發時 `lumos doctor` 退出碼**不變**。
- **判據 = 數 `[test:]` 標記個數**:`len(TEST_REF_RE.findall(inv)) == 1` → 提醒。數的是 `[test:...]` 標記出現次數,**非展開測試名數**——`[test:a,b]` 算 **1 個標記**,免單逗號 tag 繞過(見 decisions/F1)。
- **`★COMBO★` 為 invariant 行內標記**:Check K 對每 note 調 `extract_contracts(n)` 取 invariants(同 Check T 的 `invs, _ = extract_contracts(n)`),在每條 inv 文字裡做 `"★COMBO★" not in inv` 過濾;不碰節點分類/既有 Tag。
- **顯示**:命中的 inv 以 `inv.replace("★COMBO★","").strip()` 去殘留標記+殘白後收進 `combo_thin`(元素為字串),經 `_soft_list`(`[:8]` 截斷)印出。
- **三態**:無任何 `★COMBO★` → `ok("無 ★COMBO★ 標記")`;有 `★COMBO★` 但都綁 ≥2 標記 → `ok("都綁了 ≥2 個 [test:] 標記")`;有薄綁的 → `_soft_list` 提醒。

## 關鍵決策(完整 alternatives 見設計稿尾段 R1-R6)
見 frontmatter `decisions[]`:F1 判據改數標記個數(防逗號繞過)、★COMBO★ 必在 ★INVARIANT★ 之後 + 無 ★INVARIANT★ 是已知盲區、Check K 自己重掃不複用 Check T。

## 已知限制(誠實天花板)
1. **驗不了「組合性 / 夠不夠」**:綁 2 個標記都是 happy-path 也算「滿足」;lumos 只數標記個數,真正的組合覆蓋靠寫測試的人 + CI 跑。弱保證、摩擦地板。
2. **「最重」由人標 `★COMBO★`,主觀**:沒標 = 不管(同 `★IRREVERSIBLE★` 靠人標)。
3. **`★COMBO★` 無 `★INVARIANT★` 是盲區**:純 `★COMBO★` 行被 `INVARIANT_RE` 漏掉、`extract_contracts` 收不到 → Check K 看不到、誤標靜默忽略(YAGNI 不另掃)。
4. **`★COMBO★` 誤寫在 `★INVARIANT★` 前**:`INVARIANT_RE` 不匹配 → 整條 invariant 從 Check T/K 雙雙消失(prose 已標、無護欄)。
5. **軟規範會被無視**:`warn_soft` 不擋,maker 可不理。設計如此(養成習慣、非強制)。

## 相關
- 設計稿:`docs/design/2026-06-23-check-t-sentinel.md`(design-loop 達 cap 6 輪、canary 6/6 全 caught、未自動收斂 → 人工定稿放行;核心地面事實全 clean、F1 判據漏洞已修)。
- 實作計畫:`docs/superpowers/plans/2026-06-23-check-t-sentinel.md`。
- 實作落點:`scripts/lumos` `cmd_doctor` `section("K")`(L706-727);commit `15fd6ad` 本體 + `64976a6` 方法論知識同步。
