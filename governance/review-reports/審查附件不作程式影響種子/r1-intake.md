preflight-4: ran

首輪前掃由全新唯讀 lumos_reviewer /root/artifact_design_preflight 完成，四類均核查；無舊報告輸入。機械宣稱語意相符，三處正面測試使用30秒；零預算入口是正式源碼修復。

前掃 P1 未定義「未知」已補模式／物件／上限失敗的具體邊界；P2 裸卷證名已補統一目錄；P3 范圍矛盾已改為分類、共享 raw 與零預算三部分，取消守衛面排除並承認實作後補審。修改前→後逐字對照見 preflight-changes.json；修改前真檔見 preflight-plan-before.md。來源函式以正式審材為準，前掃未改核心裁定。

本設計迴圈與 code-review-artifact-impact-inputs 的第三輪代碼審不同，沒有重設其三輪上限。本輪所有席報告收齊之前不得修改被審材料。

## 正式收貨與重現

六席 raw 全部收齊後才改測試與計劃。全部 report-normalize、quote-check、seat-check 為0，且 seat-check 無 unreported/out_of_scope；五席 refcheck 為0。rollback refcheck=1 來自假設 fixture 路徑不存在，裸 file:line 也未進機械宣稱；不改原始報告，採下表真 Git 控制而非把該佐證算通過。

|ID|重現|採信|處置|
|---|---|---|---|
|DESIGN-BOUNDARY-1|python3 scripts/test_lumos.py -k t_impact_diff_special_paths；1過3敗|HIT|折入S2|
|DESIGN-VERIFICATION-1|同一真入口，精確路徑、家與事故皆失敗|HIT|折入S2，同根因|
|DESIGN-ARCHITECTURE-1|同一真入口，假種子被保留|HIT|折入S2，同根因|
|DESIGN-COST-1|python3 scripts/test_lumos.py -k t_impact_diff_head_batch_total_cap；1過2敗，請求內容累計2MiB大於1MiB|HIT|折入S3；非實際OOM|
|DESIGN-COMPATIBILITY-1|python3 scripts/test_lumos.py -k t_review_role_bookkeeping_remaining_budget；0過3敗，raw timeout20並額外讀首行，無內容候選時timed_out false|HIT|折入S4；可控時鐘|
|DESIGN-ROLLBACK-1|python3 scripts/test_lumos.py -k t_impact_diff_bookkeeping_boundary_rename；2過3敗，真Git前置R且終點644，files與角色輸入皆空|HIT|折入S5；普通角色改名約定保留|

具體 stdout、源碼指紋、argv、rc 在 r1-boundaries-red-rerun.json，測試對應正式源碼2f138ebf。六個ID對應四個根因，不把重複報告算六種新漏洞。每個major有可執行反例且父代理已查驗，依技能不另派辯方。verification 席寫批次有數量界線的判準未採信，依實際code/控制裁定只有單檔大小界線。
