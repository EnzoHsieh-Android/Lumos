severity: major

我已核對指令寫法、旗標、回傳碼、預設值和掛鉤接線,這幾項文件與真碼一致。`reread-check --help` 有 `--gate`,`drift ack --kind` 選項含 `reread`,`LUMOS_VERSION` 是 v1.3。`pre-push` 的 reread 段帶 `--gate`、回 1 擋下,其他 `pp_stop_if_signaled` 呼叫共 8 行,`ci.yml` 沒改。中途本機磁碟寫滿(ENOSPC),Bash 全部失效,後半段只能用 Read 逐段讀真碼。

下列兩項沒查成,不算已驗:
- 計劃裡 `[test:…]` 的測試名是否存在,因為沒法搜尋 `scripts/test_lumos.py`。
- 06 手冊說 `governance/drift-acks.jsonl` 屬簿記、提交不讓留痕失效,這句沒能核對。

## F1 守檔筆記計劃的〈專案開關〉仍寫預設是 warn、會印「轉擋還沒做」
severity: major
blocking: 是
引句:「沒寫、寫 null 照 warn;這一版寫 block 也照 warn 並印一句」
file: `scripts/lumos:34355`
file: `scripts/lumos:35257-35278`

1. 這句在 diff 裡是沒改到的上下文行(`守檔筆記對照改動_計劃.md` 做法第 4 節),它的鄰行都已改寫。
2. 照它做,會以為 `note_reread.gate` 沒寫是 warn、寫 block 只提醒,而且會看到一句「轉擋還沒做」。
3. 實際上 `_NOTE_REREAD_DEFAULT_GATE = "block"`,block 照實生效。`_note_reread_print` 整條印出路徑都沒有「轉擋還沒做」。
4. 這份計劃開頭寫「下面的條款改寫成不帶 `--gate` 時的行為」,但這句講的是預設值,不是不帶 `--gate` 的行為。

## F2 守檔筆記計劃的〈做法〉3 仍寫「這一版不需要表態」
severity: minor
blocking: 否
引句:「這一版不需要表態;改筆記不用重新對照(指紋只看程式那一半)」
file: `scripts/lumos:35119-35122`

1. 這句也是沒改到的上下文行。
2. `reread-record` 收尾現在會印:點出的是規則類條目,推送時會擋,要改掉或 `lumos drift ack --kind reread`。
3. 同一份計劃的 S24 和 06 手冊都已改成「要表態」,只剩這一句留著舊說法。

## F3 舊句檢查計劃的〈做法〉3、S3、S14 與〈實務隱患〉仍照舊,與新預設相反
severity: major
blocking: 是
引句:「[[Projects/舊句檢查_計劃]] 的 RETIRE-IF、2026-10-14 與 2026-12-14 兩行 REVISIT、相容性說明」
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:115`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:182`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:194`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:211`
file: `scripts/lumos:39033-39046`
file: `scripts/lumos:39212`

1. 轉擋計劃列的「要一起改的說法」對 `舊句檢查_計劃` 只列了上面這幾處。diff 也確實只動了這幾處,另外改了〈範圍〉③和〈誠實界線〉一條。
2. 還沒改的地方:
   - 第 115 行寫「設定檔讀不成 JSON → gate block、old_sentence warn」,「old_sentence 寫壞值 → warn」。
   - S3(第 182 行)寫「rc_m1 只看 old_sentence … gate 是什麼都一樣」,「寫壞值時照 warn」,綁在 `t_drift_m1_layers_and_mode`。
   - S14(第 194 行)逐字引「舊句檢查另有開關 drift_check.old_sentence,有改到程式檔時照跑」,綁在 `t_drift_m1_gate_off_wording`。
   - 第 211 行寫「預設只提醒;block 要專案自己設」。
3. 真碼不是這樣:
   - 沒寫、寫 null 或值看不懂,照 `gate`。
   - 設定檔讀不成 JSON 或不是物件,照 block。
   - gate=off 的提示句是「舊句檢查另有**明寫的**開關 …」。
4. 轉擋計劃自己也說這兩條綁定測試的斷言已改。這些條款的文字與它綁的測試、真碼都對不上。

## F4 轉擋計劃的〈回退〉承諾了一條真碼沒有的退路,與同篇〈設計〉互相矛盾
severity: major
blocking: 是
引句:「設定讀到之前的失敗改讀工作目錄設定」
file: `scripts/lumos:35151-35154`

