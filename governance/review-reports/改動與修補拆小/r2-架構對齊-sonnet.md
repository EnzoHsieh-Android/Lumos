severity: major

我檢查的是 `/tmp/改動與修補拆小-r2.md` 對照 repo `Word-wild-search-rst`。

## 問 1:提示放在 `loop next` 合不合職責

結構上合。提示放在 `loop next` 沒問題,但它和 `loop next` 現有的大小與拆案提示沒有互相對齊,見 finding 1。

- 在 `loop next` 加只附加、不改 phase 與 rc 的提示,是現有做法。例子有 `cap_hint`、`fix_check`、`related_nodes`、`scope_cap`、`cluster_hint`。
  - file: `scripts/lumos:15632`(`cap_hint`)
  - file: `scripts/lumos:15642`(`fix_check`,同樣用 `startswith("code-")` 限定代碼審)
  - file: `scripts/lumos:15601`(`related_nodes`,首輪)
- 首輪才印的條件 `n_next == 1` 也有先例。
  - file: `scripts/lumos:15592`
  - file: `scripts/lumos:15601`

**finding 1(不對齊)**:`loop next` 已經有兩套「改動太大就拆」的提示,計劃一個都沒提到。
severity: major
blocking: 是
引句:「程式加測試超過 300 行時,再印一行:「改動越大越容易跑滿三輪」
- 現況一:`scope_cap` 以 `wc -l` 為量尺、門檻 1800 行,每輪都印。它的文字寫著「本專案自己跑過三次對照實驗都量不到這個效應,所以別拿自家資料當佐證」。
  - file: `scripts/lumos:15573`(`scope_cap`)
  - file: `scripts/lumos:13271`(`_CANARY_SCOPE_SOFT_CAP_LINES = 1800`)
  - file: `skills/lumos-code-loop/reference.md:234`
- 現況二:`_cap_hint_lines` 有「換做法:拆小改動」和「熔斷:建議拆小改動」,以折入條數為量尺。
  - file: `scripts/lumos:10356`
- 照字面做,同一次輸出會並列三條拆案建議,量尺各不相同:300 新增行、1800 行、折入數。
- 其中一條又引用自家帳本回放當依據,而 `scope_cap` 那條明說自家資料量不到規模效應。
- 計劃的 PRIOR-ART 與 RETIRE-IF 都沒交代這三者的關係。
- 該怎麼改:先說明新提示與 `scope_cap`、`cap_hint` 的分工。至少要改掉 `scope_cap` 那句與新提示互相矛盾的措辭,或把新提示併進同一個欄位和措辭。⚠ 嚴重度我判不準,我標 major 是因為「兩套互相打架的拆案提示」算第二種做法。

## 問 2:新增行掛在 `_patch_file_changes` 上,還是該沿用別的數法

掛在 `_patch_file_changes` 本身站得住。專案裡其他的數法都不能直接重用:
- `_diff_added_lines` 只認 `+++ b/`,不處理引號路徑和改名。它遇到以 `+++` 開頭的內容行會跳過,也就是 S4 要避開的那個錯。
  - file: `scripts/lumos:29423`
- `_sc_changed_files` 的 numstat 要一個 git 範圍,不能對凍結 patch 檔用。
  - file: `scripts/lumos:8913`
- `scope_lines` 是人填的 `wc -l`。
  - file: `scripts/lumos:10668`

**finding 2(不對齊)**:「其餘算程式」另立了一個和專案不同的程式檔定義。
severity: major
blocking: 是
引句:「再看是不是測試(`_nodehome_is_test`);其餘算程式」
- 專案裡「算程式」的定義是 `_is_code_file`。它排除 `docs/*` 這類豁免路徑、測試檔、`.lumos/config` 的 ignore,再用副檔名或 shebang 判斷。
  - file: `scripts/lumos:8876`
- 小改動閘明確寫過「文件/圖/資料只在相對量那一維度算」,因為 2026-09-18 發生過 README 加圖把目錄數撐破。
  - file: `scripts/lumos:8960`(`_sc_diffusion` 的註解)
- 計劃的「其餘」會把 `SKILL.md`、`reference.md`、json、圖片也算成「程式 a」。
- 這樣門檻 300、100 會被文件灌水,提示會誤報。
- 該怎麼改:程式檔改用 `_is_code_file(rr, path, base)`;不是程式也不是測試也不是筆記的,另歸「其他」,不計入門檻。

