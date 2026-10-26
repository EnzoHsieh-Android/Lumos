severity: major

固定席說明:這次派工沒附固定席節點(LUMOS-LENS 寫「沒附固定席節點」),所以沒有「這次新增的殘留」段可逐條答。我另外跑了 `lumos impact --diff`,列出的節點和這輪發現無關。我也不能憑鎖檔判斷,所以沒動 `.warming` 鎖(該路徑當時不存在)。

e2e-coverage 分支:我在臨時 clone 把它合進 490dac6a,`scripts/lumos` 自動合併乾淨(只有 README 兩份衝突)。`python3.14 scripts/test_lumos.py -k coverage` 結果 62 passed, 0 failed。該分支對 `_e2e_scope_dirs`、`_e2e_scope_hit`、`_e2e_owner_index`、`_e2e_owners`、`_e2e_ai_pending_all` 都只用函式介面,沒有拆開四元組,所以接到這一版不會壞。`_e2e_ai_pending_all` 回傳形狀不變。

實驗環境:`-k android_e2e` 在 490dac6a 上 617 passed。本輪重現皆為手跑,沒有引用既有測試的綠燈。

## Findings

1. 外來文字出口沒收乾淨,`judge` 整套與 `--precheck` 仍原樣印出
severity: major
blocking: 是
引句:「print(f"擋下:{why}", file=sys.stderr)」
file: `scripts/lumos:42167`(`_e2e_full_blocked`),另 `scripts/lumos:42182`(`judge --precheck` 的 `print(f"擋下:{err}" if err else ...)`)
失敗場景:陌生專案提交的查證紀錄,其 `feature_runs` 鍵名帶換行與 ESC。跑 `judge` 時,`_e2e_record_update` 回傳的錯誤字串帶著鍵名,由 `_e2e_full_blocked` 原樣印進 stderr。結果是 AI 視野裡出現偽造的獨立一行和 ANSI 碼。這正是 S51 與 WHY 宣稱「e2e 指令印的每一行『擋下:』都清掉」的那一類,第五次出現。`--precheck` 會原樣印未追蹤檔名,同樣沒清。
重現:臨時專案寫入 `feature_runs: {"f.c\nPWN-LINE \x1b[31m": {"result":"pass","items":"x"}}` 的紀錄,再跑 `lumos android-e2e judge <run-dir>`。
- 修前(de8a99bc):stderr 含 `\x1b`,且有以 `PWN-LINE` 開頭的獨立行。
- 修後(490dac6a):輸出完全相同。
- `waive` 走同一份紀錄時已被清掉,證明漏的是 `judge` 這個出口。
- `--precheck` 另測:建一個叫 `zz\nPWN-LINE\x1b[31m.txt` 的未追蹤檔,修前修後都原樣印出。
歸因:有證據的原有漏查。兩版輸出相同,這輪十二處改寫漏了這兩處。

2. 判定改用 2MB 上限,寫入端卻不檢查寫完後的大小
severity: minor
blocking: 否
引句:「rec, rerr = _e2e_tree_json(root, sha, rel, deadline, limit=E2E_RECORD_FILE_MAX)」
file: `scripts/lumos:41737`;寫入端 `scripts/lumos:40974`(只檢查寫之前的大小)
失敗場景:紀錄 2,097,118 位元組(上限 2,097,152),`waive` 成功寫入並回 0,檔案長到 2,097,325。提交後判定擋下並要人「修好或刪掉」,再放行也被拒。使用者剛寫的放行不生效。這是 r4 想消除的「寫得進去卻照樣被擋」。要碰到需要 2MB 級的紀錄,實務上不易,所以只列 minor。
重現:用臨時專案造一份 2,097,118 位元組的紀錄(含一筆舊放行),跑 `waive`、提交,再跑 `check`。
- 修前:`check` 回 rc0,狀態 `waived`(判定讀到 16MB)。
- 修後:`check` 回 rc1,狀態 `blocked`,`bad_record=True`。
歸因:有證據的修復回歸。

