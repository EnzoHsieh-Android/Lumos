severity: major

兩項核對:`push-preview` 的本機寫入(finding 2)我沒真跑預演,依據是 `_gate_event` 的程式與工作目錄 `git status` 裡 `docs/.governance-log.jsonl` 帶 M;舊版工具不認 `--collect` 的 rc=2 路徑(finding 3)是讀 `scripts/hooks/pre-push` 的碼推得,沒實跑。bash 3.2 的空陣列行為(finding 6)我在 `/bin/bash` 3.2.57 實測過。已讀前掃折掉的 10 處,不重報。

**1. 預演靠一個環境變數,真推送時帶著它就等於跳過全套測試**
severity: major
blocking: 是 — S6 要求「擋下不可變放行」,這條路卻讓「該跑的全套測試沒跑」變成 `exit 0`,而且不留帳。
- spec 段落:做法 5。
- 引句:「掛鉤看到它,到統一判斷那一步就停」
- 問題:掛鉤只靠 `LUMOS_PUSH_PREVIEW=1` 判斷是不是預演。這個變數可以寫進 shell rc、CI 環境或 `.envrc`。
- 失敗情境:它被 export 之後,每次真的 `git push` 都在統一判斷點 `exit 0`,全套測試與自主迴圈測試完全不跑。其他逃生閥(`LUMOS_SKIP_DRIFT_CHECK` 等)都會留帳,這個不會。
- 掛鉤現況:file: `scripts/hooks/pre-push:563-587` 是測試前的位置。spec 沒要求預演模式留帳、也沒要求掛鉤分辨自己是不是被 `lumos push-preview` 叫起來的。

**2. 預演會寫入版控中的治理帳與逃逸帳,每預演一次工作目錄就髒一次**
severity: major
blocking: 是 — spec 把預演寫成零副作用(「不推送、不跑測試」),但實作會改版控檔,而且污染 RETIRE-IF 要量的數字。
- spec 段落:做法 5、實務隱患「已排除:對外送出」。
- 引句:「已排除:對外送出:預演不推送;只有真推送才連遠端,行為照舊。」
- 問題:預演照跑 `code-loop check`、`drift check` 等閘,這些閘擋人時都會落帳,預演沒有關掉的辦法。
  - file: `scripts/lumos:1495-1555` 的 `_gate_event` 寫入 `docs/.governance-log.jsonl`,這是版控內的檔。
  - file: `scripts/hooks/pre-push:464-465` 與 `:470` 會呼叫 `loop escape --auto`,擋下時記逃逸帳。
- 失敗情境:
  - 使用者預演兩次,工作目錄多出未提交的帳檔改動。我這次工作目錄一開始 `git status` 就有這個檔帶 M。
  - 預演擋下的算成「推送閘擋下」的逃逸,假造 loop 統計。
  - 預演的擋下算進 RETIRE-IF 的「被擋的推送」。
- spec 沒寫預演模式是否抑制寫帳,也沒寫 `LUMOS_PUSH_ATTEMPT` 怎麼標記預演。

**3. 掛鉤與 lumos 版本錯位時,收集模式會把擋下默默變成放行**
severity: major
blocking: 是 — 掛鉤已有「部分更新」的先例,新旗標沒有探測,直接違反 S6。
- spec 段落:做法 4、做法 5。
- 引句:「掛鉤呼叫時帶上 `--collect`。」
- 問題一(新掛鉤配舊 lumos):舊 lumos 的 argparse 不認 `--collect`,回 rc=2。
  - file: `scripts/hooks/pre-push:482` 附近註解寫明 `rc≠0/1:fail-open 放行`。
  - 後果:code-loop check 整道(含 tier=high 缺留痕、合約測試紅)靜默放行,而這道在今天會擋。
  - 對照:file: `scripts/hooks/pre-push:534-535` 與 `:640-644` 都為「舊版工具不認新旗標」做過探測。spec 沒要求同樣處理。
- 問題二(舊掛鉤配新 lumos):消費專案被 vendor 進去的舊掛鉤不認得 `LUMOS_PUSH_PREVIEW`,`lumos push-preview` 會讓它完整跑 8 分鐘全套測試,違反 S5「不應跑任何測試」。spec 沒寫 `push-preview` 要先探掛鉤是否支援預演。

**4. 「時間」一節的數字不成立,收集模式會多跑最長 300 秒的新增告警閘**
severity: major
blocking: 是 — 實務隱患答案是錯的,而且沒有總時限。
- spec 段落:實務隱患「時間」、做法 4。
- 引句:「多跑的只有本來就要跑的便宜閘(全部約十幾秒、漂移最壞每個分支 60 秒)」
- 問題:`code-loop check` 現在是早退序列,表態一擋就不會往下跑新增告警閘。
  - file: `scripts/lumos:51159-51166` 與 `:29237`:`lint_new` 預算 `budget_sec: 300`,會真的跑專案的 linter 命令。
