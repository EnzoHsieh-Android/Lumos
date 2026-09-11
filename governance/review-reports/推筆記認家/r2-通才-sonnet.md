severity: major

已讀完整份 136 行凍結稿(甲、乙、收尾、範圍外、落點、實務隱患、驗收、回頭條件、合約候選、審計修正紀錄),對照 r1-intake.md 的去重折入表逐條回查程式碼現況,並讀了舊案 `固定席扇出降權_計劃` 的 decisions 與 r1 被打穿段。五個 `[[wikilink]]` 全部存在,機械 refcheck 已跑過(0 條）故不重覆抽查裸路徑宣稱。以下先列三個固定席節點的逐條判,再列 findings,最後是實務隱患鏡頭逐類答覆。

## 固定席逐條判

- **Systems/retrieval-ranking**:不影響。本案只在既有「固定席」框架內新增第四種入口(家),不改 BM25F/融合分數/A1 先驗等既有排序公式或已凍結的評測數字;[S18] 已明文承認 `2026-08-24_about_code讀側四項落地` 會過期並要求新驗證紀錄逐篇交代,是誠實揭露不是破壞宣稱。
- **Systems/每支檔有家**:不影響。[S1] 明文重用該節點定義的純函式與 `_NODEHOME_HOME_STATUSES`/`_nodehome_key` 比對規則(已查證 `scripts/lumos:17988-18004` 邏輯與描述一致),推筆記端另建行程內查詢路徑、不碰該節點「不讀磁碟、提交索引直讀」的效能保證(`_impact_about_counts` 走 `env.notes`,不觸發 git);[S11][S15] 是在該節點既有「新違規擋、舊帳提醒」框架下加第 6/7 種違規,沿用同一開關 `node_home.gate`(`scripts/lumos:17743-17751` 確認存在),未新開一套機制。
- **Systems/節點還原**:不影響。[S12][S13][S17] 只補 `commands/09` 與 `reference.md` 第 4/6 步文字、`lumos new system` 的提醒,不改動七步驟本身或「規則五靠人工判斷落點」的既有邊界;新違規掛在每支檔有家而非節點還原自己,兩節點分工未被打破(已讀 `skills/lumos-project-notes/reference.md:1090-1104` 確認現況與 r1 判讀一致)。

### F1 [S16] 非程式檔字串預篩要求 hook 具備目前完全沒有的 vault 定位能力,且與「零成本」宣稱矛盾

severity: major
blocking: 是 — 照字面實作,implementer 得在 hook 裡新開一套 vault/Systems 掃描邏輯(或另外重複一份 `_vault_in`),沒有單源與飄移守衛,且每次非程式檔編輯都要真的做 I/O,不是「不花任何成本」。
1. `impact-hook.py` 現行 `_decide_one` 只靠副檔名/shebang 判斷是否呼叫 lumos,完全不知道 vault 或 `Systems/*.md` 在哪。
2. 找 vault 目前是 `scripts/lumos` 專屬能力,hook 端連「找不到 vault」的錯誤都要等 lumos 子行程回 rc3 才印,證實 hook 本身沒有這條路。
3. 「字串預篩」意謂 hook 要自己讀 `Systems/*.md` 找路徑字面命中,這是新增的重複邏輯,而本專案對這類重複一向要求「單源+飄移守衛」。

引句:「hook 先做字串預篩(Systems 節點原文裡有沒有這個路徑),有才叫 lumos,由家對照表做最終判定」

file: `scripts/hooks/claude/impact-hook.py:148-160` `_decide_one` 目前只用 `CODE_EXTS`/shebang 判斷,無任何 vault 或圖譜掃描邏輯
file: `scripts/hooks/claude/impact-hook.py:852` vault 找不到的訊息由 lumos 子行程回 rc3 才印,證實 hook 本身目前不解析 vault 位置
file: `scripts/lumos:14871` 唯一的 vault 定位函式 `_vault_in` 只存在於 `scripts/lumos`,不在 hook

### F2 [S8] 標頭改寫只修了一處,`lumos pitfalls` 與計劃模式(`cmd_dispatch_lens_spec`,[S6] 自己要改的同一支函式)仍留舊措辭

severity: major
blocking: 是 — 這正是 r1 外家 F11 抓過的同一種問題(必推裡混了「家」之後,講「都帶合約或事故」就不對),[S8] 只修了 `impact-hook.py` 一處,另兩個顯示同一資訊的路徑沒改,審查員/派工者照舊會誤讀「固定席=一定帶合約或事故」。
1. `lumos pitfalls` 送審前印的提示與「把固定席內容貼進派工詞」的指路文字,兩處都仍是「帶硬合約或出過事故」/「帶合約/事故的那幾篇」。
2. `cmd_dispatch_lens_spec` 就是 [S6] 明文要多印「家」頂層鍵、把家收進固定席的同一支函式,但它的訊息仍寫死「沒牽到任何帶合約/事故的節點」,家命中後這句話不準。
3. 該函式用來排序/分類 pinned 節點的 `_LENS_KIND` 字典只有 direct/indirect/incident 三種,沒有家/home 分類可用,[S6] 沒交代這裡怎麼收。

引句:「不再說每篇都帶合約或事故」

file: `scripts/lumos:19523` `lumos pitfalls` 送審提示仍寫「帶硬合約或出過事故的一定要看」
file: `scripts/lumos:19525` 同段「固定席(帶合約/事故的那幾篇)」措辭未同步
file: `scripts/lumos:23151` `cmd_dispatch_lens_spec`(計劃模式)訊息仍寫「沒牽到任何帶合約/事故的節點」
file: `scripts/lumos:22032` `_LENS_KIND` 只定義 direct/indirect/incident,無家/home 分類

### F3 名詞段「本工具鏈主程式有 31 個家」與 [S1] 自己引用的家定義算出來對不上,正確數字是 30

severity: minor
blocking: 否 — 只是舉例數字誤差一,不影響任何門檻(`LUMOS_IMPACT_ABOUT_MAX` 仍是 8)或測試斷言,實作不會因此做錯決定。
1. 機械核對 `Systems/*.md` 裡 `about_code` 精確等於 `scripts/lumos` 的節點共 31 篇,但其中 `canary-audit.md` 狀態是 `deferred`。
2. [S1] 明文重用的 `_NODEHOME_HOME_STATUSES` 只認 `doing/done/stale`,不含 `deferred`——照這個定義算,scripts/lumos 的家是 30 篇不是 31。

引句:「本工具鏈主程式有 31 個家」

file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:2-3` `type: system`、`status: deferred`,但其 `about_code` 仍列了 `scripts/lumos`
file: `scripts/lumos:17699` `_NODEHOME_HOME_STATUSES = ("doing", "done", "stale")` 明文排除 deferred

## 其餘各節逐一核對(已讀,無 finding,除非標出 F 編號)

- 為什麼(這批的來源):三條查證(about 非入口、指紋不寫入、舊案 d4 措辭)均與程式碼/舊計劃逐字對上;唯一數字誤差見 F3。
- 名詞(家/家對照表/必推/可選/大檔/從程式重建的節點/組裝檔):定義本身與 `_nodehome_homes`/`_nodehome_key` 一致,已讀無 finding(數字誤差已併入 F3)。
- [S1][S3][S4][S5][S7][S9]:已讀,無 finding——`_nodehome_homes` 讀取路徑(`env.notes[x].fields`)可支撐純函式抽取;pins 排序、大檔整批不進場、只加不降、旋鈕預設值、`about-code restamp/revert/migrate-stamp` 三指令均在程式碼中查證存在且語意相符。
- [S2][S6]:S2 本體(候選升格、去重、分數記 0)與現行 `pins/free` 分離、R1 直連保底(rescued)邏輯相容,已讀無 finding;S6 遺留的顯示文字缺口見 F2。
- [S8]:見 F2。
- [S10]:`--goldset`/`--split`/`--ablation`、`must_pinned`/`out_top3_must`/`pin_noise` 欄位在 `governance/eval/retrieval_eval.py` 均查證存在,已讀無 finding。
- [S14][S15]:兩者皆標 `[manual:…]`,協定完整、有 REVISIT,已讀無 finding(數值需實測,非可靜態查證項)。
- [S16]:見 F1。
- [S11][S12][S17][S13]:已讀,無 finding——`node_home.gate` 開關、`commands/09`/`reference.md` 現況、`lumos new system` 目前無此提醒,均與 spec 描述相符。
- [S18]:三篇待標 stale 的驗證紀錄(`2026-08-24_about_code讀側四項落地`、`2026-07-10_檢索排序v1`、`2026-07-11_檢索goldset評測`)均確認存在。
- 範圍外、落點、驗收怎麼跑、回頭條件、合約候選、審計修正紀錄:已讀,無 finding——驗收段 20 個 `[test:…]` 標籤全部被 14+1 個 `-k` 關鍵字子字串涵蓋(逐一核對通過,含 r1 G12 補回的 `impact_diff_keeps_homes`);四條回頭條件皆帶日期與具體動作,符合鐵則四。

## 實務隱患鏡頭

- **效能(Edit 前推筆記在熱路徑上)**:[S1] 的行程內快取設計可行(有 `_impact_about_counts` 同款先例);但 [S16] 的非程式檔字串預篩實際成本未算清楚,見 F1——這條在自陳的「零成本」與實作可行性之間有落差。
- **噪音與召回的取捨**:[S4] 大檔整批不進場確實照 r1 G2 的裁決閉環(不再靠合約分類,不會把舊案壓下去的搭便車噪音帶回來);但 F2 顯示「必推=帶合約或事故」的舊認知會在 `pitfalls`/計劃模式殘留,審查員可能低估家類必推項的重要性或誤以為每篇都該有合約級理由,間接影響審查召回品質。
- **舊專案相容**:沒跑 `lumos update` 的專案照舊、[S11] 只擋新蓋章節點,已讀無 finding,程式碼查證 `node_home.gate` 與健檢 S8 舊帳分流機制與描述一致。
- **回滾**:`LUMOS_IMPACT_HOME=0` 回到含舊「關於命中」的原本行為(S7/S9 已限定旋鈕範圍,查證一致);[S11] 靠 `node_home.gate` 關,是與既有每支檔有家共用的粗粒度開關而非獨立旋鈕,spec 已在實務隱患段自陳這點,不算隱藏落差。

總結:最高 severity major,blocking 共 2 條
