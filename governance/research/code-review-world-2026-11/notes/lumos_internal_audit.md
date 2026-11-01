# Lumos 代碼審查迴圈內部稽核(程式現況、帳本數字、已試與已否決)

標記法:**[程式]** 親讀原始碼確認;**[帳]** 用腳本機械數帳本;**[筆記]** 來自圖譜或手冊、未獨立驗證。「來源」用檔名與函式名,不用行號。

資料切點:工作樹 `bce8e2a05`(2026-10-31 02:53)。審查帳最後一筆 2026-10-31T00:39。除非另註,審查帳數字的**共同篩選**是:`docs/.canary-log.jsonl` 裡 `kind` 為 none/caught/missed、無 `outcome` 欄、`loop` 以 `code-` 開頭,共 **2,986 筆席次、324 個迴圈編號、813 輪**,日期 2026-07 到 2026-10-31。

全部計數腳本在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/b91acebb-68a9-4c16-b1e8-244dfdec16fe/scratchpad/lumos-audit`(stats1.py、stats2.py、stats3.py、esc.py、cost.py、sev.py、reg.py、s4.py、s5.py、s6.py)。

**全篇通用的讀數警告(寫報告時必須帶著):**
- 迴圈編號不等於獨立任務。`-v2`、`-記帳更正`、`-rebook` 是同一件事重記 [筆記:`Projects/審查回顧轉可比較eval_計劃`]。
- `findings_set` 的 id 未必去重:`code-Android目標架構產生器/r2-intake.md` 裡 F1 與 F13 是同一件事、兩席獨立報,卻佔兩個 id [帳]。下文 F 是「條目數」,不是「相異缺陷數」。
- 折入不等於正確。沒有任何欄位記「這條是不是真問題」[筆記:`Projects/審查評測集_計劃`]。

---

## 一、已實作的機制(程式驗證)

### Takeaway
Lumos 是「帳本與閘」,不是審查引擎:工具不派任何代理,派席、辯方、判讀都是編排者照手冊做,工具只驗帳面自洽與雜湊。推送時機械擋的只有兩件事跟審查有關:high 必須有 `pass|skip` 留痕,而且留痕綁版本。`pass` 本身不驗審查做過沒有,standard 與 light 的審查在推送時完全不查。

### Cited Findings

**分級**
- [程式] `scripts/lumos::_pitfall_tier` 的順序:①殘留索引與問答帳有異動(`_residual_tier_hits`:新增或拿掉殘留、合約改字、改到殘留守的檔或存著殘留決策的筆記、索引讀不出等)→ high;②`claims` 非空 → high;③改動裡沒有程式檔(`_is_code_file`,簿記檔除外)→ light;④其餘 standard。
- [程式] `claims` 來自 `_pitfall_diff_collect`,逐新增行比 `_PITFALL_DIFF_PATTERNS` 七條正規式:`requests./httpx.`、`open(`、SELECT…FROM、`time.sleep(`、`threading./Lock(/global`、INSERT/UPDATE/DELETE。只看新增行,跳過測試檔與 `_PITFALL_DIFF_SKIP_EXT`(.md、.json、.jsonl、.csv、.log、.lock、.svg、.html、.patch、.diff 等)、註解行,字串字面先挖空(SQL 除外)。**任一行命中就是 high**,沒有累積分數,也不看行數、檔案類型、歷史。
- [程式] lint 那隻手:`_pitfall_diff_collect` 不帶 `--no-lint` 時併入 lint 發現;座標對不齊時,推送閘接得住的 lint 發現不參與分級。擋推鏈(`_codeloop_pitfalls_tier`、pre-push)一律帶 `--no-lint`,所以**實際擋人的分級只有正規式與殘留帳**,「新增告警」是另一道獨立閘(`_codeloop_lint_new_step`,不看 tier)。
- [程式] 「計劃風險低、全靠人驗、小改動閘過 → light」不在 pitfalls(它不載圖譜),由 `spec-gate --push-check` 判,pre-push 另外要 pitfalls 的 `light_ok`。
- [程式] 分級有兩處、彼此不綁:推送時算的 tier,與迴圈帳第一筆宣告的 tier(`cmd_loop_next` 註明「分級由編排者第一筆記錄時宣告、之後定死;工具只照分級查表,不自己判斷」)。編排者把 high 的改動開成 standard 迴圈,資安席那道閘就不會要求。手冊把這點寫成既有天花板。

**席次與鏡頭**
- [程式] 單一來源 `_TIER_ROSTER`(`("code", tier)`)與 `_TIER_PARAMS`(`light (1,2)`、`standard (3,3)`、`high (5,3)`、`legacy (1,6)`,即寬度與輪數上限)。`cmd_loop_next` 寬度以名冊「佔人數的必派席」為準,所以 standard 實際是 1 而不是 `_TIER_PARAMS` 的 3。
- [程式] 名冊:light=架構對齊 1 席。standard=單reviewer 1 席+架構對齊(不佔人數)+外家否決(條件席)。high=鏡頭1–5 五席+架構對齊(必派)+資安(`required-gated`,唯一會擋)+外家 finder、外家否決、spec-conformance(條件席)。
- [筆記:SKILL、templates.md §7] 鏡頭名是慣例不是資料:正確性、併發與資源(工具鏈本 repo 改「資源」)、邊界、合約與圖譜一致、鏡頭5 通才。席名 `<鏡頭>-<模型>`。工具只認 `資安` 這個片段(`_auditor_matches_slot`)。預設模型 sonnet,空泛或引句大面積錨不到才升 opus。
- [筆記:templates.md §7.9,`Projects/原生代碼審當通才席_計劃`] 鏡頭5 用 Claude Code `/code-review` 八角度審法(逐行、被刪掉的行為、跨檔追蹤、重用、簡化、效率、修的深度、慣例),每角度最多 6 候選,最多報 10 條,跑在 Lumos 子代理裡。
- [程式] 派工鏡頭注入:`scripts/hooks/claude/dispatch-lens-hook.py` 依派工詞裡的 `LUMOS-IMPACT:` 標記附 `lumos impact --diff` 的固定席;`cmd_dispatch_lens` 是本體。

**辯方**
- [程式] 程式裡**沒有辯方階段**。只有記帳欄:`--refuted-set`(載體席必帶,缺了 rc2)與選填 `--refute-verdict`。`refuted_set` 語意是「編排者機械重現不到、沒折也沒放行」,id 要在 intake 重現表同列整字出現並帶 HIT/MISS(`cmd_canary`)。
- [筆記:templates.md §2、§4] 路由制:機械證實或多席一致者免辯方直接折入,只有低共識的 ≥major 才開庭,一條派一個 opus,乾淨脈絡,須附 file:line 才能降。辯方只買 code 層假陽性。

**證據閘(處置閘)**
- [程式] `_loop_status_disposal`,九步合取,全部讀側重算:①G3 雜湊鏈 ②處置集合(`folded ∪ accepted == findings`、無交集、放行理由齊;輪內有 blocker 時 accepted 必空;代碼審輪內有 major 且無 `finding_sources` 時 accepted 必空)③判定輪全席 report/snapshot 雜湊重驗,含全輪 intake ④引句錨定(載體報告對凍結快照;零引句判失敗)⑤條款綁定(代碼審略過)⑥資安席 ⑦落點(代碼審略過)⑧跑滿回顧 ⑨逐條放行(`_disposal_minor_release_step`)。
- [程式] 閘**只看最後一輪**(`rid, latest = next(reversed(groups.items()))`),判的是「這輪每條都有去向」。全折即過,不要求零發現,也不要求折入的修補被驗過。零發現輪走 vacuous 分支,仍驗留痕。
- [程式] 寫側硬擋:`cmd_canary` 拒收未正規化報告、`reported` 由機器從報告數、`--findings` 不得多於它、帳面 severity 不得低於報告最高。
- [程式] 席位報告的 severity 對帳(`_severity_tail`)與席位對帳(`_roster_tail`)都是觀測,不進合取。

**留痕與版本綁定**
- [程式] `cmd_code_loop` 的 `pass|skip` 分支只做兩件事:`_codeloop_write`、`_codeloop_gov_log`,記 status、note、HEAD sha。**不查處置閘、不查迴圈存在、不查 sync-check**。
- [程式] `_codeloop_guard_verdict` 第 4 步:留痕 sha 等於被推版本,或留痕是祖先且之後只動簿記檔(`_codeloop_record_valid`,`_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS`)才有效。壓提交或 rebase 後失效。合併提交另有「認合進來那一側」路徑(`_codeloop_merge_side_pass`)。
- [程式] 留痕有兩個來源:`governance/code-loop/` 下的 marker(被 gitignore)與版控的治理帳 `docs/.governance-log.jsonl`(`_codeloop_read_from_ledger`),CI 用後者。

**推送與 CI**
- [程式] `scripts/hooks/pre-push` 與 `.github/workflows/ci.yml` 的 code-loop gate 都呼叫 `code-loop check`。判定順序:安全證據 → Android e2e → 受波及合約測試 → 取 tier → 表態 → 新增告警 → `if tier != "high": 放行` → 留痕。pre-push 帶 `--keep-going` 全跑完再列。
- [程式] **standard 與 light 的審查留痕推送時不查**(`if tier != "high"` 那一行)。那兩級的迴圈是手冊紀律。
- [程式] fail-open 路徑:`_gate_failopen` 共 10 處呼叫,含 pitfalls 失敗、算不出 merge-base、取不到 HEAD、表態超預算且未查出問題。pitfalls 失敗時 tier=unknown,不擋。
- [程式] pre-push 跑 `impact --sync-check` 取 JSON 供後續用,不是 `pass` 的前置條件。手冊第 8 步寫「強制,不可跳」指的是手冊層(見第六節)。
- [帳] `code-loop` 事件(`docs/.governance-log.jsonl` 全帳):passed 595(相異 sha 567、110 分支,07-05 起)、skipped 46(7月7、8月19、9月9、10月11)、blocked 272(09-08 起)、dispositions 282。blocked 主因是新增告警,其次是表態不完整與留痕過時。

**修正關卡(fix-check)**
- [程式] `cmd_loop_fix_check`:驗修正紀錄完整、測試存在、紀錄裡的測試修正後是綠的、受波及合約測試全綠。只對 `code-` 迴圈,`LUMOS_SKIP_FIX_CHECK` 可跳且留帳。**只驗修正後綠,不驗修之前紅**。`loop next` 只提醒,不擋;pre-push 與 CI 都不跑它。
- [帳] 2026-10-02 起 308 次(passed 221、warned 87),76 個迴圈。同期有折入的 337 輪裡 212 輪有 fix-check 紀錄(62.9%)。

**修補後的全新席**
- [筆記:SKILL 第 5 步] 「修完可續談發現那條的席驗收,但收斂前仍派全新席掃 delta 回歸」。修訂輪凍結材料仍是整條分支 diff,另附修補差異鏡頭(templates.md §3.1,`rN-repair.patch`、`rN-repair-binding.json`)。
- [程式] 處置閘與 `pass` 都不檢查這件事(見第二節 Gaps 與第五節)。
- [帳] 2026-10-01 起開的 141 個迴圈,**79 個最後一輪仍有折入**,那些修補沒有之後記帳的審查輪。全帳口徑是 197/307(獨立覆核數的,含可能沒通過的迴圈)。
- [程式] G3 只對最後一輪跑 `_hash_chain_check`,允許 reviewed 與 result 不同;result 的雜湊在記帳時算,也就是折入之後。

**收斂與上限**
- [程式] 收斂判準=處置閘。`cmd_loop_next` 的 cap-reached 只在「資訊齊全且閘沒過」才觸發,而閘全折就過,所以幾乎碰不到。
- [程式] 上限的實際牙齒在 `_cap_retro_record_block`:只有**已記人裁**(`loop cap-decision`)的迴圈,開新一輪才會被要求先有回顧;accept-risk 後不准再開輪。沒有人裁紀錄的迴圈一律放行。
- [筆記:`Projects/審查跑滿上限提示_計劃` WHY 2026-09-26] 「處置閘在一輪全部處置完就過關,所以『跑滿還沒過』幾乎不會發生;今天的迴圈跑到第 4、5 輪,都是過了閘之後編排者自己決定再審修正差異。」
- [程式] `_cap_hint_*`:到上限時 `loop next` 與處置閘印每輪折入數、最高嚴重度與提示,只印不擋。
- [程式] 超過 1800 行是軟上限(`_CANARY_SCOPE_SOFT_CAP_LINES`),只標 `scope_oversize`。[帳] 547 筆席次帶此標記,`scope_lines` 中位 955。

**資安席**
- [程式] `_disposal_security_step`:定錨 high、生效日 2026-09-12 後的迴圈,要有 `required-gated` 席的帳列、報告與快照雜湊對、看過的檔**內容雜湊**涵蓋判定輪全部檔(`_patch_file_changes`,同檔名改內容也會擋)。看整個迴圈不是每一輪。
- [帳] 2026-09-30 後開的 42 個 high 迴圈,42 個都有資安席(席名比對)。
- [筆記:`Systems/pitfalls-code-loop` RULE] 工具鏈本 repo 只看三類(提示注入、讀寫與執行越界、非刻意一步繞過),消費專案照舊。

**外家席**
- [程式] `_TIER_ROSTER` 全部 `external` 席 requirement=`conditional`,備註「2026-09-30 使用者裁:外家預設不派(省成本)」。鏡頭5 補原外家 finder 名額。
- [筆記:SKILL] 要另一家視角時(同門分歧、碰資安或不可逆)才派 Codex;Gemini 只備援。未派時收斂措辭是「單家族視角下未發現」,閘**不提醒**(測試釘住不印)。
- [帳] 2026-10-01 起按席名:sonnet 1,574、codex/gpt/sol 286、opus 39。其中編排者非 Codex 的外家席名 168 筆、16 個迴圈,83 筆集中在 10-07 一天,最後一批 10-20(4 筆)。編排者是 Codex 的 141 筆(對它而言是同門)。

**席位隔離**
- [程式] `mods/claude/lumos-guard/hooks/register.ts`:派工詞第一個非空行是 `LUMOS-SEAT: <迴圈>/<輪次>/<席名>` 的子代理(含它再派的)套工具白名單,寫檔只准 `/tmp/lumos-seat-work/<迴圈>/<席名>/`,不准碰席報告暫存處,Bash 只粗擋(`gh`、`git push`、`claude`、GitHub API)。
- [筆記:`Projects/審查席唯讀隔離_計劃`] 防的是「被文件裡的指令誘導」,不防有心繞過的席:Bash 仍是完整 shell,在 repo 裡改檔既不擋也不報。第三輪起「事後查 repo」整段拿掉(d4)。
- [筆記:`Verification/2026-10-07_審查席隔離真引擎實測`] 真 Claude Code 2.1.292 實測:寫 repo、讀別席報告、`gh` 被擋;`/clear`、熱重載後仍認得席位;未測 `/resume`。
- [筆記:SKILL 第 3 步] 同輪獨立靠「所有席收齊才動工作目錄、先到的報告不落地」,是編排者紀律。

### Inferences
- 分級是二值的「有沒有碰到七種字面型樣」。對 Python 工具鏈,新增一行 `open(` 就進 high,等於用字面型樣近似風險;這個分級從未被拿去跟逃逸對照校準(第二節)。
- 把 `pass` 換成「驗過處置閘才寫」不是新機制,只是接線;但手冊把它標成既有天花板,要動得先看決策脈絡。

### Gaps
- 未逐一驗 `_disposal_clause_step`、`_disposal_landing_step`、`_disposal_minor_release_step` 內部。
- 消費專案的編制差異只看了手冊,沒看消費專案的帳。

---

## 二、帳本量到的表現

### Takeaway
高風險迴圈幾乎從不「審乾淨」:224 輪裡只有 1 輪零發現,每輪條目數不隨輪次下降,10 月甚至持平在 18–22 條。後續輪約四到六成條目被編排者標成「上一輪修補造成的」。輪數上限被頻繁突破且都有人裁。真正的逃逸(放行後才發現)只有 11 筆手記,工具自己標「低估」。成本只有三分之一席次有 tokens,無美元。

### Cited Findings

**審查量**
- [帳] 324 個 code 迴圈的分級(取該迴圈第一筆帶 tier 的值):standard 170、high 79、light 21、未定錨 54。
- [帳] 依開立月份:7月 high 1/未定錨 13;8月 high 9/standard 16/未定錨 4;9月 high 30/standard 74/light 4/未定錨 16;10月 high 39/standard 80/light 17/未定錨 21。
- [帳] 治理帳 `design-loop converged` 事件:code 迴圈 558 筆(重複問閘),相異 277 個。324 個裡 47 個沒有過閘紀錄。

**輪數分布**(相異 round id;無輪次的舊列逐筆算一輪)

| 篩選 | tier | n | 1 | 2 | 3 | 4 | 5 | 6+ | 平均 | 中位 |
|---|---|---|---|---|---|---|---|---|---|---|
| 全部 | high | 79 | 11 | 9 | 35 | 13 | 6 | 5 | 3.32 | 3 |
| 全部 | standard | 170 | 59 | 31 | 62 | 17 | 0 | 1 | 2.24 | 2 |
| 全部 | light | 21 | 11 | 7 | 2 | 1 | 0 | 0 | 1.67 | 1 |
| 09-30 後開 | high | 42 | 2 | 3 | 21 | 8 | 5 | 3 | 3.71 | 3 |
| 09-30 後開 | standard | 83 | 20 | 11 | 40 | 11 | 0 | 1 | 2.55 | 3 |
| 10-15 後開 | high | 12 | 0 | 1 | 7 | 2 | 2 | 0 | 3.42 | 3 |
| 10-15 後開 | standard | 25 | 4 | 5 | 10 | 5 | 0 | 1 | 2.80 | 3 |

- 註:9 輪以上併入同一格,high 有 3 個。輪數不等於「到通過為止」,含棄案與重記編號。

**上限**
- [帳] 08-25 後開的迴圈,相對上限(high 3、standard 3、light 2):high 74 個裡 19 未滿、32 剛好、**23 超過(31%)**;standard 164 個裡 84/62/18;light 21 個裡 11/7/3。
- [帳] `cap-decision` 事件 86 筆(10-06~10-30),44 個迴圈,extra-round 66、accept-risk 20。`lumos loop retro-stats`:44 個都有回顧,以最新人裁算 accept-risk 19、extra-round 25;high 23、standard 21。
- [帳] 最後一輪在 10-07 後且超過 3 輪的 high 與 standard 迴圈 21 個(high 11、standard 10),**全部有人裁紀錄**,0 個違規。
- [帳] `cap-reached` 事件全帳只有 8 筆,4 筆在 code 迴圈。

**每輪條目**(09-09 後開、該輪載體帶 `refuted_set`;F=載體 `findings_set` 條數)

| tier | 輪次 | 輪數 | 席報 reported | 席存活 | F | 每輪 F | 折入 | 放行 | 重現不到 | 有 major 席的輪 |
|---|---|---|---|---|---|---|---|---|---|---|
| high | r1 | 64 | 1491 | 1474 | 1248 | 19.5 | 1227 | 21 | 16 | 100% |
| high | r2 | 57 | 946 | 945 | 849 | 14.9 | 818 | 31 | 0 | 87.7% |
| high | r3 | 47 | 803 | 773 | 719 | 15.3 | 672 | 47 | 30 | 87.2% |
| high | r4+ | 53 | 935 | 933 | 823 | 15.5 | 725 | 98 | 0 | 77.4% |
| standard | r1 | 125 | 838 | 823 | 739 | 5.9 | 695 | 44 | 8 | 74.4% |
| standard | r2 | 90 | 413 | 413 | 380 | 4.2 | 355 | 25 | 1 | 68.9% |
| standard | r3 | 66 | 269 | 269 | 258 | 3.9 | 195 | 63 | 3 | 54.5% |
| standard | r4+ | 18 | 68 | 68 | 70 | 3.9 | 46 | 24 | 0 | 38.9% |

- [帳] high 依輪次的月份趨勢(平均每輪 F):8月 17.9→7.3→2.0;9月 16.7→8.0→8.2→5.3;**10月 20.9→18.5→18.2→21.6**。
- [帳] 同一批換算「F/席次」:9月 2.65→2.01→1.71→2.18;10月 2.75→2.60→2.12→3.09。9 月後段輪派的席少(中位 r2 4 席、r4 2 席),10 月每輪中位都 7 席;`scope_lines` 中位約 1000–1500,未隨輪次縮小。
- [帳] high 多輪迴圈(09-09 後開)末輪 F 大於等於首輪的 13/57。
- [帳] 零發現輪:high 1/224。
- [帳] 末輪狀態(09-09 後開):high 64 個裡末輪仍有 major 席 42、只剩 minor 21、零條 1;standard 131 個裡 54/63/14;light 21 個裡 3/10/8。

**嚴重度**(09-09 後開,解析 2,574 份席報告的獨立 severity 行,去掉檔級行;含少量 clean)
- [帳] major+blocker 佔比:high r1 37.3%(1,516 條)、r2 26.6%(980)、r3 23.3%(862)、r4+ 20.3%(959);standard 38.8%(865)、37.7%(422)、33.6%(286)、28.4%(88);light r1 17.7%(62)。
- [帳] 帳內 `finding_severities` 只有 92 筆載體(minor 200、major 185、blocker 29),不能代表全體。
- [帳] `finding_kinds`:code 4,695、spec 642、process 133(process 2.4%)。

**放行**
- [帳] 09-09 後開的迴圈全部:F 5,981、折 5,552、放行 429(7.2%)、重現不到 59。放行率隨輪次升高:high 1.7%→11.9%,standard 6.0%→34.3%。

**辯方與假陽性**
- [帳] `refuted_set`:全審查帳 39 筆載體 72 條,code 迴圈 61 條。佔比 high r1 1.3%、r3 4.0%;standard r1 1.1%。
- [帳] 高度集中:61 條裡 28 條來自 `code-convergence-input-guards` 與它的記帳更正(同一批材料)。依時期:09-09~09-30 為 10/1,209;09-30~10-15 為 46/3,273;10-15 後 3/1,501。
- [帳] **這不是辯方殺傷率**。欄位記的是編排者重現不到,reasons 裡有實機重現不到、核對清單不算缺陷、合約範圍外等混合理由。
- [帳] `refute_verdicts` 全帳只有 10 筆載體(10-03~10-16),判決 agree 20、evidence 2、concern 0。這記的是辯方怎麼說,不是它對不對。檔名含 refut、辯方、defender 的卷證檔 45 個;code 輪 intake 563 份裡 38 份提到「辯方」(6.7%),其中 4 句是「有翻紅重現,未開庭」。
- [帳] 席報→席存活的落差:high r1 1491→1474(1.1%)。
- 假殺證據:見第五節,無紀錄。

**修補引入**
- [帳] `regression_set`(只算帶此欄的輪,10-01 起)佔 F:high r2 37.2%(119/320,18 輪)、r3 34.9%(109/312,15 輪)、r4+ **59.6%**(370/621,27 輪);standard r2 39.9%(67/168)、r3 47.7%(63/132)、r4+ 35.4%(17/48)。全部 id 都是 findings_set 子集(161/161)。
- [帳] 這直接回答 `Projects/代碼審修正關卡第0步_計劃` 的到期 REVISIT:fix-check **通過**後的下一輪,145 輪帶欄位,**1,025/1,913 條(53.6%)**被標成上一輪修補造成,129/145 輪大於零。另 31 個下一輪沒帶欄位。
- 資料品質:欄位是編排者判斷(`--regression-set` 說明:「編排者判斷是上一輪修補造成的」),手冊要求未判定就省略,所以有選擇偏誤;id 未去重。抽樣一份有同例修前修後實跑(`code-Android目標架構產生器/r2-intake.md`)。對照:[筆記:`Verification/2026-10-04_代碼審收斂根因盤點`] 第 1 案原本多數是「兩版都壞的舊缺口」,只有一例是真修補引入,標準嚴格得多。**53.6% 應視為上限方向的訊號,不是精確修補回歸率。**
- [帳] 回顧族別(`lumos loop retro-stats`,44 份跑滿回顧,一份可多族):same-family-unswept 43、other 31、fix-induced 27、spec-unclear 21、hostile-surface 20、seat-noise 12、scope-too-big 7、bar-moved 5。回顧列出行動項 100 條。

**逃逸**
- [帳] `docs/.escape-log.jsonl` 207 列,撤回 2 筆,有效 203 列(2026-09-08~10-30)。
- [帳] **大多數不是代碼審逃逸**:177 筆自動記,其中 164 筆 source=code-loop,是「代碼審記到 major」自動歸給設計審迴圈,意思是「設計審放過、代碼審接住」[筆記:`Projects/逃逸帳對得起來_計劃` WHY]。loop_kind:design 146、plan 23、code 7、未標 27。
- [帳] 掛在 `code-` 迴圈的列 11 筆,8 個迴圈(10 major、1 minor):code-enforcement-obs(推送閘)、code-推播漏網量測(生產)、code-每支檔有家×3(消費專案真推送、使用者回報、下游代碼審)、code-筆記形狀擋×2(下游設計審、編譯檢查)、code-筆記格子第1步(CI)、code-review-convergence-eval(CI,minor)、code-代理繞閘字樣問人(合併後另跑原生 `/code-review`)、code-原生配置排行(實機,「四輪代碼審與測試都沒抓到」)。
- [帳] 另有 CI 自動記 10 筆,評測集把這類歸「待人工判定」。
- [帳] `lumos loop escape-stats`:code 類分母(處置閘過關迴圈)合計 277,有漏網 6 個(2.2%)。工具逐行標「code 類只含手動記的逃逸,低估」。放行數達 20 的格:high×未分類 43 個 2 個,5%(區間 1–15%);standard×未分類 130 個 1 個,1%(0–4%);未定錨×未分類 21 個 0 個,0%(0–15%)。其餘都標「樣本太少」。
- [筆記:`Projects/審查評測集_計劃`] 2026-09-21 回頭挖:近 90 天 341 筆 fix 比對凍結 patch,得 **41 筆漏抓候選**,未人工確認。

**成本**
- [帳] tokens 大於 0 的只有 1,050/2,986 筆席次(35%;含 0 值是 1,055),8月 55/156、9月 372/836、10月 623/1,913,首筆 08-24。欄位由編排者逐席手填(`--tokens`、`--wallclock-min`,說明「選配」),`_cost_summary` 自己標「成本(自報,GIGO…)」。已記總量 1.468 億 tokens,每席中位 111,828、p90 189,868、最大 401 萬。
- [帳] 全席都有 tokens 的迴圈(倖存者,不代表全體):standard 83 個,中位 47 萬、15 席分鐘;high 14 個,中位 240 萬、平均 301 萬、最大 978 萬、109 席分鐘;light 8 個,中位 10 萬。
- [帳] 美元:code 迴圈 0 筆。`usd` 只在自主迴圈 `auto-*` 結局帳 12 筆($2.26~$80.03)。
- [筆記:`Verification/2026-09-05_skill-doctor成本基線`] 7 天 lumos-code-loop 930 萬 tokens/49 次,歸因方式不明,不能換算美元。

**席別產出**(09-30 後、high 迴圈,以席名正規式分類;一筆席次算一次)

| 席類 | 席次 | 存活條 | severity 達 major 的席次 |
|---|---|---|---|
| 資安 | 203 | 301 | 60 |
| 架構對齊 | 154 | 393 | 62 |
| 正確性 | 151 | 476 | 86 |
| 邊界 | 141 | 506 | 67 |
| 通才 | 103 | 335 | 44 |
| 外家(未被前面鏡頭名吃掉的) | 98 | 142 | 51 |
| 合約 | 89 | 397 | 37 |
| 併發 | 76 | 183 | 25 |
| 資源 | 52 | 113 | 18 |
| 其他命名 | 112 | 537 | 33 |

- [帳] 通才席 RETIRE-IF 代理值(10-14 後開的 high 14 個迴圈,達 10 個的條件已滿):通才 54 席次 25 個 major 席;正確性 37、邊界 31、合約 13、併發資源 14,四席平均 23.75。通才沒有低於一半,不觸發。這是席級代理,RETIRE-IF 要的是「存活且折入的 major」條目數。

### Inferences
- F/席次在 2–3 附近持平,條目數主要跟派了幾席成正比,不跟剩多少缺陷成正比。這與 64.6% 獨家率(每席只抽到一部分)相容:每一輪新席都在抽新樣本。**這是推論,未排除其他解釋**,例如修補本身帶進新條目(上面 35–60%)、標準隨輪移動(回顧族 bar-moved 5 個)。
- 9 月到 10 月 r2 以後條目翻倍,同期出現三件事:修訂輪從縮編改成全編制、修補鏡頭上線(10-06)、§3.1 整條分支材料規定。三者同時,無法拆因果。
- 「處置閘通過」不代表品質,只代表帳清了;末輪 42/64 個 high 迴圈仍有 major 席。
- 放行率隨輪次升高,加上 accept-risk 19 個迴圈,顯示停手實際上是人(或編排者)的判斷,不是收斂訊號。
- 11 筆真逃逸裡,抓到的多半是**執行或真環境**(實機、消費專案真推送、CI、編譯檢查),只有 1 筆靠另一種審法。這與 `Verification/2026-10-02_代碼審完成路徑一句小實驗` 的結論同向:缺的常是程式碼裡看不到的事實。樣本小。

### Gaps
- 無法把 `pass` 事件連到迴圈:595 筆 passed 只有 195 筆的 note 含 `code-`,事件無 tier 欄。
- 無法算 standard 改動裡有多少根本沒開迴圈:推送事件沒記 tier。
- 09-09 以前的輪沒有 `refuted_set`、`reported` 欄,趨勢不能往前延伸。10-01 以前沒有 `regression_set`。
- 條目是否為真缺陷、席間重疊,2026-08-23 後都無資料。
- tokens 缺 65%,且可能偏向某類會談;不能外推總成本。

---

## 三、既有內部實驗與結論

### Takeaway
做過的受控實驗都是小樣本(每格 2–3 席),多半結論是「維持現狀」或「未判定」。最有分量的是一個離線量測(席間獨家率 64.6%)與兩個規模實驗。2026-10 那批「收斂改善」只建了工具,沒有任何一篇量到輪數下降。

### Cited Findings
- [筆記:`Verification/2026-09-03_席間覆蓋率離線量測`] 2026-07-10~08-23 的 85 個確定多席輪、822 個相異缺陷:獨家率 **64.6%**。2 席輪 74.2%、3 席 60.8%、4 席 58.3%,邊際遞減;4 席層只有 13 輪。「獨家=真漏抓」靠零放行輪的集合推論(15 輪,當時全帳放行率 1.1%),不是直接證據。`capture_counts` 手填,之後沒人填。該篇取代兩份死在設計審的量尺計劃。
- [帳] 該篇 `revalidate_when` ③ 是「放行率超過 5%」。現在 09-09 後開的迴圈放行率 7.2%,**觸發條件已成立,推論前提需重驗**。
- [筆記:`Projects/審查規模對照實驗`,2026-08-02] 同一 2770 行 patch,3 席各看三分之一 vs 各看全部:相異缺陷 4 vs 5,不支持「量大漏看」。n=1 材料,約半數發現靠讀未來 commit,判定者是作者。
- [筆記:`Projects/審查規模對照實驗二_Landmark真缺陷`,2026-08-02] 兩根上線後才發現的真缺陷、單 commit repo、判準預先登記:小 payload 3/3、大 payload(37–40K token)4/4。不支持。有天花板效應,只跑每格 3 次,M 條件未跑。事後觀察:大 payload 有一席把同缺陷降成 minor 並加但書(n=1)。1800 行軟上限因此降級為僅憑外部文獻。
- [筆記:`Verification/2026-09-11_全報vs抑噪試點`] 同一 1421 行 patch,各 3 席 sonnet,盲評:抑噪組命中已知 1.0 條、其他真問題 3、假問題 0;全報組 1.33、12、0。依預設判準**維持現狀**。全報多報的 10 條經盲評全部成立,判準沒涵蓋。兩組都沒找到 K3、K4、K6、K7,那些在真迴圈由外家、架構、資安席抓到。擴大重做的 REVISIT 已關閉進立案清單。
- [筆記:`Verification/2026-10-02_代碼審完成路徑一句小實驗`] 四個真事故、每組 2 次:加「列出完成路徑」一句 3/8 vs 3/8,不接線。沒人抓到的兩案缺的是外部 API 語意與使用情形,不是問法。
- [筆記:`Projects/審查評測集_計劃`,2026-09-21] v1 核心題 21(漏抓 15、多抓 6)、待判定 8。三層:機械事實(`loop replay --golden`,134 份回放 133 致)、下游事實、人工標註(未開工)。代理指標「當天有動測試」被判太粗。
- [筆記:`Projects/審查有沒有用記帳_計劃`,09-09 落地] 寫側拒收未正規化報告、`reported` 機器數、載體必帶 `--refuted-set`、逃逸當下記。刻意不建評測系統。
- [筆記:`Projects/自主審查量尺_計劃`,superseded] 想做類別逃逸率、抽查已放行改動、盲審對照。設計審 r1 七席 29 條,帳本接不起來,拆成 `Projects/逃逸帳對得起來_計劃`(done,做了第一件)。②抽查與③盲審留在該計劃的待辦描述,含「舊判準沒有差別時也約 98% 會觸發」的檢定問題。
- [筆記:`Projects/代碼審修復穩定性試行_計劃`] 五案試行只完成第 1 案 `code-repair-pilot-01`:4 輪、5 根因修復組、已證修復引入 1、問閘全 FAIL、無放行無推送;耗時未知。REVISIT 2026-11-03。
- [帳] 帳上 `pilot` 迴圈只有 `code-repair-pilot-01` 一個,佐證其餘四案沒開。
- [筆記:`Projects/結清式收斂_計劃`] 把「連 K 輪沒挑到」換成「逐條約束結清」,來自 AREX。僅接單席路徑。首個 dogfood(2026-07-31):settle framing 注意力探針命中 1/3,低於 panel 的 4/5;有席交「12 條全成立」卻漏掉植在主查條目裡的錯。進度會累積、失敗訊息好讀;fold 後 35 條全過期要重蓋。狀態 doing。Issue `settle路徑席位對帳無輪次可對` 仍 open。
- [筆記:`Verification/2026-10-04_代碼審收斂根因盤點`,pending] 第 1 案:多輪未收斂的主要證據是**修法沒包住整條使用路徑**,不能直接歸因成每輪新造 bug。提出修前列「資料權威、寫入者、讀取者、失敗後狀態、跨時間邊界、反例」的入口表,只限下一新案試。事後適配,不證明能事前抓到。
- [筆記:`Verification/2026-10-07_代碼審收斂改善主線交付`] 補強修補輸入與版本來源;明寫「沒有受控實輪數下降結論」。REVISIT 10-21 到期。
- [筆記:`Verification/2026-10-07_Claude代碼審公開片段調研`、`Projects/Claude代碼審流程與收斂性對照_計劃`] 讀固定公開片段與官方外掛,鏡像 2.1.88 未認證。候選:避免修訂輪持續加入非必要風格或自選重構;檢查測試能否抓住具體退化。下一步最小實驗未執行。
- [筆記:`Projects/原生代碼審當通才席_計劃`,2026-10-14] 無頭跑官方 `/code-review` 再轉格式的方案被設計審否決(隔離變弱、第二套引句與等級規則、注入假等級行、可能誤觸 ultra 計費),改成八角度寫進通才席。REVISIT 2026-11-30、2026-12-14。
- [筆記:`Verification/2026-10-07_審查回顧eval補強`] `governance/research/review-convergence-eval` 建好成對比較尺,歷史帳唯讀試行 224 個 code 編號、10 個分輪未知、153 個成本未知。**未跑真實模型對照**。
- [筆記:`Issues/流程自產工作量未量測`] 82 行唯讀功能跑 3 輪 9 席 44 條;「對流程成本效益用的是信仰」。入口是 `finding-kind`,REVISIT 10-15。
- [帳] 回看結果:process 133/5,470(2.4%)、spec 642(11.7%)。

### Inferences
- 內部實驗的共同形狀是「改問法沒用,缺的是程式碼外的事實」與「加席有效但遞減」。沒有任何實驗測過收斂判準、輪數上限、修訂輪編制這三個最貴的變數。
- 規模實驗的「不支持」只對兩根偏容易的針成立;不能拿來說 Lumos 的 1000–1500 行材料沒有問題。

### Gaps
- 全報擴大重做是否真的做了,本稽核只看到 REVISIT 關閉指向立案清單,未追到結果。
- 第 2 案入口表的成效無資料。

---

## 四、已否決或退場的做法與理由

### Takeaway
以下每條都有紀錄。重提前要有新證據,而不是新文獻。

### Cited Findings

| 項目 | 結論 | 理由 | 記在哪 | 標記 |
|---|---|---|---|---|
| 植入 canary | 2026-08-14 停用 | caught/missed 譯不出「認真」且無下游消費,空轉;煙霧偵測角色被引句錨定蓋掉;隱含「不知道被測」前提有 eval-awareness 實證。工具封存。重啟條件:能分「真醒/演醒」的探針 | `Systems/canary-audit` d5 | [筆記] |
| canary 校準器、SNR 腳本 | 2026-08-26 刪 | 輸入源斷供 | `Systems/canary-audit` | [筆記] |
| capture-recapture 殘餘進閘 | 2026-08-14 降 advisory | 殘餘<1 組下輪 major 67% vs 對照 79%,p≈0.25;f1≤1 公式退化;席獨立前提被自帳否定;攔截近隨機摩擦 | `Projects/收斂閘殘餘估計降級_計劃` | [筆記] |
| 用獨家率預測下一輪或進判準 | 明令不准 | 描述性數字;同帳不同用途 | `Verification/2026-09-03_席間覆蓋率離線量測` | [筆記] |
| 收斂閘漏項敏感度 v1、v2 | 設計審死 | 核心算子資料層不存在;對照組 92% 洩題;兩席讀同材料重疊只 36–44%,尺分不開 | 同上 | [筆記] |
| panel 閘、K=2、抽查義務 | 2026-08-25 退役 | Enzo 甲裁,改處置閘;三配套從未實作 | `Projects/probe輪退場_計劃`,`Systems/convergence-evidence-gate` | [筆記] |
| 外家席預設派 | 2026-09-30 改條件席 | 省外家成本;鏡頭5 補名額。先前 08-22 已裁缺席不硬擋 | `_TIER_ROSTER`,`Issues/外家席長期缺席仍照跑loop` | [程式]+[筆記] |
| 外家升主力席 | 2026-07-30 不採 | 連動佔人數、重疊帳、fail-closed,且硬要求第二家 CLI 違反零依賴 | `Systems/canary-audit` | [筆記] |
| 把資安鏡頭完全排除 | d5 2026-08-27 被 d6 翻 | 高風險必派資安 | `Systems/pitfalls-code-loop` d5、d6 | [筆記] |
| 工具鏈資安鏡頭照舊全範圍 | d8 2026-10-14 不選 | 一人本機、AI 依序操作;刻意多步偽造改得動帳本就改得動閘,追著加機制沒有盡頭。代價:消費專案照舊,工具鏈少看。`until:2027-04-14` | `Systems/pitfalls-code-loop` d8 與 RULE,`Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃` | [筆記] |
| 外來文字回顯類資安修補 | 2026-10-27 不修 | 不會讓判定錯誤放行或資料消失就判範圍外;code-e2e-gate 五輪每輪都在新輸出點找到這類 | `Systems/pitfalls-code-loop` RULE | [筆記] |
| 併發鏡頭(工具鏈) | 改資源鏡頭 | 只看孤兒行程、逾時誤擋、記憶體與大輸入;不審多人多會談競態 | 同上,memory `lumos-threat-model-single-user` | [筆記] |
| 資安席修補輪只看變過的檔 | 不做 | 會出現一支檔沒資安席真讀過、閘卻判涵蓋 | `Projects/審查收斂規則_計劃`〈不做〉 | [筆記] |
| 無頭跑 `/code-review` 再轉格式 | 不做 | 見第三節 | `Projects/原生代碼審當通才席_計劃` | [筆記] |
| 把審查員改 `claude -p` 只給 Read/Grep/Glob | 未採 | 席位常要跑 Bash 重現 | `Projects/審查席唯讀隔離_計劃` | [筆記] |
| 隔離用黑名單、逐詞解析 Bash、事後查 repo | 連續三輪否決 | 漏擋誤擋;事後查 repo 會執行 repo 設定的過濾指令、搶鎖 | 同上 d2–d4 | [筆記] |
| `lumos mutate` | 2026-08-26 拆 | 建了沒人跑,治理帳 0 次使用 | `Projects/建了沒人跑批次裁定_計劃`,reference.md | [筆記] |
| 舊版跑滿判斷依據 | 2026-09-26 取代 | 想掛的出口不會觸發;拿掉「修正引起的比例」訊號,因引句不給行號、patch 位移污染 | `Projects/審查跑滿上限提示_計劃` | [筆記] |
| 字面判斷的守衛繼續補字表 | 規則 | 同類第二次被打穿就換形狀;看門不做得比整套系統更難騙 | SKILL 第 4 步 | [筆記] |
| 把 finding 硬上限寫進派工 | 不設 | 會藏真 finding | reference.md 抑噪紀律 | [筆記] |
| 模型信心分數當證據 | 不用 | 信心不等於證據 | `Projects/Claude代碼審流程與收斂性對照_計劃` | [筆記] |
| 在通過的發現上做評測 | 不收 | 折入當答案等於拿自己判斷當標準 | `governance/eval/review-evalset/README.md` | [筆記] |
| 額度或成本當不機械擋的理由 | 反對 | 使用者偏好機械擋 | memory `prefer-mechanical-block-over-reminder` | [筆記] |

- [筆記:memory `lumos-threat-model-single-user`] 威脅模型:只顧中英文、單人、AI 依序操作;信賴原則不防 AI 刻意偽造;併發與多語系發現放行附理由。使用者原話見 `Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃`。**這只適用工具鏈本 repo,消費專案照舊。**
- [筆記:`Systems/pitfalls-code-loop` d7] 擋推鏈不跑 lint 的 d4 已被 d7 翻,改成獨立新增告警閘。別再提「把 lint 接進擋推」。

### Inferences
- 建議外部做法時,「多模型/跨家族預設席」「殘餘估計」「注意力檢查」「finding 上限」都已在這張表上。要重提,得帶上新的本地證據,例如逃逸數據或成本對照。

### Gaps
- 外家預設不派之後,逃逸率有無變化未量過;樣本不足(第五節)。

---

## 五、記錄在案的未解問題

### Takeaway
有一大批回頭條件在 2026-10-20 前後集中到期,多數寫著「不足十輪維持未判定」。沒有人回頭,等於資料早已足夠(本稽核直接算得出來)卻沒人讀。

### Cited Findings

**到期未關 REVISIT**
- [帳] 掃全圖譜未帶 `[closed:` 且日期 ≤ 2026-11-03、內容跟審查相關的 REVISIT:67 條(關鍵字篩選,含少量邊緣)。最相關的:
  - `Projects/代碼審修正關卡第0步_計劃`、`Systems/代碼審修正關卡`(10-20):fix-check 通過後下一輪被標修補造成的有幾條,決定要不要做「先紅」。**本稽核已算出 1,025/1,913。**
  - `Projects/代碼審修正關卡_計劃`(10-20、10-30):重開或停案;轉擋與否。
  - `Projects/審查評測集_計劃`(10-21):漏抓樣本 <50 或從未比較過配置就撤。
  - `Projects/審查回顧轉可比較eval_計劃`、`Verification/2026-10-07_審查回顧eval補強`(10-21)。
  - `Projects/每輪修補差異派工_計劃`(10-20、11-03):RETIRE-IF 十個迴圈零命中且準備中位超過 5 分鐘。
  - `Projects/審查跑滿上限提示_計劃`(10-26)、`Projects/代碼審跑滿上限的判斷依據_計劃`(10-25)、`Projects/逃逸帳對得起來_計劃`(10-26)、`Projects/雙向門放行_計劃`(10-17)、`Projects/代碼審鏡頭對照DDIA_調研`(10-27)。
  - `Projects/Claude代碼審流程與收斂性對照_計劃`(10-21)。
  - `Projects/代碼審修復穩定性試行_計劃`、`Systems/pitfalls-code-loop`(11-03)。
  - `Issues/loop機制痛點_Landmark_code-crossclaim實跑回饋`、`Systems/codex-harness`(10-16,等 Enzo 裁)。
  - `Issues/編排者改寫席位引句`(10-15):收貨當下釘指紋,或接受只靠編排者誠實。

**停滯計劃**
- [筆記] `Projects/結清式收斂_計劃` doing(7 月起);`Projects/代碼審修復穩定性試行_計劃` doing,五案完成一案;`Systems/每輪修補差異派工` doing,等觀察。
- [筆記] 「抽查已放行改動」與「盲審對照」拆出後未立獨立計劃(`Projects/逃逸帳對得起來_計劃` 第 85–86 行描述)。

**開放 Issues(審查相關,節選)**
- [筆記] `引句錨定只驗前綴_後半可編造`、`凍結接受非綠判定`、`處置表把派工問題寫成席位發現`、`工具鏈範圍外手法紀錄`、`代碼審next把新處置帳誤判舊panel`、`code-loop-pass不能指定分支`、`派工鏡頭附的表態取自會談目錄的分支`、`派工鏡頭對單篇計劃筆記算三分鐘`、`治理帳與審查帳其他讀寫函式的硬化缺口`、`治理帳多個寫入者都沒上鎖`、`流程自產工作量未量測`(doing),以及多篇「第 N 輪放行的小缺口」收尾 Issue(審查收斂規則第七輪、回頭重讀指紋第六輪、推送前收集第五輪、探針輸出寫入第八輪、原生配置排行第四輪、週評通知、Android 收據重跑第四輪等)。

**已知弱點與「沒有」宣稱**(每條列出搜尋;這些可能決定要不要動手)

下列「未發現」宣稱,搜尋包括 `lumos search` 與對 `scripts/lumos`、`skills/`、`governance/eval`、`governance/research` 的 grep。獨立覆核結果見本節末。

| 宣稱 | 我的搜尋 | 結論 |
|---|---|---|
| 辯方開與關從未對照量測 | `lumos search` 用「辯方 對照 消融」「辯方 開關 實驗」「refuter 量測」「辯方 殺錯 假陽性」(★「殺錯」0 命中);`grep -i 'refut\|辯方' governance/eval governance/research`,命中都是檢索標註資料、`rule_conflict_scan.py`,無對照實驗 | 未發現。`Systems/finding-refute` 明寫「辯方降級效力本輪未觸發,首個出現假陽性的真實 loop 才可實測」 |
| 辯方假殺率無資料 | 同上;`refute_verdicts` 10 筆;retro 族別無此類 | 未發現量測 |
| 代碼審美元成本未記 | `grep usd`:`.canary-log` 只有 `auto-*` 結局帳 12 筆;`--tokens` 手填選配 | 代碼審 0 筆 |
| 程式不驗修補後有全新席看過 | 讀 `_loop_status_disposal` 九步、`cmd_code_loop` pass、`_codeloop_guard_verdict`;`grep '全新席\|delta' scripts/lumos` 無判定邏輯 | 未發現機械檢查 |
| `pass` 不驗處置閘 | 讀 `cmd_code_loop` 全段 | [程式] 確認;SKILL 第 2 步也寫「pass 本身不回頭驗問閘有沒有過(既有天花板)」 |
| 主動抽查已放行改動未實作 | `lumos search "逃逸 量尺 抽查"`;`grep '^def .*(sample\|audit_sample\|spot)' scripts/lumos` 無相關 | 未發現實作,只有計劃文字 |
| 盲審對照未跑 | `lumos search "盲審 作者 說法"`(盲審 3 命中,都是待辦描述或外部文獻) | 未發現執行紀錄 |
| 評測集未用於比較配置 | `grep -rn 'review-evalset\|miss-candidates' scripts governance/autonomous_loop` 無引用;`git log -- governance/eval/review-evalset` 一筆改名提交 | 未發現使用 |
| 08-23 後無席間重疊量測 | [帳] `capture_counts` 欄;`revalidate_when` 仍待 | 未發現 |

**獨立覆核**(CLAUDE.md 規定:會決定要不要動手的「沒有」,先派乾淨代理用原始問題對一次):派一個 Explore 代理,只給八個原始問題,不給我的結論。八題結論全部與上表一致,另補幾條:
- 辯方:`Projects/世界解重新註解2026-10_迴圈工程_調研` 明寫「辯方的效益從沒做過開/關對照」;`Systems/finding-refute` 有 REVISIT 2026-11-30「辯方 evidence 抽驗」,尚未做。它搜過 辯方 對照、refuter 誤殺、辯方 誤殺 真發現、refuter 消融 ablation、翻轉率、殺錯、false_kill。
- 美元:12 筆 `auto-*` 合計約 $523.6,那邊由 `governance/autonomous_loop/orchestrator_result.py::extract_cost` 自動取值;代碼審沒有這條路。
- 全新席:搜過 fresh、新鮮、修後、修補另審、最後 修補 沒審。`pass` 只帶 `--note`、沒有迴圈編號,所以綁不到迴圈。
- 抽查:`scripts/lumos`、`governance/daily-governance.sh` 無 audit-sample、抽查帳、盲審;計劃裡的 `t_audit_sample_*` 測試不存在;逃逸帳無抽查站。
- 盲審:`Projects/世界解重新註解2026-10_Agent編排_調研` 記為延後,「附與不附的比較查無」。
- 評測集:`Projects/審查評測集_計劃` 的 41 筆與 8 筆確認都還沒勾,到期未處理,計劃仍 doing。
- 席間重疊:`capture_counts` 102 筆,最後 08-23;席報告都還在,理論上可重算,但沒人算過。
- 一處分歧:覆核說 `_disposal_security_step`「只查檔案涵蓋、不查版本」。我重讀程式,它比對 `_patch_file_changes` 的逐檔內容雜湊(`jchg[f] not in seen[f]`),改過內容會擋。**以我讀到的程式為準。**

**已被提過、尚未執行的候選**(外部比較時別當新點子)[筆記]:
- 同鏡頭×3、三個不同鏡頭、混家的消融,比聯集召回(`Projects/世界解重新註解2026-10_迴圈工程_調研`)。
- 辯方開與關兩組回放,統計 skip 與跳過次數(同篇)。
- 全報 vs 抑噪擴大重做(`Projects/逾期回頭條件立案清單2026-10_計劃`,評測集已有,條件比當時好)。
- 修訂輪延後非必要建議的三類案例實驗(`Projects/Claude代碼審流程與收斂性對照_計劃`)。

### Inferences
- 最便宜的下一步不是新機制,而是把已到期的 REVISIT 用現成帳本答掉:修正關卡、跑滿回顧、逃逸類別,數字都已算得出。
- `Projects/代碼審修正關卡_計劃` 設的「擋到過一次真問題才轉擋」標準,因為 53.6% 這個數字要重新看;但先要校正 regression_set 的品質。

### Gaps
- 67 條是關鍵字篩選,未逐條判斷是否真的未處理。
- Issue 清單以 `status: open|doing` 加關鍵字篩,含非審查項,已人工挑過,可能漏。

---

## 六、筆記與程式對不上的地方

### Takeaway
手冊的現行規則大致與程式一致,但 reference.md 留著多處舊段落,幾條「強制」其實是紀律。下面逐條列兩邊。

### Cited Findings
1. **外家席是否 fail-closed**:`skills/lumos-code-loop/reference.md`〈平行 panel 模式(≤3 輪,取代 6 輪循序)〉仍寫「tier=high=fail-closed…不得收斂攤人裁」。`_TIER_ROSTER` 全為 `conditional`,SKILL 寫預設不派。**以程式為準**。同檔較早一段已加 2026-09-30 註,這段沒加。
2. **辯方範圍**:reference.md〈判讀 + 辯方〉與 `Systems/finding-refute` 寫「對每條 ≥major」。SKILL 與 templates.md §2 寫「只有低共識的 ≥major」。[帳] 6.7% 的 intake 提到辯方,實務接近後者。這是規則層矛盾,程式答不了。
3. **上限是否硬停**:SKILL「到頂沒過 → 停,攤給人裁」;reference「到頂還沒收斂就停」。`cmd_loop_next` 的 cap-reached 在閘過時走不到,`_cap_retro_record_block` 對沒人裁紀錄的迴圈放行。[帳] 10-07 後實務上 21/21 都有人裁,所以是紀律守住的,不是閘。
4. **收斂的意思**:reference.md 有整段 K=2、連兩輪乾淨的文字(標回放用)。現行閘只看末輪全處置。`Systems/convergence-evidence-gate` 頁首有告示,一般讀者仍可能讀到舊段。
5. **`impact --sync-check`「強制,不可跳」**:SKILL 第 8 步這麼寫。`cmd_code_loop` pass 不呼叫它;pre-push 只取 JSON 給後續用。是否在別處擋未追完,**判不出就不改**,記為未解。
6. **「pass 留痕=審過」**:CI 訊息與手冊都把 pass 當審查留痕;程式只記一行。
7. **`_TIER_PARAMS` standard=3 人 vs 名冊 1 人**:`cmd_loop_next` 註解已說明,新迴圈以名冊為準,舊 panel 迴圈保留 3。一致,但讀 `_TIER_PARAMS` 會誤判。
8. **資安席涵蓋**:SKILL 寫「看過的檔沒涵蓋最後一版」。程式比內容雜湊,比「檔」更嚴。程式較準確。
9. **放行率前提**:`Verification/2026-09-03_席間覆蓋率離線量測` 的「這套流程幾乎不判誤報」(1.1%)已過期,現為 7.2%(不同母體與時期)。
10. **評測集 README 的「528 輪、8449 條」**:是 2026-09-21 當時數字,現在 code 迴圈就 813 輪。不是錯,是舊。
11. **`Systems/canary-audit` 等節點舊 KEY 行**:同節點內新舊並存(K=1、K=2 歷史行標明)。CLAUDE.md 已說明這種情形,以帶日期者為準。
12. **工具 `lumos gov --stats` 的「審查有沒有用」段**:SKILL 寫 code 迴圈問閘尾不印,程式 `if not readonly and not str(loop_id).startswith("code")` 分支一致。

### Inferences
- 第 1、2 條值得修文件。第 3 條若要變成閘,得決定「到上限」的定義,因為現況是閘過了還繼續開輪。

### Gaps
- 第 5 條未在此輪追到底。
- 未比對 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 與程式的逐條一致性。