- 失敗情境:S4 的例子「表態不完整且有新增告警」,collect 模式下表態擋了還要多跑最多 300 秒的 linter。一次推多個 ref 時每個 ref 各算一次。「約十幾秒」的上限被推翻。
- spec 沒給收集模式的總預算或逾時行為。

**5. 統一判斷點的位置寫錯,照字面做會漏掉兩個暫存檔**
severity: major
blocking: 是 — 指到的行不是意圖的位置,照字面做會違反全域的暫存清理規則。
- spec 段落:做法 2。
- 引句:「掛鉤現在第 586 行那一步之前」
- 問題:file: `scripts/hooks/pre-push:586` 是 mktemp 失敗分支裡的 `exit 1`。建 log 檔的 `mktemp` 在 `:571-572`。實作者若真的插在 586 之前,就在 mktemp 之後。
- 失敗情境:
  - `_AUTOLOOP_LOG`、`_TESTS_LOG` 用 `mktemp "${TMPDIR:-/tmp}/lumos-prepush-…"` 建立,不在 `$_PP_TMP` 底下,EXIT trap 清不到。
  - 每被擋一次就在 `$TMPDIR` 留下兩個空檔(`:230` 的 trap 只收 `$_PP_TMP`)。
- 另一個問題:spec 引行號,專案的筆記形狀擋禁止新寫的程式行號引用。這份要落成計劃筆記,提交時可能被擋(⚠ 我沒確認「第 N 行」的中文寫法會不會被該規則抓到)。

**6. `push-preview` 的邊界全沒定義,實作者要猜**
severity: major
blocking: 是 — 派工要求問「每一步實作者不用猜嗎」,以下每條都得猜。
- spec 段落:做法 5、S5。
- 引句:「沒有追蹤就用主線所在的遠端、同名分支」
- 問題與失敗情境:
  - detached HEAD:「目前分支」不存在,未定義。
  - 沒有任何遠端:未定義。
  - 遠端名不是 origin:這個 repo 自己的遠端就叫 `Lumos`(`git remote -v` 實查)。「主線所在的遠端」怎麼找,spec 沒說。
  - 掛鉤第 1 個參數:`_PP_REMOTE` 取自 `$1`(file: `scripts/hooks/pre-push:78`),drift check 與 reread-check 都靠它。預演要傳什麼,spec 沒寫。
  - 怎麼判斷遠端有沒有這個分支:`git ls-remote` 要連網,與「預演不連遠端」的說法衝突;用本機 remote-tracking ref 則可能過時。spec 沒選。
  - 「遠端查不到」時遠端提交填全零:這會讓 `pp_block_range_for` 改問 `push-range`,與遠端分支存在但本機沒有那個物件時走的路不同,spec 沒區分。
  - 工作目錄有未提交改動:`:284` 的簽名檔未提交檢查與 `doctor` 看工作目錄、其他閘看提交,預演結果可能與真推送對不上。spec 沒說要不要提醒。
  - 掛鉤檔的位置:來源 repo 是 `scripts/hooks/pre-push`,消費專案由 `core.hooksPath` 決定。spec 沒說怎麼找。
  - 回傳碼:「有擋下回 1」與「前提壞掉」共用 1,工具自己出錯時回什麼沒寫,呼叫者分不出「被擋」與「預演沒跑成」。

**7. `code-loop check --collect` 的輸出契約有矛盾與缺口**
severity: minor
blocking: 否 — 屬於測試寫得出但要猜的細節,不改變閘的擋與放。
- spec 段落:做法 4、S4。
- 引句:「每道擋下各印各的訊息(原本的擋下句一字不改)」
- 問題與失敗情境:
  - `reason_kind` 缺一個:file: `scripts/lumos:51065` 附近,合約測試紅的 verdict 沒有 `reason_kind`(只有 dispositions、lint_new、review 有)。spec 要求 `blocks` 每筆有 `reason_kind`,合約測試那筆叫什麼沒定。
  - `tier` 欄位矛盾:該 verdict 的 `tier` 是 `"unknown"`,而 spec 又要求先紅時照樣算風險分級。「`tier` 欄位照舊」是舊值還是新算的,沒寫。
  - 印出的話與一字不改衝突:file: `scripts/lumos:51677-51679` 在表態被擋時印「合約測試也紅了——低風險只提醒不擋」。collect 模式下合約測試紅本身就是硬擋,這句就成了謊話,spec 沒處理。
  - 治理帳筆數沒定:`_gate_event_or_warn(... hard=True)` 擋下時是記一筆還是每個原因一筆,spec 沒寫。
  - 摘要拿不到原因:掛鉤是用 `2>&1` 抓整段文字,不帶 `--json`。新增的 `blocks` 清單掛鉤根本沒讀,摘要要的「一句原因」從哪來,沒寫。

