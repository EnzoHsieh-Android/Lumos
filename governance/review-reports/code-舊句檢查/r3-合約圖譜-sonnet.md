severity: minor

## F1 計劃 r1 折入節還留著「group_ok 只給 m1 用、group 可寫也算可信」的現在式句子
severity: minor
blocking: 否
引句:「`group_ok` 只給 m1 兩處用,其他家目錄寫入點照舊嚴格」
佐證行:file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:293`
佐證行:file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:289`
1. 本次把 `group_ok` 從 `_trusted_private_dir`、`_mkdir_trusted_under_home`、`_home_cache_write` 整個拿掉(repo 內 `grep group_ok scripts/lumos` 零筆),r2 折入節(計劃 298 行)也寫了「撤回」。
2. 但 r1 折入節的兩句(289 行「加 `group_ok`…group 可寫也算可信」、293 行「`group_ok` 只給 m1 兩處用」)在 patch 裡是未動的脈絡行,沒有「已撤回」標記,也沒指向 r2 那條。下一個只讀 r1 節的人會以為 group 可寫的家目錄快取層現在被信任。
3. 這是同一篇計劃內部新舊打架(CLAUDE.md 步驟 2 說的情形),不影響程式行為;補一個「(r2 已撤回,見下)」就能收掉。r2 節第 306 行只講翻紅作廢,沒有回頭修這兩句。

## 圖譜鏡頭逐條判定
- lumos-cli-read ★INVARIANT★(search 濾網位置):本 diff 不碰 search/濾網,不影響。
- bound-tests-gate ★INVARIANT★(code-loop check 逐支真跑綁定測試):diff 動的是 drift check/m1 與家目錄目錄建立,`_mkdir_private_layer` 只影響 bound-filter 快取目錄的建立;判準(真目錄、自己的、group/other 不可寫)沒放寬,建立順序仍是「上一層驗過才建下一層」;不影響。
- guard-kill、授權與歸屬、測試假綠形態、lifecycle、design-loop:diff 未碰 guard kill rc、`_VENDORED_TOOLKIT`、re-inject、處置閘;不影響。
- vault-lock / dispatch-lens / bound-filter(Systems/hook信任邊界:逐層建逐層檢查,★任何一層不過就停手、已建的不回頭刪★):`_mkdir_private_layer` 只在 mkdir 成功時才多做一次不跟連結的 chmod(`_chmod_no_follow`,O_NOFOLLOW|O_DIRECTORY);已存在(含連結)走 FileExistsError 回 True、交給原本的 is_symlink/uid/S_IWGRP|S_IWOTH 檢查,所以合約不變。新建層原本在 umask 022 是 0755、現在是 0700,其他鄰居只有自己讀寫,沒有看到依賴 group/other 可讀的用法。不影響。
- graph-sync-coverage 提到 check-graph-sync.py 抄了一份同判準、「一邊改了另一邊要跟著改」:該 hook 的 `_mkdir_under_home` 本來就用 `mkdir(mode=0o700)`、判準同為 S_IWGRP|S_IWOTH,本次沒有需要同步的差異(0700 給了就不受 umask 放寬)。不影響。
- 存量漂移守衛:新增的 PITFALL 兩行帶日期、來源席位、`[test:]`,符合前綴規則;`快取與留痕的目錄照全家同一套判準`、時間、超長行算判不了三段與程式一致(`_drift_m1_busy`、`_drift_m1_long_note`、O_NONBLOCK+S_ISREG)。新增行沒有 `路徑:行號` 引用、沒有無來源的 FACT/FLOW/DEP。
- commands/08、pre-push、ci.yml 說明文字:改為「m1 擋下改的是 drift_check.old_sentence、改 gate 沒用」,與 `_drift_m1_report` 印的句子與 doctor 分開兩行一致;全 repo 查不到還說「群組可寫也算可信」的舊句,除上面 F1 的計劃歷史行。

最高等級:minor
