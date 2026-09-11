severity: major

### F1 [S18] 點名要標 stale 的三篇,跟「驗收怎麼跑」指定的機械指令實際掃出的清單對不上,另有三篇陌生候選沒處置
severity: major
blocking: 是 — 三個月後接手人照「驗收怎麼跑」那行指令跑,拿到的清單只有 1/3 對得上 spec 點名的三篇,另外三篇候選 spec 完全沒討論,不知道該不該動,會重蹈 r1 已經修過一次的「既有 pass 驗證被弄失效」。
引句:「另跑 `lumos stale --candidate --match 固定席` 找其他寫了」
1. file: `docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md:11` revalidate_when 三行都沒有「固定席」字面,實跑 `lumos stale --candidate --match 固定席` 掃不到這篇,但 [S18] 點名它要標 stale。
2. file: `docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md:6` 同樣掃不到(revalidate_when 只寫「vault 節點數倍增、排序參數…」),也是 [S18] 點名的三篇之一。
3. 實跑該指令回傳 5 篇,除 [S18] 點名的 about_code讀側四項落地外,多出 file: `docs/lumos-toolchain-knowledge/Verification/2026-08-05_標籤結構收編落地.md:6`(revalidate_when 含「固定席軸序變更」)、`2026-08-18_edit面查詢品質閘落地.md:8`、`2026-08-18_標註刷新落地.md:9` 三篇陌生候選,spec 全文沒提到、沒處置指示。

