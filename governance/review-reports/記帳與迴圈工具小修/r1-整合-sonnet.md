severity: minor

整合/知識同步鏡頭。spec 的內部交叉引用都核對過(S1–S25、d1/d2、〈不做〉、〈回退〉),都對得上。程式現況的宣稱我開 `scripts/lumos`、`scripts/test_lumos.py`、`skills/` 查過,大致屬實,有出入的記在下面。已查證屬實的有:
- 真帳的 147/144/2/1,我用腳本重數,一致。
- `cmd_loop_next` 的 `seq` 判法。
- 範本旗標函式 `_tpl_flags` 對 `seq` 省略 `--round`。
- SKILL 第 12、29 行的引用位置。
- 設計審 SKILL 第 20 行在步驟 1。
- 步驟 2 的前掃四項,以及 refcheck、prose-lint、`pitfalls --check`。
- 派工單的單席與多席兩種形狀。

## 1. 同一句「standard 走循序」散在 spec 沒列的處所
severity: minor
blocking: 否(照 spec 做不會做出壞系統,只是三個月後的接手者讀到舊說法,第一筆記帳被新規則擋下,訊息會指路)
引句:「真帳 144/147 個 standard 代碼審早就帶輪次,等於已經在範圍內,實際行為不變」

- 位置:〈10 手冊與筆記同步〉只改 `skills/lumos-code-loop/SKILL.md` 第 12、29 行與步驟 2、6。驗收條款 S25 也只驗這一支檔的第 1 節。
- 問題:同一個說法還在別處,改完會互相矛盾。
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 第 5 行寫「standard 走循序審(單源 `lumos-code-loop/SKILL.md`)」,第 41 行寫「單席循序與多席」。
  - `skills/lumos-code-loop/reference.md` 第 259 行(「護欄」現行段)寫「錨定 standard 的循序 3 筆」。第 438、611 行在舊版段,不是現行說明。
  - 「(多席帶輪次的迴圈;循序單審、light、舊迴圈不記)」這句,在 SKILL.md 第 66 行、`reference.md` 第 259/634 行、`commands/05-設計審查迴圈.md` 第 33 行、`lumos-design-loop` 的 SKILL.md 第 66 行與 `reference.md` 第 332/542 行都有。新規則之後,新 standard 代碼審是「一位審查員、每筆帶輪次」,工具實際走跑滿提示與回顧。依程式,這兩個功能的範圍是「每列都帶輪次」。
  - `Systems/loop-convergence-recording.md` 第 34 行有同樣的「循序單審不印」。
- 具體例:接手者讀到 `commands/06` 說 standard 循序,就去記一筆不帶 `--round` 的帳。新規則第一筆就 rc2。同一個人讀到「循序單審不記跑滿回顧」,就會漏掉新 standard 迴圈到上限時工具要求的回顧。
- 補充:`Systems/代碼審修正關卡.md` 第 19/20 行記著 `--regression-set` 的語意。d2 把它限縮成只收代碼審,但這篇不在 `lands_in`。
- 補充:「載體最後記」目前只記在 `Projects/代碼審minor解綁_計劃.md`,沒有任何 Systems 筆記。〈10〉要加提示與 S22,卻沒說這條規則寫進哪一篇 Systems,接手者從 Systems 找不到它。
- 佐證:`grep` 循序,分別落在上述各檔的行號;`scripts/lumos` 第 11054 行起的 `_cap_hint_scope` 註解寫「每一列都帶輪次(循序單審與 light 不帶)」。
- 建議補的:〈10〉加一條「全 repo 同步掃一遍並列出處所」,S25 改成涵蓋 `commands/06`、`reference.md` 護欄、上面那句限定語;`lands_in` 補 `Systems/代碼審修正關卡`,並指定「載體最後記」寫進 `Systems/loop-convergence-recording`。

## 2. 「跟載體最後記共用同一次讀帳」與程式現況不符
severity: minor
blocking: 否(實作者照字面放進那段 if 會讓 S5 測不到,測試會紅,不會把壞系統放出去)
引句:「效能:寫側只多用既有那一次讀帳」

- 位置:〈1〉`canary record` 寫側那條,以及〈實務隱患〉效能那條。
- 問題:既有的「載體最後記」讀帳整段包在 `if loop and round_id and outcome is None:`(`scripts/lumos` 第 11847 行起)。輪次規則最主要要擋的就是「這筆沒帶 `--round`」,這時 `round_id` 是 None,整段不執行,沒有讀帳可共用。
- 具體例:S5 是既有都帶輪次、這筆不帶 `--round`。照字面把檢查放在那一段後面,這筆走不進去,根本不會擋。
- 佐證:`scripts/lumos` 第 11847 行的條件。
- 修法:spec 要寫成「輪次檢查獨立讀一次帳,或把讀帳提到那個 if 外面」,並把「不多讀一次」從效能論述拿掉,或限定成「帶 `--round` 時共用」。

## 3. 名冊 mode 改名牽到一支既有測試,spec 的測試子集沒列
severity: minor
blocking: 否(測試紅了實作者會看到)
引句:「防改壞循序相容與 loop next」

- 位置:〈1〉「名冊表 `("code","standard")` 的 `mode` 標籤改成 `single` … 只影響 `--json` 的 roster 描述字串」。
- 問題:`scripts/lumos` 沒有任何讀者讀 `mode`(只有一處 `"sequential"` 字面)。但 `scripts/test_lumos.py` 第 41014 行的 `t_tier_roster_table` 斷言 `mode == "sequential"`,斷言訊息寫著「循序 tier 錨定案 supersede v1 範圍釘」。
- 具體例:改成 `single` 後這支測試紅。〈實作時要跑的子集〉沒有 `-k tier_roster`、`-k loop_next_roster`,只靠推送前整套閘發現。
- 佐證:`scripts/test_lumos.py` 第 41014 行。
- 修法:子集清單補這兩個 `-k`,並寫明該斷言要隨 d1 改。這屬於「測試期望跟著新決策改」,不是放寬規則。

## 已讀,無 finding 的範圍
- 〈2〉集合 `none`、〈3〉regression-set、〈4〉表態型別、〈5〉留痕提醒、〈6〉pitfalls、〈7〉拆包、〈8〉資安提示、〈9〉設計審順序、〈回退〉、〈合約候選〉。
  - 〈8〉說「判定輪常是只派一席的 delta 輪」,與 `_disposal_security_step` 的 docstring 一致。
  - 〈6〉說「名冊沒有的字樣不新造」可行:`_REQUIREMENT_LABEL.get(requirement, requirement)` 有退回原值,不會缺字樣。

## 風險類
- 守衛面:會碰,spec 自己已列,且有 S2、S10 釘住誤擋面。
- 舊帳相容:不溯及,有 S2。
- 已在途分支:沒有在途分支需要重新表態。
- 跟其他會談或計劃的交界:`Projects/循序codeloop-tier錨定_計劃.md` 是 status done,沒有 decisions 欄,spec 〈1〉已「回應既有決策」,無矛盾。

最嚴重 severity:minor。blocking 共 0 條。
