severity: major

引句已逐字核對:我用 `grep -F` 對審材 r2-snapshot.md 逐條比對,15 條引句各命中 1 次,全形與半形標點都與原文一致。F2 的引句已改成全形逗號。F11 的引句原本含反引號,我截到反引號之前。

審查範圍:凍結審材全文,對照 `scripts/lumos` 現況。我先假設內容簽章、凍結比對、時效檢查各自在某個輸入下會壞,再找那個輸入。沒有建臨時目錄,也沒有跑小實驗,不需要清理。

## 風險類逐類

- 守衛面(放寬或收緊擋下判定):有問題。簽章可被重放(F1、F5)。簽章沒蓋到版本綁定(F2)。判定輸入沒凍結完整(F4)。凍結規則把正常的證據更新擋掉(F3)。
- 舊資料與舊帳相容:有問題。無登記專案的行為承諾與淺層 clone 的條文互相矛盾(F6)。
- 已在途分支:不影響。起點一律取 merge-base,已在途分支重新判定是預期行為。
- 跨會談與跨計劃交界:有問題。vault 路徑來源不明,凍結比對可能整個落空(F7)。

## Findings

### F1 簽章重放:`.sig` 沒綁住「從哪一版清單換過來」,撤銷過的金鑰可以被請回來

- spec 段落:〈內容簽章〉的〈清單本身的修改〉與〈金鑰數量與遺失〉。
- 問題:換清單的簽章只簽新清單全文,簽章內容沒有 merge-base 版清單的雜湊,也沒有時間。
- 具體例:
  1. 初始清單 L0 只有金鑰 A。
  2. 使用者加入金鑰 B,簽出 L1=A+B,簽章 sig1 由 A 簽。
  3. B 洩漏給 AI,使用者撤銷,簽出 L2=A,存成 `.sig`。
  4. AI 從 git 歷史撈出 sig1,把清單寫回 L1 並放上 sig1,再推送。
  5. 驗證看的是「merge-base 版清單(L2)裡的 A 對新清單全文(L1)的簽章」,sig1 通過。B 回到清單,AI 用 B 簽出任何例外。
  6. 照 spec 字面,撤銷永遠無效。
- 引句:「刪檔的情況簽的是空內容。」
- 引句:「一把遺失時用另一把簽新清單換掉。」
- 修法方向:簽章內容改成帶型別標籤的 JSON,至少含 `type:approvers`、merge-base 版清單雜湊、新清單雜湊、日期。這同時解掉原始清單位元組跟 `lumos-security` 命名空間下其他簽章共用格式的問題。

severity: major
blocking: 是
判準:照 spec 實作會做出可被舊簽章還原金鑰的壞系統。

### F2 人審簽章沒蓋住版本綁定,簽一次之後 AI 改程式再刷新 `bindings`,人審照樣有效

- spec 段落:〈機械做不到的判斷〉與證據圍欄鍵名表。
- 問題:review 的 stale 判定靠紀錄裡的 `bindings` 和 `test_sources`,而這些欄位不在人審簽章內容裡。簽的內容只有護欄 id、revision、判定輸入雜湊、`judgments`、`reviewer`、`expires_on`。
- 具體例:
  1. 使用者對 OD-01 簽了人審,涵蓋 `legit_control_real`,到期日 90 天內。
  2. AI 之後移除所有權檢查,把紀錄的 `bindings` blob 改成新版。
  3. 護欄 revision 沒變,判定輸入雜湊沒變,簽章驗得過,review 判 qualified。
  4. 實際效果是人類簽的是舊程式,新程式照樣被放行,直到 `expires_on`。
  5. 這等於架空「紀錄綁版本,版本一變就重審」。
- 引句:「綁定的程式與護欄 revision 等於要推的提交，一變判 stale」
- 引句:「簽的內容含護欄 id、revision、判定輸入雜湊」
- 修法方向:人審簽章內容納入 `bindings` 與 `test_sources` 的 (path, blob) 清單,以及 `author`。

severity: major
blocking: 是
判準:照字面實作,人審的版本綁定只是 AI 可自行改寫的欄位。

