severity: major

# 第 2 輪 邊界-sonnet 報告

實驗目錄:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/rr-r2-work-邊界-sonnet/(repo 為 `git clone --shared`,t1 為 pathspec 實驗用的獨立小 repo)。

## F1 diff 的檔案清單用 pathspec 直接餵,檔名裡的 [ ] * 會被 git 當萬用字元,別支檔的改動混進這篇的 diff
severity: major
blocking: 是
引句:「改名的新舊路徑都放進 pathspec」
file: `scripts/lumos:28248`
1. 實測(t1):about_code 列 `app/[id]/p.tsx`(Next.js 動態路由的常見寫法),`git diff HEAD~1 HEAD -- 'app/[id]/p.tsx'` 會同時印出 `app/i/p.tsx`(`[id]` 被當成字元集合);about_code 列 `app/*.txt` 的字面檔名,pathspec 會連 `app/x.txt` 一起收。加 `--literal-pathspecs` 後才只剩該檔。開頭是冒號的檔名(`:x/a.py`)會被當 pathspec 魔法字,diff 變空。
2. spec 〈做法〉0 只講「要拿去問 git 的路徑用 git 原樣路徑」,〈做法〉2 只講「放進 pathspec」,沒有要求字面比對。照字面實作,判定者會收到「不是這篇管的檔」的 diff(誤導判定、且每篇多花字元額度),或整段 diff 空掉(該點的漂移漏掉)。
3. repo 已有同一個坑的先例與解法:`scripts/lumos:28248` 的 `_lens_git(root, "--literal-pathspecs", "diff", ...)` 和 `scripts/lumos:28620` 一帶,註解寫「檔名裡的 * 不當萬用字元」。本案的組 diff 那一步沒繼承這條。要求:組 diff 的 git 呼叫一律加 `--literal-pathspecs`(且 S2 補一個含 `[`、`*` 檔名的案例)。

## F2 推送前掛鉤把 128 以上一律當中斷停下,提醒版的「恆放行」在工具被 OOM 或 SIGTERM 殺掉時不成立,且跟 CI 的刻意處理相反
severity: major
blocking: 是
引句:「回傳碼交給 `pp_stop_if_signaled`(128 以上=被 Ctrl-C 之類的訊號中斷,整支掛鉤停下)」
file: `scripts/hooks/pre-push:50`
1. `pp_stop_if_signaled`(`scripts/hooks/pre-push:50-55`)對 rc>=128 一律 `exit "$1"`,分不出 Ctrl-C(130)、SIGTERM(143)、OOM 的 SIGKILL(137)、終端關閉的 SIGHUP(129)。
2. 〈做法〉4 同一節寫「★任何情況都回 0★」,CI 那步又特地寫「被 OOM 或逾時殺掉也吞掉,這是刻意的:提醒不值得讓 CI 紅」。但掛鉤這邊被 OOM 殺掉會讓整個推送停下(訊息還寫「被中斷」),這道只提醒的檢查因此可以擋推送;三十秒上限是 Python 內部計時,擋不住外部的殺。〈做法〉4 沒有給掛鉤一個對應的處理(例如只認 130、或外包一層 `timeout`),也沒有 S9 之類的條款覆蓋。
3. 影響:大 repo 或記憶體緊的機器上,一個提醒工具的 OOM 讓使用者只剩 `LUMOS_SKIP_REREAD_CHECK=1` 或 `--no-verify`(後者連別的閘一起繞)。要求:至少寫明「只認 130 停下,其餘 128 以上照放行並印這次沒提醒」,或在 spec 裡明說接受這個代價並列進〈實務隱患〉附回頭條件。

## F3 最外層「接住任何沒預料到的例外」沒指定接 Exception 還是 BaseException,寫成後者會把 Ctrl-C 吞掉,第 1 輪剛修的問題回頭
severity: minor
blocking: 否
引句:「任何沒預料到的例外(最外層接住)」
file: `scripts/lumos:26326`
1. 掛鉤靠回傳碼 130 讓 `pp_stop_if_signaled` 停下;若最外層寫 `except BaseException`(或裸 `except:`),KeyboardInterrupt 會被轉成 rc0 加 skipped,掛鉤繼續跑 8 分鐘全套,正是第 1 輪要消的行為。
2. 目前條款 S7、S9 都沒有「送 SIGINT 後 rc 必須不是 0」的測試。要求:spec 明寫只接 `Exception`,S7 補一個 KeyboardInterrupt 案例。理由放行:這是措辭與測試面,實作者多半會寫 Exception,所以標 minor。

