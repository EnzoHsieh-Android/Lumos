你是外部第三方 code reviewer。這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找作者沒看到的洞。
這是第 3 輪、也是最後一輪審查:火力只放在 blocker 與 major(照這份上線會做出錯的判定、該擋沒擋、不該擋卻擋、資料被刪或寫壞、兩個指令互相蓋掉);minor 照寫但不必硬湊,沒問題就交 clean。上一輪修了:合約行尾只認工具接上去的 [test:]/[audit:]/[kill:]、已有正式行綁別的測試或預告行重複時 settle 擋下、逐提交讀狀態的批次讀失敗回判不了(也影響筆記內容審的完成審)、預算在每一步開始前都看並把剩下的時間傳給批次讀、plan_refs 同一份計劃兩種寫法照樣算、猜不準那一項不列守衛紀錄、status_replay 用上一版自己的圖譜位置、scan 列出解不開的筆記並記 degraded、doctor Z 段只剩已表態時不開段、doctor 閘提醒照鄰居的設定檔防護與參數形狀、Env 宣告 undecodable、幾支函式拆短(_note_status_seq/_git_log_sha_paths/_note_base_status/_drift_scan_print)。

Diff 檔(git diff -U10,凍結版,引句只准引這份):
- 程式:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/code-存量漂移防線甲/r3-snapshot.patch(這是第 2 輪修正差異:從上一版 e72324b8 到這一版的差異,含 scripts/lumos、scripts/test_lumos.py、Systems 筆記與 .lumos/lint-waivers.json)
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(可 Read/Grep 真代碼查證上下文;python3 零依賴單檔 CLI scripts/lumos,測試 scripts/test_lumos.py,單支跑法 `python3 scripts/test_lumos.py -k <測試名片段>`)。
設計(這份 diff 要兌現的規格):同 repo 的 docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md(本次只做「甲」:〈做法〉第 0 節裡 check/scan/ack/exam 與 doctor Z 的甲部分、第 1 節全部、第 3 節 commit/status_replay/current_state 三種考法;「乙」(條件式回頭條件)還沒做,不要報「乙沒做」)。
被考的 rtb repo 唯讀複本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/rtb-exam(只准 git -C 唯讀指令;考卷 governance/eval/drift-exam/rtb-2026-09-28.json)。

變更主題:
- guard settle 轉正時把 guard plan 樣板寫的四種預告句改成歷史說法(跟狀態一致檢查 c1 共用一支行首前綴比對);settle 拆成兩步、做到一半可以重跑補完、已經 pass 回 0;guard plan/settle/abandon 各自整段拿筆記庫寫入鎖。
- 新增 lumos drift:check(推送閘,只擋「範圍裡守衛紀錄 pending→pass 還留著預告句」,c2–c5 只列出,判不了算要處理)、scan、ack(表態檔 governance/drift-acks.jsonl)、exam(考卷重放、--history)。
- 五種狀態一致檢查 c1–c5 能跑在磁碟的圖譜或任一提交的樹上:為此把 load_vault 的單篇解析抽成 _note_from_text、Env 多了 from_texts 與 env_text。
- 跟筆記內容審共用的兩段改成參數化:逐提交讀 status 的 _note_audit_closed_plans 抽成 _notes_status_flipped;_note_audit_resolve 多了 gate 與 mark 參數。
- lumos set 把計劃改成 done/superseded 時列連帶待辦;doctor 多一段 Z。

錨定紀律(硬性):
- 每條 finding 必附一段從凍結 diff 逐字複製的原文引句(≥10 字),寫成單獨一行「引句:「…」」,引句內不要再包「」、不要跨行。
- 審材外查證寫成單獨一行「file: `路徑:行號`」(反引號必加)。
- 你指出的 blocker/major 必須附能當場翻紅的最小重現(一條測試或一條指令+輸出);附不出就如實標「未能重現」,severity 自降一級。
- git 實驗一律 git -C <你自己 mktemp 的臨時目錄>;不准在任何 repo 根跑 commit/reset/restore/checkout/stash,不准改任何 repo 裡的檔;不要執行任何掛鉤腳本。

抑噪紀律:
- 低嚴重度疑慮,給不出具體失敗場景就不要標。但未定義的詞、壞引用、內部不一致一律要報。
- 不能從 diff 指出具體受影響的 file:line,就不准臆測「可能會壞別處」。
- 不要讀 governance/review-reports/code-存量漂移防線甲/ 裡除了上面那份 patch 以外的檔(尤其不要讀 r1-*.md、r2-*.md 的席報告)。

輸出格式(硬性,收貨端機械檢查):
- 檔首第一個非空行:severity: <整份最高 clean|minor|major|blocker>
- 每條 finding:標題行「## F<n> <一句話>」(標題裡不寫等級);接著獨立一行「severity: <值>」、獨立一行「blocking: 是|否 — 一句判準」(否↔minor;是↔major/blocker);一行「引句:「…」」;敘述編號條列,只寫到讓人能重現為止——哪個輸入、走到哪一行、壞在哪;不准用「可能/或許/建議考慮」收尾,判不準在敘述裡標 ⚠。
- 某塊沒問題也寫「已看,無 finding」。沒找到問題就交 severity: clean。
- 最後一行總結:最嚴重等級、blocking 共幾條(總結句裡不要寫 severity 字樣)。
- 報告只寫進指定的報告檔,不改任何其他檔;交回時只回一句「報告已寫到 <路徑>,最高 X,共 N 條」。
