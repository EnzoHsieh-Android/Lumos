severity: major

整合席 r4 報告。逐節讀完整份 spec(含 d1–d6、做法 0–11、驗收條款 S1–S24、回退、實務隱患),對照 `scripts/hooks/pre-push`、`scripts/lumos`、`scripts/test_lumos.py` 與 r3-intake 核對。我跑過兩個小實驗:舊版 lumos 收新旗標,以及對直推主線呼叫 `_push_range_start`。

## 一、blocking 級

1. 新版掛鉤配舊版 lumos 時,既有的風險低推送閘會無聲失效
引句:「pre-push 掛鉤把它手上的 `_PP_REMOTE` 與這個 ref 傳進來」
severity: major
blocking: 是——這會讓每個「掛鉤已更新、lumos 還沒更新」的專案,既有閘無聲關掉。
- 重現:現行 lumos 收到 `spec-gate --push-check HEAD~1..HEAD --push-remote origin --pushed-ref refs/heads/x --repo .`,印「擋下:不認得這幾個參數」,rc=2。
- 掛鉤只在 rc 等於 1 時擋,其餘非零一律放行,所以風險低計劃的留痕測試檢查整道被繞過。
- 那一次輸出裡也不會有「改動風險分級:light」。
- spec 只處理「舊掛鉤配新 lumos」(沒傳就跳過),沒處理反方向,也沒寫掛鉤要像 `--keep-going` 那樣讀檔探旗標。
- spec 做法 10 說「讓舊專案被提示 `lumos update`」,但提示不防止錯開的那段時間。
- file: `scripts/hooks/pre-push:475`(`--keep-going` 讀檔探測的前例,連註解都寫「掛鉤與 scripts/lumos 分開複製,版本會錯開」)
- file: `scripts/hooks/pre-push:579`(rc 等於 1 才擋)
- file: `scripts/lumos:73951`(`--push-check` 的分派)

2. 「推送範圍」有兩種相反的讀法,觸發條件與天花板六、REVISIT 互相矛盾
引句:「推送範圍(用推送版對分岔點算 `git diff --name-status -M`)改到這份計劃檔」
severity: major
blocking: 是——S1、S2、S3 與天花板六不可能同時成立,實作者得自己猜。
- 做法 1 把範圍定義成「推送版對分岔點」(累計差異)。
- 掛鉤實際傳進 `spec-gate --push-check` 的是 `_brange`,一般推送是 `遠端舊值..本地頂端` 的增量。
- 若採累計差異:第二次推送即使只改程式,範圍仍含第一次推上去的計劃檔,每次推送都會重播,天花板六所說「實作只推程式的那幾次推送不觸發」不成立。
- 若採增量:第二次推送的增量不含第一次已推的測試檔,覆蓋進分岔點那棵時缺檔,測試變成「沒跑到」,S3 與第 5 點的覆蓋測試檔都會壞。
- 掛鉤 fallback 時 `_brange` 是「空樹..頂端」,整個 repo 都算被碰到。fallback 包括推標籤、遠端舊值本機找不到(force-push 後常見)、push-range 失敗。這時所有符合條件的風險高計劃都會被選中,連沒在實作的也被要求預期值表與簽核。
- spec 沒說「跳過重播」時預期值表與簽核檢查要不要照跑(S4 只說不重播並寫 skipped)。
- file: `scripts/hooks/pre-push:41`(`pp_range_for` 的空樹退路)
- file: `scripts/hooks/pre-push:490`(`_brange` 的來源)
- file: `scripts/lumos:16317`(`touched` 用的是傳進來的 `git_range`)

3. 重播成功不寫任何事件,REVISIT 與 RETIRE-IF 的分母量不出來
引句:「有幾份從頭到尾沒有任何 `base-replay-*` 事件」
severity: major
blocking: 是——專案鐵則 4 要求回頭條件可執行,這條保證誤報。
- 全 spec 只有四種 kind:`base-replay-failed`、`base-replay-skipped`、`expected-signed`、`expected-unsigned`。「證實」(S5)不落帳。
- 重播一次就通過的計劃,在 2027-02-04 的盤點裡跟「根本沒觸發的漏網」長得一樣,都是零個 `base-replay-*` 事件。「超過三成就重新設計觸發」會被每一份成功的重播灌水。
- RETIRE-IF 第三條「skipped 佔要重播的一半以上」同樣缺分母。
- 要嘛加 `base-replay-proven` 事件,要嘛把兩個條件改成能從現有事件算出來的。

