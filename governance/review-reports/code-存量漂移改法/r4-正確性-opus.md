severity: major

# 代碼審 r4 正確性-opus(存量漂移改法,r3 修正本身)

審材:governance/review-reports/code-存量漂移改法/r4-snapshot.patch(逐 hunk 讀完)。實驗全在自己的 `git clone --shared` 臨時目錄(工具鏈 clone 與 rtb 三個工作樹的 clone)裡做,直譯器 /opt/homebrew/bin/python3(3.14);標準 YAML 讀法用 PyYAML 6.0.3 與 Ruby Psych 3.1.0 兩家對照。

## F1 c4 改成整項換掉之後,掃描提示與證據頁仍教人給「片段」,照著做會把那一項其餘的前提整段刪掉
severity: major
blocking: 是
引句:「f'--new {_drift_sh(ev["template"])}', 600))」
file: `scripts/lumos:27642`
file: `scripts/lumos:27947`
file: `scripts/lumos:27959`

1. 形狀換了(--new 是「整項新內容」),但產生提示的單一來源 `_drift_fix_hint` 的 c4 那行沒改,drift scan/check/doctor 印的仍是 `--old "<原片段>" --new "<新片段>"`;證據頁印的範例指令把範本句(「提交 <sha>;代碼審見 <卷證>」,原本設計成替換「還沒提交」那一小段的片段)直接當 `--new`。兩處都跟新語意不符,這是內部不一致。
2. 實際後果:rtb 目前 3 筆真實 c4(rtb-mainwt、rtb-notes-drift、rtb-lumos-update 三個工作樹都是這 3 筆)全是單行 `valid_under: 僅 Phase 14 增量 … 本工作樹(未提交、未過代碼審);全套測試、宣稱驗證器、ruff、mypy …` 這種形狀——「未提交」只是一長串前提裡的一小段。照證據頁把範本填好就跑,整條前提被換成範本句,rc 0、沒有任何警告。
3. 重現(在 `git clone --shared ~/rtb-mainwt` 的臨時目錄裡,用 r4 的 scripts/lumos):
   - `lumos drift scan` 第 82 行:`lumos drift fix Verification/Phase14增量2b驗證紀錄 5 --kind c4   # 先看證據與範本,再加 --old "<原片段>" --new "<新片段>"`
   - `lumos drift fix Verification/Phase14增量2b驗證紀錄 5 --kind c4 --old "(未提交、未過代碼審)" --new "提交 b2fc5122f100;代碼審見 governance/review-reports/code-phase14"` → `✓ drift fix c4 … valid_under 第 1 項整項換成 --new`,rc=0
   - `git diff`:
     `-valid_under: 僅 Phase 14 增量 2b 本工作樹(未提交、未過代碼審);全套測試、宣稱驗證器、ruff、mypy 與 Phase 13 評估 72 筆錄製離線重播;入庫展示錄製因政策升版有 8 筆模型說明找不到錄製`
     `+valid_under: "提交 b2fc5122f100;代碼審見 governance/review-reports/code-phase14"`
   驗證紀錄的「在什麼前提下成立」(跑了哪些測試、8 筆找不到錄製)整段消失;修復帳還記 template_used 為真,等於工具鼓勵這個用法。
4. 工具鏈自己的 2 筆 c4(`Verification/2026-08-24_節點還原SOP落地.md` 第 5 行也是同形狀的長單行值)同樣會被照範本清掉。舊形狀(換片段)下同一條指令只換那一小段,所以這是這次換形狀引入的回歸,不是既有行為。

## F2 「值跨行、工具不改」的判定只看緊鄰的下一行,另有三種寫法照樣整項改寫,寫出標準 YAML 整段讀不了的開頭欄位
severity: major
blocking: 是
引句:「if nxt.strip() and nxt[:1] in " \t" and not re.match(r"^[ \t]*-[ \t]", nxt):」
file: `scripts/lumos:27991`
file: `scripts/lumos:27996`

