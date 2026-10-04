severity: minor

## F1 _usage_log 沒有跟另兩支寫入器一樣擋捷徑
severity: minor
blocking: 否
引句:「p = _docs_ledger_path(env.vault.parent, USAGE_LOCAL_LOG_NAME)」
file: `scripts/lumos:16308`
失敗場景(已重現):
1. docs/.usage-local.jsonl 是指向 repo 外檔案的捷徑(例如被 git add -f 提交進來的)。
2. 使用者跑 `lumos show <節點>`,走到 _usage_log,直接 open(p,"a") 跟著捷徑寫。
3. 實測 tmp 目錄:捷徑指向的檔被追加了一行 JSON。_gate_event 與 _append_governance_log 這輪都加了 is_symlink 擋,這支漏了,r1 資安席的威脅面只補了三分之二。

## F2 _ensure_docs_gitignore 把使用者做的 .gitignore 捷徑換成普通檔
severity: minor
blocking: 否
引句:「_write_lf(gi, (raw + chunk).decode("utf-8"))」
file: `scripts/lumos:21072`
失敗場景(已重現):
1. docs/.gitignore -> ../shared.gitignore(共用忽略清單)。
2. 跑 lumos init / update 補忽略規則,_write_lf 走 os.replace,換掉的是捷徑本身。
3. 結果 docs/.gitignore 變成獨立普通檔,共用檔 shared.gitignore 內容不變、還是缺那兩行;以後改共用檔不再傳到 docs/。舊的 "ab" 追加是寫進共用檔、捷徑還在。測試 ④ 把這個行為當成期望,但沒處理「捷徑是使用者刻意做的」這種情況,也沒印一句說換掉了捷徑。另外 os.replace 會讓檔案擁有者改成目前使用者、斷開硬連結(只是同族的小處)。

## F3 合讀改讀檔尾後,S13「最近一次規格閘」會漏掉帳尾以前的計劃
severity: minor
blocking: 否
引句:「raw, _start = _gov_tail_bytes(p)」
file: `scripts/lumos:2989`
失敗場景:
1. 版控帳超過 24 MB(程式註解自己寫「帳約 16MB」且還在長)。
2. 某計劃最後一次 spec-gate-run 落在檔頭 24MB 以外(新的 spec-gate-run 之後都寫本機帳,舊的只在版控帳)。
3. S13 的 _latest 字典讀不到它,該計劃從「最近一次規格閘跑出來的紅綠弱證據」清單消失,原本整份讀會列出。cmd_gov 之外的這個讀者因此少讀;其他走 _gov_ledger_rows_by_time 的只有這一處。頭一行恰好落在行首時也會多丟一筆完整行。

## 已走過沒問題的範圍
- _gov_ts:度量段原接 (ValueError, OverflowError),現多接 OSError,是超集;非字串、naive 轉本機、aware 直通、9999 年出界都回 None,度量段與合讀行為一致;台北 +08:00 與 UTC 混用時 aware 比較不溢位,key 的 timestamp() 例外有接。
- 暖機護欄:走本機帳的 (閘,種類) 看 oldest_local,本機帳不在即不判;走版控的種類看版控 oldest;同一閘兩種混走各自正確;hard=True 的事件進版控、仍被 evs 計到,只會偏保守。本機帳最舊一筆來自別的閘也只偏保守。新增名單成員之前的舊事件在版控、之後在本機,兩本合數無遺漏或重複。
- 時間排序同秒保留讀入順序(版控在前),spec-gate-run 後寫者勝取本機,符合預期;同一事件不會同時進兩本(分流是互斥判定)。
- _local_ledger_doctor_msgs:tracked 與 ign 分支互斥、非 git 時 check-ignore 回 128 不提醒。
- _write_lf 的 BOM、CRLF、LF 位元組原樣保留,權限用 copymode 延續,例外時清暫存檔;非 UTF-8 不動。
- 兩支治理帳寫入器的捷徑擋與 False 回傳:_gate_event_or_warn 只印警告不改判定。
- 跑了 `python3.14 scripts/test_lumos.py -k gov_split`:36 passed。
- 圖譜鏡頭:判定類讀者(code-loop、fix-check、design-loop、lint-new fail-open、loop 關門)讀的閘種類都不在 _GOV_LOCAL_PAIRS 名單內,這份 diff 沒破壞「判定類只讀版控帳」的合約;名單 drift 測試仍綠。

整體只剩三處小問題:一處捷徑防護漏了使用紀錄寫入器、一處會換掉使用者的 .gitignore 捷徑、一處合讀改讀檔尾讓舊規格閘紀錄可能消失,皆不阻擋。
