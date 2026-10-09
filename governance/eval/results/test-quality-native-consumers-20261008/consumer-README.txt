# Lumos 測試品質實驗專案

這裡是兩個獨立消費專案，實際使用各自安裝的 `scripts/lumos test-quality`。用途是驗證測試是否真的會抓錯，以及收證工具會否把無效執行算成成功。

## 重跑

```sh
cd /Users/enzo/lumos-test-quality-lab-20261008
python3 run_experiment.py node
python3 run_experiment.py laravel
# 有本機 Semgrep 時加 --semgrep /absolute/path/to/semgrep
```

每次新建 artifacts/run-*，不覆寫歷史證據。runner 只改本案例的 Pricing 實作，finally 還原；請逐次執行，不要同一專案同時跑兩次。明示執行可信本機程式，沒有沙盒。Python runner 使用標準庫。

Node 使用 node:test（本次 Node v24.16.0），無 npm 依賴。Laravel 使用官方 Laravel12 skeleton、composer.lock 鎖住依賴（本次框架12.69.3、PHPUnit11.5.57、PHP8.5.10）；搬到其他機器請先 composer install 與 composer check-platform-reqs。Laravel12 是本次明確固定的驗證版本，非最新版宣告。

## 做了哪些驗證

| 情境 | Node | Laravel |
|---|---|---|
| 正常實作 | 3 個獨立需求案例通過 | 3 個 Unit + 2 個 Feature 通過 |
| 故意回傳0 | 2 個金額案例失敗 | 2 個金額 + 1 個 HTTP 案例失敗 |
| 還原原始實作 | 全綠且來源快照相同 | 全綠且來源快照相同 |
| 等價重構 | 案例全綠 | 案例全綠 |
| 篩選不存在的測試 | 收證拒絕，即使原生runner退出0 | 零案例收證拒絕 |
| 故意自己比自己 | 選配 Semgrep 列出候選 | 選配 Semgrep 列出候選 |

Laravel Feature 真正啟動框架、送 POST /quotes、驗 JSON、持久化並查詢記憶體 SQLite；另驗負數回422、沒有資料副作用。前置斷言確認 testing、sqlite、:memory:。不接正式資料庫、真郵件或外部服務。

## 證據與界線

本次結果：[Node](node/artifacts/run-yk2hztlm/check.json)、[Laravel](laravel/artifacts/run-5eb89al1/check.json)。各資料夾有原生 XML、stdout/stderr、來源／測試／設定快照、hash、receipt、零選中負例。

故障被抓到不等於測試有獨立答案。「重抄演算法」反例可能也會抓到這次故障，靜態掃描目前不會完整抓出跨語言同源算法。因此 check 明示 verdict=not_assessed，需求來源只記 declared；仍由審查者對照 REQUIREMENTS.md、預期值來源與公共介面。保持行為的重構只在本需求域（非負且100的整數倍）說明等價，本次案例全綠不證明所有輸入。

這個實驗接的是 test-quality capture/check；Node 的原生 runner 並未冒充 node-jest 的 bound-tests/guard profile。Pest、Jest、Vitest、Laravel13、Dusk、外部服務、正式DB與其他語言框架均不由本次實驗推論已驗。

設計參照：[Laravel12 Testing](https://laravel.com/docs/12.x/testing)。
