severity: minor

這一席沒找到會做出錯行為的缺陷,只有三條清理與測試品質類的發現。

派工詞裡的 `.warming` 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/93aaa64b…673f0.json.warming` 不存在,所以我沒有刪鎖,也沒有可判斷的鎖內 PID。
本機系統掛鉤這次沒有附固定席節點,見下方圖譜鏡頭段。

## F1 效能方法名不收 `$`,是縮窄能力,不是在 sh 邊界做引號
severity: minor
blocking: 否
file: `scripts/lumos:40383`(`E2E_BENCH_NAME_RE`)、`scripts/templates/android-e2e-run.sh` 的方法名檢查那行。
失敗場景:Kotlin 巢狀類別的 Macrobenchmark(`pkg.Outer$Inner#test`)原本合法,現在設定檢查直接回 2。
- 根因是 `macrobench_cmd.replace("{{TEST}}", t)` 沒做 shell 引號。修法只是把字元拿掉,沒有在換進 `sh -c` 的地方用 `shlex.quote`。
- 這是計劃書明寫的取捨(計劃書 `Android端到端驗收_計劃.md` 的〈效能〉段與 S26 寫了「不收 `$`」),所以只算修的深度類。
- 歸因:有證據的修復造成的行為變化,不是退步。
- 修前修後對照(分別載入 787dd51b 與 4b056532 的 `scripts/lumos`):
  - `E2E_BENCH_NAME_RE.fullmatch("Outer$Inner#test")` 修前 True,修後 False。
  - `E2E_BENCH_NAME_RE.fullmatch("a$b")` 修前 True,修後 False。
  - `_e2e_case_bench_err` 對 `Outer$Inner#t` 修前回 None,修後回「不收 $」的錯誤。
引句:「E2E_BENCH_NAME_RE = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_.#]*")   # 效能測試方法名:原樣換進 macrobench_cmd 交給 sh,不收 $(sh 會當變數展開、跑成別支)、開頭不准 #(sh 當註解);範本腳本同一條」

## F2 paths 的「永遠對不到」寫法只擋了三種形狀,同族還有
severity: minor
blocking: 否
file: `scripts/lumos`(`_e2e_feature_head_err`,修補新增的 `posixpath.normpath` 那段)。
失敗場景:`paths: ["app/*.kt"]` 或 `["app\\src"]` 照樣被收。`_e2e_under` 只做整段字串前綴比對,所以這種寫法永遠對不到改到的檔。
- 只有這個功能是唯一命中時,`--changed` 會明確報「對不到任何功能」。
- 同次有別的功能命中時,這個功能被靜默漏跑。改到的檔若在 app_dirs 底下,還會被列進 unmatched 提醒;不在 app_dirs 底下就沒有任何提示。
- 同一個「照收卻永遠對不到」問題,修補只擋了 `//`、`/./`、`.`,沒有在根因上擋。
- 歸因:有證據的原有漏查(修前修後都收)。
- 重現:載入 `scripts/lumos`,呼叫 `m._e2e_feature_head_err("f", {"paths": ["app/*.kt"], "cases": {"c": {}}}, re.compile(r"[A-Za-z0-9_-]+"))`。修前和修後都回 None;`a\\b` 也一樣。`a//b`、`.`、`app/./x` 修前回 None,修後被擋。
引句:「    if bad is not None:   # app//src、app/./src、. 這類寫法照收卻永遠對不到改到的檔」

## F3 測試輔助函式造出無法解析的結束時間,而且註解說的行為沒做到
severity: minor
blocking: 否
file: `scripts/test_lumos.py`,`_e2e_rejudge_copy`。
失敗場景:註解寫「結束時間往後推一分鐘」,實際是 `(st.get("ended") …)[:-9] + "59:59+08:00"`。
- `[:-9]` 切掉的是 `:SS+08:00`,不是 `SS+08:00`。
- 結果是 `2026-10-26T10:3059:59+08:00`。`datetime.fromisoformat` 對它丟 `Invalid isoformat string`。
- `_gov_ts` 回 None,`_e2e_keep_old` 的時間分支在 u1、b1 兩個案例根本沒走到。
- 這兩個案例只靠完整性規則通過,所以不會假紅,也不會假綠,但註解說的行為不存在,日後有人依它改測試會誤判。
- 歸因:修補新增的測試輔助,與原本漏查無關。
- 重現:`python3.14 -c "s='2026-10-26T10:30:12+08:00'; print(s[:-9]+'59:59+08:00')"`,印出上面那個畸形字串,對它做 `fromisoformat` 即丟錯。
引句:「    st["ended"] = (st.get("ended") or "2026-10-26T00:00:00+08:00")[:-9] + "59:59+08:00"」