### F3 「evidence_refs 被換掉就算變弱」加「簽章內含 evidence_refs 雜湊」,讓每次證據更新都需要使用者簽章

- spec 段落:〈必驗集合與判定輸入都以 merge-base 版為底〉、〈內容簽章〉的簽什麼。
- 問題:
  - 凍結規則把 `evidence_refs` 任何一列被換掉或刪掉都算「變弱」,不分新證據是否同種類或更強。
  - 沒有簽章有效的修訂紀錄就用新舊聯集判。
  - 舊 ref 指向的 Verification 節點在改實作後已被標 superseded 或 stale,聯集必然判 stale。
  - 例外與人審簽章又都含 `inputs_sha256`,而 `evidence_refs` 在雜湊裡。
- 具體例:
  1. 改了實作,證據 stale。
  2. 正常做法是重跑測試、開新的 Verification 節點,再把 ref 指向新節點。
  3. 這一步被判為變弱,聯集判必紅。
  4. 使用者得先簽一筆修訂紀錄,再重簽人審和既有例外,才能推送。
  5. S18、S19 想守的「改實作後 stale 擋下」變成「更新證據一律先找使用者簽」,AI 依序操作的流程斷在這裡。
- 具體例:刷新一份 `fault_sensitivity` 證據,例外與人審簽章同時作廢。
- 引句:「變弱而沒有核可修訂紀錄時，用新舊兩版的聯集判」
- spec 沒定義怎樣的 ref 更換算變弱。實作者只能二選一:全擋(流程卡死),或自己發明規則(沒有保證)。
- 修法方向:變弱只比 kind 集合,以及每個 kind 的 ref 數是否減少。同 kind 換節點不算變弱,且簽章雜湊不含 ref 內容。

severity: major
blocking: 是
判準:照字面實作會做出無法更新證據的閘,實作者必須自行決定「變弱」的定義。

### F4 工具清單與威脅類別表都不在凍結範圍也不需簽章,AI 可自行調低判定門檻

- spec 段落:〈二〉最低種類怎麼算、k6 的坑、〈三〉消費專案工具清單。
- 問題:閘門的判定有兩個輸入由 AI 可改的檔案決定,而 d7 的簽章與 merge-base 凍結只涵蓋護欄本體。
  - `.lumos/security-tools.json` 決定釘版本、`min_requests` 下限、允許目標、覆蓋證明種類。
  - [[Systems/資安威脅類別表]] 決定最低種類與替代欄。
- 工具清單的「核可決策」只靠 `decision_ref` 指到一個 `valid` 的決策。決策由 AI 用 `lumos decision-add` 即可寫入。
- 具體例:
  1. k6 證據請求數太少。
  2. AI 把清單的 `min_requests` 改成 1,下限檢查通過。
  3. 或 AI 把某掃描工具的覆蓋證明種類改成容易滿足的一種。
  4. 或 AI 編輯威脅類別表,拿掉某類的最低種類。
  5. 護欄本體與 evidence_refs 都沒動,凍結比對看不到,簽章也沒有牽涉。
  6. 這正是 d7 想擋的「AI 自己放自己」,只是換了入口。
- 引句:「請求數下限不由作者在圍欄宣告，由工具清單那一列登記」
- 修法方向:清單與類別表的變弱也走 merge-base 比對加簽章修訂紀錄,同護欄輸入的處理。

severity: major
blocking: 是
判準:照字面實作,AI 改一個未簽檔案就能降低判定門檻。

### F5 降級設定與修訂紀錄的簽章沒有時效、沒有專案綁定,可重放或跨專案搬用

- spec 段落:〈擋或只提醒的設定〉、〈核可修訂紀錄〉、〈內容簽章〉。
- 問題一:`gate_setting` 的簽章內容只有 `type`、`value`、`approved_on`。
  - 沒有專案識別,沒有 `expires_on`,沒有 merge-base 版清單雜湊。
  - 使用者一把金鑰通常釘在多個專案。
  - AI 可把 order-demo 已簽好的 `warn` 簽章整段貼進另一個也釘了同一把金鑰的專案的 `.lumos/config.json`,該專案整道閘降成只提醒。
  - 同一簽章也永遠有效,「過渡期」(Q4)沒有結束日,與母計劃 d9「例外最長 30 天」的精神不一致。
