severity: major

**Finding 1**

severity: major
blocking: 是
`scripts/lumos:81541`(`_choice_layer_side_write`)與 `scripts/test_lumos.py:152038`(`t_choice_layer_template_parts`)。旁檔改成只靠 `_choice_layer_plan_md` 產生,內容沒有任何測試驗證。判讀代理被告知條款、預期值表與正文都在旁檔「判讀時要讀」。旁檔如果寫成空殼,代理就看不到條款原文,只剩材料裡的條款號清單。現有測試只數旁檔的個數,並確認兩份材料都提到旁檔檔名。

最小重現:在複製的 repo 把 `_choice_layer_side_write` 的 `body` 改成 `[f"# 選擇點存活判讀材料清單 {lid} 的共用材料", ""]`,不放計劃那一段。再跑 `python3.14 scripts/test_lumos.py -k choice_layer_template_parts`,結果 4 passed、0 failed。這個測試保護的是必要行為,卻抓不到這種改壞。

`_choice_layer_plan_md(p, v, side)` 的 side 分支(指路加條款號清單)也沒有測試。材料有沒有真的省掉正文、條款號清單對不對,都沒人驗。

引句:「body = [f"# 選擇點存活判讀材料清單 {lid} 的共用材料", "", *_choice_layer_plan_md(p, ctx.view(p))]」

**Finding 2**

severity: minor
blocking: 否
`scripts/lumos:81099`(`_CHOICE_LAYER_NOT_BODY_RE`)。新的整行比對只認 `§數字` 或「大寫字母加數字」當前綴,漏掉 repo 裡真實存在的標題 `## r1/r2 審計修正紀錄`。我在 `docs/lumos-toolchain-knowledge/Projects/intake守衛_計劃.md` 實跑,`_choice_plan_sections` 回傳了 `〈r1/r2 審計修正紀錄〉`。這一節因此被當成計劃正文,第 2 層判讀的引句與判讀依據的指紋都可能取到審計紀錄的文字。上一輪的寫法(`^(?:\S+\s+)?`)原本會排除這一節。規格明寫只認節號與大寫代號,所以這是規格取捨,不是誤實作,但真實計劃已經踩到。

引句:「_CHOICE_LAYER_NOT_BODY_RE = re.compile(r"(?:(?:§\d+|[A-Z]+\d+)\s+)?(?:驗收條款|預期值表|審計修正紀錄)\s*(?:[(（][^\n]*[)）]\s*)?")」

**Finding 3**

severity: minor
blocking: 否
`scripts/lumos:81398`(`_CHOICE_LAYER_SHARED_MAX`)。份上限現在只算存活自己的材料。主計劃是「未歸計劃」時,材料會附上全部存活計劃,而每份計劃最多可以內嵌 100KB 才改走旁檔。所以單份材料大小沒有上限。例如 5 份各 90KB 的計劃,加上 200KB 的存活材料,每一份都約 650KB。上一輪的版本在總量超過 200KB 時會改走旁檔。規格第 130 行寫明份上限只拿存活材料比,所以這是設計取捨,不是疏漏。但「一份材料的位元組上限」這個常數的註解已經名不副實。

引句:「_CHOICE_LAYER_SHARED_MAX = _CHOICE_LAYER_PART_BYTES // 2   # 一份計劃的共用材料(條款、預期值表、正文)超過這個數就整份另存旁檔(第三段代碼審 r2 N3)」

**修補三問的驗收**
- 刪掉的 `_choice_layer_one_part` 和 `_choice_layer_over`:grep 顯示 `scripts/lumos` 與 `scripts/test_lumos.py` 都沒有殘留的呼叫者。
- `_choice_plan_sections` 的讀者:只有 `_choice_plan_view`。`sections`、`all` 和判讀狀態的 deps_sha 都走同一份視圖,第 2 層驗證與材料用的是同一份段落,沒有分歧。
- 前言合併:一級標題在 `stack` 為空時 `continue`,多個連續一級標題的文字合成同一段。行為與測試一致。
- 舊判讀檔退回舊判法:只在沒有 `cite` 欄位時啟用。

總結:最高等級是 major。
