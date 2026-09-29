severity: minor

方法說明(供收貨端評估可信度):對每一條筆記裡的 PITFALL/WHY 主張,都開 HEAD 的 `scripts/lumos` 讀對應函式驗語意(不只驗名字存在);對關鍵幾條(A1 shebang 語料、A4 路徑正規化、A5 status 讀不出、C2 --text、D3 other 區淨差異)另外把 `scripts/lumos`+`scripts/test_lumos.py` 複製到 repo 外的暫存目錄,手動改壞對應程式碼、重跑 `t_drift_code_review_yi_r1_regressions`,確認真的會紅(沒有改動任何 repo 內的檔)。S9/S10/S11/S13/S14/S15 綁定測試與 `-k drift`、`-k revisit` 全跑過一次(213+18 全綠),另跑 `lumos lint`、`lumos doctor` 驗筆記形狀與整庫健康。

## F1 混了甲乙兩種發現時,印出的表態指令是 argparse 會拒絕的無效語法

severity: minor
blocking: 否 — 只是提醒文字誤導,不影響擋/放行本身,也不影響單獨對每一行分別下正確 `--kind` 表態

引句:「+          + ("|".join(sorted(kinds)) if len(kinds) > 1 else next(iter(kinds)))
+          + " --reason \"<為什麼照留>\"", file=sys.stderr)」

1. `_drift_report_must`(`scripts/lumos:1017` 一帶,新增的 kinds 分支)在同一次推送裡同時有甲(c1–c5)與乙(probe)的「要處理」發現時,結尾建議指令用 `"|".join(sorted(kinds))` 把多種 kind 用 `|` 接成一個字串印出,例如 `--kind c1|probe`。
2. `dra.add_argument("--kind", ..., choices=_DRIFT_KINDS)`(`scripts/lumos:35577` 一帶)是 argparse 的 `choices`,只接受 `_DRIFT_KINDS = ("probe","c1","c2","c3","c4","c5")` 裡單一個字串,不接受用 `|` 拼起來的複合值。
3. 重現(在 mutation 副本 `scratchpad/mut` 上做,未動任何 repo 內檔案):建一個 `_dr_repo`,base 提交裡放一篇 `pending` 的守衛紀錄與一個帶 `REVISIT:[when-file:src/runner.py][by:2099-12-31]` 的節點(此時 `src/runner.py` 還不存在),下一個提交把守衛紀錄轉正成 `pass`(沒改預告句)同時新增 `src/runner.py`,跑 `lumos drift check --diff <base>..HEAD`,擋下訊息尾端印出:
   ```
   不改就留著並表態:
       lumos drift ack <節點> <行號> --kind c1|probe --reason "<為什麼照留>"
   ```
   照原樣把其中一個節點與行號代進去跑 `lumos drift ack "Verification/G" 18 --kind "c1|probe" --reason "為什麼照留測試"`,回應是 `擋下:--kind 不接受「c1|probe」這個值。是不是想寫這個: --kind probe`(rc=2)。
4. 沒有既有測試覆蓋這個組合場景:`t_drift_code_review_yi_r1_regressions` 的 C3 只測純 probe(`kinds=={"probe"}`)那一支,`t_drift_check_state_events_in_range` 只測純 c1。兩種發現同時出現在同一次推送(甲乙都跑在同一支 `cmd_drift_check` 裡)是合理場景,不是邊角案例。
5. 影響範圍小:每一條 finding 本身在 `_drift_print_findings` 裡已經各自印了 kind(見上面重現的輸出),使用者照著單筆的 kind 分別下 `--kind c1` / `--kind probe` 兩次表態仍然可行,只是結尾那行「懶人複製」的建議指令會失敗,要重讀前面才知道怎麼下。

已看、無 finding:
- `_probe_norm_value`(路徑正規化,`_posix_norm`+`nfc`)、`_drift_probe_code_path`(shebang 語料涵蓋)、`_drift_probe_one` 的 status 分支(讀不出算判不了、不算不成立)、`_notelines_rows` 的 `net` 過濾(other 區只認淨差異新行)、`_drift_probe_changes` 的 `--text`(-diff 屬性檔案照樣看得到新增行)——這五處筆記(計劃〈做法〉第 2 節四種鍵、Systems 新增的 PITFALL/WHY 行、〈跟設計稿不一樣的兩處〉三條新增項)寫的話跟程式行為逐條對得上;針對這五處各自把對應程式碼改回舊版行為,`t_drift_code_review_yi_r1_regressions` 的 A4/A1/A5/D3/C2 分別確實翻紅(未改動 repo 內任何檔,改動只發生在 `scratchpad/mut` 的獨立副本)。
- `_drift_probe_path_warn`(型別::方法寫法列成「不像檔案路徑」,還沒建的檔不誤列)、`_drift_exam_load_probes` 的文法前置檢查(改寫檔沒帶 `[by:]` 直接 rc2)——對照 B4、D4 測試與程式碼一致。
- `governance/eval/drift-exam/rtb-2026-09-28-probes.json` 與 `README.md` 更正紀錄:A7/B3/B4 三題補上 `[by:]` 的改動,程式碼(`_drift_exam_load_probes`)確實會擋沒帶期限的改寫檔,`D5` 測試證明正式改寫檔全部合文法;但「B3 2027-01-31、B4 2026-12-31 是照原文日期補的」這句話指向 rtb 專案的原始筆記,不在這個 repo 裡,判不準,標 ⚠(不影響本 repo 程式行為,不計入 severity)。
- `_nodehome_name_status` 新增 `codes` 參數:預設 `None`,既有 6 個呼叫點都沒有傳,行為不變(逐一看過 `scripts/lumos:23067/23074/23179/23194/23916/24717`),只有 `_drift_probe_changes` 這個新呼叫點用它,沒有波及既有邏輯。
- `_ns_diff(root, "--text", base, tip)` 只出現在 `_drift_probe_changes` 這一個呼叫點,沒有改到其他 26 處 `_ns_diff` 呼叫,範圍精準。
- `keep_other=True` 分支多出的那一次 `_ns_diff`(算 other 區淨差異)只有筆記形狀擋(第一層,`_note_shape_eval`)這個唯一呼叫點在用,筆記內容審(第二層)用預設 `keep_other=False`,不受影響、不多付這次 git 成本。
- 合約測試:`[S1][S2][S3][S4][S6][S7][S8][S9][S10][S11][S12][S13][S14][S15][S19]` 對應的 `-k drift`、`-k revisit` 測試(共 213+18 案例)全綠;`lumos lint` 對 `Systems/存量漂移守衛`、`Projects/存量漂移防線_計劃` 都是 0 問題;`lumos doctor` 全庫 0 issues(既有的 ⚠ 提醒與這份 diff 無關)。

最嚴重 minor,blocking 0 條。
