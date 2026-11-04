severity: minor

整體判斷:這份設計沒有引入第二種做法。祖先判斷、截止時間、`_LENS_SHA_RE`、stderr 的 `[spec-gate]` 前綴都用既有的。測試替身也沿用既有的「換掉模組屬性、finally 換回」寫法。不一致的 6 處都在細節,沒有跨層直呼。

## 第 1 問:分層與依賴方向

對齊。新邏輯放在 `_redbase_branch_rows` 裡,它已經在叫 `_lens_git`、`_lens_full_sha`、`_lens_fork_point`、`_gov_rows_delta`,新加的 git 呼叫仍在同一層。

- 判祖先走 `_lens_git_dl`,file: `scripts/lumos:64679`。
- 帶截止時間的鄰居:`_note_reread_own_fps`,file: `scripts/lumos:52749`。
- 同函式既有的說明句也印 stderr、前綴 `[spec-gate]`,file: `scripts/lumos:14384-14385`。

有兩處跟鄰居不一樣。

severity: minor
blocking: 否
引句:「再用既有的 `_push_rev` 問那個提交在不在」
- 「祖先判斷 rc 0/1/其他,其他再查存在」這個區塊,鄰居 `_note_reread_own_fps` 已經手寫了一份,file: `scripts/lumos:52749-52754`。
- 那一份用 `cat-file -e` 問存在,本設計改用 `_push_rev`(`rev-parse --verify`)問,file: `scripts/lumos:64687-64697`。
- 另一個鄰居 `_secev` 的 `ancestor()` 也是同一個 `merge-base --is-ancestor` 呼叫,file: `scripts/lumos:10302`。
- 這是同一種做法的又一份複製,不算第二種做法。但最近的鄰居跟本設計在「怎麼問存在」上不同,而且計劃沒寫為什麼不照鄰居,也沒說要不要抽共用。

severity: minor
blocking: 否
⚠ 判不準:本設計刻意維持舊行為,但方向跟鄰居相反。
引句:「沒有 head_sha、不像提交編號(既有的 `_LENS_SHA_RE`)、git 叫不起來或過了截止時間,照舊留」
- 鄰居 `_note_reread_own_fps` 在 git 判不了時「當不是」,file: `scripts/lumos:52735` 的說明句與 `:52753-52754`。
- 同一個函式在讀帳失敗時回 `[]`,也就是整批不算,file: `scripts/lumos:14384-14386`。
- 本設計的 git 失敗則是整批照留。
- 計劃只說「跟現在一樣」,沒講為什麼兩個方向並存。

## 第 2 問:命名與錯誤處理

大致對齊。有兩處跟鄰居不一致。

severity: minor
blocking: 否
⚠ 判不準:計劃沒指名用哪個淺複製判斷。
引句:「查不到而且 repo 不是淺複製(`rev-parse --is-shallow-repository` 回 false)就丟」
- 專案裡淺複製判斷有 4 種寫法:
  - `_git_is_shallow`,git 失敗回 False、逾時丟例外,file: `scripts/lumos:12021-12030`。
  - `_e2e_parent` 用 `!= "false"` 判,失敗算淺,file: `scripts/lumos:42762`。
  - 三處用 `_lens_git` 加 `== "true"`,file: `scripts/lumos:48695`、`:50236`、`:50989`。
- 本設計「回 false 才丟」只跟 `:42762` 同向。
- 若實作者選了 `_git_is_shallow`,git 失敗會被當成「不是淺複製」而把紀錄丟掉,跟計劃自己寫的「git 叫不起來照舊留」衝突。
- 計劃沒說這一次查詢算不算進整批 10 秒截止時間。

severity: minor
blocking: 否
引句:「整批共用一個 10 秒截止時間」
- 鄰居的預算都寫成具名常數:`_NOTE_REREAD_BUDGET_SEC`(file: `scripts/lumos:53164`)、`_BACKING_BUDGET`(`:25359`)、`_DRIFT_BUDGET_SEC`(`:57380`)。上限也具名,例如 `_GOV_TAIL_CAP`(`:4423`)。
- 本設計的「10 秒」「200 個」只寫成散文數字,沒指名常數。
- 截止時間由函式自己建。鄰居 `_gov_rows_delta` 與 `_note_reread_own_fps` 都是由呼叫端傳 `deadline`,file: `scripts/lumos:60940`、`:52749`。

## 第 3 問:第二種做法

沒有引入第二種做法。三項對照:

- 判祖先:沿用 `merge-base --is-ancestor`,不另寫截止時間機制。
- 測試替身:鄰居已有「換模組屬性再 finally 換回」(file: `scripts/test_lumos.py:56755-56761`)和「`calls.append(1) or real(f)` 數呼叫」(file: `scripts/test_lumos.py:22045-22047`)兩種。本設計換掉 `_raw_test_titles` 與 `_TitleIndex` 再 finally 還原,沿用這套。
- 載入單例:沿用 `_load_lumos_inproc`,file: `scripts/test_lumos.py:238-251`。

只有一處在寫法上無前例。

severity: minor
blocking: 否
⚠ 判不準:這是少一份複製,算改良還是不一致,由你定。
引句:「`_TG_CONST_PAT` 的字串那段改成用 `_TG_LIT_PAT`(已認三引號),不另寫一份」
- 專案裡所有 `_*_PAT` 都是獨立的字面字串,搜不到「一個樣式常數拼進另一個」的前例。
- 鄰居的做法是複製加註解:`_TG_LIT_PAT` 自己就是抄 `_C_STRIP_PAT` 的三引號那段,註解寫「寫法同 `_C_STRIP_PAT`」,file: `scripts/lumos:49068-49072`、`:6786`。
- 本設計要搬定義位置再拼字串,是第一次出現這種組法。
- `_TG_CONST_PAT` 現在是整串 `\s*(?:…|"…"|'…')\s*`,file: `scripts/lumos:49020`。要拼進去需包 `(?:…)`,並維持「用時才編」的 `_lazy_re`(file: `scripts/lumos:6774-6778`)。

## 第 4 問:落點

大部分合理,漏一篇。

- 第 1 項落在 `Systems/規格閘`:它的 responsibility 明寫「規格閘紅燈版的寫入與判綠觀測」,file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:6`。
- 判綠那條 WHY 要同篇更新,因為它寫的是「同一條分支之後再跑出紅」,file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:51`。
- 第 3 項落在 `Systems/test-guard`:字串常值樣式那條 WHY 已在該篇,不必另開,file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:43`。

severity: minor
blocking: 否
引句:「②效能測試改成走正式的快取路徑 `_name_collision_reason`、數標題索引建了幾次(1000 個名字只建 1 次)」
- S3 綁的 `t_name_collision_scales` 與「標題索引每平台建一次」的敘述,現況記在 `Systems/test-profile-multiplatform`,file: `docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md:85`。
- 該篇不在 `lands_in` 裡。
- 建議補進 `lands_in`,不必另開新節點。

不對齊共 6 條,其中 major 0 條。
