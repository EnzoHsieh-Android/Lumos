severity: major

## F1 「歸因不明」沒排除無佐證列,真實資料會把 5 個不相干迴圈誤判成互相歸因不明
severity: major
blocking: 是 —— 照字面實作(用 sha/defect_ref 的值分組、值相同即算同一佐證),真帳上已有的 6 列會被誤判成「同一佐證跨迴圈」,把本來該落「無佐證」桶的列錯記成「歸因不明」,統計輸出的數字就是錯的
引句:「同一個佐證(同一個 sha 或 defect_ref)出現在兩個以上迴圈的列,不算進任何迴圈的分子,另列筆數。」
file: `docs/.escape-log.jsonl:3,4,5,6,19,20` —— 這 6 列的 `sha` 與 `defect_ref` 兩個欄位都不存在(機械查證,`python3 -c` 讀檔核對),分屬 5 個不同迴圈(`code-推播漏網量測`、`code-每支檔有家`、`lint-new-gate`、`評測尺修復`、`收工點名問版本控制`)。若判「同一佐證」的邏輯直接拿 `row.get("sha") or row.get("defect_ref")` 這種值來分組,6 列的鍵都是同一個空值/`None`,會被分進同一組、組內迴圈數 ≥2 → 整批誤觸發「歸因不明」。
第二節已經另外定義了「無佐證」桶(舊列兩個都沒有時歸「無佐證」,不算率的分子也不算去重鍵),但第四節「歸因不明」段落沒有寫「先扣掉無佐證的列,只在有值的列裡比對」這句話,兩段的執行順序沒有交代:實作者可能先做歸因不明分組(這時無佐證的空值互相撞在一起)、再做無佐證篩選,或反過來——兩種順序給出的「歸因不明」與「無佐證」筆數不一樣,而 spec 沒有講哪一種是對的。
不改的話,25 列裡已有的 6 列會被算錯,而且往後任何一批因故沒填 sha/defect_ref、又跨了兩個以上迴圈的手動記帳都會踩到同一顆雷。

## F2 `--withdraw` 沒有寫「不能跟記帳/查詢參數混用」的擋下條件,行為留白
severity: major
blocking: 是 —— 這正是專案裡明確認定過的同一類錯:允許使用者以為指令同時做了兩件事、其實只做了一件,前例(`--list` 跟記帳參數混用)已經被當成必須擋下的情況處理,`--withdraw` 卻沒有同等的規則
引句:「擋下的情況:目標 token 不存在、目標已經被撤過、目標本身是撤回紀錄(撤回不能再撤;要反悔就重記一列)、理由或撤回者去掉空白後是空的。」
file: `scripts/lumos:9434-9437` —— 現有 `--list` 分支明確擋下「--list 跟 loop_id/--stage/--severity/--desc/--defect-ref 混用」,理由寫得很白:「照原樣執行你會以為記了、其實一筆都沒寫」。這正是同一形狀的坑:`--withdraw <token>` 若跟 `loop_id`(正常記帳的位置參數)、`--stage`/`--severity`/`--desc`(記�3帳必填參數)、`--auto`、`--list` 混用時該怎樣,spec 全文(第三節「指令」「撤回紀錄長這樣」「擋下的情況」三個子彈)完全沒提。字面實作有兩條可能岔路:①靜默忽略多餘參數、只執行撤回,使用者以為同時記了新的一筆或改了別的欄位、其實沒有;②直接放行讓 `--withdraw` 跟 `loop_id` 一起落進既有「記帳模式:全部驗證在此」那段(第 9476 行起),因為現有程式碼走到那段只看 `loop_id`/`severity`/`stage`/`desc` 決定要不要記,`--withdraw` 是全新旗標、舊驗證邏輯看不到它,兩個模式的程式碼路徑會同時跑,寫出一筆正常記帳列「而且」順便處理撤回,兩者互相污染。spec 對「哪些組合要擋」給了撤回目標本身的四種擋法,但漏了「撤回跟其他模式參數同時出現」這一類,跟 `--list`/`--auto` 已經定義好的先例不一致。

已看,無:第一節 loop_kind 判法(loop 開頭 code- / 審查帳有 caught|missed|none 紀錄 / 否則 plan)跟現有 `cmd_canary_record` 對 kind 值域的用法一致,不影響既有行為。第二節手動記帳要求 sha 或 defect_ref 至少一項非空、否則要 `--missing-defect-ref` 附 ≥4 字理由,跟專案裡既有 `--refuted-set`(5739/7713 行)、`--responsibility`(13828/15347 行)「≥N 字含實字」的驗證慣例同構,可執行;`--sha` 目前的 help 文字寫「--auto 用」但 dest 已存在(`esc_sha`),手動模式要收也只是接掉這個既有欄位,沒有結構性阻礙。第三節撤回紀錄的形狀(自帶 token、不跟目標共用)、寫入走 `_jsonl_append_verified`+`_vault_write_lock`(跟 `_auto_escape` 現有的上鎖寫法同構)、`_escape_rows_for` 加 `include_withdrawn` 參數並把非物件 JSON 行當壞行,都跟現有 `cmd_loop_escape --list` 對壞行的處理方式(9452-9454 行)、`_plan_file_exists` 的 NFC 比對寫法(9380-9391 行)是同一套手法的延伸,沒有新的可執行性缺口;舊版 lumos 讀到撤回紀錄時 `--list` 會把它當成「?」迴圈底下一筆 `非標準值 None(手改帳?)`,不會拋例外(用 `_esc_clean` 對 None 做 `str()` 轉換,實測不會炸),跟 spec 說的「不會壞,只是吵」相符。`rule_gap` 沿用自己找檔的讀法(`docs/.escape-log.jsonl` 或 `<repo>/.escape-log.jsonl` 兩個候選)不受影響,舊版遇到撤回紀錄只會多算一筆「unlabeled」(因為沒有 `rule` 欄位),不會拋例外,屬於同一等級的「吵但不炸」,不是新缺口。第四節分母判準(治理帳 `gate=design-loop, kind=converged` 且 `nodes` 帶迴圈編號)機械核對過:`docs/.governance-log.jsonl` 裡確實有代碼審迴圈(`code-` 前綴)寫在同一個 `gate=design-loop` 閘名下、`nodes` 帶編號(258 筆 converged、其中 173 筆屬 code- 迴圈、114 個不同編號),`gate=code-loop, kind=passed` 的 `nodes` 確認是空陣列,跟 spec「不用它」的敘述一致(對照 r2-intake.md 的 r2a-F1 重現結果,MISS 已有正確處置)。「下一站接住」的四個站名(實作/code-loop/push-gate*)機械核對過現有帳上真實出現的 stage 值(`push-gate`、`code-loop`、`實作`、`CI`、`prod`、`使用者回報`、含專案名的消費專案推送字串),沒有大小寫或空白造成誤判的邊界情況。第 S10 條 `_plan_for_loop` 加 NFC 與去 `code-` 前綴,對照過現有唯一呼叫者(`cmd_canary_record` 第 8005-8010 行)自己已經先 `derived = str(loop)[len("code-"):]` 去過前綴,重複去除是 no-op,不影響既有行為,跟 spec「回退」節的說明一致。效能節提到的帳本大小(1.7MB/13MB)與 escape-stats 只是手動/唯讀指令不進任何閘,沒有邊界疑慮。

最嚴重 severity: major;blocking 共 2 條。
