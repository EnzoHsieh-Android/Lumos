---
type: system
status: deferred
created: 2026-06-26
updated: 2026-06-26
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/deferred
summary: |-
  FLOW:lumos baseline approve <node>(算 hash→寫人工 approve 基線+留痕進 gov)｜lumos baseline status(唯讀印 vs 基線 diff)｜doctor Check C2(定位 core_base→比對當前 vs 基線→未 approve 差異 hard block,--ci 才硬擋)
  KEY:守「核心節點合約語意欄位」(summary｜decisions[].content｜valid_under)被靜默改/增/刪——一筆改錯沿 core_refs 擴散成全下游 session 真值;缺的不是 git revert,是「偵測+顯式 approve 閘」
  KEY:設計階段、擱置實作(2026-06-19)——scripts/lumos 尚無 baseline 子指令/Check C2;守備對象現僅 1 個核心合約節點,等 core_refs 消費端 >1 再進實作
  KEY:v2 pivot——v1「守不變式標記行」前提錯(獨立 grep 證核心節點 0 條該標記),改守 summary/decisions/valid_under 這些實際承載合約語意的欄位
  KEY:不自動更新 baseline(本場景正是「改壞但 doctor 照綠」,自動更新=自動吞下下毒);只 hard block、不軟硬分級;不自動 revert(git 的事)
  DEP:doctor Check C(core_refs 指針存在)｜Env(core_base)/load_vault 第二 vault｜parse_decisions(note.fm_lines)｜lumos gov reader event schema
  TEST:無(擱置實作,未寫測試);設計 canary-loop 4 輪(含 2 輪 opus)未達形式 K=2 收斂
  VERIFY:無(無實作/測試/真機證據)
decisions:
  - content: 守備對象從「核心節點的 ★INVARIANT★ 行」pivot 成 summary/decisions[].content/valid_under 三類欄位
    context: v1 前提是「核心節點靠 ★INVARIANT★ 承載合約」;R1 審計+獨立 grep 證實 citrus-core-knowledge 全 repo 0 條 ★INVARIANT★、全 vault 僅 1 條 core_refs——實際承載合約語意的是 summary/decisions/valid_under
    why_chosen: 守實際承載語意的欄位才守得到唯一存在的核心節點 custtransfer-semantics,且隨核心知識成長自動擴大;守空集合的 v1 是致命前提錯
    decided: 2026-06-19
    valid: true
  - content: approve 不重用 _append_governance_log,自寫 append 到 consumer vault 的 .governance-log.jsonl,event schema 對齊 gov reader 用 list 形 nodes
    context: R3 opus 揪出的 blocker——_append_governance_log 寫 vault.parent,對 core repo = backend/(非 repo),且無 git commit 時早退(正是 CI-checkout 情境會吞掉留痕);core repo 無 docs/ 層;reader 讀 {gate,kind,nodes[](list),hard},用 {event,node} 單數會解成空 nodes
    why_chosen: 留痕要進 lumos gov ledger 才可追蹤(對齊 loop engineering);schema 不對齊則 gov <node> 篩不到、留痕等於沒留
    decided: 2026-06-19
    valid: true
  - content: decisions 用唯一 decided 日期當穩定 key、valid_under 用 hash 集合 diff;不用位置 #index
    context: R3 opus major——#index 在 mid-list 刪一條會位移、級聯誤報後續條目「被動過」;valid_under 位置 i 同樣級聯
    why_chosen: 集合/唯一-key 比對對 mid-list 刪除穩定(刪一條 = 一個 key/hash 消失,不級聯);approve 強制 decided 唯一、碰撞或缺失報錯要人補,不自動編號
    decided: 2026-06-19
    valid: true
---
# core-invariant-baseline

> **設計階段、擱置實作(2026-06-19)。** 設計稿標題已 pivot 為 **core-content-baseline**(守的是「內容語意」非 ★INVARIANT★ 行);節點沿用檔名 `core-invariant-baseline`。`scripts/lumos` 目前**無** `baseline` 子指令、**無** doctor Check C2,測試亦無覆蓋——本節點記設計,不是已落地系統。

## 是什麼 / 解決什麼
給**跨專案核心知識**(`core_refs` 指到、住在 core-knowledge repo 的節點)的**合約語意欄位**算 hash、存進**人工 approve 的 baseline**;doctor 新增 **Check C2** 比對「當前 vs baseline」,語意欄位被靜默改/增/刪且未 approve → **hard block**,放行只能靠顯式 `lumos baseline approve`(留痕)。

