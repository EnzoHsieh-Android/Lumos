severity: major

審的是 r2 修訂稿,我替極端輸入發聲。已讀全文逐節對照程式碼。有 9 條 finding,其中 4 條 major、5 條 minor。

**實務隱患鏡頭,逐類答:**
- 併發:無。放行檔上鎖沿用既有做法,spec 只是沿用。
- 效能與記憶體:有,見 finding 4 末句。
- 資安與外來文字回顯:有,見 finding 4。
- 設定被破壞時的降級方向:有,見 finding 3。
- 兩次推送疊加的繞法:有,見 finding 2。
- 金流、對外送出、不可逆:無,spec 已寫「已排除」,只改判定與文件。

## 用詞、範圍 1(規則例外,S1)

已讀。官方頁已核對:`MediaSessionService extends LifecycleService`,`MediaLibraryService` 為其子類別,spec 的依據成立。S1 這節無 finding。

## 範圍 2(高風險路徑清單,S2)

**1.**
severity: major
blocking: 是,spec 沒定義「這次改到的檔」從哪來;照現有分級函式的 `files` 參數取,會漏掉最該嚴審的幾種改動。
引句:「這次改到的檔只要有一支等於清單裡的檔、或在清單裡的目錄底下,就判 high。」
證據:`_pitfall_tier` 的 `files` 實際是 `list(added) + list(changed_lines)`(`scripts/lumos:65214`)。我在臨時庫實跑,清單是 `src/auth`、`docs/policy.md`、`config/prod.json`。同一個提交裡做了下列改動:
- 刪 `docs/policy.md`;
- 刪 `config/prod.json`;
- 純改名 `src/auth/Login.kt` 到 `src/Login.kt`;
- `src/auth/run.sh` 只改權限位元;
- 改 `src/auth/key.bin` 的二進位內容;
- 正常編輯 `src/auth/Keep.kt`。

`git diff --name-only --no-renames` 列出 7 條路徑,傳進 `_pitfall_tier` 的卻只有 `['src/auth/Keep.kt','src/auth/Keep.kt']`。

這組結果有三個後果:
- 漏判:被刪的清單檔、搬出清單目錄的檔、只改權限的檔、二進位檔的改動,分級都不會升 high。刪除 `.md` 或 `.json` 不進 `changed_lines`,是因為 `_stack_changed_ok` 擋掉這些副檔名。
- 重複:同一支檔在列表裡出現兩次,理由句「最多 3 支檔名…等 N 支」會數成 4,實際只有 2 支。
- 先例:相鄰的殘留分級自己用 `git diff --name-only -z --no-renames`,理由是「改名的舊路徑算改到」(`scripts/lumos:64768` 起的 `_residual_tier_hits`)。spec 沒沿用,也沒說去重。

**2.**
severity: major
blocking: 是,「起點與終點取聯集」只擋同一次推送,分兩次推送就能拆掉清單,與「人工不能把分級往下調」矛盾。
引句:「所以同一次改動拿掉某條路徑不會讓自己降級,新加的當次就生效。」
- 推送 1 只刪掉 `.lumos/config.json` 或清空 `risk_high_paths`。`.lumos/config.json` 本身不在清單裡,這次分級照常是 standard 或 light。
- 推送 2 改 `src/auth/Login.kt`。起點與終點的設定都沒清單,規則「設定檔不存在或沒有這個鍵 → 不影響」生效,分級是 standard。
- 殘留機制明講防這種「先縮範圍、下次再改程式」,所以縮小或拿掉本身就判 high(`removed`、`shrunk`,`scripts/lumos:64454` 的 `_residual_tier_reasons`)。
- repo 另有先例:宣告改讀「起點與主線分叉點」那一版,理由是被審分支不能自己改宣告決定怎麼被審(`_lens_trusted_ref`,`scripts/lumos:63651`;目標架構用它)。spec 讀的「起點版」是遠端分支頂端,分支自己上次推的就是它,沒有取主線版本。
- 設定檔被改名也一樣:改名後兩版都讀不到清單。

