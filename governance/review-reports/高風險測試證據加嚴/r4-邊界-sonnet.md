severity: major

我的立場是替極端輸入發聲。實測用的小程式在 `/tmp/lumos-seat-work/高風險測試證據加嚴/邊界-sonnet/`(t1~t6.py、g1、g1s),可重跑。四條 blocking 都是 major,沒有 blocker。

## 名詞、問題與最小解、調研結論
已讀,無 finding。

## 做法(第 0 到 6 點)

1. 工具壞掉會變成擋推送,跟 spec 與掛鉤宣稱的「工具壞了不擋所有人」相反。新程式沒有任何一條路徑把例外轉成放行。
   - 引句:「理由用 `_real_chars` 數至少 10 個字;印出理由、寫一筆治理帳事件」
   - 重現:
     - 計劃開頭欄位寫成 `base_replay_skip:` 加縮排清單項(`parse_frontmatter` 對這種寫法回 `list[str]`)。實測 `_real_chars(['理由很長很長很長很長'])` 丟 `TypeError: expected string or bytes-like object, got 'list'`。`_real_chars` 只擋空值(`s or ""`),不擋非字串。
     - `LUMOS_REPLAY_TEST_TIMEOUT=abc` 或 `LUMOS_REPLAY_BUDGET=abc`。spec 沒寫解析規則,照既有 `scripts/lumos:69041` 的 `float(os.environ.get(...))` 寫法就是 `ValueError`。
     - 推送版沒有那份計劃(同一次推送刪掉風險高計劃檔、又改程式)。§1 的觸發算法會選到被刪的檔,§3 的 `_note_text_at_rev` 讀不到時回 None,spec 沒有處理分支。
     - `_spec_gate_judge_items` 在 `.lumos/config.json` 平台壞掉時回 `(None, err)`,§5 沒寫這種情況怎麼辦。
   - 壞在哪:`scripts/lumos:74340` 的 `_cli` 只接 `WriteBlocked`,其他例外是 traceback 加 rc=1。`scripts/hooks/pre-push:579` 對 `sg_rc -eq 1` 就擋推送,訊息還是「風險低計劃的條款測試沒全綠」。既有碼對非字串欄位早有防護先例(`scripts/lumos:12435` 寫明一篇壞筆記不可讓健檢整個當掉),新規則沒承接。
   - 修的方向:第 1 點到第 9 點的新檢查整段包「例外即放行並寫 skipped」,加上欄位型別與環境變數的解析規則。
   - file: `scripts/lumos:13923`、`scripts/lumos:74340`、`scripts/hooks/pre-push:579`
severity: major
   - blocking: 是,正常的作者寫法(清單型欄位、刪計劃)就會被擋,且違反 spec 自己的 fail-open 約定。

2. 總預算 `LUMOS_REPLAY_BUDGET` 在 spec 現有的接口下做不到,逾時與預算的極端值也沒定義。
   - 引句:「在兩支測試之間檢查,超過就停、沒跑到的當弱證據並講是預算用完」
   - 重現:
     - §5 只替 `_run_bound_tests` 加三個參數(每支逾時、環境、子程序登記),沒有期限參數。
     - 該函式把整批 jobs 一次跑完:串行是 `scripts/lumos:69138` 的 `seen.update(_one(k) for k in jobs)`,並行是 daemon 執行緒。兩條路徑在「兩支之間」都沒有可插入檢查的位置。
     - 結果是預算沒有上限。N 支測試串行最壞是 N×900 秒,而且每棵樹各一次。冷樹 Android 的「幾分鐘一支」就是 r3 要防的情境。
   - 極端值(實測 python3.14):
     - `subprocess.communicate(timeout=0)` 與 `-1` 都是 0.0 秒立即 `TimeoutExpired`,所有測試變「超時→弱證據」,必擋。
     - `nan` 與 `inf` 不逾時,等於沒有上限。
     - `scripts/lumos:69079` 的 `timeout if timeout else 10 ** 6` 讓 0 變成約 11.5 天。同專案的 `LUMOS_TEST_TIMEOUT` 慣例是「0=不限」,新變數沒說跟不跟。
     - 預算設 0 或負數,spec 的「超過就停」讀法會讓全部沒跑到,每次推送都擋。
     - 殘骸清理只看頂層資料夾 mtime、時限一天(`scripts/lumos:38948`)。逾時設成 inf 或 0 時,同時推送的另一個會談可能把還在跑的樹清掉。
   - 修的方向:`_run_bound_tests` 加期限參數並明寫判定時點,環境變數仿 `_confirm_tty_timeout`(`scripts/lumos:34220`)寫成「讀不懂、非正、nan、inf 一律用預設」。
   - file: `scripts/lumos:69041`、`scripts/lumos:69079`、`scripts/lumos:69138`
