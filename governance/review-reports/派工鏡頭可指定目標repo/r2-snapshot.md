---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/guards-gates
  - risk/守衛面
lands_in:
  - Systems/codex-harness
  - Systems/hook信任邊界
related:
  - "[[Projects/派工鏡頭跨repo不再靜默_計劃]]"
---
# 派工鏡頭可指定目標repo_計劃

> 白話:派審查席時,掛鉤會自動把「這次改動牽連到的圖譜筆記」貼進派工詞。它一律在「會談開在哪個資料夾」那裡算。可是做事常常在別的工作樹、甚至別的 repo:會談開在 A,要審的計劃或提交在 B,掛鉤在 A 找不到,只附一行「沒附」。改成:派工詞可以多寫一行 `LUMOS-REPO: <絕對路徑>` 指定去哪裡算;路徑要通過跟掛鉤挑 lumos 執行檔同一套的信任檢查,不合就附說明、不去跑。

## 緣起

- 2026-10-13 後端示範:會談開在 lumos 工具鏈,審的是示範 repo `order-demo` 的分支,派工鏡頭算不出牽連筆記(只附了說明行)。2026-10-14 夜裡更普遍:全域規則要求每個工作開獨立的 git 工作樹,我在三個工作樹各開一份計劃、派了十幾席設計審,計劃只存在那些工作樹裡,掛鉤在會談目錄找不到,所有席都沒拿到固定席節點。出處:使用者 2026-10-14 列的示範改進第 4 條;當晚的席報告都寫「派工尾端沒有附固定席節點」。
- 舊裁定:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行寫「不選:標記行加 repo 路徑讓掛鉤改去那裡算(標記行文法要改、派工詞的自由文字會變成掛鉤去跑 git 的路徑,先不開這個口;說明行給繞法即可)」。本計劃推翻這一條(使用者 2026-10-14 授權全權裁量)。回應:
  - 「說明行給繞法」的繞法是「從開在目標專案的會談派席」。全域規則要求每個工作開獨立工作樹,於是會談目錄跟工作目錄錯開成了常態,繞法等於每份工作都要另開一個會談——實際上沒人照做,當晚十幾席全部沒附。
  - 「自由文字變成跑 git 的路徑」:在一個 repo 裡跑 git 的風險,是那個 repo 的 `.git/config`(例如 `core.fsmonitor`)可以讓 git 執行任意指令。現況是:掛鉤把會談目錄(環境變數或事件裡的工作目錄)原樣交給 lumos,會談目錄沒有任何檢查。新路徑的差別是「來源從環境變成派工詞,派工詞可能被注入」;所以只認登記過的地方(做法 2:會談 repo 自己的工作樹、使用者裝過 lumos 的專案),派工詞指到其他任何地方都只會被拒,一次 git 都不跑。
  - 「標記行文法要改」:不改 `LUMOS-IMPACT:` 與 `LUMOS-SPEC:` 的文法,另加一行獨立標記,兩種標記都吃它。

PRIOR-ART: `lumos dispatch-lens` 本來就收 `--repo <repo 內任一路徑>`(用 `git -C <路徑> rev-parse --show-toplevel` 找根),`--spec` 的相對路徑對找到的根解析、絕對路徑要在那個 repo 裡;掛鉤只是一律傳會談目錄。本計劃只改掛鉤傳什麼。信任改用登記(做法 2):會談 repo 的工作樹照專案裡 `_events_main_trusted` 讀 `worktrees/*/gitdir` 的寫法列出,裝過 lumos 的專案由 `lumos init`/`update` 記進使用者層的清單;不另寫權限位元檢查(r1 兩席實測那套擋不住 `commondir` 與權限放寬的設定檔)。
RETIRE-IF: Claude Code 在派工事件帶出子代理的工作目錄(會談目錄與工作目錄不再可能錯開),或連續 8 週派工詞裡的 `LUMOS-REPO:` 都等於會談目錄——拿掉這一行標記。
REVISIT:2026-12-15 數一次掛鉤事件裡帶 `LUMOS-REPO:` 且通過檢查的次數與被拒的次數,照 RETIRE-IF 判。

