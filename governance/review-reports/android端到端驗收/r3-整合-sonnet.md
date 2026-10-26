severity: major

**固定席判定**
- bound-tests-gate 的 ★INVARIANT★(code-loop check 對受波及合約綁的測試逐支真跑,紅或證不出跑過就 blocked rc1):不影響。android_e2e 是 `_codeloop_guard_verdict` 裡多一道,經 `kg.hit` 進 `_codeloop_kg_finish` 的 blocks,不動 2.5 步的判斷和帳。不帶 `--keep-going` 時,e2e 若排在安全證據之後、2.5 之前,會讓 e2e 擋下的那次呼叫先早退、跳過合約測試。這跟安全證據閘是同一個前例,pre-push 固定帶 `--keep-going`,不構成違反。
- pitfalls-code-loop 的 reason_kind 對照表和 `_cl_reason_kind_sites` 守衛(③):不影響守衛本身。android_e2e 是字面字串,不踩「值要是字面」那條。但這份設計會讓另外兩支守衛翻紅(見 #4)。

**1. 〈資料怎麼流〉第 4 步「每次跑這道(過或擋都算)多印一行」會被 pre-push 在放行路徑濾掉**
severity: major
blocking: 是 — 照 spec 做出來,AI 放行通知在它存在的主要情境(因為放行才通過的推送)完全看不到。
引句:「每次跑這道(過或擋都算),只要被推送提交的紀錄裡有還沒人看過的 AI 放行,就多印一行」
- spec 段落:第 4 步最後一條(AI 放行待看行),以及〈推送前怎麼按功能判〉的「按功能放行:驗了…」行,和〈這次要改到的地方〉的接線清單。
- 問題:接線只列了 `_cl_say_block`、`_codeloop_kg_finish`、`pp_cl_reason`、逃生路文字、ci.yml。放行路徑的印出走 `_cl_say_ok_extras`,spec 沒列。hook 對 rc=0 的輸出只放行含這四個詞的行:`提醒`、`受波及合約測試`、`表態閘`、`安全證據`。
- 失敗例子:紀錄有一筆 AI 放行 → check 回 0 → 印「有 1 筆 AI 放行還沒人看過」→ hook 的 grep 把這行丟掉 → 使用者推送時看不到。「按功能放行:驗了 …」同理。S14、S12 的測試若只直接跑 `code-loop check` 會綠,真的 `git push` 才不見。
- 佐證:file: `scripts/hooks/pre-push:620` — rc=0 時 `grep -E '提醒|受波及合約測試|表態閘|安全證據'` 只放行這四個詞。file: `scripts/lumos:65962` — 放行訊息只靠 `_cl_say_ok_extras(dv)` 加印。file: `scripts/lumos:66041` — 這支函式沒有 e2e 分支。另外 `scripts/lumos:65231` 附近每次呼叫要重置 `_codeloop_guard_verdict.last_*`,spec 也沒提新的 `last_e2e`。

**2. 按功能放行對「只列效能」或略過效能的情境永遠過不了,而且與「效能只提醒」及涵蓋定義矛盾**
severity: major
blocking: 是 — 實作者照寫會做出一道「某些功能只能走整套」、而且擋下訊息叫人跑一個永遠不會變 pass 的指令的閘。
引句:「每個要驗的情境,`feature_runs` 裡都要有一筆 result 是 pass、complete 是 true;」
- spec 段落:〈推送前怎麼按功能判〉第 3 步「每個要驗的情境…result 是 pass、complete 是 true」;S27;〈一個使用情境是什麼〉。
- 問題:設定允許一個情境只列 `macrobench`,四種至少列一樣即可。已上線的寫入端對這種情境一律記 `result: unjudged, complete: false`。另外,情境列了效能而用了 `--no-perf`,`skipped=["macrobench"]`、complete 為 false。但同一段「涵蓋」的定義只列 flow、畫面、記憶體,不含效能;整套跑的效能也只進 notices,不擋。
- 失敗例子 A:`list.scroll` 只列 `ScrollBenchmark#scrollList`,改了 `MainActivity.kt` → 歸屬 list → 要驗 `list.scroll` → 每次 `--case list.scroll` 都寫 unjudged / complete false → 閘永遠擋,並印同一條指令。
- 失敗例子 B:先整套跑 pass,之後跑 `--case list.scroll`(只列效能)寫入較晚的 unjudged → 第 2 步「feature_runs 有結束得比 runs 晚而且不是 pass」→ 擋下。整套明明通過,卻被一次無可判項目的按功能跑推翻。
- 失敗例子 C:`--case x.y --no-perf` 結果 pass 但 complete false → 閘擋,spec 的涵蓋定義卻說效能不必涵蓋。
- 佐證:file: `scripts/lumos:41021`(`_e2e_case_results`)— `"complete": not skipped and bool(rs)`,`rs` 只含 ui、visual、stability 的項目;沒有項目時 `result = "unjudged"`。file: `scripts/lumos:40411`(`_e2e_case_err`)— `if not any(c.get(k) for k in kinds)` 允許只列 macrobench。

**3. 最外層 `stability` / `stability_scenarios` 改弱:指紋會變,但「指紋範圍裡的改動檔」是空集合,按功能路徑空過**
severity: major
blocking: 是 — d1 想擋的「記憶體標準在指紋外改弱」,在推送前檢查這一側被繞過。
引句:「兩端的 `e2e` 段不一樣(正規化雜湊不同)→要整套。設定改了,每個情境驗什麼都可能變。」
- spec 段落:〈推送前怎麼按功能判〉第 3 步「改到的檔…只留指紋範圍裡的檔」「兩端的 e2e 段不一樣(正規化雜湊)→要整套」;決策 d1;S2。
- 問題:e2e 段開了記憶體時,最外層 `stability` 與 `stability_scenarios` 另算一段雜湊接進指紋。這兩段不在 e2e 段內,所以「e2e 段雜湊不同」不成立;`.lumos/macrobench.json` 不在指紋檔案清單裡,所以「改到的檔」不含它。
- 失敗例子:分支只把 `stability_scenarios.player_cycle.cycles` 從 20 改成 1 →
  - 兩端指紋不同,閘要求紀錄。
  - 在新指紋上隨便對一個情境跑一次 `--case`,產生有 `feature_runs` 的紀錄。
  - 改到的檔(範圍內)為空,要驗的情境為空。
  - 「全部符合→過」,印「按功能放行:驗了 <空>」。
  - spec 沒定義「指紋不同但範圍內改動檔為空」的結果。
- 佐證:file: `scripts/lumos:40543`(`_e2e_fingerprint`)— `if e2e.get("stability") and isinstance(full, dict)` 才接 `memory-config` 雜湊。file: `scripts/lumos:40885`(`_e2e_changed_features`)— 開發端把 `.lumos/macrobench.json` 當「會影響驗收」的檔,閘這側的範圍定義卻沒有。

**4. 對照表新增 `android_e2e`,spec 只說「`_PPC_KIND_SENTENCES` 一起加」,兩支守衛測試會翻紅**
severity: major
blocking: 是 — 照 spec 清單做完推送前閘必紅,而且得連改兩處要 Enzo 簽章的測試檔。
引句:「測試檔的 `_PPC_KIND_SENTENCES` 一起加(改測試檔要 Enzo 簽章)」
- spec 段落:第 4 步「位置與接線」、〈這次要改到的地方〉對照表一條、S12。
- 問題:`t_prepush_cl_reason_table_matches_lumos` 用 `^\s+([a-z_]+)\) echo` 解析 hook,`android_e2e` 含數字 2,這個正規式抓不到,hook 抽出的種類集合永遠少一個,①必紅。`t_prepush_cl_reason_sentences_match_plan` 用 `` `([a-z_]+)` 是「…」 `` 解析計劃正本,也抓不到 `android_e2e`;它還硬寫 `len(got) == 5` 和標記字串「**對照表五句的正本在這裡**」。
- 失敗例子:hook 與 `_PPC_KIND_SENTENCES` 都加了第六句 → 前者 ① 紅(`set(hk) == emitted` 差一個);後者 ②(`got == _PPC_KIND_SENTENCES`)紅,因為計劃抽出的仍是五句。
- 佐證:file: `scripts/test_lumos.py:79955`(hook 解析)、`scripts/test_lumos.py:79985`(`len(got) == 5`)、`scripts/test_lumos.py:79983`(計劃解析)。file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:68` — 標記字串是「對照表五句的正本在這裡」。file: `scripts/hooks/pre-push:138-146` — 現有種類全是純小寫底線。

**5. 按功能放行的安全網宣稱沒有機制,RETIRE-IF 與 REVISIT 的資料來源不存在**
severity: major
blocking: 是 — 撤除條件量不出來,「靠整套兜底」的承諾也沒有任何規則兌現。
引句:「整套跑仍是推上主線前最後一次全面驗(見下一行回頭條件)」
- spec 段落:〈實務隱患〉「整套跑仍是推上主線前最後一次全面驗」;第 160 行 REVISIT 2027-01-31;〈推送前怎麼按功能判〉的 RETIRE-IF 與 passed-by-feature 治理帳。
- 問題 A:判定順序沒有區分推分支或推主線。runs 缺或沒過時,第 3 步一律走按功能,過了就放行。沒有任何規則要求推上主線前有一次整套 pass;只有碰到共用路徑或對不到功能的檔才要整套。
- 問題 B:RETIRE-IF 與 REVISIT 要數「按功能放行之後,整套跑在沒驗到的功能紅」的次數。但整套跑不被要求,這個事件只在人自願跑整套時才可能出現(選擇偏差)。治理帳只記 `passed-by-feature`(附情境清單)、`waived`、`skipped`,不記整套結果,也不記哪個功能紅。`history` 裡整套結果只有 result,不分功能,也沒有與先前放行的指紋關聯。
- 問題 C:`passed-by-feature` 沒進 `_GOV_LOCAL_PAIRS`,預設寫進版控帳 `docs/.governance-log.jsonl`,spec 沒決定去向。pre-push 每個 ref、每次重試都會再記一筆,筆數與「按功能放行次數」不等。
- 失敗例子:專案 3 個月內只用按功能跑和推送,從不整套跑 → 「之後整套紅次數」恆為 0 → 撤除條件永不觸發,但別功能被共用程式改壞的風險從沒被驗過。
- 佐證:file: `scripts/lumos:1638-1651` — `_GOV_LOCAL_PAIRS` 白名單不含 android-e2e;未列入的閘名事件預設進版控帳。file: `scripts/lumos:15996`(`_KNOWN_GATES`)尚無 `android-e2e`;spec 只說加閘名,沒說事件去向與去重。

**6. `lumos enforcement` / 開場提示的「AI 放行待看」列語意不合,且條件與範圍未定**
severity: major
blocking: 是 — 每個專案的開場提示會唸「防護有 1 層沒生效」並給錯的修法。
引句:「有待看時標成沒生效,開場提示就會印出來」
- spec 段落:第 5 步「通知」。
- 問題:`enforcement` 查的是「有沒有裝上/接上」(docstring 與輸出標題都這樣寫)。待看的 AI 放行是資料狀態,不是防護層。把它標 inactive 會:
  - 讓 `enforcement_summary` 的分母多一個永遠可能「沒生效」的層。
  - 開場掛鉤 `_enforcement_alert` 只點名 inactive/degraded,印「防護有 N 層沒生效…多半是在專案根跑 lumos install --force」,修法完全錯,真正要做的是 `waive --ack`。
- 另有三處沒說清:
  - 這一列是否只在有 `e2e` 段的專案出現。spec 寫「多一列」,字面是全部專案,Backend 之類沒有 Android 的專案也會出現。
  - 掃描範圍是只看 HEAD 指紋的紀錄,還是掃整個 `.lumos/e2e-records/`。spec 自己說舊紀錄不自動刪,若掃全部,舊指紋上的 AI 放行會永遠待看,每筆都得有終端確認再提交紀錄才清得掉。
  - 沒有「一次標看過」的指令,`--ack` 只收單一指紋。
- 佐證:file: `scripts/lumos:36029`(`cmd_enforcement`)— 「這查的是有沒有裝上/接上,不是判得對不對」,`active < total` 時印 `lumos install --force`。file: `scripts/hooks/claude/lumos-entry-hook.py:182`(`_enforcement_alert`)— 固定附 install --force。file: `scripts/lumos:36016`(`enforcement_summary`)— 狀態值域只有 active/inactive/degraded/unknown/stale 等,沒有「待處理」。

**7. ci.yml 擋下說明接線是死碼,且「CI 不跑」排在「沒 e2e 段不跑」之前,會對所有專案印一句**
severity: minor
blocking: 否 — 不會做出壞系統,只是白改一處文字,並讓非 Android 專案在 CI 多一行雜訊。
引句:「在 CI 裡(`_in_ci`)不跑這道,印一句」
- spec 段落:第 4 步第一條與「位置與接線」;〈這次要改到的地方〉ci.yml 一條。
- 問題:第 4 步第一條說在 CI 裡(`_in_ci`)不跑這道。ci.yml 的 `code-loop gate` 步驟確實跑 `code-loop check`,但這道在 CI 恆不跑,android_e2e 永遠不會在 CI 擋下,在 ci.yml 的 `::error::` 文字裡列它是死條目。
- 另外,bullet 順序是先判 CI 並印「第一版只在本機推送時判」,後面才判「主線版沒有 e2e 段→不跑」。照字面,沒有 `e2e` 段的專案在每次 CI 推送都會印這句,違反安全證據閘的「沒登記痕跡輸出一字不變」慣例。
- 佐證:file: `.github/workflows/ci.yml:221-224` — CI 呼叫 `code-loop check`,錯誤訊息列了四種原因,android_e2e 不可能出現。file: `scripts/lumos:225`(`_in_ci`)— 看 `CI` 或 `GITHUB_ACTIONS`,GitHub Actions 恆為真。

**8. 「照 LUMOS_SKIP_LINT_NEW 記治理帳 skipped」:被引用的前例沒有記帳**
severity: minor
blocking: 否 — 實作者查前例找不到記帳程式碼,要自己設計,不影響正確性。
引句:「環境變數 `LUMOS_SKIP_ANDROID_E2E` 有設時整道關掉,記一筆治理帳 skipped(照新增告警閘 `LUMOS_SKIP_LINT_NEW` 的做法)」
- spec 段落:第 4 步第一條;PRIOR-ART「環境變數整道關掉、留帳的做法」;REVISIT 2026-12-31 回頭看 skipped 次數。
- 問題:`LUMOS_SKIP_LINT_NEW` 只回 `status: off`,沒有任何治理帳寫入。實際有留帳的前例是 `LUMOS_SKIP_NOTE_SHAPE`,事件種類叫 `skipped-env`,不是 `skipped`。
- 失敗例子:實作者照「照 LUMOS_SKIP_LINT_NEW 的做法」去找記帳碼,找不到;REVISIT 數 `skipped` 的人與寫 `skipped-env` 的前例對不上。
- 佐證:file: `scripts/lumos:38731-38733` — 只設 `out["status"]` 為 off,無 `_gate_event`。file: `scripts/lumos:45647-45651` — `LUMOS_SKIP_NOTE_SHAPE` 才寫 `"skipped-env"`。

**9. 新舊段落說法不一致、過期待辦與不可達規則**
severity: minor
blocking: 否 — 新節自稱「接在 S8 讀到合格紀錄之後」,實作者不會被誤導,但三個月後接手的人會讀到互相矛盾的文件。
引句:「沒放行就看最近一次結果:result 是 pass 而且跑過的塊涵蓋主線版要求的」
- spec 段落:首段白話、第 4 步「怎麼判」、S8、S10、S32、〈這次要改到的地方〉。
- (a) 首段白話、第 4 步「其他→擋」、S8「找不到、最近一次是 fail 或 unjudged…擋下」,都沒更新「runs 缺或不是 pass 時改走按功能」。S10「只有放行、runs 是 null 的紀錄應放行」,與已上線的 `_e2e_record_err`(runs 為 null 但有 feature_runs 也合法)並存,哪種 runs 為 null 的紀錄放行沒講。
- (b) 第 3 步「兩版 features 取聯集」「主線版沒有這個情境就照被推送提交」「功能被拿掉→要整套」,以及 S32 的最後一個條件,都不可達:兩端 e2e 段雜湊相同才會走到這裡,而 features 在 e2e 段內,等於兩版 features 必然相同。
- (c) 〈這次要改到的地方〉「簿記目錄清單加 `.lumos/e2e-records/`」已經做完,程式與 pitfalls-code-loop 都已有。
- (d) 技能 `SKILL.md` 〈端到端驗收〉的「紅了看哪裡」結尾仍寫「目前推送前檢查還不會擋沒驗收的推送,也還沒有放行指令」,description 與跑法表寫「推之前整套跑一次」「準備推送…整套跑」,與按功能放行並存。〈這次要改到的地方〉寫「補 E2E 驗收一節」,但該節已存在,要的是改寫那幾句。
- 佐證:file: `scripts/lumos:40589`(`_e2e_record_err`)— runs 為 null 且有 feature_runs 合法。file: `scripts/lumos:40543`(`_e2e_fingerprint`)— `json.dumps(e2e, …)` 整段 e2e 進雜湊。file: `scripts/lumos:37466-37469` — `.lumos/e2e-records/` 已在 `_BOOKKEEPING_DIRS`。file: `skills/lumos-android-evidence/SKILL.md:56` — 過期句子。

**10. `shared_paths` 要改的落點與檢查規則沒列齊**
severity: minor
blocking: 否 — 漏的是文件與 help,不影響判定行為,但這是 spec 自己承認的唯一防線。
引句:「路徑寫法同 `features` 的 `paths`,S26 那套檢查照用」
- spec 段落:〈推送前怎麼按功能判〉設定一條、S29、〈這次要改到的地方〉、S21。
- 問題 A:〈實務隱患〉說共用程式漏標進 `shared_paths` 就擋不住。但 S21 列的 skill 六件事(接入順序、怎麼跑、紅了看哪裡、怎麼放行、AI 放行被列出、怎麼整道關掉)沒有 `shared_paths`;SKILL.md:48 逐項列 `e2e.features` 的欄位,README.md 的「功能對照表」段與 README.en.md 也各有一份,都沒有它。〈這次要改到的地方〉也沒列這些。
- 問題 B:S29「寫了不存在的路徑也擋」與「S26 那套檢查照用」衝突。已上線的 `features.paths` 只驗路徑形狀,不驗存在(`_e2e_cfg_err` 只驗 `app_dirs` 與 `flows` 存在),所以 `shared_paths` 的存在檢查是新增規則,不是「照用」。
- 問題 C:推送時用哪一版的樹檢查 shared_paths 存在也沒定。判定側對提交樹另外查,不經 `_e2e_cfg_err`。主線版 shared_paths 列了後來被刪或改名的檔,主線版變成「e2e 段不合格」(S17)而擋所有人,spec 沒說這個情境。
- 佐證:file: `scripts/lumos:40493-40505`(`_e2e_cfg_err`)— 存在檢查只有 `app_dirs + flows`。file: `skills/lumos-android-evidence/SKILL.md:48`、`README.md:386`。

**11. 閘要讀的 `feature_runs` 項目欄位與 `waivers` 結構在 spec 裡沒有名字**
severity: minor
blocking: 否 — 已上線的 `feature_runs` 寫端欄位一致,只是 spec 沒寫全。`waivers` 尚未實作,結構要在實作時定。
引句:「`feature_runs`:按功能跑的結果,`功能.情境` → result、complete、skipped、每項結果、run_id、ended、commit」
- spec 段落:〈查證紀錄長怎樣〉`feature_runs` 與 `waivers` 兩條,〈推送前怎麼按功能判〉第 3 步。
- 問題 A:寫端實際欄位是 `result`、`complete`、`skipped`、`items`(每項 `kind`、`name`、`result`)、`run_id`、`ended`、`commit`,另有可選的 `reason`。spec 寫「每項結果」「那筆的項目」,從沒給 `items` 這個鍵,也沒說 `skipped` 的值是 `macrobench` / `stability`。
- 問題 B:`_e2e_record_err` 只驗 `feature_runs` 各筆的 `result` 在 E2E_RESULTS 內,不驗 `complete` 是否布林、`items` 是否清單、`ended` 能否解析。第 3 步「結束得比 runs 晚」在 `ended` 缺或壞時沒有定義,S10 的「讀不懂」清單也沒涵蓋。
- 問題 C:`waivers` 只寫「誰、時間、理由、有沒有被人看過」,沒有鍵名。閘、doctor、enforcement、`--list`、`--ack` 五個讀者共用它,第 1 步「有放行→過」也沒說什麼樣的元素算數。例如 `"waivers":[{}]` 或 `[null]` 算不算放行。
- 佐證:file: `scripts/lumos:41021-41046`(`_e2e_case_results`)與 `scripts/lumos:41062-41107`(`_e2e_feature_record`)為欄位寫端。file: `scripts/lumos:40589-40606`(`_e2e_record_err`)為讀端驗證。

**12. 新增 `android-e2e waive` 子命令,〈這次要改到的地方〉沒列 HELP_WHEN**
severity: minor
blocking: 否 — 守衛測試會翻紅,實作者能自己補,這個坑在本計劃的 Systems 筆記已記過一次。
引句:「新子命令 `lumos android-e2e`(judge、waive)與它的家」
- spec 段落:〈這次要改到的地方〉第一條。
- 問題:`waive` 是二層子指令,`t_every_subcommand_has_when` 會檢查二層的 `--help` 是否含「什麼時候用:」;`HELP_WHEN` 表目前有 `android-e2e judge`、`select`、`history`,沒有 `waive`。Systems 筆記已有同類 PITFALL。
- 佐證:file: `scripts/test_lumos.py:11891-11893`。file: `scripts/lumos:66695-66698` 為現有條目。

**13. 第 5 步「有終端但沒人答時等 LUMOS_TTY_TIMEOUT 秒」對 stdin 是終端的情況不成立**
severity: minor
blocking: 否 — 只有「stdin 是 tty 但沒有人在」這個窄情境(例如無人看顧的 tmux 驅動)會卡,一般 Claude Code 的 Bash 沒有 tty,會立即得 None。
引句:「有終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒,預設 30」
- spec 段落:第 5 步第二條、S13。
- 問題:`_confirm_tty` 在 `sys.stdin.isatty()` 為真時直接 `input(prompt)`,沒有逾時,逾時只在 `/dev/tty` 開啟那條路。
- 失敗例子:無人看顧但 stdin 掛在 pty 上 → `waive` 永遠卡在提示,記不出 AI 放行。
- 佐證:file: `scripts/lumos:33561-33600` — `isatty` 分支無逾時。

**逐節狀態**
- 〈資料怎麼流〉第 4、5 步:有 finding(#1、#5、#6、#7、#8、#9、#13)。
- 〈查證紀錄長怎樣〉:有 finding(#11)。
- 〈推送前怎麼按功能判〉:有 finding(#2、#3、#5、#9、#10)。
- 〈這次要改到的地方〉:有 finding(#4、#9、#10、#12)。
- 條款 S8–S14、S17、S29–S33:有 finding(#4、#9、#10)。S17 的 `app_dirs` 不存在、判不清就擋,與程式現況一致,已讀無 finding。
- 〈實務隱患〉:有 finding(#5)。
- 〈回退〉:已讀,無 finding。回退刪段與環境變數兩條路徑與程式現況相容。

**實務隱患鏡頭**
- 金流、對外送出:無。紀錄只進專案自己的 git,不碰交易。
- 不可逆:放行與紀錄只增不刪,無。
- 守衛面:有,見 #1、#3、#5。
- 設定檢查與文件同步面:有,見 #6、#9、#10。

最嚴重 severity 是 major;blocking 共 6 條(#1 至 #6)。
