severity: major

# r4 正確性席審查(外部審稿人姿態)

一句白話:這份稿的主幹(從 git 直接重播)站得住,r3 的大部分問題也確實修好了。剩下的洞多在「接縫」。例如新掛鉤配舊工具會悄悄放掉原本的閘,或「對照組」在編譯型語言上一定誤擋,或兩段文字對觸發範圍寫得互相矛盾。

## 上一輪(r3 G1 到 G9)驗證

- G1(分岔點):文字已改成跟主線的 merge-base,但直接推主線的情形仍是繞過(見 7),`_plan_first_commit` 的起點只修了生效日那一處(見 2)。
- G2(觸發與選計劃):程式檔與測試判定已改用既有函式,但「推送範圍」用哪一段沒有統一(見 3),路徑解析沒有指明 `-z`(見 8),觸發條件沒有要求程式檔與計劃相關(見 6)。
- G3(讀推送版):修好了。
- G4(樹的準備):修好了,殘留見 10、12。
- G5(判定):逐支判定已修好,殘留是 keeps 對照組在編譯型語言上的行為(見 5)。
- G6(生效日):殘留見 9。
- G7(表與簽核):殘留見 4、11。
- G9(效能):總預算與逾時有訂,已讀,無 finding。

## Findings

1. 新掛鉤配舊 lumos 時,既有的風險低推送閘會被靜默關掉
   引句:「沒傳(舊掛鉤)就不重播、寫 `base-replay-skipped`」
severity: major
   blocking: 是——照字面實作會把原本該擋的風險低計劃放掉。
   - 稿只處理「新 lumos 配舊掛鉤」。
   - 反方向沒處理:新掛鉤無條件把 `--push-remote`、`--pushed-ref` 接在 `spec-gate --push-check` 後面,舊 lumos 的 argparse 不認得。
   - 我跑過同形狀的 argparse,結果是 `unrecognized arguments`、rc=2。
   - 掛鉤只有 `sg_rc -eq 1` 才擋(rc≥128 才停),rc=2 當放行。所以舊 lumos 搭新掛鉤時,風險低計劃的雙向門推送檢查整道失效。
   - 掛鉤自己的前例是 `grep -q -- '"--keep-going"' "$GRAPHCTL"` 先探旗標再帶。稿的第 10 點只說「升小版號、寫 CHANGELOG」,沒說要探旗標。
   - file: `scripts/hooks/pre-push:479`、`scripts/hooks/pre-push:565`、`scripts/lumos:73612`。

2. 基準重播借用的 `_spec_gate_twoway_static` 內部沿 HEAD 找計劃第一次進歷史,推送版不是 HEAD 時,有 keeps 的計劃會被誤擋
   引句:「重播前在推送版那份計劃上直接呼叫 `_spec_gate_twoway_static`」
severity: major
   blocking: 是——會把合法推送擋下。
   - 該函式有 keeps 時呼叫 `_plan_first_commit(rr, plan_repo_rel)`,沒有起點參數,沿 HEAD 找。
   - 稿的第 6 點替生效日那一處加了「選填的起點參數」,但第 5 點對這個函式只列了「換掉風險低前綴」這一個選填參數,沒要求把推送版傳下去。
   - 重現:HEAD 在 main(或另一條分支),執行 `git push origin feature-x`,feature-x 上有含 `[keeps]` 條款的高風險計劃。
   - 計劃不在 HEAD 歷史裡,`first is None`,印出「這份計劃還沒進 git 歷史,驗不了」並擋下。
   - file: `scripts/lumos:14231`、`scripts/lumos:14194`。

3. 觸發用哪一段推送範圍,稿裡兩處矛盾,實作選哪邊都違反另一邊
   引句:「用推送版對分岔點算 `git diff --name-status -M`」
