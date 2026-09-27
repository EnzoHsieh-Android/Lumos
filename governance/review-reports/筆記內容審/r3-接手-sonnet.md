severity: blocker

# 筆記內容審_計劃 r3 第三方審查(鏡頭:整合/知識同步,接手三個月後的人)

範圍聲明:只讀了指定的 r3-work.md、r3-delta.patch,對照 clone-ns 這份程式碼(scripts/lumos、scripts/test_lumos.py、scripts/hooks/pre-push、.github/workflows/ci.yml、scripts/templates/);決策一律照 r2 後「收窄成防疏忽」的裁定,不把「防作弊被繞過」再報成缺陷。git 驗證(reflog 行為)在 /tmp 自建的臨時 repo 用 `git -C` 做,沒有動 clone-ns。

## 逐節讀

- 開頭欄位、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。
- 〈判定者能不能用:小實驗〉:已讀,無 finding(誠實界線已自陳樣本小、切好句的侷限)。
- 〈做法〉第 0 節(防什麼、不防什麼):已讀,收窄範圍與「信任只需要單向」的論證跟第 2 節的折疊規則(取最重)方向一致,無 finding。
- 〈做法〉第 1 節(哪些行要審):圍欄行位數有內部矛盾,見 F2。其餘(上線判定、完成審定義、decisions 小標題)已核對程式碼,見下方逐項。
- 〈做法〉第 2 節(內容編號、判定檔、判定怎麼算):已讀,`_write_lf`/暫存檔命名、判定折疊三步驟跟程式碼核對一致,無 finding。
- 〈做法〉第 3 節(指令):第 2 點的範本檔登記缺口見 F1;第 4 點 decision-amend 的 fetch 新鮮度判準見 F3,結構欄清單缺口見 F6;第 8、9 點(跟代碼審的先後、CI 接線)見 F4、F5。
- 〈做法〉第 4 節(上線前校準)、第 5 節(規範文字與路由):已讀,無新 finding(第 5 節新開子檔、加路由列這兩件事本身可執行;子檔實際內容是否完整不屬於這份 spec 的條款義務,留給實作)。
- 〈條款〉S1–S16:對應關係已逐條核對,測試名跟內容大致對得上;S4 的用詞問題併入 F2 報告(它跟第 1 節同一個矛盾點,不重複開一條)。
- 〈回退〉:已讀,第 1 點提到工具鏈自己的 `.github/workflows/ci.yml` 要手改,這件事跟 F5 相關,已在 F5 一併討論。
- 〈實務隱患〉:已讀,守衛面、對外送出、可用性、已排除項無 finding;資源併發與容量段落沒討論到 F4 指出的「小改動閘/相對量」副作用,已併入 F4 報告。
- 〈誠實界線〉:已讀,無新 finding。
- 〈前身 r3 發現怎麼處理〉〈審計修正紀錄〉:記述性內容,已讀無 finding。

## F1 新範本檔沒登記進工具鏈自裝檔清單,會讓既有測試立刻翻紅

severity: blocker
blocking: 是 —— 這不是「可能」,是這份 repo 現有一支測試會machine-verifiable 地翻紅,且 spec 全文没有一處提到要改這張表。

〈做法〉第 3 節第 2 點要新增範本檔:

引句:「★派工詞放在新範本檔★ `scripts/templates/note-audit-judge.md`」

但 `scripts/templates/` 是工具鏈自裝檔的白名單目錄之一,消費專案安裝/更新時整夾複製,而且有一支測試逐檔比對「這個目錄底下受版控的每一支檔」是否跟白名單 `_VENDORED_TREE_FILES` 一模一樣:

file: `scripts/lumos:16901-16923`(`_VENDORED_TREE_DIRS = ("scripts/hooks", "scripts/templates")` 與 `_VENDORED_TREE_FILES` 白名單,目前只列了 `scripts/templates/graph-discipline.md` 一支)

file: `scripts/test_lumos.py:11554-11569`(`t_vendored_file_list_matches_what_install_ships`,用 `git ls-files scripts/hooks scripts/templates` 跟白名單集合比對,少登記直接 `check(...)` 失敗)

該測試的說明已經寫死了後果:

file: `scripts/test_lumos.py:11555-11556`(該測試的 docstring 講明少登記的後果:那支檔會被當成專案自己的程式檔掃、撐高風險分級)

也就是說:只要照 spec 把 `scripts/templates/note-audit-judge.md` 加進版控卻不同時把它加進 `_VENDORED_TREE_FILES`,這支既有測試(不是 note-audit 自己的新測試)當場翻紅;而且在翻紅之前,這支範本檔在「每支檔有家」「小改動閘」等既有機制眼中會被當成「消費專案自己的程式檔」處理(因為安裝端的跳過判斷認的是這張白名單,不是目錄前綴——`scripts/lumos:16908-16910` 的註解已經講白了這條坑是 2026-09-10 代碼審抓到的)。spec 通篇(用 `grep -n "vendored" r3-work.md` 核對,0 命中)沒有任何一處提到這張表要跟著改,S13 條款也只驗「派工詞內容對不對」,不驗「範本檔有沒有掛進安裝清單」。

