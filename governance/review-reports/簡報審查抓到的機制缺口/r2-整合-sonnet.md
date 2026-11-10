severity: major

## 逐節讀完,整體判讀

先講結論:這份 r2 修訂稿最大的洞,是「高風險路徑清單」照抄了殘留索引「起點與終點取聯集」的形狀,卻漏掉旁邊那段已經踩過坑的防線(拿掉清單本身要升 high、檔案清單用 `--no-renames`)。另一個洞是新設定鍵沒有進任何驗證或文件的既有位置。補進來的段落,README 實驗句與 Service 例外兩處,各有一個沒查證的宣稱。

已讀、無 finding 的部分:
- 前言、PRIOR-ART、RETIRE-IF、用詞。
- 「不做」。
- 回退、天花板、REVISIT。
- 依據來源裡的 LifecycleService 那兩列:我另行打開官方頁,確認 `MediaSessionService extends LifecycleService`、`MediaLibraryService` 為間接子類別,宣稱屬實。
- 「本 repo 新加過 3 處 `# noqa`」:查 git 歷史屬實(2026-09-07、09-29、10-19 各一)。

---

**F1**
severity: major
blocking: 是——這是「人工不能把分級往下調」的實質破口,而且既有同族防線已在鄰居程式碼裡,不是新問題。
引句:「範圍起點那一版與終點那一版(終點是工作目錄時讀工作目錄)的清單取聯集,所以同一次改動拿掉某條路徑不會讓自己降級」

範圍 2 只防「同一次推送」把清單清空。分兩次推送就躲得掉:
1. 第一次推送只把 `src/auth` 從清單拿掉,改動只碰 `.lumos/config.json`,分級是 standard,過關。
2. 第二次推送的起點版,是增量推送時的遠端舊值(`scripts/lumos:68713` `_push_range_start`:舊值是所有分岔點的祖先就用舊值)。那一版的清單已是空的。這時再改 `src/auth/Login.kt`,仍判 standard。

