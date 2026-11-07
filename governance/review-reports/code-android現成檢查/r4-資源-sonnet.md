severity: minor

F1. 50 MB 的 CI 檔要 8.8 秒,記憶體約 660 MB。這比正常的 lint-check 慢很多,但不到卡死,也沒有指數或平方級的爆炸。
severity: minor
blocking: 否
引句:「for ln in text.replace("\\\n", " ").split("\n"):   # CRLF 已由 read_text 的通用換行轉成 \n」
- 重現:50 MB 的 `.github/workflows/ci.yml`,每行是 `      - run: ./gradlew assembleDebug`。用 `python3.14 scripts/lumos lint-check --repo <臨時目錄> --json` 量。
- 空 repo 基準:0.81 秒,常駐記憶體約 350 MB。
- 50 MB 檔:總共 8.83 秒,最大常駐記憶體 660 MB。
- 逐函式拆開量:讀檔加去註解 `_ci_workflow_texts` 約 2.7 秒,`_android_ci_lint_evidence` 約 4.0 秒。
- 讀檔那段(`_ci_workflow_texts` 的 `read_text`)本來就沒有位元組上限。這是既有行為,不是 r4 引入的。
- 建置檔掃描有 `max_bytes`,CI 檔沒有。CI 檔通常很小,所以只算順手可以補的一件事。

沒有問題的項目(都是 `lint-check --repo <臨時目錄> --json`,空 repo 基準 0.81 秒):

| 輸入 | 耗時 | 最大常駐記憶體 |
|---|---|---|
| 10 萬行全是反斜線續行 | 1.13 秒 | 349 MB |
| 單行 100 萬字元(含空白) | 1.12 秒 | 351 MB |
| 單行 100 萬字元(無空白) | 0.93 秒 | 351 MB |
| 單行 200 萬個 `check` 詞(無 gradle 詞) | 2.89 秒 | 463 MB |
| 單一 300 萬字元的 `/` 詞 | 1.18 秒 | 352 MB |
| 50 萬個 `a:` 接 `lint!` | 0.96 秒 | 441 MB |
| 1000 段各 1000 字元的 `a…a:` 接 `Lint` | 0.89 秒 | 348 MB |

`_ANDROID_LINT_WORD` 的巢狀量詞在這些輸入上沒有災難性回溯。

**Jenkinsfile 與 `_strip_c_comments`:**
- 10 MB 不閉合的 `/*`:1.37 秒。
- 100 萬個單引號:0.89 秒。
- 100 萬個雙引號:0.91 秒。
- 100 萬個 `/`:0.88 秒。
- 50 萬行 `sh 'a' // c`(5.8 MB):2.07 秒。
- 10 萬行續行:1.01 秒。
- 最大常駐記憶體都在 348 到 418 MB,沒有成長失控。

**`_is_gradle_head` 與共用詞表在 detekt 路徑:**
- 把它換掉原本的 `posixpath.basename` 是常數成本,每段一次 `re.split`。
- `_detekt_plugin_values` 掃 1000 段是 0.007 秒,掃 10 萬段是 0.49 秒,線性。
- 單一 200 萬字元、含 100 萬個 `/` 的詞呼叫 `_is_gradle_head` 只要 0.05 秒。

F2. `t_lint_android_ci_advice` 整支在這台機器上跑了 83.4 秒(使用者時間 58.9 秒),112 條檢查全過。
severity: minor
blocking: 否
引句:「check("r3 折入 CI 設定檔是符號連結 → 略過(照印 A1)", "A1" in quick(root), str(quick(root)))」
- 超時上限是 180 秒。測試工具自己印「餘裕 2x ⚠ 餘裕不足 3 倍」,所以機器忙的時候有逾時風險。
- 這次跑的時候,別的 session 的全套分片(4 個程序)在同機並行,數字有被拉長的成分。
- 新加的案例用 `quick()` 直接呼叫函式,沒有各自起子程序,這一點是對的。耗時主要是這支原本就有的案例量。
- 暫存:跑完後 `$TMPDIR` 底下沒有留下 `gctl-andci-*`。我沒有看到卡住的子程序。
- 殘留的 `gctl-run-*` 是別的 session 的全套分片在跑,不是這支測試留下的。

總結:最嚴重是 minor(50 MB 的 CI 檔 8.8 秒、660 MB,以及測試耗時餘裕只有 2 倍),會擋 0 條。

我的臨時目錄 `/tmp/lumos-seat-work/code-android現成檢查/資源-sonnet` 已刪除。
