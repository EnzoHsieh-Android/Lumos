severity: major

我把 r2-snapshot.md 從頭讀到尾,再對照 `/Users/enzo/harness/lumos-highrisk-evidence` 的程式、手冊、測試、治理帳和 r1 卷證。我沒有在 lumos 的工作目錄寫任何檔,也沒有建臨時目錄。

**一句白話**:這份修訂稿的主幹(設計審過了,風險高就套風險低那一套「新行為先紅」)能走通。但接在原文旁邊的補丁有六處會讓接手的人撞牆。這六處是:舊說法漏列、手冊流程接點沒講、預期值表和先紅的順序互相卡住、風險低的「測試名不重複」檢查沒帶過來、實作後重跑會被誤擋、迴圈編號對不上就悄悄不生效。

---

1. 「跟著改的說法」清單漏掉至少七處使用者看得到、仍寫著舊規則的地方。
引句:「舊規則散在這些地方,同一個提交改掉」
severity: major
blocking: 是 — 這些文字會繼續叫人走舊路(風險高設計審過就直接實作),沒有任何測試會因此變紅。
- 做法 5 只列了注入範本、`lumos-design-loop` 手冊「先判門」那段,以及 `lumos-project-notes` 的 `03-寫回圖譜.md` 和 `reference.md`。
- 實際還有這幾處寫著舊說法:
  - file: `docs/指令參考.md:68`(「風險高只印不擋」)
  - file: `docs/command-reference.md:68`(英文版「high-risk only prints」)
  - file: `CLAUDE.md:90`、`AGENTS.md:91`(「風險高再進實作前的審查迴圈」)
  - file: `skills/lumos-project-notes/commands/INDEX.md:19`(「風險高:…紅綠只印、再進審」)
  - file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:12`(「紅綠只印,接著 loop next」)
  - file: `skills/lumos-design-loop/reference.md:535`(「綁的測試真跑印紅綠不擋」)
- 做法 5 把 `reference.md` 寫得不指明是哪一份。`skills/` 下有三份 `reference.md`,只有 `lumos-project-notes` 那份講 `signoff`,所以還得猜。
- 這些是散落的說法。repo 裡只有「不做清單、輕量審」那句有守衛測試(`scripts/test_lumos.py:78874` 的 `t_design_loop_manuals_nogo_major_std`),「風險高只印不擋」沒有。漏改也不會紅,三個月後就是舊說法和現況並存。

2. 新流程接在手冊哪一步沒定義,而手冊現在的寫法是設計審一過就放行實作。
引句:「`commands/03-寫回圖譜.md` signoff 那列與 `reference.md`」
severity: major
blocking: 是 — 照 `lumos-design-loop` 手冊走完設計審的人,下一步被告知是「放行實作」,到推送才撞上 `high-red-missing`。
- 新流程是:設計審過 → 再跑一次規格閘拿先紅 → 寫預期值表 → `signoff --expected` → 推送。
- 設計審手冊的 description 寫「…就放行實作」(`skills/lumos-design-loop/SKILL.md:3`)。步驟 8 寫「✅ 過 → 出迴圈」(`:58`)。步驟 9 是凍結判定。步驟 10〈過了之後〉只講合約候選(`:60`)。
- 先紅模式要靠步驟 9 凍結出來的判定檔才會啟動,所以「再跑規格閘」應該落在步驟 9 之後。做法 5 只改「先判門」那段,那段讀在整個迴圈之前,不是迴圈結束的位置。
- `skills/lumos-code-loop/SKILL.md` 與其 `reference.md` 完全沒有 `spec-gate` 或 `signoff`。`signoff --expected` 排在 `code-loop pass` 之前還是之後,沒有任何一份文件講。這點要在手冊與計劃裡定下來。
- 在 `code-loop pass` 之後簽核,寫出的事件落在版控治理帳,看起來能跟著帳本提交送出(`scripts/lumos:53288` 附近的既有做法)。這一點是我的判斷,沒有實跑。

3. 預期值表的檢查擺在規格閘裡,卻又叫人「先跑規格閘拿先紅」,順序互相卡住。
引句:「規格閘在先紅模式跑完雙向靜態檢查之後做這道,任何一項不過就擋(rc1),逐項列出。」
severity: major
blocking: 是 — 擋下訊息(S6)指的那條路走不通。
- 做法 1 規定「全部過了才寫留痕」,所以 `red_first` 留痕要等表格檢查通過才會寫。
- 因此在設計審剛過、表還沒寫的時候,按 S6 擋下訊息的指示跑規格閘,會先被「沒有預期值表節」擋成 rc1,拿不到先紅留痕。
- 唯一走得通的順序是先寫表、再跑規格閘。這和說明這個新流程的順序(先紅、再寫表)相反。
- 計劃應該明寫順序,擋下訊息也要提示先寫表。不然兩個出口(S6 的指令、S8 的檢查)互相指向對方。
- file: `scripts/lumos:15258`(`_spec_gate_front`,靜態檢查在跑測試之前)

4. 「同一套雙向檢查」少借了一塊:風險低專屬的加嚴檢查(測試名不可重複、測試要真的存在),先紅模式會漏掉。
引句:「先紅模式下,`_spec_gate_front` 對風險高也算 keeps、跑 `_spec_gate_twoway_static`」
severity: major
blocking: 是 — d1 的理由是「風險低那套已處理過這些」,這一塊正好沒帶過來,有具體繞法。
- 風險低計劃的測試名互不相同、懸空測試擋,是靠 `_clause_check(door="low")` 裡的 `_clause_check_twoway`。計劃的借用清單(PRIOR-ART)沒有它。
  - file: `scripts/lumos:14788`(`if door == "low": tw = _clause_check_twoway(...)`)
  - file: `scripts/lumos:15275`(`_spec_gate_front` 只在 `door == "low"` 時跑 `_spec_gate_twoway_gate`)
- 先紅模式的門仍是 high。五條新行為條款全部綁同一支必紅的測試(例如 `[test:t_x]`),`_spec_gate_twoway_run_verdict` 逐條看同一個紅判定,五條都過。風險低會被擋,這裡不會。
- 計劃也沒說先紅模式該不該要求「回退節」。`_clause_check` 對 high 要求 ≥20 字回退節(`scripts/lumos:14792`),對 low 不要求,實作者得自己猜。
- 補法:在做法 1 明寫「先紅模式呼叫 `_clause_check` 時 door 傳什麼」,並加一支重複測試名的先紅案例。

5. 實作之後重跑規格閘會被誤擋,因為風險低的「已有放行留痕就不用重跑」只認風險低的留痕。
引句:「沒過交給 `_spec_gate_low_not_red` 印同一套補紅燈做法」
severity: major
blocking: 是 — 先紅模式的使用者在最常見的情況(實作做完、條款沒改)重跑,拿到 rc1 和「換回空殼」的繁瑣做法。
- `_spec_gate_low_not_red` 的 (a) 路徑在 `_rec_plan_risk(rec) == "low"` 且條款指紋相同時回 0、不寫新留痕(`scripts/lumos:15361-15373`)。
- 先紅模式的留痕 `plan_risk` 記 high。計劃沒有把 (a) 改成也認 `red_first`。於是實作做完、條款沒改的重跑,會走到 (b) 擋下。
- 設計審手冊同一頁還寫「實作後重跑時,已有條款沒變的放行留痕就不用重跑」(`skills/lumos-design-loop/SKILL.md:13`),和這個行為相反。
- 另一個誤擋:高風險計劃的代碼審常順手修條款字句。條款指紋一變,推送前判留痕過期、要求重跑。實作已綠、`done` 寬待又不適用,結果是每次只能再走一輪換回空殼。「誤擋」那條隱患只寫了「第一次跑就晚了」,沒寫這個重複來源。

6. 設計審判定檔的路徑用 `_loop_id_for_plan`(檔名去掉 `_計劃`),但實際的迴圈編號常不是這個字串,對不上就悄悄不進先紅模式。
引句:「governance/replay/<迴圈編號>/verdict.json」
severity: major
blocking: 是 — 失敗是靜默的:該被加嚴的風險高計劃被當成「沒有判定檔」,照舊只印不擋。
- 手冊規定迴圈編號是檔名「去 `_計劃` 轉 kebab」(`skills/lumos-design-loop/SKILL.md:14`)。程式的 `_loop_id_for_plan` 沒轉 kebab(`scripts/lumos:20000`)。
- 實例:
  - 計劃檔 `Projects/筆記標籤_過時判定與按需載入_計劃.md` 的審查帳迴圈編號是 `筆記標籤-過時判定與按需載入`,帳上有 18 列。
  - 判定檔在 `governance/replay/筆記標籤-過時判定與按需載入/verdict.json`。
  - 程式算出的編號是 `筆記標籤_過時判定與按需載入`,兩邊不等,找不到判定檔,也找不到首筆帳(回傳 None)。
- 全 repo 有 394 篇 Projects 筆記,其中 56 篇檔名中間含底線。
- 另有 15 個帶 `-r4`、`-std`、`-v2` 後綴的設計審迴圈。例如 `governance/replay/筆記測試綁定要存在-r4/`。計劃檔名導不出這些編號。
- 天花板四只提「改檔名」,沒提這兩類原本就對不上的情況。

7. 圖譜裡仍寫著「風險高照半套」的條款與綁定測試沒列入,「被改寫的舊決策與 RULE」也沒列全。
引句:「`Projects/業務簽核留痕_計劃` 加一句指過來」
severity: minor
blocking: 否 — 這些是線索層文字,不會推翻程式,但會讓下個 session 讀到互相矛盾的筆記。
- `Systems/規格閘.md` 第 39 行寫「風險高照半套:紅綠只印不擋…」,綁 `[test:t_spec_gate_oneway_keeps_halfset]`,做法 5 沒提。第 20 行(綁 `t_spec_gate_help_says_low_risk_blocks` 的 PITFALL)與第 62 行(「半套所有計劃照舊派審」)也沒提。
- `Projects/雙向門放行_計劃.md` 是「風險高照半套」的單一來源:第 45 行「風險高照半套」,S20 條款(第 263 行)「當門判為單向,規格閘應照半套只印紅綠不擋」。計劃的 related 與做法 5 都沒有它。
- 可補一句「設計審過且在生效時間之後的風險高計劃例外」。

8. 新欄位 `red_first` 沒加進推送前讀本機審查帳時的欄位白名單,會被濾掉。
引句:「`plan_risk` 照記 high,多一欄 `red_first: true`」
severity: minor
blocking: 否 — 計劃自己的 S5、S6 測試用真實流程跑,實作時會變紅,屬實作陷阱。
- `_spec_gate_ledger_index(env, _SPEC_GATE_PUSH_FIELDS)` 只保留名單內的欄位,`red_first` 不在其中(file: `scripts/lumos:15792`、`:15804`)。
- 合併讀時,`_spec_gate_pick` 在時間相同時選本機那筆(file: `scripts/lumos:15508`)。多數情況會讀到被剝掉欄位的本機版,`rec.get("red_first")` 為空。
- 結果是 S5 不走全套檢查,S6 誤報 `high-red-missing`。
- 計劃的「新增機制前的最小解自問」說新帳欄只有一個,沒寫要加這份白名單。

9. 「迴圈首筆帳不早於生效時間」只讀本機審查帳,而消費專案的這本帳預設被 git 忽略;沒有帳時的行為計劃沒定義。
引句:「迴圈首筆帳:審查帳裡這份計劃的迴圈編號最早一筆非結局帳的時間」
severity: minor
blocking: 否 — 現有程式有先例(沒有帳視同符合),但計劃沒寫,實作者可能選反。
- `_loop_first_ts_key` 只讀 `.canary-log.jsonl`,沒有帳回 None(file: `scripts/lumos:14975`)。
- 規格閘句式的現有先例是 `first is None or first >= SINCE` 視同符合(file: `scripts/lumos:14998`)。
- 在另一台機器或乾淨 clone 推送時沒有這本帳,先紅模式要不要開、要不要擋,計劃沒說。
- 計劃明明強調留痕要「兩本帳合併讀」,首筆帳卻沒有對應的版控帳來源。

10. 先紅計劃走 `_spec_gate_push_one` 時,會順帶要求「不做清單略過危險詞」的輕量設計審;⚠ 我沒實跑,判不準實際會不會擋。
引句:「之後同一支 `_spec_gate_push_one`:條款指紋過期要重跑」
severity: minor
blocking: 否 — 要求的審查是否成立取決於該計劃最後一輪審查有沒有綁到不做清單的快照,我沒實跑確認。
- `_spec_gate_push_one` 無條件呼叫 `_spec_gate_push_light(env, prel, now["nogo_skipped"], ctx)`,不看門是 high 還是 low(file: `scripts/lumos:16134-16140`)。
- 風險高計劃的「## 不做」節常出現金流、不可逆這類詞,`nogo_skipped` 就非空。
- 規格閘本身的 `needs_light_review` 只在 low 時成立,也就是先紅模式跑規格閘時不要求、推送時才要求。
- 要通過就得有綁到凍結快照、且被略過的行與現在相同的審查。審查完才改過不做清單的計劃會被擋。
- 計劃只說「全部照舊」,沒寫這一支。

11. pre-push 掛鉤那兩行是 bash 固定訊息,「改成照計劃講」做不到,新的擋下原因也會被誤標。
引句:「程式字串:`cmd_spec_gate` 的說明與印出的那行」
severity: minor
blocking: 否 — 只是訊息誤導,不影響放行判定。
- 掛鉤在 `spec-gate --push-check` 回傳 1 時,固定印「風險低計劃的條款測試沒全綠(或留痕過期)」,並記擋下理由同一句(file: `scripts/hooks/pre-push:581-582`)。
- 掛鉤只拿得到回傳碼。`expected-unsigned`、`high-red-missing` 這兩種擋下也是回傳 1,會被標成「風險低計劃的條款測試沒全綠」。
- 計劃要不就寫中性措辭,要不就定義讓掛鉤讀 lumos 輸出的做法。

12. 治理帳統計的「去重鍵含 token」並不成立,而且 `gov --stats` 目前沒有「signoff 段」。
引句:「(gov 統計的去重鍵含 token,同一個提交簽兩次不會被折成一筆)」
severity: minor
blocking: 否 — 影響人簽、AI 簽的次數統計,不影響放行。
- `_gov_row` 只對特定閘輸出 `token`:`fix-check` 等;其他閘 `token` 是空字串(file: `scripts/lumos:16987-17000`、`:17056-17061`)。
- 去重鍵 `(commit, nodes, gate, kind, token, check)` 對 `signoff/expected-signed` 的 token 是空,同一個提交的兩筆會被折成一筆。
- 計劃只說 `_gov_row` 要把 `by` 帶出來,沒說要把 signoff 閘的 token 一起帶出來。先例見 `Systems/reversibility-governance-ledger.md` 的 fix-check 那條 WHY。
- `gov --stats` 的現有版面是按閘分列,沒有可以「分開印 human 與 ai」的 signoff 段(file: `scripts/lumos` 的 `_render_gov_stats`),要新增。

13. 「簽的人」的來源描述不準。
引句:「簽的人(環境變數 USER,同端到端驗收放行)」
severity: minor
blocking: 否 — 不影響放行,只影響事件欄位內容。
- 端到端驗收放行用的 `_e2e_who` 先讀 `git config user.name`,沒有才用 `getpass.getuser()`;AI 簽時直接寫 "ai"(file: `scripts/lumos:43283`、`:43520`)。
- 計劃寫的是環境變數 USER。

14. 第二批第 7 點自己舉的例子,用它指定的做法(型別名字尾認)認不出來。
引句:「照 [[Systems/test-guard]] 已有的做法」
severity: minor
blocking: 否 — 第二批只定方向,但寫著「照這些設計」,接手的人會照字面做。
- test-guard 的字尾規則是「…Error、…Failure、Throwable」(file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:35`)。
- 同一條 bullet 舉的漏網例子 Mockito `WantedButNotInvoked`,字尾是 `Invoked`,不是 Error 或 Failure,字尾規則抓不到。r1 邊界席和正確性席都列過這個類名(`r1-正確性-sonnet.md:41`、`r1-邊界-sonnet.md:69`)。
- 需要補:Mockito 的 verify 例外怎麼認。

