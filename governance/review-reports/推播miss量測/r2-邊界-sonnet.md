severity: blocker

# 審查立場

本席替極端輸入發聲:零推播、同工作階段連續編輯同檔、編輯讀取交錯、子代理逐字稿、Codex 逐字稿、週邊界與時區、逐字稿時間欄缺漏、推播全文被截斷、節點路徑含空白/中文、同名筆記在不同資料夾、search 串管線。逐節讀完 r2-snapshot.md 全文,並對照 governance/eval/lens-utilization/recount.py、scripts/hooks/claude/impact-hook.py、scripts/lumos、governance/autonomous-loop.sh、~/.claude/projects 與 ~/.codex/sessions 下的真實逐字稿實測。

# 開頭(frontmatter/summary)

已讀,無 finding。四條 related 連結([[Projects/GraphRAG對節點關聯_調研]]、[[Projects/主session鏡頭利用率_計劃]]、[[Systems/retrieval-ranking]])與正文交叉引用逐一開檔核對存在。

# 緣起

已讀,無 finding。「那份計劃還掛著 REVISIT:2026-09-17」一句查證屬實——`Projects/主session鏡頭利用率_計劃.md` 第 16/89/93/135 行確有四條 REVISIT:2026-09-17。

# PRIOR-ART

已讀,無 finding。「零新元件」的措辭雖與 S4 新增 `lens_weekly.py`/`weekly/`/`local/` 字面有出入,但通讀語境是指「不建第二條獨立分析管線」而非逐檔零增量,正文本身也老實列出了新檔,不構成隱瞞或誤導。

## G1

severity: blocker
blocking: 是
敘述:S3 描述的三種零命中判法裡,排序模式與舊模式(`--legacy`/`--regex`)兩種的「結尾」字串跟 `scripts/lumos` 現有輸出對不上——真實輸出結尾另外還接了固定尾字("...想照檔名排加 --legacy)"、"...[已排除 code block,--code 可含]"),不是 spec 講的那兩句本身結尾。若照字面用 `endswith` 判斷,排序模式與舊模式兩種零命中會全部判不出,只剩 `--json` 模式還能用,S3 的核心產出(零命中次數)在真實資料上會系統性低估到接近零。
引句:「舊模式(`--legacy`,以及會自動退回舊模式的 `--regex`)結尾」
file: `scripts/lumos:3171`
file: `scripts/lumos:3186`
驗證:實跑 `python3 scripts/lumos search "quokkazzzz whompiter blorgnaxfoo"` 真零命中,排序模式最後一行是 `(共 0 篇候選,照相關性排序;想照檔名排加 --legacy)`;`--legacy` 模式最後一行是 `0 處 / 0 篇 [已排除 code block,--code 可含]`——兩者皆非 spec 所稱的「結尾」字串,且有/無命中時這段固定尾字都存在(用「絕對 查不到 的東西 xyzzy999」實測 139 篇候選時也接同一尾字),證明不是零命中專屬的特例文字。

## G2

severity: major
blocking: 是
敘述:S3 對「串了多個(`;`、`&&`、管線)」記判不出的規則,沒說清楚「`lumos search | head -N` 這種單一 search 後接過濾指令」算不算「串了多個」。抽樣本機十筆以上真實逐字稿裡的 `lumos search` 呼叫,幾乎每一筆都接 `| head -N`(含一筆真零命中案例,見附註),若照嚴格解讀全算「串了」判不出,S3 在真實資料上會幾乎收不到樣本。
引句:「一次 Bash 呼叫裡恰好一個 `lumos search` 才判;串了多個(`;`、`&&`、管線)的輸出分不開,記」
file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/9e5c5b9b-61bf-4a36-ba13-5ab423238854.jsonl`(idx 15840:指令 `scripts/lumos search "t_bad_command_gives_near_name_not_wall_of_text" 2>&1 | head -6`,輸出為真零命中「(共 0 篇候選,照相關性排序;想照檔名排加 --legacy)」;同份逐字稿另有 9 筆以上 search 呼叫同樣接 `| head -N`)

## G3

severity: major
blocking: 是
敘述:S2「讀取窗口」的錨點/讀取比對機制完全在單一逐字稿檔案內運作(`scan_file`/`scan_codex_file` 的迴圈只掃自己那份 `objs` 清單),但子代理逐字稿是獨立檔案(`*/subagents/agent-*.jsonl`)。實測確認主稿與子代理稿共用同一個 `sessionId`,但兩份檔案在現行架構與 S1/S2 描述裡都是各自獨立掃描、互不跨檔比對。若編輯後派子代理去讀查證筆記(本專案本身鼓勵的做法),那些讀取對母編輯的視窗完全不可見,會把「agent 真的讀了」錯記成 miss。
引句:「錨點是那次編輯本身**:逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列」
file: `governance/eval/lens-utilization/recount.py:348`(`scan_file` 迴圈只在單一 `objs` 內比對,跨檔案無關聯機制)
file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/1f020202-26e8-4a11-9a5b-b0c40ac7f2f7.jsonl`(與其 `subagents/agent-a6d5506d9a302f236.jsonl` 的 `sessionId` 欄位實測完全相同,但兩檔各自獨立掃描)

