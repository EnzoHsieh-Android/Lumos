severity: minor

核對範圍:`README.md`、`README.en.md`、`docs/指令參考.md`、`docs/command-reference.md`、新增的 `docs/updates/2026-10-10-readme-audit.md`。我逐 hunk 讀完 `r1-snapshot.patch`,再對照程式。沒有找到說法與程式相反、會讓讀者照做出錯的地方,所以沒有 major。找到 7 條 minor。

另外跑了 `python3.14 scripts/test_lumos.py --suite docs`(在 `/tmp` 的 shared clone 裡):733 過、0 紅。1 支被跳過(`t_codex_s1_r1_fixes`),被跳過的測試不算驗到,但這是測試環境的跳過,與這份 diff 無關。

## A1 README 新寫的「哪些檢查可以調鬆」,和緊鄰的漂移守衛圖仍寫舊的「其餘可調」,兩者互相打架
severity: minor
blocking: 否

這次改動正是要收掉「其餘會擋的檢查都能調成只提醒」這個講太滿的說法,新文字也改成明列沒有開關的項目。但同一節嵌入的 `assets/drift-guard-zh.svg` 與 `assets/drift-guard-en.svg` 沒跟著改,還留著同一句。

引句:「這些沒有開關可調：改程式沒動筆記、連結斷掉、高風險改動沒有審查紀錄」

證據:
- file: `assets/drift-guard-zh.svg`,圖內文字:「除了兩項一定擋下的檢查、其餘可由專案改成提醒」。
- file: `assets/drift-guard-en.svg`,圖內文字:「Other blocks can be set to warn by the project.」
- 實際只有 `drift_check.gate`、`note_reread.gate`、`note_shape.gate`、`node_home.gate`、`lint_new.gate` 這類有開關(讀取函式在 `scripts/lumos:39190`、`scripts/lumos:34735`、`scripts/lumos:30413`、`scripts/lumos:28954`、`scripts/lumos:27823`)。測試或掛鉤檔的 anchor 核可、高風險改動的審查紀錄、Python 3.14 檢查都沒有。
- 建議:這是「同族一次掃完」沒掃到圖。請把兩張圖的最後一格改成與新段落一致,或刪掉那一格。

## A2 評測圖的圖內文字與 desc 沒跟著改,和新的通知與範圍說法不符
severity: minor
blocking: 否

README 把圖的 alt 文字改成「出問題時通知人」,又把「只在 Lumos 自己的 repo 跑」改成「主要在…另外會順帶考另一個專案」。但圖本身沒動。

引句:「這些評測主要在 Lumos 自己的 repo 跑；查詢考卷另外會順帶考排程腳本裡指定的另一個專案」

證據:
- file: `assets/evals-overview-zh.svg`,圖內文字:「在 Lumos 自己的 repo 排程執行」「退步或沒過，通知人」。
- 它的 `<desc>` 還寫「退步或沒過就通知人」。
- file: `assets/evals-overview-en.svg`,圖內文字:「Scheduled in Lumos's own repo」「Alert on regressions」。
- 程式:查詢考卷退步只記錄不通知(`governance/autonomous-loop.sh:331-336`)。排程另外考 Landmark(`governance/autonomous-loop.sh:466`)。
- README 新加的「圖中的『通知人』不是每種檢查都有」這句,等於承認圖與事實有落差。alt 文字也已經和圖內文字不同。建議把圖一併改掉。

## A3 3 輪上限新用了「中等風險 / medium」,程式與 README 其他處沒有這個級別
severity: minor
blocking: 否

引句:「中等或高風險的審查（設計審、代碼審都算）跑到 3 輪上限仍未通過」

證據:
- file: `scripts/lumos:12128`:`_TIER_PARAMS = {"light": (1, 2), "standard": (3, 3), "high": (5, 3), "legacy": (1, 6)}`。分級只有 light、standard、high,「medium」不存在。
- `scripts/lumos:9205` 的 `_cap_hint_scope` 與 `scripts/lumos:14004` 的 `cmd_loop_cap_decision` 實際收的是「多席、非 light」的迴圈,也就是 standard 加 high。
- `docs/指令參考.md` 把級別寫成「standard / high」,README 審查段稱「一般改動」。同一份 README 對同一級別用了新名詞。
- 範圍本身(設計審與代碼審都算、light 不算)是對的。建議改成「standard 或 high」這類與程式、指令參考一致的詞,或加一句對照。

## A4 專案開關表的前言和說明有三處講得比程式更滿
severity: minor
blocking: 否

引句:「改了記得提交：推送前的幾道檢查讀的是被推那個提交裡的版本。沒寫就用下表的預設；寫壞了（讀不成 JSON、值看不懂）會講一句，多半照預設。」

