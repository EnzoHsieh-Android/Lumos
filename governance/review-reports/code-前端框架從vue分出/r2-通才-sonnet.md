severity: major

通才鏡頭,八個角度都走過。我在 `/tmp/lumos-seat-work/code-前端框架從vue分出/通才-sonnet/after/` 解開修後 b9ff5494 的 `scripts/`,對 lumos 做了十多個故障變體,再跑對應的測試子集。

**已驗的主張(變體都翻紅)**
- 虛擬時鐘那支測試(`t_review_roles_classify_loop_respects_budget`)抓得到錯。拿掉迴圈預算檢查,結果是 60 支全判;只標 timed_out 不清 blobs,結果是 60 且 timed_out=True。兩種都紅,不靠牆鐘。
- 這幾組變體都翻紅:
  - `min_lines` 的基準改回數增刪行
  - 張力候選的 `applicable_ids` 傳 None,或過濾關掉
  - 不可逆掃描改回舊副本樣式
  - 建置檔判定的記憶拿掉
  - 不剝建置檔註解
  - `_uses_vitest` 的 jest 分支拿掉
- 三支被拿掉的小函式(`_stack_drop_excluded`、`_tension_drop_excluded`、`_stack_perf_questions`)在修後版本沒有任何殘留引用。它們的期望已搬到 S22/S23/S27/S32/S33 這幾支。
- 新測試單支執行約 1 到 6 秒,其中約 1 秒是啟動;張力那組 15 支共 32 秒。效率上沒有可報的問題。
- 受時間影響的只剩 S35 和 13 萬空行兩支,門檻 3 秒,對照的壞版本要 45 秒以上,不貼著機器快慢。

**發現**

1. 跑過證據樣式的 200 字上限沒有測試守著
severity: major
   - blocking: 是
   - 歸因:有證據的原有漏查。修前版本同樣抓不到,不是這次修補造成的。
   - 問題:S35 的輸入是「Tests: 」接 8 萬個 9。這個輸入只能分辨出最初的 `Tests:.*?[1-9]\d*\s+passed`,那個版本我量到 45.5 秒。
   - 現行樣式有兩道防線:`(?<![0-9])` 和 `{0,200}?`。各自單獨拿掉,S35 都照綠,因為只剩一道就夠處理這個輸入。
   - 具體例:
     - 把 `{0,200}` 改成 `*`,即 `Tests\b[^\n]*?(?<![0-9])`。
     - 在 after 副本跑 `python3.14 scripts/test_lumos.py -k ran_evidence`,結果 `14 passed, 0 failed`。
     - 同一條樣式對 `"Tests 1 " * 30000` 這一行,上限版 0.14 秒,無上限版 81.27 秒。
     - 推送會卡在這條樣式上,這正是樣式註解 ② 說要擋的事。
   - 修法:在測試補一行 `"Tests 1 " * 30000`(不含 passed)的斷言。
   - 引句:「check("S35:8 萬字長行 3 秒內回沒跑過", ok is False and dt < 3.0, f"{ok} {dt:.2f}s")」

2. 整批讀取總量上限只比有沒有傳參數
severity: major
   - blocking: 是
   - 歸因:有證據的修補新增、沒有行為證據。上限常數和這支測試都是修補新加的。
   - 問題:`t_review_roles_batch_total_bytes_capped` 攔下 `_nodehome_cat_blobs_capped` 的呼叫,只看 `max_total_bytes` 是正整數。16MB 這個數字有沒有生效,沒有任何斷言。
   - 具體例:
     - 把 `_ROLE_MAX_TOTAL_BYTES = 16 * 1024 * 1024` 改成 `10 ** 15`。
     - 跑 `-k batch_total_bytes`,結果 `1 passed, 0 failed`。
     - 把整批上限實質拿掉,記憶體保護就沒了,測試仍綠。
   - 修法:把常數 monkeypatch 成很小的值,斷言超過總量的建置檔回 None、角色退回判不出。
   - 引句:「check("資3:批次讀取帶 max_total_bytes", isinstance(seen.get("max_total_bytes"), int) and seen["max_total_bytes"] > 0, str(seen))」

