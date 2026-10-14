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
related:
  - "[[Projects/派工鏡頭跨repo不再靜默_計劃]]"
---
# 派工鏡頭可指定目標repo_計劃

> 白話:派審查席時,掛鉤會自動把「這次改動牽連到的圖譜筆記」貼進派工詞。它一律在「會談開在哪個資料夾」那裡算。可是做事常常在別的工作樹、甚至別的 repo:會談開在 A,要審的計劃或提交在 B,掛鉤在 A 找不到,只附一行「沒附」。改成:派工詞可以多寫一行 `LUMOS-REPO: <絕對路徑>` 指定去哪裡算;路徑要通過跟掛鉤挑 lumos 執行檔同一套的信任檢查,不合就附說明、不去跑。

## 緣起

- 2026-10-13 後端示範:會談開在 lumos 工具鏈,審的是示範 repo `order-demo` 的分支,派工鏡頭算不出牽連筆記(只附了說明行)。2026-10-14 夜裡更普遍:全域規則要求每個工作開獨立的 git 工作樹,我在三個工作樹各開一份計劃、派了十幾席設計審,計劃只存在那些工作樹裡,掛鉤在會談目錄找不到,所有席都沒拿到固定席節點。出處:使用者 2026-10-14 列的示範改進第 4 條;當晚的席報告都寫「派工尾端沒有附固定席節點」。
- 舊裁定:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行寫「不選:標記行加 repo 路徑讓掛鉤改去那裡算(標記行文法要改、派工詞的自由文字會變成掛鉤去跑 git 的路徑,先不開這個口;說明行給繞法即可)」。本計劃推翻這一條(使用者 2026-10-14 授權全權裁量)。回應:
  - 「說明行給繞法」的繞法是「從開在目標專案的會談派席」。全域規則要求每個工作開獨立工作樹,於是會談目錄跟工作目錄錯開成了常態,繞法等於每份工作都要另開一個會談——實際上沒人照做,當晚十幾席全部沒附。
  - 「自由文字變成跑 git 的路徑」:在一個 repo 裡跑 git 的風險,是那個 repo 的 `.git/config`(例如 `core.fsmonitor`)可以讓 git 執行任意指令。現況是:掛鉤把會談目錄(環境變數或事件裡的工作目錄)原樣交給 lumos,lumos 在那裡跑 `git -C …`,會談目錄沒有任何擁有者或寫入權檢查。新路徑的差別是「來源從環境變成派工詞,派工詞可能被注入」;所以對派工詞指定的路徑加一道會談目錄沒有的檢查(做法 2):路徑、它的父目錄、它的 git 資料夾都屬於自己、都不是別人可寫——比會談目錄嚴。殘餘風險見〈實務隱患〉。
  - 「標記行文法要改」:不改 `LUMOS-IMPACT:` 與 `LUMOS-SPEC:` 的文法,另加一行獨立標記,兩種標記都吃它。

PRIOR-ART: `lumos dispatch-lens` 本來就收 `--repo <repo 內任一路徑>`(用 `git -C <路徑> rev-parse --show-toplevel` 找根),`--spec` 的相對路徑對找到的根解析、絕對路徑要在那個 repo 裡;掛鉤只是一律傳會談目錄。本計劃只改掛鉤傳什麼。信任檢查仿同一支掛鉤裡 `_trusted_lumos` 的 `_ok`(擁有者是自己、自己與父目錄都不是 group/other 可寫);`_ok` 只收檔案、而且那段在多支掛鉤之間是有守衛盯著的逐字複本,所以另寫一支資料夾版,不改它。
RETIRE-IF: Claude Code 在派工事件帶出子代理的工作目錄(會談目錄與工作目錄不再可能錯開),或連續 8 週派工詞裡的 `LUMOS-REPO:` 都等於會談目錄——拿掉這一行標記。
REVISIT:2026-12-15 數一次掛鉤事件裡帶 `LUMOS-REPO:` 且通過檢查的次數與被拒的次數,照 RETIRE-IF 判。

## 做法

