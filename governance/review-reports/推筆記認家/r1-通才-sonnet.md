severity: major

### F1 dispatch-lens 的 spec 模式結構上看不到「家」
severity: major
blocking: 是 — spec 沒說 spec 模式要換路徑,實作者會照原句直接宣告完工,結果 spec 模式那半功能沒接上、[S6] 的測試對不到真正該改的程式碼。
引句:「派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家」
file: `scripts/lumos:23116` — `cmd_dispatch_lens_spec` 呼叫的是 `impact --file --json`,沒有帶 `--ranked`。
file: `scripts/lumos:21761-21766` — 非 ranked 分支的 JSON 只吐 `{file, direct, indirect, incidents}`,沒有 `results`/`pinned`/`about_hit`。
file: `scripts/lumos:21657` — `_impact_mark_about`(家的標記點)只在 `ranked or incidents_only` 分支裡才會被呼叫。
diff 模式(`cmd_dispatch_lens`)是走 `cmd_impact_diff`→`cmd_impact(ranked=True)`,確實會吃到家;但 spec 模式是另一條路,[S2] 把「家」接進 `impact --ranked` 融合區一句話蓋不到它。

### F2 重提的「新證據」跟自己講的門檻對不上
severity: major
blocking: 是 — Enzo 要靠這句話判斷「丙(第四條保送)」能不能重提,門檻寫「零」、證據卻是「幾乎沒有」,不修正這句話就是拿一個沒達標的證據去核准一個曾經被明文擋下的方向。
引句:「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」
引句:「三個 POS 專案整理後健檢 S8 幾乎沒有沒家的檔」
「幾乎沒有」不等於「零」,同一段話自己先立了「零」的門檻,下一句就承認沒有到。
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-11_每支檔有家落地.md:26` — 本工具鏈自己的圖譜健檢:沒有家的程式檔還有 43 支,列為「上線前的舊帳,只提醒」不是擋。
file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:34` — 每支檔有家本身的決定(d4)是「新違規擋、舊帳只提醒」,不是把漏標率清零;拿它當「漏標率壓到零」的證據,量的是不同的東西(有沒有家 vs. 家標得全不全)。

### F3 大檔門檻沒解決「合約射程」,舊案點名過的噪音源現在還在
severity: major
blocking: 是 — [S4] 自己講的目標是防「舊案 held 那題 22 誤放」,但機制沒解決舊案自己診斷出的根因,大檔(尤其是本案主戰場 scripts/lumos)照樣會把主題不相干的家灌進必推名單。
引句:「只有帶合約的家進必推,其餘家在可選名單照分數競爭」
[S4] 判「帶合約」用的是 `bool(contract)`,不分合約種類、也不管合約講的是不是被改的那段——這正是舊案自己點名「②合約的射程」是「最根本」卻沒解的缺口。
file: `scripts/lumos:21636` — 現有 indirect 路徑已經用 `LUMOS_IMPACT_HARD_PIN` 把「帶合約就保送」收窄成只認 INVARIANT/IRREVERSIBLE、RISK·* 類降參考道;[S4] 對「家」沿用的卻是沒收窄過的版本。
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:23` — 現存合約行講的是 CLAUDE.md re-inject byte-equal,不是泛指 scripts/lumos 任何一段。
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:90-93` — 這篇 about_code 含 scripts/lumos,是它 31 個家之一(機械重算,/tmp 乾淨 clone 跑 `_nodehome_homes` 驗證);同一批家裡 14/31 帶合約——舊案點名這篇是「四題都噪音」的實例,現在會因為是家而在任何一次改 scripts/lumos 時進必推。

