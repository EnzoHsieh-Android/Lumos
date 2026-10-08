severity: major

(鏡頭:邊界與可執行。spec 檔 /tmp/照留表態-r1.md;對照 /Users/enzo/harness/lumos-b1/scripts/lumos。唯讀,未改任何檔。)

## F1 讀不到綁的節點一律判「不在了」,git 失敗或批次含壞路徑時整批照留同時失效
severity: major
blocking: 是 一次 git 讀取失敗就讓所有綁去處的照留同時失效,推送檢查會把無關發現全部列回要處理並擋推送。
spec 段落:做法 3。
引句:「給提交就用 `_drift_cat(root, where, paths, timeout=60)` 一次讀完所有綁的節點」
問題:`_drift_cat` 底層 `_nodehome_cat_blobs` 在 git 逾時/失敗時回整個 None(`/Users/enzo/harness/lumos-b1/scripts/lumos:27327`),而且只要批次裡任何一個 spec 含換行就整批回 None(`/Users/enzo/harness/lumos-b1/scripts/lumos:27321`)。spec 對「讀不到」只有一種處理:判「綁的 X 不在了」,沒分「節點真的不存在」與「這次讀取本身失敗」。
具體例:表態檔手改或損壞,有一筆 `tracked_in` 值含換行(或 git 正好逾時)。輸入:50 筆有效的綁去處照留 + 1 筆壞值。預期:只有壞的那筆失效。實際:整批 None,50 筆全判「綁的 X 不在了」,推送檢查把它們對應的發現全列回 must,block 模式擋下與本次推送無關的改動。放寬方向也有問題:若實作者反過來「None 就當有效」則 git 失敗時等於全部放行(fail-open),spec 沒指定。
修法方向:spec 要分「確定不存在」(判失效)與「這次讀不了」(該筆判不了、點名,不批次失效);非字串/含換行/空字串的 tracked_in 先在讀取前逐筆剔出,不進批次。

## F2 多筆照留同一行新舊混雜時的「有效」語意沒定義,舊表態會讓新綁定失效不被看見
severity: major
blocking: 是 spec 沒說明同鍵多筆時怎麼合成有效性,照字面實作的「任一筆有效即算」會讓新紀錄的失效被舊紀錄蓋掉。
spec 段落:做法 4。
引句:「kind 在 `_DRIFT_ACK_ROUTED` 的照留,`dead` 不是空字串的不算」
問題:這句是逐筆過濾,對照現有 `_drift_split_acked`(`/Users/enzo/harness/lumos-b1/scripts/lumos:34372`):probe/retire 不在 `_DRIFT_BOUND_KINDS`,所有同鍵表態進同一個 `keys` 集合,「有一筆活的就算已表態」。於是:
- 例 A(2026-11-06 前):同一行有一筆舊表態(無欄位、legacy 有效)和一筆新的 `--tracked-in` 綁到的 Issue 已 resolved。預期:使用者剛綁的去處收尾了,這行應重列。實際:舊 legacy 那筆仍活著,整行繼續算已表態,到 11-06 才同時失效。這條「綁的那篇收尾就失效」的承諾在上線後 30 天內對所有有舊表態的行等於沒有。
- 例 B:同一行多筆,最新一筆已過期但更早一筆是 `until` 未到的 → 仍算已表態,「到期」被較舊紀錄延長。使用者明明按 `--tracked-in` 重新表態、舊的卻會蓋掉失效。
- 例 C:`dead_ack` 取「最新一筆」,但「最新」沒定義(檔內順序?`date`?`seq`?)。probe/retire 現有紀錄沒有保證的 seq(`cmd_drift_ack` 寫入時有 seq,但合併後可同號,見 `_drift_bound_latest` 註解的「兩個工作樹各自追加後合併可能同號」)。
修法方向:對 probe/retire 明寫「同鍵取最新一筆(以 seq,同號取 date 再取檔內位置)決定有效性」,或明寫任一筆有效即可並把例 A 接受為天花板;驗收條款補一條混雜案例。

