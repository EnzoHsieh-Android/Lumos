# r2 收貨紀錄(code-存量漂移防線乙)

凍結材料:r2-snapshot.patch(r1 折入的修正差異 e8f17913..123aaf47,git diff -U10,含 scripts/lumos、scripts/test_lumos.py、圖譜筆記、考卷改寫檔;1500 行,sha256 4f110e1d…)。
分級:守衛面(推送閘),照 high 審。只審修正差異,全新 7 席(沒有 r1 的任何一席)。
7 席:正確性 opus;併發、邊界、圖譜一致、架構對齊、資安 sonnet(Sonnet 5.5);外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒,從 clone 目錄啟動)。

## 席位收貨

- 7 席全交,等完成通知、ls 確認後才讀;clone 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 7 份;quote-check 6 份全錨定。資安席 3 句錨不到:它把換行寫成字面的 `\n`、把引號寫成 `\"`;照紀律不改報告,到它自己標的快照行號(521–523、626、681–682)機械核對,三句都逐字在,照採信。資安席這輪 0 條發現,這三句都在「看過、沒問題」的段落。
- 發現 19 條(正確性 5、邊界 4、併發 3、外家 3、架構對齊 3、圖譜一致 1、資安 0);blocker 1 條(邊界 F1),major 6 條(正確性 F1、邊界 F2 F3、併發 F1 F2、外家 F1)。
- 同一件事被多席報到的:表態指令印成 `c1|probe`(正確性 F5、圖譜一致 F1、外家 F3);反斜線路徑(正確性 F2、邊界 F3);BOM(正確性 F4、邊界 F2)。
- 規則:本輪有 blocker 與 major,accepted 必須是空的,19 條全折。

