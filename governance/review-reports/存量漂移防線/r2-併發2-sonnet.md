severity: major

# 審查範圍與方法
逐節讀完 `governance/review-reports/存量漂移防線/r2-snapshot.md`(凍結快照),聚焦資源與併發:
guard settle 併鎖後的重入/死鎖、兩檔寫入的失敗交錯與補救、表態檔多分支追加、推送掛鉤閘序與多分支預算、
scan/doctor 每次推送的成本與 git 子行程次數/逾時、治理帳寫入頻率。對照程式碼在
`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns`
的 `scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`,以及 `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md`。

## F1 doctor 的 Z 段(drift scan)每次推送無條件跑,且用 git 子行程、預算與既有段落不同量級,跟純文件推送的快路徑精神衝突
severity: major
blocking: 是 — 照這份 spec 實作,純文件(README/docs/assets)推送與極小改動推送也會被迫多付出到 60 秒的 doctor 成本,且此成本只隨「全圖譜 when-條件總數」增長、不隨「這次改了什麼」收斂,會系統性拖慢每一次推送、誘使大家常態性 `--no-verify`(這正是 pre-push hook 自己在別處反對的理由)。
引句:「doctor 的 Z 段就是 scan,同一個預算。」
1. spec〈做法〉第 0 節(r2-snapshot.md:46)定義:條件評估要跑 `git grep`/`git ls-tree`,單次沿用 `_lens_git` 的 20 秒逾時,「整次 check 或 scan 總預算 60 秒」。
2. 〈實務隱患〉·效能(r2-snapshot.md:129)明講 scan 會對全圖譜「每個」帶條件的行各跑一次 `git grep`/`ls-tree`,而且明白指出「doctor 的 Z 段就是 scan,同一個預算」——即 doctor 也要付到 60 秒。
3. 對照程式碼:`_lens_git`(scripts/lumos:29249-29260)每次呼叫都是獨立 `subprocess.run(...timeout=20)`,是真的會花時間的外部行程;既有 doctor 段落(例如 G 段筆記同檔名檢查、L 段欄位 lint,scripts/lumos:1199-1238)全部只走已經載入記憶體的 `notes` dict,不呼叫 git,量級是「全部段落加起來 1.1 秒」(見下一點)。drift scan 是 doctor 裡第一支需要外部子行程、且有明確到 60 秒上限的段落,量級整整高了一到兩個數量級。
4. `scripts/hooks/pre-push` 自己的成本表(scripts/hooks/pre-push:166-167)寫死「實測:除了全套測試以外,所有閘加起來約 13 秒(anchor 0.22s / 簽名檔 0.04s / doctor 1.1s / pitfalls 0.23s / code-loop 0.61s / test-layers 0.21s / 自主迴圈那支 10.3s)」,而 doctor 呼叫(scripts/hooks/pre-push:181)是在**逐 ref 迴圈之外、對每一次推送只跑一次**、且**不分是不是 docs-only/light 推送**都會跑(圖譜存在就跑;`have_vault` 判斷跟 docs/light 判斷是兩件事)。專案自己的鐵律(CLAUDE.md「本 repo 的測試子集怎麼跑」段)特別強調「純文件推送只跑文件子集」,但 doctor(含新加的 Z 段)完全不在這個快路徑保護傘下——drift scan 一旦條件數變多,「純文件推送」也要多等到 60 秒。
5. 這筆 60 秒也沒有算進 spec 自己揭露的多分支預算裡:〈實務隱患〉·多分支一次推(r2-snapshot.md:130)只講「check 在推送前掛鉤的逐分支迴圈裡跑,每個分支各自一個 60 秒預算;三個分支一起推最多約 3 分鐘」——這段只算了 per-ref 的 `check`,沒有把 doctor 裡「每次推送(不分幾個分支)另外還要付一次」的 Z 段 60 秒算進去。同一份 spec 自己在 129 行才講「doctor 的 Z 段就是 scan,同一個預算」,跟 130 行的「最多約 3 分鐘」兩處對不上:三分支worst case 應是 60(doctor Z 段,一次)+ 3×60(check,逐分支)= 最多約 4 分鐘,不是「約 3 分鐘」。這是快照內部自己前後不一致,不是我外加的假設。
6. CI(.github/workflows/ci.yml:96-97)`doctor --ci` 同樣是每次 push 觸發都跑、不分 docs/light,結論同上,只是沒有多分支迴圈那一段。

