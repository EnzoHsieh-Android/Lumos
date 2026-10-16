severity: major

已讀全份凍結審材與 r1-intake。前掃已修的各條不重報。下列規則細節都用 python3.14 實際跑過,實驗目錄已刪。

風險類逐類:
- **守衛面**:碰,見 F1–F5、F14。
- **舊資料與舊帳相容**:碰,見 F12(既有測試的釘)。詞表是放寬,新命中是舊命中的子集;門規則版本升級讓舊留痕重數,計劃已寫明。
- **已在途分支**:碰,見 F14。
- **其他會談與計劃的交界**:碰,見 F10,與〈前端框架從vue分出〉的 `_stack_key_for_file` 順序。

## F1 `第二個/第二次` 的豁免後面接什麼都放行
spec 段落:做法 9,送出的正規式。
引句:「(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次])」
- 問題:負向前瞻只看「第二個/第二次」,不看後面接什麼。S19 只釘「第二個請求」。
- 具體例:「重試時送出第二次通知給客戶」→ 預期照舊命中對外送出 → 照 spec 的正規式實跑回 False(不命中)。「送出第二個郵件」同樣 False。
- 後果:這兩句是後端計劃常見的重試寫法。若該計劃別處沒有其他命中,風險會判低。spec 的天花板段只承認「送出請求,目的地是外部物流」那一種,沒承認這一種。
- 佐證:`scripts/lumos` 的 `PITFALL_CLASSES`(約 29907 行)現在是裸字 `送出`,新規則只會變鬆。
severity: major
blocking: 是(照字面實作會把真的對外送出判成風險低,且 S19–S22 都測不到)

## F2 去處「緊接」的條件太窄,兩個自然寫法漏判
spec 段落:做法 9,送出的第二、第三個分支。
引句:「但前端語境詞後面緊接著寫出去哪(給、到、至、往)照算」
- 問題:只認「請求/表單」之後緊接 給/到/至/往。
- 具體例:「送出表單資料給客服」→ False。「使用者請求送出補發通知給客戶」→ False,因為「請求」在這裡是動詞,被當前端語境。
- 差別:這是在 spec 已承認的「隔了別的字」天花板之外,多出「請求」當動詞、「表單」後接名詞這兩種。
severity: minor
blocking: 否(方向是多放行,spec 已用 RETIRE-IF 兜底,但例子應補進 S 條款或天花板段)

## F3 大寫 `PAYMENT` 的豁免依形狀、不依字,S25 是空殼
spec 段落:做法 9,金流的正規式和 S25。
引句:「payment(?<!(?-i:_PAYMENT))(?!(?<=(?-i:PAYMENT))_)」
- 問題:凡是大寫 PAYMENT 緊貼底線一律豁免。實跑 `PAYMENT_API_KEY`、`PAYMENT_WEBHOOK_SECRET`、`PAYMENT_PROVIDER`、`ENABLE_PAYMENT`、`MY_PAYMENT` 全回 False。
- 自相矛盾:spec 自己的 WHY 寫「STRIPE_SECRET_KEY、REFUND_WINDOW_DAYS 這類大寫識別字多半真的在接金流」,`PAYMENT_API_KEY` 比它們更像金流設定。
- S25 是空殼:S25 用 `STRIPE_SECRET_KEY`,它靠 `stripe` 那個詞命中,不經過 payment 的例外。就算例外放寬到所有大寫識別字,S25 照綠。
引句:「[test: t_door_keyword_caps_stripe_still_hits]」
- 缺的條款:應有一條釘「`PAYMENT_API_KEY` 仍命中」,或在 d1 明寫它被豁免。
severity: major
blocking: 是(照字面實作會讓大寫金流設定名脫掉金流判定,且沒有測試能抓到)

## F4 infra 題的觸發字寫在字串裡,會被 `_stack_norm_line` 剝掉
spec 段落:做法 6,infra 題表與 S12。
引句:「六題,每題 when 只收那一題的寫法」
- 問題:觸發比對前會先把字串字面挖空,見 `scripts/lumos` 的 `_stack_norm_line` 與 `_strip_string_literals`(約 30503–30514 行)。只有 `when_raw` 欄位才看字串內容,spec 一個字沒提 `when_raw`。
- 實測(同一個剝字串函式):
  - `LOCK="/tmp/e2e.lock"` 變成 `LOCK=""`。
  - `curl -s "http://localhost:3000/health"` 變成 `curl -s ""`。
  - `docker run --name "web-$X" -p 5432:5432 pg` 變成 `docker run --name "" -p 5432:5432 pg`。
  - `rm -rf "$(realpath "$DIR")"` 變成 `rm -rf ""$DIR""`。
- 具體例:新增行 `PIDFILE="/tmp/e2e.pid"` → 預期 infra-shared 亮 → 實際不亮。`PIDFILE=/tmp/e2e.pid` 沒加引號才亮。
- S12 的缺口:S12 寫「新增行有 `/tmp/`」,測試作者用不加引號的寫法就會綠,真實腳本幾乎都加引號。`/tmp/`、`localhost:數字`、`--name` 後的名字、`realpath` 都得進 `when_raw`,spec 要寫明。
severity: major
blocking: 是(infra-shared 最想抓的 /tmp 鎖檔,在慣用寫法下觸發不了)