## 機械重現(在審的那一版 123aaf47 的 scripts/lumos 上跑新的回歸測試 t_drift_code_review_yi_r2_regressions;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 邊界 F1(深巢狀檔讓整支當掉) | _drift_py_names 餵「註解裡有名稱 + 20 萬個 - + 1」 | HIT:丟 MemoryError('Parser stack overflowed…'),沒接住 |
| 正確性 F1(候選沒跟上判定) | src/api.py 只刪包住 def 的兩行三引號;bin/tool 只在第一行加 #!;各跑 drift check | HIT:兩次都 rc 不是 1、輸出沒有那一行 |
| 外家 F1(單一檔讀不到當不成立) | 批次讀一律回 None,one("symbol","src/api.py::new_api") | HIT:False(應為判不了) |
| 外家 F1 第 2 點(筆記讀不到當不存在) | 同上,_drift_tree_env 建圖譜 | HIT:notes 是空的 |
| 外家 F1 第 2 點(NFD 檔名) | git 裡以 NFD 存 src/café.py,one("symbol","src/café.py::cafe_fn") | HIT:stored_nfd=True got=False |
| 正確性 F2 / 邊界 F3(反斜線 ..) | _probe_parse 對 `file:..\x.py`、`symbol:..\a.py::f` | HIT:errs 都是空的 |
| 正確性 F4(BOM 的 Python 檔) | src/b.py 開頭 BOM,docstring 裡有 def ghost_b | HIT:(real_b, ghost_b) = (False, True) |
| 邊界 F2(BOM 的 #! 腳本) | scripts/runner 開頭 BOM + #!,不帶路徑找 cmd_bom | HIT:不是 True |
| 併發 F1(工作目錄讀檔不看預算) | disk 樹把 deadline 設成已過,one("symbol","real_b") | HIT:回確定答案,不是 None |
| 併發 F2(帶路徑的條件逐檔開 git) | 4 行各指不同檔的條件,數 _nodehome_cat_blobs 的呼叫 | HIT:[1, 1, 1, 1] |
| 正確性 F5 / 圖譜一致 F1 / 外家 F3(c1\|probe) | _drift_report_must 同時給 c1 與 probe | HIT:印出 `--kind c1\|probe` |
| 正確性 F3(重放第③項) | 計劃 doing、Issue 寫 when-status P=done,_drift_exam_replay | HIT:set() |
| 外家 F2(--budget inf/nan) | drift scan --budget inf、--budget nan | HIT:rc [0, 0](inf 在 git 呼叫時才炸、nan 讓預算失效) |
| 併發 F3(淨差異一律先算) | 只改正文的兩個提交,_notelines_new keep_other=True,數範圍那次 diff | HIT:多跑了一次 |
| 邊界 F4(像不像檔名) | _drift_probe_path_warn 對 v1.2::x、Makefile::build | HIT:v1.2 不列;Makefile 的提示沒講還沒建 |
| 架構對齊 F1(自寫 #! 判定) | grep 語料那段 | HIT:`self._text[p].startswith("#!")`,沒用 _head_is_shebang |
| 架構對齊 F2(自寫 python 判定) | grep _drift_probe_is_py | HIT:另一套首行判法(沒 #! 門檻、轉小寫) |
| 架構對齊 F3(快取淘汰跟鄰居不同) | grep _DRIFT_LS_CACHE | HIT:滿 8 筆整包清空,沒寫為什麼 |

16 條測試斷言在舊版全紅(0 passed, 16 failed),另外 3 條架構對齊是結構問題、用讀碼重現。

## 處置

- 全部折進程式與筆記。回歸測試先寫(在舊版全紅),修完做 14 個改壞檢查,每一個都確認對應的斷言翻紅;最後為了過新增告警閘又拆了兩支函式,改壞檢查整批重跑一次,仍然 14 個全紅。
- 觀察與判準分開驗:
  - 正確性 F1:現象屬實。它建議借 _ns_became_code;沒照這個做,因為那只補「加 #!」一種,補不到「只刪三引號」。改成換形狀:不帶路徑的條件看「這次改到的程式檔在終點的全文」有沒有這個名稱。要處理只看終點成立,所以只要終點;原本算新增行的那次 diff 一起拿掉,r1 的 -diff 屬性那個坑也跟著消失。這是同一類發現連兩輪被抓,照「同類兩輪換形狀」處理。
  - 外家 F1:單一檔讀不到算判不了;筆記讀不到建成讀不出的筆記;讀到 None 時換成 NFD 路徑再讀一次(只多一次行程)。不帶路徑的條件找到定義就算成立,找不到而語料裡有讀不出的檔才算判不了。
  - 邊界 F1:MemoryError、RecursionError 跟語法錯一樣退回正則。
  - 正確性 F4 / 邊界 F2:讀程式檔改用 utf-8-sig(全庫讀取器本來就這樣)。
  - 正確性 F2 / 邊界 F3:正規化之後再驗一次文法;`.` 本身也算不合法的路徑。
  - 併發 F1:工作目錄模式每支檔之前都看預算。
  - 併發 F2:scan 與 check 在評估前,把帶路徑條件指到的檔每一版一次讀完。
  - 併發 F3:範圍淨差異改成用到才算(開頭欄位其他欄真的有一行對上逐提交新增的文字時才跑),git 失敗時整次回 None,跟原本一樣。
  - 正確性 F3:重放的第③項改用改之前的圖譜算,跟 lumos set 一致。
  - 外家 F2:--budget 要是大於 0 的有限數。
  - 正確性 F5 / 圖譜一致 F1 / 外家 F3:表態指令一種一行。
  - 邊界 F4:副檔名要字母開頭(v1.2 不算);提示裡講明還沒建的根目錄檔(Makefile)不用管。
  - 架構對齊 F1:語料的 #! 判定改呼叫 _head_is_shebang。
  - 架構對齊 F2:抽出 _shebang_line_is_python,派工鏡頭的 _shebang_python_blob 與這裡共用;這裡因此多了 #! 門檻、少了轉小寫。
  - 架構對齊 F3:行為不改,在快取旁邊寫明為什麼要設上限(鍵是提交編號,exam --history 一次走上百個提交)。
- 筆記:Systems/存量漂移守衛 的 -diff 那條 PITFALL 改寫成兩輪的來龍去脈,新增深巢狀、BOM、讀不到算判不了三條,路徑正規化那條補「正規化後再驗」;〈跟設計稿不一樣〉新增候選判法一條、改寫「不像檔案路徑」一條;計劃〈做法〉第 0 節的候選定義與 git 次數、第 2 節的正規化同步改。
- 驗證:回歸測試 yi_r1 + yi_r2 共 40 條綠;相關子集 drift 229、revisit 18、note_shape 113、note_audit 175、lens 213、shebang 28、set_plan 10,全綠;python3.9 跑 drift scan 正常、--budget inf 回 2;考卷重考(python3.9)不變:擋到 8、點到 3、漏 0、誤列 1。
- refuted 無;accepted 無。
