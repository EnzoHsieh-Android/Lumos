severity: minor

## 問 1 分層與依賴方向

對齊。第二輪的三處修補都接到鄰居已有的函式上。

- **`--diff` 與 HEAD 解析**:`_situation_rule_diff_problem` 與 `_situation_rule_target` 現在都呼叫 `_lens_full_sha`(`scripts/lumos:69513`),不再自己叫 git。這跟 `scripts/lumos:15414`、`16185`、`23245` 等十幾處同一種做法。人裁這一段已沒有剩下的 `subprocess` 直呼。`_codeloop_git_head`(`scripts/lumos:72457`)是不帶逾時、不接 OSError 的舊式寫法,留給 code-loop 那一層用。
- **檔頭掃描**:`_situation_rule_header_scan` 呼叫全庫的 `_strip_c_comments(kotlin=True)`(`scripts/lumos:6869`),跟 `scripts/lumos:39565`、`40226` 同一個入口。
- **`-p` 專案目錄**:用共用的 `_under_root`(`scripts/lumos:16839`)接路徑,沒有另寫 `isabs` 拼法。
- **任務清單**:仍走 `_detekt_walk_segments`、`_gradle_args_tasks`,沒有跨層直呼。

## 問 2 命名與錯誤處理

大致對齊,有一處重複寫法(見 a1)。

- 新函式的前綴(`_situation_rule_*`、`_gradle_*`)、rc 2 加 `_situation_rule_say` 印原因、輸出一律過 `_kill_esc`,都跟 `scripts/lumos:75918`~`75955` 一帶的鄰居一樣。
- run_cmd 不是字串時,鄰居 `_detekt_plugin_values`(`scripts/lumos:40888`)是靜默回空。這裡改成講清楚並回 rc 2。人裁的語意本來就是「殺傷力沒跑要說明」,所以這個差異合理,不列。

## 問 3 第二種做法

結構上沒有新增平行的整套做法,但有兩處自寫小機制(見 a2、a3)。

- 取任務、取段、剝註解、解析 rev、接路徑,都借用既有函式。
- shell 註解辨識與換行標記法是新寫的小機制。兩者都長在既有函式裡,沒有另立入口,所以我判 minor,不判 major。

## a1 設定鍵名公式複製了兩份
severity: minor
blocking: 否
引句:「key = f"platforms.{pdata['default_platform']}.run_cmd" if pdata.get("multiplatform") else "test.run_cmd"」
file: `scripts/lumos:75935`
對照 `scripts/lumos:76452`:`_situation_rule_android_cmd_problem` 裡有同一條公式。這輪修補在 `_situation_rule_platform` 又抄了一份。兩處以後只改一處,畫面上的設定鍵名就會對不上。鄰居裡沒有別的地方拼這個字串,可以抽成一個小函式共用。

## a2 shell 註解辨識是手寫的詞級判斷,丟掉了 shlex 本來有的引號資訊
severity: minor
blocking: 否
引句:「cut = next((k for k, w in enumerate(seg) if w.startswith("#")), None) if comments else None」
file: `scripts/lumos:40983`
- `_detekt_split_segments`(`scripts/lumos:40647`)用 shlex 切詞,並明寫 `commenters = ""`(依判定表不當註解)。這輪在切完詞之後才用 `w.startswith("#")` 判註解,docstring 自己承認「引號包住的 `"#x"` 也當註解」。
- 同一支 shared walker 因此多了一種預設關閉的模式,detekt 判定與人裁走的是兩套註解規則。結構上是旗標,不是另一套函式,所以只判 minor。
- 先 shlex 後切註解,還有一個副作用:註解裡有單引號(如 `# don't`)時,`_detekt_split_segments` 回 None,整行被略過。這一行的 test 任務就不會被檢查到。這屬於正確性席的範圍,我只提示有這個副作用。
- ⚠ 判不準:改在 `_detekt_split_segments` 加參數是否更合鄰居的做法。shlex 的 `commenters` 在詞中間遇到 `#` 也會截斷,跟 POSIX 不同,所以我不判 major。

## a3 檔頭掃描用 NUL 標記補行首狀態,鄰居沒有這個做法 ⚠
severity: minor
blocking: 否
引句:「lines = _strip_c_comments(src.replace("\n", "\n" + _SR_LINE_MARK), blank_strings=True, keep_newlines=True, kotlin=True).split("\n")」
file: `scripts/lumos:76254`
- 剝註解與字串仍走唯一入口,但為了知道「行尾是否落在註解或字串裡」,先在每個換行後插 `\x00`,再看剝完後有沒有留下。
- `scripts/lumos:39565`、`40226` 的鄰居用 `keep_newlines` 或 `keep_length` 直接逐行對齊,沒有靠注入字元來傳遞狀態。
- ⚠ 判不準:這是靠 `_strip_c_comments` 不吃 NUL、只有被剝掉的區段才會抹掉 NUL 的實作細節。如果 `_strip_c_comments` 之後改成逐字元重建,標記可能無聲消失。一般情況下 NUL 不會出現在 `.kt` 原文裡,所以我只判 minor。

不對齊共 3 條,其中 major 0 條
