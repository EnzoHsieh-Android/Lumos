---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/design-loop
  - Systems/convergence-evidence-gate
  - Systems/finding-refute
related:
  - "[[Projects/probe輪退場_計劃]]"
  - "[[Verification/2026-10-14_修補大小與下一輪major回放]]"
  - "[[Projects/改動與修補拆小_計劃]]"
---
# 代碼審minor解綁_計劃

代碼審的處置閘現在規定:輪內任一席 severity 是 major 以上,這輪的 accepted 必須是空的——不只 major 要折,連同輪的 minor 也一條都不准附理由放行。帳本上,同時有 major、恰一筆載體、載體標了逐條嚴重度的代碼審輪有 78 輪,176 條 minor 有 174 條被折入;這個比例是規則本身造成的(閘禁止放行,折入率必然接近全部),量的是規則不是編排者偏好。其中 23 輪含 blocker 席(29 條 minor,blocker 規則不動,改了也放不行),真正會受影響的是只含 major 的 55 輪、147 條 minor。另外,有 major 的代碼審輪共 461 輪,歷史上只有 78 輪(17%)的載體帶逐條嚴重度;新規則要編排者主動帶逐條來源(`--finding-source`)才生效,手冊把它寫成「major 輪要放行 minor 時的必要動作」,沒帶的照舊。「為了折一條 minor 新加了通道、下一輪因為新通道缺測試被判 major」在卷證裡有一個完整個案(`code-週評通知` r2→r3,這個迴圈沒標逐條嚴重度、不在上面 78 輪內),是單一個案、不是普遍規律。

這份計劃把連帶拿掉:major 以上照舊一律折,minor 可以附理由放行;放行的每一條都要指回席報告裡原本那一條,閘直接讀原報等級,不信編排者自填。並把「哪些問題算 major」寫進審查席讀得到的地方。

