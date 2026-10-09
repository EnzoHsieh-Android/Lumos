severity: minor

審查範圍:修補 0221bd2e → b53500e2(完整改動入口 2494971e)。我在 `/tmp/lumos-seat-work/code-README與指令參考校正-std/正確性2-sonnet/repo` 這份淺層複製上做了讀碼與實跑,沒動原工作目錄。

## F1 專案開關表前言說「各自在什麼情境用,見 skill 手冊 06、07」,多數開關在這兩份手冊裡根本沒寫
severity: minor
blocking: 否

引句:「這張表是各開關的彙整；各自在什麼情境用，見 skill 手冊 06、07。」

- 失敗場景:讀者想查 `lint_new.gate`、`note_lint.gate`、`note_shape.tag_hints`、`close_summary`,照指引去翻 06、07,找不到。`grep -rn "lint_new\|note_lint\|tag_hints\|close_summary" skills/` 零命中。
- `drift_check.*` 只在 04、08 出現。`node_home` 在 03、09 和 reference.md,不在 06、07。06、07 實際只講到 `note_reread`、`note_shape`(含 test_refs、slots)、`stack_questions`、`note_audit`。
- 證據:`skills/lumos-project-notes/commands/06-代碼審與推送.md`、`07-安裝維運.md`;英文版 `docs/command-reference.md:151` 同句。
- 歸因:有證據的修復回歸。修前 `git show 0221bd2e:docs/指令參考.md | grep -c "見 skill 手冊 06、07"` 得 0,修後 `b53500e2` 得 1。這句是修補新加的。

## F2 新增的四個 note_shape 提醒開關列沒講「note_shape.gate=off 會連它們一起關掉」
severity: minor
blocking: 否

引句:「提交時只提醒的寫法檢查：否定現況句、筆記前綴、結案摘要、新寫句子（一行綁多支測試、數量句等）」

- 失敗場景:專案把 `note_shape.gate` 設成 `off`,想著只關舊的程式行號檢查,卻發現四種提醒也全沒了。四個開關各自預設 warn,列裡沒有任何依賴說明。
- 證據:`scripts/lumos:33088-33089` 在 `mode == "off"` 時直接 `return 0`。四個提醒的 `_ns_negation_prepare`、`_ns_tag_hints_prepare`、`_ns_wording_prepare` 與 close_summary 收集,都排在 `scripts/lumos:33093` 之後,所以 gate=off 時不會跑。
- 對照:同表 `note_shape.slots` 列就寫了「也受 `note_shape.gate` 管」。
- 開關鍵名(`negation`、`tag_hints`、`close_summary`、`wording`)、值域(warn/off)、預設(warn)我讀 `_note_shape_mode_parse`(`scripts/lumos:31449-31470`)都核對對了。
- 歸因:有證據的修復回歸。修前 `git show 0221bd2e:docs/command-reference.md | grep -c "note_shape.negation"` 得 0,修後得 1,這一列是修補新加的。

## F3 清點「README 處置」欄仍說 README 註明用量帳預設不開,但這輪修補把 README 這句拿掉了
severity: minor
blocking: 否

引句:「評測一節補一段保護說明（README 只留一句，細節在這份清點）；用量帳註明預設不開（週跑沒帶 `--max-per-window`）」

- 失敗場景:讀者照這欄去 README 找「用量帳預設不開」,找不到。README.md 和 README.en.md 全文已無「用量帳」、「usage ledger」。
- 前半句「細節在這份清點」成立:同一列第一欄仍寫「選配本機用量帳跨批次限制啟動次數」。但「預設不開」只剩在處置欄的這半句裡,README 並沒有這個註明。
- 驗證:`git show 0221bd2e:README.md | grep -c 用量帳` 得 1,`git show b53500e2:README.md | grep -c 用量帳` 得 0,而兩版清點檔的 `用量帳註明預設不開` 都是 1。
- 歸因:有證據的修復回歸。README 那句是修補拿掉的,處置欄沒跟著改。

## F4 審查回放通知條件「補齊」後仍漏講:補漏凍結失敗、逾時、游標寫入失敗也會通知
severity: minor
blocking: 否

引句:「審查回放有案子結論對不上、需要重新凍結、舊案凍不了或逐案回放出錯，以及情境探針有題沒過，會通知人」

- 失敗場景:一個已收斂、帶 spec_path 的舊案,補漏凍結時 `loop replay --freeze` 回非零。週跑會把它放進 `errors` 並發 LINE「回放執行錯誤:freeze:<id>:rcN」,但 README 的「逐案回放出錯」講不到這種「凍結出錯」。逾時和 `cursor:write-fail` 也一樣。
- 證據:`governance/autonomous_loop/replay_weekly.py:101`、`104`、`127`、`136`、`162` 全進同一個 `errors` 清單,`replay_weekly.py:175-176` 只要它非空就發訊息。
- 紅燈(結論對不上)、過期(需重新凍結)、舊案凍不了這三項的對應都正確。讀者照 README 做不會做錯事,只是「補齊」沒補全。
- 歸因:未判定。修前文字是「審查回放執行出錯也會通知」,範圍更廣;修後的「逐案回放出錯」較窄。英文版 "errors out on replay" 同樣偏窄。沒有證據證明這是修補才讓它不準,但它仍是修補主題裡沒補全的條件。