## F2 golive 截斷起點借的既有函式有兩種不同先例,spec 沒寫清楚該學哪一種;學錯會讓新分支/新 clone 首推把整段歷史當「這次推送」去掃,連誤擋帶效能都出問題
severity: major
blocking: 是 — 選錯先例會讓 golive 截斷靜默失效,新分支首推或找不到主線時退回空樹起點,把上線前的舊帳整批當成這次推送引入而擋下(不是提醒,是 block),同時把 scan/check 的掃描量從「這次推送範圍」放大成「整條歷史」,兩者都是會讓作者做出壞系統的方向。
引句:「①推送範圍起點借三道檢查共用的推送起點判法(`_lens_push_base`)並截到自己的上線點(`_nodehome_clamp_base` 的做法)」
1. spec〈PRIOR-ART〉(r2-snapshot.md:27)只講「借 `_nodehome_clamp_base` 的做法」,〈做法〉第 0 節(r2-snapshot.md:40)也只講「截到這道檢查自己的上線點(推送前掛鉤裡出現標記 `drift check` 的第一個提交)」,兩處都沒點名要不要傳 `_nodehome_clamp_base` 的 `hook` 參數、傳哪一個。
2. 程式碼裡 `_nodehome_clamp_base`(scripts/lumos:22967)簽名是 `(repo_root, base, tip, mark=None, hook=_NOTELINES_PRECOMMIT)`——**預設值是 pre-commit hook 檔**(`_NOTELINES_PRECOMMIT = "scripts/hooks/pre-commit"`,scripts/lumos:22952)。它內部呼叫 `_nodehome_golive`(scripts/lumos:22956-22964),那支函式的邏輯是 `git log --reverse -S<mark> -- <hook檔>`,也就是去某個 hook 檔的**內容變更歷史**裡找「第一次出現這個標記字串」的提交——找的是哪個檔,完全看 `hook` 參數。
3. 專案裡同一個函式現在有兩種先例,行為互不相同,而且都是刻意的:
   - `cmd_note_shape` 的推送路徑(scripts/lumos:24132)呼叫 `_nodehome_clamp_base(root, base, tip, _NOTE_SHAPE_GOLIVE_MARK)`——**省略 `hook`,吃預設值 pre-commit**。這是對的,因為 `_NOTE_SHAPE_GOLIVE_MARK = "note-shape --staged"`(scripts/lumos:23477)這個標記字串本來就只會出現在 pre-commit hook 裡(pre-push 那道只是「同一段範圍再查一次,接住 --no-verify」的後盾,不是這道檢查真正的上線點)。
   - `cmd_note_audit`(第二層/筆記內容審)的推送路徑(scripts/lumos:24435)呼叫 `_nodehome_clamp_base(root, base, tip, _NOTE_AUDIT_GOLIVE_MARK, _NOTELINES_PREPUSH)`——**明寫傳 `_NOTELINES_PREPUSH`**,因為 `_NOTE_AUDIT_GOLIVE_MARK = "note-audit check"`(scripts/lumos:24179)這個標記只會出現在 pre-push hook 裡(這道檢查本來就只掛在推送前/CI,沒有 pre-commit 版本)。
