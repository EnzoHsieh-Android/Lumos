# r3 收貨紀錄

## 席位收貨

四席報告從逐字稿存,四份都全數錨定(quote-check)。編號:正確性 1–12 記 c1–c12、邊界 1–14 記 b1–b14、整合 1–16 記 i1–i16、架構對齊依報告出現順序 1–12 記 a1–a12(a1 跑不了時擋下跟鄰居放行不同、a2 生效常數名稱、a3 base_replay_skip 沒登記鍵、a4 新事件欄位、a5 提示沒清理與「沒簽」、a6 樹準備第三種做法、a7 覆蓋檔案的做法、a8 判定重寫一份、a9 程式檔第三個定義、a10 表格拆格第三份、a11 沒用 `_real_chars`、a12 落點)。

## 最小實驗(Enzo 裁「先做最小實驗再加開第四輪(推薦)」)

腳本放在會談暫存區(不進 repo),用 `python3.14 -I exp.py <repo>` 跑:載入 scripts/lumos 為模組;`git merge-base HEAD Lumos/main` 取分岔點;`_isolated_worktree(rr, commit=分岔點)` 開推送版那一棵,在 scripts/lumos 加 `_exp_replay_new_fn`、在 scripts/test_lumos.py 加兩支測試(一支呼叫新函式、一支只檢查 1+1==2,斷言用測試程式自己的 `check`);再開分岔點那一棵,只把改過的 scripts/test_lumos.py 複製進去;兩棵各用 `_spec_gate_judge_items` 跑兩支新測試與既有的 `t_git_partial_clone_keys`。

| 測試 | 推送版 | 分岔點 |
|---|---|---|
| t_exp_replay_needs_new_fn | green | red(輸出 `EXCEPTION: module 'lm' has no attribute '_exp_replay_new_fn'`) |
| t_exp_replay_no_dependency | green | green |
| t_git_partial_clone_keys | green | green |

- 分岔點(跟主線):98dbcd775aab。
- 每棵樹跑三支約 8 秒(每支約 2.7 秒,大多是啟動)。
- 平台名不能寫死:舊式單一平台設定的平台鍵是 profile 名(這個 repo 是 python),先用 `load_platforms` 取 `default_platform`。
- 測試程式不認原生 `assert`,沒有 `check` 會判「一條斷言都沒有」(工具自己的防假綠,不是重播的問題)。
- 測試只要跑紅就保留暫存現場(`gctl-run-*`,`--keep-tmp` 只能加不能關);實驗共留下 18 個,都已用字面絕對路徑刪掉。重播在分岔點本來就要紅,所以計劃第 4 點加了「子程序的暫存目錄指到樹底下」。
- 兩棵隔離工作樹離開時都收乾淨(查過沒有 `lumos-exp-*` 殘留)。

## 世界查證

本輪修法多是改用 repo 既有做法(test-guard 的主線分岔點、修正關卡的樹準備、既有判定函式);外部只再確認 GFM 表格列行首最多 3 個空白仍算表格列(上輪已查的 GFM 規則)。

## 依根因分組與去向

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 分岔點取推送範圍起點(第二次推送、標籤、空樹) | c1 c11 b1 b3 i2 i3 | 折:分岔點改成推送版跟主線的 merge-base(`_push_mainlines`),標籤與找不到主線不重播、寫 skipped |
| G2 | 觸發與選計劃(只推實作、程式檔定義、卷證、零條款、調研筆記、Android 測試目錄) | c2 c3 c7 b2 b12 i6 a9 | 折:程式檔改用 `_is_code_file`,測試判定帶 `_nodehome_layout`;只認 _計劃.md 加 type 加至少一條條款;只推實作的漏網寫成天花板六加 REVISIT |
| G3 | 讀工作目錄而不是推送版 | c8 b14 i7 | 折:計劃文字一律從推送版讀;簽核時讀工作目錄(簽的人看的那份),推送前比推送版的指紋 |
| G4 | 樹的準備(設定檔、依賴資料夾、樹外平台根、覆蓋檔案的做法) | c5 b5 i5 a6 a7 | 折:修正關卡的樹準備抽成共用函式;釘不住版本的平台不重播;複製只搬內容、符號連結不複製 |
| G5 | 判定細節(逾時欄位、整套跑的平台、改名、重寫判定、跑不了時擋或放、import 錯誤) | c4 c6 c9 b4 b11 i11 a1 a8 | 折:逾時讀第 6 欄 startswith 超時並抽共用;沒有 {method} 不重播;改名先刪舊路徑;合條款與判定借 `_spec_gate_run_clauses`、`_spec_gate_twoway_run_verdict`;工具壞了照既有約定放行並寫 skipped;import 錯誤印提示、第二批補 |
| G6 | 生效日與開關(created 可改、回退關不乾淨、沒有專案開關、常數名) | c10 b6 b8 i16 a2 | 折:created 與 `_plan_first_commit` 取較晚者;加 `high_risk_evidence` 專案開關;常數改名 `_HIGH_RISK_EVIDENCE_SINCE`;回退改寫三種關法 |
| G7 | 表與簽核(縮排列、跳脫、跳過欄寫不進、事件欄位、提示清理與逾時、簽核進哪個提交、拆格與字數共用) | b7 i1 i12 i13 a3 a4 a5 a10 a11 | 折:表格列認行首 0–3 空白、表後任何縮排的表格列都算錯;先處理跳脫再切格;`base_replay_skip` 進 SCALAR_KEYS 等;row_count、nodes、origin 進欄位型別表;提示過 `_out_clean`、加「沒簽」與 300 秒逾時參數;簽核跟功能提交或併進留痕帳本提交;拆格寫成共用函式、字數用 `_real_chars` |
| G8 | 文件、測試清單、自相矛盾、第二批引用、落點 | i4 i8 i14 i15 b13 a12 | 折:第 10 點補 ARCHITECTURE、心智模型、方法論、svg、SKILL、`_auto_escape`;第 11 點改成在 `_sg_plan` 產生器補 created;r1 那行標成歷史;S1 與 status 對齊;版號不倒退;第二批改引 guard殺傷力驗證 d1 與零依賴;lands_in 補 Systems/代碼審修正關卡 |
| G9 | 效能與資源(冷編譯逾時、沒有總預算、樹重建、排序與快取、Ctrl-C) | c12 b9 b10 i9 i10 | 折:重播專用逾時 900 秒與總預算 1800 秒;多份計劃共用兩棵樹;排在既有檢查之後;不快取寫進〈不做〉;Ctrl-C 照並行路徑收子程序 |

全部 54 條折入,0 條放行,0 條重現不到。