1. **新標記** `LUMOS-REPO: <絕對路徑>`:單獨一行,正規式 `^LUMOS-REPO:\s*(.+?)\s*$`(路徑可以有空白,macOS 常見),跟 `LUMOS-IMPACT:` 或 `LUMOS-SPEC:` 同一份派工詞才有作用;同一份派工詞出現兩行以上,視為不合格(原因 `repo_duplicate`),照做法 4 處理——不去任何地方算、只附說明。
2. **信任檢查**(照順序,全部要過;前四條都不跑 git):
   - 是絕對路徑(`repo_not_absolute`);`realpath` 之後存在、是資料夾(`repo_missing`)。
   - 找它的 git 資料夾,不跑 git:`<路徑>/.git` 是資料夾就是它;是檔案(工作樹)就讀裡面的 `gitdir:` 那一行,再讀那個資料夾裡的 `commondir` 檔(有的話)找到共用的 git 資料夾;都沒有就不是 repo 根(`repo_not_root`)。
   - 這個資料夾、它的父目錄、它的 git 資料夾(工作樹時連共用的那個)都屬於目前使用者,而且都不是 group/other 可寫(`repo_untrusted`)。用新寫的資料夾版檢查函式。
   - 底下有 `docs/*-knowledge/`(`repo_not_lumos`)。
   - 前四條都過了,才跑 `git -C <路徑> rev-parse --show-toplevel`(`git` 取自 PATH,跟 lumos 跑 git 一樣),結果要等於 `realpath`(要指 repo 根,不收子資料夾,免得同一個 repo 有多種寫法;不等於也是 `repo_not_root`)。擋下的路徑一次 git 都不跑。
3. **過了**:`dispatch-lens` 的 `--repo` 改傳這個路徑,其餘照舊。設計審的 `LUMOS-SPEC:` 相對路徑照舊以 repo 根為基準。
4. **沒過**:不改去那裡算,也不退回會談目錄算(退回會用錯的樹,比沒附更糟);派工詞附一行 `LUMOS-LENS:` 說明,原因代碼是掛鉤自己的六個(`repo_not_absolute`、`repo_missing`、`repo_not_root`、`repo_untrusted`、`repo_not_lumos`、`repo_duplicate`,每個一句固定話),放在掛鉤自己的字彙表,跟 lumos 印的失敗代碼表分開;路徑照舊經 `_clean_field` 消毒後顯示;記一筆掛鉤事件。
5. **沒寫**:照舊用會談目錄。範圍或計劃在會談目錄算不出來時,說明行的繞法加一條「派工詞加一行 `LUMOS-REPO: <目標 repo 的絕對路徑>`」。
   - **設計審那條路也要有說明行**:現在 `dispatch-lens --spec` 失敗(計劃不存在、不在那個 repo 裡、沒有圖譜)時不印失敗代碼,掛鉤的說明行也只給代碼審範圍那條路用,所以設計審算不出來時派工詞什麼都沒附——今晚十幾席就是這樣。lumos 端替這三種加固定代碼 `spec_missing`、`spec_outside_repo`、`no_knowledge`(進既有的失敗代碼表),掛鉤的說明行拿掉「只在有範圍時」的條件,另寫一句計劃版的說明。
   - **說明行的措辭分兩版**:沒帶 `LUMOS-REPO:` 時照現在寫「在會談專案 … 算不出來」並給加 `LUMOS-REPO:` 的繞法;帶了而且通過檢查、lumos 在目標 repo 又失敗時,寫「在指定的 repo … 算不出來」,繞法不再叫人「從開在目標專案的會談派席」。
6. **範本與手冊**:`lumos-design-loop` 的 `templates.md` 與 `lumos-code-loop` 的派工說明,在 `LUMOS-SPEC:`/`LUMOS-IMPACT:` 那一行旁邊寫明:工作目錄不是會談目錄時(工作樹、別的 repo),多寫一行 `LUMOS-REPO:`。
7. **Codex 編排不在本計劃範圍**:`--arm` 的武裝檔以目標 repo 根為鍵,子代理開場認領時查的是 Codex 會談目錄的根,兩者不同就領不到;Codex 的開場事件也讀不到派工詞裡的 `LUMOS-REPO:`。要支援得另案讓認領找得到別的根,手冊不寫「`--arm --repo` 可跨 repo」。
8. **舊裁定標作廢**:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行(含「不選:標記行加 repo 路徑…」那一格)與它〈範圍〉裡「不做:讓標記行指定 repo」那一句、[[Systems/codex-harness]] 裡同一條 WHY,都標 `[status:superseded]`、`[被取代:Projects/派工鏡頭可指定目標repo_計劃]`;用 lumos 的指令改開頭欄位,正文用 Edit。