- 問題二:修訂紀錄沒有到期日,spec 自己說明舊紀錄不必刪除。
  - 使用者核可「removed: true」,之後重新加回同內容的護欄。
  - AI 照舊紀錄再移除一次,仍然簽章有效、不需使用者重簽。
- 引句:「所以 AI 改一行設定關不掉這道閘；使用者要給過渡期（Q4）或誤擋時要退，簽一次就能降成只提醒。」
- 引句:「舊紀錄可以直接刪，刪了只會少一筆可用的核可，不會放寬。」
- 後一句不成立,因為舊紀錄不刪就仍可被重放。
- 修法方向:簽章內容加專案識別(例如首個提交或 repo 名)、`expires_on`,並限制 gate 降級的最長期限。

severity: major
blocking: 是
判準:照字面實作,一次簽章可被複製到別的專案或在條件重現時再次使用。

### F6 「無登記專案行為不變」跟淺層 clone、無共同祖先的無條件擋下互相矛盾

- spec 段落:〈起點一律是 merge-base〉對〈不受影響〉與 S1、S30。
- 問題:〈不受影響〉承諾沒登記痕跡的專案輸出與退出碼跟現在逐字相同。〈起點一律是 merge-base〉卻寫「淺層 clone:擋 `shallow_clone`」和「沒有共同祖先:擋 `freeze_base_unavailable`」,沒有附「有登記痕跡」條件。附條件的只有 `commit_unavailable` 和〈擋下條件〉其中幾條。
- 具體例:消費專案自己的 CI 用 `actions/checkout` 預設 `fetch-depth: 1` 跑 `lumos code-loop check`。沒登記任何資安護欄。照字面實作,每次 CI 都被 `shallow_clone` 擋下,S1 變紅。
- 引句:「沒有任何資安登記痕跡的專案，這一步回 None、不寫治理帳，輸出與退出碼跟現在逐字相同；」
- 修法方向:先用提交樹的 `git grep` 預檢,沒有痕跡就早退,之後才判淺層與祖先。

severity: major
blocking: 是
判準:實作者必須自己決定哪個條文優先,無法同時滿足 S1 與起點規則。

### F7 vault 路徑的來源沒定義,搬動 vault 目錄可讓 merge-base 版變空、凍結比對落空

- spec 段落:〈從提交樹產快照〉。
- 問題:`_secinv_snapshot_tree(repo_root, sha, vault_rel)` 的 `vault_rel` 是單一參數,且「要推的版與 merge-base 版都用它」。
- spec 沒說 `vault_rel` 從哪裡來。現況 `find_vault` 與 `_secinv_select_vault` 都從工作目錄往上找。
- 具體例:
  1. AI 在同一次推送內把圖譜目錄從 `docs/x-knowledge` 搬到 `docs/y-knowledge`,同時削弱某條護欄。
  2. 若 `vault_rel` 取自工作樹(也就是推送版),merge-base 版在新路徑下是空的,視為無痕跡。
  3. 所有護欄被當成新增、通過,凍結比對看不到削弱。
  4. 若兩邊 vault 位置不同,則需各自解析。
- 引句:「要推的版與 merge-base 版都用它，不讀工作目錄」
- 此處的矛盾是:spec 說不讀工作目錄,但 `vault_rel` 的取得現況只能來自工作目錄。
- 修法方向:`vault_rel` 對兩個提交各自從該提交樹解析,並明定圖譜在 merge-base 版存在而推送版消失或搬家時的判定。

severity: major
blocking: 是
判準:照字面實作,搬動 vault 目錄即可讓凍結比對失效。

### F8 「必驗集合意外為空」的條件在邏輯上永遠不會單獨成立