證據:
- **讀取來源不一致**:`stack_questions.gate` 由 `scripts/lumos:26867`(`_stack_questions_config`)直接讀工作目錄的 `.lumos/config.json`,註解寫「直讀 repo_root」。`note_lint.gate` 由 `scripts/lumos:6776` 讀工作目錄。這兩項不是讀被推提交。`note_reread`、`drift_check`、`note_shape`、`note_audit` 才是讀被推頂端提交(`scripts/lumos:34735`、`scripts/lumos:39190`)。
- **「值看不懂照預設」不全對**:`note_lint.gate` 預設是 warn,看不懂卻改用 on(`scripts/lumos:6812`)。`node_home.gate` 看不懂也用 on(`scripts/lumos:28962`)。前言只用「多半」帶過。
- **表漏列有擋效力的開關**:`note_shape.slots` 預設 block(`scripts/lumos:32015`),表裡沒有。README 寫「另有幾個較少用的開關,見指令參考」,讀者會以為表已列全。
- **「全套測試沒過」過度概括**:「Lumos 自己 repo 的全套測試沒過」沒有開關,這句成立。但推送前純文件或 light 改動只跑子集(`scripts/hooks/pre-push:641-652`),只有部分推送會跑全套。

## A5 開關表列出 `note_audit.gate`(預設 block),但隨附的推送前掛鉤沒有接 `note-audit check`
severity: minor
blocking: 否

引句:「筆記內容審（`note-audit check`）」

證據:
- file: `scripts/hooks/pre-push:531-537` 只呼叫 `note-audit reread-check --gate`。整支掛鉤和 `.github/workflows/ci.yml:264` 都沒有 `note-audit check`。
- file: `scripts/lumos:33330`:`_NOTE_AUDIT_GOLIVE_MARK = "note-audit check"`,註解寫「推送前掛鉤裡有這串=第二層上線了」。`scripts/lumos:41037-41045` 的 doctor 會檢查有沒有接線。
- 「預設 block」是設定讀取函式的預設(`scripts/lumos:33354`),不代表現在每次推送都會擋。表上沒註明這道檢查要掛鉤接線才有效,讀者可能以為已經在擋。建議在「管什麼」欄註明,或不列。

## A6 評測「通知誰」的列舉比程式少兩種會通知的情形
severity: minor
blocking: 否

引句:「審查回放有案子結論對不上或需要重新凍結、情境探針有題沒過，會通知人」

證據:
- file: `governance/autonomous_loop/replay_weekly.py:166-181`:`build_msg` 除了紅燈和過期,還會在「回放執行錯誤」和「舊帳無 spec_path 凍不了」時組出訊息,`governance/autonomous-loop.sh:440-445` 就會發出通知。
- README 列舉後接著說「查詢考卷退步只記錄」「推播漏網只留清單」,讀者容易把前一句當成通知條件的完整清單。
- 其餘幾項屬實:探針只在總結行 p≠n 時通知(`governance/autonomous-loop.sh:392-399`),查詢考卷只在未標率 ≥ 一成時通知。建議補「執行出錯也會通知」,或把「會通知」改成「主要會通知」。

## A7 把「專案能調鬆與沒開關」的細目和探針內部機制放進 README,偏離已定的分工
severity: minor
blocking: 否

計劃 `Projects/對外說明親和化改寫` 的決策 d2 寫明:README 保留結論與導向,完整圖與盲區說明集中到中英文心智模型文件。這次 README 新加的兩段,細目程度都是機制內部的:
- 「這些沒有開關可調」那串 6 項清單。
- 情境探針一段約 4 句的保護機制(每場重新複製凍結副本、事故整批停、壞場次不算分、用量帳預設不開)。

引句:「每場都從同一份凍結的副本重新複製，前一場改的東西帶不到下一場」

證據:
- `docs/心智模型.md` 第四節「強制力」只講強制力光譜,沒有補對應的「哪些能調鬆」結論。
- 該檔裡探針只有一個 mermaid 節點(`docs/心智模型.md:116`)。
- 這是結構取捨,不是事實錯。若維持放在 README,建議在心智模型中英文版補一份完整版,README 留一句結論加連結。

## 核對過、屬實的句子
- **「改程式沒動筆記」這道一定擋、專案不能關**:`scripts/hooks/pre-commit:276-306`,這段沒有讀任何設定。`--no-verify` 跳過後 `scripts/hooks/post-commit` 會記帳(檔頭註解寫 bypass 留痕)。
- **`drift_check.gate` / `old_sentence` / `retire` 預設與跟隨關係**:`scripts/lumos:39167-39190`、`scripts/lumos:39138` 與 `scripts/lumos:35596`(預設 block;子開關沒寫照總開關)。
- **`note_reread.gate`**:預設 block、只有本機掛鉤帶 `--gate` 才擋、CI 只提醒:`scripts/lumos:34735`、`scripts/hooks/pre-push:526`、`.github/workflows/ci.yml:264`。`lumos note-audit reread-check -h` 的說明相同。
- **其餘開關的預設與值域**:
  - `note_shape.gate` block、`note_shape.test_refs` warn:`scripts/lumos:30413`、`scripts/lumos:32505`。
  - `node_home.gate` on/warn/off、預設 on:`scripts/lumos:28954-28962`。
  - `lint_new.gate` block:`scripts/lumos:27663-27666`。
  - `note_audit.gate` block:`scripts/lumos:33354`。
  - `stack_questions.gate` all/high-only/off、預設 all:`scripts/lumos:26863-26881`。
  - `note_lint.gate` 預設 warn:`scripts/lumos:6776`。
