severity: major

立場:三個月後照這份 spec 與它產生的訊息做事的接手的人,預設文件與現實已對不上。以下路徑皆在 clone-ns 底下。

## F1 刪除守衛的量法照抄跑不出數字,「detail」欄位也不存在
severity: major
blocking: 是
引句:「記在既有的 delguard 治理事件的 detail 裡(RETIRE-IF ② 要抽樣這些名稱)」
file: `scripts/lumos:29401`(`_delguard_log_result`)
file: `docs/.governance-log.jsonl`(delguard 事件的欄位是 gate/kind/hard/nodes/note)
1. delguard 事件只有 `note` 欄,內容是 `tokens=N hits=N secs=…`;沒有 `detail` 欄。實作的人會在「改 `_delguard_log_result` 加 detail 欄」與「把字串塞進 note」之間自己選。選哪個,REVISIT 的抽樣寫法就不同,spec 沒定。
2. REVISIT ② 寫的量法是 `grep '"gate": "delguard"' docs/.governance-log.jsonl`。我在 clone 實跑:923 筆全中(ok 816、degraded 107),spec 沒定「因工具檔跳過」的標記字串(例如 `vendored_skipped=N`)。RETIRE-IF ② 的「累計 ≥20 次」與「抽樣 5 次被跳過的名稱」照這條指令算不出來。
3. 工具鏈本體 `_is_toolchain_repo` 為真時 skip 恆為空集合,工具鏈的帳裡永遠是 0 次跳過。跳過只會發生在消費專案(rtb)。REVISIT ② 沒寫「要在 rtb 跑」,①才寫了。接手的人在工具鏈跑完得到 0,可能誤判「從沒跳過」而撤機制。
4. 「最多列 20 個名稱」放進單行 note 的長度與格式(逗號?JSON?)沒定,抽樣的人拿到的字串形狀無從預期。
要補:標記字串、欄位名、名稱清單格式、並寫明在消費專案的帳上量。

## F2 `--values=-x` 的退路在多項時是錯的,預填指令也沒套用它
severity: minor
blocking: 否
引句:「`--values` 的單一項以 `-` 開頭時要寫成 `--values=-x`(argparse 的限制)。」
file: `scripts/lumos:37590`(drift fix 的 argparse 區段;`--values` 尚未存在)
1. 我用 `/opt/homebrew/bin/python3` 照 spec 的接線(`nargs="+"`)實測:`--kind c4 --values=-x b c` 回 `unrecognized arguments: b c`;`--values -x b` 回 `expected at least one argument`。等號寫法在 `nargs="+"` 下只吃一個值,後面的項全被丟掉。所以「寫成 `--values=-x`」只在整欄剛好一項時成立,多項時不成立。
2. 證據頁預填指令用 `_drift_sh` 印各項,而 `_drift_sh` 的白名單含 `-`,`-x` 這種不含空白、以 `-` 開頭的項會原樣印出,照貼直接掛掉。含空白的項(如 `-1 個`)實測是 positional,沒事。
3. 接手的人遇到時只能看到 argparse 的英文錯誤,spec 沒要求證據頁在這種項出現時改印逐項清單或加提示。
建議:對這種項比照「含控制字元」走「請自己組指令」,或改用 `--values` 之外的收法。

## F3 第 6 節漏了 `scripts/test_lumos.py` 是錨點檔,測試一改就要人工重簽
severity: minor
blocking: 否
引句:「- 測試:新測試一起拿掉;`t_drift_fix_c4_evidence_then_replace` 改回證據頁印 `lumos set` 的斷言」
file: `governance/anchor-baseline.json:4`
file: `skills/lumos-project-notes/commands/04-自檢與健康.md:18`
1. `scripts/test_lumos.py` 在 anchor-baseline 裡。第 6 節要改寫既有測試、新增至少 7 支測試,回退節還要拿掉它們,兩個方向都會讓雜湊對不上,`lumos anchor verify` rc1,pre-push 擋。
2. 第 6 節與回退節都沒有「`lumos anchor approve --note`(人工核可)」這一步,也沒把 [[Systems/anchor-integrity]] 放進 related。前一個計劃(baseline 的 note)做過這步,三個月後的人沒有線索。

## F4 乾淨檢查的位置:條款文字與接線描述互相矛盾
severity: minor
blocking: 否
引句:「過了才做乾淨檢查、鎖內寫入、寫後驗證、記一筆帶 reports_same、reports_name 的修復帳」
file: `scripts/lumos:27779`(`_drift_fix_load`,乾淨檢查在這裡,先於 `_DRIFT_FIX_COMPUTE`)
1. S2 說五道值檢查先、乾淨檢查後。但 spec 的接線是把 `_drift_fix_load` 的條件改成「c4 且沒帶 `--values`」才不做乾淨檢查,即帶 `--values` 時乾淨檢查在 `_drift_fix_load` 就做,先於 `_drift_fix_c4` 裡的五道檢查。兩者次序相反。
2. 具體差異:筆記有未提交改動、又給了壞值時,依接線先看到「有未提交的改動(不是 drift fix 自己留下的)——先提交或還原再修」,依 S2 應先看到值錯誤。S8 只測乾淨檢查會擋,測不出次序,實作者可任選。
3. 連帶:第④道訊息說「有人剛改過這一欄」,那個人的改動若未提交,實際上會先被乾淨檢查以另一句話擋下,兩句話建議的動作不同(提交/還原 vs 用 set)。

