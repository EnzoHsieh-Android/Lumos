severity: minor

# 邊界-sonnet 第 1 輪報告(審 r1-snapshot-code.patch)

實驗方式:在 m1impl 的 HEAD(620a6f73)上用臨時 git repo 跑真的 `lumos drift check --diff`、`lumos drift ack`,HOME 換成臨時目錄。

## F1 同一行很長且命中很多次時,m1 的 30 秒上限不生效,時間隨行長平方成長
severity: minor
blocking: 否
引句:「toks = sorted({m.group(0) for m in rx.finditer(ln) if not _drift_m1_clause_hist(ln, m.start())})」
佐證: `scripts/lumos:29071`(掃筆記那行)與 `scripts/lumos:28741`(`_drift_m1_clause_hist`)
1. 輸入:起點版 `a.py` 定義 `old_func_name`、終點版刪掉;一篇筆記只有一行、把 `old_func_name` 重複 N 次(空白隔開)。
2. 實測(cold HOME、warn 模式、同一台機器):N=1000(14 KB)4 秒;N=2000(28 KB)14 秒;N=4000(56 KB)53 秒;N=20000(260 KB)超過 120 秒沒跑完,被工具逾時打斷。
3. 壞在哪:`_drift_m1_scan_note` 每 200 行才 `check_time()`,同一行內每個命中都呼叫 `_drift_m1_clause_hist`,那支對整行做一次 `re.sub` 加括號掃描(每次 O(行長)),命中數乘行長就是平方。單行沒有任何時間檢查,`_DRIFT_M1_BUDGET_SEC` 管不到。
4. 影響:一篇被推送的筆記(或表格、貼進來的長清單)就能讓 pre-push 與 CI 卡分鐘級;warn 模式也一樣卡,最後才 rc 0。要 2000 次以上命中才明顯,現實少見,所以只列 minor。
5. 未量:多行但每行都短(6000 行各一次命中)只要 1 秒,不受影響。

## F2 名稱頭尾有空白時,照提示貼的表態永遠對不上(一直被列出、block 下擋不掉)
severity: minor
blocking: 否
引句:「rec["names"] = sorted({str(n).strip() for n in names})」
佐證: `scripts/lumos` 中 `_drift_m1_name_ok` 與 `_drift_m1_split_acked` 兩處,patch 內 `return 1 <= len(s) <= _DRIFT_M1_NAME_MAX and _esc_clean(name, 10 ** 6) == name`
1. 輸入:`a.py` 有 `p.add_argument("--trail ")`(旗標字面值尾端一個空白),終點版刪掉;筆記一行寫 `用 --trail  與 --old-flag`。
2. `_drift_m1_name_ok` 用去空白後的長度判可列,但列出去的 `names` 是未去空白的 `--trail `;提示印 `'--name=--trail '`。
3. 照貼執行 `lumos drift ack … --name='--name=--trail ' …` 成功(rc 0),但記進帳的是去空白後的 `--trail`(帳裡實看到 `"names": ["--old-flag", "--trail"]`)。
4. 提交表態後重跑 `drift check`:同一行仍列出,名稱還是 `--trail `。`_drift_m1_split_acked` 用 `set(f["names"]) <= got`,`"--trail "` 不在 `{"--trail"}` 裡,永遠不算已表態。
5. 影響:只有旗標字面值帶頭尾空白這種極少見的輸入;若該行落在「要處理」層又是 block,唯一出路是改筆記或 `LUMOS_SKIP_DRIFT_CHECK=1`。修法方向:列出前就對名稱 strip,或比對時兩邊都 strip(不寫進報告的建議,僅指出不一致點)。