## G4

severity: major
blocking: 是
敘述:S5 只點名既有 `t_lens_recount_classify` 需要補 `_need_src` 守門,但實際 grep `scripts/test_lumos.py` 發現另外兩支既有測試(`t_codex_s3_recount_codex`、`t_codex_s3_r1_fixes`)也在函式體內引用了 `lens-utilization` 這段路徑字串,目前同樣沒有 `_need_src` 守門。S5 自己新寫的守門測試(掃「提到 lens-utilization 的測試函式」)如果照描述實作,會在這兩支被遺漏的既有測試上立刻抓到不合規,而驗收清單只交代要驗 `t_lens_recount_classify` 全綠,沒提這兩支。
引句:「本案新增的測試與既有 `t_lens_recount_classify` 都先」
file: `scripts/test_lumos.py:30583`(`t_codex_s3_recount_codex` 內有 `lens-utilization` 字串、無 `_need_src`)
file: `scripts/test_lumos.py:30649`(`t_codex_s3_r1_fixes` 內有 `lens-utilization` 字串、無 `_need_src`)
驗證:`sed -n '29862,29936p;30577,30619p;30644,30703p' scripts/test_lumos.py | grep _need_src` 三支函式範圍內均 0 命中;`grep -n "lens-utilization" scripts/test_lumos.py` 只有這三處,S5 只提到其中一處。

## G5

severity: major
blocking: 是
敘述:S4「上一個完整週」的週邊界判斷完全沒有講時區。逐字稿的 `timestamp` 欄位(Claude 與 Codex 皆同)是 UTC(`Z` 結尾),而 shell 端 `date +%G-W%V` 用的是系統本地時區(本機實測為 Asia/Taipei,UTC+8)。`run_replay` 本身沒有任何以時間戳過濾資料的邏輯(純輪替抽樣器),不是可借來的時區慣例先例,週日深夜到週一這段(本地 00:00–08:00)存在被錯歸到前一週的具體風險,驗收清單也沒有任何測試涵蓋這個邊界。
引句:「只收編輯時間落在上一個完整 ISO 週的列(逐字稿每行帶時間)」
file: `governance/autonomous_loop/replay_weekly.py:66`(`run_weekly` 全函式無任何時間戳過濾,只做輪替抽樣)
file: 本機 `date`/`python3 -c "import time;print(time.tzname)"` 實測回 `CST`(UTC+8);抽樣真實逐字稿 `timestamp` 值為 `2026-09-02T01:41:14.556Z` 等 UTC 格式,Codex rollout 同款,兩邊時區基準不同且 spec 未言明如何折算

## G6

