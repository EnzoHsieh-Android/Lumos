severity: major

我讀完範圍內所有段落,並用 `scripts/lumos`、`scripts/hooks/pre-push`、`ci.yml` 查證。已實作的判定、按功能跑、`_e2e_*` 函式群只當背景,不開 finding。〈回退〉照做退不乾淨,RETIRE-IF 兩條都缺資料來源或缺撤除動作,另有四個局部缺口(findings 3、4、5、8),見下。

**會寫下東西的入口**
- 紀錄的 `waivers`、`feature_runs`、`history`。
- ack(寫進同一份紀錄,要提交)。
- 治理帳的 `waived`、`skipped`、`passed-by-feature`。
- `features`、`shared_paths`(整段 `e2e` 設定都進指紋)。
- 本機的 `history.jsonl`、裝置鎖。

---

**1. 〈回退〉與 RETIRE-IF 的撤除動作沒有可執行的機制,而且〈回退〉列的步驟本身退不乾淨**
severity: major
blocking: 是,實作者照字面做出的「回退」會讓專案卡死或退不乾淨,判準是實作者會做出壞系統。

- **位置**:〈回退〉全節、第一條 RETIRE-IF、第二條 RETIRE-IF。
- **缺口一,「降回只提醒」沒有模式**:
  - 引句:「AI 放行佔全部放行的一半以上,就把擋推送降回只提醒」
  - 〈設定〉沒有 mode/warn 之類的鍵。〈回退〉只有「環境變數一次」和「刪整段 `e2e`」兩條路,都是整道關掉。
  - 照 RETIRE-IF 觸發後,操作者找不到「只提醒」的開關。
  - 對照:新增告警閘有 `_LINT_NEW_GATE_MODES = ("block","warn","off")`。
  - 就算補一個 mode 放進 `e2e` 段,整段 `e2e` 的正規化雜湊都進指紋。切一次模式,所有現存紀錄的指紋全失效,切回來要整套重跑。
- **缺口二,撤掉按功能沒有步驟**:
  - 引句:「就把按功能這條路撤掉、改回只認整套」
  - 〈回退〉完全沒提按功能。它只有「撤掉那次提交」,但按功能是另外已併入主線的提交,不是同一個提交。
  - 唯一的辦法是從設定刪掉 `features` 與 `shared_paths`。這會改 `e2e` 段雜湊,所有舊紀錄換指紋,且本計劃沒寫。
- **缺口三,〈回退〉第一條可能不成立**:
  - 引句:「刪段的那次推送本身用環境變數關,合進主線後判定就不跑」
  - 該推送改用主線版設定,兩端指紋相同,只刪 `e2e` 段本身不會被擋。
  - 但若同一提交把 `stability` 或 `stability_scenarios` 一起拿掉(整理設定時很自然),`memory-config` 那一行會變,就被擋。
  - 計劃沒寫判定要拿哪個提交的 `macrobench.json` 當 `full`,見 finding 5。
- **缺口四,程式回退沒說順序**:
  - 引句:「回退就是撤掉那次提交」
  - 還原 `_macrobench_config` 後,「只有 `e2e` 段」的專案會回到 `macrobench.json 要有 results_dirs` 而 rc 2。
  - 消費專案若先還原 lumos、後刪段,`lumos macrobench` 與效能 L0 先壞。
  - 還原會把 `.lumos/e2e-records/` 從 `_BOOKKEEPING_DIRS` 拿掉。專案裡已提交的紀錄變成一般檔,之後每次提交紀錄都讓代碼審留痕失效。
  - 還原會動 `test_lumos.py` 的 `_PPC_KIND_SENTENCES`,要 Enzo 簽章。無人看顧的回退卡在這裡,〈回退〉沒寫。
  - 〈回退〉也沒提 pre-push 的 `pp_cl_reason`、`ci.yml` 說明、`_KNOWN_GATES`、doctor/enforcement 兩列、skill、消費專案裡已複製的 `android-e2e-run.sh`(舊 lumos 沒有 `judge` 與 `select`)。
