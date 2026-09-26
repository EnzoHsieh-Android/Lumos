severity: major

## F1 rule-gap 改叫 _escape_rows_for 會讓消費專案(standalone 佈局)的逃逸帳從「找得到」變「找不到」
severity: major
blocking: 是——照 spec 字面把 `rule-gap` 從自己開檔讀改成呼叫 `_escape_rows_for`,standalone 佈局的消費專案會從「rule-gap 讀得到帳」退化成「讀不到」,而且撤回也不會生效(因為根本沒讀到帳),跟 S3 要保證的事直接相反。
引句:「逃逸清單(`loop escape --list`)與規則缺口統計(`rule-gap`)自己開檔讀,要改成呼叫它——不然撤回在那兩處看不到。」
file: `scripts/lumos:20223-20226` `cmd_rule_gap` 現在的開檔邏輯:「逃逸帳位置:記帳那支寫在「知識庫的上一層」,標準佈局是 `<repo>/docs/`,但知識庫本身就是 repo 根的那種佈局(standalone)會落在別的地方——兩個都找(r1 通才席)」,接著 `cands = [Path(repo_root) / "docs" / ".escape-log.jsonl", Path(repo_root) / ".escape-log.jsonl"]`,兩個候選路徑都會試。
file: `scripts/lumos:7397-7404` `_escape_rows_for` 只有單一路徑 `log = env.vault.parent / ".escape-log.jsonl"`,沒有任何 standalone 候選邏輯。
file: `scripts/lumos:17792-17795` `_vault_in` 對 standalone vault(如「MOC/ + Systems/」直接在 repo 根)回傳 `d` 本身,即 `env.vault == repo_root`;此時 `env.vault.parent` 是 repo 的**上一層目錄**(repo 外面),不是 `_vault_in` 判準所說的「標準佈局是 repo/docs/」那個位置,也不是 rule-gap 候選 2 的 `repo_root` 本身。
file: `scripts/lumos:23438-23439` 另一處(`delguard`)明文承認同一個現象:「standalone vault(vault 即 repo 根)→ 帳會寫到 repo 外(vault.parent)」,可見 `env.vault.parent` 對 standalone 佈局是已知會算錯位置的路徑,不是本案新引入的推測。
把 rule-gap 改成呼叫 `_escape_rows_for` 之後,standalone 佈局的消費專案(例如核心 repo 自己那種「MOC/+Systems/ 在根目錄」的佈局)會從「兩個候選路徑都試,找得到帳」退化成「只試 `env.vault.parent`,通常找不到帳、或指向錯誤位置」——這不只是沒修好撤回,是把現有能動的 standalone 支援改壞。

