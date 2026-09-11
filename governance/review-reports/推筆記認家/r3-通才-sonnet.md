severity: major

### 名詞、核心裁定 [S1][S3][S4][S5][S7][S9][S10] — 已讀,無 finding
逐條與程式碼核對:`_nodehome_homes`(`scripts/lumos:17995`)只認 Systems 類 doing/done/stale 狀態,跟名詞段「家」定義一致;`_NODEHOME_HOME_STATUSES`(`scripts/lumos:17699`)與大檔門檻沿用 `LUMOS_IMPACT_ABOUT_MAX`(`scripts/lumos:21280`)也對得上;`about-code restamp/revert/migrate-stamp` 三個子指令都存在(`scripts/lumos:11356`、`:11393`、`:11439`)。[S9]「旋鈕關掉時舊關於命中照舊跑」與現行 `_impact_mark_about` 開頭的旋鈕早退(`scripts/lumos:21275`)一致。無 finding。

### [S2] 參考道折入驗收 — 已讀,無 finding
r1/r2 折入後的「已經是候選(含參考道)」寫法核對程式碼:`_impact_mark_about` 現在插在 `lane_raw` 填完、`lane_items` 截斷之前(`scripts/lumos:21657`,截斷發生在 `:21701` 之後)——照這個既有插入點接續實作,新函式自然拿到完整 `lane_raw`(未截斷),不會漏掉被 `LANE_N` 砍在顯示外的候選。折入有效,無 finding。

### [S6] 計劃模式排序、多檔聚合 — 已讀,無 finding
`cmd_dispatch_lens_spec` 的 `impact --file --json`(不帶 `--ranked`)輸出只有 `{file,direct,indirect,incidents}`(`scripts/lumos:21762`),`cmd_dispatch_lens`(diff 模式)直接吃 `cmd_impact_diff` 的 `results`/`pinned`(`scripts/lumos:22910`),`cmd_impact_diff` 目前的 `pins` 排序只有 `(-score, node)`(`scripts/lumos:21948`)、沒有 kind 分層——跟外家 F4/[S6] 描述的缺口一致,規格要求改寫這支排序鍵,三條路徑的接線點都存在且可行。無 finding。

### F1 check-graph-sync.py 的固定席措辭沒被列進 [S8] 的改寫範圍
severity: major
blocking: 是 — 不改,「家」單獨命中的節點被 impact --diff --sync-check 撈進 missing 清單時,check-graph-sync.py 仍會印出跟事實不符的原因(它不是合約也不是事故),跟 r1 已判 major 的 G13 是同一類缺陷。
引句:「其他講到固定席的地方一起改:風險掃描送審前的提示」
- file: `scripts/hooks/claude/check-graph-sync.py:600` `_impact_missing` 呼叫 `lumos impact --diff HEAD --sync-check --json`,吃的正是 [S6] 要改寫的同一份 pinned 結果,所以「家」單獨命中的節點會出現在這裡的 missing 清單。
- file: `scripts/hooks/claude/check-graph-sync.py:764` 印出固定字串「跟你改的程式碼直接相關(合約 / 事故 / 直接相依)」,枚舉的三種理由不含「家」,[S8] 只列了 `scripts/lumos:19523`/`:19525`/`:23151` 三處要改,沒提到這一處。

### [S8] 星號與種類表其餘位置 — F4
severity: minor
blocking: 否 — 只是空白標籤,不會讓人誤判理由,不影響決策。
引句:「顯示(旋鈕開著時):Edit 前推筆記的清單上」
- file: `scripts/lumos:21743` `cmd_impact` 的人讀(非 JSON)輸出的種類標籤字典沒有「家」這個 kind 的對應顯示文字。
- file: `scripts/lumos:21982` `cmd_impact_diff` 的人讀輸出用同一種字典寫法,同樣沒有「家」。
- file: `scripts/lumos:22032` 對照:`_LENS_KIND` 是 [S8] 明確承諾要加「家」的那份種類表,上面兩處是另外兩個沒被點名的種類表。

### [S11][S12][S13][S17] 乙、節點還原 — 已讀,無 finding
`_nodehome_parse_note`(`scripts/lumos:17905`)目前確實不讀 `regen` 欄,跟 r2 H6 抓到的缺口一致,規格明寫「節點解析多讀 regen 欄」;`becomes_home` 判法(`scripts/lumos:18232`)是既有可重用的「這篇這次才成為現況」比對寫法,[S11]「新蓋章」判法照抄同一種形狀,技術上站得住。`node_home.gate`/`node_home.ignore` 都是 `_nodehome_config`(`scripts/lumos:17707`)已有的設定鍵。`commands/09-節點還原.md`、`reference.md:1080` 目前確實只寫「起手指令」沒寫「必要」也沒有檢查,跟「為什麼」段的宣稱一致。Check J 只掃摘要行(`reference.md:1100`)、不驗 regen,`[S11]`「不動 Check J」的理由站得住。無 finding。

### [S14][S15][S16] — 已讀,無 finding
`home_audit.py` 是全新檔案,依規則不算未定義。[S16] 「hook 只看副檔名/shebang、不讀圖譜」核對 `_decide_one`(`scripts/hooks/claude/impact-hook.py:143`)屬實,H1 折入後的收窄寫法與現況一致。

