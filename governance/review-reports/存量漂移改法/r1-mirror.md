已處理 43、部分 16、未處理 0、相反 2;新矛盾 6

(61 條 = 正確性 11 + 邊界 12 + 接手 9 + 併發 6 + 回滾 6 + 架構對齊 10 + 外家 7,逐份機器數過 `^## F`。)
簡稱:「計劃」= clone-ns/docs/lumos-toolchain-knowledge/Projects/存量漂移改法_計劃.md;「lumos」= clone-ns/scripts/lumos。

## 一、部分 / 未處理 / 相反(逐條)

| 席 | F | 判定 | 缺什麼 / 相反在哪 |
|---|---|---|---|
| 正確性 | F5 | 部分 | settle 已加 `--date`,但「真的要寫日期才推」沒做:計劃第 38 行(§1 步驟 1)c1 一律先推日期,而 whynot 句與刪 settle 句(rtb F4–F7 情境)根本不用日期,推不出仍會擋(lumos:12086–12105 只有 test、why、settle 換句會用 today) |
| 邊界 | F1 | 部分 | `-S` 已換成 `-G "^status: pass"`;但 git 路徑的 NFC/NFD 與 quotepath/`-z`、`%as` 作者日期在「推前壓成一個提交」後會變壓縮那天,計劃都沒寫(誠實界線第 121 行也沒收) |
| 邊界 | F2 | 相反 | 發現要的是「同鍵多筆時最新一筆為準、或有 related 的優先」;計劃第 76 行、[S8](第 94 行)寫的是「任一筆沒記 related 就算已表態」,正是發現指出的遮蔽行為(舊的沒 related 那筆永遠對得上)。另 related 欄位不是清單時(手改成字串、null)的處置沒寫 |
| 邊界 | F5 | 部分 | 日期格式錯已回 2;仍缺:參數對種類不合(`--kind c3` 卻給 `--old`、c4 給 `--status`、c1 給 `--by`)回 2 與訊息、`--dry-run` 搭 c4 不帶 `--old`/c1 推不出日期的輸出、`預告的合約:` 行被手改掉時 fix 的擋下訊息 |
| 邊界 | F8 | 部分 | 空結果、shallow、未提交已寫(第 65 行);仍缺檔案改名後 `--diff-filter=A` 只回改名那次、卷證目錄「名字含」的比對法(子字串/NFC/大小寫) |
| 邊界 | F9 | 部分 | 判準、刪行、連帶空行已寫(第 54 行);仍缺「因手補而刪除」的句型要不要進 `missing`(lumos:12295 `_guard_settle_record` 用 `missing` 印提醒,會多印一行誤導的「找不到」) |
| 邊界 | F11 | 部分 | 提示三處已列(第 82 行);仍缺 `_CMD_HELP` 的 drift 說明字典(lumos:35687 一帶)與 drift 分派處(lumos:37029–37032「不是 scan 就當 ack」,新增 fix 會被當 ack 執行)、doctor Z 段 advice(lumos:2273) |
| 接手 | F2 | 部分 | 只有 `_drift_report_must`、scan、ack 三處提示;仍缺 `commands/06-代碼審與推送.md:19` guard settle 列的 `--test` 必填字樣、`commands/04` 與 INDEX(現在只有 drift-history)、頂層說明字典、`Systems/存量漂移守衛` 的 responsibility 行(寫著「check、scan、ack、exam」);第 83 行指的「commands/ 裡存量漂移那一檔」不存在(見新矛盾 5) |
| 接手 | F3 | 部分 | 拿不到發現時擋下已寫;仍缺:計劃改名後 related 存的是舊路徑,現在清單是新路徑 → 誤判「多了新計劃」重新列出,沒寫這個誤報邊與退場(重新表態)提示 |
| 接手 | F5 | 部分 | `--date` 與 `--test` 選填已寫;仍缺 lumos:12199 的 `IDENT_RE.match(method)` 排在讀狀態之前,method 為 None 會先擋(要挪到 pending 分支後),以及 `_guard_settle_record` 成功訊息會印「綁上 [test:None]」 |
| 接手 | F6 | 部分 | 「整篇改完 c1 全部消失」只答了單次呼叫;沒答之後對同一篇其餘 c1 行號再 `drift fix` 會被 [S1] 擋成「現在不是那一種發現」(誤導成 scan 清單錯)——沒定義「已修」回 0 或改訊息 |
| 接手 | F7 | 部分 | 用 E5 同一支判定已寫;仍缺:`lumos set <Issue> status pass`(set 不驗類型值域)也會觸發列出,沒寫「取 Issue 的 resolved/done/wontfix 交集」;E5 讀 status 要用 `_drift_str` 防清單值 |
| 併發 | F4 | 部分 | 先筆記後帳、失敗還原、id 用 token 已寫;仍缺帳檔是否提交進版控、多工作樹各自追加同一本 jsonl 的合併衝突(表態檔也沒有 merge=union),rtb 24 筆多會談並行修時會碰到 |
| 回滾 | F5 | 部分 | 回退第 101 行已不再說「本來就是 settle 會產生的樣子」;仍缺既有測試要跟著改:test_lumos.py:50767 斷言「第四句整行換成已轉正」、50812 斷言 pass 印「已轉正」回 0——[S3] 改了這兩個行為,條款與回退都沒列要改哪些既有測試 |
| 架構對齊 | F3 | 部分 | c1 的 `-G`/`_nodehome_git` 已寫;c4 證據①沒借 lumos:5843 的 `_plan_first_commit`(註解寫了為何不信 frontmatter created),第 66 行仍自己走 `_nodehome_git` 再做一支;PRIOR-ART 的宣稱不準(見新矛盾 5) |
| 架構對齊 | F7 | 部分 | `DFIX-` 前綴、`_jsonl_append_verified` 已寫;仍缺 `_DRIFT_FIXES` 常數名、是否記 `_gate_event_or_warn`(`cmd_drift_ack` 有,lumos:27141)、印不印「要提交帳檔」提示 |
| 外家 | F4 | 部分 | 只把限制寫進誠實界線第 122–123 行並加 REVISIT,機制沒變:related 仍只存路徑,計劃重開再收尾後清單相同、舊表態照樣命中(發現要的是綁收尾事件或版本指紋);屬「承認、不修」,不是處理 |

