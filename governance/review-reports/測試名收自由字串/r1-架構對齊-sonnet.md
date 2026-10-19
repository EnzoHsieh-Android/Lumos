severity: major

審查對象是 `測試名收自由字串_計劃` 的 r1 快照,對照的是 web-gaps 工作樹的 `scripts/lumos` 與圖譜 Systems 節點。以下 file:行號都出自 web-gaps 工作樹。

## 1. 分層與依賴方向

大方向對得上,但有一處是「同一件事兩個寫法」。

整份計劃把名稱合法性收成一支 `_test_name_ok`,取代三種分散的判法,方向跟既有做法一致。判法目前有三份:
- `_KILL_METHOD_OK_RE`:`scripts/lumos:18003`
- 綁定路徑上的 `IDENT_RE`:`scripts/lumos:16850`
- `_NsTrJudge._plat` 自己寫的方括號判斷

`_run_cmd_expand` 加 `name_filter` 參數也順著既有結構。它本來就是 guard kill、合約測試閘、過濾探針三處共用的展開點(`scripts/lumos:19219`、`19561`、`54367`、`54418`),呼叫端各自傳平台設定,沒有跨層直呼。

`name_filter` 這個 profile 鍵跟 `comment_strip`、`file_name_match`、`scaffold_name` 這些靜態鍵同形(`scripts/lumos:5826`),沒問題。

**finding 1**
severity: minor
blocking: 否
- 計劃第 6 節「歸檔」與「`guard trace`」兩處要改的邊界規則,既有程式有兩種寫法。
- 一種是 ASCII 模式 `\b` 加 `re.escape`:`scripts/lumos:929`、`20460`、`24493`。
- 另一種是 `_strip_test_comments` 那類共用輔助。
- 計劃說「兩處改用同一支邊界規則」,但沒指名新函式放在哪、舊的 `\b` 其他呼叫處(`scripts/lumos:929`、`20460`、`24493`、`45895`、`45919`、`45920`、`48015`)是否照舊。
- 這樣會變成專案裡同時有「頭尾英數才加邊界」和「一律 `\b`」兩套邊界。
- 建議在計劃寫明:新函式只管測試名,其餘 `\b` 呼叫不動,並在新函式註解標註適用範圍。
引句:「兩處改用同一支邊界規則(名稱頭尾是英數底線才加「前後不是英數底線」,否則不加),不各寫一份」

## 2. 命名與錯誤處理

命名跟著現有慣例走:底線開頭的內部函式,`_test_name_ok`、`_test_name_of_match`、`_apply_test_overrides`。`_apply_test_overrides` 的抽法也對得上 `load_test_profile` 現有的覆蓋段(`scripts/lumos:5880`)。

訊息形狀的缺口:

**finding 2**
severity: minor
blocking: 否
- 新增的壞名訊息(名稱有冒號要寫平台前綴)、含逗號提示、`guard scaffold` 擋下訊息,計劃只給了一句話,沒有照三段式(發生什麼、為何在意、指令獨立一行)寫。
- 既有的 `resolve_test_refs` 壞前綴訊息(`scripts/lumos:6011`)和 `_clause_check` 的訊息(`scripts/lumos:8525`)都是「發生什麼 + 下一步指令」形狀。
- 這幾條是新增訊息,實作時要依三段式落字。建議在計劃寫明即可。
引句:「壞名訊息補一句這個寫法。單平台照舊整串當名字。」

**finding 3**
severity: minor
blocking: 否
- `_clause_check` 現在印 `✓ — N 條全標(…懸空 k 只提醒不擋…)`,計劃改成 `⚠` 並逐條列出。
- 既有同函式內的失敗行用 `✗ — …` 加縮排補充行(`scripts/lumos:8525` 起)。
- `⚠` 不是這個函式既有的狀態符號,而且 status 仍回 `ok`,輸出符號和回傳狀態對不上。
- 需要在計劃說明:status 維持 `ok` 但輸出改 `⚠` 是刻意的,並確認呼叫端(處置閘第五步、規格閘)不會用 `✓` 字樣比對。
引句:「改成:有懸空就印 `條款綁定: ⚠ — N 條都有標,其中 k 條懸空(綁的測試找不到)`」

## 3. 第二種做法

沒有引入新解析器,多數處理沿用既有:
- 反引號名稱拆殼沿用 `_kill_norm_method`(`scripts/lumos:18461`)。
- 使用者自訂 regex 沿用 `_safe_user_regex`(`scripts/lumos:5984`)。
- shell 引號沿用 `shlex.quote`。

