severity: major

審稿立場:假設三個月後有人照這份做。派工尾端沒有附上任何合約或事故節點(只在材料清單裡看到 `Systems/規格閘`、`Systems/test-guard` 與兩份相關計劃),所以固定席的逐條判沒有對象可判。我改為自查這兩篇 Systems 的 WHY 與 `_TG_LIMITS`(見 F8、F10)。

## 逐節結果

- 名詞:已讀。「祖先」「分岔點」「head_sha」「撞名」的定義與程式一致。我用真 git 重現了 rc 碼:不存在的提交回 128;壓掉但物件還在的提交回 1;`rev-parse --is-shallow-repository` 回 false;`--verify -q` 對不存在的提交回 1。這些都與 spec 的假設吻合,無 finding。
- 問題與最小解:有 F1、F2、F3。
- 做法 1:有 F1、F2、F3、F9。
- 做法 2:有 F6。
- 做法 3:有 F4、F7、F8、F10。
- 做法 4:有 F5。
- 驗收條款:有 F4、F9。S5 的實際輸出字樣已核對:`★已撤回(原因;誰,日期)★` 與標頭 `其中 N 筆已撤回(統計不算)` 都在 `scripts/lumos:20100` 與 `20114`,無 finding。
- 回退:有 F5。
- 實務隱患:有 F1、F2、F3、F5。
- 交叉引用核對:`[[Projects/紅燈版實跑三缺口_計劃]]`、`[[Projects/規格閘紅燈測試快照_計劃]]`、`_redbase_branch_rows`、`_lens_git_dl`、`_push_rev`、`_LENS_SHA_RE`、`_name_collision_reason`、`_TitleIndex`、`_raw_test_titles`、`_TG_CONST_PAT`、`_TG_LIT_PAT`、`_tg_ident` 都存在。測試 `t_name_collision_scales` 與 `t_tq_guard_string_comma_args` 存在。`t_spec_gate_redbase_green_other_branch` 是新測試,尚未存在,符合預期。

## Findings

1. 祖先過濾對「治理帳進版控」的專案是純退步,而這個修法原本只需要管「被忽略」的專案
severity: major
blocking: 是——實作者會把一道原本正確的守衛,為了只在被忽略專案才有的 bug,在所有專案上放鬆。
引句:「讀這條分支的紀錄時,只留帶的 head_sha 是目前 HEAD 祖先(或就是 HEAD)的」
重現:治理帳進版控時,工作目錄的帳本來就隨分支切換,「減掉分岔點那一版」已經正確隔離別條分支。現在在這條路上再疊祖先過濾。
- 輸入:分支上先有判綠紀錄(head_sha=W1),之後 `git rebase origin/main` 或做規定的壓提交(全域 CLAUDE.md 要求推送前壓成一個)。
- 壞在哪:W1 不再是 HEAD 祖先,這條分支自己的判綠紀錄與上一份紅燈版去重全被丟掉。
- 後果:被忽略專案才需要的過濾,被套到所有專案;天花板一(壓/rebase 後保護變鬆)因此也擴散到沒有 bug 的專案。
- RETIRE-IF 自己也承認「治理帳進版控時過濾多餘」,但設計沒有把過濾限縮在被忽略的情況。
- 既有 `_gov_ledger_ignored` 已能判斷帳是否被忽略,spec 沒考慮只在 `ignored`/`unknown` 時才過濾。
file: `scripts/lumos:14380`——`_gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, ...)` 在帳進版控時已經只取本分支新增的列。
file: `scripts/lumos:1775`——`_gov_ledger_ignored` 已存在。

