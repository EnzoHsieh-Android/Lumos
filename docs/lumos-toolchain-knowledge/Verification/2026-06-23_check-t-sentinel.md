---
type: verification
status: pass
feature: "[[Systems/check-t-sentinel]]"
commit: 15fd6ad
date: 2026-06-26
valid_under:
  - "scripts/lumos cmd_doctor 維持 Check 段尾順序 T→R→S→H→K→V、section(\"K\") 不被改名/占用"
  - "TEST_REF_RE 維持「數 [test:] 標記個數」語義(非展開名數)、★COMBO★ 仍為 ★INVARIANT★ 之後行內標記"
  - "warn_soft/_soft_list 維持不計 issues、不影響 rc(軟 Check 語義)"
revalidate_when:
  - "改 Check K 判據(標記個數 ↔ 名數)或 ★COMBO★ 過濾/顯示邏輯"
  - "改 extract_contracts / TEST_REF_RE / INVARIANT_RE 解析"
  - "Check 段順序或 section id 變動、warn_soft 改為計 issues/擋"
tags:
  - type/verification
  - status/pass
---
# Verification: check-t-sentinel(Check K ★COMBO★ 軟提醒)

## 證據

### 1. 回歸測試(macOS)
`python3 scripts/test_lumos.py` → **258 passed, 0 failed**。

`t_check_k`(`scripts/test_lumos.py:1300`)4 案 fixture 驅動(構造臨時 vault 跑 doctor 驗輸出):
- `★INVARIANT★ + ★COMBO★` 綁 1 個 `[test:OverbookHappy]` → doctor 輸出含「happy-path」軟提醒。
- 綁 2 個標記 `[test:Happy] [test:Combo]` → 不提醒。
- 有 `★INVARIANT★` 無 `★COMBO★` → 不提醒。
- **F1 逗號繞過守衛**:`[test:HappyA,HappyB]`(單標記多名)算 1 個標記 → **仍提醒**,坐實判據用標記個數而非展開名數。

### 2. rc 不變(軟 Check 語義)
Check K 走 `_soft_list` → `warn_soft`,不動 issues、不影響 rc;觸發時 `lumos doctor` 退出碼不變(同 Check S)。`gov_events` 記 `{"gate":"check-k","kind":"warned","hard":False}`。

### 3. design-loop 收斂史
2026-06-23 design-loop **6 輪、canary 6/6 全 caught(opus 零漏)**,severity blocker→good→major→good→major→major。核心地面事實 5-6 輪逐項查證與代碼一致;F1 判據漏洞(逗號繞過)已修。達 cap 未自動收斂,卡在文檔級「壞§ref」與已修的 F1 → **人工定稿放行**(核心修正已折、剩 F3/F4 文檔級無 blocker)。

## 落點
- 實作:`scripts/lumos` `cmd_doctor` `section("K")`(L706-727)。
- commit:`15fd6ad`(Check K 本體)、`64976a6`(方法論知識同步)。
