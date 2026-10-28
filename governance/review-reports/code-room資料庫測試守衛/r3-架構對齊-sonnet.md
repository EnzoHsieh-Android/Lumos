severity: major

锁檔 `...json.warming` 不存在(ls 回 No such file),所以沒有鎖要處理,我也沒刪任何東西。

我把 332557454 版的 `scripts/lumos` 存到審查臨時目錄(`/tmp/lumos-seat-work/code-room資料庫測試守衛/架構對齊-sonnet/lumos.py`),以下行號都對那份檔案。

## 問 1:分層與依賴方向

讀舊版檔案這條對齊。新增的 `read_old = _nodehome_reader(root, start)`(patch 的 `_rg_dao_changes`)走既有讀取函式,並用 `_rg_text` 讀內容。鄰居 `_rg_triggered` 也是同一寫法:`rs, rt = _nodehome_reader(root, start), _nodehome_reader(root, tip)`。

file: `scripts/lumos:47456` 是上面那個鄰居寫法。

`_rg_spans` 抽出方法與型別轉換範圍,呼叫端只有 `_rg_dao_changes` 一個,依賴方向跟鄰居一樣。

解析 diff 的舊側範圍這件事不對齊,見 F1。

## F1 `_rg_hunks` 又手寫一份舊側行範圍解析,沒用專案已有的工具
severity: major
blocking: 是 因為這是第二種做法:專案裡已有兩處在做同一件事(解析 `@@ -a,b +c,d @@` 取舊側 `(a, a+b-1)` 範圍),這支卻自己再寫一份。
引句:「a, acnt, c, cnt = (int(g) if g is not None else 1 for g in m.groups())」

- file: `scripts/lumos:62745` 的 `_lens_hunks_base_ranges` 同樣用四群組 regex,算出舊側 `(a, a + b - 1)`,並用 `b == 0` 跳過純新增。
- file: `scripts/lumos:44275` 有現成的 `_NOTELINES_HUNK_RE`,也是四群組。
- file: `scripts/lumos:44278` 的 `_notelines_parse_hunks` 是共用 `-U0` 解析器,結果同時帶舊行號與被刪行、新行號與被加行。`scripts/lumos:44626`、`scripts/lumos:46038` 等多處在用。
- `_rg_hunks` 在 `scripts/lumos:47352` 把同一條 regex 逐字再寫一次,又用 `_lens_diff_header` 自己追蹤檔頭與改名狀態。
- 這次修補新增的 `dels`(舊側刪除範圍)正是第二份舊側解析。
- 歸因:有證據的修復回歸。`_rg_hunks` 自己解析新側是修前就有的,但舊側範圍抽取是這次才加,所以重複是這次造成的。
- 這是我讀兩邊程式後的判斷,沒有實際跑過。

## 問 2:命名與錯誤處理

- 命名:`_rg_spans` 沿用 `_rg_` 前綴和「名稱 + 起行 + 迄行」元組,跟 `_rg_methods` 對齊。`dels`、`hit_old`、`read_old` 的命名跟鄰居風格一致。
- 錯誤處理:`_rg_hunks` 回 `None`、由 `_rg_dao_half` 轉成 `warns`,這條沿用原樣沒動。`_rg_text(read_old, ...) or ""` 的讀不到退路跟新版那一側一致。

## F2 計劃筆記同一行掛兩個 `[test:]`
severity: minor
blocking: 否 因為結構沒問題,只是同一條偏離紀錄的寫法跟鄰居的單一 `[test:]` 不一致。
引句:「[test: t_room_dao_whole_method_deletion_no_neighbor] [test: t_room_dao_partial_deletion_edges_required]」

- file: `docs/lumos-toolchain-knowledge/Projects/Room資料庫測試守衛_計劃.md:163-164`(patch 前)的兩條 r1 偏離紀錄,每條只掛一個 `[test:]`。
- 其他文件裡一行兩個 `[test:]` 也有先例(例如 `docs/design/2026-06-23-check-t-sentinel.md`),所以只列 minor。
- 歸因:有證據的修復回歸。

## 問 3:第二種做法

只有 F1。

`_rg_check_sources` 把 exportSchema 提醒搬到提早返回之前,是同一個 `out["warns"].append`,訊息文字沒變,沒有新做法。

其他兩處也都對齊:
- 測試放在 `t_room_...` 系列,用既有輔助函式 `_nh_repo` 和 `_rg_dao`。
- 區塊標題 `# ── 代碼審 code-room資料庫測試守衛 r2 折入(2026-10-28)──` 照 r1 那條 `scripts/test_lumos.py:117243` 的格式。

## 修補有沒有把原本對齊的地方改成不對齊

沒有。讀起點版本、`warns` 輸出方式、元組回傳的形狀都維持原樣。

## 固定席筆記

這次派工沒附固定席節點(LUMOS-LENS 寫「這次沒附固定席節點」),所以沒有可逐條判的內容。

不對齊共 2 條,其中 major 1 條
