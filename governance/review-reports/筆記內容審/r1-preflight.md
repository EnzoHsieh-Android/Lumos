# 前置掃描報告:筆記內容審_計劃.md

被掃文件:`docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md`
對照 repo:`clone-ns`(`scripts/lumos`,33062 行)
本掃描只做機械核對,不評設計好壞。未讀 `governance/review-reports/` 底下任何檔案內容(僅用 `ls` 確認檔名/目錄存在,未讀內容),未讀 `scratchpad/DR3/`。

---

## ① 未定義的詞

逐一核對文件用到但自己沒解釋的詞、欄位、指令、旗標、設定鍵、事件種類,結果:皆能在文件自身或 repo 既有慣例中找到定義,未發現真正「查無來源」的詞。列出幾個特別核對過、容易誤判成「未定義」的:

引句:「`prepare --diff <範圍> --orchestrator claude|codex`**(編排者那一家必填,照 `loop next` 的既有規矩)」
查到什麼:`scripts/lumos:10365`(`LOOP_ORCHESTRATORS = ("claude", "codex")`)、`scripts/lumos:10865-10867`(`loop next` 對新審查編號強制要求 `--orchestrator claude|codex`,值域同為 claude/codex)。
判定:無問題(旗標值域與既有指令一致,非未定義)。

引句:「有、內容一樣 → 拒絕並指向翻案指令」
查到什麼:`scripts/lumos:32199`(`decision-supersede` 子指令,說明「翻盤一條決策(valid:false+superseded_by)」),及全檔「翻案」一詞在既有連鎖判定/決策系統中大量使用(如 `scripts/lumos:1892` `1926` `1993` 等)。
判定:無問題(「翻案指令」對應既有 `decision-supersede`,非未定義新詞)。