3. r4 新增的兩個「git 失敗要擋」的生產端沒有測試守住
severity: minor
blocking: 否
引句:「return None, _E2eGitErr(f"{rev[:8]} 的 {rel} 在樹裡卻讀不出內容(物件缺或 git 失敗)")」
file: `scripts/lumos:41443`、`scripts/lumos:41448`、`scripts/lumos:41438`;`scripts/lumos:41632` 起的 `_e2e_parent`;測試 `scripts/test_lumos.py` 的 `t_android_e2e_record_size_gate` 與 `t_android_e2e_gate_r4_paths`
失敗場景:`t_android_e2e_record_size_gate` 直接把 `_e2e_tree_json` 換成回 `_E2eGitErr` 的 lambda;`t_android_e2e_gate_r4_paths` 把 `_e2e_parent` 整支換掉。真實的 `_e2e_tree_blob` 和 `_e2e_parent` 從沒被這兩支測試執行。真實 git 暫時失敗時,若 `_E2eGitErr` 被拿掉,判定會誤叫人刪好紀錄;若 `_e2e_parent` 失敗改回放行,會在查不到主線時漏放。
重現:在 490dac6a 的臨時 clone 做三個變異,全套 `-k android_e2e` 都是 617 passed, 0 failed。
- 把 `_e2e_tree_blob` 的三處 `_E2eGitErr(` 拿掉。
- 把 `_e2e_parent` 的 `if raw is None` 回傳改成 `return "", None`。
- 把 `return (parts[1] if len(parts) > 1 else "")` 改成 `parts[1]`(根提交會 IndexError)。
歸因:有證據的修復回歸(新碼的守衛沒有真測試)。

4. 十一處 `_e2e_say_block` 呼叫點只有兩處有測試守住
severity: minor
blocking: 否
引句:「print(f"擋下:{_e2e_clean(msg, 2000)}", file=sys.stderr)」
file: `scripts/lumos:41395`;呼叫點 `scripts/lumos:40273`、`40301`、`41134`、`41152`、`41982`、`42053`、`42057`、`42131`、`42141`
失敗場景:`t_android_e2e_text_gates` 只守 `_e2e_waive_ack` 和 `waive` 的 `record_update` 兩處。另外 9 處(包含 `_macrobench_mode` 的 2 處、`select`、`judge_partial`、`waive` 的指紋與提交檢查、`judge_selected` 的兩處)改回原樣 `print(f"擋下:…")`,測試仍綠。
重現:在 490dac6a 的臨時 clone,九處逐一改回原樣,`-k text_gates` 全部 SURVIVES;九處同時改回,全套 `-k android_e2e` 617 passed。`shared_paths` 超過 1000 項的上限刪掉,`-k text_gates` 也仍綠。
歸因:有證據的修復回歸(這輪新碼沒測試守)。

5. `_e2e_parent` 重做了專案已有的「取上一版並分辨失敗」寫法
severity: minor
blocking: 否
引句:「raw = _nodehome_git(root, "rev-list", "--parents", "-n", "1", sha, timeout=_secev_git_left(deadline))」
file: `scripts/lumos:41632`;既有寫法 `scripts/lumos:60636`(`_push_rev`,回 `(sha 或 None, 查詢本身失敗了嗎)`),前例 `scripts/lumos:61001`(`_push_rev(repo_root, f"{tip}^1")`);同檔 `_e2e_gate_resolve` 就在用 `_push_rev`
失敗場景:沒有現成失敗,只是重複。兩份「失敗與沒有分開」的邏輯要各自維護。
歸因:未判定。

6. README 說「要先合主線」的擋下不印放行指令,與程式不符
severity: minor
blocking: 否
引句:「blocks for a missing mainline, a timeout, needing to merge the mainline first, a removed e2e section or an unreadable record print no waive line」
file: `README.en.md`(中文 `README.md` 對應句同);程式 `scripts/lumos:66959`、`66964`
失敗場景:`_e2e_gate_full_note` 設 `mainline_newer` 時,`info` 帶有 `fp`,`_cl_say_e2e_block` 照印放行指令。只有 `merge_main=True` 那條(沒有 `fp`)才不印。我用 `cfg_weakened` 的版本跑出完整輸出,確認同樣會印放行指令。
歸因:有證據的修復回歸(這句是 r5 新寫的;修前沒有這段說明)。

## 三問

① 修復效果的行為證據。
- 路徑含控制字元的設定:`macrobench --check-config` 現在拒收。
- 一次 `waive` 與 `waive --ack` 遇到鍵名帶 ESC 的紀錄:修前原樣印出,修後已清。
- 超過 2MB 的紀錄:判定端擋下。
- `waive --list`:標「超過 2MB」並邊讀邊印,深層巢狀、非 UTF-8 的紀錄跳過,不崩。
- `cfg_weakened`:實跑輸出「先改回跟主線一樣」,且不叫人合主線。

② 修補處相鄰路徑是否成立。不完全成立。
- `judge` 整套與 `--precheck` 沒收進統一出口(發現 1)。
- 寫入端沒跟上新的 2MB 判定(發現 2)。
- 新守衛的真實生產端沒有測試(發現 3、4)。
- e2e-coverage 接到這一版沒問題(見上)。

③ 新發現,修前修後各是什麼。
1. 修前有、修後仍有。
2. 修前放行、修後擋下。
3. 修前沒有這些守衛,修後有守衛但沒有測試守住。
4. 修前沒有,修後新碼測試不足。
5. 修前沒有這個函式,修後重複。
6. 修前沒有這段說明,修後說錯。

最高等級 major,擋實作的 1 條(發現 1)。
