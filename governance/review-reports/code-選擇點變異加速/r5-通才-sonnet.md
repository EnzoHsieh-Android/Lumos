severity: clean

**範圍與前提**
- 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/9715c2af…json.warming` 不存在。我沒動它,照派工詞審查。
- 修補差異 `100d3851..f14bd5881` 對 `scripts/lumos`(產品碼)是 0 行,只動 `scripts/test_lumos.py`、`guard-kill.md`、`anchor-baseline.json` 和治理帳。
- 因為產品碼沒變,「修前、修後同一案例」比的是測試對產品碼的抓力,不是產品行為前後差。修前的 `100d385` 沒有新斷言,所以不另開 before worktree。

**通才八角度結果**
1. 逐行:新增的三組斷言都讀過所在函式。耗時 1、5、1 秒剩 3.0:第一支量完門檻 3.0,不小於,照量;第二支量完平均 3、門檻 4.5 大於 3,收手,恰好量 2 支,與測試期望一致。剩餘時限 -5:`cap = min(full, max(remaining, 1.0))` 得 1.0,與斷言一致。
2. 被刪掉的行為:`t_choice_kill_merge_cap_wiring` 重寫成 `run()` 輔助函式,原本三條斷言(逾時值 ≤ 60、呼叫三次)都還在,清理照舊在 finally。沒有少掉守衛。
3. 跨檔:呼叫端 `_kill_merge_base`、`_kill_merge_singles`、`_kill_merge_screen` 的程式碼未改,沒有新的前提。
4. 重用:新測試沿用 `_ckm_inproc`、`_ckm_repo`、`_ck_cleanup`,沒有重做既有東西。
5. 簡化、6. 效率:沒有具體失敗場景,不報。
7. 修的深度:這輪是補測試,不是在症狀上貼補丁。
8. 慣例:`anchor-baseline.json` 的 test_lumos.py 雜湊與 HEAD 實際檔相符(`shasum` 為 `cd75d7dc…`)。簽章 note 寫的是「睡前事先授權」,與 `overnight-2026-11-24-delegation.md` 記的範圍(只適用這個迴圈的 r5 這一次)一致。

**已驗主張**

主張一:新增的耗時 1、5、1 秒案例能分出「平均」和其他估法。

引句:「check("r4 通才 #1 耗時 1、5、1 秒、剩 3.0 秒 → 量了 2 支就收手(平均 3,不是最小值或第一支的 1)」

- input:`took = {a: 1.0, b: 5.0, c: 1.0}`,剩 3.0
- expected:`got is False`、量了 2 支
- 兩版:修前沒有這條斷言,無法比較。修後 `python3.14 scripts/test_lumos.py -k choice_kill_merge_` 兩次都是 `140 passed, 0 failed`。
- 變異(我把 `sum(measured) / len(measured) * left` 換掉,在 after worktree 做):
  - 換成 `min(measured)`:紅,回 `True`、量了 3 支,正是這條新斷言抓到。
  - 換成 `measured[-1]`:紅,被原本的 1、3、1 案抓到。
  - 換成 `max(measured)`:紅,被原本的 1、3、1 案抓到。
- 結論:新舊兩組合起來,平均和最小值、最後一筆、最大值都分得出來。

主張二:剩餘時限為負時,單支基準與合併基準收到的上限都是保底 1 秒。

引句:「check("r4 邊界 #3 剩下時限 -5 秒 → 第一支單支基準收到的上限是保底 1 秒", bool(caps) and caps[0] == 1.0, str(caps))」

引句:「check("r4 邊界 #2 量完單支基準後剩下時限 -5 秒 → 合併基準收到的上限是保底 1 秒", bool(seen) and seen[0] == 1.0, str(seen))」

- 變異:把單支那處的 `max(mg.remaining(), 1.0)` 拿掉,`budget_edge` 紅,收到 `-5.0`。把合併基準那處的保底拿掉,`cap_wiring` 紅,收到 `[-5.0]`。兩處各自被獨立抓到。
- 修前沒有這兩條斷言,無法比較。

主張三:`--json` 輸出的存活列不帶 `judged`。

引句:「check("r4 整合 #1 合併開著時 --json 輸出的存活列不帶 judged(判法只在收尾算一份)",」

- 變異:在 `_kill_merge_emit` 的 survived 列加 `"judged": "merged"`,`cap_wiring` 紅,輸出列裡有 `'judged': 'merged'`。
- 合併確實走了:同一輪 `seen` 斷言要求三次帶合併標記的呼叫,所以這條不是靠逐支流程湊出來的。

**回答三問**
- ①原問題的修復效果:r4 提的三個測試抓力缺口(平均 vs 最小值、保底 1 秒、`judged` 洩漏)都有翻紅證據,見上面三條主張。
- ②正常、錯誤與相鄰路徑:產品碼未改。原有 3 組 cap_wiring 斷言和 r3 的 1、3、1 秒案例、`budget_reestimate` 都照常通過。
- ③新發現的同一案例修前修後:沒有新發現。

**未驗範圍**
- 整套 `test_lumos.py` 不在對話裡跑,依規定留給推送前的閘與 CI。
- `docs/.governance-log.jsonl` 的內容沒審。
- 小提醒(不算 finding):`guard-kill.md` 的 `PITFALL:快篩逾時上限…` 那行,出處沒補 r4 邊界 #2,但測試註解已引它。沒有具體失敗場景,不報。

臨時目錄:我建的 worktree 已用 `git worktree remove --force` 移除,`/tmp/lumos-seat-work/code-選擇點變異加速/通才-sonnet/` 已清空刪除。

總結:最高嚴重度 clean
