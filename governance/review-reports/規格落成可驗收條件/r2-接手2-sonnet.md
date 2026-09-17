severity: major

# 外部審稿報告——規格落成可驗收條件_計劃(r2)

## 逐節審查

### Frontmatter / decisions(d1–d10)
已讀。數字已重新機械查證:當前 `docs/lumos-toolchain-knowledge` 開頭欄位 `- risk/<值>` 命中 34 篇(守衛面 29、不可逆 5、金流 0、對外送出 0),與 d9 所述一致,量法（只認開頭欄位）也照實作方式可重算。無 finding。

### 為什麼(數字)/ 兩層要分開
已讀,無 finding。

### 一、門怎麼判
已讀。已排除行跳過規則、四類詞彙對照表與硬單向門訊號 2(合約行掃描)在本節文字裡交代清楚,與 r1 折入紀錄一致。無新 finding。

### 二、條款句式
1. **finding**:文法本身極寬鬆——「回應」段沒有子文法限制內容,只要求含「應」與不以 當/在/若/若啟用 開頭,這代表機械檢查實質上只驗「有沒有觸發詞前綴」與「有沒有『應』字」,連 S19「CI 紅但失敗步驟不是測試,逃逸帳**不應**多一筆」這種否定語句也能無障礙通過(「不應」字面含「應」)。文件宣稱「一條文法」聽起來收斂,但實際可過檢的句子空間非常大,這點沒有在文中誠實寫出(誠實界線節只講「驗形狀不驗意思」,沒有指出「形狀」本身有多鬆)。
severity: minor
blocking: 否(不影響機制本身的正確性,只是「文法很嚴謹」的印象與實際寬鬆度有落差,值得補一句誠實描述,但不阻礙實作)

### 三、綁定規則
已讀,無 finding。「雙向門不准 [manual:]」「keeps 標記」「測試名互異」在本節與第四節銜接一致。

### 四、新閘 `lumos spec-gate`
2. **finding**:S8「處置閘第五步應呼叫與規格閘同一支條款檢查器,兩邊對同一份計劃給出相同判定」與第三節「雙向門不准 [manual:]、單向門 [manual:] 照舊」矛盾——同一支檢查器要嘛對 manual 有一致行為、要嘛得吃「門」當參數才能對雙向門拒 manual、對單向門收 manual。目前 `_disposal_clause_step`(`scripts/lumos:15708`)完全不知道門的概念,只驗「有沒有標 [test:]/[manual:]」,S8 沒有講清楚共用檢查器要新增哪個參數、也沒講「相同判定」在 manual 政策不同時要怎麼定義。
severity: major
blocking: 否(這是實作介面細節,設計方向本身可行,但落地前必須先把「同一支檢查器」的介面契約寫清楚,否則兩個呼叫點會各自量產不一致行為)

3. **finding**:S8 落地時 [[Systems/design-loop]] 的 ★INVARIANT★ KEY 行(目前見 `docs/lumos-toolchain-knowledge/Systems/design-loop.md:39`,內容細到 `_visible_lines`/`_strip_inline_markup`/清單前綴判定等實作級描述)必須整段重寫,但 spec 只說「要綁測試加審計」,沒有講新文字要包含哪些不變量、也沒有指名綁哪一支測試(現有測試是 `t_disposal_clause_gate`,新文法/keeps/manual 禁令是否沿用同一支測試名、還是要新開,完全沒交代)。這正是派工詞問題④的核心,三個月後的實作者拿不到具體指引,只能自己猜這段 KEY 怎麼寫。
severity: major
blocking: 否(不阻礙設計方向,但屬於「S8 落地前必須先決定」的事項,建議在動手前先把新 INVARIANT 文字與綁定測試名寫進計劃)

4. **finding**:推送閘改讀「所有仍 doing 的雙向門 spec-gate 留痕」的 [test:] 清單(第四節末段、S21),但沒有處理「PASS 記錄之後計劃被編輯(條款改名/新增/刪除測試)」的情況。已驗證 `_door_for_loop`(`scripts/lumos:7479-7494`)是讀 `.canary-log.jsonl` 裡**最後一筆** `kind=spec-gate` 記錄,不是重新讀活檔——照同一模式,S21 若也取「最後一筆記錄」的 [test:] 清單,計劃編輯後若未重跑 `spec-gate`,推送閘會繼續對已改名/不存在的舊測試名下手,可能造成假性擋推(測試名跑不到)或漏檢(新條款沒進清單)。spec 全文(第四、五節)都沒有回答「編輯計劃後何時該重跑 spec-gate、誰來偵測記錄已過期」。
severity: major
blocking: 否(這是可預期的常見操作路徑——雙向門計劃在 PASS 之後才開始實作,實作中途調整條款幾乎必然發生——落地前應該先決定是否要「計劃 sha 變了就要求重跑」)

