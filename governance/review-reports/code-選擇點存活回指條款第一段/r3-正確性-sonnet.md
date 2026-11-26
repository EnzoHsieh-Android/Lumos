severity: minor

本輪一句白話:修補本身都落在該落的地方,78 個 choice_cov 測試全綠。我只找到一個修補引入的小洞,和一個快取被誤刪的小洞。

**finding 1**
severity: minor
blocking: 否
`scripts/lumos:29309`(`_KillCovBase.red_rerun`):掛覆蓋逾時就在不掛重跑之前先斷路。測試本身真的會卡住時會誤斷路。
- 輸入:某支守的測試 T 不論掛不掛覆蓋都會跑到單支上限(600 秒)。例如它等網路,或單獨就超過 600 秒。
- 走法:`after` 呼叫 `red_rerun`,此時 `res[3]` 為真、`cap == self.full`,所以第一個提前返回不成立。
- 結果:緊接著 `self.trip("掛覆蓋才紅", ...)` 就把整個平台斷路,之後的測試都不掛覆蓋。
- 之後才跑不掛的重跑,結果同樣逾時,`green` 為假,記成「基準不綠」。「覆蓋設定讓測試卡住」的歸因於是錯的。
- 代價:損失覆蓋加速,所有壞法改跑全部測試。結果仍安全,只是變慢,`reach_why` 也被記成「掛覆蓋才紅」。
- 對照:前一輪的設計是不掛綠才算數。
- 測試缺口:`t_choice_cov_rerun_edges` 第一案只給了「不掛重跑綠」的情況,抓不到這個誤判。
- 建議:斷路挪到不掛重跑確認綠(`green`)之後再下。
- 未能重現(只讀碼推得),已自降一級。

引句:「if res[3] and not self.tripped:   # 掛覆蓋跑滿單支上限:比掛覆蓋紅更強的訊號,當場斷路,不等連續 3 支(代碼審 r2 資源 s2)」

**finding 2**
severity: minor
blocking: 否
`scripts/lumos:29238` 與 `scripts/lumos:29280`(`cached()` 搭配 `robo_zero`)。
- 前提:快取鍵 `(plat, 測試名, blob, 腳本版本)` 不含 `pkgs`,但 `robo_zero` 用的是這次的 `pkgs`。
- 輸入:同一個 `at_sha` 先對檔 A(套件 com/a)跑,Robolectric 測試 T 的覆蓋資料有 com/a 的紀錄,存進快取。接著對檔 B(套件 com/b,例如用 `--only`)續跑,T 沒碰 com/b。
- 走法:專案類別有紀錄數 = 0 且是 Robolectric,`robo_zero` 為真,於是 `cached()` 刪掉這份對檔 A 仍然有效的快取,並重新量測。
- 影響:只是效能損失,不影響判定。
- 順帶:重量後 T 仍記成「覆蓋接不起來」。「0 筆就是設定沒生效」這個前提是上一輪就有的,本輪的新增只是「把它刪掉」。
- 建議:不刪,只是不採用;或把 `pkgs` 納入快取鍵。
- 未能重現(只讀碼推得)。

引句:「if data is not None and _choice_cov_exec_classes(data) is not None and not self.robo_zero(data):」

**修補三問**(逐項對過 diff 與真代碼)
- ① Groovy GString:`def want = [...]*.toString()` 正確,`it.name in want` 比對 String 與 String。測試靜態擋加真跑 Groovy(找不到 Groovy 時只做靜態)。
- ② `_write_bytes_atomic`:簽章與例外行為相符(OSError 被 `store` 接住)。
- ③ `_choice_cov_prune`:`subs[KEEP-1:]` 加上排除 `cur` 名稱,清完共 KEEP 個。符號連結不在 `subs`,不跟、不刪。
- ④ 缺鍵算失敗:`_choice_cov_parse` 要求 `nolines` 是 list、`noclasses` 是 bool 且為假;真的 Groovy 腳本三個鍵都寫。
- ⑤ `robo_zero` 不進快取:除上面 finding 2 外,`store` 的 scratch 檔名 `lumos-cov-{len(got)}.exec` 不會互撞,因為 `got` 只增不減。
- ⑥ 逾時斷路:見 finding 1。
- ⑦⑧ `after` 固定回 6 項:所有分支都回 6 項(非掛覆蓋、綠、綠但無資料、紅截斷、紅重跑)。`_kill_measure_singles` 無 `after` 時自算 `cut`。截斷時 `return False` 且不寫 baselines,行為正確。
- ⑨ `cov_judged` 已進 gov ck 白名單(`scripts/lumos:18587`)與 `int` 型別表(`scripts/lumos:18496`)。
- ⑩ 新測試:能翻紅的點都綁在行為上,例如 `name_check` 的 `todo` 與 `why`、`robo_zero_cache` 的快取份數。未發現假綠。
- 同類位置:`_kill_merge_singles` 的另一個呼叫端沒傳 `after`,走舊分支;其他地方沒有第二個 `after` 實作。

**圖譜固定席**(摘要)
- `bound-tests-gate`、`guard-kill`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop` 的 ★INVARIANT★ 都綁既有測試,本輪沒有碰到合約行為,無衝突。
- `guard-kill` 的 PITFALL 行 `[test:t_choice_cov_red_breaker]` 已更新「`after` 固定回 6 項」的描述,但綁定測試仍只守紅斷路,新增的 `rerun_edges` 沒掛進來。這是建議補綁,不阻擋。
- `red_rerun` 的 docstring 還寫「回傳 5 項」,實際已是 6 項(只是文字,不構成 finding)。

總結:最高等級是 minor
