severity: major

## resources-F1
severity: major  
blocking: 是  
引句:「測試只在臨時 Git repo 操作，不寫使用者工作目錄、不外呼。」  
file: `governance/review-reports/source-coordinates/r1-snapshot.md:56`  
file: `scripts/test_lumos.py:69709`

fixture 直接執行 `git init/add/commit`，未隔離全域／系統 Git 設定，也未停用 hooks、簽章或加入 timeout。具體情境：使用者設有 `core.hooksPath`，commit hook 會照常執行，可能寫入臨時目錄外或外呼；設有 `commit.gpgSign=true` 時則可能等待簽章或失敗。結果是四支測試可因使用者環境假紅、永久卡住，且 hook 造成的外部副作用不會被 `TemporaryDirectory` 清理。驗收需明定 fixture 隔離 Git 設定／hooks／簽章並限制子程序時間。

已完整讀取凍結 spec，並依指定鏡頭檢查下列材料：

- `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md`
- `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- `docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`