## F5 觸發字沒有詞界,並且沒有任何反向驗收
spec 段落:做法 6 的 infra 表,與實務隱患第三條。
引句:「題目 when 只收具體寫法,不是改到」
- 問題:表裡的觸發字是裸詞,又以 `re.I` 編譯(`_STACK_TRIGGERS`)。
- 實測:
  - `wait` 命中 `await page.goto(url)`,所以每支 e2e `.ts` 只要有 await 就亮 infra-signal。
  - `kill` 命中 `const skill`、`const killed`。
  - `ps ` 命中 `echo steps ok`。
  - `cd ` 命中 `mkdir_cd = 1`。
- 後果:infra 已定進表態閘(d2),假觸發會變成要表態才推得出去。實務隱患聲稱「不是改到 .sh 就整組亮」,但 S1–S29 裡 infra 的條款(S6、S11、S12、S15)全是正向,沒有一條是「無關改動不亮」。
- 缺的條款:應補反向 S 條款,例如「`.sh` 只改 echo 文字,applicable 不含 infra」,並要求觸發字帶詞界(如 `\bwait\b`、`\bkill\b`)。
severity: major
blocking: 是(照字面實作會做出誤擋的閘,而且驗收條款抓不到)

## F6 S11 的「適用題」與它給的輸入互相矛盾
spec 段落:S11,與做法 6 的 infra-timeout 觸發。
引句:「適用題應不含 vue-reactive、應改列 infra 題組。」
- 問題:輸入只有新增行 `fetch(`。infra 六題的觸發字裡沒有 `fetch(`。infra-timeout 收的是 curl、wget、docker、psql、mysql、gradlew、until、sleep。
- 實測後果:
  - 若「適用題」指 `stack_questions_applicable`,infra 會是空的,條款寫不成綠。
  - 若指 `stack_questions`(整組清單),測試成立,但 S12 說的「適用題」是另一個意思。
- 要二選一:把 `fetch(` 加進 infra-timeout(e2e 的 TS 版「沒逾時的外呼」本來就是這個場景),或把 S11 改成斷言 `stack_questions` 的鍵。
severity: major
blocking: 是(S11 是 W4 唯一的路徑類驗收,照字面寫不成測試)

## F7 風險面 `when` 的大小寫沒定,最常見的寫法會漏
spec 段落:做法 1、做法 2、做法 6(verify-infra-script)。
引句:「when 比 e2e、end-to-end、端到端、Playwright、Cypress、docker compose、起後端、起資料庫」
- 問題:`_pitfalls_stage` 用 `re.search(w, text)`,不帶旗標,大小寫敏感(約 47671 行)。既有列要大小寫不分時自己寫 `(?i)`,例如 perf-target。
- 具體例:「E2E 測試腳本要起後端」→ 預期 verify-infra-script 亮 → 小寫 `e2e` 比不到。`docker-compose.yml` 帶連字號,也比不到「docker compose」。
- 前端判準同理:`react-query`、`vite.config` 全小寫會漏,spec 的框架名都是首字大寫。
- 缺的決定:`_FE_PLAN_WHEN` 與 verify-infra-script 要不要整條 `(?i)`、連字號要不要收,spec 要寫死。S1–S6 全用首字大寫或副檔名,測不到。
severity: major
blocking: 是(題組入口在最常見寫法下不亮,而且驗收條款抓不到)

## F8 `_FE_PLAN_WHEN` 的型別與比對對象沒定
spec 段落:做法 1、做法 3。
引句:「下面的前端面全部用這一條當 when」
- 型別:`--stage --json` 會把 `facets` 整個 `json.dumps`,`when` 是字串清單。若實作成已編譯的正規式物件,JSON 輸出會拋 TypeError。spec 要寫成字串。
- 比對對象:計劃模式的 `corpus` 來自 `_pitfall_strip_spec`,會剝掉行內程式碼和 `.md/.py/.sh/.json` 檔名,不剝 `.tsx`。spec 說比「計劃全文」,但計劃模式與 `--check` 手上是剝過的 `corpus`。
- 具體例:計劃只寫「改 `src/App.tsx`」→ `--stage` 用全文,命中;計劃模式若比 `corpus`,行內程式碼被剝,不命中。同一份計劃兩個入口結論不同。
severity: minor
blocking: 否(實作者撞到會改,但兩個入口應寫明同一個對象)

## F9 計劃模式的 `--json` 和 `--check` 的 ✗ 分支沒被點名
spec 段落:做法 3,三個入口。
引句:「對前端計劃多印一行提醒」
- `--json`:`cmd_pitfalls` 計劃模式的 `--json` 會先輸出 `{hits, general, class_questions, known_pitfalls}` 就 return 0(約 47757–47760 行)。spec 只改文字輸出,JSON 讀者拿不到前端面。
- `--check` 的 ✗ 分支(命中類但缺節)在印完 ✗ 就 return 1,提醒要不要在那條路上也印,spec 沒說;S8 只測一條路。
severity: minor
blocking: 否(平行輸出路徑漏改,但不影響門判定)

