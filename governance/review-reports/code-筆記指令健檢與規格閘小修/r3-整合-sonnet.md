severity: major

審查範圍:修補差異 `r3-repair-docs.patch`、`r3-repair-lumos.patch`,對照 `scripts/lumos`。被審的 342cf099 與目前 HEAD 8e78ff91 的 `scripts/lumos` 沒有差異。

1. 決策 d3 與程式不一致:已完成計劃的寬待比 d3 寫的寬。
   - 位置:`_spec_gate_push_one`(`scripts/lumos:9923`)。
   - d3 原文:寬待「只寬待留痕指紋對不上與某支留痕測試找不到兩種」,其餘照 doing 一樣嚴。
   - 程式行為:`_spec_gate_push_stale` 有四種回傳原因,分別是讀不成文字、測試索引建不起來、門現在判成風險高、條款指紋變了。`done=True` 時四種一律只進 `notes`,不擋。
   - 重現:
     1. 做一份風險低計劃並留痕,另開提交把狀態改成 done。
     2. 再提交一次,在正文加「這份會處理退款扣款金流。」,同時讓留痕測試全綠。
     3. 跑 `spec-gate --push-check HEAD~1..HEAD`。
   - 實際輸出:rc 0,印「已完成,留痕對不上現在的計劃(…留痕時風險低,現在判成風險高(關鍵字「金流」…))…其餘找得到的 1 支條款測試全綠、不擋」。
   - 預期:依 d3,這種情形不在寬待範圍,該被擋。
   - 後果:一份已完成計劃新增金流關鍵字、門已判高,只要舊測試綠就能推上去,不會回去走設計審。
   - 歸因:原有漏查,不是這輪修補造成。修前版本 86aa8f40 的 `if stale and not done` / `if stale:` 結構相同,這輪只改了 `_spec_gate_status_at` 的起點。修前沒有另外重跑這個案例。
   - 兩條修法都可以:收窄程式,只對「條款指紋不符」放寬;或把 d3 與計劃正文改成四種都寬待,並寫明理由。這個修補還沒做到其中任何一條。
   - 引句:「而且只寬待留痕指紋對不上與某支留痕測試找不到兩種:不做清單那道照查、其餘找得到的測試照跑、紅了照擋」
severity: major
   - blocking: 是
   - 歸因:有證據的原有漏查。

2. 其餘文件與程式一致,下列各項都實際核對過。
   - d1:`summary-line` 在非 git 專案跳過檢查,`summary-add` 擋下,git 跑不起來(`None`)兩支都擋。`_is_git_worktree` 的三態與 `_summary_write_shape_check` 相符。
   - d2:補跑步驟的文字與計劃正文一致,都是先提交、既有檔 `git restore --source`、新檔換空殼不要移走。
   - cochange:不帶範圍照 `--staged`。`home check`、`note-shape`、`cochange check` 三支的 `--diff ""` 都是 rc 2,三支不帶範圍都是 rc 0 並先印一句。
   - refcheck 截斷條件的實跑結果與計劃第 8 節一致。
     - `scripts/lumos doctor`、`scripts/e2e.sh --cleanup`、`scripts/lumos --help`、`scripts/lumos 的某函式`:只核對第一個詞。
     - `scripts/lumos x.md`、`scripts/nope run`:整串核對。
   - 兩個小疑慮,都不另立為 finding。
     - 第一,`scripts/lumos README.md` 這種「指令加檔名」會被當成帶空白路徑,報整串 missing。文件已寫明這是設計,修前也是同樣結果。
     - 第二,「還沒有前.js」這類時間詞後接半形句點的輸入會被判成子句而不提醒。這是統一規則的已知代價。
   - 推送閘起點改用 `_range_base`,三點範圍取 merge-base,與計劃及 `t_prepush_spec_gate_done_three_dot_base` 相符。
   - 子句標點:Unicode P 類(扣掉 Pc 與斜線、連字號類、底線)、「只要…就」「等到…才」配對,與量測程式 `neg_revisit_measure.py` 的寫法逐行相同。

3. 指令實跑結果。
   - `python3.14 scripts/lumos doctor --ci`:rc 0,「圖譜健康 — 0 issues (894 篇)」。
   - `python3.14 scripts/lumos note-shape --diff 0beb6d7d..HEAD`:rc 0,但印「筆記測試綁定:這組的 20 秒用完了,剩下的名稱這次不查」,測試名綁定沒有全查。我改用 grep 逐一確認這輪新增或改動的 `[test:]` 都存在:
     - `t_prepush_spec_gate_done_three_dot_base`
     - `t_note_shape_negation_clause_punct_unicode`
     - `t_drift_fix_shape_follows_gate`
     - `t_prepush_spec_gate_done_stale_still_checks_nogo`
     - `t_home_and_note_shape_default_staged`
     - `t_ref_path_first_word_of_command`
   - 相關測試子集全綠:negation 150、ref_path 21、refcheck 204、summary_ 113、prepush_spec_gate 30、drift_fix_shape 4、home_and_note 5、cochange 31、spec_gate_low 14。

4. 新增的 WHY 行(筆記內容閘、規格閘、lumos-cli-write、lumos-refcheck)都帶 `[出處:]`、`[因:]`、`[test:]`,每支改動檔仍有家。`r3-docs.patch` 裡刪掉的 FLOW 與 KEY 行是前幾輪的改動,不在這輪修補差異內,我沒有逐條追。

三問的回答:
- ①原問題的修復效果:refcheck 子命令誤報、三點範圍起點、同秒取本機、冒號前置檢查、補跑紅的警告扣簿記檔,都有實跑或測試佐證已修好。這些問題修前版本都沒有各別重跑,所以只能說「修後正常」,不能說「修前確實壞」。
- ②正常、錯誤、相鄰路徑:寬待路徑的相鄰分支(測試綠、紅、找不到、不做清單、本輪才改 done)沒有新的回歸。上面第 1 條是寬待邊界與 d3 不符,屬原有漏查。
- ③新發現的同一案例,修前修後:第 1 條只在修後版本實跑過。修前版本的程式結構相同,但沒有實際重跑,所以歸因寫「原有漏查」,依據是程式結構,不是兩版實測。

臨時目錄 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/整合-sonnet` 已刪。

最嚴重 severity:major;blocking 共 1 條。
