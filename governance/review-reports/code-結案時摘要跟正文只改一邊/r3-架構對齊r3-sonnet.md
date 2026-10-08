severity: minor

## 問一:分層與依賴方向
Grep 確認:note-shape 層新程式(`_ns_close_summary_*`、`_note_shape_mode_parse`)裡以 `_drift_` 開頭的呼叫只剩 `_drift_close_summary_untouched` 一處(`scripts/lumos:32439`,位於 `_ns_close_summary_collect`),判定細節(收尾值、摘要切法、待定判定)全在 drift 層 `scripts/lumos:34704`。依賴方向 note-shape → drift 單向,入口吃兩版全文,不再跨層直呼內部函式。與既有先例 `_ns_tag_hints_*`(`scripts/lumos:31096`-`31160`)的「判定沿用既有函式」同向;`_drift_fix_args_err`(`scripts/lumos:37143`)改查表 `_DRIFT_NO_FIX` 結構對。
引句:「★提交前的筆記形狀檢查只呼叫這一支★:收尾值、摘要切法、待定判定都在這層、跟 c7 同一套」
結論:前兩輪的跨層問題已收掉。

## 問二:命名與錯誤處理
命名 `_ns_close_summary_{candidates,collect,emit,doctor_lines}` 與 `_ns_tag_hints_*`(`scripts/lumos:31096`、`31142`、`31173`)同形;蒐集與印出已拆;doctor 行已補並接進 `_note_shape_doctor_lines`(`scripts/lumos:31718`);記帳 `check=close-summary` 帶 rules/lines/notes,與 tag-hints 帳欄位對齊;出錯只印一句、不改 rc,同先例。小差異(見 F1、F2):設定提醒印的時機、git 呼叫入口。
引句:「提醒:結案時摘要的對照這次沒做成({e.__class__.__name__}),不影響這道檢查的判定」

## 問三:第二種做法
讀設定共用 `_note_shape_mode_parse`(`scripts/lumos:31072`),批次讀 blob 用既有 `_nodehome_cat_blobs`(`scripts/lumos:29336`),不再另起;沒有第二套收尾值或摘要切法。僅剩兩處輕微偏離既有節奏。
引句:「return _note_shape_mode_parse(text, "tag_hints", "筆記前綴提醒")」

## F1 設定提醒的印出時機跟 tag_hints 不同
severity: minor
blocking: 否
tag_hints 的設定提醒只在「這次有新寫的摘要行」才印(`_ns_tag_hints_collected`,`scripts/lumos:31131`),並由 prepare/collected 三段傳遞。close_summary 在 collect 一進來(只要 staged 且有 base)就無條件印設定提醒:開關寫錯時每次提交都唸,即使沒有任何筆記改狀態;也沒有 prepare 那一段、warns 在 collect 裡直接 print,蒐集函式帶了輸出副作用,與「蒐集與印出分開」不完全一致。
引句:「for w in cfg["warns"]:
            print(f"提醒:{w}", file=sys.stderr)」(同一段:cfg = _note_shape_mode_parse(cfg_text, "close_summary", "結案摘要提醒"))

## F2 git 呼叫入口用 _lens_git 而非 note-shape 層的 _ns_git
severity: minor
blocking: 否
note-shape 層的 git 讀取慣例走 `_ns_git`(`scripts/lumos:30153`,其註解說明測試靠換掉它造 git 失敗;同層 `scripts/lumos:30239`、`30293` 都是 `diff --name-status -z -M`),新的 `_ns_close_summary_candidates` 直接用底層 `_lens_git(..., binary=True)`,測試無法用同一個縫隙造 git 失敗。結構不算第二種做法,屬入口不一致。
引句:「r = _lens_git(root, "diff", "--cached", "--name-status", "-z", "-M", "--diff-filter=MR", "-G", "^status:",」

不對齊共 2 條,其中 major 0 條
