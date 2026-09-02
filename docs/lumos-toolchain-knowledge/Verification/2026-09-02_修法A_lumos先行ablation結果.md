---
type: verification
status: pass
date: 2026-09-02
valid_under: Claude Code 2.1.258 的 claude -p 預設模型;探針判準=期望的 lumos 指令出現在任何 Grep/Read/grep 之前;兩組都保留 ~/.claude/skills 的 lumos-project-notes 與 PreToolUse impact-hook;題庫=commands.jsonl 23 題+answers.jsonl 5 題(2026-09-02 版);without 組定義=砍 CLAUDE.md「### 第一個工具呼叫是 lumos」到「### 三條鐵則」之前+LUMOS_ENTRY_HOOK_OFF=1
revalidate_when: 換模型或 Claude Code 大版;改探針判準(forbid_before 集合);CLAUDE.md 那一節結構改動(尤其 09-20 若裁「對照表留、勸告句拿掉」要用同一套題重跑當第二組對照);題庫擴到 paraphrase/discipline/absence 時另立節點不覆寫本篇
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/修法A_lumos先行ablation_計劃]]"
---
# 2026-09-02_修法A_lumos先行ablation結果

> 白話:第一次量自家一條散文規矩有沒有用。拿掉 CLAUDE.md 開頭「動手前第一個工具呼叫是 lumos」那一節(加上開對話時 hook 唸的同一句),同樣 28 題各跑 3 次,Claude「先查圖譜再動手」的比率從 **94% 掉到 58%**。差 35.7 個百分點,遠超過跑之前寫死的「15 個百分點算有效」門檻。★結論:那一節有用、留;它是本專案第一條被前後量過的紀律。★但它改的是「先查圖譜還是先 grep」的**路徑**,不是答案對不對——答案題內容正確率兩組幾乎一樣。

## 四個尺(只算有效場;撞用量上限的 115 場不算)

| 尺 | with(現況) | without(拔那一節) | 讀法 |
|---|---|---|---|
| M1 通過率(期望 lumos 指令在 Grep/Read 之前) | 79/84 = 94.0% | 49/84 = 58.3% | **差 35.7pp ≥ 15pp → 預註冊規則 2:有效、留** |
| M2 整場有沒有敲過 lumos 子指令 | 84/84 = 100% | 62/84 = 73.8% | 拔掉後四分之一的場次**一次都沒敲**,直接 grep/sed 讀檔到底 |
| M3 首次敲 lumos 的步數中位 | 1(第 0 步多半是調 skill) | 1 | 兩組一樣——會敲的都很早敲;差在「敲不敲」不在「幾步後才敲」 |
| M4 答案題(5 題×3)「敲對指令且答案含關鍵事實」 | 15/15 | 0/15 | 預註冊定義=指令+答案合取,without 全敗在指令那半;見下面事後分析 |
| 儀器噪音(同題三次不一致的題數) | 1/28 = 3.6% | 6/28 | 規則 5:<30%,結論不降級;without 行為明顯更隨機 |
| 缺場 | 0 | 0 | 規則 6:第一輪撞上限損失 115 場,補跑一次(runner 逐題補缺)後齊 |

M1 差值的兩組每題明細(3 次中過幾次)存 `governance/eval/ablation-lumos-first/2026-09-02/summary.md`。12 題有差:s06-impact 3→1、s07-rename 3→2、s17-ci 3→0、s18-guard 3→1、s20-recent 3→0、s21/s22 還原題 3→2、s23-restore-existing 3→0、答案題 a01–a05 各 3→0;s14-design-loop 兩組都不穩(1 vs 2);s15-new-verification 兩組皆 0/3(既有失敗,與本案無關,週抽查 08-31 已紅過)。

## 事後分析(★非預註冊,只當補充解讀★)

- **答案內容本身對不對**(只比 `answer_expect` 的關鍵事實,不管走哪條路):with 15/15,without **14/15**。拔掉那一節後 Claude 用 `grep -ril canary docs/…` + `sed -n` 讀檔,一樣答出「2026-08-14、Enzo 裁、引句錨定蓋掉」。所以那一節**沒有讓答案更對**,它改的是取得答案的路徑。這對 [[Issues/散文紀律沒有退場機制]] 的意義:規矩的價值要用「它想改變的那個行為」來量(這裡是先查圖譜),用結果面的尺量會量不出來——兩種尺都要擺著。
- **失分是丟了「對照表」還是丟了「勸告句」**(計劃節點第一輪就記的觀察):12 題失分裡,期望指令只在那張表才有專屬對應的只有 `s17-ci`(ci-wait/ci-status)與部分 `s20-recent`;其餘 10 題期望的是 search/context/show/impact 這類通用進場指令,skill 索引也有。★所以主效應是「先查圖譜再 grep」這個行為本身,不是查表功能★。09-20 若要再細拆(表留、勸告句拿掉),用同一套題跑第三組即可。
- **第一動作分布**:with 組 84 場裡 45 場第一刀直接敲 lumos、39 場先調 skill;without 組只有 22 場直接敲、61 場先調 skill。也就是拔掉那一節後,Claude 更依賴 skill 說明才知道要用 lumos——skill 撐住了 M2 的七成四,那一節撐的是剩下那四分之一加上「別先 grep」的順序。
- **失敗形態**(without 35 場失敗):20 場整場沒敲 lumos;8 場敲了但在它之前先 Grep/Read;7 場敲了 lumos 但不是題目期望的子指令(例:`s17-ci` 敲 search 不敲 ci-wait)。

## 儀器與過程(誠實帳)

- **成本不是錢,是帳號配額**:第一輪 4 路平行 35 分鐘就撞到五小時窗口上限,之後 115 場全是 4 秒假失敗;探針原本把它記成「沒敲到」。同日修:`is_limit_hit` 標記不算分、`--wait-on-limit` 撞到等重置、runner 改逐題補缺。第二輪(12:35–14:40,2 路)沒再撞。★每窗口約 55 場探針★是之後所有探針實驗的硬約束。
- **「敲過 lumos」的尺第一版灌水**:用字界比對把 `grep … docs/lumos-toolchain-knowledge/` 路徑也算成敲了 lumos,without 組 M2 曾顯示 98.8%;改成「lumos 後接空白+子指令」重算得 73.8%。上表是修正後的數字。
- **calls 截斷**:第一版結果只存前 12 個工具呼叫(with 34 場、without 42 場超過 12 步),M2/M3 重算時第 12 步之後的 lumos 呼叫看不到 → without 的 M2 可能**略低估**;M1 不受影響(判定在記錄當下用全序列算)。第二版已改存全部。
- **兩組共用 skill 文字**:量的是那一節在 skill+機械 hook 之上的邊際貢獻,不是「圖譜先行」理念的總效果。
- **模型版本**:Claude Code 2.1.258 預設模型(未釘 model id);跨版重跑要記。
- 測試:`scripts/test_autonomous_loop.py` 115 條綠(本案 +9:strip/lumos_stats/limit/backfill/needed/merge)。
- 原始資料:`governance/eval/ablation-lumos-first/2026-09-02/`(gitignore,不入庫;本篇記數字)。
