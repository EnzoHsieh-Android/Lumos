severity: major

# 架構對齊審查(第 2 輪)

## 問一:找節點是不是走 `env.find` + `_node_not_found`

對齊。`_spec_gate_load` 這次改成 `rel = env.find(node)`、找不到就呼叫 `_node_not_found(env, node)` 再回 `(None, "", None)`,`cmd_spec_gate` 收到 `p is None` 時 `return 2`——這跟 dispatcher 裡其他吃節點名的分支(`scripts/lumos:29160-29163`,`links/backlinks/context/map/show` 共用同一段 `rel = env.find(...); if rel is None: return _node_not_found(env, args.note)`)是同一條路,也跟 `cmd_spec_trace`(`scripts/lumos:5004-5006`,自己印訊息但同樣走 `env.find` 判 `None`)同源。`write_side` 沒有傳(預設 False)也對——這是讀取指令,跟 `set/append/remove/new` 那批寫入指令才該傳 `write_side=True`(`scripts/lumos:29347`)分得清楚。原本被拆掉的舊寫法(`env.resolve` + `hasattr` 探測 + 手拼 `node + ".md"`)本身就是本檔案裡的孤例寫法,這次折入反而是消掉那個孤例、回到主流慣例。

引句:「rel = env.find(node)   # 跟 spec-trace 與其他吃節點名的指令同一條路(代碼審 r1:短名叫不到、退回手拼漏了 Projects/)」

## 問二:`as_list` 用法

對齊。`_plan_system_links` 這次把 `lands_in`/`related` 兩個欄位都包進 `as_list(...)`,跟全檔另外 30+ 處(`scripts/lumos:528,536,1129,1146,1201,1222,1468,1746,1816,1948,4548,10503,10624,10825,11380,11381` 等)讀 frontmatter 欄位一律先過 `as_list` 再展開的寫法一致,修的正是「這裡漏了會靜默丟掉」這個原本的孤例。

引句:「links = [str(x) for x in as_list(note.fields.get("lands_in"))]   # 字串/清單都收(代碼審 r1:別處都過 as_list,這裡漏了會靜默丟掉)」

## 問三:`_visible_lines` 消費者怎麼處理標題(回退節 Setext 判定)

不對齊。`_rollback_section_chars` 這次自己加了一段偵測「下一行是 `---`/`===` 就當作 Setext 標題」的邏輯,把它拼成假的 `"## " + 內容` 再丟給既有的 `_ROLLBACK_H2_RE` 判。但全檔目前只有兩個地方在判標題:這裡,以及 `scripts/lumos:14219` 的 `idx = next((i for i, l in enumerate(lines) if l.startswith("#")), None)`——後者純 ATX、完全不管 Setext。這支新邏輯沒有進到 `_visible_lines` 這個共用層(它的職責本來就限定在「fence 判定★全檔唯一★」,不含標題語法),而是在單一函式裡另開一套「標題等不等於 ATX」的私有判法,屬於「引入第二種做法」——往後任何人要在別處認 Setext 標題(例如合約行所在的 Systems 節點若用 Setext 開二級標題)不會被同一套邏輯覆蓋,行為會因函式而異。

更嚴重的是這段新邏輯跟同一份 patch 自己寫的 KEY 文件互相打臉:KEY 行明寫「回退節只認 ATX 二級標題(設計寫死,Setext 不認)」,但緊接著的程式碼與新測試 `t_spec_gate_code_review_r1_folds` 的第④點卻是在驗證 Setext **會**被認(`r4.returncode == 0`)。文件描述與程式行為方向相反,屬於文件跟合約行本身的真實性問題——⚠ 這條的嚴重度不完全落在「second way/跨層直呼」的錨點上,但既然是同一次修正引入、又直接影響下一個讀者對規則的理解,仍記一條,嚴重度打折為 minor。

引句:「setext = bool(re.fullmatch(r"[-=]{3,}\s*", nxt)) and not ln.startswith("#") and ln.strip() != ""」

severity: major

引句:「回退節只認 ATX 二級標題(設計寫死,Setext 不認)」

severity: minor

## 問四:`_lens_contract_lines`/`_lens_contract_rows` 現在是不是都走 `_contract_key_matches`

不對齊,而且正是 r1 抓到、要求折的那條 major 本身沒折乾淨。新函式 `_contract_key_matches` 的 docstring 自稱「★全檔唯一的『合約行』掃描★」,並且明寫「派工鏡頭(`_lens_contract_lines`)與規格閘的相依回歸(`_contract_texts`)都走這裡」——注意這句話**沒有提到 `_lens_contract_rows`**。實地核對 `scripts/lumos:24766-24777`,`_lens_contract_rows` 仍是自己逐行 `INVARIANT_RE.match(s)/CHECKPOINT_RE.match(s)/IRREVERSIBLE_RE.match(s)` 三個 if/elif,完全沒有改成呼叫 `_contract_key_matches`。也就是說,原本的「合約行掃描第三套」只收斂了兩套(`_lens_contract_lines`、`_contract_texts`),`_lens_contract_rows` 這一套原封不動留著,變成現在唯一還獨立存在的「第二套」——跟計劃節點裡「代碼審 r1(...)折入:...合約行掃描第三套收斂成一支」(`docs/lumos-toolchain-knowledge/Projects/規格落成可驗收條件_計劃.md`,凍結 patch 行 16)這句宣稱不符,也跟 `_contract_key_matches` 自己標榜的「★全檔唯一★」矛盾——這正是本輪要驗證的「`_lens_contract_rows` 有沒有被漏掉變成剩下的第二套」,答案是:漏了。這屬於「引入/留下第二種做法」的典型 major。

引句:「派工鏡頭(_lens_contract_lines)與規格閘的相依回歸(_contract_texts)都走這裡(代碼審 r1 架構席:別再各寫一份)。」

file: `scripts/lumos:24766-24777`(`_lens_contract_rows` 仍自行三支 if/elif,未改呼叫 `_contract_key_matches`)

severity: major

## 小結

不對齊共 3 條,其中 major 2 條。
