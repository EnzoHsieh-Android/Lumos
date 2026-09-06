severity: major
- [major] `--ff` 在分片前重排完整測試集合；不同機器或行程讀到不同失敗快取時，各片不再構成同一集合的分割，會重複並漏跑測試。
  引句:「tests = [t for t in tests if t.__name__ in _lf] + [t for t in tests if t.__name__ not in _lf]」
  位置:scripts/test_lumos.py:23358
  blocking:是
  why:輸入為兩個執行者分別跑 `--ff --shard 1/2`、`--ff --shard 2/2`，且第一個快取含測試 A、第二個快取含測試 B。預期兩片聯集恰等於完整測試集合；實際上各自先把不同名字移到索引 0，再依索引奇偶取片，會造成某些測試兩片都取到、另一些兩片都取不到。`--seed` 在分片後才 shuffle，單獨與分片合用沒有此問題。

- [major] 四個分片共用並競寫同一個失敗快取；最後完成的分片覆蓋其他三片的失敗名單，且寫入不是原子操作。
  引句:「_cache.write_text(_jc2.dumps({"failed": _failed_names}, ensure_ascii=False),」
  位置:scripts/test_lumos.py:23445
  blocking:是
  why:輸入為 pre-push 同時啟動四個 runner。預期每個行程只寫自己的隔離狀態，或由父行程合併四份結果；實際 `_cache` 固定指向 repo 的 `.lumos/test-cache.json`，不在各行程的暫存根內，四片都會重寫它。最後內容只代表最後完成的一片；交錯寫還可能留下無效 JSON，之後讀取錯誤又被靜默忽略。這不會讓本次 pre-push 假綠，因為它未帶 `--ff`，但會破壞作者新增的 `--ff` 狀態。

- [major] 能力探測對舊版 runner 會先額外跑一次完整套件；舊 runner 正是以寬鬆解析忽略 `--help`，因此一次 push 可能從八分鐘變成約十六分鐘。
  引句:「if ! "$PY" "$REPO_ROOT/scripts/test_lumos.py" --help 2>/dev/null | grep -q -- "--shard"; then」
  位置:scripts/hooks/pre-push:220
  blocking:是
  why:輸入為本 patch 前使用 `parse_known_args()` 的 runner。預期能力探測快速返回說明，探不到就串行跑一次；實際舊 runner 會忽略 `--help` 並執行全套，管線等它跑完才判斷沒有 `--shard`，隨後 fallback 又跑一次全套。新增測試只用了立即退出的假舊 runner，沒有重現真正的舊解析行為。

- [major] runner 不論是否使用 `--ff` 都在其所在專案根寫快取；vendored 到消費專案後會建立或改寫消費者的 `.lumos/test-cache.json`，而本 patch 的 `.gitignore` 規則不會隨單一測試檔自動 vendor。
  引句:「_cache = Path(GRAPHCTL).resolve().parent.parent / ".lumos" / "test-cache.json"」
  位置:scripts/test_lumos.py:23349
  blocking:是
  why:輸入為消費專案內的 `scripts/test_lumos.py` 與 `scripts/lumos`。預期測試隔離狀態落在該行程的假 HOME／暫存根，或至少只在啟用 `--ff` 時建立；實際 `GRAPHCTL` 解析到消費專案，任何普通、關鍵字或分片執行結束都會在消費專案 `.lumos/` 寫檔。若消費專案沒有同步新增 ignore 規則，工作樹會被污染。

- [minor] `--list` 在分片、種子及關鍵字處理前直接返回，組合旗標時會列出全部測試，與「只跑其中一片／只跑名稱含此字串」的介面語意不一致。
  引句:「if _args.list: for _n in sorted(k for k in globals() if k.startswith("t_")):」
  位置:scripts/test_lumos.py:23340
  blocking:否
  why:輸入為 `--shard 2/4 --list` 或 `-k foo --list`。預期列出將被該命令選中的測試，方便檢查分片覆蓋；實際在建立及篩選 `tests` 前就列出所有 `t_`。新增分片測試甚至註明此限制並改用零命中關鍵字計數，顯示目前 `--list` 無法驗證實際片內容，但 CLI 沒有警告組合旗標被忽略。

- [clean] pre-push 的 PID 收集與等待在目前 shell 選項下能保留所有子行程失敗；不會因第一個非零 `wait` 提前退出。
  引句:「for _p in "${_pids[@]}"; do wait "$_p" || _rc=1; done」
  位置:scripts/hooks/pre-push:238
  blocking:否
  why:查證 hook 僅啟用 `set -u`，沒有 `set -e` 或 `pipefail`。`$!` 是單一數字，`_pids+=($!)` 在此不會拆壞；每個 PID 都會被等待，任一非零都把 `_rc` 設為 1，後續仍繼續收割其他子行程。

- [clean] `-x` 與分片合用時，提早停止的分片仍以非零退出，父 hook 會判整體失敗；JSON 摘要未被當作放行依據，因此不會把未完成片誤判為綠。
  引句:「拿它當判準等於「runner 不支援新旗標就一律紅」。」
  位置:scripts/hooks/pre-push:237
  blocking:否
  why:輸入為某片帶 `-x` 且首個失敗後停止。預期整體閘失敗；實際 runner 的全域 `FAIL` 已增加，最終離開碼非零，父行程的 `wait ... || _rc=1` 正確擋下。摘要只供閱讀，不參與 verdict。

- [clean] 圖譜健康段移除「無 vault 就結束整支 hook」後，沒有遺失既有必要放行路徑；其後新增的昂貴測試仍受來源 repo 條件保護。
  引句:「if [[ $have_vault -eq 1 ]] && ! "$PY" "$GRAPHCTL" doctor --ci; then」
  位置:scripts/hooks/pre-push:98
  blocking:否
  why:查證舊提早退出點之後原本只剩 `doctor --ci` 的成功／失敗收尾；沒有其他既有副作用依賴該退出。新版本無 vault 時只略過 doctor，而兩支測試各自要求 `skills/lumos-project-notes` 與對應 runner 存在，因此一般消費專案不會意外跑來源 repo 全套。
