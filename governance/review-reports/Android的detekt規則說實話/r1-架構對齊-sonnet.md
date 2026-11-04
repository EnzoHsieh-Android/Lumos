severity: minor

這份設計大致沿用鄰居的做法,沒有引入第二套。有三處跟鄰居不一致,都是結構對、細節有出入,屬 minor。有四處規格沒寫,我標 ⚠,不算不對齊。

**1. 分層與依賴方向:對齊**
- 設計寫「判定表寫成一支函式,lint-check 與健檢 F 段共用」。
  引句:「判定表寫成一支函式,lint-check 與健檢 F 段共用(不留兩份)。」
  這跟既有的 `_lint_load_and_validate` 同形:模組層級的純函式,由 `cmd_lint_check` 與 doctor F 段兩邊呼叫。
  file: `scripts/lumos:37714`、`scripts/lumos:37758`、`scripts/lumos:4093`
- 判定的輸入用 `_lf["config"]`,也就是既有載入函式已經讀好的設定,不重讀檔。
  `parse_error` 時不判,跟 F 段 elif 鏈、以及 lint-check 的 rc2 路徑一致。
  file: `scripts/lumos:37732`、`scripts/lumos:4118`、`scripts/lumos:37770`
- 逐項防型別的寫法,跟 smoke 迴圈的 `cmds if isinstance(cmds, list) else []` 同一個樣子。
  file: `scripts/lumos:37780`
- ⚠ 函式放哪、叫什麼,設計沒寫。S1 只說函式回傳「提醒代號集合」。
  兩個呼叫端都要印中文提醒,代號對應文字的那張表放哪裡沒講。
  鄰居的做法是文字由驗證函式一起產出(`_lintcheck_validate` 回的 issue 字串)。
  如果實作成「函式回代號、兩邊各自配文字」,會留下兩份文字。
  file: `scripts/lumos:37689`、`scripts/lumos:37803`

**2. 命名、錯誤處理、輸出方式:大致對齊,有兩條不一致**
- 對齊的部分:
  - 健檢 F 段用 `warn([], head, advice)`,是既有「有 eslint 設定沒接」那則的同一個形狀。
    空清單算一段提醒、不計 issues,`--ci` 退出碼不變。
    file: `scripts/lumos:4101`、`scripts/lumos:2045-2056`
  - 不寫入 `gov_events`,跟 `_lint_hits` 那條一致。
  - `--json` 只輸出一個物件,欄位 `advisories`(小寫英文、字串清單)跟 `problems`、`declared` 命名風格一致。
    沒宣告那條路徑不動,跟既有行為一致。
    file: `scripts/lumos:37773`、`scripts/lumos:37801`
  - 拆詞失敗整條不判,跟 `_own_hook_interpreter` 的 `try split / except ValueError → None` 同款。
    file: `scripts/lumos:35462-35466`
- 不對齊 A:設計寫「lint-check:人讀輸出在既有結果之後印提醒,健康與有問題兩條分支都印」,沒寫文字形狀。
  引句:「人讀輸出在既有結果之後印提醒,健康與有問題兩條分支都印」
  鄰居 `skipped_stacks` 那則是固定的三段:「提醒:…」、「為什麼在意:…」、指令獨立一行。
  這是專案長期標準「發生什麼→為何在意→指令獨立一行」。
  設計的提醒(尤其是 T1、P1 這種「目前沒有現成修法」)沒指定要走這個形狀。
  file: `scripts/lumos:37789-37794`
severity: minor
  blocking: 否
- 不對齊 B:新判定函式要提到 `{LINT_FILES}`(P1、P2 的條件),但設計沒提到既有守衛。
  `t_lint_files_substitution_has_one_implementation` 用白名單 `ALLOWED` 限制哪些函式能碰這個佔位符。
  名單外的函式一提到它就紅。
  現有的「推送閘接不接得住」判斷,是各處行內寫 `_LINT_NEW_FILES_TOKEN not in cmd`,每處都已列進白名單。
  新函式要嘛加進白名單並寫理由,要嘛改成不碰字面。設計兩者都沒寫,實作時會先紅一次。
  file: `scripts/test_lumos.py:17108`、`scripts/test_lumos.py:17148-17155`、`scripts/lumos:38889`、`scripts/lumos:58862`
