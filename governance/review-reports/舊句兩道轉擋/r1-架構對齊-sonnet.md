severity: major

審的是 /tmp/舊句兩道轉擋-r1.md 對照 `aspidochelone-reread-block` 工作樹。設計大半沿用既有做法,三分法、開關鍵名、`blocked` 事件、照留表態的位置都跟鄰居一樣。唯一的 major 是「結構行」判定:設計另造一套判法,而專案已有三處不同的判法。

## 1. 分層與依賴方向

大致對齊,有一處不對齊。

- 對齊:呼叫方向與鄰居相同。
  - 指令 → 本體 → 幫手函式。reread 本來就呼叫存量漂移那邊的函式,見 `scripts/lumos:34398` 的 `_drift_empty_tree`。
  - 反方向也有先例:存量漂移用 reread 那邊的 `_path_special_chars`,見 `scripts/lumos:38852`、`scripts/lumos:37650`。
  - 所以第二層呼叫 `_drift_load_acks` 和 `_drift_ack_key`(`scripts/lumos:37220`、`37235`)不算跨層直呼。
- 對齊:掛鉤和 CI 只透過 CLI 回傳碼接,沒有繞過工具。

### F1 新邏輯沒切 core / guarded / report
- 鄰居的做法:`_drift_retire_guarded`(`scripts/lumos:38633`)和 `_drift_m1_guarded`(`scripts/lumos:39629`)都拆成「判定、兜底、印出記帳」。回傳碼在印出之前就定好。
- 設計把第一層擋、第二層、判不了三分都塞進 `_note_reread_check`(`scripts/lumos:34927`),沒講怎麼切。
- 這支函式已經被 lint-waive,要在 2026-11-01 前拆到複雜度 10 以內。見 `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:98-101`。
- 引句:「第二層是新的小機制(讀已提交判定紀錄的內容、判結構行、比對表態),零件都用既有的」
severity: minor
- blocking: 否

## 2. 命名與錯誤處理

設定鍵名、回傳碼語意、`LUMOS_SKIP_REREAD_CHECK` 的 `skipped-env`、壞設定「照預設 block」的講法都對齊。對齊的鄰居是 `note_shape.gate`(`scripts/lumos:30343`)、`drift_check.old_sentence`(`scripts/lumos:38533`)和 `_drift_gate_config`。不對齊有四處。

### F2 掛鉤與 CI 的回傳碼處理跟鄰居不同
- 掛鉤:
  - 鄰居(每支檔有家、筆記形狀擋、drift check)的做法:
    - 所有 ≥128 先交給 `pp_stop_if_signaled`(`scripts/hooks/pre-push:70-75`)。
    - rc1 擋,並在標準錯誤印「逃生:」一段(`scripts/hooks/pre-push:380-389`、`510-523`)。
    - 其他非零一律講一句「這次沒檢查」再放行,這句話涵蓋「舊版工具沒有這個子指令」(`bound-tests-gate.md:109` 有寫)。
  - 設計:130 才停,「2 也擋」。
  - 後果:新掛鉤配舊 lumos 時,argparse 回 2,每次推送都被擋。守檔筆記對照改動計劃 144 行原本明寫這種情況回 2 放行。
  - 設計也沒提「逃生:」那段。
- CI:
  - 鄰居的做法:`|| { rc=$?; if [ "$rc" -eq 1 ]; then echo "::error::…"; exit 1; fi; exit "$rc"; }`,見 `.github/workflows/ci.yml:239-246`。
  - 設計只說「拿掉 `|| true` 與 `continue-on-error`」,沒有 `::error::` 說明和逃生寫法。reread 這步現在在 `.github/workflows/ci.yml:247-264`。
- 引句:「回傳 1 就擋、130 交給中斷處理、2 也擋並講參數錯」
severity: minor
- blocking: 否

### F3 訊息走標準輸出、帶「提醒」前綴,跟擋下型的鄰居不同
- 鄰居(`_drift_m1_report`、`_drift_retire_print`、`cmd_home_check`、`cmd_note_shape`)的做法:
  - 擋下原因走標準錯誤,開頭是「擋下:」。
  - 判不了那句統一用 `_drift_unknown_hint`(`scripts/lumos:39477`)。
