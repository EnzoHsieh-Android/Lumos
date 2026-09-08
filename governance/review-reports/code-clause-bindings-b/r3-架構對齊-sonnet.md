severity: minor

# 架構對齊審查——code-clause-bindings-b(r3,sonnet,上限輪)

被審(凍結):全量 `governance/review-reports/code-clause-bindings-b/r3-snapshot.patch`;delta `governance/review-reports/code-clause-bindings-b/r3-delta.patch`。只判第 2 輪(`code-clause-bindings-b` r2)折入(delta)有沒有引入「跟這個專案既有做法不一樣」的寫法,以及前輪本席那條 major(clause_bindings 裡三條規則散在解析器內)折入後對不對齊。不找 bug,不評風格。

核對:`r3-delta.patch` 裡 `scripts/lumos` 的變更 hunk 起訖(index `e4392cf..a376481`)與 `git rev-parse 04bb7dc:scripts/lumos`(=`e4392cf`,`-b r1` 折入後狀態)→`git rev-parse HEAD:scripts/lumos`(=`a376481`,commit `9bf50c2`「code-clause-bindings-b r2 折入 9 條」)完全對應——這批 delta 就是已落盤的 `-b r2` 折入內容,已是 HEAD。baseline 讀 `git show HEAD:scripts/lumos`(本地落地 `/tmp/lumos_head.py`)確認既有慣例與消費端關係;working tree 另有不相干的未提交改動(`_extra_fm_keys`/`_lumos_config_near_vault`),不屬本次審材,已排除。

LUMOS-IMPACT: Lumos/main..HEAD

---

## 1. `_strip_inline_markup` 與 `INLINE_CODE_RE`——兩層各一份,還是行內層兩份?

**判定:對齊。**

先答框架問題:是「兩層各一份」。第一層(行/圍欄層)全檔仍只有 `_visible_lines` 一份實作;新函式 `_strip_inline_markup` 是**第二層(行內層)**的新增,不是對第一層的重寫。第二層原本就只有 `INLINE_CODE_RE` 這個原語(单反引號 span),`_strip_inline_markup` 內部呼叫它、不重寫它:

> 引句:「    search 的 probe 刻意只用 INLINE_CODE_RE 不走這裡:搜尋寧可多看見,截掉=靜默看不見(2026-08-03 那個坑)。"""」

程式上驗證:`_strip_inline_markup`(file: `scripts/lumos:167`)全檔唯一呼叫點是 `clause_bindings`(file: `scripts/lumos:4103`);其餘所有直接使用 `INLINE_CODE_RE` 的地方(file: `scripts/lumos:2035`、`scripts/lumos:2134`、`scripts/lumos:2577`、`scripts/lumos:3772`、`scripts/lumos:14606`、`scripts/lumos:16404`、`scripts/lumos:17862`)分兩類,都不是「行內層第二份等價實作」:①`_search_visible_lines`(file: `scripts/lumos:2577`,search 的 probe)與 `cmd_link_candidates` D1(file: `scripts/lumos:13911` docstring 自述「即 search 的 include_code=False 同款組合」、`scripts/lumos:14000`)是**同一組既有的、比 `_strip_inline_markup` 更寬鬆的既定組合**(`_visible_lines`+裸 `INLINE_CODE_RE.sub`),這是這批折入之前就存在、且在多處 docstring 互相對照過的標準寬鬆搭配,不是新分岔;②refcheck 家族(`_refcheck_scan` file: `scripts/lumos:14606`)、stale-path(file: `scripts/lumos:2035`)、ghost-symbol(file: `scripts/lumos:2134`)、doctor pitfalls corpus(file: `scripts/lumos:16404`)全部是用 `INLINE_CODE_RE.findall`/`.sub` 做**抽取或降噪**,語意跟「剝掉反引號範例、不信未閉合內容」相反或無關,不構成同一問題的第二種解法。

`_strip_inline_markup` 本身是composed 函式(HTML 註解→雙反引號→`INLINE_CODE_RE`→未閉合截斷,四步疊加),沿用既有原語做內部一步而不是另起爐灶,結構上與既有的 `_strip_fences_text` vs `_strip_code_text`(同一份 `_visible_lines` 上疊出兩支不同用途的 composed 函式,且各自 docstring 都寫「為什麼不用另一支」)同構——這正是上一輪(r2)Q1 判定 `~~~` 補丁「對齊」時已經核可的那個「單一原語+多支具名 composed 函式,各自文件化用途差異」架構,這批折入把它延伸到行內層,方向一致。

docstring 有沒有把差異講清楚:大致講清楚,但有一處用詞可以更精確——「★全檔唯一★,別在別處自寫第二份」這句話語境是指「跟 `clause_bindings` 同等級的嚴格判定不要重寫」,緊接著自己就舉了 search 這個「刻意不走這裡」的例外並附理由,讀者順著讀不會誤判;但字面上沒有明講「裸用 `INLINE_CODE_RE`(link_candidates 等既有寬鬆組合)本來就不算『自寫第二份』」,對只掃過這一支 docstring、沒去查其他六個呼叫點的人有極小機率誤讀成「INLINE_CODE_RE 的其他直接用法都該遷來這裡」。這個精度落差不影響架構本身(沒有第二套判定邏輯被建出來),不列入不對齊計數。

- severity: clean
- blocking: 否

---

## 2. `_visible_lines` 加圍欄配對與跨行註解——其他消費端行為有沒有一起變、docstring 有沒有跟上

**判定:對齊。**

折入處只動了 `_visible_lines` 這一支「全檔唯一的 fenced-code 判定實作」本身,新增兩個狀態:

> 引句:「    fence = None          # 開著的圍欄是哪一種(``` 或 ~~~):只有同一種才能關(-b r2 外家席:兩種共用一個 toggle 會被交錯反轉可見性)」
> 引句:「    in_comment = False    # 跨行 HTML 註解 <!-- … -->:整段不算內容(單行的由 _strip_inline_markup 剝)」

問題點名的三個消費端逐一核對,全部是「呼叫 `_visible_lines`」而不是「自己 toggle 圍欄/註解」,新行為透明生效:
- `_strip_fences_text`(file: `scripts/lumos:2553`):一行 `return "\n".join(ln for _no, ln in _visible_lines(text.split("\n")))`,本身無算法陳述,docstring 只講「為什麼不能用 `_strip_code_text`」(輸出語意差異),沒有對圍欄/註解演算法的具體宣稱會過期。
- `_strip_code_text`(file: `scripts/lumos:2483`):經 `_search_visible_lines`(file: `scripts/lumos:2563`)間接呼叫 `_visible_lines`,docstring 是一大段歷史事故記錄(未閉合圍欄、縮排圍欄的爆炸半徑量測),同樣沒有對「圍欄配對規則」「HTML 註解」下具體斷言,新行為不會讓既有文字變假。
- refcheck 家族:`_refcheck_scan`(file: `scripts/lumos:14599`)呼叫 `_strip_fences_text`,同一條鏈路;`cmd_refcheck`(file: `scripts/lumos:17704`)docstring 明講「抽取規則同 doctor Check P step 1-2(刻意複製、不共用)」,這是既有、與本輪無關的另一層次分工,本輪沒有去動它。

這正是 `_visible_lines` 自己 docstring 開宗明義講的「★為什麼所有人都必須走這裡★」(file: `scripts/lumos:2517-2532`)的設計目的:讓內部規則進化時消費端不用逐一改——這與上一輪(r2)Q1 對 `~~~` 補丁的判定(「這對它們是透明生效,不需要各自另補」)完全同構,本輪只是把同一個機制擴大到「同種圍欄才能關」與「跨行 HTML 註解」兩條新規則,適用同一個結論。

唯一一個沒有被三個消費端問題點名、但值得記一筆的邊界(不影響本問判定):`keep_fenced=True`(唯一呼叫路徑是 `_search_visible_lines` 的 `include_code=True`,即 `search --code`)時,圍欄內文字若字面含 `<!--` 而未在同一圍欄內閉合,會被新的 `in_comment` 分支一併吃掉——這是圍欄與跨行註解兩個新規則疊加出的次要互動,docstring(file: `scripts/lumos:2520`「保留圍欄內的文字」)沒有覆蓋到這個邊界,但這不是「消費端各自要不要另補」的問題(它仍是 `_visible_lines` 單一實作內部的邊界情形),不屬本問範圍,不列入不對齊計數。

- severity: clean
- blocking: 否

---

## 3. `listlike_extra` 復用 `duplicate` 狀態——跟既有命名慣例一不一致

**判定:不對齊(minor)。**

折入處新增第四個累加字典,結構上跟既有 `defined`/`fallback`/`dup` 同一種「dict-per-concern、鍵是 cid」慣例,沒有問題:

> 引句:「    defined, fallback, dup, listlike_extra = {}, {}, {}, {}」

但輸出狀態的分配上,`listlike_extra`(合法定義過、又出現在一行**認不得的清單前綴**或**反引號截斷後仍判為清單**的行)被直接歸進既有的 `duplicate` 狀態,跟 `dup`(**同一個 cid 在兩處都被 `_CLAUSE_LEAD_RE` 判成合法定義行**)共用同一個狀態字串與同一種輸出形狀:

> 引句:「        if cid in listlike_extra:   # 合法定義過,卻又出現在像清單的認不得的行(或反引號前綴的行)→ 當重複/認不得,擋」

對照緊接在後、本輪沒有改動的原生 `dup` 分支,兩者 `out.append` 內容除了取數來源不同,連 `"state": "duplicate"` 這個字面值都一字不差:

> 引句:「            out.append({"id": f"S{cid}", "line": defined[cid][0], "refs": [], "manual": [], "defined": True, "state": "duplicate",」

這兩種成因在語意上並不相同——`dup` 是「兩行都合格地定義了同一個編號」,`listlike_extra`(此分支)是「只有一行合格定義,另一行是格式看不懂、判不了是不是引用的疑似清單行」。`clause_bindings` 自己的 docstring 在同一個函式裡,對另一個軸(懸空)明確立過「一個成因一個狀態」的慣例(該句本身含「」符號,依卷證規則不逐字引用,改用 file 定位:file: `scripts/lumos:4094`,原文為「狀態七種……四態不是三態、懸空要分「寫錯」與「設定認不到」,後者不進量測分母」)——當初把懸空拆成 dangling/unrecognized/mentioned 三態,理由正是「後者不進量測分母」,即成因不同會影響下游怎麼算、怎麼講。這批折入在 `duplicate` 這一軸沒有循同一慣例另立狀態名(例如 `listlike-conflict`),而是直接復用,`_CLAUSE_STATE_ZH` 的中文說明也維持原字面「兩行都寫成定義」的措辭,沒有為新成因擴寫:

> 引句:「                    "undefined": "非定義(只在範例/引用裡出現,不算條款)", "duplicate": "編號重複定義(兩行都寫 [SN])"}」

後果落在使用者看得到的閘訊息上:`_disposal_clause_step` 對 `state == "duplicate"` 的兩種成因印出同一句話,字面斷言「一個編號只能定義一次」——即使實際上這個編號只被合法定義了一次:

> 引句:「        print("[disposal] 條款綁定: ✗ — 條款編號重複定義:" + "、".join(f"{b['id']}(第 {'/'.join(map(str, b['dup_lines']))} 行)" for b in dups) + ";一個編號只能定義一次,不然第二筆沒標會漏過")」

這批折入自己的測試也印證了這個訊息會被印在「只定義一次」的情境下(`cgt.md` 只有一個 `- [S1]` 合法定義,第二行是認不得的清單前綴 `→ [S1]`,不是第二個合法定義):

> 引句:「    r = _loop(v, f"cg-t-{_M1U}", "cgt.md", base + "- [S1] 已標 [manual:人看一次]\n→ [S1] 第二次定義沒標\n")」

擋下這個組合、把它跟真正的重複定義同樣列入「需要人修好才能過閘」的判斷是合理的(兩者確實都該擋),不改變本問對「該不該擋」的判斷;不對齊的地方在**命名層**——復用既有狀態字串描述一個新成因,讓 `_clause_summary` 的統計桶(file: `scripts/lumos:4194` 起算,含 `duplicate` 計數)與 `_disposal_clause_step`/`cmd_spec_trace`(file: `scripts/lumos:4244`、`scripts/lumos:4265`,兩處都把 `"duplicate"` 跟 `"untagged"` 並列判定)混進兩種不同成因,往後想單獨追蹤「真的重複定義」發生幾次會被這批新流量污染,且面向作者的錯誤訊息在這個分支下字面失真(「一個編號只能定義一次」用在只定義一次的檔案上)。這正是 major/minor 錨點裡「命名/錯誤處理不一致但結構對」的典型:accumulator 字典的結構、worst-wins 式的擋閘邏輯、輸出 dict 的欄位形狀都跟著既有架構走,沒有另開一條路或跨層直呼,只是名字挑錯了。

- severity: minor
- blocking: 否

---

## 小結

不對齊共 1 條,其中 major 0 條。
