severity: clean

背景鎖清理：已讀，無 finding。`cmd_dispatch_lens` 以單一 `finally` 呼叫 `_lens_release_owned_lock`，原本正常出口的第二個清鎖點已移除；快取命中、錯誤返回與例外均經相同出口。file: `scripts/lumos:33980`、file: `scripts/lumos:34001`、file: `scripts/lumos:34005`

ref 漂移：已讀，無 finding。父程序解析完整 SHA 後以 `warm_range` 傳入，子程序 argv 使用固定範圍；鎖名稱也由實際取得的鎖直接傳入環境。file: `scripts/lumos:33917`、file: `scripts/lumos:33962`、file: `scripts/lumos:34141`

同名替換：已讀，無 finding。現行同版流程在舊鎖存在時不會合法換入同名鎖；本 patch 清鎖只執行一次。測試在第一次刪除後立即換入同名新鎖，確認沒有第二次刪除。人工、舊版或同 UID 外部換檔已明列於計劃界線。file: `scripts/lumos:33992`、file: `scripts/test_lumos.py:54958`、file: `docs/lumos-toolchain-knowledge/Projects/背景快取命中清鎖_計劃.md:26`

錯誤出口：已讀，無 finding。impact、JSON、base-tree 失敗及未預期例外都由外層 `finally` 清理，測試同時核對原返回碼或例外不被改寫。file: `scripts/lumos:34003`、file: `scripts/test_lumos.py:54888`

Windows：已讀，無 finding。`os.getuid` 僅在平台提供時使用，行為與既有私有目錄檢查的跨平台分支一致；POSIX 擁有者及可寫權限拒絕仍有測試。file: `scripts/lumos:33140`、file: `scripts/lumos:33530`、file: `scripts/test_lumos.py:54819`

測試假綠：已讀，無 finding。實跑 `t_lens_warmer_` 得 13 passed、0 failed；缺少 `getuid` 得 2 passed、0 failed；背景實際完成與清鎖得 8 passed、0 failed；殘留鎖邊界得 9 passed、0 failed。`py_compile` 與 `git diff --check` 亦通過。測試命中真正的 wrapper、派工入口和背景整合路徑。

總結：最嚴重 severity: clean；blocking: 0。
