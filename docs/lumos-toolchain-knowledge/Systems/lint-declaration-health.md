---
type: system
status: done
created: 2026-07-17
updated: 2026-11-06
self_audit: sonnet/2026-07-27
about_code_stamp: batch-2026-08-23/2026-08-23/4921126118e5
tags:
  - type/system
  - status/done
  - risk/守衛面
  - scope/stack-knowledge
related:
  - "[[Systems/pitfalls-lint-adapter]]"
  - "[[Systems/lint-version-watch]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Issues/lint-watch空轉假綠]]"
summary: |-
  KEY:[代碼審 r2 折入 2026-09-16]★守衛改成白名單制,而且這是同一個毛病第三次★——語法樹版我在註解裡寫了「拿變數繞也擋得住」,實測擋不住(先賦值給變數再用就看不到)。改成白名單:不看你怎麼寫,只看★哪些函式碰得到這個佔位符★,名單外的函式提到它就紅。實測擋得住「新開一支函式自己做替換」;★擋不住「名單內的函式用變數繞」與 getattr 取方法★——這次照實寫進註解,不再宣稱密不透風。前兩次分別是「唯一實作」(r1 架構席抓到)與「機械保證」(r1 架構席抓到) [test:t_lint_files_substitution_has_one_implementation]
  KEY:[代碼審 r1 折入 2026-09-16]兩件事:①★冒煙遇到「這個棧還沒有檔」要講實話★——那條路原本刻意設計成把命令原樣送出、只驗命令本身跑不跑得動,而同批加的「佔位符沒換掉就不跑」讓它變成保證失敗,還回一句錯的診斷(說工具沒裝,其實工具好好的)。現在回報「這個棧還沒有檔,沒驗到」,既不假警報也不假裝驗過。②★「只准有一處替換佔位符」的守衛改用語法樹★——原本逐行字串比對,拆成多行、多一個空白就繞過去了,「機械保證」四個字名不副實;語法樹版實測擋得住拆行寫法。★它買到什麼沒買到什麼★:擋得住換行/換縮排/改用 re.sub/拿變數繞,擋不住 getattr 取到 replace(要刻意才寫得出來),不宣稱密不透風 [test:t_smoke_says_no_files_instead_of_crying_broken,t_lint_files_substitution_has_one_implementation]
  KEY:[佔位符只剩一份實作 2026-09-16]「把要檢查的檔換進指令」這件事原本在四個地方各寫一次,★算改動風險那一條漏了★(於是那條路等於從沒檢查過東西)。現在統一走 `_lint_cmd_with_files`,冒煙、規則索引核對、新增告警閘、算風險四處都呼叫它。★並且從原始碼層釘住★:整支程式只准有一處在替換那個佔位符,再出現第二處測試就紅——第一版只在註解裡寫「唯一實作」,同族掃描當場指出另外兩處還在自己手寫,所以改成機械保證。出身見 [[Issues/風險掃描的linter那隻手沒送檔進去]] [test:t_lint_files_substitution_has_one_implementation]
  KEY:★2026-08-26 接線收口(plan:[[Projects/lint接線收口_計劃]])★:①靜態層併入 doctor 兌現——[F] 檢共用 _lint_load_and_validate helper(cmd_lint_check 同源單一實作),有宣告才驗、無宣告一行跳過、壞=紅擋 CI;路徑解析=_repo_root_from_env(standalone 回退;env.vault 直拼與 doctor 區域 repo_root 兩個陷阱都踩過被測試抓紅,教訓入案)②smoke 維持手動+責任歸屬:分家(2026-08-20)後 KDS 自負;Landmark 條件待辦=[[Issues/Landmark宣告lint時接smoke排程]]③擋推鏈 --no-lint 兩側同跳已結構化入 [[Systems/pitfalls-code-loop]] decisions(2026-10-15 起:無宣告但根目錄有 eslint 設定時,改印「還沒接上」提醒與可貼的 lint.json 範本,只有連 eslint 設定都沒有才一行跳過)
  KEY:lint-check 收「宣告了跑不動的東西」破口——同 lint-watch 空轉([[Issues/lint-watch空轉假綠]])同病根:宣告與現實脫鉤、無機制對帳。lumos lint-check <repo> 兩層:靜態格式校驗(恆跑)+ --smoke 真跑冒煙
  FLOW:讀 .lumos/lint.json → _lintcheck_validate 靜態校驗(非dict/value非list/命令空/缺{LINT_SARIF_OUT}佔位符)→ [--smoke:格式過才對每條命令 _lint_run_and_parse、無可解析SARIF產出=跑不動]→ rc 0健康(含無宣告)/1有問題/2非JSON
  KEY:兩層各抓一類——靜態層抓「格式錯」(便宜、純靜態);smoke層抓「格式對但跑不動」(工具/task/檔案缺;唯一能抓 gradle task 或外部 jar 存不存在的方法,靜態永遠抓不到)
  KEY:真實案例(2026-07-17 KDS)——Citrus_KDS 的 lint.json 格式完全正確(`{"kt":["java -jar /tmp/detekt-dist/...detekt-cli.jar --report sarif:{LINT_SARIF_OUT}..."]}`),但 detekt jar 放在 /tmp 被系統清掉→靜態層正確放行、--smoke 正確抓「跑不出 SARIF」rc1。靜態抓不到、smoke 抓得到,正是兩層必要性的鐵證;[2026-07-27]同案重演(jar 又被清)→根治=改 brew 安裝+共用 config(標準接法立於[[Systems/linter精選目錄]]),KDS lint.json 換宣告後 smoke 綠
  KEY:誠實天花板——靜態層驗格式不驗命令跑不跑得動;smoke真跑=慢(每linter一次完整run)、且對「輸出SARIF到stdout而非佔位符檔」的宣告會報錯(那也是宣告錯,smoke正確抓出,非誤報);外部工具放 /tmp 這類易失位置=宣告脆弱,smoke 是唯一守衛
  KEY:設計哲學=宣告即契約需對帳——lint.json/lint-watch.json/test-layers.json 三個宣告檔都吃「宣告了不存在/跑不動的東西沒人知道」風險;lint-check 是 lint.json 這條的對帳器,同族收口
  DEP:scripts/lumos cmd_lint_check + _lintcheck_validate｜復用 _lint_run_and_parse(smoke)
  TEST:t_lintcheck_validate(格式校驗含 value 非 list 誤植案例)+t_lintcheck_cli(無檔rc0/空殼rc1/格式對rc0/smoke抓跑不動rc1/smoke真產SARIF rc0/非JSON rc2);全套 1236 passed
  WHY:lint-check 與健檢 F 段對 detekt 宣告照指令字面印「實際會怎樣」的提醒(型別資訊缺、等號寫法、Gradle 純 detekt 任務、推送只記錄不擋、多檔拒跑),只提醒不改退出碼;「推送閘接不接得住」改由新增告警閘、風險分級、本判定共用同一支小函式 [出處:[[Projects/Android的detekt規則說實話_計劃]] 設計審 r1] [因:這些落差 detekt 本身不報錯,沒人說就以為有在檢查;Android 專案目前沒有修法,擋了只會訓練人繞過] [不選:記成宣告問題讓 CI 變紅(沒出口的紅);冒煙探針實跑驗規則(改到推送前真的擋那案)] [test:t_lint_detekt_advice_table] [test:t_lintcheck_detekt_advice_output] [test:t_doctor_lint_detekt_advice]
  WHY:detekt 宣告提醒跟著逗號佔位符改:帶 {LINT_FILES_CSV} 的不印 P1、P2,P2 只看舊 {LINT_FILES} 並指向 {LINT_FILES_CSV},T1 指向 CI 型別檢查範本,新增 T4(宣告有 detekt 而 .github/workflows/ 沒有 detekt<變體> 任務字樣就印型別規則哪裡都沒擋);冒煙取樣跳過分隔字元路徑;{LINT_FILES_CSV} 單獨被引號包住記成格式問題 [出處:2026-11-06 [[Projects/Android的detekt推送前真的擋_計劃]] 範圍 4、5] [因:推送前只擋不用型別的規則,型別規則改由消費專案 CI 擋,沒接的要講出來不讓人以為有在擋;引號疊兩層讓含空白的路徑多出字面引號] [不選:T4 改退出碼(先提醒,REVISIT 2027-02-01 看有沒有人接);叫 T3(代號已被等號寫法用掉)] [test:t_lint_detekt_advice_csv_and_ci] [test:t_lintcheck_smoke_csv]
  WHY:Android 現成檢查的三則提醒(A1 CI 設定檔裡找不到 Android Lint 的跡象、A2 用 Compose 卻一套 Compose 規則都沒接、A3 宣告的外掛檔不在)另起一則(lint-check 的 --json 仍與 detekt 提醒共用同一個 advisories 字串清單,A 系列條目以 [CI] A1:、[kt 第 N 條] A3: 開頭可分)、不放進 detekt 那支函式與標題 [出處:2026-11-06 Projects/Android現成檢查接上CI與推送前_計劃 設計審 r1] [因:T4 要求宣告裡有 detekt 命令,這三則只要 kt 棧加 Android 專案;混在 detekt 標題底下會誤導] [不選:沿用 T4 只看 .github/workflows/(GitLab、Bitrise 等專案會永遠誤印)] [test:t_lint_android_ci_advice]
  WHY:A1 用證據模型——CI 設定檔都找不到 Android Lint 跡象(lint 任務名、跟 gradlew 或 gradle 寫在同一邏輯行的 check/build、Azure tasks/gradle action arguments/Bitrise gradle_task 三個欄位值裡的 check/build;CircleCI 的 command 是通用欄位、不收)才提醒,不判斷「有沒有接」;建置檔的 lint 區塊與 lint-baseline.xml 不算跡象 [出處:2026-11-06 code-android現成檢查 r2、r3、r4、r5] [因:設計審 r1、代碼審 r1、r2 三次被字面判斷打穿;OpenSSF Scorecard 官方檢查文件同樣只找已知名字、承認會漏] [不選:逐條解析 Gradle 命令(各寫特例、連輪被打穿);整檔有 gradle 字樣就認 check/build(needs: build、stage: build 讓沒接的專案靜默,r3 三席);建置檔設定當證據(範本第 1、2 步的痕跡,正是沒做第 3 步該提醒的狀態)] [代價:寫了字樣卻沒真的跑也算有跡象,少印提醒] [test:t_lint_android_ci_advice]