未處理:0 條。

## 二、新矛盾 / 新宣稱對不上

1. **補 related 的 17 筆補不上**:計劃第 77 行要對 17 筆 c2 表態「各重跑一次 `drift ack`(同理由)補上 related」,但表態檔只增不改(`_drift_split_acked` lumos:27079 把全部表態收成鍵集合),重跑是「再 append 一筆」,舊的沒 related 那 17 行還在;而計劃第 76 行、[S8](第 94 行)規定「任一筆沒記 related……就算已表態」,舊行永遠讓它對得上。原句:「實作收尾時,對工具鏈 2026-09-29 那 17 筆 c2 表態各重跑一次 `drift ack`(同理由)補上 `related`,讓這批已知案例也受新規則保護」(計劃:77);〈實務隱患〉「今天那 17 筆也補上」(計劃:111)。兩處互相打架,新保護對這批與之後任何「舊行+新行」同鍵的情況都不生效。
2. **c1 前提檢查失敗的出口是死路**:計劃第 48 行:「沒有就回 2,說明『這篇是手改成 pass 的,家節點沒有正式合約行,不改句——先走 guard settle 或手動處理』」;但第 59 行 §3 讓 `guard settle` 對 pass 節點走「第 2 節同一支(日期規則、前提檢查……)」,而 pass 節點在 lumos:12225 本來就不進 pending 轉正路徑,前提檢查會同樣回 2。提示指到的 `guard settle` 走回同一個擋,只剩「手動把 status 改回 pending 再 settle」這條計劃沒寫的路。
3. **鎖內「重讀重判」沒說怎麼判**:計劃第 40 行:「用 `_drift_state_findings` 對『重讀後的內容』重判……不用指令開頭載入的 env 判」,第 42 行寫完「重讀整篇、用同一支判定」。但 `_drift_state_findings(env, only=None)`(lumos:26078)的 status、type、plan_refs、valid_under 都讀 `env.notes[..].fields`(載入時快照),只有 c1、行文字才讀 `env_text`;c3、c4 若不重建 Env(該函式 docstring 提到 `Env.from_texts`),重讀後判定看到的還是舊欄位:鎖內判定擋不住兩會談同修一篇,寫後驗證「那一筆不在了」對 c3、c4 永遠不成立。計劃沒寫要重建 Env。
4. **c4 寫入走 `_set_conditions_locked` 與 §1 的順序接不上**:計劃第 66 行:「寫入走既有的 `_set_conditions_locked`」。該函式(lumos:14863–14888)自己讀檔、自己 `atomic_write_verify`、寫完立刻印「✓ set … 整欄換成」並回 0,沒有 dry-run 出口;而 §1 步驟 4 要求 `--dry-run` 不寫、步驟 5 要在寫後重判、失敗還原改前原文、步驟 6 才記帳。照字面:dry-run 會真的寫入;驗證失敗還原時終端已印過「✓ set」。要嘛拆成「算值」與「寫」,要嘛在計劃寫明包一層,現在沒寫(架構對齊 F2#4 就是點這個,折入時只採了「走既有函式」)。
5. **PRIOR-ART 與同步清單裡幾句對不上程式與檔案**:
   - 計劃第 23 行:「`_nodehome_git` 已經用 `git log -S`……、`git log --diff-filter=A`(兩處),本計劃照同一支呼叫,不另起 subprocess」。實查:`-S` 在 lumos:23860 屬實;`--diff-filter` 經 `_nodehome_git` 的只有 lumos:24215–24216 一處、且是 `--diff-filter=AR`(帶 `-M`、`--name-only`);精確 `--diff-filter=A` 的兩處是 lumos:5846(`_plan_first_commit`)與 lumos:1816,都是裸 `subprocess.run`。第 66 行「走 `_nodehome_git`,同既有兩處」同誤。且 `_nodehome_git` 回位元組(lumos:23351,`binary=True`),計劃沒提解碼。
   - 計劃第 38 行「git 一律走 `_nodehome_git`(有逾時)」與第 52 行用的 `_git_is_shallow`(lumos:4861)是裸 `subprocess.run`、無逾時,前後不一(小)。
   - 計劃第 82 行「`drift scan` 每種發現的建議」:`_drift_scan_print`(lumos:27306)沒有任何下一步建議,是「新增」不是「改成」;第 82 行「`drift ack` 的提示」只有「只認提交進去的表態檔」一句,沒有 c1/c3/c4 的手改建議可改。
   - 計劃第 83 行:「lumos-project-notes 的指令表(`commands/` 裡存量漂移那一檔)」:`skills/lumos-project-notes/commands/` 底下沒有存量漂移專檔,只有 04 的 drift-history 一列與 INDEX;要新增而非同步。
6. **§5 標記與 §1 c4 條款的小落差**:計劃第 70 行 E5 在 Issue 行尾加「(這篇 Issue 已結案)」,但 E5 顯示走 `warn_soft`、只列前幾行(lumos:2245–2262,cap 後折成「另 N 條」),標記在第 4 筆起看不到;[S6](第 92 行)沒限定只斷言可見範圍。(邊界 F10#2 的餘項,折入時沒處理。)