severity: major
   - blocking: 是,§4 效能與資源的上限宣稱在 spec 的接口下是假的,0 與負數會讓每次推送必擋或必卡。

3. ⚠ 預期值表與簽核檢查是否在「找不到分岔點」時照跑,spec 沒定義。兩種讀法都出事。
   - 引句:「不重播,印一句原因、寫一筆 `base-replay-skipped`(原因欄寫是哪一種)」
   - 重現:
     - §7 與 §9 的對象是「第 1 點選出的計劃」,而選計劃要用推送版對分岔點算 `git diff --name-status -M`。
     - 標籤、找不到主線、推送 main 本身,以及舊掛鉤沒傳 `--push-remote` 與 `--pushed-ref` 時,§2 只說「不重播、寫 skipped」。
     - §2 強制把遠端舊值當全零。`_push_no_mainline`(`scripts/lumos:65203`)在全零且無主線時回 `_EMPTY_TREE_SHA`,分岔點是空樹。
   - 讀法一:此時不選計劃。這樣 `git clone --single-branch`、直推 main、舊掛鉤都能完全繞過簽核,且只留一筆 skipped 事件。
   - 讀法二:照空樹算 diff。每個檔都是新增,所有 doing 的風險高計劃都被選中,一次要求補表與簽。
   - 簽核檢查本身不需要分岔點,只要推送版加計劃檔有改。選計劃應該跟重播解耦。
   - file: `scripts/lumos:64902`、`scripts/lumos:65203`
severity: major
   - blocking: 是,不寫清楚,簽核這道不是被繞過就是誤擋整個 repo。

4. 生效日有幾個邊界沒封住,條件偏緊(多查),不是漏放。
   - 引句:「常數改名 `_HIGH_RISK_EVIDENCE_SINCE`(純日期,值事先訂好,不早於合併日)」
   - (a) 專案慣例是「設隔日不設當日」(`scripts/lumos:14810`、`scripts/lumos:17224`:合入當天日粒度切不開先後)。spec 允許「不早於合併日」即同一天。
     - 本計劃自己 created 是 2026-11-04,通篇沒有 `## 預期值表` 節。若常數等於合併日,它登陸的那次推送會被自己的 S22 和 S24 擋。
     - S15 只寫「早於」,等於當天算生效,沒明說。
   - (b) 「淺複製只看 `created`」做不到。我實測淺複製(`--depth 1`)裡 `git log --diff-filter=A -- <檔>` 回邊界提交(當日),不是空。`_plan_first_commit`(`scripts/lumos:14194`)沒有淺複製偵測,所以每份舊計劃的「第一次進歷史」都變成今天。
   - (c) 計劃檔改名後,新路徑的第一個 A 是改名那次提交(實測 2026-11-04,原始是 09-01),舊計劃被當新計劃。
   - (d) `%cs` 是提交者時區的日期,跨時區的人在常數前後一天內會判不同。
   - 淺複製常見於 AI 沙箱,而且正是「無人看顧」的流程。天花板七只講到壓提交與 rebase。
   - 修的方向:常數寫隔日並明寫等於當天的判法,淺複製要明寫用 `rev-parse --is-shallow-repository` 偵測。
   - file: `scripts/lumos:12694`、`scripts/lumos:14194`
severity: minor
   - blocking: 否,偏向多查而非漏放,且有 `high_risk_evidence: off` 出口。

5. `high_risk_evidence` 的錯值與讀哪一版設定沒定義。
   - 引句:「加 `high_risk_evidence: block|warn|off`(預設 block)」
   - 重現:寫成 `"OFF"`、`false`、`"warn "`、物件、或檔案不是合法 JSON。既有先例 `_note_shape_config`(`scripts/lumos:45490`)是「壞值回 block 並印警告、從被檢查的版本讀」。
   - spec 沒寫壞值當什麼,也沒寫讀推送版還是工作目錄那份(§4 的樹準備明講用推送版設定,§6 沒講)。
   - 讀工作目錄那份,未提交的 `off` 就能繞過。讀推送版,推送自己能順手改成 off。
