severity: clean

### 逐問覆核(三問,均一致,附對照 file:line;非 finding,供編排者核對用)

1. 分層與依賴方向:讀取層 `_nodehome_mark_note_content`(`scripts/lumos:18088`)繼續由它獨自呼叫 `_nodehome_reader`,把算好的 `content_notes` 放進分組;判定層 `_nodehome_evaluate`(`scripts/lumos:18140`)本輪改動後仍未新增任何 git/reader 呼叫,只消費 `g["content_notes"]`。收工前跑過的 `t_nodehome_diff_route_counts_content_per_commit` 尾端那段 AST 檢查(用 `_calls(fn) & io` 掃 `_nodehome_evaluate`)本輪沒被動到、原樣留著且通過,佐證判定層仍未跨層直呼 git,跟 `cmd_home_check`(`scripts/lumos:18462`)「組好輸入再呼叫 `_nodehome_evaluate`」的既有分工一致。

2. 命名與錯誤處理:`content_notes` 內每篇的 `own` 用 `{k for k in (_nodehome_key(v) for v in x["about"]) if k}` 算,跟 `_nodehome_homes`(`scripts/lumos:17995`)裡 `keys = {k for k in (_nodehome_key(v) for v in n["about"]) if k}` 同一支 `_nodehome_key` 取鍵,沒有另開一套判等規則。讀不到時的退路(`n`/`o` 為 `None` 時 `type` 預設 `"system"`、`status` 預設 `"doing"`)精確對應 docstring「讀不到一律當有變,照原本那樣查」——`"doing"` 落在 `_NODEHOME_HOME_STATUSES`(`scripts/lumos:17699`)裡,兩個預設值都保證不會被後面的類型/狀態過濾掉。`_nodehome_render`(`scripts/lumos:18304`)新加的「這是那個提交裡的名字,之後改名或刪掉了」判斷句,格式跟同一函式裡既有的 foreign-awakened 括號附註(`scripts/lumos:18358` 一帶)同樣是「主句+括號補充」寫法,訊息語氣沒有分岔。

3. 第二種做法:沒發現新引入的第二套「取管的檔」或「判家」規則——`per_commit` 路徑(`scripts/lumos:18239` 起)與既有 `routed`/`mine` 路徑(`scripts/lumos:18201` 起)是因為輸入資料形狀不同(推送前逐提交 vs. 提交前整批/讀取層失敗兜底)而分流,不是同一輸入下的兩套互斥實作;兩邊最終都吐同形狀的 `("route", (rel, files))` block 與 `pairs`,跟 `cmd_home_check` 後段的治理帳映射(`scripts/lumos:18543` 附近的 `elif kind == "route":`)接口一致。`content_paths`(舊名)在全庫已無殘留引用(已核對 grep),沒有留下「兩套機制並存」的痕跡。

實跑 `python3 scripts/test_lumos.py -k nodehome` 175 support 全過,含本輪新增的合併分支重現案例與既有的判定層零 git 呼叫斷言。

總結:最高 severity clean,blocking 共 0 條
