severity: minor

## 問一 分層與依賴方向
結構對齊。掛鉤新函式 pp_block_range_for 放在 pp_range_for 正下方,範圍推導仍交給 lumos(`scripts/hooks/pre-push:511` 的 drift check 段同樣「掛鉤不自己算、交 lumos」),沒有掛鉤自己重算分岔點的第二份邏輯;cmd_push_range 只包 _push_range_start,跟 `scripts/lumos:35764` 的 cmd_drift_check 用同一支起點函式、同一個 _note_audit_root,沒有跨層直呼。cmd_push_range 插在 _push_range_start 與它的幫手 _push_no_mainline 之間(把一組 _push_* 幫手拆開),但 cmd_drift_check 也貼著自己的幫手放,不算不一致。
引句:「root = _note_audit_root(repo)」

## 問二 命名與錯誤處理
大致對齊,有三處小差異(見 F1 到 F3)。結果放全域 _PP_BR 與 `scripts/hooks/pre-push:205` 的 impact_once(_IMPACT_JSON)同一種「全域變數回傳」寫法;rc 規矩沿用 pp_stop_if_signaled(`scripts/hooks/pre-push:513` 同樣先 stop 再判 rc1);子命令 dest 前綴 prg_ 與其他子命令的短前綴一致。
引句:「pp_stop_if_signaled "$pr_rc" "新分支首推起點(push-range)"」

## 問三 第二種做法
沒有引入新的回傳方式或新的推送參數規矩的結構性差異。零值判斷與測試現場各有一個小分歧(F4、F5),都沒到第二套機制的程度。
引句:「_PP_BR="$(pp_range_for "$1" "$2")"」

## F1 push-range 不在非 git 目錄時的 rc 與鄰居相反
severity: minor
blocking: 否
引句:「print("擋下:這裡不是 git 專案", file=sys.stderr)」
對照:`scripts/lumos:35764` 起的 cmd_drift_check 在 root 為 None 時印「這裡不是 git 專案,跳過」回 0;`scripts/lumos:32151` 的 reread-check 也回 0。push-range 回 2。掛鉤端因為只認 rc0 加格式吻合才採用,行為安全,但同樣吃推送參數的兩個鄰居是回 0 放行,這裡是 rc2,規矩不一。

## F2 推送參數檢查寫法與鄰居不同
severity: minor
blocking: 否
引句:「print("擋下:--push-remote 與 --pushed-ref 都要給(值可以是空字串)", file=sys.stderr)」
對照:`scripts/lumos:35764` 起 cmd_drift_check 用「(push_remote is None) != (pushed_ref is None)」判「要一起給、都不給也行」,訊息「要一起給」;reread-check 同。push-range 改成「兩個都必給」,等於另立一套參數規矩(語意有理由,因為這支沒有「手動不帶」的路徑,但 argparse 層也沒用 required=True,而是 default=None 再在函式內擋,跟 --diff 的 required=True 寫法不齊)。

## F3 呼叫端用位置參數、鄰居用關鍵字參數
severity: minor
blocking: 否
引句:「return cmd_push_range(args.prg_repo, args.prg_diff, args.prg_remote, args.prg_ref)」
對照:同段 note-audit 與 drift 分派(`cmd_drift_check(repo=args.dr_repo, diff_range=..., push_remote=..., pushed_ref=...)`)一律關鍵字傳參。

## F4 零值判斷另寫一套正則,鄰居用 $_ZERO 字串比對
severity: minor
blocking: 否
引句:「[[ "$1" =~ ^0{40}(0{24})?$ && "$3" == refs/heads/* ]] || return 0」
對照:同檔 pp_range_for(`scripts/hooks/pre-push:38` 附近)與推送迴圈都用 [[ "$1" == "$_ZERO" ]]。新函式為了 SHA-256 長度改用正則,於是同一支掛鉤內有兩種「遠端舊值為零」的判法,且 pp_range_for 在 64 位零時走 cat-file 失敗才退空樹,語意靠巧合一致。pr_rc 也沒像 _out 一樣宣告 local(鄰居 dr_rc 等是全域,算齊;但同一函式內一個 local 一個不 local)。

## F5 新測試另寫一套臨時 repo 與掛鉤執行幫手
severity: minor
blocking: 否
引句:「def _fp_hook(d, stdin):」
對照:既有 `scripts/test_lumos.py:55905` 的 _dr_hook_fakes(假 lumos 記 argv、支援 FAKE_SIG_CMD 殺訊號)與 t_prepush_range_scan 的 run_pp/setup_lumos 已涵蓋「跑掛鉤、模擬訊號」。新測試自建 _fp_repo(symlink 或 wrapper 字串)與 _fp_hook,等於第三套現場;也漏了 commands/INDEX.md:36 那種索引同步(見 F6)。

## F6 命令索引 INDEX.md 沒補 push-range
severity: minor
blocking: 否
引句:「推送範圍（`push-range` 推送前掛鉤在新分支首推時取跟主線的分岔點）」
對照:`skills/lumos-project-notes/commands/INDEX.md:36` 的 06 檔列把 ci-wait、ci-status、note-audit 逐一列名,diff 補了 06 檔本文、08 檔、reference.md 與 ARCHITECTURE 數字,但 INDEX.md 的 push-range 出現次數仍是 0;而 reference.md 已稱 INDEX 是「81 個指令的總目錄」。

不對齊共 6 條,其中 major 0 條