## pitfalls manifest 判定
- 內建的 `open(` handle 題:這次改動沒有新增 `open(`,判誤報。
  - 我用 `git diff 787dd51b..4b056532` 過濾 `^+.*\bopen(` 在 scripts/lumos、scripts/test_lumos.py、scripts/templates 三處,零命中。
  - 新增的檔案寫入都走 `Path.write_text` 或既有的 `_local_ledger_append`。
  - 範本腳本用的是既有的 `Steps.save()`(`open` + `os.replace`,不在修補範圍)。
- `lumos pitfalls --diff` 另外列出一條修補新增的 ruff 提示:`scripts/lumos:40985` `Consider [*rs, runs["result"]] instead of concatenation`,對應 `"fail" in rs + [runs["result"]]`。
  - 這個 repo 沒有 ruff 設定檔,全域推送前掛鉤不會因此擋推送。
  - 它是新增的告警,但純屬風格,沒有行為影響。
- 併發類題目依派工詞判範圍外。

## 圖譜鏡頭
- 掛鉤這次沒附固定席節點(LUMOS-LENS 寫「這次沒附固定席節點」),所以沒有逐條可答的固定席筆記。
- 我另外讀了計劃書(`docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md`)的相關條款作為判準來源:
  - S22、S23、S25、S26、S27 對照修補程式,沒有找到違反的地方。
  - 「不收 `$`」「重判更早不蓋」「只列效能的情境回 1」都有寫在條款或正文,與程式一致。
- 沒有發現筆記與程式對不上的地方,不需要立 Issue。

## 三問的回答

**① 原問題的修復效果,行為證據。**
- 做法:在 787dd51b 的乾淨副本換上修後的 `scripts/test_lumos.py`,跑 `python3.14 scripts/test_lumos.py -k android_e2e`,與 4b056532 的乾淨副本對照。
- 版本確認:兩份都是 `git clone --shared` 後 checkout 到指定 sha,`git log --oneline -1` 回 787dd51b 與 4b056532。
- 結果:
  - 修前 345 過、14 紅。
  - 修後 359 過、0 紅。
- 修前的 14 條紅涵蓋以下根因:
  - `$` 方法名。
  - paths 為 `//` 或 `.`。
  - `macrobench_cmd` 非字串時噴 traceback。
  - 只列效能的情境回 0(修前印「通過」)。
  - 共用 flow 混合命中沒列提醒。
  - `--case` 加 `--changed` 對不到時被擋。
  - 清單重複不去重。
  - 失敗不覆蓋先前通過。
  - 重判更早不蓋。
  - 替身收集腳本仍寫紀錄。
  - 殘留的 `LUMOS_STABILITY_SCENARIO` 帶給 stability 段。
  - history 照情境篩混入別的情境結果。
- 這只證明這批斷言在修前紅、修後綠。斷言本身是否充分,依 F3 有一處輔助函式名實不符。

**② 修補處的正常、錯誤與相鄰呼叫路徑。**
- 未改動的相鄰測試在修前修後都綠(同一輪 -k android_e2e):
  - `t_android_e2e_changed_pick`
  - `t_android_e2e_judge_perf_memory`
  - `t_android_e2e_lists_match_templates`(範本腳本與 `E2E_BENCH_NAME_RE` 兩邊規則相等)
  - `t_android_e2e_run_script`
  - `t_android_e2e_memory_by_case`
- 我另外直接呼叫 `_e2e_keep_old` 驗了六種覆蓋組合,沒有發現不合理的結果:
  - 舊完整 pass、新 fail:蓋掉。
  - 舊完整 pass 且較新、新 fail 較舊:留舊。
  - 舊完整 pass、新 unjudged:留舊。
  - 舊完整 fail、新完整 pass:蓋掉。
  - 舊不完整 pass、新 unjudged:蓋掉。
  - 舊完整 fail、新不完整 pass:留舊。
- `_e2e_feature_head_err` 對 `app`、`app/`、`./app`、`app/src/` 仍通過。

**③ 新發現的同一案例在修前修後各是什麼。**
- F1:上面已列修前修後對照,結果是修復造成的行為變化。
- F2:修前修後都收,屬於原有漏查,不是回歸。
- F3:修前沒有這個測試輔助,是修補新增的。

**未驗範圍**
- 沒有接真實 adb 與 Maestro 的端到端跑法,只看到測試用替身。
- 沒有對大型 repo 的 `git ls-files --others` 做效能實測。逾時改成擋下是修補新增的行為,我只從程式讀到,沒有在大型 repo 上量測。
- 只回答了本席的三問與鏡頭範圍,不代表整體無回歸保證。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭5-通才-sonnet` 與紅燈留下的測試現場 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-run-7h32l157` 都已用字面絕對路徑刪除。

修補把已知缺陷都收進測試,零個會出錯的行為缺陷,留下三條清理類的小問題,包含效能方法名縮窄 `$`、paths 同族寫法沒擋乾淨,以及一個名實不符的測試輔助函式。
