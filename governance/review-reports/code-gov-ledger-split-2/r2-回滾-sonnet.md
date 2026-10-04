severity: minor

## F1 唯讀的 docs/.gitignore 即使兩行都在也會被誤報「開不了」
severity: minor
blocking: 否
引句:「fd = _os.open(str(gi), _os.O_RDWR | _os.O_APPEND | nofollow)」
file: `/home/user/Lumos/scripts/lumos:21078`(_ensure_docs_gitignore 現況)
失敗場景(已實跑重現:臨時目錄、以 nobody 身分、docs/.gitignore 權限 444 且已含兩行,呼叫 `_ensure_docs_gitignore` 印出「開不了(PermissionError)……請自己在……加上」並回 [])。
1. 消費專案的 docs/.gitignore 是唯讀(權限 444、別的帳號或容器 root 擁有的共用檔)且兩行本來就在。
2. 修補前:read_bytes 讀完發現沒缺行就安靜回 [];只有缺行才會去開寫入。
3. 修補後:一開始就用 O_RDWR 開,唯讀檔在這一行失敗,走 `_manual("開不了…")`,印出「請自己加兩行」的警告。這個專案其實什麼都不缺。
4. 每次 lumos update、init 都重印這個誤報;doctor 的提醒又叫人跑 update,不會好。
回退面影響:只是誤報,不丟資料;但把「規則已在」與「補不了」混為一談,使用者會去手動重複加行(重複行無害)。修法方向:先唯讀開檔比對,確定缺行才升級成寫入開檔。

## F2 〈回退〉的帳檔「衝突才取聯集」漏掉無衝突的靜默刪行,且「同 lumos update 的做法」不是 revert 可用的機制
severity: minor
blocking: 否
引句:「還原時 `docs/.governance-log.jsonl`、`docs/.canary-log.jsonl` 這類只往後加的帳檔若衝突,一律取兩邊的行聯集」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:104`(〈回退〉原文,在審材外;diff 檔裡沒有此段,上面是該檔逐字原文)
file: `/home/user/Lumos/scripts/lumos:20748`(`lumos update` 的取聯集只用在「來源 repo 髒了簿記帳、要 pull」,不在 git revert 路徑上)
失敗場景:
1. `git diff 91f4b29e..HEAD --stat` 顯示這批改動在版控帳上加了 `docs/.governance-log.jsonl` +375 行、`docs/.canary-log.jsonl` +24 行、`docs/.bypass-log.jsonl` +1 行、`docs/.usage-log.jsonl` +2 行(其中有擋人與略過紀錄)。
2. 壓成單一功能提交後,這些行都在那個提交裡。若還原時尾端沒有後續追加,`git revert` 乾淨套用,沒有衝突,把這幾百行(含 bypass 記錄)原樣刪掉;〈回退〉只說「若衝突」才取聯集,這個沒衝突的路徑沒人叫你保留。
3. 有後續追加時才衝突,這時「取聯集」要人手動解,沒有指令也沒有 merge driver(repo 的 .gitattributes 沒有 merge=union),「同 lumos update 的做法」只是類比。
後果:還原後的版控帳少了擋人與略過紀錄,事後只能從 git 歷史撈,可復原但不在流程裡。建議〈回退〉改成:還原後對這幾本帳檔一律用 `git checkout HEAD -- <帳檔>`(保留還原前的內容),不分有沒有衝突。

## 圖譜鏡頭(固定席逐組判)
- bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、canary-audit、slim 安裝/卸載三篇、design-loop、pitfalls-code-loop、loop-convergence-recording、節點範圍與索引守衛、cochange-guard、check-r/check-t、core-invariant-baseline、judge-severity-gate、lumos-refcheck 等 INVARIANT/RISK 守衛面:本輪修補只動本機帳寫入器、補忽略行、暖機起點與 cmd_gov 常數;判定類讀者(code-loop、fix-check、design-loop)仍只讀版控帳,`_gate_event` 的 hard 事件與 `_KNOWN_GATES` 檢查路徑未變,沒看到違反。
- reversibility-governance-ledger(RISK·守衛面):本輪修補沒有新增不可逆動作。唯一寫入新檔的是新建 docs/.gitignore(只放兩行加註解)與在既有檔尾追加,兩者都可手動還原;追加沒有備份,屬可接受。
- lumos-deinit(RISK·不可逆):本輪沒動 deinit;⚠ init 新增的 docs/.gitignore 兩行 deinit 是否逆轉我沒有查到對應處理(未驗),遺留的兩行無害。
- 新舊版並存:暖機起點改為不晚於 now 的第二早,只在帳裡有未來時間戳時與舊版判定不同(舊版會被卡死,新版放行);cmd_gov 的 GOV_LOG_NAME 與原字面值相同,新舊一致。⚠ 另一處不對稱:度量計數那行仍把未來時間算進去。
引句:「cnt = sum(1 for g, k, t in evs if g == gate and k == kind and t >= cutoff)」
file: `/home/user/Lumos/scripts/lumos:4033`(同函式,計數不設上界,未來時間戳的事件仍計入;屬修補前就有的行為,是否要與暖機一致沒有定論,所以只標 ⚠、不列 finding)

## 已走過沒問題的範圍
- `_local_ledger_open`:無讀者的管線在 O_NONBLOCK 下開檔失敗回 None;捷徑在 O_NOFOLLOW 下失敗(含懸空捷徑);有讀者的管線開得起來但 fstat 不是一般檔會關掉回 None;fd 在各分支都關。三支寫入器呼叫端 `if f is None` 後的 return/continue/return 語意與原先一致,本機帳失敗不連累版控帳。
- `_ensure_docs_gitignore` 新建分支:O_EXCL 競爭落到已存在路徑,寫入失敗回 []、印提示;追加前看現在檔尾、O_APPEND 保證寫到檔尾;硬連結只在缺行時才警告。
- `_gov_metric_events(now)` 與 `_doctor_metric_lines` 把 now 提前:順序無相依問題,時區都是帶時區。
- 本 repo 回退:根 .gitignore 的兩行會被還原拿掉,〈回退〉要求還原前先移出兩本本機帳,與現況一致;`lumos update` 在來源 repo 自己不補 docs/.gitignore(`scripts/lumos:20905`),doctor 新措辭正確。

最高等級為輕微:共兩條,都不擋推送,其中一條已實跑重現。