severity: major
   blocking: 是——第 1 點、S2、S3、天花板六互相打架。
   - 第 1 點的觸發是拿分岔點到推送版的整段 diff 判「改到計劃檔又改到程式檔」。
   - 這樣第一次推完含計劃加程式之後,同一條分支之後每一次推送(包含只推測試或只推文件)整段 diff 仍含兩者,每次都重播。這違反 S2「只推了測試檔不重播」。
   - 天花板六卻寫「實作只推程式、沒動計劃檔的那幾次推送不觸發」,那是用本次增量範圍判的。
   - 既有的 `_spec_gate_push_check` 在 `if not plans: return 0`(用掛鉤傳進來的增量範圍算 `plans`)就提早回傳。把重播排在後面,只能走增量範圍,與第 1 點寫的文字相反。
   - file: `scripts/lumos:16317`、`scripts/lumos:16333`。

4. `signoff --expected` 沒有推送上下文,無法判「這次才完成」,可能造成簽不了又推不上去
   引句:「不是第 1 點那種計劃或表格檢查不過,rc2、不寫」
severity: major
   blocking: 是——會讓流程卡死。
   - 第 1 點把計劃分成「status 是 doing」,或「推送版是 done 而分岔點不是 done」。
   - `cmd_signoff(env, node, note, by, ref)` 只有計劃節點,沒有推送版與分岔點。
   - 代碼審通過後才簽(稿第 8 點明寫「代碼審留痕之後才簽的」),此時計劃多半已改成 `status: done`。
   - 實作若照「status 是 doing」判資格,對 done 的計劃回 rc2「不需要簽核」。推送時 done 加分岔點非 done 又被第 9 點要求簽核,結果簽不了、推不上去。
   - 稿沒有定義簽核資格怎麼在沒有推送範圍時判。
   - file: `scripts/lumos:16533`。

5. keeps 對照組在編譯型語言上幾乎必定不綠,S8 會誤擋
   引句:「分岔點:新行為條款綁的每一支都要紅,keeps 綁的每一支都要綠,弱證據不算」
severity: major
   blocking: 是——在稿的主要場景 Android(Kotlin、Gradle)上,會把合法計劃擋下。
   - 新行為測試在推送版呼叫了新符號,覆蓋進分岔點後整個測試原始碼集編譯失敗。
   - `--tests` 只篩執行,不篩編譯,所以同模組的 keeps 測試一起紅。
   - 這個 repo 判 Kotlin、Java 時 `n is None`,`_spec_gate_verdict` 回 `red if verdict == "red"`,不是弱證據,所以 keeps 在分岔點判「紅」,觸發 S8「重播環境不可信」。
   - 同檔情形一樣:pytest 在檔頭匯入新符號,整檔收集錯誤。
   - 稿只在〈誤擋二〉處理「新測試」的匯入錯誤,沒處理 keeps。天花板四只說「分岔點的紅不分例外還是斷言」。
   - 結果:含 keeps 條款的 Kotlin 計劃,出口只剩整份 `base_replay_skip`。
   - file: `scripts/lumos:15057`、`scripts/lumos:15069`。

6. 已分次合併的計劃,下一次只要碰計劃檔加任何程式檔就被判「舊程式上就綠」
   引句:「只改計劃、卷證、帳本、文件的推送不觸發;只推測試(TDD 先推紅的測試)也不觸發」
severity: major
   blocking: 是——會誤擋正常收尾,而且沒有逐條出口。
   - 觸發條件只要求「改到任一支程式檔」,不要求那支程式檔跟計劃有關。
   - 重現:
     1. 計劃 P 的 S1 到 S3 已隨第一個 PR 合進 main,P 還是 doing。
     2. 新分支從 main 切出,為了追加審計紀錄或把 P 改成 done 而改了 P,同時順手改了一支不相干程式檔。
     3. 分岔點(main)已含 S1 到 S3 的實作,新行為測試在分岔點是綠,判 S6「新行為在分岔點綠」並擋下。
   - 這些測試是計劃建立後才寫的,不能標 keeps(`_spec_gate_twoway_static` 驗「計劃建立前就存在」),唯一出口是整份 `base_replay_skip`。
   - 天花板六只說「同一條分支」的重播會重來,沒處理「前半已在主線」。