## F4 專案設定 note_reread.mode 寫錯值、寫壞、父層不是物件、檔案不存在時的行為沒定義,而且 off 讀設定的時機在解析範圍之後,跟 S13「不寫帳」對不上
severity: minor
blocking: 否
引句:「`.lumos/config.json` 的 `note_reread.mode`:`warn`(預設)/`off`,從被檢查的頂端版本讀」
file: `scripts/lumos:28742`
1. 既有先例 `_drift_gate_config`/`_drift_old_sentence_config`(`scripts/lumos:28742-28816`)把「讀不成 JSON、父層不是物件、值不在清單、null」四種各給一個預設加一句提醒。本案沒有:例如寫 `"mode": "block"`(以為轉擋)、`"Off"`、`true`、`note_reread` 是字串,實作者可能 `cfg["note_reread"].get(...)` 丟 AttributeError,被最外層吞成每次推送都記一筆 skipped(帶「例外」原因),噪音混進兩週量測。
2. 設定要從「被檢查頂端」讀,頂端得先過 `_note_audit_resolve`;但 resolve 在淺層 clone、頂端已在主線、沒有圖譜時就提早結束(頂端根本還沒算出來)。這時 mode=off 的專案仍會印原因並記 skipped,跟 S13「off 時印一行、回 0、不寫帳」矛盾。要求:定義四種壞值的落點(建議一律 warn 並印一句),並寫明 off 是在 resolve 之前(從 HEAD 或推送頂端直接讀)還是之後。

## F5 補測試檔規則只認同層與根目錄的 tests/<X> 對 src/<專案>/<X>,monorepo 與沒有 src/ 的專案補不到,而且沒講 `_nodehome_is_test` 要帶 layout
severity: minor
blocking: 否
引句:「或它在 `tests/<X>/…` 而那支檔在 `src/<專案>/<X>/…`(兩個 `<X>` 相同;實驗在 rtb 用的就是這條)」
file: `scripts/lumos:23636`
1. 沒寫 `tests/` 是不是只錨在 repo 根。monorepo 的 `packages/a/tests/core/x.py` 對 `packages/a/src/a/core/x.py` 字面不成立;Flutter 的 `test/foo/bar_test.dart` 對 `lib/src/foo/bar.dart`、Maven 的 `src/test/java/...` 對 `src/main/java/...`、Go 之外沒有 `src/` 的專案,都補不到任何測試檔。行為不出錯(只是 diff 少了測試),但 r1 正確性席指出的「rtb 測試跟程式不在同一層、一支都補不到」在這些形狀上原樣存在,〈誠實界線〉沒講。
2. 「`_nodehome_is_test` 判是測試」:該函式第二個參數 layout 預設 `({}, {})`(`scripts/lumos:23636`),不帶 layout 就認不出 Swift/C#/Kotlin 的測試資料夾(`FooTests/`、`src/androidTest/`)。`_nodehome_required` 是每次用 `_nodehome_layout(side.all_paths)` 帶進去的;spec 沒要求 reread 也帶。
3. 要求:寫明 `tests/`、`src/` 是否允許出現在任意深度前綴之下、layout 帶不帶;或在〈誠實界線〉補「補測試檔只涵蓋這兩種佈局」。

## F6 報告 json 區塊的抽法只講「整行就是」,沒講 CRLF、行尾空白、大小寫與最後一個區塊沒收尾的情況;逐項「其餘照收」讓非字串的 quote 與 why 進到紀錄與終端輸出
severity: minor
blocking: 否
引句:「`quote`、`why` 缺了當空字串。同一個行號出現多次只留第一次。其餘照收。」
file: `scripts/lumos:26326`
1. 〈做法〉0 只對「筆記」規定去尾端 `\r`,報告沒有。判定者(尤其 codex 或在 Windows 存檔的報告)輸出 CRLF 或 ```json 後帶空白時,「整行就是」字面比對失敗,整份拒收 rc2,作者得手改報告。最後一個 ```json 沒有收尾圍欄(輸出被截斷)時,是取最後一個未收尾的、還是退回前一個完整的,沒定義。
2. `quote`、`why` 存在但不是字串(數字、null、物件、超長字串)時「照收」,寫進紀錄檔沒事,但結尾要「印點出的行(行號、原句、理由)」;沿用 `_esc_clean` 之前這裡會 TypeError 或把控制字元(ANSI 逸出序列,內容來自筆記與 diff,即提示注入的載體)直接印到終端。既有先例:`scripts/lumos:28900` 一帶 `_drift_print_findings` 印前都過 `_esc_clean`,註解指明是資安席發現的。〈實務隱患〉說提示注入最壞結果是少點幾行,沒算到終端輸出。
3. 要求:寫明報告行的去尾規則與未收尾區塊的處理,`quote`、`why` 不是字串時轉字串截長,印出前一律過 `_esc_clean`。

