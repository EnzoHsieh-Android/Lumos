severity: major

我從資源與效能鏡頭逐節讀完 r2 整份,範圍 3、5、7 和〈實務隱患〉查證最細。實驗用的臨時目錄已用字面絕對路徑刪除。

## 固定席節點判定

- **Systems/規格閘**:不影響。
  - 計劃只在選擇點段加「依列號」小節。
  - 它讀的是 `_render_gov_choice` 收到的去重列,不重讀帳、不改處置鍵。
  - 我實測 22MB、約 12.5 萬行的真帳,`gov --stats` 全程約 3 秒。新小節是 O(選擇點事件數),成本可忽略。
  - 這份帳裡 choice-kill 事件是 0 筆,所以 RETIRE-IF 目前沒有任何真資料可對。
- **Systems/kotlin規則包**:有條件不影響。
  - 計劃走的是「型錄、規則、樣本一次做齊」,所以不破壞「表從安裝版型錄讀」的合約。
  - 前提是 r1 要先修好(`?:` 與運算子正規式 `_CHOICE_OP_RE`),否則第一版行會崩。

## findings

### r1 `_CHOICE_OP_RE` 照字面加 `?:`,會讓 `_choice_top_prec` 對含頂層 `?:` 的第一版行拋 KeyError

severity: major
blocking: 是。照寫會做出壞系統:推送前選擇點那一道對這類行會崩,而不是退成提醒。
引句:「`_CHOICE_OP_RE` 最前面加 `?:`。」

- **段落**:範圍 3「`_CHOICE_OP_RE` 最前面加 `?:`」、用詞「`?:` 的錨點」、S7。
- **問題一**:`re.compile(rb"?:|===|…")` 直接 `re.error: nothing to repeat`,必須寫成 `\?:`。
- **問題二**:跳脫後仍有崩潰。
  - 同一支正規式被 `_choice_top_prec` 共用,它對每個比對結果直接查 `_CHOICE_PREC[...]`。
  - `_CHOICE_PREC` 沒有 `?:`,spec 也沒說要補。
  - 現況 `?:` 不在正規式裡,該函式會回 0(一律加括號)。
  - 加進去後,任何運算元頂層含 `?:` 的第一版命中,在換成不同優先層級的運算子時都會 KeyError。例子是 `a ?: b == c`、`x ?: false && y` 這類,Kotlin 裡 `?:` 比比較、`==`、`&&` 綁得緊。
  - S7 只釘「不含 `?:`」的行,正好漏掉這一類。
- **後果**:`_choice_push_scan` 只接 `_ChoiceUnverifiable`、`_KtSitUnverifiable`、`OSError`、`TimeoutExpired`,KeyError 不會被接住。
- **建議**:改成獨立的 `?:` 專用錨點正規式,或在 `_CHOICE_PREC` 補 `?:` 的層級,並補一條含頂層 `?:` 運算元的 ROR、LCR 案例。
- **重現**:
  ```
  python3.14 -c "…載入 scripts/lumos;patch _CHOICE_OP_RE 為 rb'\?:|===|…';m._choice_top_prec('a ?: b')"
  ```
  輸出:現況 `0`,加 `?:` 後 `KeyError '?:'`。
- 佐證:file: `scripts/lumos:77177`(`_choice_top_prec` 的 docstring 與 `_CHOICE_PREC[m.group(0)…]` 取值)、file: `scripts/lumos:77297`(`_choice_top_prec` 呼叫處)、file: `scripts/lumos:76875`(`_CHOICE_PREC` 無 `?:`)。

### r2 S9 與範圍 7 的門檻量不到真實退步,量法也不可重現

severity: major
blocking: 是。這是整份計劃唯一的上線擋點,而且是 `[manual:]`。判準不明確,實作者會做出錯誤的上線決定。
引句:「哪一列讓有選擇點的行比例多出超過 10 個百分點,或讓最大檔挑壞法超過 10 秒」

- **段落**:範圍 7、S9、實務隱患「推送負擔」「挑壞法時限」。
- **a. 量錯對象,真正的成本沒量**
  - 範圍 7 門檻只看「有選擇點行比例 +10pp」與「最大那支檔挑壞法 ≤10 秒」。
  - 「平均壞法數」只記錄、沒門檻。
  - 真正放大的是 choice-kill 的牆鐘時間,而且沒有任何數字管它。
  - 第一版驗收在 Gradle 熱的情況下是每個壞法約 17.5 秒,冷編譯沒量。
  - 每次 choice-kill 最多 30 個壞法、上限 1800 秒。
  - `no_result` 一律重跑,而且排在新行之後。
  - 這些都會被第二批的編不過壞法(`.let`→`.also`、`!!`)吃掉。
  - 佐證:file: `docs/lumos-toolchain-knowledge/Verification/2026-11-15_改動選擇點真實Android端到端驗收.md:27`(17.5 秒、冷編譯沒量)、file: `scripts/lumos:77981`(`_choice_kill_pick` 的 no_result 一律重跑)。
