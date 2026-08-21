# D — 散文紀律層審計(CLAUDE.md / graph-discipline.md / skills/)

範圍:`CLAUDE.md`(6,797 字元)、`scripts/templates/graph-discipline.md`(6,565 字元,CLAUDE.md 核心段的機械同步來源)、`skills/lumos-project-notes`(SKILL.md 20,591 + reference.md 87,860)、`skills/lumos-design-loop`(SKILL.md 30,240 + reference.md 13,003 + templates.md 15,782)、`skills/lumos-code-loop`(SKILL.md 27,559 + reference.md 21,741)、`skills/lumos-pitfalls-gapfill`(5,098)、`skills/lumos-core-knowledge`(7,578)。**合計 242,814 字元**——比 audit-common.txt 起手estimate的「150K」還多 62%。

imperative marker(必須/須/不得/一律/嚴禁/★)計數:CLAUDE.md 16、graph-discipline.md 16(幾乎全同——見下)、project-notes SKILL 55/reference 131、design-loop SKILL 74/reference 23/templates 15、code-loop SKILL 83/reference 14、pitfalls-gapfill 3、core-knowledge 1。**design-loop+code-loop 兩支 SKILL.md 合計 157 個強制標記,壓在 57,799 字元裡。**

## 表:逐機制

| 機制 | 目的(一句話) | 執行力 | 有沒有真的動(證據) | 到得了 Claude 嗎 | 判定 | 修法(一句話,具體) |
|---|---|---|---|---|---|---|
| CLAUDE.md「圖譜先行」(第一個工具呼叫必須是 lumos) | 逼動手前先查圖譜再查 code/DB | **prose(honor-system)**——無任何 hook 檢查「第一個工具呼叫是不是 lumos」 | 無法量;圖譜自己的 Issue [[散文紀律沒有退場機制]] 把它列為「首選待測」——**選中的原因正是它從沒被驗證過** | 到(CLAUDE.md 全文注入 system prompt) | **修** | 按該 Issue 的 A 案做一次真 ablation(帶/不帶跑同批任務,比對是否真的少查錯圖譜),別再讓它免驗 |
| CLAUDE.md「對人回報用白話」 | 降低人閱讀理解成本 | prose(honor-system) | 無機械檢查器;本報告本身也在對抗這條(不易自證) | 到 | 保留 | 不用修,但承認它是純信任 |
| CLAUDE.md PRIOR-ART 三問 | 逼設計動筆前先查世界解 | prose,**答案要求寫入節點**(半結構化留痕) | `PRIOR-ART:` 字樣在多個計劃節點出現(見 檢核收緊五件_計劃「PRIOR-ART」段)——**有被實際遵守的樣本**,但無機械檢查逼你答 | 到 | 保留 | 加一條 lint:計劃節點若含「設計」相關 tag 卻無 `PRIOR-ART:` 行 → warn(小修,別造新機制) |
| CLAUDE.md「已知行為測試先行/未知行為實驗先行」 | 防止讀 code 找原因就開始建理論 | prose(honor-system) | 無法量 | 到 | 保留 | 同上,無立即修法 |
| CLAUDE.md「寫入圖譜三條鐵則」(不確定不標/wikilink list/純量用 lumos set) | 防 ghost 節點與 frontmatter 損毀 | **部分 hard**:鐵則 1(wikilink 字串型)、鐵則 3+4 由 `lumos lint`/`doctor` 機械檢查(reference.md:199-209 有實際 grep 偵測法);鐵則「不確定不標」是判斷力,無法機械 | `lumos lint`/`doctor` 是真跑的指令(pre-push 硬擋);L4 交叉審計 2026-08-21 抓到 445 條主張、70 條不一致,證明**檢查真的在抓東西** | 到(lint/doctor 輸出進 Bash 結果) | 保留 | 無 |
| `scripts/templates/graph-discipline.md`→ CLAUDE.md 同步 | 讓所有消費專案的 CLAUDE.md 圖譜先行段與源模板一致 | **hard(機械同步)**——非榮譽制:`lumos init/update` 用 sentinel 註解(`LUMOS:GRAPH-DISCIPLINE:START/END`)替換整段,`scripts/test_lumos.py` 有對應測試(見 4328/4417/4560/4582/4687/9790 行) | diff 驗證:CLAUDE.md 對應段與模板逐字相同(僅 `{{KG}}` 佔位符替換),機制在跑 | 到 | 保留 | 這是本區唯一「內容重複但有機械防漂移」的健康案例,別動 |
| pre-commit L2(圖譜同步硬擋) | code 異動未同步圖譜 → 擋 commit | **hard**:真的 `exit 1`,已驗證命中 Gate1(污染指紋)/Gate2(code 副檔名)/Gate3(有無圖譜 md) | `docs/.bypass-log.jsonl` 記錄逃生口使用率:61 筆(2026-06-29~2026-08-04),★之後 17 天(至 08-21)零筆★——不是 hook 壞了(hooksPath 已裝、可執行),是近期 commit 一律同批帶圖譜 .md(抽查 9a95bc4/7bd9ab2 均含 docs/.governance-log.jsonl+docs/*.md);94 天 8,915 筆治理帳中 L2 僅 61 筆(=61 次合法逃生,不是硬擋事件——硬擋本身不寫帳) | 到(git 原生 hook stdout 直接進 Bash tool 結果) | 保留 | 無 |
| post-commit bypass 觀測 | 量「逃生口用多兇」 | **hard 的觀測面**(hook 必跑),但**只記錄不阻擋** | 61 筆,近期歸零(見上) | 到(僅在下次 `gov` 查詢時,commit 當下不印) | 保留 | 無 |
| pre-push:anchor verify | 防驗證器本身被動過手腳 | hard,`exit 1` | 未見反例(未量測次數,但邏輯是每次 push 必跑) | 到 | 保留 | 無 |
| pre-push:tier=high → code-loop check 硬擋 | 逼高風險 diff 過對抗審 | hard | `docs/.governance-log.jsonl`:`code-loop` gate 79 筆去重,其中 **passed 56 / skipped 23 → skip 率 29%** | 到 | **修** | skip 率 29% 值得盯;2026-08-21 已立案(檢核收緊五件 S3)要把 skip 從「免費」改「必須自報 class」,但**該案三輪 blocker 10/9/10 無下降、達 cap 未收斂、人裁擱置**——目前仍是舊制(skip 零成本) |
| pre-push:doctor --ci | 圖譜整體健檢硬擋 | hard | 有,`doctor-run` 事件 2026-08-21 才剛開始落帳(僅 2 筆——這個「乾淨 run 有沒有痕跡」的地基缺口正是下面第一條 deficiency) | 到 | 保留 | 無 |
| `check-s`(自足性審計軟提醒) | 提醒節點該重做自足性審計 | **soft,只印不擋** | ★[[Issues/自足性審計提醒空轉四十六天]] 實測:46 天內響 18,283 次(去重 7,317),涉 42 節點,**0 次被處理**,直到 2026-08-20 才靠「做別的任務時順手 grep」發現★ | 印到 stdout,但**沒有任何回看觸發點**——等同「印進沒人讀的串流」 | **虛設候選,已被系統自己抓到** | 已知,2026-08-21 用 L4 交叉審計清帳 30 節點(governance/l4-audit/2026-08-21/),但「誰會去看」仍無機械路徑——治標未治本 |
| `check-e1` | (自足性審計相鄰的另一道軟提醒/ratchet) | soft | 703 去重筆/1,752 原始行,191 個 commit | 印到 stdout,無回看路徑 | **修** | 同 check-s,是同病灶的第二個實例 |
| L3/check-e2/check-e3/check-j(部分)/check-k/check-r/kill | 驗證腐爛(L3)、規格追溯(e2/e3)、重生 provenance(j)、?(k)、可逆性綁定(rollback,r)、合約殺傷力驗證(kill) | **hard 邏輯已寫**(scripts/lumos:785-1030,1308,2997,3009 都是真判斷式,非死碼) | **90 天治理帳 8,915 筆中,這 7 道閘一筆都沒出現**(`gov --stats` 自報) | 若真觸發會到(hard 擋);但從沒觸發過,所以模型也從沒在實戰中見過它的輸出 | 待判(gov --stats 自己的告誡:「未出現≠沒用」,硬擋不寫帳) | 逐道人工判「情境沒發生」vs「死碼」——已被 [[Issues/只退場不痛的機制]] 點名為待裁清單,尚未拆開判 |
| `lumos-design-loop` canary 段落(頁頂告示+步驟 2/4①/4.5/6 的刪除線殘留) | 歷史帳判讀(協議已於 2026-08-14 停用) | **N/A(已停用)** | 協議停用 | 到,但**佔用讀取頻寬**——SKILL.md 233 行裡至少 15 行是「~~已停用~~」型刪除線殘留、頁頂 3 段告示 | **精簡** | 停用 6 天以上的協議該搬進 reference.md 或直接砍,SKILL.md 頭版不該留刪除線考古 |
| `lumos-design-loop` 1800 行/30K token 軟上限 | 防審查員被脈絡衝淡漏看 | **soft(純 advisory,超標不擋)** | 段落本身用 20 行(SKILL.md:63-73)講「這條純粹借外部文獻,本專案三次對照實驗都不支持,別拿來當佐證」——★機制活著、佐證已撤,只留一句「代價遠小於漏一個 blocker」撐著★ | 到,但這 20 行是**純歷史考古**,操作指令只有一句「wc -l 超過就拆」 | **精簡** | 把三次失敗實驗的敘事全搬 reference.md,SKILL.md 只留「軟上限 1800 行,理由:外部實測(非本專案驗證)」一行 |
| `lumos-design-loop` 收斂 cap 數字 | 定義「跑幾輪算放棄」 | hard(`_TIER_PARAMS`,scripts/lumos:4589) | **SKILL.md 內部三處數字互相打架**:L17「cap=2」(disposal 一輪流程)、L150「max cap＝6 筆 record」(護欄段,實為 legacy tier 專屬)、L213「cap=2」(light 檔重試)——而**實測收斂到頂的真實案例全部是 3 輪**(檢核收緊五件 r1/r2/r3、gov-stats 三輪、doctor-run事件 4 輪)。code 端 `_TIER_PARAMS = {"light": (1,2), "standard": (3,3), "high": (5,3), "legacy": (1,6)}`——standard/high 的 cap 是 **3**,不是 6 | 到,但**讀者無法從 SKILL.md 單獨判斷正確 cap 是幾** | **修** | L150 的「max cap＝6」要嘛刪、要嘛明講「僅 legacy tier」;跟 `_TIER_PARAMS` 對齊成單一敘述 |
| `lumos-design-loop` K=1(panel)vs K=2(循序) | 定義收斂連續乾淨輪數 | hard(`_loop_status_panel` 只取最後一輪) | code-loop SKILL.md 自己承認過去寫反過(現存段落:「本行原本只寫『連 2 輪』,與下方 panel 節自相矛盾;**code 實作的是 panel 節那個**」)——★已修正,但修正說明本身變成永久嵌入 SKILL.md 頭部的考古段★ | 到 | 精簡 | 修正過的內容應該只留最終結論,不留「我曾經寫錯」的解說(那段解說本身不影響操作,純佔位) |
| `lumos-design-loop`/`lumos-code-loop` 外家否決席(family=external) | maker≠checker 地基 | **soft:`note-if-absent`**(缺席不擋,只要求「收斂宣稱要講小」) | [[Issues/外家席長期缺席仍照跑loop]]:Codex/Gemini 管道連續數週全部不可用,三輪 panel 九席全 claude 家族仍照常收斂——★缺席從未被統計持續幾輪★ | 到(SKILL.md 有寫),但**執行結果與寫的語意不一致**:語意是「有就用」,實況是「持續數週沒有也没人算」 | **修** | 2026-08-21 檢核收緊五件 S3 想把它綁進 `code-loop pass/check`(硬 fail-closed),**三輪對抗審未收斂、人裁擱置**——當前仍是舊制軟性但書 |
| `lumos-code-loop` panel K=1 收斂但門檻最鬆 | — | hard,但**skill 自己標注矛盾未解**:「panel 是風險最高的路徑,判準卻最鬆」(引 arXiv 2605.12280 建議 two-consecutive-clean,本專案尚未照改) | 已知未解,SKILL.md 明講「此處只先把矛盾講白,不偷偷改判準」 | 到 | **修** | 這是一條「知道有問題但决定先不修」的紀律,建議另立一個追蹤節點而不是讓警語常駐在每次讀 SKILL 時重複出現 |
| `lumos-project-notes`:frontmatter 四鐵則(ruby YAML 解析/Obsidian 解析/字串型 wikilink/summary 結構) | 防圖譜物理損毀 | **hard**:reference.md:199-209 給出可執行 grep/ruby 一行指令,`lumos lint` 內建對應檢查 | 有——L4 清帳(2026-08-21)顯示 lint 抓到的問題是真的(445 主張/70 不一致) | 到 | 保留 | 無 |
| `lumos-project-notes`:★INVARIANT★→[test:]→[audit:]→[kill:] 合約鏈 | 分級驗證合約(綁測試/獨立審計/殺傷力驗證) | **部分 hard**:`[test:]` 綁定由 doctor Check T 強制;`[audit:]`/`[kill:]` 是**選配**,且據 user memory「合約鏈殺傷力驗證」:①已交付,②③④待辦——kill 90 天內零觸發(見上表) | 混合;test 層有真綁定,kill 層形同虛設(未交付+零使用) | 到 | 修 | 對外宣稱這條鏈四段時要註明②③④仍是未完工地基,別讓 skill 讀起來像四段都成熟 |
| `lumos-pitfalls-gapfill` | 網搜補 linter 沒收錄的坑 | **honor-system**(WebSearch→反證預篩→人裁);無機械執行,5,098 字元裡幾乎沒有強制標記(僅 3 個) | 未在本次查證範圍內找到觸發統計(該 skill 產物進圖譜的 linter-gap 節點,未逐筆核數) | 到 | 保留 | 若要驗證,加一條 `gov --stats` 可讀的 gate 事件 |
| `lumos-core-knowledge` | 跨專案業務規則升格/偏離治理 | **honor-system**(1 個強制標記,7,578 字元幾乎純慣例說明) | 未量;本專案(lumos-toolchain 自身)不是核心圖譜的主要消費端,難以從本 repo 帳本判斷觸發率 | 到 | 保留 | 無法在本 repo 內評估——建議下次審計換一個有 core_refs 高使用量的消費 repo 驗證 |

## 3-5 個最重要的缺陷(有 file:line/證據)

1. **軟提醒是機械上「活的」,但社會上死的——check-s 46 天響 18,283 次、0 次處理**,直到人「順手 grep」才發現(`docs/lumos-toolchain-knowledge/Issues/自足性審計提醒空轉四十六天.md`)。這不是猜測,是系統自己 2026-08-20 立案承認的。`check-s` 印到 stdout 但**沒有任何回看觸發點**——這正是 audit-common.txt 定義的「reminder that prints into a stream nobody reads」的教科書實例。`check-e1`(703 去重筆/191 commit)是同病灶第二例。這兩道閘的「有沒有真的動」答案是:**技術上動了(每次都印),制度上沒動(印了没人看)**。

2. **散文紀律本體從未被驗證過有沒有效,而且已知的外部證據方向不利。** `skills/` 全樹 150,810 字元(project-notes 的 87,860 是最大宗)裡,系統自己查證後承認「被前後量過效果的:0 條」(`docs/lumos-toolchain-knowledge/Issues/散文紀律沒有退場機制.md`)。更嚴重的是它引用的兩篇外部論文:TDAD(arXiv 2603.17973)顯示「只加一段『請照測試先行做』的程序散文」把回歸率從 6.08% 惡化到 **9.94%**(比什麼都不加更糟);AGENTS.md 實測(arXiv 2602.11988)顯示 LLM 生成的脈絡檔成功率 **-3%/成本 +20%**。而**CLAUDE.md 本身「動手前第一個工具呼叫必須是 lumos」這條,被系統自己列為「首選待測」對象——正因為它跟被證明有害的那類程序性指示同型**,卻至今仍是純散文、零機械檢查、零 ablation。這是本審計範圍內風險最高、卻最貴(每次對話都載入)的一條規則。

3. **design-loop 的核心「硬閘」在真實案例中反覆打不進去,靠人裁繞過——閘的「收斂」語意跟實況脫鉤。** 抓 `git log --grep "未收斂"` 的樣本:2026-08-21 當天就有兩起(`檢核收緊五件` 三輪 blocker 10/9/10 無下降達 cap;`gov --stats` 三輪 blocker→blocker→major 達 cap),再往前至少 15 起同型紀錄(`code-loop pass` 人裁豁免放行、`公開精簡版` 未收斂人裁放行、`檔案測試依賴地圖` 達 cap 攤牌人裁……)。閘的操作定義是「跑滿 3 輪(_TIER_PARAMS standard/high cap=3)沒收斂就停手攤人」,而**人在被攤牌後幾乎每次都是「放行、拆案、或人工核准」**——閘從未真正阻止一次交付,它只是把裁決權交還給人,跟沒有閘的差別是多耗 3 輪審查成本。`skills/lumos-code-loop/SKILL.md` 甚至自己承認 pre-push 的 tier=high 硬擋有 **29% 走 skip**(56 passed / 23 skipped,`docs/.governance-log.jsonl` 統計)。

4. **SKILL.md 內部自相矛盾的數字,讀者(包括模型)無法單看該檔判斷哪個是真的。** `skills/lumos-design-loop/SKILL.md:17` 寫 disposal loop cap=2、`:150` 寫「max cap＝6 筆 record」、`:213` 寫 light 檔 retry cap=2;而 `scripts/lumos:4589` 的 `_TIER_PARAMS = {"light": (1,2), "standard": (3,3), "high": (5,3), "legacy": (1,6)}` 顯示 standard/high 的真實 cap 是 **3**,「6」只屬於幾乎不用的 legacy tier。三個月來所有真實達 cap 案例(見上一條)都在第 3 輪停,與程式碼的 3 一致、與 SKILL.md 護欄段寫的「6」不一致——這條規則對一個只讀 SKILL.md 沒去讀 scripts/lumos 原始碼的模型會直接誤導它「還可以跑到第 6 輪」。

5. **maker≠checker 的地基(外家否決席)曾連續數週全滅,而閘的語意設計成「缺席不算 blocker」,系統對此毫無自動偵測。** `docs/lumos-toolchain-knowledge/Issues/外家席長期缺席仍照跑loop.md`:Codex CLI 模型不可用、Gemini pro 額度=0、flash 逾時,三個管道同時掛,但三輪 panel(9 席)照常收斂,唯一的補償是**在文件裡多寫一句「收斂宣稱要講小」**——這句話本身也是純散文,沒有任何機制統計「已經連續幾輪沒有外家」。這是 audit-common.txt 定義的「a gate that fires on paper but not in practice」的直接案例:`_TIER_ROSTER` 表面上把外家席標成 `required-fail-closed`(design/high, code/high),但 code 端只有 2026-08-21 才開始設計(尚未落地、三輪對抗審未收斂)把它變成真的 fail-closed——目前為止全程是「轉述,不阻斷」。

## 補充:今日(2026-08-21)紀律違反/機制自產工作量的直接樣本

- `governance/review-reports/檢核收緊五件/`:三輪 panel(r1 六席含外家、r2 六席含外家、r3 七席含兩席外家)、blocker 計數 10→9→~10,**沒有下降趨勢**,最終人工裁定「不放行、拆三案、地基先行」——耗費 9,250~22,919 字元/席報告 × 19 席次,產出結論是「這個機制自己的地基(乾淨 run 零痕跡的棘輪、range 綁定跟 git 打架)撐不住這次要加的三個新閘」。
- `docs/lumos-toolchain-knowledge/Issues/流程自產工作量未量測.md` 明確承認:同一天(2026-08-21)兩個案例(`doctor-run事件` 4 輪 10 席、`檢核收緊五件` 3 輪 19 席)裡,**相當比例的 findings 是在修流程自己要求產出的規格文件的內部矛盾**,不是在修產品程式碼;這個比例從未被系統性量測——「對檢索排序做消融實驗、對這套流程的成本效益用信仰」,是系統自己的原話。
- `git log` 未見 `--no-verify` 直接用於繞過本區審計流程的痕跡(`.bypass-log.jsonl` 61 筆全部集中在 2026-06-29~2026-08-04、且全部是 code-only 沒圖譜的合法逃生口,近 17 天歸零)——**紀律違反不是靠硬繞過發生的,是靠 skip/人裁等「合法但頻繁使用的逃生門」發生的**,這比純粹的 --no-verify 濫用更難用單一數字量,但影響更大(見上表 code-loop skip 29%)。