### F4 驗收子集的 `-k` 清單漏了一支測試
severity: minor
blocking: 否 — 寫測試的人自己會發現要加關鍵字,不會做錯設計決定,但這是可機械驗的內部不一致,依規定仍要報。
引句:「子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`」
[S6] 列的測試候選是 `t_impact_diff_keeps_homes`,逐一比對「驗收怎麼跑」列的 8 個 `-k` 關鍵字(impact_home / impact_pins_order / dispatch_lens_includes_homes / about_stamp_no_longer / regen_node_requires / restore_sop_requires / new_system_without_code / impact_hook_shows_home),沒有一個是它的子字串——照單全跑「驗收怎麼跑」列的指令,這支測試永遠不會被執行到,清單卻宣稱涵蓋全部驗收項。

### F5 旋鈕關掉是不是真的「完全照原本」講不清楚
severity: major
blocking: 是 — 回滾是這次明講要審的鏡頭之一;旋鈕語意不清,實作者可能留著兩個互相覆蓋的旋鈕,或誤刪一個已經上線的功能當作「順便清乾淨」。
引句:「新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本)」
引句:「預標指紋不再影響推筆記」
[S9] 是不加條件的敘述(沒寫「僅當 knob=1」),讀起來是把舊的 about_hit 過期判斷永久拿掉;但 [S7] 又說 knob=0 要「完全照原本」——原本的行為包含過期判斷。這兩句要嘛互相矛盾,要嘛「原本」的定義被悄悄改成「沒有 about 訊號的三軸基線」,而這是個比「關掉這次新功能」更激進的退回,spec 沒有挑明。
file: `scripts/lumos:21275` — 既有旋鈕 `LUMOS_IMPACT_ABOUT` 現在還在管 about_hit 那套;新旋鈕 `LUMOS_IMPACT_HOME` 上線後這兩個旋鈕並存還是誰取代誰,全文沒提。
file: `scripts/lumos:1412` — doctor 的 Check S2(about_code_stamp 過期提醒)現在讀的正是 `LUMOS_IMPACT_ABOUT`;[S9] 把過期判斷從排序拿掉後,這段提醒是保留(變成純粹過期資訊)還是也跟著退場,spec 沒講。

### F6 regen 節點缺 about_code 要不要分「新違規/舊帳」,没有交代
severity: minor
blocking: 否 — 本工具鏈目前 0 篇節點帶 `regen:` 欄位(全庫查證,沒有立即衝突),風險落在消費專案身上,不是本 repo 眼前會炸的東西,但屬於明確可預期的落地缺口。
引句:「從程式重建的節點 about_code 至少要有一支檔;`lumos lint` 對這種節點缺 about_code 報錯」
同一週的姊妹計劃(每支檔有家)為了同一類問題(新規則上線前就存在的舊內容,要擋還是只提醒)走了 d1→d3→d4 三次裁決才定案;[S11] 完全沒有處理「這條規則上線前就已經蓋了 regen 章、卻沒填 about_code」的既有節點該怎麼辦,對走節點還原 SOP 的消費專案(這條規則的主要適用對象)是實際會踩到的情境。
file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:34` — 姊妹案的對應決定(d4):新違規擋、舊帳只提醒;[S11] 沒有引用或比照這條先例。

### F7 「同一個函式,不另寫一套」跟熱路徑成本的說法對不上
severity: major
blocking: 是 — [S1] 承諾重用既有函式,但那支函式的資料來源跟 Edit 前推筆記熱路徑現有的資料來源不同;照字面實作,要嘛多一輪 git 讀檔(拖進 hook 的 30 秒預算)、要嘛實作者自己另寫一套比對邏輯而違反 [S1] 的字面承諾。
引句:「家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套)」
引句:「既有的 about 計數已經有快取,本案沿用,不另掃一次」
file: `scripts/lumos:17995` — `_nodehome_homes(repo_root, side)` 吃的 `side` 是 `_nodehome_side` 建出來的快照,靠 `_nodehome_reader`(git index/tree)逐篇讀節點內容。
file: `scripts/lumos:398` — `cmd_impact` 用的 `Env(vault)` 是 `load_vault(vault)` 直接讀磁碟工作樹,跟上面是兩條不同的資料來源、不是同一份已載入的物件。
file: `scripts/lumos:21253` — 「既有 about 計數的快取」指的是 `_impact_about_counts`,只回 `{檔:篇數}`,沒有節點名單,不足以拿來當「家一定進必推名單」要用的入口清單——實務隱患段講的「沿用快取」只覆蓋巨檔門檻那一步,沒覆蓋找出「是哪幾篇」這一步。