**3.**
severity: major
blocking: 是,「JSON 解析失敗就判 high」不分專案有沒有用這個鍵,選用功能會變成壞設定專案的全域擋閘。
引句:「設定檔讀得到但 JSON 解析失敗、或 `risk_high_paths` 不是字串清單、或超過 200 項 → 判 high,理由寫「risk_high_paths 讀不出」,跟殘留索引讀不出的方向一致。」
- 殘留索引的 `head_bad` 有條件:讀不出而且「起點有殘留、或這次推送動過索引」才升 high(`scripts/lumos:64812`)。spec 說「方向一致」,卻拿掉這個條件。
- 目標架構更明確:「沒宣告的專案設定壞掉,架構對齊段不該多東西」(`scripts/lumos:63687`)。
- 具體輸入:從沒用過 `risk_high_paths`、`.lumos/config.json` 卻帶 UTF-8 BOM(`json.loads` 實測拋 `JSONDecodeError`),或合併衝突標記 `<<<<<<<`,或頂層是 `[]`。這個專案之後每次推送都是 high,要代碼審留痕才推得出去。
- 修這個設定檔的那次推送,起點版也讀不出,自己先被判 high。
- 狀態缺漏:現成讀法 `_lumos_config_at_ref`(`scripts/lumos:63624`)有 ok、missing、unreadable、git-failed 四種狀態,spec 只分「不存在」與「解析失敗」。「git 本身讀不出(逾時、物件遺失)」、「頂層不是物件」、「非 UTF-8」都沒定義。

**4.**
severity: major
blocking: 是,spec 說靠「對不到任何檔」那行防寫錯被靜默略過,但那行在推送路徑上看不到,也沒定義輸出在哪。
引句:「清單裡某條路徑在終點那一版一支檔都對不到時,pitfalls 的輸出多印一行「risk_high_paths 這幾條對不到任何檔」,不影響分級」
證據:
- `scripts/hooks/pre-push:567` 呼叫 `pitfalls --json 2>/dev/null`;`:574` 的人讀輸出只在 `tier=high` 時才印。寫錯的條目恰恰讓分級不是 high,所以那行從不出現。
- 在 `--json` 模式多印一行純文字,會害 `:616` 的 `json.load(sys.stdin)` 失敗,`affected_keys` 取不到。spec 沒說這行進 JSON 欄位還是純文字。
- 配套缺口:repo 對同形資料已有 `_e2e_relpath_err`(`scripts/lumos:44884`)在設定時擋掉不合格式;spec 只借了比對、沒借驗證。以下條目各自靜默變成死條目:
  - CODEOWNERS 風格的 `/src/auth/`(spec 自己借 CODEOWNERS 的形狀)
  - `src/auth/*`
  - `src\auth`
  - `src//auth`
  - `.`
- 這些條目印出時沒說要經 `_plain_label` 清洗(spec 只清洗檔名)。
- 效能:判「終點版一支檔都對不到」要列整棵樹,範例測試 `_risk_paths_unmatched(root, "HEAD", …)` 也是這個形狀。spec 的效能句只算「多兩次 git 讀檔」,低估了。
- 受影響呼叫:`pitfalls` 在一次推送會被呼叫多次(掛鉤兩次,`code-loop check` 再一次)。

**5.**
severity: minor
blocking: 否,只影響理由句與接縫,分級結果同為 high。
引句:「多個理由並存時照既有寫法用「;」串起來,不互相蓋掉。」
證據:`_pitfall_tier` 現在的寫法是殘留命中就提早 `return "high", ";".join(why) + (";另命中風險型樣或新告警" if claims else "")`(`scripts/lumos:64523` 起)。spec 另一句寫「在殘留索引那一步之後」讀 `risk_high_paths`。照字面實作,殘留命中時提早回傳,高風險路徑理由與「讀不出」理由就被蓋掉,與「不互相蓋掉」矛盾。要不要把高風險路徑理由併進那個提早回傳的字串、「另命中…」尾巴怎麼接,spec 都沒定。

## 範圍 3(行內忽略註解,S3)

**6.**
severity: major
blocking: 是,多行 `@Suppress(` 在規則與指紋兩層都沒定義,結果是漏數或一次放行整檔所有規則。
引句:「但括號裡的字串全是全大寫加底線的(例如 `"UNCHECKED_CAST"`,那是 Kotlin 編譯器的警告名,不是檢查工具的規則名)就不算」
證據:
- 逐行掃描時,多行寫法 `@Suppress(\n    "MagicNumber"\n)` 的開頭行 `@Suppress(` 括號裡沒有字串。「全是…」對空集合成立,就會漏數;若改成「沒字串就算」,多行的 `"UNCHECKED_CAST"` 又誤報。兩種寫法 spec 沒選。
- 我用真實的 `_lint_new_key` 驗證:同一檔裡一個 `@Suppress(`(下一行 `"MagicNumber"`)與另一個 `@Suppress(`(下一行 `"LongMethod", "ComplexMethod"`),指紋都是 `lumos/inline-suppression|A.kt|    @Suppress(`,完全相同。放行一次,等於整檔所有「開頭單獨一行」的 `@Suppress(` 都放行,不管壓的是什麼規則。
- 括號裡有幾十條規則時,ktlint 與 Android Studio 的自動排版預設就是多行,這是常態輸入。
- 另有歧義:「(正規式,除非註明都不分大小寫)」若連「全大寫」判斷也套 `re.I`,`MagicNumber` 會被當成編譯器警告名而不算。