7. 直接推主線(分岔點算不出來)整道不重播,而這個 repo 的掛鉤明寫支援主線直推
   引句:「把遠端舊值當成全零,交給推送範圍指令的 `_push_range_start`」
severity: major
   blocking: 是——該擋的放掉,而且是最直接的路徑。
   - 推 `refs/heads/main` 時,`_push_mainlines` 會跳過「就是這次被推的那條」:`refs/remotes/origin/HEAD`、`main@{upstream}`、`origin/main` 全部解到同一個 `refs/remotes/origin/main`,全被跳過。
   - 候選為空,走 `_push_no_mainline`;舊值被強制當全零,回空樹,稿的第 2 點此時「不重播、寫 skipped」。
   - 稿的〈天花板〉只列 `--no-verify` 與沒碰計劃檔的分支,沒列「直接推主線」。
   - 掛鉤註解寫有「分支與 main-direct 同軌」。
   - 只要直接推主線,整道基準重播與簽核檢查都不跑,只留一筆 skipped 事件。
   - 主線預設分支名不是 main 或 master(如 develop)的 repo,也一樣整道不重播。
   - file: `scripts/lumos:64890`、`scripts/lumos:65203`。

8. 觸發與改名處理沒指明 `-z` 與 `core.quotePath=false`,中文計劃檔名會讓觸發悄悄失效
   引句:「用推送版對分岔點算 `git diff --name-status -M`」
severity: major
   blocking: 是——此類計劃永遠不會被觸發,也不會報錯。
   - 我在暫存 repo 驗證:同一份 `Projects/高風險_計劃.md`,預設輸出 `"Projects/\351\253\230...\346\.md"`,加 `-c core.quotePath=false` 才是原樣。
   - 稿寫的指令沒帶這個設定。實作者照字面跑,檔名帶引號與八進位轉義,`endswith("_計劃.md")` 與 `vrel + "/Projects/"` 前綴都比不到。
   - 第 4 點的測試檔改名先刪舊路徑也受影響。
   - 既有同類碼:`_spec_gate_push_check` 自己用 `-c core.quotePath=false`,`_fix_git_z` 用 `-z`。
   - 稿的借用清單沒列這兩支或 `_nodehome_name_status`。
   - file: `scripts/lumos:16317`、`scripts/lumos:21936`。

9. 生效日的第二個來源在淺複製與改名下,不會像稿說的退回只看 `created`
   引句:「淺複製、讀不到歷史時只看 `created`」
severity: minor
   blocking: 否——只是多查,方向與天花板七同向。
   - `_plan_first_commit` 在淺複製裡查到的是淺邊界那個提交(那個提交裡全部檔案都算新增),不是「讀不到」,回傳的是邊界提交。
   - 稿沒要求偵測 `--is-shallow-repository`,所以日期會是邊界提交的日期,晚於生效日,舊計劃被當新計劃。
   - 計劃檔改名後,不帶 `--follow` 的 `git log --diff-filter=A -- <路徑>` 查到的是改名那個提交,同樣變新。
   - 天花板七只列壓過提交與 rebase。
   - file: `scripts/lumos:14194`。

10. 分岔點那棵樹沒有平台根資料夾時,測試跑起來會直接丟例外,掛鉤把它當擋
    引句:「平台根在樹外、沒進版控、是子模組或符號連結的,標成釘不住版本」
severity: minor
    blocking: 否——窄輸入,且可由 `base_replay_skip` 先擋住。
    - 釘版本檢查只看推送版那一側。若這次推送新增了一個平台根(例如新模組資料夾),分岔點那棵沒有該資料夾。
    - `_run_bound_tests` 沿用該根當 `cwd`,`subprocess.Popen(..., cwd=不存在的路徑)` 丟 `FileNotFoundError`,沒有人接。
    - Python 例外退出碼是 1,掛鉤判成「擋下」,違反稿所說「工具壞了不擋所有人」。
    - file: `scripts/lumos:26168`。

