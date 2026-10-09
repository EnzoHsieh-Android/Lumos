severity: major

已完整讀取：

- `governance/review-reports/read-result-evidence/r1-snapshot.md`
- `scripts/scenario_probe.py`
- `docs/lumos-toolchain-knowledge/Systems/codex-harness.md`
- `docs/lumos-toolchain-knowledge/Issues/探針讀碼證據不足.md`
- `governance/scenarios/paraphrase.jsonl` 的 v04 題目
- `scripts/test_lumos.py` 中所有直接涵蓋 scenario probe 解析、runner、分母、舊 v04 重評及 CLI 摘要的相關測試

逐節結論：

- 前言／PRIOR-ART／RETIRE-IF：方向合理。
- 根因、改變與保持：有一項會污染被測環境的重大問題。
- 驗收條款：缺少「還原失敗必須穿透 main 並中止整批」的驗收。
- 實驗證據與限制：對舊資料的版本隔離不完整。
- 實務隱患：金流、外送及不可逆排除合理，但漏列量測註解觸發既有 hook。
- 回退：方向合理；須先補以下兩項 blocking 設計。

severity: major  
blocking: 是  
引句:「在已建立的隔離副本，對該行加Python行尾註解，含每次嘗試新產生的隨機標記。」

注入發生在沙盒快照提交之後，會讓 `scripts/lumos` 成為未提交的程式碼改動。探針刻意保留真實 hooks；Claude runner 沒關 Stop block，Codex runner 預設也開著。只要模型做過一次 Read、Grep 或 Bash，收工 hook 就會看到「程式碼已改、圖譜沒改」，阻擋並追加一輪提示。這會改變答案、工具序列、回合數與截斷率，量到的是儀器自己製造的髒工作樹，不是原本 v04 行為。S1–S4 沒要求證明 runner 啟動及結束時治理 hook 看見乾淨工作樹。

外部佐證 file: `scripts/scenario_probe.py:13`  
外部佐證 file: `scripts/scenario_probe.py:356`  
外部佐證 file: `scripts/scenario_probe.py:423`  
外部佐證 file: `scripts/hooks/claude/check-graph-sync.py:1017`  
外部佐證 file: `scripts/hooks/claude/check-graph-sync.py:1028`  
外部佐證 file: `scripts/hooks/claude/check-graph-sync.py:1088`  
外部佐證 file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:24`

修正要求：標記必須成為被測 session 看來的乾淨基線，或以不改變 hook 判定的隔離方式注入；並增加測試證明兩個 runner 都不會因標記觸發 Stop block。

severity: major  
blocking: 是  
引句:「還原前重驗路徑安全，失敗列儀器例外並停止整批，避免後續污染。」

現有 `main` 會捕捉 runner 拋出的所有例外，把它轉成單場儀器例外後繼續下一場。若 `finally` 的安全檢查或還原失敗只是拋例外，便會被這層吞掉，違反「停止整批」；後面還會無條件執行 git checkout／clean。S4 只要求 finally 還原，沒有驗收「還原失敗不得被逐題 catch 吞掉」，因此符合目前文字的實作仍可能在污染或路徑異常的沙盒繼續量測。

外部佐證 file: `scripts/scenario_probe.py:703`  
外部佐證 file: `scripts/scenario_probe.py:705`  
外部佐證 file: `scripts/scenario_probe.py:724`  
外部佐證 file: `scripts/test_lumos.py:36774`

修正要求：定義不可被逐題 catch 攔截的致命儀器錯誤，並增加 main 層測試，確認還原失敗後不啟動下一次 runner，也不寫入可被誤認為有效的摘要。

severity: minor  
blocking: 否  
引句:「新GRADER_VERSION應與舊版不同，舊歷史不改寫。」

只替新紀錄寫 `grader` 不足以隔離舊資料。現有週抽入口只用 `seed` 判斷本週是否跑過；同週若已有舊判準紀錄，即使部署新版 grader 也會直接跳過。現存舊歷史列亦沒有 `grader`。結果是新版讀碼證據可能整週沒有被實際執行，日誌卻仍聲稱本週已抽過。

外部佐證 file: `governance/autonomous-loop.sh:367`  
外部佐證 file: `governance/autonomous-loop.sh:369`  
外部佐證 file: `scripts/scenario_probe.py:607`  
外部佐證 file: `governance/scenarios/history.jsonl:1`

修正要求：週抽去重鍵至少包含 `seed + grader`，並明定缺少 grader 的舊列只能歸入 legacy 分區，不能阻止新版執行。

blocking數: 2