severity: major

先講結論:r1 的 F1 到 F6 都照它要的方向修了。這一輪新冒出 2 條會擋的(治理帳多了第二支讀取函式、盲判與表態的讀法分家),另有 4 條小的。

## r1 六條逐條核對

- **F1 範圍計算**:已抽成共用。`code-loop check` 與盲判都呼叫 `_codeloop_disp_range`,退路一致(`scripts/lumos:72427`、`scripts/lumos:73134`)。
- **F2 分支解析**:已共用。合併提交認合進來那一側時,盲判跟著讀那一側的分支名與帳(`scripts/lumos:72048`、`_disp_bj_source`)。
- **F3 入口**:已走 `cmd_code_loop`,`--branch`、`--at-sha` 與 dispositions 同一套解析(`scripts/lumos:73712`)。
- **F4 欄位型別**:`role`、`seg`、`row`、`keys` 都登進 `_GOV_FIELD_TYPES`(`scripts/lumos:17473-17475` 的註解規定要補)。
- **F5 編解碼**:`_kt_sit_key_enc` / `_kt_sit_key_dec` 一對管寫入、去重與統計。「每格取第一筆」併進 `_kt_bj_fold`。
- **F6 讀表**:`dt_sources` 與 `_KT_DT_SOURCES` 已刪。出處跟著 `dt_table` 的列走,縮寫表由 `abbr_table` 與 `abbr_hit` 共用(`configs/ast-grep/kotlin-android/check.py:197`)。

## ① 模組邊界

範圍計算與分支解析都收進共用函式了,模組分工對。剩下兩處小毛病,都不是結構錯。

引句:「tip_on_ml, rng = _codeloop_disp_range(repo_root, branch, at_sha, diff_range)」
對照:`scripts/lumos:73134`。原本內嵌的那段已經搬進 `_codeloop_disp_range`,check 與盲判現在共用。

**F1**
severity: minor
blocking: 否
引句:「mb = _codeloop_default_base(repo_root)」
- 沒給 `--diff` 時,推導「預設起點..版本」這兩行在盲判又寫了一份(`_kt_bj_segments`,`scripts/lumos:72589`),`_codeloop_guard_verdict` 本來就有(`scripts/lumos:73071`)。
- 兩邊一個接 `HEAD`、一個接 `at_sha`,各自有退路,所以只算小問題,不是第二套範圍規則。

**F2**
severity: minor
blocking: 否
引句:「merge_ledger=lambda: merge_cache.get("ledger"))」
- 判定函式直接伸手進合併查找的內部快取鍵 `"ledger"`,那個鍵是 `_codeloop_merge_side_lookup` 寫的(`scripts/lumos:71738-71745`)。
- 同一個檔案內、沒有跨層,但這是隱性耦合。已經有查找函式回傳 `(帳, 原因)` 的形狀可以直接用。

## ② 命名與錯誤處理

事件 kind、擋下訊息、回傳碼都沿用既有寫法。以下兩處不一致。

引句:「bj=({"file": args.cl_bj_file, "template": args.cl_bj_template, "mode": args.cl_bj_mode,」
對照:`scripts/lumos:73712`(`cmd_code_loop`)。其他子指令的參數都是平的:`disp_file`、`qid`、`loop`。

**F3**
severity: minor
blocking: 否
引句:「def _codeloop_blind_judge_args(repo_root, branch, at_sha, diff_range, bj):」
- 盲判是唯一把旗標打包成 dict 傳給 `cmd_code_loop` 的子指令。
- 多出一層只做旗標組合檢查的包裝函式,表態那邊是檢查直接寫在 `_cmd_codeloop_dispositions` 裡(`scripts/lumos:73632`)。

**F4**
severity: minor
blocking: 否
引句:「def abbr_table(text):」
- check.py 的函式命名是公開的讀表入口(`dt_table`、`dt_row`、`dt_triggers`)搭配底線開頭的內部輔助(`_dt_header`、`_cells`)。
- 這次新增的 `abbr_table`、`abbr_hit` 是公開名字,同時新增的 `_main_names`、既有的 `_src_expand` 卻是私有名字,同類輔助的命名分成兩種。

## ③ 第二種做法(治理帳讀取、壞行處理、範圍計算、讀表)

範圍計算、讀表、`keys` 編碼、投票折法這四項都收斂成一套了,沒有新增第二種。治理帳讀取和標記檔政策這兩項有問題。

引句:「cells = _kt_bj_fold(bj)」
對照:`scripts/lumos:17499` 附近 `_gov_situation_collect`。統計端改用 `_kt_bj_fold`,跟核對端同一支,F5 的方向對。

**F5**
severity: major
blocking: 是
引句:「def _kt_bj_ledger_events(raw, branch):」
- 讀治理帳 code-loop 事件的篩選條件(`gate == code-loop`、`kind`、`head_sha` 是非空字串)現在有兩份:既有的 `_codeloop_ledger_events`(`scripts/lumos:69949`)與新寫的 `_kt_bj_ledger_events`。
- `_codeloop_ledger_events` 的註解自己寫「哪些事件算數只寫一次」。這一輪把盲判從它身上拿掉,另寫了一支讀取函式。
- 壞行處理也分了兩種:既有的接 `except Exception`,新的接 `(ValueError, RecursionError)`,後者是照 `_drift_jsonl_parse` 的接法(`scripts/lumos:57543`)。
- 新函式的理由是「位元組預篩、不整份解碼帳」,在 `_kt_sit_reminder_log` 有先例。比較整齊的做法是讓共用那支接受位元組、多一個分支條件,而不是另開一條讀取路徑。

**F6** ⚠ 判不準,交編排者
severity: major
blocking: 是
引句:「紀錄只有治理帳一份(代碼審 r1 甲,事件溯源:只追加的帳是唯一真相)」
- 我的判斷:這算這次引入的第二種做法。
  - `_codeloop_read_dispositions` 仍是「標記檔優先、壞了退治理帳」(`scripts/lumos:71627`)。
  - 盲判改成「只讀治理帳、分支名完全相同」之後,同一個專案裡對「本機標記檔 vs 治理帳誰是真相」有兩套讀法。
  - 兩者是這次修補才分家的:r1 的盲判原本照表態那組走。
- 盲判這一側的設計比較站得住腳:CI 只讀治理帳,標記檔只是快取(見 `_cmd_codeloop_dispositions` 的註解,`scripts/lumos:73660` 附近)。
- 問題是只改一半。表態讀取仍有「舊標記檔蓋掉帳」的同一個洞,而 `_codeloop_write_marker` 的註解也被改成「表態用」(引句:「表態用;盲判只寫治理帳,代碼審 r1 甲」)。
- 標 ⚠ 的原因:要不要把表態也改成只讀治理帳,是政策裁量,超出架構對齊席的範圍。
- 最低要求是把這個分歧記進圖譜(帶回頭條件),不能只留在程式註解裡。

不對齊共 6 條,其中會擋的 2 條。
