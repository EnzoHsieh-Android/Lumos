severity: major

## 1. 分層與依賴方向:對齊

- 對照:安全證據判定分兩層。判定本體 `_secev_evaluate` 放在自己的段落,接線薄殼是 `_codeloop_security_step`。薄殼排在放行早退之前,回帶 `reason_kind` 的擋下 dict,再由 `_CodeloopKg.hit` 收。
  - file: `scripts/lumos:65241`
  - file: `scripts/lumos:65414`
  - file: `scripts/lumos:65108`
- 設計的位置同形:判定排在放行早退之前,擋下種類是 `android_e2e`,接進 `_cl_say_block`、`_codeloop_kg_finish` 與 `pp_cl_reason`,細節寫在 `Systems/android-e2e-acceptance`。
  - 引句:「位置與接線:跟安全證據判定一樣排在所有放行早退之前;擋下種類 `android_e2e`」
- 主線挑法直接用 `_secev_mainline(repo_root, sha, pushed_branch, range_start, deadline)`,與設計寫的兩種情況一致。已上線的 `_e2e_changed_files` 也呼叫它,有先例。
  - file: `scripts/lumos:10027`
  - file: `scripts/lumos:40853`
- e2e 段的程式呼叫 `_secev_*` 私有函式,`_secev_int`、`_secev_mainline` 已有先例,不算新的跨層。
  - file: `scripts/lumos:40866`
  - file: `scripts/lumos:40580`
- 沒有跨層直呼。判不清就擋與安全證據閘同向,不是 fail-open 的 lint-new 那條。
  - file: `scripts/lumos:10759`

## 2. 命名與錯誤處理:大體對齊,有四處小不一致

- 對齊的部分:
  - 閘名 `android-e2e` 與 `lint-new`、`bound-tests`、`security-evidence` 同為連字號,要登記進 `_KNOWN_GATES`(`scripts/lumos:15996`)。
  - `reason_kind` 用底線小寫,與 `lint_new`、`security_evidence` 同。
  - 擋下回 1。waive 缺理由回 2、被拒回 1,與 `cmd_lint_waive` 同(`scripts/lumos:37746`)。

1. 治理帳事件寫法跟鄰居不一致,而且設計引的鄰居說法對不上。
   - 設計寫「照新增告警閘 `LUMOS_SKIP_LINT_NEW` 的做法」記 `skipped`。實際上 lint-new 的 `off` 路徑只回 status,沒寫任何治理帳(`scripts/lumos:38731`、`scripts/lumos:65162`)。
   - 專案裡真正記「環境變數略過」的是 fix-check,事件種類是 `skipped-env`,且 `_SLOT_METRIC_KINDS` 也只列 `skipped-env`。
     - file: `scripts/lumos:21261`
     - file: `scripts/lumos:4790`
   - 設計只列 skipped、waived、passed-by-feature 三種事件,沒寫「擋下」要不要記。安全證據閘擋下時記 `blocked` 並帶 `hard=True`(`scripts/lumos:65424`)。RETIRE-IF 與 REVISIT 要的「誤報多過真報」缺這個分母。
   - 引句:「記一筆治理帳 skipped(照新增告警閘 `LUMOS_SKIP_LINT_NEW` 的做法)」
severity: minor
   - blocking: 否

2. 環境變數略過的判法,鄰居本身就不一致,標 ⚠ 交編排者。
   - 設計寫「有設時整道關掉」,這是 `LUMOS_SKIP_LINT_NEW` 的真值判法(`scripts/lumos:38731`)。
   - 〈回退〉卻寫 `LUMOS_SKIP_ANDROID_E2E=1`。`LUMOS_SKIP_BOUND_TESTS` 與 `LUMOS_SKIP_NOTE_SHAPE` 只認 `== "1"`(`scripts/lumos:63999`、`scripts/lumos:45647`)。
   - 專案沒有單一做法可對,設計也沒挑一邊。

## 3. 第二種做法:有一條 major