severity: minor
   - blocking: 否,有先例可抄,屬於補寫。

6. S10 的 `base_replay_skip` 不夠長時「當成沒寫」,沒有任何提示。
   - 引句:「不夠長時應當成沒寫;lumos set 應寫得進這個鍵」
   - 重現:作者寫了 9 字理由,以為已跳過,實際跑一場數十分鐘的重播。
   - 反方向,`_real_chars` 數數字:`base_replay_skip: 0000000000` 這種十個字也算有理由。
severity: minor
   - blocking: 否,只是體驗與弱檢查。

7. 觸發的插入點會被既有的提早 return 跳過。
   - 引句:「裡新增一道,排在既有的風險低檢查之後」
   - 重現:`_spec_gate_push_check` 在 `scripts/lumos:16333` 有 `if not plans: return 0`,在 `scripts/lumos:16336` 有 `if bad is None: return 0`。
     - 後者在「平台設定讀不動且沒有其他 bad」時成立,例如同一次推送有風險低計劃加壞掉的平台設定。
     - 新檢查若照字面插在後面,這種推送完全不查,其中表格與簽核根本不需要平台設定。
   - 只要放在這兩個 return 之後,就會被一併跳過。
severity: minor
   - blocking: 否,觸發條件窄。

8. 覆蓋測試檔時的改名可能刪掉分岔點的正式程式,造成假「證實」。
   - 引句:「改名的(`-M` 給的舊路徑、新路徑)先刪掉分岔點那一棵的舊路徑再複製新的」
   - 重現:`lib/helpers.py` 改名成 `tests/helpers.py`。我實測 `_nodehome_is_test("lib/helpers.py")` 是 False,`_nodehome_is_test("tests/helpers.py")` 是 True。
   - spec 沒寫舊路徑也要判成測試才刪。照字面做,分岔點會被刪掉一支正式程式,新行為測試因匯入失敗而紅,被判「證實」。對照組只有計劃有標 keeps 才抓得到。
severity: minor
   - blocking: 否,需要特定改名,且有對照組部分補救。

## 預期值表(第 7 點)

9. 全標 `[keeps]` 的風險高計劃沒有任何寫法能過表格檢查,`base_replay_skip` 也救不了。
   - 引句:「資料列至少一列、每列剛好四格、四格都不能是空的」
   - 重現:
     - 純重構、維持行為的風險高計劃,條款全標 `[keeps]`。
     - §7 要求資料列至少一列,同節又規定條款欄寫了標 keeps 的條款算格式錯。「每條新行為條款至少一列」在沒有新行為條款時也不給任何列的出口。
     - 結果是表格檢查永遠不過,S24 讓 `lumos spec-gate` 永遠 rc1。
     - §7 明寫「不論有沒有寫 `base_replay_skip`」,所以 skip 這個出口也沒用。
     - 唯一的出口是專案級 `off`,或硬加一個假的新行為條款。
   - 修的方向:「沒有新行為條款」時表可空、可標「無新行為」,或這類計劃不要求表。
severity: major
   - blocking: 是,合法工作流被死鎖,且擋下訊息教不出怎麼修。

10. 拆格規則裡「外側空的」是字面空字串還是去空白後空,有歧義。
    - 引句:「第一格與最後一格若是空的(行頭行尾的外側管線)丟掉,只丟這兩格」
    - 重現:`| S1 | a | b | c | `,最後一個 `|` 後面跟一個空格、tab 或全形空白。
      - 字面空的話,最後一段是 `" "`,不丟,成了第五格,擋成「不是剛好四格」。編輯器常留行尾空白,作者看不出錯在哪。
      - 去空白後空的話,結果相反,通過。
    - S18 與 S19 都沒有這一列的案例,實作者會自己選。
severity: minor
    - blocking: 否,只影響訊息可理解度,方向確定後即可解。

## 表指紋與簽核(第 8 與 9 點)