1. 這次換形狀宣稱「語法全由工具決定」、「值跨行的工具不改」,但 `_drift_c4_item` 只判下一行,而且下一行只要是 `-` 開頭(不看縮排)就放行;開頭字元擋單也漏了 `#`。下面三個輸入在改寫前標準 YAML 讀得出來、本工具也列成 c4,`drift fix` 全部 rc 0 寫入,寫完 PyYAML 與 Ruby Psych 都直接報語法錯(整個開頭欄位讀不了,Obsidian 屬性面板會壞):
   - (a) 項目與接續行之間隔一個空行:
     `valid_under:` / `  - 本工作樹(未提交)` / `` / `    接續的一行` / `  - 第二項`
     改寫前 YAML 讀成 `['本工作樹(未提交)\n接續的一行', '第二項']`;`drift fix … --old "本工作樹(未提交)" --new "已提交 abc"` 後 → `ParserError while parsing a block collection`。
   - (b) 接續行比項目更深、以 `- ` 開頭:
     `  - 本工作樹(未提交)` / `    - 另見 CI`
     改寫前 YAML 讀成 `['本工作樹(未提交) - 另見 CI']`;改寫後 → `ParserError`。
   - (c) 欄位名那一行是註解、清單在下面:
     `valid_under: # 以下前提都在未提交的工作樹上量` / `  - 全套測試` / `  - ruff`
     本工具把註解讀成值(c4 第 5 行),YAML 讀成 `['全套測試', 'ruff']`;`--old "以下前提都在未提交" --new "已提交 abc"` 後變成 `valid_under: "已提交 abc"` 緊接兩行清單項 → `ParserError while parsing a block mapping`。欄位名那一行本來就不可能有接續的清單項,`-` 開頭的下一行不該放行;`raw[0]` 擋單也沒有 `#`。
2. 重現:在 `git clone --shared ~/rtb-production-agent-demo` 臨時目錄的 Verification/ 下各寫一篇(type: verification、status: pass、date,valid_under 如上)、提交,`lumos drift scan --json` 確認列為 c4(ZB 第 6 行、ZC 第 5 行、ZD 第 6 行),照上面參數跑 `drift fix`,三筆都印 `✓ drift fix c4`;之後 `python3 -c "import yaml; yaml.safe_load(open(F).read().split('---\n')[1])"` 三筆都丟 ParserError(改寫前都讀得出)。
3. 寫入後的自驗只用本工具的讀法(`after[diff[0]] != new`、`check` 比 as_list),所以這三種全部驗過;這正是換形狀要根除的「兩種讀法不同、自己的讀法驗不出」那一類,只是換到結構判定這一層。

