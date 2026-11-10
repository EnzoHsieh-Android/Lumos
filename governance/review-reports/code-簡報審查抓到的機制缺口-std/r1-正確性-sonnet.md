severity: major

我把規則與逐例表在複本上重放、逐項改壞再跑,沒有直接跑 `scripts/test_lumos.py`,因為 repo 唯讀。重放用的是同一支 `scan`,加上 `check.py`(結果「規則 228 條,問題 0 個」)。重放環境與腳本在 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/正確性-sonnet/`(`pack/` 是規則包複本,`harness/` 是腳本),收貨後由編排者刪。

## 1. 正規式的 `androidx.lifecycle.` 前綴沒有任何一例守著
severity: major
blocking: 是
引句:「regex: '^(androidx\.lifecycle\.|androidx\.media3\.session\.)?(LifecycleService|MediaSessionService|MediaLibraryService)\s*\('」
file: `configs/ast-grep/kotlin-android/rules/state.yml:190` 就是這條正規式。
file: `docs/lumos-toolchain-knowledge/Projects/簡報審查抓到的機制缺口_計劃.md:24` 範圍 1 寫明「可帶 `androidx.lifecycle.` 或 `androidx.media3.session.` 前綴」。
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:66` 的 WHY 規定每個正規式選項與錨點都要有例子變紅,否則記成等價改壞。

- **改壞**:把 `(androidx\.lifecycle\.|androidx\.media3\.session\.)?` 改成 `(androidx\.media3\.session\.)?`。
- **結果**:C227~C233 七例的命中數與行號全部不變(C227~C230 零命中,C231 在 [5],C232 在 [6],C233 在 [6]),`check.py` 也過。
- **為什麼測試抓不到**:逐例表只有 C228 用了 `androidx.media3.session.` 前綴,沒有任何一例寫 `androidx.lifecycle.LifecycleService()`。
- **會出錯的輸入**:`class S : androidx.lifecycle.LifecycleService() {\n    fun f() {\n        lifecycleScope.launch { repo.changes.collect { upload(it) } }\n    }\n}`。
- **新舊差別**:原規則零命中,改壞後報在第 5 行,等於把這次修補要放行的寫法又擋回去。
- **補哪一例會翻紅**:`C234.kt` 放上面那段,預期零命中。
- **缺口**:`test_lumos.py` 的 docstring 列的改壞只有「拿掉 media3 前綴 → C228 紅」,沒有 lifecycle 前綴;repo 內也沒有等價改壞的卷證。

## 2. docstring 把 `^` 錨點歸給 C231,但 C231 只守得住建構子括號
severity: minor
blocking: 否
引句:「regex 拿掉 ^ 錨點與建構子括號、改成名字出現就算 → C231 紅」
file: `scripts/test_lumos.py:127304` 是 docstring 所在的函式 `t_kotlin_rulepack_security_rules`。

- **只拿掉 `\(`**:C231 紅,因為 `MediaSessionService.Listener` 不再被排除。
- **只拿掉 `^`**:七例全綠,`check.py` 也過。
- **拿掉 `^` 的效果**:`class S : com.acme.LifecycleService()` 與 `class S : BaseLifecycleService()` 從「報 1 次、第 5 行」變成零命中。計劃〈不做〉寫自寫基底類別「照舊報」,這兩個寫法也在這一帶。
- **只拿掉 `\s*`**:七例全綠。`LifecycleService ()` 這種寫法實務上罕見,算近似等價。
- **docstring 的問題**:只有同時拿掉 `^` 與 `\(` 才紅,docstring 讓人以為 `^` 單獨有守。

## 3. ProcessLifecycleOwner 的「照報」寫成無條件,但放在 Service 類別裡實際不報;逐例表也與計劃預期值表不一致
severity: minor
blocking: 否
引句:「不報外圍類別自己繼承 LifecycleService、MediaSessionService、MediaLibraryService 的收集,ProcessLifecycleOwner 照報」
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:71` 是這條 WHY。
file: `docs/lumos-toolchain-knowledge/Projects/簡報審查抓到的機制缺口_計劃.md:52` 的 [S1] 與 `:64` 的預期值表都寫成無條件「照報」。
file: `scripts/test_lumos.py:127254` 的 C232 用的是 `class App : Application()`。

- **會出錯的輸入**:`class S : LifecycleService() {\n    override fun onCreate() {\n        super.onCreate()\n        ProcessLifecycleOwner.get().lifecycleScope.launch { session.state.collect { show(it) } }\n    }\n}`。
- **實跑結果**:零命中,因為外圍類別繼承 `LifecycleService`。
- **文件與程式的矛盾**:[S1] 同一條裡,「Service 內不報」與「ProcessLifecycleOwner 的收集照報」對這個輸入給出相反答案,沒寫哪個優先。WHY 的「因」說 PLO 的 STARTED 就是 App 在前景,「正是這條規則管的情況」,這個理由在 Service 裡同樣成立。
- **測試沒覆蓋**:沒有任何一例涵蓋「Service 裡用 PLO」。
- **預期值表與 C232 不一致**:計劃預期值表第六列寫「Fragment 裡 `ProcessLifecycleOwner…`」,C232 卻用 `Application`;壞例樣本檔用的是 `BannerFragment`。
- **要裁的事**:這個輸入要報還是不報,請編排者裁並寫進計劃與 WHY。

## 4. 新 Issue「放行綁指紋…」的 `[repro:]` 照字面做不會重現
severity: minor
blocking: 否
引句:「新加兩行一模一樣的 except Exception: # noqa: BLE001,先放行其中一條的指紋」
file: `scripts/lumos:42855` 是 `_lint_new_diff_claims`,`scripts/lumos:43267` 的 `kept = [c for c in new if c.get("key") not in waivers]` 是過濾那行。

- **根因本身是對的**:我在臨時 repo(ruff 選 BLE)實測,同檔兩行一模一樣的 `except Exception:` 得到同一個指紋 `3e7a3633b3943108`,`lint-waive` 放行一次後,`lint-new` 回報「沒有新增的告警」,第二行不再列出。
- **repro 的問題**:repro 帶了 `# noqa: BLE001`。同樣的 repo、選 BLE,兩行都加 `# noqa: BLE001`,`ruff check` 輸出「All checks passed!」,`lint-new --diff` 回報「沒有新增的告警(狀態 clean)」。沒有告警,就沒有指紋可放行,照 repro 做無法看到 Issue 說的現象。
- **缺的前提**:Issue 沒寫要先在 `.lumos/lint.json` 接上 ruff,也沒寫去掉 noqa。