- **佐證**:
  - file: `scripts/lumos:38179`(`_LINT_NEW_GATE_MODES`)。
  - file: `scripts/lumos:39423`、`scripts/lumos:39433`(`only_other` 與 results_dirs 檢查)。
  - file: `scripts/lumos:37466`(`_BOOKKEEPING_DIRS` 已含 `.lumos/e2e-records/`)。
  - file: `scripts/lumos:40543`(指紋的 `e2e-config` 與 `memory-config` 兩行)。

---

**2. 第二條 RETIRE-IF(按功能)與 REVISIT 2027-01-31 從現有資料數不出來**
severity: major
blocking: 是,撤除條件量不到,等於沒有撤除條件。

- **位置**:第二條 RETIRE-IF、REVISIT:2027-01-31、`passed-by-feature` 那條、〈實務隱患〉。
- **失敗例子**:2027-01-31 到期,要數「按功能放行之後整套跑在沒驗到的功能紅」的次數,輸入是治理帳與 `.lumos/e2e-records/`。
  - **分子沒有來源**:
    - 整套 judge 只改紀錄,不寫治理帳。紀錄的 `runs` 每次被整套覆蓋。
    - `history` 只存 result、run-id、ended,沒有哪個功能紅。
    - 逐項明細只在 git 忽略的本機 `history.jsonl`,各機器各一份。
  - **分母沒有關聯鍵**:
    - 引句:「附情境清單(RETIRE-IF 從這裡數)」
    - 事件只帶情境清單,不帶指紋或提交,無法對到「之後」的整套跑。
    - 每次 `code-loop check` 通過都記一筆,同一次推送被重試、被 `--keep-going` 預演就重複計。
  - **窗口放不下**:
    - 治理帳讀取只讀檔尾 24MB,`_SLOT_METRIC_MAX_WEEKS = 8` 註解說「約兩個月」。
    - RETIRE-IF 要「跑滿三個月」,讀不到頭。
    - `passed-by-feature`、`waived`、`skipped` 都不在 `_GOV_LOCAL_PAIRS`,進版控帳,受同一上限。
  - **偏差**:整套只在共用或對不到功能時才被強迫跑(S32),「按功能放行後被整套抓到」的樣本天生偏少。沒人自願跑整套時指標恆為零,撤除條件永遠不觸發。
  - **日期**:引句:「按功能放行上線後,連續兩個真實專案跑滿三個月」。按功能的推送前判定還沒實作,「兩個真實專案」目前只列了 KDS 一個,2027-01-31 到期時不可能滿三個月。
- **佐證**:
  - file: `scripts/lumos:41306`(整套 judge 只改紀錄、不寫治理帳)。
  - file: `scripts/lumos:4364`(`_GOV_TAIL_CAP = 24 * 1048576`)。
  - file: `scripts/lumos:4792`(`_SLOT_METRIC_MAX_WEEKS = 8`)。
  - file: `scripts/lumos:1637`(`_GOV_LOCAL_PAIRS`)。

---

**3. 「整套跑是推上主線前最後一次全面驗」這句宣稱沒有任何機制,撤掉按功能後主線上未全面驗的版本也沒有補驗步驟**
severity: major
blocking: 是,〈實務隱患〉用一句不成立的緩解把風險標成已處理。

- **位置**:〈實務隱患〉按功能放行那一條、〈推送前怎麼按功能判〉第 3 步。
- **引句**:「整套跑仍是推上主線前最後一次全面驗」
- **失敗例子**:
  - 判定順序第 3 步不分「推分支」與「推主線」。
  - 專案只改 `player` 的檔、只跑過 `--case player.open-close`,就可以直接推到主線並按功能放行。
  - `list` 功能被它改壞(沒列進 `shared_paths`),主線上從頭到尾沒有人被強迫跑整套。
  - 依照 RETIRE-IF 撤掉按功能後,判定只比較「分岔點與被推送提交」。這些按功能放行過的版本成為新的基準,不會被重驗,〈回退〉也沒有「重建整套基準」的步驟。
- **佐證**:file: `scripts/lumos:40543`(指紋只吃兩端的樹,沒有「主線需有過整套」這類狀態)。

---

**4. 紀錄的 `runs: null` 語意被偷換,S10 與〈查證紀錄〉的原文在按功能撤掉或實作順序上會放行沒驗過的版本**
severity: major
blocking: 是,字面實作會讓只有 `feature_runs` 的紀錄被當放行。

