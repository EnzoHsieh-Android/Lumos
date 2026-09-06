severity: major
- [major] 預設暫停仍會在首次執行時啟動昂貴的八題 Claude 探針
  位置:`governance/daily-governance.sh:34`
  引句：「`  "$DIR/autonomous-loop.sh" --dry-run 6 >> "$DIR/logs/autonomous.log" 2>&1`」
  why: wrapper 改成每日無條件進入後，沒有 `history.jsonl` 週戳的新機器會立即跑 `scenario_probe.py --sample 8 --timeout 600 --max-turns 18`；考卷、nags、replay 的 stamp 缺失也會觸發首次執行及可能的 LINE 通知。這使「預設暫停」仍可能花費模型配額並寫 history、delta、replay、backlog 等檔案，與只停昂貴派工的宣稱不符。各閘分別是考卷 ≥7 天、probe 每 ISO 週、nags 每 ISO 週、replay 每 ISO 週；沒有 stamp 時全部視為到期。

- [major] bootstrap 會用消費專案的舊 vendored hooks 覆蓋剛從最新版來源安裝的全域 hooks
  位置:`scripts/lumos:11607`
  引句：「`    _sync_global_from_project(root)`」
  why: `cmd_bootstrap` step 2 先從最新的 `home` 執行 `install --force`，但已有 vault+vendored 的 step 3 仍呼叫 `_install_hooks_py(root)`；新的相容外殼會立刻從可能很舊的消費專案再次同步全域 hooks/settings，將 step 2 的新版倒退。`_vendor_toolchain` 路徑已改成自癒後同步，這條既有專案路徑沒有，兩條行為不一致。

- [major] 以 set 判斷「獨有行」會遺失合法的重複帳列
  位置:`scripts/lumos:11135`
  引句：「`                    have = set(now)`」
  why: JSONL 是事件序列而非集合；若遠端已有一筆內容 X，而本機在共同基線後又合法 append 一筆完全相同的 X，`l not in have` 會把本機新增事件丟掉。若本機新增兩筆相同事件而遠端已有一筆，兩筆都消失。新增測試只使用三個不同的 `ts`，無法抓到此資料遺失。

- [major] checkout 後沒有持久備份，程序中斷或寫回失敗會永久丟失未提交帳列
  位置:`scripts/lumos:11128`
  引句：「`            subprocess.run(["git", "-C", str(src), "checkout", "--"] + paths,`」
  why: 本機獨有資料只存在 Python 記憶體；checkout 一完成，SIGKILL、斷電、pull 卡死後被殺或後續寫入失敗都會讓資料消失。錯誤訊息聲稱可由 `HEAD@{1}`/git 物件庫救回也不成立，因為未提交內容從未進入 git 物件庫。普通的 pull 非零回傳會走寫回迴圈，通常救得回，但沒有涵蓋中斷窗口；寫回 `OSError` 後函式也只警告並失去唯一副本。

- [minor] porcelain 路徑解析不是 Git 格式解析，rename 與 quoted path 都會被誤讀
  位置:`scripts/lumos:11112`
  引句：「`    paths = [ln[3:].strip().strip('"') for ln in dirty if ln.strip()]`」
  why: `?? path` 可碰巧工作，但 rename/copy 的內容是 `old -> new`，帶特殊字元的 quoted path 還包含 Git 的 C-style escapes；單純剝外層引號不會解碼。現有白名單下這些情況多半是保守地拒絕自動合併，尚未看到可把非白名單檔誤判成白名單的直接路徑，但會讓合法簿記 rename 或特殊路徑無法更新。

- [minor] 暫停測試只釘文字位置，開關失效或觀測實際不可達仍會假綠
  位置:`scripts/test_lumos.py:26135`
  引句：「`        check("暫停開關: ★所有週期觀測都排在開關之前(關掉派工不會連它們一起關)★", not after, str(after))`」
  why: 例如在第一個觀測呼叫前加 `exit 0`，或把 gate 改成永遠不成立但保留同一行文字，測試仍全綠；它沒有證明 `LUMOS_AUTOLOOP_OFF=1` 時五段真的執行且 gap selector 沒執行。就目前實作而言，pause 的 `exit 0` 會觸發 trap；因 `GAP_JSON` 尚空，finalize 在移除 scratch 與 lock 後直接返回，不會記結局帳、requeue 或發連敗通知，鎖會正常釋放。

- [minor] hook 更新反事實測試漏驗 bootstrap 路徑及 settings/Codex 同步
  位置:`scripts/test_lumos.py:26172`
  引句：「`        check("update: ★全域 hook == 來源的新版★(不是更新前的舊副本)", got == want, f"len={len(got)} want={len(want)}")`」
  why: 測試只跑 `lumos update` 並比較一支 Claude hook；即使 `_install_hooks_py` 在 bootstrap 已有專案路徑重新覆蓋舊版，或 Claude settings、Codex hooks/settings 完全沒同步，這支測試仍綠。

- [minor] 聯集合併測試未檢查命令成功，後續 update 壞掉仍可能假綠
  位置:`scripts/test_lumos.py:26224`
  引句：「`    check("update/來源髒帳: 沒有被擋下(rc 不是中止)", "擋下:工具鏈來源拉不到最新版" not in r.stderr, r.stderr[-200:])`」
  why: 斷言名稱說「rc 不是中止」，實際卻不檢查 `r.returncode`；只要 pull 和帳本復原已發生，update 隨後在 vendor、reinject 或全域同步階段非零退出，五個內容斷言仍可能全部通過。它也未覆蓋重複行、pull 失敗及 checkout 後中斷等資料安全情境。