## F3 legacy 判定只看「兩個欄位都沒有」,手寫或舊版工具產生的無欄位表態都能在 11-06 前繞過 B1/B2 的收緊
severity: major
blocking: 是 本案最核心的新擋(新寫就成立必須綁去處)在 30 天內可被一行無欄位紀錄整個繞過。
spec 段落:範圍第 2、4 條,做法 3。
引句:「舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效」
問題:legacy 是從表態紀錄的「欄位缺席」推出的,不是從「紀錄寫成的日期」推出的。紀錄本身有 `date`(`cmd_drift_ack` 寫入 `/Users/enzo/harness/lumos-b1/scripts/lumos:34548` 一帶),spec 卻不用。後果:
- 任何人(或 AI)在上線後手動 append 一行 `{"id":..,"path":..,"text":..,"kind":"probe","reason":..}` 就是 legacy,推送新寫的、寫下時就成立的條件(本案 S4 要擋的 rtb 一次改寫 33 行當場照留 11 行的情境)照樣放行到 11-06。
- 另一台還沒更新 lumos 的機器(symlink 安裝,見記憶 lumos 更新分發)或 CI 舊版產生的新照留也沒有兩個欄位,被當 legacy 享有 30 天到 11-06 的寬限;寬限窗口內新增的照留數量沒有上限。
- 同時,spec 把 `legacy` 的優先序寫成「兩欄位都沒有」,但沒定義欄位存在但值壞:`until` 為空字串、null、0、非字串時「沒有就取」是看 key 存在還是值真假?`dict.get("until") or LEGACY` 會把 `until:""` 當 legacy 延到 11-06;`tracked_in:""`、`tracked_in:null` 同理被當「沒有 tracked_in」。
修法方向:legacy 限定為 `date` 早於或等於上線日的紀錄(上線日寫成常數);`date` 缺/壞且無兩欄位則直接失效或照 legacy 但不享 born_now 例外。欄位「存在但值壞」一律走壞值分支(失效),不退回 legacy。

## F4 tracked_in 可綁「那條回頭條件所在的同一篇」,自己綁自己,B1/B2 的「去處」形同虛設
severity: major
blocking: 是 S4/S5 要求的「照留要綁去處」可以綁到有該條件的開著的計劃本身,一行 `--tracked-in` 就過關,守衛等於只多一個旗標。
spec 段落:範圍第 3 條、做法 2。
引句:「「綁的那篇還開著」只認 Issue(狀態 open、doing)與計劃(狀態 todo、doing)」
問題:被表態的那一行,最常見的來源就是處於 doing 的計劃或 open 的 Issue(REVISIT 行就寫在計劃裡,spec 自己也是 `status: doing` 的計劃且帶 REVISIT 行)。spec 沒有禁止 `--tracked-in` 指向被表態那行所在的筆記本身(`cmd_drift_ack` 已有 `rel`,比對是一行)。具體例:`lumos drift ack Projects/X_計劃 40 --kind probe --tracked-in Projects/X_計劃 --reason "還沒評估"`。預期:這一行的條件已成立卻「排進」自己,沒有新去處,應擋。實際:X_計劃 是 doing,tracked 有效,born_now 的發現放行,只要 X_計劃 沒收尾就永久消音——rtb 那 11 筆「還沒補/還沒評估」就是這個形狀(多半在 Systems,Systems 本身不收,但 Projects 與 Issue 裡的條件全可自綁)。spec 的天花板 1 只講「綁一篇無關但長期開著」,沒涵蓋這個零成本特例,而這個特例才是最短路徑。
修法方向:`cmd_drift_ack` 擋「tracked 與被表態那篇同一篇」(rc2),判斷時 dead 也要含這一條(手改紀錄);天花板補寫仍可綁別篇無關開著的。