aliases:
  - lint 宣告健康檢查
about_code:
  - scripts/lumos
verified_by:
  - "[[Verification/2026-08-26_lint接線收口落地]]"
---
# lint-declaration-health——lint 宣告健康檢查(收「宣告了跑不動的東西」破口)

> **緣起**:2026-07-17 收窄 lint-watch 後盤點消費專案,使用者指出「宣告了跑不動的東西,也要是被檢測出來的一環」——這正是 lint-watch 空轉([[Issues/lint-watch空轉假綠]])的同病根:**宣告與現實脫鉤,沒有機制逼對帳**。

PRIOR-ART: ① 最小解層級——復用既有 `_lint_run_and_parse`(smoke)+ 新增純函數校驗,無新機制。② 世界解過——CI 界 config-lint/schema-validation(actionlint 驗 workflow、renovate-config-validator);本質是「宣告檔的宣告器」。③ 裁定=borrow-design。

## 兩層設計(各抓一類壞)
| 層 | 抓什麼 | 成本 |
|---|---|---|
| **靜態格式校驗**(恆跑) | 格式明顯錯:非 dict / value 非 list / 命令空 / 缺 `{LINT_SARIF_OUT}` 佔位符 / `{LINT_FILES_CSV}` 單獨被一對引號包住(2026-11-06) | 便宜(純靜態) |
| **`--smoke` 冒煙**(可選) | 格式對但**跑不動**:task 不存在、plugin/jar/工具缺、SARIF 無產出 | 貴(每 linter 真跑一次) |

