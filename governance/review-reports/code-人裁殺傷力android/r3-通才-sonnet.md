severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/bfbdd1dda13e21ff2edea589e634f2ceaadba0d3044ffa9f33ca6d18a47db26b.json.warming` 不存在,沒有鎖要處理,也沒刪任何東西。我逐 hunk 讀完 r3-repair.patch,三處重點(`_strip_c_comments` 檔頭掃描、每段合併的任務清單、`_lens_full_sha`)都追到呼叫端,只找到一條問題。

## t1 行尾註解帶單引號時整行被丟掉,擋下檢查靜默放行
severity: minor
blocking: 否
引句:「segs = _detekt_split_segments(line)」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40647`(`_detekt_split_segments` 拆詞失敗回 None)、`/Users/enzo/harness/lumos-srl-android/scripts/lumos:40978`(`_detekt_walk_segments` 遇 None 就 `continue`)

r2 的 b2 要讓「`#` 起到行尾是註解」不再被當任務。實作是先用 shlex 把整行切詞,再從切好的詞找 `#` 截斷。註解裡若有不成對的引號,第一步就失敗,後面的截斷永遠沒機會跑。

失敗場景:
1. 設定的 run_cmd 是 `./gradlew test --tests '*{method}' # don't use :app:test`。
2. shlex 在註解的 `'` 處丟 ValueError,`_detekt_split_segments` 回 None,`_detekt_walk_segments` 跳過整行。
3. `_gradle_task_list` 回空清單,Android 專案的頂層 `test` 沒被擋(該 run_cmd 在 Android 專案會被擋)。
4. 人裁照樣往下跑殺傷力。Gradle 的 test 任務不收 `--tests`,最後以 killed_unattributed 被拒,用戶還是遇到「擋下訊息」本來要避免的那種晚期失敗。

重現(唯讀載入 scripts/lumos,輸出已實跑):
```
_gradle_task_list("./gradlew test --tests '*{method}' # don't use :app:test")  → []
_gradle_task_list("./gradlew test # ok")                                        → [('', ['test'])]
_gradle_task_list("./gradlew test # it's\n./gradlew :app:test")                 → [(''', [':app:test'])]
```
最後一行實際輸出是 `[('', [':app:test'])]`:同一行的 `./gradlew test # it's` 被整行丟掉,只剩下一行。

`t_situation_rule_android_run_cmd_segments` 的註解案例都用成對引號或沒有引號,沒測這條。修法是先切註解再 shlex:找到引號外的 `#` 就截行,或 shlex 失敗時退回「截在第一個以空白開頭的 `#`」再重試。這是 r2 b2 同族沒修乾淨的地方,不是新引入的退步:r2 前這種行也一樣被丟。

## 逐項確認不影響(未列為 finding)
- **`_detekt_walk_segments(comments=False)` 預設路徑**:改寫後行為與舊版等價。空段跳過、`sh` 沒帶 `-c` 不產出、其餘 yield。detekt 的兩個既有呼叫端(40891、41040 行)不受影響。
- **`_gradle_args_tasks(values=…)`**:只多記值。`-p` 與 `--project-dir` 都在 `_GRADLE_VALUE_OPTS`,`--opt=值` 與 `--opt 值` 兩種寫法都取得到。
- **檔頭掃描換行標記法**:換行後補 `\x00`,`_strip_fill` 在 `keep_newlines` 下把被剝區段換成純換行,所以註解與字串內的行首標記會消失、行尾乾淨判斷成立。我走了跨行區塊註解與三引號字串這幾種邊界,行號與乾淨判斷都對得上。`lines = src.split("\n", at + 1)` 的越界判斷(`at >= len(lines) - 1`)也對。
- **`_codeloop_git_head` 換成 `_lens_full_sha(rr, "HEAD")`**:只換了 situation-rule 的一處。`_codeloop_git_head` 其他呼叫端(76993、77018、77345、77681 行)不在這次範圍。兩者都回完整 sha,後續比對不變。
- **run_cmd 非字串的拒絕**:擋在 `_situation_rule_platform`,早於 `_situation_rule_android_cmd_problem`。我沒找到任何地方把 list 當合法 run_cmd 用,所以沒有誤擋既有設定。

## 附:圖譜鏡頭
這次沒附固定席節點(LUMOS-LENS 備援段:範圍內沒有釘到的節點),不逐條回答。我順帶看了 diff 裡改到的筆記:計劃〈用詞〉的檔頭區、任務清單、擋下的 test 任務三條,以及 `Systems/棧別提問表態閘` 的人裁那條 WHY。它們描述的行為和程式一致:每段合併、`:test` 當頂層、`-p` 換專案目錄、檔頭區走 `_strip_c_comments`。t1 的註解行為是程式的限制,筆記那句「`#` 開頭的詞起到行尾是 shell 註解,不算任務」沒寫引號例外,修 t1 時要一起改。

最嚴重 severity:minor,blocking 共 0 條。