4. 直推主線(推的那條就是主線)永遠算不出分岔點,整道不跑,天花板沒列
引句:「不重播,印一句原因、寫一筆 `base-replay-skipped`(原因欄寫是哪一種)」
severity: major
blocking: 是——支援的推送形狀無聲繞過,不是「工具壞了」的例外。
- 重現:我造了一個有 `origin/HEAD`、`origin/main`、`main@{upstream}` 的 repo,對 `refs/heads/main` 呼叫 `_push_range_start(root, "0"*40, tip, "origin", "refs/heads/main")`。回的是空樹和「找不到主線……或就是這次推的那條」。同樣的 repo 推 `refs/heads/feat` 則回真的分岔點。
- `_push_mainlines` 會跳過「就是被推的那條」,所以直推主線時候選全被跳過。spec 又規定舊值當全零,不能退回遠端舊值。
- 掛鉤自己的註解寫明支援「分支與 main-direct 同軌」。
- 〈實務隱患〉七條天花板沒有這一條。RETIRE-IF 第三條能偵測到,但它是撤除條件,不是已知繞法的聲明。
- file: `scripts/lumos:64902`(`_push_range_start`)
- file: `scripts/lumos:65203`(`_push_no_mainline` 全零回空樹)

5. `_spec_gate_judge_items` 沒列進要加參數的清單,新增的逾時、環境、登記傳不到,總預算也做不出來
引句:「`_run_bound_tests` 加三個選填參數(既有呼叫端不帶,行為不變)」
severity: major
blocking: 是——spec 指定的呼叫路徑與它列的改動對不起來,第 139 點照字面做不出來。
- 第 5 點要求用 `_spec_gate_judge_items` 跑重播。它內部寫死 `_run_bound_tests(rr, items, tails=tails)`,沒有任何參數能穿透。
- `_run_bound_tests` 內部經 `_kill_run` 開程序,而 `_kill_run` 沒有 `env` 參數,`Popen` 也沒帶 env。所以 `TMPDIR` 覆蓋要改的是 `_kill_run`,spec 沒提。
- 「在兩支測試之間檢查總預算」做不出來:`_run_bound_tests` 一次收整批去重後的 jobs,串行是 `seen.update(_one(k) for k in jobs)`。這個 repo 的設定還有 `bound_tests.parallel: 4`,並行時根本沒有「兩支之間」。
- `_spec_gate_judge_items` 有 5 個呼叫端,第 11 點也沒把它們列為要看的。
- file: `scripts/lumos:15105`(`_spec_gate_judge_items`)
- file: `scripts/lumos:15111`(呼叫處)
- file: `scripts/lumos:69029`(`_run_bound_tests`)
- file: `scripts/lumos:26160`(`_kill_run` 的 Popen)

## 二、minor(非 blocking)

6. 掛鉤「下一步」重查指令沒帶新旗標,第 11 點漏列釘它的測試
引句:「pre-push 掛鉤訊息與 `signoff` 參數的字串測試照新說法改」
severity: minor
blocking: 否——實作時測試會先紅,不會悄悄上線。
- `pp_record_block spec-gate ... "lumos spec-gate --push-check $_brange"`(`scripts/hooks/pre-push:582`)是印給人照抄的指令。
- 呼叫加了 `--push-remote`、`--pushed-ref` 之後,若這串不跟著改,人照抄會得到「未傳旗標,跳過重播,rc0」,看起來像修好了。
- `t_prepush_next_step_is_the_call_the_gate_ran`(`scripts/test_lumos.py:84170` 附近)逐字比對最後一行與假 lumos 收到的呼叫,會因此紅。
- 前例是 drift、room-guard、reread 三道都有 `$_push_args`(`scripts/hooks/pre-push:698`)。
- 中斷清單與 `t_prepush_interrupt_stops_every_gate` 不需動:沒有新增 lumos 呼叫。`t_prepush_block_range_callers` 的正規式 `spec-gate --push-check "\$_brange"` 在後面加旗標仍符合。

7. 第 11 點「一處改、全批跟著」不成立,新的規格閘擋下會紅更多既有測試
引句:「在這兩支產生器補一個早於生效日的 `created`(一處改、全批跟著)」
severity: minor
blocking: 否——跑測試就看得到,但清單與說法要更正。
- 第 7 點讓 `lumos spec-gate <計劃>` 對風險高、生效日之後的計劃缺預期值表就 rc1(S24)。
- 另有 `_sg_plan_linked`(`scripts/test_lumos.py:75658`)和 `_qo_plan`(`scripts/test_lumos.py:73863`)兩個產生器,不帶 `created`、沒有實務隱患節(門判風險高)。
- 再加 35 處直接 `write_text("…type: project…")` 的計劃。
- 例如 `t_backend_qo_question_section_not_parsed`(`scripts/test_lumos.py:73820`)預期 rc0,新規則下會 rc1。
- `t_spec_gate_high_risk_half`(`scripts/test_lumos.py:76631` 一帶,標題是「風險高照半套」)釘的就是風險高只印不擋,同樣要重看。

