---
type: project
status: done
created: 2026-08-02
updated: 2026-08-02
about_code_stamp: batch-2026-08-23/2026-08-23/e34a0cab048b
related:
  - "[[Systems/retrieval-ranking]]"
  - "[[Systems/cochange-guard]]"
  - "[[Verification/2026-08-02_slim三缺陷修復_實驗產出]]"
tags:
  - type/project
  - status/done
summary: |-
  FLOW:★2026-08-02 人裁 A 案、已落地★(B/C 加閘案不做,理由見下)。問題=code-loop skill 白紙黑字要求「派 reviewer 前跑 `lumos impact --diff` 並附 manifest 當第二鏡頭」,但★純紀律層、無任何機械提醒★ → 2026-08-02 實測我自己就忘了 → 修法=A 免費提示(已落地)
  KEY:★這不是工具缺口,是執行落差★——`impact --diff` 本來就會逐檔用 hunk 文字當 query 跑 BM25F,固定席(帶硬合約標記的節點)不參與排序競爭故永不被擠掉,hop1 撈得到「改 A 壞 B」的 B。今天跑起來第一行就是後來被證實違反合約的那個節點
  KEY:★誠實天花板(先寫,不得事後淡化)★:任何機械化只能證明「指令被執行過」,★證明不了「manifest 真的餵進 reviewer 的 prompt」★——派工發生在模型腦內,外部不可觀測。與 design-loop M0 進場硬否決同一種 honor-system 天花板
  KEY:★已排除的做法★把 impact 掛進 `pitfalls --diff`——實測 pitfalls 0.18s、impact 4.7s,而 pitfalls ★在 pre-push 熱路徑上逐 ref 跑★(scripts/hooks/pre-push:98),掛上去等於每次 push 慢 26 倍;`--incidents-only` 不便宜(4.73s,成本在載 vault 非排序)
  DEP:scripts/lumos cmd_impact_diff / cmd_code_loop / _codeloop_guard_verdict｜governance/code-loop/<branch>.json｜skills/lumos-code-loop/SKILL.md
  PRIOR-ART:①最小解在既有機制層——`governance/code-loop/<branch>.json` 收據+`_codeloop_guard_verdict` 判定式已是成熟樣板,新增一種收據即可,不造新機制 ②世界解過=CI required checks／PR gate「附上證據才能合併」,同型 ③裁定=borrow-design(沿用本專案既有收據+判定式模式,不引任何依賴)
about_code:
  - scripts/lumos
---
# 送審前 impact 鏡頭機械化（計劃）

## 問題（有實例，不是假想）

`lumos-code-loop` skill 白紙黑字寫著：

> **impact 鏡頭**：派前跑 `lumos impact --diff <range> --json` → 附 manifest 當第二鏡頭

**2026-08-02 我自己沒跑。** 派審查員時只給了 diff 路徑與 repo 路徑，讓它自己 grep。

而事後補跑，第一行就是：

```
1.00 直接 Systems/slim-uninstall-一行卸載.md ★INVARIANT★ [固定]
```

**那正是後來被證實違反的那條合約所在的節點。**

## ★這不是工具缺口，是執行落差★

`impact --diff` 本來就做得很好，三個設計都對：

- **逐檔**用該檔 hunk 文字當 query 跑 BM25F（不是單一全域 query）
- **固定席**：帶 `★INVARIANT★` 的節點不參與排序競爭，**分數再低也不會被擠掉**——安全網不建在「排序算得準不準」上面
- **hop1**：撈得到「改 A 壞 B」裡那個你不會想到去看的 B（實例：改 `slim/install.py` → 撈出隔一跳的 `Systems/測試假綠形態`）

**唯一的問題是沒有任何東西提醒你去跑它。**

## ★已排除的做法（附實測理由）★

**把 impact 掛進 `pitfalls --diff`** —— 這是最直覺的做法（因為 `pitfalls` 是我每次都會跑的，用來拿 tier）。**排除**：

| 指令 | 耗時 |
|---|---|
| `pitfalls --diff` | **0.18s** |
| `impact --diff` | **4.7s** |
| `impact --diff --incidents-only` | 4.73s（**不便宜**，成本在載 vault 不在排序） |

而 `pitfalls --diff` **在 pre-push 熱路徑上逐 ref 跑**（`scripts/hooks/pre-push:98`）。掛上去 = 每次 push 慢 26 倍。**不可接受。**

## 兩個候選（★2026-08-02 人裁：A★）

### A. 免費提示（不動任何 gate）

`pitfalls --diff` 的**人可讀輸出**多印一行（純文字，零額外計算；pre-push 的 verdict 走 `--json`，不受影響）：

```
tier: standard
→ 派審查員前:lumos impact --diff <range>(附 manifest 當第二鏡頭,固定席必答)
```