同一個函式的鄰居早就為此立了規則:
- `scripts/lumos:64768` `_residual_tier_hits` 寫明「removed:拿掉殘留本身要過代碼審,分兩次推送也躲不掉」。
- 同處還有 `shrunk`:「先縮守備範圍、下一次推送再改程式就躲得掉」。
- 決策出處在 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:73`。
- `review_roles`、`arch_targets` 的宣告改讀主線分岔點(`scripts/lumos:39434`、`:65129` 起 `_trusted_decl_ref`),理由是「被審的分支不能自己改宣告決定自己怎麼被審」。

spec 的 S2、預期值表與 `scripts/test_lumos.py:5437` 的 `t_pitfall_tier_risk_paths` 都只測單次推送。第二次推送起點版清單已空的情況,沒有任何條款。

---

**F2**
severity: major
blocking: 是——「改到的檔」的來源沒定義,實際管道會漏掉整類改動,清單等於對這幾類改動失效。
引句:「這次改到的檔只要有一支等於清單裡的檔、或在清單裡的目錄底下,就判 high」

`_pitfall_tier(claims, files, …)` 收到的 `files` 是 `list(added) + list(changed_lines)`(`scripts/lumos:65147`、`:65214`)。這份資料來自 `git diff -U3` 的 `---` / `+++` 檔頭(`_pitfall_diff_collect`)。

我在暫存 repo 實測:同一個 `src/auth/` 底下做下面四種改動,`git diff -U3` 一行 `---` / `+++` 都沒有:
- 純改名搬出目錄
- `chmod +x`
- 二進位檔(如 `key.jks`)內容變
- 新增空檔

還有一條漏洞:刪除只進 `changed_lines`,而那一份先被 `_stack_changed_ok` 濾過。`.json`、`.md`、測試檔等副檔名的刪除不算改到。

既有做法是另外取檔名清單:
- `_test_suite_for_range` 用 `git diff --name-only -z --no-renames`。
- 殘留索引那條路也用 `--no-renames`(`pitfalls-code-loop.md:73`:「改名的舊路徑也算」)。

測試 `t_pitfall_tier_risk_paths` 是手工傳 `["src/auth/login.py"]` 進 `_pitfall_tier`,根本沒走真正的蒐集管道,所以抓不到這件事。

---

**F3**
severity: major
blocking: 是——spec 自己要防的失效(寫錯路徑被靜默略過),在推送閘上正好看不見。

引句:「清單裡某條路徑在終點那一版一支檔都對不到時,pitfalls 的輸出多印一行」

1. 「對不到」那行只能出現在 `pitfalls --diff` 的人讀輸出(`scripts/lumos:65291` 一帶)。推送掛鉤在 `scripts/hooks/pre-push:567` 跑的是 `--json … 2>/dev/null`,人讀版只在 `_tier_high` 已經成立時才印。`code-loop check` 也只讀 JSON。
2. 路徑打錯(例如 `src/Auth`,macOS 大小寫不分、git 分)時,分級不是 high,掛鉤不印人讀輸出,打錯的人永遠看不到那行。
3. `_pitfall_tier` 回傳 `(tier, why)` 兩值、JSON 沒有承載欄位,spec 沒講資料怎麼走。
4. 既有路徑型設定鍵都有驗證出口,這個新鍵沒有:
   - `e2e.shared_paths`:`_e2e_relpath_err`(拒絕對路徑、`..`、萬用字元、`\`)。
   - `review_roles`、`arch_targets`:`_config_glob_error` 加警告,doctor 也讀(`scripts/lumos:71786`)。
5. 它們比對前先 `nfc()`(`scripts/lumos:63617` 與 `_residual_note_hits`)。spec 沿用的 `_e2e_norm` 不做 NFC。這個 repo 滿是中文路徑,NFC 與 NFD 不同時會靜默對不上。

---

**F4**
severity: major
blocking: 是——新鍵沒進「預設與值以這裡為準」的唯一彙整表,三個月後的人找不到它,也看不到它跟其他鍵讀法不同。
引句:「`docs/指令參考.md` 的 pitfalls 與 lint-waive 說明、`cmd_lint_waive` 的說明字串」

範圍 5 的清單漏了這些會被改變的地方:
- `docs/指令參考.md:162-178` 的〈專案開關〉表。
  - 表頭寫「預設與值以這裡為準」。
  - 總述寫「多數檢查讀被推那個提交裡的版本,但 `lint_new`、`stack_questions` 讀工作目錄那份」。`risk_high_paths` 是第三種(起點加終點兩版),要補。
  - 總述另寫「寫壞了…多半退回預設」,新鍵是讀不出判 high,與此相反,要補。
  - `lint_new.gate` 那列的描述會因 `lumos/inline-suppression` 而變。
- 英文孿生 `docs/command-reference.md:140`、`:163-176`:spec 只列中文版。
- `skills/lumos-code-loop/reference.md:415` 與 `:598`:`:415` 寫「tier: high(manifest 命中任一 pattern)」,路徑觸發後這句就錯;`:598` 是 `SKILL.md:13` 的孿生段落,spec 只列 SKILL.md。

---

**F5**
severity: major
blocking: 是——新增第二個內建檢查來源,跟該節點記錄的決策與核心定位相反,spec 沒翻案、也沒把那兩行列入要改的清單。
引句:「把新加的忽略註解當成一條新增告警送進同一條路,不另做放行流程」

`docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md` 的兩處記載:
- KEY:「lumos 只解 SARIF 一種格式…不內建任何棧規則、不裝/管 linter;規則庫讓給社群 linter」。唯一例外只有 `tq/`,而且寫明在 test-guard。
- `DECISION:[2026-07-04] 吃社群 linter(SARIF 整合)不自建規則庫(valid)`。

spec 加了一張涵蓋十幾種工具的抑制寫法表,以及新規則 `lumos/inline-suppression`。claim 的 `source` 寫 `lumos`,也偏離 KEY 記的 `source:"lint:<driver>"`(`scripts/lumos:42377`)。

lands_in 列了 `Systems/pitfalls-lint-adapter`,但範圍 5 只列要改 `pitfalls-code-loop` 的分級 KEY。PRIOR-ART 只引 SonarQube,沒處理本 repo 這條既有決策。

---

**F6**
severity: major
blocking: 是——acceptance 條款 S4 把一個已被同一份來源文件更新過的宣告寫死成驗收條件。
引句:「筆記正確時的幫助還沒量」

來源文件 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 的 H2 段(約第 38 行)寫:戊組已於 2026-09-21 跑完 80 場,H2 得到支持但只靠一題(H06:只看程式碼 0/5,有筆記的三個組合共 8/15)。

對應紀錄 `/Users/enzo/harness/lumos-gvc/docs/lumos-toolchain-knowledge/Verification/2026-09-21_戊組知識只在Issue的四題八十場.md` 存在。

spec 的 S4 `[manual:]` 只對 2026-09-19 那份四組對照。那份寫「那是戊組,等外家出題」,是戊組開跑之前的話。照 S4 驗收,README 會固定寫「還沒量」,而實際是「量過一次、效果薄弱、只靠一題」。

另外,唯一核對依據是別的工作樹裡「未提交」的檔(來源表第 81 行),三個月後可能已不在。

---

**F7**
severity: minor
blocking: 否——只影響理由字串與傳遞,分級結果本身不變。
引句:「多個理由並存時照既有寫法用」

`_pitfall_tier`(`scripts/lumos:64523` 起)在殘留理由命中後直接 `return`。spec 要求新步驟放「殘留索引那一步之後、風險型樣那一步之前」,殘留與風險路徑同時命中時,風險路徑的理由會被吞掉,與「不互相蓋掉」矛盾。實作得把檢查挪進殘留 `why` 的串接,spec 沒講,`t_pitfall_tier_risk_paths` 也沒有兩者並存的案例。

---

**F8**
severity: minor
blocking: 否——寫出來就能補,但會成為補丁隱性的測試缺口。
引句:「Service 裡的內部類別也豁免、Activity 裡的內部 Service 類別也豁免、Activity 本身照報」

範圍 1 列了這三種行為,另有 `MediaLibraryService`、帶套件前綴的寫法。S1 與預期值表只覆蓋 LifecycleService、MediaSessionService、Fragment、`MediaSessionService.Listener`、ProcessLifecycleOwner。現有樣本(`configs/ast-grep/kotlin-android/samples/{bad,good}/kt-lifecycle-collect-without-repeat/…kt`)也沒有巢狀類別、內部 Service、Activity 本身這三種。

`Systems/kotlin規則包.md` 有一條 WHY:自寫規則要逐項拿掉每個 has/not/inside/stopBy,每項都要有例子變紅。新增的外圍類別條件不守住這三種,改壞了不會紅。

另外,「型錄 STATE-5 那列補一句」沒說補在哪一欄。該列的欄位被 `check.py` 的 `catalog_problems`、`wiring_problems`、`stats_problems` 讀,例如〈實測〉欄寫的「樣本實測中壞例、好例不報」。補錯欄會讓自檢誤判。

---

**F9**
severity: minor
blocking: 否——是會靜默漏數的覆蓋缺口,但天花板節可補一行。
引句:「`pnpm exec`、`yarn`、`uv run`、`python -m`、`python3 -m` 同理」

- `_SHELL_WRAPPERS` 只有 `env nice time command nohup exec`(`scripts/lumos:40311`),所以 spec 得自加一層,這點對。
- 清單漏了本 repo 自己的標準直譯器 `python3.14 -m ruff`(`_cmd_basename` 取到 `python3.14`,不是 `python3`)。
- `uv run --python 3.14 ruff` 這種寫法,「下一個非選項的詞」會取到 `3.14`。
- 這類認不出的命令,忽略註解不會被數,沒有任何輸出。天花板節只講「寫法」認不全,沒講「包裝詞」認不全。

---

**F10**
severity: minor
blocking: 否——是 wording 與計數基礎的問題。
引句:「移除它,或用 lumos lint-waive <指紋> --note 寫明為什麼要忽略」

- 「確認是誤報就放行」這句固定文字還在這些地方,spec 只點名 `cmd_lint_waive` 說明字串:
  - `scripts/lumos:40826`、`:40859`、`:76226`(`_cl_say_lint_next`,實際擋下訊息)
  - `scripts/lumos:76888`、`:77973`
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md:16`
  - `skills/lumos-project-notes/commands/test-quality-standard.md:40`(那邊已經寫「改動是需求要的…照擋下訊息放行」,可對齊)