**為什麼要兩層**:靜態永遠抓不到「gradle task 存不存在」「外部 jar 還在不在」(那要真跑才知道);smoke 是唯一能抓的方法。但 smoke 慢,故分開——日常/巡檢跑靜態,定期/setup 後跑 smoke。

## 真實案例:KDS 的脆弱宣告(2026-07-17)
Citrus_KDS 的 `.lumos/lint.json` **格式完全正確**:
```json
{"kt": ["…/java -jar /tmp/detekt-dist/detekt-cli-1.23.7-all.jar --input …/MainActivity.kt --report sarif:{LINT_SARIF_OUT} --build-upon-default-config"]}
```
用獨立 detekt CLI jar(非 gradle plugin)跑。但 jar 放在 `/tmp/detekt-dist/…`——`/tmp` 被系統清掉後 jar 沒了。
- **靜態層**:格式合法(kt→list、有佔位符)→ 正確放行 ✓
- **`--smoke`**:真跑 → jar 不存在 → 跑不出 SARIF → 正確抓 rc1 ✓

兩層必要性的鐵證:靜態抓不到(宣告本身沒錯)、smoke 抓得到(現實跑不動)。教訓:**外部工具放 `/tmp` 這類易失位置=脆弱宣告**,靜態校驗無能為力,smoke 是唯一守衛;根治是把工具放持久位置或走 gradle plugin。

