# B 面白話對照表:hooks(pre-commit / pre-push / post-commit / claude hooks / lumos 特定指令)

範圍:`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`scripts/hooks/post-commit`、
`scripts/hooks/claude/check-graph-sync.py`、`scripts/hooks/claude/impact-hook.py`、
`scripts/hooks/claude/ci-status-hook.py`、`scripts/lumos` 的 `cmd_pitfalls`(提問句+tier 訊息)、
`cmd_code_loop`(pass/skip/check 訊息)、`cmd_delguard_check`/`cmd_cochange_*`(警告句)。

本輪只做對照表,不改檔。表格「建議白話」欄用 `<br>` 換行,對應原文規格的「指令另起一行」要求。

---

## A. scripts/hooks/pre-commit

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| pre-commit:50 | Gate CC 前置:這台機器找不到 python3 或 scripts/lumos | `pre-commit: 無 python3 或 scripts/lumos,跳過 co-change 警告` | 提醒:這台機器上找不到檢查用的程式,這次沒辦法確認「改一個檔會不會漏改搭配的檔案」。<br>不影響這次提交,只是少了一項自動檢查。 | 無 |
| pre-commit:70-79 | Gate 1:staged 圖譜筆記的日期欄位被工具(如 notesmd-cli)動過手腳、加了引號,格式被污染 | `🚫 圖譜污染指紋: frontmatter 日期欄位被加引號 (典型來源 = notesmd-cli frontmatter --edit)` … | 擋下:這次要提交的筆記檔案,日期欄位被工具動過手腳、變成不對的格式,而且整篇欄位排列可能被打亂,沒辦法看出真正改了什麼。<br>先確認是不是不小心用了會搞壞格式的工具,再決定要修好還是還原。<br>看差異:<br>`git diff --cached -- <圖譜資料夾>`<br>還原:<br>`git checkout -- <檔案>`<br>如果真的是刻意這樣做(很少見):<br>`git commit --no-verify` | 無 |
| pre-commit:96-104 | Gate L:staged 的圖譜筆記沒通過格式自我檢查(例如一個欄位塞了兩個連結卻沒分行寫) | `🚫 lumos lint 未過: $f` … `修到 lint 綠再 commit;確屬刻意 → git commit --no-verify(留一句為什麼)` | 擋下:這次要提交的筆記格式有問題(例如一個欄位裡塞了兩筆連結卻沒有分開寫),不修好會讓之後的自動比對失效。<br>自己檢查:<br>`lumos lint <筆記名稱>`<br>改到通過再提交;確定要跳過:<br>`git commit --no-verify`(請留一句原因) | scripts/test_lumos.py:3818-3841(t_precommit_lints_staged_graph_nodes)斷言 rc==1 且 stdout+stderr 含字串「lint」——白話需保留「lint」這個字(如指令名 `lumos lint`)。 |
| pre-commit:145-167 | Gate 2/3:這次提交改了程式碼,但沒有任何圖譜筆記(.md)一起被 staged | `🚫 Pre-commit graph sync gate (git native hook): commit 改了原始碼但沒同步圖譜` … | 擋下:這次提交改了程式碼,但沒有同步更新說明這些程式碼的筆記。<br>之後看筆記的人(可能是你自己)會對不上實際的程式碼。<br>這次改的程式碼檔案(最多列出前 10 個):<br>`<路徑逐行列出>`<br>請選一條:<br>1. 補寫筆記後一起提交:<br>`git add <筆記路徑>`,再重試 commit<br>2. 確定這次不需要筆記(像是打字修正、格式調整、註解):<br>`git commit --no-verify -m "..."` | 無(t_precommit_vendored_exempt 只驗 rc,不驗文字) |

## B. scripts/hooks/pre-push

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| pre-push:33 | 這台機器找不到 python3 或 scripts/lumos | `pre-push: 無 python3 或 lumos,跳過圖譜巡檢(GitHub Actions CI 在 push 後兜底)` | 提醒:這台機器上找不到檢查用的程式,這次 push 前沒辦法巡一遍筆記的健康狀況。<br>之後遠端會補跑一次,不用太擔心。 | 無 |
| pre-push:41-48 | 錨點驗證:負責把關的檢查程式本身被改動過,跟原本存的版本兜不上 | `🚫 pre-push: anchor verify 失敗——驗證器檔案與 baseline 不符,push 已擋下` … | 擋下:負責把關的檢查程式被改動過,跟原本留存的版本不一樣,沒辦法信任接下來的檢查結果。<br>請選一條:<br>1. 不是故意改的 → 還原後重 push:<br>`git checkout -- <被動過的檔案>`<br>2. 確實是刻意要改 → 先取得核准:<br>`lumos anchor approve --note "理由"`<br>3. 都不是,先放行(會留下記錄):<br>`git push --no-verify` | 無 |
| pre-push:56 | push 前開始跑一次完整測試(僅本工具原始碼專案) | `pre-push: 跑 test_lumos.py 全量(源 repo 測試閘,~32s)…` | 提醒:push 前先跑一次完整測試,大約 30 秒。 | 無 |
| pre-push:59-67 | 完整測試跑完,有沒過的 | `🚫 pre-push: test_lumos.py 有紅——push 已擋下(完整輸出: /tmp/lumos-prepush-tests.log)` … | 擋下:push 前跑的測試沒有全部通過。<br>帶著壞掉的測試推上去,之後大家都會踩到同一個坑。<br>完整結果存在:<br>`/tmp/lumos-prepush-tests.log`<br>請選一條:<br>1. 修到全部通過再 push<br>2. 確定這次可以先放行(如環境造成的偶發失敗):<br>`git push --no-verify` | scripts/test_lumos.py:9141-9142,9149-9150(t_prepush_test_gate)斷言 stderr 含「test_lumos.py 有紅」與「--no-verify」——白話**必須**保留這兩段字串。 |
| pre-push:99-105 | 這次要推送的 diff 掃到寫法上的常見風險(併發/效能/資源類),本身不擋 push | `⚠ pre-push:$_rref tier=high(代碼形態風險命中 $_range,見下)` | 提醒:這次要推送的改動裡有寫法上的風險(像是資源沒確定關掉、可能有併發問題),細節列在下面。<br>push 前值得看一眼,能省下之後排查的時間。 | 無 |
| pre-push:113-120 | 上一則風險提醒沒有被複查或明確放行,push 被擋下(僅限推到分支的情況) | `🚫 pre-push: $_rref tier=high 代碼未過 code-loop → push 已擋下` … | 擋下:這次的高風險改動還沒經過複查,也沒有人明確說「這次先跳過」,所以 push 不了。<br>高風險改動沒人看過就推上去,是最容易出事的環節。<br>請選一條:<br>1. 找人複查改動,通過後重 push<br>2. 複查過、覺得是誤判或可以先跳過(會留下紀錄):<br>`lumos code-loop skip --note "<原因>"`<br>3. 真的很急、要先跳過(不留原因):<br>`git push --no-verify` | scripts/test_lumos.py:8940-8946(t_codeloop_guard_prepush 情境A)斷言 stderr 含「code-loop」(或「lumos-code-loop」)、「skip」、「--no-verify」——白話**必須**保留這三個詞(建議版本已含)。 |
| pre-push:127 | 推送對象不是一般分支(如標籤 tag),即使掃到風險寫法也不擋 | `💡 pre-push: $_rref 非分支 ref、tier=high——advisory 放行(tag 內容 gate 另訂策略)` | 提醒:這次推送的不是一般分支,雖然掃到風險寫法,但這種情況目前只提醒、不擋下(advisory)。 | scripts/test_lumos.py 的 t_prepush_range_scan(tag 情境)斷言 stderr 含「advisory」——白話需保留「advisory」一詞,或明寫測試需同步改斷言。 |
| pre-push:132-134 | 這次改動的檔案類型有對應的效能檢查清單(kt/cs/vue/sql 各自的常見地雷),不擋、只提醒 | `💡 pre-push:$_rref 棧別效能檢核(advisory,不擋;終審留痕請含答案)` | 提醒:這次改動的檔案有對應的效能檢查清單,順手看一下能省下之後排查的時間(不會擋下 push)。 | 無 |
| pre-push:153-161 | push 前巡檢筆記健康狀況,發現問題(連結斷掉、該補的紀錄沒補) | `🚫 pre-push: lumos doctor 發現圖譜問題(見上方),push 已擋下` … | 擋下:筆記巡檢發現有問題(像是連結斷掉、該補的紀錄沒補齊),詳細內容列在上面。<br>筆記壞掉沒人發現,之後找資料的人會被誤導。<br>請選一條:<br>1. 把上面列出的問題修好再 push<br>2. 覺得是巡檢工具誤判 → 找人一起核對後再決定<br>3. 確定這次可以先放行(遠端仍會補跑一次完整檢查):<br>`git push --no-verify` | 無 |

## C. scripts/hooks/post-commit

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| post-commit:104-107 | 這次提交跳過了「程式碼要同步筆記」的檢查(用 --no-verify 或其他方式繞過) | `📋 L2 bypass 已留痕 (docs/.bypass-log.jsonl): ${#src_files[@]} 個 code 檔未帶圖譜異動` … | 提醒:這次提交跳過了「程式碼要同步筆記」的檢查,系統已經記下這件事,不會擋你。<br>如果這次其實該補筆記,趁還記得的時候補上比較省事。 | 無 |

## D. scripts/hooks/claude/check-graph-sync.py(Stop hook)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| check-graph-sync.py:339-343 | 累積到 3 筆以上「筆記可能過期」的偵測結果還沒人處理 | `📋 rot-queue 累積 {N} 筆 finding 涵蓋 {M} 篇 Verification (oldest: {日期})。跑 lumos gov 看…` | 提醒:有一批「筆記內容可能過期」的偵測結果還沒人處理,已經累積到需要看一下的量。<br>指令:<br>`lumos gov` | 無 |
| check-graph-sync.py:404-427 | 這一輪對話改了程式碼,但沒有同步更新對應的筆記(Stop 事件觸發) | `⚠️  這個 turn 改了 {N} 個原始碼檔但沒看到對應的圖譜更新:` … | 提醒:這一輪改了程式碼,但沒看到對應的筆記跟著更新。<br>改了的檔案:<br>`<逐行列出路徑>`<br>筆記資料夾在:<br>`<路徑>`<br>以下筆記提到這些檔案,可能要一起更新:<br>`<逐行列出筆記路徑>`<br>功能異動通常要一起更新:系統說明筆記、這次驗證的紀錄、有做設計選擇的話記一下為什麼。<br>如果這次只是打字修正、重構、調整格式(沒改變行為),可以不用管這則提醒。 | 無(僅有 hook 註冊測試,無文字內容比對) |

## E. scripts/hooks/claude/impact-hook.py(PreToolUse hook,Edit/Write/MultiEdit 前觸發)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| impact-hook.py:244-247 | 每次列完「這次改動可能牽連到的筆記」清單後,附上的行動指示(注入給 Claude 看,不是給人看的終端輸出) | `動手前先判上列直接/間接節點會不會被你這次改動影響、需不需要同步更新圖譜。消掉不相關的…` | 提醒:上面列的是這次改動可能牽連到的筆記。<br>動手前看一眼——真的有關的就同步更新,不確定的話先記一句話,不相關的就跳過。 | scripts/test_lumos.py 多處(t_impact_hook_inject:7643;t_impact_hook_v11_delta_and_format:7497)斷言含「動手前」——白話**必須**保留「動手前」開頭。 |
| impact-hook.py:269(build_additional_context) | 列「跟這次改動直接有關」的筆記清單標題 | `直接關聯:` | 直接有關的筆記: | 無 |
| impact-hook.py:286(build_additional_context) | 列「要繞幾層關聯才連到」的筆記清單標題 | `間接關聯(hop N):` | 間接有關的筆記(繞 N 層才連到): | 無 |
| impact-hook.py:311(build_additional_context) | 列「過去跟這類改動有關的事故」清單標題 | `相關事故:` | 過去踩過的坑: | scripts/test_lumos.py:7856(t_impact_hook_incidents_inject,build_additional_context 分支)斷言含「相關事故」——白話需保留「相關事故」字面,或同步改測試。 |
| impact-hook.py:343(build_ranked_context) | 列「一定要看」項目(踩到規則或出過事)的標題,不受排序影響、固定出現 | `必看(合約/事故固定席 {N}):` | 一定要看({N} 項——踩到規則或出過事的地方): | 無 |
| impact-hook.py:350(build_ranked_context) | 列其餘依相關程度排序的項目標題 | `相關(排序 top {N}):` | 其他相關(依相關程度排序,列前 {N} 項): | 無 |
| impact-hook.py:356(build_ranked_context) | 分數不夠但跟改動直接有關、被保留下來的項目標題 | `⛑ 直連保底({N},被閾值或名額截斷、因直連被救回):` | ⛑ 保留下來的直接相關項目({N} 項——分數不夠但直接有關,不想漏掉): | 無 |
| impact-hook.py:361(build_ranked_context) | 分數太低沒列出來的項目數量提示 | `(+{N} 條低分截斷)` | (另有 {N} 項分數較低,沒有列出) | scripts/test_lumos.py:7496(t_impact_hook_v11_delta_and_format)斷言含「+4 條低分截斷」——白話**必須**保留「+{N} 條低分截斷」這段格式,或同步改測試。 |
| impact-hook.py:363(build_ranked_context) | 這次改動的檔案類型有對應的效能檢查清單標題 | `[{stk} 效能檢核——動手時順答]` | [{stk} 效能檢查清單——動手時順便看一下] | scripts/test_lumos.py:14001,14007(t_impact_hook_stack_questions)斷言含「效能檢核」——白話需保留「效能檢核」字面,或同步改測試。 |
| impact-hook.py:482-485 | 這個專案沒有筆記資料夾,略過影響分析(只印到 stderr,一般看不到) | `[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。` | [impact-hook] 這個專案沒有筆記資料夾,略過影響分析。 | 無 |

## F. scripts/hooks/claude/ci-status-hook.py(SessionStart hook)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| ci-status-hook.py:88-89 | 開新對話時,發現上一次 push 的自動化測試沒通過 | `⚠ 上次 push 的 CI 是紅的（{workflow} / {failed_step}） sha={sha} → {url}` `本輪開工前先處理或明確跳過;細節:lumos ci-status` | 提醒:上一次推送的自動化測試沒有通過。<br>指令:<br>`lumos ci-status` | scripts/test_lumos.py:15726(t_ci_hooks)斷言 stdout 含「CI」與「紅」——白話**必須**保留「CI」與「紅」兩字。 |

## G. scripts/lumos:cmd_pitfalls(提問句與 tier 訊息)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:11850 | `pitfalls --diff` 掃完這次改動後,印出風險等級結論 | `tier: {data['tier']}` | 風險等級: {高 / 一般} | scripts/test_lumos.py:5806(t_pitfalls_lens 前置檢查)斷言某行以「tier: 」開頭——**改字需同步改測試**,建議改成斷言行首為「風險等級:」。 |
| scripts/lumos:11859-11862 | 提醒在複查這次改動前,先看看牽連到哪些筆記 | `→ 派審查員前:lumos impact --diff {diff_range}(附 manifest 當第二鏡頭,固定席=帶硬合約/事故的節點必答)` | 提醒:找人複查這次改動之前,先看一下這次牽連到哪些筆記。<br>指令:<br>`lumos impact --diff {diff_range}` | scripts/test_lumos.py:5807-5809 斷言 stdout 含「lumos impact --diff」且帶真實 range——白話**必須**原樣保留 `lumos impact --diff {diff_range}` 這段指令。 |
| scripts/lumos:11994 | 文件內容踩到金流/對外送出/不可逆等高風險字眼,但沒有寫「實務隱患」節回答風險問題(--check 模式) | `✗ pitfalls --check: 命中風險類 {hits} 但無「## {section_title}」節 → 補節(寫『無』也要寫+為什麼無)` | 擋下:這份文件提到高風險內容(像是金流、對外送出、不可逆的操作),但沒有寫清楚要怎麼應對。<br>就算答案是「沒有風險」,也要寫下來、並說明為什麼沒有。 | 無(僅檢查 rc==1,文字可自由改寫) |
| scripts/lumos:11996 | --check 模式通過(已經寫了風險應對,或整篇都沒踩到風險字眼) | `✓ pitfalls --check: {有節/零命中}(命中類={hits})` | 通過:{已經寫了風險應對 / 這份文件沒踩到任何已知風險類別} | 無 |
| scripts/lumos:12007 | 每次都要回答的基本風險提問標題 | `實務隱患提問(通用,恆答):` | 這幾題每次都要想一下: | 無 |
| scripts/lumos:10267-10273(_PITFALL_GENERAL,under 12007-12009 印出) | 同上,四題內容本身 | `併發——同資源兩請求同時進來會怎樣?` / `效能——這段會進熱路徑/大資料量嗎?` / `資源——連線/檔案/鎖有沒有確定釋放?` / `列出此功能碰到的風險類…` | ①如果同一份資料同時被兩個請求動到,會發生什麼事?<br>②這段會不會在很常跑到的路徑上、或處理很大量的資料?<br>③用到的連線/檔案/鎖,結束後確定會被釋放嗎?<br>④這個功能還踩到哪些風險(不只金流、對外送出、不可逆操作,也想想認證、同時處理、快取、資料搬遷、個資、流量限制、多處資料要保持一致等)?每一類都答一下有沒有風險;沒有的話寫「沒有,因為……」。 | scripts/test_lumos.py:5831(t_pitfalls_spec)斷言 stdout 含「併發」「效能」「資源」三字——白話**必須**保留這三個字(建議每題開頭關鍵字不變,只把說明講白話)。 |
| scripts/lumos:12011 | 文件踩到某個已知風險類別(如金流)時,追加提問的標題 | `命中風險類追問({類別}):` | 這份文件還踩到 {類別中文名},多想這幾題: | 無 |
| scripts/lumos:10275-10280(_PITFALL_QUESTIONS,under 12013 印出) | 四個風險類別各自的追加提問內容 | `冪等鍵怎麼設計?重複扣款如何防?部分失敗怎麼補償/對帳?` 等四條 | 金流:重複送出同一筆請求時,怎麼確保只扣一次錢(冪等)?如果扣一半失敗了,怎麼補救、怎麼對帳?<br>對外送出:同時大量重試,對方受得了嗎?對方怎麼判斷收到的是重複的(去重)?逾時要等多久?<br>正式環境不可逆操作:出錯了退得回去嗎?先後順序跟鎖表時間會不會卡住別人?<br>這套檢查機制本身:誤擋到人時有沒有明確的逃生方法?用了逃生方法會留下紀錄嗎? | scripts/test_lumos.py:5832(payment 追問含「冪等」)、5833(external-send 追問含「去重」或「重試」)——白話**必須**保留「冪等」與「去重」/「重試」其中之一。 |
| scripts/lumos:12015 | 業界已知的常見錯誤,文件踩到就多問一句(僅供參考,不擋) | `已知坑追問(世界已知,advisory——答或寫『已排除:理由』,panel 審):` | 這是業界已知的常見錯誤,順手回答一下(不會擋下,回答或寫「不適用:理由」都可以): | 無 |

## H. scripts/lumos:cmd_code_loop(pass/skip/check 訊息)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:14241 | 記錄「這次審查已通過」或「這次刻意跳過審查」 | `{label} code-loop {status} [{branch}@{head_sha[:8]}] {note}` (例:`✅ code-loop passed [main@a1b2c3d4] done`) | 已記錄:{這次審查通過 / 這次刻意跳過審查}(分支 {branch},備註:{note}) | 無(t_codeloop_ledger 等測試只讀寫入的 JSON 檔 status/head_sha/note 欄位,不比對這行 stdout 文字) |
| scripts/lumos:14242-14243 | 說明這筆「審查通過」的紀錄綁定在目前版本上 | `(留痕綁本 sha;其後只准簿記檔 commit——治理帳/usage-log/anchor-baseline/code-loop 留痕——動到其他檔即失效,需重跑 pass/skip)` | 這筆紀錄只認目前這個版本;之後只要有新的程式碼提交(系統自己寫的記錄檔除外),這筆紀錄就會失效,要重新跑一次。 | 無 |
| scripts/lumos:14258-14259 | 查詢「這次改動能不能過關」,結論是不行 | `⚠ code-loop check: BLOCKED [{branch}@{head_sha[:8]}] {reason}` | 擋下:這次改動還不能過關({reason})。 | 無(rc 由 pre-push 腳本層測試覆蓋,見 B 表 pre-push:113-120 那列) |
| scripts/lumos:14261 | 查詢「這次改動能不能過關」,結論是可以 | `✅ code-loop check: OK [{branch}@{head_sha[:8]}] tier={tier} {reason}` | 通過:這次改動可以過關(風險等級:{tier},{reason})。 | 無 |

## I. scripts/lumos:cmd_delguard_check(code 側刪除傳播守衛,警告句)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:11654,11663,11699 | 檢查「刪掉的程式碼是不是還被筆記提到」跑太久,中途放棄 | `delguard: 超時降級({deadline}s),放行;本輪掃描不完整(已記治理帳 delguard/degraded)` | 提醒:「刪掉的程式碼會不會還被筆記提到」這項檢查跑太久,中途放棄了,這次沒有掃完整。<br>不會擋你,但這次結果不完整。 | scripts/test_lumos.py:11145(delguard 降級訊息在 stdout)斷言含「超時降級」——白話**必須**保留「超時降級」四字,或同步改測試。 |
| scripts/lumos:11677 | 沒查到刪掉的東西還被筆記提到,但這次刪的東西太多,有一部分沒掃到 | `delguard: 無命中;{dropped} 個符號超 cap 未掃(--json 看已掃全量)` | 沒有查到問題;不過這次刪的東西太多,有 {dropped} 個沒掃到(完整結果可以用 --json 看)。 | 無 |
| scripts/lumos:11681 | 這次刪掉的函式/變數,還在筆記裡被提到,筆記可能沒跟著更新 | `⚠ delguard: code 側刪除傳播——{N} 個被刪符號在圖譜仍被提及(高信心 {hi}/低信心 {其餘})` | 提醒:這次刪掉的東西,有 {N} 個還在筆記裡被提到({hi} 個確定沒別的地方在用,其餘不確定)。<br>筆記講的東西如果已經被刪掉,看的人會被誤導。 | scripts/test_lumos.py:16418(標頭計數測試「1 個被刪符號」)斷言含「{N} 個被刪符號」——白話**必須**保留「{N} 個被刪符號」這個片語。 |
| scripts/lumos:11683 | 逐條列出「哪篇筆記的哪一行」還在講已刪掉的東西 | `  [{conf}] {node}:{line_no} 「{line}」 ← {tokens}` | [{確定沒別的地方用 / 不確定}] {筆記路徑}:{行號} 原句:「{那一行內容}」 ← 提到了 {被刪的名稱} | 無 |
| scripts/lumos:11686 | 命中太多,只列出前 10 條,其餘沒展開 | `  …另有 {rest} 處命中/{dropped} 個符號超 cap 未展開(--json 看已掃全量)` | …還有 {rest} 處沒列出來、{dropped} 個沒掃到(完整結果可以用 --json 看) | scripts/test_lumos.py:11170(「超 cap」)、11175(「另有 {rest} 處命中」)斷言——白話**必須**保留「超 cap」與「另有 {N} 處命中」這兩段字串。 |
| scripts/lumos:11688 | 有筆記這次只加了連結,正文其實還在講已刪掉的東西,可能假裝有同步 | `  ⚠ 假同步嫌疑: {n} 本次只掛連結(純連結編輯)但內文仍講被刪符號` | 提醒:{筆記路徑} 這次只加了連結,正文沒有真的更新,但正文還在講已經被刪掉的東西。 | 無(僅 JSON 欄位 fake_sync 被測試,stdout 文字未被斷言) |
| scripts/lumos:11689-11690 | 收尾前提醒要親自檢查上面列出的每一句筆記還成不成立 | `退場前自問: 1) 這次拿掉/反轉了什麼? 2) 上列原句逐句判:改動後還成立嗎? 3) 還成立→一句話為什麼;不成立→現在改掉或標作廢。新增 verified_by/related 連結不算同步。` | 收尾前想一下:這次到底拿掉/改變了什麼?上面列出的每一句話,改完之後還是對的嗎?<br>還對的話,寫一句話說明為什麼;不對的話,現在就改掉或標記過期。<br>光是幫筆記加個連結,不算真的更新內容。 | scripts/test_lumos.py:11148,16407(delguard 警告走 stdout+S3 問句)斷言含「退場前自問」——白話**必須**保留「退場前自問」四字。 |
| scripts/lumos:11717 | 這項檢查自己出了技術問題(不是使用者的錯),只好放行 | `delguard: 內部錯誤({e.__class__.__name__}),放行(已記治理帳 delguard/degraded)` | 提醒:這項檢查自己出了點技術問題,這次先放行,不擋你。 | scripts/test_lumos.py:11106(delguard 降級寫治理帳測試上下文)、11118(「delguard 內部錯誤 fail-open rc0+訊息」)斷言含「內部錯誤」——白話**必須**保留「內部錯誤」四字。 |

## J. scripts/lumos:cmd_cochange_check / cmd_cochange_rules(警告句)

| file:line | 何時印(觸發情境) | 原文(截 80 字) | 建議白話(完整) | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:11333-11334 | `lumos cochange rules` 印出結尾統計行 | `({N} 條規則 / {n_txn} transactions / {n_files} 檔)` | (找到 {N} 條「常一起改」的規則,根據 {n_txn} 次提交、{n_files} 個檔案算出來的) | 無("transactions" 建議翻成「提交」) |
| scripts/lumos:11397-11398 | 這次只改了 A 檔,但過去歷史上 A、B 常一起改,這次沒改到 B | `cochange: 改了 {changed} 但未動 {missing}(歷史 {conf:.0%} 同改,共 {support} 次)——確認是否漏改` | 提醒:這次改了 {A 檔},但過去這兩個檔案有 {N%} 的機率會一起被改(歷史上一起改過 {support} 次)。<br>這次沒動到 {B 檔},確認一下是不是漏改了。 | scripts/test_lumos.py:10877 只斷言 stdout 含檔名(如「B.md」),未鎖死其餘文字——可自由改寫。 |
| scripts/lumos:11214 | 專案自訂的 cochange 設定檔壞掉(格式錯誤),系統改用內建預設值 | `cochange: .lumos/cochange.json 解析失敗({e}),改用預設值` | 提醒:自訂的「常一起改」設定檔案格式有問題,這次先用內建預設值。 | scripts/test_lumos.py:10913 斷言含「解析失敗」——白話**必須**保留「解析失敗」。 |
| scripts/lumos:11223 | 設定檔裡某個門檻值不是數字 | `cochange: {k} 非數值({cfg[k]!r}),改用預設 {預設值}` | 提醒:設定檔裡的 {某個門檻} 不是數字,這次先用內建預設值 {N}。 | scripts/test_lumos.py:10930 斷言含「非數值」——白話**必須**保留「非數值」。 |
| scripts/lumos:11226 | 「至少要一起改幾次才算規則」門檻設太低(只要 1 次),系統強制拉高到 2 | `cochange: min_support={N} 低於硬底線,視為 2(單次共改=巧合)` | 提醒:設定的「至少要一起改幾次才算規則」門檻太低,系統改成至少 2 次(只發生一次可能只是巧合)。 | scripts/test_lumos.py:10912 斷言含「視為 2」——白話**必須**保留「視為 2」。 |

---

## 最常被印的 5 條(依觸發頻率判斷,先改這些)

1. **impact-hook.py 的「動手前」清單與各段落標題(E 表全部)**——每次 Edit/Write 到有圖譜的程式碼檔都可能觸發(有 20 分鐘冷卻,但一個工作階段會改很多不同檔案),是曝光量最高的一組訊息,而且是直接餵給 Claude 看的「脈絡」,措辭品質會直接影響後續判斷品質。
2. **check-graph-sync.py 的「這個 turn 改了程式碼但沒同步筆記」提醒(D 表第二列)**——每輪對話結束(Stop 事件)只要這輪動了程式碼、沒動筆記就會跳出,不需要真的執行 commit,是門檻最低、最常被看到的軟提醒。
3. **pre-commit 主同步閘「commit 改了程式碼但沒同步圖譜」(A 表第四列)**——每次 `git commit` 只要沒帶圖譜筆記就會擋下,是最常見的硬擋訊息,也是 CLAUDE.md 開頭就強調的核心紀律。
4. **pre-commit 的 cochange 漏改警告 / delguard 刪除傳播警告(J 表第二列、I 表第三/七列)**——這兩道檢查每次 commit 都會跑,只要命中就印,在活躍開發期間出現頻率很高。
5. **pre-push 的高風險寫法提醒與 code-loop 擋下(B 表 tier=high 兩列)**——雖然 push 頻率低於 commit,但一旦命中就是「擋下」等級,使用者一定會看到、且需要照著做動作(複查或 skip),影響決策的份量最重。
