severity: blocker

### F1 dispatch-lens spec 模式不吃 --ranked,家的邏輯若掛在 ranked 分支就吃不到
severity: blocker
blocking: 是 — 不改,[S6]「dispatch-lens 的 diff 與 spec 兩種…也認家」對 spec 模式會系統性落空,連派這次審查用的鏡頭本身都吃不到「家」。
引句:「派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家」
1. `cmd_impact` 有兩條輸出路徑:ranked 分支算 `results`/`pins`([S2]–[S9] 描述的排序、about_hit 都活在這裡);非 ranked 分支只印 `{direct,indirect,incidents}`,是完全不同的資料結構。
2. `cmd_dispatch_lens_spec` 呼叫子行程時明確不帶 `--ranked`,自身註解也寫著「不是 --diff 的 results/pinned」——它讀的是 `all_direct`/`all_indirect`/`all_incidents`。
3. 若「家」的候選注入依自然位置寫進 ranked 分支,spec 模式永遠看不到「家」;[test:t_dispatch_lens_includes_homes] 若只測 diff 模式,會誤判整條規則已經過了。

file: `scripts/lumos:21586` ranked 分支起點(`if ranked or incidents_only:`)
file: `scripts/lumos:23116` `cmd_dispatch_lens_spec` 呼叫 `impact --file` 不帶 `--ranked`
file: `scripts/lumos:23121` 該處註解明寫兩種 JSON 形狀不同

### F2 「帶合約」沒定義含不含 RISK·* 標籤,恐讓 pin-denoise-a-v4 壓下去的噪音回歸
severity: blocker
blocking: 是 — 不改,實作者很可能沿用旁邊現成的 `bool(contract)` 寫法,把 RISK·* 家整批塞回必推名單,重現 held 58/96 那次噪音。
引句:「只有帶合約的家進必推,其餘家在可選名單照分數競爭」
1. `_impact_contract` 對 `risk/` 標籤節點回傳非 None 的 `"RISK·<...>"`;既有 direct 節點的「帶合約」判準是 `bool(x.get("contract"))`(含 RISK·*),但既有 indirect 節點特地用 `hard_pin` 把 RISK·* 濾出必推、丟進「參考道」,理由正是它是 held 噪音 58/96 的主力。
2. 「家」是全新第四條入口,[S4] 沒指名它比照哪一邊的「帶合約」定義。
3. 實測 scripts/lumos:31 個家裡有 10 篇帶 `risk/守衛面`(如 anchor-integrity、check-j-regen-guard),且完全不在現有 direct/indirect 候選裡——若採寬定義,這 10 篇每次改主程式都會被強制推進必推名單。

file: `scripts/lumos:21065` risk/ 標籤轉 `contract = "RISK·" + tag`
file: `scripts/lumos:21616` direct 節點「帶合約」= `bool(x.get("contract"))`
file: `scripts/lumos:21636` indirect 節點用 `hard_pin` 把非 INVARIANT/IRREVERSIBLE(含 RISK·*)濾出必推

### F3 家與既有 direct/indirect 節點重疊時,spec 沒定義去重,單檔候選會同節點重複列出
severity: major
blocking: 是 — 不改,Edit 前那支 hook 的「必看」清單會把同一篇節點印兩行,跟 [S4] 想壓的噪音背道而馳。
引句:「家一定進候選、而且進必推名單,不必正文用反引號寫這支檔」
1. `results` 是攤平的 list,「家」若照字面實作成一段新的注入迴圈、沒檢查目標節點是否已以 direct/indirect/incident 身分在 `results` 裡,就會讓同一節點出現兩筆。
2. 實測 scripts/lumos:31 個家裡有 16 個(過半)本來就已經是 direct 節點——不是邊界情況,是這個大檔的常態。
3. Edit 前那支 hook 的渲染逐項印 `pins`、不做 node 去重;`impact --diff` 因為按 node 鍵聚合才躲過這問題,但 [S2] 描述的正是「--file --ranked」單檔輸出,不是走 `--diff` 那條聚合路。

file: `scripts/hooks/claude/impact-hook.py:637` `pins = [x for x in res if x.get("pinned")]`(不依 node 去重)
file: `scripts/hooks/claude/impact-hook.py:641` `for x in pins:` 逐列印出

### F4 [S7] 旋鈕關掉「完全照原本」跟 [S8] 無條件拿掉舊「★關於★」標示互相矛盾
severity: minor
blocking: 否 — 兩種讀法都可實作,只是要挑一種,不影響核心排序邏輯對不對。
引句:「新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本)」
1. [S7] 承諾 `LUMOS_IMPACT_HOME=0` 時行為「完全照原本」,原本行為裡舊 about_hit 命中會顯示「★關於★」。
2. [S8] 卻說原本的「★關於★」標示拿掉,沒有用旋鈕狀態限定這句——字面讀起來不論開關都不再出現。
3. knob=0 時到底該不該印「★關於★」,[S7] 與 [S8] 對同一種情境給了不同結論。

### F5 大檔裡「不帶合約的純家」在可選名單要用什麼分數競爭,spec 沒定義
severity: major
blocking: 是 — 不改,實作者要嘛漏掉這批節點(讓 [S2]「家一定進候選」對它們落空),要嘛得自己發明一套分數,兩條路都跟任何 test 對不齊。
引句:「其餘家在可選名單照分數競爭」
1. ranked 分支的詞彙分只對 `all_direct`+`all_indirect` 節點跑 BM25F,純靠 about_code 進來、既非 direct 也非 BFS 可達的家沒有 hop、也不在這個候選集合裡,算不出 L 或 G。
2. 實測 scripts/lumos:31 個家裡有 5 篇(codex-harness、graph-sync-coverage、test-profile-multiplatform、棧別提問表態閘、每支檔有家)不帶合約、且完全不在現有 direct/indirect/incident 名單裡——要它們「照分數競爭」,分數從哪來沒寫。
3. 就算硬塞進 free 池,新增候選會跟既有候選搶 `LUMOS_IMPACT_FREE_QUOTA`(預設 10)名額,可能把原本會出現在「可能相關」清單的既有節點擠出視窗,跟整份計劃「只加不降」的自我定位有落差。