## rc 語意
`0`=健康(含無 lint.json=無宣告,不報) / `1`=有問題(格式或 smoke) / `2`=lint.json 非合法 JSON。

## 誠實天花板
- 靜態層只驗格式,不驗命令跑不跑得動——smoke 的責任田。
- smoke 對「輸出 SARIF 到 stdout 而非 `{LINT_SARIF_OUT}` 檔」的宣告會報錯——不是誤報:那確實是宣告錯(缺重導向),宣告端須把 SARIF 導向 `{LINT_SARIF_OUT}`。
- smoke 真跑消費專案自己宣告的 shell 命令(非外部輸入),風險等同該專案 CI 跑自己的 lint;且慢,不進 doctor --ci。

## 同族收口(宣告即契約需對帳)
lumos 三個宣告檔都吃「宣告了不存在/跑不動的東西沒人知道」風險:
- `.lumos/lint.json`(該跑什麼 linter)→ **本節點 lint-check 對帳**
- `.lumos/lint-watch.json`(該盯什麼 linter 新版)→ 心跳行 + 收窄([[Issues/lint-watch空轉假綠]])
- `.lumos/test-layers.json`(該跑什麼測試層)→ 恆 fail-open advisory(尚無對帳器,見待辦)

## 待辦
- [ ] 接巡檢:`lint-check` 靜態層併入 `doctor --ci`(消費專案 push 前掃自己 lint.json 格式);smoke 太慢不進 doctor,留 CI/setup 手動或 daily-governance
- [ ] test-layers.json 也給對帳器(同族第三個宣告檔,目前無檢查)
- [x] KDS:detekt jar 從 /tmp 移到持久位置——2026-07-27 完成:改 `brew install detekt`+共用 config(標準接法見 [[Systems/linter精選目錄]]),lint.json 換宣告、`--input` 擴到整個 source set,`lint-check --smoke` 綠

## 逗號佔位符與 detekt 提醒跟著改(2026-11-06,[[Projects/Android的detekt推送前真的擋_計劃]] 範圍 4、5)