11. 簽核逾時參數與拆格敘述有兩處照字面做不出來
    引句:「與選填逾時(簽核預設 300 秒,表要讀;其他呼叫端不傳、照舊)」
severity: minor
    blocking: 否——測試會先紅,不會悄悄做錯。
    - `_waive_origin_tty` 只轉呼叫 `_confirm_tty(prompt, stdin_timeout=True)`。逾時由 `_confirm_tty_timeout()` 讀環境變數 `LUMOS_TTY_TIMEOUT`(預設 30)決定。
    - `_confirm_tty` 沒有逾時參數,稿沒把它列為要改的函式。
    - 實作者只能改全域環境變數(影響別的呼叫端),或再改 `_confirm_tty`。
    - 第 7 點拆格寫「先逐字元掃過…還原…再用沒被跳脫的 `|` 切格」。字面順序是先還原再切,還原後已分不出哪個 `|` 是跳脫的,應該是一次掃過邊還原邊切。
    - file: `scripts/lumos:34193`、`scripts/lumos:34220`、`scripts/lumos:38429`。

12. 兩棵樹同時缺 gitignore 的必要檔時,被判「推送版不綠」而不是跳過
    引句:「兩棵是同一種方式建的,環境壞了兩棵都會壞,不會只讓舊版紅」
severity: minor
    blocking: 否——有 `base_replay_skip` 出口。
    - 樹的準備只補 `.lumos/config.json` 與依賴資料夾。Android 的 `local.properties`、各種 `.env`、簽章檔通常被 gitignore,隔離工作樹裡沒有。
    - 兩棵都跑不起來:推送版判不綠、S7 擋下。這其實是環境不可信,稿在這種「兩邊同壞」時沒有「跳過」的分類,只有「擋」。
    - 〈誤擋一〉只討論測試依賴的資料檔,沒討論建置必要檔。

## 逐節

- 名詞、問題與最小解、調研結論:已讀,無 finding。
- 做法第 6 點的生效開關欄位:專案層 `high_risk_evidence` 沒寫從工作目錄、還是推送版的 `.lumos/config.json` 讀。兩邊不同時行為不定,併入 9 的實作細節,不另立。
- 預期值表 S17 到 S19 的解析規則:除 11 的拆格敘述外,已讀,無 finding。
- 驗收條款、回退:已讀,無 finding。

## 風險類(逐類)

- 金流:無。只動推送前檢查與本機治理帳,不碰收費或扣款。
- 對外送出:無。不寄信、不推播,只讀本機 git 並寫本機帳。
- 不可逆:無。治理帳只追加,隔離樹離開時收掉。唯一的刪除是自己建的暫存資料夾與 `worktree remove --force`,殘骸清掃只動超過一天的同前綴資料夾。
- 守衛面:有,即上面 1、3、5、6、7、8。
- 效能:總預算 1800 秒與單支逾時 900 秒夠用。已讀,無 finding。
- 資源:隔離樹與 `TMPDIR` 隨樹收。無 finding。
- 併發:兩個推送同時重播,各自的暫存資料夾名不同,清殘骸只清超過一天的,不會誤清。無 finding。

## 固定席節點

- `lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間的 body,sentinel 之外 byte-equal 保留):不受影響。稿只在注入範本 `graph-discipline.md` 的 sentinel 內補一句,並升小版號。綁定測試 `t_reinject_preserves_outside` 管的是 sentinel 外面,這個改動碰不到。
- `test-quality-cli`(`scripts/test_quality.py`):不受影響。稿的〈第二批〉明寫「只借不改」,第一批不碰這支檔。
- `Verification/測試品質第四輪修補驗證`:不受影響,同上。

總結:最嚴重為 major,共 12 條,其中 blocking 8 條(1、2、3、4、5、6、7、8)。
