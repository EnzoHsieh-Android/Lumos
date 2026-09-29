severity: minor

# r3 合約與圖譜一致(合約圖譜-sonnet)

## F1 對「其他非零放行」的兩處說明沒跟上 128 以上會停下
severity: minor
blocking: 否
引句:「(推送前掛鉤對其他非零是放行並講一句「這次沒檢查」,兩邊刻意不同:CI 是最後一道後盾)。」
佐證行:file: `scripts/hooks/pre-push:50`(pp_stop_if_signaled,rc 大於等於 128 就 exit)
敘述:
1. 這次改動讓掛鉤在 drift check 回傳碼 128 以上時停下(不放行);bound-tests-gate 兩行與掛鉤註解都寫對了。
2. ci.yml 這句註解(patch 內為 context 行)與 commands/08 的欄位「工具沒跑成(錯誤、git 太慢)講一句就放行」仍寫成「其他非零一律放行」,沒有排除 128 以上。同一份 diff 已改 08 的那一列(起點由工具算),卻沒補這個例外,讀的人會以為 Ctrl-C 也放行。
3. 影響只在說明,不影響行為;不會誤導測試或閘。

## F2 「呼叫那兩行逐字相同」沒講 python 與 python3 之別
severity: minor
blocking: 否
引句:「呼叫那兩行跟工具鏈 ci.yml 逐字相同、回傳碼照原樣讓那步紅綠」
佐證行:file: `scripts/test_lumos.py:51254`(測試 docstring 自己寫「python 與 python3 之別除外」)
敘述:
1. ci.yml 用 `python scripts/lumos drift check ...`,doctor 範本 `_DRIFT_CI_STEP` 用 `python3 scripts/lumos drift check ...`,不是逐字。
2. 測試已把直譯器名去掉再比,筆記沒寫這個例外,筆記與測試的口徑不同。低風險。

## 圖譜鏡頭逐條判定

- Issues/code-loop守衛main-direct盲區:不影響。它講的是 code-loop 範圍算法(merge-base..HEAD 與 stdin 推送範圍);這次 diff 對 code-loop check 只加了一行 `pp_stop_if_signaled "$cl_rc" "code-loop check"`,沒動它的範圍與擋放邏輯。該筆記正文的舊行號引用(`pre-push:64-88`)是這次之前就有的,不是這次新寫。
- Systems/存量漂移守衛(家):行為一致。WHY 行與「推送時自動跑」條目都改成「起點由 `_push_range_start` 算、掛鉤與 CI 帶 `--push-remote/--pushed-ref`」,與程式(`cmd_drift_check` 有 push 時走 `_push_range_start`、沒帶照 `_lens_push_base`)吻合;「不帶後兩個參數時照共用起點判法」也與程式一致。已無「掛鉤自己算起點」「CI shell 補法」的現況句,僅剩的是明標「r1 曾…r2 改」的歷史句。
- Systems/每支檔有家:一致。新增「兩道被中斷、128 以上時掛鉤停下」與程式(每支檔有家、筆記形狀擋各一行 `pp_stop_if_signaled`)相符;前置測試 t_prepush_gates_stop_on_signal 數到五道。
- Systems/筆記內容閘(家,牽連檔 pre-push):diff 沒改這篇;它管的 note-shape 只多了被中斷停下,見每支檔有家那句,不影響它自己的合約。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言):沒破壞。新增與改動的測試都帶前置斷言:t_prepush_gates_stop_on_signal 先斷言 `n == 5` 與「拿掉停下的舊掛鉤被殺掉的閘當放行、跑全套」;t_doctor_drift_ci_template_start_fallback ① 先證明現場成立。
- Systems/anchor-integrity、lumos-cli-lifecycle(re-inject sentinel 合約)、lumos-cli-read(search 排除 superseded):不影響;diff 沒碰 anchor、CLAUDE.md 注入、search 濾網。
- Systems/bound-tests-gate:一致。PITFALL 行改成「起點只在 `_push_range_start` 算」,與程式、掛鉤、CI 三處一致;新增 WHY 五道閘清單與掛鉤實際五處 `pp_stop_if_signaled` 一一對應(anchor verify、doctor 本來就任何非零都擋,合理)。
- Projects/存量漂移防線_計劃:第 120 行保留 r1 的句子(掛鉤自己算、CI 用父提交)後接 r2 的改法,寫明「r1 後…r2 查出…改成」,不是現況誤述。但條款 [S1] 仍寫「起點照共用推送起點判法」,而掛鉤與 CI 已改走 `_push_range_start`;不是新增矛盾(手動跑仍是共用判法,且 [S1] 綁的測試沒變),不計入 finding。
- 兩篇 Issue:新開的「健檢CI範本說明貼進workflow…」PITFALL 帶重現(ruby YAML.safe_load)與 REVISIT 日期,符合 PITFALL 與鐵則 4;「推送前其他閘…多算」摘要與內文已改成「漂移那道已由工具算、這兩道還沒改」,與程式一致(home check、note-shape 尚無 --push-remote)。
- skills commands/08:pre-push 那列與 CI 那列都寫了新參數與「起點由工具算」,與程式一致(除 F1 的 128 例外)。
- `lumos drift check --help`:實跑(clone 內 python 3.14)有 `--push-remote 遠端名` 與 `--pushed-ref ref` 兩項與說明,符合;沒有另外的說明頁需要同步(grep 其餘 skills 檔無 drift check 參數描述)。
- 新寫筆記行對 CLAUDE.md 前綴規則:新行皆為 WHY/PITFALL/RULE 類,WHY 有出處(代碼審 r2 某席)、PITFALL 有 [test:] 或重現;提到的函式用名稱不用行號;沒有無來源標記的 FACT/FLOW/DEP。未見違規。

最高等級:minor
