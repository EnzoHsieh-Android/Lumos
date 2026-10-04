severity: minor

## Z1 prefetch_paths 重複了 prefetch 的最後一行
severity: minor
blocking: 否
引句:「self._read(sorted(p for p in paths if p in self.files))」
file: `scripts/lumos:32694`

`_DriftProbeTree.prefetch`(scripts/lumos:32550-32555)已經有一模一樣的收尾 `self._read(sorted(p for p in paths if p in self.files))`(32553),前面只是先從條件算出路徑集合。新的 `prefetch_paths` 是同一個動作的第二份寫法,不是第二套機制:兩支都是「樹上有的路徑一批讀進 _text」。結構方向對(沒有跨層),但 `prefetch` 可以改成算完路徑後呼叫 `prefetch_paths`,避免兩處各自維護「過濾樹上有的、排序、批次讀」這件事。上一輪把 `text_of(*paths)` 的多載拆開本身是對的,這條只是順手收斂。

## Z2 _count_eval 解析失敗的例外清單比既有 ast 解析少 MemoryError
severity: minor
blocking: 否
引句:「except (SyntaxError, ValueError, RecursionError):」
file: `scripts/lumos:33191`

同檔既有的 ast 解析 `_drift_py_names`(scripts/lumos:32308)接的是 `(SyntaxError, ValueError, MemoryError, RecursionError)`,並附註解說明巢狀很深的合法檔 CPython 解析器丟 MemoryError、不接會讓整支 scan 當掉(代碼審 r2 邊界席)。`_count_eval` 對同一類檔(drift scan 同一棵樹讀出來的 Python 檔)做同一件事卻少接一個,錯誤處理不一致,也會重現當初那個坑。另一處 5541 同樣沒接 MemoryError,但那不是 drift 這一層,不拿來當對照。

## 三問總答

1. 分層與依賴方向:對齊。`_count_*` 求值函式在 drift 區段內、放在 `_drift_probe_scan` 之後(33058 起),`_drift_count_scan` 讀檔走 `_DriftProbeTree`(同回頭條件那棵樹、同預算),`_drift_fix_count` 用 `_drift_probe_tree(root, "disk")` 取樹(scripts/lumos:34303 一帶),doctor Z 段只呼叫 `_count_lines` 數標籤、不讀程式檔(同 `_probe_lines` 的先例,scripts/lumos:35800 一帶)。沒有往上層或別的家直呼。`_count_parse` 改回 `errs` 清單後形狀同 `_probe_parse`(scripts/lumos:32205),`_drift_count_scan` 與 doctor 取用方式(`pr["errs"]`)與回頭條件那邊一致。
2. 命名與錯誤處理:除 Z2 外對齊。`_count_*` 前綴自成一族、與 `_drift_*`/`_probe_*` 並存,跟 `_retire_lines` 這類另起前綴的先例同類。`text_of(path)` 的回傳語意(不在樹上、讀不了、讀不出一律 None)與 `_read` 的 False/None 記法一致。`import ast` 區域匯入在檔內與 `import ast as _ast` 各 5 處並存,不算新做法。
3. 第二種做法:
   - `_count_mutated` 的 ast 走訪:跟 `_drift_py_names`(32314)同一路,都是 `ast.walk(tree)` 單趟、逐節點 isinstance 分流,沒有另寫 NodeVisitor 或正則;不是第二種做法。
   - `_DRIFT_FIX_SELF_JUDGED`:跟 `_DRIFT_BOUND_KINDS`(31608)同形,都是頂層種類 tuple、以 `kind in …` 取用、行尾或上一行註解講用途;放置位置在 `_DRIFT_FIX_KINDS` 旁、與同系列常數相鄰。對齊。載入函式裡原有的 `kind != "c4"` 字串特例(34xxx,既有)沒被一併收進常數表,但那是既有程式碼、不在本 diff。
   - `prefetch_paths` 與 `prefetch`:見 Z1,是同一動作的重複收尾,不是兩條不同的讀取路徑,列 minor。

總結:不對齊共 2 條,其中 major 0 條;最高等級 minor
