severity: major

### F1 [S14] 驗收怎麼跑仍寫「兩家族各判一次」,跟同一份 spec 改成一家判的裁定互打
severity: major
blocking: 是 — 照字面「驗收怎麼跑」操作,實作者會誤以為還要等 Codex 額度恢復湊滿兩家才能收工,跟 Enzo 已裁的「一家判、額度不等」直接衝突。
引句:「由一家(Claude)的審查員逐對判」
引句:「清單,兩家族各判一次後」
1. [S14] 本文與回頭條件都明確改成「一家(Claude)判,Codex 額度恢復後要不要補第二家由 Enzo 裁」,但「驗收怎麼跑」段落原句未同步改,仍寫「兩家族各判一次後」與 `tally <判定一> <判定二>` 兩個判定檔參數。
2. 這正是這一輪要審的兩處改寫之一在文件裡漏改的殘留舊說法,不是無關筆誤。

### F2 大檔舉例的家數「31」跟被引用的權威節點自己記的「30」對不上
severity: minor
blocking: 否 — 兩個數字都落在 `LUMOS_IMPACT_ABOUT_MAX`(預設 8)門檻之上,不影響大檔判定或任何決策分支。
引句:「本工具鏈主程式有 31 個家。」
1. 名詞段「大檔」定義與範圍外段落兩處都寫「本工具鏈主程式有 31 個家」,但本案自己說家的定義照 `[[Systems/每支檔有家]]`,那篇天花板 KEY 行寫的是「本工具鏈主程式有 30 篇」。
2. file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:29` 天花板 KEY 行明寫 30 篇；我用同一套「type:system、狀態 doing/done/stale、about_code 含 scripts/lumos」規則手動掃過整個圖譜也得到 30,跟 spec 的 31 對不上。

### F3 [S11] 新違規跟既有「新開節點沒寫負責範圍」違規重疊,「五種改六種」的算法沒交代清楚
severity: major
blocking: 是 — 對「新開的」regen 節點,兩條判定會同時命中同一件事,實作者若不處理去重,擋下訊息會把一個問題報成兩條、且「六種」的計數基準本身站不住。
引句:「同一個提交改成六種。」
1. file: `scripts/lumos:18318-18320` 現有 `new-node-resp` 違規:只要是新節點或這次才變成家狀態,沒寫負責範圍就擋,不管 about_code 或 regen 欄位——這條件是 [S11] 描述的「about_code 空、也沒寫負責範圍」的超集,對「新開的」regen 節點兩者必然同時觸發。
2. [S11] 真正補到的缺口只有「這次才加上章的」(狀態沒變、只加 regen 欄)這個子案例,spec 沒有點名這個重疊、也沒交代兩條要不要合併顯示。
3. 每支檔有家.md 現有 KEY 行本身把「新開節點沒寫負責範圍」列在五種之外(用分號另起、「也擋」),可見基線就不只五種,「改成六種」這個算法本身沒有先核對基線。

### F4 [S8] 改了固定席的用語,但落點段沒交代 retrieval-ranking 自己 FLOW/CLI 說明文字要同步改
severity: major
blocking: 是 — 上線後 retrieval-ranking.md 自己記的 FLOW 與 CLI 說明仍寫「固定席=事故+合約」,下一個照這篇筆記做事的人會誤判固定席只有兩種來源。
引句:「改檔前推筆記的排序本來就記在這篇」
1. file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:14` FLOW 行寫「impact --ranked(固定席=事故+合約...)」，`:51` CLI 段寫「固定席降噪」，都只講兩種來源。
2. 落點段只承諾把 Edit 前推筆記那支 hook 檔加進 about_code(簿記動作),沒有一句要求同步改寫這兩處既有敘述,等於本案自己會製造「文件與現實對不上」。