引句:「`lumos note-audit skip --diff <範圍> --note "<理由至少 4 個字>"`」「`LUMOS_SKIP_NOTE_AUDIT=1` 單次跳過記 `skipped-env`」
查到什麼:同族既有機制 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:23955-23957`)與事件種類 `skipped-env`/`warned`/`blocked`(`scripts/lumos:23957` `24022` `24018`)已存在同構寫法,文件明講「照第一層」沿用。
判定:無問題(新指令/新旗標,文件自己定義,且明講是新的)。

引句:「`decisions` 裡被判的用新的 `lumos decision-amend` 改」
查到什麼:`decision-amend` 目前 repo 裡不存在(`scripts/lumos` 無此子指令),但文件本身在條款 [S12] 與〈做法〉第 3 節第 4 點完整定義了它的行為,且未宣稱它是既有指令。
判定:無問題(文件明寫是要新增的指令)。

`[manual:]`、`REVISIT:YYYY-MM-DD`、`[test:]` 等既有記號亦逐一核對過,分別對應 `scripts/lumos:3818`(`MANUAL_REF_RE`)、`scripts/lumos:1958-1960`(Check E5 REVISIT 判準)等既有機制,非未定義。

**小結:①無。**

---

## ② 壞引用

### [[連結]]

逐一核對文件全部 7 個 `[[連結]]`:

| 連結 | 是否存在 |
|---|---|
| `[[Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋]]` | 存在(`docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md`) |
| `[[Issues/治理帳多個寫入者都沒上鎖]]` | 存在(同目錄下有此檔) |
| `[[Projects/筆記形狀擋_計劃]]` | 存在 |
| `[[Projects/筆記不存程式碼推得出的事_計劃]]` | 存在 |
| `[[Systems/外部對照-code衍生wiki]]` | 存在(`Systems/外部對照-code衍生wiki.md`) |
| `[[Systems/筆記內容閘]]` | 存在 |
| `[[Systems/pitfalls-code-loop]]` | 存在(`Systems/pitfalls-code-loop.md`) |

引句:「同日對近一個月 25,282 行新增筆記跑「目前沒有/只有 N 種」句型,抽樣約三分之一是真的,見 Issue〈擋什麼的初步實測〉」
查到什麼:`docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:127`,標題行原文正是「**擋什麼的初步實測(2026-09-27,單人目測,樣本小)**:把近一個月 473 個提交裡新增的 25,282 行筆記…」——這是該 Issue 內部的段落標題,不是獨立筆記,文件本身用的是散文提及(非 `[[連結]]` 語法),且文末〈前身 r3 發現怎麼處理〉已自陳「駁回:邊界席 F5 說〈擋什麼的初步實測〉查無此篇——那是 Issue 裡的段落標題(第 127 行),不是一篇筆記」,與程式碼查到的行號完全吻合。
判定:無問題(非壞引用,文件已自行標注清楚;行號比對正確)。

引句:「`Systems/筆記內容審`」(文末落點/新家)
查到什麼:`docs/lumos-toolchain-knowledge/Systems/` 下目前不存在「筆記內容審.md」。
判定:無問題(文件明寫是「本計劃的新家」,屬於「新增的」,依規則不算壞引用)。

### 反引號裡的路徑/函式名/常數名

逐一核對所有反引號內容(共 50+ 項),既有的部分全數存在於 repo:

| 反引號內容 | 查到什麼 |
|---|---|
| `_note_shape_eval` | `scripts/lumos:23763` |
| `_ns_range_added` | `scripts/lumos:23579` |
| `_validate_repo_ref` | `scripts/lumos:19819` |
| `scripts/hooks/pre-commit` | `scripts/lumos:16920``18301`;`scripts/hooks/pre-commit` 檔存在 |
| `scripts/hooks/pre-push` | `scripts/lumos:16921``18302`;`scripts/hooks/pre-push:236,247` |
| `governance/rel-cascade/<id>.jsonl` | 目錄 `governance/rel-cascade/` 存在,內有 `c-<時間戳>-<hash>.jsonl` 型式檔案(樣板佔位符,語意相符) |
| `governance/review-reports/筆記不存程式碼推得出的事/r3-*` | 目錄與 `r3-外家否決-codex.md`、`r3-正確性-opus.md`、`r3-架構對齊-sonnet.md`、`r3-併發-sonnet.md`、`r3-接手-sonnet.md`、`r3-邊界-sonnet.md` 等 12 個 `r3-*` 檔皆存在(僅核對檔名,未讀內容) |
| `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md` | 檔案存在且可讀(此路徑不在禁讀清單內) |
| `.lumos/config.json` | 真實存在(`ls -la .lumos/config.json` 有結果),且是 `_note_shape_config`/`_nodehome_config` 既有讀取的設定檔 |
| `note_shape.gate` | `scripts/lumos:23494-23497` |
| `home check`、`note-shape --diff` | `scripts/hooks/pre-push:236,247` 兩者確實依序呼叫 |
| `loop next` | `scripts/lumos:10813`(`cmd_loop_next`) |
| `lumos decision-amend`、`decision-amend <節點> <決策編號> …`、`note-audit`、`note_audit.gate`、`LUMOS_SKIP_NOTE_AUDIT`、`governance/note-verdicts/`、`.lumos/note-audit/` | repo 目前皆不存在(用 `find`/`grep` 全庫搜尋 `note-audit`/`note_audit` 僅命中本文件與相關計劃/系統筆記),但文件明寫是本計劃要新增的指令/資料夾/開關 |

判定:無問題,未發現壞引用(既有引用全部存在;標記為新的項目 repo 裡確實不存在,符合「明寫是新的不算壞」的規則)。

**小結:②無。**

---

## ③ 範圍自相矛盾

重點核對三個容易前後打架的地方:①判定檔讀取來源的分工(工作目錄 vs 已推送頂端提交 vs 遠端頂端提交)、②「取最重、只有申訴能調輕」規則與「同批非申訴報告judged不同即整份拒絕」規則是否衝突、③本機與 CI 範圍算法是否被兩處講成不同版本。逐一核對如下,均未發現矛盾:

- `prepare` 讀「工作目錄裡的判定檔」(〈做法〉第 3 節第 1 點)、`check` 讀「被推送的那個頂端提交裡」(第 3 節第 6 點)、doctor 事後掃描讀「遠端頂端提交」(第 3 節第 8 點)——三處各自針對不同呼叫時機(prepare 在本機寫檔前、check 在推送當下、doctor 在推送之後),條款 [S5][S10][S16] 也分別對應這三種來源,彼此不衝突、是分工不是矛盾。
- 「取最重的那次非申訴判定」(〈做法〉第 2 節)是跨「判定檔」的彙總規則;「同一次呼叫裡兩份非申訴報告對同一編號判得不同 → 拒絕」(〈做法〉第 3 節第 5 點)是同一次 `record` 呼叫內、寫檔之前的前置檢查——兩者作用的範圍不同(一個管已落地的判定檔之間如何取值,一個管落地前這批報告內部要不要先過一致性檢查),不是同一件事的兩種講法。
- 「本機與 CI 的範圍可能不同」段落(〈誠實界線〉)所描述的「本機新分支起點=不在任何遠端分支上的最早提交;CI 從空樹截到上線點、只排除主線」,與 `scripts/hooks/pre-push:225`(`git rev-list … --not --remotes`,排除所有遠端分支)及 doctor 給消費專案 CI 貼的那一步(`scripts/lumos:23885-23888`,只建本地 `main` 追蹤分支、未排除其他遠端分支)兩處程式碼行為吻合,文件內外一致,非矛盾。

**小結:③無。**

---

## ④ 機械宣稱驗語意

逐句核對文件裡「某既有函式/機制現在會做 X」型的宣稱,以下逐條列出:

引句:「範圍函式 `_ns_range_added` 只回「範圍裡每個提交加過的行文字」的集合,不帶行號、後來刪掉的也還在」
查到什麼:`scripts/lumos:23579-23664`,回傳為 `by_path`(`{NFC路徑: 行文字 set}`,無行號欄位)、`paths`(淨改動路徑)、`old_by`;逐提交 `dest.setdefault(p, set()).update(...)` 只做聯集不做差集,故某提交新增、後續提交刪掉的文字仍留在集合中。
判定:無問題。

引句:「「終點版本裡還在、落在哪一塊、第幾行」是 `_note_shape_eval` 在自己的迴圈裡邊查規則邊算的」
查到什麼:`scripts/lumos:23799-23819`,在 `_note_shape_eval` 的 `for i, ln in enumerate(lines, 1)` 迴圈裡用 `regs = _ns_regions(text)` 算區塊、用 `ln.strip() not in texts_by.get(nfc(p), ())` 判斷該行是否仍在新增集合裡(即「終點版本裡還在」),行號 `i` 也是在同一迴圈取得。
判定:無問題。

引句:「區塊判定沿用第一層那支(正文、summary、decisions 文字子欄算;結構欄與開頭欄位其他欄不算)」
查到什麼:`scripts/lumos:23500-23523`(`_ns_regions`),回傳值只有 `body/summary/decisions/other`;`decisions` 底下命中 `_NS_STRUCT_KEY_RE`(結構鍵如 id/decided/valid)的行被歸為 `other`,開頭欄位本身與非 summary/decisions 的其他頂層鍵也歸 `other`。
判定:無問題。

引句:「目前有三處寫死看提交前掛鉤 `scripts/hooks/pre-commit`——上線點函式、範圍起點截斷函式、範圍函式裡逐提交判上線的那一段」
查到什麼:第一處 `_nodehome_golive`(`scripts/lumos:22943-22951`)直接以 `"--", "scripts/hooks/pre-commit"` 限定搜尋路徑;第二處 `_nodehome_clamp_base`(`scripts/lumos:22954-22966`)透過呼叫 `_nodehome_golive` 間接依賴同一寫死路徑;第三處 `_ns_range_added` 內 `hb = _nodehome_cat_blobs(repo_root, [f"{c[0]}:scripts/hooks/pre-commit" for c in commits])`(`scripts/lumos:23603`)直接寫死。
判定:無問題。

引句:「`note_shape.gate`…事件種類照第一層:warn 時有不涵蓋的行只印不擋、記 `warned`;off 時直接放行、不寫帳…環境變數 …單次跳過記 `skipped-env`」
查到什麼:`scripts/lumos:23999-24001`(`mode == "off"` 時只印一行、直接 `return 0`,沒有呼叫 `_gate_event`/`_gate_event_or_warn`);`scripts/lumos:24021-24024`(warn 模式有違規時呼叫 `_gate_event_or_warn(root, "note-shape", "warned", …)`);`scripts/lumos:23955-23957``23974`(`LUMOS_SKIP_NOTE_SHAPE` 與淺層 clone 都記 `skipped-env`)。
判定:無問題。

引句:「不是 block 時 doctor 每次印一行」
查到什麼:`scripts/lumos:23877-23880`(`_note_shape_doctor_lines`:`if mode != "block": out.append(...)`)。
判定:無問題。

引句:「`prepare --diff <範圍> --orchestrator claude|codex`(編排者那一家必填,照 `loop next` 的既有規矩)」
查到什麼:`scripts/lumos:10865-10867`(新審查編號第一次呼叫 `loop next` 必須帶 `--orchestrator claude|codex`,否則擋下)。
判定:無問題。

引句:「pre-push 裡 home check 與 note-shape 的呼叫位置」對應〈做法〉「`check --diff <範圍>`…跟 `home check`、`note-shape --diff` 並排」
查到什麼:`scripts/hooks/pre-push:236`(`home check --diff "$_hrange"` 先跑,`rc==1` 才 exit)、`scripts/hooks/pre-push:247`(`note-shape --diff "$_hrange"` 接著跑,同一段 `if [[ -n "$_hrange" ]]` 區塊、同一個 `$_hrange`,`rc==1` 才 exit)。
判定:無問題(兩者確實在 pre-push 同一段範圍算法下依序並排呼叫,文件提議第三支 `note-audit check` 沿用同一位置)。

引句:「`_validate_repo_ref`(它本來就拒絕絕對路徑與 `..`)」
查到什麼:`scripts/lumos:19827-19832`(`token` 為空、絕對路徑(POSIX 或 Windows)、或 parts 含 `..` 一律回傳 `"missing"`)。
判定:無問題。

引句:「照關係層連鎖帳本 `governance/rel-cascade/<id>.jsonl` 的做法(那支的註解寫明刻意用可追蹤的逐筆檔)」
查到什麼:`scripts/lumos:15023-15028`(`_rel_cascade_dir` docstring:「帳本目錄=…(可追蹤逐 cascade 檔,非 vault-parent 隱藏帳慣例——刻意設計)」),文字幾乎逐字對應。
判定:無問題。

引句:「寫法照連鎖帳本那支(整檔一次寫、拒絕捷徑)」
查到什麼:`rel_cascade_create`(`scripts/lumos:15055-15078`)以 `O_CREAT|O_EXCL` 建新檔、內容以單次 `os.write(fd, hdr.encode("utf-8"))` 寫入(=整檔一次寫;`O_EXCL` 在路徑已存在時失敗,含已存在的 symlink,達成「拒絕捷徑」的效果);同模組另一支 `_ledger_append`(`scripts/lumos:15036-15052`)則是對既有檔案 append、且明確用 `O_NOFOLLOW` 拒絕 symlink 終點,但那是「整行」而非「整檔」寫入。文件描述的「新建一個檔、一次寫完」語意較貼近 `rel_cascade_create`,「拒絕捷徑」在兩支函式裡各以不同機制(`O_EXCL` / `O_NOFOLLOW`)達成同一效果。
判定:無問題(語意相符,只是「連鎖帳本那支」實際橫跨該模組兩支寫入函式的特性組合,非單一函式逐字對應;不影響宣稱的正確性)。

引句:「消費專案的根 `.gitignore` 沒有工具會去改(前身 r3 併發席查證 init 與 update 都不碰它)」
查到什麼:全庫搜尋 `.gitignore` 相關寫入,只有兩處:`_scaffold_project` 寫 `kg.parent / ".gitignore"` 即 `docs/.gitignore`(`scripts/lumos:17347`)、`_init_additive_setup` 寫 `root / "governance" / ".gitignore"`(`scripts/lumos:17367`);`cmd_update`→`_vendor_toolchain`(`scripts/lumos:17149-17196`)只複製 `_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES`(`scripts/lumos:16903-16923`)清單內的檔案,清單中沒有根目錄 `.gitignore`,也沒有 `.github/workflows/ci.yml`。
判定:無問題。

引句:「這支檔不在 `lumos update` 的同步清單裡,要手改」(指 `.github/workflows/ci.yml`)
查到什麼:同上,`_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES`(`scripts/lumos:16903-16923`)未列 `.github/workflows/ci.yml`,`_vendor_toolchain` 也無其他寫入該路徑的邏輯。
判定:無問題。

引句:「照第一層只看遠端最新 200 個提交、不在 `--ci` 路徑跑」
查到什麼:`scripts/lumos:23457`(`_NS_DOCTOR_SCAN_CAP = 200`)、`scripts/lumos:23894-23896`(`if ci: … return out`,事後逐提交重算段落在 `if ci` 判斷之後才執行,`ci=True` 時提早 return,不會跑到那段)。
判定:無問題。

引句:「不照新增告警閘放行檔的「一個檔、讀改寫上鎖」」
查到什麼:`_lint_waivers_add`(`scripts/lumos:21446-21450`)docstring 明寫「★讀-改-寫要上鎖★」並以 `with _vault_write_lock(p):` 包住讀取、判斷、寫入全流程,操作對象是單一共用檔 `_lint_waivers_path(repo_root)`。
判定:無問題(文件描述的「一個檔、讀改寫上鎖」precedent 確實存在且行為相符)。

**小結:④ 全部核對項目皆「無問題」,未發現機械宣稱與實際程式碼行為不符之處。**

---

## 總結

四段掃描(①未定義的詞、②壞引用、③範圍自相矛盾、④機械宣稱驗語意)均未發現具體缺陷。文件對既有程式碼行為的引用(函式回傳形狀、掛鉤呼叫順序、事件種類、設定讀取時機、`.gitignore`/`ci.yml` 不被同步覆寫等)逐一核對後與 `scripts/lumos`、`scripts/hooks/pre-push`、`.lumos/config.json` 的實際內容一致;所有 `[[連結]]` 與既有反引號路徑/函式名皆存在,標記為新的部分(`note-audit`、`decision-amend`、`governance/note-verdicts/` 等)repo 中確實不存在但文件已明寫是要新增的,不算壞引用。
