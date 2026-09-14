severity: minor

## F1 混雜輸出的復原機制,只要前導雜訊裡有一個 `{` 就抓錯起點

severity: minor
blocking: 否
引句:「raw[raw.find("{"):] if "{" in raw else ""」
file: `scripts/lumos:20991`

`cmd_dart_sarif` 為了應付「stdout 前面混了別的字」,做法是找第一個 `{` 的位置往後切一段再試 `json.loads`。但如果前導雜訊本身就含一個花括號(現實裡很常見,例如版本管理工具的橫幅訊息提到 `{deprecated}`、`{debug}` 這類字眼),`find("{")` 會抓到雜訊裡那個花括號,切出來的字串不是合法 JSON,整段判定失敗。

最小重現:
```
printf 'Warning: {deprecated} flag used\n{"version":1,"diagnostics":[]}\n' | python3 scripts/lumos dart-sarif
# 輸出:擋下:讀到的不是 dart analyze --format=json 的輸出——不產出結果檔……
# rc=2
```
對照組(雜訊裡沒有花括號時能正常救回):
```
printf 'Some tool banner line\n{"version":1,"diagnostics":[]}\n' | python3 scripts/lumos dart-sarif
# 正常吐出 SARIF,rc=0
```
降權理由:真的 `dart analyze --format=json` 實測(Dart 3.13.3,含 INFO/ERROR 混合、中文與空白檔名、無 pubspec、語法錯誤等情境)輸出都是乾淨的單一 JSON,沒有夾雜文字;这條路徑在目前唯一已知的呼叫方(`_lint_new_verdict`)裡失敗時會落進「env-unavailable→自動放行並記帳」而不是誤判「乾淨」,不違反 diff 自己宣稱的「不吐假的空結果」那條 invariant,所以不判 major。

## F2 合法 JSON 後面多出任何內容,一律判「讀不懂」

severity: minor
blocking: 否
引句:「raw[raw.find("{"):] if "{" in raw else ""」
file: `scripts/lumos:20991`

同一段復原邏輯只往前找起點,不處理「JSON 已經結束、後面還有多餘內容」的情況。`json.loads` 對多出來的尾隨內容會丟 `Extra data` 例外,兩次嘗試(原文、切過的文字)都一樣失敗。

最小重現:
```
printf '{"version":1,"diagnostics":[]}\nSome trailing banner\n' | python3 scripts/lumos dart-sarif
# 輸出:擋下:讀到的不是 dart analyze --format=json 的輸出……
# rc=2
```
降權理由同 F1:目前實測的真 `dart analyze` 輸出沒有尾隨雜訊,此為對輸入格式本身的邊界測試,尚未在真實 dart 環境重現;失敗後果一樣是「跑不動」而非「假乾淨」。

## F3 `--out` 給到父目錄不存在的路徑,整支指令會用未接手的例外死掉

severity: minor
blocking: 否
引句:「with open(out, "w", encoding="utf-8") as fh:」
file: `scripts/lumos:21025`

`cmd_dart_sarif` 寫檔前沒有檢查目的路徑的父目錄是否存在,`open(out, "w")` 直接讓 `FileNotFoundError` 往外拋,印出 Python traceback,結束碼是未捕捉例外的 1,不是這支指令自己定義的 rc2「讀不懂」語意。

最小重現:
```
echo '{"version":1,"diagnostics":[]}' | python3 scripts/lumos dart-sarif --out /tmp/nonexistent_dir_xyz/out.sarif
# Traceback ... FileNotFoundError: [Errno 2] No such file or directory
# rc=1
```
降權理由:實際閘只會用 `_lint_run_and_parse` 裡 `tempfile.mkstemp(suffix=".sarif", ...)` 產生的暫存檔路徑呼叫 `--out`,那個路徑的父目錄(系統暫存區)保證存在,這條路徑在真正的新增告警閘流程裡摸不到。而且這個寫法跟 `cmd_sqlfluff_sarif`(scripts/lumos:20916)、`cmd_stylelint_sarif`(scripts/lumos:20950)完全一樣,是既有共通模式,不是這次 dart 橋接新引入的缺陷。

---

## 邊界輸入實測清單(以下皆為真跑,非只讀碼)

