severity: major

我讀了 diff 檔全部內容,並在 `/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence` 用 python3.14 在行程內載入 `scripts/lumos` 重現。八個角度跑完後去重,剩 5 條。

- 被刪掉的行為:`_dispositions_validate` 的 satisfied 分支抽成 `_disp_satisfied_shape` 後邏輯逐句相同,沒有掉守衛。
- 呼叫者:`_strip_c_comments` 既有呼叫者沒有傳 `kotlin`,走原路,沒有改變。
- 呼叫者:`_dispositions_verdict` 只有一個呼叫者(`scripts/lumos:72205`),已補傳 `diff_range`。
- 測試:`_isolate_environment` 把型錄凍成永不亮的小表。這讓既有測試維持舊語意,也代表它們不會覆蓋情境題。

F1
severity: major
blocking: 是
引句:「        cache["segs"] = _kt_situation_segments(repo_root, diff_range, at_sha, skip=_vendored_skip(repo_root, diff_range)) or []」
file: `scripts/lumos:38979`(`_kt_situation_segments` 內的 `hunks = _kt_sit_hunks(repo_root, diff_range) or {}`)、`scripts/lumos:71738`
問題:推送前核對時,重算情境段一旦失敗,會靜默變成「沒有段」,表態被放行。`_kt_sit_hunks` 在 git 回傳非 0 時回 None,`_kt_situation_segments` 用 `or {}` 吞掉。`diff_range` 是 None 時也直接回 `[]`。`_kt_sit_read` 讀不到檔也只是 `continue`。`_kt_sit_verdict_one` 的 `if cache["segs"] else []` 再把空清單當成「這題不核」,回 None 並計入 `checked`。
矛盾:`_kt_situation_apply` 的註解寫「推送前核對時會重算,算不出來就判無法驗證、擋下」,但只有 `TimeoutExpired` 會走到那條擋下的路徑。git 非 0、`diff_range=None`、`at_sha` 找不到,全都放行。
重現:
```
m=<載入 scripts/lumos>; ent={"status":"satisfied","segments":[{"seg":"x","rows":{"D-1":{"applies":False}}}]}
m._kt_sit_verdict_one(".", "nonexistent..HEAD", None, ent, {})   # 回 None=過
m._kt_sit_verdict_one(".", None, None, ent, {})                  # 回 None=過
```
建議:區分「git 或讀檔失敗」與「真的沒有段」。前者在核對時回「無法驗證」並擋下。

F2
severity: minor
blocking: 否
引句:「    env = os.environ.get("LUMOS_KT_CATALOG")」
file: `scripts/lumos:38130` 附近(`_kt_catalog_path`)
問題:`LUMOS_KT_CATALOG` 指到任何小表,整個情境題就關掉,而且不留帳也不印提醒。`LUMOS_SKIP_*` 這類逃生變數至少會留帳,`_isolate_environment` 也只清 `LUMOS_SKIP_` 前綴。這個變數是測試用,卻能在正式推送時當作無痕略過。
建議:改成只在測試模式生效,或用了就記一筆帳。

F3
severity: minor
blocking: 否
引句:「型錄隨工具鏈安裝,讀不到或格式壞就不加這一題(沒有型錄就沒有題目可問)」
file: `scripts/lumos:38125`(`_KT_CATALOG_DEFAULT`)
問題:預設路徑是 `Path(__file__).resolve().parent.parent / "skills" / "kotlin-idioms" / "checks-catalog.md"`。`CLAUDE.md` 說 init 會把 CLI 複製進消費專案的 `scripts/`。副本的上上層沒有 `skills/`,型錄讀不到,情境題就整題消失。消費端只會在有 kt 改動時看到 `_kt_sit_catalog_warnings` 的一行提醒,那是 warning、不擋推送。
限制:我沒驗證 vendored 副本的實際佈局,所以只列 minor。
建議:改走 `_lumos_src()`(`LUMOS_HOME`)找型錄,或在消費專案缺型錄時擋下。

F4
severity: minor
blocking: 否
引句:「    return [], f"{c[0]} 欄位數 {len(c)},表頭有 {len(header)} 欄」」
file: `scripts/lumos:38200` 附近(`_kt_decision_table`)
問題:型錄任何一列格式壞(例如列尾少一個 `|`,`_kt_dt_cells` 的 `[1:-1]` 會吃掉最後一格),整張決策表回 `([], 原因)`,整題情境題一起關掉。對外只是 stderr 一行提醒加核對時的 warning。一個格子寫壞就讓整個閘靜默失效。
建議:格式壞時擋下,或至少升成 problem 而不是 warning。

F5
severity: minor
blocking: 否
引句:「        print(f"提醒:情境段算不出來({e.__class__.__name__}),情境題照逐行觸發字判;推送前核對時會重算", file=sys.stderr)」
file: `scripts/lumos:39024`
問題:逾時時 `row["applicable"]` 保持 True,但回傳的 `sit_segs` 是 `[]`,`situation_segments` 不會進 JSON。`_dispositions_template` 因此產出 `segments: []`。`_kt_sit_shape` 對空 segments 回「satisfied 要附 segments」,使用者拿到的樣板答不了這題。
建議:此時不要產空樣板,或在樣板裡明講要重跑。

總結:最嚴重是 F1(重算情境段失敗會靜默放行表態,與自己的註解矛盾),會擋 1 條。
