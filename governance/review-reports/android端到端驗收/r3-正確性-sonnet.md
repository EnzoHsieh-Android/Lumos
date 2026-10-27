severity: major

以下 findings 對照的是 `scripts/lumos` 已實作的部分(`_e2e_feature_record`、`_e2e_keep_old`、`_e2e_case_results`、`_e2e_fingerprint`、`_e2e_record_err`、`_e2e_changed_files`)。推送檢查那一道本身(`code-loop check` 的 android_e2e 判定)在 repo 裡還沒有實作,以下都是對 spec 字面的推演。

## Findings

**1. 〈資料怎麼流〉第 4 步與 S8 對「沒放行、`runs` 不是 pass」的判法,跟新節〈推送前怎麼按功能判〉第 3 步互相矛盾**
severity: major
blocking: 是 — 實作者照 S8 與照新節會寫出兩種判定,而且各有測試(`t_android_e2e_gate`、`t_android_e2e_gate_by_feature`)互相打架。
引句:「最近一次是 fail 或 unjudged 而且沒有放行→回 1 擋下並印出哪一塊沒過與要跑的指令」
- 第 4 步「怎麼判」寫「沒放行就看最近一次結果:result 是 pass 而且…→過;其他→擋」。S8 寫「最近一次是 fail 或 unjudged 而且沒有放行→回 1 擋下」。新節第 3 步寫「`runs` 不是 pass…→改走按功能」。
- 新節自稱「接在 S8 讀到合格紀錄之後」,但 S8、第 4 步、S10 都沒改。
- 失敗例子:紀錄 `runs.result = fail`、`feature_runs["player.open-close"]` 是較新的 pass、只改了播放頁。
  - 照 S8 字面:擋。
  - 照新節:放行。
- 同一個輸入有兩個預期結果。
- 相關的殘留說法:〈查證紀錄〉寫「只有放行的紀錄是 null」(`runs` 欄),S10 寫「只有放行、`runs` 是 null 的紀錄應放行」。
  - 現行 `_e2e_record_err` 的註解已寫明,只做過按功能跑的紀錄也是 `runs: null`、沒有 waivers。
  - 這種紀錄在 S10 該放行還是走按功能判,spec 沒說清楚。
- 佐證:file: `scripts/lumos:40589`(`_e2e_record_err` 註解)與 `scripts/lumos:41062`(`_e2e_feature_record`)。