- **結 Issue**:`drift fix --kind c2 --close` 在待定決策行、未處理回頭條件時擋(`scripts/lumos:38596-38630`);`lumos set` 結案只列出、不擋(`scripts/lumos:36299`、`scripts/lumos:36323`、`scripts/lumos:52068`)。
- **查詢考卷**:
  - 分數退步只記錄,只在 `unjudged_rate ≥ 0.10` 時通知(`governance/eval/refresh_labels.py:424`、`governance/eval/refresh_labels.py:465`)。
  - 另考 `LandmarkMember`:`governance/autonomous-loop.sh:466`。
  - 推播漏網不發通知:`governance/autonomous-loop.sh:450-452`。
- **情境探針**:
  - 每場從基線複製(`scripts/scenario_probe.py:1259`)。
  - 全域 skills 健康檢查失敗、清不乾淨會讓整批停(`scripts/scenario_probe.py:1282-1289`、`scripts/scenario_probe.py:1386-1403`)。
  - 截斷與用量上限不計分,有效場次不到一半不下結論(`scripts/scenario_probe.py:1078-1103`)。
  - `--max-per-window` 預設 0 即停用,週跑沒帶(`scripts/scenario_probe.py:1168`、`governance/autonomous-loop.sh:383-386`)。
- **指令旗標**:`loop retro`、`loop cap-decision`、`loop fix-check`(說明含「約 5 分鐘,在背景跑」「只提醒不擋」)、`loop escape`、`lint-waive`、`note-audit reread-prepare` / `reread-record` / `reread-check`、`test-quality scan` / `capture` / `check`(三個位置參數加必填 `--target`)、`summary-line` 三個位置參數、`updated-sync --stale --dry-run`、`events --session`、`spec-gate`、`drift scan` / `fix` / `ack`(含 `--kind reread`),我都用 `python3.14 scripts/lumos <指令> -h` 對過,與指令參考一致。
- **頂層指令數**:`lumos --help` 有 85 個,「八十多個 / more than eighty」成立。
- **金環說法**:`assets/graph-demo-zh.svg` 與 `assets/graph-demo-en.svg` 的圖說是「帶合約,並連到驗證紀錄」,新文字與它一致。`lumos guard kill` 存在(`lumos guard -h`)。
- **更新清點**:
  - `git rev-list --count 20f41c8e..8e648f3d` 為 170。
  - 分類計數 chore 54、docs 38、feat 10、fix 37、merge 21、test 10 與 git 一致。
  - 表格有 170 列。
  - 20f41c8e 是上一份清點的提交,且是 8e648f3d 的祖先。
  - `release` 指向 `4a42dede`:`git ls-remote Lumos release`。
- **中英對應**:README 與指令參考兩邊的 hunk 一一對應。專案開關表中英各 11 列,「只列出、不擋」中英各 6 條。錨點 `#專案開關`、`#project-switches` 都存在。英文新增的「測試品質」一節與中文逐段對應,位置也相同。
- **寫法對齊**:首屏沒動。「圖譜」用詞保留。清點檔表頭與分組表格式與 10-07 版一致;少了「尚未合入」和「共用手冊接線核對」兩節,檔內已說明理由(未合併分支不列),可接受。

## 沒核對的範圍
- 沒有開 `docs/lumos-toolchain-knowledge` 的 Systems 節點,逐篇確認這次改動是否已寫回圖譜。
- 清點表 170 列的每一個提交雜湊與標題,沒有逐筆比對 git,只對了總數與分類。
- 沒逐條重驗 10-10 清點分組表裡各提交的功能描述。我只抽查了 `arch_targets`、回頭重讀、探針用量帳。
- `drift_check` 與 `note_reread` 的「寫壞設定的各種分支」,我只讀了簽名與 docstring,沒有跑實驗。

## 固定席筆記(圖譜鏡頭)
這次派工沒有附上固定席節點,只有「圖譜沒有釘到節點」的備援段(受影響測試 0、共改 0、呼叫者 0),那段不是合約。這份 diff 只改對外文件與新增一份更新清點,不改 `scripts/` 的任何行為或合約,所以沒有破壞任何已知節點宣稱的行為。

最高等級:minor
