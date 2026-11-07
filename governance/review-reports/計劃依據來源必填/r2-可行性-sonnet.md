severity: major

核對與實驗都在臨時複本做完(複本已刪)。第一輪可行性問題已解:讀不到日期當今天、型錄範例都沒再出問題。這一輪有兩條 major,其餘為 minor。

**第一輪核對**
- 「讀不到日期當今天」:我照字面實作了 `_plan_sources_since()`,讀不到日期時當今天,並在測試總檔加 `LUMOS_PLAN_SOURCES_SINCE=9999-12-31`。跑 `python3.14 scripts/test_lumos.py -k spec_gate`,410 passed、0 failed,跟沒改的基線相同,r1 的 2 條紅已解。
- 型錄計數:用 intake 那段指令重算得 473 / 140 / 324,對得上。範圍 7 的 `dt_sources` 見 F4。

**實驗結果**
- 鏡頭③:照字面寫的判法放到計劃自己的〈依據來源〉表,19 列全過。repo 裡其他計劃都沒有這一節,所以沒有第二份可試。
- 鏡頭④:`_gate_event` 在規格閘(非推送)路徑拿得到全部參數。`rr` 與 `rel` 都在手上,`spec-gate` 已在 `_KNOWN_GATES`,實際寫進了版控治理帳。

F1
severity: major
blocking: 是
計劃自己的預期值表第 115 行有未跳脫的 `|`,現有規格閘的預期值表檢查會把它擋下,計劃過不了自己的閘。這份計劃風險高、`created` 是 2026-11-06、生效日常數也是 2026-11-06,所以預期值表照規定要查。在複本跑 `lumos spec-gate 計劃依據來源必填_計劃 --no-run`,輸出「預期值表: ✗ — … 第 115 行:要剛好 4 格,現在 5 格(格內的 | 要寫成 \|)」,退出碼 1。
引句:「| S1 | 表頭寫成「機制|出處」兩欄 | 擋 | 本計劃〈用詞〉依據來源節 |」

F2
severity: major
blocking: 是
推送前重查若照字面接在 `_expected_push_one` 的迴圈上,`status: todo` 的新計劃會漏過。計劃寫的是「對這次範圍碰到的每一份新計劃」,但那個迴圈只放行 doing,或本次改到的 done(`_spec_gate_push_scan` 裡的 `_live`)。我在臨時 repo 提交兩份缺節的新計劃,一份 todo、一份 doing,再跑 `lumos spec-gate --push-check HEAD~2..HEAD~1`。只有 doing 那份被擋,rc=1;todo 那份沒有任何輸出。本計劃自己就是 `status: todo`,S3 的測試若用 todo 計劃就會紅。實作得另寫一個不看狀態的迴圈,計劃沒講。
引句:「對這次範圍碰到的每一份新計劃,用範圍 1 同一支判定函式再查一次〈依據來源〉,不合格就擋推送(跟它對預期值表簽核的既有做法同一個出口、同一種留帳)」
file: `scripts/lumos:15693`(`_live` 的判定在 `_spec_gate_push_scan` 內)

F3
severity: major
blocking: 是
出處判法的第②種「repo 內存在的檔案路徑」,用 `_refcheck_scan` 判會誤擋合法路徑。`_refcheck_scan` 只抽「第一層是 repo 頂層目錄、含 `/`」的反引號路徑。我實跑:`` `CLAUDE.md` ``、`` `README.md` `` 回傳 `[]`,`` `.github/workflows/x.yml` `` 也回傳 `[]`。照字面實作,這幾種路徑會判成沒有合格出處而被擋。這兩個檔都存在於 repo 根。`_refcheck_scan` 的輸入是整段文字、輸出是 claims 清單,不是「路徑存在」的布林,介面也要自己包一層。另外它對目錄也回 ok,`` `scripts/` `` 會過關。
引句:「repo 內存在的檔案路徑:反引號包住,用 refcheck 現成的 `_refcheck_scan` 判存在(相對 repo 根,解析後要在 repo 根底下,工作目錄裡有的檔就算)」
file: `scripts/lumos:37571`

F4
severity: minor
blocking: 否
範圍 7 說 `dt_sources` 已在 `check.py` 實作,但本分支與 main 都沒有這個函式。它只存在未合併的 `origin/EnzoHsieh-Android/android-situation-evidence`(`configs/ast-grep/kotlin-android/check.py:245`)。範圍 6 也要改 `check.py`,計劃只寫了要等 android-lint-ci 合併,沒提這條分支,合併時會有衝突。
引句:「已由 [[Projects/Android寫法語意情境表態與盲判_計劃]] 實作(`check.py` 的 `dt_sources`:決策表一列的「對應檢查」到主表找來源欄」

F5
severity: minor
blocking: 否
推送前擋下的標題與收尾提示會講錯話。計劃沒提 `_spec_gate_push_bad_head` 與收尾那行。我實跑,依據來源不合時印出「1 份風險低計劃沒過(風險低不派審,推送閘是它唯一的閘)」,收尾還叫人「把條款的測試做綠再推」,但該計劃是風險高、問題是缺節。實作要補一個標籤分支。
引句:「這樣實作中或審查輪才冒出來的機制,只要寫進計劃時漏了出處,推送前會被擋;規格閘過了之後整節被刪也擋得到。」

F6
severity: minor
blocking: 否
使用者原話的格式,repo 現有寫法會被誤擋。我拿 `推送只跑受影響測試_計劃` 預期值表的來源格試判,「使用者 2026-11-05「是不是可以…」」(日期後沒有冒號)判不合格。用詞段只收「使用者 YYYY-MM-DD:」。另外全形冒號「:」實跑也不合格。
引句:「④使用者原話:「使用者 YYYY-MM-DD:」後面接引號且引號內至少 4 個實字(用現成的 `_real_chars` 算)」

F7
severity: minor
blocking: 否
健檢範圍 3 判新舊要逐篇呼叫 `_plan_effective_day`,每篇跑 2 到 3 次 git。我實測 185 篇 todo/doing 計劃共 19.9 秒,其中 4 篇判新。計劃沒提短路(例如 `created` 已不早於生效日就直接判新,不再查 git),健檢會多出約 20 秒。
引句:「`lumos doctor` 對〈用詞〉定義的「計劃(健檢範圍)」裡、判成新計劃、而且〈依據來源〉不合格的,列名字(最多 20 篇,超過印總數)」

總結:最嚴重是推送前重查漏掉 todo 新計劃、計劃自己過不了自己的預期值表閘、`_refcheck_scan` 抽不到頂層檔與點開頭目錄,會擋 3 條。