## F5 表態檔手改壞與超大量時,dead 計算沒有容錯與成本界線
severity: major
blocking: 是 沒有型別防護的新讀取路徑會把例外送進兜底,讓推送檢查整段「沒跑完、不擋」,新機制反而造成 fail-open。
spec 段落:做法 3、「只讀一次」。
引句:「`_drift_load_acks(root, where)` 讀完表態後,替 kind 在 `_DRIFT_ACK_ROUTED` 的每筆算 `dead`」
問題:
- 型別:現有 `_drift_load_acks` 只驗 `path`、`kind`(`/Users/enzo/harness/lumos-b1/scripts/lumos:34369`)。新欄位 `tracked_in` 手改成 list/數字/巢狀 dict 時,組成 `paths` 去重或 `f"{where}:{p}"` 就丟 TypeError/造成怪規格;`until` 為數字或 list 時 `date.fromisoformat` 丟 TypeError(spec 只寫「期限格式壞」處理,未明寫涵蓋非字串)。retire 檢查路徑(`/Users/enzo/harness/lumos-b1/scripts/lumos:35667` 附近)有 `except Exception` 兜底成「沒跑完、不擋」,所以手改壞一筆就讓整個撤除條件檢查靜默跳過。這是 fail-open。
- 路徑安全:`where=None` 時直接 `root / tracked_in` 讀工作目錄(spec 寫「同本函式讀表態檔的寫法,符號連結不跟」,但表態檔是固定路徑,`tracked_in` 是自由字串)。`../../x`、絕對路徑 `/etc/x`、符號連結目錄下的路徑都會被讀(`is_file` 不防上層目錄是符號連結),`cmd_drift_ack` 用的 `_drift_ledger_path_err` 那組檢查沒被沿用。讀出的只是 frontmatter 的 type/status,洩漏面小,但行為(讀 repo 外的檔決定放不放行)不對。
- 規模:spec 對所有 probe/retire 紀錄無差別算 dead(包含根本沒有對應發現的),每次 `_drift_load_acks` 呼叫都付一次 git 批次讀取;`_drift_load_acks` 有 5 個呼叫點(`/Users/enzo/harness/lumos-b1/scripts/lumos:35667`、`35741`、`36671`、`36739`、`36801`),其中 m1 路徑(36671)根本不用 probe/retire 的 dead 卻也被迫算。表態檔只追加不清理(spec 自己「不做」自動刪),一個久用的消費專案會累積上千行,每次推送都為歷史紀錄重讀全部綁定節點,且 `timeout=60` 一次耗盡就觸發 F1 的整批失效。
修法方向:`dead` 改成延遲、只對「這次有對應發現的鍵」算;tracked_in 先驗型別為非空單行字串、無 `..`、非絕對路徑,否則該筆直接 dead(「綁的路徑寫壞了」);新增例外不得上拋(逐筆兜底成該筆失效並點名)。

## F6 判「今天」「到期」的邊界與時鐘來源沒寫死,四種輸入各自走到不同結果
severity: minor
blocking: 否 只影響邊界那一天或畸形輸入的結果,但驗收條款沒覆蓋,測試會各寫各的。
spec 段落:做法 3、實務隱患第 1 條。
引句:「今天(本機日期)晚於期限」
問題:
- 「期限剛好是今天」:規則「晚於」代表當天仍有效,但驗收條款 S2 只說「期限已過」「期限沒到」,沒有當天這個點;`--until` 又記「今天+30 天」,第 30 天的 23:59 與次日 00:00 在 UTC/台北間錯一天,spec 已承認但只承認「多列一筆」。反方向沒分析:CI 在 UTC(較晚時區方向?台北比 UTC 早 8 小時)台北已是隔天時,CI 的「今天」還是前一天,期限當天 CI 判有效、本機判失效——是本機多擋、CI 放行,CI 的行為比本機寬;spec 稱「影響是多列一筆(不是放行)」在這個方向不成立,CI 會多放行一天。
- 日期格式:`date.fromisoformat` 在 Python 3.11+ 接受 `20261106`、`2026-W45-5`;spec 沒指定格式,測試無法寫「壞格式」的明確反例。
- 期限遙遠(手改成 9999-12-31)或遠古(0001-01-01):spec 說「固定 30 天」(「不做:讓 `--until` 可以自己選天數」),但判斷時沒上限檢查,手改一個字就永久有效;兩者都沒驗收條款。
- 日期比較要用字串字典序還是 date 物件,影響 `2026-11-6`(缺零)這種輸入:字串比較時 `"2026-11-6" > "2026-11-06"`(字元 '6' > '0')判失效,date 物件則在 3.14 對缺零報錯。spec 沒寫。
修法方向:補一條「期限=今天仍有效、=昨天失效」邊界條款;格式只收 `YYYY-MM-DD` 的嚴格正規式;until 超過「紀錄 date + 30 天」視為壞值。