- **b. 單檔門檻不等於總時限**
  - `_CHOICE_PICK_BUDGET` 15 秒是整次推送所有檔共用,spec 自己也這樣寫。
  - 超時後,後面每支檔的第一行檢查就會 raise,全部記成「驗不了」。
  - 所以「最大檔 ≤10 秒」擋不住「很多中型檔加起來 >15 秒」。
  - 這類超時的結果是閘降成只提醒,等於上線新規則反而削弱守衛。
  - 佐證:file: `scripts/lumos:77431`(`_choice_file_points` 的 deadline 檢查)、file: `scripts/lumos:78321`(`_CHOICE_PICK_BUDGET` 與既有實測表)。
- **c. 條件沒定義,不可重現**
  - 「最大那支檔」的改動行範圍沒寫(全檔都算改動?)。
  - 「隨機抽 10 段」沒有種子,秒數是絕對值而且沒指定機器。
  - CI 與本機速度不同,同一份規則兩邊結論可能相反。
  - 比例的分母沒寫。Verification 用的是全專案程式行(39834 行,13.1%),要明寫沿用。
- **d. 逐列判定與聚合判定矛盾**
  - 範圍 7 寫「哪一列讓比例多出超過 10pp 那一列不加」,是逐列。
  - S9 寫「第二批規則掃過,比例增加不超過 10pp」,是聚合。
  - 六列各自低於 10pp、合計高於 10pp 時,依哪個為準?該拿掉哪一列?規則沒說,邊際貢獻也受列的加入順序影響。
  - `?.`、`?:`、`.let` 是最密的語法,這個情況很可能真的發生。
- **建議**:改成「全套加入後」的聚合門檻,另加「每 20 行平均壞法數」上限與 choice-kill 預估牆鐘上限。量測固定種子、固定「全檔視為改動」、同一台機器。

### r3 ast-grep 輸出量與「實測持平」宣稱沒查證(與 r2 版的規則數不符)

severity: major
blocking: 是。r2 新增的宣稱與實作內容矛盾,而且批次輸出的 64MB 上限會讓大推送退回逐檔。
引句:「掃描時限 `_KT_SIT_BUDGET` 照第一版(ast-grep 多兩支規則實測持平)」

- **段落**:實務隱患「挑壞法時限」:「掃描時限 `_KT_SIT_BUDGET` 照第一版(ast-grep 多兩支規則實測持平)」。
- **問題**:
  - r2 實際新增 `nul.yml` 兩條加 `api.yml` 四條,共六條規則、一個新檔。「兩支」是 r1(`nul.yml`、`compose.yml`)的殘留數字。
  - 「實測持平」沒有出處,只是 r1 沿用的宣稱。
- **我的實測**:
  - 我把 `?:`、`?.`、`.let`、`combine`(四條,沒做 spec 說的排除)加進複製的規則包。
  - 對 1.8MB、4.8 萬行的合成 Kotlin 檔跑 `ast-grep scan --json=stream`。
  - 時間:2.06 秒變 2.25 秒,約 +9%。這方面沒問題。
  - 輸出:30.7MB(3.6 萬筆命中)變 75.1MB(9.6 萬筆命中)。
  - Python 剖析 JSON:0.35 秒變 0.74 秒。
- **重點**:
  - 輸出已超過 `_LINT_SARIF_MAX_BYTES`(64MB)。
  - 批次超過上限,會退回逐檔,每檔一個程序。
  - 逐檔也超過就整檔記「算不出來」,只提醒。
  - 單批可承載的程式碼量因此縮到約 0.4 倍,這是密度極端的人造檔,真實比例要實測。
- **建議**:
  - 把實測改成可重現的量測:輸出位元組、命中筆數、是否觸發批次退回。
  - 放進範圍 7 的量測項,並把「兩支」改成實際條數。
- 佐證:file: `scripts/lumos:43084`(`_LINT_SARIF_MAX_BYTES = 64MB`)、file: `scripts/lumos:77041`(`_choice_scan_batch` 超過上限回 None)、file: `scripts/lumos:77075`(`_choice_scan_one` 超過上限 raise)。

### r4 範圍 5 的統計欄位沒說清楚:`new_sha` 不在統計列、「時間最新」的排序鍵未定義

severity: minor
blocking: 否。真實帳的整合測試會立刻紅,不會靜默出錯;但 spec 缺描述,實作者會多繞一圈。
引句:「吃已去重的統計列(`_render_gov_choice` 收到的那份,不重讀帳)」

- **段落**:範圍 5 第一、二條。
- **問題一**:「吃已去重的統計列(`_render_gov_choice` 收到的那份,不重讀帳)」,又要「以 (檔, 行指紋, 壞法雜湊 new_sha) 為一個」。
  - `_gov_row` 只把 `file, fp, killing_test, changed, mutant_lines, secs, reasons` 放進 `ck`,沒有 `new_sha`。
  - `new_sha` 只在讀入時通過型別檢查。
  - 要先改 `_gov_row`,spec 沒寫。
