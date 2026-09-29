severity: minor

## F1 兩態判斷的 git 呼叫數與時間不受守衛 deadline 約束
severity: minor
blocking: 否
引句:「+    before = _vendored_state(root, "HEAD")[0]」
佐證行:file: `scripts/lumos:29602`(`_over()` 只在 `_delguard_vendored_skips` 回來之後才查,見 29637 到 29642)
佐證行:file: `scripts/lumos:33249`(`_lens_git` 每次 git 逾時 20 秒,大於守衛自己的 15 秒 deadline)
1. `_vendored_state(root, ref)` 對整份 `_VENDORED_ALL` 每支各跑一次 `git show`(共 17 支),再加一次讀 `.lumos/vendored.json`;兩態合計 2×(17+1)=36 次,跟這次暫存差異裡出現幾支工具檔無關(「diff 沒出現工具檔路徑就不算」的門檻只是字串比對,任何提到 scripts/lumos 字樣的文字行都會觸發)。註解與計劃寫的「每支工具檔一次」低估了實際呼叫數。
2. 實測:消費專案(17 支工具檔全在、清單齊全)在本機快 git 下兩態 0.65 秒,尚可。
3. 重現(在 shared clone 建消費 repo,PATH 前置一支對 `show` 睡 0.5 秒的 git shim,`LUMOS_DELGUARD_DEADLINE` 預設 15):`_delguard_vendored_skips(root, "scripts/lumos")` 耗時 19.1 秒,超過 15 秒 deadline。回到 `cmd_delguard_check` 後 `_over()` 為真,整次守衛走「timeout 降級」放行,tokens 一個都沒掃;所以慢檔案系統(NFS、Windows)上,沒碰工具檔內容、只是 diff 文字提到路徑的提交,反而把原本能掃完的刪除守衛吃成降級。
4. 最壞情形:git 卡住時每次都到 20 秒逾時,36 次 = 720 秒,pre-commit 被拖住十二分鐘,deadline 完全無效。註解宣稱「時間算在這道守衛的 deadline 裡」在這段不成立(只是事後比對)。
5. 未做:只查 diff 裡實際出現的工具檔(把 `_vendored_state` 的檔名集合限縮成 diff 命中的那幾支),呼叫數會從 36 降到 2×(命中數+1);目前是全清單。

## F2 讀不到暫存區被當成「已不在暫存區」,刪除行反而被跳過(fail-open 方向錯)
severity: minor
blocking: 否
引句:「+    after, after_present = _vendored_state(root, "")」
佐證行:file: `scripts/lumos:17826`(`elif r.returncode == 0` 才算 present;rc 非 0 一律當不存在,跟逾時的 `r is None`(當在、沒對上)處理不同)
1. `_vendored_state` 對 `git show` 的 rc≠0(檔案真不存在、還是索引讀取失敗)不分:兩者都不進 present。
2. `_delguard_vendored_skips` 的規則是 `p in after or p not in after_present`,「不在暫存區」被解讀成拆除,刪除行跳過。所以暫存區讀取回 rc≠0(非逾時)時,改之前原封不動的工具檔一律被判拆除、名稱不抽。
3. 重現:消費 repo 暫存一支被專案改過的 `scripts/lumos`,真實 git 下 `scripts/lumos in rm_skip` 為 False(正確,照抽);把 PATH 前置一支對 `show :*` 回 rc128 的 git shim,同一輸入變成 True,專案自己寫的被刪名稱整支漏看。逾時(None)那條路徑是安全方向,rc≠0 這條是不安全方向。
4. 自然觸發條件(索引檔損毀或短暫不可讀)罕見,所以只到 minor;⚠ 未找到不靠 shim 的觸發法。

## 其他鏡頭項目的判定(不成 finding)
- git 逾時或跑不起來(`_lens_git` 回 None):`_vendored_state` 把該檔當「在、沒對上」→ 不算原封不動 → 照抽,方向安全;HEAD 讀不到清單時 `before` 為空,一支都不跳,安全。
- 沒有 HEAD(第一個提交):git show 回 rc≠0,before 空集合,一支都不跳,安全。
- 治理帳寫入:`_delguard_log_result`/`_delguard_log_degraded` 都在兩態計算之後、各自 try/except best-effort;兩態計算本身不寫帳,沒有半寫入問題。timeout 降級時 note 仍帶 `vendored-skip=`(用的是已算出的 parsed),一致。
- 照計劃回退:`git revert --no-commit` 會把 `_delguard_vendored_skips`、`added_skip` 參數與測試一併退回,帳本檔留現況;退回後 `cmd_delguard_check` 回到 r1 版呼叫 `_vendored_state(root)[0]`,不遺留孤兒呼叫。未見不一致。

## 圖譜鏡頭逐條
- 存量漂移守衛:本次改動只碰 delguard 與 c4 證據頁輸出,不影響其合約。
- bound-tests-gate ★INVARIANT★:綁定測試機制不受影響;新增 `t_delguard_vendored_two_states` 已在計劃綁定。
- guard-kill、授權與歸屬、測試假綠形態、lumos-cli-read、lumos-cli-lifecycle、design-loop:diff 未動其宣稱行為(rc 優先序、JSON 純度、授權白名單、re-inject、search 過濾、處置閘),判不影響。

最高等級:minor