## 驗收條款

- [S1] 當派工詞有 `LUMOS-SPEC: docs/x-knowledge/Projects/a_計劃.md` 與 `LUMOS-REPO: <另一個 repo 的根>`,而那份計劃只存在另一個 repo 時,掛鉤應在另一個 repo 算、附上固定席節點。[test: t_dispatch_lens_hook_repo_marker]
- [S2] 當 `LUMOS-REPO:` 指的路徑是相對路徑、不存在、是 repo 裡的子資料夾、group 可寫(資料夾、父目錄或 git 資料夾任一個)、或底下沒有圖譜時,掛鉤應附一行帶對應原因代碼的 `LUMOS-LENS:` 說明,不在那裡、也不在會談目錄算。[test: t_dispatch_lens_hook_repo_rejected]
- [S3] 當路徑別人可寫時,掛鉤應一次 git 都不在那裡跑(用一支假 git 記錄呼叫驗)。[test: t_dispatch_lens_hook_repo_no_git_on_untrusted]
- [S4] 當派工詞沒有 `LUMOS-REPO:` 時,行為應與現在相同;範圍在會談目錄算不出來時,說明行應多一條加 `LUMOS-REPO:` 的繞法。[test: t_dispatch_lens_hook_fail_reason_notice]
- [S5] 當同一份派工詞有兩行 `LUMOS-REPO:` 時,應附 `repo_duplicate` 的說明,不在任何地方算;路徑含空白的 `LUMOS-REPO:` 應照常認得。
- [S6] 設計審的計劃在指定的(或會談的)repo 找不到、不在那個 repo 裡、或那個 repo 沒有圖譜時,掛鉤應附一行帶 `spec_missing`、`spec_outside_repo`、`no_knowledge` 的說明。[test: t_dispatch_lens_hook_spec_fail_notice][test: t_dispatch_lens_hook_repo_rejected]

## 實務隱患

- 守衛面:掛鉤會改寫子代理的派工詞,也是錨點清單裡的檔。風險一是讓 lumos 去不可信的目錄跑 git(做法 2 擋別人可寫的那一類;擋不住的是「自己擁有、但內容不可信」的資料夾——例如自己用 `cp -r` 或解壓縮拿到、`.git/config` 帶 `core.fsmonitor` 的 repo。這一類在會談目錄也一樣擋不住(會談目錄沒有任何檢查),而且使用者自己在那個資料夾裡敲 `git status` 就會觸發,不是本計劃新開的口;單人使用的威脅模型下接受);風險二是指錯 repo 時附上錯的節點,讓審查席以為那些就是牽連範圍——路徑必須是 lumos 專案的根,而且指錯時附上的節點會跟審材明顯對不上,席位照範本本來就要逐條判。
- 已排除:金流:不碰。
- 已排除:對外送出:只在本機跑 git 與 lumos。
- 已排除:不可逆:還原提交即回到只用會談目錄;派工詞多出的那一行舊掛鉤不認,照舊忽略。
- 改了錨點清單裡的掛鉤與測試檔,提交前要 `lumos anchor approve`。

## 回退

- 還原提交即回到只用會談目錄;已寫進範本的 `LUMOS-REPO:` 行,舊掛鉤看不懂、原樣留在派工詞裡,不影響其他標記。消費專案 `lumos update` 取回舊掛鉤後要重新 `anchor approve`。

## 審計修正紀錄

- r1 前掃(2026-10-14):9 條(語意命中 5、③ 2、② 1、存在命中 1)直接修進本文:Codex 跨 repo 認領領不到,改寫成不做;重複標記的處理前後矛盾,統一成不算;信任檢查要先讀 `.git` 檔、不能先跑 git,另寫資料夾版不改逐字複本;更正「跟會談目錄受到的保護相同」(會談目錄現在沒有檢查);設計審失敗沒有說明行,補三個代碼;原因代碼拆成六個並與 lumos 的表分開;舊裁定兩處加會談 codex-harness 標作廢;路徑可以有空白。前掃紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r1-intake.md`。
