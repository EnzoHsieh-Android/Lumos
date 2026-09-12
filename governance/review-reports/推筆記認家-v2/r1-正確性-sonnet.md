severity: blocker

### F1 「確認過的家」對無副檔名的檔(scripts/lumos 與三支 git hook)判準不明,兩級篩選在最大宗的檔上可能整個失效
severity: blocker
blocking: 是 — 若判準落地成「裸字出現即算確認」,分兩級篩選對本工具鏈家數最多的檔完全不起作用,等於重蹈舊案(固定席扇出降權_計劃 d4)當初要擋的「填錯的家被無條件推上必推名單」
引句:「那篇的摘要或正文出現這支檔的完整路徑或檔名(含副檔名)。主檔名不算」
1. 這句判準只講清楚「有副檔名」的情況(檔名含副檔名算、主檔名不算),沒講無副檔名的程式檔(`scripts/lumos`、`scripts/hooks/pre-push`/`pre-commit`/`post-commit`)這時「檔名」到底算不算數——因為這類檔的「主檔名」跟「檔名」是同一個字串,規則字面上兩邊都套得上、也兩邊都套不上。
2. 這不是紙上談兵:`scripts/lumos` 是本工具鏈家數最多的檔(31 家,逼近大檔門檻),而全庫 65 篇 Systems 節點裡有 62 篇正文/摘要出現裸詞「lumos」;若判準落在「裸字出現即確認」,這支檔的兩級篩選等於沒篩。
3. [S14] 上線抽查問的是「這篇是不是在講這支檔負責的事」(語意對不對),不是「有沒有寫出檔名」(確認判準本身這件事),接不住這個洞。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:9` about_code 掛 `scripts/lumos`(無副檔名),正是同時逼近 8 篇大檔門檻的實例
file: `docs/lumos-toolchain-knowledge/Systems/節點還原.md:28` 這篇沒把 `scripts/lumos` 列進 about_code,正文卻用了裸詞「lumos」,示範裸字比對對這支檔沒有鑑別力
file: `scripts/lumos:18080` `_nodehome_homes` 是家對照表唯一算法,只濾 type/status、不濾「是否確認」;確認判準要另外加在這批候選之上,但無副檔名時加不出來

### F2 大檔門檻沿用舊環境變數名,但兩套計數口徑不同,拿舊調參結果背書新門檻
severity: minor
blocking: 否 — 兩種模式(旋鈕開/關)各自的邏輯本身是對的,只是同一個旋鈕在兩種模式下代表不同量尺,不會讓程式直接做錯事
引句:「家對照表裡這支檔有 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)個家」
1. 旋鈕關(舊機制)用 `_impact_about_counts` 算「不分類型狀態」的 about_code 命中數;旋鈕開(新機制)改用家對照表(只算 type=system 且 doing/done/stale)算,對同一支檔算出的數字不同。
2. 實測 `scripts/lumos`:舊算法 65、新算法(家)31——同一個「8」在兩種模式下的實質篩選力道差超過一倍,拿舊算法時代網格調參(train 掃 N∈{5,8,12})的結果去支持新算法下沿用同一個數字,論證基礎已經換了量尺。
3. [S10] 的評測只在兩種旋鈕狀態各跑一次消融,沒有針對這個門檻本身重新網格搜。
file: `scripts/lumos:21365` 舊巨檔判定 `counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))`,`counts` 來自 `_impact_about_counts`(scripts/lumos=65)
file: `scripts/lumos:18080` 新家對照表 `_nodehome_homes` 用不同的型別/狀態過濾,同一支檔算出 31

### F3 每支檔有家.md 的既有 DEP 句上線後會失真,S18/S19 的稽核範圍沒覆蓋到這類節點
severity: major
blocking: 是 — 不改,以後讀圖譜的人(或 AI)會被這篇一句已經不成立的規則誤導,判斷跟現況相反
引句:「上線那次提交處理會失效的既有驗證紀錄,共六篇,逐篇判要不要標 stale」
1. [S18] 的稽核只掃「既有驗證紀錄」(Verification 型節點,用 `lumos stale --candidate --match 固定席` 找六篇),範圍不含其他型別節點裡會失真的散文宣稱。
2. `每支檔有家.md` 的 DEP 行寫著「推筆記只認反引號路徑的裁定見 固定席扇出降權_計劃」——本案 [S2] 上線後,about_code 確認過的家會成為第四條入口,這句話不再是事實,但它既不在 [S18] 點名的六篇裡,`--match 固定席` 找的是驗證紀錄不是任意節點的散文句,也掃不到它。
3. 本案的「落點」段本就會編輯這篇節點(補 about_code、寫 [S11]/[S15]),但落點段沒把「順手修這句舊宣稱」列成交付項,容易在實作時被漏掉。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:30` DEP 行原文「推筆記只認反引號路徑的裁定見 [[Projects/固定席扇出降權_計劃]]」,本案上線後不再成立

## 逐節讀完的其餘部分:已讀,無 finding

