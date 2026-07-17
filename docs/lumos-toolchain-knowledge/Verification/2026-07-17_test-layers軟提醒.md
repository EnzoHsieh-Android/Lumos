---
type: verification
status: pass
date: 2026-07-17
valid_under:
  - "cmd_test_layers 簽名與 .lumos/test-layers.json schema 不變"
  - "pre-push advisory 段未動"
revalidate_when:
  - "test-layers.json schema 改動"
  - "pre-push 呼叫段改動"
  - "_testlayers_* 函式改動"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[test-layers軟提醒_計劃]]"
  - "[[test-layers軟提醒_實作計畫]]"
related:
  - "[[test-layers軟提醒_計劃]]"
  - "[[test-layers軟提醒_實作計畫]]"
summary: |-
  TEST:全量 1197 passed 0 failed(t_testlayers_units 純函式+t_testlayers_cmd e2e:無宣告靜默rc0/命中提醒/壞range fail-open/缺--diff rc2);bash -n pre-push OK;anchor approve 過(pre-push+test_lumos.py)
  VERIFY:T1 純函式(config 載入 fail-open+棧命中去重保序)/T2 cmd_test_layers 子命令+argparse 接線(JSON/人讀雙輸出)/T3 pre-push advisory 段(|| true 隔離,恆 rc0,anchor approve 已過)/T4 本節點(code-loop skill test-layers 鏡頭併入+圖譜收尾)——四 task 對應 [[test-layers軟提醒_實作計畫]]
  KEY:valid_under=cmd_test_layers 簽名與 .lumos/test-layers.json schema 不變、pre-push advisory 段未動;revalidate_when=schema 改動/pre-push 呼叫段改動/_testlayers_* 函式改動
---
# 2026-07-17_test-layers軟提醒

驗證 [[test-layers軟提醒_計劃]] 落地——`lumos test-layers` 子命令(vault-free,恆 rc0)+ pre-push advisory 段 + code-loop skill 鏡頭三件套,四 task TDD 全量測試通過。

## 測試結果
- `scripts/test_lumos.py` 全量 **1197 passed, 0 failed**。
- `t_testlayers_units`:宣告檔 fail-open 載入(無檔/壞 JSON/非 dict 頂層皆回 None)+ 棧命中去重保序+計數。
- `t_testlayers_cmd`(e2e,臨時 git repo + subprocess 跑 CLI):無宣告檔靜默 rc0、命中提醒(人讀+JSON 雙輸出)、壞 diff range fail-open rc0、缺 `--diff` 唯一 rc2。
- `bash -n scripts/hooks/pre-push` OK;pre-push 段 `|| true` 雙保險,恆不影響 rc。
- pre-push 是 anchor 保護檔,T3 已 `lumos anchor approve --note` 走正門。

## 交付範圍
1. `_testlayers_load_config` / `_testlayers_hits` 純函式(scripts/lumos)。
2. `cmd_test_layers` 子命令 + argparse 註冊/dispatch(`lumos test-layers --diff <range> [--repo] [--json]`)。
3. `scripts/hooks/pre-push` 尾段軟提醒(advisory,`|| true` 隔離)。
4. `skills/lumos-code-loop/SKILL.md` §3「派乾淨 reviewer」新增 test-layers 鏡頭段(impact 鏡頭之後,有宣告才附)。

## 誠實天花板(承 [[test-layers軟提醒_計劃]])
關「忘了跑」,關不掉「刻意不跑」——v1 純 advisory,不驗「有沒有真的跑」;消費專案真機驗證(LandmarkMember 或前端)留待 ship 後行動,不在本輪範圍。