severity: minor
  blocking: 否
- ⚠ 外來字串回顯:設計沒寫提醒會不會帶出命令片段、Gradle 任務名或副檔名。
  如果會帶,要走既有清洗,例如 `_esc_clean` 或 `_plan_quote`。
  鄰居 `{ready[:60]}` 是直接回顯命令,沒清洗,但那是舊寫法,不當對照。
  file: `scripts/lumos:19351`、`scripts/lumos:19360`、`scripts/lumos:37772`
- ⚠ 一條命令中好幾個代號時,F 段是每個代號各呼叫一次 `warn([])`,還是整段合成一次,設計沒寫。
  選前者的話,「提醒段數」會被灌得很大。
  設計只說「結尾提醒段數會多算一段」。

**3. 第二種做法:沒有引入第二套,但有一處值得提醒**
- 我 grep 過 `detekt`、`gradlew`、`shlex`、`punctuation_chars`,`scripts/lumos` 裡沒有「認出某條 lint 命令是哪個工具」的函式。
  `detekt` 只出現在文字說明與註解,`gradlew` 只出現在測試命令樣板和基礎設施關鍵字的正則裡,兩者都不是同一種判定。
  `_linter_config_hits` 是看根目錄設定檔名,輸入不同,不重疊。
  所以這張判定表是第一份,不是第二份。
  file: `scripts/lumos:4117`、`scripts/lumos:32615`、`scripts/lumos:36916`
- 拆詞用 shlex,跟既有 `_shlex.split` 同一個函式庫。
  設計寫「posix 模式、標點拆開」,即 `punctuation_chars=True` 的 `shlex.shlex`,和既有的純 `split(cmd)` 用法不同。
  這是同庫的另一種模式,不算第二套。
  但「去環境變數、去 env/exec/time 等包裝詞、`sh -c` 遞迴」是專案原本沒有的小型命令解析。
  只有設計自己的判定表在用,沒有第二處重複實作。
  file: `scripts/lumos:35462-35466`
- 「這條命令推送閘接不接得住」(P1 的條件)是既有概念,三處行內判斷、其中一處是 `c["_push_gate_covers"]`。
  P1 是第四處,判斷式相同。
  這是既有的慣例,不是新做法。
  file: `scripts/lumos:38889`、`scripts/lumos:58862`
- 這題沒有 major。

**4. 落點:主體合理,有一處漏列**
- 程式放進 `Systems/lint-declaration-health`:它的 `about_code` 是 `scripts/lumos`,F 段與 lint-check 的設計本來就寫在這篇。合理。
- 共用設定補開兩條規則放進 `Systems/linter精選目錄`:它的 `about_code` 正好是 `configs/detekt/android.yml`,而且 detekt 的接法樣板也在這篇。合理。
  file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md`(frontmatter `about_code`)
- 不對齊 C:設計的「知識同步」逐處列出要改的現況描述,其中 `Systems/效能檢核目錄` 的四列要重寫。
  這是 Systems 節點,但 `lands_in` 沒列它,只列了兩篇。
  引句:「[[Systems/效能檢核目錄]] 協程 scope、結構化並發、大集合、primitive array 四列:「共用 config 已開」改成「已開,要型別資訊才跑;推送時不擋」」
  按全域慣例,現況落在哪幾篇就要列進 `lands_in`。
  相較之下,同批的姊妹案 `Android的detekt推送前真的擋_計劃` 只列了一篇,範圍單純,所以不構成對照。
  `skills/kotlin-idioms/SKILL.md` 是文件檔,家是別的節點,但設計也沒寫它落哪篇。
severity: minor
  blocking: 否

不對齊共 3 條,其中 major 0 條。

另有 ⚠ 判不準 4 條:代號文字放哪、外來字串回顯、F 段每代號是否各呼叫一次 `warn([])`、`kotlin-idioms` 的落點。這四條都是設計沒寫,不是已知不對齊,所以沒算進上面的條數。
