severity: major

## Finding R2-ARCH-1：部署檢查另行解析全域 argv，漏掉合法的 `--vault`

severity: major  
blocking: 是  
引句:「if argv[:1] != ["test-quality"]:」

新增的部署檢查只看第一個參數，形成第二套命令辨識機制；正式 argparse 則允許 `--vault <path> test-quality ...`。因此同一個 `test-quality` 命令會因全域選項位置不同，走出不同錯誤通道。

file: `scripts/lumos:49220`  
file: `scripts/lumos:49324`  
file: `scripts/lumos:50237`  
file: `scripts/lumos:50261`

具體觸發：部署缺少三個 sidecar 時，直接呼叫可得到 structured JSON；加上受支援的頂層 `--vault` 後，preflight 被跳過，最後由 argparse 吐 stderr，stdout 為空。

最小翻紅驗證：

```sh
python3.14 lumos test-quality scan sample.py --json
python3.14 lumos --vault "$PWD/vault" test-quality scan sample.py --json
```

第一個命令目前回傳可解析的 `complete:false` JSON；第二個命令 stdout 為空，stderr 為：

```text
擋下:不認得這幾個參數:scan sample.py --json。
```

最小測試應斷言兩種合法頂層排列都產生可解析的 structured deployment error；目前第二式在 JSON 解析處翻紅。

歸因：有證據的原有漏查。相同 `--vault` 案例在 base commit 也已失敗；R2 修補直接形式時沒有覆蓋正式全域語法。

## Finding R2-ARCH-2：handbook 程序清理的守門測試放在 CLI 測試套件

severity: major  
blocking: 是  
引句:「path = TOOL.parent.parent / "governance/eval/test_quality_handbook.py"」

`test_model_timeout_stops_worker_without_paid_call` 直接改寫並執行 handbook 模組，但被放進 `scripts/test_test_quality_cli.py`。既有圖譜把 handbook 實作及其獨立控制歸給 `governance/eval/test_test_quality_handbook.py`；照該系統既有測試入口驗證時，這項回歸不會被執行。

file: `scripts/test_test_quality_cli.py:477`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:35`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:37`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:38`

具體觸發：維護者修改 `governance/eval/test_quality_handbook.py`，把 `model_command(...)` 改回舊的 `subprocess.run(..., timeout=...)`，然後只跑 handbook 所屬測試套件。

最小翻紅驗證已在 `/tmp/lumos-seat-work/r2-architecture` 的臨時 checkout 完成：

```sh
python3.14 -m unittest discover \
  -s governance/eval \
  -p 'test_test_quality_handbook.py' -v
```

模擬回歸後上述 15 項仍全綠；再執行：

```sh
python3.14 scripts/test_test_quality_cli.py \
  QualityCLI.test_model_timeout_stops_worker_without_paid_call -v
