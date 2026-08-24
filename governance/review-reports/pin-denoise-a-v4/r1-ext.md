# 外部審查結果

## f1 — blocker

**Spec 段落：**「落地驗收」§116，並與主案 §71–76、工具清單 #2 衝突。

引句:「P@8/nDCG:**逐 byte 相同**(測試釘)。must_in_out:不變(測試釘:被降節點仍在 JSON results)。」

**問題：**驗收仍要求被降節點留在 JSON `results`，但本輪核心安置模型明定 `results` 完全不含 lane、被降節點只能出現在頂層 `lane`。這不是措辭問題，而是互斥的可執行測試要求：照 §116 實作會直接破壞獨立鍵模型；照測試③「被降者在 JSON lane 鍵」實作則 §116 必翻紅。應改為「被降節點仍在 JSON 輸出之頂層 `lane`，且 cap 內計入 must_in_out」，並刪除「must_in_out:不變」這個跨 cap 的絕對宣稱。

**查證：** `/tmp/pin-denoise-a-v4-r1.md:71-80`、`:114-116`、`:126-133`；現行 JSON 組裝點 `scripts/lumos:14523-14528`。

## f2 — blocker

**Spec 段落：**主案 §2 opt-in 名單、工具清單 #2b/#3、測試 #6。

引句:「②hook `build_ranked_context` 新小節讀 `data["lane"]`」

**問題：**hook 的 opt-in 不只 `build_ranked_context`。現行 `inject_ranked_context` 在呼叫 formatter 前先以「`results` 與 `stack_questions` 都空」為條件直接 return；新 CLI 完全可能輸出 `results=[]`、`lane=[…]`。這時即使 `build_ranked_context` 已支援 lane，也永遠不會被呼叫，整條參考道靜默消失。工具清單及 11 條測試均未要求修改/測試這個入口守衛；至少須把 `lane` 納入非空判定，並新增「lane-only payload 仍產生 additionalContext」回歸測試。

**查證：** `scripts/hooks/claude/impact-hook.py:332-373`、`:376-383`、`:494-501`；lane-only 可由現行候選流程在只有被降 indirect、沒有存活 pins/free/rescued 時形成，產生流程見 `scripts/lumos:14457-14475`、`:14480-14528`。

## f3 — major

**Spec 段落：**主案 §2 opt-in 名單、工具清單 #2b。

引句:「★opt-in 名單(#2b;獨立鍵模型下「不改就不受影響」,要 lane 的才改)★」

**問題：**全 repo 的 ranked-impact 消費者仍漏列 `governance/eval/build_goldset.py::edit_pool`。它只抽 `results` 建未來 edit 題標註池；新 lane 節點不會被送去標註，但 `retrieval_eval.edit_universe` 又按 spec 將 lane 帶入 must/unjudged 口徑。結果是新建或 append 的 goldset 系統性漏標 lane，之後評測可能被未標閘擋住，或 lane 在計分時被當成 0。即使「本案凍結現有 goldset」，這個長期 producer 仍是獨立鍵模型的實際讀者，不能從 opt-in 清單省略。

**查證：** `governance/eval/build_goldset.py:157-167`；`governance/eval/retrieval_eval.py:122-139`、`:159-168`、`:207-233`、`:318-362`。

## f4 — major

**Spec 段落：**主案 §2 hook opt-in、實務隱患／回滾。

引句:「截斷後這一份=JSON `lane` 鍵=人讀=hook,兩個口徑合一」

**問題：**沒有定義 hook/CLI 混版相容協定。新 hook 若以 `.get("lane", [])` 讀舊 CLI，能安全退化；但舊 hook 配新 CLI 會完全忽略頂層 lane，且在 lane-only 回應中不注入任何 context。現行 hook 透過 PATH 尋找已安裝的 `lumos`，hook 檔與 CLI 並非同一檔案或原子載入，因此混版是實際部署狀態，不是理論情境。總開關只控制新 CLI 行為，無法修復「新 CLI 已轉正、舊 hook 尚未更新」的靜默漏報。Spec 應指定安裝更新順序或 schema/capability handshake，並測試「新 hook＋舊 CLI」與「舊 hook＋新 CLI」兩向相容；至少轉正前必須保證 hook 先更新。

**查證：** `scripts/hooks/claude/impact-hook.py:185-203`、`:332-383`、`:456-501`；新 CLI schema 組裝點 `scripts/lumos:14523-14537`。

## 已讀，無 finding

- 間接保送限定 `INVARIANT`／`IRREVERSIBLE`，以及 `RISK·不可逆` 與 `IRREVERSIBLE` 的精確值區分。
- lane 產生端 cap、R 公式與排序鍵 `(-score, hop, node)`。
- `meta.lane`／`meta.lane_truncated` 的定義。
- `cmd_impact_diff`、sync-check 與 `_bound_tests_for_diff` 明文不消費 lane。
- per-split 棘輪協定、工具清單 #6–#8及 r3 審計紀錄；除上述互斥驗收與漏接點外，未找到其他否決級問題。

最嚴重 severity：blocker
