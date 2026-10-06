severity: major

(鏡頭:簡化/反過度設計。已讀 /tmp/照留表態-r2.md 全文,並對照 /Users/enzo/harness/lumos-b1 的 `scripts/lumos`。「兩種都給、至少選一」與「舊表態從上線日起算 30 天」不重裁,只看實作形狀。)

## F1 推送檢查為「已收尾」多建一條讀樹管線
severity: major
blocking: 是(新增跨三個呼叫點的參數與條件式建樹,換到的只是一個同提交內才會發生的邊界,判準:新機制要有今天的證據,這裡沒有)
段落:做法 5、7;驗收條款 S6。
引句:「`_drift_split_acked(findings, acks, vault_rel, today=None, status_of=None)`」
問題:`born_now` 的照留要「綁的那篇在被推送版本裡還開著」,所以 `_drift_split_acked` 得多收 `status_of`,核心路徑還得在「有 born_now 且有帶 tracked_in 的照留」時才懶建 `_drift_tree_env`(做法 7)。`_drift_split_acked` 現有呼叫點:`scripts/lumos:35668`(retire,手上有 tenv)、`scripts/lumos:35742`(核心路徑,沒有 tenv)、`scripts/lumos:36672`(m1)、`36739`、`36801`(scan/其他)。核心路徑本來只讀表態檔(`_drift_load_acks(root, tip)`),新規則讓它多了一條「條件式建整棵樹」的分支,而且「建不出來」時的行為(判活?判死?)spec 沒寫。
具體例:推送新寫一條已成立的回頭條件,照留綁 Issue A(表態時開著、`drift ack` 已驗)。要擋的情境只有「A 在同一次被推送的提交裡被改成 done」。這個情境今天沒有任何實例(rtb 三筆實例都是「條件成立、事沒做」)。
替代形狀:推送檢查只看 `born_now` 的發現有沒有 `tracked_in`(表態時 `cmd_drift_ack` 已驗開著);A 之後收尾,scan 的 `_drift_ack_live` 本來就會判失效重列(做法 3)。這樣 `status_of` 參數、核心路徑的懶建樹、S6 最後半句都可刪;天花板第 1 條已承認「綁的那篇」只是弱綁定,再多驗一次開著並沒有把它變強。
預期 vs 實際:作者要嘛補今天的實例證明「同提交收尾綁定去處」會發生,要嘛砍掉;目前 spec 兩者皆無。

## F2 `until` 欄位是 `date` 欄位的衍生值,還要另寫一套防呆
severity: major
blocking: 是(新增持久欄位與一整串校驗只為了存一個可由既有欄位算出的值,判準:資料冗餘造出可自相矛盾的新狀態)
段落:做法 2、3;驗收條款 S1、S3。
引句:「沒帶就記 `until` = 表態日 + 30 天」
引句:「不早於表態日 `date`、不晚於 `date` + 30 天,否則失效」
問題:表態紀錄今天就有 `date`(`scripts/lumos:34550` 的 rec 含 `"date": datetime.date.today().isoformat()`)。`until` 永遠等於 `date` + 30(固定天數,範圍「不做」也明說不讓自選),所以存下來的 `until` 是純衍生值。存它就得再寫「`until` 要是 ISO 日期、不早於 date、不晚於 date+30」這三道防呆(做法 3),還要 S3 的對應案例、S1 的欄位斷言、「`until` 與 `date` 矛盾」的失效原因文字;改成「沒有 `tracked_in` 就以 `date` + `_DRIFT_ACK_DAYS` 判期限」後,這些全消失,同時也不會出現「手改把 until 拉長」這種繞過。
具體例:舊表態與新表態處理一致——舊表態沒有欄位,期限取 `max(date+30, 寬限日)` 不成立,仍沿用 spec 已裁的固定 11-05;新表態直接 date+30,不需 `until`。檔案少一個欄位,回退(舊程式忽略新鍵)也更乾淨。
預期 vs 實際:spec 實際會寫出兩個來源(`date`、`until`)必須互相一致的資料;作者需證明存 `until` 買到什麼(例:將來允許改天數;但範圍已寫「不做:讓期限可以自己選天數」)。

## F3 `_drift_ack_live` 的 tracked_in 路徑校驗重複了查表本身會做的事
severity: minor
blocking: 否(多幾行判斷,不改行為,判準:冗餘分支而非缺陷)
段落:做法 3、4。
引句:「要是字串、不帶 `..`、在圖譜資料夾底下,否則失效」
問題:做法 4 的 `status_of` 是用 NFC 路徑去 `env.notes` 查(字典查找);帶 `..` 或不在圖譜資料夾底下的字串查不到,本來就回 None → 判「不在了」。另寫「不帶 `..`」「在資料夾底下」兩道前置檢查,只是把同一個失效換個原因文字。只需保留 `isinstance(str)`(確保不丟例外,這條 S3 要求的)。表態檔是工具追加的 jsonl,「手改壞了」的防禦在 c2/c3 的 `_drift_related_ok` 已有先例,但那是因為它要拿清單做集合運算,這裡沒有。
預期 vs 實際:`tracked_in: "../x.md"` → 預期失效;只用 `status_of` 查表也得到失效,多出的分支沒有多擋任何輸入。

