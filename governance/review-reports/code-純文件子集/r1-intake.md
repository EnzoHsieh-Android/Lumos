# r1 收貨(2026-09-18;六席全交回才動工作目錄;外家 finder/否決缺席:Codex 額度用盡至 2026-09-19 21:45,結論降級為單家族視角)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| C1 | 正確性-sonnet | major | HIT:governance/Tool.PY 判成 docs(_nodehome_code_kind 大小寫敏感) | 折:文件判定改成副檔名白名單 _DOCS_ONLY_EXTS(lower 比對),不再靠「不在程式清單」;案例③c |
| C2 | 正確性-sonnet | major | HIT:a...b 拿左端點當起點 | 折:_range_base 三點算 merge-base,_pitfall_tier 同族一起換;案例⑪/⑪b。誠實界線:_is_code_file 磁碟優先,checkout 跟範圍終點不同時仍會讀到磁碟那份(既有行為,自動閘不走這條) |
| R1 | 併發與資源-sonnet | major | HIT:--keys check 選中 1021/1021 | 折:_affected_test_keys 只取頂格 def(縮排的是巢狀/方法);執行器一個關鍵字選中 >30% 就丟並印出;案例⑤b、太泛關鍵字 |
| R2 | 併發與資源-sonnet | minor | HIT:keys 在分片 wait 完才串行跑 | 折:keys 跟 docs 各自分片、同時跑(_run_group) |
| R3 | 併發與資源-sonnet | major | HIT:push-check 先存檔跑完才 cat | 折:tee 即時印 + PIPESTATUS 取 rc |
| R4 | 併發與資源-sonnet | minor | HIT:_sg_out 逐檔 rm、exit 1/中斷會漏 | 折:所有暫存收進 _PP_TMP,掛既有 trap |
| B1 | 邊界與輸入-sonnet | blocker | HIT:governance/tools/x.rb 判成 docs | 折:同 C1(反過來列文件);案例③b |
| B2 | 邊界與輸入-sonnet | major | HIT:foo,bar.py 的關鍵字 round-trip 被切 | 折:關鍵字只留 [A-Za-z0-9_.-]{3,};案例⑤c |
| B3 | 邊界與輸入-sonnet | minor | HIT:「不跑全套」後接「全套約 8 分鐘」 | 折:子集那條路訊息不提全套時間;測試斷言 |
| G1 | 合約與圖譜一致-sonnet | major | HIT:t_commands_table_shape 不在 --suite docs(路徑在輔助函式裡) | 折:文件子集連看測試呼叫的本檔輔助函式(一跳,只套根目錄文件規則);斷言它在 |
| G2 | 合約與圖譜一致-sonnet | major | HIT:假執行器 keys 只回 0/3,「有紅要擋」沒測試走到 | 折:假執行器 FAKE_KEYS_RC,新情境 rc1 擋 |
| G3 | 合約與圖譜一致-sonnet | minor | HIT:30% 是拍的 | 折:改 25% 並註明實測 209/1021≈20% 與為什麼要有上限 |
| A1 | 架構對齊-sonnet | major | HIT:_DOCS_SUITE_PATHS 手抄一份 | 折:執行器 _load_lumos_inproc()._DOCS_ONLY_PATHS;相等測試改成「本檔沒有模組層白名單常數」 |
| A2 | 架構對齊-sonnet | minor | HIT:CI 用 "$BEFORE" 既有步驟用 "$BEFORE^{commit}" | 折:對齊 |
| A3 | 架構對齊-sonnet | minor | HIT:兩函式各跑一次 git diff | 折:_test_suite_for_range 回 code 清單,_affected_test_keys 吃它 |
| S1 | 資安-sonnet | major | MISS(席位原句):不相干的★程式檔★搭便車——小改動閘的擴散查整段範圍的程式檔,落點外就擋(t_pitfalls_tier_light_sources ④);HIT(鄰近形狀):測試檔/skills/workflow 這種既非文件也非程式的檔擴散不查,會搭便車 | 折:pitfalls 多 light_ok(非文件檔全是程式檔),掛鉤 light 要它為真;新情境「夾測試檔 → 全套」 |
