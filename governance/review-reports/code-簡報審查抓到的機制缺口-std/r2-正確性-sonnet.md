severity: minor

整體判斷:r1 到 r2 之間 `state.yml` 一個位元組都沒動,修補只加測試、樣本註解和文件。C227~C239 的預期命中數與行號我逐例手算過,全部對得上,四處文件對同一行為的說法也一致。找到三條 minor,沒有 blocker 或 major。

驗證環境與日期:ast-grep 0.51.1、python3.14,2026-11-10。我把修前 `3beebb94` 與修後 `0f2989d0` 各 clone 到 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/正確性-sonnet/{before,after}`,原 repo 沒動。

## Findings

### 1. 例外規則的兩處正規式放寬,逐例表與樣本檢查照綠
severity: minor
blocking: 否
引句:「regex: '^(androidx\.lifecycle\.|androidx\.media3\.session\.)?(LifecycleService|MediaSessionService|MediaLibraryService)\s*\('」
file: `configs/ast-grep/kotlin-android/rules/state.yml:176`(after clone,規則本體)

兩個具體改壞,`t_kotlin_rulepack_security_rules` 都是 `445 passed, 0 failed`:

- **改壞 A,前綴放寬成任意套件。**
  - 做法:把 `(androidx\.lifecycle\.|androidx\.media3\.session\.)?` 換成 `(\w+\.)*`,也就是同包 Application 排除用的寫法。
  - 輸入:`class S : com.acme.LifecycleService() { ... lifecycleScope.launch { repo.changes.collect { upload(it) } } }`。
  - 原規則在第 6 行報,改壞後不報。
  - 沒有任何一例放「同名但非 androidx 的 Service」,而這是本案點名的高風險形態。
- **改壞 B,`\s*\(` 換成 `.*\(`。**
  - 輸入:`class F : Fragment(), MediaSessionService.Listener by impl() { ... lifecycleScope.launch { vm.player.collect {...} } }`。
  - 原規則在第 5 行報,改壞後不報。
  - S1 明列「實作 MediaSessionService.Listener 的 Fragment 應照報」,但 C231 的 Listener 後面沒有括號,碰不到這個變體。
  - 這個輸入罕見,所以只算輔助。

降成 minor 的理由:S1 條款沒有寫「非 androidx 同名要照報」,改壞 B 的輸入也不常見。被保護的行為在條款裡沒有明文。

歸因:有證據的原有漏查。
- 規則沒變:`git diff 3beebb94 0f2989d0 -- configs/ast-grep/kotlin-android/rules` 輸出為空。
- 修前(DIR=before)與修後(DIR=after)套用同一改壞,都是綠。
- 改壞 A 的 E07 掃描結果:修前、修後都是原規則 `[6]`、改壞後「不報」。

### 2. README 第二批 80 場那句,比原始紀錄寬鬆
severity: minor
blocking: 否
引句:「the other three questions were near full marks in every group」
file: `/Users/enzo/harness/lumos-gvc/docs/lumos-toolchain-knowledge/Verification/2026-09-21_戊組知識只在Issue的四題八十場.md:26`(H04 在「現行」組是 3/5,另一組 4/5)
file: `/Users/enzo/harness/lumos-gvc/docs/lumos-toolchain-knowledge/Verification/2026-09-21_戊組知識只在Issue的四題八十場.md:51`(只有 Haiku、只有四題、每格 5 場,整批結論靠 H06 一題)

- 原始表格 H04 一欄是 5/5、3/5、4/5、5/5,README 的「四組都接近滿分」把 60% 也算進去。
- 這句也沒寫明這批 80 場只有 Haiku 跑過。上一句剛講完 Opus 在天花板,讀者容易以為這批也含 Opus。
- 原始紀錄第 32 行自己的措辭就是「四組都接近滿分」,所以 README 是照抄原句,與 S4 的四個必寫事實都不衝突。
- 數字本身全部對得上:20/25、12/25、Opus 四組 25/25、0/5 對 8/15、每組 20 場共 80 場。中英兩版數字相同。

歸因:有證據的原有漏查。`git diff 3beebb94 0f2989d0 -- README.md README.en.md` 為空,修前修後文字相同。

### 3. 壞例樣本註解「ProcessLifecycleOwner 不豁免」沒限定在非 Service 類別
severity: minor
blocking: 否
引句:「// ProcessLifecycleOwner 不豁免:官方說它是所有 Activity 的合成生命週期,STARTED 就是 App 有畫面在前景」
file: `configs/ast-grep/kotlin-android/samples/bad/kt-lifecycle-collect-without-repeat/src/main/kotlin/kt-lifecycle-collect-without-repeat.kt:23`(after clone)

這句沒加「非 Service 類別裡」。C236 的 `class S : LifecycleService()` 裡用 `ProcessLifecycleOwner.get().lifecycleScope.launch { collect }`,規則一律不報,兩個版本都是如此。

其他三處(S1 條款、規則包 WHY、測試 docstring)都已寫成「外圍是 Service 時不報」,只剩這句沒限定。

歸因:未判定。
- 這行在修補差異裡是未改動的上下文,修前修後都存在。
- 修前的 WHY 與計劃寫「ProcessLifecycleOwner 照報」,與規則實際行為不符;修補把文件改齊了,這句樣本註解沒跟著改。
- 嚴格說,這個不一致是 r1 狀態就有、修補沒收乾淨的漏查,所以我歸為原有。

## 三問

### ① 原問題的修復效果有何行為證據?

修補只加測試與文件,規則本身沒變,所以對 C234、C235、C239 來說,補的是「守衛」不是「行為」。

| 主張 | 輸入 / 預期 | case_source | 修前 | 修後 | 比較 |
|---|---|---|---|---|---|
| C234 守住 androidx.lifecycle 前綴 | `class S : androidx.lifecycle.LifecycleService()` / 不報 | `_KTSEC_CASES` C234 | 拿掉該前綴的改壞:`433 passed, 0 failed`(守不住) | 同改壞:`443 passed, 2 failed`(C234 紅) | 規則沒變,只有守衛差異 |
| C235 守住 `^` 錨點 | `class S : BaseLifecycleService()` / 報第 6 行 | C235 | 拿掉 `^`:433 綠 | 拿掉 `^`:C235 紅 | 同上 |
| C239 守住括號前空白 | `class S : LifecycleService ()` / 不報 | C239 | 拿掉空白那段:433 綠 | C239 紅 | 同上 |
| C236 定 Service 裡的 PLO 不報 | `class S : LifecycleService()` 裡用 PLO 收 / 不報 | C236 | 直接掃描:不報 | 不報 | 行為本來就是不報,是文件改齊,不是行為修復 |
| C237、C238 對應預期值表 | C237 報 `[5]`;C238 報 `[12]`,Service 那處不報 | C237、C238 | 規則直接掃描:`[5]`、`[12]` | 同 | 兩版一致 |

另外,docstring 列的各項改壞我都重放過,紅的案例與寫的一致:
- 拿掉 `inside` 的 `stopBy: end`:紅在 C227~C230、C233、C234、C236、C238、C239。
- 排除名字換成不存在的名字:同一組紅。
- `has` 加 `stopBy: end`:只有 C233 紅。
- 拿掉 media3 前綴:C228 紅。
- 拿掉建構子括號:C231 紅。
- 拿掉 `MediaLibraryService`:C229 紅。
- 名字換成 `\w*Service`:C235 紅。

### ② 修補處的正常、錯誤、相鄰路徑是否仍成立?

修後 clone 實跑結果:

| 測試 | 結果 |
|---|---|
| `t_kotlin_rulepack_security_rules` | 445 passed(修前 433 passed) |
| `t_kotlin_rulepack_samples` | 27 passed |
| `t_kotlin_rulepack_good_cross_rule` | 7 passed |
| `t_kotlin_catalog` | 60 passed |
| `check.py` 自檢 | 規則 228 條,問題 0 |
| `lumos spec-gate` 計劃 | S1 綠 |
| 6 篇改到的筆記 `lumos lint` | 皆 0 問題 |

- **修前的 samples 測試未跑**,是否通過未判定。
- **邊界實跑**,用真規則掃 24 種寫法:
  - 多行繼承清單、`LifecycleService(\n)`、括號前 tab、`Foo, MediaLibraryService()`、companion、Service 裡的巢狀類別:都不報。
  - `com.acme.` 前綴、`Foo by LifecycleService()`、泛型父類 `Base<LifecycleService>()`、Fragment 裡的巢狀 Service 旁的 Fragment 收集、頂層函式:都照報。
  - Service 裡的內部 Fragment 不報,計劃〈實務隱患〉已明寫。
- **未列為 finding 的邊界**:
  - 次建構子寫法 `class S : LifecycleService { constructor() : super() }` 會報,但計劃明定只認建構子呼叫形式。
  - 繼承清單裡帶註解的 `LifecycleService/* c */()` 與 `object : LifecycleService()` 會報,Android 不會實例化這兩種寫法,我沒有找到實際失敗場景。
- **效能與記憶體**:60 層巢狀加 3000 個候選,再加 3000 個同層類別。
  - 新規則 0.67 秒、73MB,舊規則 0.44 秒、73MB。
  - 命中數 7500 與預期一致:6000 加 1500 個 Fragment。

### ③ 新發現的同一案例,修前、修後各是什麼結果?

三條 finding 的修前、修後結果相同,見各條歸因。三條都不是修補造成,因為 `state.yml` 與 README 在兩版之間完全沒動。

## 圖譜鏡頭

- **`Systems/測試假綠形態` 的 INVARIANT**(還原翻紅釘要有前置斷言證明現場成立):不破壞。
  - 測試裡有 `★前置★ 掃得起來`。
  - 每個預期 0 的例子都有對照正例。
  - 我把例外整個拿掉(M11、M13)後,各 0 例都轉紅,現場走得到被測分支。
- **`授權與歸屬`、`arch-alignment-lens`、`lumos-cli-read`、`design-loop`、`test-quality-handbook`**:不影響。diff 只動規則包設定、樣本、逐例表與文件,沒碰 SPDX 清單、搜尋排除、處置閘或 `scripts/lumos`。
- **兩篇 Issue 的主張**:屬實,但不在本席主鏡頭,只核到「與程式吻合」這一層。
  - `_lint_new_diff_claims` 算出現次數,`_lint_new_tools` 用 `key not in waivers` 過濾。
  - `_codeloop_pass_shape` 與 `code-loop check` 留痕那一道都不讀迴圈定錨分級。
- **實測紀錄**:計劃引用的 LifecycleService 官方頁,已知直接子類別含 `MediaSessionService`,間接含 `MediaLibraryService`;media3 頁宣告 `MediaSessionService extends LifecycleService`。兩頁都確認。

## 未驗範圍

- 修前的 `t_kotlin_rulepack_samples` 沒跑。
- 計劃說 fix-check 全部通過,結果只存在終端與 `r2-intake.md`,我沒重跑。
- 中文以外的 README 其他段落沒看。

我的臨時目錄 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/正確性-sonnet/` 還在,待編排者刪除。

總結:本報告最高嚴重度為 minor
