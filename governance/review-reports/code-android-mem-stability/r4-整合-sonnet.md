severity: major

整合席報告(合約與圖譜一致)。審材是 r4-pkg-docs.patch,修補差異是 r4-repair-docs.patch(f0d41453 到 5fc4e715)。我在 `/tmp/lumos-seat-work/code-android-mem-stability/整合-sonnet/wt` 取出 5fc4e715 做了還原實驗,實驗完已用 `git worktree remove` 刪掉。

## Finding

### F1 計劃 S23 新寫的「ps 失敗」句子沒綁到會守它的測試
severity: major
blocking: 是

引句:「查 ps 失敗時不把好的追蹤檔當成提早結束」
引句:「t_android_memstab_collect_cleanup,t_android_memstab_collect_interrupt_windows,t_android_memstab_collect_signals,t_android_memstab_collect_start_window,t_android_memstab_collect_heap_timeout」

- 場景:S23 新增了「查 ps 失敗時不把好的追蹤檔當成提早結束」這句,但 `[test:]` 清單裡沒有唯一守它的 `t_android_memstab_collect_record_alive`。
- 證據一:`scripts/lumos spec-trace` 顯示 S23 綁了、懸空 0,看起來全綠。
- 證據二:我在臨時工作樹把 `perfetto_alive` 還原成舊的 `ps -A -o PID,NAME | grep -w <pid>`,也就是撤掉 r3 的修法。結果 S23 綁的五支測試全綠,cleanup 10、interrupt_windows 8、signals 11、start_window 2、heap_timeout 3,都是 0 failed。
- 證據三:同一個還原下,只有未綁進任何 S 條款的 `t_android_memstab_collect_record_alive` 紅,訊息是「第一次 ps 失敗 → 照樣停錄製、cycle_trace ok」,實際是 `failed` 並說「到了上限」。
- 所以這條條款名義上綁了,實際沒有守衛。
- 兩版對照:f0d41453 的 S23 沒有這句,是 r4 修補新寫的句子加上漏綁。
- 歸因:有證據的修復回歸(文件側)。
- 修法:在 S23 的 `[test:]` 補上 `t_android_memstab_collect_record_alive`。

### F2 事故筆記把根因改成另一個錯的函式名
severity: minor
blocking: 否

引句:「`lumos dispatch-lens` 在 `cmd_dispatch_lens` 裡用」

- 場景:修補把 `cmd` 改成 `cmd_dispatch_lens`。
- 程式實況:`cmd_dispatch_lens`(`scripts/lumos:60556`)只是清鎖的外殼。真正呼叫 `_codeloop_read_dispositions(root, _codeloop_git_branch(root), marker_only=True)` 的是 `_dispatch_lens_graph`(`scripts/lumos:60691` 起,呼叫在 60729)。f0d41453 的同一呼叫在第 60698 行,也在同一個函式。
- 三個月後的人照名字搜會找錯地方。
- 另外,引文裡的 `…` 把 `marker_only=True` 吃掉了。這個旗標正是「只讀本機 marker」的行為,跟「什麼條件算修好」要改的地方有關。
- 歸因:有證據的修復回歸(修成另一個錯的名字)。

### F3 計劃的設計正文沒跟 S23 與 skill 對齊
severity: minor
blocking: 否

引句:「被 SIGTERM 或 Ctrl-C 中斷時回 2 並印「擋下:」」
引句:「直接進 L3,不先走 L1、L2」

- 設計第 2 點寫只有 SIGTERM 與 Ctrl-C 會中斷。程式現在接 SIGTERM、SIGHUP、SIGQUIT 加 Ctrl-C:`scripts/templates/android-stability-collect.sh:36` 的 `INTERRUPTS`。S23 已改,正文沒改。
- 設計第 5 點寫記憶體類沒過直接進 L3,沒提 `stability.test_data` 這道門。skill 的 L0 第 8 步與逐層診斷 S6 都明寫「沒宣告就停在 L0 並記 `[GAP] L3 未授權`」。
- 同一份「單源」計劃跟下游文件對不上。
- 歸因:有證據的原有漏查。第 5 點的缺口在 S6 與 skill 修改時就存在,SIGHUP 那段是 r4 修補後新漂移。

### F4 「test_data 宣告」在三處寫法不一致,漏了 value:false
severity: minor
blocking: 否

