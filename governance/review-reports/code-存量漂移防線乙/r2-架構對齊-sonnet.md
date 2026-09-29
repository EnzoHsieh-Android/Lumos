severity: minor

# 架構對齊審查(r2 修正差異,ac5c7ccf..123aaf47)

範圍:scripts/lumos 裡跟「乙:回頭條件改成機器能判的條件」有關的新碼(`_DriftProbeTree`、`_drift_probe_*`、`_drift_list`/`_DRIFT_LS_CACHE`、`_drift_disk_list`、`_probe_norm_value`、`_notelines_range_cand`/`_notelines_rows`、`_nodehome_name_status` 加 `codes` 參數)。圖譜筆記與 test_lumos.py 的改動只是跟著程式改動同步記錄與補測試,不涉及架構抉擇,略過。

## 問1:分層與依賴方向

新碼整批放在既有的 `_drift_*`/`_probe_*` 家族裡(`scripts/lumos:25816-26180` 一帶),對下只呼叫既有的共用層原語——`_nodehome_list`/`_nodehome_git`/`_nodehome_cat_blobs`(git 讀取層)、`_ns_git`/`_ns_diff`(diff 層)、`_notelines_parse_added`/`_strip_inline_markup`/`_visible_lines`(行文字層)、`_nodehome_name_status`(改名解析層),沒有看到跨層直接開 `subprocess`。對上只被 `cmd_drift_scan`/`cmd_drift_check`/`_drift_check_core`/`_drift_exam_*`/`run_doctor`/`cmd_set` 這些既有的指令層呼叫,呼叫方向跟鄰居(`_nodehome_required` 呼叫 `_nodehome_list`、`_is_code_file` 呼叫 `_nodehome_code_kind`/`_head_is_shebang`)一致,沒有反向呼叫。

`_notelines_new` 拆成 `_notelines_range_cand`/`_notelines_rows` 兩支(file: `scripts/lumos:23991-24045` 附近),新函式只被 `_notelines_new` 自己呼叫,不對外露出,跟 `_notelines_range_added` 原本「一支大函式配幾支小助手」的分法一致(比對 `_notelines_regions`/`_notelines_parse_added` 這種同檔案已有的助手函式切法)。

`_drift_probe_prepare`/`_drift_probe_changes` 改成呼叫共用的 `_nodehome_name_status(raw, codes=codes)` 拿改名對照,不再像設計稿原本寫的那樣「借 `_notelines_range_added` 的內部改名追蹤」——這正是把當初設計稿的跨層借用(`_drift_*` 伸手進 `_notelines_*` 內部細節)改成走共用底層原語,方向更乾淨。

已看,無 finding。

## 問2:命名與錯誤處理

失敗回傳:新函式全部延用「git 失敗/預算用完回 None,呼叫端 `if X is None: return`」這套(`_drift_list`、`_drift_probe_tree`、`_drift_disk_list`、`_drift_probe_changes` 都是),跟 `_nodehome_list`/`_nodehome_side` 同款。`_nodehome_name_status` 新增的 `codes=None` 在函式內部就地寫入(out-parameter),這個寫法本檔已有先例(`_rules_ids_from_json(data, out=None)`,file: `scripts/lumos:20924`),不是新樣式。

命名字首:把原本 `_ProbeTree`/`_probe_changes`/`_probe_is_candidate`/`_probe_judge`/`_probe_prepare` 這批「乙專用邏輯」都加上 `_drift_` 字首(變成 `_DriftProbeTree`/`_drift_probe_changes`…),跟純語法解析的 `_probe_parse`/`_probe_lines`/`_probe_value_err`/`_probe_norm_value` 留在 `_probe_` 字首分開——這個切法跟本檔既有「`_probe_*` 管條件語法本身、`_drift_*` 管乙這套應用邏輯」的分工一致,是好的收斂,不是不對齊。

錯誤訊息字串沿用既有句型(「判不了(git 讀不出…)」「擋下:…」),沒有新句型。

已看,無 finding。

## 問3:第二種做法

### F1 `corpus()` 的 #! 判定沒呼叫 `_head_is_shebang`,自己重寫一份

severity: minor
blocking: 否 — 兩份判定在能想到的輸入下(BOM、CRLF、非法位元組)結果一致,是結構重複、不是行為分歧,依錨定紀律第 3 點自降一級
引句:「_nodehome_code_kind(p) == "ext" or self._text[p].startswith("#!")」

1. `scripts/lumos` 既有的 `_head_is_shebang(head)` 明寫「每支檔有家與 `_is_code_file` 共用這一支——代碼審 r2 架構席:別各寫一份」(file: `scripts/lumos:6270-6271`),是這個 repo 對「開頭是不是 #!」唯一被指名要共用的判定。
2. 這份差異新寫的 `_DriftProbeTree.corpus()`(file: `scripts/lumos:25923-25931`)在把候選檔收進語料時,對沒副檔名的檔另外用 `self._text[p].startswith("#!")` 自己判一次,沒有呼叫 `_head_is_shebang`。可重現(結構重複,不是行為分歧):
   ```
   grep -n 'def _head_is_shebang' scripts/lumos
   grep -n 'self._text\[p\].startswith("#!")' scripts/lumos
   ```
   兩處各自獨立做同一件事:一份在 bytes 上做(`head[:200].split(b"\n",1)[0].startswith(b"#!")`),一份在已解碼的 str 上做(`.startswith("#!")`)。