**finding 3(不對齊)**:簿記判斷沿用常數,但專案已經有寫過同一個條件的地方,計劃沒說為什麼不抽共用的。
severity: minor
blocking: 否
引句:「簿記判斷沿用 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`,不另寫第二套。」
- `f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS)` 這個條件已經散在至少四處。
  - file: `scripts/lumos:45420`
  - file: `scripts/lumos:45824`
  - file: `scripts/lumos:37636`
  - file: `scripts/lumos:8919`(閉包 `_bk`,還加了 `vrel`)
- 計劃再加一份是第五處,不算引入新做法,但「不另寫第二套」這句話與實作不符。
- 建議實作時只複用常數,不要寫成新的判斷函式。

**finding 4(不對齊)**:`added_out` 是這個函式第一個「輸出參數」,和既有參數的性質不同。
severity: minor
blocking: 否
引句:「`_patch_file_changes` 加 `added_out=None`;給了一個 dict 時」
- 既有的 `headers`、`lf_only`、`hunk_tag` 都只改變指紋怎麼算,回傳型態不變。
  - file: `scripts/lumos:26681`
- 計劃宣稱的「加參數有先例」成立,但只限於參數形式。
- 結構上仍然對:共用檔頭狀態機,比另寫一份解析好。

**finding 5(不對齊)**:帳本回放用的數法和產品用的不是同一套,但計劃說兩者「同單位」,門檻直接從回放搬來。
severity: minor
blocking: 否
引句:「門檻 300 與 100 取自回放(第一輪大小約在 300 行開始升高;修補新增行數中位數約 100),是起點不是最佳值。」
- 回放腳本用 `difflib.SequenceMatcher` 對整份 patch 的內容行做順序比對。它沒分程式、測試、筆記。
  - file: `docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md:84-144`
- 產品是逐檔、多重集合相減,並且分三類。
- 兩者算出來的數可能不同。計劃保留回放腳本不動,卻拿它的門檻直接當產品門檻。
- 建議驗證筆記補一句口徑差異,或在 S 條款裡加一條「抽樣對照兩種數法差多少」。

## 問 3:手冊與驗證筆記的落點

**finding 6(不對齊)**:`reference.md` 的落點沒指定,而且已有兩個大小相關的段落。
severity: minor
blocking: 否
引句:「`reference.md` 一段說明兩行提示的意思、門檻依據與「只是建議」」
- `reference.md` 已有〈一輪能丟多少:軟上限 1800 行〉。
  - file: `skills/lumos-code-loop/reference.md:231`
- 也有〈修復穩定性試行〉第 1 條「修復若擴成新格式…先重估是否拆案」。
  - file: `skills/lumos-code-loop/reference.md:127`
- 新段應放在軟上限那段旁邊,並互相交叉引用。否則手冊裡會有兩個大小段落、兩組數字,讀者不知道哪個管用。

**finding 7(不對齊)**:SKILL.md 要加半句的位置寫錯了。
severity: minor
blocking: 否
引句:「SKILL.md 第 2 步(`loop next`)那句加半句「首輪與續輪會印改動大小」」
- SKILL.md 第 2 步是「派審查員」。
  - file: `skills/lumos-code-loop/SKILL.md:28`
- `loop next` 的介紹和「首輪會印『主題既有節點』」在「什麼時候用」那條。
  - file: `skills/lumos-code-loop/SKILL.md:14`
- 半句應加在第 14 行,和主題既有節點那句放在一起。

**finding 8(不對齊)**:`lands_in` 選的節點不是 `loop next` 提示的家。
severity: minor
blocking: 否
引句:「lands_in:
  - Systems/pitfalls-code-loop」
- `Systems/pitfalls-code-loop.md` 完全沒有提到 `loop next`。
- `loop next` 提示的既有紀錄在 `Systems/canary-audit.md`(`scope_cap` 與 `scope_oversize`,第 74 行)和 `Systems/design-loop.md`(首輪「主題既有節點」,第 73 行)。
- 改 `scripts/lumos` 的 `cmd_loop_next` 時,筆記應寫進這兩篇之一。
- 驗證筆記的落點(`Verification/…修補大小與下一輪major回放`)本身沒問題。

## 總結

不對齊共 8 條,其中 major 2 條(finding 1、finding 2)。

最嚴重等級是 major,blocking 共 2 條。
