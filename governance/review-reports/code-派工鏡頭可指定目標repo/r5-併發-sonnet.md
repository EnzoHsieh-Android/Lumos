severity: major

## 資源席第五輪報告

本輪新增的名字出口和 NFC 去重沒有造成耗時或記憶體問題。實測發現一個舊有、作者自量沒涵蓋的問題:提交寫法的輸出行數沒有上限。這個問題本輪沒有引入,但本輪改到那幾行,也沒有補上限。

實驗在 `git clone` 出來的 lens-repo(版本 9fa8af1e)上做,用 `lumos dispatch-lens --spec` 實跑。耗時為單次量測,只代表這台機器。

| 輸入 | 耗時 | 記憶體 | 輸出 |
|---|---|---|---|
| 5000 個程式檔(含逗號與 NFD 寫法)加 300 個連結,工作樹寫法 | 1.2 秒 | 約 294MB | 22KB |
| 同一份計劃,提交寫法 | 2.1 秒 | 約 295MB | 22KB |
| 1MB 計劃(約 4 萬個不同候選),工作樹寫法 | 3.3 秒 | 約 249MB | 1 位元組(無輸出) |
| 同一份 1MB 計劃,提交寫法 | 4.3 秒 | 約 254MB | 741 位元組,印「超過 5000 個,只算到一半」 |
| 5000 個連結,節點只在提交裡、會談目錄沒有,提交寫法 | 6.6 秒 | 約 259MB | 914KB、5006 行 |
| 5000 筆 `lands_in`,節點都不存在,工作樹寫法 | 1.2 秒 | 約 248MB | 524KB、5002 行 |

severity: major
blocking: 是 — 派工詞尾端可被單一計劃撐到近 1MB(約 30 萬 token),子代理的派工詞超過上下文就派不出去,而且沒有上限、也沒有「另有 N 個」的收斂
引句:「extra += [f"- {_lens_author_name_show(f'{vault_rel}{n}.md', _LENS_SPEC_PATH_MAX)} [計劃連結]:只在那個提交裡,會談目錄還沒有這篇"」
問題:`only_nodes` 沒有筆數上限,每個節點印一行。程式檔類(`only_files`、`code_files`、`too_generic`、`skipped_files`)都限 5 個。`max_lines=400` 只管固定席節點的渲染,管不到 `extra` 和 `landing`。`_nodehome_landing_sizes` 的落點行同樣每項一行、沒上限。掛鉤直接把整段接在派工詞後面,沒有字數截斷。本輪新加的出口只擋「名字長相」,沒擋「名字有幾個」。
具體失敗情境:
- 計劃寫 5000 個 `[[Systems/…]]` 連結,節點只存在於凍結提交、會談目錄還沒有。這正是提交寫法的設計用途,先凍結再於別的工作樹補節點。
- 輸出 914,503 位元組、5006 行,每條 `- docs/…/Systems/zz節點N_… [計劃連結]:只在那個提交裡,會談目錄還沒有這篇`。
- 5000 筆 `lands_in`(新節點計劃常見)則印出 524KB、5002 行「還不存在(要新開)」。
- 1MB 計劃上限允許更多,因為連結候選上限 5000 管的是「問提交」,不管列幾行。
- 作者自量 300 個連結、247MB、4.67 秒,只量了時間和記憶體,沒量輸出大小,所以這個問題沒被看到。
- 修法方向:`only_nodes` 與落點行都像 `only_files` 那樣取前 N 個,其餘併成一句「另有 M 篇」,並用輸出總字數上限當最後一道防線。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49607`;file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49516`

### 已讀,無 finding

- **名字出口耗時**:`_lens_author_name_ok` 先判長度(最長 300 字)再跑整串比對和逐字類別檢查,所以超長名字不會做無謂比對。`_lens_spec_names_line` 與 `_lens_author_names_show` 吃的串列至多 5 個(`code_files`、`only_files`、`too_generic`、`skipped_files`),大量名字進不了這條路。5000 個含逗號的名字全部走拒絕路徑,仍在 1.2 到 2.1 秒內。
- **NFC 去重**:`_lens_spec_code_cands` 以 NFC 為鍵、原寫法為值,只有一份字典,沒有多一份大集合。`_lens_spec_linked` 與目標架構段新增的 `seen` 是單層集合,記憶體差異在實測雜訊內(約 250 到 295MB)。NFC 對每個候選正規化兩次,5000 個連結下可忽略。
- **目標架構段**:候選清單沒有 5000 個的上限,只受計劃 1MB 限制。新加的 `shown` 字典是一次線性走訪。`_arch_target_rule_index` 每個候選重建一次規則清單是舊有成本,本輪沒有放大。
- **掛鉤新增的 `_spec_what`、`_spec_name_show`、`_range_what`**:先判長度再比整串,沒有二次方。`_SPEC_HEX_RE.fullmatch(head)` 是線性,而且標記行是 `\S+`,不會出現超大的中間字串。
- **逾時與孤兒行程**:本輪沒有新增行程。`impact` 子行程帶剩餘秒數的逾時,舊有且未改。掛鉤逾時時,`subprocess.run` 只殺 `lumos` 本身,正在跑的 `impact` 子行程可能存活到自己的逾時,最長約 30 秒。這是舊有行為,本輪沒有惡化。
- **清理**:實驗目錄已刪除,刪前 `lsof` 看到一個 git 程序開著 `.git/objects` 的索引檔,我沒有刪它,是 `rm -rf` 之後目錄才確認消失。

最高等級 major,blocking 1 條。
