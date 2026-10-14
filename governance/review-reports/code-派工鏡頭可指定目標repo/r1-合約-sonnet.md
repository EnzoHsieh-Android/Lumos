severity: minor

我讀了兩份 patch、計劃、手冊,並用 lens-repo 的實作(565763ce)驗證。另外在暫存 clone 上做了約 17 次變異實驗,事後已刪除。結論是:S1–S22 每條的 `[test:]` 都對得上條款,22 支測試都存在,實跑全綠。多數守衛一拆就翻紅,例如短編號、符號連結、isspace、字元集、`--out` 覆寫、掛鉤與 fsmonitor、以及對只在提交裡的檔跑 impact 這幾個。下面只列會漏掉或對不上的地方。`governance/anchor-baseline.json` 兩個雜湊與 565763ce 的實際檔案一致。

severity: minor
blocking: 否 — 條款 S1、S7 沒寫節點內容取哪一版,測試守不到的是做法 6 與實務隱患明寫的行為
引句:「S7: rc0、第一篇(會談目錄有)附內容,並寫明節點內容是會談目錄的版本」
問題:做法 6 與實務隱患都說連結節點內容讀會談目錄那份、提交裡改過的版本不附,附加段頭也這樣聲明。但 `_lr_repo()` 先在 base 提交建好「已有節點」,再開第二個工作樹,所以提交裡與會談目錄裡的節點內容完全相同(都含 `LR-SESSION-BODY`)。S1、S2、S3、S7、S15 斷言的都是這個字串。
具體失敗情境:我把 `cmd_dispatch_lens_spec` 的 `_read_wt` 改成「有提交時優先 `git show <提交>:<節點>`」,`-k dispatch_lens_spec` 88 條全綠。實作被改成附提交版本時,頭上那句「節點內容是會談目錄的版本」就成了假話,測試卻不會紅。
佐證:`scripts/test_lumos.py:42584`(`_lr_repo`)、`scripts/test_lumos.py:42819`、`scripts/lumos:49488`(`_read_wt`)

severity: minor
blocking: 否 — NFC 守衛不屬於任何 S 條款的必驗行為,但它是計劃明寫的設計理由
引句:「S3: 路徑是 NFD → spec_missing」
問題:做法 2 說非 NFC 路徑要先擋,不交給 git,否則平台相依。但這條 NFD 斷言拿掉守衛照樣綠:NFD 檔名在提交裡本來就找不到,由 `ls-tree` 那道更晚的檢查代打(實測 macOS 上也是)。實作紀錄說 spec-freeze 也擋非 NFC,S18 卻完全沒有 NFD 案例。CI 只跑 ubuntu,沒有 macOS 的機會抓。
具體失敗情境:我把 `scripts/lumos:49255` 的 NFC 檢查整段停用,`-k spec_commit_path_rules` 26 條全綠。我也把 spec-freeze 的 `_ud.is_normalized` 拿掉,`-k spec_freeze` 25 條全綠。macOS 上若有人用 NFD 檔名,spec-freeze 會印出一行每席都回 `spec_missing` 的 `LUMOS-SPEC:`,正是實作紀錄想避開的情況。
佐證:`scripts/test_lumos.py:42722`、`scripts/lumos:49255`、`scripts/lumos:49703`

severity: minor
blocking: 否 — 這幾項不在任何 S 條款內,但都是做法或實作紀錄明寫的行為
引句:「判法逐檔呼叫:每個候選各跑一次」
問題:做法 5 說只在提交裡的檔最多列 5 個(`len(only) < _LENS_SPEC_MAX_FILES`),S6 只放了 2 個。spec-freeze 的 mode 100755/100644 判斷沒有任何測試看 mode。實作紀錄寫的 `--json` 欄位 `only_in_commit`,以及「提交寫法一律加注入框」(含沒有任何節點的情況),也沒有斷言。
具體失敗情境:我把 5 個上限拿掉,`-k dispatch_lens_spec` 88 條全綠。我把 mode 固定成 100644,`-k spec_freeze` 25 條全綠。可執行的計劃檔會被凍成不可執行,計劃檔多時鏡頭行會無上限變長,測試都不會紅。
佐證:`scripts/lumos:49368`、`scripts/lumos:49719`、`scripts/test_lumos.py:42789`(S6)