**7.**
severity: minor
blocking: 否,命令沒被認出來時沒有任何訊號,但屬於認法限制。
引句:「沿用 detekt 判定那套命令切段(`_detekt_walk_segments` 剝環境變數與包裝詞、展開 `sh -c`),每段取第一個詞的檔名(`_cmd_basename`)」
證據:我對真實的 `_detekt_walk_segments` 實跑,下列寫法產出的段首詞都不是工具名,所以整條命令不認:
- `timeout 60 ruff check {LINT_FILES}`:第一個詞是 `timeout`,`_SHELL_WRAPPERS` 只有六個(`scripts/lumos:40311`)。
- `(ruff check …)`:第一個詞是 `(ruff`。
- `bash -lc '…'`:只認 `-c`,`-lc` 整段被丟掉。
- `python3.14 -m ruff …`:spec 只列 `python -m`、`python3 -m`,本 repo 測試就要求 3.14。
- `uvx ruff@0.14.0 …`、`npx eslint@9 …`:「下一個非選項的詞」是 `ruff@0.14.0`,spec 沒說去版本尾巴。
- `npx -p eslint@9 eslint …`、`uv run --python 3.12 ruff …`:下一個非選項詞是選項的值。
- `ruff.exe`、`eslint.cmd`。

認不出時行為是靜默為 0 條,也沒有「這條命令沒認到任何工具」的提示。這些寫法在 spec 裡沒有明說。

**8.**
severity: minor
blocking: 否,表的涵蓋範圍是已知限制,但缺口目前就存在,延到 2027-05 才核對太晚。
引句:「對照表跟 Systems/linter精選目錄 的工具菜單核對一次,菜單多了的工具補上它的忽略寫法」
證據:目錄現在就有 sqlfluff(`.sql`;經 `lumos sqlfluff-sarif` 橋接,`-- noqa` 不在表裡)、Java 的 PMD 與 Checkstyle(2026-09-13 實跑通)、Dart analyzer。對照表都沒有。`SELECT 1 -- noqa` 在 sqlfluff 命令下是 0 條。這是寫 spec 當下查得出的,不必等半年後的 REVISIT。

**9.**
severity: minor
blocking: 否,對一行兩種寫法、第一次推送這兩種輸入,規則定義不全。
引句:「同一份快照裡,同一支檔同一行只算一次(多條命令都認到同一個工具時不重複)。」
- 一行兩種寫法:`x = 1  # noqa  # type: ignore`,`lint.json` 同時宣告 ruff 與 mypy。同一行只算一次,訊息「(<工具>)」寫哪一個沒定義。作者照訊息拿掉 `# noqa` 後,行內容變了,指紋換新,又是一條新增(spec 自己承認「改一行就算新增」)。
- 與「不追溯」矛盾:「已經存在的忽略註解不追溯,只看這次新加的」只在起點版有檔時成立。下列輸入都會讓既有忽略註解全算新增:
  - 起點是空樹:`_lens_push_base` 在「找不到主線,從空樹算」(`scripts/lumos:68633` 附近)。
  - 檔被判成刪除加新增,例如改名相似度低於 50%:`_lint_new_changed_files` 的 `A` 分支,基準版為 None(`scripts/lumos:42697`)。

  spec 的「Kotlin 專案 `@Suppress` 量大」只說只數規則名,沒給這兩種輸入的出口。

## 範圍 4、5、不做、天花板、驗收與預期值表、回退

已讀。README 中英兩版(`README.md:450`、`README.en.md:450`)已是目標句,數字與 Verification 原文(Haiku 20/25 對 12/25、Opus 四組 25/25、丙組 20 有「要打折扣」)核對相符。外部宣稱已核對:ruff 文件的 `ruff: ignore`、`file-ignore`、`disable` 與 `noqa` 不分大小寫屬實;detekt 文件的 `@Suppress` 寫法與前綴屬實。範圍 4、不做、驗收條款(含 S4)與回退無 finding。

最嚴重 severity: major;blocking 共 5 條(第 1、2、3、4、6 條)。
