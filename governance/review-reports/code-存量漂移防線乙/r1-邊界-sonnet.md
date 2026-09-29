severity: major

## F1 when-file/when-symbol/when-test 的路徑值沒有 NFC 正規化,中文/組合字元路徑會靜默判成「條件不成立」且不留任何痕跡

severity: major
blocking: 是 — 整支乙機制對這個 repo(圖譜與程式碼路徑常含中文、macOS 上常見組合字元)最主要的服務對象會系統性失效:條件永遠評不成立、scan 不報任何 problem、doctor 不會唸,連「期限保底」都救不回來(因為 by 到期時 E5 只唸「到期了」,不會告訴作者路徑打錯,跟拼錯名字是同一種盲區,但這裡是工具自己造成的正規化落差,不是作者手誤)。

引句:「return v in self.files」

file: `scripts/lumos:25821`(`_ProbeTree.one` 的 `k == "file"` 分支)
file: `scripts/lumos:25890`(`_probe_is_candidate` 的 `k == "file"` 分支:`if k == "file" and v in ch["touched"]:`)
file: `scripts/lumos:25895`(`_probe_is_candidate` 的 `symbol`/`test` 路徑分支:`if path.strip() in ch["touched"]:`)
file: `scripts/lumos:25833`(`_ProbeTree.one` 的 `symbol`/`test` 分支:`items = [(path, corpus.get(path))] if path else list(corpus.items())`)

1. `_nodehome_list`(`scripts/lumos:22786` 起)回傳的路徑一律 `path = nfc(os.fsdecode(p))`,所以 `_ProbeTree.files`(`self.files = set(lst[0])`)與 `_probe_changes` 算出的 `ch["touched"]`(`touched.update(ps)`,`ps` 來自 `nfc(toks[i+1])`,見 `scripts/lumos:25849` 一帶)★都是 NFC 正規化過的路徑集合★。
2. 但 `when-file:<值>`、`when-symbol:<路徑>::<名稱>`、`when-test:<路徑>::<名稱>` 裡的**路徑值**,從 `_probe_parse`(`_PROBE_TOKEN_RE` 抓 `m.group(2).strip()`)到 `_ProbeTree.one`、`_probe_is_candidate`,全程沒有任何一處呼叫 `nfc()`。全庫其他每一處路徑比對(`_notelines_range_added`、`_nodehome_changed_vs_disk`……)都刻意 `nfc()` 過再比,這裡是唯一漏掉的。
3. 結果:筆記裡如果用 macOS 常見輸入(Finder 拖曳、部分中文輸入法、剪貼板)貼出來的 NFD 形式路徑寫 `when-file:`,即使那支檔案在 git 裡是 NFC 存的且確實存在,`v in self.files`(比對)與 `v in ch["touched"]`(候選篩選)都會判 False——條件永遠評不成立,而且不是「判不了」(None),是確定的「不成立」。
4. 更嚴重的是 `_drift_probe_scan` 的 problem 偵測(`scripts/lumos:26160` 一帶 `_drift_probe_scan`)只在「`file` 指到資料夾」時才把 `when-file` 列成問題,對「單純比對不到、但也不是資料夾前綴」的情況完全不列 problem——這正是 NFC/NFD 落差會落入的分支:整條回頭條件會安靜地永遠評不成立,scan、doctor Z 段都不會多印一個字,只能等 `[by:]` 到期讓 E5 唸「到期了」,而且唸出來的字面看不出是正規化問題,作者八成以為是自己拼錯路徑去重打一次同樣打成 NFD 又踩一次。

重現(在真代碼 clone-ns 上直接跑,兩組對照,唯一差異是 `when-file:` 的值用 NFC 還是 NFD 打同一個檔名 `café.py`,檔案本身用同一份 NFC 位元組建立、git 存的也確定是 NFC——用 `git ls-tree` 驗過):

```
$ python3 clone-ns/scripts/lumos --vault "$ROOT_NFD/docs/kg-knowledge" drift scan --json
{
 "at": "工作目錄", "vault": "docs/kg-knowledge",
 "unknown": [], "problems": [], "findings": []
}
```