## F5 規格閘家筆記的摘要仍留著 2026-09-17 的「半套只印不擋紅綠、不寫審查帳」,與同篇 FLOW 行和新補的一條互相矛盾
severity: minor
blocking: 否

引句:「跟上面第⑤步不符,指令參考也照抄成不擋」

- 失敗場景:下一個 session 讀這篇的摘要,先看到 `規格閘.md:19` 的 `KEY:[2026-09-17]半套只印不擋紅綠、不寫審查帳`,會以為風險低也不擋、也不寫帳。實際上同篇 FLOW 行和 `cmd_spec_gate` 都是風險低要擋(`scripts/lumos:7809`)、兩種門都寫審查帳(`_spec_gate_record`)。
- 修補在正文尾端補了一條 2026-10-10 校正,但沒處理摘要這一行。
- 歸因:有證據的原有漏查。`git show 0221bd2e:"docs/lumos-toolchain-knowledge/Systems/規格閘.md" | grep -c 半套只印不擋紅綠` 與 `b53500e2` 都是 1。這一行不是修補引入的,但修補改了這篇卻漏掉它。

## 三問與各鏡頭結論

**① 原問題的修復效果有何行為證據?**
- `python3.14 scripts/lumos spec-gate --help` 與 `--help` 總表都印出新說法。
- 三種情境我讀碼走過:
  - 風險低:`scripts/lumos:7809` 紅綠不符就 rc1。
  - 風險高:只印不擋,走 `loop next`。
  - 相依回歸:`scripts/lumos:7807` 不分門,紅就 rc1。這個「紅」其實還包括懸空、弱證據和跑不起來,文件只說「紅」,可接受。
- 新測試 `t_spec_gate_help_says_low_risk_blocks` 在修後版本綠。
- 查詢考卷門檻:`governance/eval/retrieval_eval.py` 的 `collect_unjudged` 分母是計分觸及的候選筆記,分子是沒標的。`refresh_labels.py` 的 `signal --threshold` 預設 0.10,`autonomous-loop.sh` 只 grep `over=yes`。所以「計分觸及的候選筆記沒標過的比例」成立,「題目都有標準答案也可能觸發」成立。
- 派工掛鉤:`scripts/lumos:47129-47174` 的 `lens_fail` 六種原因(`not_git`、`commit_missing`、`sha_unresolved`、`no_mainline`、`base_not_mainline`、`empty_range`)都會讓 `dispatch-lens-hook.py` 附一行。格式錯誤的範圍回 rc2 且不帶 `lens_fail`,所以「範圍格式寫錯不在此列」成立。
- `lint_new` 與 `stack_questions` 讀工作目錄那份,`note_lint` 在 `scripts/lumos:1992` 與 `6518` 同樣讀工作目錄,與前言說法一致。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立?**
- `python3.14 assets/readme-diagrams/generate.py --check` 綠(22 張 SVG)。
- 圖內可見字沒動,只動 `<desc>`。desc 的「candidate notes」與 README 兩版一致。
- 連結都指得到:`docs/updates/2026-10-10-readme-audit.md`,以及 `../skills/lumos-project-notes/commands/07-安裝維運.md`。
- 中英兩份指令參考的每一列逐項對得上。
- `python3.14 scripts/test_lumos.py -k spec_gate` 得 104 passed、0 failed。
- `--suite docs` 得 733 passed、0 failed,另有 1 支 skipped(`t_codex_s1_r1_fixes`),被 `EXPECTED_SKIP_MAX` 判紅。我是在 `git clone --shared` 的複本上跑的,這支屬來源 repo 專用,我判斷是複本環境造成,不是這次改動造成,但沒在原目錄驗證。案例檔寫的是 736 條,我的實跑數不同。
- 圖譜鏡頭:diff 動到的是 help 字串、新增一支測試、`generate.py` 的 desc 字串和兩篇家筆記。上面列的 INVARIANT 合約(處置閘第五步、search 排除 superseded、還原翻紅釘、bound-tests 合約、guard kill、reinject、授權檔)的程式路徑都沒被碰。授權檔那條的 SPDX 檔頭也沒動。我判不影響,但沒有逐條實跑那些合約綁定的測試。
- 角色卡:be-api-compat 與 be-authz 都不適用。只改 argparse help 文字、沒有新增或改名任何對外欄位、旗標、端點。argparse 的旗標與位置參數形狀沒變。

**③ 新發現在修前、修後各是什麼結果?** 見各 finding 的歸因與 `git show 0221bd2e:… / b53500e2:…` 對照:
- F1、F2、F3 修前不存在,修後出現。
- F4 未判定。
- F5 兩版都存在。

**鏡頭 2:新測試的脆度**(不另立 finding)
- 回退測試:
  - 把 `HELP_WHEN` 改回「印紅綠(不擋)」,① ② 轉紅。
  - 只把總表那一行改回舊字,③ 轉紅。
  - 所以三條斷言各自釘得住「還原舊字」。
- 弱點:改成「風險低時紅綠是放行條件(不擋)、風險高也不擋。」三條斷言全綠,語意已反卻抓不到。測試只釘子字串,守不到 README 或指令參考,也不守實際的 rc。
- 我判這是 help 文字守衛的合理成本,所以只報在此。

最高等級:minor
