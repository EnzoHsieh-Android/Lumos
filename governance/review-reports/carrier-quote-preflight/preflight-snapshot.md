---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
  - risk/守衛面
lands_in:
  - Systems/canary-audit
---
# 載體零引句在記帳前拒收_計劃

## 問題與範圍

零發現報告誤帶處置集合時，記帳成功把 literal `none` 當作一條 finding ID；最後處置閘因載體報告沒有引句而失敗。這是輸入錯誤造成的流程折返，不能解釋成修補產生了新 bug。來源是前案 code-seat-input-validation 的 r2 原始帳與 protocol correction；新最小探針另保存 record rc0／gate rc1 與正確空輪 record rc0／gate rc0 的對照。

PRIOR-ART: Python 官方 all() 文件明定空集合也回 True，空驗證需有獨立語意；argparse 的 error() 以狀態碼 2 回報無效輸入。採用現有 quote 抽取器與 rc2 出口，不引入 schema 套件。參考 https://docs.python.org/3/library/functions.html#all 與 https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.error 。

RETIRE-IF: 如果 canary 記帳改成直接共用完整處置閘的前置證據驗證，且同組負向／正向控制仍通過，就撤掉這裡重複的局部零引句分支。

## 核心裁定

只把「有處置集合的載體報告必須有可核對引句」這項既有讀側判準往寫側移。保留原處置閘，舊帳仍以同樣判準拒絕；不清除歷史錯帳，不增減輪數，不重置前案。不做 findings 數量與全輪彙總 ID 數相等的限制：載體是全輪集合，數量欄是該席存活數，兩者本來不同。`none` 可以是合法真實 ID，不能全域當成空集合。

正確零發現空輪不帶任何處置旗標，允許沒有引句、照常重驗所有留痕並通過。非載體的無引句報告不加新限制。只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。

## 驗收條款

- [S1] 當載體報告零引句且快照可讀，記帳器應以 rc2 拒收，提示沒有引句、取消零發現輪的處置選項或改用可核對的載體；不得追加成功 canary 帳列或印成功訊息。普通與 -O 執行都驗；ID 包含 none 及一般 ID。 [test:t_canary_carrier_zero_quote_rejected]
- [S2] 當非載體的零發現報告沒有引句，記帳器應成功記帳；正確空輪仍能通過處置閘且不宣稱驗了引句。 [test:t_loop_disposal_zero_findings]
- [S3] 當載體引句足夠長度且全錨，記帳器應成功記帳，包括真實 ID none、未填 findings，以及全輪 ID 數大於載體席的 findings 數。 [test:t_canary_carrier_quote_positive_controls]
- [S4] 當載體有引句但快照缺失，記帳器應沿用快照 IO 錯誤出口，不以「零引句」誤導；新拒收前後 canary 帳逐位元相同。 [test:t_canary_carrier_zero_quote_rejected]

## 回退

這是現有寫側函式的局部改動；回退該功能提交即可恢復原寫側行為，讀側處置閘繼續拒絕零引句載體。沒有不可逆外部動作。保留實際歷史錯帳與試驗收據，避免回退時抹去事故證據。

## 實務隱患

- 已排除金流、寄送、正式環境資料異動與 Windows：只處理審查報告寫帳前驗證。
- 全輪集合不能等同單席數量；以正向控制防止把收斂補強變成新誤擋。
- 零發現空輪和零引句載體有不同語意；前者是正確使用，後者已有讀側閘判失敗。
- 保留可讀快照與 IO 失敗的區別；不吞非本案例外、不設旗標繞過。
- 隔離複本 hooks 不啟用，推送前手動執行來源家、筆記形狀、新增告警、合約測試及乾淨複本回放。

REVISIT:2026-10-20 收集接下來十次真實記帳收據，核對零引句前置拒收有無誤擋與少耗一輪；從 lumos canary 的 blocked／成功帳以及相關迴圈卷證核對，合成測試不算實際輪數改善。