- 對齊的部分:
  - `waive` 的讀改寫鎖與 `_write_lf` 寫入,對應已上線的 `_e2e_record_update`(`scripts/lumos:40815`),它本身就是照 `_vault_write_lock` 加 `_write_lf`(`scripts/lumos:38618`)。
  - `shared_paths` 的路徑規則「S26 那套檢查照用」,對應 features 的 paths 已走 `_e2e_relpath_err`(`scripts/lumos:40456`)。
  - 掛在 `lumos android-e2e` 子指令下,與 judge、select、history 並列。

3. 「把改到的檔對到功能」沒有說要重用,現況已有兩種不同的範圍定義,設計很可能再多出第三套。
   - `_e2e_changed_features` 把「列出改到的檔」(`_e2e_changed_files`,讀工作目錄)和「歸屬判斷」寫在同一個迴圈裡,歸屬規則是 paths 前綴或某情境的 flows 列了它,直接吃 `feats` 與 `_e2e_under`。
     - file: `scripts/lumos:40885`
     - file: `scripts/lumos:40895`
   - 它的「算驗收範圍」是寬鬆版:`app_dirs` 不扣 `exclude`,另加 `.maestro` 與兩個設定檔。
   - `_e2e_fingerprint` 內嵌的是另一版:`app_dirs` 扣 `exclude` 與預設排除的單元測試,再加驗收素材目錄與門檻檔。這段寫在 `ls-tree` 迴圈裡,沒有獨立的判斷函式。
     - file: `scripts/lumos:40552`
     - file: `scripts/lumos:40563`
   - 設計要的是:
     - 輸入改成「分岔點到被推送提交」的差異。
     - 範圍「跟 S2 算指紋同一套,兩端各用自己那版的 `e2e` 段取、取聯集」。
     - 歸屬在主線版與被推送提交兩版的 `features` 取聯集。
     - 範圍外的檔直接不影響判定。
   - 這三件事現有函式都做不到,只能抽出或另寫:歸屬函式與範圍函式要拆成吃 `feats`、`e2e` 的純函式,指紋與 `--changed` 一起改用。
   - 設計全程沒點名 `_e2e_changed_features`、`_e2e_under`、`_e2e_norm`、`_e2e_fingerprint`,也沒寫「抽出共用」,只用散文說「同一套」。
   - 引句:「範圍跟 S2 算指紋同一套,兩端各用自己那版的 `e2e` 段取、取聯集」
   - 引句:「每支改到的檔,在主線版與被推送提交兩版的 `features` 裡找歸屬(`paths` 包住它、或某個情境的 `flows` 列了它)」
   - 照字面實作,接手的人會在 `--changed` 的歸屬、指紋的範圍、推送前的歸屬與範圍三處猜哪一套才是準的。建議設計補一句:抽出共用的歸屬判斷與指紋範圍判斷,三處共用。
severity: major
   - blocking: 是

4. 放行的形狀,與 `lint-waive` 有四處不同,只有第一處是新增做法,標 ⚠。
   - `_confirm_tty` 目前只有 `cmd_init` 一處呼叫(`scripts/lumos:33713`),人放行與 AI 放行靠它分,是新機制。
   - 誰:lint-waive 取 `USER`、`USERNAME`、`unknown`,設計取 git `user.name`,沒設才取登入帳號。
     - file: `scripts/lumos:37770`
   - 重複放行:lint-waive 對已放行的指紋回 1(`scripts/lumos:38626`),設計是同指紋再放行就多一筆。
   - 放行檔:lint-waive 是專案單一檔 `.lumos/lint-waivers.json`,設計是每個指紋一個紀錄檔。
   - 鎖和寫入沿用得對,以上四處有 Enzo 的裁示與計劃理由,結構沒壞。
   - 引句:「用 `_confirm_tty` 問一次「確定放行嗎」:答了 y → 記成人放行」
severity: minor
   - blocking: 否