有兩處值得提:

**finding 4**
severity: major
blocking: 是
- 計劃明說「JS 不能剝字串」,所以 JS/Playwright/Dart 的字串字面要原樣留著抓名字。
- 但 `discover_test_methods` 先跑 `_strip_test_comments` 的 c-style(`scripts/lumos:6264`),它用 `//[^\n]*` 剝註解,完全不認字串。
- 句子名只要含 `//` 或 `/*`,例如 `it('GET http://x 回 404')`,名字會在掃描前被截斷。計劃要求整串比對,所以這種名字會變成永遠懸空。
- 專案裡 Java 已有 `c-style+strings` 模式專門處理這類「字串影響掃描」(`scripts/lumos:6264`、`6290` 一帶的註解)。
- 計劃既沒採用該模式,也沒講明這個限制。
- 這是「第二種做法」:字面抓名字卻不處理註解剝除與字串的先後。
- 建議二選一:
  - 在做法 2 補一節,說明 JS 三家的剝法(例如先掃字串字面再剝註解),並新增驗收條款。
  - 把「含 `//` 或 `/*` 的名稱不收」寫進〈不做〉。
引句:「JS 不能剝字串,否則名字就沒了」

**finding 5**
severity: minor
blocking: 否
- 計劃新寫一支 `_test_name_ok`,把 `-` 開頭、控制字元、`[ ] ,` 的判斷集中起來,這個方向對。
- 但專案已有路徑與控制字元的共用謂詞:`_NOTE_REREAD_CTRL_CATS`(`scripts/lumos:38104`)和 `_esc_clean`(`scripts/lumos:13225`)。
- 計劃沒說明控制字元判法是否復用它,還是另寫一份。
- 建議計劃指明「控制字元判法呼叫既有謂詞」,以免出現第三份控制字元定義。
引句:「去頭尾空白後不是空的、至多 200 字、沒有控制字元與換行、不以 `-` 開頭、不含 `[` `]` `,`(半形逗號)。」

## 4. 落點

**finding 6**
severity: major
blocking: 是
- 計劃 `lands_in` 列了 `Systems/lumos-guard`,理由是「guard 那組落在 lumos-guard 與 guard-kill」。
- 實際讀該節點:
  - 它的 `responsibility` 是「審查席隔離外掛:認出派工詞第一行帶 LUMOS-SEAT 的子代理……」。
  - `about_code` 全是 `mods/claude/lumos-guard/...` 的 TypeScript 外掛檔。
  - 它跟 `lumos guard bind/scaffold/settle/trace` 這些 `scripts/lumos` 的子命令完全無關。
- 計劃要改的是 `guard bind`、`guard scaffold`、`guard settle`、`guard trace` 的程式碼,位置在 `scripts/lumos`。
- 這些子命令目前沒有專屬節點,散在 `Systems/guard-kill`(主要談 kill)與 `Systems/lumos-cli-write`(提到 `guard bind` 一次)。
- 照計劃寫進 `lumos-guard`,會讓說明落在「管外掛」的節點,違反「節點只准寫自己家的檔」。
- 建議把 `Systems/lumos-guard` 從 `lands_in` 拿掉。`guard bind/scaffold/settle/trace` 的說明改落在實際擁有該行為的節點,或另開 `lumos guard` 子命令族的節點;要不要另開由編排者裁。

**finding 7**
severity: minor
blocking: 否
- `lands_in` 其餘節點的歸屬基本合理:
  - `規格閘`:規格閘一行與跑測試行。
  - `bound-tests-gate`:推送前合約測試閘。
  - `筆記內容閘`:note-shape 與 doctor S20。
  - `guard-kill`:guard kill 配方檢查。
  - `test-profile-multiplatform`:`TEST_PROFILES`、`load_platforms`、`resolve_test_refs`。
- 但 `scripts/lumos` 同時掛在這五篇的 `about_code`,所以「每支檔有家」成立,只是歸檔(`cmd_archive`)與 `guard trace` 的改動也沒有被任何一篇 `lands_in` 明確接住。
- 計劃要補一句這兩處說明寫進哪一篇,否則提交時 pre-commit 的「改 code 沒動圖譜」會卡在不知道寫哪裡。
- `guard-kill.md:30` 已有 `guard settle` 的 WHY 行,`settle` 可寫進 `guard-kill`。
引句:「guard 那組落在 [[Systems/lumos-guard]] 與 [[Systems/guard-kill]]。」

不對齊共 7 條,其中 major 2 條