1. 〈回退〉寫「兩道都只要把設定改成 warn 就回到提醒(掛鉤讀被推頂端的設定;設定讀到之前的失敗改讀工作目錄設定)」。
2. 同篇〈設計〉卻寫「設定讀到之前就發生的例外照預設 block … 不另設工作目錄設定的退路」。
3. 真碼 `_note_reread_guarded` 的註解也寫「不另設讀工作目錄設定的退路」。
4. 照〈回退〉做的人,遇到設定讀到之前就失敗的情況,會以為改工作目錄的設定能放行,實際上仍擋。

## F5 CHANGELOG 開頭只講「本機推送前擋」,但名稱消失檢查在 CI 也擋
severity: minor
blocking: 否
引句:「改成在本機推送前預設擋,推送前掛鉤跟著改,所以升版」
file: `.github/workflows/ci.yml:239-244`

1. CI 的 drift check 步驟回 1 就 `exit 1`。`old_sentence` 沒寫現在照 `gate`(預設 block),所以消費專案 CI 若有接 drift check,升級後會因舊句要處理而紅。
2. CHANGELOG 只對 reread 講了「CI 不受影響」。名稱消失那條沒說 CI 也會紅,轉擋計劃的「CI 維持現狀」同樣不準。
3. 08 手冊的 CI 列有寫對,所以這是 CHANGELOG 與計劃的措辭問題。

## F6 CHANGELOG 沒提 reread 在 block 時「判不了也擋」
severity: minor
blocking: 否
引句:「擋兩層——這次改程式又改到家筆記、還沒派判定者對照這一版程式的(第一層)」
file: `scripts/lumos:35229-35238`
file: `scripts/lumos:35287-35292`

1. `--gate` 加 block 時,git 失敗、30 秒逾時、判定紀錄讀不懂、起點算不出都回 1 擋下,只能用 `LUMOS_SKIP_REREAD_CHECK=1` 略過。
2. 06 手冊有寫,CHANGELOG 的升級影響清單沒有。大圖譜專案升級後若遇到逾時會被擋,CHANGELOG 沒預告。

## F7 README(中英)把名稱消失檢查寫成「函式刪了或檔名改了就擋」
severity: minor
blocking: 否
引句:「Pushes are blocked if deleted functions or renamed files are still mentioned by their old names or paths」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:159`

1. 實際只會擋 Python 的定義名和旗標、被刪的程式檔路徑,而且只擋「這次改到的程式檔的家筆記或摘要行」。其他地方只列出,不擋。
2. 非 Python 專案刪函式,README 讀起來像會擋,實際不擋。中文 README 第三道有同樣的寫法。

## F8 手冊與索引的 `drift ack` 種類說明沒補 `reread`
severity: minor
blocking: 否
引句:「表態要提交才算;回頭條件與撤除條件的照留記期限或綁的那篇;c2、c3 會記下當時連著的已收尾計劃」
file: `skills/lumos-project-notes/commands/INDEX.md:36`

1. 04 的「這一行確定照留」列和 INDEX 第 36 行只講 m1 的 `--name` 和 retire,沒提 `--kind reread`。
2. 06 手冊有講,所以不會讓人做錯,只是從 04 或索引找不到這個種類。

## 筆記格式(鏡頭 3)

- 新增兩條 RULE 欄位齊全:`[依據:人]`、`[since]`、`[retire:人裁]` 加 `[until]`、`[confirmed]`。
- 被取代的舊 RULE 有 `[status:superseded][被取代:[[…]]]`。
- 新增的 WHY 都有 `[出處:]` 和 `[因:]`。
- 各 `[closed:…]` 理由只有純路徑文字,沒有 `[[連結]]`,符合手冊 03 的規定。
- 沒找到違規。

## 圖譜鏡頭(固定席)

- 存量漂移守衛:diff 把「m1 沒寫是 warn、不跟 gate 走」那條舊 RULE 正確標作廢並補了新 RULE,與轉擋後的行為一致。與本節點宣稱的行為沒有矛盾。
- 筆記內容審:reread 段的行為已改成帶 `--gate` 擋兩層,內文同步更新,與真碼一致。
- bound-tests-gate:`pp_stop_if_signaled` 仍是 8 行,段落已改成「六道會擋的閘」,與 hook 一致。
- README圖產生器:只新增 2026-10-09 一條記事,中英兩版圖與替代文字也一起改了。沒有與節點矛盾,產生器本體在程式那一半,不在本席範圍。
- guard-kill、lumos-cli-read(兩條 ★INVARIANT★)、code-loop守衛main-direct盲區、筆記內容閘、pitfalls-code-loop、每支檔有家:這份文件段沒有碰到它們宣稱的行為或合約。
  - 搜尋預設排除 superseded 但不排除 stale。
  - guard kill 的回傳碼優先序。
  - `--json` 輸出純度。

最高嚴重度:major(F1、F3、F4)。
