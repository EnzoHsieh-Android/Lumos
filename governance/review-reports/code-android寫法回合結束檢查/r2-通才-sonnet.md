severity: major

第一輪通才席 F1 到 F6 逐條核對如下。

- F1(放行指令被截成 160 字):已修好。`_waive_ok` 不再改字元也不截斷。我用 1060 字的放行指令實跑 `_reason`,整條原樣印出。
- F2(整段硬截 1490 字):已修好。`_reason` 改成逐條累加,放不下就停,結尾「另 N 條」那行保證留得下。
- F3(決策列在挑到時就落標記):作者選擇接受並在 docstring 與筆記寫明,沒有改行為,可以接受。
- F4(Popen 到登記之間收到 SIGTERM):已修好。`spawning` 與 `pending` 兩個旗標先記下訊號,登記完補跑 `_on_sigterm`。我逐一推演各個時間點,沒找到漏洞。
- F5(死碼 `_inner_budget` 包裝):已修好。它被換成逐字複本,是真的有人呼叫的函式。
- F6(同一份編輯內容取兩次):已修好,改成 `extract_delta_texts` 一次取段。

此外確認 `_trusted_lumos` 與 `_outer_budget` 到 `_inner_budget` 兩段在 `check-graph-sync.py`、`stop-lint-hook.py`、`impact-hook.py` 三支裡逐字相同,三支的 md5 一致。

F1
severity: major
blocking: 是
標題:lint-new 自己的內部失敗(git 算不出工作樹、cat-file 格式對不上、過濾器關不掉)回 rc3 但 `undone` 是空的,`_unchecked_kind` 回 None,鉤子把它記成 ok,等於 r1 邊界席 F2 的「失敗被記成綠」在新路徑上又發生。
引句:「    刻意不查(合併中、宣告檔不乾淨、超過上限、不在白名單)回 None(鉤子照設計做完了判斷,記 ok)。」
引句:「    if data.get("status") == "env-unavailable" or "env" in kinds:」
失敗情境:`_lint_new_wt_json` 回傳的欄位裡,`undone` 只裝工具命令層級的失敗(`budget`、`too-long`、`env`、`guard`)。
下列三條路徑都是 `status="not-checked"`、rc3,而且 `undone` 為空:
- `_lint_wt_unready` 因 `_lint_wt_filter_args` 回 None(git config 讀不出或過濾器名字收不了)。
- `_lint_wt_pairs` 的 `err="git 算不出工作樹上的改動"`。
- `_lint_wt_blobs` 因 git 失敗或輸出對不上格式而回 None。
鉤子看到 rc3、`kinds` 為空、status 不是 env-unavailable,就當作「刻意不查」。於是每回合都 git 失敗的專案,在 `lumos enforcement` 上永遠顯示 ok。
計劃筆記自己寫「git 失敗整次 rc3」,同時寫「刻意不查的 rc3 照記 ok」,兩句放在一起互相矛盾。
佐證 file: `scripts/lumos:40479`(`why = _lint_wt_unready(repo_root)` 之後 `out["status"], out["reason"] = "not-checked", why`)與 `scripts/lumos:40487`(`err` 分支)。
修法:lint-new 在這幾條路徑往 `undone` 補一筆 `{"kind":"git",...}`,鉤子把它歸 error;或在 JSON 加一個「刻意/非刻意」欄位。

F2
severity: minor
blocking: 否
標題:`check-graph-sync.py` 的 `import time` 成了無用匯入。
引句:「+    return _claim_mark(mp.parent, mp.name)」
失敗情境:佔名額的 `os.write(... time.time() ...)` 搬進 `_hookshared._claim_mark` 後,`check-graph-sync.py` 沒有任何地方再用 `time`。
我實跑 `ruff check --select F` 報 F401(`check-graph-sync.py:33`)。repo 目前沒有 ruff 設定,全域推送前掛鉤不會擋,但之後有人加設定就會當場紅。
修法:刪掉 `import time`。

F3
severity: minor
blocking: 否
標題:`extract_delta_text` 的 `new_only` 參數在正式路徑已經沒人用,留下兩套取段入口。
引句:「+def extract_delta_text(payload: dict, cap_bytes: int = DELTA_TEXT_CAP, new_only: bool = False):」
失敗情境:`.kt` 走 `extract_delta_texts`,其他副檔名走 `extract_delta_text(payload)` 且不帶 `new_only`。我搜過 `scripts/hooks` 與 `scripts/lumos`,正式程式裡沒有任何呼叫帶 `new_only=True`。
這個參數與 docstring 裡「new_only=True 只取…」的說明成了只給測試用的分支。日後有人改取段規則,要同時顧三個函式(`_delta_parts`、`extract_delta_text`、`extract_delta_texts`)。
修法:拿掉 `new_only`,新內容一律走 `extract_delta_texts`;測試改呼叫它。

總結:最嚴重是 lint-new 自身的 git 失敗被記成 ok(F1),會擋 1 條。

我在 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/通才-sonnet/` 放過一支驗證用腳本,已刪除。