- **冒煙**:帶 `{LINT_FILES_CSV}` 的命令取樣時跳過路徑含逗號或分號的檔(detekt 會把那支拆成兩個不存在的路徑、整條拒跑,冒煙就報一個假的「跑不動」),用其餘檔換成逗號串;換檔走共用替換函式。舊 `{LINT_FILES}` 照舊取前三支 [test:t_lintcheck_smoke_csv]。
- **格式問題**:`"{LINT_FILES_CSV}"` 或 `'{LINT_FILES_CSV}'`(那對引號只包住佔位符)記成格式問題、退出碼 1——換進去的值已經交給 `shlex.quote`,再包一層會讓含空白的路徑多出字面引號。`sh -c '…{LINT_FILES_CSV}…'` 整段包裝不算;舊佔位符不追溯。健檢 F 段共用同一支校驗,所以那邊也會列成宣告問題。
- **detekt 判定表改的列**(單一來源仍是 [[Projects/Android的detekt規則說實話_計劃]] 的判定表,這次改的列寫回那篇):帶逗號佔位符的算推送時接得住,不印 P1、P2;P2 只看舊 `{LINT_FILES}`、文字改成「改用 `{LINT_FILES_CSV}`」;T1 文字指向 CI 型別檢查範本;新增 T4(計劃字面叫 T3,但 T3 已是等號寫法):宣告裡有 detekt、而 `.github/workflows/` 底下沒有任何 `detekt<變體>` 任務字樣(跟判定表〈Gradle 任務名怎麼分〉的「有型別任務」同一支分類)→ 印「型別規則目前哪裡都沒擋」,一個專案一則、標 `[CI]`;只看字面、不執行、不改退出碼 [test:t_lint_detekt_advice_csv_and_ci]。

## 沒宣告但專案有 eslint 設定時(2026-10-15,[[Projects/前端框架從vue分出_計劃]] W7)

健檢 [F] 段在 `.lumos/lint.json` 不存在時先看 repo 根有沒有 eslint 設定(`eslint.config.{js,mjs,cjs,ts,mts,cts}`、`.eslintrc` 與 `.eslintrc.{js,cjs,json,yml,yaml}`,只看根目錄);有就不再說「沒有接 linter」,改說看到哪幾個檔、印一份可貼的 lint.json 範本(`npx eslint -f @microsoft/sarif -o {LINT_SARIF_OUT} {LINT_FILES}`,鍵 ts/tsx/js/jsx)與接法三步。根 package.json 的 `eslintConfig` 值是物件時也算舊式設定(null、字串、陣列不算,r2 折入,測試 t_eslint_config_key_must_be_object;代碼審 r1 折入,測試 t_eslint_package_json_eslintconfig;兩份 eslint 檔名清單由 t_eslint_config_names_in_lint_globs 釘住一致)。只有舊式設定時範本指令前面加 `ESLINT_USE_FLAT_CONFIG=false`(eslint 9 不設就不讀舊式設定)。仍是提醒、不計 issues。init 收尾在 lint.json 不存在時印同一件事的一行提醒,指令另起一行;**不替使用者寫 lint.json**(宣告了跑不動的 linter 會讓這段一直唸、讓新增告警閘拿到壞宣告)。偵測表 `_LINTER_CONFIG_MARKERS` 目前只有 eslint;新增告警閘搬設定檔進快照的 `_LINT_CONFIG_GLOBS` 用途不同、不合併,但 eslint 檔名兩邊都要認得(這次補了 mts/cts)。測試 t_doctor_lint_detects_eslint_flat_config、t_doctor_lint_detects_eslintrc、t_doctor_lint_eslintrc_template_legacy_flag、t_doctor_lint_no_config_message_kept、t_init_mentions_eslint_without_writing_lint_json、t_init_eslint_hint_skipped_when_declared。
