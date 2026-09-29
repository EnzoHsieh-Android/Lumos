severity: clean

# 併發回滾-sonnet 第 1 輪報告(鏡頭:併發、資源與回滾)

沒有 finding。逐項查證如下(皆讀真代碼,並在臨時 git repo 跑了 `git show -z --name-only --diff-filter=AR --format=` 的邊界:根提交、非快轉合併裡的新增檔、整個目錄改名,輸出都符合 `_drift_c4_same_commit` 的預期)。

## 查證摘要
1. git 失敗/逾時/中斷:`_nodehome_git` 對 OSError、逾時(`_lens_git` 20 秒)、rc!=0 一律回 None,`_drift_c4_same_commit` 回 None,`_drift_c4_print_dirs` 印「同提交:查不到(git 失敗或沒有)」,不是「沒有」;git 成功但沒加卷證目錄時回 [],不印那句,清單只剩計劃名比對或「查不到」。shallow 或 `_plan_first_commit` 逾時時 sha 為 None,範本寫 `<sha>`,`set` 會擋。沒有把「查不到」印成肯定結論的路徑。
2. 刪除守衛寫帳失敗:`_delguard_log_result`、`_delguard_log_degraded` 的寫帳都在 try/except Exception 裡,`_delguard_vendored_note` 也在 try 內;寫帳失敗不改守衛回傳(恆 rc0)、不改印出的提醒。`vend` 在解析前就出例外時 `locals().get("vend")` 為 None,`_delguard_vendored_note` 對 None 回空字串,不出錯。
3. 新舊版相容:`vendored-skip=` 只是治理事件 note 尾端的自由文字,scripts/lumos 內沒有任何解析 delguard note 的程式(grep 過 secs=、hits=、reason=),舊版讀得過。c3 的 `--reason` 只是多接一段「;理由:…」進正文,舊版當一般正文;舊版 CLI 遇到 `--reason` 會回「不收」,只影響新參數本身。舊版 set 不擋 `<卷證>`、`<sha>`,不會讀壞任何東西。
4. 照〈回退〉`git revert --no-commit`:程式、測試、筆記、anchor-baseline 同一提交一起退;帳本檔按計劃留現況,`vendored-skip=` 那幾行留在 append-only 帳裡無讀取者;c3 理由行留在筆記是一般正文。〈回退〉五項清單與 diff 的改動面一一對得上。
5. 大 repo 的 git 次數:c4 是單一發現、單次呼叫,新增一次 `git show`(上限 20 秒),合計 shallow 判斷 + `log` + `show` 三次,沒有每個發現多跑的迴圈(`_drift_c4_evidence` 只由 `_drift_c4_print` 呼叫一次)。刪除守衛新增零次 git,只多一次 `_is_toolchain_repo` 的檔案存在判斷;`_delguard_parse_diff` 拆函式後每個 `diff --git` 行才算路徑旗標,`-` 行 token 用預編譯正則,不比原本慢。
6. `_delguard_parse_diff` 拆分前後行為等價:逐分支對照(diff 頭、Binary、非 +/- 行、vault 行、排除檔、`.md`、`-` 行收 token),控制流由 continue 改 elif 鏈,判定條件相同。

## 圖譜鏡頭逐條判定
- 存量漂移守衛:不破壞。c4/c3/c1 只改證據頁與訊息,判定、修復帳、乾淨檢查(指紋認修復帳最後一筆)沒動;c3 的 `--reason` 沿用 c2 的長度/單行/佔位字檢查。
- bound-tests-gate(INVARIANT):不影響。沒動 code-loop check 對綁定測試的判定流程,只有測試檔增減並重簽 anchor-baseline。
- guard-kill(兩條 INVARIANT:rc 優先序、--json 純度):不影響。改的只是 `_guard_settle_missing_say` 的訊息與回傳(原本無回傳),兩個呼叫端不使用 rc 或 stdout JSON。
- 授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT、檔頭 SPDX):不影響。`_VENDORED_ALL` 只被讀、沒被改,scripts/lumos 檔頭沒動。
- 測試假綠形態(還原翻紅釘要配前置斷言):不影響本輪程式路徑;新測試是否附前置斷言不在併發回滾鏡頭內。
- lumos-cli-read、lumos-cli-lifecycle、design-loop:不影響。search、re-inject、處置閘都沒碰。

最高等級:clean