## F5 第④道擋下後的下一步講不完整,走完又落回沒有修復帳、還可能卡乾淨檢查
severity: minor
blocking: 否
引句:「要刪項目或有人剛改過這一欄:看過之後用 lumos set 整欄改」
file: `scripts/lumos:15128`(`_set_conditions_locked`,set 不寫修復帳)
1. 訊息沒給可貼的 set 指令(證據頁那條預填指令已在螢幕上方,但含 `--values` 版本,不是 set 版本),接手的人要自己把 `--values` 換成 `lumos set <節點> valid_under`。
2. 走 set 就沒有修復帳,也就是 rtb 回報的第二條(改完修復帳沒紀錄)在這條路上照舊存在。「要刪一個不含三詞的舊項目」在 drift fix 裡根本沒有路,只能走 set。訊息沒提這點。
3. set 寫完筆記是「未提交的、不是 drift fix 留下的」改動。此後同一篇再跑任何 drift fix(例如 c1、c3)會被乾淨檢查擋。這件事只寫在〈誠實界線〉,第④道的擋下訊息本身沒說「改完先提交」。接手的人只看訊息會卡在下一步。
4. RETIRE-IF ① 依賴修復帳筆數,這條 set 路徑不進帳,c4 筆數會偏低,見 F7。

## F6 翻案決策與舊 PITFALL 的記法在現行圖譜上沒有可照做的落點,文件同步也沒列齊
severity: minor
blocking: 否
引句:「翻案用 `lumos decision-add` 記在存量漂移守衛。」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:44`(舊 PITFALL,綁 `[test:t_drift_fix_c4_evidence_then_replace]`)
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:41`、`:77`、`:40`
1. 存量漂移守衛沒有 `decisions:` 欄位,舊的「c4 改走 set」只存在於一條 PITFALL,不是決策紀錄。沒有東西可以 `decision-supersede`。回退節寫「翻案決策用 `lumos decision-supersede` 撤」,撤的是新決策,語意上可以,但「翻的是哪一條」在圖譜上沒有編號可指。
2. PITFALL 沒有 `[status:superseded]` 這類機器標記(那是 RULE 專有)。「標成被取代」要寫成什麼字、lint 認不認,spec 沒定。那條 PITFALL 的綁定測試 `t_drift_fix_c4_evidence_then_replace` 又被改寫,PITFALL 內文「原封不動照貼會被 set 擋下」靠的是保留的那一段,得說清楚。
3. 第 6 節列的文件漏了同一篇裡其他還在講舊行為的句子:第 41 行 WHY「c4 只給證據由人給要換的片段」、第 77 行用法「c4 只列證據與一條預填好的 `lumos set`」、第 40 行 TEST 清單(要加新測試名)。另外 `_drift_fix_c4` 的 docstring、`_drift_fix_hint` 的 c4 說明字串、`t_drift_fix_c4_evidence_then_replace` 與 `t_drift_fix_*` 那條「c4 只列證據也做乾淨檢查 → ⑩紅」的測試 docstring 也還寫舊說法。
4. 消費專案(rtb)用的是安裝進去的工具副本,第 6 節沒寫要 `lumos update` 才會有 `--values`(rtb 若不更新,證據頁仍印舊行為)。

## F7 RETIRE-IF ① 沒有資料不足的分支,REVISIT ① 的指令在帳檔不存在時會噴 traceback,rtb 的帳誰去拿沒指名
severity: minor
blocking: 否
引句:「上線兩個月後(以 REVISIT 那天為準):①工具鏈與 rtb 合計 c4 修復帳 ≥5 筆」
file: `scripts/lumos:26256`(`_DRIFT_FIXES = "governance/drift-fixes.jsonl"`)
1. 我在 clone 根目錄照抄那條 `python3 -c` 指令:`governance/drift-fixes.jsonl` 不存在,直接 `FileNotFoundError`(這個 repo 目前沒有那份帳)。接手的人得到 traceback 而不是「0 0」。
2. c4 修復是稀有事件(rtb 一次 26 筆裡 c4 是少數)。到 2026-11-30 合計不到 5 筆很可能,而規則只定義了「≥5 且零筆」撤、沒定義「<5」怎麼辦(延期?保留?)。REVISIT 那天會沒有決定可下。
3. 「rtb 的帳由本工具鏈的會談用跨會談訊息請 rtb 會談回報」:三個月後沒有指名 rtb 是哪個 repo、哪個會談、路徑,也沒說 rtb 要先 `lumos update`(F6-4)。跨會談訊息不留在 repo。
4. 走 set 的 c4 不進帳(F5-2),計數偏低。