15. 第二批第 7 點沒有完整反映 r1 卷證已抓到的坑。
引句:「設計審 r1 已抓到的坑,第二批照這些設計」
severity: minor
blocking: 否 — 第二批另開計劃,但這裡自稱「已抓到的坑」,漏的會在實作時重新被發現一次。
- 缺單檔大小上限(file: `r1-邊界-sonnet.md:244-248`,`_SECEV_FILE_MAX` 16MB 的先例)。
- 缺走目錄要排除 `node_modules`、`.git`、`Pods` 這類目錄。
- 缺「手機上跑的測試報告沒有失敗型別」的處理(file: `r1-intake.md` 的 p3,多掃 `build/outputs/androidTest-results/`)。
- 缺找不到報告判弱證據和走目錄逾時判「未判」方向不一致的取捨(file: `r1-整合-sonnet.md` 第 14 條)。
- 第 7 點第 4 個 bullet 只寫了「逾時不算紅」,和上述走目錄逾時不是同一件事。

16. RETIRE-IF 的第二個條件在現行工具裡量不出來。
引句:「而且同期逃逸帳裡沒有一筆是」
severity: minor
blocking: 否 — 撤除條件變成純人讀,不會有機器去數。
- 後面接的是「測試預期值抄實作」或「測試沒在驗」這兩類。`lumos loop escape` 沒有類別欄位,只有自由字串 `--desc`、選填 `--rule`、`--stage`(file: `scripts/lumos:72720-72735`)。
- 計劃要不要規定用 `--rule` 記成固定 id 沒說。