- **位置**:S10、〈查證紀錄〉`runs` 欄、S27。
- **引句**:
  - 「只有放行、`runs` 是 null 的紀錄應放行」
  - 「只有放行的紀錄是 null」
- **失敗例子**:
  - S27 讓「沒有任何放行、`runs` 是 null、只有 `feature_runs`」成為常態紀錄。
  - 實作者依〈查證紀錄〉那句以 `runs is None` 當放行的判斷,就會把這種紀錄放行。
  - 按功能撤掉(RETIRE-IF 觸發、判定退回 S8/S10 的語意)時,已提交的 `feature_runs`-only 紀錄在退回版本下也被誤判成放行。
  - 〈資料怎麼流〉第 4 步「有放行→過」沒說「放行」=`waivers` 非空,與 S10 的措辭不一致。
- **佐證**:
  - file: `scripts/lumos:40589`。`_e2e_record_err` 的註解寫明「不能只看 runs 是 null 就當放行」,也就是現有實作已經知道這個坑,計劃文字沒跟上。
  - schema 仍是 1 且未升版,舊版讀到的新紀錄不會因 schema 被擋。判定「遇到比自己新的版本就擋」對這個語意改變完全無效。

---

**5. 指紋演算法沒有版本標記,lumos 升降版會讓所有紀錄「找不到」,且訊息誤導成沒跑過驗收**
severity: minor
blocking: 否,代價是多重跑一次驗收,不會做出錯誤放行。

- **位置**:〈查證紀錄〉`schema`、`fingerprint`,decisions d1,S2 例外。
- **失敗例子**:
  - d1 把 `stability` 與 `stability_scenarios` 加進指紋,但 `schema` 與指紋輸入都沒有版本。
  - 開了記憶體的專案,回退到沒有 d1 的 lumos,或在兩台 lumos 版本不同的機器間切換,都會因指紋不同而一律「找不到紀錄」。
  - 擋下訊息是「重跑驗收」,看不出是演算法換了,不是沒驗。重跑寫出的新紀錄,再升回來又對不上。
- **另一個相關缺口**:S2 與 d1 沒說判定時 `memory-config` 的 `full`(整份 `macrobench.json`)取自哪個提交。
  - 〈資料怎麼流〉第 4 步說 `e2e` 段用同一份設定,但 `full` 沒說。
  - 若分岔點端與被推送端各取各自的 `full`,只要被推送提交動了 `stability`,兩端指紋必不同。
- **佐證**:file: `scripts/lumos:40543`。`mem` 那一段只在 `e2e.get("stability") and isinstance(full, dict)` 時才接進雜湊。

---

**6. 新增 `app_dirs` 項目的提交,在分岔點端會算指紋失敗而被擋,與 S9 矛盾**
severity: major
blocking: 是,〈實務隱患〉自己建議的補法會被判定擋死。

- **位置**:〈資料怎麼流〉第 4 步「何時要求」、S9、S17。
- **引句**:
  - 「分支新加 flow 或改 `app_dirs` 並跑過驗收時,判定應認得那份紀錄」
  - 「用同一份設定算分岔點與被推送提交兩端的指紋」
- **失敗例子**:
  - 分支把新模組 `feature-x` 加進 `app_dirs`,這是〈實務隱患〉要求的 `--preflight` 修補。
  - 用被推送提交的設定去算分岔點端的指紋時,`feature-x` 在分岔點的樹不存在。
  - `_e2e_fingerprint` 回「app_dirs 的 … 不存在」,判定「判不清就擋」,印的原因還是「被推送提交的 `app_dirs` 有一項不存在」(S17)。
  - S17 的文字只提被推送提交,沒涵蓋分岔點端。
- **佐證**:file: `scripts/lumos:40543`。`gone` 非空就 `return None, "app_dirs 的 … 在 … 不存在"`,沒有端別區分。

---

**7. doctor 與 enforcement 的「待看 AI 放行」掃描範圍沒定義,舊紀錄永不清除,回退或關閉判定後仍然報警**
severity: major
blocking: 是,掃描範圍留白,字面實作會做出永久紅燈。

