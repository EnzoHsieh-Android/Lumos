preflight-4: ran

# 殺傷力配方當場試跑 r1 收貨紀錄

## 前掃(2026-10-02,sonnet 一席,報告 r1-preflight.md)

①未定義的詞、②壞引用、③範圍矛盾、存在類:全部直接改進計劃,不算 findings。
- 新增〈名詞〉:短身分(8 碼以上前段、照 kill-rm 擋零條與多條)、判定 vs 證據弱(verdict 與 weak 欄)、配方指的檔(相對平台 repo 頂)。
- 回傳碼描述照實:有強證據 killed 0、survived 或全弱判定 1、drifted/abort/error 2。
- RETIRE-IF 改成只靠問(kill-log 沒有「這次只跑一條」的欄位)。
- kill-add 的「下一步」兩行已查過沒有測試釘字面。

④語意類(修改前 → 後):
1. ★動到做法★ `--try` 判 survived:「呼叫端推斷」→「cmd_guard_kill 多選用參數 results_out 交回逐條判定;判法、回傳碼不變」。依據:guard kill 只回 rc,rc 1 也包含全弱判定。
2. ★動到做法★ 「之後程式改過」:「_codeloop_record_valid_ex 判無效」→「配方指的檔在 head_sha..HEAD 之間改過(在平台 repo 頂 git diff --quiet),整段上限 _BACKING_BUDGET」。依據:那支判法只要有任何非簿記改動(含筆記)就算,實務上每行都會帶;head_sha 是平台 repo 的。
3. 不重複列:_kill_p2_scan 多回已列問題的配方身分集合(原本丟掉 _kill_p2_one 的回傳)。
4. P2 另開一個軟提醒、check-p2 事件 kind 用 survived;跳過規則抽 _kill_p2_skips 三處共用。
5. 取最新一筆:「比 ts」→「檔內順序最後一筆」(同 _backing_judge_groups);合約前段取筆記的;weak 為 true 的 survived 照列加註。
6. --id 比對照 kill-rm(前段、8 碼以上、零條或多條擋);列表抽 _guard_kill_rm_rows,guard kill 那邊印到標準錯誤、結尾改「只跑某一條」。
7. 修正關卡提醒:配方平台 repo 頂要等於修正關卡的 repo 頂;一條說明加每條指令各一個 note;只在沒早退的輪跑到。
8. kill-add --try:只更新 covers 時也試跑;預先講清楚一定會印未提交警告、weak=true、程式未提交時 drifted。

## r1 席報告收貨(2026-10-02,4 席)

機械三道:四份 `report-normalize` 都已是正規格式;`quote-check --spec r1-snapshot.md` 四份全數錨定;`refcheck --repo .` 四份 missing 0、out_of_range 0;`seat-check` 派工單沒列逐檔材料,vacuous。

### 編號對照(帳上用的 id = 席別字首 + 報告 F 號)

- c1–c9 = r1-正確性-opus.md F1–F9
- i1–i10 = r1-整合-sonnet.md F1–F10
- b1–b4 = r1-邊界-sonnet.md F1–F4
- a1–a9 = r1-架構對齊-sonnet.md F1–F9

