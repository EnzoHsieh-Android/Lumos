severity: major

## 逐節閱讀記錄

**Frontmatter/summary、緣起、人裁、PRIOR-ART**:已讀,無 finding(緣起段的清點數字屬背景陳述,不是條款依賴的機械判準,未逐一重算)。

**[S1]**:已讀,見 C1、C4。roster 表加法本身(family/occupies_w/requirement 三欄寫法)與既有 `_rseat` 慣例一致,已用 `_TIER_ROSTER` 原始定義核對過。

**[S2]**:已讀,見 C1、C2、C3。凍結/回放模式的處理邏輯(用 `spec_sha_override is not None` 判斷、不重讀早輪報告檔)已用 `cmd_loop_replay` 的 `--freeze` 實際程式碼核對,推理站得住——`files` 字典只收判定輪的 report/snapshot,早輪報告檔本來就不受版控錨定保護,不重讀是對的設計。

**[S3]**:已讀,無新 finding。`_SECURITY_SEAT_SINCE` 的比較法(`_loop_ts_key`、無時區判 fail)逐行核對過 `_disposal_clause_step`/`_CLAUSE_GATE_SINCE` 的既有實作,寫法與比法一致。

**[S4]**:已讀,無 finding。看什麼/不報什麼/攻擊路徑要求與嚴重度錨的內容完整;§7.7 立場表新增列未給精確文字,但該表本身規定「範例池、每輪改述、不逐字貼」,不給精確文字反而是照既有規則。

**[S5]**:已讀,見 C5。

**[S6]**:已讀,無 finding——實際執行 `lumos decisions Systems/pitfalls-code-loop` 驗證過,d5 顯示 ❌ 已被 d6 取代、d6 顯示 ✅ 有效,和 [manual:] 宣稱的指令輸出相符(但 d6 的內容文字本身有問題,見 C3)。

**邊界與不做、承認的限制**:已讀,四條限制各自附了可執行的回頭條件,格式合CLAUDE.md 鐵則。但這份清單少列了一條真實存在的限制,見 C4。

**實務隱患**:併發/效能/資源/可逆性/凍結判定與回放/金流/對外送出/認證等——逐項核對程式碼後皆為準確描述,已讀無 finding。守衛面段自己列的「誤擋」清單(判定輪只派一席、生效日前的迴圈、席名沒帶模型尾碼、Codex 編排)有兩個真實會發生的誤擋/漏擋場景沒被納入清單,見 C1、C4。

**驗收**:已讀。測試案例只涵蓋「無 hyphen」與「多一段中文字」兩種席名反例(`資安審-sonnet`、`非資安-sonnet`),沒有涵蓋「模型名本身帶連字號」這種本帳本裡佔比 35% 的真實形態,呼應 C1。

---

## Findings

### C1

[S2] 用「取最後一個連字號前那段」抽鏡頭段,要求整段等於「資安」才算數。但這個 repo 自己的審查帳本裡,308 個歷史席名有 109 個(35%)帶 2 個以上連字號,常見成因就是模型名本身含連字號(`gpt-5.6-terra`、`gemini-3-flash` 這類)。照這條規則,派工單如果誠實記成「資安-gemini-3-flash」,取最後一個連字號前段會得到「資安-gemini-3」,不等於「資安」,問閘會判成沒有資安席,即使資安審查真的做了、報告也真的在。

引句:「取最後一個連字號前那段;沒有連字號就整個名字」

file: `docs/.canary-log.jsonl:1265` 真實帳列 `"auditor": "外家codex-gpt-5.6-terra"`——3 個連字號、模型名本身含連字號
file: `docs/.canary-log.jsonl` 另有 `s6-external-premise-gemini-3-flash`、`s7-external-implement-gemini-3-flash`、`crossfamily-gemini-flash` 等同構案例(逐行掃描本帳本全部 308 個 unique auditor 值得出 109 個 ≥2 連字號)

severity: major
blocking: 是
判準:不修,實作者會照抄這條規則做出一個對現行常見命名法系統性假陰性的機械閘,擋下真的做過資安審查的推送。

### C2

[S2] 只承諾把 `scripts/lumos` 裡 `_loop_status_disposal` 這一處「四條合取」的說明文字改正,但同一句過期措辭(把處置閘描述成恆定四項)還逐字寫死在至少三個外部技術文件裡。這次上線後,處置閘實際條件數會變成六項(G3、處置集合、留痕重驗、quote-check、條款綁定、資安席),而這三處文件的說法只會更錯,不會被這次的修正動到。

引句:「是過期的,實作時一併改正」

file: `skills/lumos-project-notes/reference.md:695` 「design-loop 新制(2026-08-04):收斂閘改…(四條合取:G3∧處置帳全清∧留痕 sha 重驗∧quote-check 引句全錨定)」
file: `skills/lumos-project-notes/reference.md:1284` 同一句逐字重複第二次
file: `skills/lumos-design-loop/reference.md:93` 「`lumos loop status <id> --disposal --spec <計劃節點> --repo <root>`(四條合取全讀側可重算:G3∧處置全清∧留痕 sha 重驗∧引句全錨定)」

severity: major
blocking: 是
判準:不補這三處,下一個接手的人照這幾份文件數處置閘的條件數會漏算(既漏掉早已存在的條款綁定,又漏掉這次新加的資安席),判斷「還差幾項才過」時算錯。

### C3