3. 這不是"新語言、舊函式做不到"的情況——`self._text[p]` 已經是解碼過的內容,要接上 `_head_is_shebang` 只差把前 200 字元重新編碼餵進去;沒有 API 不相容的理由。判準是「鄰居已經有同功能,又自己另寫一份」,符合派工詞 Q3 例舉的「自創的 #! 判斷」。
4. 影響範圍小:因為 `#!` 只看最前面兩個字元,ASCII 在 UTF-8 下逐位元組對應,兩份判定目前不會給出不同答案,所以不會造成觀察得到的誤判——這也是把它從 major 降到 minor 的原因;但兩份邏輯以後各自被改動(例如 `_head_is_shebang` 未來要認 BOM 或限制掃描長度)時會悄悄分岔,而不會有任何機制提醒。

### F2 `_drift_probe_is_py` 的「是不是 python 檔」判定另一套寫法,沒有走既有的 `_shebang_python_blob`

severity: minor
blocking: 否 — 同樣沒有可重現的行為分歧,是否要收斂由編排者判斷(⚠)
引句:「_nodehome_code_kind(p) == "shebang?" and "python" in txt.split("\n", 1)[0].lower()」

1. 本檔既有 `_shebang_python_blob(root, base_sha, path)`(file: `scripts/lumos:31452-31454`)已經是「沒副檔名的檔要不要當 python 檔看」的判定,寫法是 `r.stdout.startswith("#!") and "python" in r.stdout.split("\n", 1)[0]`,被 `_lens_fallback` 的呼叫者格用來決定要不要對一支無副檔名的檔跑 `_lens_py_defs`(file: `scripts/lumos:31401`)。
2. 這份差異新寫的 `_drift_probe_is_py(p, txt)`(file: `scripts/lumos:25823-25824`)做的是同一件事(「這支沒副檔名的檔是不是該當 python 解析」),但另外寫了一份:少了 `startswith("#!")` 這道門檻(只要首行含 "python" 字樣就算,不要求真的是 shebang),多了 `.lower()`。
3. ⚠ 判不準:`_shebang_python_blob` 的簽名是 `(root, base_sha, path)`,每次呼叫都自己 `git show` 抓內容,不接受呼叫端已經讀好的文字;而 `_DriftProbeTree` 這裡的內容已經在 `self._text` 快取裡,要接上舊函式得先改舊函式的簽名(接受可選的已讀內容),不是單純呼叫就能解決——這跟 F1(單純沒接既有函式)不同,有一定的 API 不相容理由,所以標 minor 而非直接判 major,實際要不要收斂交編排者裁。

### F3 `_DRIFT_LS_CACHE` 用「滿 8 筆就整包清掉」,跟本檔其它 6 支模組層快取的「行程內不設上限」不同

severity: minor
blocking: 否 — 是新的快取行為變體,不是新的快取機制;有合理的成因(見下)
引句:「if len(_DRIFT_LS_CACHE) >= 8:」

1. 本檔既有模組層快取都是「行程內、不設上限、一次寫入不淘汰」:`_GIT_DATES_CACHE`(file: `scripts/lumos:29701`)、`_BASENAME_COUNTS_CACHE`/`_REPO_FILES_CACHE`(file: `scripts/lumos:29743-29744`)、`_ABOUT_COUNTS_CACHE`/`_HOME_MAP_CACHE`(file: `scripts/lumos:30050,30069`)、`_NODE_FLAVOR_CACHE`(file: `scripts/lumos:20454`)都沒有大小上限或淘汰邏輯。
2. 這份差異新寫的 `_DRIFT_LS_CACHE`(file: `scripts/lumos:25872-25887`)加了「滿 8 筆整包清空」的淘汰:
   ```
   grep -n '_DRIFT_LS_CACHE' scripts/lumos
   ```
   `_drift_list` 用這個快取記「同一個提交的樹在一次 check 裡只列一次」,key 是 `(root, 完整 40 字提交編號)`。
3. 這不是「引入第二種快取機制」(還是同一種「模組層 dict、lazy 填、行程內存活」的形狀,只是多了一個 `len()>=8` 的清空判斷),但的確是本檔第一個帶淘汰邏輯的模組層快取,判準比較模糊,所以標 minor 而不是 major。成因合理:既有那批快取的 key 是 repo_root/vault(一次 CLI 呼叫裡種類有限,天然有界),`_DRIFT_LS_CACHE` 的 key 是提交 sha,而 `lumos drift exam --history 100` 這種歷史重放一次會走過上百個不同提交(計劃〈做法〉第 3 節門檻②),不設上限會讓這個快取隨提交數線性長,加界是有理由的,只是選了跟鄰居不同的做法(其他快取遇到這種情境時,是把 key 縮小到 repo_root 範圍而不是加淘汰——但那幾支本來就沒有「同一個 repo 內還要分版本」的需求,不算直接可比的先例)。

不對齊共 3 條,其中 major 0 條。

最嚴重等級為 minor,blocking 共 0 條。