### 五、逃逸自動記
5. **finding**(工具指令引用層,派工詞提示的「不顯眼處」):S18、S19 的 `[test:]` 綁的測試名 `t_escape_auto_unreviewed_twoway`、`t_escape_auto_ci_only_test_step` 在 `scripts/test_lumos.py` 裡**不存在**(已用 `grep -n` 逐字核對,零命中)。「進度」節自己承認這兩條的行為實際上是被 `t_escape_auto_scope_rules` 一起釘住的,但 S18/S19 條款行卻各自宣稱綁了一支獨立、不存在的測試——這正好違反本篇自己第三節訂的規則(測試要真的存在)與「誠實界線」節的宣稱「20 條全綁測試」。
引句:「S18/S19/S20 由 `t_escape_auto_scope_rules`/`t_escape_auto_lock` 釘住」
severity: major
blocking: 是(這是可機械驗證、已確認為假的宣稱,且直接牴觸本篇對自己「全綁測試」的誠實承諾;規格閘一旦落地,這份計劃自己會先被自己的閘擋下——建議 r2 定稿前把 S18/S19 的 [test:] 改成實際存在的測試名,或補寫對應獨立測試)

### 六、退場條件
已讀。撤除條件已改成絕對門檻,上線順序寫死(逃逸自動記→S13→才開放雙向門),邏輯自洽。無 finding。

### 進度
已讀,無 finding(對照 `scripts/lumos`/`scripts/hooks/pre-push` 已逐項驗證屬實:`_escape_auto_failed`、`_vault_write_lock`、`finding_kind=code` 篩法均已落地)。

### 要動什麼
6. **finding**(派工詞問題⑤,skill 同步範圍):表格只列 `scripts/templates/graph-discipline.md`,沒有列本 repo 自己的根目錄 `CLAUDE.md`。已確認 `CLAUDE.md:62` 與 `scripts/templates/graph-discipline.md:60` 目前是逐字相同的一行(「設計 spec 寫完…→ lumos-design-loop」),且 `scripts/hooks/claude/lumos-entry-hook.py` 的 `_discipline_lag`(第 27–52 行)只是**事後提醒**「跑 `lumos update`」,不是自動同步——若落地時只改模板不重跑安裝,本 repo 自己在被規格閘生效之前會持續走舊行為(所有 spec 一律進 design-loop),直到有人注意到 SessionStart 的提醒。
severity: minor
blocking: 否(已有機械提醒機制兜底,不會無聲漂移,但建議「要動什麼」表補一行「落地後在本 repo 跑一次 `lumos update`」,否則審視者容易誤以為改了模板就等於改了本 repo 的行為)

7. **finding**(派工詞問題①,`_round_valid_m2` 與其他讀側):已逐一核對 `scripts/lumos` 裡至少 9 處硬編碼 kind 白名單的讀側(`_round_valid_m2:6331`、`gov --stats` 對抗層增量帳 `:5315`、`loop status` 相關 `:7151/7210/7277/7378/7827/7836/7864/8796`)。這些讀側幾乎全部先判斷 `not lp`(無 `loop` 欄位)就跳過,而 spec 全文未曾提及 `spec-gate` 記錄要不要帶 `--loop`——只要照現況(不帶 `--loop`)實作,這些讀側不會受影響,`_round_valid_m2` 的「未知 kind 使輪無效」規則因此實務上不會被觸發。但 spec 原文只點名了 `_round_valid_m2` 一支函式(「讀側 `_round_valid_m2` 也要認得這個 kind」),沒有講清楚其餘讀側為什麼不用改或不用管,三個月後的人單看 spec 文字容易誤以為只有一處要顧。
severity: minor
blocking: 否(已驗證現況安全,純屬文件說明不完整,不影響機制正確性)

8. **finding**(派工詞問題③):spec 稱「兩條不回溯常數的關係寫死」(`_CLAUSE_GATE_SINCE` 與新 `_SPEC_GATE_SINCE`),但 `scripts/lumos` 目前實際存在**第三個**同型常數 `_LANDING_GATE_SINCE`(`scripts/lumos:15778`,管處置閘落點/`lands_in` 那一步,2026-09-12 加入),spec 全文未提及它與新常數的關係。三個月後的人看到三個 `*_GATE_SINCE` 常數並存,會直接問「為什麼是兩條不是三條、第三條跟這次改動有沒有關係」,spec 沒有回答。
severity: minor
blocking: 否(落點檢查與條款句式/門判定在功能上大機率互不相干,只是文件用詞「兩條」造成誤導,補一句排除理由即可)

### 實務隱患
已讀,無 finding。四類的處置陳述與第一節一致。

### 驗收條款(S1–S21,派工詞問題⑦)
9. 已核對 20 條(S1–S13、S15–S21)逐條句式,除 finding 5(S18/S19 測試名不存在)外,其餘條款在寬鬆文法下均可解析、可讀。已核對 S20(`t_escape_auto_lock`)、S9–S11、S18/S19 內容涵蓋(`t_escape_auto_scope_rules`)在 `scripts/test_lumos.py` 中確實存在對應測試函式(僅命名與 S 條款標的名稱不同,見 finding 5)。
severity: minor
blocking: 否(併入 finding 5 處置,這裡僅記錄逐條核對結果)