4. `drift check`(S1)照 spec 的接線只掛「推送前掛鉤與 CI」(r2-snapshot.md:44、114 的 S17),完全沒有 pre-commit 版本,跟「筆記內容審」是同一種形狀,不是跟「筆記形狀擋」同一種形狀——照理該學 `_NOTELINES_PREPUSH` 那個先例。但 spec 引用時只寫「`_nodehome_clamp_base` 的做法」一句話,沒有點名要傳 `_NOTELINES_PREPUSH`,也沒有提到這個參數存在。若實作時直接照抄「筆記形狀擋」那個更常見、看起來更簡潔的呼叫形式(省略 `hook`),`_nodehome_golive` 會去 `scripts/hooks/pre-commit` 裡找字串 `"drift check"`——但這個字串永遠不會出現在 pre-commit hook 裡(drift check 沒有 pre-commit 版本),於是 `_nodehome_golive` 永遠回 `None`,`_nodehome_clamp_base` 直接回傳原本沒截斷的 `base`——golive 截斷整段靜默失效。
5. 失效後果不是小事:`_lens_push_base`(scripts/lumos:29220-29246)自己的 docstring 講得很白:「★不能直接回「範圍找不到、放行」★...新分支首推會整批放過」、「★也不能一律當空樹★:新分支開在主線頂端時會把主線上線後的舊帳當新增誤擋」——這正是 `_nodehome_clamp_base` 存在的理由。截斷失效時,新分支首推、或本機找不到 remote 物件時,drift check 的診斷範圍會退回 `_lens_push_base` 給的 `_EMPTY_TREE_SHA..tip`,把**這個 repo 有史以來**所有「守衛紀錄 pending→pass」的提交都當成這次推送新引入的 c1(見〈做法〉1-5,r2-snapshot.md:62「推送閘只擋 c1、而且只擋這次帶進來的」),對任何第一次推送的分支或新 clone 直接判成整批要處理,而且是 block 模式擋下,不是只列出。這跟 spec 自己在〈誠實界線〉最後一條(r2-snapshot.md:146)承諾的「只看這次推送帶進來的」正好相反。

## F3 c1–c4 沒有對稱涵蓋 settle 兩段式寫入失敗後的「家筆記已轉正、守衛紀錄仍 pending」半套狀態
severity: minor
blocking: 否 — 不會造成資料損毀或誤導性阻擋,S5 補救路徑本身可用(重跑一次 settle 就能補完),只是沒有主動偵測/提醒機制;作者照 spec 實作出來的系統是可運作、可恢復的,只是這一種半套狀態會悄悄躺著沒人catch,直到 `lumos guard required` 的「逾期」邏輯用錯誤措辭(叫使用者「快去做」而不是「快去重跑 settle 補寫」)意外帶出來。
引句:「若家筆記已經是這條合約的正式行(同一句合約、同一個 `[test:]`)而守衛紀錄還是 pending,就只做第二步」
1. r2-snapshot.md:55 的補救路徑明確承認、也設計了修復這種半套狀態的指令(S5,r2-snapshot.md:102),但〈做法〉1-4(r2-snapshot.md:57-61)定義的 c1–c4 四種一致性檢查裡,c1 只抓「驗證紀錄 status 是 pass、卻還寫著舊預告句」——方向是「紀錄已轉正、筆記沒跟上」;沒有一條檢查「紀錄仍 pending、但家筆記已經轉正」(方向相反)。
2. 這個半套狀態由 settle 自己兩段式寫入中途失敗造成(第一段家筆記寫成功、第二段守衛紀錄寫失敗即進入此態,r2-snapshot.md:54-55),而 scan/check/doctor Z 段(r2-snapshot.md:38-46)只掃 c1–c4 與乙的 when-條件,不含這第五種狀態,等於甲自己製造出來的一種半套狀態,甲的健檢清單裡沒有對應項目回頭抓它。
3. 現有 `cmd_guard_required`(scripts/lumos:11900-11931)會在 due 日期過後把它列成「逾期」,但訊息是「還沒完成,最遲 X 要做完」——對這個特定半套狀態而言,實際工作已經做完,只差重跑一次 settle 補寫紀錄,訊息卻叫人去補做工作本身,容易誤導。

