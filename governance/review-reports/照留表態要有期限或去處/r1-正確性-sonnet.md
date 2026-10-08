severity: major

# 正確性/邏輯鏡頭審查:照留表態要有期限或去處_計劃

對照程式:/Users/enzo/harness/lumos-b1/scripts/lumos(`_drift_load_acks`、`_drift_split_acked`、`cmd_drift_ack`、`_drift_probe_check`、`_drift_probe_old`、`_drift_born_one`、`_drift_check_c`、`_drift_print_hints`)。派工時沒有附上牽連的合約/事故節點,圖譜鏡頭那一項無節點可判(沒有附上就沒有逐條判)。

## F1 born_now 的「只認綁去處」在 born 判不了(unknown)時整個失效,同條件重複行是穩定的繞法
severity: major
blocking: 是——該擋(寫下時就成立、只該認綁去處)的被放行,正是本案要堵的洞(rtb 一次改寫 33 行、當場照留 11 行)。

spec 段落:範圍第 4 條、做法第 5 條。

引句:「`_drift_probe_check` 的 must 裡 `old` 為假(起點沒有同一條)的發現加 `born_now: True`」

問題一(drift scan 端):spec 只在 `born.state == "true"` 時加 `born_now`;`unknown` 一律當一般發現,裸照留(30 天)照收。`_drift_born_one` 在下列情況回 unknown:終點同一篇有不只一行是同一組條件(`_DRIFT_BORN_DUP`)、超過預算、超過 `_DRIFT_BORN_MAX_COMMITS` 個提交、歷史讀不出。`file: /Users/enzo/harness/lumos-b1/scripts/lumos:34205` 的 `n_now > 1` 分支。
具體例:一篇 Systems 筆記有兩行 RULE,撤除條件同為 `[retire:when-file:scripts/lumos]` 且已成立。兩行 born 都是 unknown→不帶 `born_now`→`drift ack --kind retire --reason "還沒評估"`(自動 30 天、不綁去處)就算已表態,scan 不列。預期:寫下時就成立的行要綁去處;實際:放行。rtb 的實例(Mock-DSP、共用行程基礎的 RULE)正是同一篇多行共用同一條件的形狀,最容易踩到 DUP。
問題二(推送端):`_drift_probe_old` 用「起點這篇的條件元組集合」比對(`file: /Users/enzo/harness/lumos-b1/scripts/lumos:33758`),新增一行但條件元組跟同篇既有某行相同 → `old` 為真 → 不是 `born_now`;起點成立 → 根本不列,起點不成立 → 當一般「讓條件成立」。所以「這次新寫、條件已成立」對重複條件的行判成不是新寫,推送端同樣不收緊。
spec 沒有說 unknown 與重複條件怎麼處理(沒說擋、也沒說列為判不了),也沒在天花板承認。
修法方向要 spec 自己定:unknown 的 probe/retire 發現在「照留要綁去處」的規則下算哪一邊;重複條件行是否另外以行為單位算 born_now。

## F2 壞的表態列(型別不對、路徑帶換行)會讓整批判定崩潰或整批判死
severity: major
blocking: 是——一筆手改或合併壞掉的表態列就可能讓 drift check 對每次推送崩潰(不該擋的被擋),或讓所有綁去處的照留同時失效。

spec 段落:做法第 3 條。

引句:「給提交就用 `_drift_cat(root, where, paths, timeout=60)` 一次讀完所有綁的節點」

問題:
(a) spec 只定義了「期限格式壞(字串)→失效」,沒定義 `until` 是數字/清單/null、`tracked_in` 是清單/數字/空字串時怎麼辦。`_drift_load_acks` 是在 `_drift_check_c` 裡不包 try 呼叫的(`file: /Users/enzo/harness/lumos-b1/scripts/lumos:35741`),新算 `dead` 若對非字串型別拋例外,整個 `lumos drift check` 以 traceback 結束,推送前掛鉤與 CI 對每次推送都紅。既有程式對同類手改壞資料有明確先例(`_drift_seq_ok`、`_drift_related_ok` 就是為「手改壞了」寫的),本案新增欄位卻沒有同等條款,也沒有對應測試條款(S1–S6 都沒有壞型別案例)。`tracked_in` 空字串在 `cmd_drift_ack` 端因 `if tracked_in` 為假,被當成沒帶、悄悄記 30 天,使用者以為綁了去處。
(b) 批次讀取的失敗是整批:`_nodehome_cat_blobs` 只要任一 spec 含換行(`file: /Users/enzo/harness/lumos-b1/scripts/lumos:27321`)、git 子行程失敗或逾時就整批回 None。spec 把「讀不到」逐條對應成「綁的 X 不在了」,但整批 None 時是全部綁了去處的照留在同一次判定中一起失效(一筆壞列、或一次 git 暫時失敗就夠),結果是 push 端所有 born_now 發現被擋、scan 端全部重列,且訊息說「不在了」而不是「讀失敗」。spec 沒分「這一篇沒有」與「這次讀不了」。
(c) `timeout=60` 在 `_drift_check_c` 的 20 秒預算之外追加(`file: /Users/enzo/harness/lumos-b1/scripts/lumos:35741` 的 acks 載入發生在 `_drift_check_core` 的 deadline 之後),spec 沒說這段算不算預算;讀不到卡滿 60 秒才整批失效。
具體例:`tracked_in` 值為 `"Issues/x.md\nY"`(合併衝突手解壞)→ `_drift_specs` 組出含換行的 spec → 整批 None → 全 repo 所有 probe/retire 綁去處的照留當天一起失效。

## F3 時區風險段寫反方向,且「不是放行」不成立
severity: minor
blocking: 否——只影響邊界那幾小時,對錯由 spec 自己的說法更正即可。

