### ext-f1
severity: clean
引句:「兩者都是紀錄非碼,補進白名單=pitfalls 不掃 + code-loop 留痕不因它們失效。」
佐證:file: `scripts/lumos:15995`
說明:豁免使用 `all(...)` 檢查留痕 SHA 到目標 SHA 之間的全部變更檔；只要同一 commit 另有任何非白名單 code 檔，就不會進入豁免。測試亦明確提交 `app2.py` 並斷言 rc1，無法靠順帶修改 canary-log 繞過。
結論:否決不成立(code-loop 判斷是「只動白名單檔」，不是「有動白名單檔」)。

### ext-f2
severity: clean
引句:「這些檔是紀錄不是要合入的碼。」
佐證:file: `scripts/lumos:13159`
說明:pitfalls 只在逐檔掃描條件中精確排除兩個固定 JSONL 路徑，沒有以前綴排除整個 docs 目錄；同內容放到一般 code 檔仍會照掃。兩帳是 canary/bypass 事件資料，排除可避免帳內描述 `open(...)` 等字樣反覆誤觸發，未見可執行碼或其他檔案被連帶漏掃。
結論:否決不成立(排除範圍精確且資料帳本不屬於 code-pattern 掃描目標)。

### ext-f3
severity: clean
引句:「advisory fail-open,pre-commit 多等幾秒換掃完整」
佐證:file: `scripts/lumos:12972`
說明:delguard 的最壞等待確實由 5 秒增至 15 秒，因此超時案例的 pre-commit 最多多卡約 10 秒；但這是 diff/vault 掃描的總 deadline，仍有上限、可由 `LUMOS_DELGUARD_DEADLINE` 覆寫，且 patch 已明示此成本。沒有無限等待或硬擋 commit 的新路徑。
結論:否決不成立(延遲增加是有界且明確接受的完整性取捨)。

### ext-f4
severity: clean
引句:「600 撐不過 ~15min CI(2026-08-27),→1800 並順帶治 ci-status 過期」
佐證:file: `scripts/lumos:14074`
說明:持續 in-progress 的 CI 現在可能讓前景 `ci-wait` 阻塞最多 30 分鐘，但它是 push 後手動等待命令，不在 pre-commit/pre-push hook；紅燈、工具失效、全數完成及 no-run 仍會提早返回，且使用者可用 `--timeout` 覆寫。這符合等待約 15 分鐘 CI 完成的目的。
結論:否決不成立(等待上限變長有可預期成本，但未形成不該過級問題)。