- 名詞(其餘定義:家、家對照表、必推名單、可選名單、大檔本身、從程式重建的節點、組裝檔):彼此不衝突,「必推名單/可選名單」與既有 pins/free 概念一致。
- [S1]:家對照表單一算法、行程內快取寫法與既有 `_ABOUT_COUNTS_CACHE`/`_BASENAME_COUNTS_CACHE` 同款,查證程式碼(`scripts/lumos:18080` `_nodehome_homes`、`:17699` `_NODEHOME_HOME_STATUSES`)與名詞定義的「doing/done/stale」一致。
- [S3]:核對 `_impact_knob`/`pins.sort` 現有寫法(`scripts/lumos:21746`),新排序需求可疊在同一個 stable-sort 上不牴觸;「事故同時是家的算事故」與測試⑨改成只在旋鈕關掉時檢查的改寫一致。
- [S5]:「只加不降」敘述與 [S2] 一致,沒找到能反例的情境。
- [S6]:merge 時「分數較高整項取代要併回家標記」的風險,spec 已自己點名(不算未覆蓋的洞);查證 `cmd_dispatch_lens_spec`(`scripts/lumos:23201`)呼叫 `impact --file` 確實未帶 `--ranked`,JSON 形狀確實是 `{direct,indirect,incidents}`,與 spec 描述相符。
- [S7]:旋鈕語意與既有 `LUMOS_IMPACT_ABOUT`/`LUMOS_IMPACT_BASENAME_MATCH` 慣例一致;查證 `_impact_mark_about`(`scripts/lumos:21354`)現況與「旋鈕關時完全照原本」的描述相符。
- [S8]:實作時「兩張種類表」以外,`scripts/hooks/claude/impact-hook.py:643,652` 與 `scripts/lumos:22117` `_LENS_KIND` 也各有一份種類對照——但 S8 用「其他講到固定席的地方一起改」這種開放式列舉沒有排除它們,漏改頂多是缺一個顯示標籤(空字串),不影響任何晉升/排序判斷,未達成 finding 門檻。
- [S9]:「旋鈕開時舊關於命中整段不跑,LUMOS_IMPACT_ABOUT 對排序失效」是明講的取捨,有對應測試 `[test:t_about_stamp_no_longer_affects_ranking]`,不是遺漏。
- [S10]:必看棘輪、噪音棘輪、`out_top3_must`、`ablation_blocked` 都已是現成機制(`governance/eval/retrieval_eval.py:187,282,320`),S10 只是把兩個旋鈕值各跑一次,接線方式與既有慣例相符。
- [S11][S12][S13][S17]:查證 `每支檔有家.md` 現有「擋的五種新違規」與新增第六種的敘述在數量上自洽(前五項與後兩項本就是分開列的兩組);`node_home.gate` 現有 on/warn/off 三態與 S11 的接法一致。
- [S15]:觸發時機(新加進 about_code 但正文/摘要沒提到)可以掛在既有 `_nodehome_golive`/`_nodehome_evaluate` 已有的新舊快照比對(`scripts/lumos:18253` 起)上,機制上站得住;判準本身的模糊(是否算「提到」)已併入 F1,不重複開一條。
- [S16]:非程式檔經 `impact --diff` 的 `_impact_diff_seed_ok`(`scripts/lumos:21878`)確實不擋副檔名、只擋 `.md/.jsonl/governance 下的 .json`,與 spec 說法相符;`.md` 版面檔仍推不出來這件事 spec 自己已經講明,不是隱藏的洞。
- [S18](六篇既有驗證紀錄本身、S19 決策回寫):敘述與舊案 d1-d4 的原文核對一致(逐字核對 `Projects/固定席扇出降權_計劃.md` decisions 段),沒有找到反例;範圍外的邊界(每支檔有家.md 的 DEP 句)已獨立開 F3,不重複。
- 範圍外、落點(除 F3 外)、實務隱患(除 F1/F2 涉及的部分外)、驗收怎麼跑、回頭條件、合約候選、審計修正紀錄:逐段讀完,內容彼此不矛盾,回頭條件都有日期與具體要看的指令/數字,沒有發現新的未定義詞、壞引用或執行缺口。

## 固定席逐條判(這份設計會不會破壞該節點宣稱的行為或合約)

- `Issues/各棧測試資料夾被當成要家.md`:不影響——本案「範圍外」明文排除,留給另一個提交處理。
- `Systems/retrieval-ranking.md`:不算破壞,是本案的目的地(擴充 impact 排序、接 evaluation),沒有找到跟它既有宣稱衝突的地方。
- `Systems/每支檔有家.md`:會受影響,但不是「破壞」而是「遺漏」——見 F3,DEP 行的既有裁定描述會失真,需要一併修正。
- `Systems/節點還原.md`:本案直接修改這篇的 SOP 文字([S12]),是設計出來要做的事,不算破壞既有宣稱。
- `Issues/canary-record未落盤事件.md`、`Issues/code-loop守衛main-direct盲區.md`、`Issues/hook卸載殘留註冊.md`、`Issues/init-force-slug誤用basename.md`(四篇事故節點,經 `governance/eval/retrieval-goldset.json` 牽連):不影響——本案沒有改動這四個事故各自的觸發條件或 goldset 的讀寫機制,只影響 impact 排序的「家」入口。
- 其餘「超出上限,只列名」的節點(`vendored測試套件在消費端假紅`、`known-pitfall-refresh-token`、`lumos-cli-read`、`pitfalls-code-loop`、`lumos-refcheck`、`anchor-integrity`、`測試假綠形態`、`slim-install-安裝器`、`slim-uninstall-一行卸載`、`design-loop`、`lumos-cli-lifecycle`):都是因為 `scripts/test_lumos.py` 本身牽連過廣(108 篇)才被列出;本案只在這支檔案裡新增測試函式,不改動既有測試邏輯,不影響這些節點自身宣稱的合約。
- `Verification/2026-07-10_檢索排序v1.md`、`Verification/2026-07-11_檢索goldset評測.md`、`Verification/2026-08-24_about_code讀側四項落地.md`:會受影響,但這正是 [S18] 點名要標 stale 的三篇,本案已經正面處理,不算意外破壞。

總結:最高 severity blocker,blocking 共 2 條
