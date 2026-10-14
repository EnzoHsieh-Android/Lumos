severity: minor

整體判斷:推主線新做法在計劃、06 手冊、筆記內容審三處一致。舊的「祖先核對」說法已清掉,`grep` 剩下的「祖先」都是兩類:範圍終點是否為分岔點祖先(判斷是不是分支自己的紀錄),以及歷史敘述(標明 r3 做法、已拿掉)。`_note_reread_bp_vs_remote` 在程式與文件裡都已不存在。「機器忙時重推可能就會過」跟程式一致,逾時看的是 `deadline`,依機器負載而定(`scripts/lumos:37875`、`37985`)。計劃 S31 到 S33 條款列的 13 支測試名都存在於 `scripts/test_lumos.py`,條款與綁定一一對上。入口 WHY 有代價,也寫了範圍外(`GIT_DIR`、`GIT_WORK_TREE` 不清),跟 `scripts/lumos:53399-53402` 的實作相符。下面是我找到的三條問題。

severity: minor
blocking: 否 — 說錯的是跳過帳放在哪一本,不影響擋或放行的判定,也不影響指紋正確性。但這是 r4 專門修過的「說得比實際強」,結果改成另一個錯的說法,而且印給使用者看。
引句:「跳過只留在本機帳;CI 用真遠端重算時會再列出」
問題:計劃、06 手冊、筆記內容審三處,加上擋下時印給使用者的訊息,都說單次跳過「只留在本機帳」「沒隨推送送出」。實際上 `note-reread` 的 `skipped-env` 不在 `_GOV_LOCAL_PAIRS`,該表只列 `note-reread` 的 `reminded`、`covered`、`none`。`_gov_routes_local` 因此回 False,事件寫進 `GOV_LOG_NAME`,也就是 `docs/.governance-log.jsonl`。這個檔被 git 追蹤,本 repo 一直用「chore(lumos): …」帳本提交把它送上去。本機帳 `docs/.governance-local.jsonl` 才是 gitignore 的那本。測試 `t_reread_fp_timeout_blocks` 只比對字串,沒有驗證帳落在哪一本,所以這個錯不會翻紅。
具體失敗情境:使用者讀到「跳過只留在本機帳」,以為這次跳過留不下版控痕跡。實際上它在版控帳裡,下一個帳本提交就會連同推送送出。稽核者或下一個 session 照文件找本機帳,會在錯的檔案裡找不到。
佐證:``file: `scripts/lumos:1368-1373` `` 的 `_GOV_LOCAL_PAIRS`;``file: `scripts/lumos:1487-1493` `` 的 `_gov_routes_local`;``file: `scripts/lumos:37696` `` 的 `_gate_event_or_warn(root, "note-reread", "skipped-env", ...)`;``file: `.gitignore` `` 只忽略 `docs/.governance-local.jsonl`。

severity: minor
blocking: 否 — 這是回頭看的條件(REVISIT)判準的覆蓋缺口,不影響程式行為。
引句:「有一筆就逐筆查是不是本機遠端追蹤 ref 被改過或單次跳過」
問題:新的 REVISIT 判準是「CI 那一步列出還沒對照的篇,而本機帳裡同一個頂端推送前那筆 `note-reread` 是 covered」。單次跳過在 `scripts/lumos:37694-37696` 提早 return,只記 `skipped-env`,不會產生 `covered`。所以「或單次跳過」這個查因根本進不了判準:用跳過繞過的推送,本機帳裡沒有 covered,不會被抽到。判準另外假設做抽查的人手上有推送當下那台機器的 gitignore 本機帳。換機器或換 session 就數不到,這點寫在文件裡的 REVISIT 沒提。
具體失敗情境:有人用 `LUMOS_SKIP_REREAD_CHECK=1` 推主線,CI 那一步照樣列出未對照的篇,但本機帳沒有 covered,這筆被判準放掉。「有真的繞過就把 CI 那一步改成擋」的條件對最典型的繞過方式永遠不觸發。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:132` ``;``file: `scripts/lumos:37694-37696` ``。

severity: minor
blocking: 否 — 入口 WHY 的 `[test:]` 綁定看起來涵蓋 `GIT_EXTERNAL_DIFF`,實際只有「兩道都拿掉」才紅,屬於守衛證明力的缺口,不是目前會出錯的行為。
引句:「都照綠(另一道擋得住),兩道都拿掉才 ③紅」
問題:計劃的變異驗證自己承認,單拿掉入口的 `GIT_EXTERNAL_DIFF` 那一行,`t_reread_fp_ignores_external_diff` 照綠。入口 WHY 卻把這支測試列進綁定,並把拿掉 `GIT_EXTERNAL_DIFF` 當成已被守住的決定。入口那一行因此沒有獨立的翻紅釘,只剩指紋 diff 的 `--no-ext-diff` 一道線在守。以後有人把 `--no-ext-diff` 重構掉,又或者別處的 git 呼叫沒帶這個旗標,入口這一行缺席就沒有任何測試發現。這是同一族「繞過才算守衛」的問題。
具體失敗情境:有人刪掉 `scripts/lumos:53402` 的 `os.environ.pop("GIT_EXTERNAL_DIFF", None)`,全套測試仍綠。WHY 上卻寫著有綁定測試守著這個決定。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:16` `` 的 `[test:…ignores_external_diff]`;``file: `scripts/lumos:53399-53402` ``。

最高等級 minor,blocking 0 條。
