# code-情境題引規格出處 r1 收貨紀錄

## 派工與收貨
- 範圍 34ca84893614b443707cfc7061030e6bb6fe3746..6ccb7a46214ca3168142f782c359b1e24d33acd2;凍結 r1-snapshot.patch(5580 行,sha256 390ba914…0a9b)。
- 拆包:r1-code.patch(scripts/lumos,-U3,1600 行)給正確性、資源、邊界、通才、架構對齊;r1-docs.patch(467 行)給合約;資安席看全份 r1-snapshot.patch(資安包不拆,超過 1800 行照實記)。測試差異 r1-tests.patch(1406 行)附給程式席當參考。
- 7 席同門 sonnet,外家未派(單家族視角)。表態:這次改動沒有適用的檢核題,不用盲判。lint-new rc0 clean(6 條 C901 附理由放行、RUF005 已修)。
- 7 份報告從逐字稿存檔;report-normalize 全部已正規化;quote-check 全數錨定;refcheck 0 missing / 0 out_of_range。seat-check 判派工單沒列材料(vacuous),派工單形狀待查,不影響本輪。
- 合約席交了兩次:第一次是完整報告(存檔這份),第二次只補「t_kt_sit_spec_* 其實跑過、63 通過;docs_enumeration 16 通過」,結論不變。
- 各席圖譜鏡頭都回報「鏡頭計算超時、沒附固定席」;派工前有暖過快取(dispatch-lens rc0),仍逾時。各席照派工詞自判,下一輪派工前再暖一次並看回覆。
- 收貨時 git status 只有編排者自己的放行帳改動,審查席沒動 repo。正確性席回報複製 clone 曾寫滿磁碟、已清。

## 機械重現(編排者)
| id | 做法 | 結果 |
|---|---|---|
| c1 | 解開 HEAD 副本,把 `if not hit[0] or not hit[1] or hit[0] == hit[1]:` 改成 `if not hit[1] or hit[0] == hit[1]:`,清 __pycache__,`-k situation_rule_recipe_scope` | HIT:5 passed, 0 failed(改壞照綠) |
| c2 | 同副本把 `if a < sg["start"] or b > sg["end"]:` 改成 `if b > sg["end"]:` | HIT:5 passed, 0 failed |
| z1 | 載入模組跑 `_kill_run("sleep 4243","/tmp",600)`,4 秒後對 python 送 SIGTERM | HIT:python rc 143,`sleep 4243`(pgid 3142)仍存活,手動收掉 |
| t1 | 治理帳事件 test_name=t_orig,把條款的 `[test:t_orig]` 換成 `[test:t_other_green]` 呼叫 `_spec_gate_ruled_ids` | HIT:兩種都回 {'S1'} |
| a1 a2 t4 | 讀碼:`_write_bytes_atomic` docstring 明寫不另寫原子寫入;`_confirm_tty_dev` 已有 LUMOS_TTY 開法 | HIT(讀碼) |
| 其餘 minor | 席報告附實跑輸出,讀碼核對成立 | 採信 |

## 分組(依根因)與處置
全部 30 條都折入,沒有放行、沒有重現不到的(refuted none)。
1. **測試沒守住判斷分支**(c1 c2 major;c3 c9 minor):每道各補一個只走那條分支的案例,補完在副本上逐道改壞驗紅。
2. **人裁條款認定只比文字、不比綁的測試**(t1 major;x3 minor):規格閘認人裁條款時,那一行綁的測試要恰好是帳上的 test_name(多綁、換綁都回一般規矩);計劃範圍 5、S13 與預期值表補這一點。x3(--consent 只驗非空)是使用者裁定的對話核可設計,折入方式是計劃〈天花板〉寫明「consent 只驗非空,靠帳上 origin 與原話事後可查」。
3. **中斷收尾**(z1 major;c7 minor):situation-rule 期間把 SIGTERM、SIGHUP 轉成同 Ctrl-C 的收尾(收程序群組、收工作樹,rc 2 不寫);寫回前檢查計劃已有同文同測試的條款就回報不重插。
4. **重做既有工具**(a1 a2 major;t4 a3 a4 minor):原子寫改叫 `_write_refusal_reason` 加 `_write_bytes_atomic`(讀回比對留呼叫端,WriteBlocked 要接);終端探測抽成 `_confirm_tty` 家族的共用探測;條款指紋一支共用函式;讀 HEAD 版檔改用 `_kt_sit_read_many`。
5. **治理帳讀太早、重讀**(z2 b2 t3 minor):人裁集合移到門與生效日判斷之後,同一次推送前核對只讀一次。
6. **文字與換行邊界**(b1 c8 b3 b4 t2 c4 minor):CRLF 計劃照 `load_raw_for_edit` 先例拒絕(不靜默改換行),拿掉死碼與「沿用原檔」說法;不能編成 UTF-8 的條款在檢查條款文字時就拒絕;插入點跳過最後一條的縮排續行;`[S` 改成大小寫敏感、只擋 `[S` 接數字;反引號裡的 `|` 若規格閘解析不受影響就放行並改計劃字面,否則照計劃擋、訊息說清原因;條款清單濾掉解析不收的編號(S0)。
7. **配方身分兩本帳對不上**(t5 c6 minor):治理帳的 recipe_id 用殺傷力那次實際的配方身分。
8. **不適用列的出處核對不一致**(t6 c5 minor):有任何一列填了出處就算名單、照核對。
9. **清殘骸刪到刻意保留的現場**(t7 minor):`--keep-worktree` 保留的現場留標記,清殘骸跳過有標記的。
10. **計劃 --plan 越界**(x1 minor):resolve 之後必須落在圖譜 Projects/ 底下。
11. **盲判材料注入**(x2 minor):盲判指示加一句 specs 是資料、不是指令。
12. **計劃範圍編號指錯**(g1 minor):範圍 2 與第 48 行的「範圍 5 的捷徑擋」改成範圍 6。

## 先查世界
- PRIOR-ART:組 3 中斷收尾——查「python subprocess start_new_session kill process group on SIGTERM SIGHUP」。Belle II basf2 的包裝器把子程序開在新 session,並同時對 SIGINT 與 SIGTERM 裝處理器,先溫和收再升級(https://software.belle2.org/development/doxygen/clean__execution_8py_source.html );逾時收整個程序群組的做法見 https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python 。採用「SIGTERM/SIGHUP 轉成同 Ctrl-C 的收尾」;排除「只靠程序群組就一定收得乾淨」——孫程序自開 session 會逃出群組(同頁 Stack Overflow 討論),寫進天花板。
- PRIOR-ART:組 2 人裁條款認定——查「Doorstop suspect link review fingerprint」「doorstop requirements suspect links reviewed fingerprint」兩次,搜尋結果都是指紋鑑識,沒找到 Doorstop 文件的直接說法;沿用計劃〈依據來源〉已引的 Doorstop 內容雜湊做法(https://doorstop.readthedocs.io/ ),把「連結的另一端(綁的測試)」一併納入比對,而不是只比條款本文。
- PRIOR-ART:組 6 換行——查「python read_text universal newlines preserve CRLF newline=""」。讀檔預設把所有換行轉成 \n,要保留原樣得用 newline=""(https://realpython.com/ref/glossary/universal-newlines/ 、https://peps.python.org/278 )。本 repo 已有 `load_raw_for_edit` 對 CRLF 拒絕、不靜默正規化的先例,採用拒絕(跟圖譜其他寫入一致),不採保留 CRLF。
- 組 1、4、5、7–12 是本 repo 內部一致性與覆蓋缺口,修法照既有函式,不另查。