17. 本計劃改了 pre-push 掛鉤字串和注入範本,卻沒決定是否升版,而 repo 有「改掛鉤或範本就升版」的前例。
引句:「程式字串:`cmd_spec_gate` 的說明與印出的那行」
severity: minor
blocking: 否 — 沒升版只是少了「叫還沒更新的專案跑 `lumos update`」的提示。
- file: `CHANGELOG.md` 的 v1.3、v1.4:紀律範本或掛鉤變了就升版,讓舊專案被提示 `lumos update`。
- 未更新的消費專案 `CLAUDE.md` 紀律區塊仍寫「風險高再進審查」,AI 照它做,到推送被 `high-red-missing` 擋下。
- 計劃沒寫升版與否,也沒寫 CHANGELOG 要不要列。

18. S2 要求的那句提示,會對永遠不進先紅模式的計劃也印出來。
引句:「規格閘應照舊紅綠只印不擋,並印一句設計審過了之後要再跑一次拿先紅」
severity: minor
blocking: 否 — 只是白費一次重跑。
- S2 涵蓋「迴圈首筆帳早於生效時間」的計劃。這類計劃的設計審做完也不會進先紅模式(〈不做〉:不回頭套用)。
- 提示卻叫它設計審過了再跑一次,跑了仍是只印不擋。需要把提示限定在「還有機會進先紅模式」的情形。