11. 簽核提示把每格截成 4000 字,指紋卻算整格;表長度與格長度都沒有上限。
    - 引句:「表一列一行,每一格各自過 `_out_clean`(它會把換行變空格、截到 4000 字,所以不能整張表一起丟進去)」
    - 重現:
      - 我實測 `_out_clean("x"*5_000_000)` 回 4001 字以 `…` 收尾,耗時 0.7 秒。
      - 一格 4000 字以上時,簽的人只看到前 4000 字,指紋卻綁整格。表格檢查沒有格長度或列數上限。
      - 提示大小因此不受控。`_confirm_tty_dev`(`scripts/lumos:34241`)先 `os.write(fd, prompt)` 再 `select`,300 秒逾時不涵蓋寫入阻塞。
    - 插入點的缺口:`_confirm_tty`(`scripts/lumos:34193`)的逾時只讀環境變數 `LUMOS_TTY_TIMEOUT`(`scripts/lumos:34220`)。spec 只替 `_waive_origin_tty` 加逾時參數,沒說 `_confirm_tty` 怎麼接,也沒說環境變數與參數誰優先。
    - 規模本身沒問題:實測 20 萬列、8MB 的表,`_h2_section_lines` 只要 0.12 秒。
    - 修的方向:表格檢查加格長度與列數上限,超過算格式錯。
severity: minor
    - blocking: 否,須構造長格才觸發,簽核本來就是軟的(d3)。

12. 推送版治理帳的壞行處理沒寫,規模也沒寫。
    - 引句:「推送版裡沒有治理帳或解析不了,擋下並講原因」
    - 重現:本 repo 的 `docs/.governance-log.jsonl` 是 21MB、12 萬行,每個會談都在追加,合併時會留衝突標記行。
    - 既有讀法 `_gov_vc_gate_events`(`scripts/lumos:22229`)與 `_gov_rows_at`(`scripts/lumos:61061`)都是壞行跳過、只有檔案整個讀不出才回壞。
    - 若「解析不了」被實作成整檔,任何殘留的壞行就讓全部風險高推送被擋,而 `base_replay_skip` 對簽核沒有出口。
    - 我沒構造出會擋的案例,所以判不準。
    - ⚠ minor
severity: minor
    - blocking: 否,判不準,先請作者寫清楚是逐行還是整檔。

## 驗收條款、回退、實務隱患
已讀。S1~S24 與第 10 點的一致性核過,沒找到交叉引用錯誤。回退已讀,`base_replay_skip` 留在帳上無害(`scripts/lumos:12422` 只給軟提醒)。

## 圖譜鏡頭(固定席節點)
- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★:re-inject 只覆蓋 sentinel 之間、之外 byte-equal。不影響。
  - 理由:第 10 點只在注入範本 `scripts/templates/graph-discipline.md` 的 body 加一句,不動 sentinel 行,也不碰 sentinel 之外的內容。
  - 前提:實作時不能改到 sentinel 行本身。
- `Systems/test-quality-cli` 與 `scripts/test_quality.py`:第一批不改,第二批「只借不改」。不影響。
- `Systems/test-guard`、`Systems/test-quality-evidence`、`Verification/測試品質第四輪修補驗證`:提示只給標題,我沒讀到內容,不影響,但不是逐條核過。

## 風險類逐類
- 金流:無。只改推送前檢查與帳,不碰收費或扣款。
- 對外送出:工具本身無新增。但重播會把專案測試在舊程式上多跑,測試若真的有外呼或寫外部狀態,會在每次推送多執行兩次。既有合約測試閘也在 pre-push 跑同類,所以新增的是次數,不是類別。
- 不可逆:治理帳是追加,樹離開時收掉。測試若寫到樹外共用狀態(`~/.gradle`、模擬器、資料庫),隔離工作樹不涵蓋。
- 守衛面:新增兩道會擋的檢查。發現 1、2、3、9 是它們的可靠性缺口。
- 效能:發現 2。預算接口不足,0、負數、nan、inf 行為未定。資料量方面 20 萬列表只要 0.12 秒,不是問題。
- 資源:⚠ Gradle daemon 若脫離程序群組,`killpg` 收不到,樹被刪後仍佔著。我沒實測,不列 finding,實作時要驗。TMPDIR 指到樹底下的設計成立。
- 併發:發現 2 提到的殘骸清理時限。`node_modules` 與 `.venv` 連回主目錄(`_lint_link_deps`),兩個同時推送的重播共用同一份,寫入衝突 spec 沒講。
- 回退:三種關法邏輯自洽,沒找到漏洞。

最嚴重 severity: major,blocking 共 4 條(發現 1、2、3、9)。