**2. 指紋範圍內沒有任何改到的檔時,「要驗的情境」是空集合,整段空真(vacuous truth)放行**
severity: major
blocking: 是 — 這是放錯的洞,而且正好是 d1 決策想堵的那件事。
引句:「只留指紋範圍裡的檔(`app_dirs` 扣掉 `exclude`、加上驗收素材」
- 新節第 3 步:改到的檔「只留指紋範圍裡的檔」,「全部符合→過」。
- 指紋在 `e2e.stability` 開著時,還會算進最外層 `stability` 段與 `stability_scenarios`(file: `scripts/lumos:40543` 的 `memory-config`)。但 `.lumos/macrobench.json` 本身不在指紋範圍(`app_dirs` / `.maestro` / 門檻檔 / `flows`)。
- 失敗例子(輸入 → 預期 → 照 spec 字面得到):
  - 輸入:分支只把 `macrobench.json` 的 `stability_scenarios.player_cycle.cycles` 從 10 改成 1。`e2e` 段不動。
  - 此時兩端指紋不同,S8 觸發。開發者在乾淨提交上跑任一個 `--case list.scroll`,就會在新指紋下產生一份只有 `feature_runs` 的紀錄。
  - 預期:記憶體標準改弱,要整套重驗。
  - 照字面:`git diff` 的檔在範圍外 → 被濾掉 → 集合為空;`e2e` 段雜湊相同 → 不要整套;沒有要驗的情境 → 過,印「按功能放行:驗了 」。
- 缺口是「指紋因範圍外的輸入而變、改到的檔卻是空」這個狀態沒有定義。
- 同一缺口也在 finding 5(路徑引號)裡出現。

**3. 較新的 `unjudged` 或 `complete:false` 按功能紀錄,會讓一份較舊的整套 pass 被步驟 2 擋下**
severity: major
blocking: 是 — 該放的擋了,而且擋下訊息引導的動作解不掉。
引句:「再看 `feature_runs` 裡有沒有哪個情境結束得比 `runs` 晚而且不是 pass;有→擋,印出那個情境」
- 步驟 2 寫「`feature_runs` 裡有哪個情境結束得比 `runs` 晚而且不是 pass→擋」。「不是 pass」把 `unjudged` 與 `complete:false` 的開發中途跑也算進來。
- 失敗例子:
  - 先整套跑 pass(T1)。再跑 `android-e2e-run.sh --case player.open-close --no-memory`(T2),這個情境只列了記憶體。
  - `_e2e_case_results` 對沒有會判項目的情境回 `result: unjudged, complete: false`。
  - `_e2e_keep_old` 只在既有那筆「完整且判完」時才保留舊的;`feature_runs` 沒有這個情境時,新的 unjudged 直接寫入。
  - 推送:步驟 2 擋下,點名該情境,理由是「最新的結果說沒過」。其實同一指紋下有更完整的整套 pass。
- 只能重跑整套或放行才解得開。
- 佐證:file: `scripts/lumos:41021`(`_e2e_case_results`)、file: `scripts/lumos:41049`(`_e2e_keep_old`)。

**4. 只列效能測試方法的情境,永遠通不過步驟 3,而擋下訊息還叫人去跑 `--case`**
severity: major
blocking: 是 — 擋下訊息給的出口(`--case` 指令)無論怎麼跑都解不開,是做出壞系統。
引句:「每個要驗的情境,`feature_runs` 裡都要有一筆 result 是 pass、complete 是 true」
- `_e2e_case_err` 允許一個情境只列 `macrobench`(「至少列一樣」)。
- `_e2e_case_results` 對這種情境永遠回 `unjudged, complete:false`,理由寫「只列了效能(只提醒)」。
- 步驟 3 要求每個要驗的情境「result 是 pass、complete 是 true」。
- 失敗例子:`features.bench.cases.scroll = {"macrobench": ["ScrollBenchmark#scrollList"]}`,只改了 `bench.paths` 底下的檔。
  - 跑 `--case bench.scroll` 後再推,仍被擋,訊息又印同一條 `--case` 指令。
- 同時 finding 3 的機制會讓這筆 unjudged 蓋過先前的整套 pass。
- 佐證:file: `scripts/lumos:40421`(`_e2e_case_err`)、file: `scripts/lumos:41021`。

**5. 歸屬判定用 `git diff --name-only --no-renames` 而不帶 `-z`,中文路徑被引號跳脫後比對不到,被當成「範圍外」默默丟掉**
severity: major
blocking: 是 — 擋推送的判定在這種輸入下 fail-open,與 WHY「判不清就擋」相反。
引句:「分岔點到被推送提交的差異(`git diff --name-only --no-renames`,改名的新舊路徑都算)」
- 新節第 3 步第一條寫了字面指令,沒有 `-z`。現行 `_e2e_changed_files` 的 `--changed` 路徑有帶 `-z`。
- 本機實測:`git show --name-only` 對 `app/播放.kt` 輸出 `"app/\346\222\255\346\224\276.kt"`(core.quotepath 預設)。
  - 這條字串不會落在任何 `app_dirs` / `paths`。
  - 若這是唯一改到的檔,集合為空 → 落入 finding 2 的空真放行。
  - 若混在別的檔裡,這個檔的功能歸屬會被丟掉,該驗的情境少驗。
- 影響:專案裡有中文檔名時發生。lumos 威脅模型明列只顧中英文,所以這屬於範圍內。

**6. 「兩版取聯集」、「功能被拿掉要整套」、「照主線版同名情境涵蓋」這幾條在 spec 自己的邏輯下是死分支**
severity: minor
blocking: 否 — 不會判錯,只是會讓實作者寫出不可達的分支與測不到的測試。
引句:「兩端的 `e2e` 段不一樣(正規化雜湊不同)→要整套」
- 步驟 3 第二條已規定「兩端 `e2e` 段正規化雜湊不同→要整套」。`features` 與 `shared_paths` 都在 `e2e` 段裡。
- 因此走到歸屬那一步時,兩版的 `features` / `shared_paths` 必然相同。
  - 「兩版取聯集」等於任一版。
  - 「功能在主線版有、被推送提交拿掉」不可能發生。
  - 「主線版沒有這個情境就照被推送提交的」與「被推送提交改名或刪掉的不算缺」也不可能發生。
- 失敗例子:`t_android_e2e_gate_by_feature` 無法造出這些分支的輸入。
- 同時這讓 S9 的「分支新加 flow 並跑過驗收→認得」只剩整套路徑,按功能路徑對任何設定改動都要整套。spec 沒寫明這個代價。

**7. 「結束得比…晚」的比較在欄位不可解析、同秒、或缺 `ended` 時沒有定義**
severity: minor
blocking: 否 — 現有寫入端都會產生合法值,只有手改或殘破紀錄才碰到,但判定的失敗方向沒寫。
引句:「推送前檢查比兩邊的結束時間,取較新的那個」
- 欄位是帶時差的 ISO 字串,精度到秒(file: `scripts/templates/android-e2e-run.sh:385` 的 `now()`)。實際寫入端兩邊都有值,跨時區用 `_gov_ts` 轉成帶時區時間就能比,這部分沒問題。
- 失敗例子:`feature_runs["a.b"] = {result: fail, ended: "garbage"}`。`_gov_ts` 回 `None`。
  - 實作若把「比不出來」當成「不晚」,就放行;若當成「晚」,就擋。
  - spec 的「判不清就擋」(S17)列舉裡沒有這一類。
- 同秒(`ended` 相等)時「晚」為假,fail 被忽略。

**8. `passed-by-feature` 治理帳只附情境清單,RETIRE-IF / REVISIT 要的「之後整套跑在沒驗到的功能紅」無法從帳算出**
severity: minor
blocking: 否 — 影響的是回頭條件能不能被評估。
引句:「事件種類 `passed-by-feature`,附情境清單(RETIRE-IF 從這裡數)」
- 新節 RETIRE-IF 與 REVISIT 2027-01-31 要比對「按功能放行的次數」和「之後整套跑在沒驗到的功能紅的次數」。
- 帳只附情境清單,沒有指紋或提交。`runs` 每次整套都覆蓋,`history` 只留 `result` / `run-id` / `ended`,不留是哪一個功能紅。
- 而且整套跑的指紋通常跟當時按功能放行的指紋不同(內容又改過),兩邊無從連起來。
- 另外,`code-loop check` 每次執行(手動重跑、`--keep-going`)都會記一筆,次數會被灌水。

## 逐節結論

- **〈資料怎麼流〉第 4、5 步**:findings 1、5(以及 S8 的衝突)。第 4 步其餘部分(主線挑法、CI、`LUMOS_SKIP_ANDROID_E2E`)已讀,無 finding。
- **〈查證紀錄長怎樣〉**:`feature_runs` 的欄位(`ended`、`run_id`、`commit`、`complete`)在現行寫入端都有,時間比較做得到(finding 7 只是邊角)。「只有放行的紀錄是 null」的說法過期,併入 finding 1。
- **〈推送前怎麼按功能判〉**:findings 1、2、3、4、5、6、8。
- **S8 / S9**:S9 靠整套路徑成立,見 finding 6。
- **S10**:`runs` 為 null 又沒放行的紀錄語意,見 finding 1。
- **S11**:已讀,無 finding。指紋用 tree 物件編號,壓提交或 rebase 後不變。
- **S12**:已讀,無 finding。
- **S13、S14**:已讀,無 finding。
- **S17**:已讀,無 finding;「判定內部出錯→擋」足以涵蓋 `feature_runs` 殘缺的讀取例外。finding 7 的不可解析時間不算「內部出錯」,所以仍是缺口。
- **S29–S33**:findings 2、3、4、6。
- **〈實務隱患〉**:逐類答覆如下。
  - 金流、對外送出:無,spec 的理由成立。
  - 不可逆:無。放行只增不刪,已實作的 `feature_runs` 覆寫由 `_e2e_keep_old` 規則管,新節沒增加刪除。
  - 時間:本機時區、帶時差的 ISO 可跨時區比較(finding 7)。
  - 新舊互讀:舊 lumos 寫的整套紀錄沒有 `feature_runs` 時,`_e2e_record_err` 以 `{}` 讀入,安全。
  - 寫一半:`_write_lf` 原子寫入,推送端只讀 git 樹,無問題。
  - 衍生資料(指紋與紀錄對不上):`_e2e_record_err` 擋指紋欄位不等於檔名。memory-config 造成的範圍外變動見 finding 2。
  - 守衛面:兩個洞是 finding 2 與 5 的空集合 / 引號丟檔。
- **〈回退〉**:已讀,無 finding。

## 固定席逐條判

- **`Systems/bound-tests-gate`**:不影響。
  - 該節點宣稱的行為是「對 impact 固定席上合約綁的測試逐支真跑,紅/懸空/偽證據就擋」。
  - 新一道 `android_e2e` 是獨立的擋下種類,走自己的 rc,不改綁定測試的挑選或執行。
  - 只在 `pp_cl_reason` 對照表與逃生路文字加一種句子。
- **`Systems/pitfalls-code-loop`**:不影響,但有一個條件。
  - 新判定排在所有放行早退之前,與安全證據閘同位置。
  - `blocked=True rc1` 的既有合約不變。
  - 簿記目錄清單加 `.lumos/e2e-records/` 時,spec 已要求「看過那份清單的其他用處」。
- **`Systems/macrobenchmark-adapter` / `android-stability-collector` / `安全證據閘`**:這幾篇只存在於凍結提交,會談目錄沒有,我讀不到它們宣稱的行為。這份設計對這些節點的不影響判定,交編排者在有節點內容時補判。

最嚴重 severity 是 major,blocking 共 5 條(findings 1、2、3、4、5)。
