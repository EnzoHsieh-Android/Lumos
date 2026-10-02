preflight-4: ran

# 筆記測試綁定要存在 r1 收貨紀錄

## 前掃(2026-10-02,sonnet 一席,報告 r1-preflight.md)

①未定義的詞(14)、②壞引用、③範圍矛盾、存在類:全部直接改進計劃,不算 findings。
- 〈名詞〉補 note-shape/筆記內容閘、單次跳過、治理帳、rtb、Check T、doctor S5、佔位字、活測試;rtb 的提交編號標明是 rtb 的。
- 量測數字照前掃重算改正:26 個 = 4 待補 + 12 範例(bad-name)+ 7 其他 fake + 3 dangling(原寫 11/12/3)。
- 測試名前綴照鄰居改 t_note_shape_。
- 散文撤除擋不到寫進〈範圍〉不做與〈實務隱患〉。

④語意類(修改前 → 後):
1. ★動到做法★ 判「新」的單位:「新寫的行」→「新加的測試名」(起點版本同篇沒有的名稱)。依據:`_notelines_new`/`_notelines_range_added` 以 diff 新增行為準,改舊行任何字整行算新寫,原寫法會擋舊行原有的壞名字,與「舊的不擋」矛盾;改後也收掉升級前提交被當新寫的問題。
2. ★動到做法★ 規則的開關與帳本:「跟 note-shape 其他規則同一處讀、違規照既有」→「自己一組:`_note_shape_test_refs_parse`、自己的違規清單、事件帶 `test_refs` 欄位、單次跳過也記」(照 `note_shape.slots`)。依據:既有 viol 只受總開關、帳上沒有規則欄位,RETIRE-IF 量不到。
3. ★動到做法★ 作廢標記:「`[被取代:]` 或 `[status:superseded]`」→「只認 `[status:superseded]`(`_ns_superseded`)」。依據:單有 `[被取代:]` 程式不視為作廢。
4. `[test-gone:]` 提交檢查:「提交在 repo 裡」→「至少 12 碼、在分支歷史上(照 `_pin_commit`),淺層判不了略過」。依據:筆記內容閘 PITFALL 記過只查物件存在會被 commit-tree 捏造繞過。
5. 圍欄:「照既有新增行抽取的區塊判定略過」→「用 `_visible_lines` 略過;反引號用 `_strip_inline_markup`(未閉合之後整行不認)」。依據:既有區塊只有 body/summary/decisions/other,沒有圍欄。
6. doctor 段:「`--ci` 記事件」→「不寫帳(照 S17–S19)」。
7. 合約行說法:「已驗存在並真跑」→「Check T 驗存在,波及到的才由推送前合約測試閘真跑」;條款定義行限計劃、行首 `[SN]`。
8. 佔位字:改成字面判(`待補` 在本 repo 判 fake 不是 dangling),改法照前綴分(防回歸無只對 PITFALL)。
9. `[test-gone:]` 登記進格子鍵表、PITFALL 三選一變四選一(否則照指示改寫後被格子規則擋);新增條款 S15。
10. 補:索引建不起來 fail-open(S10)、總開關優先序(S12、S13)、帳本欄位(S14)。

## 派席前跟筆記格子會談對齊(2026-10-02,同意形狀)

折進〈做法〉8:三選一寫死的三處一起改;`slot_check` 只驗形狀、歷史那半放本案;已作廢的行格子照慣例跳過;`test-gone` 不進 `_SLOT_NEW_ONLY`(編排者決定,理由在計劃);筆記格子那篇計劃一起改。改完才重新凍結 r1-snapshot.md。

## r1 席報告收貨(2026-10-02,4 席)

機械:四份 report-normalize 已正規;quote-check --spec r1-snapshot.md 四份全數錨定;refcheck 全 ok。

編號:c1–c13 = r1-正確性-opus.md F1–F13;b1–b10 = r1-邊界-sonnet.md F1–F10;i1–i11 = r1-整合-sonnet.md F1–F11;a1–a6 = r1-架構對齊-sonnet.md F1–F6。blocking 25(c 9、b 10、i 5、a 1)。

### 重現

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 / b4 / i2 | `_mk_kill_env` 換多平台設定,`_classify_test_refs("[test:bad:TestLimitFive, t_new_missing]")` 對照逐名送(scratchpad/tbrep.*/r.py) | HIT:整行只回一筆 bad-name,t_new_missing 被吞;逐名送分得出 dangling |
| c4 / b6 / i1 | 讀碼:單平台設定下平台根是 repo 根,`git status --porcelain` 連暫存的筆記也算改動 | HIT(讀碼;席位實測) |
| c6 / b5 / i4 | 席位實測:平台根不存在或沒設平台時索引不丟例外、名稱全判指不到 | HIT(席位實測,讀碼核對 `_platform_test_index` 不驗根) |
| c8 / c9 / b8 / b9 / i11 | 讀碼:`[test-gone:]` 只驗提交在分支上——同提交刪測試寫不出編號、壓提交後編號不在分支、任意提交加假名稱也過 | HIT(讀碼) |
| c2 / c3 / b3 / b10 / i3 / i8 | 讀碼:起點按同路徑找、新寫行減整篇、實體行為單位 | HIT(讀碼;正確性席實測改名與搬行) |
| c7 / b1 | 席位實測:`[Test:x]`、全形冒號、名稱包反引號滿足格子 PITFALL 卻抽不到 | HIT(席位實測) |
| 其餘 minor 與 a1–a6 | 讀碼核對席位引的行(refcheck 全 ok) | 採信 |

### 處置

全折(40 條),無放行、無駁回。根因三組換形狀(見計劃〈審計修正紀錄〉r1),其餘照補。PITFALL 四選一這點本輪改回不改(測試刪了就是沒有守衛,要表態防回歸無),已告知筆記格子那邊的會談,它同意,並補充:舊 PITFALL 行只把 `[test:X]` 改成 `[test-gone:X]` 時格子走舊行判定,不會因少了三選一被擋。

### 折後鏡像核對(sonnet 一席)

40 條:29 已處理、11 部分處理(c5、c13、b1、i5、i6、i9、i10、a2、a3、a4、a6)、0 沒處理 → 11 條補齊:判存在改成「工作目錄與被檢查版本兩邊都說有/都說沒有才算」(推非簽出分支也不誤擋,1c 與 test-gone 同一套)、帳本 extra 合併與違規種類欄、doctor S20 位置與標題、只掃 summary 不掃 decisions、文件清單(含 03/04/06/INDEX/reference)、抽取器用自己的寬鬆正則與理由、不設上線記號的理由、範本不動(t_slots_single_table 不比選填鍵)。另修前後不一:白話 1c 只擋新寫、test-gone 提交「不驗存在、只驗寫法」統一、PITFALL 改 test-gone 時另寫防回歸、佔位字先於判存在、行號報法、1c 新寫跨篇比、前掃條標明兩點已被 r1 改掉、blocking 數 29→25;做法有條款沒釘的補成 S17–S20,S11、S12 改寫。
