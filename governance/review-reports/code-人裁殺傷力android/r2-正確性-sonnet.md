severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/47ebf45980d0bdbe5649fdd88d49a06caa7c1a9c79bc3e574bbe39410d0647f9.json.warming` 不存在,沒有鎖要處理。

派工附的角色卡沒有出現在尾端,所以角色鏡頭略過。

## c1 人裁的 run_cmd 檢查只看第一個 gradle 段,第二段以後的 `test` 不擋
severity: minor
blocking: 否
引句:「每一段第一個檔名是 `gradlew` 或 `gradle` 的詞之後、不以 `-` 開頭的詞」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40965`(`_gradle_task_list` 的實作是取到第一個 gradle 段就 `return`)

規格〈用詞〉寫「每一段」,實作遇到第一個 gradle 段就回傳。
1. 輸入:Android 專案(`app/build.gradle.kts` 有 `com.android.application`),`run_cmd` 為 `./gradlew clean && ./gradlew test --tests '*{method}'`。
2. `_detekt_walk_segments` 切出兩段,迴圈在第一段 `clean` 就 `return ['clean']`,第二段的 `test` 沒看到。
3. `_situation_rule_android_cmd_problem` 因此回 None,人裁不擋、照常跑殺傷力。同一條命令拿掉 `clean &&` 就會被擋(rc 2)。
4. 後果是這條 Android 頂層 `test` 加 `--tests` 會在基準階段 abort,不是判錯。但擋下訊息要等跑完基準才看得到,Android 冷建構可能十幾分鐘。

實跑輸出(用建好的假 Android 專案呼叫 `_situation_rule_android_cmd_problem`):

| run_cmd | 結果 |
|---|---|
| `./gradlew clean test --tests '*{method}'` | BLOCK |
| `./gradlew clean && ./gradlew test --tests '*{method}'` | PASS |
| `./gradlew --stop; ./gradlew test --tests '*{method}'` | PASS |
| `./gradlew build -x lint && ./gradlew :app:test --tests '*{method}'` | PASS |

另有兩點:
- 這是舊實作(遇 `&&` 就停)已有的限制,修補把它換成 detekt 的切段後沒改到。
- 測試只釘了 `&& echo test`(⑪)與 `cd sub && ./gradlew …`(⑬),沒有「兩個 gradle 段」的案例。把 `_gradle_task_list` 改成回傳第一個 gradle 段,現有測試全綠,只有這個新案例會紅。
- 同類的次要缺口:`./gradlew -p android :app:test` 裡 `-p` 的值被跳過,模組路徑照平台根解析,找不到 `android/app` 的建置檔,不擋。

## 逐項判讀

**檔頭區判定**
- 實跑的輸入:package 前有註解、多行 `@file:`、方括號 `@file:[…]`、行尾註解加分號、`;` 一行兩句、BOM、檔尾沒換行、`as` 別名同名、`flatMapConcatX` 子字串,共 12 格,行為都符合規格。
- 對照程式讀取路徑:CRLF 在 `_kt_sit_read_many`(把 `\r\n` 換成 `\n`)和 `cmd_guard_kill` 的文字模式讀檔兩邊同樣被換成 `\n`;BOM 兩邊都保留。所以 also 的 old 與殺傷力讀到的行一致。
- 檔尾沒換行或插入點是最後一行,會 fail-closed 拒絕,不會插錯位置。

**also 套用**
- 主替換改到 import 區造成錨點跑掉:人裁入口用 `_kill_also_apply(src.replace(old, new, 1), also)` 先試套一次,對不上就在跑基準前擋下。
- 殺傷力端對不上判 error,發生在寫檔前。

**`_kill_run_dir`(殺傷力改在平台根跑)**
- 平台根是 `.`、`sub`、`sub/x` 都對。
- 沒提交的目錄判 error,基準不跑。
- 唯一的偏差是平台根資料夾名稱以 `..` 開頭(例如 `..hid`)時,`rel.startswith("..")` 會誤判。現實幾乎不存在,沒有具體場景,不單獨標。
- 對既有設定的影響:同一條 `run_cmd` 在推送前的合約測試閘本來就在平台根跑,所以能過閘的設定不會因此壞。
- 計劃、guard-kill 筆記與程式內說明的「不加 cd」與「在平台根跑」互相一致,沒有殘留舊說法。
- `--json` 輸出純度合約(`t_guard_kill_json_purity`):修補沒有新增 stdout 輸出。
- rc 優先序合約(`t_guard_kill_rc_precedence`):整組 error 走 `_kill_err_all` 仍是 error,沒有破壞。

**`fail_excerpt`**
- 實跑:真 Gradle 樣式輸出,兩種路徑形式(`file:///private/var/…` 與 `/var/…`)都遮成 `<worktree>`。
- `/Users/enzo2` 不被家目錄遮罩吃掉。
- 多位元組每行截 200 字,沒有亂碼。
- 挑不到錯誤行時退回結尾 800 字。CRLF 行尾會去掉 `\r`。
- 小邊界(不標):路徑後面緊接 `.` 時不遮。例如 `…/wt.` 或 `/Users/enzo.` 句尾;這不是新增風險,是邊界規則的取捨,影響僅限遮罩漏一處。

**測試品質**
- 路徑邊界、工作樹在家目錄底下、`app:test`、`-P`/`-D`/`--console` 值、`sh -c` 展開都有行為斷言和對照格。
- ⑭是結構測試,但同一支測試另有 ⑬ 行為斷言,符合手冊第 6 點。
- 唯一缺口是 c1 的第二個 gradle 段案例。

## 附:圖譜鏡頭
本次 `impact` 列了 37 個固定席,下面只對真正相關的幾篇逐條判斷。
- `Systems/guard-kill.md` 的兩條 ★INVARIANT★:
  - rc 優先序 `t_guard_kill_rc_precedence`:不影響。新增的平台根錯誤列判 error,仍落在 drifted/abort/error 回 rc 2。
  - `--json` 成功時 stdout 恰一行 `t_guard_kill_json_purity`:不影響。修補沒有新增 stdout 輸出。
- `Systems/bound-tests-gate.md` 的 ★INVARIANT★(推送前閘對合約測試逐支真跑):不影響。閘的程式沒動,只是殺傷力改成與它同一個執行目錄。
- `Systems/lumos-cli-lifecycle.md`(init 骨架的家):不影響。Android 骨架只改 `run_cmd` 與 `_請先確認` 的說明,不碰 re-inject 的 sentinel 合約。
- 其餘固定席(slim 系列、design-loop 等)的合約與這次改動無關,判不影響。

最嚴重 severity:minor;blocking 共 0 條。
