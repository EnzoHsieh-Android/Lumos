severity: minor

# 邊界-sonnet 第 2 輪報告(邊界與輸入)

驗證方式:`git clone --shared` 到我自己的臨時目錄、HEAD=73bc8aff。每一格都「同時跑 `_kill_recipe_judge` 與真跑 `guard kill --json`」比對(自寫的跑批腳本,沿用 t_kill_recipe_check_matches_guard_kill 的 cell/對照表):
- 路徑 60 餘格:空字串、`/`、`.`、`..`、`./`、`//`、`./prod.py`、`prod.py//`、`./././prod.py`、`sub/..`、`prod.py/..`、`prod.py/./`、`./prod.py/.`、結尾 `/..`、`../myrepo/prod.py/../prod.py`、大小寫混合(PROD.PY、SUB/a.py、sub/A.PY、STRASSE↔straße、ﬁ 連字)、中文檔名、NFC/NFD 檔名與資料夾名(四種組合含 `./` 與 `..` 混用)、含空白/引號/反斜線/換行/結尾空白的檔名、300 與 5000 字長檔名、120 層 `x/../` 往返、`.git/config`、`.git`、資料夾(含 `sub/.`、`sub/`)、old 空字串/跨行/CRLF/BOM/空檔。全部一一對得上,只有一格不同(見 F3 附帶,NUL)。
- test 欄(單平台與多平台兩套設定):空、`p:TestX`、`q:TestX`、`:TestX`、`p:`、Kotlin 反引號 `` `a b` ``/`` `` ``/`` ` ``、含點與空白、`a;b`、中文、`a:b:c`、`p:p:Test`、換行結尾等 29 種。全部對得上。
- 欄位型別(new/old/file/test/invariant/platform 各自缺、None、int、list、空字串、未知平台):判斷函式與 guard kill 對得上,例外見 F2。
- 設定檔讀不了配方(kill-add 與 doctor P2 各跑一次):壞 JSON、空檔、最外層是 list/str/null、兩平台沒預設、預設指向不存在、平台 spec 是 null、root 是 null/int、profile 是 list、root 不存在、root 不在 git repo、設定檔不存在、`test` 不是物件、`platforms` 是 list。逐一確認 kill-add 印恰好 1 行(換行除外,見 F1)、照寫入、rc 0、stdout 兩行不變;P2 照 S4 字面。
- kill-add 提醒字面(file 欄 14 種、test 欄 9 種、old 空/含換行與 ESC):全部恰一行、人寫欄位有加引號並跳脫控制字元(`\n`、`\u001b`、`‮` 都沒漏到終端)、字面照狀態。
- kill-rm:15 條混合配方(物件、int、null、str、list、缺欄位、重複身分、含換行檔名、巢狀、float、bool、空物件、含 NUL 與雙向覆寫字元的 old)逐條用 8~12 字元短身分移除:每次恰移 1 條(重複身分移 2 條)、其餘不動;7 字元、`0x` 前綴、65 字元、空字串、非十六進位都擋下回 2 且筆記不變;大寫與前後空白被接受。
- P2 逐條行:15 條混合配方各自一行,格式壞的有第幾條與欄位、修法短身分與 kill-rm 實際可用的一致。

## F1 設定檔來源的字串沒過 _kill_show:提醒與 P2 項目可變成多行、帶原始控制字元
severity: minor
blocking: 否
引句:「out.update(status="noroot", detail=f"平台 {_kill_show(plat)} 的根找不到({pentry['root']}:{why})")」
佐證行:file: `scripts/lumos:13353`(_kill_p2_one 裡 noroot 分支同一族);`scripts/lumos:13221`(cfg 狀態 `detail=f"設定檔讀不了:{ctx['cfg_err']}"` 同樣原樣放進去);`scripts/lumos:13309`(_kill_add_warn 的 else 分支 `msg = f"{res['detail']},沒驗原文"`)

1. 第 1 輪資安席的修法(`_kill_show`)只套在「配方裡人寫的欄位」。設定檔來源的字串(`cfg_err`、`pentry['root']`、`why`)仍原樣進提醒行。設定檔跟筆記一樣會隨提交進來,同一個威脅面;S1 又明寫「恰好一行」。同族漏網,沒掃完。
2. 最小重現(自己的臨時 repo,`.lumos/config.json` = `{"platforms":{"a\nb":{"profile":"zz"}}}`,跑 `lumos guard kill-add Systems/Limit 上限恆為5 --file prod.py --old "LIMIT = 42" --new Z --test T`):
   stderr 變成 2 行:`⚠ 提醒:設定檔讀不了:設定檔 platforms['a` / `b'].profile 填了 'zz',工具不認得(...),沒驗原文`。
3. 控制字元版:profile 值寫 `"zz\u001b[2Kfake\nFIXED"`,stderr 第 1 行含原始 ESC `[2K`(清行碼),第 2 行是偽造的 `FIXED',工具不認得…`。`default_platform` 含換行同樣兩行。
4. 平台根版:`{"platforms":{"a":{"profile":"python","root":"nodir\nx"}}}`(root 不存在)→ kill-add 提醒 2 行(`…/myrepo/nodir` 換行 `x:不存在),沒驗原文`);doctor P2 的「它底下 2 條配方沒驗」項目被拆成兩行,第二行是 `x:不存在),它底下 2 條配方沒驗`。
5. doctor 的 P2 設定檔錯誤項(`設定檔讀不了:…`)同樣把原始 ESC 與換行印出來(`doctor --verbose` 實測,ESC 原樣在輸出)。
6. 影響:提醒仍會出、仍照舊寫入、rc 不變,所以不會擋錯推送;壞的是「恰好一行」合約與資安席要擋的偽造/蓋字面。修法方向:cfg_err、root、why 與 top 進提醒前一律過 `_kill_show`(或取首行並跳脫),並補一格測試(設定檔含換行的平台名)。

## F2 test 或 invariant 是數字時,判斷函式說 malformed、guard kill 其實照跑
severity: minor
blocking: 否
引句:「bad = [f"{k} 沒寫或不是字串" for k in ("file", "old", "new", "test") if not isinstance(r.get(k), str)]」
佐證行:file: `scripts/lumos:12920`(`_kill_method_name` 用 `str(test or "")`,guard kill 呼叫它,整數 5 會變 "5" 通過白名單)

1. 重現:筆記 kill_recipes 裡把 `"test": 5`(或 `"invariant": 5`)手寫成整數,真跑 `guard kill --json` → verdict `survived`(whole-suite,rc 1),配方正常套用;判斷函式 → `malformed`,P2 會列「配方欄位格式不對(test 沒寫或不是字串)」,而 P2 標題宣稱列的是「guard kill 跑到會判 drifted 或擋下」的配方。
2. 同一族:`new` 為 None/int/list、`old`/`file` 為 int、`platform` 為 list 時 guard kill 確實崩潰(TypeError,rc 1),判 malformed 正確;`test`、`invariant` 兩個欄位是例外,guard 容忍。
3. 影響很小:只有手改 JSON 才會出現整數;kill-add 寫不出來。要修就把 `test` 與 `invariant` 的檢查改成跟 guard 實際行為一致(接受非字串或照 `str()` 轉),或在 malformed 字面講清楚「這種寫法 guard kill 雖然能跑,但不合格式」。
4. 另外觀察(不構成問題):缺 `old`/`file` 時 guard kill 回 drifted(old 當成空字串命中多次)或逃逸,判斷函式回 malformed;兩邊都警告,字面不同但沒誤導。

## F3 NUL 字元的檔名:判斷函式判 missing,guard kill 實際崩潰
severity: minor
blocking: 否
引句:「return "missing", f"工作目錄裡沒有這支檔({ex.strerror or ex})"」
佐證行:file: `scripts/lumos:13194`(`_kill_read_text`);`scripts/lumos:13262`(`os.path.lexists` 對含 NUL 的路徑回 False 而不是丟例外)

1. 重現:筆記裡 `"file": "prod\u0000.py"`(只能手改 JSON,argv 帶不進 NUL)。判斷函式 → `missing`(提醒「會判 drifted」);真跑 guard kill → rc 1、`ValueError: lstat: embedded null character in path`(程式出錯,沒有 verdict)。
2. 兩邊都表示這條配方壞了,P2 仍會列它,只是「判 drifted」的字面不準。因為 NUL 檔名不可能是真檔,實務幾乎不會發生;給不出更具體的失敗場景,所以降到 minor。可以選擇不處理。

## 沒問題的部分(對照條款 S1–S7 與〈實作紀錄〉)
- S1:提醒恰一行(除 F1)、照寫入、stdout 與 rc 不變、ok 不印;被判重擋下不印這點我只靠讀程式(判重在 `_kill_add_warn` 之前 return),沒另外跑。
- S2:設定檔壞 JSON/不是物件/讓 load_platforms 丟例外/平台不在/根找不到,全印「沒驗原文」一行,load_platforms 的警告被接走沒多印。
- S4:設定檔讀不了字面「設定檔讀不了:<原因>」與整段兜底「這一段算不出來」分得開。
- S5/S7:本席路徑與 test 欄的新增格子與 guard kill 全部一致;未動 `cmd_guard_kill`。
- S6:kill-rm 邊界見上,全部符合。
- 附帶(非本次 diff):最外層是 list 的 `config.json` 會讓 doctor 在 `load_symbol_profile` 崩潰(`AttributeError: 'list' object has no attribute 'get'`,rc 1、沒有 P2 段)。這是既有碼,不歸本次改動,但 S4 若要涵蓋「最外層不是物件」,doctor 實際走不到 P2。file: `scripts/lumos:4357`。

最高等級:minor
