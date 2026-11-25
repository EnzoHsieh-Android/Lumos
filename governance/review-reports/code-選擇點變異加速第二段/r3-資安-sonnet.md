severity: clean

hook 有附上固定席段(`LUMOS-IMPACT` 與固定席節點清單)。我把其中的表態記錄當可反駁的宣稱核對,`py-external na` 成立。補讀後結論不變:這輪沒有能被利用的洞。

## 涵蓋範圍補正
上一版我只讀了 `r3-snapshot.patch` 與 `r3-repair.patch` 重疊的部分,這次補上缺口。我讀了 snapshot 裡以下 9 個檔的 diff。

| 檔 | 補讀方式 |
|---|---|
| `scripts/lumos` | 逐行整段讀完(snapshot 第 552–1213 行) |
| `scripts/test_lumos.py` | 沒有逐行讀。用關鍵字掃新增行(subprocess、os.system、shell=、environ、http、token、secret、rmtree、unlink、絕對路徑、PYTHONPATH、LUMOS_SKIP、eval、exec),並看了函式簽名與關鍵段落 |
| `Systems/guard-kill.md`、`Systems/規格閘.md` | 讀 diff 與 WHY、PITFALL 行 |
| `skills/lumos-project-notes/commands/06-代碼審與推送.md` | 讀完整改動 |
| 計劃 `選擇點變異加速第二段_計劃.md` | 先前讀過重疊部分;這次對 1–551 行(含 PRIOR-ART)用關鍵字掃新增行 |
| 計劃 `改動選擇點都要有需求守住_計劃.md`、`選擇點變異加速_計劃.md`、`選擇點變異覆蓋選測試_計劃.md` | 只用關鍵字掃,沒有逐行讀 |

關鍵字掃出的東西:
- 新增行裡的 URL 都是 PRIOR-ART 與依據表的論文、文件引用。
- 沒有信箱、密鑰、新的下載來源。
- 唯一會讀環境變數的是 `LUMOS_SKIP_CHOICE_MERGE`。這個變數不是新增的,只出現在文件與回退節的描述裡。
- 測試的新增行沒有拼接命令的新路徑。
  - 測試用 `tempfile.mkdtemp(prefix="gctl-ckm-")` 開暫存目錄,收尾用 `_ck_cleanup`。
  - 指令字串是固定的 `_CKM_CMD` 與假的 `run_cmd`(例如 `{python} tests/run.py {method}`),不含外部輸入。

## 三類結果
- ① 提示注入:已看,無。
  - 新進治理帳的欄位有 `merge_kind`、`single_runs`、`merge_unclean`、`merge_off`。
  - 欄位值只來自 `_choice_merge_classify` 的固定字串、固定常數 `_CHOICE_MERGE_TRIPPED` 與整數。
  - 「N 支對不到」那條已由 `_kill_merge_base` 折成「對不到名字」。
  - `_choice_merge_facts` 回的原因也是固定字串。
  - 測試名、檔名、tail 都沒有流進這些欄位。
  - 平台名當字典鍵與印字時,印字有包 `_kill_esc`。
  - 治理帳欄位的型別已登記進 `_GOV_FIELD_TYPES`,型別不合會被跳過。
- ② 讀寫與執行越界:已看,無。
  - 這次沒有新增 subprocess、檔案寫入點、路徑組合或下載。
  - 結果資料夾圍欄 `_choice_merge_results_dir` 仍在,而且在時限門之前就判。
  - 「結果資料夾不在工作樹」現在會明確記原因,不再靜默。
  - 提示裡的 `--max-seconds X` 是 `math.ceil` 算出的整數,不含外來文字。
  - `_kill_merge_failed_first` 只重排 `chunk`,不執行任何外部東西。
- ③ 非刻意一步繞過的守衛:已看,無。
  - Ctrl-C:第一個訊號設 `mg.interrupted` 並收掉合併程序。接著 `_kill_merge_base` 或 `_kill_merge_screen` 丟 `_KillHalt`,停下;被收掉的快篩不交列、不記存活。
  - 總時限到:`hk.between()` 與 `should_stop` 丟 `_KillHalt`,記「時限到」,不印、不放行。
  - 訊號與總時限同時來,最多把分類標成「中斷」,只影響 `merge_off` 欄的標籤,沒有任何路徑因此判出存活。
  - 合併仍然只判存活。先紅順序只改逐支跑的先後,判定還是由單支結果決定。
  - 新增的 `_ran_solo` 在 `--json` 輸出時被列入過濾清單,不外洩內部欄位。
  - 沒有新增 `LUMOS_SKIP_*` 或 `PYTHONPATH` 的讀取點。
  - 單一壞法也合併時,`len(uniq) < 2` 的判斷排在時限門前,不會因此意外開合併。
- 表態記錄:`py-external na` 成立。這次沒有新增外呼,只有既有的本機 Gradle 與 ast-grep 子程序。

這份報告沒有 finding。

## 讀過的檔
- `/Users/enzo/harness/lumos-choice-speed2/governance/review-reports/code-選擇點變異加速第二段/r3-snapshot.patch`:讀完 `scripts/lumos`、`Systems/guard-kill.md`、`Systems/規格閘.md`、`06-代碼審與推送.md` 的 diff;`scripts/test_lumos.py` 與四份計劃見上表。
- `/Users/enzo/harness/lumos-choice-speed2/governance/review-reports/code-選擇點變異加速第二段/r3-repair.patch`:讀完。
- `/Users/enzo/harness/lumos-choice-speed2/scripts/lumos`:讀真代碼,範圍是 `_kill_merge_iter`、`_KillMerge`、`_choice_merge_classify`、`_KillHalt` 各呼叫點。
