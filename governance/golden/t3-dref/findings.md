# t3-dref — 凍結 findings 語料（3 輪 panel，達 cap 未 clean 收斂）

design-loop `t3-dref`，panel 模式（每輪 3 sonnet 異鏡頭 + Codex 否決席讀 repo + opus 辯方）。三輪 canary 全 caught（達注意力門檻），findings 逐輪收窄（12→6→5），但 r3 三席匯聚指出 v3 晚加設計仍是半成品 → 達 3 輪 cap、人裁凍結。校準用途：replay 時對照各模型接住率。

---

## r1（canary a✓ b✓ c✗｜12 findings｜severity blocker）

canary：a=candidates 只列 valid vs 測試含已翻案（矛盾）✓；b=promote 兩步 vs 單次 atomic ✓；c=`--force` 未定義旗標 ✗（C 席漏抓，但挖出更深真 blocker F1/F2，判決按紀律不完全採信、F1/F2 自證真已折）。
Codex 否決席：**核心成立**——candidates 用 `build_typed_index`+`parse_decisions` 可建、E2/E3 不對稱信任接線行號全對。

存活真 findings（全折 v2）：
- **suggest 非 lumos 命令**（A/C/Codex）→ 改 Claude 編排「suggest 流程」合稱，CLI 只有真原語。
- **批次選取無原語**（C/A）→ 補 `backlog`，與 candidates 同集合。
- **add-ai 自驗存在性**（Codex/A/B）→ `_append_decision_ref` 不驗目標存在，add-ai 自己驗。
- **promote 雙欄原子 + 重驗 dangling**（Codex/B）→ 單次 read-modify-write、防失效 ref 蓋章洗白。
- 原語目標 `<驗證>`→`<節點>`、prune 兩欄語意、candidates 無 id 跳該條、audit 改顯式 `list`、候選摘要機械化。

## r2（canary a✓ b✓ c✓＝3/3｜6 findings｜severity blocker）

canary：a=promote-warn / b=backlog-單欄 / c=prune-單欄，全被抓。
Codex：v2 底層零件足夠（六原語 argparse 無衝突、讀側/writer 夠），唯 promote/prune 需**新雙欄 edit helper**、promote 需 **count-based expected_check**。

存活真 findings（折 v3）：
- **T3 覆蓋誠實降級**（B#1 blocker→人裁「收窄」）：candidates/backlog 是 1-hop 邊解析、只碰**結構可達子集**；「覆蓋背包大宗」宣稱撤。← **這是凍結的關鍵 ROI 信號**。
- **否決記憶**（B#4 major）：加 `decision_refs_rejected` + `prune --reject`。← v3 晚加，成 r3 非收斂焦點。
- promote dangling rc=2 拒非 warn、backlog 鎖有 id 決策、candidates skipped_no_id 計數、兩欄都有 dedup 收斂、add-ai 冪等明文、存在性≠權威性、reindex id 穩定性交叉引用 M1、反向測試 prune 正欄→E2 停抑制。

## r3（canary a✓ b✓ c✓｜5 findings｜severity major｜達 cap）

canary：a=add-ai 不查 rejected（矛盾）✓；b=兩欄 vs 三欄（矛盾）✓；c=兩欄都有 rc2 vs dedup（矛盾，論證 dedup 對）✓。

三席匯聚的**根因**（非收斂集中處）——v3 晚加的 `decision_refs_rejected` 是半成品：
- **無解除原語**（永久鎖死）／**不在 candidates+promote 各層強制**（繞道洗白）。
- **backlog 正確判準＝集合差**（候選−三欄≠空）**非 N 欄皆空**（深洞，B 席）。
- **candidates 該讀側標/濾 rejected**，非靠 add-ai 晚拒。
- count-check「`_ai` 無」語意模糊（該＝此 ref 不在 `_ai`、非整欄空）／add-ai 缺「已在正欄」檢查／T1 不認 rejected。

→ **達 3 輪 panel cap 未 clean 收斂**（非收斂localized 在 rejected-memory late add-on）。收斂到明確 v4 方向（見 spec.md §v4）→ 人裁凍 golden、暫停實作。

---

## 誠實天花板（凍結時記）

1. 三輪 canary 全 caught，證「醒著的審計員」在跑；但 **c 席 r1 漏抓表面 canary、卻挖出更深真 blocker**——注意力與深度不總是同一軸。
2. 凍結不是「T3 設計失敗」，是 design-loop 正確履行**功能體檢**職能：暴露 T3 是窄覆蓋小加分（結構子集），且為它堆的保險機械成本 > 收益。**T1 已交付真價值**、不受影響。
3. v4 方向（雙欄 + 集合差 backlog + candidates 讀側去重）尚未再過 loop——日後撿起實作前，v4 本身應重跑一輪 panel 確認簡化無新洞。
