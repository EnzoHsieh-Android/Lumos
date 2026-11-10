severity: major

我把這份投稿當作「第 2 版修訂稿」逐節讀過。實驗放在 `/private/tmp/lumos-seat-work/簡報審查抓到的機制缺口/正確性-sonnet/`:`exp1` 是拋棄式 git repo,`exp2` 是 ast-grep 規則實驗,`probe.py` 是呼叫 `_pitfall_diff_collect` 的探針。依規定由編排者收貨後刪,我沒動。

## 發現

**1. 範圍 2 沒指定「改到的檔」從哪來。`_pitfall_tier` 實際收到的清單會漏檔也會重複檔,高風險路徑照字面做會漏判。**
severity: major
blocking: 是——判高風險路徑的守衛對刪檔、二進位、改名、改模式整批靜默放行。
引句:「這次改到的檔只要有一支等於清單裡的檔、或在清單裡的目錄底下,就判 high」
- file: `scripts/lumos:65147` 和 `scripts/lumos:65214` 傳給 `_pitfall_tier` 的是 `list(added) + list(changed_lines)`。`added` 只收有 `+` 行的檔;`changed_lines` 還要過 `_stack_changed_ok`,會排除 `.md`、`.json`、測試檔等。
- 重現:`exp1` 的 main 設 `risk_high_paths=["src/auth","config/permissions.json","docs/policy.md","keys","deploy.sh"]`。分支上做以下五件事,每件都落在清單內,探針量到 `files=[]`、`tier=light`:
  - 整檔刪 `config/permissions.json`。
  - 整檔刪 `docs/policy.md`。
  - 改二進位 `keys/release.keystore`。
  - `chmod +x deploy.sh`。
  - 純改名 `src/auth/Moved.kt` 到 `lib/Moved.kt`。
- 其他三種輸入:
  - 只刪 `docs/policy.md` 一行,`files=[]`。
  - 改名加小改,`files=['lib/Moved.kt','lib/Moved.kt']`,舊路徑(在高風險目錄裡)根本沒出現。
  - 改 `src/auth/Login.kt` 並加行,同一檔列兩次。
- 重複會讓「最多 3 支檔名,超過寫等 N 支」的 N 與顯示都錯。spec 沒說要去重。
- 姊妹函式 `_residual_tier_hits` 自己跑 `git diff --name-only -z --no-renames` 取檔名,正是為了避開這個缺口。
- 先紅測試 `t_pitfall_tier_risk_paths` 是手寫 `files` 直接呼叫 `_pitfall_tier`,不走 `pitfalls --diff`,抓不到這個洞。

**2. 範圍 2 讀「範圍起點那一版」的清單,分兩次推送就能自己降級。這是本 repo 已有慣例明文要防的形狀。**
severity: major
blocking: 是——spec 自己宣稱的不降級,拆兩次推送就破功,且不留任何高風險理由。
引句:「範圍起點那一版與終點那一版(終點是工作目錄時讀工作目錄)的清單取聯集」
- 重現(spec 沒寫、我沒有實作可跑,從設計推演;`exp1` 只驗證了清單來源那一半):
  1. main 設 `["src/auth"]`。
  2. 分支提交 A 把清單清空。只動 `.lumos/config.json`,分級是 light,推送通過。
  3. 提交 B 改 `src/auth/Login.kt`。第二次推送起點是遠端分支頂端 A,A 的清單已空,聯集為空,只判 standard。