10. **finding**(問題⑦「哪一條寫測試會寫不出來」):S21(推送閘對所有仍 doing 的雙向門測試清單全跑)是對 `scripts/hooks/pre-push`(bash)行為的斷言。本 repo 確實有先例用 subprocess 方式對 pre-push 做黑盒測試(`scripts/test_lumos.py` 約 15265 行起的 Task 4、612–643 行的沙盒測試),所以「寫不出來」不成立;但這類測試偏重、需要建真實 git sandbox,spec 沒有承認這支測試的成本比其他 S 條款高一截,誠實界線節也沒有提到。
severity: minor
blocking: 否(可行,只是成本被低估,不影響設計正確性)

### 回退
已讀,無 finding。回退步驟已綁 `git tag pre-spec-gate` 錨點,對齊 r1 折入。

### 誠實界線
11. **finding**:引句:「第一個消費者是本篇自己:上面 20 條就是照那條文法寫的、全綁測試」——此句在 finding 5 的事實核對下不成立(S18、S19 綁的測試名不存在)。這句話是本篇對自己誠信度最核心的宣稱,恰好是錯的,而且是在 r1 六席、23 條全折之後的第二版仍未被抓到的新洞,呼應派工詞提示「越成熟的稿子,殘留的洞越傾向藏在工具指令引用…這類不顯眼處」。
severity: major
blocking: 是(與 finding 5 同一件事,合併計入同一條 blocking——見 finding 5 的處置建議)

### 審計修正紀錄
已讀,無 finding。r1 的 23 條去重與折入紀錄與 `governance/review-reports/規格落成可驗收條件/r1-intake.md` 對得上。

## 固定席節點逐條判

- **Systems/design-loop**(★INVARIANT★,處置閘第五步):**會被本設計直接改動**。合約行本身就是本案要重寫的對象;風險已在 finding 3 展開(新文字內容與綁定測試未定)。
- **Issues/code-loop守衛main-direct盲區**:不影響——該事故是 main 分支直推繞過 code-loop 守衛的盲區,與本案改的「設計審 vs 規格閘」路由無關,本案沒有改動 main-direct 判定邏輯。
- **Systems/anchor-integrity**(★RISK★):不影響其合約本身——本案改 `scripts/hooks/pre-push`/`scripts/lumos` 確實會觸發 `lumos anchor verify` 翻紅,但這是預期中的正常錨點更新流程(spec「進度」節已寫明要 `anchor approve`),不是破壞 anchor 完整性合約。
- **Systems/每支檔有家**:不影響——本案的 `lands_in` 已依既有慣例規劃新開 `Systems/規格閘` 認領新程式碼,吻合「每支檔有家」的登記方式,且 `scripts/lumos` 一貫允許多篇 Systems 節點分別認領其不同功能區塊(已用 grep 核對至少 20 篇既有節點都以反引號認領 `scripts/lumos`)。
- **Systems/lumos-cli-read**(★INVARIANT★,search 排除 superseded 不排除 stale):不影響——本案不改 `lumos search`/`lumos context` 邏輯。
- **Systems/bound-tests-gate**(★INVARIANT★,code-loop 對 impact 固定席合約測試的驗證):不影響——這是 code-loop（代碼審)用的合約測試機制,與本案改的是設計審/規格閘的條款檢查器,是兩條不同管線,彼此不共用程式碼路徑。
- **Systems/lumos-cli-lifecycle**(★INVARIANT★,re-inject 只覆蓋 sentinel 之間):不影響——本案若要更新 `graph-discipline.md`(sentinel 內文字),re-inject 機制本來就是為了同步 sentinel 內容而存在,不涉及覆蓋 sentinel 外文字,不牴觸該不變量。
- **Systems/測試假綠形態**(★INVARIANT★,修 bug 要配前置斷言證明現場成立):不直接牴觸——本案多處已宣稱「先紅後綠」與「翻紅釘」(進度節),但 finding 5 顯示至少兩條驗收條款根本沒有各自的翻紅釘測試,是本節不變量精神在本篇自我實踐上的具體破口(已併入 finding 5,不重複計)。

## 抑噪說明
未定義詞(如「主體」「回應」未給出精確子文法)、S6/S9 等內部用頓號連接多子條件是否算「複合觸發」——這類在寬鬆文法下都可解析、沒有具體失敗場景,依抑噪規則不單獨標記。

---

**最嚴重 severity:major**
**blocking 計 2 條**(finding 2「S8 共用檢查器 manual 政策矛盾」與 finding 5/11「S18/S19 綁定測試名不存在,牴觸本篇自我宣稱」——後兩者合併計為同一條 blocking)
