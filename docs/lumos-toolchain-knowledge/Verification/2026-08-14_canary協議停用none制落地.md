---
type: verification
status: pass
date: 2026-08-14
valid_under: scripts/lumos 現行五處閘謂詞(panel/_round_valid_m2/light/verify-progress/settle)、test_lumos.py -k panel(49)/canary(66)/loop(215) 全綠、kind=none 純加性(舊 caught/missed 語意未動)
revalidate_when: 動任何 loop status 收斂謂詞、動 canary record 欄位、或重啟 canary 協議時
tags:
  - type/verification
  - status/pass
summary: |-
  VERIFY:canary 協議停用(Systems/canary-audit d5)的工具面落地驗訖——①record kind 加 none(無植入輪純處置帳載體)②五處閘謂詞納 none:panel 輪有效(none 制=記帳席≥2 且 0 missed)/_round_valid_m2(五consumer共用)/light(ratchet+末輪+K-streak good)/verify-progress(caught_ok)/settle(is_caught_round)③嚴重度合取讀 caught+none(原只讀 caught,none 輪會盲掉存活 findings 假 PASS——新測試翻紅釘釘住)
  TEST:t_loop_panel_none_kind 三向(none×2 乾淨→rc0/none 輪 major→rc1/單席→rc1)+既有 -k panel 49、-k canary 66、-k loop 215 全綠(舊帳回放語意未動)
  KEY:設計原則=純加性——caught/missed 舊分支原樣保留,歷史帳回放與 A 案 K=2 機制碼不動;none 只是第三值
---
# 2026-08-14_canary協議停用none制落地

驗證 [[Systems/canary-audit]] d5(協議停用)的工具面配套:停用植入後每輪仍須記帳(record 是處置閘的讀取源),故 kind 需一個中性值,且所有消費 caught 的閘謂詞不得把 none 輪判死或盲讀。

## 改動與驗證

1. **record 收 `none`**:parser choices 加值+docstring 標協議停用。測試:record none rc0。
2. **panel 輪有效 none 制**(`_panel_round_conjuncts`):none 輪=記帳席≥2 且 0 missed 即有效;嚴重度合取改讀 caught+none——**不改會假 PASS**(maxsev 只算 caught 列,全 none 輪的 major 被盲掉),`t_loop_panel_none_kind` 第②向釘住。
3. **`_round_valid_m2`**(gate/fold/定錨/ledger/W 歸屬五處共用):白名單納 none、席數計 caught+none。
4. **light 閘**:ratchet(major 永久升級)與末輪判定納 none——ratchet 不納會使停用後 major 輪失去永久升級(閘變鬆)。
5. **循序 K-streak `good()`/verify-progress `caught_ok`/settle `is_caught_round`**:一律 kind∈{caught,none}。

測試:新增 `t_loop_panel_none_kind`(三向);回歸 `-k panel` 49、`-k canary` 66、`-k loop` 215 全綠。

## 邊界

- 歷史 caught/missed 帳回放語意未動(純加性);A 案 K=2 與抽查機制碼保留。
- `loop next` 仍會印植入指引(工具封存未拆)——skill 頁頂告示明文「照跳過」,此為已知的殘留摩擦,非缺陷。
- 觸發脈絡之一:Landmark code-crossclaim 實跑「r5 單席 caught<2 輪無效白跑」(見 [[Issues/loop機制痛點_Landmark_code-crossclaim實跑回饋]])——none 制下輪有效只看記帳席數,該型白跑不再發生。