8. `_spec_gate_twoway_static` 裡的 `_plan_first_commit` 呼叫仍沿 HEAD,spec 只幫 d6 的日期判斷加了起點
引句:「它沿 HEAD 找;推送版不是 HEAD 時改從推送版找,給它加一個選填的起點參數」
severity: minor
blocking: 否——只在推的不是目前 checkout 的 ref、且計劃有 keeps 條款時誤擋。
- `_spec_gate_twoway_static` 內部呼叫 `_plan_first_commit(rr, plan_repo_rel)`(`scripts/lumos:14231`),spec 只替它加了前綴參數,沒有起點參數。
- 場景:HEAD 在沒有這份計劃的分支,推 `feat:feat`。`first` 是 None,印「這份計劃還沒進 git 歷史,驗不了」並擋。
- 這跟 S12 說的「照推送版那份計劃判」不一致。

9. 抽樹準備:回傳面與 `fix_check.link_deps` 耦合沒定義,修正關卡的測試沒列
引句:「樹的準備抽成一支共用函式,修正關卡與基準重播都用它」
severity: minor
blocking: 否——介面細節,但第 11 點本該列出受影響的既有測試。
- 現行 `cmd_fix_check` 內的準備段還產出 `plats`、測試索引五件組,以及 `unpinned` 的說明字串。
- 連依賴資料夾由 `fix_check.link_deps` 決定(`scripts/lumos:21492`)。基準重播共用後,是跟著 `fix_check` 的設定,還是無條件連?spec 沒說。
- 釘這些行為的修正關卡測試沒列:`t_fix_check_tree_setup`(`scripts/test_lumos.py:101225`)釘 `link_deps=false`,`t_fix_check_*` 的⑧⑪⑫(`scripts/test_lumos.py:100917`、100931、100934)釘「釘不住版本」的訊息字面。
- 另外,分岔點那棵要用推送版設定覆蓋,但現行是「樹裡沒有才複製」(`scripts/lumos:21944`),規則不同,抽出時要明寫。

10. 簽核逾時的選填參數要穿過 `_confirm_tty`,預設 300 秒超過 Bash 工具預設逾時 ⚠
引句:「與選填逾時(簽核預設 300 秒,表要讀;其他呼叫端不傳、照舊)」
severity: minor
blocking: 否——只影響無人看顧時的簽核路徑,且我判不準環境是否有控制終端,故標 ⚠。
- 逾時現在只讀環境變數 `LUMOS_TTY_TIMEOUT`(`scripts/lumos:34220`)。`_confirm_tty` 沒有逾時參數,spec 只提 `_waive_origin_tty`,漏了往下穿。
- 參數與環境變數誰優先沒說;測試若靠 `LUMOS_TTY_TIMEOUT=1` 加速,參數蓋掉環境變數時 S20 的「逾時記 ai」要等 300 秒。
- AI 在有可開啟 `/dev/tty` 的環境跑 `lumos signoff --expected`:提示會等 300 秒,Bash 工具預設 120 秒先逾時。命令被殺,「記成 AI 簽」的退路永遠走不到。

11. 專案開關的涵蓋範圍沒定,回退第一招可能關不掉設計時的擋下
引句:「專案層把 `.lumos/config.json` 的 `high_risk_evidence` 設成 off(整道不跑,事件照記)」
severity: minor
blocking: 否——寫表就能過,但回退節的承諾不實。
- 做法 6 與 S16 的「整道」不清楚是只含推送前基準重播,還是也含 S24 的 `lumos spec-gate` 預期值表擋下、第 9 點的推送前簽核檢查。
- 若 S24 不受開關管,off 的專案跑 `lumos spec-gate` 仍 rc1,而設計審流程規定先跑它。
- 開關讀工作目錄還是推送版的設定,也沒說(對照第 4 點「兩棵樹用推送版設定」)。

12. 注入範本與版號的連動:本 repo 自己的 CLAUDE.md、AGENTS.md 沒列
引句:「改掛鉤與注入範本照前例升小版號、寫 CHANGELOG,讓舊專案被提示 `lumos update`」
severity: minor
blocking: 否——不影響行為,但三個月後進這個 repo 的人會被「區塊落後」提示干擾。
- 本 repo 的 `CLAUDE.md:2` 與 `AGENTS.md:3` 內嵌 v1.4 的紀律區塊,內容來自 `scripts/templates/graph-discipline.md`。
- 範本改了、版號升 v1.5 後,這兩個檔要重新注入,入口掛鉤的「區塊≠範本」才不會提醒。
- 第 10 點的清單沒有這項。
- 另外 `skills/lumos-design-loop/templates.md:71` 也在講推送前的行為,同樣沒列。