- **問題二**:「取時間最新那筆」的排序鍵沒定義。
  - 統計列的 `ts` 是 HEAD 的提交時間,同一提交內的多筆事件靠穩定排序的帳檔順序。
  - 選擇點事件的 `written_at` 沒有被放進統計列。
  - 跨兩本帳(版控帳加本機帳)讀入時,同 `ts` 的先後順序也沒保證。
  - 「放行之前最近一筆存活」同樣有這個問題。
  - 現有測試用的是同一個 `ts`,S8 預期值表也沒涵蓋跨提交順序。
- **問題三**:原因字串對不上。
  - spec 寫「基準沒綠所以沒跑」。
  - 程式實際的字串是「基準不綠沒跑」,而且 `reason` 是 `why:節錄` 的自由文字。
  - 要定義比對鍵(原因冒號前那段),否則 RETIRE-IF 的「跑不出結果超過一半」會把環境原因算進去。
- 佐證:file: `scripts/lumos:18422`(`_gov_row` 的 `ck` 欄位清單)、file: `scripts/lumos:77862`(「基準不綠沒跑」字串)、file: `scripts/lumos:18486`(`ded` 依 `ts` 穩定排序)。

### r5 `?:` 的 ast-grep 規則寫法在 YAML 會直接解析失敗

severity: minor
blocking: 否。實作時第一次跑就會看到錯誤,不會做出壞系統,但 spec 的範例寫法會誤導。
引句:「`?:` 用 pattern `$A ?: $B`」

- **段落**:範圍 2「`?:` 用 pattern `$A ?: $B`」。
- **重現**:
  ```
  rule:
    pattern: $A ?: $B
  ```
  `ast-grep scan` 回 `mapping values are not allowed in this context`。
- **處理**:必須寫成 `pattern: '$A ?: $B'`。加引號後我實測可用。
- **建議**:在範圍 2 加一句「pattern 要加引號」,並讓 S6 樣本核對涵蓋規則檔能被解析。
- 佐證:實測 `ast-grep 0.51.2`,使用複製的 `kotlin-choice` 規則包。

### r6 冪等與記帳:`no_result` 一律重跑,新編不過壞法會被反覆重編,放行也可能重複計數

severity: minor
blocking: 否。方向已被 spec 部分承認(「編不過落成跑不出結果」),缺的是成本量化與放行計數口徑。
引句:「編不過的落成跑不出結果、人可判不適用,範圍 5 依列號累計」

- **段落**:實務隱患「編不過」「推送負擔」、範圍 5 放行口徑。
- **問題一**:`.let`→`.also` 與 `$A!!` 預期會產生大量編不過。
  - `_choice_kill_pick` 對 `no_result` 每次呼叫都重跑,每次都再編一次已知壞的壞法。
  - 每輪 choice-kill 的 30 個名額也會被它們佔用。
  - 每次重跑還各追加一筆帳。
  - spec 只說「人可判不適用、超過一半拿掉那一列」,沒說上線前要不要量「每個壞法重跑的成本」。
  - 這項最好併入 r2 的量測。
- **問題二**:放行的計數口徑。
  - 範圍 5 寫「每筆選擇點放行」都歸到最近存活事件的列。
  - 放行事件的去重鍵包含提交。
  - 同一行在兩個不同提交各放行一次會算兩筆,「等價/不是需求」比例被灌水。
  - 建議改成每個 (檔, 行指紋) 只取最後一筆放行,與壞法的「終態」口徑一致。
- 佐證:file: `scripts/lumos:77981`(no_result 一律重跑)、file: `scripts/lumos:18414`(放行事件的去重鍵)。

## 已讀、無 finding

- **範圍 4(check.py)**:`CHOICE_CATEGORIES` 在尾端加 `NUL` 後,沒有 `NUL` 節點的行,洗牌用的類別清單內容不變,S7 的前提成立。
  - 佐證:file: `scripts/lumos:77368`(`cats` 先依本行出現的類別過濾,再用 `fp` 當種子洗牌)。
- **回退、天花板、依據來源**:兩條路徑宣稱我在檢查時都對得上,`--catalog-only` 與 `--sg` 旗標確實存在。
  - 佐證:file: `configs/ast-grep/kotlin-android/check.py:1946`。
- **暫存檔與子程序清理**:沒有新增。選擇點掃描用 `tempfile.TemporaryDirectory`,子程序走 `_lint_spawn` 並登記收掉,第二批不改這條路徑。
- **Compose 兩列**:規則(`LaunchedEffect`、`remember`)我沒完整實測排除條件,規則裡的 `not:` 與常數判斷在實作時還要實驗。

## 實務隱患鏡頭(資源與效能)

- **掃描量**:每次整檔跑所有規則,多六條規則約 +10% 時間,輸出量約 2.4 倍(見 r3)。
- **gov --stats**:無新風險(見上)。
- **突變測試跑不完**:風險存在,而且是此計劃最大的缺口(見 r2、r6)。
- **暫存與子程序**:無新增,「無+為什麼」見上。
- **冪等**:壞法計數用 (檔, 行指紋, `new_sha`) 去重,重跑不會重複計壞法;放行計數有重複風險(r6)。
- **併發**:單人單機,不問。

最嚴重 severity:major,blocking 共 3 條(r1、r2、r3)。
