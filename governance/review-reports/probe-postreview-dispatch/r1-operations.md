severity: major

S8：逾時留下的「看似完整」結果檔沒有被隔離，下一次續跑可能把事故資料當成有效樣本。  
severity: major  
blocking: 是  
引句:「整批應停止下一題、留下失效 summary 並退出 3；不能讓例外略過批次收尾。」  
evidence file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:97`  
evidence file: `docs/lumos-toolchain-knowledge/Issues/探針批次停止後的剩餘工作與落檔邊界.md:24`  
evidence file: `governance/eval/ablation_lumos_first.py:77`  
evidence file: `governance/eval/ablation_lumos_first.py:95`  
evidence file: `governance/eval/ablation_lumos_first.py:166`  
evidence file: `governance/eval/ablation_lumos_first.py:177`  
最小翻紅重現：讓 `subprocess.run` stub 先依 `--out` 寫入一份 `fatal=false`、`inconclusive=false`、`skills_health_bad=[]` 且含一筆 `reason=ok` 的合法 JSON，再拋 `TimeoutExpired`；第一次應回 3。接著以同一 `out_dir` 重跑，斷言該題仍須補跑。照目前設計僅把 summary 標失效，逐題檔本身沒有事故標記；`collect_skills_health` 會接受它，`load_results`／`needed` 會把它計入，導致不再補跑。S8 應要求啟動例外或逾時時刪除、隔離或原子改寫本次輸出為 `fatal=true`，並增加「事故後續跑仍補該題」的驗收。

S8：失效摘要與日誌未規定保留足以處置的診斷資料。  
severity: minor  
blocking: 否  
引句:「整批應停止下一題、留下失效 summary 並退出 3」  
evidence file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:97`  
evidence file: `governance/eval/ablation_lumos_first.py:174`  
evidence file: `governance/eval/ablation_lumos_first.py:351`  
目前 log 在呼叫前只寫命令；例外發生後，既有 summary 合成路徑只會留下泛稱「探針程序失效且沒有可採信的結果檔」。照 spec 字面實作可以滿足 rc3 與失效旗標，卻丟掉例外型別、訊息、arm、qid、log 路徑及重試處置，維運者無法分辨缺執行檔、權限問題或未來的 timeout。S8 應明訂這些最小診斷欄位，並驗證秘密或完整命令參數不被抄進 summary。

S9／回退：多路拒絕的適用範圍與舊 CLI 遷移沒有定義，可能誤擋純合併恢復流程。  
severity: minor  
blocking: 否  
引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路。」  
evidence file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:98`  
evidence file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:100`  
evidence file: `governance/eval/ablation_lumos_first.py:15`  
evidence file: `governance/eval/ablation_lumos_first.py:299`  
evidence file: `governance/eval/ablation_lumos_first.py:326`  
既有 usage 與預設值都是 workers=2，而 `--merge-only` 根本不派模型。若實作者在 parse 後全域拒絕 workers>1，既有 `--merge-only --workers 2` 恢復命令也會無必要地退出；若回退時把「舊 CLI 顯示」理解成恢復預設2，又會讓預設命令撞上新拒絕。應明訂拒絕只套用 `not merge_only` 的 live dispatch，更新 usage/help，並把回退範圍寫成可恢復文案但預設仍為1，直到可取消 runner 通過。

PRIOR-ART：已讀，選擇序列派工避開 running future 無法取消的限制，無 finding。

吞吐取捨：已讀，安全恢復多路的事件入口與競速驗證條件具體；除上述 CLI 遷移缺口外，無 finding。

watchdog 界線：已讀，已誠實聲明目前沒有 outer timeout，setup/cleanup 卡住另走外層 watchdog，無 finding。

S9 停派語意：已讀，條款要求事故後後續工作不得進入 `run_job`，且測試名稱已綁定，無額外 finding。

回退的資料安全底線：已讀，保留失效摘要與紅燈反例、禁止未驗證即重開並行，無額外 finding。

總結最嚴重 severity: major；blocking 條數: 1