## F3 Env.find 剝掉 ./ 之後沒有斜線就退回用檔名猜,./-x 仍會找錯篇,`lumos set ./-x` 寫到別篇
severity: minor
blocking: 否
引句:「a = a[2:] if a.startswith("./") else a」
file: `scripts/lumos:700`
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:43`

1. 家節點寫「drift fix 與一般查找都把 ./ 開頭當明確路徑」,但 Env.find 只是剝掉 `./`:`./-x` 剝完是 `-x`、沒有 `/`,直接走 by_stem 猜,同名好幾篇時印「同名筆記,取第一個」;取第一個是照排序,資料夾名排在 `-x.md` 前面的(例如 `+old/`)會被選中。drift 的提示正是對根目錄 `-` 開頭的節點印 `./-x`(計劃收尾的「看:lumos context ./-y」)。
2. 重現(rtb clone):根目錄 `-x.md` 與 `+old/-x.md` 兩篇 → `lumos context ./-x --brief` 印 `⚠ 同名筆記 2 個,取第一個: +old/-x.md`、內容是 +old 那篇;`lumos set ./-x status resolved` → `✓ set +old/-x.md: status 已改成 resolved`,根目錄那篇沒動。
3. 同一個 `./X` 在 `_drift_fix_target` 是「根目錄那篇,找不到就報錯」,在 Env.find 是「任一資料夾的 X」,兩處查找對同一寫法的解讀不同。r3 測試 ④ 的 context 那格用的是帶斜線的 `./-d/z`,根目錄 `./-x` 這種沒測到。

## F4 衝突合併中的筆記,乾淨檢查報成「有 3 種 Unicode 拼法的檔並存」
severity: minor
blocking: 否
引句:「return f"{repo_rel} 這個名字在 git 裡有 {len(ps)} 種 Unicode 拼法的檔並存」
file: `scripts/lumos:27767`

1. `_drift_git_paths` 用 `git ls-files -z` 收全部相符項目,合併衝突時同一路徑在索引裡有 stage 1/2/3 三筆,`git ls-files` 會印三次;`len(ps) > 1` 就被當成 Unicode 拼法並存。原本 `_guard_raw_git_path` 取第一筆、再走 diff 判成「有未提交的改動」,訊息是對的。
2. 重現:臨時 repo 做出 f 的合併衝突後,`_drift_git_paths(repo, "f")` → `['f', 'f', 'f']`,`_drift_fix_clean_err` → `f 這個名字在 git 裡有 3 種 Unicode 拼法的檔並存,工具分不出要改哪一篇;先手動整理成一篇`。一樣擋下(不會寫壞),但叫人去找不存在的重複檔;去重後再數就行。

## F5 --literal-pathspecs 只加在印給人看的指令,工具自己的乾淨檢查仍把檔名裡的 * 當萬用字元
severity: minor
blocking: 否
引句:「r = _lens_git(root, "diff", "--quiet", "HEAD", "--", gp)」
file: `scripts/lumos:27769`

1. r3 修正替印出的 git 指令加 `--literal-pathspecs`(檔名裡的 `*` 不被展開),同一個原樣路徑拿去跑乾淨檢查的 `git diff --quiet HEAD -- <路徑>` 沒加,也沒設 GIT_LITERAL_PATHSPECS。
2. 重現(rtb clone):提交 `Issues/q*.md`(open、連到已收尾的 Phase9 計劃,是 c2)與 `Issues/qz.md`,只改 qz.md 不提交 → `lumos drift fix 'Issues/q*' 3 --kind c2 --close --status done --reason "這次真的修好了"` → `擋下:…Issues/q*.md 有未提交的改動`,rc 2;`git diff --quiet HEAD -- …/q*.md` rc 1,加 `--literal-pathspecs` rc 0。方向是誤擋(目標檔本身一定在比對範圍內,不會誤放),訊息指錯篇。⚠ c1 推轉正日期的 `git log -G … -- <路徑>` 同樣沒加,可能把別篇的轉正日期算進來(不在本 patch 的 hunk 內,沒另外重現)。

## 其他鏡頭逐項結論(沒出 finding 的部分)

- `_yaml_quote` 選引號:沒有雙引號、沒有反斜線就用雙引號,不然沒有單引號就用單引號,兩種都有就擋;`--new` 另擋控制字元與看不見的格式字元(Unicode 類別 C 開頭,含 U+FEFF、U+200B、U+0085、代理與非字元)、頭尾空白(str.strip 含全形空白與 NBSP)、分行字元。我逐一試了 `a: b`、`[x]`、`- x`、`#註解`、`*alias`、`true`、`|`、`已提交 "abc" ok`、單獨的 `"`、`'`、`\`,本工具讀法(剝頭尾一層引號、不解跳脫)跟標準 YAML 的雙引號(沒有反斜線就沒有跳脫)與單引號(沒有 `'` 就照字面)讀出來一樣。問題不在加引號,在 F2 的結構判定。
- 保留前綴:列表項保留原本的 `[ \t]*-[ \t]+`(原縮排、tab、`-` 後多個空白照留),值本身是本工具讀得出的列表項才會被列成 c4,前綴不變所以不引入新差異;tab 縮排的項目本工具本來就讀不到、不會被列。欄位名那一行統一寫成 `valid_under: `,冒號後沒空白、有 tab 的都順便修正。
- 真實 c4 有沒有被新規則擋掉:工具鏈 2 筆(雙引號長項、單行長值)與 rtb 3 筆(單行長值)都不含行內清單、區塊文字、行尾註解、跨行,新規則不擋,都修得了;代價是 `--new` 要整條重打(見 F1)。
- `_drift_fix_target` 的 explicit:`./-x` 在 r3 前會被剝掉之後改用檔名猜(同名就報錯),現在只認根目錄那篇,r3 測試 ④ 還原會翻紅。行為變化只有一處:`./X` 在 X 只在子資料夾時,以前找得到,現在報「找不到」——方向是拒絕,不寫錯檔。
- `_drift_git_cmd`/`_drift_git_hint`:三處印指令(驗證失敗、帳寫不進去、成功後的 git add)都改走原樣路徑、不截斷,路徑含控制字元就改印說明;`git failed` 時退回索引鍵。上面沒看到新問題(git add 那條沒有 `--`,路徑以 `-` 開頭會被 git 當選項,但圖譜在 docs/ 下時 repo 路徑不會以 `-` 開頭,沒找到實際會踩到的專案,不列)。
- `_plan_for_loop` 改用 `_nfc_child`:第一段先直接找 NFC 名稱,找不到才逐項比 NFC;舊版建 dict 同 NFC 名取最後一個、新版取第一個,只有同一資料夾裡同時有兩種以上非 NFC 拼法才分得出差別;OSError 與不是資料夾的處理相同。行為等價。
- `_sh_quote` 搬到檔頭:內容沒變,檔頭的 SPDX 與 MIT 全文沒動。
- 佔位字正則拿掉 `<小寫/小寫>`:c3 的狀態清單照貼進 `--status` 會被狀態列舉擋下,拿掉它不會放掉佔位字;加上「整項新內容」對應 skills 04 印的佔位字。
- 測試有沒有走到被測分支:r3 ① C1/C2 斷言訊息含「行尾註解」「跨到下一行」,證明真的走到 `_drift_c4_item`;C3 斷言改寫結果;② 接線那格的替身同時也替掉了乾淨檢查的查詢(回傳不存在的 NFD 路徑,`git diff` 回 0,乾淨檢查照放),不影響它要驗的成功訊息;③ 直接呼叫;④ `./-x` 在修正前會報同名,確實翻紅;c4 ⑤b 用 rc 0 加讀回比對加每一行都是 `_yaml_quote` 的寫法,不經 `_yaml_quote` 直接寫會紅。缺的是 F2 的三種寫法與 F3 的根目錄 `./-x`。
- 角色卡:派工詞尾端只有 `LUMOS-ROLE-CARDS: on` 這一行,沒有附角色卡內容,無從逐條對照。

