severity: minor

審查的是 `r1-snapshot.patch` 裡 `scripts/lumos` 的改動(A 到 G)。我沒找到 major 或 blocker,下面三條都是邊界情況,都是 minor。BOM 與反引號兩例,以及 OverflowError 一例,是我拿同一條正規式與 `json`、`float` 在 `/tmp/lumos-seat-work/code-選擇點存活回指第一段補修/r1-邊界-sonnet/` 重現過的。

先說審過沒問題的邊界:
- **(D) 空殼結果檔**:`tests="0.0"` 不當空殼、照舊拒收;`tests` 屬性缺當 0;根是 testsuites 底下混真結果時,空殼略過、其餘照讀。
- **(D) 目標測試對帳**:空殼加真結果混在一起時,目標測試仍由 `_choice_merge_classify` 要求恰好對到一筆,所以沒有誤放行的路徑。
- **(C) `.base.json` 驗證**:空檔、陣列、`rc` 是 bool True、`el` 是字串、`to` 不是 bool 都回 None;`el` 為 0 通過。
- **(C) 續跑快取**:舊快取沒有 `.base.json` 時會刪掉重量,不會漏洞。
- **(E) 全部測試記到 0 個專案類別時斷路**:`any_proj` 是跨測試累計,第一支沒碰專案類別不會誤斷。
- **(F) 掛覆蓋逾時改在重跑之後判**:不掛也逾時就不斷路,符合規格。

severity: minor
blocking: 否
`scripts/lumos:79793` `_choice_cov_src_pkgs` 讀套件宣告的正規式漏掉三種檔頭。
引句:「_CHOICE_COV_PKG_RE = re.compile(r"^[ \t]*package[ \t]+([\w.]+)", re.M)」
- 第一行 `package` 前有 UTF-8 BOM 的檔:BOM 解碼後留成 `\ufeff`,`^[ \t]*package` 比對不到。
- `package` 寫在 8KB 之後的檔(例如很長的授權檔頭)。
- `package` 帶反引號的檔。
- 失敗場景:這三種檔的套件被記成預設套件 `""`,真正的套件沒進 `pkgs`。只碰這些套件類別的 Robolectric 測試專案類別數會算成 0,`robo_zero` 為真,這支被判「覆蓋接不起來」。這正是 (A) 要修的那種誤判,只是範圍縮小了。
- 不影響其他支測試;整批斷路也不受影響,因為 (E) 是跨測試累計。
- 重現:`package com.a.b` 前加 BOM,以及 ``package `com.a.b` ``,正規式都回 None。

severity: minor
blocking: 否
`scripts/lumos:79789` 掃描目錄的跳過名單與 20000 支上限會讓套件集合漏收。
引句:「_CHOICE_COV_SRC_SKIP = frozenset(("build", ".gradle", ".git", ".idea", "node_modules", "test", "androidTest", "testFixtures"))」
- 名單用資料夾名在任何深度比對。主程式裡名叫 `test` 或 `build` 的套件資料夾(例如 `com/foo/test/`)整個被跳過。Gradle 模組資料夾恰好叫 `test` 或 `build` 時也一樣。
- 20000 支上限用 `os.walk` 的自然順序截斷,是靜默的。主程式加上沒被跳過的 `sharedTest`、`jvmTest`、`.cxx` 這類資料夾合計超過時,後面的套件漏收。
- 失敗場景與上一條相同:只碰漏收套件的 Robolectric 測試被判「覆蓋接不起來」,而且沒有任何提示。

severity: minor
blocking: 否
`scripts/lumos:79832` 基準檔讀出與寫入各有一個沒處理的邊界。
引句:「or type(doc.get("el")) not in (int, float) or type(doc.get("to")) is not bool or doc["rc"] != 0 or doc["to"]):」
- 讀:`el` 是超大整數(例如 400 位數)時,後面的 `float(doc["el"])` 丟 `OverflowError`,不在 `except (OSError, ValueError)` 範圍內,會讓整個流程崩潰。`NaN` 與 `Infinity` 也會通過型別檢查,進到 `c.baselines` 後污染耗時估算。這需要快取檔被人改過,單人自用的威脅模型下機率低。
- 寫:`store()` 裡 `.base.json` 寫失敗(磁碟滿)會讓整個 `try` 回傳 None,`take()` 記成「覆蓋資料沒產出」。可是 `.exec` 其實已經寫好了,這支覆蓋被白白判成不明。
- 讀的重現:`float(json.loads('{"el":' + '9'*400 + '}')["el"])` 丟 `OverflowError`。
- 修法:讀端用 `math.isfinite` 並接 `OverflowError`;寫基準檔的失敗另包 `try`,不要讓它影響 `.exec` 的結果。

總結:最高等級是 minor