## F2 手動記帳的 `--defect-ref` 新規矩沒有同步進三份操作說明,現有指令範例會被新擋下擋住
severity: major
blocking: 是——實作者若只照 spec 改程式、不改文件,使用者/agent 照 skill 給的指令打,會被 S2 的新硬擋擋下(rc2),而三份文件都沒有任何跡象顯示需要跟著改。
引句:「新寫的列至少要有 `sha` 或 `defect_ref` 其中之一。手動記帳兩個都沒有時,要明寫 `--defect-ref none:<為什麼沒有>`,否則擋下。」
file: `skills/lumos-design-loop/SKILL.md:61` 「`lumos loop escape <編號> --stage <實作|code-loop|CI|prod|使用者回報> --severity <minor|major|blocker> --desc <一句>`」——沒有 `--defect-ref`,S2 落地後這句照打會被擋。
file: `skills/lumos-code-loop/SKILL.md:54` 「`lumos loop escape <編號> --stage <站> --severity <s> --desc <一句>`」——同樣缺 `--defect-ref`。
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:27` 「`lumos loop escape <迴圈編號> --stage <實作\|code-loop\|CI\|prod\|使用者回報> --severity <minor\|major\|blocker> --desc <一句>`」——同樣缺 `--defect-ref`。
手動模式目前也沒有 `--sha` 這個入口可用(`--sha` 的 help 寫死「--auto 用」,手動分支的 `rec` 也不組 `sha` 欄——見 `scripts/lumos:30823` 與 `scripts/lumos:9404-9525` 手動記帳段落),所以 S2 落地後手動記帳幾乎每次都要靠 `--defect-ref none:<理由>` 才能過關;三份操作說明目前教的指令形狀完全沒反映這件事,而計劃的「要動什麼」範圍(scripts/lumos 與新條款)也沒提到要同步這三份文件。

## F3 撤回一旦讓 `_escape_rows_for` 濾掉那一列,自動記的去重會把「已撤回」當成「沒發生過」,同一個 sha 重觸發會悄悄補回被撤回的那筆
severity: major
blocking: 是——照 spec 字面「所有讀逃逸帳的地方都要走這支」無差別套用到去重邏輯,會讓撤回這個動作在同 sha 重觸發(例如 CI 對同一個紅色 sha 重跑)時失效,且沒有任何條款或誠實界線提到這個交互作用。
引句:「所有讀逃逸帳的地方都要走這支」
file: `scripts/lumos:9344` `_auto_escape` 的去重集合直接來自 `for r in _escape_rows_for(env): existing.add((nfc(str(r.get("loop", ""))), r.get("stage"), r.get("sha")))`——`_escape_rows_for` 一旦依 S3 濾掉被撤回的列,這個 `existing` 集合就不會再包含被撤回的那一筆。
file: `scripts/lumos:9354-9357` 去重判準是 `if (nfc(loop_id), stage, sha) in existing: ... 不重複`;`existing` 少了被撤回那筆,下次同一 `(loop, stage, sha)` 觸發(CI 對同一個紅 sha 重跑最常見)就不再判定「已記過」,會**重新寫入一筆**跟被撤回那筆內容幾乎相同的新紀錄。
docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md:78 已有的驗收條款 `[S5] 若同一計劃、同階段、同 sha 已有逃逸紀錄,則不應重複寫入`(`test:t_escape_auto_dedup`)是這條去重邏輯的既有合約;本案沒有任何一句話處理「撤回之後 S5 的『已有』該不該把撤回算進去」,而字面上「所有讀逃逸帳的地方都要走這支」把兩者綁在一起,結果是撤回會被同 sha 重觸發悄悄抵銷,而且抵銷的當下沒有任何撤回紀錄以外的痕跡(帳上看起來就是同一列又出現一次)。

## F4 `escape-stats` 借用的 `_plan_for_loop` 沒有 NFC 正規化,跟同檔案已知踩過的坑是同一種
severity: minor
blocking: 否——目前 repo 的 `Projects/*.md` 檔名機械檢查全部是 NFC,沒有實例會踩到;是潛在的統計偏差(rows 被誤歸「未分類」),不會做錯決定或做出壞系統,只在特定平台/檔名正規化情境下發生。
引句:「範圍類:用 `_plan_for_loop` 找到的計劃的 `scope/<類>` 標籤」
file: `scripts/lumos:9293-9298` `_plan_for_loop` 用 `(env.vault / "Projects" / cand).is_file()` 直接比對檔名,沒有做任何正規化。
file: `scripts/lumos:9284-9292` 緊鄰的姊妹函式 `_plan_file_exists` 特地加了 NFC 正規化並註明原因:「計劃檔存在性,兩邊都做 NFC 再比(r1 邊界席:git 回的路徑與磁碟檔名的正規化形式可能不同)」——同一個檔案裡已經記錄過這類問題發生過,`_plan_for_loop` 卻沒有補這道防線。
`escape-stats` 若在 NFD 正規化的檔案系統(例如 macOS 對中文檔名的預設行為)或消費專案上跑,遇到迴圈編號對應的計劃檔名正規化形式不同,`_plan_for_loop` 會回 None,該迴圈的範圍類統計會被錯歸進「未分類」——跟 S7 條款要求的「計劃有兩個範圍類標籤時應兩類各算一次」不衝突,但會系統性低估某些類別的放行數,而樣本量本來就小(門檻 20 筆),這類偏差在小樣本下影響不小。

已看,無:
- 條款 [S1] 的分類三規則(代碼審自動記歸 design、`code-` 開頭歸 code、其餘依審查帳判 design/plan)跟現有資料吻合——`docs/.escape-log.jsonl` 裡確實有 `loop` 欄位字面以 `code-` 開頭且 `source` 為 None 的手動列(如 `code-enforcement-obs`、`code-每支檔有家`),證明規則 2 有真實資料可套用,不是死規則;代碼審自動記的列(`source: "code-loop"`)`loop` 欄則已經是去掉 `code-` 前綴後的名字,規則 1 的特判(檢查 `source=="code-loop"`)是可行的推斷依據,新舊列都能靠同一支函式推回同樣結果。對照 `docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md` 已定死的語意(「代碼審記到 major 時自動記的逃逸……歸給設計審迴圈」),沒有衝突。
- 「下一站接住」清單只列「實作、code-loop、push-gate」三個站名,不含 `push-gate-unreviewed`,這是精確比對(不是前綴比對)才對:`push-gate-unreviewed` 這一路本身就是「風險低計劃被判錯、下游擋下」的訊號(`docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md` 明寫這是「門判錯的訊號」),理當算漏網、不能算「下一站接住」,跟 `scripts/lumos:6383` 的 `push-gate`(受波及合約測試沒過,才是真的被下一站攔下)語意不同,目前的兩個站名字串（`push-gate` / `push-gate-unreviewed`）在程式碼裡是分開的,只要實作用精確字串比對就不會混淆。
- S2 的 `sha`/`defect_ref` 二選一要求跟 `逃逸自動記_計劃` 既有的歸因守衛放寬(「迴圈在審查帳 OR 計劃檔存在」)是兩件互不相關的事:歸因守衛管的是「這筆逃逸能不能對到迴圈」,S2 管的是「這筆逃逸有沒有可查證的佐證」;三個自動來源(`_auto_escape` 的呼叫全都會帶 `sha`,見 `scripts/lumos:6383`/`8010`/`25069`)本來就滿足 S2,不會被新擋下擋到,兩份計劃的決定不衝突。
- 舊編號(自主審查量尺 r1)七席 29 條卡住的核心問題——loop 欄語意混淆(→ S1 的 `loop_kind`)、部分列沒有缺陷佐證(→ S2)、寫錯撤不掉(→ S3)、分子分母單位不同導致率可超過 1、對負數開根號(→ S4,「分子與分母都應以迴圈為單位」)——本案條款逐一對應到,r1-intake.md 記錄的「兩席誤讀 loop 欄為 bug」也在計劃摘要裡用 WHY 行說明清楚並更正,沒有遺留未解的核心問題。
- `docs/.escape-log.jsonl` 現有 25 列全部落在 `loop_kind` 三分類的其中一類之內(design/code/plan 語意上都能對應到某一列),沒有看到會落到分類規則三選都不中的孤兒列。

總結:最嚴重 severity 為 major;blocking 共 3 條(F1、F2、F3)。
