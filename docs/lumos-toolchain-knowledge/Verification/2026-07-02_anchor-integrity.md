---
type: verification
status: pass
created: 2026-07-02
updated: 2026-07-02
tags:
  - type/verification
  - status/pass
related:
  - "[[Systems/anchor-integrity]]"
valid_under: scripts/lumos cmd_anchor_verify/approve(ANCHOR_FILES 5 檔列舉 + sha256 + rc 0/1/2);接線=pre-push vault 閘門前 + autonomous-loop.sh 每輪派工前;governance-log 寫者=doctor --ci + anchor approve
revalidate_when: 改 ANCHOR_FILES 列舉;改 cmd_anchor_* 邏輯;改 pre-push/autonomous-loop.sh 接線段;anchor-baseline.json schema 變更
summary: |-
  TEST:t_anchor 14 checks 全綠(無 baseline rc0 警示/缺 note rc2/approve 建檔 5 錨點+note/verify rc0/gov-log anchor-approve 事件/lumos gov 顯示 note/改檔 rc1 列名/--json 精確/缺檔 rc1/重簽容缺 4 錨點/repo 解析 rc2);308 passed 0 failed 無回歸
  VERIFY:真 repo 實錨自測——初始 approve 5 錨點+verify rc0(baseline 含接線後 pre-push 自身 hash,審查員實算 sha256 對照一致);pre-push 直呼 smoke(乾淨 rc0、篡改 post-commit rc1 擋下、還原乾淨)
---
# 2026-07-02 anchor-integrity 驗證

`python3 scripts/test_lumos.py`:t_anchor 14 checks 全綠,308 passed 0 failed(含 t_governance_log_write 無回歸)。
真 repo:`lumos anchor approve --note "初始 baseline"` 寫入 5 錨點、`verify` rc=0;baseline 內 pre-push hash 經審查員獨立實算 sha256 對照一致(自指閉合成立)。pre-push 直呼 smoke——乾淨 repo rc=0,篡改 `scripts/hooks/post-commit` 後 rc=1 正確擋下,還原後乾淨。
接線語法:`bash -n` 兩檔皆過;loop 入口 errexit-safe 寫法(if ! …)經審查員模擬 baseline 缺失/verify 失敗實測,正確走到通知+exit 1。
