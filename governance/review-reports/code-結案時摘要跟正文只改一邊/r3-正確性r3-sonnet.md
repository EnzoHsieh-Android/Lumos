severity: minor

## F1 結案摘要的設定提醒每次暫存提交都印,不管有沒有候選筆記
severity: minor
blocking: 否 — 只多印提醒、不改 rc
引句:「for w in cfg["warns"]:」
file: `scripts/lumos:32419`(對照 `scripts/lumos:31131` 的 _ns_tag_hints_collected 只在 seen 時才印設定提醒)
場景:.lumos/config.json 寫 close_summary 為 "OFF"(或整檔不是合法 JSON)。每一次有圖譜的暫存提交,即使完全沒動筆記狀態,collect 一進來就先印「看不懂/讀不了」。設定檔讀不了時,_note_shape_config 與這一行各印一次,同一次提交出現兩條同因提醒。前綴提醒與否定現況句都限定在「這次真的有相關行」才印。實測只多印、不影響判定,故 minor。
建議:把設定提醒挪到確定有 items 才印。

## F2 只靠換行路徑被挑掉時,「超過 50 篇」那句話是錯的
severity: minor
blocking: 否 — 只影響提醒措辭
引句:「skipped = max(0, len(cands) - _NS_CLOSE_SUMMARY_MAX_NOTES) + len(bad)」
file: `scripts/lumos:32425`、`scripts/lumos:32463`
場景:狀態有動的筆記只有 1 篇,路徑含換行;skipped=1,但 emit 若有別篇 items 會印「狀態有動的筆記超過 50 篇,另 1 篇沒看」,與事實不符。若 items 為空則整段不印(靜默)。挑掉邏輯與計數本身是對的:bad 先挑再算上限,沒重複計;`c not in bad` 對 tuple 做線性比對,N 為候選數(不受 50 上限約束)時是 O(N²),實測可忽略。

## F3 摘要只有空白行時會印出空白列
severity: minor
blocking: 否 — 只是提醒多幾行空白
引句:「return [ln for _no, ln, reg in _drift_pending_lines(text) if reg == "summary"]」
file: `scripts/lumos:34565`(_drift_pending_lines 把 summary: 之後的空行也當 summary 區塊)
最小重現(已跑):`summary:` 後接兩個空行再接收尾 `---`,上一版 status: open、這一版 status: resolved,摘要不變 → 回 `[('', False), ('', False)]`,提交時會印出「這篇摘要沒跟著改」並列出兩行空白。實務上要寫出 `summary:` 空值又帶空行才會中,少見。

## 已讀無 finding(依鏡頭逐項)
- 只改縮排/尾端空白:新舊是逐字 physical 行比對,縮排不同 → 判「摘要有動」→ None(實測 `KEY:a` 兩格縮排改四格回 None)。偏向少提醒,方向保守,對只提醒的檢查可接受。
  引句:「or _summ(old_text) != new_summary):」
- 續行與多行/單行互轉:單行值入列(行首非空白且值非 |>#),續行縮排行入列,`|` 與 `>` 標頭行不入列(`|`→`>` 仍提醒,內容未動所以對);單行轉區塊因行文字不同 → None,保守。實測皆符合。
  引句:「if in_sum and ln[len("summary:"):].strip()[:1] not in」(實際在 `_drift_pending_lines` 內)
- _drift_note_status 兩版各叫一次:每篇至多 2 次 split+parse_frontmatter,且短路後 old 只在 new 已是收尾值時才算。但 `_summ(new_text)` 排在狀態判斷之前,每個候選都多掃一次正文 _visible_lines;上限 50 篇,可忽略。無 frontmatter 時 _drift_fm_end 回 0,range(1,0) 為空,不拋例外(已跑)。
  引句:「new_summary = _summ(new_text)」
- doctor 多一行:預設(沒設 close_summary)回 [],既有 doctor 測試的行數/Grep 計數斷言不受影響;只有 off 或壞值才多一行,測試 ⑩ 已覆蓋。
  引句:「out += _ns_close_summary_doctor_lines(txt)」
- 記帳欄位 rules、lines:`sum(len(x) for _r, x in items)` 的 x 是 [(行,bool)],型別對。
  引句:「"lines": sum(len(x) for _r, x in items), "notes": len(items), "skipped": skipped」

資料狀態五問:空(無 summary/無 frontmatter)→回 None 不拋;單一(單行摘要)→照算;大量(候選超 50)→截斷+計數,O(N²) 的 not-in 可忽略;重複/換行路徑→挑掉計入 skipped,措辭見 F2;髒資料(CRLF、BOM)→decode utf-8-sig、strip 判分隔線,不影響。

總結:修正本身方向正確、未引入會誤判結案的新洞,僅有三條只影響提醒雜訊與措辭的小問題。