[S2] 明文禁止把新步驟叫「第五條」,理由是條款綁定已經佔用「第五步」這個位置、名字會撞。但同一批工作已經寫進圖譜的 `[[Systems/pitfalls-code-loop]]` KEY 行與決策 d6,卻逐字把新步驟稱為「處置閘第五條合取」——直接違反 spec 自己剛定下的命名禁令,而且不是假設情境,是已經存在、已經跑 `lumos decisions` 驗證過確實生效(d5 已標超越、d6 已生效)的圖譜內容。

引句:「它對 code 迴圈恆 skip,所以功能不撞,但名字會撞」

file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:35` KEY 行「機械擋=處置閘第五條合取:整個迴圈至少一筆席名鏡頭段是資安的審查席帳列、報告在且 sha 對」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:71` 決策 d6 content「機械擋=處置閘第五條合取(整個迴圈至少一筆席名鏡頭段是資安的審查席帳列、報告在且 sha 對)」

severity: major
blocking: 是
判準:不修,實作者若照圖譜節點(而非整份 spec 全文)工作,會把新函式、commit 說明或 note 取名「第五條」,重現 spec 自己剛剛指出要避免的撞名問題。

### C4

`_roster_observe` 判斷「同門席位夠不夠」只查 `_TIER_ROSTER[(kind,tier)]` 這張靜態表跟帳面同門席總數,完全不看時間。[S1] 把 `("code","high")` 的必派同門席數從 5 提到 6 之後,任何一個生效日前就已經合規收斂的舊 high 迴圈,只要事後被人用 `loop status <id> --disposal`(非唯讀模式)重新查一次,就會立刻冒出全新的「seat_shortfall」異常並寫進該迴圈的 `roster-alerts.log`——即使問閘本身的 rc 不變(roster 是 advisory)。[[Projects/roster對帳併入問閘_計劃]] 明訂 2026-11-26 要靠這份 log 的真實出現次數決定 `--roster` 該不該退場,這種舊迴圈被追溯貼標籤的假訊號會混進那次盤點,而 spec 的〈承認的限制〉四條裡沒有一條提到這個風險。

引句:「這輪要派的審查人數配額」

file: 實際指令輸出——`python3 scripts/lumos loop status code-batch2 --roster --repo .`(2026-08-26 的真實 high 迴圈)印出「應派 required 同門 5」「實派 6 席(同門[claude] 5/外家 1)」,零異常;`_TIER_ROSTER[("code","high")]` 加入資安席後同一指令會把「應派」變成 6,而 5<6 立即觸發 seat_shortfall
file: `docs/lumos-toolchain-knowledge/Projects/roster對帳併入問閘_計劃.md`「REVISIT:2026-11-26 查 roster-alerts 真實出現數(零→--roster 重審退場;上行條款)」

severity: major
blocking: 是
判準:不處理,過去合規的舊迴圈會在毫無新增風險的情況下被貼「席位短缺」標籤,污染既有的兩季覆核與退場判準,讓人誤判歷史審查缺席。

### C5

[S5] 要求把「架構對齊」在文件裡出現的每一處都比照補上資安席,但只舉 3 個例子並用「等」帶過,沒有機械化的漂移守衛盯住這份清單完不完整。實測全 repo 含「架構對齊」字樣的技術文件其實有 6 個,比 [S5] 舉例的還多至少一個沒被點名;而這個系統對同類問題早有機械化前例可以直接套用,這次卻選擇純人工「逐一對過」。

引句:「commands/06、code-loop reference.md、design-loop SKILL.md 等」

file: `skills/lumos-project-notes/reference.md:1084`「code-loop 的架構對齊席負責抓『跟既有寫法不一樣』」——[S5] 舉例清單未點名此檔,但此檔同樣描述席位分工,是資安席上線後可能該補一句卻沒人記得補的候選
file: `scripts/test_lumos.py:5452` `t_marker_doc_sync`——本專案既有的「逐一比對兩份文件裡固定關鍵字集合、缺一就翻紅」機械漂移守衛寫法,S5 未採用同等機制

severity: major
blocking: 是
判準:不做機械化守衛,三個月後同類文件散落仍會漏改,而這正是可以現在用既有寫法一次解決、之後不用再靠人記得的成本。

---

## 圖譜鏡頭(固定席)逐條判

- **[[Systems/pitfalls-code-loop]]**:會受影響,見 C3——這份設計沒有破壞此節點宣稱的行為/合約本身(風險掃描類軸、PITFALL_CLASSES、三道防污染皆未被此案觸碰),但此節點已寫入的 KEY 行與決策 d6 內容與這份 spec 自己的命名規則矛盾,需要一併修正才能落地。
- **[[Systems/arch-alignment-lens]]**:不影響——此節點宣稱「四個席位表各加一席架構對齊」,這份設計只在 `("code","high")` 單一組合加資安席,不觸碰設計審三級與 code standard 的編制,架構對齊席在四張表裡的既有位置與行為完全未被改動。
- **[[Systems/hook信任邊界]]**:不影響——此節點管的是三支 hook(進場/圖譜同步/影響鏡頭)解析 `lumos` 執行檔的信任鏈,這份設計的改動全部落在 `scripts/lumos` 主檔的處置閘邏輯與技能文件,不涉及任何 hook 檔案或其執行路徑。

## 總結

最嚴重 severity:major。blocking 共 5 條(C1、C2、C3、C4、C5)。
