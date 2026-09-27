| n | label | confidence | code location | reason |
|---|---|---|---|---|
| 1 | CODE | high | src/rtb/demo/page.py:433-434; src/rtb/demo/server.py:4 | `<meta http-equiv="refresh" content="2; ...">` 逐行可查,展示頁確實每 2 秒整頁重讀 |
| 2 | MIXED | med | claims/*.json(五個檔,實測共 78 支 evidence,非 75);tools/verify_claims.py:1213 | 清單份數與證據測試支數可由 claims/ 目錄與 evidence 陣列長度算出(CODE;現況 78 支非 75,親測確認);「42.4 秒」是單次執行耗時,需實際跑一次才能得到(CONTEXT) |
| 3 | CONTEXT | high | — | 逐字取自決策 d12 的 why_chosen(工程判斷/未有 Eval 證據前不用 Jev 的原則),屬設計理由,程式碼答不出「為什麼」 |
| 4 | MIXED | high | 分析端(src/rtb/analyzer/*.py)未 import src/rtb/executor/capability_signer.py 任何一支檔 | 「寫入相關金鑰不在分析端正常程式路徑上」可用匯入掃描驗證(CODE,已確認);「從第一天就設計並測到」是決策時序/意圖敘述(CONTEXT) |
| 5 | CODE | high | tests/executor/test_audit_tables.py | 「停下紀錄、核可、DSP 操作紀錄沒有機械守衛」是程式碼可查的型別斷言(現況已補上只增不改的機械守衛測試,敘述現已不成立,但仍屬 CODE 類型) |
| 6 | CODE | high | src/rtb/demo/driver.py:939(F7_TIME_LIMIT_SECONDS = 300) | 錄製模式 60 秒放寬是 Phase13 舊機制,現況已隨 Phase14 增量3 刪除,可由常數核對 |
| 7 | CONTEXT | high | — | 逐字取自決策 d2 的 why_chosen(計劃規定與「預期不偏袒任一方」的判斷),是流程規則與意圖陳述,不是程式現況 |
| 8 | CODE | high | src/rtb/analyzer/instrumented.py:85-122(僅剩 rule_source) | 現行 instrumented.py 只剩 rule_source(正式規則路徑用),AI 調查用的來源函式已刪除,與句子所述相反 |
| 9 | CODE | high | src/rtb/eval/generator.py:18-20;src/rtb/domain/worth.py:33-38 | 5 格 × 20 組 × 3 變體均為程式常數,逐一核對相符 |
| 10 | CODE | high | src/rtb/stepbudget.py:22-25(MODEL_TIMEOUT_SECONDS=15.0、GROUP_EXIT_WAIT_SECONDS=5.0、SETTLE_ATTEMPTS=3) | 三個數字都是具名常數,逐一核對相符 |
| 11 | CODE | high | src/rtb/analyzer/policy.py:156;src/rtb/domain/nine_rules.py:408-419 | 「只看曝光、點擊正數」是舊行為描述;現行 code_rule 呼叫九條規則,還檢查轉換與營收,敘述現已不成立 |
| 12 | CODE | high | src/rtb/analyzer/runner.py:126,132 | 現況(Phase12 起)分析端驅動程式已建置並傳入 operation_lookup,與句子所述「還沒有啟動程式」相反 |
| 13 | CODE | high | src/rtb/analyzer/policy.py:156;src/rtb/domain/nine_rules.py:423 | 該 Issue 標記 resolved,現行決策改用九條規則而非只看 1 小時曝光點擊 |
| 14 | CONTEXT | high | — | 逐字取自決策 d6 的 why_chosen(選 pytest 的理由),屬工具選型設計取捨,非程式現況 |
| 15 | CODE | high | src/rtb/analyzer/flow.py:428-434(`_BLOCK_CODES` 現有 7 種) | 筆記正文自註「寫下時是五種」,現況已是 7 種,可由程式碼常數核對 |
| 16 | CONTEXT | high | — | 逐字取自決策 d2 的 why_chosen(為何選獨立行程模擬 DSP 的理由),屬設計取捨敘述 |
| 17 | CODE | high | src/rtb/httpkit.py:29,117-118,252-254 | 僅接受綁定 127.0.0.1,且僅 HTTP/1.0 缺 Host 時放行,逐項核對相符 |
| 18 | CODE | high | src/rtb/executor/runner.py:39(EXIT_UNSAFE_DB=5),:176-177(st_nlink>1 拒絕啟動) | 硬連結檢查與退出碼 5 逐字可查,與現況相符 |
| 19 | CODE | high | src/rtb/analyzer/runner.py:1-3;src/rtb/analyzer/instrumented.py:91 | 「尚未接入」可由程式碼是否有正式入口與跨窗核對邏輯查證;現況已有正式入口且跨窗核對已接上,與句子矛盾(可能是舊筆記) |
| 20 | CONTEXT | high | — | 「規則沒有因為看過答案而改」是因果聲明,「換批只為了讓情境不自相矛盾」是決策動機,程式碼讀不出來 |
| 21 | CODE | high | src/rtb/ops/metrics.py:74(MAX_WINDOW=24h),:84-85(EXIT_WINDOW_TOO_LONG=4,EXIT_UNSTABLE=5) | 窗長上限與兩個結束代碼都是常數,逐字相符 |
| 22 | MIXED | med | src/rtb/executor/execution.py:574(self.dsp.write 正式路徑無條件寫入);src/rtb/analyzer/dsp_client.py 全檔只有讀函式 | analyzer 端 DSP 用戶端確實只讀(支持句子),但 executor 端的正式路徑本來就會寫入 DSP;句子範圍界定不明,若指全系統則與程式碼矛盾 |
| 23 | CODE | high | src/rtb/analyzer/policy.py:337-343(revision=1 寫死,註解自稱示範規則) | 修訂序號寫死為 1 且註解明講,逐字可查 |
| 24 | CODE | high | src/rtb/domain/nine_rules.py:290-293(after_window_complete) | 函式與註解逐字對應句子所述 D+4 日 00:00 UTC 門檻 |
| 25 | MIXED | med | 全庫找不到任何 agent/evidence-gate 模組(grep 0 筆) | 「尚未實作」可由程式碼缺席驗證(CODE);「固定蒐集兩份證據就決策」是尚未寫代碼的設計方案,屬計劃/意圖(CONTEXT) |
| 26 | CODE | med | src/rtb/analyzer/flow.py:15-17;反例 src/rtb/analyzer/runner.py(正式入口已存在) | 「操作查詢」參數行為可查程式碼;但「分析行程還沒有啟動程式」與現況(已有 runner.py 正式啟動程式)不符,疑似描述較早期狀態 |
| 27 | CONTEXT | high | (現碼已無此機制:task_store.py 移除 renew_lease,flow.py:194 註明已隨 AI 那一步撤除,全庫 grep renew_lease 0 筆) | 句子講的是 Phase13 當時的歷史行為,機制已整支刪除,現在的程式碼答不出這件事怎麼運作過 |
| 28 | CODE | high | src/rtb/modelclient.py:19-20;src/rtb/modelledger.py:221-225 | 花費上限數字(每次展示 1 美元、每月 20 美元)逐字寫在程式與註解裡 |
| 29 | CODE | high | src/rtb/ops/slo.py:42(SCALE=60),:118-120(Burn fast 14.4、slow 6) | 快燒 14.4、慢燒 6、示範縮短 60 倍三個數字都對應常數 |
| 30 | CONTEXT | high | — | 給尚未存在的 Agent 訂的架構設計原則,是規劃意圖不是現狀描述;全庫查無對應 agent 模組可對照 |
| 31 | CODE | high | `grep 'if __name__ == "__main__"' src/rtb` 現況共 18 個檔,而非 9 個 | 命令列入口數量是可直接數的程式碼事實;句子綁定在 Phase11B 歷史階段,以現況程式碼算是 18 支,供對照 |
| 32 | CODE | high | src/rtb/ops/side_effects.py:39(MAX_PAGES=20_000,註解「一頁 50 筆」) | 分頁大小逐字寫在註解裡 |
| 33 | CODE | high | src/rtb/analyzer/task_store.py:144(MAX_GENERATION=3),:828-830(replan_limit_reached=3) | 錯誤字串格式與數字 3 都能直接讀到 |
| 34 | CODE | high | src/rtb/analyzer/task_store.py:125(LEASE_DURATION=timedelta(seconds=60)) | 租約長度常數逐字相符 |
| 35 | CODE | high | src/rtb/dsp/store.py:267-272 | 只判 update_budget/pause_campaign,其餘一律 raise UnknownAction,與敘述相符 |
| 36 | CODE | high | src/rtb/executor/inbox_store.py:65-67(MAX_REVISIONS_PER_TASK=50、MAX_ROWS=5000、RETENTION=2h) | 三數字全對得上 |
| 37 | CODE | med | src/rtb/domain/worth.py:94;反證 src/rtb/analyzer/policy.py:13 | `is_positive(impressions) and is_positive(clicks)` 確實在九格表 cell_of 裡判一格,但 policy.py 明言舊判法已撤掉;敘述把局部條件說成整體規則 |
| 38 | CODE | high | src/rtb/demo/flow.py:52-53,63,141-144 | a_candidate 節點與 a_route→a_candidate 邊仍在,即使正式決策已撤除 AI 參與 |
| 39 | CODE | high | src/rtb/eval/adoption.py:29-32(WORTH_RECALL_BAR=0.80/MIN=16、OTHER_BAR=0.95/MIN=73) | 數字全部對上 |
| 40 | CODE | high | src/rtb/analyzer/runner.py:41(EXIT_UNSAFE_CONFIG=7) | 結束代碼 7 逐字相符 |
| 41 | CODE | high(反證) | src/rtb/executor/capability_signer.py:42-46(Tenant 現有 campaigns、max_budget、aggregate_limit 三欄) | 現況是三欄,不是只有兩欄;此句像是 Phase6 動筆前的起點描述,對現況不成立 |
| 42 | CODE | high | src/rtb/analyzer/runner.py:42-43,163(BACKOFF_CAP_SECONDS=10.0,2**misses 加倍) | 確是加倍且上限 10 秒 |
| 43 | CODE | high(反證) | tests/executor/test_f7_end_to_end.py:18-19(CAMPAIGNS=3000、WORKERS=8) | 工作者數對,但件數是 3000 不是 300 |
| 44 | CODE | med | src/rtb/domain/worth.py:94;反證 src/rtb/analyzer/policy.py:13 | 同 37,該行判準只是九格表其中一格的條件,不是整個「值不值得加」判斷現在唯一依據 |
| 45 | CODE | high(反證) | src/rtb/analyzer/runner.py:82-102(_unsafe/_unsafe_rule_steps) | 啟動時會斷言租約不等式,不符就拒絕啟動,是機械守衛,並非「沒有」 |
| 46 | CODE | high | src/rtb/analyzer/task_store.py:24-28;src/rtb/eval/investigation_eval.py:10-14 | 評估執行器確實逐筆呼叫正式路徑同一支 AI 決策函式;但 renew_lease 已被拿掉,現行程式不存在「續租回呼」可談成功與否 |
| 47 | CODE | high | src/rtb/domain/worth.py:1;src/rtb/analyzer/policy.py:188-196 | route() 用 or 短路,正式路徑(candidate=None)不會呼叫 cell_of,對外決策結果確實不受評分格影響 |
| 48 | CODE | high | src/rtb/executor/runner.py:42-43(EXIT_BUSY=6、BUSY_LIMIT=3) | 連續忙碌次數與結束代碼相符 |
| 49 | CODE | high | src/rtb/executor/guardrails.py:19(DECISION_FRESHNESS=timedelta(minutes=15)) | 超過就判 decision_stale,相符 |
| 50 | CODE | high | src/rtb/analyzer/task_store.py:121,743(MAX_ERROR_DETAIL_LENGTH=2000) | 寫入時截斷,相符 |
| 51 | CODE | high | src/rtb/capabilitykit.py:34,55(MIN_KEY_BYTES=32,is_usable_key) | 短於 32 位元組視為不可用金鑰,相符 |
| 52 | CODE | high | src/rtb/analyzer/flow.py:322,343,349,370,404 | 現有 5 個轉 FAILED 的觸發點,不是只有 Decide 一處 |
| 53 | CODE | high | src/rtb/eval/rule_mining_prompt.py:9-11,191-210;src/rtb/eval/rule_mining_baseline.py:138 | 預檢只在建版時跑、只看位元組閘與分母可達性,無前版比對機制 |
| 54 | CONTEXT | high | — | 整句是計劃筆記決策 d1 的 why_chosen 欄位,屬人的決策記錄,程式碼答不了 |
| 55 | CODE | high | tests/analyzer/test_boundaries.py:20-27;src/rtb/executor/capability_signer.py:1-10 | 機械擋 analyzer 匯入 rtb.dsp/rtb.executor,簽發金鑰只在 executor,分析端拿不到,確為可測事實 |
| 56 | CODE | high | src/rtb/analyzer/policy.py:74-78,107-112 | WorthCandidate 協定只帶 judge 與 timeout_seconds,相符 |
| 57 | CODE | high | src/rtb/demo/driver.py:1497-1499;tools/verify_claims.py:53 | VERIFIER_TIMEOUT_SECONDS=960.0(外層),TIMEOUT_SECONDS=900(驗證器自身),相符 |
| 58 | CODE | high | src/rtb/analyzer/runner.py:14-16 | Phase14 增量3 已將 --ai-judge、--hold-submit 整段撤除,固定走規則輪,此句描述的是已撤除的 Phase13 舊行為 |
| 59 | CONTEXT | high | — | 決策 why_chosen 逐字比對,屬設計取捨/決策理由,非程式可證 |
| 60 | CODE | high | src/rtb/analyzer/runner.py:1,5-12,83-101 | runner.py 自稱正式入口且有機械守衛(租約不等式檢查),與句子所述相反(此為 Phase11B 舊況) |
| 61 | CODE | high | src/rtb/domain/evidence.py:23;src/rtb/domain/_checks.py:15 | MAX_UNTRUSTED_TEXT_LENGTH=512、MAX_ID_LENGTH=128,相符 |
| 62 | CODE | high | claims/prompt-injection.json:3(policy 欄位已無「未開 AI 決策時」字樣,已改為全域) | 可直接讀檔確認/反駁 |
| 63 | CODE | high | src/rtb/domain/_checks.py:32-34;src/rtb/domain/nine_rules.py:92-95(is_fixed_amount) | 只認固定兩位小數字串,相符 |
| 64 | CODE | high | src/rtb/executor/inbox_store.py:69(MAX_EVENTS_PER_CODE=200) | 相符 |
| 65 | CODE | high | src/rtb/analyzer/runner.py:14-16 | docstring 明寫 Phase14 增量3 已撤除相關參數,固定用規則輪 |
| 66 | CODE | high | src/rtb/executor/attempt_store.py:51-54(MAX_SENDS=3、MAX_VERIFICATION_TIMEOUTS=5、MAX_ROWS_PER_KEY=50、MAX_UNRESOLVED=20) | 逐一對應相符 |
| 67 | CODE | high | src/rtb/demo/driver.py:148,280 | docstring 與常數註記「永遠只用九條規則」,相符 |
| 68 | MIXED | med | src/rtb/executor/attempt_store.py:763-795(溢位時退回 aggregate_used_reference 的退路機制實際存在) | CODE 部分:退路機制確有實作;CONTEXT 部分:「原本擔心」的心境與「另存合計方案否決」屬決策記錄 why_chosen,程式碼看不出被否決的替代方案 |

## 統計
- CODE: 54
- CONTEXT: 9（編號 3, 7, 14, 16, 20, 27, 30, 54, 59）
- MIXED: 5（編號 2, 4, 22, 25, 68）
- 合計：68
