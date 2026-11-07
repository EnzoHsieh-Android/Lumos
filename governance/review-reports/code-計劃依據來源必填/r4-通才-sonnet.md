severity: minor

**第三輪通才席 F1–F5 核對**:五條都修好了,各項都在臨時 repo 實跑過。
- F1:首次加入日改成分範圍。實跑 `Projects/a_調研.md`、`Systems/s.md` 在 note 範圍都回 2026-11-07,plan 範圍只有 `b_計劃.md`。改名鏈 `a_調研.md` 到 `Systems/a2.md` 的日期也接得上。
- F2:去註解改成線性時間。單行 20 萬個 `<!--`、20 萬行各有一個沒閉合的 `<!--`,都在 0.5 秒內跑完。
- F3:行內註解不再跨行,表格列與清單項原樣保留。
- F4:行號改走 `_repo_ref_line_span`,5000 位數字回 False 並講行號,不再丟 `ValueError`。
- F5:快取只存非一般檔(符號連結、子模組)路徑集合,樹清單改用 `_drift_oids`。

另外我實跑了符號連結、子模組、大小寫、空檔、沒有結尾換行、CR 等路徑與行號的邊界,沒有找到會判錯的路徑。以下是新找到的問題,都不是會做出錯行為的類型。

**F1 大小寫寫錯、又經過已提交的符號連結時,擋下訊息還是叫人「先提交」**
引句:「        return "工作目錄有、HEAD 還沒有——還沒提交,先提交再跑"」
severity: minor
blocking: 否
- 輸入→實際:臨時 repo 已提交 `lnd -> a` 與 `ln -> a/b.py`。
  - 出處寫 `Lnd/b.py`、`LN`、`Ln2`、`LND/B.py`,全部回 False,訊息都是「工作目錄有、HEAD 還沒有——還沒提交,先提交再跑」。
  - 預期:講大小寫與版控不同。
  - 同樣的錯誤也出現在 `.GIT/config`:macOS 上 `.GIT` 就是 `.git`,`parts[0] == ".git"` 認不出,結果叫人去提交 `.git` 底下的檔。
- 原因:`_plan_src_miss_reason` 的③只掃 `files`(一般檔)。連結本身與經過連結的路徑不在 `files` 裡,④的 `realpath` 在 macOS 又找得到,於是掉到⑤。
- 代價:這正是 r3 要修的「照做之後同一句再出現」。修補宣稱涵蓋大小寫,但漏了連結路徑。
- 更簡單的做法:③掃 `files` 加 `nonreg`,或逐段比對。`.git` 的判斷改用 `parts[0].lower()`。

**F2 家節點 `Systems/規格閘.md` 的 WHY 還寫著這輪拿掉的行為**
引句:「行中的要後面同一段真有 --> 才算」
severity: minor
blocking: 否
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:62`
- 這行同時還寫「`_plan_tree`:一次 git ls-tree -r -z --full-tree,程序內快取」和「最後不是 blob 不算」。
- 現在的程式碼是:行內註解只在同一行判、樹清單走 `_drift_list`、最後要落在一般檔。這輪只改了該節點的首次加入日那條 WHY。
- 代價:下一個讀者會以為行內註解還會往後面幾行找閉合。這個「同一段」判準已被連續兩輪打穿,正是這輪特意拿掉的。

**F3 行首區塊註解在清單項、縮排 2–3 格時,沒閉合會蓋到檔尾,但真正的渲染不會**
引句:「_PLAN_SRC_HTML_BLOCK_RE = re.compile(r" {0,3}<!--")」
severity: minor
blocking: 否
- 輸入:`"- 說明\n  <!-- 備註沒收\n\n## 依據來源\n| 機制 | 依據 | 出處 |\n..."`
- 實際:`_plan_sources_uncomment` 把後面全部換空,規格閘會報「沒有〈依據來源〉這一節」。
- 預期:CommonMark 裡這個 HTML 區塊屬於清單項。未縮排的 `## 依據來源` 會關掉清單項,區塊也隨之結束,所以渲染出來看得到那一節。
- 代價:新計劃被誤擋,作者要補 `-->` 才過。因為是偏向多擋、且機率低,所以只算 minor。
- 做法:區塊開頭只認真正在頂層的行,也就是前一行不是清單項內縮排。或在計劃〈依據來源〉的偏離條目裡補一句承認這個偏離。

**F4 `_plan_tree` 的控制流難讀,測試裡還留著舊形狀的死分支**
引句:「lst = _drift_list(root, sha) if _PLAN_TREE_CACHE.get(key, ()) is not None else None」
severity: minor
blocking: 否
- 一行裡混了三種快取狀態:沒查過、查過失敗、查過成功。後面又重複判兩次 `key not in _PLAN_TREE_CACHE`。
- 測試 `t_psrc_tree_shared_drift` 有 `keys = set(tree[0]) if isinstance(tree, tuple) else {...v[1] == "blob"...}`,else 是舊 dict 形狀,現在永遠走不到。
- 代價:下次改這段容易判錯。
- 更簡單的做法:先 `if _PLAN_TREE_CACHE.get(key, 0) is None: return None`,查到清單才快取。測試直接取 `tree[0]`。

總結:最嚴重是 minor(F1 大小寫或 `.GIT` 經過連結時仍叫人先提交、F2 家節點 WHY 與程式不符),沒有會做出錯行為的問題,會擋 0 條。

臨時目錄 `/private/tmp/lumos-seat-work/code-計劃依據來源必填/通才-sonnet` 已刪;鎖檔 `…bef592….json.warming` 檢查時不存在,我沒有動它;沒有修改 repo。
