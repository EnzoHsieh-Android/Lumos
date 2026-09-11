# 主 session 鏡頭利用率——唯讀重算

單源:`docs/lumos-toolchain-knowledge/Projects/主session鏡頭利用率_計劃.md`(第一段:零新元件)。

重跑:
```
python3 governance/eval/lens-utilization/recount.py --repo . [--json] [--out 報表.json]
```
讀 `~/.claude/projects/*/` 下所有逐字稿(主+`subagents/`),用逐字稿行的 `cwd` 篩「在本 repo 或其 worktree 之下」;
只認 `attachment.type == hook_additional_context` 且 `hookName ∈ PreToolUse:Edit|Write|MultiEdit` 的注入;
固定席從注入全文解析(新舊兩種「必看」標頭;事故行沒有 ★TAG★);錨點=toolUseID 對到的那次 tool_use 行序。
★只印分佈,不出單一命中率、不設門檻;不寫任何帳;結果不進 hook、不進 lumos gov★。
逐字稿依 Claude Code 的 cleanupPeriodDays(預設 30 天)會被清,歷史窗有限。

## Codex 逐字稿(2026-09-04,Projects/Codex完全支援_計劃 S3)

- 多讀 `--codex-sessions`(預設 `$CODEX_HOME/sessions` 或 `~/.codex/sessions`,遞迴找 `rollout-*.jsonl`);第一行 `session_meta` 的 `cwd` 篩本 repo,`cli_version` 不在 `CODEX_TRANSCRIPT_VERSIONS`(目前 `0.144.1`)就整份跳過、不猜。
- hook 注入在 Codex 稿裡★實測★落在 `response_item/message role=developer`——但這型別不是 hook 專屬(權限說明、skills、插件、團隊指令也都是 developer 訊息),真正的辨識靠首行標頭(「必看——這 N 篇」/「LUMOS-LENS range=」),不靠 role;主代理稿的「必看——」列成 `PreToolUse:apply_patch` 行;子代理稿(`thread_source=subagent`)的「LUMOS-LENS range=…」列成 `SubagentStart:dispatch-lens` 行(只計筆數,沒有釘住清單可比)。
- 錨定是啟發式:Codex 沒有 toolUseID,取同一輪內離注入最近的 apply_patch 呼叫(先往後找再往前找;實看兩種順序都有),目標檔=其 patch 標頭第一個路徑。
- 「有沒有讀」的判法跟 Claude 行同一支 `classify_bash`(exec 的 `cmd` 字串,有引號/無引號 key 都抽);rows 帶 `harness` 欄,summary 多 `by_harness`/`codex_lens_rows`/`codex_files`。
- 天花板同 Claude 行:只證「注入後有沒有動作碰到釘住的節點」,不證有沒有讀懂。


## 推播漏網(2026-09-11,Projects/推播miss量測_計劃)

上面那段看「推了的有沒有被讀」;這段看反面——**沒推卻被 agent 自己讀了的筆記(miss)**。程式在同一支 `recount.py`(`run_misses` 那一段),週跑由 `governance/autonomous_loop/lens_weekly.py` 叫。

重跑(手動、或補漏跑的週):
```
python3 governance/autonomous_loop/lens_weekly.py . [--week 2026-W37] [--archive-dir 別的目錄] [--budget 300]
```

- **推播四段都認**:「必看」「可能相關的 N 篇」「另外 N 篇分數不高但直接提到這個檔」「守衛面參考」;舊版三段(直接提到/間接牽到/過去的事故)也認。分數行切成分數、種類詞、路徑;截斷行(「+N 條低分截斷」「另有 N 條守衛面參考未列出」)不算推了;效能檢核題、多檔 patch 的「只算了前 N 檔」說明、收尾指示、框線認得、跳過。某段行數少於標頭 N、或有認不得的段 → 那筆 `pushed_complete=false`,它的 miss 不進三類統計。
- **錨點是每次編輯本身**:Edit/Write/MultiEdit(Codex 是 apply_patch)各一列,只收 impact hook 自己判斷會處理的檔(`_decide_one`);配不到推播附件=零推播,照樣算。Claude 用 toolUseID 配;Codex 沒有呼叫編號,配同一輪最近的 apply_patch,同一輪兩次以上就記配不準。一次改多檔時各檔共用那次推播的聯集。hook 對同一支檔推過(開窗)之後,冷卻窗內(`ttl_min`,預設 20 分)再改只跑事故快速路:那支檔看得到的=開窗那次 ∪ 窗內快速路推的(`cooldown_inherited`),窗逐檔記、不因快速路延長。每列帶 `pushed`(看得到的推播節點)與 `used`(推了、之後讀了)。
- **讀取**:事件先後看(行序, 同一則訊息裡第幾個工具呼叫),同一則訊息先改後讀照樣排在編輯之後。Read 工具(結果是錯誤的不算)、單純讀動詞、`lumos context|show|contracts`(裸名在節點清單唯一才認)。每筆讀取只算一次:先往前找最近一次「跟這篇有關」的編輯,都沒有才給最近一次。推了的、那次編輯之前就讀過的不算。
- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F(借 lumos 本體的開頭欄位解析,清單與單值都認,單行 `[a, b]` 多拆一步);判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計;總預算用完、git 沒問到的筆記一律當存在(`git_skipped` 計數)。
- **搜尋零命中**:配 Bash 呼叫與它的輸出;先逐行、再用 hook 的切段函式切(`;` `&&` `||` `|`,引號內不切),恰好一段含 `lumos search` 才判(後面接 `| head` 之類是另一段,照判)。認三種現行輸出(看整段輸出裡有沒有那一行):排序模式一行以「(共 N 篇候選」開頭、`--json` 的 `candidates`、舊模式一行以「N 處 / M 篇」開頭。其他、串了兩個、背景執行 → 判不出。
- **週跑**:自主迴圈週期觀測段的 `run_lens_weekly`(照 `run_replay`:週戳 `.weekly-stamp`、`date +%G-W%V`、模組失敗不蓋戳)。只收編輯時間(換成本機時區)落在**上一個完整 ISO 週**的列,寫 `weekly/<週>.json`(版控;工作階段代號雜湊、repo 相對檔名、節點名、分類、計數——不存逐字稿原文、不存查詢字串);零命中查詢字串寫 `local/<週>-queries.json`(gitignore)。同週重跑覆寫同一份;漏跑的週不自動補。總預算一把管整次:掃逐字稿用完就不再開新檔(`files_unscanned`)、分類用完就不再叫 impact / git,兩種都標 `budget_hit`。逐字稿壞行只跳那一行(`bad_lines`)、Codex 版本不在認得的表整份跳過(`codex_version_skipped`)、缺時間的行沿用前一行時間(前面都沒有的編輯計 `edits_without_time`、不收)。
- **天花板**:只證「沒推卻被讀」,不證那篇真的該推(位置偏差之外的相關性要人標);用現在的圖譜判當時的推播(編輯後才補上 F 路徑的筆記會被算成該推沒推);子代理的讀取不算給主 session 的編輯(少算);Bash 改檔沒有推播、量不到;零命中判法靠輸出字樣,措辭一改就會數錯(有測試釘住現行三種)。回頭條件都在計劃筆記。
