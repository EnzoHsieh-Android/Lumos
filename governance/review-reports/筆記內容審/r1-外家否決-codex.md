severity: blocker

## F1 校準閘只量一致率與誤擋，零召回的判定者也會達標

severity: blocker

blocking: 是 —— 校準可放行完全抓不到程式現況的判定者，核心守衛沒有成立

引句:「一致率低於 85%,或人工對照有超過 2 行純理由被判推得出,就不接線、改派工詞重來」

1. 位置：〈上線前校準與接線〉及 S15，`governance/review-reports/筆記內容審/r1-work.md:85`。
2. 失敗場景：兩席把所有行都判成「脈絡」，兩席一致率為 100%；人工抽查中「純理由被判推得出」為 0 行，因此達標接線。所有程式碼推得出的新增行仍獲放行。
3. 查證：前置實驗刻意用 55 句現況句量「抓到幾句」，見 `governance/review-reports/筆記內容審/r1-work.md:33`；正式校準卻沒有「程式現況被誤判成脈絡」的上限。需要同時定義 false-negative/recall 門檻。

## F2 刪除或直接改寫判定檔，就能洗掉最重判定

severity: blocker

blocking: 是 —— 前身重寫要修的「重擲洗判定」仍可用刪檔或改檔完成

引句:「同一個內容編號在所有判定檔裡,★取最重的那次非申訴判定★」

1. 位置：〈內容編號與判定檔〉、`check`，`governance/review-reports/筆記內容審/r1-work.md:60`、`:78`。
2. 失敗場景：先提交一份把某內容判成「推得出」的檔；下一個提交刪掉該檔，或直接把 JSON 判定改成「脈絡」，再加入較輕判定。`check` 只讀推送頂端樹，歷史中的重判定已不可見，該行隨即涵蓋。
3. 查證：現有快照讀取器對指定提交只以 `git show <tip>:<path>` 讀檔，刪除後回 `None`，見 `scripts/lumos:22542`、`scripts/lumos:22566`。spec 沒有禁止修改/刪除、對基準版本追查歷史、判定檔雜湊鏈或 append-only manifest。

## F3 先出現的「脈絡」誤判無法被後來更重的普通判定糾正

severity: blocker

blocking: 是 —— 「取最重」與 record 的待審過濾互相矛盾，核心折疊規則無法照字面實作

引句:「報告裡不在目前待審集合的編號忽略並列出來」

1. 位置：〈內容編號與判定檔〉與 `record`，`governance/review-reports/筆記內容審/r1-work.md:61`、`:62`、`:73`。
2. 失敗場景：第一份報告誤判為「脈絡」，該 ID 因此已涵蓋；第二份非申訴報告正確判為「推得出」時，重算後該 ID 已不在待審集合，報告被忽略。「最重判定」永遠進不了判定檔。
3. 申訴路徑也無法修正：spec 限定申訴只能調輕，見 `governance/review-reports/筆記內容審/r1-work.md:61`、`:69`。需要明定已涵蓋 ID 的加重入口與折疊規則。

## F4 同一區塊的相同文字共用 ID，但分類依上下文可不同

severity: major

blocking: 是 —— 一個 ID 無法承載兩個不同分類，會固定誤放或誤擋其中一處

引句:「同一塊裡一字不差出現兩次的,共用一個編號,清單列出每一處」

1. 位置：〈內容編號與判定檔〉及派工報告格式，`governance/review-reports/筆記內容審/r1-work.md:58`、`:68`。
2. 失敗場景：同一篇正文在「現況」與「否決方案」兩個標題下各有一行 `- 沒有採用快取。`。前者是可由程式碼判定的現況，後者是歷史決策脈絡；兩行的路徑、區塊與去空白文字完全相同，因此共用 ID。
3. prepare 雖列出每一處及各自上下文，報告仍只允許「內容編號｜分類」一列，無 occurrence key。判定者無法分別作答，record 也無法分別涵蓋。

## F5 prepare 的上下文未綁定 record，舊上下文報告可驗收新內容環境

severity: major

blocking: 是 —— spec 明知分類依賴上下文，卻沒有防 prepare 與 record 之間的 TOCTOU

引句:「清單每行附內容編號、區塊、行號,以及★它前後各兩行的上下文★」

1. 位置：`prepare` 與 `record`，`governance/review-reports/筆記內容審/r1-work.md:67`、`:72`、`:73`。
2. 失敗場景：prepare 後修改標題或鄰接句，但保持被審行文字不變；該行 ID 與待審集合指紋不變。record 只讀清單開頭的編排者、模型、派工詞版本，再按現況重算 ID，仍會接受基於舊上下文產生的報告。
3. spec 未要求 prepared 檔記錄 tip/tree SHA，也未要求 record 重生完整清單並比對清單雜湊。上下文改動本身即使另行受審，原行仍沿用舊分類。

## F6 `file:line` 借用的驗證器會跟隨 repo 內捷徑讀到 repo 外