### F2 範圍外段的連結指向不存在的節點
severity: minor
blocking: 否 — 這個 Issue 節點本來就標「另一個提交修」,不影響本案要動的程式;只是文件裡的懸空連結。
引句:「每支檔有家的漏洞,另一個提交修,見」
- file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md` 這篇節點不存在——`find`/全庫 `grep -rl` 都掃不到,只有計劃與席報告文字裡提過這個名字,節點本身從沒被開過。

### F3 [S18] 的「共六篇」在今天重跑同一條指令會多一筆
severity: minor
blocking: 否 — [S18] 自己已經寫了「上線當下再跑一次那條指令,多出來的也照辦」,這條政策本身就能接住這個漂移,不會讓實作者做錯決定。
引句:「lumos stale --candidate --match 固定席 2026-09-12 實跑多掃到的三篇」
- file: `docs/lumos-toolchain-knowledge/Verification/2026-08-22_受波及合約測試真跑閘落地.md:6` 今天實跑 `python3 scripts/lumos stale --candidate --match 固定席` 除了 spec 點名/掃到的五篇之外,還多印出這一篇(狀態已是 `stale`,不是本案會讓它失效的「既有 pass」,但確實不在 spec 列的名單裡)。

### F5 「為什麼」段「四條路」與實際列出的項目數對不上
severity: minor
blocking: 否 — 這句在背景敘述段,不是規格條款,不影響要蓋什麼;純粹是讀者會被這個數字卡住。
引句:「決定推哪幾篇的只有四條路」
- 同一句接著只用頓號列出三項(正文反引號路徑、沿連結往外擴、事故觸發條件),跟「四條路」字面對不上;若是把「完整路徑」與「裸檔名比對」算成兩條,又跟舊案(`docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:145`)把它們稱為「材料只有一種」矛盾——兩種讀法都通不過,文字本身沒有交代是哪一種算法。

### 收尾、範圍外(其餘)、落點、驗收怎麼跑、回頭條件、合約候選、審計修正紀錄 — 已讀,無 finding
六篇驗證紀錄(About_code讀側四項落地、檢索排序v1、檢索goldset評測、標籤結構收編落地、edit面查詢品質閘落地、標註刷新落地)除 F3 提到的一篇外全部存在;`落點` 段五個 wikilink 除 F2 外全部存在;`驗收怎麼跑` 逐一核對十五個 `-k` 關鍵字對十八個 `[test:]` 標籤,全部能用子字串比對收到(G12 的折入確實補齊,無新漏)。四條 `REVISIT:YYYY-MM-DD` 都獨立成行、緊鄰原句,符合鐵則四的格式。

## 固定席逐條判(r3-lens.txt)

1. **Systems/retrieval-ranking** — 不影響:該節點目前 0 條合約行,本案只在既有 pins 排序上新增一種 kind 並改寫 stable sort 鍵,不動 BM25F/融合公式,也不改已記錄的 P@8/nDCG 數字;本案還會把這篇列為落點,屬計劃內既定的文件更新,不是意外破壞。
2. **Systems/每支檔有家** — 不影響:0 條合約行;其 KEY 行「五種新違規」與「家對照表算法」正是本案要在同一次提交改寫的落點,屬預期更新而非破壞;唯一數字風險見 F3。
3. **Systems/節點還原** — 不影響:0 條合約行;是乙案明寫的落點,SOP 第 4/6 步的改寫是設計目標本身。
4. **Issues/canary-record未落盤事件** — 不影響:`pitfall_when` 觸發字串是 `content:canary record`,跟 `governance/eval/retrieval-goldset.json` 的關聯只是該檔內容裡巧合含有這個字串,本案不改這個事故描述的失效場景(canary 記錄落盤)。
5. **Issues/code-loop守衛main-direct盲區** — 不影響:觸發字串是 `glob:scripts/hooks/pre-push` 與 `content:code-loop check`,跟本案的 impact/家對照表邏輯是不同的檢查面,本案不改 pre-push 對 main 分支的守衛邏輯。
6. **Issues/hook卸載殘留註冊** — 不影響:觸發字串 `content:HOOK_ENTRIES`/`content:_install_hooks_py`,講的是安裝器殘留登記,跟推筆記排序無關。
7. **Issues/init-force-slug誤用basename** — 不影響:觸發字串 `content:_slugify_vault`/`content:def cmd_init`,講的是 `lumos init` 的 slug 判定,本案不碰這支函式。
8. **Issues/vendored測試套件在消費端假紅** — 不影響:觸發字串 `content:_VENDORED_TOOLKIN`(`_VENDORED_TOOLKIT`),講的是消費端假紅,跟本案的讀側排序無關;這五篇事故都是因為 `governance/eval/retrieval-goldset.json` 內嵌歷史 code 片段被觸發字串巧合命中(`scripts/lumos:21787` 附近的註解已明講這個已知現象),不是本案邏輯真的牽動它們描述的失效場景。

## 實務隱患鏡頭

1. **效能**(Edit 前推筆記在熱路徑上):spec 自己給的 30 秒/20 秒數字跟 `scripts/hooks/claude/impact-hook.py:61/64/794` 對得上(r1 已核實);家對照表承諾行程內快取、不讀 git,跟既有 `_impact_about_counts`(`scripts/lumos:21253`)同款寫法一致。無新增隱患。
2. **噪音與召回的取捨**:spec 自己的「噪音變多」段已誠實列出 8 家門檻沿用舊值、REVISIT 排了重校時間;沒有隱藏這個代價。無新增隱患。
3. **舊專案相容**:沒跑 `lumos update` 的專案照舊、[S11] 只擋新蓋章節點——跟 `_nodehome_evaluate` 現有的「新舊分流」寫法(`scripts/lumos:18229` 一帶)是同一套邏輯,可信。無新增隱患。
4. **回滾**:`LUMOS_IMPACT_HOME=0` 的字面路徑跟現有 `LUMOS_IMPACT_ABOUT=0` 的早退寫法(`scripts/lumos:21275`)完全同款,`node_home.gate` 也是既有可用鍵;可信能回到原狀。無新增隱患。

總結:最高 severity major,blocking 共 1 條