### 重現(編排者親跑或讀碼核對)

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 / i2 / b1 | `_mk_kill_env` 加一條配方,`.lumos/config.json` 寫成 `{bad`,`_kill_recipe_judge` 與 `_kill_p2_one` 判那條(腳本 scratchpad/repro-r1.*/r.py) | HIT:`cfg-status: cfg`、`p2_one: cfg items: []`——不在 items 裡卻「不是 ok」,照舊字面會被 survived 清單跳過 |
| b3 | 同夾具,筆記 kill_recipes JSON 第一個元素改成字串、提交後 `guard kill Systems/Limit`(scratchpad/repro-b3.*/r.py) | HIT:rc 1、`AttributeError: 'str' object has no attribute 'get'` |
| i4 | 讀 `t_guard_kill_add_warns_drifted_recipe`:case() 斷言 `r.stdout == ok.stdout`,各格 `--old` 不同 | HIT(讀碼):短身分進標準輸出後必不等;改印標準錯誤也會讓判重那格的行數斷言失準 |
| c6 / i1 | 讀 `cmd_guard_kill` 開頭:配方只在函式內讀、片段過濾在函式內 | HIT(讀碼):dispatch 層沒有配方,舊計劃兩句不能同時成立 |
| b2 / c9 | 讀 `cmd_guard_kill` 蓋章 `weak` 含 `node_dirty`;rc 只看 verdict | HIT(讀碼):`--try` 時 weak 必 true,舊計劃「強證據」定義下 S2 造不出 |
| c2 c3 c4 c5 c7 c8 i3 i5–i10 b4 a1–a9 | 讀碼核對席位引的行(refcheck 全 ok);c4、c7 席位附實測腳本 | 現象採信,均為 minor,全折 |

### 處置

全折(32 條),無放行、無駁回。折法摘要寫在計劃〈審計修正紀錄〉r1 那行;要點:
- c1/i2/b1:`listed` 只收真的逐條列出的狀態碼,cfg/noroot 不收;S3 加「設定檔讀不了時應照樣列」。
- c6/i1/b3:`id_prefixes` 在函式內、對整篇、片段過濾之前比對;對到格式壞的回 2 給 kill-rm 指令;S1 補三格。
- b2/c9/c5:回傳碼只看判定、拿掉「強證據」;weak 時另印背書不採信;rc 2 時第一行「配方已寫進筆記,試跑沒跑成」、drifted/abort 給 `guard kill --id`。
- i4:測試改成比對前去掉 `--id` 那行,列進〈既有測試〉。
- c3/a5:最近一筆改比 ts(同 ts 取檔內後者),寫明跟背書刻意不同;ts 不帶時區列隱患並綁回頭事件。
- c4/i3:短身分從筆記那條算;`_backing_note_recipes` 多帶 `_recipe`。
- c7/a4/b4:git diff 照 `_lens_git` 三旗標、收 stderr、單次逾時夾剩餘時間(`_lens_git` 加 timeout 參數)。
- c2:標題寫「補強過測試的先重跑」,盲區寫明。
- c8:〈名詞〉配方指的檔改正、PRIOR-ART 拿掉 `_codeloop_record_valid_ex`。
- i5:survived 清單接在 P2 鏈之後、自己的例外保護與訊息。
- i6/a2:閘名另開 `check-p2s`、kind warned。
- i7:共用列表收 `dup_note` 參數。
- i8:新增〈測試怎麼造〉。
- i9/a7:文件清單補 INDEX、reference(含 slim)、說明字典與 argparse、「不改它」兩句。
- i10/a3:④ 用修正關卡樹裡那份設定與釘不住版本的判定;後段回 2 時提醒不印寫明。
- a1:`result_out` 字典;a6:`_kill_note_skipped`、P 段內嵌不動;a8:dest `gk_id`/`gk_try`,`--id` 只收重複不收逗號;a9:鎖外直接算身分、`warn_box` 不改。

### 折後鏡像核對(sonnet 一席,只看本輪 diff 加席報告目錄)

32 條逐條對過:31 條已處理、1 條部分(i3 附帶點:帳本對回的知識庫可能不是 doctor 掃的那個)→ 補進 ③。另抓 5 處文字前後不一,全改:依據的 rtb 編號跟〈做法〉①–④ 撞號、REVISIT 的 F7 沒定義;`--try` 的 weak「一定 / 幾乎一定」統一成一定,S2 那句改成「weak 是 true 時」;kill-rm 前段比對沒列成共用函式 → 〈共用的小整理〉補 `_kill_match_prefixes`;〈範圍〉補 `listed`、`_recipe`、`_kill_log_latest`,〈既有測試〉補背書測試;related 補修正關卡計劃。
