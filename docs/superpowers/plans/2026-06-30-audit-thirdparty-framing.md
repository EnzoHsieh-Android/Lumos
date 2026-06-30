# audit-thirdparty-framing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 G1 的「待審物框定為第三方」免費結構招在 design-loop 兩條審計路徑拉滿:orchestrator 自折去裁量 + 審計員派工明說「當外部投稿審」。

**Architecture:** 純 prompt markdown 措辭調整,改 2 個檔共 3 處(`governance/autonomous_loop/orchestrator-prompt.md` step 3+5、`skills/lumos-design-loop/SKILL.md` step 3)。零 code、零測試框架改動。

**Tech Stack:** 純 markdown 提示檔。驗證靠 grep + 通讀。

## Global Constraints

- **不改任何 code**(`scripts/lumos`、`governance/autonomous_loop/*.py` 一律不碰)。
- 不動 `[audit:]`/L4 派工(已到位)、不動 judge/辯方 framing、不加 per-finding 折入帳。
- 改動為 additive/措辭性;步驟編號與既有引用不可被破壞。
- 語意以 spec `docs/design/2026-06-30-audit-thirdparty-framing.md` 為準;措辭可依各檔語氣微調,語意一致即可。

---

### Task 1: design-loop 審計派工第三方框架補強(3 處 prompt 編輯)

**Files:**
- Modify: `governance/autonomous_loop/orchestrator-prompt.md`(step 3 第 36 行、step 5 第 39 行)
- Modify: `skills/lumos-design-loop/SKILL.md`(step 3 第 25 行)

**Interfaces:** 無(prompt 措辭;無 code 介面)。

- [ ] **Step 1: fix #1 — orchestrator step 5 自折去裁量**

`governance/autonomous_loop/orchestrator-prompt.md`,用 Edit 把這行(L39):

```
5. 你**讀 judge 回報的 severity(不再自評)**,並讀 auditor 報告決定哪些 findings 折進 spec。
```

換成(消除「決定哪些」裁量語、對齊 step 7 的無裁量規則):

```
5. 你**讀 judge 回報的 severity(不再自評)**,並讀 auditor 報告;**辯方裁決後存活的真 finding 一律折入(不挑、不過濾;這是你寫的 spec 也照折),被辯方駁倒的不折**——折入動作與細節見步驟 7。
```

- [ ] **Step 2: fix #2 — orchestrator step 3 加第三方投稿 framing**

`governance/autonomous_loop/orchestrator-prompt.md`,用 Edit 把這行(L36):

```
3. **用 Agent 工具 spawn 一個 opus auditor**:要它 REFUTE 工作副本、逐節找洞、**強制地面事實查證**(spec 每個現況假設——欄位/函數/檔案/常數——實際 grep/Read 驗 scripts/lumos 等真實 code,報告列查證指令與結果),逐條標 severity。
```

換成(在 REFUTE 前加「當外部投稿審」框架):

```
3. **用 Agent 工具 spawn 一個 opus auditor**:**framing — 把工作副本當外部第三方的投稿來審,不是你/本系統寫的;你的職責是挑出投稿者沒看到的洞。** 要它 REFUTE 工作副本、逐節找洞、**強制地面事實查證**(spec 每個現況假設——欄位/函數/檔案/常數——實際 grep/Read 驗 scripts/lumos 等真實 code,報告列查證指令與結果),逐條標 severity。
```

- [ ] **Step 3: fix #2 — design-loop SKILL.md step 3 加第三方投稿 framing**

`skills/lumos-design-loop/SKILL.md`,用 Edit 把這行(L25)的 `**refute framing**:要它逐節讀` 片段:

```
指向工作副本、**refute framing**:要它逐節讀、主動找洞
```

換成:

```
指向工作副本、**refute framing(把工作副本當外部第三方的投稿審,不是你/本系統寫的——挑出投稿者沒看到的洞)**:要它逐節讀、主動找洞
```

> 用唯一片段替換,避免動到該行其餘文字(`不告知有 canary`、`第一次 missed 起就加碼 framing` 等保持原樣)。

- [ ] **Step 4: 驗證改動存在 + 流程未破壞**

```bash
cd /Users/enzo/harness/lumos-toolchain
# fix #1:step 5 不再有「決定哪些」裁量語、且出現「一律折入」
grep -n "決定哪些 findings 折進" governance/autonomous_loop/orchestrator-prompt.md   # 應 0 命中
grep -n "一律折入" governance/autonomous_loop/orchestrator-prompt.md                  # 應 1 命中(step 5)
# fix #2:兩處審計員派工都含「外部第三方的投稿」
grep -rn "外部第三方的投稿" governance/autonomous_loop/orchestrator-prompt.md skills/lumos-design-loop/SKILL.md  # 應 2 命中
# 流程未破壞:步驟編號仍 1..8 完整(orchestrator)、SKILL.md step 3 其餘文字仍在
grep -n "^3\.\|^5\.\|^7\.\|^8\." governance/autonomous_loop/orchestrator-prompt.md | head
grep -n "不告知有 canary" skills/lumos-design-loop/SKILL.md   # 應仍 1 命中(沒被誤刪)
```
Expected: 「決定哪些 findings 折進」0 命中、「一律折入」1 命中、「外部第三方的投稿」2 命中、步驟編號完整、`不告知有 canary` 仍在。

- [ ] **Step 5: Commit**

```bash
git add governance/autonomous_loop/orchestrator-prompt.md skills/lumos-design-loop/SKILL.md
git commit -m "feat(design-loop): 審計派工第三方投稿 framing + orchestrator 自折去裁量(G1)"
```

---

## Self-Review

**Spec coverage**(對照 `docs/design/2026-06-30-audit-thirdparty-framing.md`):
- §範圍 fix #1(orchestrator step 5 去裁量、對齊 step 7)→ Step 1。✓
- §範圍 fix #2(orchestrator step 3 + SKILL.md step 3 加「當外部投稿」)→ Step 2 + Step 3。✓
- §邊界 YAGNI(不動 [audit:]/L4、judge/辯方、不加折入帳、不改 code)→ Global Constraints + 僅 3 處措辭編輯,符合。✓
- §測試策略(無單元測試;grep 改動存在 + 通讀流程)→ Step 4。✓
- §誠實天花板 → 屬設計認知,不需 code。✓

**Placeholder scan:** 無 TBD/「similar to」;每個編輯步驟給出完整 old/new 字串。✓

**Type consistency:** 無 code 介面;3 處編輯字串與現行檔案(L36/L39/L25)逐字對應,grep 驗證關鍵詞一致(「一律折入」「外部第三方的投稿」)。✓