同一支檔案、同一個真實存在的路徑,`when-file:` 只是換成 NFD 打法,`findings` 就從「已成立」變空、`problems` 也是空(完全靜默):

```
$ python3 clone-ns/scripts/lumos --vault "$ROOT_NFC/docs/kg-knowledge" drift scan --json
{
 "at": "工作目錄", "vault": "docs/kg-knowledge",
 "unknown": [], "problems": [],
 "findings": [
  {"kind": "probe", "path": "Systems/A.md", "line": 16,
   "text": "REVISIT:[when-file:café.py][by:2099-01-01] 用 NFC 打的路徑(控制組)",
   "why": "條件已經成立,該處理了(期限 2099-01-01)", "acked": false}
 ]
}
```

兩個 repo 除了 `when-file:` 的值分別是 `unicodedata.normalize("NFC","café.py")` 與 `normalize("NFD","café.py")` 之外完全一致(檔案內容、frontmatter、期限都相同),`git ls-tree` 驗過兩邊的實際檔案路徑 bytes 都是 NFC(`caf\xc3\xa9.py`)。`_probe_is_candidate` 那條候選路徑同樣會踩到,因為它比對的也是同一份未正規化的 `v` 對 nfc 過的 `ch["touched"]`——`check`(推送閘)一樣會漏擋,不只 `scan` 漏列。

修法方向:`_probe_parse` 解析出 `file`/`symbol`/`test` 的路徑段時就地 `nfc()`(跟 `_nodehome_list`/`_probe_changes` 對齊),或在 `_ProbeTree.one`、`_probe_is_candidate` 兩處比對前各自 nfc 一次。

## F2 `_ProbeTree` 的 `where=None` 分支是死碼,跟自己的 docstring 承諾的「三種模式」對不上

severity: minor
blocking: 否 — 目前沒有任何呼叫點會走到這個分支,不會造成現在任何一條路徑翻紅,純粹是文件與可達性不一致,屬於抑噪紀律裡「未定義/內部不一致一律要報」那條,不是功能性錯誤。

引句:「在某一版(提交的樹、工作目錄 'disk'、或空的 None)上判條件」

file: `scripts/lumos:25777`(class docstring)
file: `scripts/lumos:25784`-`25785`(`if where is None: self.ok, self.files, self.layout = True, set(), ({}, {})`)

`_ProbeTree.__init__` 明寫支援 `where=None` 這個模式(docstring 說「或空的 None」),而且刻意讓 `where is None` 時 `self.ok=True`、`self.files=set()`——也就是把「沒有這個版本」判成「確定 False(檔案都不存在)」而不是「判不了」。但全庫目前只有三個呼叫點:

```
$ grep -n '_ProbeTree(' scripts/lumos
25918:    tip_ctx = _ProbeTree(root, tip, tenv, deadline)
25919:    base_ctx = _ProbeTree(root, base, benv, deadline) if base else None
26227:    pfound, probs = _drift_probe_scan(tenv, _ProbeTree(root, sha or "disk", tenv))
```

`tip` 永遠是已解析的 sha;`base` 為假時走的是 `else None`(整個 `base_ctx` 變數本身是 Python 的 `None`,不是 `_ProbeTree(..., where=None)` 的實例);`scan` 用 `sha or "disk"`,`sha` 為空時落的是 `"disk"` 不是 `None`。三個呼叫點都繞開了 `where=None`——這個分支現在進不去。不是「無害」,是「文件承諾了一個沒人走過的行為」:未來如果有人真的傳 `where=None` 想表達「這個版本不存在,判不了」,拿到的其實是「所有 file 條件一律 False」而不是 None(判不了),跟計劃裡「判不了要算要處理,不能放行」([S2] 的既有裁決)的精神反著來——這條線一旦被接上會是靜默的錯誤方向,值得在合併前把 docstring 改成只講兩種模式,或者把這個分支改成回 `self.ok=False`(判不了)以防後續真的被接上。

## 已看,無 finding 的部分

