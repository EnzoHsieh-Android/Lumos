---
type: verification
status: pass
feature: decision_refs 自動養成 P+T1 code-loop 硬化(異質 panel r1 5修 + delta 複審)
commit: 待填
date: 2026-07-15
valid_under:
  - "confirm 選欄 fail-safe:只 by==human 落可信 decision_refs、其餘(含未知)落 decision_refs_ai"
  - "decision_ref 拒含 \"/\\/換行/tab(不可 round-trip),值純引號包裹"
  - "E3 firing 聯集 (rel,ref) 去重;reindex --all 內外層 except 含 OSError"
revalidate_when:
  - "T3 AI suggest 落地(decision_refs_ai 大量填,reconcile 命令補上時)"
  - "strip_quotes/序列化跳脫語意變更"
plan_refs:
  - "[[decision_refs自動養成_實作計畫]]"
tags:
  - type/verification
  - status/pass
---

# 驗證：decision_refs 自動養成 code-loop 硬化

P+T1（[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]）push 前的 tier=high 對抗代碼審。異質 panel（3 sonnet 異鏡頭 + Codex 否決席 + mutation 冒煙）canary 3/3 caught、5/5 mutation 全滅、四席一致驗證不對稱信任接線正確。

## r1 五修（去重後全落）
- **FIX1（A, major）**：`reindex --all` 內層 loop + dispatcher except 補 `OSError`（寫檔面磁碟滿/權限 → rc=2 非裸 traceback；補齊與 rel-cascade dispatcher 的一致性）。
- **FIX2（C, medium/安全）**：confirm 選欄由 fail-**open** 翻 fail-**safe**——`"decision_refs" if by == "human" else "decision_refs_ai"`：只有明確 human 落可信正欄，非 ai/human（None/打錯/未來值）一律落不可信 ai 欄。安全守門不靠上游 argparse choices 撐（誤落正欄＝可抑制 E2＝破安全設計）。
- **FIX3（A+C, minor）**：E3 firing 聯集 `(rel,ref)` 去重（過渡態同 ref 兩欄都有時不重複虛胖計數）。
- **FIX4（B/Codex）**：`_append_decision_ref` 顯式拒含 `"`/`\`/換行/tab（strip_quotes 不反跳脫、合法 `<rel>#dN` 永不含這些）——把「靜默 soft-fail」提前成明確錯誤，不留隱形回寫缺口；引號化簡化為純包裹（死碼 escape 移除）。
- **CX2（Codex）**：回寫 soft-fail 訊息軟化——不再宣稱「可 reconcile」（該命令未實作、列 future），改述「帳本已記為地面真相、節點欄位本次未同步」。

## 誠實留檔（非修，記清）
- **CX1 併發 lost-update（Codex, 降級）**：`_append_decision_ref` read-modify-replace 無鎖＝**全 CLI 既有 last-writer-wins 模型**（M1 決策已明載「兩 session 併發改同節點 frontmatter 是既有性質、非新引入、不加鎖」），非本次引入，記不修。
- **兩套不對稱信任模型（C 深水區觀察）**：① decision_refs 欄位級（ai 欄**絕不**抑制 E2）② M3 帳本級 `_led_terminal`（ai-prune **可**抑制 E2，但走 [S3] auto-prune 保守+留痕+可翻案的獨立安全模型）。兩者威脅模型不同、都成立，**非矛盾**——此處明文記清免日後誤判為 bug。

## 測試
`t_dref_codeloop_hardening`（FIX1 code 錨/FIX2 未知 by→ai 欄/FIX3 兩欄去重/FIX4 拒斥）；全套 1127 passed/0；mutation 5/5 全滅（含 MUT3「E2 誤讀 ai 欄」被抓＝不對稱安全網有測試守）。

## 相關模組
- [[decision_refs自動養成_實作計畫]]（P✅ T1✅ + code-loop 硬化 → T3 design-loop）
- [[Systems/lumos-cli-write]]
