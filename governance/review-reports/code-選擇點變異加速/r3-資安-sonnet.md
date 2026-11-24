severity: clean

在〈工具鏈三類〉三類範圍內,沒有找到攻擊者能利用的洞。派工詞點名的鎖檔 `.../dispatch-lens/baf3be87….json.warming` 不存在,我沒有刪任何鎖。我沒建 worktree,也沒建臨時目錄。

## 已驗主張

**①提示注入:無。**
- 新帶進給 AI 的文字,來源只有固定字串或整數。
- 帳本欄位 `judged` 只會寫 `merged` 或 `single`。
- 標準錯誤那行用的 `_CHOICE_MERGE_BASE_WHY` 是固定表。
- 「對不到名字」那條原因只帶整數計數。
- 席報告、筆記內文和檔名都沒有流進派工詞。
- 測試輸出的 tail 只進 `_kill_res_excerpts`,走原有路徑,不是新增入口。

**②讀寫與執行越界:無。**
- **shell 插值:** 合併指令每一段都交給 `_run_cmd_expand`,用 `shlex.quote` 和名稱篩選跳脫,與逐支流程同一套。`_kill_merge_ready` 先對每個名稱過 `_test_name_ok` 和撞名判定,才組指令。
  - 引句:「segs = [_run_cmd_expand(shape["seg"], n, name_filter=name_filter) for n in sorted(names)]」
- **圍欄成立:** `_choice_merge_clear` 的 `shutil.rmtree` 前有圍欄,目標必須在工作樹內。
  - 引句:「return real if real.startswith(os.path.realpath(str(wt)) + os.sep) else None」
  - 圍欄在 `_choice_merge_results_dir`。路徑尾段固定為 `build/test-results/<測試任務名>`,任務名受 `_GRADLE_UNIT_TASK_RE` 限制。
  - 測試 S14 覆蓋 `-p /tmp/elsewhere` 與 `-p ../x`,並且有翻紅釘。
- **XML 讀取:** 讀結果檔走既有的 `_secev_junit_facts`,我另外查過 `scripts/lumos:9046`。DTD 在 `tq.junit` 就被拒(`JUnitRejected`),剖析錯誤和過深也回「沒跑乾淨」,不丟例外。
  - 新加的單檔 8 MiB、合計 64 MiB 上限在 `_choice_merge_facts` 先檢查。
  - 結果檔若是符號連結,指到的東西只會被剖析,內容不會外流。
- **未登記路徑的寫入:** 新增的寫入只有工作樹內被壞法改的檔,以及 `build/test-results` 的清除。
- **密鑰與信箱:** snapshot 的 `+` 行搜過信箱、token、`curl`、`wget`、`os.system`、`shell=True`、`eval(`、`pickle`、`http://`,沒有新寫的密鑰或信箱。
- **hook 與安裝腳本:** `scripts/hooks` 與安裝腳本在 `47a37c05..744f7b6d6` 之間沒有改動。

**③非刻意、一步繞過守衛:無。**
- 合併快篩只可能把壞法判成「存活」,也就是更嚴格、要人處置的方向。它永遠不判殺掉,所以不會讓有存活的行被當成已殺掉。
  - 引句:「合併永遠不判殺掉、編不過、掛住。」
- 殘留環境變數 `LUMOS_SKIP_CHOICE_MERGE` 只能關掉合併、退回原本逐支流程,不放寬任何閘。判斷式只認 `1`:
  - 引句:「merge = not no_merge and os.environ.get("LUMOS_SKIP_CHOICE_MERGE") != "1"」
- **按 Ctrl-C:** 第一個訊號只收帶合併標記的程序,不拋例外(`st.defer` 為真)。`_kill_merge_screen` 在還原後才丟 `_KillHalt`,而且不交列、不記帳。
  - 套完壞法、開快篩之前若已收到訊號,會先還原再停,工作樹不會留著壞法。
- **`anchor-baseline.json`:** `scripts/test_lumos.py` 的新雜湊用 `git show 744f7b6d6:scripts/test_lumos.py | shasum -a 256` 算出,確實等於 `b72ebebc…`。note 寫明有使用者原話「簽」,雜湊與內容一致。
  - 引句:「"scripts/test_lumos.py": "b72ebebcbb27869bf80a752cd8f51e5a4c7d7b2c563c3f549f4d9f6929b6bf99"」
  - 我無法從材料驗證「簽」是否真的出自使用者,這屬於範圍外的人工核可,不算洞。

**測試檔:** 新增測試都放在 `tempfile.mkdtemp(prefix="gctl-ckm-")` 底下,假 gradle 腳本只寫臨時目錄,沒有看起來真能用的憑證,也沒有拼接外部輸入的命令。

## 審查範圍外的觀察
- 工作樹裡的測試會執行不可信碼,例如在 `rmtree` 與讀取之間替換符號連結。這是 choice-kill 本來就要跑被審分支測試的前提,不是這次改動新增的攻擊面,所以不報。

## 讀過的檔
這 10 支檔都是整份 diff 讀的;`scripts/lumos` 和 `scripts/test_lumos.py` 讀的是 hunk 與必要上下文。
1. `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md`
2. `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`
3. `docs/lumos-toolchain-knowledge/Projects/選擇點變異平行_計劃.md`
4. `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
5. `docs/lumos-toolchain-knowledge/Systems/規格閘.md`
6. `governance/anchor-baseline.json`
7. `scripts/lumos`
8. `scripts/test_lumos.py`
9. `skills/lumos-code-loop/SKILL.md`
10. `skills/lumos-project-notes/commands/06-代碼審與推送.md`

另外讀了這些來源:
- `/tmp/lumos-seat-work/code-選擇點變異加速/r3-共用派工說明.md`
- `templates.md` 的 7.8 節
- `scripts/lumos@744f7b6d6` 的 `_secev_junit_facts` 與 `_run_cmd_expand`

總結:最高嚴重度 clean