**8. 彙總格式與 `pp_record_block` 的實作細節沒定**
severity: minor
blocking: 否 — 實作者選一種做法即可,但測試沒有鎖,可能留下潛在崩潰。
- spec 段落:做法 1、做法 2。
- 引句:「累積在 `_PP_BLOCKS` 陣列」
- 問題與失敗情境:
  - 欄位編碼未定:三個欄位(閘名、ref、原因)放進同一個陣列元素,要選分隔字元。git ref 名可含 `|`,code-loop 的原因文字也可能含換行或長字串,選錯就切壞。spec 只說「一句」,沒說超長、含換行或 shell 特殊字元怎麼處理(應用 `printf '%s'` 與三個平行陣列)。
  - bash 3.2 空陣列:掛鉤有 `set -u`(`:15`),macOS 內建 bash 3.2.57 實測 `for x in "${A[@]}"` 對空陣列報 unbound variable。掛鉤內已有 `${_PP_LINES+"${_PP_LINES[@]}"}` 的慣例,spec 沒提醒。若實作者先迴圈再判斷,最常見的「無擋下」路徑會直接崩。
  - 「ref(多 ref 時)」:以「有幾行 stdin」還是「ref 欄是否非空」判斷,沒定。
  - 只推刪除、推 tag:迴圈對刪除 `continue`(`:348`),tag 不跑 `code-loop check`,spec 沒說這兩種的彙總長什麼樣。

**9. 後面的閘會受前面失敗連累,RETIRE-IF 因而無法被當作證據**
severity: minor
blocking: 否 — 設計取捨,但撤除條件的度量沒定義來源。
- spec 段落:緣起、RETIRE-IF。
- 引句:「上線 8 週內,被擋的推送裡」
- 問題:
  - 連累:`doctor --ci` 有壞連結時,依賴圖譜索引的 `home check`、`spec-gate --push-check`、`reread-check` 可能連帶擋下或 rc=2。連帶出來的第二、三筆會被記成獨立的一道,把「兩個以上原因」的次數灌大。
  - 只對裁判簽名那一道加了警語,對 doctor 失敗造成的連累沒有。
  - 度量來源:彙總沒要求落任何帳或事件,所謂「次數」要從哪裡量沒寫。⚠ 若靠現有 `_gate_event` 的 hard 事件加 attempt_id 去分組,不是每道閘都有落事件,我沒逐道確認。

**10. 驗收條款的可執行性**
severity: minor
blocking: 否 — 測試做得出來,但現成範本做不到 S1 之外的閘,且部分條款不會先紅。
- spec 段落:S1–S6。
- 引句:「當兩道彼此獨立的便宜閘同時擋下」
- 問題與失敗情境:
  - 範本只能走兩道:file: `scripts/test_lumos.py:18885` 起的 `t_prepush_cheap_gates_run_before_expensive_suite` 用 `refs/heads/main dummy refs/heads/main dummy` 當輸入。`dummy` 不是真的 git 物件,迴圈內 `home check`、`note-shape`、`code-loop`、`drift`、`reread` 都走 fail-open 或不擋。S1 只能用「迴圈外」的 doctor 加簽名檔未提交,測不到「同一道被多個 ref 擋下各記一筆」,而這一句是做法 1 的核心行為。
  - 假 repo 搭建:簽名檔未提交要靠一份能讓 `anchor verify` 通過、再被修改的 `governance/anchor-baseline.json`。範本沒有,spec 沒給做法。
  - 不會先紅:S3(找不到 Python 3.14 立刻結束)與 S2 的「沒有擋下就跑到全套」,今天的掛鉤就已經成立,測試一開始就是綠的,守不到改動。S6 只寫「拿兩道真的閘驗」,沒有覆蓋 code-loop 內部 rc 轉成記錄這條新路徑。
  - 缺的邊界測試:沒有條款涵蓋 push-preview 在 detached HEAD、沒有遠端、遠端名不是 origin 的行為,也沒有涵蓋刪除遠端分支(local_sha 全零)與 tag。

**各節結論**
- 緣起、舊裁定、PRIOR-ART、回退:已讀,無 finding。
- 實務隱患「金流、不可逆」:已讀,無 finding。
- 做法 3(前提壞掉的照舊立刻停):已讀,無 finding。我核對過掛鉤的 `exit 1`/`exit 0` 清單(`:228`、`:253`、`:586`、`:616`、`:733`),與前掃的分類一致。

固定席節點:派工尾端沒有附。

最嚴重 severity:major;blocking 共 5 條(finding 1、2、3、4、5、6 中 blocking 為「是」的共 6 條,實為 1、2、3、4、5、6 全是「是」)。

更正總結:blocking 為「是」的共 6 條(finding 1 至 6),minor 共 4 條(finding 7 至 10)。
