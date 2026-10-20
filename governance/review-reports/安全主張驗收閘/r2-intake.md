preflight-4: ran (r1 已跑,本輪沿用)

## r2 處置

r2 七席共 70 條(blocking 35 條;數法:各席報告 `^blocking: ?是` 的行數,發現數是 `^(- )?severity: ` 行數扣掉報告開頭那一行,見〈r2 機械重現〉M1)。組別照編排者裁定 U1–U11;不在這十一組的寫「其他」。本輪多席報 major,所以不用 accepted:major 全 folded,minor 也全 folded(一句補得了就補),沒有 refuted。帳上 id = 席名縮寫 + 席報告內編號(正=正確性-sonnet、邊=邊界-sonnet、整=整合-sonnet、資=資源-sonnet、回=回滾-sonnet、架=架構對齊-sonnet、外=外家finder-codex);架構對齊席報告最後一條「給編排者的 ⚠」沒有編號,記成 架8。發現種類一律 spec(被審文件缺陷)。

| id | 組 | 處置 | 一句 |
|---|---|---|---|
| 正1 | U1 | folded | 清單 `.sig` 改成核可鏈:撤銷寫在鏈上、主線鏈必須是推送版前綴,舊 `.sig` 重放接不上鏈;S48、S49 |
| 正2 | U1 | folded | 人審核可的 `content_sha256` 蓋整份 review_record(含 bindings、test_sources、fixture_globs、author、kind);S40 加刷新 bindings 樣本 |
| 正3 | U3 | folded | 變弱只比種類集合與每種類列數,同種類換節點不算;判定輸入雜湊不含節點名;S31 加換節點對照 |
| 正4 | U3 | folded | 工具清單跟主線 tip 比,變弱要 `tool_list_change`;表版號換成最低種類較少的版本要 `threat_table_change`;S31、S55 |
| 正5 | U1 | folded | gate 設定與修訂都進核可鏈,每筆帶 `project_id` 與到期上限(30 天),跨專案貼與重放都不算數;S45、S48 |
| 正6 | U2 | folded | 取到提交後先對推送版與主線 tip 做登記痕跡預檢,沒痕跡就回 None,淺層 clone 與起點只在有痕跡時判;S30 加沒痕跡的淺層 clone |
| 正7 | U2 | folded | `vault_rel` 對每一版從那一版的提交樹解析,三版以護欄 id 對齊,搬圖譜目錄不讓凍結落空;S29 加搬目錄樣本 |
| 正8 | U11 | folded | 刪 `unexpected_empty`,全部被刪由逐條 `control_removed_unapproved` 擋;S3 改寫預期代碼 |
| 正9 | U10 | folded | 刪 PR 起點定義,寫明 PR 事件不跑這一道(照 d9) |
| 正10 | U1 | folded | 核可鏈每筆有 `signer`,驗章 `-I` 直接用它,不枚舉也不用 find-principals |
| 正11 | U11 | folded | 刪 `stale:tool_version_changed`,工具版本一律 `invalid:tool_version_mismatch` |
| 正12 | U8 | folded | `vulndb_fetched_at` 晚於 `observed_at` 判 `invalid:vulndb_after_observed`;`observed_at` 比 committer date;S36、S44 |
| 邊1 | U5 | folded | `required_evidence` 空、`threat_categories` 空或含未知 id、表版號不認得都是護欄層 unsound,空集合不算零下限;S57 |
| 邊2 | U1 | folded | gate warn、修訂紀錄、清單 `.sig` 三種重放都由核可鏈的 seq、前一筆雜湊、專案識別與到期擋;S45、S48 |
| 邊3 | U1 | folded | 人審核可蓋 `kind` 與 bindings,複製一份改成 deployment 或刷新 bindings 都對不上;S40 |
| 邊4 | U2 | folded | 主線用既有候選加本機 main/master,認不出主線而有痕跡就擋 `mainline_unknown`,只有沒 remote 也沒本機 main/master 才當空樹;S52 |
| 邊5 | U3 | folded | 同種類換 Verification 節點不算變弱,只比列數;S31 |
| 邊6 | U6 | folded | 定義命中(宣告規則的 error/warning 或 kind=fail)與處置(suppressions 含 inSource 不算,只有鏈上 suppression 核可算);S58 |
| 邊7 | U11 | folded | `approved_on` 由 payload 自動填 UTC 日期,未來判 `approval:approval_in_future`;S23 加台灣清晨手填樣本 |
| 邊8 | U8 | folded | JUnit 列改正現況描述(任何一個 error 元素整份拒),拒收改帶型別並對映代碼;S59 |
| 邊9 | U11 | folded | 同正8:刪 `unexpected_empty`,S3 寫明預期代碼 |
| 邊10 | U11 | folded | 改寫「永遠同一答案」:同一提交、同一主線 tip、同一 UTC 日期才同答案,午夜前後 CI 可能紅;S28 加同日條件 |
| 邊11 | U8 | folded | 總量按不同 blob 算一次、照(路徑、blob)排序累計,項數超過照(護欄、種類、路徑)排序;S41 加總量與項數樣本、跑兩次比對 |
| 邊12 | U8 | folded | `expires_on` 跟「observed_at 的 UTC 日期加 90 天」比、恰好那天有效;vulndb 上界見正12;簽章人見正10 |
| 邊13 | U11 | folded | k6 REVISIT 用本席實測結案([closed:2026-10-20]),下限比整體 `http_reqs`,`foreign_rejected` 改成大於 0 另判 |
| 整1 | U9 | folded | `question_refs` 改用 `pq_parse` 加 `_pq_settled`,節點解析抽 `_pq_node_target` 共用;S15 加「已決但決策被翻案」樣本 |
| 整2 | U9 | folded | `security list` 不加 `--commit`、不驗章,維持 S7;considerations 只顯示簽章未驗,判定在閘門;S4 改寫、S63 |
| 整3 | U5 | folded | 最低種類用護欄記的表版號那一版;表未核可前只印「表未核可、未比對」不擋,REVISIT 綁表節點轉 active;未知 id 是護欄層錯誤 |
| 整4 | U2 | folded | 同邊4,寫明為什麼用 `_push_mainlines`/`_push_range_start` 那組、為什麼不沿用它的空樹退路 |
| 整5 | U10 | folded | doctor 印 CI 步驟範本(S61);order-demo 用本機 bare repo 當 origin 真推送;第 4 步用 `lumos update --source` 只給 order-demo |
| 整6 | U1 | folded | gate 設定改成核可鏈 `gate_setting`,帶 project_id、30 天上限、signer;`approved_on` 在鏈上那一筆 |
| 整7 | U9 | folded | 不沿用 `_backing_judge_groups`,只沿用 `_backing_valid_rows`,逐組判另寫一支回細的 kill_ 代碼;S37 加只有 unattributed 的樣本 |
| 整8 | U9 | folded | 快照建在 `_nodehome_list` 加 `_nodehome_cat_blobs_capped` 上、寫明路徑含換行的轉接;背書改放 `docs/.security-backing.jsonl`,不讀 2000 萬位元組的治理帳 |
| 整9 | U8 | folded | `load_receipt` 一併抽、三份 capture 子目錄名寫定、`junit()` 改帶型別、補 `report_unparseable` 等代碼、要跟著改的地方加重驗 Verification/測試品質第四輪修補驗證 |
| 整10 | U10 | folded | 要跟著改的地方補 anchor approve、pre-push 逃生句、ci.yml 紅燈訊息、commands/08-自動跑的.md、security help 與 `_SECINV_NOTICE`、tag 觸發只跑安全那一個工作 |
| 整11 | U11 | folded | 指消費專案檔的兩條 when-file REVISIT 改成純日期,k6 那條結案 |
| 整12 | U10 | folded | schema v2 唯一清單補「證據種類值域從五種擴成十一種」一列 |
| 整13 | U10 | folded | 快照寫明 NFC 碰撞、符號連結、容量常數的轉接,新增 S56 釘提交樹這條路徑 |
| 資1 | U8 | folded | `junit()` 改 iterparse 邊解析邊數深度;JSON 新呼叫端各自接 RecursionError 轉該項 invalid;S42 改成只擋引用它的項 |
| 資2 | U8 | folded | 快取只存濃縮事實(每份上限 10 萬筆)、同一時間只解析一份,寫明解析後記憶體預算 |
| 資3 | U8 | folded | 256 MiB 按不同 blob 算一次、累計照路徑排序;REVISIT 量測目標改成 1000×9(在項數上限內)另加超限一項 |
| 資4 | U8 | folded | 每個 ref 60 秒,超過擋 `evaluation_timeout`、退出碼 1;`--security-only` 任何非 0 都擋;寫明 fail-closed 是刻意偏離 `_gate_failopen`;S60 |
| 資5 | U11 | folded | 同邊7:`approval_in_future` 代碼與 payload 自動填 UTC |
| 資6 | U1 | folded | 放行時印 7 天內到期的核可、vulndb 與 review 提醒;S25 加前八天樣本 |
| 資7 | U8 | folded | Verification 節點超過 2 MiB 只讓引用它的護欄判 `invalid:evidence_node_too_large`,給拆節點指引;S56 |
| 資8 | U8 | folded | `observed_in_future` 比 committer date;S44 加 --amend 樣本 |
| 回1 | U1 | folded | 同正5:降級與修訂進核可鏈、帶到期與專案識別 |
| 回2 | U1 | folded | `approvers_init` 由使用者手動做、`code-loop security-approval-add` 寫入前當場驗一次;主線鏈從第一筆就沒有有效金鑰時可整條換掉;S50 |
| 回3 | U1 | folded | 驗鏈只讀推送版與主線 tip,不依賴 merge-base;新增〈哪些整道擋下可以降級〉逐代碼表;S51 |
| 回4 | U9 | folded | `_KNOWN_GATES` 登記 `security-evidence`,漂移釘子同步;背書另走自己的檔,不經 `_gate_event` |
| 回5 | U9 | folded | 背書檔與核可鏈一律從要推的提交樹讀,背書沒提交就判 missing,本機與 CI 同答案;S37 加「寫了沒提交」 |
| 回6 | U9 | folded | 背書加 `--supersede` 更正、超長拒寫不截斷、讀到截斷行判 `invalid:backing_truncated`;S38 |
| 回7 | U9 | folded | 例外使用記帳鍵改(護欄、種類、鏈 seq)、只首次寫,不再每次推送弄髒工作樹;S24 |
| 回8 | U10 | folded | 回退分兩個提交逐項列(test_quality 與 bundle digest 同進同退等),寫明降回 v1 要先撤 ② 或簽 warn、降 v1 會讓核可雜湊全部對不上 |
| 回9 | U11 | folded | 承認時間相依,回退到舊樹沒有特例(〈一〉的〈判定跟日期有關〉) |
| 回10 | U2 | folded | 推主線本身時主線 tip 用 `before`/遠端舊值;force push 退版取不到就擋 `mainline_unknown` 並寫明原因,不退成空樹(退用 origin/main 會是自己比自己) |
| 架1 | U9 | folded | 同整8:`_secinv_snapshot_tree` 建在 `_nodehome_list` 加 `_nodehome_cat_blobs_capped` 上,不另寫批次讀取 |
| 架2 | U9 | folded | 寫入子命令搬到 code-loop 族(`security-backing`、`security-approval-add`),security 族維持唯讀,help 與 `_SECINV_NOTICE` 跟著改 |
| 架3 | U9 | folded | 寫明 fail-closed 是刻意偏離 `_gate_failopen`,`evaluation_error`/`evaluation_timeout` 不走它 |
| 架4 | U9 | folded | 值域只 block/warn,壞值與 off 當 block 並說一句;改正「同族」說法(lint_new 那族);讀法沿 `_lint_new_config(from_snapshot=True)` |
| 架5 | U9 | folded | 〈一〉補兩個指令狀態詞對照表,寫明不通用 |
| 架6 | U8 | folded | 改正「`_secinv_json_loads` 有深度上限」的描述,新呼叫端自己接 RecursionError |
| 架7 | U9 | folded | lands_in 拿掉 guard-kill 與棧別提問表態閘(本篇不改它們);寫明 ci.yml、pre-push 的說明寫在安全證據閘(實作時 append about_code),原家只加連結 |
| 架8 | U3 | folded | 工具清單變弱要核可鏈 `tool_list_change`,跟其他核可同一套,不再有「決策引用」與「金鑰」兩種核可方式 |
| 外1 | U4 | folded | 主線 tip 版有、推送版刪掉的證據項照算,除非同 control、kind、targets 且 observed_at 更新的項取代;S54 |
| 外2 | 其他 | folded | d2 列了「報告是否偽造」,新增要人的判斷 id `report_provenance`,人審要具名看過執行或可信來源;S62 |
| 外3 | U2 | folded | 必驗集合擴成推送版 ∪ merge-base 版 ∪ 主線 tip 版;S53 |
| 外4 | U1 | folded | 撤銷寫在鏈上、主線鏈必須是前綴,舊分支用已撤金鑰簽的不算數;S49 |
| 外5 | U1 | folded | 同正5:warn 進核可鏈、最長 30 天、到期自動恢復擋;S45 |
| 外6 | U7 | folded | 新增 `fixture_globs`,展開結果必須在 bindings;自動找不到的夾具與 helper 寫成工具天花板加 REVISIT;S9 |