severity: minor
blocking: 否 — 手冊與撤除條件脫鉤,不會讓功能壞掉,但 RETIRE-IF 可能誤觸發
引句:「連續 8 週沒有新的派工單帶」
問題:RETIRE-IF 與 REVISIT 都靠 `grep spec_commit` 派工單來數用量,做法 9 寫「編排者照範本寫」。但「rN-dispatch.json 多記 `spec_commit`」只出現在 `skills/lumos-design-loop/reference.md`。主入口 `SKILL.md` 第 3 步與 `templates.md` 的派工單欄位清單(round、seat、lens、materials、auditor)都沒加,也沒有範本。
具體失敗情境:編排者照 `SKILL.md` 操作,派工單不會有 `spec_commit`。2026-12-15 的 REVISIT 與八週 RETIRE-IF 因此數到 0,把還在用的寫法與 `lumos spec-freeze` 判成該撤。
佐證:`skills/lumos-design-loop/SKILL.md:26`、`skills/lumos-design-loop/reference.md:513`、計劃第 43、107 行

severity: minor
blocking: 否 — 手冊走得通,但快照、工作副本、指紋三者可能各是一個版本,收貨時才發現
引句:「rN-snapshot 就用它寫出的那份」
問題:`SKILL.md` 第 1 步複製工作副本並 `sha256sum` 留指紋,第 2 步 refcheck 命中時「直接修真檔」,第 3 步才 spec-freeze。快照現在是第 3 步從真檔凍出來的,席位卻仍「指向工作副本」,`--reviewed` 的指紋也還是第 1 步算的。手冊沒交代這三者要怎麼對齊。
具體失敗情境:第 2 步修了真檔後,席位讀的是修前的副本,快照與鏡頭附的節點是修後的內容。席位引到修前的句子,`quote-check --spec <快照>` 錨不到,有效 finding 被丟。第 1 步的指紋也對不上快照的雜湊。
佐證:`skills/lumos-design-loop/SKILL.md:20-26`

severity: minor
blocking: 否 — 影響範圍僅限計劃筆記命名與落點對不上
引句:「Systems/每輪修補差異派工」
問題:計劃 `lands_in` 把這篇列為現況落點,做法 11 的「要一起改的說法(列全)」卻沒有它,這次也沒改這篇。它的 `about_code` 含 `skills/lumos-design-loop/templates.md`,而這次 `templates.md` 改了兩處。落點說有、實際沒寫,下一個 session 會去這篇找設計審提交寫法的現況而找不到。
另外,計劃標題「派工鏡頭可指定目標repo」與決策 d1 的「不讓派工詞指定任何目錄或別的 repo」字面相反。舊裁定本身(`Projects/派工鏡頭跨repo不再靜默_計劃` 的不選項與不做項)保持一致,codex-harness 沒殘留作廢標記,這點沒問題。只有標題字面會讓搜「指定 repo」的人誤判。
引句:「不讓派工詞指定任何目錄或別的 repo」
佐證:計劃 front matter `lands_in`、`docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md`(`about_code`)、計劃第 32 行

severity: minor
blocking: 否 — 兩項實際影響都小,但〈實作紀錄〉號稱完整列出偏離,與程式對不上
引句:「vault 也用這支回的那個(提交寫法是路徑得出的 vault)」
問題:有兩處偏離〈實作紀錄〉沒列。
- 做法 4 說工作樹寫法的目標架構段 vault「跟現在相同」,但原本取 HEAD 樹裡排序第一個 vault(`_arch_target_vault_rel(root, "HEAD")`),現在改傳工作樹 glob 的 `slugs[0]`。工作樹有未提交的、排序更前的 `docs/*-knowledge` 時,兩邊會選到不同 vault,節點又固定從 HEAD 讀,目標架構段會退化。這一項我只讀碼推論,沒跑。
- 掛鉤的範圍版 `_fail_note` 記事件,原本是 `except Exception: pass`,現在改走新的 `_mark_event`,只吞 `ImportError`、`SyntaxError`、`AttributeError`、`OSError`、`TypeError`、`ValueError`。同檔另外三處(spawn、lock、timeout)的記事件還是 `except Exception`。fail-open 的接住範圍變窄,而且新舊兩種寫法並存。`_hookevent.mark` 目前很簡單,實際風險低。
佐證:`scripts/lumos:49567-49576`(`_dispatch_lens_spec_with_arch`)、`scripts/hooks/claude/dispatch-lens-hook.py:264-271`、`scripts/hooks/claude/dispatch-lens-hook.py:298`

最高等級 minor,blocking 0 條。
