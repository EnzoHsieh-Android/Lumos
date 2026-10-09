# r1 intake

preflight-4: ran

開輪依據：推送前規格閘判本計劃的低風險放行不成立（全靠人驗、改動超過小改動範圍）；事後補綁測試又違反「keeps 只給計劃前已存在的測試、新行為須現在紅」，故作者自標 plan_risk: high 走設計審。實作已在本分支完成並經代碼審，本輪審的是計劃文字與實作是否相符。

## 前掃（便宜代理，四類）

- ① 未定義的詞 3 條，直接修真檔：sidecar 補定義為三支測試品質輔助檔；`_vendored_digest` 補說明為換行統一成 LF 再算 SHA-256 的既有工具檔指紋函式；「有界 bytes」改為「每支先讀最多 10 MiB 的 bytes」（核對 scripts/lumos 的 _test_quality_bundle_sources 讀 10 MiB+1 並比對指紋）。
- ② 壞引用：無。
- ③ 範圍矛盾 1 條：RETIRE-IF 寫「撤除入口專用配套指紋」與 S1–S3 驗指紋並存。判讀：RETIRE-IF 是未來撤除條件、不是現況，不矛盾，不改。
- ④ 機械宣稱驗語意：S1、S3 前掃判成立。S2 前掃判「無法判」，編排者核對：_test_quality_load_bundle 以 exec(compile(已驗指紋的 raw bytes)) 載入，不經磁碟上的舊 .pyc，故「執行已驗 bytes 的判讀」成立；另有 test_source_bytes_not_stale_bytecode_authorize_capture 控制。前→後：計劃文字不變。

## 收貨

四席收齊後才一次寫入卷證；quote-check 四份全數錨定。GEN-1、BND-1、HND-1 三席獨立指出同一根因（Semgrep 轉接器載入時從磁碟另載共用 runner），編排者以同時間戳同大小舊 pyc 重現：指紋檢查回報合格，轉接器綁到的 CaptureTimeout 訊息為舊版、與已驗模組不是同一物件。多席一致且有可執行證據，直接折、不派辯方。

## 重現與處置

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| GEN-1 | 通才 | major | HIT | folded | 程式改依賴順序載入加載入後引用核對；test_semgrep_adapter_uses_verified_runner_not_stale_bytecode 修前紅在 ZeroDivisionError、修後綠；只留守衛改回舊順序時回部署不完整 |
| BND-1 | 邊界 | major | HIT | folded | 同 GEN-1 |
| HND-1 | 接手 | major | HIT | folded | 同 GEN-1；S2 人工驗收改列 capture 與 scan --semgrep 兩條控制 |
| ARC-1 | 架構對齊 | major | HIT | folded | 計劃補寫為何另立指紋表、與 vendored.json 的分工 |
| ARC-2 | 架構對齊 | minor | HIT | folded | PRIOR-ART 補寫與 _handoff_load_hook 的差別 |
| ARC-3 | 架構對齊 | minor | HIT | folded | 計劃補寫三支在 main 開頭一起載入的理由 |
| ARC-4 | 架構對齊 | minor | HIT | folded | 移除走不到的純文字 ModuleNotFoundError 分支 |
| ARC-5 | 架構對齊 | minor | HIT | folded | lands_in 補 Systems/lumos-cli-lifecycle |
| GEN-2 | 通才 | minor | HIT | folded | 佔位入口收 -h，test_incomplete_bundle_short_help_is_structured 修前紅修後綠；子指令前放其他選項寫明不在保證內 |
| GEN-3 | 通才 | minor | HIT | folded | 計劃寫明報告內來源指紋是執行期重讀磁碟的原始 SHA，不等於配套校驗結果 |
| BND-2 | 邊界 | minor | HIT | folded | 只收一般檔、例外改全接；test_fifo_sidecar_does_not_hang_other_commands 修前 10 秒逾時、修後綠 |
| BND-3 | 邊界 | minor | HIT | folded | 同 GEN-3 |
| BND-4 | 邊界 | minor | HIT | folded | 實務隱患補併發（更新期間暫時拒絕屬預期）、效能、資源 |
| HND-2 | 接手 | minor | HIT | folded | 計劃列出改或新增 sidecar 要同步的五處與檔名前綴要求 |
| HND-3 | 接手 | minor | HIT | folded | 例外全接、死分支移除；test_sidecar_runtime_error_only_blocks_test_quality 修前 --version 崩潰、修後綠 |
| HND-4 | 接手 | minor | HIT | folded | RETIRE-IF 改成可觀測條件並帶 [retire:人裁][until:2027-04-09] |
| HND-5 | 接手 | minor | HIT | folded | S1–S3 人工驗收改列可照做的指令與控制名 |
| HND-6 | 接手 | minor | HIT | folded | 同 ARC-1 |