## F10 W4 的跳過放哪裡,與 `_stack_changed_ok` 共用的風險
spec 段落:做法 7。
引句:「分級不因造資料的 SQL 變 high」
- `_stack_changed_ok` 在 `_pitfall_diff_collect` 同一函式裡被三處呼叫:`changed_lines` 兩處(約 47245、47254 行)給棧別觸發用,另一處(約 47259 行)給 claims 掃描用。
- 若實作者把 `_TEST_INFRA_PATH_RE` 加進 `_stack_changed_ok`,infra 檔的 `changed_lines` 也消失,S11、S12 全紅。跳過必須只加在 claims 那一處,spec 沒指名。
- 另外 `_PITFALL_DIFF_TEST_PAT`(`test_`、`.spec.`、`/tests?/`)已經把 `scripts/test_e2e.sh`、`tests/e2e/...`、`order.e2e.spec.ts` 擋在前面,這些檔拿不到 infra 題。spec 的樣式表列了 `order.e2e.ts`、`run_e2e.sh`,沒說測試命名的 e2e 檔不在範圍。
severity: minor
blocking: 否(實作者會被自己的測試擋下,但應寫明位置)

## F11 角色鏡頭:`_ROLE_FRONT_EXTS` 先於棧鍵判斷,「不再附前端卡」不完全成立
spec 段落:做法 6 末段。
引句:「e2e 腳本不是產品畫面」
- `_review_role_for` 先判副檔名:`tsx/jsx/vue/css/html` 直接回 frontend,後面才看 `_stack_key_for_file`(約 30333–30341 行)。
- 具體例:`e2e/pages/LoginPage.tsx` 仍是 frontend、仍附前端卡。只有 `.ts` 的 e2e 檔才變「判不出」。spec 沒寫這個交界,也沒有條款釘。
severity: minor
blocking: 否(影響只是前端卡多附幾次)

## F12 既有測試的釘會紅,spec 只列了一個
spec 段落:做法 6、S27。
引句:「規則指紋應等於測試釘的新值」
- `t_stack_question_triggers` 把全部題目 id 集合釘死,加 infra 六題必紅(`scripts/test_lumos.py` 約 56428 行,id 格式 `^[a-z]+-[a-z0-9]+$`,infra-* 合格)。
- `t_door_rule_version_pin` 釘 `door_rule=12` 與指紋(約 67408 行)。
- 回退與驗收段只提後者。
severity: minor
blocking: 否(全套會紅、實作者會補)

## F13 S28 的量測腳本沒進版控
spec 段落:S28、做法 9 的量法。
引句:「重跑 2026-10-15 那支唯讀比對腳本」
- `git ls-files` 在本工作樹找不到任何比對腳本,三個消費專案 repo 在本機別處。
- 後果:三個月後接手的人無法照字面「重跑」,REVISIT 2027-01-15 同樣依賴這支腳本。
- 應做:把腳本或做法 9 的最小命令寫進計劃或圖譜。
severity: minor
blocking: 否(回頭條件到期時才咬)

## F14 infra 進表態閘後,在途分支沒被討論
spec 段落:實務隱患守衛面第三條。
引句:「進閘已定(d2,編排者 2026-10-15」
- `_dispositions_verdict` 每次推送用當下範圍重算 `stack_questions_applicable`,沒有表態記錄就直接擋(約 55556 行起,「還沒有表態記錄」)。
- 上線後,任何含 `.sh` 改動、原本沒有表態的在途分支(本 repo 有 20 支 `.sh`:`get.sh`、`governance/*.sh`、`scripts/*.sh`)推送時都會多出這道門。
- spec 的守衛面只談新增手續,沒回答共同要求的「已在途分支要不要重新表態」。至少該寫「無影響」或「首次推送會被擋,處理方式」。
severity: minor
blocking: 否(一次性手續,但屬於必答的風險類)

## F15 infra 的檔案範圍比說明少
spec 段落:做法 6。
引句:「本機基礎設施腳本:起停後端、資料庫、容器的 shell 與 e2e 設定檔」
- 說明含「e2e 設定檔」與「容器」,規則只收 `.sh`、`.bash` 與 `e2e`/`fixtures`/`seeds` 路徑。
- 具體例:`docker-compose.e2e.yml` 用 `[._-]e2e(...)` 的第三支分支才會被路徑樣式抓到,但副檔名 `.yml` 在 `_STACK_PERF_QUESTIONS` 裡沒有鍵。`playwright.config.ts`、`scripts/run.zsh`、無副檔名的 `scripts/e2e` 腳本(後者路徑樣式抓得到,前兩者抓不到)則整個落空。
- 該決定要不要收、或明寫不收。
severity: minor
blocking: 否

已讀各節:做法 3 的前端面表、做法 4(範本改述)、做法 5(資安席八項,templates.md §7.8 的 `_sub_block` 切法容得下新增 ### 小節,不碰〈消費專案六類〉的逐字釘),以及做法 8、回退。已讀,無 finding。

最嚴重 severity: major;blocking 共 6 條(F1、F3、F4、F5、F6、F7)。