---

已讀、無 finding 的段落:名詞;核心裁定甲的 S2(內容本身)、S3、S5、S8、S10;核心裁定乙的 S12、S13;範圍外;落點;實務隱患段的「寫錯的家」「評測尺量不到」「兩家一致」「不可逆、金流、對外寄送」四條;回頭條件(兩條都帶日期,符合鐵則四);合約候選。所有五個 wikilink 交叉引用(每支檔有家_計劃、retrieval-ranking、節點還原、check-j-regen-guard、固定席扇出降權_計劃)逐一開檔核對,目標皆存在。

## 背景查核:有沒有重蹈覆轍

舊案 r1 被打穿的具體錯誤是「降級」——about 命中改判自由席,把 2/9、3/5 的必看項主動踢出固定席。這份計劃讀過那次教訓:[S5] 明寫只加不降、[S2] 家的加入不影響既有三條路徑判定,機制上沒有重演「降級」那個坑。但重提本身依賴的評估("about 漏標率壓到零")本身沒被誠實對待——見 F2。另外舊案自己留下但沒解決的「合約射程」缺口,被這次的大檔安全網原樣繼承而不是重新面對——見 F3。方向上沒有走回頭路,但兩個舊案留下的作業(一個是門檻要誠實、一個是射程要收窄)都還沒真的補完,只是換了個包裝再出現。

## 固定席逐條判

- **Systems/retrieval-ranking.md**:會被寫回(落點段已排定),但摘要裡沒有 ★INVARIANT★/★IRREVERSIBLE★ 合約行(已查)——不影響它宣稱的行為,只是多記一段機制脈絡。
- **Systems/節點還原.md**:同樣是要被寫回的落點,現況沒有任何跟 about_code 衝突的既有規則——不影響。
- **Systems/check-j-regen-guard.md**:[S11] 在它的守衛家族裡加一條新檢查,不動 J-a/J-b/J-c/J-d 既有邏輯,也不改 `check_regen_provenance` 現有的簽名或回傳形狀——不影響既有合約,但引入方式(共用函式 vs 獨立檢查)沒寫清楚,已併入 F6 談。
- **Issues/canary-record未落盤事件.md、code-loop守衛main-direct盲區.md、hook卸載殘留註冊.md、init-force-slug誤用basename.md、vendored測試套件在消費端假紅.md**(五篇事故節點,經 `pitfall_when` 觸發):[S3][S5] 明文事故永遠排最前、不受家的加入影響——不影響。

## 實務隱患鏡頭逐項

- **效能**(Edit 前推筆記在熱路徑上):有隱患,見 F7——承諾重用的函式跟熱路徑現有資料來源不同源,字面實作有把 git 讀檔拖進 30 秒預算的風險。
- **噪音與召回的取捨**:有隱患,見 F3——大檔安全網用「有沒有合約」而非「合約管不管這段」篩選,舊案點名過的噪音源(lumos-cli-lifecycle 等)還在,且是 scripts/lumos 這個本案主戰場的家。
- **舊專案相容**:有隱患,見 F6——regen 節點缺 about_code 沒分新違規/舊帳,姊妹計劃走過同一類問題的三輪裁決沒被引用或比照。
- **回滾**(關掉旋鈕能不能完全回到原樣):有隱患,見 F5——新旋鈕 `LUMOS_IMPACT_HOME` 的「完全照原本」跟 [S9] 對舊 stamp 機制的無條件退場語意兜不攏,且沒講既有 `LUMOS_IMPACT_ABOUT` 旋鈕與 doctor Check S2 的去留。

總結:最高 severity major,blocking 共 5 條