spec 段落:實務隱患第一條。

引句:「台北凌晨 0–8 點推送時兩邊可能差一天,期限當天的照留可能本機算有效、CI 算失效」

問題:台北是 UTC+8,本機日期比 UTC 早到下一天。以期限 D 為例,台北 D+1 凌晨本機 `today > until` 成立(失效),CI(UTC 仍是 D)算有效——方向是「本機算失效、CI 算有效」,跟 spec 寫的相反。後果也不同:本機端對 born_now(只認綁去處,期限只影響 legacy 例外)在 11-07 凌晨 0–8 點會先判舊表態失效而擋下推送,CI 卻放行同一個提交;反過來在日期落後 UTC 的機器上(本機有效、CI 失效)則是本機放行、CI 才紅。spec 的結論「影響是多列一筆(不是放行)」只對其中一個方向成立。
另外 `_DRIFT_ACK_LEGACY_UNTIL` 是寫死日期:若上線日晚於 2026-10-06,舊表態的寬限就少於「上線日 +30 天」(Enzo 裁的是從上線日起算);spec 沒說上線日延後時要同步改常數、也沒有測試把常數跟上線日綁起來。

## F4 擋下訊息與改法提示仍教人下裸照留指令
severity: minor
blocking: 否——判定本身不錯,只是照提示做會原地打轉。

spec 段落:做法第 6 條。

引句:「`_drift_print_findings` 與 drift scan 的已表態說明處,`dead_ack` 存在就印」

問題:程式裡教使用者怎麼表態的固定文案不只這兩處:`file: /Users/enzo/harness/lumos-b1/scripts/lumos:34713`(probe 改法)、`file: /Users/enzo/harness/lumos-b1/scripts/lumos:34717`(retire 改法)、`file: /Users/enzo/harness/lumos-b1/scripts/lumos:34820`、`file: /Users/enzo/harness/lumos-b1/scripts/lumos:35722`(retire 擋下固定段)、`file: /Users/enzo/harness/lumos-b1/scripts/lumos:35771`、`file: /Users/enzo/harness/lumos-b1/scripts/lumos:46102`(指令說明)。這些全是裸的 `lumos drift ack <節點> <行號> --kind probe --reason "…"`。spec 只改了 `dead_ack` 與 `born_now` 那一句。具體例:推送新寫已成立的回頭條件被擋,擋下訊息尾端的固定提示教人跑裸 ack;照做後(得到 30 天 `until`)再推仍被擋,只有 `born_now` 那一行小字才說要綁去處,兩段互相矛盾。要嘛 spec 列出這幾處一併改,要嘛寫明以 born_now 那句為準。

## F5 舊版 lumos 寫的表態在上線日後仍被當舊表態享有寬限
severity: minor
blocking: 否——只放寬到 2026-11-06,且需要舊版寫入者。

spec 段落:範圍第 2 條。

引句:「舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效」

問題:「舊」是以欄位缺席判定,不是以記錄日期判定。lumos 是每台機器各自裝、消費專案各自更新(舊版不認新鍵、照舊寫沒有 `until` 的表態,spec 回退節自己也承認)。上線日之後在還沒更新的機器上寫出的裸表態,仍被當 legacy,連 `born_now` 都放行到 2026-11-06。spec 的 `ack` 記錄有 `date` 欄,可以用「`date` 早於上線日」判舊表態,spec 沒用。

## 各節覆核

- frontmatter / WHY:已讀,無 finding。
- 白話、依據、PRIOR-ART、RETIRE-IF:已讀,無 finding(`_drift_split_acked` 的 related/seq 形狀屬實)。
- 範圍:見 F1、F5(其餘條目與程式相符:doctor 的 `_drift_split_acked` 只吃 c 類發現,確實不受影響;`drift fix --keep` 呼叫 `cmd_drift_ack` 是 c2,`file: /Users/enzo/harness/lumos-b1/scripts/lumos:35473`,屬實)。
- 做法 1(常數):已讀,無 finding(`_STATUS_ENUM` 的 issue open/doing 與 project todo/doing 屬實,`file: /Users/enzo/harness/lumos-b1/scripts/lumos:16850`;repo 內 Issue 的 type 值是 issue、計劃是 project)。
- 做法 2(argparse/cmd_drift_ack):見 F2(a)的 `--tracked-in ""`。
- 做法 3(`_drift_load_acks`):見 F2、F3。
- 做法 4(`_drift_split_acked`):見 F1;非 born 的比對、`dead_ack` 取最新一筆與既有 keys 集合相容,無 finding。
- 做法 5(born_now 標記):見 F1。
- 做法 6(印出):見 F4。
- 做法 7(寫回):已讀,無 finding(兩篇 Systems 節點存在)。
- 實務隱患:見 F3;「舊表態一起到期」「綁的節點改名」兩條已讀,無 finding。
- 實務隱患的風險類逐類:金流、對外送出、不可逆——無(spec 已排除且屬實:只改筆記治理工具、表態檔只追加)。併發:表態檔寫入仍走既有 `_vault_write_lock`,新欄位在鎖外算(`tracked_in` 解析在鎖前),讀到的節點狀態在寫入前可能變化,影響只是記下一筆馬上失效的照留,無 finding。資源:見 F2(c)。
- 驗收條款:已讀;S1–S6 沒有壞型別/批次讀失敗/unknown/重複條件的案例(對應 F1、F2),交叉引用的測試名是新測試,無法驗存在;[S6]、[S1] 共用同一個測試名屬實可行。
- 回退、天花板、REVISIT:已讀,無 finding(天花板兩條屬實;未列入的是 F1 的 unknown 與重複條件)。

總結:最嚴重 severity major,blocking 2 條(F1、F2);minor 3 條(F3、F4、F5)非 blocking。