```

才會因 worker 仍存活而翻紅。臨時 checkout 已還原且工作樹乾淨。

歸因：有證據的修復回歸。程序清理由 R2 修好，但新增的守門測試跨越既有測試所有權，令正式 handbook 測試入口漏驗。

## 修補因果覆核

1. **原問題是否修好**：JUnit 數量核對、直接形式的部署完整性檢查、deinit bytecode 清理、capture 取消、模型程序群清理、輸出上限、impact 分類及 scanner 共用參數，在凍結碼及目前測試中均有正向證據。部署完整性只屬部分修好，合法的 `--vault ... test-quality` 形式仍漏掉。
2. **既有行為是否保持**：凍結碼下 `scripts/test_test_quality_cli.py` 33 項、`scripts/test_test_quality_scan.py` 21 項、handbook 15 項及 historical controls 均通過。指定材料沒有完整的 base/head 逐案例原始輸出，因此只能確認這些控制保持，不能獨立證明全部既有行為。
3. **新問題歸因**：
   - Finding 1：原有漏查，R2 修補未覆蓋。
   - Finding 2：修補新增測試的放置造成。
   - 其餘行為是否完全保持：材料不足，未判定。

## 架構三問

1. **分層與依賴方向**：不完全對齊。Finding 2 由 CLI 測試反向承擔 handbook 模組的守門責任。scanner 參數由 `test_quality_scan.add_scan_arguments` 共用、CLI 傳入同一 namespace，這部分已讀,無 finding。
2. **命名、錯誤處理與介面**：不完全對齊。Finding 1 令同一命令在直接形式回 structured JSON，在帶合法全域選項時改由 argparse stderr 報錯。其餘新 helper 的責任與命名已讀,無 finding。
3. **第二套機制**：存在。Finding 1 的 `argv[:1]` 是正式 argparse 之外的第二套命令辨識。`_IMPACT_RECORD_DIRS` 對既有 bookkeeping 分類作窄幅延伸，已讀,無 finding。

## 固定鏡頭前 8 篇合約

1. `Issues/vendored測試套件在消費端假紅.md`：鏡頭未列合約；已讀,無 finding。
2. `Systems/lumos-cli-lifecycle.md`：reinject 只替換 sentinel body、外部 byte-equal；本次未改 reinject 路徑，已讀,無 finding。
3. `Systems/lumos-deinit.md`：鏡頭未列 invariant；新增 bytecode 清理從 `_VENDORED_TOOLKIT` 推導，並保留 symlink 與使用者 cache，已讀,無 finding。
4. `Systems/lumos-cli-read.md`：search 排除 superseded、不得排除 stale；本次未改 search 路徑，已讀,無 finding。
5. `Systems/bound-tests-gate.md`：綁定測試必執行，失敗、懸空等情況阻擋；本次未改 gate，已讀,無 finding。
6. `Systems/guard-kill.md`：
   - rc 優先序：本次未改 guard-kill，已讀,無 finding。
   - JSON stdout 純淨：本次未改 guard-kill，已讀,無 finding。
7. `Systems/授權與歸屬.md`：
   - license 檔不得進 vendored whitelist：`_VENDORED_TOOLKIT` 未包含 license 類檔案，已讀,無 finding。
   - vendored 檔保留授權標頭：相關 CLI 與 sidecar 仍有 SPDX／MIT 標頭，已讀,無 finding。
8. `Systems/測試假綠形態.md`：修 bug 的紅測試須證明已進入目標路徑；新增 worker/capture 測試先等待 pidfile 或 worker 啟動再觸發停止，已讀,無 finding。

## 剩餘鏡頭名稱

- `Systems/pitfalls-code-loop.md`
- `Systems/design-loop.md`
- `Systems/reversibility-governance-ledger.md`
- `Systems/loop-convergence-recording.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/lumos-refcheck.md`
- `Systems/check-t-sentinel.md`
- `Systems/check-r-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/cochange-guard.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/引用座標依實際換行_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Projects/異常派工單回報輸入錯誤_計劃.md`
- `Systems/judge-severity-gate.md`
- `Systems/core-invariant-baseline.md`

## 材料邊界

`r2-repair.patch` 與四份 split patch 的 stable patch-id 相同，指定修補內容一致。實際 base-to-head 範圍另有 59 個未列入 R2 patch 的路徑，多為 R1 卷證與治理紀錄；`r2-repair-binding.json` 未列這些排除項、tree hash、歸因限制或各案例的 base/head 原始輸出。因此完整範圍歸因及全行為保持不可得。

AGENTS 指定的「代碼審修復穩定性試行」計劃與 2026-10-04 驗證檔，在凍結 tree 及指定位置均不可得。

## 未實作提案的架構建議

sidecar digest 綁定宜沿用 `_vendored_digest` 的 LF-normalized 規則，並由同一個 bundle 來源產生 CLI 內嵌 digest；校驗後應保存同一批已驗證 bytes，再從這些 bytes `compile/exec`，避免校驗與載入之間重新讀檔及 stale `.pyc`。

命令辨識應由既有 argparse 結果 `args.cmd` 決定。可在 parser 建立期保存 `deployment_error` 並註冊不 import 的 placeholder，parse 完後只對 `args.cmd == "test-quality"` 校驗及載入；如此自然涵蓋 `--vault`，也不會再建立一套 global argv 解析。預載任一模組失敗時需回滾該次放入 `sys.modules` 的項目，mixed scanner 的 fallback 應只處理已辨識的 bundle 不相容錯誤。

總結：最嚴重 severity: major；blocking: 2 條。