severity: major

blocking: 是 —— 違反「證據一律關在 repo 裡」的明文資料邊界

引句:「★證據一律關在 repo 裡★:`file:line` 走既有的 `_validate_repo_ref`」

1. 位置：`record` 證據驗證，`governance/review-reports/筆記內容審/r1-work.md:76`。
2. 失敗場景：repo 內有捷徑 `evidence.txt -> /repo外/secret.txt`，報告寫 `file:line evidence.txt:1`。既有驗證器會判目標存在並讀取第一行，repo 外內容通過證據驗證。
3. 查證：`_validate_repo_ref` 只拒絕絕對路徑與 `..`，見 `scripts/lumos:19828`；其工作樹路徑直接呼叫 `target.exists()` 與 `target.read_text()`，兩者均跟隨捷徑，見 `scripts/lumos:19849`、`scripts/lumos:19858`。search 路徑有寫捷徑限制，file 路徑沒有。

## F7 `decision-amend` 用陳舊 remote-tracking refs 無法保證決策尚未推送

severity: major

blocking: 是 —— 指令宣稱的不可改邊界會被另一會談剛推上的決策穿透

引句:「遠端追蹤參照只在 fetch 或 push 時更新,所以同時印出上次 fetch 距今多久」

1. 位置：`decision-amend`，`governance/review-reports/筆記內容審/r1-work.md:70`、S12 `:108`。
2. 失敗場景：本機 fetch 後，另一位作者把同一決策編號推到另一遠端分支；本機 remote-tracking ref 尚未更新。`decision-amend` 讀到「遠端沒有」並准改，推到不同分支仍可成功，已推決策因此被當作未推決策修改。
3. 「超過一天提醒 fetch」不是判定條件；一天內的陳舊狀態無提醒，超過一天也仍准改。spec 必須把新鮮度變成前置條件，或收窄「只准改還沒推上去」的承諾。

## F8 判定檔聲稱借用「整檔原子寫」，但所指 prior art 並不提供這個語意

severity: major

blocking: 是 —— 實作依 spec 借錯原語，強殺或短寫會留下已命名但不完整的判定檔

引句:「寫法照連鎖帳本那支(整檔一次寫、拒絕捷徑)」

1. 位置：〈判定檔〉與 S9，`governance/review-reports/筆記內容審/r1-work.md:60`、`:105`。
2. 查證：`rel_cascade_create` 直接以最終檔名 `O_CREAT|O_EXCL` 建檔，再呼叫一次 `os.write`；沒有暫存檔換名，也沒有驗證 header 寫滿，見 `scripts/lumos:15055`、`scripts/lumos:15068`、`scripts/lumos:15075`。後續內容則用 append 修改同檔，見 `scripts/lumos:15036`、`scripts/lumos:15548`。
3. S9 只驗兩行程同時寫、分支合併不衝突，沒有強殺、ENOSPC 短寫或 torn JSON 測試。應指定真正的 temp→驗證→replace 原語及唯一檔名衝突處理。

## F9 doctor 沿用第一層的字串檢查，註解或停用步驟也會被判成已接 CI

severity: major

blocking: 是 —— 消費專案可在完全沒有 CI 後盾時得到假綠體檢

引句:「所以 doctor 檢查專案 CI 有沒有呼叫 `note-audit check`,沒有就印一行並給要貼的那一步」

1. 位置：〈消費專案的 CI 與 doctor〉與 S16，`governance/review-reports/筆記內容審/r1-work.md:83`、`:112`。
2. 失敗場景：workflow 只有註解 `# python scripts/lumos note-audit check`，或命令位於永不成立的條件步驟。沒有實際檢查，doctor 卻不提醒；`git push --no-verify` 後只剩事後掃描。
3. 查證：第一層 doctor 把所有 YAML 純文字串起來，再用 `"note-shape --diff" not in body` 判接線，見 `scripts/lumos:23881`、`scripts/lumos:23890`。新設計明寫「跟第一層並排」，卻沒有補語意檢查或至少排除註解的條款。

## F10 第二層提高治理帳寫入頻率，實務隱患卻宣稱風險沒有變大

severity: minor

blocking: 否 —— 破壞的是事件統計與 RETIRE 量測，不直接改變判定檔的擋放結果

引句:「治理帳只記短事件(沿用既有寫入器,治理帳多個寫入者都沒上鎖 的風險照舊、沒有變大)」

1. 位置：〈實務隱患／資源併發〉，`governance/review-reports/筆記內容審/r1-work.md:127`。
2. 失敗場景：兩個會談同時 record，或 record 與 doctor 同時寫 `.governance-log.jsonl`；寫入交錯形成壞 JSON 行後，讀端跳過該行，申訴率、skip 數與 RETIRE-IF 統計少算。
3. 查證：`_gate_event` 直接以 append 模式寫、沒有鎖，見 `scripts/lumos:927`。既有 Issue 已明記多寫者、壞行靜默跳過，且點名「第二層要寫通過紀錄，是最需要修的使用者」，見 `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:16`、`:37`、`:52`。本 spec 又承認幾乎每次推送都會跑判定者，見 `governance/review-reports/筆記內容審/r1-work.md:141`，頻率不是照舊。