- **位置**:〈資料怎麼流〉第 5 步「通知」、S14、〈查證紀錄〉`waivers`。
- **引句**:
  - 「被推送提交的紀錄裡有還沒被人看過的 AI 放行時」
  - 「`lumos doctor` 把還沒人看過的 AI 放行列成提醒」
  - 「舊紀錄檔不自動刪」
- **失敗例子**:
  - S14 只定義了推送那一行(看被推送提交的紀錄)。doctor 與 enforcement 沒說掃哪些紀錄。
  - 若掃工作目錄全部紀錄:有人用無終端放行了一版,分支沒合併、換電腦,或紀錄沒提交,這筆就永遠沒人 ack。`lumos enforcement` 那一列永久「沒生效」,開場提示永遠印。
  - 這與已關掉判定(刪 `e2e` 段、或 `LUMOS_SKIP`)的專案同樣成立,因為舊紀錄還在。
  - 若只掃 HEAD 提交的紀錄,則別條分支的 AI 放行永遠不被通知,與 WHY 宣稱的「每次推送、開場與體檢都把還沒人看過的 AI 放行列出來」不符。
  - `waivers` 單筆欄位的鍵名與缺欄位(沒有「看過」欄)時的預設,計劃也沒寫。
- **佐證**:file: `scripts/lumos:40589`。紀錄驗證只檢查 `waivers` 是清單,不檢查單筆欄位。

---

**8. 治理帳的 `skipped` 先例引用不實,事件種類也偏離慣例**
severity: minor
blocking: 否,判準是 REVISIT 到期時 `skipped` 的次數可能是零,但不會造成錯誤放行。

- **位置**:〈資料怎麼流〉第 4 步第一個子點、REVISIT:2026-12-31「回頭看治理帳 android-e2e 的 skipped」。
- **引句**:「記一筆治理帳 skipped(照新增告警閘 `LUMOS_SKIP_LINT_NEW` 的做法)」
- **失敗例子**:
  - 新增告警閘的 `LUMOS_SKIP_LINT_NEW` 只把判定結果的 `status` 設成 `off`,沒有寫治理帳事件。
  - 實作者「照做法」會不寫帳,REVISIT 的次數恆為零。
  - 其他閘的環境變數略過一律是 `skipped-env`,且 `[retire:] 度量` 只收 `blocked/warned/skipped-env/hinted/acked`。計劃新造的 `skipped` 配不上機器式度量。
- **佐證**:
  - file: `scripts/lumos:38731`(`LUMOS_SKIP_LINT_NEW` 分支只設 status)。
  - file: `scripts/lumos:4790`(`_SLOT_METRIC_KINDS`)。
  - file: `scripts/lumos:45651`(note-shape 的 `skipped-env`)。

---

**範圍內各節已讀**
- 〈資料怎麼流〉第 4、5 步:findings 1、4、6、7、8。
- 〈查證紀錄長怎樣〉:findings 2、4、5。
- 〈推送前怎麼按功能判〉:findings 2、3、4、6。
- S8–S14、S17、S29–S33:S9、S10、S14、S17 有 finding;S29、S30、S31、S32、S33 已讀,在回退鏡頭下無 finding。
- RETIRE-IF 與 REVISIT:findings 1、2、8。

**交叉引用核對**:〈實驗室驗收〉、〈按功能與使用情境跑〉、S26、`r2-intake.md`、REVISIT 回頭看次數,以及 `Projects/推送前一次列出全部擋下原因_計劃`〈做法〉5,目標都存在。

**實務隱患(逐類)**
- 金流:無,只讀驗收輸出與程式檔。
- 對外送出:無,紀錄只進專案自己的 git。
- 不可逆:有,finding 3(已推上主線的按功能放行版本沒有補驗步驟)與 finding 1(回退卡在簽章)。
- 資料版本相容:有,findings 4、5。
- 併發與鎖:無新洞,讀改寫鎖已涵蓋。
- 守衛面(誤擋與漏擋):有,finding 6 是誤擋,finding 3 是漏擋。

最嚴重 severity 是 major,blocking 共 6 條(findings 1、2、3、4、6、7);minor 共 2 條(findings 5、8),blocking 否。