## 已跑過、沒發現問題的邊界(逐項一句)
- 純文件推送:rc 0,不印不記。
- 只刪 `.sh`:列成路徑名稱(`run_it.sh`、`scripts/old_tool.sh`),並印「2 支非 Python 程式檔改動(只看路徑)」;路徑帶 `bin/` 的檔依 `_DELGUARD_EXCLUDE_DIRS` 被排除,屬設計。
- 沒副檔名、`#!` python 腳本(放在 `scripts/`):刪除與修改都正確抽出定義名。
- 只改超過 4 MB 的 py:走文字抽定義,印「1 支用文字比對」,結果正確。
- BOM、CRLF:定義照抽,判定正確。
- 語法錯的 py、含 NUL 的 py、3000 層括號巢狀:不當機,記進剖不動;語法錯的終點版讓那支檔內消失的名稱整批不判,結論行仍印「沒有名稱消失」,只靠下一行「1 支剖不動」補充(計劃有寫,不算 bug);同一支檔同時算剖不動與文字比對時,那行路徑會重複印(`d.py、d.py`),純顯示。
- 名稱是旗標、中文、含 `;`、`$(id)`、空白:提示過 `_drift_sh`,實貼安全;含控制字元的名稱與超過 200 字的名稱不列並計入「太長沒列」(含控制字元的也叫「太長」,措辭略不準,不影響判定)。
- 同一行 20 個各 155 字的名稱:提示 3300 多字仍印出完整 ack 指令。
- 路徑含換行、含 `$(id)` 與反引號的筆記名:提示以引號包起,安全;帳 rows 過 `_esc_clean`。
- 筆記超長多行(6000 行各一個名稱):1 秒內完成。
- 筆記讀不出:沒改到的計「N 篇沒掃」照掃其他;改到的走 unreadable 並印提醒。
- 快取目錄:HOME 唯讀、`drift-defs` 是 symlink、目錄 777、HOME 未設,全都靜默當沒快取,沒寫到 symlink 指向處。
- `.lumos/config.json` 的 `old_sentence`:`[]`、`{}`、`123`、`true`、`"BLOCK"`、含 ESC 的字串都回 warn 並印提醒(`{v!r}` 已跳脫 ESC);`null`、`"off"`、`"block"` 正常。
- 新分支首推(遠端空、遠端有 main)、只有根提交:分別印「從空樹算」「沒有起點版可比」「從分岔點算」,rc 0。
- 表態:`--name=--flag` 正確記下;`--name=`、`--name= `、`--name` 少值、缺 `--name`、`--kind c1 --name=x`、含換行、201 字都以 rc 2 擋下;200 字剛好過。
- 帳事件超過 4096 位元組:rows 丟到 0 且 nodes 截到 20 仍超(實測 4728 位元組,60 篇長路徑家筆記)——照計劃「再超過照寫」,不是缺陷。

## 圖譜鏡頭固定席(前 8 篇,從邊界與輸入角度逐條判)
- `Systems/lumos-cli-read`(search 預設排除 superseded、不排 stale):不影響。patch 只動 drift 一帶與 `_lens_cache_write`,沒碰 search 的濾網;m1 不讀 status,實測 superseded 的家筆記也照算家(計劃已明寫)。
- `Systems/bound-tests-gate`(綁定測試逐支真跑、算不出不擋):不影響。m1 沒改 code-loop check 或 impact 的路徑;實測 drift check 的 rc 只由 m1 自己與 gate 兩個開關決定。
- `Systems/guard-kill`(rc 優先序、--json 純度):不影響。patch 沒碰 guard kill;m1 的輸出全走 stderr,沒有 stdout JSON。
- `Systems/授權與歸屬`(授權檔不進 _VENDORED_TOOLKIT、主程式檔頭 SPDX 與 MIT):不影響。patch 對 `scripts/lumos` 的 hunk 都在 1137 行之後,檔頭沒動;沒新增要被複製的檔。
- `Systems/測試假綠形態`(還原翻紅釘要有前置斷言):不影響本審的程式 patch(測試在另一份 patch,不在我審的範圍)。
- `Systems/lumos-cli-lifecycle`(re-inject 不動 sentinel 外內容):不影響。m1 只讀 git 物件與圖譜、只寫 `~/.cache/lumos/` 與治理帳,不寫 CLAUDE.md;實測快取目錄不可寫、是 symlink、777、HOME 未設都靜默略過。
- `Systems/design-loop`(處置閘第五步、審材必須是 .md 計劃):不影響。m1 沒碰 loop 的處置閘;跑到的 drift 路徑與 loop id 判定無交集。
- `Systems/pitfalls-code-loop`(RISK):不影響行為。`_lens_cache_write` 改成轉呼 `_home_cache_write`,我實測 dispatch-lens 快取寫入的信任目錄檢查邏輯搬過去後仍走 `_mkdir_trusted_under_home` 與 `_trusted_private_dir`;寫失敗仍靜默(只多回 False)。未跑派工鏡頭本身的邊界輸入,標為未驗。
- 其餘只列名的節點:未逐篇判。

最高等級:minor