2. 天花板二用的是工具自己印出來的標準流程,不是罕見情況;且已有欄位能做更穩的分流,spec 沒比較
severity: major
blocking: 是——spec 宣稱修掉「判綠紀錄限本分支」,但標題 bug 的重做情境仍會重現。
引句:「判綠時實作還沒提交、之後從同一個 HEAD 開新分支重來,那筆判綠紀錄的 head_sha 仍是新分支的祖先」
重現:
- 主流程:`_redbase_note_green` 在 `cmd_spec_gate` 判完當下就寫,中間沒有提交步驟。`_spec_gate_low_not_red` 還專門印「工作目錄有還沒提交的改動」的警告,所以「實作未提交時判綠」是預期狀態,不是例外。此時 head_sha 是實作前的 HEAD(例如主線 M)。
- 輸入:分支 A 在 M 上實作(未提交),跑規格閘,記判綠(head_sha=M);放棄 A,`git switch -c B main`。
- 結果:M 是 B 的祖先,判綠留下,B 的紅燈版又被擋。這正是標題要修的「新分支一個紅燈版都存不到、不出聲」。
- 同類:A 以 fast-forward 或 merge commit 併回主線(非 squash)後,A 的 head_sha 成為主線祖先,之後任何分支都留下它。
- 較穩的做法:`_gate_event` 已有 `ref` 參數。判綠與留痕多記分支名,過濾時「祖先成立,且有記分支名時必須同名」。這樣壓、rebase 都不影響(F1 的問題消失),同 HEAD 重做也擋得住。
- PRIOR-ART 只引了 `--is-ancestor` 的文件,沒有評估這條。
file: `scripts/lumos:15259`——判綠在判完後立即寫。
file: `scripts/lumos:15224`——擋下訊息本身處理「有未提交改動」的情況,可見未提交是常態。

3. 200 個上限與 10 秒截止時間的母體估計錯了,且過濾會在最需要的專案悄悄失效
severity: major
blocking: 是——設計用「不到十筆」定出的上限,會讓這個修法在目標專案(帳被忽略、累積多月)失效。
引句:「一條分支的判綠紀錄通常不到十筆」
重現:`_redbase_branch_rows(rr)` 不帶迴圈編號。帳被忽略時,它收到的是工作目錄裡所有分支、所有迴圈的 `spec-gate-record` 與 `spec-gate-green`(這正是 bug 的成因)。
- mOrangePos 2026-06 起被忽略。每次規格閘留痕都會在 `docs/.governance-log.jsonl` 加一筆帶新 head_sha 的列。累積幾個月後,不同 head_sha 超過 200 個是自然結果。
- 超過就「整批照舊留」,等於過濾關掉,只多印一句。bug 在最需要修的專案重現,而且沒有條款或測試會發現。
- 修法:改成在去重前先按 `rec["loop"]` 縮小母體。`_redbase_attach` 呼叫端已有 `rec["loop"]`。
- 連帶影響:`_redbase_branch_rows` 簽名要改。既有測試呼叫它時只傳一個參數,見 F9 引用的 `scripts/test_lumos.py:123782`。
file: `scripts/lumos:14511`——呼叫端已有 `rec["loop"]` 可傳入。
file: `scripts/lumos:14403`——`_redbase_branch_state` 才按 loop 過濾,已經在整批 git 查詢之後。

4. S4 綁定的既有測試沒有涵蓋條款情境,實作前就是綠的;做法 3 也沒說要補
severity: major
blocking: 是——條款沒有紅綠證據,實作者忘記補案例也會過關,守衛改壞也抓不到。
引句:「比對工具應列 tq/assert-weakened [test:t_tq_guard_string_comma_args]」
重現:`t_tq_guard_string_comma_args` 現在只有「三引號字串裡的 assertEquals 字樣不算強斷言」的 assert-weakened 案例,沒有兩邊都是三引號常值的案例。
- 我載入 `scripts/lumos` 驗證:`_tg_const_stmt('assertEquals("""a""", """a""")')` 現在回 False。這個案例今天不會列 assert-weakened,所以補上案例後測試才會紅;但做法 3 沒寫要補這個案例。
- 該測試的 docstring 掛的是另一份計劃的 S1;追加案例時要同步改它的說明。
file: `scripts/test_lumos.py:121342`——函式本體;`scripts/test_lumos.py:121402` 附近的 assert-weakened 檢查沒有常值案例。
file: `scripts/lumos:49197`——只有 `all(... fullmatch(a) for a in sp[2])` 這條路會讓三引號常值進 assert-weakened,而它目前用單行樣式。

