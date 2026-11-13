severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/3e6c2aa7…ffdba22.json.warming` 不存在,沒有鎖要處理。

我逐 hunk 讀完 diff,在 `/tmp/lumos-seat-work/` 底下載入 `scripts/lumos` 的函式實跑邊界輸入。測試差異只看了函式名清單,沒有跑 `test_lumos.py`。實驗的臨時目錄已用字面絕對路徑刪除,repo 沒有被改。

沒有找到 blocker 或 major。`--import` 的形狀驗證、`also` 的檢查與套用、`--diff` 入口驗證都擋得住我送的壞輸入:
- `--import` 擋住空字串、`*`、`as`、反引號、尾隨換行或空白、分號和重複給兩次。
- `also` 擋住 `None`、字典、兩筆、非 import 行和缺結尾換行。
- `--diff` 擋住 `-x..HEAD`、`A..`、`..HEAD`、三點、空白、換行和不存在的提交。右端寫成 `@`、分支別名、完整或縮寫 sha 都等於 HEAD,收下是對的。
- 從 `_kt_sit_read_many` 到 `open(encoding="utf-8")` 全程換行統一成 `\n`,所以 CRLF 檔不會讓 `also` 對不上。

## b1 檔頭區內的區塊註解裡的 import 被當成真 import
severity: minor
blocking: 否
引句:「at = next((i for i in reversed(rows) if lines[i].startswith("import ")), None)」
file: `scripts/lumos:76100` 附近(`_situation_rule_imports_problem`、`_situation_rule_has_import` 都只看「行首是 `import `」)
1. 輸入:檔頭是 `package a`、`import x.Y`,接著 `/*`、`import old.Z`、`*/`,再接 `class C {}`,加上 `--new` 含 `Q`、`--import "import q.Q"`。
2. 走到:`_situation_rule_header_rows` 把區塊註解內的行算進檔頭區,`at` 選到註解裡的 `import old.Z`。
3. 壞在:補的 `import q.Q` 插進註解裡,等於沒補。基準跑完後壞法編譯失敗,判 killed_unattributed 被拒,白跑一次 Gradle。
4. 同一個原因的另一面:註解裡有 `import old.Q`,而 `--import "import q.Q"` 被誤判成「檔頭已經 import 了 Q」,一律拒絕。
5. 重現:`_situation_rule_imports_problem("package a\nimport x.Y\n/*\nimport old.Z\n*/\nclass C {}\n","Q.foo",["import q.Q"])` 回 `old: 'import old.Z\n'`。第二個例子回「檔頭已經 import 了 Q」。
6. 規格〈用詞〉檔頭區把註解算進檔頭區,但沒說註解內的 `import ` 行算不算,實作等於照字面做。Kotlin 的區塊註解可以巢狀,`_situation_rule_header_rows` 遇到第一個 `*/` 就結束,同樣會誤判。

## b2 檔案開頭有 BOM 時整個被當成沒有檔頭
severity: minor
blocking: 否
引句:「elif t and not t.startswith(("//", "@file:", "package ", "import ")) and t != "package":」
file: `scripts/lumos:76033`(`_situation_rule_header_rows`)
1. 輸入:以 UTF-8 BOM 開頭的 Kotlin 檔(`\ufeffpackage a.b`),帶任何合法的 `--import`。
2. 走到:`str.strip()` 不會去掉 U+FEFF,第一行不是 `package ` 開頭,檔頭區是空的。
3. 壞在:rc 2,訊息是「檔頭區既沒有 import 也沒有 package 那一行」,但檔案明明有。人會被誤導去改檔,而這支檔其實用得了 `--import`。
4. 重現:`_situation_rule_imports_problem("\ufeffpackage a.b\n\nimport x.Y\n\nfun f(){}\n","Z.foo",["import q.Z"])` 回「檔頭區既沒有 import 也沒有 package…」。
5. 另一個類似的小處:`package<Tab>a.b`(關鍵字後面是 Tab)也會讓檔頭區提前結束,結果相同。

## b3 兩個 --import 名稱相同、套件不同時照收,到編譯才失敗
severity: minor
blocking: 否
引句:「if imp in imports[:k]:」
file: `scripts/lumos:76075`(`_situation_rule_imports_problem`)
1. 輸入:`--import "import a.Q" --import "import b.Q"`,`--new` 含 `Q`,檔頭沒有 Q。
2. 走到:重複檢查只比整行。同名檢查只比 HEAD 檔頭,不比 `--import` 彼此。兩行都過,產出同一筆 `also`,一次補兩行同名 import。
3. 壞在:Kotlin 會報 import 名稱衝突。這要等基準跑完(Android 可能十幾分鐘)、壞法編譯失敗後才被拒,而這個錯誤在入口就看得出來。
4. 重現:`_situation_rule_imports_problem("package a\nimport x.Y\nfun f()=Q\n","Q",["import a.Q","import b.Q"])` 回 `new: 'import x.Y\nimport a.Q\nimport b.Q\n'`,沒有錯誤。

## b4 run_cmd 寫成 `app:test`(沒有前導冒號)沒被擋
severity: minor
blocking: 否
引句:「parts = t[1:].split(":")[:-1] if t.startswith(":") and t.endswith(":test") else []」
file: `scripts/lumos:76345`(`_gradle_blocked_tasks`)
1. 輸入:`./gradlew app:test --tests '*{method}'`,`app/build.gradle.kts` 是 Android。Gradle 把 `app:test` 當成 `:app:test`。
2. 走到:只認 `:` 開頭的路徑,這個任務不進 (b) 條件,人裁的前置檢查回 None。
3. 壞在:殺傷力照跑,基準因 Android 的 test 任務不收 `--tests` 而 abort,白等一次冷建構。
4. 重現:`_situation_rule_android_cmd_problem` 用這個 run_cmd 回 None,`./gradlew :app:test` 則會擋。
5. 實作跟規格〈用詞〉的 `:<模組>:test` 字面一致,是規格定義比 Gradle 實際語意窄,所以只標 minor。

## b5 規格自己前後不一致:S2 條款對照範圍 1 與預期值表
severity: minor
blocking: 否
引句:「當 --import 的名稱不是這次新寫法才有的觸發字、或形狀不合、或檔裡已有同一行,人裁指令 應 在跑殺傷力之前拒絕」
file: `docs/lumos-toolchain-knowledge/Projects/人裁殺傷力在真實Android專案跑得起來_計劃.md:99`
1. S2 說名稱不是觸發字就拒絕。但〈範圍〉1 寫「名稱不必是觸發字(D-5 換成 `SharingStarted.Lazily` 要補 `SharingStarted`)」,預期值表 S1 的 D-5 列也寫「收下、產生 also」。
2. 實作照範圍 1 做:名稱只要在 `--new` 出現且檔頭沒有就收。
3. 照 S2 字面寫測試或驗收的人會得到跟實作相反的結論。S1 條款也寫成「新寫法觸發字的 import」,同樣偏窄。S2 條款要改成跟範圍 1 同一句。

## b6 家目錄遮蔽用前綴字串取代,會改壞名稱相近的其他路徑
severity: minor
blocking: 否
引句:「text = text.replace(q, tag)」
file: `scripts/lumos:26750` 附近(`_kill_mask_paths`)
1. 輸入:家目錄 `/Users/enzo`,輸出裡有 `/Users/enzo2/x`、`/Users/enzoABC/z`。
2. 結果:變成 `~2/x`、`~ABC/z`,不是整段遮掉,也不是原樣保留,誤導人以為是家目錄下的路徑。
3. 重現:`_kill_mask_paths("/Users/enzo2/x /Users/enzo/y /Users/enzoABC/z", "/var/folders/xx/T/lumos-kill-abc/wt", "/Users/enzo")` 回 `~2/x ~/y ~ABC/z`。
4. 工作樹路徑同樣是純字串取代,但臨時目錄的命名不太會出現相近前綴,影響更小。

## 附:圖譜鏡頭
這次沒有附固定席節點(`LUMOS-LENS` 寫明沒有),不逐條回答。我對照了規格 `lands_in` 的 `Systems/guard-kill`,它的合約行「rc 優先序」和「`--json` 成功時 stdout 恰一行 JSON」都不受影響:
- `abort`、`killed_unattributed` 的 rc 判定沒改。
- 新增的 `fail_excerpt` 只是結果列多一個欄位,`--json` 的輸出形狀沒變。
- `--diff` 沒採用的提示是 `situation-rule` 指令自己印到 stdout,不經過 `guard kill`。

最嚴重的是 minor,共 6 條,blocking 共 0 條。