## F8 rtb 五條回報:三個月後無法核對每條是否真的解掉,第一條實測只解一小部分
severity: minor
blocking: 否
引句:「所以驗證紀錄第一次被提交的那個提交裡一起加進來的卷證目錄是強線索」
file: `governance/review-reports/漂移修法補強/r1-intake.md`(全卷證裡沒有 rtb 的原始案例)
1. 〈依據〉說 rtb 訊息「逐條附了 rtb 的實際案例」,但 spec 與 r1 卷證裡一條都沒抄進來(訊息是跨會談的,不進 repo)。接手的人沒有辦法拿 rtb 的輸入重現、驗收只剩合成測試。
2. 第一條(c4 卷證目錄找不到)。我抽 clone 裡最近 60 篇驗證紀錄,用 spec 的指令 `git show -z --name-only --diff-filter=A --format=<首次提交>` 算「同提交卷證目錄」:只有 19/60 非空。範本只自動填「兩者都有」,交集比 19/60 更小,多數情況範本仍是 `<卷證>`,人照舊要自己挑。它解掉的是「證據頁看得到候選」,不是「找得到」。rtb 那次的案例若是名稱對不上且驗證紀錄另提交,這條照樣找不到,〈誠實界線〉自己也承認。⚠ 未驗 rtb 實際情形。
3. 第二條(c4 沒修復帳)照 spec 解掉,但只限走 `--values`(F5-2)。第三條(c1 訊息)見 F9。第四條(c3 理由)是接線加單行接尾,能解。第五條(工具檔誤報)只在清單與工具檔一起暫存的提交解掉,只暫存 `scripts/` 或拆除工具鏈仍會誤報(〈誠實界線〉已寫)。

## F9 c1/settle 訊息:回傳集合要串過的呼叫鏈沒列,只點名兩處印訊息
severity: minor
blocking: 否
引句:「`_drift_fix_c1` 與 `guard settle` 印訊息時:已是轉正後說法的種類講」
file: `scripts/lumos:12290`、`scripts/lumos:12537`、`scripts/lumos:12556`、`scripts/lumos:12438`、`scripts/lumos:12572`
1. `_guard_settle_rewrite` 的回傳要多一個集合,但它有兩層包裝:`_guard_pass_rewrite`(回 4 元組,呼叫者 `guard settle` 補改分支 12425 與 `_drift_fix_c1` 27836)與 `_guard_settle_record_lines`(回 3 元組,呼叫者 `_guard_settle_record` 12565 與 c5 28010)。spec 沒列這兩層要跟著改。
2. `guard settle` 有兩條印訊息路徑(補改 12438、pending 轉正 12572),都走 `_guard_settle_missing_say`;spec 只說 `guard settle`,實作者可能只改其中一條。S4 的測試只綁 c1(`t_drift_fix_c1_already_settled_message`),沒綁 settle 兩條。
3. c5 走 `_guard_settle_record_lines` 並丟掉 missing,它印的訊息不在範圍內,但 c5 也是「已轉正就不用改」的同型場景,沒被提到是刻意還是漏。

## 合約與 INVARIANT 判定
- [[Systems/guard-kill]] 兩條 ★INVARIANT★(guard kill rc 優先序;`--json` 成功時 stdout 恰一行 JSON):本設計只改 `guard settle` 的訊息與 `_guard_settle_rewrite` 的回傳,不碰 `guard kill`,不影響;訊息走 stderr/stdout 的既有管道,不動 kill 的 rc。
- [[Systems/lumos-cli-write]]:clone 內該篇沒有 ★INVARIANT★ 行,只有 WHY(第 18 行綁 `t_drift_fix_c4_evidence_then_replace` 的 set 擋 `<整項新內容>`)。拆函式後 set 的擋下訊息與順序不變是 S3 的責任;這條 WHY 綁的測試被改寫但那一段保留,只要保留就不影響。
- [[Systems/delguard]]:沒有 ★INVARIANT★ 行;「恆 rc0、fail-open」是程式文件裡的契約(`cmd_delguard_check` docstring),spec 的做法(超時或出錯照降級路徑不跳)符合,不影響。

## 實務隱患逐類
- 不可逆:`--values` 寫的是版控裡的筆記,乾淨檢查保證退得回來;不影響(見 F4 次序)。
- 對外送出:無,不打外部。
- 資安:目錄名走 `_esc_clean`、指令參數走 `_drift_sh`,`-` 開頭項是唯一漏縫(F2)。
- 併發:鎖內比指紋既有;第④道以「原文出現在 --values」擋別人剛加的項,語意成立;未提交改動先被乾淨檢查擋(F4-3)。
- 效能:`git show` 沿用 `_lens_git` 的 20 秒逾時,證據頁與 `--values` 各一次;不影響。
- 守衛面:刪除守衛少抽名稱只提醒不擋,已記帳,但記帳量法有洞(F1)。

## 已讀,無 finding 的節
〈範圍〉、〈回退〉(除 F3、F6-4 提到的缺項)、〈實務隱患〉、〈誠實界線〉第 1、4 條(與程式相符)、S1、S3、S5、S6、S7。

最高等級:major;blocking 共 1 條