severity: major
blocking: 是
敘述:S4 只講了單檔子行程 60 秒逾時,沒有整體時間預算,跟它聲稱效法的 `run_replay` 明確設 `BUDGET_SECONDS=300` 並會截斷不同。`take_lock` 是整支 `autonomous-loop.sh` 唯一的鎖,包住 run_exam/run_probe/run_nags/run_replay 到新的 run_lens_weekly 全部依序執行;遇到改動檔數異常多的一週(例如一次性大量檔案重構或 vendored 更新),run_lens_weekly 沒有總預算兜底,可能長時間佔鎖,讓當天後續排程或另一次觸發的 `autonomous-loop.sh` 直接判「別人在跑」而整支跳過。
引句:「每個子行程設 60 秒逾時,逾時那支檔的分類記」
file: `governance/autonomous-loop.sh:272`(`take_lock || { ...}` 是整支腳本唯一的鎖入口)
file: `governance/autonomous-loop.sh:449-454`(run_exam/run_probe/run_nags/run_replay 依序在同一次鎖內執行)

## G7

severity: minor
blocking: 否
敘述:S1 說「守衛面參考」段跟「可能相關」段是同一種分數行格式(「同上」),但實際上 `build_ranked_context` 對 lane 段的節點名直接印 `x.get('node','?')`,沒有像其他三段一樣過 `_plain_label()`(去控制字元、換行轉空白、120 字上限)。這是既有 hook 程式碼裡的既存不對稱,`_frame_injected` 的框線過濾仍能擋掉最嚴重的偽造系統話攻擊,但一行式解析假設(1 節點=1 行)在極端節點名(內嵌換行/超長)下只有這一段少一層清洗。
引句:「:同上(例 `0.20 hop1 Systems/c.md`);只有這一段、沒有必看段的注入也存在。」
file: `scripts/hooks/claude/impact-hook.py:667`(lane 段用 `x.get('node','?')`,未經 `_plain_label`)
file: `scripts/hooks/claude/impact-hook.py:653`(對照:可能相關段用 `_plain_label(x.get('node'))`)

## G8

severity: minor
blocking: 否
敘述:S1 的完整性判斷是整筆推播(整個 hook 附件)層級,只要四段中任一段解析行數不足標頭 N,整筆 `pushed_complete=false`,連帶讓其餘三段原本可靠的資料也一起被排除出三類統計。這是「不猜」哲學下可以理解的保守選擇,但 spec 沒有討論過這個顆粒度取捨,可能讓權重最低的守衛面參考段偶發截斷時,拖累原本完整可靠的必看段資料一起消失。
引句:「某段實際解析到的行數少於標頭宣稱的 N,或遇到認不得的段標頭 → 那筆 `pushed_complete=false`,它的 miss 不進三類統計、另計」

## G9

severity: minor
blocking: 否
敘述:讀取窗口以「下一次任何編輯」為界,不分是不是同一支檔案。若連續編輯 A 檔、B 檔,之後才回頭讀跟 A 有關的筆記,那些讀取會被算進 B 的視窗、不會算給 A,承認的限制段落沒有提到這個交錯編輯下的歸屬偏誤。
引句:「不重複算給更早的編輯。既有程式的窗口一路掃到逐字稿結尾」

## G10

severity: minor
blocking: 否
敘述:Codex 子代理稿的 `SubagentStart:dispatch-lens` 列(hook_name 不在 Edit/Write/MultiEdit/apply_patch 之列)沒有被 S1/S2 明確排除在「每次編輯都是一列」的錨點機制外。這類列現有實作固定回 `n_pinned=0`、`touched=[]` 的樁,若被誤套零推播規則,會把子代理派工的起手式誤判成一次零推播的編輯。
引句:「逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列,推播清單用呼叫編號去配 hook 附件」

# 條款其餘部分

- S1 的四段標頭字串、`PIN_LINE` 吃進種類詞的既有缺陷描述、截斷行文字(「(+N 條低分截斷,沒列出來)」「(另有 N 條守衛面參考未列出)」)全部逐字比對 `scripts/hooks/claude/impact-hook.py:641/650/656/660/665/669` 精確相符,已讀,無 finding(除 G7/G8 外)。
- S2 的 impact 直連兩條規則(body-inline-code 完整路徑/裸檔名 git 追蹤唯一)比對 `scripts/lumos:19819` `_impact_reverse_lookup` 精確相符;`pre_touched` 欄位確實是既有欄位(`scan_file`/`scan_codex_file` 都有)。已讀,無 finding(除 G3/G9/G10 外)。
- S4 效能實測數字查證屬實:全量重算 `time python3 governance/eval/lens-utilization/recount.py --repo .` 實跑 27.15 秒;`lumos impact --file` 單次實跑 1.76 秒。已讀,無 finding(除 G5/G6 外)。
- S6(README 同步)已讀,無 finding——是文件同步任務,無可驗證的技術宣稱。

