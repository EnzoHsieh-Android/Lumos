severity: major

### F1 重開丙案的依據只回應了舊決策一半的理由
severity: major
blocking: 是 — 沒處理,人裁時只看到「漏標率」被推翻,看不到舊決策同一句話裡「評測尺是死表」的那一半仍然成立,等於用半個理由否決了一個雙理由的決策。
- 舊案 d4 的擱置理由是兩件事合起來:①about 漏標率沒壓到零 ②即使壓到零,「必看 15/69 坐固定席、前 3 席組成幾乎不變,觀測一個月只會得到水平線」是死表。本案「為什麼」段只回應①(改成「只加不降」+上線抽查),完全沒回應②。
- 本案自己的實務隱患「評測尺量不到」段承認的正是②同一個症狀:主程式是大檔、家對它沒作用,自由席必看是計劃/驗證紀錄、家碰不到——但這段沒有回頭承認「這就是舊案說的死表」,讀者看不出兩者是同一件事。
- 引句:「標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有作用」
- file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:35` — d4 context 原句「必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變,觀測一個月只會得到水平線」,本案未回應這半句。

### F2 [S11] 新違規對「新開的」regen 節點多半是重複既有守衛
severity: major
blocking: 是 — 照字面實作,實作者會以為補了一個洞,但對最常見的「新開節點」情境其實什麼都沒多擋,真正補到的窄範圍(既有節點事後補蓋 regen 章、about_code 之後才變空)沒有被點名也沒有對應測試候選,補的東西補錯地方。
- 現行 `每支檔有家` 對「新開的,或這次才從 planned/deferred 轉成 doing/done/stale」的 Systems 節點,已經無條件要求 `responsibility` ≥10字有實字,完全不看 about_code 是否為空。
- 這代表 [S11] 描述的「新開的 regen 節點沒 about_code 又沒負責範圍 → 擋」對新開節點來說,今天就已經被擋,不需要本案。真正還沒被蓋到的窄案例是「既有節點這次才第一次蓋 regen 章、且 about_code 這次才變空、但沿用了舊的(非空但沒解釋不管檔理由的)負責範圍文字」——這種案例才是唯一會被新機制多擋下的東西,但 spec 的說明語氣(「新開的,或這次才加上章的」)沒有把讀者導向這個窄案例,列出的三個 test 候選名字也看不出鎖定它。
- 引句:「about_code 是空的、也沒寫負責範圍講明它為什麼不管檔 → 擋」
- file: `scripts/lumos:18317` — `becomes_home = n["status"] in _NODEHOME_HOME_STATUSES and (b is None or b["status"] not in _NODEHOME_HOME_STATUSES)`;`if b is None or becomes_home: if not _nodehome_resp_ok(n["resp"]): blocks.append(("new-node-resp", …))`,判定不看 about_code。
- file: `scripts/test_lumos.py:37158` — `t_nodehome_check_blocks_new_node_without_responsibility` 已經釘住「新節點沒負責範圍 → rc1」,fixture 甚至帶著 about_code 一樣被擋。

### F3 單家判定沒有機制攔「錯判為是」,「錯誤率」量不到它
severity: major
blocking: 是 — 不改,上線閘門會用一個結構性只看得到「已經被懷疑」那一半的錯誤率數字,去核准一個「全部配對」的品質保證,審查員系統性偏寬鬆時會直接漏放。
- 抽查流程只把「否」與「判不準」送給 Enzo,判「是」的配對完全不會被人看第二眼;「錯誤率=人裁確認判錯的配對÷總配對」這個分母包含全部配對,但分子只可能來自那個會被送審的子集。
- 舊案原本的雙評審設計是兩家都判、同值才算過,不同值才變成要人裁的「disputed」——換句話說,舊機制裡「一家判是、另一家判否」這種情況會被攔下來給人看;單家判定把這條攔截路徑整個拿掉,不是「獨立性降一級」這麼輕,是「這一類错误的唯一防線消失」。
- 引句:「判錯的超過一成就先修家、再上線;逐對結果與錯誤率寫進驗證紀錄」
- file: `governance/eval/refresh_labels.py:219` — `cmd_merge` 現行邏輯:「一致(同值)→agreed;不一致→disputed」,disputed 才送人裁——本案沒有第二家提供「不一致」訊號,判「是」的配對不會有機會變成 disputed。

### F4 「只加不降」的承諾沒覆蓋既有 about_hit 的排序加成
severity: minor
blocking: 否 — 影響的是固定席內部顯示順序,不影響任何項目在不在必推名單,不會讓實作者做錯安全性判斷,但會讓一小撮既有節點的排序在使用者沒被告知的情況下退步。
- 現行 stable sort 鍵是 `(kind != incident, not about_hit)`,任何 about_code 命中目標檔的候選都會被排到同類其餘節點之前,不分「確認過」與否。
- S9 說旋鈕開著時舊的「關於命中」整段不跑;S5「只加不降」只講「不因為不是家而被降」,講的是 pinned/free 的去留,沒有講排序。結果是:一個 about_code 命中但过不了新「確認」測試(比方只寫得出主檔名)的既有候選,今天有 about_hit 排序加成,上線後會悄悄失去它,退回其餘同類原序——這正是「降」,只是降在排序而非去留,現有四個合約候選都沒蓋到這一種。
- 引句:「預標指紋不影響推筆記;`about-code restamp/revert/migrate-stamp` 指令與健檢的指紋過期提醒保留」
- file: `scripts/lumos:21746` — `pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))` 是唯一決定「同為必推、誰排前面」的鍵,S9 讓這條鍵背後的計算整段不跑。

### F5 「43 支沒家的舊檔」與本次唯讀重算的 44 支對不上
severity: minor
blocking: 否 — 不改變論證方向(不管 43 或 44,都支持「舊前提沒達到」這句話),純粹是數字對不上現況,換算或抓取時間點的差異,不影響任何實作決策。
- 引句:「本工具鏈自己還有 43 支沒家的舊檔」
- file: `scripts/lumos:2125` — 本次在乾淨唯讀副本(`/tmp/lumos-review-check`,由本次審查建立、只讀不寫)跑 `python3 scripts/lumos doctor`,這行印出「有 44 支是上線前就在、還沒有家的舊檔」,不是 43。

---

## 逐節讀完覆蓋(未列 finding 的段落)

- 為什麼(這批的來源)其餘部分:已讀。查證「三條路+about_code 不是入口」的現況敘述、`_impact_reverse_lookup`/`_impact_contract`/`_impact_bfs` 分工說法,與現碼相符,無 finding。
- 名詞:已讀。「31 個家」「115 對/109/4/2」等數字內部加總一致(109+4+2=115),與 `_nodehome_homes`/`_nodehome_key` 現碼演算法對得上(含容易漏算的純量寫法 `about_code: scripts/lumos`),無 finding。
- [S1][S2][S3][S4][S5][S6][S7][S8]:已讀。與 `_impact_mark_about`、`lane_raw`/參考道、`cmd_impact_diff` 的 merge 邏輯(`merged[x["node"]] = {**x, "files": cur["files"], "pinned": pinned}` 只留 files/pinned)、`cmd_dispatch_lens_spec` 呼叫不帶 `--ranked` 的 `impact --file --json`(回傳形狀 `{direct,indirect,incidents}`)逐一核對,描述與現碼行為相符,無 finding。
- [S10]:已讀。`--goldset`/`--split`/`--ablation`、`_macro`、`must_pinned`/`pin_noise`/`out_top3_must` 皆存在,「不帶 --split 跑全體/練習/保留三組」與 `splits = [args.split] if args.split else [None, "train", "held"]` 相符,無 finding。
- [S15][S16]:已讀。`_impact_diff_seed_ok` 現碼確實排除 `.jsonl`/`.md`/`governance/*.json`,「寫成 .md 的檔家不會被波及計算推出來」屬實,無 finding。
- [S12][S13][S17]:已讀。`lumos new system` 的 `--code`/`--responsibility` 旗標存在;`commands/09-節點還原.md` 與 `reference.md` 第 4 步現況確實只是示例寫法、沒有標「必要」也沒有機械檢查,與 spec 描述相符,無 finding。
- 收尾 [S18][S19]:已讀。點名三篇加指令掃出三篇,與派工鏡頭附件裡「超出上限只列名」名單中出現的三篇 Verification(`2026-07-10_檢索排序v1`、`2026-07-11_檢索goldset評測`、`2026-08-24_about_code讀側四項落地`)吻合,無 finding。
- 範圍外、落點:已讀,三個落點節點(`Systems/retrieval-ranking`、`Systems/每支檔有家`、`Systems/節點還原`)均存在,無 finding。
- 驗收怎麼跑:已讀,指令格式與既有腳本慣例(`test_lumos.py -k`、`retrieval_eval.py --goldset/--split/--ablation`)一致,無 finding。
- 回頭條件、合約候選:已讀,五條 REVISIT 均帶日期與可執行指令,四條合約候選與兩級機制敘述一致,無 finding(F4 提到的排序退步未被任何合約候選覆蓋,已在 F4 記)。
- 審計修正紀錄:歷程記錄,不重複覆核前幾輪已折入的項目。

## 固定席逐條判

- **Systems/retrieval-ranking**:會被改到——`cmd_impact` ranked 融合區塊是這篇管的核心機制,本案直接加排序鍵與新旋鈕。但改法是「只加不降」+獨立旋鈕(`LUMOS_IMPACT_HOME=0` 完全回到現況),這篇現有 TEST 清單(`t_tokenizer/impact_ranked/impact_diff` 等)不會翻紅,只需要落地後補列新測試——不破壞它現在宣稱的行為。
- **Systems/每支檔有家**:會被改到——[S1] 要把它的家對照表算法抽成共用純函式,[S11] 建在它的違規清單上。抽成純函式不改變它「只看欄位值、不看預標指紋」的既有合約;[S11] 本身有重疊問題,見 F2,但不影響這篇既有的五種違規判定。
- **Systems/節點還原**:不影響——這篇是手寫方法論節點,`about_code: []`、沒有 `regen` 章,不落入 [S11] 的新違規範圍;[S12][S17] 改的是 SOP 文件(`commands/09`、`reference.md`)本身,不改這篇 System 節點的欄位要求。
- **Issues/各棧測試資料夾被當成要家**:不影響——這篇講的是「哪些檔可以不必有家」(排除規則),跟本案「有家的檔怎麼被推、家怎麼分級」是兩層不同的問題,沒有交集。
- **Issues/canary-record未落盤事件**:不影響——講 canary 紀錄寫後自驗,跟讀側排序/家分級無關;會被鏈進來純粹因為 `pitfall_when` 字面命中本案要碰的 `governance/eval/retrieval-goldset.json`。
- **Issues/code-loop守衛main-direct盲區**:不影響——講 pre-push 的 code-loop tier 判定用 merge-base 在 main-direct 情境失效,跟 `cmd_impact` 排序機制無關,同樣是字面命中鏈入。
- **Issues/hook卸載殘留註冊**:不影響——講 hook 安裝/卸載的登記對稱性,與本案機制無關,同樣是字面命中鏈入。
- **Issues/init-force-slug誤用basename**:不影響——講 `lumos init --force` 的 slug 判斷 bug,與本案機制無關,同樣是字面命中鏈入。
- **超出上限只列名的其餘 15 篇**:多數是 `scripts/lumos` 的其他既有家(31 個家遠超巨檔門檻 8,[S4] 明文巨檔不當入口、只加顯示標記),不受本案影響;其中 3 篇 Verification 正是 [S18] 自己點名要處理的舊驗證紀錄,屬於計劃已排入清單的已知影響,不是遺漏。

## 實務隱患鏡頭(逐類)

- **效能(Edit 前推筆記在熱路徑上)**:有——[S1] 明講家對照表從已載入圖譜算、行程內快取、不讀 git、不開子行程,同一份快取邏輯與既有 about 計數共用;唯一新成本是全庫一次性建表,量級與現有 `_impact_about_counts` 相同。可信。
- **噪音與召回的取捨**:有——分兩級(只有確認過的家保送)+大檔門檻(8+ 個家不當入口)+顯示標記(可選名單裡的家只標不升)三道一起限縮噪音面;殘留風險(填錯但被確認的家)已被實務隱患段誠實列出,配 [S14] 抽查與 [S15] 提醒兩道殘餘防線——但 [S14] 的殘餘防線有 F3 講的結構性盲區,是本輪最需要回頭看的地方。
- **舊專案相容**:有——沒跑 `lumos update` 的專案完全不受影響;跑過的專案裡,[S11] 只擋「新蓋章」的節點,舊還原節點只進健檢舊帳提醒不擋,不會讓既有專案一夕變紅。
- **回滾(關掉旋鈕能不能完全回到原樣)**:有——`LUMOS_IMPACT_HOME=0` 明文包含「舊的關於命中」的完整復原(照舊排序與顯示 ★關於★),[S11] 另有獨立開關 `node_home.gate`;兩個旋鈕各自關各自的功能,沒有交叉依賴問題。

總結:最高 severity major,blocking 共 3 條