## F7 綁定節點的名稱解析與路徑形式:NFC/NFD、同名多篇、改名後重綁的行為沒定義
severity: minor
blocking: 否 影響範圍窄(macOS 上寫的中文路徑、同 stem 筆記),結果是多列或誤綁,不會放行危險改動。
spec 段落:做法 2、3,實務隱患「綁的節點改名」。
問題:
- `env.find` 對同名筆記(同 stem 多篇)印警告後「取第一個」(`/Users/enzo/harness/lumos-b1/scripts/lumos:747`),`cmd_drift_ack` 把這個結果記進紀錄。使用者以為綁的是 `Projects/X_計劃` 卻綁到 `Issues/X_計劃`,而 type/status 判定又都通過。spec 沒要求同名時擋(表態端用 `./` 明確路徑是現有出口,但提示句型沒教)。
- 判斷端 where=None 時用 NFC 路徑去 `root / path` 讀:在 Linux 上檔案實際存成 NFD 時讀不到→判「不在了」。where=提交時靠 `_drift_oids` 的 NFC 鍵能對上(`/Users/enzo/harness/lumos-b1/scripts/lumos:33239`),但 `where` 不是完整提交編號時(`_drift_list` 的非 SHA 分支)`oids` 是空,退回「版本:路徑」讀,NFD 檔名同樣讀不到(`_drift_cat` docstring 自己寫了這個坑)。兩條路徑在 NFD 檔名上結果不一致,spec 沒有單一規則。
- 「綁的那篇」被改名後 spec 選擇「不追改名,重綁一次」,但失效說明印的是「綁的 X 不在了」,沒有像 `_drift_old_reason`(`/Users/enzo/harness/lumos-b1/scripts/lumos:34457`)那樣在同 stem 筆記還在時提示新路徑;rtb 規模(11 筆)可以人工,但每筆都要自己找。
修法方向:同名多篇擋並要求 `./` 明確路徑;判斷端讀取統一走 NFC 規一化對照(列檔後以 oid)。

## F8 驗收條款缺邊界案例,spec 列的最壞輸入沒有任何一條會翻紅
severity: minor
blocking: 否 spec 宣稱的收緊在畸形/混雜輸入下沒有測試守著,屬可執行性缺口但不改機制。
spec 段落:驗收條款 S1–S6。
問題:S1–S6 全是單一正常值(綁開著、綁已收尾、沒帶、期限已過、legacy)。沒有:空的表態檔(`_drift_jsonl_parse` 回空,走哪一支?應等同沒表態,需明寫)、同一行多筆混雜(F2)、期限當天(F6)、tracked_in 壞值/換行(F1、F5)、自綁(F4)、無欄位但 `date` 在上線後(F3)、超大量表態的時間上限。依用戶的修審查發現紀律(同根因每條路徑各一支先紅測試),這些各缺一支。另 S1 與 S6 兩條共用 `[test:t_drift_ack_routed_fields]` 一支測試,一支測試名同時承擔「寫入記哪個欄位」與「綁驗證紀錄/Systems 被擋與事後變成這些類型要失效」兩件事,翻紅時定位不了是哪條壞。
修法方向:補上述邊界各一條驗收條款與測試名;S1/S6 拆開綁不同測試。

## 節別覆核
- frontmatter/summary/白話/依據/PRIOR-ART/RETIRE-IF:已讀,無 finding(RETIRE-IF 的「連續 60 天」與 REVISIT 2026-12-06 時間點一致,60 天自 10-06 起算約 12-05,可接受)。
- 範圍:第 2、3、4 條見 F2、F3、F4;第 5、6、7 條已讀,無 finding。
- 做法 1(常數):已讀。`_STATUS_ENUM`(`/Users/enzo/harness/lumos-b1/scripts/lumos:16850`)的 issue 值為 open/doing/resolved/done/wontfix、project 為 todo/doing/done/superseded,與 spec 的開著值取法一致,無 finding。
- 做法 2:見 F4、F7;`drift fix --keep` 固定 c2 不帶 tracked_in 的宣稱已讀,無 finding。
- 做法 3:見 F1、F3、F5、F6。
- 做法 4、5、6:F2 涵蓋 4;5 的 born_now 位置(`_drift_born_annotate` 之後、扣表態之前,見 `/Users/enzo/harness/lumos-b1/scripts/lumos:36735` 一帶)與現有順序一致,6 已讀,無 finding。
- 做法 7:已讀,無 finding。
- 實務隱患:風險類逐項——金流、對外送出、不可逆三項 spec 已排除,我同意:不碰金流、不連網;表態檔只追加,不可逆性成立。日期取本機見 F6(spec 的方向論述不完整);舊表態一起到期、改名見 F3/F7;並行與資源面見 F5(無鎖讀、批次成本)。
- 回退:已讀,無 finding(多出的鍵舊程式忽略,與 `_drift_load_acks` 只取 path/kind 一致)。
- 天花板:已讀;補充 F4(自綁)屬於比第 1 條更便宜的繞法,未列入。

## 圖譜牽連節點
派工時 hook 未附上合約/事故節點,本席無固定席可逐條判定;未收到節點清單,故無「不影響」判斷可寫。

總結:最嚴重 severity major,blocking 共 5 條(F1、F2、F3、F4、F5),minor 3 條(F6、F7、F8)。