WHY:代碼審處置閘改成「放行的每條都必須指回席報告原條、原報等級 ≤minor;原報 major 的每一條都必須指到已折入的 id,或帶辯方反證(evidence)與可核對 file:line 的降級放行」,不再因同輪有 major 就禁止放行任何條 [出處:2026-10-14 使用者裁;[[Verification/2026-10-14_修補大小與下一輪major回放]];Codex 交叉診斷 `governance/review-reports/收斂診斷/codex-gpt-6-astra.md`;設計審 r1 七席 `governance/review-reports/代碼審minor解綁/`] [因:連帶規則讓 minor 修補進入當輪、修補膨脹又帶出新的驗證義務;d2 當初要補的是「major 可附理由放行」這個洞,本計劃 major 照舊必折,洞沒有重開] [不選:維持現制;把 major 也開放附理由放行(代碼審 major=會做出錯行為,必修);只改手冊不改閘;數量配平(放行的 minor 數不得多於報告 minor 數——r1 七席一致指出分子自填、分母可用 clean 行、重記報告、降級清單灌大,擋不住把 major 標成 minor);另開降級清單旗標(跟既有辯方表態 `--refute-verdict evidence` 重複);只限 minor 修補範圍、不動閘([[Projects/改動與修補拆小_計劃]] 已縮成提示,證據不足以單獨立案)]
PRIOR-ART: Google Engineering Practices 的審查標準把必要的改正與可選的細節(Nit)分開處理(https://google.github.io/eng-practices/review/reviewer/standard.html);本 repo 散文設計審早就允許 non-blocking 附理由接受([[Projects/設計審收斂重定義_計劃]] 決策 d1,內文稱 d5)。逐條嚴重度(`--finding-severity`,帳上 `finding_severities`,可重複旗標)、報告嚴重度解析(`_report_severities`,回傳報告裡每一行獨立 severity 宣告的出現序)、辯方表態(`--refute-verdict id=evidence`,寫側已強制 evidence 必在 accepted)、留痕重驗(`_prov_check`)都已存在;新旗標照 `--finding-severity` 的可重複寫法,新檢查照既有 `_disposal_*_step` 的獨立步驟寫法。
RETIRE-IF: REVISIT 抽查時,放行的原報 minor 經人判定其實是 major、或辯方降級放行的原報 major 經人判定反證不成立,兩類合計累計 3 條;或使用者回頭審放行理由覺得在放水——就照〈回退〉恢復舊規。(逃逸自動記看不到被標成 minor 的條,所以不拿逃逸帳當觸發。)

## 範圍

- 做:①處置閘代碼審輪級條件改成「逐條指回原報」;②載體新增可重複旗標 `--finding-source`(每個 id 指向哪份席報告的第幾條);③辯方用反證把原報 major 降級放行,沿用既有 `--refute-verdict id=evidence`,另要求放行理由附可核對的 file:line;④派工範本代碼審席的嚴重度判準補三類常見爭議;⑤用 `lumos decision-add` 正式取代 d2 的字面範圍;⑥手冊與筆記同步。
- 不做:不改 blocker 規則(輪內有 blocker 照舊 accepted 必空);不開放不帶反證的 major 放行(原報 major 只能折,或經辯方 evidence 加可核對 file:line 降級後放行);不改散文設計審;不改三輪上限、必派席與架構對齊席的嚴重度錨(架構對齊「引入第二種做法或跨層直呼算 major」是使用者先前定的,要動另裁);不改「原始報告不可改」——不做「編排者下調嚴重度後放行」;不新增降級清單旗標;不開新的略過旗標。

## 做法

- **逐條來源**(`canary record` 載體筆新增可重複旗標 `--finding-source <id>=<報告檔名>#<序號>`,帳上欄位 `finding_sources: {id: ["檔名#序號", …]}`,型別加進 `_GOV_FIELD_TYPES`):
  - 序號=該份報告經 `_report_severities` 解析出的宣告,去掉檔首那一行檔級宣告之後的第幾個(從 1 起)。報告已正規化(記帳寫側本來就擋沒正規化的),所以檔首必是檔級行。
  - 同一個 id 可以指多條(多席報了同一件事);同一條原報也可以被多個 id 指(編排者把一條拆成兩件處理)。同一個 `id=檔名#序號` 重複給視為一條(去重)。
  - `_GOV_FIELD_TYPES` 加 `finding_sources`(dict),`_gov_event_types_ok` 同步加「值必須是字串清單」(比照 `finding_kinds`、`refute_verdicts` 的值檢查)。
  - 寫側只驗格式:id 要在 findings-set、檔名要是同輪某一列帳的 `report_path` 檔名、序號是正整數。真正的等級核對在處置閘做(載體不一定最後記,記帳當下拿不到同輪全部報告)。
  - 不帶就不帶:沒有 `finding_sources` 的載體,major 輪照舊規則判。
- **處置閘第 ② 步(處置集合)**,代碼審輪:
  - 輪內有 blocker 席:照舊 accepted 必空。
  - 輪內有 major 席、accepted 非空、載體沒帶 `finding_sources`:照舊判不過,訊息原句保留(含「major 一律折」,`t_panel_probe_retired` 斷言它)。
  - 輪內有 major 席、accepted 非空、載體帶 `finding_sources`:第 ② 步不判這一條,交給下面新增的獨立步驟;第 ② 步其他條件(全集、去向、理由字數)照舊。
- **新增獨立步驟 `_disposal_minor_release_step`**(放在留痕重驗之後,跟 `_disposal_security_step` 等同一種寫法;只在上面第三種情況執行):讀同輪**每一列帳**的報告(含同一席重記前的舊報告——每一份都要被交代,不只最新一份),讀檔走 `_prov_check` 驗過 sha 的路徑、`errors="replace"`;讀不到或 sha 不符,這一步判不過。然後逐條核對:
  1. **來源存在**:每個 `finding_sources` 指的檔在本輪帳上、序號沒超出那份報告的宣告數;不然判不過並點名。
  2. **原報 major 都有交代**(blocker 輪已在第 ② 步分流,寫側又規定帳面不得低於報告最高,所以這一步只會遇到 major):每份報告裡每一條原報 major 的宣告,都至少被一個 id 指到;沒被指到的點名判不過(防「把 major 跟 minor 併成一個 id」與「指錯條」——指錯了,真正那條 major 就沒人指)。
  3. **原報 major 只能去折入或有證據放行**:指到原報 major 的 id 必須在 folded;若在 accepted,必須同時符合 `refute_verdicts[id] == "evidence"` 且該 id 的放行理由裡有至少一個 ``file: `路徑:行號` `` 佐證、路徑在 repo 裡存在且行號不超出檔長(沿用 refcheck 的解析)。重現不到清單(refuted-set)不提供豁免:寫側規定它的 id 不得在發現清單,所以被列進去的原報 major 一定沒有 id 指到,由第 2 點擋下(防「把 major 塞進重現不到清單、其餘全放行」)。
  4. **放行的每條都有來源**:accepted 裡每個 id 都必須在 `finding_sources` 裡,沒有來源的點名判不過。
  5. **自填等級不得低於原報**:載體帶 `finding_severities` 時,每個 id 自填的等級不得低於它所指各條原報的最高值(第 3 點有證據降級的除外)。
  - 原報宣告為 clean 的條(席位寫「已讀,無問題」)不需要被指到,也不提供任何放行空間。
  - 這一步不數數量、不用分母,所以 clean 行、重記報告、多席撞題都不會讓放行空間變大。
- **辯方降級**:沿用既有 `--refute-verdict id=evidence`(寫側已強制 evidence 的 id 必在 accepted)。本計劃只在處置閘多驗一件事:原報 major 經降級放行的 id,放行理由要附 file:line 佐證且找得到。不另開旗標。只有重現成功、只表達疑慮(concern)都不算降級。
- **放行理由與去向**:放行的 minor 理由除了既有的「至少 4 字含實字」,手冊要求寫明去向——不修的理由,或延後到哪個 Issue。機械只驗既有條件,去向靠人;但載體帳上的 `accept_reasons` 與 `finding_sources` 已足以事後列出「哪幾輪放行了哪些原報 minor、理由是什麼」,REVISIT 抽查就從帳上列。
- **嚴重度判準**(寫在審查席讀得到的地方:`skills/lumos-design-loop/templates.md` §3 代碼審派工詞的輸出格式那段;`skills/lumos-code-loop/SKILL.md` 第 4 步 severity 那一句後面接一句指向它;〈編排者判讀規則〉只留一句指針):
  - 測試抓不住錯:能指出一個具體、合理的改壞而測試照綠,而且被保護的是必要行為——合約或驗收條款、修補本身宣稱要擋的那個錯、或守衛類(程序清理、唯讀、權限、防誤刪)的唯一驗證 → major;是否有 `[test:]` 綁定只是佐證,不是必要條件。只是覆蓋面可以更完整、講不出具體改壞 → minor。
  - 第二種寫法:照架構對齊席既有的錨判(不在這份計劃改);其他席報的「重複 helper」若講不出具體行為或維護風險 → minor。
  - 文件不一致:照文件做會做出錯的操作、會讓測試或推送擋下、或跟合約衝突 → major;措辭、精度、過期的歷史數字 → minor。
- **舊裁定 d2**:實作同一個提交裡,用 `lumos decision-add` 在 [[Projects/probe輪退場_計劃]] 記一筆新決策取代 d2 的字面範圍(新範圍:代碼審原報 major 一律折,唯一例外是辯方 evidence 加可核對 file:line 的降級放行;原報 minor 經逐條指回後可放行;blocker 輪照舊全折),並用 `lumos set` 把 d2 標成被取代、指向新決策。這樣下一個會談不會拿 d2 把閘改回去。同篇開頭欄位的 KEY 行與 c4 敘述寫著舊範圍,一併改成指向新決策;`Verification/2026-08-25_probe輪退場與多席路由統一落地` 是當時的驗證紀錄,不改。
- **其他讀 `finding_severities` 的地方行為會變**(明寫,不另改程式):
  - 逃逸自動記按逐條嚴重度判,被放行的原報 minor 不會進逃逸帳;經辯方降級放行的原報 major 也不會。所以 RETIRE-IF 不拿逃逸帳當觸發。
  - 修正關卡的同類重複提醒:帶逐條嚴重度時,折入的 minor 不再被當成 major 觸發「要寫 prior」。這是放寬,手冊照實寫。
- **手冊與筆記同步**(全部要改到,S12 逐處核):
  - `skills/lumos-code-loop/SKILL.md` 第 4 步 severity 一句、第 7 步「code 迴圈輪內任一席 severity ≥ major 則 accepted 必空」與同步驟「架構對齊席與棧別檢核題…minor 可 accepted」那段;
  - `skills/lumos-code-loop/reference.md` 第 7 步重複版那一句,另新增一段:放行 minor 怎麼帶 `--finding-source`、去向怎麼寫、辯方降級怎麼記;
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 問閘那句;
  - [[Systems/design-loop]] 寫「code 迴圈輪級加嚴(major 席→accepted 必空,d2)」那一行;
  - [[Systems/convergence-evidence-gate]] 同句;
  - `scripts/lumos` 處置閘舊訊息保留原句(走舊規則時印),新步驟的訊息另寫;
  - `--refute-verdict` 原本寫「純記帳、不掛判閘」的地方,改成「記帳;代碼審 major 輪放行時處置閘會讀 evidence」:[[Systems/finding-refute]] 那三句(含「要動得走設計審」那句,回填本計劃)、`skills/lumos-design-loop/templates.md` 辯方範本那句、`scripts/lumos` 寫側那段註解。
  - 不改:散文設計審的 blocker 句(各處「輪內有 blocker 席,accepted 必須為空」照舊有效)。
- **與另一個會談的程式衝突**:它把處置閘入口抽成 `_disposal_judge`,但那只是轉呼叫 `_loop_status_disposal` 的入口;accepted 判斷仍在 `_loop_status_disposal` 的處置集合區塊,回放也直接呼叫 `_loop_status_disposal`。本計劃改的是處置集合區塊,新步驟接在 `_loop_status_disposal` 的步驟序列裡,不碰 `_disposal_judge`。實作排在它合併之後。
- **回放**:`loop replay` 跟 `loop status --disposal` 用同一支處置判定,新規則上線就套到回放。新規則只在載體帶 `finding_sources` 時生效,現有帳上沒有任何載體帶這個欄位,所以所有既有凍結判定的判定輪都走舊分支,判定不變;`_REPLAY_ENGINE_REV` 上線時不 bump(bump 會讓全部凍結判定變成過期、跳過重算)。附帶:凍結判定裡「判定輪有 major 席、accepted 非空」的只有兩份(`code-待決問題改存開頭欄位` r9、`code-審查跑滿回顧` r4,都判不過、載體都沒帶逐條欄位);`code-純文件子集` r3、`code-prose-conv-impl` r1 也有 major 輪放行,但都不是判定輪(判定輪分別是 r3b、r2);`code-規格閘半套` r1 曾在 major 輪帶逐條嚴重度放行兩條 minor,但它不是判定輪(判定輪 r3 accepted 為空),回放只判最後一輪,所以也不受影響。

## 驗收條款

- [S1] 當代碼審某輪有 major 席、載體帶 `finding_sources`、accepted 的每個 id 都指到原報 minor、每條原報 major 都指到 folded 的 id 時,處置閘 應 判過 [test:t_disposal_code_minor_release]
- [S2] 當同樣情況但某個 accepted 的 id 指到一條原報 major(沒有辯方 evidence)時,處置閘 應 判不過並點名那個 id [test:t_disposal_code_minor_release]
- [S3] 當報告裡有一條原報 major 沒有任何 id 指到(例如編排者把它和一條 minor 併成一個 id、只指到 minor 那條)時,處置閘 應 判不過並點名那份報告的第幾條 [test:t_disposal_code_minor_release]
- [S4] 當代碼審某輪有 major 席、accepted 非空、載體沒帶 `finding_sources` 時,處置閘 應 照舊判不過,訊息含「major 一律折」 [test:t_disposal_code_minor_release]
- [S5] 當輪內有 blocker 席、accepted 非空時,不論逐條來源,處置閘 應 照舊判不過 [test:t_disposal_code_minor_release]
- [S6] 當一條原報 major 被列進 refuted-set(因此不在發現清單、沒有 id 指到)、其餘原報 minor 全放行時,處置閘 應 判不過並點名那份報告的第幾條 [test:t_disposal_code_minor_release]
- [S7] 當指到原報 major 的 id 在 accepted、帶 `--refute-verdict id=evidence` 且放行理由附的 file:line 找得到時,處置閘 應 判過;同情況沒帶辯方表態、理由沒附 file:line、附的檔不存在、或行號超出檔長時 應 判不過(表態 agree/concern 卻放行,寫側本來就 rc 2,不在閘測) [test:t_disposal_code_minor_release]
- [S8] 當同一席同輪重記、新報告只剩 minor 而舊報告有 major 時,舊報告那條 major 沒被指到 應 判不過(重記不能洗掉原報 major) [test:t_disposal_code_minor_release]
- [S9] 當報告裡有多條 clean 宣告、編排者把一條原報 major 指成 clean 那條時,原報 major 沒被指到 應 判不過(clean 不提供放行空間) [test:t_disposal_code_minor_release]
- [S10] 當記載體筆帶 `--finding-source` 而 id 不在 findings-set、檔名不是同輪帳上的報告、或序號不是正整數時,`canary record` 應 以 rc 2 擋下 [test:t_canary_record_finding_source]
- [S13] 當 `finding_sources` 指到不在本輪帳上的報告、或序號超出那份報告的宣告數時,處置閘 應 判不過並點名 [test:t_disposal_code_minor_release]
- [S14] 當 accepted 裡有 id 不在 `finding_sources` 時,處置閘 應 判不過並點名那個 id [test:t_disposal_code_minor_release]
- [S15] 當載體自填的逐條嚴重度低於該 id 所指原報的最高值(沒有辯方降級)時,處置閘 應 判不過 [test:t_disposal_code_minor_release]
- [S16] 當本輪某份報告讀不到或 sha 跟帳上不符時,新步驟 應 判不過 [test:t_disposal_code_minor_release]
- [S11] 當用現有帳本對既有已凍結的迴圈跑 `loop replay` 時,判定 應 與改動前相同;`_REPLAY_ENGINE_REV` 應 不變 [test:t_disposal_code_minor_release]
- [S12] 當讀〈手冊與筆記同步〉列的各處時,三類爭議判準與新的處置規則 應 寫在上面、跟程式一致 [manual:SKILL.md 第 7 步、reference.md 第 7 步重複版、06 命令速查問閘句、Systems/design-loop 與 Systems/convergence-evidence-gate 那一行,這五處不再出現「major 席則 accepted 必空」且寫了新規則;templates.md §3 有三類判準;Systems/finding-refute 不再寫純記帳;scripts/lumos 舊訊息原句保留;散文設計審的 blocker 句不動]

測試造帳提醒(給實作者):同輪至少兩列帳(一列 major 席、一列載體),兩份報告內容不同、都已正規化;沿用 `t_panel_probe_retired` 的造帳方式(迴圈名 `code-` 開頭、帶 `--snapshot`/`--spec`/`--reviewed`)。

## 回退

- 處置閘:把第 ② 步那條改回「代碼審且任一席 ≥major → accepted 必空」,新步驟拿掉;`--finding-source` 旗標可以留著不用(帶了也不影響舊規則)。
- **回退時必須 bump `_REPLAY_ENGINE_REV`**:上線期間凍結的、在 major 輪放行過 minor 的判定(當時判過)在舊制下會判不過;不 bump 的話回放會把這次授權的制度改回誤報成「邏輯漂移」。bump 後回放把它們報成「制度已演進、跳過重算」,再逐一確認後重凍。
- d2:再用 `decision-add` 記一筆恢復。
- 文件:還原〈手冊與筆記同步〉列的各處。

## 實務隱患

已排除:金流:只改審查流程的判定與文件,不碰付款
已排除:對外送出:不連網、不寄送
已排除:不可逆:帳本只往後加,規則改回後新帳照舊判;沒有資料會被刪改
- 守衛面:處置閘是推送前的審查留痕依據,放寬會讓少修的輪也能過閘。防線:major 以上照舊必折;放行要逐條指回席報告原條,閘讀原報等級,每條原報 major 都必須指到已折入的 id(或有可核對反證的辯方降級);重現不到清單不能拿來消掉 major;舊帳回放判定不變(S11)。誤擋的逃生口:指錯條就改正 `--finding-source` 換新輪重記;沒有新增略過旗標。
- 天花板:序號指的是原報的哪一條,指錯成另一條原報 minor 時,原本那條原報 major 會沒人指,第 2 點就會擋;但若同一份報告裡原報等級本身就判錯(席位把 major 寫成 minor),這一層看不到——那是席報告品質,靠收貨判讀。辯方 evidence 是編排者記的,閘只驗 file:line 存在,不驗反證內容對不對。
- 放水風險:編排者可能把該修的原報 minor 都放行。去向寫明靠人;REVISIT 從帳上列出放行清單抽查。
- 量測:這個改動預期只讓修補縮小、折入條數變少;major 照舊必折,第三輪仍有 major 的比率不一定會降。帳本裡「這輪 minor 多、下一輪更容易有 major」看不出差別(判準證據席重算:minor 較多的 11 輪下一輪有 major 10 輪,major 較多的 49 輪是 43 輪)。

REVISIT:2026-11-14 從載體帳列出上線後放行原報 minor 的輪與理由,抽查是否其實該是 major、去向有沒有寫;另列出 `refute_verdicts` 為 evidence 且指到原報 major 的放行,逐條核對反證 file:line 是否真的推翻(這類不進逃逸帳,只能靠這裡回頭看);同時比上線前後「有 major 的輪下一輪仍有 major 的比率」與「跑滿三輪的比率」,交使用者裁留或撤

## 審計修正紀錄

- r1(2026-10-14,6 席同門 + 外家 Codex 1 席):防放水、降級、判準、舊帳、回放五組根因;六席報 major。結論:數量配平擋不住把 major 標成 minor(分子自填、分母可灌),整個換成逐條指回原報;降級清單撤掉、改用既有辯方表態;判準改放審查席讀得到的地方並不以綁定為前提;d2 正式取代;回退要 bump 回放版本;同步清單補齊。
- r1 折入後鏡像核對(便宜代理一席,只看本輪改動):13 條內部不一致全折——兩條條款寫側就記不進帳改寫成造得出的情境、補四條沒條款的規則、辯方降級放行納入 REVISIT 與退場條件、同步清單補辯方表態「純記帳」各處、lands_in 對齊。
- 卷證:`governance/review-reports/代碼審minor解綁/`