19. 效能隱患那句宣稱「同一趟讀」,但現有的讀法讀不到簽核事件。
引句:「跟現有的留痕索引同一趟讀(`_spec_gate_gov_index`),不另外整本再讀」
severity: minor
blocking: 否 — 多讀一次治理帳(r1 量到約 20MB),不是正確性問題。
- `_spec_gate_gov_index` 只取 `gate=="spec-gate"`、`kind=="spec-gate-record"`(file: `scripts/lumos:15492-15505`)。
- `expected-signed` 的閘是 `signoff`。要同趟讀,必須把 `_gov_vc_gate_events` 改成傳閘名 tuple(它支援,file: `scripts/lumos` 的 `_gov_vc_gate_events` docstring)並重寫索引的回傳形狀。
- 計劃沒寫要改這個索引。

20. `signoff --expected` 與既有 `--by` 參數同名不同意,答 n 的回傳碼未定義。
引句:「帶計劃、迴圈編號、表指紋、列數、`by`(human 或 ai)」
severity: minor
blocking: 否 — 實作者要自己猜,猜錯影響小。
- 既有 `signoff` 的 `--by` 是「誰確認的」自由字串,寫進 `rec["by"]`(file: `scripts/lumos:72901`、`:16550`)。
- 新事件的 `by` 是 human 或 ai,兩個同名欄位意思不同。`--expected --by 小明` 怎麼處理沒說。
- S10 寫答 n「印沒簽而且不寫」,沒寫回傳碼(S11 只定義了表格檢查不過和寫不進帳是 rc2)。