5. 做法 4 的「只動考場本機分支」與回退說法都不成立
severity: major
blocking: 是——實作者會以為做完可以安全 git 還原,實際上全域設定與別的工作樹已被改。
引句:「也不碰 mOrangePos 主目錄(那裡有別人的改動)」
引句:「第 4 項考場分支 git 還原 lumos 那幾支檔」
重現:`cmd_update` → `_vendor_toolchain` 除了複製 vendored 檔,還會:
- `git pull` Lumos 來源 repo(`_pull_source_or_abort`)。
- `git config core.hooksPath scripts/hooks`(`_set_hooks_path`)。git config 是整個 repo 共用,考場工作樹與 mOrangePos 主目錄看到同一份。
- `_sync_global_from_project` 覆蓋全域 `~/.claude/hooks` 與設定,claude 與 codex 兩邊都動。
- `_reinject_all` 重寫 CLAUDE.md 紀律區塊與 Codex 指示檔。
- `_init_additive_setup` 補設定骨架。
回退只還原「lumos 那幾支檔」,全域 hooks 與設定、hooksPath、CLAUDE.md 區塊、來源 repo 的 pull 都不會回來。全域 hooks 是整台機器所有會談共用的。
file: `scripts/lumos:32798`——`_scaffold_project`、`_init_additive_setup`、`_set_hooks_path`、`_reinject_all`、`_sync_global_from_project` 連續呼叫。
file: `scripts/lumos:34020`——`_sync_global_from_project` 的說明明寫會覆蓋全域 hooks。
file: `scripts/lumos:32523`——`_pull_source_or_abort`。

6. 效能測試的篩選設定位置寫得含糊,放錯位置會空轉
severity: minor
blocking: 否——放錯會讓 S3 的「建 1 次」斷言變成 0 次而自己紅,實作者一定會發現,只是要試一次。
引句:「pentry 給 `name_filter: regex_tail`(給 `ident` 會直接回 None、不建索引,測試空轉)」
重現:`_name_collision_reason` 讀的是 `pentry["profile"]["name_filter"]`,鍵(快取 key)用 `pentry["profile_name"]`,不是 `pentry` 頂層。既有測試的寫法是 `{"profile": dict(m.TEST_PROFILES[prof]), "root": root, "profile_name": prof}`。
file: `scripts/lumos:68855`——`_name_collision_reason` 取 `prof` 與 `nf` 的方式。

7. 做法 3 描述三處 fullmatch 的用途與程式不符
severity: minor
blocking: 否——只是描述錯,不影響要改的正規式。
引句:「`_TG_CONST_PAT` 有三處 fullmatch(判預期值是常值、判實際值是常值、判兩邊都常值)」
實際三處:
- `assertThat` 單參數鏈。
- `assertTrue`/`assertFalse` 的條件。
- 實際值清單 `all(...)`。
沒有一處判「預期值是常值」。
file: `scripts/lumos:49191` 與 `scripts/lumos:49195`、`scripts/lumos:49197`。

8. 放寬 `_TG_CONST_PAT` 會讓含三引號常值的既有候選指紋改變,已放行的會復活;設計沒提
severity: minor
blocking: 否——只影響含三引號常值斷言、且之前被 lint-waive 放行過的函式,少見。
重現:assert-weakened 的指紋字串含 `{co}->{cn}` 常值斷言數。
- 某消費專案的測試含 `assertEquals("""a""", """a""")`,且該函式的 assert-weakened 已被 `lumos lint-waive` 放行。
- 改版後常值數變了,指紋變了,舊放行失效,推送重新被擋。
- 實務隱患只寫了「走設計審與代碼審」,沒有講這一點。
file: `scripts/lumos:49759`——assert-weakened 指紋組字串。