- REVISIT 標記文法的多種怪寫法(`[by:]` 放在條件標記前面單獨出現 → 正確判成 `bad`;`[by:]` 夾在兩個條件中間 → `_probe_parse` 不管順序照樣吃到;同一行兩個 `[by:]` → 第二個算 `errs`、第一個值保留,不會 crash)三個都在 clone-ns 上直接呼叫 `_revisit_split`/`_probe_parse` 驗證過,行為跟計劃〈做法〉第 0 節「`REVISIT:` 後面(去掉空白)若以 `[when-` 開頭才算條件式」的文字定義完全一致,不是漏洞。
- 條件標記值含空白、含 `=`、含 `|`(僅 `when-status` 的語意用到 `=`/`|` 分隔,其餘鍵只是值裡出現這些字元)都照 `[^\]\n]*` 收進去,不會截斷或誤切。
- CRLF 筆記:`_revisit_split` 內部先 `line.strip()` 才判斷開頭與切詞,行尾 `\r` 會被一起吃掉,直接測過帶 `\r` 的字串,分類結果正常(`('cond', ...)`),不受影響。
- 表格行判定:`_probe_lines`/`_ns_revisit_violations`/`_revisit_split` 三處都用「先剝行內反引號、再看 `.lstrip().startswith("|")`」同一套判法,縮排的表格行(前面有空白再接 `|`)也正確辨識為表格、不評估。
- symbol/test 名稱含正規式特殊字元:`_ProbeTree.one` 與 `_probe_is_candidate` 兩處都用 `re.escape(name)`,不會被當成正規式語法解讀。
- 非 ASCII(中文)symbol 名稱:Python `re` 模組的 `\w`/lookaround 對 CJK 字元一樣視為「詞字元」,直接測過中文函式名的邊界比對(`檢查函式` 能命中、`檢查函式2`/`xx檢查函式` 正確不誤觸),沒有 F1 之外額外的問題。
- exam probe 題原文在筆記裡出現兩次:`_drift_exam_probe`/`_swap` 會把兩處都換掉(各自保留自己的縮排),`hit_kind`/`_drift_exam_others` 用「同一篇同一種發現」排除,不會把重複那一行誤算成噪音或誤報——沒有具體會翻紅的失敗場景,不標。
- `t_drift_when_probes_evaluate_and_trigger`、`t_note_shape_revisit_needs_date_or_probe`、`t_doctor_revisit_skips_probe_lines`、`t_note_audit_skips_conditional_revisit`、`t_set_plan_closed_lists_satisfied_status_probes`、`t_drift_probe_scan_and_doctor`、`t_drift_exam_probe_mode` 七支新測試在 clone-ns 上實跑全部通過(`python3 scripts/test_lumos.py -k <測試名>`),但都沒有涵蓋中文/NFD 路徑這條,跟 F1 的落差一致。

## 圖譜鏡頭:這次改動牽連到的筆記

- `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`:diff 只更新〈考試結果〉與〈修復結果〉節的記錄性文字(乙的考試分數、乙的門檻②還量不到、加一行 `REVISIT:2026-10-26`)。這些是「照事實填」的記錄行,不宣稱程式行為,diff 本身也沒有改到程式對應的部分被這篇筆記合約化,不影響其宣稱——已看,無 finding。
- `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md`:新增「條件式回頭條件(乙)」一節與一條 WHY、一條 RULE、兩條 PITFALL,並把 TEST 清單接上這次新增的七支測試。這篇是「管 `lumos drift` 家族」的家筆記,F1 踩到的正是它管轄範圍內 `when-file`/`when-symbol`/`when-test` 的路徑比對,但筆記本身沒有對「NFC 正規化」做出任何宣稱(沒有一句話說「路徑比對已正規化」),所以 F1 不算打臉這篇筆記的宣稱,是程式碼本身的邊界缺口——診斷寫在這裡,之後補洞時這篇筆記大概率要多一條 PITFALL,但這次 diff 沒有讓筆記說謊。
- `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md`、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md`:各自新增一條 WHY 說明「條件式回頭條件不送審」「REVISIT 行在第一層擋什麼」,跟程式碼裡 `_note_audit_items` 排除條件式那段、`_ns_revisit_violations` 擋新寫那段逐一核對過,敘述與實作一致——已看,無 finding。

最嚴重等級為 major,blocking 共 1 條(F1)。