- 設計:
  - 輸出維持標準輸出,沿用「回頭重讀提醒:」前綴。
  - 另寫一句講 `LUMOS_SKIP_REREAD_CHECK=1` 的略過寫法。
  - 這句話內容跟 `_drift_unknown_hint` 同形,只差寫死的環境變數名。
- 該把 `_drift_unknown_hint` 加參數共用,不要抄第三份。
- 引句:「所有輸出照舊走標準輸出(掛鉤丟掉標準錯誤)」
- 引句:「印原因與 `LUMOS_SKIP_REREAD_CHECK=1` 單次略過的寫法」
severity: minor
- blocking: 否

### F4 ⚠ 事件名:warn 記 `reminded`、判不了記 `skipped`
- 鄰居:block 記 `blocked`,warn 記 `warned`。見 `scripts/lumos:39611` 的 m1 和 `_drift_retire_report`。
- 設計:block 用 `blocked` 與鄰居一致,但 warn 沿用 `reminded`,判不了的 warn 記 `skipped`。
- ⚠ 交編排者:`reminded` 已有 18 筆歷史,RETIRE-IF 也在數它,改名會斷連續性。這是慣例對連續性,我不硬判。
- 引句:「warn 時同樣印、記 `reminded`、回 0」
severity: minor
- blocking: 否

### F5 ⚠ 子開關沒寫時的預設:固定 block,還是照總開關
- 鄰居不一致:
  - `_drift_old_sentence_config` 各管各的,預設固定。
  - `_drift_retire_config`(`scripts/lumos:38503`)沒寫時照總開關 gate。理由是「專案設 gate=warn 只提醒的,升級後不會被新檢查擋」,這是較新的先例。
- 設計選固定 block,所以把 `drift_check.gate: warn` 的專案也一併擋下。
- 存量漂移守衛 82 行還有一條有效的 RULE(since / retire / confirmed 俱全,2026-09-30 確認),寫著「m1 沒寫是 warn,不跟 gate 走」。設計要靠人裁推翻,計劃沒點名要把這條標 superseded。
- ⚠ 交編排者定奪。
- 引句:「`_drift_old_sentence_config` 沒寫、寫 null、讀不成 JSON、`drift_check` 不是物件、整份設定不是物件、值看不懂時一律回 block」
severity: minor
- blocking: 否

## 3. 第二種做法

有一個 major,兩個 minor。

### F6 另造一套「結構行」判法
- 專案已有三種判法,各有理由:
  - `INVARIANT_RE`(`scripts/lumos:5403`)錨定在 `KEY:` 開頭。旁邊註解明說:「排除散文中提到標記的誤報」。
  - `RULE:` 只在摘要區認 `startswith`。見 `_retire_lines`(`scripts/lumos:35951`)、`scripts/lumos:31405`。判區域靠 `_notelines_regions`(`scripts/lumos:30347`),接續行靠 `_ns_summary_logical`(`scripts/lumos:31963`)。
  - `[test:` 是各行型自己抽。
- 設計在整份筆記的任何一行,去掉列表符號後,用「含 `★INVARIANT★`」「含 `[test:`」和「`RULE:` 開頭」判。
  - 這恰好是 `INVARIANT_RE` 註解要避開的誤報:散文提到標記。
  - 也會把正文列表裡的 `- RULE:` 算成結構行,專案其他地方不這樣認。
- 同一個判斷第二層擋行和 `_drift_ack_line_err`(`scripts/lumos:37453`)都要用,分屬不同家。設計沒說放哪一支。
- 建議收成一支共用謂詞,放在 reread 常數那段,照 `_path_special_chars` 的先例。內部用既有的區域判斷和 `INVARIANT_RE` 等錨定規則。
- 引句:「以 `RULE:` 開頭、或含 `★INVARIANT★`、或含 `[test:`」
severity: major
- blocking: 是