file: `scripts/lumos:21604` ranked 詞彙分候選集合只收 all_direct+all_indirect

### F6 「大檔」門檻該用哪個計數函式算「家的篇數」,spec 沒指名,兩個現成函式數字不同
severity: minor
blocking: 否 — 目前圖譜裡沒有檔案在兩個函式的計數上跨過門檻 8,不會改變現有結果。
引句:「大檔」:家的篇數 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)的檔
1. 既有 `_impact_mark_about` 現成掛在旁邊的計數是 `_impact_about_counts`,算的是「所有筆記(不分類型/狀態)裡 about_code 提到這支檔的次數」;名詞段定義的「家」只算 `type=system` 且狀態 doing/done/stale。
2. 兩個函式對同一支檔給不同數字:實測 `scripts/hooks/pre-push` 用 `_impact_about_counts` 算出 6、用「家」定義算出 4;全庫 30 個有 about_code 的檔裡 19 個兩者不同。
3. 若實作直接沿用 `_impact_about_counts` 當「家的篇數」,門檻在未來某支檔上會提前觸發(把還沒到 8 個真家的檔誤判成大檔),跟名詞段定義對不上。

file: `scripts/lumos:21279` `_impact_mark_about` 現有門檻讀 `_impact_about_counts`
file: `scripts/lumos:17995` `_nodehome_homes`(「家」定義的計數)

## 逐節讀完的其餘部分

- **為什麼(來源)**:已讀。引用舊案 d4「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」逐字核對過舊案節點,原文一致;引用「每支檔有家_計劃」(2026-09-11 上線)當新證據,已用 `scripts/lumos:18492` `cmd_home_check`、`scripts/hooks/pre-commit:124`、`scripts/hooks/pre-push:198` 核對過真的接進提交前/推送前掛鉤,不是紙上計劃——舊案攔截條件成立,無 finding。
- **名詞**:「家」的定義與計數(31 個)已用 `_nodehome_homes` 實跑核對相符,無 finding(門檻計數函式歧義另見 F6)。
- **核心裁定甲 [S1][S3][S5][S9][S10]**:[S1] 沿用 `_nodehome_key`/`_nodehome_homes`,跟「每支檔有家」同一函式,已核對相符。[S3] 排序取代邏輯與 [S9] stamp 不再生效的意圖清楚,唯與 [S7]/[S8] 顯示層交互見 F4。[S5]「只加不降」對既有三軸本身查無牴觸,唯新軸與既有候選競爭視窗的擠壓效應見 F5。[S10] 評測尺的鑑別力天花板計劃自己已承認並附 REVISIT,查無新洞。
- **核心裁定乙 [S11][S12][S13]**:已讀,跟 `check-j-regen-guard.md`、`節點還原.md`、SOP 快查表交叉核對過現況(intake 已驗「沒有任何檢查」屬實),無 finding。
- **範圍外 / 落點**:已讀,無 finding。
- **實務隱患**:已讀;「噪音變多」「評測尺量不到」兩條已自陳並附 REVISIT,「效能」「舊專案沒更新」「不可逆/金流」查無牴觸;「RISK·* 家會不會被巨檔門檻放過」這條隱患完全沒被提到——見 F2。
- **驗收怎麼跑 / 回頭條件 / 合約候選**:已讀,無 finding。「合約候選」兩條(家一定進必推、只加不降)跟 F3/F5 揭露的執行落差有關,收斂時複核建議一併看這兩條 F。
- **審計修正紀錄**:空白(首輪凍結副本本就沒有修正紀錄),無 finding。

## 固定席逐條判

- `Systems/retrieval-ranking`:不影響——本案就是要改的落點節點,現有內容沒有 ★INVARIANT★/★IRREVERSIBLE★ 合約行鎖住排序公式,只有描述現況的 KEY 行(本案的落點段本就打算更新它)。
- `Systems/節點還原`:不影響——沒有合約行;[S12][S13] 是在它管的 SOP 步驟裡加東西,不是改既有步驟的承諾。
- `Systems/check-j-regen-guard`:不影響——它的合約(J-a/J-b/J-c)管的是 regen 節點的 DECISION provenance 分級,不管 about_code 存在與否;[S11] 是新增一條獨立檢查,落點段本就指名掛在這篇,不牴觸既有 J 系列判準。
- `Issues/canary-record未落盤事件`、`code-loop守衛main-direct盲區`、`hook卸載殘留註冊`、`init-force-slug誤用basename`、`vendored測試套件在消費端假紅`:全部不影響——這五篇會被鏡頭列出,只是因為它們的 `pitfall_when` 觸發條件(`content:canary record`/`content:HOOK_ENTRIES`/`content:_slugify_vault`/`content:_VENDORED_TOOLKIT`/`glob:scripts/hooks/pre-push`)剛好命中計劃提到的 `governance/eval/retrieval-goldset.json`(內嵌歷史程式碼片段的已知偽觸發模式),跟這份「認家」設計的排序/合約邏輯完全無關。

總結:最高 severity blocker,blocking 共 4 條