## F11 新閘名沒有列入既有白名單工作項，所有治理事件會被寫入器拒絕

severity: major

blocking: 是 —— record、warn、skip 與環境跳過事件全數不落帳，條款 S11 與 RETIRE-IF 無資料

引句:「治理帳只記事件與筆數(判了幾行、各類幾行、申訴幾筆),不列編號,所以每筆都很短」

1. 位置：〈內容編號與判定檔〉、〈出口與開關〉、S11，`governance/review-reports/筆記內容審/r1-work.md:63`、`:81`、`:107`。
2. 查證：`_gate_event` 對不在 `_KNOWN_GATES` 的名字直接拒寫，見 `scripts/lumos:893`、`:898`；現有名單到 `note-shape` 為止，沒有 `note-audit`，見 `scripts/lumos:6595`、`:6615`。
3. 前身 spec 曾明寫要把 `note-audit` 登記進閘名單；重寫稿刪掉這項，條款只驗事件結果，沒有把必要常數更新列入做法。照重寫稿的變更清單實作會得到 `telemetry-write-failed`。

## 逐節覆核

- 開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF：已讀；資源併發宣稱見 F10，其餘無 finding。
- 〈判定者能不能用〉：已讀；正式校準漏掉召回判準見 F1。
- 〈做法 1：哪些行要審〉：已讀,無 finding。
- 〈做法 2：內容編號與判定檔〉：F2、F3、F4、F8、F11。
- 〈做法 3：指令〉：F5、F6、F7、F9。
- 〈做法 4：上線前校準與接線〉：F1。
- 〈做法 5：規範文字與路由〉：已讀,無 finding。
- 〈條款〉：S4、S8–S9、S11、S15–S16 未封住上述 findings；其餘已讀,無 finding。
- 〈回退〉：已讀,無 finding。
- 〈實務隱患〉：F10；其餘分類見下節。
- 〈誠實界線〉：已讀；沒有揭露 F1–F5 的核心判定生命週期缺口。
- 〈前身 r3 發現怎麼處理〉：已讀；F2、F3 顯示「重擲洗判定」修法仍不封閉。
- 〈審計修正紀錄〉：已讀,無 finding。

## 交叉引用與現況核對

1. 八個 `[[…]]` 目標均存在：兩篇 Issues、兩篇 Projects、四篇 Systems。`Systems/筆記內容審` 尚未建立，但 spec 明列為新家，不判壞引用。
2. `judge_prompt.md`、judge-experiment 目錄、`governance/rel-cascade/`、兩支 hook、CI workflow 與 `.lumos/config.json` 均存在。依禁令未開啟前身 `governance/review-reports/` 卷證。
3. 指名的現況函式均存在並已讀語意：`_ns_range_added`、`_ns_regions`、`_note_shape_eval`、`cmd_note_shape`、`_note_shape_doctor_lines`、`_gate_event`、`cmd_lint_waive`、`_lint_waivers_add`、`_nodehome_golive`、`_nodehome_clamp_base`、`_validate_repo_ref`。
4. 現有 CLI 已核對：`note-shape --diff`、`home check --diff`、`loop next --orchestrator`、`lint-waive`、`update` 存在且旗標相符。`note-audit`、`decision-amend` 目前不存在，屬本 spec 預定新增，非壞引用。
5. `lumos refcheck governance/review-reports/筆記內容審/r1-work.md --repo . --json` 回報 5 個可辨識檔案引用全數存在、0 missing、0 out-of-range。

## 實務隱患鏡頭

- 守衛面：有。F1–F5、F9 會造成假放行、無法糾錯或 CI 假接線。
- 判定卷證完整性：有。F2、F3、F8。
- 檔案系統與資料邊界：有。F6 會經捷徑讀出 repo。
- Git／遠端狀態：有。F7 的 remote-tracking snapshot 不足以證明尚未推送。
- 資源併發：有。判定檔分檔避免互蓋，但治理帳仍有 F10；同 provider 的 prepared 上下文競態見 F5。
- 可用性：有但無額外 finding；模型中斷有顯式 skip，check 仍 fail-closed。
- 容量：有但無額外 finding；小檔成長已設 REVISIT 與量測。
- 對外送出：有但無額外 finding；資料送往既有編排供應商，沒有增加供應商，但確實擴大到筆記上下文與程式碼。
- 不可逆：無——推送前只新增本機提交與可刪判定檔，回退順序完整。
- 金流：無——不碰付款或計費業務；模型額度屬已明示的資源成本。

總結：最嚴重 severity 為 blocker；blocking 10 條。