severity: minor

**第四輪通才席核對**
- F1(大小寫經連結仍叫人先提交)修好了。我在臨時 repo 實跑 `DOCS/LNK`、`LND/a.py`、`lnd/A.PY`、`Sub/TL`、`LND`、`.GIT/config`,都不再叫人先提交。
  - 其中 `LND` 這條走的是「經過符號連結、解析不到」。
  - `.GIT/config` 不附原因。
- F2(家節點 WHY 還寫舊行為)修好了:`Systems/規格閘.md` 第 62 行已改成現況。
- F4(`_plan_tree` 控制流)修好了:三種快取狀態拆清楚,測試裡的死分支也拿掉了。
- F3 放行理由大致成立。理由是偏差方向多擋,少擋的寫法要刻意偽造。這條偏離也已寫進計劃的偏離列。
- 在 `plan-sources-required` 工作樹跑 `python3.14 scripts/test_lumos.py -k psrc`,250 條全過。
- 我另外對 20 萬組隨機字串(混 CR、LF、CRLF、`\x0b`、`\x85`、`\u2028`)比對新的只計數版和舊的建行清單版。str 與 bytes 的結果都一致,沒有差異。
- 另外實跑了含空格的連結名、連結名裡帶 `12` 的批次輸出解析,都正常。
- 沒找到會讓閘做出錯誤放行或擋下的行為,下面都是 minor。

**F1 檔名大小寫其實已經對,擋下訊息卻說大小寫不同**
引句:「hit = _plan_tree_resolve(head, tree, path, fold=True)」
severity: minor
blocking: 否
- 輸入→實際:臨時 repo 已提交連結 `Sub/tl -> Target.py`,版控裡真正的檔是 `Sub/target.py`。macOS 上這種連結本機可用,別處讀不到。
  - 出處寫 `Sub/tl`(跟版控一字不差),被擋,訊息是「大小寫跟版控不同(這條路徑經過符號連結,版控裡解析到 `Sub/target.py`;要照版控的寫法)」。
- 預期:跟 r3 一樣講「經過符號連結,解析不到」,或講連結目標的大小寫不對。
- 原因:`fold=True` 對連結讀出來的目標也不分大小寫,成功後 `hit` 就被當成作者寫錯大小寫。
- 代價:作者拿自己寫的路徑去對版控,發現一樣,卻被叫「照版控的寫法」,找不到哪裡錯。
- 更簡單的做法:`hit[0]` 跟 `path` 逐字相同時(錯在連結目標)改講連結目標大小寫不符,或沿用舊的「解析不到」訊息。

**F2 行數出現第二份算法,計劃的決策列沒跟著改**
引句:「def _repo_ref_source_line_count(text):」
severity: minor
blocking: 否
- 計劃筆記第 112 行仍寫「行號與行數只有一份算法:`_repo_ref_source_lines` 算行數…兩邊各寫一份、只靠註解說一致,日後一改就分岔」。
- 現在 `_plan_blob` 用 `_repo_ref_source_line_count`,`_validate_repo_ref` 用 `_repo_ref_source_lines`,是第二份實作,等於 r3 架構對齊席 F2 剛拿掉的重複。
- 代價:語意目前一致(我 20 萬組隨機比對沒差異),靠 `t_psrc_blob_crlf_count` 的 14 個樣本守;筆記卻明寫只有一份,下一個讀的人會被誤導。
- 做法:把第 112 行改成現況(兩支同語意、由測試守)。或讓 `_repo_ref_source_lines` 的 str 版直接呼叫計數版。

**F3 這輪新增的機制沒補進計劃〈依據來源〉表**
引句:「r4 起讀取走既有的 _nodehome_cat_blobs_capped、上限沿用 _NOTE_REREAD_FP_MAX」
severity: minor
blocking: 否
- 本案要求每個機制的依據補回計劃(計劃筆記引了使用者 2026-11-06 的原話)。
- 這輪 patch 在計劃表只改了「行內註解不跨行」那一列。
- 用 `grep` 查計劃筆記,`NUL`、`_nodehome_cat_blobs_capped`、`source_line_count`、`fold`、`不分大小寫` 全部 0 筆。
- 漏掉的有:路徑含 NUL 先擋、os 呼叫接 ValueError、`.git` 不分大小寫、擋下原因的大小寫比對涵蓋連結、讀 blob 改走有上限的批次讀取、只計數的行數。
- r4 收貨紀錄〈先查世界〉已經查到 Python 官方文件和專案既有函式,只是沒寫回計劃。
- 代價:這些機制的依據只在卷證裡,日後迭代的人在計劃找不到。

**F4 每個 `:行號` 的檔多開一次 git,耗時約兩倍**
引句:「got = _nodehome_cat_blobs_capped(root, [spec], _NOTE_REREAD_FP_MAX, timeout=_disp_git_timeout())」
severity: minor
blocking: 否
- 現在每支不同的檔先跑一次 `cat-file --batch-check` 問大小,再跑一次 `cat-file --batch` 讀內容。
- 實測 150 支內容不同的檔各帶 `:2`:新 4.97 秒,舊的單次 `cat-file blob` 2.51 秒。
- 這就是三支計 git 次數的測試從 4 放寬到 5 或 6 的原因。
- 代價:規格閘、推送前、健檢三處共用,引用很多支檔的計劃會明顯變慢。
- 更便宜的做法:同一份計劃要驗的 oid 先收集起來,問一次大小、讀一次內容。

**F5 每次擋下都重建整棵樹的小寫索引**
引句:「fl.setdefault(p.lower(), p)    # files 照 git 列樹的順序,同名取先列到的」
severity: minor
blocking: 否
- `_plan_tree_resolve(fold=True)` 每次呼叫都對全部檔案重做 `lower()` 加字典(`nl`、`fl`),`_plan_src_miss_reason` 還另外對非一般檔做一份 `low`。
- 實測合成 10 萬檔的樹、100 個不存在的路徑:1.18 秒,舊的單次線性掃描 0.51 秒,每個被擋的路徑約 12 毫秒。
- 這個索引跟樹一對一,可以跟著 `_PLAN_TREE_CACHE` 算一次。
- 代價:不大,只在計劃有很多不合格路徑、而且 repo 很大時才顯現。

總結:最嚴重是 minor(F1 連結目標大小寫錯時擋下訊息誤導作者、F2 行數出現第二份算法而筆記仍寫只有一份、F3 新機制的依據沒補回計劃),沒有會做出錯行為的問題,會擋 0 條。

臨時目錄 `/private/tmp/lumos-seat-work/code-計劃依據來源必填/通才-sonnet` 已刪。鎖檔 `.warming` 檢查時不存在,我沒有動它。沒有修改 repo。