## 圖譜鏡頭固定席逐條判定

- Systems/lumos-cli-read(search 預設排除 superseded、不排除 stale):本 patch 只動 Env.find 的 `./` 剝除,沒碰 search 的濾網與分岔,不影響。Env.find 的查找問題見 F3,跟這條合約無關。
- Systems/guard-kill(rc 優先序、--json 純度):沒碰 guard kill 的任何路徑,不影響。
- Systems/lumos-cli-lifecycle(re-inject 只改 sentinel 之間):沒碰注入,不影響。
- Systems/bound-tests-gate(固定席綁定測試逐支真跑):只在家節點 TEST 清單多一支 t_drift_fix_review_r3_edges,測試索引裡也有這支,不影響閘的判定邏輯。
- Systems/授權與歸屬(授權檔不進白名單、主程式檔頭帶 SPDX 與 MIT):`_sh_quote` 搬到第 397 行附近,檔頭 1–390 行沒動,白名單沒動,不影響。
- Systems/測試假綠形態(翻紅釘要有前置斷言證明現場成立):新測試格大多用「訊息含特定字」或「rc 0 加讀回」當現場證明(見上一節);② 接線那格的替身讓乾淨檢查變成恆過,但它要驗的是成功訊息,不算假綠。沒違反。
- Systems/design-loop(處置閘第五步):沒碰 loop status 與處置閘,不影響。
- Systems/pitfalls-code-loop:沒碰 pitfalls 分級,不影響。
- 其餘只列名的節點(loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛、lumos-deinit 等):patch 的 hunk 沒有碰到它們管的函式(`_drift_*`、Env.find、`_plan_for_loop`、`_sh_quote` 位置除外),`_plan_for_loop` 行為等價、`_sh_quote` 內容不變,判不影響。

最高等級:major