## F4 引用 Issues/治理帳多個寫入者都沒上鎖 的說法目前跟該筆記實際內容對不上,而且 spec 自己的修復/接線步驟沒有排回頭補寫的工作項
severity: minor
blocking: 否 — 不影響 drift-check 本身的運作正確性,是圖譜協調準確度的落差;不改也不會讓作者做出壞系統,但會讓 2026-10-11 的裁決依據不完整。
引句:「那篇 REVISIT 時把本計劃的表態檔與 drift-check 事件也算進去」
1. r2-snapshot.md:131(〈實務隱患〉·併發)寫:「表態檔是只追加的 jsonl,兩條分支各自追加合併會有衝突行(治理帳同一種問題,見 [[Issues/治理帳多個寫入者都沒上鎖]],那篇 REVISIT 時把本計劃的表態檔與 drift-check 事件也算進去)」。
2. 實際讀 `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md`,其 `REVISIT:2026-10-11` 那行(檔案第 52 行)全文是:「跟 rtb 回饋那篇同一天決定要不要另開計劃修。第二層([[Projects/筆記內容審_計劃]],取代了原本寫在這裡的舊計劃)2026-09-28 收窄後不拿治理帳判涵蓋,壞行只影響它的觀測數字,但寫入頻率會變高,決定時把它算成第一個受影響的使用者。」——完全沒有提到「存量漂移防線_計劃」「表態檔」或「drift-check」任何字樣,只提到「筆記內容審」這個不同的計劃。
3. spec 的〈做法〉第 4 節「掃全圖譜與修復」(r2-snapshot.md:89-95)、〈條款〉S16(r2-snapshot.md:113)只要求把工具鏈與 rtb 的漂移掃描結果修復並記錄,沒有任何一步要求「回去把 Issues/治理帳多個寫入者都沒上鎖.md 的 REVISIT 行加上本計劃與 drift-check 這兩個新寫入者」——照 CLAUDE.md「同一次工作內寫回」與「回頭條件要接電」的鐵則,這個承諾若沒有對應工作項落地,10/11 那篇筆記被重看時就看不到這兩個新增的併發寫入者,回頭條件等於斷線。

# 已讀、無 finding 的部分
- 〈做法〉0「共用:指令家族 lumos drift」的表態(ack)/內容編號/簿記豁免設計:已讀,內容編號綁「路徑+區塊+小標題+行文字+發現種類」跟改名/換原因失效的邏輯內部一致,無 finding。
- guard settle 整段包進 `_vault_write_lock` 後的重入問題:已讀程式碼——`_vault_write_lock`(scripts/lumos:14251-14297)用 `_VAULT_LOCK_HELD` 這個以「鎖檔路徑字串」為鍵的計數器做同行程可重入判斷(scripts/lumos:14271-14277),`_vault_lock_where`(scripts/lumos:14207-14234)算路徑用 `os.path.realpath` 正規化,同一個 `env.vault` 在同一次 settle 呼叫內算出的鍵一定相同;lumos 全專案沒有用到 `threading`/`ThreadPoolExecutor` 之類跨執行緒併發(唯一命中是 idioms 規則清單裡拿來偵測「別的語言程式碼有沒有用執行緒」的樣式字串,scripts/lumos:20101,不是 lumos 自己在用),是單行程序循序 CLI,不存在同行程內兩個執行緒互搶同一把鎖造成死鎖的情境。若 settle 內部真的呼叫 `cmd_set`(它自己也會 `with _vault_write_lock(env.vault):`),屬於巢狀重入,會直接命中可重入分支放行,不會卡死——無 finding。
- 〈做法〉2「乙:回頭條件」的 when 條件語法與評估、〈條款〉S9–S12:已讀,語法與 scan/check 的職責切分內部一致,無 finding(非我這道鏡頭的重點,粗略核對過交叉引用有效)。
- 〈回退〉一節:已讀,各退路(推送閘拿掉一行、`note_shape.gate=warn`、settle 改寫不給開關且理由講得通)內部一致,無 finding。

# 總結
最嚴重等級為 major,blocking 共 2 條(F1、F2)。
