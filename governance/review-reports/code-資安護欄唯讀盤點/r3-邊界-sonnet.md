severity: minor

## 邊界席 r3 報告(code-資安護欄唯讀盤點/r3/邊界-sonnet)

白話說明:上一輪修補把「圖譜路徑上有捷徑就不讀」補上了,我試了好幾種極端輸入,都守得住,只剩一條繞法:`--vault` 的路徑裡先經過捷徑、再用 `..` 往上走。

### Finding 1:`--vault` 路徑中的 `..` 會把「路徑上沒有捷徑」的檢查騙過去

引句:「    p = Path(os.path.abspath(str(p)))」

severity: minor
blocking: 否

歸因:有證據的原有漏查(修前修後都讀到 repo 外,不是這次修補造成的回歸)。這也是 R2 同症狀「--vault 讀到 repo 外」還沒補完的一角。

- 失敗場景:
  - 輸入:repo 內有捷徑 `link`,指到 repo 外的 `outside/inner`;repo 內和 repo 外各有一個 `real-knowledge`。在 repo 根執行 `lumos --vault link/../real-knowledge security list --json`。
  - 預期:擋下,因為路徑上有捷徑。
  - 實際:檢查用的是 `abspath` 純字面化簡後的 `repo/real-knowledge`,看起來安全。但實際開檔用的是 `_secinv_select_vault` 回傳的原始 `Path(vault_arg)`,作業系統會沿捷徑解析到 `outside/real-knowledge`。
- 證據:
  - 兩版輸出都是 `scope.files=1, bytes=14, read_complete=true`,`vault` 欄位是 `link/../real-knowledge`。
  - repo 外那篇內容是 `# outsidenote\n`,剛好 14 位元組;repo 內那篇只有 9 位元組。所以讀到的是 repo 外的檔。
- 真正的缺陷點:`scripts/lumos` 的 `_secinv_vault_problem`(檢查字面化簡後的路徑),以及 `_secinv_select_vault` 回傳原始 `Path(vault_arg)`。圖譜根只用 O_NOFOLLOW 擋最後一段。
- 現實性:自動找圖譜的入口不受影響,因為它用的是 `Path.cwd()` 的實體路徑。要觸發得由操作者自己在 `--vault` 裡寫出 `捷徑/..`,所以我定 minor。
- 修法方向:`--vault` 的路徑逐段比對(含 `..` 段先拒絕),或檢查與開檔用同一個正規化後的路徑。

## 三問

**① 原問題的修復效果有何行為證據?**

| 組 | 案例(input) | 修前 | 修後 | 結論 |
|---|---|---|---|---|
| R2 | `docs` 是捷徑指到 repo 外,自動找圖譜 | 讀到外部,files=1,rc0 | 擋下,訊息「圖譜路徑上的 …/docs 是捷徑,不跟隨」 | 已修好 |
| R2 | 同一個 `docs` 捷徑,用 `--vault docs/b-knowledge` | 讀到外部 | 同樣擋下 | 已修好 |
| R2 | `--vault link/../real-knowledge` | 讀到外部 | 讀到外部 | 沒修到,見 Finding 1 |
| R1 | 圖譜目錄名含 ESC、U+202E、U+3164、U+FE0F、U+00AD,選圖譜失敗的 stderr | 原樣印出 | 全部跳脫成 `\uXXXX` | 已修好 |
| R4 | 同一篇有 80 條壞來源的控制項,後面再接一條壞證據的 `LATE`(錯誤超過每篇 50 筆上限) | 錯誤 81 筆 | 錯誤 51 筆,附 `errors_truncated` omitted=31 | 已修好 |
| R4 | 同上,看被截掉錯誤的那幾條 | `B79`、`LATE` 的 `references_valid` 為 false | 同樣為 false,`GOOD` 為 true | 已修好,上限不會把引用錯誤吞掉 |

- 這些案例的 input、before 與 after 命令都已實跑並留下結果。命令都是對 `lumos security list --json` 加 `--vault` 或在不同工作目錄下跑。
- 修前修後各用 worktree `aadf6b07` 與 `84a58aee` 比對。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**

以下 preserve 案例修前修後結果一致,沒有發現回歸:
- 正常 repo,從子目錄執行自動找圖譜,可正常讀取。
- 正常 repo,用絕對路徑 `--vault`,可正常讀取。
- 剛好 2MiB 的檔案可讀;2MiB+1 位元組得到 `file_too_large`;只有 BOM 的檔案正常讀入。
- 10001 個 Markdown 檔得到 `too_many_files`,只讀 10000 個,耗時約 1.2 秒,兩版相同。
- 2000 層深的目錄得到 `enumeration_failed`(目錄巢狀太深),不崩潰。
- 33 種畸形登記值,包含 null、陣列、數字、布林當 `schema_version`、超深巢狀 3 萬層、不可雜湊值、全形日期、超大年份。兩版都沒有 Traceback,錯誤歸類一致。
- 中文帶空白的檔名、NFD 檔名、非 UTF-8 檔案、空檔、指向目錄與檔案的捷徑,都有正確分類,沒有崩潰。
- `_secinv_show` 加了 `hidden=True` 後,中文全形標點與 U+3000 不會被誤跳脫。Hangul filler、ZWJ、變體選擇符、tag 字元會被跳脫。
- 順帶發現:U+00A0 與 U+3000 看起來像空白但沒有被跳脫。這兩個字元不會讓輸出偽造指令,所以我沒算成 finding。
- 順帶發現:`_secinv_show` 的預設上限改成 2000 字,連帶影響 `vault` 路徑與選圖譜失敗的訊息,超長路徑會被截斷。這是設計取捨,我沒算成 finding。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- Finding 1:修前與修後都讀到 repo 外(bytes=14),所以是原有漏查,不是回歸。

## 未驗範圍
- 沒有逐項驗證表態記錄的 py-* 宣稱。
- 沒有對 `t_seclist_r2_docs_symlink` 等守護測試做破壞測試。
- 沒有驗證「同層多個圖譜」的行為。
- 沒有驗證 `--vault` 指到 repo 以外沒有 `.git` 的目錄時,檢查範圍只剩目錄本身這件事是否符合預期。

## 清理
兩個 worktree 與我自己的 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/邊界-sonnet/` 都已刪除。目錄裡另外 4 個 `r3-通才-sonnet-*` 是別席的,我沒碰。

最嚴重 severity:minor,blocking 共 0 條。
