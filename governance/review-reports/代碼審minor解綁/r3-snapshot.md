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
  - Systems/loop-convergence-recording
related:
  - "[[Projects/probe輪退場_計劃]]"
  - "[[Verification/2026-10-14_修補大小與下一輪major回放]]"
  - "[[Projects/改動與修補拆小_計劃]]"
---
# 代碼審minor解綁_計劃

代碼審的處置閘現在規定:輪內任一席 severity 是 major 以上,這輪的 accepted 必須是空的——不只 major 要折,連同輪的 minor 也一條都不准附理由放行。帳本上,同時有 major、恰一筆載體、載體標了逐條嚴重度的代碼審輪有 78 輪,176 條 minor 有 174 條被折入;這個比例是規則本身造成的(閘禁止放行,折入率必然接近全部),量的是規則不是編排者偏好。其中 23 輪含 blocker 席(29 條 minor,blocker 規則不動,改了也放不行),真正會受影響的是只含 major 的 55 輪、147 條 minor。另外,有 major 的代碼審輪共 461 輪,歷史上只有 78 輪(17%)的載體帶逐條嚴重度;新規則要編排者主動帶逐條來源(`--finding-source`)才生效,手冊把它寫成「major 輪要放行 minor 時的必要動作」,沒帶的照舊。「為了折一條 minor 新加了通道、下一輪因為新通道缺測試被判 major」在卷證裡有一個完整個案(`code-週評通知` r2→r3,這個迴圈沒標逐條嚴重度、不在上面 78 輪內),是單一個案、不是普遍規律。

這份計劃把連帶拿掉:原報 major 以上照舊一律折,原報 minor 可以附理由放行;放行的每一條都要指回席報告裡原本那一條,工具直接讀原報等級,不信編排者自填。並把「哪些問題算 major」寫進審查席讀得到的地方。