- spec 段落:〈擋下條件〉的意外為空。
- 問題:必驗集合已定義為「HEAD 的 active 資安條目 ∪ merge-base 版有、這次被刪除或降級而沒有簽章修訂紀錄的條目」。merge-base 版非空時,若沒有簽章紀錄,後者本身就讓集合非空。有簽章紀錄時,「這中間又沒有把它們全部移出的核可修訂紀錄」又為假。所以 `unexpected_empty` 沒有可到達的情況。
- 後果:S3 的「全部條目被刪」樣本其實由 `missing:control_removed_unapproved` 擋下,不是 `unexpected_empty`,測試依代碼比對時會對不上。
- 引句:「而 merge-base 版的必驗集合不是空的、這中間又沒有把它們全部移出的核可修訂紀錄。」

severity: minor
blocking: 否
判準:不改不會做出壞系統,只是死代碼與一個永遠不輸出的原因代碼。

### F9 CI 的 pull_request 事件在本節裡既「不跑」又「當起點」

- spec 段落:〈四〉的起點一律是 merge-base,與〈內容簽章〉的〈為什麼不是 PR 核准〉。
- 問題:〈內容簽章〉說 code-loop gate 在 PR 上不跑。〈起點一律是 merge-base〉卻給了 pull_request 事件的起點定義。〈要跟著改的地方〉的 `.github/workflows/ci.yml` 只寫「加 tag 觸發與只跑安全判定的一步」,沒說 PR 事件要不要跑。
- 引句:「pull_request 事件用 base 的提交」
- 引句:「但 code-loop gate 那一步只在 push 事件跑；PR 上不跑，等例外合進 main 才判，已經晚了。」

severity: minor
blocking: 否
判準:實作者要自己決定 PR 事件要不要跑安全判定。

### F10 驗章的 `-I` 簽章人從哪來沒定義

- spec 段落:〈內容簽章〉的驗。
- 問題:`ssh-keygen -Y verify` 需要 `-I <簽章人>`,但核可物件的鍵表(例外、risk_accepted、not_applicable、修訂紀錄、gate 設定、人審紀錄)都沒有「簽章人」欄位。實作者要自己決定:先用 `find-principals`,或枚舉清單全部 principal 逐個試。兩種做法對 allowed_signers 含萬用字元 principal 時結果不同。

severity: minor
blocking: 否
判準:實作者可自行選一種做法,不會做出壞系統,但各人選法不一致。

### F11 原因代碼表有一個沒有任何條文使用的 stale 代碼

- spec 段落:〈原因代碼〉。
- 問題:`stale:tool_version_changed` 在 stale 列。〈綁版本與環境指紋〉把工具版本不等於清單判為 `invalid:tool_version_mismatch`,證據記的版本與輸出自帶版本不符也沒有指向 stale。實作時「同一個代碼只屬於一種判定」的逐一對照測試會找不到使用處。
- 引句:「工具版本要等於消費專案工具清單（見〈三〉）登記的釘版本；不等就是」

severity: minor
blocking: 否
判準:不影響判定結果,只是表與條文不一致。

### F12 時間欄位只比提交時間,不比現在,`vulndb_fetched_at` 沒有上界

- spec 段落:證據圍欄鍵名表與〈依賴掃描結果跟著漏洞庫變〉。
- 問題:`vulndb_fetched_at` 填未來日期(例如 2099-01-01),「距今超過 14 天」算出負數,永遠不是 stale。`observed_at` 只檢查不晚於提交時間,而提交時間可由 `GIT_COMMITTER_DATE` 任意設定。
- 引句:「漏洞庫抓取時間，只收 ISO 8601 含時區；不收版本號（算不出幾天）」
- 這兩個欄位本來就是自述,攻擊者直接填今天日期效果相同,所以我只標 minor。

severity: minor
blocking: 否
判準:不增加新的偽造能力,只是缺了一個明顯的邊界檢查。

## 已讀無 finding

- 整體判定彙總規則(sound、excepted、unsound 與護欄層優先)。
- 同種類多筆證據取最差的判定。
- 30 天算法與 UTC 邊界。
- 種類 × 格式允許表。
- k6 新舊格式的處理。
- SARIF 嚴格解析與覆蓋證明。
- 資源上限與批次讀取。
- 回退順序。

最嚴重 severity:major;blocking:是 共 7 條(F1、F2、F3、F4、F5、F6、F7)。