## 做法

1. **新標記** `LUMOS-REPO: <絕對路徑>`:單獨一行,正規式 `^LUMOS-REPO:\s*(.+?)\s*$`(路徑可以有空白),跟 `LUMOS-IMPACT:` 或 `LUMOS-SPEC:` 同一份派工詞才有作用(兩個都有時跟現在一樣以 `LUMOS-IMPACT:` 為準,`LUMOS-REPO:` 對它生效)。
   - **只看圍欄與引用塊以外的行**:派工詞常貼進計劃或範本全文,裡面的範例行不算(圍欄 ``` 裡的行、`>` 開頭的行都略過)。
   - **同一個值出現多次算一次**;出現兩個不同的值,原因 `repo_duplicate`,不算、只附說明。
   - **寫歪也不退回**:一行裡出現 `LUMOS-REPO` 字樣卻不合上面的格式(全形冒號、前面有 `- `、整行包在反引號裡、冒號後沒有路徑),原因 `repo_malformed`,不算、只附說明——不能因為寫歪就落回會談目錄、附上錯的樹(r1 邊界席)。
2. **信任靠登記,不靠權限位元**:路徑要在「允許清單」裡才去那裡算。允許清單是兩樣的聯集:
   - **會談 repo 自己的工作樹**:讀會談 repo 的 git 共用資料夾底下 `worktrees/*/gitdir` 檔(每個工作樹一個,專案裡 `_events_main_trusted` 已經這樣讀,照它的寫法:相對路徑以那個檔所在的資料夾為基準)加上主工作樹本身。不在目標路徑跑任何 git。
   - **登記過的 lumos 專案**:`lumos init`、`lumos update` 與 `install.sh` 跑完時,把那個專案的根(realpath)追加進使用者層的 `~/.config/lumos/projects.txt`(一行一個、去重)。這些是使用者自己裝過 lumos 的專案。
   - 比對用 `os.path.samefile`(大小寫、Unicode 正規化寫法不同都對得上);路徑讀不到、含 NUL、比對丟例外,一律當成不在清單。
   - 不在清單:原因 `repo_not_registered`,說明行附一句怎麼登記(在那個專案跑一次 `lumos update`),一次 git 都不在那裡跑。
   - 清單檔本身要屬於目前使用者、不是 group/other 可寫(檔與它的資料夾,仿 `_trusted_lumos` 的 `_ok`,另寫在新函式裡、不改那段逐字複本);不合就當清單是空的。
   - **為什麼不用權限位元**:r1 正確性席與邊界席實測,檢查資料夾權限擋不住 `.git` 資料夾裡的 `commondir` 指到別人可寫的地方(實測真的執行了任意指令)、擋不住資料夾裡權限放寬的設定檔,而且在 Linux 的 `/tmp` 底下會把每個合法 repo 都誤殺;更根本的是,自己擁有、從沒打開過的下載 repo 也過得了。登記制回答的是「這是不是使用者自己在用的 lumos 專案」,這正是要問的。
3. **過了**:`dispatch-lens` 的 `--repo` 傳清單裡對到的那個路徑(realpath),其餘照舊。設計審的 `LUMOS-SPEC:` 相對路徑照舊以 repo 根為基準。附加段開頭多印一行來源「這段牽連節點在 <repo 路徑,消毒後> 算出」,讓審查席核對得到用的是哪個 repo(成功時也看得出來,r1 正確性席)。
4. **沒過**:不改去那裡算,也不退回會談目錄算;但仍用會談目錄叫一次 lumos 只取角色卡與架構段(它們不看圖譜,現在圖譜段失敗時也照附——不能因為標記被拒就少附,r1 邊界席)。派工詞附一行 `LUMOS-LENS:` 說明,原因代碼是掛鉤自己的四個(`repo_not_absolute`、`repo_not_registered`、`repo_duplicate`、`repo_malformed`,每個一句固定話),放在掛鉤自己的字彙表,跟 lumos 印的失敗代碼表分開;路徑經 `_clean_field` 消毒後顯示。
5. **沒寫**:照舊用會談目錄。範圍或計劃在會談目錄算不出來時,說明行的繞法加一條「派工詞加一行 `LUMOS-REPO: <目標 repo 的絕對路徑>`」。
   - **設計審那條路也要有說明行**:現在 `dispatch-lens --spec` 失敗(計劃不存在、不在那個 repo 裡、沒有圖譜)時不印失敗代碼,掛鉤的說明行也只給代碼審範圍那條路用,所以設計審算不出來時派工詞什麼都沒附——今晚十幾席就是這樣。lumos 端替這三種加固定代碼 `spec_missing`、`spec_outside_repo`、`no_knowledge`(進既有的失敗代碼表,`_dispatch_lens_fail` 說明裡的「六種」跟著改),掛鉤的說明行拿掉「只在有範圍時」的條件,計劃路徑經 `_clean_field` 消毒,另寫一句計劃版的說明;`_fail_note` 多一個參數表示 repo 是不是來自標記。新掛鉤配舊 lumos 時,設計審失敗照舊不印說明(舊 lumos 不給代碼),這是過渡期的已知行為。
   - **說明行的措辭分兩版**:沒帶 `LUMOS-REPO:` 時照現在寫「在會談專案 … 算不出來」並給加 `LUMOS-REPO:` 的繞法;帶了而且通過、lumos 在目標 repo 又失敗時,寫「在指定的 repo … 算不出來」,繞法不再叫人「從開在目標專案的會談派席」。
6. **預算**:讀登記清單與工作樹清單都是讀檔,不跑子行程;放在掛鉤開始計時之後(先起算內層預算再做這些),所以時間會從後面 lumos 那次呼叫的預算裡扣掉,不會讓總時間超過外層上限。掛鉤自己不再跑 `git rev-parse`(找根交給 lumos 的 `--repo`,它本來就會算)。
7. **記帳**:掛鉤事件只有 ok/timeout/error 三種與一個 note 欄;這裡用 note 記固定字首:通過記 `repo_marker pass same_as_session=0|1`,被拒記 `repo_marker reject <代碼>`(被拒時事件 kind 用 `ok`,不跟真正的錯誤混在一起)。這是對 [[Projects/派工鏡頭注入_計劃]]「不擋不驗不記不量」的有限鬆綁——只記這一個標記的結果,不記注入次數;理由是 RETIRE-IF 要量。
8. **範本與手冊**:編排者看不到會談目錄是哪裡,所以範本不寫成條件句,一律寫「派工詞照抄一行 `LUMOS-REPO: <你這份工作所在的 repo 根的絕對路徑>`」(會談目錄本身也在允許清單裡,寫了不會壞),並標明只對 Claude 編排有效(Codex 編排見第 9 點)。要改的地方:`skills/lumos-design-loop/templates.md` 講 `LUMOS-SPEC:`、`LUMOS-IMPACT:`、終點寫完整提交編號、「從開在目標專案的會談派席」的那幾段;`skills/lumos-design-loop/SKILL.md` 與 `reference.md` 講派工鏡頭的段落;`skills/lumos-code-loop/SKILL.md`(「掛鉤在會談的專案目錄解讀」那句)與 `reference.md`;`skills/lumos-project-notes/commands/05-設計審查迴圈.md`、`06-代碼審與推送.md` 講派工鏡頭的列、`reference.md` 講派工鏡頭的那處;[[Systems/design-loop]] 講派工鏡頭的那句;掛鉤自己的 `FAIL_NOTE` 與檔頭說明。
9. **Codex 編排不在本計劃範圍**:`--arm` 的武裝檔以目標 repo 根為鍵,子代理開場認領時查的是 Codex 會談目錄的根,兩者不同就領不到;Codex 的開場事件也讀不到派工詞裡的 `LUMOS-REPO:`。要支援得另案讓認領找得到別的根,手冊不寫「`--arm --repo` 可跨 repo」。
10. **舊裁定只作廢被推翻的那一格**:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行主決策(算不出範圍時附說明行)、消毒設計、「不轉述錯誤原文」都還有效,本計劃沿用;只有「不選:標記行加 repo 路徑…」那一格被推翻。做法:把那一格拆成獨立一行 `WHY:` 再標 `[status:superseded]`、`[被取代:Projects/派工鏡頭可指定目標repo_計劃]`,原行保留;它〈範圍〉裡「不做:讓標記行指定 repo」那一句旁加註被本計劃取代。[[Systems/codex-harness]] 的 WHY 沒有被推翻的那一格,不標作廢,只把它列舉的失敗代碼補上新增的三個。用 lumos 的指令改開頭欄位,正文用 Edit。
11. **版本錯開看得出來**:成功時附加段開頭那一行來源(做法 3)只有新掛鉤會印,範本寫明「附加段沒有來源那一行,代表裝的掛鉤是舊版,在任一 lumos 專案跑一次 `lumos update`(會同步 `~/.claude/hooks/`)」;手冊同一處寫明更新後要重跑。
12. **lumos 的 git 呼叫多一道保險**:`_lens_git` 一律帶 `-c core.fsmonitor=false`(派工鏡頭只讀歷史,用不到 fsmonitor);即使登記清單裡的專案設定被改,讀取時也不會因此執行指令。

## 驗收條款

- [S1] 當派工詞有 `LUMOS-SPEC: docs/x-knowledge/Projects/a_計劃.md` 與 `LUMOS-REPO: <會談 repo 的另一個工作樹>`,而那份計劃只存在那個工作樹時,掛鉤應在那個工作樹算、附上固定席節點,附加段開頭應印來源那一行。[test: t_dispatch_lens_hook_repo_marker]
- [S2] 當 `LUMOS-REPO:` 指到另一個登記過的 lumos 專案時,應在那裡算;指到一個沒登記、也不是會談 repo 工作樹的 repo(包含自己擁有的),應附 `repo_not_registered` 的說明,不在那裡、也不在會談目錄算。[test: t_dispatch_lens_hook_repo_rejected]
- [S3] 當路徑沒登記時,掛鉤與 lumos 都應一次 git 都不在那裡跑(假的 `subprocess.run` 依命令分派並記錄每次呼叫的參數與工作目錄)。[test: t_dispatch_lens_hook_repo_no_git_on_untrusted]
- [S4] 當派工詞沒有 `LUMOS-REPO:` 時,行為應與現在相同;範圍在會談目錄算不出來時,說明行應多一條加 `LUMOS-REPO:` 的繞法。[test: t_dispatch_lens_hook_fail_reason_notice]
- [S5] 同一份派工詞有兩個不同值的 `LUMOS-REPO:` 時應附 `repo_duplicate`、同值出現兩次應照常算;圍欄或引用塊裡的 `LUMOS-REPO:` 範例行不應算;路徑含空白應照常認得;`- LUMOS-REPO: …`、全形冒號這類寫歪的應附 `repo_malformed`,不應退回會談目錄算。[test: t_dispatch_lens_hook_repo_marker_grammar]
- [S6] 設計審的計劃在指定的(或會談的)repo 找不到、不在那個 repo 裡、或那個 repo 沒有圖譜時,掛鉤應附一行帶 `spec_missing`、`spec_outside_repo`、`no_knowledge` 的說明。[test: t_dispatch_lens_hook_spec_fail_notice]
- [S7] `lumos init`、`lumos update` 跑完後,`~/.config/lumos/projects.txt` 應有那個專案的根(去重);清單檔是 group 可寫時應當成空的。[test: t_lumos_update_registers_project]
- [S8] 標記被拒時,有 `LUMOS-ROLE-CARDS: on` 的派工詞應照附角色卡。[test: t_dispatch_lens_hook_repo_rejected_keeps_cards]
- [S9] 通過與被拒時,掛鉤事件的 note 應分別是 `repo_marker pass same_as_session=…` 與 `repo_marker reject <代碼>`。[test: t_dispatch_lens_hook_repo_marker_event]

- 測試怎麼搭:測試把 `HOME` 指到暫存資料夾(登記清單寫在那裡),暫存 repo 放在測試自己建的 0700 資料夾底下;假的 `subprocess.run` 依 `argv` 分派(lumos 那次回 JSON、其他記錄下來),不再用一支回同一個物件的假函式。S1 用 `git worktree add` 造工作樹。

## 實務隱患

- 守衛面:掛鉤會改寫子代理的派工詞,也是錨點清單裡的檔。風險一是讓 lumos 去不可信的目錄跑 git:做法 2 只認會談 repo 的工作樹與使用者自己裝過 lumos 的專案,下載來、從沒用過的 repo 不在清單上,派工詞被注入一行指過去也只會被拒;清單裡的專案被改了設定,做法 12 讓派工鏡頭的 git 呼叫不跑 fsmonitor。剩下的是「使用者自己裝過 lumos 的專案被改成惡意設定」,那跟使用者在那個專案裡平常敲 git 是同一個風險,單人使用的威脅模型下接受。登記之後到實際跑之間路徑被換掉(先查後用的空隙)同樣在威脅模型外;風險二是指錯 repo 時附上錯的節點,讓審查席以為那些就是牽連範圍——路徑必須是 lumos 專案的根,而且指錯時附上的節點會跟審材明顯對不上,席位照範本本來就要逐條判。
- 已排除:金流:不碰。
- 已排除:對外送出:只在本機跑 git 與 lumos。
- 已排除:不可逆:還原提交即回到只用會談目錄;派工詞多出的那一行舊掛鉤不認,照舊忽略。
- 改了錨點清單裡的掛鉤與測試檔,提交前要 `lumos anchor approve`。

## 回退

照順序:
1. 還原程式、掛鉤、範本與手冊的提交(範本與掛鉤一起退,免得範本還叫人寫 `LUMOS-REPO:`、掛鉤卻不認)。
2. 把做法 10 標作廢的那一格與〈範圍〉旁的註記改回(不然舊裁定會顯示被一個已撤回的計劃取代)。
3. 每個消費專案跑 `lumos update`,再 `lumos anchor approve --note "<為什麼>"` 並提交簽名檔;最後一個跑 update 的專案會把它的掛鉤寫進 `~/.claude/hooks/`,所以要等每個專案都更新過,並核對 `~/.claude/hooks/dispatch-lens-hook.py` 的指紋跟還原後的版本相同。
4. 還有派工詞帶著 `LUMOS-REPO:` 的進行中迴圈:舊掛鉤看不懂這一行,會在會談目錄算、而且不附來源那一行——照做法 11 的說法,看到附加段沒有來源行就當成沒附,手動 `lumos impact --diff` 貼固定席。
5. `~/.config/lumos/projects.txt` 留著無害(舊版不讀它),要清可以刪。

## 審計修正紀錄

- r1 前掃(2026-10-14):9 條(語意命中 5、③ 2、② 1、存在命中 1)直接修進本文:Codex 跨 repo 認領領不到,改寫成不做;重複標記的處理前後矛盾,統一成不算;信任檢查要先讀 `.git` 檔、不能先跑 git,另寫資料夾版不改逐字複本;更正「跟會談目錄受到的保護相同」(會談目錄現在沒有檢查);設計審失敗沒有說明行,補三個代碼;原因代碼拆成六個並與 lumos 的表分開;舊裁定兩處加會談 codex-harness 標作廢;路徑可以有空白。前掃紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r1-intake.md`。
- r1(2026-10-14,6 席):32 條/blocking 11/信任靠權限位元擋不住 `.git` 裡的 `commondir`、權限放寬的設定檔、從沒用過的下載 repo,又會在 `/tmp` 底下誤殺;標記寫歪會退回會談目錄附上錯的樹;成功時看不出用的是哪個 repo;被拒時連角色卡一起丟;記帳量不到撤除條件;舊裁定照字面作廢會把還有效的決策一起作廢;回退「無害」不成立;全數折入:改成登記制(會談 repo 的工作樹加裝過 lumos 的專案)、寫歪與重複都不算也不退回、成功印來源行、被拒照附角色卡、掛鉤自己不再跑 git、事件 note 固定字首、只作廢被推翻的那一格、手冊要改的地方列全、回退改成清單。席報告在 `governance/review-reports/派工鏡頭可指定目標repo/`。
