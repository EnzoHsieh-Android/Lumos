### ext-f1 / major

引句:「_repo_root_from_env 有 standalone 回退恆非 None。」

佐證:file: `scripts/lumos:5360`

佐證:file: `scripts/lumos:8273`

說明：`_repo_root_from_env()` 在非 `docs/<slug>-knowledge` 佈局時回傳 `env.vault.parent`，但 repo 既有定義明確指出 standalone vault 的 repo root 是 `env.vault` 自身。因此 standalone repo 的 `.lumos/lint.json` 會被錯誤地查到父目錄；真正宣告即使損壞，doctor [F] 仍會輸出「未宣告跳過」並可能以 rc0 假綠。新增測試只覆蓋 Landmark 的 `docs/` 佈局，沒有覆蓋註解聲稱已支援的 standalone 分支。

### ext-f2 / major

引句:「except (OSError, json.JSONDecodeError) as e:」

佐證:file: `scripts/lumos:10983`

佐證:file: `scripts/lumos:1479`

說明：共用讀取函式以 UTF-8 開檔，卻沒有捕捉 `UnicodeDecodeError`。只要 `.lumos/lint.json` 含非法 UTF-8，doctor [F] 和 `lint-check` 都會直接 traceback，而不是把壞宣告轉成受控 finding／rc1 或 rc2。這違反本次「宣告壞掉要被 doctor 靜態驗出」的 fail-closed 目的，也會讓 CI 巡檢非預期中止。新增測試只測語法錯誤的 Unicode 文字 JSON，未測檔案編碼損壞。

### 試過但乾淨的攻擊面

- mutate CLI、dispatch 與 help 的退場完整性
- calibration／SNR 腳本及對應測試引用清除
- doctor [F] 對合法 JSON、schema 錯誤、無宣告三條路徑
- disposal roster 尾端不改 PASS／FAIL rc
- `only_rid` 是否誤掃其他輪次
- `__seqN` round-less 跳過與顯式 `--roster` 去重
- roster 異常留痕寫入失敗時是否吞掉原始警告
- vendored consumer 的來源檔精確 skip 守衛替換