3. 工作樹讀檔的兩個上限接線沒有測試
severity: minor
   - blocking: 否
   - 歸因:有證據的原有漏查。舊的 `_kt_worktree_text` 也沒有對應測試。
   - 問題:`_worktree_text` 自己的 `max_bytes` 和 `head` 有單元測試,但 `_kt_flavor` 與 `_kt_role` 傳進去的那兩個值沒有。
   - 具體例:
     - 把 `_kt_flavor` 的 `content = _worktree_text(repo_root, file_rel, head=_KT_HEAD_BYTES)` 拿掉 `head=`,`-k kt_` 29 條仍全綠。
     - 把 `_kt_flavor` 裡建置檔那個 lambda 的 `max_bytes=_ROLE_MAX_BYTES` 拿掉,`-k kt_` 29 條仍全綠。
     - `_worktree_text` 的註解說「總量有界」靠這兩個值,但沒有任何測試證實。
   - 引句:「content = _worktree_text(repo_root, file_rel, head=_KT_HEAD_BYTES)」

4. eslint 檔名同步守衛只擋一個方向
severity: minor
   - blocking: 否
   - 歸因:有證據的修補新增、單向。
   - 問題:`t_eslint_config_names_in_lint_globs` 只驗偵測表的檔名都在 `_LINT_CONFIG_GLOBS` 裡。偵測表自己少了檔名,測試照綠。
   - 具體例:
     - 把 `_ESLINT_FLAT_CONFIGS` 的副檔名清單砍成 `("js","mjs","cjs")`。
     - 跑 `-k eslint`,結果 `14 passed, 0 failed`。
     - 只有 `eslint.config.mts` 或 `.cts` 的專案,`lumos init` 和 doctor 就認不得,卻沒有測試翻紅。doctor 的測試只用了 `.js` 和 `.eslintrc.json`。
   - 引句:「check("架5:偵測表的每個 eslint 檔名都被搬設定檔的名單認得", not miss, str(miss))」

5. S35 的 docstring 跟斷言不一致
severity: minor
   - blocking: 否
   - 歸因:有證據的修補造成。修補只改了 `big` 和兩條斷言,沒改 docstring。
   - 問題:docstring 還寫「4 萬個數字:1 秒內」,現在是 8 萬字、3 秒。「舊樣式實測 11 秒」那句也過期。我實測原始樣式 8 萬字是 45.5 秒,不是 11 秒。
   - 引句:「4 萬個數字:1 秒內回沒跑過(舊樣式中段不限長,實測 11 秒)」

6. 清理類的小項
severity: minor
   - blocking: 否
   - `_node_pkg_text` 現在只轉呼叫 `_worktree_text`,唯一呼叫者是 `_node_flavor` 裡的一個 lambda,可以直接內聯。
   - 引句:「return _worktree_text(repo_root, rel)」
   - `t_stack_android_only_inside_applicability` 與 `t_worktree_text_shared_reader` 各有一條 `not hasattr(m, ...)` 的結構斷言,只證明舊名字不在,不是行為驗證。同一支測試裡已有行為斷言,所以不單獨升級。

**三問的回答**
- ① 原問題的修復效果:時鐘、空行回溯、跨行、`min_lines`、不可逆掃描共用判定,這幾項我用故障變體各翻紅一次,有行為證據。「跑過證據」的二次方回溯只證明了舊的完整版,見發現 1。整批總量上限沒有行為證據,見發現 2。
- ② 修補處的相鄰路徑:`_uses_vitest` 的新舊分支、`_stack_applicability` 的 `exclude` 與 `added_by_stack`、張力候選的 `applicable_ids`,正常、錯誤、相鄰三條路都有紅綠證據。工作樹讀檔的上限接線沒有,見發現 3。
- ③ 同一案例修前修後:發現 1 的原版樣式修前也抓不到(修前的 `{0,200}` 加 `\b` 版,拿掉上限 40k 量到 0.0 秒)。其他發現的修前行為我沒有逐一跑,標未判定。

**未驗範圍**
- 沒跑全套。
- 沒驗圖譜固定席那幾個節點宣稱的行為。這份 diff 沒碰 search 排除 superseded、guard kill、re-inject 和 design-loop 處置閘。
- 沒驗文件那半的 r2-repair-docs.patch。

臨時目錄 `/tmp/lumos-seat-work/code-前端框架從vue分出/通才-sonnet/` 還在,請編排者收貨後刪。

最嚴重 severity:major,blocking 共 2 條。