## 鏡頭 4 逐項
- **(a) regex 對 delegation_specifier 文字**:
  - 該放行且放行的(實跑):`LifecycleService()`、`androidx.media3.session.MediaSessionService()`、`MediaLibraryService()`、多行繼承清單、帶 primary constructor、接 `, Listener`、巢狀 inner class、companion object、Service 內的匿名物件。
  - 該報且報的:`MediaSessionService.Listener`、`Service()`、`Fragment(), Foo by bar`、Activity 內另有 inner Service 時 Activity 自己的收集(C233)。
  - 報了但屬規格邊界、不單獨列問題:Service 的擴充函式 `fun LifecycleService.x()`、typealias、帶註解的父類、`object : LifecycleService()` 匿名物件、舊 `android.arch.lifecycle.`、`com.acme.LifecycleService()`、`BaseLifecycleService()`。
  - 第 1、2 項已涵蓋正規式各片段的測試缺口。
- **(b) C227~C233 預期值**:
  - 預期值都是寫死的字面值,不是從規則算出。
  - 實跑命中數與行號全對:C227~C230 為 0,C231 在 [5],C232 在 [6],C233 在 [6]。
  - 預期值表第六列用 Fragment、C232 用 Application,已併入第 3 項。
- **(c) README**:
  - 兩版數字與計劃一致,也與 `/Users/enzo/harness/lumos-gvc/docs/lumos-toolchain-knowledge/Verification/2026-09-19_受控實驗程式碼為主四組對照.md` 與 `2026-09-21_戊組知識只在Issue的四題八十場.md` 逐項核對:每組 25 場,Haiku 只看程式碼 20、現行 12,Opus 四組 25/25,80 場裡 H06 為 0/5 對 8/15。
  - repo 內沒有別處矛盾。README 沒說明 80 場那批只測 Haiku,屬措辭精度,不列問題。
- **(d) 官方依據**:
  - `LifecycleService` 頁寫明已知直接子類別 `MediaSessionService`、間接子類別 `MediaLibraryService`。`MediaSessionService` 頁寫 `extends LifecycleService`。
  - `ProcessLifecycleOwner` 頁寫「composite of all of your Activities」、`ON_DESTROY` 永不派送、用來回應 App 回前景或進背景。
  - `coroutines-views` 頁那句「only when the UI is visible on the screen」是描述 `repeatOnLifecycle` 的效果,不是適用範圍的聲明;「Service 本來就在背景收」是作者的推論,頁面沒這句。這個推論與 Service 的生命週期一致,規則行為與這兩點相符,只有第 3 項的交界輸入沒交代。
- **docstring 的改壞宣稱**:我逐條重放,除第 2 項那條外全部屬實。拿掉 `has` 的 stopBy 改成往類別本體找,C233 紅;換成不存在的名字、或拿掉外層 stopBy,C227~C230 與 C233 紅;拿掉 media3 前綴,C228 紅;`LifecycleService`、`MediaSessionService`、`MediaLibraryService` 三個名字各拿掉,對應那例紅。
- **效能**:8000 個函式的大檔加 150 層巢狀類別,單條規則改前改後都約 0.54 秒,命中 8001 條,沒有退化。

## 鏡頭 3 固定席節點
- **`Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要有現場成立的前置斷言)**:不影響。C227~C230 這幾個「不報」例子的現場確實走得到規則:換成不存在的名字或拿掉外層 stopBy,這幾例都會翻紅。C231~C233 與它們同形狀,是對照組。
- **`Systems/授權與歸屬` ★INVARIANT★**:不影響。沒動 `_VENDORED_TOOLKIT`、主程式檔頭或授權檔,也沒新增被複製的檔。
- **`Systems/lumos-cli-read` ★INVARIANT★、`Systems/design-loop` ★INVARIANT★**:不影響。本次是代碼審,沒碰 `search` 的篩選;計劃 [S1] 綁了存在的測試,所以處置閘第五步沒被違反。
- **`Systems/arch-alignment-lens`、`Systems/test-quality-handbook`、`Projects/回頭重讀指紋不因主線前進失效_計劃`(★RISK★)、`Projects/審查收斂規則_計劃`(★RISK★)**:已讀,無 finding。diff 只動規則、樣本、逐例表與文字,不碰它們管的程式。
- **只列名的節點**:沒有逐條展開,diff 沒有碰它們宣稱的行為。

severity: major
