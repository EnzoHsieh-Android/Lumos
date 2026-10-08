severity: major

## F1 note-shape 層仍直呼 drift 層兩支內部函式,與「只呼叫這一支」的宣稱不符
severity: major
blocking: 是
引句:「hit = _drift_close_summary_untouched(_drift_note_status(ot), _drift_note_status(nt),」
另一處在 emit 的 _drift_summary_is_current(ln) 呼叫(同樣是 drift 層內部函式)。
說明:第 1 輪的結論是 note-shape 只經一支入口進 drift 層,diff 自己的註解也寫「提交前的筆記形狀檢查只呼叫這一支,不自己判收尾值與待定」。實際上 `_ns_close_summary_collect` 還直接呼叫 `_drift_note_status`(`scripts/lumos:32423`),`_ns_close_summary_emit` 直接呼叫 `_drift_summary_is_current`(`scripts/lumos:32445`)。這兩支是 drift 層內部的助手,等於舊問題換了位置重現。同層既有做法(`_ns_tag_hints_*`、`_ns_negation_*`,`scripts/lumos:31096-31170`)沒有任何 `_drift_` 呼叫。修法方向:入口自己吃兩版全文、回傳「(摘要行, 是否還寫待定)」,讓 note-shape 一個 _drift_ 名字都不碰。

## F2 新開關沒有 doctor 提醒,設定解析的警告也被丟掉
severity: minor
blocking: 否
引句:「if _note_shape_mode_parse(cfg_text, "close_summary", "結案摘要提醒")["mode"] == "off":」
說明:前綴提醒有 `_ns_tag_hints_doctor_lines`(`scripts/lumos:31162`),並在 `_doctor_note_shape` 那串呼叫裡掛上(`scripts/lumos:31706`),專案把開關關掉或寫壞時 doctor 會唸。close_summary 在 diff 的 scripts/lumos 部分沒有對應的 doctor 行,也沒有新增掛進 `scripts/lumos:31706` 那串。另外前綴路徑會印 r["warns"](`_ns_tag_hints_collected`,`scripts/lumos:31131`),close_summary 只取 ["mode"],設定檔壞掉或值寫錯(bad_value)時靜默照 warn,使用者得不到「看不懂」的一句,與共用解析函式的設計目的不符。

## F3 記帳形狀與前綴提醒略有差異
severity: minor
blocking: 否
引句:「extra={"check": "close-summary", "notes": len(items), "skipped": skipped})」
說明:同層 `_ns_tag_hints_emit` 的 extra 帶 check、rules、lines、notes(`scripts/lumos:31155`),close-summary 帶 check、notes、skipped,結構上同屬 hinted 帳、可接受;check 值用連字號(tag-hints / close-summary)一致。僅 skipped 是新欄位,屬自然差異,不另列嚴重。此條只記錄,不要求改。(⚠ 若編排者認為不算不一致可剔除)

## 三問
1. 分層與依賴方向:拆成 collect/emit、批次讀用 `_nodehome_cat_blobs`(`scripts/lumos:29336`)、摘要比對用 `_ns_summary_logical`(`scripts/lumos:31343`),都對齊同層做法。但 drift 層的入口只收一半(見 F1)。引句:「_drift_close_summary_untouched。開關 note_shape.close_summary=off 就不收。」
2. 命名與錯誤處理:`_ns_close_summary_*` 命名、出錯只印一句、不改 rc、hinted 帳都跟前綴提醒一致;缺 doctor 提醒與警告丟失(F2)。引句:「print(f"提醒:結案時摘要的對照這次沒做成({fail}),不影響這道檢查的判定", file=sys.stderr)」
3. 第二種做法:設定解析已抽成 `_note_shape_mode_parse` 與前綴共用,讀版本走 `_nodehome_cat_blobs`,摘要走 `_ns_summary_logical`,沒有另起一套;c7 加進 `_DRIFT_KINDS`、`_drift_fix_hint`、`_drift_doctor_lines` 與 `_DRIFT_NO_FIX` 也順著 c6/probe 的先例。唯一殘留是 F1 的跨層直呼。引句:「_note_shape_mode_parse(text, key, label):」

不對齊共 3 條,其中 major 1 條