---

## 各節狀態

- 名詞:有 F6、F9;其餘已讀,無 finding。
- 問題與最小解:已讀。數字 r1 已重算過,無 finding。
- 調研結論:已讀,無 finding。
- 做法第一批:見 F3、F4、F5、F8、F10、F11、F12、F13、F19、F20。
- 做法第 5 點(跟著改的說法):見 F1、F2、F7、F17。
- 做法第 6 點(會紅的既有測試):`t_spec_gate_help_says_low_risk_blocks` 對得上。`t_spec_gate_oneway_keeps_halfset`(`scripts/test_lumos.py:76630`)在沒有判定檔的情況下仍綠,不會紅。doctor「半套」字串對得上第 3515 行,該段沒有字串釘測試。未發現漏列的會紅測試。
- 第二批:見 F14、F15。
- 不做:已讀,無 finding。
- 驗收條款:S2 見 F18;S3 見 F4;S5、S6 見 F8;S10 見 F20;其他已讀無 finding。
- 回退:已讀。回退後 `red_first` 留痕被重跑會被覆蓋成沒有 `red_first`(計劃已寫明),無 finding。
- 實務隱患:效能見 F19,誤擋見 F5,其餘見下方逐類。
- 審計修正紀錄:r1 的 68 條、41 blocking 數字與卷證 `r1-intake.md` 對得上。已讀,無 finding。
- d1–d5 與正文一致性:d1、d3、d4、d5 與正文一致。d2 與「不做」一致。d5 的裸編號與 S9 一致。