引句:「專案沒有 `stability.test_data` 宣告時不往下」
引句:「`test_data` 不寫就不錄 Java 快照」

- 計劃 S15 與逐層診斷 S6 都明講「不寫,或 value 是 false」都不錄。
- skill L0 第 8 步與 reference.md 只寫「沒有宣告」「不寫」。
- 場景:專案寫了 `{"value": false, ...}`。照第 8 步字面,有宣告所以往下進 L3。但 L3 標題(value 是 true 才做)與程式都說不錄。
- 接手的人會被同一份 skill 裡兩句話指到相反方向。
- 歸因:有證據的修復回歸。第 8 步與 L3 標題是 r4 同一輪寫的,兩處用了不同的條件。

### F5 逐層診斷 S6 的人驗證據沒涵蓋新寫的路徑
severity: minor
blocking: 否

引句:「從 L0 直達 L3 的路徑停在 L0」

- 新句子聲稱「記憶體類 check 在 L0 就因沒授權停下並記 GAP」。
- 條款末尾掛的人驗證據,仍是 2026-10-23 s05 那次「L2 往下沒授權停在 L2」。
- 條款自己也承認:`stability.test_data` 這個寫法 10-24 才有,有宣告的那一側靠實驗室驗收。
- 沒宣告的 L0 直接停這一側,沒有任何人跑過。
- `spec-trace` 對 S6 顯示「靠人」並通過,但證據和這句話對不上。
- 歸因:未判定。我沒有可靠的方法重跑人驗,只能指出證據範圍不符。

### F6 實機驗收紀錄的有效範圍沒追上 r3 的裝置端新指令
severity: minor
blocking: 否

引句:「代碼審 r1、r2 的修補之後只用假工具測試驗過,實機沒重跑」

- r3 之後多了幾個裝置端行為:`pkill -TERM -f <追蹤檔路徑>`、不在裝置上 grep 的 `ps -A -o PID,NAME`、`unreachable` 失敗訊息改寫。
- 這份 Verification 的 `valid_under` 只寫到 r1、r2。
- `pkill -f` 只在測試的假 adb 裡驗過,假 adb 對 `pkill` 一律回成功。
- 計劃的 REVISIT 沒有一條要求在實機確認它。2027-04-30 那條只提到 `dumpsys` 與崩潰讀取。
- 場景:實機的 toybox `pkill -f` 若行為不同,錄製開起來但 pid 沒回來時被中斷,裝置上的錄製不會停。
- 歸因:有證據的原有漏查,是 r3 修補後新增的未驗範圍。

### F7 舊寫法門檻條目也開始擋 decided_by 佔位,驗收門檻計劃 S5 沒記
severity: minor
blocking: 否

引句:「decided_by 寫成 <裁定的人> 這種佔位也擋」
引句:「寫了 `check` 的條目改驗那種檢查自己的欄位」

- `_macrobench_signed_err` 同時套用在舊寫法條目(`_macrobench_threshold_item_err` 現在回傳它)。
- 舊寫法條目多了一個擋下條件:`decided_by` 空白或佔位。
- Macrobenchmark驗收門檻_計劃 S5 這次只改了 `check` 條目那半句,沒寫 `decided_by` 的新規則。
- 綁定的 `t_macrobench_threshold_bad_file` 也沒有佔位案例。
- 守衛靠 `t_android_memstab_check_fields_strict` 的舊寫法案例,在另一份計劃的條款 S25 下。
- 歸因:有證據的修復回歸,屬輕微的條款與測試歸屬錯位。

最嚴重 severity:major,blocking 共 1 條(F1)。

## 條款綁定核對(S1–S27)

- `scripts/lumos spec-trace 'Projects/Android記憶體與穩定性驗收_計劃'` 的結果是 27 條,靠人 3(S17–S19)、綁了 24、懸空 0。
- 我逐條核對 r4 新增或改動的條款,測試都真的存在,斷言也對得上句子。
- 對得上:
  - S7、S22 的 `logcat_scope` 三條路。
  - S20 的負數、`stability_unjudged` 的 `--json`、孤立代理字元、40 類別警語。
  - S25 的佔位。
  - S27 的 `result_fields`。
  - S24 的 `.gitignore` 只寫 `*.json`、同名 `json.py`、`PYTHONPATH`、同 run-id、`ps` 只認自己 pid。