WHY:代碼審處置閘改成「放行的每條都必須指回席報告原條、原報等級是 minor;原報 major 的每一條都必須指到已折入的 id」,不再因同輪有 major 就禁止放行任何條 [出處:2026-10-14 使用者裁;[[Verification/2026-10-14_修補大小與下一輪major回放]];Codex 交叉診斷 `governance/review-reports/收斂診斷/codex-gpt-6-astra.md`;設計審 r1、r2 各七席 `governance/review-reports/代碼審minor解綁/`] [因:連帶規則讓 minor 修補進入當輪、修補膨脹又帶出新的驗證義務;d2 當初要補的是「major 可附理由放行」這個洞,本計劃原報 major 一律只能折,洞沒有重開] [不選:維持現制;把 major 也開放附理由放行(代碼審 major=會做出錯行為,必修);只改手冊不改閘;數量配平(r1 七席一致指出分子自填、分母可用 clean 行、重記報告、降級清單灌大);另開降級清單旗標(r1:跟既有辯方表態重複);辯方反證降級後放行原報 major(r2 五席報 major:閘只能驗佐證檔存在,貼任一存在的行號就能放行,等於零成本;佐證又不在凍結範圍,檔案改動後回放誤報漂移——要做另案裁);只限 minor 修補範圍、不動閘([[Projects/改動與修補拆小_計劃]] 已縮成提示,證據不足以單獨立案)]
PRIOR-ART: Google Engineering Practices 的審查標準把必要的改正與可選的細節(Nit)分開處理(https://google.github.io/eng-practices/review/reviewer/standard.html);本 repo 散文設計審早就允許 non-blocking 附理由接受([[Projects/設計審收斂重定義_計劃]] 決策 d1,內文稱 d5)。逐條嚴重度(`--finding-severity`,可重複旗標)、報告嚴重度解析(`_report_severities`,回傳報告裡每一行獨立 severity 宣告的出現序,圍欄內不算)、寫側讀同迴圈帳列(`--regression-set` 用 `_loop_records`)、留痕重驗(`_prov_check`)、獨立處置步驟(`_disposal_security_step` 等)、收貨端逐檔報告工具(`report-normalize`)都已存在;新旗標照 `--finding-severity` 的寫法,新步驟照既有獨立步驟的寫法,序號清單掛在 `report-normalize` 上,不另開指令。
RETIRE-IF: REVISIT 抽查時,放行的原報 minor 經人判定其實是 major 的累計 3 條;或上線後四週內帶 `--finding-source` 的 major 輪不到 3 輪(代表負擔太重、大家仍全折,改動形同沒做);或使用者回頭審放行理由覺得在放水——就照〈回退〉恢復舊規。

## 範圍

- 做:①處置閘代碼審輪級條件改成「逐條指回原報」;②載體新增可重複旗標 `--finding-source`,記帳當下完整核對、錯了不寫帳;③`report-normalize --items` 列出報告各條序號與等級並印範本;④派工範本代碼審席的嚴重度判準補三類常見爭議;⑤用 `lumos decision-add` 正式取代 d2 的字面範圍;⑥手冊與筆記同步。
- 不做:不改 blocker 規則(輪內有 blocker 照舊 accepted 必空);不開放任何形式的原報 major 放行(含辯方降級);不改散文設計審;不改三輪上限、必派席與架構對齊席的嚴重度錨(架構對齊「引入第二種做法或跨層直呼算 major」是使用者先前定的,要動另裁);不改「原始報告不可改」;不改 `--refute-verdict`(仍是純記帳);不開新的略過旗標。

## 做法

- **逐條來源**(`canary record` 載體筆新增可重複旗標 `--finding-source <id>=<報告路徑>#<序號>`,帳上欄位 `finding_sources: {id: ["報告路徑#序號", …]}`):
  - 報告路徑=跟帳上 `report_path` 同一套正規化的 repo 相對完整路徑(不用檔名,避免不同目錄同名);拆序號用最後一個 `#`。
  - 序號=那份報告經 `_report_severities` 解析出的宣告,去掉檔首那一行檔級宣告之後的第幾個(從 1 起;clean 宣告也佔序號,圍欄內的不算)。人不用手數,用 `report-normalize --items` 列。
  - 同一個 id 可以指多條(多席報了同一件事);同一條原報也可以被多個 id 指。同一個 `id=路徑#序號` 重複給視為一條。
  - `--finding-source` 加進「要跟 `--findings-set` 一起給」的旗標清單(單獨給就擋,不靜默忽略)。
  - `_GOV_FIELD_TYPES` 加 `finding_sources`(dict);`_gov_event_types_ok` 另寫一個分支驗「值是字串清單」(不能照抄進驗字串值的那個清單,會把合法值判錯)。
- **核對規則**(一支共用函式,寫側與處置閘都呼叫同一支;輸入是「本輪各列帳的報告」加載體帳列):
  1. **適用條件**:迴圈是代碼審(`code-` 開頭)、本輪有 major 席、沒有 blocker 席、accepted 非空、載體帶非空的 `finding_sources`(空 dict 視為沒帶)。不符就不走這裡(blocker 輪與沒帶的照舊判)。非代碼審迴圈帶 `--finding-source`,寫側 rc 2(散文設計審本來就能放行,不需要這條路)。
  2. **報告形狀**:本輪任一份報告檔級是 major,但去掉檔級行後沒有任何一條是 major → 這輪不能走逐條放行(這類報告的 major 寫在散文或標題裡,工具看不到,無從核對;真帳約兩成 major 席報告長這樣)。訊息指路:不帶 `--finding-source`、全折。
  3. **來源存在**:每個來源的路徑是本輪某列帳的報告、序號沒超出那份報告的宣告數。
  4. **原報 major 都折了**:每份報告的每一條原報 major,都至少被一個 id 指到,而且指到它的每個 id 都在 folded。沒被指到、或有任一個指到它的 id 在 accepted,點名判不過。
  5. **放行的都是原報 minor**:accepted 的每個 id 都必須有來源,所指各條至少一條是 minor、沒有任何一條是 major(只指 clean 條的不算數,點名判不過)。
  6. **自填等級不得低於原報**:載體帶 `finding_severities` 時,每個 id 自填的等級不得低於它所指各條的最高值。
  - 同一路徑多列帳(同一份報告記兩次)按路徑去重;沒帶報告的帳列跳過。
  - 重現不到清單(refuted-set)的 id 寫側規定不得在發現清單,所以被列進去的原報 major 一定沒人指,由第 4 點擋下。手冊寫明:這輪有原報 major 重現不到時,不能走逐條放行,照舊全折。席位在更正版報告裡撤回某條 major 時,舊報告那條照樣要被交代(指到一個折入的 id),或這輪不走逐條放行。
- **記帳當下就核對完**(`canary record` 載體筆帶 `--finding-source` 時):合法報告集合=本輪帳上已有各列的報告,加上這一筆自己的 `--report`;讀檔同寫側既有讀報告的方式。核對規則任何一條不過就 rc 2、不寫帳,所以指錯不會吃掉一輪。手冊規定代碼審載體最後記(程式註解早寫明這是代碼審慣例,這裡升格成這條路的必要條件)。
- **處置集合區塊(`_loop_status_disposal` 的「②處置集合重算」)**:現行「`code-` 迴圈、輪內有 major 席、accepted 非空 → 判不過」那一個分支改成:載體帶非空且型別正確的 `finding_sources` 時跳過這個分支、交給下面的新步驟判;沒帶、空的、型別壞掉的照舊判不過,訊息原句保留(含「major 一律折」,`t_panel_probe_retired` 斷言它)。blocker 分支不動。
- **處置閘新增獨立步驟 `_disposal_minor_release_step`**:對本輪全部帳列(含載體之後才記的)再跑一次同一支核對,防載體記完後又有席入帳、或帳被手改。
  - 讀報告:一次讀位元組、算 sha 跟帳上 `report_sha256` 比,再解碼(`errors="replace"`);讀不到或 sha 不符判不過。`finding_sources` 型別不對(不是 dict、值不是字串清單)判不過,不噴例外。
  - 接線照既有獨立步驟:不適用時印一行「—(原因)」並回 skip;失敗名稱加進 `fails`;加進成功橫幅的步驟清單;更新 `_loop_status_disposal` 的步驟說明;接在既有獨立步驟序列最後,不插進中間改動既有編號。訊息照既有「現象、為什麼在意、接下來怎麼做」三段。
  - 這一步只讀判定輪帳列的報告檔,這些檔本來就收在凍結閉包裡,回放能重算。
- **序號清單**(`report-normalize --items <報告…>`,唯讀):對每份報告印序號、等級、該條附近的標題或引句(截短),並標出「檔級 major 但各條沒有 major」的報告;最後印一段範本:每條原報 major 一行 `--finding-source <填 id>=<路徑>#<序號>`。載體記帳前就能對各席報告和載體自己的報告用。
- **放行理由與去向**:放行的 minor 理由除了既有的「至少 4 字含實字」,手冊要求寫明去向——不修的理由,或延後到哪個 Issue。機械只驗既有條件,去向靠人;載體帳上的 `accept_reasons` 與 `finding_sources` 足以事後列出「哪幾輪放行了哪些原報 minor、理由是什麼」,REVISIT 從帳上列。
- **嚴重度判準**(寫在審查席讀得到的地方:`skills/lumos-design-loop/templates.md` §3 代碼審派工詞的輸出格式那段;`skills/lumos-code-loop/SKILL.md` 第 4 步 severity 那一句後面接一句指向它;〈編排者判讀規則〉只留一句指針):
  - 測試抓不住錯:能指出一個具體、合理的改壞而測試照綠,而且被保護的是必要行為——合約或驗收條款、修補本身宣稱要擋的那個錯、或守衛類(程序清理、唯讀、權限、防誤刪)的唯一驗證 → major;有沒有 `[test:]` 綁定只是佐證,不是必要條件。只是覆蓋面可以更完整、講不出具體改壞 → minor。
  - 第二種寫法:照架構對齊席既有的錨判(不在這份計劃改);其他席報的「重複 helper」若講不出具體行為或維護風險 → minor。
  - 文件不一致:照文件做會做出錯的操作、會讓測試或推送擋下、或跟合約衝突 → major;措辭、精度、過期的歷史數字 → minor。
- **舊裁定 d2**:實作同一個提交裡,用 `lumos decision-add` 在 [[Projects/probe輪退場_計劃]] 記一筆新決策取代 d2 的字面範圍(新範圍:代碼審原報 major 一律折;原報 minor 經逐條指回後可放行;blocker 輪照舊全折),並用 `lumos set` 把 d2 標成被取代、指向新決策。同篇開頭欄位的 KEY 行與 c4 敘述寫著舊範圍,一併改成指向新決策;`Verification/2026-08-25_probe輪退場與多席路由統一落地` 是當時的驗證紀錄,不改。
- **其他讀帳的地方**:`--refute-verdict` 照舊純記帳,不受影響。真正會變的是跑滿提示(`_cap_hint`)的「累計折入」數:放行的 minor 不再算進折入,數字會比以前小,這是預期效果。逃逸自動記與修正關卡的同類重複提醒,本計劃不改程式,行為以程式為準,也不拿它們當量測依據。
- **手冊與筆記同步**(全部要改到,S12 逐處核):
  - `skills/lumos-code-loop/SKILL.md` 第 4 步 severity 一句、第 7 步「code 迴圈輪內任一席 severity ≥ major 則 accepted 必空」與同步驟「架構對齊席與棧別檢核題…minor 可 accepted」那段;
  - `skills/lumos-code-loop/reference.md` 第 7 步重複版那一句,另新增一段:怎麼用 `report-normalize --items` 拿序號(clean 也佔序號,跟「報了幾條」的口徑不同)、怎麼帶 `--finding-source`、載體最後記、去向怎麼寫、哪些情況不能走逐條放行(報告形狀不符、有原報 major 重現不到、席位更正版撤回 major 時舊報告那條仍要指到折入的 id)、閘端才失敗時怎麼辦、附一個完整範例;
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 問閘那句;
  - [[Systems/design-loop]] 寫「code 迴圈輪級加嚴(major 席→accepted 必空,d2)」那一行;
  - [[Systems/convergence-evidence-gate]] 頁頂 KEY 行與「落地實證」段兩處同義句;
  - [[Systems/loop-convergence-recording]] 記帳旗標與 `report-normalize` 的說明,補 `--finding-source` 與 `--items`;
  - `scripts/lumos` 處置閘舊訊息保留原句(走舊規則時印),新步驟的訊息另寫。
  - 不改:散文設計審的 blocker 句(各處「輪內有 blocker 席,accepted 必須為空」照舊有效)。
- **與另一個會談的程式衝突**(對方尚未合併,`_disposal_judge` 在目前主線查不到,以合併後的程式為準,實作前重新確認處置集合區塊位置):它把處置閘入口抽成 `_disposal_judge`,但那只是轉呼叫 `_loop_status_disposal` 的入口;accepted 判斷仍在 `_loop_status_disposal` 的處置集合區塊,回放也直接呼叫 `_loop_status_disposal`。本計劃改的是處置集合區塊,新步驟接在 `_loop_status_disposal` 的步驟序列裡,不碰 `_disposal_judge`。實作排在它合併之後。
- **回放**:`loop replay` 跟 `loop status --disposal` 用同一支處置判定,新規則上線就套到回放。新規則只在載體帶 `finding_sources` 時生效,現有帳上沒有任何載體帶這個欄位,所以所有既有凍結判定都走舊分支,判定不變。`_REPLAY_ENGINE_REV` 旁的慣例是「判定語意改版就 bump」,這次刻意不 bump:舊輸入的判定不變,bump 只會讓全部凍結判定變成過期、跳過重算,反而失去回放保護。新步驟只讀凍結閉包裡的報告檔,上線後新凍結的判定也能重算。附帶:凍結判定裡「判定輪有 major 席、accepted 非空」的只有兩份(`code-待決問題改存開頭欄位` r9、`code-審查跑滿回顧` r4,都判不過、載體都沒帶逐條欄位);`code-純文件子集` r3、`code-prose-conv-impl` r1、`code-規格閘半套` r1 也有 major 輪放行,但都不是判定輪。

## 驗收條款

- [S1] 當代碼審某輪有 major 席、載體帶 `finding_sources`、accepted 的每個 id 都指到原報 minor、每條原報 major 都只被 folded 的 id 指到時,處置閘 應 判過 [test:t_disposal_code_minor_release]
- [S2] 當同樣情況但某個 accepted 的 id 也指到一條原報 major 時,載體記帳 應 以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過並點名那個 id [test:t_disposal_code_minor_release]
- [S3] 當報告裡有一條原報 major 沒有任何 id 指到(例如編排者把它和一條 minor 併成一個 id、只指到 minor 那條)時,載體記帳 應 以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過並點名那份報告的第幾條 [test:t_disposal_code_minor_release]
- [S4] 當代碼審某輪有 major 席、accepted 非空、載體沒帶 `finding_sources` 時,處置閘 應 照舊判不過,訊息含「major 一律折」 [test:t_disposal_code_minor_release]
- [S5] 當輪內有 blocker 席、accepted 非空時,不論逐條來源,處置閘 應 照舊判不過 [test:t_disposal_code_minor_release]
- [S6] 當一條原報 major 被列進 refuted-set(因此不在發現清單、沒有 id 指到)、其餘原報 minor 全放行時,載體記帳 應 以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過並點名那份報告的第幾條 [test:t_disposal_code_minor_release]
- [S7] 當本輪有一份報告檔級是 major、但各條宣告裡沒有 major 時,帶 `finding_sources` 的載體 應 在記帳時以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過;兩邊訊息都指路「不帶逐條來源、全折」 [test:t_disposal_code_minor_release]
- [S8] 當同一席同輪重記、新報告只剩 minor 而舊報告有 major 時,舊報告那條 major 沒被指到 應 判不過(重記不能洗掉原報 major) [test:t_disposal_code_minor_release]
- [S9] 當 accepted 的某個 id 只指到 clean 條時,載體記帳 應 以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過並點名那個 id [test:t_disposal_code_minor_release]
- [S10] 當載體帶 `--finding-source` 而 id 不在 findings-set、路徑不是本輪帳上或本筆 `--report` 的報告、序號不是正整數或超出宣告數、或沒帶 `--findings-set` 時,`canary record` 應 以 rc 2 擋下且不寫帳;指向本筆自己 `--report` 的來源 應 收 [test:t_canary_record_finding_source]
- [S11] 當載體記帳時核對規則第 4、5 點不過(原報 major 沒指到、或放行的 id 指到原報 major)時,`canary record` 應 以 rc 2 擋下且帳本行數不變 [test:t_canary_record_finding_source]
- [S12] 當讀〈手冊與筆記同步〉列的各處時,三類爭議判準與新的處置規則 應 寫在上面、跟程式一致 [manual:按語意逐處核,不綁字串:SKILL.md 第 4 步有指向判準的一句、第 7 步兩段改成新規則;reference.md 第 7 步重複版改成新規則且新增段落含完整範例與更正版、閘端失敗兩種情況;06 命令速查問閘句;Systems/design-loop 那一行;Systems/convergence-evidence-gate 兩處;Systems/loop-convergence-recording 補新旗標與 --items;Projects/probe輪退場_計劃 的 d2 已被新決策取代、KEY 行與 c4 指向新決策;templates.md §3 有三類判準;scripts/lumos 舊訊息原句保留;散文設計審的 blocker 句不動]
- [S13] 當不同目錄有同名報告、一份第 1 條是 major(折入)、另一份第 1 條是 minor(放行)時,用完整路徑指的來源 應 各自對到正確那份,處置閘判過 [test:t_disposal_code_minor_release]
- [S14] 當載體記完後同輪又有一席入帳、它的報告有 major 沒被指到時,處置閘 應 判不過並點名 [test:t_disposal_code_minor_release]
- [S15] 當載體自填的逐條嚴重度低於該 id 所指原報的最高值時,載體記帳 應 以 rc 2 擋下且帳本不變;同樣的帳列直接寫進帳本時,處置閘 應 判不過 [test:t_disposal_code_minor_release]
- [S16] 當本輪某份報告讀不到、sha 跟帳上不符、或帳上 `finding_sources` 型別壞掉時,新步驟 應 判不過且不噴例外 [test:t_disposal_code_minor_release]
- [S17] 當用造好的假帳(major 輪、accepted 非空、沒帶 `finding_sources`)凍結後重新回放時,判定 應 跟凍結時相同;帶 `finding_sources` 判過的假帳凍結後回放 應 也相同 [test:t_disposal_code_minor_release]
- [S18] 當對一份含 clean 條、圍欄內示範行與檔級行的報告跑 `report-normalize --items` 時,印出的序號 應 跟 `_report_severities` 去掉檔級行後的順序一致,並為每條 major 印一行範本;檔級 major 而各條沒有 major 的報告 應 被標出 [test:t_report_normalize_items]
- [S19] 當 `canary record` 帶合法的 `--finding-source` 寫入後跑 `lumos gov` 時,那一列 應 照常出現(`finding_sources` 的字串清單值不被判成型別錯誤) [test:t_canary_record_finding_source]

- [S20] 當同一個 `id=路徑#序號` 重複給、或兩個 id 指同一條原報 minor 都放行時,核對 應 視為合法(去重不重複計,多 id 指同條不擋) [test:t_disposal_code_minor_release]
- [S21] 當同一份報告在本輪記了兩列帳、或本輪有一列帳沒帶報告時,核對 應 按路徑只讀一次、跳過沒報告的列,判定跟只記一列相同 [test:t_disposal_code_minor_release]
- [S22] 當帳本裡載體的 `finding_sources` 指到本輪帳上沒有的報告、或序號超出宣告數(手改帳)時,處置閘 應 判不過並點名 [test:t_disposal_code_minor_release]
- [S23] 當治理帳裡某列的 `finding_sources` 值是字串而不是字串清單時,`lumos gov` 應 判成型別錯誤;值是字串清單時 應 照常收 [test:t_canary_record_finding_source]

測試造帳提醒(給實作者):同輪至少兩列帳(一列 major 席、一列載體),兩份報告內容不同、都已正規化;沿用 `t_panel_probe_retired` 的造帳方式(迴圈名 `code-` 開頭、帶 `--snapshot`/`--spec`/`--reviewed`)。寫側會擋的情境(S2、S3、S6、S7、S9、S15 的閘端那一半、S22)用手寫帳列直接附進帳本造;寫側那一半走 `canary record` 驗 rc 2 且帳本行數不變。回放條款用造好的假帳,不用真帳本(真帳會長大)。

## 回退

- 處置閘:還原 `_loop_status_disposal`「②處置集合重算」裡那個 `code-` major 分支(不再看 `finding_sources`),新步驟拿掉。寫側對 `--finding-source` 改成 rc 2 並指路「此路已停用,照舊全折」,免得記帳成功、問閘才發現不能放行;`--items` 可以留著(唯讀)。
- **回退時必須 bump `_REPLAY_ENGINE_REV`**:上線期間凍結的、在 major 輪放行過 minor 的判定(當時判過)在舊制下會判不過;不 bump 的話回放會把這次授權的制度改回誤報成「邏輯漂移」。bump 後回放把它們報成「制度已演進、跳過重算」,再逐一確認後重凍。S17 屆時跟著改。
- d2:再用 `decision-add` 記一筆恢復。
- 文件:還原〈手冊與筆記同步〉列的各處。

## 實務隱患

已排除:金流:只改審查流程的判定與文件,不碰付款
已排除:對外送出:不連網、不寄送
已排除:不可逆:帳本只往後加,規則改回後新帳照舊判;沒有資料會被刪改
- 守衛面:處置閘是推送前的審查留痕依據,放寬會讓少修的輪也能過閘。防線:原報 major 一律只能折;放行要逐條指回席報告原條,工具讀原報等級;每條原報 major 都必須只被折入的 id 指到;工具看不到逐條 major 的報告形狀整輪不能走這條路;重現不到清單不能拿來消掉 major;舊帳回放判定不變(S17)。誤擋的逃生口:記帳當下就擋、不寫帳,改正 `--finding-source` 重新記同一輪即可。載體記進去之後才在閘端失敗(載體之後又有席入帳、報告被改、sha 不符):一輪只能有一筆載體,不能重記,這輪就照舊全折——開下一輪時不帶 `--finding-source`;會多用一輪,手冊寫明「載體最後記」就是為了避開這種情況。沒有新增略過旗標。
- 天花板:來源是編排者指的。它擋得住「把 major 標成 minor」(工具讀原報等級)和「指錯一條」(真正那條 major 會沒人指),但擋不住編排者刻意把某件 major 的實際問題掛在另一條原報 minor 的 id 下放行、同時把原報 major 指到一個不相干的折入 id——那要明確造假兩處對應,帳上留得下來,靠 REVISIT 抽查。席報告在記帳前被改等級(改證據)也看不到,靠既有「席報告從逐字稿存」紀律。
- 放水風險:編排者可能把該修的原報 minor 都放行。去向寫明靠人;REVISIT 從帳上列出放行清單抽查。
- 負擔:放行任何 minor 都要替同輪每條原報 major 寫一個來源(真帳的 major 輪 2 到 18 條),靠 `--items` 印範本減輕;負擔仍太重、大家照舊全折,RETIRE-IF 的使用量條件會抓到。
- 量測:這個改動預期只讓修補縮小、折入條數變少;原報 major 照舊必折,第三輪仍有 major 的比率不一定會降。帳本裡「這輪 minor 多、下一輪更容易有 major」看不出差別(r1 判準證據席重算:minor 較多的 11 輪下一輪有 major 10 輪,major 較多的 49 輪是 43 輪)。

REVISIT:2026-11-14 若屆時上線未滿 28 天(實作排在另一會談合併之後,上線日未定),把這個日期改成上線日加 28 天;到期時從載體帳列出上線後 major 輪中帶 `finding_sources` 的輪數與比例(不到 3 輪即觸發 RETIRE-IF)、放行原報 minor 的輪與理由,抽查是否其實該是 major、去向有沒有寫;同時比上線前後「有 major 的輪下一輪仍有 major 的比率」與「跑滿三輪的比率」,交使用者裁留或撤

## 審計修正紀錄

- r1(2026-10-14,6 席同門 + 外家 Codex 1 席):防放水、降級、判準、舊帳、回放五組根因;六席報 major。結論:數量配平擋不住把 major 標成 minor(分子自填、分母可灌),整個換成逐條指回原報;降級清單撤掉、改用既有辯方表態(r2 已撤:原報 major 只能折);判準改放審查席讀得到的地方並不以綁定為前提;d2 正式取代;回退要 bump 回放版本;同步清單補齊。
- r1 折入後鏡像核對(便宜代理一席,只看本輪改動):13 條內部不一致全折——兩條條款寫側就記不進帳改寫成造得出的情境、補四條沒條款的規則、辯方降級放行納入 REVISIT 與退場條件、同步清單補辯方表態「純記帳」各處(這兩項 r2 隨降級路一起撤)、lands_in 對齊。
- r2(2026-10-14,6 席同門 + 外家 Codex 1 席):七席全報 major,blocking 共 18 條,歸成五組根因。結論:辯方降級放行原報 major 整條拿掉(只驗佐證檔存在等於零成本放行,佐證又不在凍結範圍會讓回放誤報漂移);核對改在載體記帳當下完整做、錯了不寫帳(手冊規定載體最後記,閘再核一次);來源改用完整路徑;檔首 major 而各條沒有 major 的報告整輪不能走新路;`report-normalize --items` 列出序號並預填範本,減少手數。
- r2 折入後鏡像核對(便宜代理一席):11 條全折——補處置集合區塊怎麼讓路、限定代碼審、寫側會擋的條款拆成寫側與閘端兩半、補 S20–S23、同步清單與 S12 改成按語意逐處核、閘端失敗的出路、REVISIT 跟上線日掛鉤、回退時寫側停用旗標。
- 卷證:`governance/review-reports/代碼審minor解綁/`