5. `shared_paths` 的存在性檢查比同層的 `features.paths` 嚴。
   - features 的 paths 現在只驗路徑寫法(`scripts/lumos:40456`),不驗存在。設計對 `shared_paths` 多一條「寫了不存在的路徑也擋」。
   - 同一設定檔裡兩個欄位規則不同。
   - 推送前用兩版聯集判,一方版本刪掉的目錄在另一版仍可能合法列著,存在性要看哪一版也沒寫。
   - 引句:「路徑寫法同 `features` 的 `paths`,S26 那套檢查照用;寫了不存在的路徑也擋」
severity: minor
   - blocking: 否

6. 沒有逾時預算與單檔上限,與安全證據判定不同。
   - 安全證據閘:有 `deadline`、`evaluation_timeout`,讀檔有 `_SECEV_FILE_MAX` 上限(`scripts/lumos:10947`、`scripts/lumos:10953`、`scripts/lumos:11023`)。
   - 新增告警閘有 `budget_sec`(`scripts/lumos:65169`)。
   - 設計只寫「其他內部錯誤→擋」,沒寫讀樹與跑 git 的上限,也沒寫判定整體的時間預算。
   - 引句:「從被推送提交的檔案樹讀 `.lumos/e2e-records/<被推送提交的指紋>.json`(不讀工作目錄)」
severity: minor
   - blocking: 否

7. CI 與接線自相矛盾,標 ⚠。
   - 設計寫在 CI 裡不跑,也要把說明接進 ci.yml,兩句放一起不通。
   - 安全證據閘在 CI 照跑,tag 工作也跑。專案裡目前沒有別道判定用 `_in_ci()` 自我關閉,這會是第一道。
   - 引句:「在 CI 裡(`_in_ci`)不跑這道,印一句「第一版只在本機推送時判」」
   - 引句:「ci.yml 的擋下說明」
   - 這是 Enzo 在 r1 裁示的範圍,我只標出接線清單要不要保留 ci.yml 那一項。

## 4. 落點:大致合理,有兩處待確認

- `Systems/android-e2e-acceptance` 已在工作樹(78 行),responsibility 已寫明「之後 code-loop check 那一道與放行也歸這裡」。設計把判定與放行的細節放在這裡,與安全證據閘有自己的家 `安全證據閘` 同形,不必另開。
- `Systems/pitfalls-code-loop` 只加一行連結。它已有 `.lumos/e2e-records/` 簿記那條(約在 `Systems/pitfalls-code-loop.md:63`),也沿用 2026-10-20 安全證據那行的寫法(約在 `Systems/pitfalls-code-loop.md:290`)。
- `Systems/bound-tests-gate` 的 about_code 含 `scripts/hooks/pre-push` 與 `.github/workflows/ci.yml`,`pp_cl_reason` 的 WHY 也在那篇(約在 `Systems/bound-tests-gate.md:137`)。先例是安全證據閘把 pre-push 與 ci.yml 的改動寫在這裡(約在 `Systems/bound-tests-gate.md:167`)。把擋下原因表寫這裡是對的。
- 兩處待確認:
  - 「`lumos doctor` 列提醒」與「`lumos enforcement` 多一列」沒有指定落點。`lumos-cli-read` 等篇有 enforcement 的說明,但計劃的 lands_in 四篇都沒涵蓋。依「每支檔有家」要補寫落在哪一篇。
  - `lumos enforcement` 的設計是「這查的是有沒有裝上/接上」,未生效時提示跑 `lumos install --force`(`scripts/lumos:36047`)。「AI 放行待看」是待辦計數,不是裝沒裝上,修法也不是重裝。標 ⚠:這一列的語意與處置提示跟其他列不同,沒有先例可對。
    - 引句:「`lumos enforcement` 多一列「android-e2e AI 放行待看」,有待看時標成沒生效」
severity: minor
    - blocking: 否

不對齊共 7 條,其中 major 1 條

編號對應:第 1、2、4、5、6、7 條分別是上面的第 2 節發現 1、發現 2(⚠)、第 3 節發現 4、發現 5、發現 6、發現 7(⚠);第 3 條是 major(第 3 節發現 3);第 7 條 enforcement 語意是第 4 節的 ⚠。實際列出的不對齊發現共 7 條(第 2 節 2 條、第 3 節 4 條、第 4 節 1 條),其中 major 1 條。
