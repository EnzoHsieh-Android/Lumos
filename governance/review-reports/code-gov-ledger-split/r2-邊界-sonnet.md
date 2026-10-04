severity: minor

(LUMOS-IMPACT:派工尾端沒有附固定席筆記、也沒有「圖譜沒有釘到節點」備援段,圖譜鏡頭無條目可答;下面只就邊界輸入實跑。)

## F1 第三支寫入器 _usage_log 沒套上捷徑守衛
severity: minor
blocking: 否
引句:「p = _docs_ledger_path(env.vault.parent, USAGE_LOCAL_LOG_NAME)」
file: `/home/user/Lumos/scripts/lumos:16308`
失敗場景:本輪在 _gate_event(1458)與 _append_governance_log(1535)加了「本機帳是捷徑就不寫」,理由是被強制提交進來的捷徑可指向 repo 外。同一個資料夾的 .usage-local.jsonl 同樣被忽略、同樣可被 `git add -f` 提交成捷徑,但 _usage_log 仍直接 open(p,"a")。輸入:docs/.usage-local.jsonl 是指向 /tmp/victim 的捷徑,執行 `lumos show <節點>` → 追加一行到 /tmp/victim。守衛只補了一半,威脅模型沒收乾淨。

## F2 .gitignore 改整份替換後,唯讀檔與捷徑檔被換成新檔
severity: minor
blocking: 否
引句:「_write_lf(gi, (raw + chunk).decode("utf-8"))」
file: `/home/user/Lumos/scripts/lumos:17727`
失敗場景:實跑(臨時目錄)。輸入 A:docs/.gitignore 內容 `x\n` 且 chmod 444(使用者刻意鎖住),非 root 下原本 open(...,"ab") 會 PermissionError 而不動;現在 os.replace 只看資料夾權限,檔案被換成新檔(copymode 保留 444,但內容已改),結果 `['.governance-local.jsonl', '.usage-local.jsonl']` 並寫入。輸入 B:docs/.gitignore 是指向共用檔的捷徑(已追蹤的 symlink),現在被換成一般檔,git status 出現 typechange,而共用檔沒補到規則。輸入 C:docs/ 唯讀但 .gitignore 可寫,原本追加成功,現在 _write_lf 建暫存檔失敗 → 靜默回 [],本機帳沒被忽略。意圖(防併發重複補、不寫到捷徑指的地方)成立,但副作用沒進測試與說明。

## F3 兩本合讀改讀檔尾 24MB 後,規格閘「最近一次」會漏掉較舊的計劃
severity: minor
blocking: 否
引句:「raw, _start = _gov_tail_bytes(p)」
file: `/home/user/Lumos/scripts/lumos:2989`
失敗場景:舊寫法 read_text 讀整本,_gov_ledger_rows_by_time 唯一的呼叫端 S13 要的是「每份計劃最後一筆 spec-gate-run」(後寫者勝)。現在每本只讀尾 24MB(_gov_tail_bytes 會丟掉切半的頭一行)。輸入:版控帳 > 24MB(正是 doctor 在警告的膨脹情況),某計劃唯一一筆 spec-gate-run 落在被截掉的前段 → 該計劃從清單消失;只剩那一份時印「還沒有任何計劃跑過規格閘」,是錯話。24MB 邊界:剛好 24MB 整份讀、多 1 位元組就從第 1 個位元組起切並丟頭一行。未能重現成檔(只推導,讀法差異在 diff 可見)。

## F4 度量暖機護欄:一筆偏舊的壞時間就讓本機帳的暖機失效
severity: minor
blocking: 否
引句:「oldest = t if oldest is None or t < oldest else oldest」
file: `/home/user/Lumos/scripts/lumos:3975`
失敗場景:實跑 _gov_ts。輸入 `0001-01-01T00:00:00+05:00` 這類帶時區的極早時間,解析成功(0001-01-01 00:00:00+05:00,timestamp -62135614800.0,比較不溢位),成為 oldest_local。本輪把暖機護欄改成看本機帳最舊一筆,所以本機帳剛建立、只有今天幾筆,加上一筆時鐘錯亂寫下的舊 ts,`first > cutoff` 為假、護欄放行,近 N 週數出 0 筆,誤報「這條限制該撤」(帶時區的 9999 年也被算進近 N 週窗內,反向灌水)。沒帶時區的 0001 與 9999 年則經 astimezone 溢位被 _gov_ts 回 None 而略過,這條路是安全的。

## 已走過沒問題的範圍
- _gov_ts:9999/0001 無時區(回 None)、`+24:00`(ValueError 回 None)、`+23:59`、`Z`、純日期、整數、None 全部實跑,無例外外洩。
- _gov_ledger_rows_by_time:版控帳是壞捷徑、本機帳是目錄 → _gov_tail_bytes 的 stat/open 丟 OSError 被吞,回 []。
- _ensure_docs_gitignore:空檔、只有 BOM(補成 BOM、換行、兩行)、BOM 後接已有規則(多補一行重複,git 本身會略過 BOM,無害)、CRLF 與 LF 混用且最後一行無換行(沿用 CRLF、補行尾)、壞捷徑(換成一般檔)、捷徑指向目錄(read_bytes 丟 OSError 回 [])、非 UTF-8(decode 失敗回 [])全部實跑符合預期。
- _local_ledger_doctor_msgs:PATH 清空(git 不在)時大小提醒已先加入、追蹤檢查丟 OSError 後 continue,不崩;帳檔是壞捷徑或目錄時 is_file 為假而跳過。
- 本機帳是捷徑時 _gate_event 回 False,走 _gate_event_or_warn 只印警告、不改判定;drift-check 的 ledger-miss 只是追加一行快取檔,無擋人後果。
- 度量:本機帳不在、不滿 N 週時不判(測試涵蓋);_gate_event 與 _append_governance_log 的 `batch is local` 身分判斷在兩批同為空清單時被 `not batch` 先短路,不誤判。

總結:四條都是低風險邊角(守衛漏補一支寫入器、整份替換的副作用、檔尾讀法的資料窗縮小、暖機護欄被偏舊時間繞過),沒有崩潰或擋人類的缺陷。
