severity: minor

## F1 涵蓋報告自己另設一道範圍篩子,跟推送前判定不是同一個口徑
severity: minor
blocking: 否
引句:「if app is None or not inside:   # 驗收素材、單元測試、範圍外的檔不算程式檔」
file: `scripts/lumos:41570`
1. 推送前判定 `_e2e_gate_need` 先用 `[f for f in allf if _e2e_scope_hit(f, e2e, dirs)[1]]` 篩出檔案,再交給 `_e2e_gate_owners`。`--changed` 的 `_e2e_changed_features`(`scripts/lumos:41083`)也只看 `[1]`。`[1]` 為真的檔包含驗收素材(`.maestro`、門檻檔、flows)。
2. 涵蓋報告多加一道條件:`app is None` 就丟掉。app_dirs 以外的素材檔,推送前判定會因「對不到任何功能」要求整套跑,涵蓋報告卻不列。
3. 結構是對的,歸屬判定也共用了 `_e2e_file_owner`。但 `_e2e_coverage_report` 的 docstring 寫「沒歸屬加共用程式正好是推送前判定要整套跑的那批」,範圍篩這一層做不到。
4. `t_android_e2e_coverage_same_as_gate` 只用 app_dirs 底下的檔,測不到這個差異。
5. 這裡是刻意把素材排除在「程式檔」之外,不是漏用共用函式,所以我判 minor,不判「第二種做法」。要嘛篩子改成鄰居那樣只看 `[1]`,要嘛把 docstring 和計劃筆記的「正好是」改成「程式檔部分」。

## F2 文字版報告印檔名用 `_esc_clean`,同族 stdout 鄰居用 `_out_clean`
severity: minor
blocking: 否
引句:「return "、".join(_esc_clean(x, 200) for x in xs) or "無"」
file: `scripts/lumos:19371`
1. `_out_clean` 的 docstring 寫明它是「擋下訊息與判定結果裡的外來文字(設定值、紀錄鍵名、檔名)」用的底層清理。e2e 區直接印給使用者的檔名,例如 `_e2e_judge_partial` 印 unmatched 那行,走的是 `_out_clean`。
2. 涵蓋報告的 stdout 檔名、資料夾名、功能名全走 `_esc_clean(…, 200)`。這跟 `_e2e_gate_owners` 的用法一致,但那裡的結果最後還會經 `_say_block` 的 `_out_clean`,涵蓋報告沒有這道。
3. 差在 U+2028/2029、方向標記、BOM,以及逃逸帳標記的拆字,涵蓋報告印出的文字不會經過這些清理。
4. 外來文字回顯屬範圍外,所以只記為「與鄰居清理函式不同」,判 minor。

## 三問

**1. 分層與依賴方向:基本對齊,F1 是例外。**
- 新碼放在 `_e2e_check_cmd` 前面,仍在 e2e 區內。依賴方向是 `_e2e_coverage_cmd` → `_e2e_coverage_input` / `_e2e_coverage_report` → `_e2e_scope_dirs`、`_e2e_scope_hit`、`_e2e_file_owner`,沒有跨層。
- `_e2e_gate_owners` 改成呼叫 `_e2e_file_owner`,把歸屬判定收成一支共用的。這是收斂,不是繞過。
- 設定讀取用 `_e2e_worktree_e2e`(`scripts/lumos:41147`),和 `_e2e_select_cmd`、`_e2e_judge_partial` 一致。
- 改動清單用 `_e2e_changed_files`(`scripts/lumos:41035`),和 `_e2e_changed_features` 共用。
- 整棵樹的檔案清單用 `_nodehome_git(... "--literal-pathspecs" ...)` 加 `_nodehome_split_z`,和 `_e2e_present`、`_e2e_gate_need` 同一套。
- doctor 的 AE 段照原本的「提醒不擋」格式,用 `warn_soft`。
- 唯一例外是 F1:範圍篩子多了一道,與鄰居不同。

**2. 命名與錯誤處理:對齊,F2 是例外。**
- 錯誤一律走 `_say_block(err)` 加 rc 2,和 `_e2e_select_cmd`、`_e2e_check_cmd` 相同。
- 成功時 rc 0,JSON 用 `json.dumps(..., ensure_ascii=False)`,和 select、check 相同。
- dispatch、`HELP_WHEN`、argparse 的 `dest="e2e_*"` 命名,都和既有子命令同形。
- 小處不一致:`_e2e_cov_names` 用縮寫 `cov`,同一份 diff 裡其他函式用全名 `coverage`。這屬純風格,不列。

**3. 第二種做法:沒有引入新的讀設定或跑 git 的方式。**
- 沒有自創工具函式去取代鄰居已有的。逐檔歸屬、設定讀取、git 呼叫、擋下訊息都沿用既有的。
- 範圍判斷沒有另寫一套,只多一道篩子(F1)。
- 上輪修補(d36d194f 到 0bed2210)把涵蓋報告的設定從提交版改成讀工作目錄,並抽出 `_e2e_owner_ctx` / `_e2e_file_owner`。這兩步都是收斂回既有做法,沒有新增分岔。

不對齊共 2 條,其中 major 0 條