- 對不上的只有 F1。
- S24 的 Big5 句子:
  - 在有 `zh_TW.Big5` 的機器上有殺傷力。我把 wrapper 改成 `python3 -I` 後,`t_android_memstab_collect_edges` 紅(18 passed、1 failed)。
  - CI 是 `ubuntu-latest`,多半沒有該語系,只印略過,REVISIT 2026-12-31 已誠實記下。
  - 結論:這條只在作者本機成立,CI 驗不到。
- 我另外跑了 `scripts/lumos lint` 檢查改到的 7 篇筆記,都是 0 問題。

## 圖譜鏡頭(固定席)

- `Systems/lumos-cli-read.md`(search 排除 superseded 的 INVARIANT)、`Systems/lumos-cli-lifecycle.md`(re-inject sentinel 的 INVARIANT)、`Systems/guard-kill.md`(rc 優先序與 `--json` 純度的 INVARIANT)、`Systems/design-loop.md`(處置閘第五步的 INVARIANT):判不影響。r4 修補只動 macrobench 區段、收集範本、測試與筆記,沒有改這些合約管的函式。
- `Systems/測試假綠形態.md`(還原翻紅釘要有前置斷言):新測試多數有前置斷言,例如 `signals` 的「前置:送出時收集還在跑」。F1 就是用還原實驗找出的反例,屬 S23 綁定問題,不是這條合約被破壞。
- `Systems/bound-tests-gate.md`(綁定測試逐支真跑):對 F1 有牽連。它只跑被綁的測試,所以漏綁的測試不會被閘跑到。
- `Issues/vendored測試套件在消費端假紅.md`、`Systems/pitfalls-code-loop.md`:判不影響。
- 其餘只列名的節點不必答。

## 表態記錄與殘留(被標「可反駁的宣稱」)

- `infra-pid satisfied — scripts/templates/android-stability-collect.sh:296`:
  - 行號指到的是 `perfetto_alive`。
  - 它確實是用 pid 比對。
  - 但這條只讀程式碼,不算行為證據,且派工詞自己標了「背書:沒有」。
  - 行為證據要靠 `record_alive` 與 F1,而 F1 說明這支測試沒被 S 條款綁住。
- 派工詞要求逐條回答的「新增殘留」:
  - 派工詞自己寫「算不出來」,我沒有去翻 `governance/residual-index.json`。
  - 這一項未判定。

## 三問的回答

1. **原問題的修復效果(文件側)**
   - 計劃 S7、S20、S22–S25、S27、skill L0 第 8 步、reference.md 的 `device_model` 與 `stability_unjudged`、統計化計劃的指向,逐句對過程式與測試,基本成立。
   - 統計化計劃指向的 `Projects/Macrobenchmark退步提醒_計劃` 與 `Verification/2026-10-23_macrobench實機端到端` 各有一條 2026-12-21 的容差實測 REVISIT,指得對。
   - 不成立的是 F1(綁定)、F2(函式名)、F4(值為 false 的矛盾)。
2. **修補處的正常、錯誤與相鄰路徑**
   - 相鄰路徑出現新漂移:F3(SIGHUP 與 test_data 門沒回寫設計正文)、F4、F7。
3. **同一案例修前修後**
   - F1:修前 S23 沒有這句,修後新增且漏綁。還原實驗是在修後版本做的:S23 綁的五支全綠,只有 `record_alive` 紅。
   - F2:`git grep` 顯示 f0d41453 與 5fc4e715 的呼叫都在 `_dispatch_lens_graph`,兩版文件都沒寫對。
   - F3–F7:靠逐句對照,沒有跑兩版指令。

## 未驗範圍

- 沒有碰 adb 與實機。
- 沒有逐條還原整份 `[test:]` 做殺傷力檢查,只對 F1 與 Big5 兩處做了還原實驗。
- 沒有核對 `docs/.governance-log.jsonl` 與 `residual-index.json`。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/docs/lumos-toolchain-knowledge/Issues/派工鏡頭附的表態取自會談目錄的分支.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/skills/lumos-android-evidence/SKILL.md`

file: `scripts/lumos:60729` 實際呼叫 `_codeloop_read_dispositions` 的位置,在 `_dispatch_lens_graph` 裡。
file: `scripts/test_lumos.py:18712` 唯一守「ps 失敗」的測試,沒被任何 S 條款綁。