### F7 表態比對可能手寫成第二條路
- 鄰居:m1 和 retire 讀完表態都走 `_drift_split_acked`(`scripts/lumos:37239`)。一般種類的分支(`scripts/lumos:37264`)用 `(路徑, 原文, kind)` 比對,reread 丟進去就能用。
- 設計只寫「用 `_drift_ack_key` 比對」,沒指名 `_drift_split_acked`。若手寫迴圈,就多一條比對路徑。
- 該指名走 `_drift_split_acked`。
- 引句:「用 `_drift_load_acks` 讀頂端提交的樹,`_drift_ack_key` 比對路徑與原文」
severity: minor
- blocking: 否

### F8 ⚠ 「判不了」的邊界跟鄰居不同,而鄰居本身就不一致
- drift check 的三分法跟設計一致:參數錯回 2,環境沒東西回 0,判不了算要處理。見 `cmd_drift_check` docstring(`scripts/lumos:38586`)。
- 但 `_note_audit_resolve`(`scripts/lumos:33701`)在「讀不到檔案清單」時是靜默回 0(`scripts/lumos:33757`)。每支檔有家和筆記形狀擋同一種情況也明寫 fail-open(`scripts/lumos:30222`、`32991`)。
- 設計把「讀不到檔案清單」歸到判不了,block 時回 1。與 drift check 的同一道前置不同,也與另外兩道不同。
- 實作上,resolve 的 reasons 把淺層 clone、沒有圖譜、讀不到檔案清單全標成 `skipped`。要切開就得改共用函式,或回頭比對訊息文字。守檔筆記對照改動計劃 205 行明說不要用比對文字的做法。設計沒說怎麼切。
- ⚠ 交編排者:先定「讀不到檔案清單」要不要擋,再定怎麼表達。
- 引句:「判不了(git 呼叫失敗、讀不到檔案清單、逾時、讀不了或讀不懂判定紀錄、沒預料的例外)」
severity: minor
- blocking: 否

## 4. 落點

三篇 lands_in 的分工合理,不用另開新篇,各篇該寫的東西如下。

- `Systems/存量漂移守衛`
  - 負責:`drift ack` 家族、old_sentence 開關與 doctor 行、掛鉤與 CI 裡呼叫 reread-check 的那一段。
  - 要改寫的舊句:`存量漂移守衛.md:82` 的 RULE(要標 superseded)、`:125`「只提醒、恆放行」、`:129`「沒寫是 warn」。
- `Systems/筆記內容審`
  - 負責:reread-check 判什麼,也就是兩層和判不了的分法。
  - 要改寫:`筆記內容審.md:70-87` 的 reread 段。
  - `:98-101` 的複雜度放行要一起處理(見 F1)。
- `Systems/bound-tests-gate`
  - 負責:掛鉤順序和回傳碼慣例。
  - 要改寫:`bound-tests-gate.md:107-109` 整段「只提醒的回頭重讀」。
  - `t_prepush_gates_stop_on_signal` 數行數的那條也會變,計劃只列了三支要改的測試,漏了它。

### F9 轉擋後的配套沒交代:消費專案 CI 範本與版本號
- 消費專案 CI:
  - 守檔筆記對照改動計劃 94 行寫「轉擋那天另案處理」。
  - 其他會擋的閘都有 doctor 給的 CI 範本或提醒:`_DRIFT_CI_STEP`(`scripts/lumos:39913`)、note-shape 的 doctor 行(`scripts/lumos:32315`)。
  - 設計沒說 reread 這步要不要有。`lumos update` 帶不到 CI,所以消費專案的 `--no-verify` 後盾會缺。
- 版本號:
  - v1.2 的先例是「掛鉤改了就升版,CHANGELOG 同版,讓舊專案被提示 `lumos update`」。見 `CHANGELOG.md:9`。
  - 設計只寫「CHANGELOG 同版寫明」,沒說升 `LUMOS_VERSION`。
- 引句:「CHANGELOG 同版寫明」
severity: minor
- blocking: 否

不對齊共 9 條,其中 major 1 條