- 這與 spec 的宣稱(同一次改動拿掉某條路徑不會讓自己降級)、不做段的「人工不能把分級往下調」互相打臉。
- 本 repo 對同一類問題的既有做法:
  - 殘留索引明寫「拿掉殘留,分兩次推送也躲不掉」,另有 removed、shrunk 兩種升 high 理由。見 file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:73`。
  - 讀宣告一律走 `_lens_trusted_ref` / `_trusted_decl_ref`,讀「起點與主線的分叉點」,理由是推分支時起點是遠端分支頂端、不在主線上。見 file: `scripts/lumos:63651`。
- PRIOR-ART 只說借用 `_e2e_norm`、`_e2e_under`,沒提這條既有慣例。

**3. 範圍 3 認工具的規則,對常見的版本釘選與包裝寫法會靜默認不到,忽略註解整條命令不數。**
severity: major
blocking: 是——不是「換了別的工具」,是表內工具換個常見呼叫寫法就整個繞過,而且沒有任何提示。
引句:「第一個詞是 `npx`、`bunx`、`uvx` 時看下一個非選項的詞」
- 下列宣告字面上取到的詞與表內名字不等,該命令的忽略註解掃到 0 條:
  - `npx eslint@8.57.0 {LINT_FILES}`:取到 `eslint@8.57.0`。
  - `uvx ruff@0.6.9 check …`:取到 `ruff@0.6.9`。
  - `uvx --from ruff==0.6.9 ruff check …`:取到 `ruff==0.6.9`。
  - `pnpm dlx eslint`、`poetry run ruff`:不在 spec 的包裝詞清單。
  - `./gradlew ktlintCheck`:detekt 走 Gradle 任務會被 `_detekt_segment_codes` 認到,ktlint 沒有對應判斷。
- file: `scripts/lumos:40588` 的 `_cmd_basename` 只切 `/` 與 `\`,不剝 `@版本`。
- spec 對「路徑寫錯被靜默略過」引了 CODEOWNERS 的教訓,所以對不到的路徑會印一行;但命令認不出工具時沒有同類提示。
- 天花板那條只講「表外工具與新語法」,沒涵蓋「表內工具、換呼叫寫法」。

**4. 驗收條款 S1 與預期值表沒把「巢狀類別」那半句釘死,照字面犯的錯能全綠過關。**
severity: major
blocking: 是——spec 範圍 1 明寫「Activity 本身照報」,但沒有任何樣本或條款會對錯誤實作翻紅,等於這句話沒綁測試。
引句:「外圍類別任一層是 Service 就豁免,所以 Service 裡的內部類別也豁免、Activity 裡的內部 Service 類別也豁免、Activity 本身照報」
- 在 `exp2/t.kt` 放五個類別:Service、Fragment、Activity、Activity 內的 Service、Service 內的 Fragment,各有一處 `lifecycleScope.launch { x.collect {} }`。
- 規則寫成 `not inside class_declaration has delegation_specifier`(只看直接子節點)時,報在 Fragment(行 8)與 Activity(行 11)。
- 把 `has` 加上 `stopBy: end`(會往 class body 裡鑽到內部 Service),只報 Fragment(行 8),Activity 被誤豁免。
- 第二種寫法能通過 S1 列出的全部輸入:Service、Fragment、`Q : Fragment(), MediaSessionService.Listener`、ProcessLifecycleOwner Fragment。
- 現有 bad 樣本檔也沒有「Activity 內含 Service」。

**5. `@Suppress` 的判法對多行與小寫名沒交代。**
severity: minor
blocking: 否——是判準模糊,不是已知必錯;但落在新增告警閘要擋的主場。
引句:「只數括號裡有工具規則名的那些;編譯器警告名(全大寫底線)不算」
- 輸入一:`@Suppress(` 後換行再列 `"MagicNumber",`、`"LongMethod"`。逐行掃時第一行括號內沒有字串,「全是全大寫」成了空集合為真,可能被當成編譯器警告名放掉。
- 若改成算,告警只落在 `@Suppress(` 那一行,指紋(規則+檔+片段)等於 `@Suppress(`。同檔一次放行就涵蓋之後所有多行 `@Suppress(`,比 spec 已承認的「同一行複製貼上」嚴重,因為它們內容不同。
- 輸入二:`@Suppress("unused")` 是 Kotlin 編譯器/IDE 警告名但不是全大寫,會被當成工具規則名多擋。

**6. 對照表缺少同一批工具的行內設定式抑制,REVISIT 只涵蓋「工具新增語法」。**
severity: minor
blocking: 否——寫法沒被表列到,不是新設計錯,但與天花板的歸因不符。
引句:「忽略註解只認對照表裡的工具與寫法;換一種寫法(例如工具新增的抑制語法)就認不出」
- 表內工具的這些寫法都認不到:
  - eslint 的 `/* eslint no-console: off */`。
  - mypy 的 `# mypy: ignore-errors`、`# mypy: disable-error-code=…`。
- 這些是既有語法,不是「新增」,REVISIT 2027-05-09 只核對工具菜單,不會補。

**7. 範圍 2 的插入位置與「不互相蓋掉」互相衝突。**
severity: minor
blocking: 否——只影響理由文字,分級本身仍是 high。
引句:「在殘留索引那一步之後、風險型樣那一步之前,讀 `risk_high_paths`」
- file: `scripts/lumos:64523` 的 `_pitfall_tier` 現在是 `if why: return high` 後直接回傳,`if claims: return high` 也直接回傳。
- 照字面「在殘留之後插入」做,殘留命中時會在高風險路徑那步之前就回傳,路徑理由與「risk_high_paths 讀不出」整句消失。
- 要滿足「並存不蓋掉」得重排結構,spec 沒說,測試也沒有並存案例。

**8. 「讀不出」的狀態定義不全,「方向一致」的宣稱也不準。**
severity: minor
blocking: 否——是行為待定,不是必然誤判。
引句:「跟殘留索引讀不出的方向一致」
- 殘留索引的做法:起點版內容壞掉(bad)照舊不升 high,只有「git 讀不出」才升。
- spec 只列「JSON 解析失敗、不是字串清單、超過 200 項」,沒分:
  - 解析失敗發生在哪一版(起點壞、終點已修好的修復推送會被誤升)。
  - git 讀不出(淺層 clone、物件遺失)算不存在還是讀不出。
  - 頂層不是物件。
  - 開頭有 BOM。
- 可重用的 `_lumos_config_at_ref` 已有 ok/missing/unreadable/git-failed 四態(`scripts/lumos:63624`),spec 沒指定用它。

**9. 「任一層」豁免會豁免巢狀在 Service 裡的 Fragment 或 Activity。**
severity: minor
blocking: 否——spec 是明文選擇,實際出現機率低。
引句:「所以 Service 裡的內部類別也豁免」
- 輸入:`class S : LifecycleService() { class DebugFragment : Fragment() { … lifecycleScope.launch { x.collect {} } } }`。
- `exp2` 實測行 18 不報。「畫面類別」被「外圍是 Service」蓋過。

**10. 「對不到任何檔」那行的語意與成本沒寫全。**
severity: minor
blocking: 否——只影響提醒行與效能估算。
引句:「清單裡某條路徑在終點那一版一支檔都對不到時」
- 終點是工作目錄時要列哪一版的樹,spec 沒寫(先紅測試用 `"HEAD"`)。
- 這次把整個目錄都刪光時,終點確實對不到檔,卻會印成「路徑寫錯」。
- 實務隱患寫「每次推送多兩次 git 讀檔」,沒算列終點整棵樹這一次。

**11. 範圍 3 的訊息範本沒帶 `--rule`,放行紀錄的統計會少算。**
severity: minor
blocking: 否——閘本身會印帶好 `--rule` 的完整指令,只有照訊息範本手打才中。
引句:「放行紀錄裡 rule 是 lumos/inline-suppression 的筆數」
- 訊息範本寫的是 `lumos lint-waive <指紋> --note`,沒有 `--rule`、`--file`。
- file: `scripts/lumos:41881` 的 `cmd_lint_waive` 自己就提醒「沒帶規則代號,健檢按規則統計放行時會算不到它」。
- 手打的放行紀錄 `rule` 欄是空的,RETIRE-IF ③ 與 REVISIT 的「按 rule 數筆數」會低估。

## 已讀、無 finding 的節
- **用詞、不做、回退:** 已讀,無 finding。
- **依據來源:**
  - 官方頁面核過:media3 的 `MediaSessionService` 宣告是 `extends LifecycleService`。
  - ruff 的 `ruff: ignore`、`ruff: file-ignore`、`ruff: disable` 三種寫法都有文件。
  - 引用的節點檔都存在。
- **範圍 4 與 S4:** README 中英兩版第 450 行已是目標句,數字與 `Verification/2026-09-19_受控實驗程式碼為主四組對照` 一致,無 finding。
- **預期值表:** S1 列不含巢狀(見 4),S2、S3 逐列與先紅測試吻合。

## 資料狀態五問
- **新舊互讀:**
  - 舊設定檔沒有這個鍵,不影響。
  - 舊放行紀錄用指紋雜湊,不會撞新規則名。
  - ⚠ 掛鉤與 `scripts/lumos` 分開複製、版本會錯開。舊版 lumos 讀到新鍵靜默無作用,spec 沒有版本檢查或健檢,我只標記,不列 finding。
- **寫一半:** 設定檔寫到一半是壞 JSON,會判 high,方向安全;放行檔讀改寫已有鎖。無 finding。
- **衍生資料:** 沒有新增快取或衍生檔。代碼審留痕綁版本,不受清單新增影響。
- **時間:** 提交 SHA 終點讀 git 物件,結果穩定。無 finding。
- **不可逆:** 放行紀錄只增不減,回退段已說明。同意其「已排除」。

## 實務隱患鏡頭逐類
- **守衛面(推送閘判定):** 碰到,見 1、2、3、4。
- **併發:** 無,新掃描只讀快照,放行檔已上鎖。
- **效能:** 正則沒有巢狀量詞、不會爆;只有 10 的低報成本。
- **輸入信任:** `.lumos/config.json` 是被審分支可控的宣告,見 2。
- **金流、對外送出、不可逆:** 無,因為只改判定與文件、整段可還原。
- ⚠ **檔名清洗:** `_plain_label` 只擋 ASCII 控制字元,不剝 C1、U+2028、雙向字元,同檔其他處用 `_kill_esc`。依本 repo 單人威脅模型只記不列。

最嚴重 severity:major;blocking 共 4 條(1、2、3、4)。