**缺口**:改一條核心節點的 `summary` 或某條 `decisions[].content` 不破連結、不讓 doctor 變紅(Check C/T/R 都不看語意文字有沒有被動過)、grep 也搜不出。一筆改錯**靜默變成所有下游 session 的真值**,沿 `core_refs`/wikilink 擴散。git 本來就留歷史,**缺的不是 revert,是「偵測 + 顯式 approve 閘」**。守的是**記憶狀態**(核心節點合約語意被靜默改寫),**不是** Check R(撤世界動作)。

**源起**:日報 2026-06-19 gap 2 ——「共通節點是多人共編的共享記憶,卻沒有『退回上一版良好狀態』的機制,一筆寫錯會沿連結擴散」;對應 inspiration「借 OWASP 已知良好快照+可回退,doctor 比對標出被動過的鐵則行」。

## 守備欄位(對齊真實 schema)
守這三類**承載「規則是什麼 / 邊界在哪」**的欄位:`summary`、`decisions[].content`、`valid_under`(list,逐條)。
**v1 不守**(留升格):`context`/`why_chosen`/`trade_offs`/`alternatives_considered`(理由欄,改寫風險低、變動頻,守了假陽多);`revalidate_when`/`verified_by`(流程性,非合約本體)。

## 三個單元(設計)
1. **baseline 檔** `core_base/.lumos/core-content-baseline.json`(住被守的 core-knowledge repo、多專案共用)。存 `{text, hash}`(hash = `sha256(normalize(text))[:16]`,常數 `BASELINE_HASH_LEN=16`),text 本體供報文顯示「舊→新」。節點 key = 相對 `core_base` 的 posix 路徑 + NFC。`decisions` key = 該條 `decided` 日期(approve 強制唯一);`valid_under` 用 hash 集合 diff。
2. **`lumos baseline {approve,status}`**:`approve` 先用 Check C 定位邏輯找 `core_base`、再 `Env(core_base)`/`load_vault(core_base)` 直建 transient Env(core repo 無 `docs/*-knowledge` 結構,**不可**走 `find_vault`);`decisions` 抽取走 `parse_decisions(note.fm_lines)`(**不可**用 `note.fields["decisions"]`,parse_frontmatter 對 nested dict 產 garbage);枚舉按節點 `type` 過濾(`core-business`),**非**「欄位非空」(避免擋到非合約的 Verification 節點);寫後自驗、空欄位跳過。`status` 唯讀印四類 diff(一致/被動過/新增/刪除)。
3. **doctor Check C2**:接在 Check C 之後;能定位 `core_base` 且 baseline 存在才跑,core repo 不在環境(CI 未 checkout)→ 跳過、baseline 不存在 → 提示建基線、皆不誤判 block。差異計入 `issues`,**pre-push 走 `--ci` 才硬擋**(bare `lumos doctor` issues>0 仍 exit 0)。

## 跟既有 Check 的分工
- Check C(既有):core_refs 指針「檔案在不在」。
- **Check C2(新)**:core_refs 指到的核心節點「合約語意欄位有沒有被靜默改」。
- Check T:★INVARIANT★ 有沒有綁可執行測試。Check R:不可逆動作有沒有寫回退。

## 已知限制 / 誠實天花板
- **只證沒被靜默改,不證語意對不對**(同 Check T 的 verification≠validation 邊界)。
- **擋靜默改、擋不了明知故改**(hash tripwire 只擋「沒人注意的改」;擋不了「明知故改+隨手 approve 過」)。它抬的是「核心改動必須經一次顯式停頓+留痕」的地板,不是 oracle。
- **守備對象現極少**:目前全域**僅 1 個**核心合約節點(`custtransfer-semantics`),守備價值隨核心知識成長才放大。
- **留痕不對稱**:baseline 住共用 core repo,但 approve 留痕寫執行端 consumer vault 的 governance-log → consumer A 的 approve 對 consumer B 的 `lumos gov` 不可見(B 卻已吃到 A 改的 baseline)。
- **擱置理由**:守備對象只 1 個(對齊計畫「等 core_refs/核心節點變多再做」);此 loop 揭發 canary 機制限制(4 輪 3 次 canary 出問題,真正接住缺陷的是「真 findings + 手動查證」非 canary),形式 K=2 未收斂、硬刷投報率低。**重啟條件**:核心合約節點 >1(或新增 core_refs 消費端)。

## 相關
- 設計稿:`docs/design/2026-06-19-core-invariant-baseline.md`(canary-loop 4 輪 R1–R4 含 2 輪 opus,審計修正紀錄+擱置決定在尾段)。
- 實作計畫:無(擱置,未進 writing-plans)。
- 預定落點:直接進 `scripts/lumos`(要接 doctor/pre-push 硬閘);實作順序 ①core_base 定位+第二 vault+hash → ②`baseline approve` → ③`baseline status` → ④Check C2 比對+hard block → ⑤approve 留痕進 gov。