## r2 作者另外改的

- 開頭欄位:`decision-add` 記 d10、`decision-supersede` d7(by #d10);Q1、Q9 的 decision 改指 #d10(否則 `_pq_settled` 會把兩題當沒結);d8 還沒推上去,用 `decision-amend` 把「d7 的金鑰簽章」改成「核可鏈(d10)上的 human_review」;`lands_in` 拿掉 Systems/guard-kill、Systems/棧別提問表態閘。
- [[Systems/安全證據閘]]:responsibility 用 `lumos set` 改成核可鏈、背書檔與兩個寫入子命令;正文「內容簽章核可」改成「核可鏈」。[[Systems/資安威脅類別表]] 不用改(表未核可的處理寫在計劃,REVISIT 綁它的 status)。
- 檢查過 [[Issues/code-loop守衛main-direct盲區]](推 main 時 merge-base 等於 HEAD 讓守衛空轉):本篇「推的就是主線本身時主線 tip 用遠端舊值或 `before`」正是避開這個坑,不會自己比自己。

## r2 機械重現

工作樹 /Users/enzo/orca/workspaces/lumos-toolchain/security-gate,基底 07092812,2026-10-20 跑;合成 repo 與探針放 /private/tmp/claude-501/sec-fold3/,做完已刪。

- M1(數字):`grep -cE '^blocking: ?是'` 逐席:正確性 7、邊界 6、整合 6、資源 4、回滾 5、架構對齊 1、外家 6,共 35;`grep -cE '^(- )?severity: '` 逐席 13、14、14、9、11、9、7,各扣掉開頭一行得 12、13、13、8、10、8、6,共 70。
- M2(整1,`_pq_decision_target` 對 #Q3):載入 `scripts/lumos` 當模組,假 env 只有 `Projects/X_計劃.md`。`_pq_decision_target(env, "Projects/Y.md", "Projects/X_計劃#Q3")` → `('bad', None, None)`;`"#Q3"` → `('bad', None, None)`;對照 `"Projects/X_計劃#d3"` → `(None, 'Projects/X_計劃.md', 'd3')`;`_dref_parse("Projects/X_計劃#Q3")` → `None`。HIT:照原寫法每條帶 question_refs 的護欄都會 `question_open`。
- M3(回4,`_KNOWN_GATES` 對新閘名):`"security_evidence"`、`"security-evidence"`、`"security_backing"`、`"security-backing"`、`"security-exception"` in `_KNOWN_GATES` 全是 False;名單裡含 `sec` 的閘名 `[]`;`scripts/lumos` 的 `_gate_event` 對不在名單上的閘名印警告後 `return False`。HIT:不登記就整批記帳被吞。
- M4(整4、整5,order-demo remote):`git -C /Users/enzo/orca/workspaces/order-demo remote -v` 沒有輸出(0 行,rc 0);`ls -d .../order-demo/.github` → No such file or directory;`git branch --list main master` → `* main`。結論:order-demo 沒有 remote 也沒有 CI,但有本機 main,照新規則主線就是本機 main,不會落到空樹。
- M5(邊4、整4,`_mainline_ref` 無 origin):`git init -b feature` 加一個空提交、沒有 remote 也沒有 main 的合成 repo:`_mainline_ref(d)` → `None`;`_push_mainlines(d, None, "refs/heads/feature")` → `([], '')`;`_push_range_start(d, "0"*40, tip, None, "refs/heads/feature")` → 空樹 `4b825dc6…`,說明「找不到主線…新分支首推:從空樹算」。同一 repo `git branch main` 之後 `_mainline_ref(d)` → `('main', <sha>)`。HIT:沿用 `_push_range_start` 的退路會讓凍結比對對空樹比,所以本篇只借候選與分岔點算法、認不出就擋。
- M6(邊8,junit 現況):`test_quality.junit()` 吃兩個案例、其中一個帶 `<error>` → `ValueError runner/suite errors`(整份拒,不只 suite 層);200 層 `<a>` 包住空 testsuite → `ValueError zero testcases`(先建完整棵樹才報,沒有深度檢查)。HIT。
- M7(架6、資1,JSON 深度):`_secinv_json_loads('['*100000 + ']'*100000)` → 解析成功,沒有深度上限。HIT:新呼叫端要自己接 RecursionError。
- M8(整8,治理帳大小):`wc -c docs/.governance-log.jsonl` → 20480865。`'docs/.security-backing.jsonl' in _BOOKKEEPING_FILES` → False(實作要加,已列進〈要跟著改的地方〉)。
- M9(資4,pre-push 退出碼):`scripts/hooks/pre-push` code-loop 那段註解「rc≠0/1(異常,128 以上除外):fail-open 放行」;403 行起「最壞每個 ref 判定本體 60 秒的預算」。HIT:逾時與 argparse 錯若不回 1 就放行,所以本篇規定回 1、`--security-only` 非 0 一律擋。
- M10(整2,S7):`scripts/test_lumos.py` 有 `t_seclist_s07_read_only_no_exec`;`security list` 的 parser description 寫「不執行測試、不寫檔、不連網」。結論:`--commit` 與驗章不放 list。
- M11(整9,capture 名):`scripts/test_quality.py` 的 `check()` 讀 `('baseline', args.baseline), ('fault', args.fault), ('restored', args.restored)`,另有 `--refactor`。子目錄名照這四個寫定。
- M12(架7,檔的家):`lumos impact --file scripts/hooks/pre-push` 的家有 anchor-integrity、bound-tests-gate、存量漂移守衛、每支檔有家、筆記內容閘;`Systems/bound-tests-gate` 的 about_code 列了 `.github/workflows/ci.yml` 與 `scripts/hooks/pre-push`;`lumos impact --file scripts/test_quality.py` 的家是 test-quality-cli。
- 收尾:`lumos lint Projects/安全主張驗收閘_計劃` 0 問題;`lumos lint Systems/安全證據閘` 0 問題;`lumos prose-lint` 沒掃到模糊措辭;`lumos fold-check` 的 value_drift 0、只剩 reverse_omission 40 筆(計劃沒有 summary 欄,全是「正文提到、摘要沒提」,r1 收尾時同類 31 筆);`lumos spec-gate` 條款 63 條全標、句式與回退節已驗、待決問題沒有擋進實作的、相依回歸 2 支綠(lands_in 拿掉 guard-kill 後從 4 支變 2 支)。