13. 讀推送版治理帳沒規定只讀一次、也沒有期限
引句:「讀推送版裡的治理帳(`git show <推送版>:docs/.governance-log.jsonl`,同樣的解析)」
severity: minor
blocking: 否——慢和偶發誤擋,不是錯判。
- 這本帳現在約 21 MB、12.4 萬行(`docs/.governance-log.jsonl`)。
- spec 沒說一次推送(每個 ref 與每份計劃)要不要共用同一次讀取,也沒說逾時多久。
- 「讀不到或解析不了就擋」在慢磁碟或逾時時會變成誤擋。
- 前例有現成的:`_merge_side_ledger`(`scripts/lumos:69918` 一帶)用帶期限的 `_lens_git` 讀同一個檔,並只讀一次。
- 現有的 `_gov_vc_gate_events`(`scripts/lumos:22229`)讀的是工作目錄,不能直接拿來讀 git 內容,實作者得抽出解析部分。

14. 多批次合併過的計劃,最後一次推送會因測試在主線上已綠而被擋,天花板六只講「重播一遍」
引句:「分岔點是跟主線算的,之後任何一次改到計劃檔又改到程式的推送(通常是把 status 改成 done 的那次)會把整份重播一遍」
severity: minor
blocking: 否——有 `base_replay_skip` 出口,但說法應改成會擋。
- 若計劃的第一批已合進主線,之後再推(補丁或翻成 done)而且同時碰計劃與程式,分岔點已含第一批實作。
- 新行為測試在分岔點就綠,命中 S6 的擋下:「沒在驗這次的改動」。
- 同樣情形也發生在計劃長期維持 doing、每次補丁都動計劃檔的情況。

15. 其他小處
引句:「先紅模式的風險高計劃要有預期值表,整張表的指紋要有簽核才推得上去」(d3)
severity: minor
blocking: 否——敘述不齊,不影響行為。
- d1 的 content 仍寫「created 不早於生效日」,d6 已改成 created 與第一次進 git 取較晚者。決策正文沒跟著改。
- 天花板與第 125 點寫「原因欄寫是哪一種」,但沒定義原因欄的列舉值,RETIRE-IF 第三條的分類沒依據。
- 〈實務隱患〉不可逆節寫「被強殺留下的殘骸下次同前綴清掉」。實際 `_isolated_worktree_sweep` 只清超過 86400 秒的(`scripts/lumos:38948`),「下次」最長是一天後;每份殘骸是整個 repo 的檢出。
- `_h2_section_lines` 已經回 `(行號, 原始行)`(`scripts/lumos:13774`)。第 7 點「回傳每行的行號」是多餘的,真正缺的只有「標題出現次數」。

## 三、此功能碰到的風險類,逐類答

- **金流**:無。只動推送前檢查、規格閘的表格檢查與簽核指令,不碰扣款。
- **對外送出**:無。只讀本機 git 與帳、寫本機治理帳。重播會在舊版程式上跑專案自己的測試,但現行風險低推送檢查已經在跑同類測試,新增風險沒有質變。
- **不可逆**:治理帳只追加,回退留著無害。見 15 的殘骸清除時限,其餘無。
- **守衛面(新增會擋的閘)**:有。1、2、3、4、5、11 是這一類。
- **相容(新舊版混用)**:有。1(新掛鉤配舊 lumos)是最嚴重的一條。
- **效能**:有。2(累計差異會讓每次推送都重播)、5(預算做不出來)、13。
- **資源**:有。兩棵工作樹的殘骸清除要一天(15);子程序登記與 Ctrl-C 收尾的設計方向是對的。串行路徑在現有碼已登記進 `_BtProcs`,spec 寫的「串行也登記」是已成立的事,真正缺的是外部登記供呼叫端收。
- **併發**:無嚴重問題。`_isolated_worktree_sweep` 以目錄修改時間超過一天才清,不會清到正在用的樹;兩個推送同時重播各自建樹。⚠ 掛鉤收到 TERM 或 HUP 時,bash 要等手上的前景 lumos 結束才跑陷阱,重播最長可達 1800 秒以上,這段時間掛鉤不會停。
- **回退**:有。11(開關涵蓋範圍)。其餘三種關法與「已升版號不倒退」都對得上。
- **簽核事件與「留痕後只准提交帳本」**:接得上。`docs/.governance-log.jsonl` 在簿記白名單(`scripts/lumos:38108`),追加簽核事件不會讓代碼審留痕失效。
- **簽核流程的實務**:簽核缺漏要到推送才發現,此時通常已有帳本提交。「不另開提交」其實是要 amend,不是單純併進。這個判斷來自流程推演,不是實測。

總結:最嚴重 severity: major,blocking 共 5 條(第 1、2、3、4、5 條)。
