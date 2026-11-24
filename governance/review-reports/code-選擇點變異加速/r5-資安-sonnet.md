severity: minor

資安-sonnet 對 r5-snapshot.patch(2906 行)全部讀完,只看〈工具鏈三類〉。**能被利用的洞沒有找到。** 只留一條治理流程的疑慮,標推論、不擋。

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/9715c2af…json.warming` 在我查時不存在,沒有要處理的鎖。我沒建 worktree,也沒建臨時目錄,所以沒有東西要移除。

## Findings

### 1. 測試檔錨點這次靠「睡前事先授權」代簽,跟前幾次逐次「簽」不同(推論)
severity: minor
blocking: 否
引句:「"note": "使用者 2026-11-24 睡前事先授權」
file: `governance/anchor-baseline.json:539`
攻擊路徑(只填得出推論):
- 誰:代簽的 AI 編排者。
- 從哪:`anchor approve`,更新 `scripts/test_lumos.py` 的雜湊。
- 送什麼:note 裡引一段先前的概括授權,不是對這一筆改動的當下回覆。
- 拿到什麼:測試檔錨點被重設,沒有使用者對這一筆的明確「簽」。

查證:
- 前五筆錨點提交的 note 都寫「使用者在對話中核可,原話「簽」」。
- 本輪 f14bd5881 改成「選項原話「准再一輪就停」……代簽測試檔」,是概括授權。
- 本輪簽的內容是補測試案例,note 寫「沒有放寬既有檢查」。我沒有在簽核內容裡找到放寬的證據。
- 使用者全域記憶的規定是每次都要那一次的簽。這條是否算數,我無法從 patch 判斷,⚠ 交編排者核對對話原文。

重現:
```
git -C /Users/enzo/harness/lumos-choice-speed log --format='%h %s' -6 -- governance/anchor-baseline.json
git -C /Users/enzo/harness/lumos-choice-speed show 100d3851c:governance/anchor-baseline.json | grep '"note"'
git -C /Users/enzo/harness/lumos-choice-speed show f14bd5881:governance/anchor-baseline.json | grep '"note"'
```
前一版是「簽」;修後版是事先授權。
歸因:未判定。這不是程式行為,沒有兩版測試結果可比;只確認 note 措辭前後不同。

## 已驗主張(逐類)

**①提示注入:已看,無。**
- 新增的輸出都過 `_kill_esc` 或固定字串。例如 `⚠ {_kill_esc(c.plat)}:{_CHOICE_MERGE_BASE_WHY.get(why, why)}`,`why` 只來自 `_choice_merge_classify` 的固定原因字串。
- JUnit 結果檔內容不會原文進派工詞、hook 或帳。快篩通過時存活列只帶基準 tail 與遮過路徑的 excerpt。
- 結果檔內文只拿來判狀態與名稱。
- `--only` 提示的檔名走 `_kill_esc`。

**②讀寫與執行越界:已看,無可利用的洞。**
- 結果資料夾:`_choice_merge_results_dir` 先 `realpath`,再要求在工作樹底下,否則回 None 且整組不合併。
  引句:「real if real.startswith(os.path.realpath(str(wt)) + os.sep) else None」
- 刪除範圍:`shutil.rmtree(rdir, ignore_errors=True)` 只刪過這道圍欄的真實路徑,圍欄只能落在拋棄式工作樹內。`t_choice_kill_merge_results_dir_fence` 有樹外哨兵檔的 e2e 驗證(`-p` 絕對路徑)。
- 兩個攻擊面:`-p` 絕對路徑與 `..` 被圍欄擋下;模組各段經 `_SR_MODULE_PART` 驗證,不含 `.` 與 `..`。
- 套壞法寫檔:`target.startswith(c.wt_real + os.sep)` 與原逐支路徑同圍欄。
- 結果檔符號連結(`TEST-*.xml` 指向樹外檔):只會被當 XML 解析,失敗回固定字串「結果檔讀不出來」,內容不回顯、不外洩。
- 指令組裝:全部測試名先過 `_test_name_ok` 與 `_name_collision_reason`。每段交跟逐支同一支 `_run_cmd_expand`,沒有第二套切詞或引號。長度上限 32768 位元組。
- 其餘:沒有新增下載、網址、密鑰、信箱或全域設定寫入。
- 同類殘餘風險:測試程序本身就能執行 repo 控制的碼,屬既有慣例。

**③非刻意一步繞過守衛:已看,無。**
- 環境變數只能關掉優化,而且只認 1。
  引句:「merge = not no_merge and os.environ.get("LUMOS_SKIP_CHOICE_MERGE") != "1"」
- 合併永遠不判殺掉,只會多記存活。存活在推送閘要人處置,所以殘留環境變數無法放行壞程式。
- Ctrl-C 或 SIGTERM:`on_first` 當場收合併程序。`_kill_merge_screen` 在 `mg.interrupted` 時丟 `_KillHalt`,該壞法不交列、不記帳。
- 假存活佔回報上限名額,計劃〈實務隱患〉已承認,屬縱深,不是繞過。
- 時限、寫入後修改時間沒錯開、基準非綠,三種情形都退回逐支或記 abort 或弱證據,不會放寬。

## 三問(修補鏡頭,資安面)
1. **原問題的修復效果**:資安面沒有被指定的原問題。我只驗了 r5 修補新增的路徑(重估、保底 1 秒、接線),沒發現新攻擊面。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:合併基準與快篩的逾時都有 `max(remaining, 1.0)` 保底,不會出現負數逾時。`merge=None` 的呼叫端(人裁 `situation-rule`、`guard kill`)路徑不變,由測試 `S12 merge=None` 驗。
3. **同一案例修前後結果**:本席沒有跑兩版測試,資安面也沒有可比案例。以上只靠讀碼,未做行為驗證;除錨點 note 比對外,這點未判定。

## 讀過的檔
- `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/選擇點變異平行_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
- `docs/lumos-toolchain-knowledge/Systems/規格閘.md`
- `governance/anchor-baseline.json`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `skills/lumos-code-loop/SKILL.md`
- `skills/lumos-project-notes/commands/06-代碼審與推送.md`

另外讀了 r5 共用派工說明、`templates.md` 第 442 行起的〈7.8 資安席派工〉,以及 `lens.txt` 的固定席摘要。

總結:最高嚴重度 minor
