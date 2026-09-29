severity: minor

## 問一 分層與依賴方向
新碼放的位置與呼叫方向跟鄰居大致一致:_drift_decode、_drift_cat_nfc、_DriftProbeTree、_drift_probe_candidates 都接在 _drift_list 之後的存量漂移區塊,往下呼叫 _nodehome_cat_blobs、_head_is_shebang 這類共用底層,沒有反向呼叫;_NotelinesNet 緊鄰 _notelines_range_cand,是它唯一的建構者。沒有跨層直呼的 major。
只有一處放位置不順,列 F1。

## F1 首行 #! 判定的兩個共用件分在檔案兩端,存量漂移區塊往下呼叫派工鏡頭區
severity: minor
blocking: 否 — 結構方向對,只是共用件放的位置與既有那支不同處
引句:「+def _shebang_line_is_python(first_line):」
file: `scripts/lumos:6270`(_head_is_shebang,bytes 版,每支檔有家區)
file: `scripts/lumos:25845`(_drift_probe_is_py 呼叫 _shebang_line_is_python)
file: `scripts/lumos:31565`(_shebang_line_is_python 定義在派工鏡頭區)
1. 同一件事「首行是不是 #!」現在有兩支共用件:_head_is_shebang(6270,吃 bytes)與 _shebang_line_is_python(31565,吃 str)。前者已在每支檔有家區與 _is_code_file 共用,後者卻放在 _shebang_python_blob 旁的派工鏡頭區,存量漂移區塊(25845)得往檔尾方向呼叫。
2. 副作用:語料判定得把 str 轉成 bytes 才能呼叫前者(引句見 F1 之外的 corpus 改動「_head_is_shebang(self._text[p][:200].encode("utf-8"))」),別處鄰居都是拿到 bytes 才呼叫它。
3. 對照鄰居:_head_is_shebang 的註解自己寫「別各寫一份」,新增一支放在另一區就是各放各的。

## 問二 命名與錯誤處理

## F2 _NotelinesNet 用 failed 旗標、事後由呼叫端檢查,跟同檔「失敗回 None」的做法不同
severity: minor
blocking: 否 — 結構(延遲計算)與既有 _NodehomeSide 的「需要時才讀」同類,只有失敗傳遞方式不同
引句:「+    if net is not None and net.failed:」
file: `scripts/lumos:22887`(_nodehome_side:讀不出直接回 None)
file: `scripts/lumos:26054`(_drift_probe_one/_DriftProbeTree.one:None=判不了)
1. 鄰居(_nodehome_side、_DriftProbeTree.one、_drift_probe_line)都用「函式回 None 表示失敗」;_NotelinesNet.lines 失敗時回空集合、另記 self.failed,要等 _notelines_new 迴圈跑完才回頭看旗標。
2. 迴圈內第一次失敗後,後續每篇筆記的 net() 仍照常回 ()(_m={} ),中途會照舊往下算 _notelines_rows,只是最後整批丟掉;鄰居是當場短路。
3. 這是刻意為了讓 lambda 傳進 _notelines_rows 不必改簽名;仍屬「第二種失敗編碼」。⚠ 若編排者認為 lambda 介面下只能這樣,可降為不列。

## F3 prefetch 的呼叫方式 check 與 scan 不對稱
severity: minor
blocking: 否 — 只是包一層與不包一層的差別
引句:「+def _drift_probe_prefetch(conds, trees):」
引句:「+        tree.prefetch([c for _p, rows in per for _n, _t, pr in rows for c in pr["conds"]])」
file: `scripts/lumos:26145`(check 經 _drift_probe_prefetch 迴圈各版)
file: `scripts/lumos:26276`(scan 直接呼叫 tree.prefetch)
1. check 端先包一支只做「跳過 None 樹再呼叫 t.prefetch」的模組層函式,scan 端則自己判 tree is not None 後直呼。同一個動作兩種寫法。
2. 該包裝函式只有一個呼叫者,命名(_drift_probe_prefetch)又跟方法 prefetch 同名不同層,讀者容易當成兩套機制。

## 問三 第二種做法

## F4 NFD 重讀是為「樹清單已 NFC」自創的補救,鄰居的做法是保留 git 原樣路徑
severity: minor
blocking: 否 — ⚠ 鄰居本身沒有「列樹後批次讀」的原樣路徑版本(_nodehome_list 只回 NFC),判不準是第二種做法還是唯一可行解,交編排者
引句:「+    retry = [i for i, b in enumerate(blobs) if b is None and unicodedata.normalize("NFD", paths[i]) != paths[i]]」
file: `scripts/lumos:23024`(_nodehome_name_status 的 norm=False:「要拿去 git 查的呼叫端用」)
file: `scripts/lumos:23889`(_notelines_range_added:「鍵用 NFC、拿去 git 查的一律用原樣路徑」)
file: `scripts/lumos:22787`(_nodehome_list 一律 nfc(os.fsdecode(p)))
1. 專案既有做法:要拿去 git 讀的路徑保留原樣、只有比對用的鍵才 NFC(驗收輪明文定案)。
2. 這份差異在 _drift_cat_nfc 走反方向:先接受 NFC 路徑,讀到 None 再猜「轉 NFD 重讀」,多開一個行程。它只覆蓋整串 NFD,對「部分組合字元」的混合形式讀不到。
3. 若判定要對齊既有做法,應讓 _drift_list 這一層回原樣路徑對照(NFC→原樣),而非在讀取端猜。因 _nodehome_list 本來就沒有該對照,這一步要改共用件,超出本輪,所以只標 ⚠。

## F5 延遲計算有兩種新寫法並存
severity: minor
blocking: 否 — 兩者都對,鄰居也有類別式(_NodehomeSide 的 shebang 需要時才讀)
引句:「+    memo, base_lines, todo, unknown = {}, {}, [], []」
引句:「+class _NotelinesNet:」
file: `scripts/lumos:22762`(_NodehomeSide:類別內的延遲讀)
file: `scripts/lumos:26167`(_drift_probe_candidates 內 memo 字典閉包)
1. 同一份差異裡,一處用 {"v": ...} 閉包字典做一次性延遲(_tip_text),一處用新類別加 failed 旗標(_NotelinesNet),另一處(_DriftProbeTree._read)用 self._text 字典。鄰居的既有寫法是類別欄位或模組層快取(_DRIFT_LS_CACHE、_NODE_FLAVOR_CACHE)。
2. 閉包字典的 "v" 鍵沒有既有同名寫法,grep 全檔 memo 只有這一處。

## 其他已看,無 finding
- _drift_decode:只是 utf-8-sig 加 errors="replace",跟 _nodehome_parse_note 的解碼寫法一致(全庫 utf-8-sig)。與 _drift_tree_env 的嚴格解碼並存是因為用途不同(筆記讀不出要記成讀不出,程式檔換字元照判),不算第二種做法。
- _drift_probe_cond_candidate / _drift_probe_is_candidate 的 True/False/None 三態跟 _drift_probe_one、_drift_probe_line 一致。
- 提示訊息(--budget 擋下、drift ack 一種一行、_drift_probe_path_warn 的括號提示)寫法跟同檔「擋下:…」「(代碼審 rN …)」註解慣例一致。

不對齊共 5 條,其中 major 0 條
最高 minor,blocking 共 0 條
