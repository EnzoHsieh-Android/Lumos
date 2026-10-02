severity: minor

審查範圍:r2-delta.patch 全 503 行逐 hunk 讀;在 `git clone --shared` 的臨時目錄(code-tb-r2/w)對真代碼做實驗。五支新測試與 S20 相關測試都跑過(全綠),另做三個變異(各自翻紅,見測試節)。

## F1 帳本 new 的「名稱所在行」用子字串找,名稱是別人的子字串、或帶前綴的寫法跟切分後不一致時會記錯
severity: minor
blocking: 否
引句:「hits = [i for i in span if nm and i <= len(lines) and nm in lines[i - 1]] or span」
file: `scripts/lumos:28955`(`_ns_tr_is_new`,臨時目錄同位置)與 `scripts/lumos:28643`(`_test_names_of` 把全形冒號換成半形、去掉前綴後的空白)

1. 名稱是另一個名稱的子字串:摘要條目兩行,第 2 行(舊)`[test:t_a]`、第 3 行(新寫)`[test:t_ab]`。對 `t_a` 呼叫 `_ns_tr_is_new("t_a", [2,3], lines, {3})`,兩行都含 `t_a`,hits=[2,3],回 True;實際 `t_a` 在舊行,應為 False。已跑出 True。
2. 前綴寫法被正規化:`_test_names_of` 把 `ios:TestFoo`(半形、無空白)切出來,但原文若是 `ios：TestFoo`(全形冒號)或 `ios: TestBar`(冒號後空白),`nm in line` 為假,hits 為空,退回整條 span。條目第 9 行(舊)`ios：TestFoo`、第 10 行(新)有別的名稱時,`_ns_tr_is_new("ios:TestFoo",[9,10],lines,{10})` 回 True;實際在舊行。已跑出 True。
3. 影響:只影響帳本 `items[].new`(RETIRE-IF 第②條要用的量),且兩種都是往「誤報為新」的方向錯;不影響擋不擋。第一輪要修的就是「續行新加的名稱記成舊行」的反向問題,這裡在多行條目裡仍會有誤差。
4. 建議:找行時用單字邊界(名稱前後不是識別字元),且比對時把原文的全形冒號與前綴後空白同樣正規化;或讓 `_test_names_of` 多回名稱在 raw 值裡的原樣。

## F2 計劃筆記與改後的代碼不一致:〈做法〉8 寫「check 欄照既有判法不變」,代碼這輪加了 check
severity: minor
blocking: 否
引句:「`check` 欄照既有判法不變。提交時被單次跳過時」
file: `docs/lumos-toolchain-knowledge/Projects/筆記測試綁定要存在_計劃.md:68`;代碼端 `scripts/lumos:29008`(`_ns_tr_add_extra` 寫 `ex["check"] = "+".join(...)`)

1. 計劃正文仍說 check 不變,實作已是 `test_refs` / `shape+test_refs` / `slots+test_refs`;下一個只讀計劃的人會以為帳上沒有這個欄位值,依 check 去重(`scripts/lumos:8024` 的去重鍵含 check)也會被誤判成「不變」。r1 折入紀錄(行 130)有寫「帳本補 check 欄」,但〈做法〉本文沒改。
2. 同族:〈做法〉3 第 2 項、〈做法〉5 沒寫「合約行佔位字、空方括號、`[test-gone:]` 說假話照查、條款行免佔位字」;行 43 只說「這兩種行上的測試名本案不驗存在;但標了作廢…」,與 `_ns_tr_test_viol` 現在的行為(條款行免佔位字、合約行查佔位字)只靠 r1 紀錄補,沒進本文。
3. 另一個小處:`_ns_test_refs_collected` 的說明字串寫「資訊 {"new": {(路徑, 行號): 在不在新寫行上}}」(`scripts/lumos:28965`),鍵現在是 `(路徑, 行號, 名稱)` 三元組。

## 逐題看過、沒找到洞的部分
- 實體行號清單:摘要區塊接 `decisions:` 時,`_notelines_regions` 把 decisions 行標成 decisions/other,span 只收 region 為 summary 的行,不會吃到。我造了 `summary: |-`(含空行、最後一條有續行)後接 `decisions:` 的筆記,得到 span `[5]`、`[6,7,8]`、`[9,10]`;最後一條停在 10,沒進 decisions。單行 summary 的條目 span 只有鍵行本身,正確。條目間空行會併進前一條 span,但空行不含名稱,無影響。
- 規則範圍:合約行作廢+有活測試仍報「作廢的條目還掛活測試」;合約行帶佔位字報佔位字;合約行同時帶 `[test-gone:活測試]` 報「測試還在」;條款行佔位字免查、作廢條款帶佔位字也不報(行為小瑕疵但屬設計先行的延伸,不構成錯)。正文散文空 `[test-gone:]` 不算,已實測。
- 保險先看:CI 只在 push 事件跑這步(`.github/workflows/ci.yml` 的 note-shape 步 `if: github.event_name == 'push'`),checkout 預設 HEAD 即推送 SHA,不會因 HEAD 對不上而降級;測試 ② 顯示「沒違規也印提醒」是設計(r1 F6)。副作用是推非目前簽出分支時,碰到含 `[test` 的筆記就會印「只提醒不擋」,即使沒違規——訊息措辭對無違規的情況有點誤導,但不改判定,不標。
- check 欄併值:`_ns_skip_slot_extra`、`_note_shape_report` 的 slots、shape+slots、純測試綁定四種組合讀碼與測試 ①②③ 都對;`lumos gov` 去重鍵含 check,所以同提交同節點的「形狀擋」與「測試綁定」事件現在會分成兩筆,這是想要的方向,沒發現反而折錯的輸入。
- doctor S20:`env_text` 對記憶體 Env 與磁碟都能讀(磁碟端同為 utf-8-sig);整行 `_esc_clean(..., _DOCTOR_LINE_MAX)`。本 repo 跑 `doctor --verbose` S20 正常列出 19 條指不到與 32 條佔位字/空。

## 測試是否空轉(變異驗證,每次還原)
- 把 `_submodule_hit` 的「列不出就回 None」改成回 False → `t_note_shape_test_refs_git_fail_and_guard` ① 翻紅(「('no', ...) []」)。
- 把保險那行改成 `why = None` → 同測試 ② 翻紅。
- 拿掉「正文只留非空 test-gone」那段 → `t_note_shape_test_refs_scope_consistency` ① 翻紅。
- `line_attribution` ①②:修前的算法(看條目第一行)在 ①②會得到相反值,夾具確實走到被修的路徑;`check_key` ①②③ 斷言直接比 `ev.get("check")`,夠緊。
- 缺口(不標):沒有測「作廢的條款行帶佔位字」與「名稱互為子字串」的測試,後者即 F1。

## 圖譜固定席
這次沒附固定席節點(鏡頭計算超時),不逐條答。從我讀到的筆記看,唯一牽連的是計劃筆記本身(F2);沒看到 diff 破壞其他節點宣稱的合約。

最高等級:minor,blocking 共 0 條