- **檔名含空白與中文**:`lib/資料夾 with space/中文檔 c.dart` 真的用 `dart analyze --format=json` 分析,`lumos dart-sarif` 正確轉出對應 URI(含轉義的中文與空白),`_lint_run_and_parse` 也正確剝出來。
- **多支檔 + 刪檔**:在臨時 git repo 建 base/head 兩版,`lib/a.dart`(舊有未使用變數)、`lib/sub dir/b file.dart`(新增,含空白檔名)、刪掉 `lib/to_delete.dart`,直接呼叫 `_lint_new_verdict`——只有兩支新引入的未使用變數被判「新增告警」,舊債與被刪檔都沒有誤觸發,`status: blocked`、`new` 長度 2,吻合閘的設計意圖。
- **分析器吐 INFO 等級**:啟用 `unnecessary_this` lint rule,真機拿到 `"severity":"INFO"`,`lumos dart-sarif` 正確映射成 SARIF `"level":"note"`。另外確認 `level` 欄位在 `_lint_run_and_parse` 裡完全沒被讀取(`grep '"level"'` 全庫只有寫入端這一處),INFO/WARNING/ERROR 對閘的擋不擋沒有差別——這是三支橋接共通的既有行為,不是本次新增的差異。
- **極大輸出**:合成 5 萬筆診斷(~9.6MB stdin),`lumos dart-sarif` 在約 2 秒內轉完 SARIF,沒有崩潰或明顯效能問題。
- **Windows 路徑形狀**:餵 `"C:\\Users\\dev\\proj\\lib\\a.dart"` 給 `_dart_rel`,在 macOS(posixpath)上 `os.path.isabs` 判非絕對路徑,原樣放行不誤轉——這是 Python `os.path` 隨平台切換的正常行為,無法在此機器上驗證 Windows 原生執行的正確性,但也沒看到會壞的邏輯(相對路徑判斷失敗時一律回傳原字串)。
- **符號連結目錄**:額外自建一個非 macOS 內建的符號連結(`/tmp/dart_symlink_proj` → `/tmp/dart_real_proj`),從連結路徑下跑 `dart analyze | lumos dart-sarif`,URI 正確轉成 `lib/a.dart`,驗證 `_dart_rel` 對 `cand`/`os.path.realpath(cand)` 雙重嘗試的設計確實有效。
- **snapshot 前綴剝除**:同上「多支檔+刪檔」那組臨時 repo 測試已一併證實,`_lint_run_and_parse` 的 `path_prefix` 與 `_dart_rel` 的相對路徑轉換接得起來,沒有殘留 `.lumos/lintbase-*/head/` 那層前綴。
- **dart 沒裝(環境不可用)**:把 `.lumos/lint.json` 的 dart 指令換成不存在的執行檔,真跑 `_lint_new_verdict`,結果 `status: env-unavailable`、`blocked: false`、`autopass: true`——沒有被誤判成 `clean`,吻合 diff 聲稱修掉的假綠問題(用同樣的臨時寫法驗證過,如果照舊寫法讓 dart-sarif 吐零條 SARIF,這裡會變成 `status: clean`,那才是真的假綠)。
- **測試子集**:`python3 scripts/test_lumos.py -k t_dart_sarif_bridge` 12 案例全過。

## 固定席逐條判(是否破壞該節點宣稱的行為)

- **guard-kill.md**(★INVARIANT★ rc 優先序 / JSON purity):不影響。`cmd_dart_sarif` 是獨立新函式,沒有共用或修改 guard kill 的 rc 判定與 `--json` 輸出路徑。
- **授權與歸屬.md**(★INVARIANT★ SPDX/MIT 全文、LICENSE 白名單):不影響。新函式插入在 `scripts/lumos` 檔案中段,檔頭 SPDX 與 MIT 全文未被觸及;diff 沒有新增檔案進 vendored 清單或動到 `deinit` 白名單邏輯。
- **lumos-cli-read.md**(★INVARIANT★ search 排除 superseded):不影響。這次改動完全不碰 `search`/檢索過濾邏輯。
- **lumos-cli-lifecycle.md**(★INVARIANT★ re-inject 只覆蓋 sentinel 內、外部 byte-equal 保留):不影響。AGENTS.md 裡「73→74」那行落在 `<!-- LUMOS:GRAPH-DISCIPLINE:END -->` 之後,屬 sentinel 外的人工維護區,不受這條 invariant 規範,也沒有動到 sentinel 內的內容。
- **design-loop.md**(★INVARIANT★ 處置閘第五步的審材格式判定):不影響。純新增 CLI 子命令與轉換邏輯,未觸及 design-loop 的審材類型判定。
- **pitfalls-code-loop.md**(★RISK★):不影響。這是 lint-adapter 的 SARIF 橋接層,不是 `pitfalls --diff` 的風險分級演算法本身,兩者沒有程式碼路徑交集。
- **loop-convergence-recording.md**(★RISK★):不影響。與代碼審/設計審的收斂留痕機制無關。
- **lumos-deinit.md**(★RISK★):不影響。沒有新增檔案需要處理進 deinit 白名單,`dart-sarif` 只是既有 `scripts/lumos` 內的新函式與新 subcommand,不是新的獨立檔案。

最高嚴重度為 minor,三條 finding 全部非阻擋:核心新增告警閘邏輯(多檔、刪檔、空白/中文檔名、符號連結、snapshot 前綴、dart 未安裝的 fail-open-and-log)在真機實測下都如設計運作,唯一站得住腳的缺口是 SARIF 輸入的「JSON 前後夾雜文字」復原機制本身不夠健壯,但失敗時走的是既有、有留痕的自動放行路徑而不是假造乾淨結果。
