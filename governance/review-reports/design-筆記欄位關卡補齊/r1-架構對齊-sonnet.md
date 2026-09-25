severity: major

# 架構對齊審查(r1)——筆記欄位關卡補齊_計劃

被審材料:governance/review-reports/design-筆記欄位關卡補齊/r1-snapshot.md(sha256 fd1b2651…d420d1c2)

## Q1 分層與依賴方向

新邏輯的落點跟既有同類檢查一致:欄位規則(status/日期/valid/about_code/lands_in)放進 lint、健檢新段落放進 doctor、讀提交內容改用 `_nodehome_reader` 同款包裝——這條軌跡跟既有「lint 單篇快檢、doctor 全圖權威、兩者共用同一支檢查函式防兩入口漂移」的分工一致,對照 `scripts/lumos:4526` 的 Check J 共用檢查器註解與 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md` 的 d2 決策(「doctor(全圖權威)與 lint(單檔快檢)分工」)。讀提交內容那段(做法二)也不是新做法:`_nodehome_reader(repo_root, where)`(`scripts/lumos:21678`)本來就是一支通用的 `read(path)->bytes|None`,不是綁死在「每支檔有家」語意上,拿來給 lint 讀 index 版本內容屬於重用而非跨層直呼。CI 傳 touched 清單給 doctor(做法一)也是延伸既有管道——doctor 早就吃 `--touched-from`(`scripts/lumos:30353`),pre-push 已經在傳(`scripts/hooks/pre-push:178-180`),只是 CI 目前沒傳(`.github/workflows/ci.yml:97` 只有 `python scripts/lumos doctor --ci`,沒有 `--touched-from`)——這處沒有跨層直呼,只是把既有旗標多接一個呼叫端,跟 CI 已有的 `BEFORE..SHA` range 慣例(`.github/workflows/ci.yml:34-40`、`105-113`,pitfalls/code-loop 兩步都這樣算)同形狀。

此問未見不對齊,不掛 severity。

## Q2 命名與錯誤處理

做法一的「碰到清單內錯誤→擋、清單外/沒清單→只提醒」跟既有的「預告合約只擋碰到的」是同一支機制:`run_doctor` 的 S15 段落(`scripts/lumos:2310`)已經用 `_guard_touches(_gn, env, touched)`(`scripts/lumos:2331`,定義於 `scripts/lumos:11035`)做「touched 內擋、touched 外提醒」的判斷,touched=None 時整段退化成不擋(`scripts/lumos:11043` `if touched is None:`)——這跟 S2「沒有碰到清單時全部只提醒」是同一種退化邏輯,不是另立一套分級規則。責任欄字數下限延伸到 `lumos set responsibility`(S10)也是直接複用既有共用函式 `_nodehome_resp_ok`(`scripts/lumos:21492`,已被 `lumos new`〔`scripts/lumos:15052`〕與多處 doctor 檢查共用),不是新寫一套判斷。

快照沒有寫到實際錯誤訊息文字(仍是做法層級的設計,未到訊息稿),所以「擋下:」字首之類的措辭規範無法逐字核對;就目前寫下的分級邏輯看不出跟鄰居不一致之處,不掛 severity。

## Q3 第二種做法

## F1 「新舊比對」用另一套版本欄位差集,沒有對到既有的新增告警閘同款機制

severity: major
- blocking: yes
- 快照原文:「以下都只擋**新違規**:這一版有、上一版沒有(提交時上一版=目前最新的提交;推送時=推送的起點;這一版才新建的筆記整篇都算新)。上一版就有的違規只提醒。」——引句:「以下都只擋**新違規**:這一版有、上一版沒有」
- 為什麼不對齊:專案裡已經有一套「只擋新增的、舊的只當底數」的落地機制,就在同一支 `scripts/lumos` 的 lint 子系統裡——`_lint_new_diff_claims(base_claims, head_claims, base_files, head_files)`(`scripts/lumos:20529-20553`)靠指紋(`_lint_new_key`,`scripts/lumos:20504-20520`,規則+檔名+命中片段/退化訊息弱比對)算 base 版出現幾次、head 版出現幾次,超過 base 次數的才算新增,支撐「新增告警閘」(`lint-new` gate,memory `lint-new-gate-delivery-status.md` 已記交付)。這條既有機制解的正是同一個問題形狀:「規則是新加的,不要一次把舊帳全部翻紅,只擋這次新冒出來的」。S5–S9、S11 卻是另外設計一套「讀上一版 YAML 欄位值、逐欄位比對有沒有從無到有」的比較邏輯(讀 `commit^:path` 的 frontmatter,跟現在版本的 status/日期/valid/about_code/lands_in 逐項比),跟指紋計數法是兩種不同的實作路徑解同一件事,而計劃的 PRIOR-ART 只提到「每支檔有家」的 cutoff 形狀與「_ENUM_CUTOFF/_ALIASES_CUTOFF 靜態日期切點」兩個對照(`scripts/lumos:4854`、`4863`),完全沒有提到、也沒有解釋為什麼不沿用已經上線的 `_lint_new_*` 差集機制。這正是題目給的範例:「另一套『新舊比對』…而既有已有同功能」。
- 附帶一提:_ENUM_CUTOFF/_ALIASES_CUTOFF 走的是第三種形狀(寫死日期切點,不比對上一版內容),計劃在 intake 的 HIT-1/HIT-2 已經論證過為什麼不能用建立日/cutoff(子項目可以在舊筆記裡新加,cutoff 抓不到)——這段推理成立,但沒有把它跟 `_lint_new_diff_claims` 放在一起比較,遺漏的是「既有的新舊比對機制」而不是「既有的 cutoff 機制」。

## Q4 落點合不合理

## F2 lands_in 漏了這次真的會改到的 CI 檔案的家

severity: minor
- blocking: no
- 快照原文(做法一,S3 對應段落):「**有碰到清單時**(推送前掛鉤本來就傳;CI 改成用推送前的起點算出同一份清單):清單裡的筆記有錯誤 → 擋;其他筆記有錯誤 → 只提醒並列出篇名。」——引句:「CI 改成用推送前的起點算出同一份清單」
- 為什麼不對齊:S3 明確要改 `.github/workflows/ci.yml`(讓 CI 用 `BEFORE..SHA` 算出 touched 清單傳給 doctor)。但 `.github/workflows/ci.yml` 現在的家不是快照 frontmatter `lands_in` 列的三篇任何一篇——它已經登記在 `Systems/bound-tests-gate.md` 的 about_code 裡(`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:43` `- .github/workflows/ci.yml`),快照 frontmatter 的 `lands_in` 只寫「[[Systems/lumos-cli-write]]」「[[Systems/lumos-cli-read]]」「[[Systems/每支檔有家]]」三篇(引句:`- "[[Systems/lumos-cli-write]]"`,對照快照 frontmatter 第 16 行),沒有 `Systems/bound-tests-gate`。照 CLAUDE.md 鐵則五「改到的每支檔都得先有家…改到程式要寫說明就寫進改到那支檔的家」,這次落成後 ci.yml 那段改動的說明理當寫進 `bound-tests-gate`,計劃的 `lands_in` 該補上這一篇,不然會出現「改了 ci.yml,但沒有任何 lands_in 落點篇提到這件事」的缺口——恰好正是這份計劃自己要新增的 S9 規則(計劃缺 lands_in 要擋)想抓的那種問題,只是這裡缺的是「該補的一項」而不是整個欄位。
- 結構本身沒問題(lumos-cli-write/lumos-cli-read/每支檔有家三篇分別對到 set 類寫入原語、lint/doctor 讀取原語、pre-commit/pre-push 每支檔有家形狀,都對得上),只是清單漏列一篇,判 minor。

不對齊共 2 條,其中 major 1 條。