- **成本**：近乎零，改動 < 10 行
- **效力**：純提醒。忘了照樣能跑完全程
- **流程**：trivial，可跳 design-loop（commit 註明）

### B. 提示 + 收據 + 閘

在 A 之上：

1. `lumos impact --diff <range>` 成功時寫收據 `governance/impact-lens/<branch>.json`
   ——`{range, head_sha, manifest_sha256, pinned_count, ts}`
2. `_codeloop_guard_verdict` 增加一條：**tier=high 且無匹配收據 → blocked**
   （tier=standard 只警告，不擋）

- **成本**：新增收據讀寫 + 判定式一條分支 + 測試（含還原翻紅釘）
- **效力**：tier=high 時真的擋得住
- **流程**：★這是守衛面，依 `lumos-design-loop` 進場硬否決，**不給 light、必須跑完整 panel loop 才能實作**★

## ★誠實天花板（先寫死，不得事後淡化）★

**任何機械化都只能證明「指令被執行過」，證明不了「manifest 真的被餵進 reviewer 的 prompt」。**

派工發生在模型腦內，外部不可觀測。這與 `design-loop` M0 進場硬否決是**同一種 honor-system 天花板**。

但它仍然是真進步：**今天的失敗是「連跑都沒跑」**，跑了至少代表我看見了。

## 還沒想清楚的

- 收據的有效期怎麼定？綁 `head_sha` 的話，每多一個 fix commit 就得重跑 4.7s——會不會逼人用 `--no-verify`？
  - ★2026-08-03 自己踩到了，而且比預期糟★：這不是「多跑 4.7 秒」的問題，是**雞生蛋**。現行 `code-loop pass` 把留痕綁 `head_sha`，而留痕本身寫在 `governance/code-loop/<branch>.json`——**一 commit 那個檔就又改了 HEAD，留痕當場失效**。我連續三次「記 pass → commit → push 被擋」才想通。
  - 可行解（本次採用的）：**先做完最後一個 commit，再記 pass，然後直接 push，marker 留在工作區不 commit**（hook 讀的是工作區的檔案，不是 git 裡的）。但這要人記得順序，**沒有任何東西會提醒**——★同一個機制上，「收據」與「被收據認證的東西」互相依賴，是設計問題不是操作問題★。
  - 若日後真要做 B/C 案的閘，這個雞生蛋**必須先解**，否則新閘會複製同一個坑。
- tier=standard 要不要也擋？今天那次正是 standard，**擋 high 不擋 standard 的話，今天這個案例還是漏的**。
- 有沒有更強的版本：要求對每個固定席節點給一句裁決（同實驗三「強制逐檔裁決」的招）——**可機械檢查條數**，但會不會變成應付式填表？

## ★裁定與落地（2026-08-02）★

**採 A（免費提示），不做 B/C 的閘。**

### 為什麼不加閘（★這條理由是寫計劃時才發現的，值得記★）

B 的設計是「tier=high 且無收據 → 擋」。但**觸發本計劃的那次失敗，`tier` 是 `standard`**。

> **照 B 做完，同一個失敗還是會再發生一次。**

要真的擋到得連 `standard` 一起擋（C 案），但 `standard` 是最常見的分級，每次都逼跑
4.7 秒＋一份收據——**很可能的結果是開始用 `--no-verify` 繞過，閘門變成裝飾**。

★這是「加了守衛，但守在錯的門」★。加閘之前得先答出「怎麼在不擋住最常見路徑的前提下擋到它」，
現在答不出來，所以不加。

### 落地內容

`_pitfall_diff_mode()` 的**人可讀分支**（`scripts/lumos`）多印一行：

```
tier: standard
→ 派審查員前:lumos impact --diff <range>(附 manifest 當第二鏡頭,固定席=帶硬合約/事故的節點必答)
```

- **`--json` 分支一個字都沒動**——那是 pre-push 讀 verdict 的路徑，混進散文會讓解析端壞掉
- **提示帶真實 range**，可直接複製貼上（寫死佔位符等於沒用）
- **不真的跑 impact**：實測 0.18s vs 4.7s，而本函式在 pre-push 熱路徑逐 ref 跑

### 驗證

`t_pitfalls_diff_prints_impact_lens_hint_human_only`，6 條斷言，含兩條「現場成立」前置。

**兩個還原翻紅釘各驗一條**：
- 拿掉那行 print → 「人可讀要有提示」「提示要帶真實 range」翻紅
- 把 print 移出 `else`（兩邊都印）→ 「`--json` 不得混進提示」「每行必須是合法 JSON」翻紅

全套 2119 → **2125 全綠**。

### 這條提示的效力（誠實）

**它擋不住任何東西。** 忘了照樣跑得完全程。它買到的只有一件事：
**在我一定會看的那個輸出上，把下一步寫出來。**

夠不夠，要看之後的 Verification 節點裡還會不會再出現「派 reviewer 前沒跑 impact」這個形狀。
