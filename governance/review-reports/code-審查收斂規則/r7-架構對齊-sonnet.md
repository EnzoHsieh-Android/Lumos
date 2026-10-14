severity: minor

severity: minor
blocking: 否 — 現有讀者不帶 `bare` 行為不變,屬形狀偏好而非第二種做法;但再有第二個旗標就該收斂成一個具名函式
引句:「def _vault_slug_of(path, bare=False):」
對照:`scripts/lumos:44354` 與 `scripts/lumos:44368` 兩處既有讀者呼叫 `_vault_slug_of(nfc(f))`,不帶旗標,只認 `docs/<名>-knowledge`。`scripts/lumos:26351` 的 `_vault_in` 才是認 `docs/knowledge` 的另一條路。
判定理由:殘留分級要認 `docs/knowledge/`,作法是在共用函式上加一個改變回傳語意的布林。多的那種佈局沒有另寫一套判定,這點比 r6 之前的另寫小段好。`bare` 會回 "knowledge",跟其他讀者拿回傳值拼 `docs/<slug>` 的前提不同,docstring 已講明不給既有讀者用。`bare` 這個名字也跟 `scripts/lumos:28572` 的「bare=不含 / 的裸 token」同名異義,容易讀錯。目前只有一個旗標,還不算旗標累積。

severity: minor
blocking: 否 — 走的是同層既有的 `_lens_git`,沒有跨層直呼;只是整樹列路徑這件事在檔內已有多份各自解析
引句:「r = _lens_git(repo_root, "ls-tree", "-r", "-z", "--name-only", "--full-tree", rev, binary=True, timeout=t) if t >= 1 else None」
對照:同層 `scripts/lumos:35203` 的 `_lens_git(self.root, "ls-tree", "-r", "-z", self.tip, ...)` 與 `scripts/lumos:50262` 的 `_lens_git(root, "ls-tree", "-r", base_sha, quote=True)`。另有 `scripts/lumos:31556` 的 `_nodehome_git(... "ls-tree","-r","-z","--full-tree", where)`,那是節點家那一層,不是同一層。
判定理由:有走既有的 `_lens_git`,逾時、binary、NFC 處理也跟鄰居一致,也沒有跳去呼叫節點家層的 helper。檔內沒有「列整棵樹的路徑集合」的共用函式,這是第三份各自解析的 `ls-tree -r`(`:35203`、`:50262`、`:44677`)。目前三份用途不同(子模組、模式表、路徑集合),不到引入第二種做法的程度。再多一份就該抽出來。

severity: minor
blocking: 否 — 同一欄位值型別混用,但讀端和比對端都已處理,不會產生行為分叉
引句:「val = lambda v: v if isinstance(v, str) else _j.dumps(v, ensure_ascii=False, sort_keys=True)」
對照:`scripts/lumos:19169` 起 `_residual_index_entries` 的 `notes = {殘留指標: 路徑字串}`,其他欄(node、fp、residuals、about_code、test_files)都是單一型別。`scripts/lumos:44657` 的 `_residual_index_notes` 讀端要分字串、`dict`、缺欄三種情況。
判定理由:`unresolved` 用 `{"unresolved": 原因}` 這種字典塞進原本只放字串的 `notes` 欄,索引其他欄沒有這種混型。作法是在原欄位上加一種形狀,不是另開欄位。比對鍵(`_residual_index_row_key`)和讀端(`_residual_index_notes`)兩處都補了分支,沒有漏掉的讀者。要我選,獨立一欄會比混型乾淨,但這裡是偏好,不是引入第二種做法。

鏡頭排序級(`keyed` 值多一格 rank、`want` 取 `min`)沿用 r5 已有的排序級寫法,只是從兩值元組擴成三值,所有讀寫點都同步改了,沒有新舊兩種形狀並存。入口清 git 環境那段四個分支逐字同一段,是既定裁定,我不列。

最高等級 minor,blocking 0 條。