## F4 失效照留的 `prev_ack` 要另開形狀、另改兩個印出點
severity: minor
blocking: 否(輸出文字層面的加碼,判準:不影響判定,可減)
段落:做法 5、7。
問題:現有 `prev_ack` 的形狀是 `{related, reason}`,`_drift_prev_ack_line`(`scripts/lumos:34451`)只認 related;spec 讓同一個欄位多一種 `{reason, dead}` 形狀,印的函式要分支,又要讓 `_drift_scan_print` 也印,還要確保有 `prev_ack` 時不再印舊的「改過或搬了」那句。這是為了讓使用者看到「以前照留過、理由、為什麼失效」;但 `_drift_old_reason`(`scripts/lumos:34464` 附近)已經有「用原文與種類找舊理由」的機制。把失效原因併進發現的現有說明行,不碰 `prev_ack` 形狀,可少一個欄位形狀與一個函式分支。
預期 vs 實際:失效時使用者要的是「失效了、為什麼、怎麼續」三件事;spec 為此動到三處(split_acked、prev_ack_line、scan_print),其中形狀擴充那處可省。作者如能舉出「理由貼回去」確實需要 prev_ack 結構(而非 `_drift_old_reason`)的失敗例再保留。

## F5 `--tracked-in` 的六種拒絕與判活共用同一個條件,卻列兩次
severity: minor
blocking: 否(重複敘述會造成兩處實作漂移,判準:實作形狀可合併,非功能缺陷)
段落:範圍第 4 項、做法 2、做法 3、驗收條款 S2、S3。
問題:「開著」的定義(Issue 狀態在 `_DRIFT_OPEN_ISSUE`、計劃狀態在 `_STATUS_ENUM["project"]` 扣掉 `_DRIFT_CLOSED`)在表態時(`cmd_drift_ack`)與判活時(`_drift_ack_live`)各檢查一次,spec 三處分別描述。應該寫成單一純函式 `_drift_open_note(type, status) -> bool` 兩處共用,spec 現在沒有點出共用,實作容易分叉(例如一邊漏掉 `type` 檢查)。另:現有常數裡 Issue 的 `doing` 與計劃的 `doing` 值相同,但 `_STATUS_ENUM["system"]` 也有 `doing`——所以「只看狀態」會誤放 Systems 節點,type 檢查不可省;要在共用函式內寫死,不要讓兩個呼叫端各自記得。
預期 vs 實際:同一個節點在表態時被收、判活時被拒(或反之)就是這種分叉的結果;共用一個函式後 S2 與 S3 的相關案例可合測。

## F6 常數與旗標:可保留的部分(已讀,無 finding)
severity: minor
blocking: 否(僅確認)
`_DRIFT_ACK_DAYS`、`_DRIFT_ACK_LEGACY_UNTIL`、`_DRIFT_EXPIRING_KINDS` 三個常數:前兩個是使用者已裁定的數字(固定 30 天、固定 11-05);第三個把 c1-c6/m1/count 排除在外,命名照 `_DRIFT_BOUND_KINDS`,有存在理由。`born_now` 標記(做法 6)只標 `old` 不為真的,與 `_drift_probe_judge` 的新寫分支條件一致,是 B2 必需的最小標記,不另需 `_drift_born_annotate` 的歷史回溯(已避開 scan 的判不了)。「不做」清單各項(不自選天數、不刪表態檔、不改 c1-c6)都在縮小範圍,方向正確。

## 逐節
- 範圍:已讀;F1(第 3 項「推送版本裡還開著」)、F2、F5 相關。
- 做法 1(常數):已讀,無 finding(見 F6)。
- 做法 2(表態寫入):F2、F5。
- 做法 3(`_drift_ack_live`):F2、F3、F5。
- 做法 4(`status_of`):已讀,無 finding(沿用呼叫端圖譜物件,方向對;只在 F1 的推送路徑建樹那點有疑)。
- 做法 5:F1、F4。
- 做法 6:已讀,無 finding。
- 做法 7:F1、F4。
- 做法 8、9:已讀,無 finding(說明同步是必要成本)。
- 實務隱患:已讀,無 finding。逐類:日期取本機=只在 scan,不擋,無;金流、對外送出、不可逆=spec 已排除且理由成立;守衛面=收緊 B2 有 S6、S7 兩條對照,F1 的簡化不改這一點。
- 驗收條款:S1、S3 隨 F2 變動;S6 隨 F1 變動;S2、S4、S5、S7 已讀,無 finding。
- 回退、天花板、REVISIT、審計修正紀錄:已讀,無 finding(天花板第 1 條反而支持 F1 的簡化)。

## 圖譜鏡頭(固定席)
本次派工附的合約/事故節點清單未在 prompt 中給出,無從逐條判;已讀 spec 的 lands_in 為 Systems/存量漂移守衛。簡化建議(F1–F5)只減少機制、不新增行為,不會破壞既有 c2/c3/c6 `related`/`seq` 綁定語意(spec 明說不動那條分支,見 `scripts/lumos:34372` 的 `_DRIFT_BOUND_KINDS` 分支與 m1 分支),判「不影響」。

最嚴重 severity:major;blocking 條數:2(F1、F2)。
