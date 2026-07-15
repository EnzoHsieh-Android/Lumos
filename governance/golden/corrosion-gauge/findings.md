# corrosion-gauge design-loop 逐輪存活 findings(辯方裁決後)

零判斷純搬運自 /tmp/auto-loop-2026-07-14/.canary-log.jsonl 與 spec 審計修正紀錄(2026-07-14,K=3 high 級,7 輪收斂,r4 missed 不折)。

## r1(caught,minor,折 5)
- F2′ 措辭:build_message 綁死 spec-readiness banner、corrosion 走 send()+自建 dict(F2 major 遭辯方駁倒降 minor:spec 未混淆兩路徑;banner 為 wrapper 6 呼叫點已容忍的既有屬性)
- F3:SCOPE 排除 scripts/test_*.py(unittest fixture 灌噪 dup_ratio)
- F4:HEAD 去重假等價(髒工作樹)→ scope_hash 內容指紋
- F5:dead_defs 引用判準釘死(ast.walk 全 FunctionDef+詞邊界 regex 排 def 行;短名互撞=漏報方向)
- F6:ledger append 加 fcntl.flock

## r2(caught,minor,折 7)
- F2:dup_ratio 重複視窗數釘死 Σ(count−1)
- F3:整數指標噪音地板恆不 binding=空條款,刪(地板只留 dup_ratio 0.3pt)
- F4:flock 臨界區擴到「讀尾行比對+append」整段
- F5:遞迴自引/互引死函數=另一類結構性漏報,補天花板
- F6:hooks 無副檔名檔 shebang 分類
- F7:誠實天花板編號重排 1–8
- ⚠:ast.parse SyntaxWarning 靜音(免灌 cron log)

## r3(caught,minor,折 2)
- F1′:SCOPE 明寫「非遞迴、僅檔案」+ scripts/hooks/claude/*.py v1 取捨明示(F1 major 遭辯方駁倒:IsADirectoryError/.pyc 鏈繫於審計員自造的遞迴前提)
- F4:「只量 loop 自我修改面」過宣稱 → rationale 據實(governance_flex_builder 等一併入帳)

## r4(missed,不折)
- 7 條 minor 全繞開植入壞 §ref,判決不採信;SCOPE 漂移/除零/ledger commit 於 r5 獨立重發現收回。

## r5(caught,minor,折 4)
- F1′:SCOPE 邊界=覆蓋面漂移,天花板 1 具名+trend bullet 邊界段+v2 reset(F1 major 遭辯方駁倒:單一邊界無法獨力偽造 k=4 單調)
- F3:dup_ratio 0 視窗除零守衛(釘 0)
- F4:ledger commit 動線據實記明(cron 只寫、人 commit)
- F5:k=4 語意釘死=窗 4 列(3 遞增比較)

## r6(caught,minor,折 3)
- F2:parse_errors 歸體積類(不觸發 trend)
- F3:detail 檔釘定(governance/corrosion-detail.json、每次 snapshot 覆寫)
- F4:scope_hash 檔清單排序後 hash(堵 glob 序抖動)

## r7(caught,clean,折 0)
- 排除 canary 後零真 finding;auditor 明言機制主體收斂。

## 跨家族複核
- qwen:status=ok、worst=minor、parse_fallback=false → endorsed(唯 verdict 行 5 tokens 零論證,訊號弱,誠實記明——同 risk-tiered-review 收斂案的 cross_audit 已知調校點)