### F5 [S12] 「寫進 node_home.ignore 並說明理由」在現有結構下做不到
severity: major
blocking: 是 — ⚠ 判不準:實作者最可能把「理由」塞成清單項的一部分(例如物件或帶註解字串)去滿足「說明」,但現有解析會把非字串項整條丟掉且只印警告,等於那個檔根本沒被排除,行為跟預期相反。
引句:「寫進專案設定 `node_home.ignore` 並說明理由」
1. file: `scripts/lumos:17762` 與 `:17768` 現有邏輯明講 `node_home.ignore` 只認字串清單,非字串項「略過這一項」(靜默失效,不擋)。
2. spec 沒說「理由」要寫在哪(commit message?節點負責範圍?新 schema 欄位?),這個字串清單完全沒有掛「理由」的位置。

### F6 範圍外段引用的 Issue 描述成「待另一個提交修」,但那篇筆記自己記著同日已 resolved
severity: minor
blocking: 否 — 這篇 Issue 本來就不在本案動手範圍內,敘述時序不準不會讓實作者去重做或漏做任何本案要交付的東西。
引句:「每支檔有家的漏洞,另一個提交修」
1. file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md:3` `status: resolved`，`:24` 「✅ 已修正(2026-09-12):...修正、測試與這篇在同一個提交」。
2. spec 範圍外段用未來式「另一個提交修」點名這篇當作排除理由,但它跟 spec 同一天已經修完並收案,措辭該改成「已由另一個提交修過」,避免三個月後的接手人以為這還是待辦。

## 逐節讀完、其餘無 finding 的部分
- 名詞、甲(S1–S10、S14–S16 除上列外)、乙(S13)、收尾(S18 除上述外、S19)、實務隱患、驗收怎麼跑(除 S14 一行)、回頭條件、合約候選、審計修正紀錄:已讀,無 finding。
- [S8] 逐條核對過 `scripts/lumos` 裡「帶硬合約或出過事故的一定要看」「帶合約/事故的那幾篇」「合約 / 事故 / 直接相依」「沒牽到任何帶合約/事故的節點」四句現行文字,全部逐字存在,改寫有本可依。
- [S6] 派工鏡頭計劃模式確認呼叫 `impact --file --json`(不帶 `--ranked`),跟 spec 描述一致(`scripts/lumos:23198` 附近的 `cmd_dispatch_lens_spec`)。
- [S18] 實跑 `lumos stale --candidate --match 固定席` 核對:確認「重驗條件沒寫固定席字樣」的說法屬實(--candidate 只掃 revalidate_when,`檢索排序v1`/`檢索goldset評測`的 revalidate_when 確實沒有這個詞),六篇總數與逐篇判斷邏輯站得住。

## 固定席逐條判(這份設計會不會破壞該節點宣稱的行為或合約)
- **Systems/retrieval-ranking**:不影響其排序合約(只加一條入口、旋鈕可完全回退、不動分數公式);唯其 FLOW/CLI 說明文字會因此過期(見 F4)。
- **Systems/每支檔有家**:不影響其既有違規判定行為,本案是在它自己的職責範圍內擴充([S1] 抽算法共用、[S11][S15] 加新項),擴充跟既有項的關係需講清楚(見 F3)。
- **Systems/節點還原**:不影響任何機械檢查(它本就聲明「regen 章是宣告制,不蓋完全繞過」),本案只改 SOP 文字。
- **Issues/canary-record未落盤事件**:不影響——它的觸發字串(canary record 落盤)跟本案的 about_code/家/regen 判定完全不重疊,只是共同連到 retrieval-goldset.json 才被列出。
- **Issues/code-loop守衛main-direct盲區**:不影響——觸發字串是 pre-push tier 判定,跟本案改動面不重疊。
- **Issues/hook卸載殘留註冊**:不影響——觸發字串是 hook 安裝/卸載註冊,跟本案不重疊。
- **Issues/init-force-slug誤用basename**:不影響——觸發字串是 `cmd_init`/`_slugify_vault`,跟本案不重疊。
- **Issues/各棧測試資料夾被當成要家**:對它既有修法不影響(邏輯不重疊),但本案引用它的時態有誤(見 F6)。

總結:最高 severity major,blocking 共 4 條
