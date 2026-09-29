# r1 收貨紀錄(code-存量漂移防線乙)

凍結材料:r1-snapshot.patch(ac5c7ccf..e8f17913,scripts/ 與圖譜筆記、考卷目錄,1315 行,sha256 f18690f2…);另給 r1-snapshot-code.patch 與 r1-snapshot-tests-notes.patch 兩份拆開版方便讀,記帳的 reviewed 用整份的指紋。
分級:守衛面(推送閘),照 high 審。
7 席:正確性 opus;併發、邊界、圖譜一致、架構對齊、資安 sonnet;外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒,從 clone 目錄啟動)。

## 席位收貨

- 7 席全交,等完成通知、ls 確認後才讀;clone 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 7 份皆已正規化;quote-check 7 份引句全錨定。
- 發現 30 條(正確性 8、外家 9、邊界 2、併發 2、架構對齊 5、圖譜一致 4、資安 0),沒有 blocker;major 14 條(機械數各報告的 severity 行)。
- 規則:本輪有 major,accepted 必須是空的,30 條全折。

## 機械重現(在舊版 e8f17913 的 scripts/lumos 上跑;指令稿在編排者的暫存區,結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1(沒副檔名的程式檔) | 建 repo,scripts/tool 開頭 #! 的 Python;_ProbeTree.one("symbol","scripts/tool::cmd_old") 與 "cmd_old" | HIT:兩個都 False |
| 正確性 F2(-diff 屬性) | .gitattributes 標 src/gen.py -diff,推送加 class Foo;_probe_changes | HIT:added_text 是空字串、code_shape False |
| 正確性 F3(要處理的修法提示) | 讀 _drift_report_must:must 不空就印改預告句,不分種類 | HIT:讀碼確認,probe 發現也印預告句修法 |
| 正確性 F4 / 外家 F9(set 第③項不看舊狀態) | 非 git 圖譜,P doing、Issue 寫 =doing\|done,lumos set P status done | HIT:印「第 9 行的 status 條件因這次收尾成立」 |
| 正確性 F5(不是 git 專案的 status 條件) | 同上圖譜跑 drift scan --json | HIT:findings 空,problems 列「判不了(git 讀不出程式檔)」 |
| 正確性 F6 / 外家 F8(E5 雙反引號) | E5 的輸入(只剝 INLINE_CODE_RE)對 ``REVISIT:[when-file:x.py][by:2020-01-01] 範例`` 判 cond;_probe_lines 同一行 | HIT:E5 判 cond、_probe_lines 回空 |
| 正確性 F7 / 外家 F3 / 邊界 F1(路徑沒正規化) | _probe_value_err("file","./src/a.py") 與 one("file","./src/a.py");NFD 的 src/café.py 對 NFC 樹 | HIT:文法放行、判定 False;NFD 判 False |
| 正確性 F7 後半(型別::方法) | 讀 _probe_named_err 與 _drift_probe_scan:路徑段不存在不列問題 | HIT:讀碼確認,scan 不列 |
| 正確性 F8 / 外家 F7(改寫檔沒帶期限) | 解析 rtb-2026-09-28-probes.json 五題的 [by:] | HIT:A7、B3、B4 為 None,exam 照考成擋到 |
| 外家 F1 / 架構對齊 F5(字串裡的 def) | _ProbeTree.one("symbol","launch"),語料是三引號字串裡的 def launch | HIT:True |
| 外家 F2(status 指到讀不出的筆記) | Env.from_texts unreadable=["Projects/P.md"],one("status","Projects/P=done") | HIT:False(應為判不了) |
| 外家 F4(推送範圍的舊開頭欄位) | valid_under 已有一句,正文新寫同一句;_notelines_new keep_other=True 推送範圍 | HIT:第 5 行(舊的 valid_under)被算成 other 新行 |
| 外家 F5(工作目錄模式讀 index) | 沒追蹤的新檔與刪了沒 stage 的舊檔,_ProbeTree(root,"disk") | HIT:新檔 False、刪掉的 True |
| 外家 F6(scan --budget) | lumos drift scan --budget 1 | HIT:「擋下:不認得這幾個參數:--budget 1。」rc2 |
| 併發 F1(預算與重複列樹) | 掛 _nodehome_git 計數跑 _drift_check_core(一條條件式、兩個提交) | HIT:ls-tree 5 次,起點列 3 次、終點列 2 次 |
| 併發 F2(帶路徑仍整批讀) | 5 支測試檔,one("test","tests/test_0.py::test_x"),記 cat_blobs 批次大小 | HIT:[5] |
| 圖譜一致 F4(code_shape 沒排 governance/) | 只新增 governance/eval/x.py,_probe_changes | HIT:code_shape True |
| 邊界 F2(where=None 死分支) | grep _ProbeTree( 三個呼叫點 | HIT:沒有呼叫點傳 None |
| 架構對齊 F1–F4、圖譜一致 F1–F3 | 結構與文件一致性,讀碼與筆記對照 | HIT:讀碼確認各處描述屬實(F4 另見上面 name-status 計數) |

## 判讀與處置

- 全部折進程式與筆記。先寫回歸測試 t_drift_code_review_yi_r1_regressions(24 條 check,新介面在舊碼上不存在,整支紅),並把 [S2] 那支 t_drift_unknown_blocks_check_not_scan 補上乙的一半(圖譜一致 F3);修完做 21 個改壞檢查,逐一確認對應的 check 會翻紅;第一次跑「算新增行不帶 --text」那個沒紅——測試同一次推送也新增了別的程式檔,候選被另一條路觸發,測不出這一條;把 -diff 那個情境拆成單獨一次只改那支檔的推送後翻紅。
- 觀察與判準分開驗:
  - 正確性 F1 的現象屬實;它的判準是「語料要收沒副檔名的程式檔」。實際修法多一步:候選篩選(新增行、程式檔形狀改變)跟語料共用同一支判定,不然推送改了 scripts/lumos 的新增行照樣看不到(同一個缺口的另一半,回歸測試 C1 的不帶路徑那條)。
  - 併發 F2 的判準「帶路徑只讀那一支」照做;正確性 F1 第 4 點(test 指到非測試檔)同一個修法解掉——作者明寫了哪支檔,就讀那支,不再用分類排掉。
  - 外家 F1 與架構對齊 F5 同一件事:改用 ast(跟 _py_declared_methods、_lens_py_defs 同一種做法);語法壞掉的檔退回原本的正則,不讓一支壞檔把整批條件變成判不了。
  - 架構對齊 F3(ok 旗標)與正確性 F5(status 不需要 git)一起處理:樹物件改成列不出路徑就不建(回 None,跟 _nodehome_side 一樣),status 條件搬出樹物件、只看筆記。邊界 F2 的死分支隨之消失。
  - 架構對齊 F4 與圖譜一致 F1:範圍改動只跑一次 name-status,交給共用的 _nodehome_name_status(加一個可選的狀態字母輸出),筆記改名對照也從這一次拿,不再另起 git。計劃 PRIOR-ART ⑧ 原本寫借 _notelines_range_added 的內部改名追蹤,改寫成實際做法與原因。
  - 併發 F1:同一個提交的樹清單加記憶(只記完整提交編號);列樹、起點圖譜、每條候選之前都看預算。
  - 正確性 F7 後半(型別::方法)是文法本身的定義;修法是 scan 在「路徑段不像檔案路徑」時列成問題,不改文法、不擋還沒建的檔。
  - 外家 F4:推送範圍裡開頭欄位其他欄的行,另對一次範圍淨差異的行號;只在第一層(keep_other)多一次 diff,第二層不受影響。
  - 正確性 F8 / 外家 F7:改寫檔補上期限(B3、B4 照原文日期,A7 原文沒日期、比照同主題的 B4),exam 先用第一層同一套文法驗改寫檔;重考結果不變(擋到 8、點到 3、漏 0、誤列 1)。
  - 架構對齊 F2(命名):只被 drift 用的幾支改掛 _drift_ 前綴;_probe_parse、_probe_lines、_revisit_split 這些四處共用的維持原名。
  - 圖譜一致 F2:計劃 PRIOR-ART ⑥ 改寫成實際用的那一對行級函式。
- refuted 無;accepted 無。