## F7 30 秒上限說每次 git 呼叫前看截止時間,但被重用的函式都沒有截止時間參數,實際上限是每個 git 呼叫固定 20 秒的總和
severity: minor
blocking: 否
引句:「同舊句檢查 `_DRIFT_M1_BUDGET_SEC` 的量級,不吃別道檢查的時間」
file: `scripts/lumos:34787`
1. `_lens_git` 每次呼叫的逾時是寫死的 20 秒(`scripts/lumos:34795-34796`);`_note_audit_resolve`(約 10 次 git)、`_nodehome_side`(每篇 Systems 筆記一次 git show,本 repo 75 篇兩邊約 0.8 與 1.5 秒)、`_nodehome_changes` 都不收 deadline。spec 只給 `_note_audit_resolve` 加「回原因」參數,沒說要不要讓它們收 deadline。
2. 本 repo 實測整段很快(resolve 0.16 秒、side 0.8 秒、changes 0.03 秒),所以這只是「慢磁碟、大 vault 時 30 秒不成立」的問題,而且 S7 的「超過 30 秒」測試只能靠注入假時鐘,測不出真實上限。要求:註明 30 秒是「在 reread 自己的呼叫點之間檢查」的軟上限,不保證含共用函式內部;或給共用函式加 deadline 參數。逐 ref 各 30 秒(推 20 條分支最壞 10 分鐘)〈實務隱患〉已承認,這裡不重報。

## 已讀無 finding 的節與情境(逐項查過)
- 新分支首推(全 0 舊值):`_push_range_start`(`scripts/lumos:34701`)→ 有主線用分岔點、沒主線回空樹;`_note_audit_resolve` 對空樹回 base=None,`_notes_status_flipped` 的做法 `rng0 = tip` 對 base=None 走整段歷史,`_nodehome_side(where=None)` 回空邊,`_nodehome_changes(base=None)` 用空樹。共用函式抽出後沿用同一寫法即可,無 finding。上線點截斷對空樹起點回上線點(`scripts/lumos:24201-24202`),無 finding。
- force push:舊值本機找不到時走 `_push_pick_base`/`_push_no_mainline`,重定基底後分岔點不是舊值祖先會取分岔點,不會把主線新提交算成這次的;無 finding。
- 只推 tag:`pushed_ref=refs/tags/...` 時 `target=None`、主線候選都保留;tag 指到已在主線的提交會回 None 並記 skipped,合理;指到 tree 或 blob 的 tag 在 `_lens_full_sha` 失敗,落到「終點找不到」skipped,無 finding。
- about_code 列不存在的檔、資料夾、glob:家對照表是字面比對(`_nodehome_key`,`scripts/lumos:23849`),資料夾與 glob 本來就不會成為家,不會產生候選;指紋把不在頂端一般檔清單裡的都記「已刪」,穩定不出錯。一個副作用:資料夾項或符號連結項底下的內容變了指紋不變,屬〈誠實界線〉已寫的範疇。
- 筆記被改名或刪除:`git log --name-only -M` 取新路徑、頂端不存在的濾掉、起點那邊的舊路徑只在頂端也存在時才算,行為一致;改名會換指紋、重列一次,可接受。
- 同一支檔被兩篇家列:兩篇各自成候選、各自組 diff,無互相覆蓋。
- 項目檔頭與本文分隔:檔頭在前、分隔線 `---本文---` 只可能被筆記或 diff 內容以「整行相同」的形式撞到的機會是零(筆記行帶行號前綴、diff 行帶 +/-/空白前綴),頭部 `dict(findall)` 讀法不受影響;無 finding。
- 治理帳與 _KNOWN_GATES(`scripts/lumos:6943`、`scripts/lumos:1220`):新閘名必須登記,spec 已寫;無 finding。

最高等級:major;blocking 共 2 條