### F2 [S11] 沒交代怎麼接進「每支檔有家」既有的五種違規資料結構與 S8–S10 健檢,字面實作會漏掉健檢那一半
severity: major
blocking: 是 — 沒有這段,實作者不知道新違規要對應到 doctor 的第幾段、要不要擴充判定函式回傳的資料結構,大機率漏做「舊帳只提醒」那一半或塞錯位置。
引句:「上線前就蓋了章沒填的舊節點:健檢列出、不擋」
1. file: `scripts/lumos:17905` `_nodehome_parse_note` 目前只回傳 type/status/about/resp/sig/text,沒有 regen 欄——[S11] 要判「這次新蓋章 vs 舊節點」得先讓這支函式多認 regen 欄並跟舊版比對,spec 沒提這個前置改動。
2. file: `scripts/lumos:2113`、`scripts/lumos:2134`、`scripts/lumos:2151` 現有 S8/S9/S10 三段健檢各自對應「沒家/別人的檔/管太多沒寫負責範圍」三種舊帳;regen 節點沒填 about_code 是第四種形狀,`_nodehome_ledger`(`scripts/lumos:18434`)回傳的 dict 沒有對應欄位可讓 doctor 印出來,spec 沒說要不要新開一段或該叫第幾段。
3. file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:20` 現有 KEY 行寫死「擋的五種新違規」,[S11] 上線後實際變六種,落點段只說「[S11] 新違規...[[Systems/每支檔有家]]」,沒指示要同步改寫這一行 KEY。

### F3 [S14] 家的品質抽查沒有可重跑的程序,REVISIT 要求的複測執行不了
severity: major
blocking: 是 — 沒有寫死抽樣方法與派審流程,2026-11-12 REVISIT 要求的「換一批配對再抽一次同樣規模」沒人知道怎麼重做,一次性把關等於形同虛設。
引句:「配對(三個 POS 專案全部 46 對,加本工具鏈隨機 20 對)」
1. `python3 scripts/lumos home --help` 實跑只有 `check` 一個子命令,沒有任何列出「檔 → 家」配對或做隨機抽樣的子命令、旗標,spec 全文也沒指名用哪支既有工具產生這份清單。
2. file: `governance/eval/refresh_labels.py:4` docstring 明寫這是「標註刷新工具」,標的是 goldset 的必看標籤(query/edit 判準),不是 about_code 配對正不正確,不能直接套用當 [S14] 的雙評審載具,spec 也沒交代兩個模型家族怎麼被派工、分歧怎麼收斂成錯誤率。
3. [S15] 引的「本工具鏈 69 對」「三個 POS 46 對」標成「2026-09-12 實算」,顯示這數字是一次性手算出來的,不是任何 lumos 指令跑出來的,印證這條程序目前沒有機械或文件化的重現路徑。

### F4 家一定進必推跟既有「lane 參考道」機制的互動沒討論,可能違反 spec 自己的「只出現一次」
severity: major
blocking: 是 — 不補,實作者容易漏掉「lane 節點剛好也是目標檔的家」這種情況,讓同一篇在 hook 輸出裡出現在兩個地方,直接牴觸這份 spec 自己列的合約候選。
引句:「同一篇在推筆記清單上只出現一次([S2])」
1. file: `scripts/lumos:21640` RISK·* 類的 indirect 候選在算完就 `continue` 分流進 `lane_raw`,自始不進 `results`;file: `scripts/lumos:21657` `_impact_mark_about` 只掃 `results`,lane 節點不會被判定成「已經是候選」。
2. file: `scripts/lumos:21720` `lane` 是 JSON 輸出的獨立頂層鍵,跟 `pins`/`free` 分開印——若那個 lane 節點剛好也是目標檔的家,依 [S2] 的規則會被判成「還不是候選」而在 `pins` 新增一筆分數 0 的「家」項,同一篇同時出現在 `lane` 與 `pins` 兩處。
3. spec 全文沒有一處提到 `lane`/`LUMOS_IMPACT_HARD_PIN` 這個既有機制,[S6]「另外三條讀取路徑也認家」列的三條(diff 聚合、派審查員圖譜參考、計劃模式)也沒把 lane 算進去。

### F5 [S16] 非程式檔字串預篩的「零成本」宣稱跟 hook 目前純轉發的架構對不上
severity: major
blocking: 是 — hook 現在完全不讀圖譜內容,只轉呼叫 lumos;字面實作「先做字串預篩」等於要 hook 自己新增一輪掃全部 Systems 正文的 I/O,跟「沒家的不花任何成本」互相矛盾,實作者需要先知道這個落差才能做對取捨(例如改成叫 lumos 一支輕量子指令來做,而不是 hook 自己掃檔)。
引句:「hook 先做字串預篩(Systems 節點原文裡有沒有這個路徑)」
1. file: `scripts/hooks/claude/impact-hook.py:8` docstring 明寫現行流程是「攔截 Edit/Write/MultiEdit → 過濾(只 code 副檔名) → TTL 冷卻窗判定 →」,file: `scripts/hooks/claude/impact-hook.py:9` 下一步就是「subprocess 呼叫 `lumos impact --file <path> --repo <repo> --json`」,整支 hook 是純轉發層。
2. 全檔搜尋 read_text/open/glob 只命中暫存標記檔(TTL 冷卻窗那個 marker 檔),沒有任何讀取 `docs/*-knowledge/Systems` 內容的程式碼——[S16] 要求的「字串預篩」若做在 hook 這層,是全新的一段圖譜掃描邏輯,不是沿用 [S1] 講的「行程內快取」(那是 lumos 那支長行程單次呼叫內的快取,hook 每次都是全新 subprocess,快取不會跨呼叫留存)。

---

## 逐節讀完結果(未列入 finding 的部分)

- **frontmatter(lands_in/summary 三行 KEY)**:內容與正文對得上,落點三篇(retrieval-ranking/節點還原/每支檔有家)問題已併入 F1/F2/F4 討論,不重複列。
- **為什麼(重開舊案的依據)**:核對 `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md` d4 原文與 r1/r2/r3 打穿段——「新前提沒達到、不拿它當授權」的改寫誠實(承認自己 43 支沒家、POS 46 對不是同一份語料),「只加不降」與 [S4] 大檔整批不認家的組合,確實避開了舊案 r1 版「有欄不含目標檔→降自由席」被 `Issues/hook卸載殘留註冊` 打穿的那種傷害形狀;已讀,無 finding(這塊已被 r1 G4 处理過,重查未見新洞)。
- **名詞**(家/家對照表/必推名單/可選名單/大檔/從程式重建的節點/組裝檔):`家` 的定義與 `_NODEHOME_HOME_STATUSES = ("doing", "done", "stale")`(`scripts/lumos:17699`)逐字對得上;「regen 章」的說法跟 `reference.md:634`「重建完蓋章」既有用語一致,不是新造詞;已讀,無 finding。
- **[S1][S3][S5][S7][S8][S9][S10]**:抽核跟現行 `_nodehome_key`/`_nodehome_homes`/`_impact_mark_about`/`_impact_knob` 慣例吻合,r1 G6/G7 已把「同一個函式」與旋鈕關閉時的回滾範圍收斂清楚,重查未見新增缺口;已讀,無 finding。
- **[S6]**(diff 聚合、派審查員圖譜參考、計劃模式三條路徑認家):三條路徑本身的分工敘述跟 `scripts/lumos:21935` 一帶的聚合邏輯、`dispatch-lens-hook.py` 的呼叫模式對得上;跟 lane 的互動缺口已併入 F4,不重複列。
- **[S12][S17]**(SOP 快查表/完整版兩處一致):對照 `skills/lumos-project-notes/commands/09-節點還原.md:10` 與 `reference.md:1094` 現況,兩處目前確實都只有起手式沒有「必要」字樣;現有測試 `t_nodehome_rules_in_hint_skill_and_discipline`(`scripts/test_lumos.py`)的驗法是逐檔關鍵字比對而非要求逐字相同,[S12]/[S17] 沿用同一種「兩處一致」不會把快查表撐成長文;已讀,無 finding。
- **[S13]**:`lumos new system` 沒帶 `--code` 多印提醒,落點雖沒被「落點」段明講,但 `scripts/lumos` 已在每支檔有家的 about_code 範圍內(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:9`),隱含歸屬清楚;已讀,無 finding。
- **範圍外、驗收怎麼跑(除 [S14] 外)、合約候選、審計修正紀錄**:逐項核對關鍵字都能對應到候選測試名(接續 r1 G12 已修的漏項),範圍外排除項與正文沒有互相矛盾;已讀,無 finding。

## 固定席逐條判(這份設計會不會破壞該節點宣稱的行為或合約)

- **Systems/retrieval-ranking**:`lumos contracts` 回「合約 0 條、技術債 1 條」(多詞片語回退,跟本案無關)。本案 S1–S10、S14、S16 動的正是這篇描述的排序機制,沒有機械合約可破,但如 F4 所述,新的「家」入口跟這篇 KEY 已經記載的「lane 參考道」(`scripts/lumos:21624` 一帶)互動沒交代——判「不算破壞既有合約(沒有),但落地後這篇的 KEY 需要同時講清楚家跟 lane 的關係,否則行為描述會跟現實脫節」。
- **Systems/每支檔有家**:`lumos contracts` 回「沒有登記任何『動了會壞』的合約」。S1/S11/S14/S15/S16 動的正是這篇管的判定機制,如 F2 所述擴大了它的違規種類卻沒同步「五種新違規」那行 KEY 與 S8–S10 的資料結構——判「不算破壞既有合約(沒有),但擴大了管轄範圍卻沒同步權威描述」。
- **Systems/節點還原**:`lumos contracts` 回「沒有登記任何『動了會壞』的合約」。[S12][S13][S17] 只改 SOP 文字與新增一道每支檔有家的檢查,不改機制本身——判「不影響」。
- **Issues/canary-record未落盤事件、code-loop守衛main-direct盲區、hook卸載殘留註冊、init-force-slug誤用basename、vendored測試套件在消費端假紅**:五篇 `lumos contracts` 都回「沒有登記任何『動了會壞』的合約」,主題各自獨立(canary 落盤/pre-push 盲區/hook 卸載殘留/init slug/vendored 假紅),只是因為本案驗收指令用到 `governance/eval/retrieval-goldset.json` 而被派工鏡頭撿到,跟家/about_code/regen 機制無關——判「不影響」。

## 實務隱患鏡頭(逐條想過)

- **效能(Edit 前推筆記在熱路徑上)**:有隱患,見 F5——[S16] 若字面實作成 hook 層自己掃圖譜全文做字串預篩,是熱路徑上一段沒被既有 30 秒/20 秒預算涵蓋的新增 I/O,跟「不花任何成本」的宣稱衝突。
- **噪音與召回的取捨**:這正是重開舊案要接住的核心,[S4]/[S5] 的加法設計本身站得住(見上「為什麼」段判讀);但如 F3 所述,[S14] 抽查沒有可重跑程序,「上線前抽查」目前只是一次性手動量測,比 spec 自己承認的「單次量測」天花板還低一層——沒有機制能保證 REVISIT 真的能重做。
- **舊專案相容**:additive-only 設計本身沒問題,沒填 about_code 的舊專案這條路徑不觸發、行為退回既有三軸;但如 F2 所述,[S11] 的新違規要怎麼在消費專案 `lumos update` 後被健檢看見沒有交代,存在「新增了擋、但沒人看得到對應舊帳提醒」的落差。
- **回滾(關掉旋鈕能不能完全回到原樣)**:[S7] `LUMOS_IMPACT_HOME=0` 與 [S11] 的 `node_home.gate` 各自獨立回滾,spec 自己講清楚且跟兩段各自的旋鈕慣例一致;F4 指出的 lane/家重複是「旋鈕開著時」的顯示問題,不是回滾機制本身的洞,回滾路徑沒發現新問題。

總結:最高 severity major,blocking 共 5 條