## F2 圍欄行的判準,同一節裡「三個以上」跟「四個以上」自相矛盾,且跟程式碼對不上

severity: blocker
blocking: 是 —— 兩處文字互相矛盾,任一種讀法都會讓另一半的描述變成假的;而且較多數的文字(不審的行、S4 條款)指向跟程式碼不符的門檻,照著實作會漏擋最常見的三個反引號圍欄記號行。

〈做法〉第 1 節「所屬小標題」那一段先說:

引句:「它認得三個以上反引號或波浪號的圍欄」

三個句子之後,「不審的行」那一段卻說:

引句:「含四個以上反引號與波浪號」

這兩句講的是同一個函式 `_visible_lines`(前一句明講「用全檔唯一的圍欄判定 `_visible_lines`」)。核對程式碼,圍欄標記判定是:

file: `scripts/lumos:3262`(`is_marker = indent <= 3 and not ln.startswith("\t") and s.startswith(("```", "~~~"))`)

`s.startswith(("```", "~~~"))` 認的是三個反引號/波浪號起跳,不要求第四個字元。程式碼站在「三個以上」這句這邊,「不審的行」那句是錯的。但條款 S4 抄的是錯的那句:

引句:「圍欄記號行(含四個反引號)」

這代表:①同一份 spec 對同一件事講了兩種互斥的門檻,任何人照文字實作都會挑其中一邊,而多數複述(不審的行段落 + S4 條款,兩處對一處)都指向錯的那個;②如果照「四個以上」實作,一般 markdown 最常見的三個反引號圍欄開頭/收尾行(這份 spec 自己、CLAUDE.md、幾乎所有專案筆記都這樣寫圍欄)就不會被排除在待審之外——這些純標記行會被當成「新寫的筆記行」送進判定者,產生沒有意義的內容編號、耗用判定額度,而且判定者依派工詞第③④句的邏輯多半會把單獨一行「\`\`\`」判成看不出主張、體驗上等於雜訊,浪費 prepare 切分的 150 行配額。

## F3 decision-amend 的遠端新鮮度判準,對「剛 clone」這個情境不成立

severity: major
blocking: 是 —— 這是可重現的 git 行為(見下方臨時 repo 實測),不是臆測;剛 clone 完馬上想用 decision-amend 是完全合理、大概率會撞到的第一次使用情境(對應審查鏡頭要求的「Claude/Codex 會談各會撞到什麼」)。

〈做法〉第 3 節第 4 點:

引句:「reflog 裡最新一筆(fetch、pull、push、clone 都算)距今不超過 10 分鐘」

我在 `/tmp` 自建臨時 repo(`git init` → commit → `git clone` 到另一個目錄,不做任何 fetch)驗證:`git clone` 只會在 `refs/remotes/origin/HEAD` 留下 reflog(「clone: from …」那一筆),不會在具名分支的追蹤參照(例如 `refs/remotes/origin/main`)留下任何 reflog——`git reflog show origin/main` 回傳空、`.git/logs/refs/remotes/origin/` 底下只有 `HEAD` 這一個檔,沒有 `main`。也就是說,如果 decision-amend 照 spec 描述去讀「每個遠端底下追蹤參照」(即 `origin/main` 這種具名分支參照)的 reflog,剛 clone 完、一次 fetch 都還沒做過的情況下,這一步查到的是「沒有紀錄」,會被判定拒絕——跟 spec 自己講的「clone 都算」直接矛盾。這個判準原本就是為了取代「全新 clone 沒有 FETCH_HEAD」這個已知洞(同一段稍早提到)而設計的,但它換的這個機制本身在同一個情境(全新 clone)底下也是空的,沒有真的補上那個洞。

（好消息是:一旦做過一次 `git fetch`,具名分支的 reflog 就會正常寫入,所以這只影響「clone 完全新的分支追蹤參照、一次 fetch 都還沒做就想 decision-amend」這一種窗口,而且擋下時會印 `git fetch --all`,跑一次就能解;不是不可恢復,所以列 major 不是 blocker。)

## F4 判定檔不算簿記,會讓「小改動閘」的相對量檢查被判定檔本身的內容撐爆

severity: major
blocking: 是 —— 這是現有小改動閘的既有計算邏輯直接可推出的行為,不是新機制,只是 spec 沒討論這個副作用。

〈做法〉第 8 節解釋了為什麼不把 `governance/note-verdicts/` 加進簿記豁免:

引句:「那組常數有四個消費者,加資料夾會悄悄改到小改動閘與風險分級」

但這句話只講了「不加」的理由,沒有回頭檢查「不加」造成的後果。核對程式碼,小改動閘(`_SMALL_CHANGE`,給 `spec-gate --push-check` 用的「全靠人驗的風險低計劃」快速放行路徑)有四個維度,其中「擴散」(max_files/max_dirs)確實只算 `_is_code_file` 認得的程式檔副檔名,`.json` 不在 `_NODEHOME_CODE_EXTS` 裡,不會被算進去(`scripts/lumos:6270`);但「相對量」維度不是這樣算的——`_sc_churn` 直接吃 `_sc_changed_files` 給的全部非簿記檔案(只用 `_bk()` 排簿記,不排副檔名,`scripts/lumos:6236-6237`),單檔改動超過 `max_abs_lines=300` 行(`scripts/lumos:5410`)就會被判「相對量」不合格,進而讓整批推送掉出小改動快速放行路徑。

一份判定檔要裝「每一行的(內容編號、分類、證據、理由、證據驗過沒)」,prepare 一批最多到 150 行待審(〈做法〉第 3 節第 1 點),一份報告對應一份判定檔(第 3 節第 5 點);150 筆結構化 JSON 記錄用 `indent=2` 序列化,輕易超過 300 行。也就是說,只要一次 note-audit record 涵蓋的行數夠多(计劃收尾整篇重審時尤其容易,spec 自己在〈實務隱患〉也提到「計劃收尾時可能上千行」),它產生的判定檔本身的 diff churn 就會讓這次推送在小改動閘的「相對量」維度不合格——即使當次真正的程式碼改動小到符合小改動閘的其餘三個維度。這個副作用完全發生在 note-audit 自己的紀錄檔上,跟作者實際改了什麼程式碼無關,〈實務隱患〉的「資源併發」「容量與速度」兩段都沒有提到這一層。

## F5 「note-audit check 排在 code-loop check 之前」這個不變量,在這份工具鏈自己的 CI 裡沒有對應的安排,且無測試覆蓋

severity: major
blocking: 是 —— 這份 repo 自己的 `.github/workflows/ci.yml` 目前的實際順序剛好跟 spec 宣稱的順序相反,S10 的測試標籤明文只綁「推送前掛鉤」,不驗 CI 的步驟順序;〈回退〉第 1 點又明講這支 CI 檔要手改,代表它在實作範圍內。

〈做法〉第 8 節與條款 S10 都宣稱:

引句:「推送前掛鉤裡 note-audit check 應排在 code-loop check 之前」

第 8 節給的理由是「先過筆記內容審(record、提交判定檔),再做代碼審留痕」「所以沒審的會先在這裡被擋」。但這句話只驗證過推送前掛鉤(pre-push hook)的既有順序——核對 `scripts/hooks/pre-push`,確實是 `home check`(約行 236)→`note-shape --diff`(約行 247)→`code-loop check`(約行 309),note-shape 在前。可是這份工具鏈自己的 `.github/workflows/ci.yml`(〈回退〉第 1 點點名「這支檔不在 `lumos update` 的同步清單裡,要手改」,代表它是本次要動的檔,不是消費專案的事)裡,同一組檢查的實際順序是反過來的:

file: `.github/workflows/ci.yml:98`(`code-loop gate` 步驟先跑)

file: `.github/workflows/ci.yml:121`(`note-shape gate` 步驟後跑)

〈做法〉第 9 節給 doctor 的接線指示是:

引句:「步驟照第一層 doctor 給的那步,在它後面加一行」

也就是把 note-audit check 接在既有 note-shape 步驟後面——如果這支 CI 檔照同一個邏輯手改(在 note-shape gate 那步後面加 note-audit check),得到的順序會是 code-loop gate → note-shape gate → note-audit check,note-audit check 排在 code-loop check 之後,直接違反第 8 節宣稱的不變量。S10 的測試標籤 `t_note_audit_check_reads_tip_and_order` 明文只講「推送前掛鉤裡」,不會去驗 `.github/workflows/ci.yml` 的步驟順序,所以這個落差沒有機械守衛會抓到。實際後果比較輕(CI 最終還是會紅,只是「哪個錯誤先出現」的順序跟本機不同),但這正好戳破第 8 節論證「已經先留痕才被擋,代價很低」的前提——那個論證假設 note-audit 一定先擋下,CI 裡目前的排法卻不保證這件事,而 spec 沒有承認或處理這個落差。

## F6 decision-amend 禁改欄位清單漏了 `ended`

severity: minor
blocking: 否 —— 這是誤用才會踩到的邊界(正常 note-audit 流程只會叫它改 content/context/why_chosen 這類文字欄),不是正常操作路徑會撞到的問題,沒有具體會被觸發的場景。

〈做法〉第 3 節第 4 點列出不准用 decision-amend 改的結構欄:

引句:「`id`、`decided`、`valid`、`superseded_by` 這些結構欄不准用它改」

但 `cmd_decision_supersede`(`scripts/lumos:14814-14889`)顯示 `ended` 也是一個帶語意的結構化日期欄位(供「E2 時序法」判斷翻案先後),同樣不該被當成任意文字子欄覆寫,清單裡卻沒有它。照 spec 字面「只改那一條決策的那一個文字子欄」搭配「不准改的清單」是這四個,`--field ended --text "任意文字"` 目前沒有被明文禁止。

## 總結

檔級 blocker,共 5 條 blocking(F1–F5,blocker/major 各佔一部分),1 條 minor(F6)不計入 blocking。F1、F2 是可重現、機械可驗的既有測試/程式碼衝突;F3 是實測驗證過的 git 行為落差;F4、F5 是既有機制交互作用下的副作用,spec 都沒有處理或承認。