## 圖譜鏡頭(派工附上的固定席節點,逐條判)

- Systems/test-guard:不影響第一批。第二批借它的字尾做法,見 F14。第一批不改它的比對函式。
- Systems/test-quality-evidence:不影響。第一批沒碰它的證據欄位。
- Systems/guard-kill(兩條 ★INVARIANT★:rc 優先序、`--json` 輸出純度):不影響。第一批不碰 `guard kill`。第二批第 9 點對「不自動產生變異」的說明和 guard-kill 的 KEY(「繞開等價變異不可判定」)方向一致。
- Systems/test-quality-cli:不影響。第一批不碰 `scripts/test_quality.py`,部署指紋 `_TEST_QUALITY_BUNDLE_DIGESTS` 不受影響。
- Systems/lumos-cli-lifecycle(★INVARIANT★ re-inject 只覆蓋 sentinel 之間,sentinel 外 byte-equal 保留):不破壞。改注入範本只動 sentinel 之間的內容。副作用是未更新專案會停在舊文字,見 F17。
- Verification/測試品質第四輪修補驗證:不影響。

## 實務隱患逐類

- **併發**:新增的 `expected-signed`、擋下事件都是治理帳追加寫入,寫法同現有 `_gate_event`,沒有新鎖需求。留痕兩本帳合併讀的「同秒本機勝」是既有行為,但會導致 F8 的問題。其他無新增風險。
- **效能**:先紅模式只多讀一個小 JSON 判定檔,沒問題。簽核事件的讀法見 F19。表格解析是對單一小節的線性掃描,沒有放大風險。
- **資源**:治理帳每次擋下推送都追加一筆,和現有閘的增長方式相同。大型輸入未見新的放大點。
- **回滾**:`_HIGH_RED_SINCE` 設遠未來可回退,計劃已寫明已寫的 `red_first` 留痕仍被當風險低查,且新 kind 事件留在帳上無害。回退時重跑規格閘會覆蓋掉 `red_first`,計劃已承認。無新增 finding。
- **資安**:簽核事件的 `by` 是自報、`ai` 可代簽,屬 d3 明文的設計取捨,不算 finding。

最嚴重 severity 為 major,blocking 共 6 條(F1–F6)。