- 訊息指令沒帶 `--rule`。不帶就記不到規則:`.lumos/lint-waivers.json` 現有 423 筆放行,302 筆沒有 `rule`。RETIRE-IF ③ 與 2027-05-09 的 REVISIT 要數的正是 rule 為 `lumos/inline-suppression` 的筆數。

---

**F11**
severity: minor
blocking: 否——spec 只在範圍 2 一句帶過掛鉤,文件與簽核清單沒有。
引句:「推送掛鉤印的提醒改成先印 pitfalls 給的理由,不再固定說」

`scripts/hooks/pre-push` 與 `scripts/test_lumos.py` 都在 `governance/anchor-baseline.json` 的受護清單裡,改它們要 `lumos anchor approve`,而且是對話核可。範圍 5、實務隱患的守衛面一句都沒提。

---

**F12**
severity: minor
blocking: 否——本 repo 單人自用的威脅模型下風險低,但跟既有慣例不一致。
引句:「檔名經 `_plain_label` 清洗」

- `scripts/lumos:65254` 與 `:65273` 的註解:「檔名被審分支可控,人讀輸出一律跳脫」,用的是 `_kill_esc`。
- `_plain_label`(`scripts/lumos:70006`)只去 CR、LF、小於 32 的控制字元,U+2028、雙向覆寫不處理。
- 「對不到」那行若列出設定值,與 `_arch_targets_config` 的慣例相反:「警告只寫第幾條與固定原因,不回填專案寫的值」。

---

## 實務隱患鏡頭逐類

- **資安/信任邊界**:有。對應 F1(宣告讀哪一版)、F12(外來字串回顯)。其餘無,理由:不碰付款、不對外送出。
- **併發/鎖**:無。放行檔讀改寫已有 `_vault_write_lock`(`scripts/lumos:42908`),spec 沿用。
- **效能/資源**:無。我實測整棵樹列檔 19,667 檔只花 0.07 秒,「對不到」判斷不是成本問題。
- **資料正確性/不可逆**:有。對應 F1、F2、F6。
- **相容性/回退**:有。F11 的 anchor 簽核不在回退段。其餘無,理由:新鍵不存在時行為不變。
- **文件/測試/CI 同步**:有。對應 F4、F8、F10、F11。CI 設定 `.github/workflows/ci.yml` 不需改,CI 的 `code-loop check` 取 `BEFORE..SHA` 範圍與本機同一條路。

最嚴重 severity:major;blocking 共 6 條(F1、F2、F3、F4、F5、F6)。
