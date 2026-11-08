severity: major

**審查範圍**:`_batch4_have` 的新寫法、補前綴的 25 列、重跑的樣本、測試改壞覆蓋。`python3.14 scripts/test_lumos.py -k kt_catalog` 195 項全綠。我沒有改 repo 任何檔,下面的改壞是在 scratchpad 用複製的邏輯模擬的。

**回歸鏡頭的結論**
- **`_batch4_have` 判斷:** 對真型錄所有列都判對。真型錄的通電批次共 11 種形狀,含 `告警帶寫法=批一、批四(…)`、`批一(只有提示級規則,預設不接)、批四(…)` 和 `批四(…);當下推相關列=批二`,全部 0 個位置問題。
- **「之間不准有別的 =」:** 目前沒有誤報既有寫法。批一括號裡沒有 `=`。
- **呼叫端:** 回傳型別改成 tuple,只有 `_wiring_row_problems` 一個呼叫端(`check.py:442`),已跟上。`scripts/`、`configs/` 沒有別處用到。
- **補前綴的 25 列:** 我用 `batch4_candidates` 對比修前修後,新增恰好 38 個候選,全是真的檢查 id,沒有把非 id 的字補成前綴。仍沒前綴的是 `detekt:`、`dagger-lint:`、`structured-coroutines:` 這類口徑本來不認的前綴。PERF-3 的 `WrongThreadInterprocedural(預設關)` 和 ARCH-28 的 `FragmentConstructorInjection`(廠商待查)沒補是對的。
- **角色鏡頭(be-api-compat、be-authz):** 這份改動是型錄自檢工具,沒有對外 API,也沒有端點授權,兩題不適用。

**重跑樣本的抽查**
我抽了 UI-84、UI-13、ARCH-71、DATA-46、API-44、ARCH-25、ARCH-79、ARCH-88、UI-16、UI-23、UI-3、UI-87、UI-100、API-47、DATA-79、ARCH-77,逐支對照壞寫法欄。
- **UI-84:** 已拿掉預設值,判定改擋不到,理由欄寫明同函式只報 ModifierWithoutDefault。
- **UI-13:** 改成明確的 `s.value` 讀寫。
- **ARCH-71:** manifest 外殼只剩 exported=true,沒有 intent-filter。
- **DATA-46:** 沒有權限宣告,判定改擋不到。
- **API-44:** 第二種另開模組,targetSdk 23、minSdk 23。
- **其餘 11 列:** 樣本都照壞寫法欄寫,沒有另加觸發條件。DATA-79 把佔位字串換成真形金鑰是上輪樣本席要求的。
- **行號:** UI-16、UI-3、UI-23、UI-100、ARCH-79、ARCH-25 判定理由裡的行號,跟樣本檔現在的行號對得上。

---

**1.**
severity: major
blocking: 是

**批四位置檢查三個條件裡有兩個,拿掉後測試照綠。** 檔案:`configs/ast-grep/kotlin-android/check.py` 的 `_batch4_have`(約 `check.py:387-398`);測試是 `scripts/test_lumos.py` 的 `t_kt_catalog_batch4_evidence`。

引句:「    if i < 0 or ms[0].start() < i or "=" in batch[i + len("告警帶寫法="):ms[0].start()]:」

- **失敗場景:** 這行是上輪 a2(批四寫在別的子段要報)的修補核心,有三個條件。測試只補了兩個位置改壞例:
  - `行為測試或正向約束=批四(…);告警帶寫法=未接(x)`,只踩到第二個條件 `ms[0].start() < i`。
  - 兩個批四括號,踩到 `len(ms) > 1`。
- **沒被守住的兩種輸入:**
  - 批四寫在 `告警帶寫法=` 之後、但在別的子段:`告警帶寫法=未接(x);行為測試或正向約束=批四(Android Lint)`,對應第三個條件(兩者之間有別的「=」)。
  - 完全沒有 `告警帶寫法=`、只有 `批四(Android Lint)`,對應第一個條件 `i < 0`。
- **為什麼會漏過:** 這種批四標籤剛好等於判定要的標籤時,後面的 `have != want` 比對也不會報。位置檢查是它唯一的防線。
- **最小重現(模擬,不是實改 repo):** 在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/5b6d202a-9139-47f7-b6b9-deb227707ba4/scratchpad/m.py` 把三個條件分別拿掉,餵測試現有的兩個輸入和上面兩種新輸入。結果:

| 變體 | 測試現有兩輸入 | 新輸入(位置在別的子段、無 `告警帶寫法=`) |
|---|---|---|
| 原邏輯 | 報、報 | 報、報 |
| 拿掉「=」條件 | 報、報 | 不報、報 |
| 拿掉 `i<0` 條件 | 報、報 | 報、不報 |

  測試現有輸入在變體下都照報,所以測試不會翻紅。
- **修法:** 補兩道改壞例,各自逐道拿掉後要先紅再綠。
- **為什麼標 major:** 被保護的是守衛,而且這個缺口正是 r1 a2 想補的那類盲區。

---

**2.**
severity: major
blocking: 是

**UI-54 的實測狀態欄還寫「真跑沒報」,跟判定表矛盾。** 檔案:`skills/kotlin-idioms/checks-catalog.md:381`,對照判定表同檔 `:922-923`。

引句:「未測;Android Lint 照這列壞寫法真跑沒報 ComposeModifierMissing(2026-11-08,見〈接電證據〉;本體空的元件不報)」

- **失敗場景:** 這次重跑把樣本補上 `Text(title)`,UI-54 兩筆判定都從擋不到改成擋得到,通電批次也改成 `批四(CI 範本:Android Lint;推送前:detekt 外掛 compose-rules)`。第 10 欄卻沒跟著改,還說 Android Lint 沒報。
- **誰會被誤導:** 型錄是單一來源。讀實測狀態欄的人會以為 ComposeModifierMissing 擋不到,與同一列的批四標記和判定表衝突。
- **自檢為什麼沒抓到:** 自檢只比對判定表與通電批次,第 10 欄的文字它不管。
- **其他列:** 型錄裡帶「見〈接電證據〉;」字樣的列只有 API-9、UI-11、UI-54 三處,其中只有 UI-54 的判定在這次重跑翻面。
- **修法:** 把第 10 欄改成「未測」或改寫成與判定一致的說法。
- **重現:** 在 repo 根跑 `grep -n "照這列壞寫法真跑沒報" skills/kotlin-idioms/checks-catalog.md`,會命中第 381 行。同一列的判定表(`:922-923`)是擋得到。

---

最高等級 major;blocking 2 條

臨時檔只有 scratchpad 的幾支 py(`p.py`、`q.py`、`c.py`、`m.py`),沒有建 `/tmp/lumos-seat-work/` 目錄。