# 邊界與不做

已讀,無 finding。「不動 impact hook、不動派工鏡頭...不改 `docs/.usage-log.jsonl`(F08)」與「不出單一命中率、不設門檻、結果不回灌排序」跟本案所有條款描述一致,沒有發現條款內容偷偷越界。

# 承認的限制

已讀,無 finding,除已在 G3/G5/G9/G10 分別列出的具體缺口外。「反方向,程式檔後來改名的,舊路徑在 impact 比對不到,本該是規則內的會掉進判不出」一句本身邏輯自洽,是本輪(r1 邊界席)新補的誠實揭露,沒有發現新的內部矛盾。

# 實務隱患

- 併發:已於 G6 指出額外風險(整體鎖佔用時長無上限)。
- 效能:已於 G6 指出(缺整體預算)。
- 資源:已讀,無新 finding——子行程重載整個圖譜是既有 `lumos impact` 的已知成本,spec 誠實揭露。
- 隱私:已讀,無 finding——查詢字串只進本機 gitignore 目錄、版控只留推導列,跟現有 `.gitignore` 沒有既存規則衝突(`git check-ignore` 實測該路徑目前確實未被忽略,新增規則不會跟舊規則打架)。
- 金流、對外送出、不可逆:已讀,無 finding——本案確實不碰這幾類。

# 驗收

已讀,無 finding,除 G4/G5 指出的具體缺口外。七條驗收案例文字都能對回 S1-S5 的條款描述,沒有發現案例本身自相矛盾。

# 審計修正紀錄

已讀,無 finding。`governance/review-reports/推播miss量測/` 下確有 r1 四席(通才/邊界/架構對齊/整合)報告與 r1-intake.md,跟「四席」「r2 補派」的敘述一致。

# 圖譜鏡頭:固定席節點逐條判斷

- `Systems/canary-audit.md`(★INVARIANT★ ×2,canary record/second 落盤與純 telemetry):不影響——本案明文「不寫任何帳」「不進 hook、不進 `lumos gov`」,recount.py/lens_weekly.py 全程不呼叫 `lumos canary record`,不動 `.canary-log.jsonl`/`.governance-log.jsonl`/loop status,兩條 INVARIANT 的寫入路徑與 gate 輸出都沒有被本案觸碰。
- `Systems/retrieval-ranking.md`(牽連 `retrieval_eval.py`):不影響——本案只讀 `edit_universe`/`refresh_labels.py` 既有流程作為說明對照,不改它們的程式碼,且明文「結果不回灌排序」,排序行為不受影響。
- `Issues/vendored測試套件在消費端假紅.md`(牽連 `retrieval-goldset.json`):部分相關但本案是在**修正**這個既有教訓(S5 就是照這個 Issue 的教訓加 `_need_src` 守門)——唯一的問題是修正範圍不完整,已列在 G4,不是本案破壞了這條教訓,而是本案想落實卻漏了兩支既有測試。
- `Issues/canary-record未落盤事件.md`:不影響——本案不寫任何 canary record,無寫後自驗需求。
- `Issues/code-loop守衛main-direct盲區.md`:不影響——本案新增的檔案是 JSON 報表與唯讀腳本,不是 gate/guard 類程式碼,不落在這個盲區描述的「main-direct 繞過 code-loop」風險範圍內;`autonomous-loop.sh` 本身在 run_exam/run_probe/run_nags/run_replay/新增的 run_lens_weekly 這段也沒有自動 git commit/push 動作。
- `Issues/hook卸載殘留註冊.md`:不影響——本案不動 hook 安裝/卸載/`settings.json` 註冊。
- `Issues/init-force-slug誤用basename.md`:不影響——本案不動 `lumos init`/slug 邏輯。
- `Systems/known-pitfall-refresh-token.md`:不影響——本案與 OAuth/refresh token 輪換無關。

# 總結

全份最高嚴重度是 blocker,blocking 共 6 條。