9. 「判綠過、不存」的幾條既有說法會變假,但沒列進要改的地方;S1/S2/S6 之外的三條「照舊留」路徑與留痕過濾也沒有條款
severity: minor
blocking: 否——不影響實作正確性,但三個月後讀到會跟程式不符。
引句:「壓掉的提交上的判綠紀錄不再算數(head_sha 不再是祖先)」
- `_TG_LIMITS` 的「判綠過的、逾時紅的不存」與 `test-quality-standard.md` 同一份「抓不到」清單,壓或 rebase 後不成立。該清單由 `t_tq_guard_cli_contract` 釘,需要同步改。
- `Projects/規格閘紅燈測試快照_計劃.md` 第 61 行「只有直接在 main/master…才看整本帳」、第 62 行「判綠觀測只讀…只看這條分支自己寫的那幾筆(跟分岔點那一版做行差)」、第 78 行「判綠過的…不存」,本計劃改了機制卻沒列。
- `Systems/規格閘.md` 的 WHY(`t_spec_gate_redbase_skips_after_green`)在 `lands_in` 裡,但做法沒有任何一步要寫回它。
- 另外,「不會漏比」這句沒有證據:壓過提交後第一次判紅若是實作後版本,存下的就是實作後版本。
- 條款:S1/S2/S6 只涵蓋判綠與祖先判斷。淺複製照舊留、截止時間、超過 200 個、git 叫不起來這四條「照舊留」路徑,以及「別條分支的上一份紅燈版不再去重」都沒有條款。
file: `scripts/lumos:50148`——`_TG_LIMITS` 該條。
file: `skills/lumos-project-notes/commands/test-quality-standard.md:39`——同一份清單。
file: `scripts/test_lumos.py:123782`——既有測試以單參數呼叫 `_redbase_branch_rows`。

10. 「已知漏判」那一行標 `[closed:]` 沒有作用,且正文仍寫著將變假的現況
severity: minor
blocking: 否——只是舊筆記留下錯的現況描述。
引句:「做法 1 那行「已知漏判」與它的 REVISIT 標成已處理」
`[closed:…]` 只被 REVISIT 行的檢查認得。「已知漏判」那段是普通段落,仍寫著 `assertEquals("""a""", """a""")` 不會被當成常值,補完後即為假。`Projects/紅燈版實跑三缺口_計劃.md` 第 61 行「5 處一起生效」也會變成不準。
file: `scripts/lumos:54151`——`_REVISIT_CLOSED_RE` 只用於 REVISIT 行。
file: `docs/lumos-toolchain-knowledge/Projects/紅燈版實跑三缺口_計劃.md:64`——已知漏判段落。

## 實務隱患逐類

- 金流:無。只改本機判讀與測試,同意 spec 的排除。
- 對外送出:有。spec 寫「只多叫本機 git」,但做法 4 的 `lumos update` 會 `git pull` 來源 repo 並覆蓋全域 hooks(見 F5)。
- 不可逆:有疑慮。做法 1~3 可逆,做法 4 的全域 hooks 與 git config 不在回退範圍(F5)。
- 回滾:做法 1~3 可逆,做法 4 不完整(F5)。拿掉祖先過濾後,已寫入的帶 head_sha 列無害,這點成立。
- 與推送前比對(`_tg_redbase_records`)互動:推送端讀版本控帳 base..head 的行差,不過濾 head_sha;寫入端改成按祖先過濾。兩端對「這條分支的列」判法不同。壓提交後寫入端少去重,會多存一份內容相同的紅燈版,推送端鏈式比對遇到相同本體不產生候選,無害。但分支選擇性的退步仍在(F1、F2)。
- 與 test-guard 互動:放寬常值樣式改變 assert-weakened 指紋(F8)。

最嚴重為 major;blocking 共 5 條(F1、F2、F3、F4、F5)。
