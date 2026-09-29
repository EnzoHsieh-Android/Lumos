severity: major

# r2 正確性-opus 報告(審材 r2-snapshot.patch,53b6389c..429b109f)

實驗全在自己的 `git clone --shared` 臨時目錄(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/r2c`、`mutA`),重現腳本在同一個 scratchpad 的 `probe/p1.py`、`p2.py`、`p3.py`,用 test_lumos.py 自己的夾具(`_df_repo`、`_df_fix`、`_df_commit`)搭現場。基線:`-k drift_fix` 125 passed。

## F1 c4 的標準 YAML 檢查看的是「換之前」那一項有沒有引號,--old 把引號一起框進去就整個繞過,寫出 Obsidian 解析不了的開頭欄位、工具回 ✓

severity: major
blocking: 是
引句:「raw = mb.group(2).rstrip()」
file: `scripts/lumos:27974`
file: `scripts/lumos:27966`

1. `_drift_c4_yaml_err` 看換之前那一項(`raw`)的第一個字元決定走哪條路:原本有引號就只查 `--new` 裡沒有同一種引號,查完直接回 None,不再看換完那一項長什麼樣;原本沒引號才查 `_yaml_plain_ok`。但 `--old` 是對原始文字精確比對(`_drift_valid_under_hits`),可以含引號本身,這樣換完的那一項就不再被引號包住,兩道檢查都不看。
2. 輸入:`valid_under:\n  - "本工作樹(未提交)"\n  - 另一項`,提交後跑下面四種。四種都是 rc 0、印 ✓、記修復帳;PyYAML 6.0.3(`yaml.safe_load`,標準 YAML 讀法)讀換完的開頭欄位:
   - `--old '本工作樹(未提交)"' --new '已提交 abc'`:第 5 行變成 `  - "已提交 abc`,標準 YAML 報 `ScannerError: while scanning a quoted scalar`,整份開頭欄位都讀不出來
   - `--old '"本工作樹(未提交)"' --new '*alias'`:變成 `  - *alias`,報 `ComposerError: found undefined alias 'alias'`
   - `--old '"本工作樹(未提交)"' --new 'true'`:標準 YAML 讀成 `[True, '另一項']`,本工具讀成字串 true
   - 單引號版 `--old "本工作樹(未提交)'" --new '已提交 abc'`:變成 `  - '已提交 abc`,同樣 ScannerError
3. 行內清單是同一種洞的另一條路:`valid_under: [本工作樹(未提交), 乙]`,`--old '本工作樹(未提交)' --new '*a'` → rc 0,換完是 `valid_under: [*a, 乙]`,標準 YAML 報 `found undefined alias 'a'`。`raw[:1] == "["` 直接放行、交給項數檢查;可是項數檢查用的是本工具自己的讀法,這一輪 PITFALL 已經明寫它驗不出這種問題。`--new` 的結構字元檢查擋了 `[]{}`,沒擋 `*` `&` `!` `|` `>`。
4. 本工具自己的 `_handled` 與前後項數比對照樣會過,因為本工具讀 `"已提交 abc` 就當成一個字串。所以第 1 輪邊界 F2、外家 F1 要防的「寫出標準 YAML 讀法不同的開頭欄位、自驗照過」只防到「--old 沒有碰到引號」這一種輸入。真實圖譜裡現成的 c4 發現就是加了雙引號的一項(`Verification/2026-07-15_主網M3_cascade帳本.md` 第 10 行 `- "…torn 行跳過(=未提交)"`),整段連引號一起複製來當 `--old`,是很自然的操作。
5. 重現:`probe/p1.py`(A–D 四格)、`probe/p3.py`(行內清單那格)。把判斷改成看換完那一項(`ma.group(2)`)開頭是不是引號,就能讓這四格變成擋下;現在的 ④ 測試格只測了 `--old` 在引號裡面的那一種。

## F2 計劃收尾的連帶待辦裡,「看:lumos context <節點>」沒加引號;就在同一個節點、已經加了引號的「改:」那行正上方,照貼就會執行檔名裡的指令

severity: major
blocking: 是
引句:「node = _drift_sh(path[:-3] if path.endswith(".md") else path)」
file: `scripts/lumos:26440`
file: `scripts/lumos:26629`

1. 第 1 輪資安 F1 的修法是在 `_drift_fix_hint` 裡加 `_drift_sh`,家節點 WHY 行也寫成通則:「印給人照貼的指令……其他加 shell 引號」。但 `_drift_print_followups` 同一個迴圈裡,對同一個 `p` 先印一行 `看:lumos context {p[:-3]}`,這行沒有引號,也沒過 `_esc_clean`;緊接著那行 `改:` 走 `_drift_fix_hint`,有加引號。這是同一支函式裡同一種形狀,沒有掃到。
2. 重現(`probe/p2.py`):計劃 `Projects/Open_計劃` 的 status 是 doing;`Issues/a$(touch PWNED).md`(open)連到它,`Verification/V$(touch PWNED2).md`(pending,plan_refs 指它);提交後跑 `lumos set Projects/Open_計劃 status done`。實際輸出:
   ```
         看:lumos context Issues/a$(touch PWNED)
         看:lumos context Verification/V$(touch PWNED2)
         改:lumos drift fix 'Verification/V$(touch PWNED2)' 3 --kind c3 --status <abandoned/pass/stale/superseded>
   ```
   把「看:」後面那兩行交給 `bash -c` 執行(`lumos` 換成 `true`),repo 根目錄就會出現 `PWNED` 和 `PWNED2` 兩個檔。攻擊入口與第 1 輪 F1 相同:投稿者提交一篇檔名含 `$(…)` 的筆記,連到某份計劃;受害者收尾那份計劃時,照貼這行「看」的指令。
3. 同一類但只是顯示、不是指令:`_issue_close_revisits` 印 `· {rel}:{no}` 時 `rel` 沒過 `_esc_clean`(`scripts/lumos:26629`),`drift fix --kind c2 --close` 成功之後也會走到這裡。第 1 輪資安 F2 修了 ✓ 那一行,這一行漏了。

## F3 已有結案橫幅的判定只認「已結案」開頭,認不出本專案自己最常見的三種橫幅,結案時會再疊一個

severity: minor
blocking: 否
引句:「if j < len(body) and _DRIFT_BANNER_RE.match(body[j]):」
file: `scripts/lumos:27841`

1. 本 repo `Issues/` 裡人工寫的橫幅,實際形狀是 `> ## ✅ 已結案(2026-08-22)— …`(出現五次)、`> ✅ **已結案(2026-09-21)**:…`、`**★已結案(…)★**`、`> ★已結案(…)★:`。新的正則只接受 `>`、空白、`**` 之後直接接「已結案」,這幾種全部不符。
2. 重現(`probe/p3.py`):三篇 open 的 Issue,標題後面第一段分別是上面三種橫幅,連到已收尾的計劃,各跑 `drift fix --kind c2 --close --status done --reason 這次真的修好了`。三篇都是 rc 0、印「正文加了結案橫幅」,檔內「已結案」都變成 2 個:新橫幅插在舊橫幅上面。
3. 這不是 r1 修正造成的退步(舊判定 `lstrip("> ").startswith("已結案")` 一樣認不出 `## ✅` 這種),但 r1 的修正重寫了判定、docstring 也宣稱能認得出橫幅,拿本專案的真實寫法一測就沒認出來。c2 這條路要處理的,正是「正文已經寫結案、status 沒改」的 Issue,也就是會帶這些橫幅的那一群。

## F4 佔位字檢查把合法理由裡的 <…> 也擋掉,連原本就有的 drift ack 也受影響

severity: minor
blocking: 否
引句:「_DRIFT_PLACEHOLDER_RE = re.compile(r"<[^<>\n]{1,40}>")」
file: `scripts/lumos:27583`

1. 只要角括號之間是 1 到 40 個字就算佔位字,不看內容是不是提示裡真的出現過的那幾個(`<為什麼算解決,附提交或測試>`、`<為什麼還沒解決>`、`<為什麼照留>`、`<sha>`、`<卷證>`、`<原片段>`、`<新片段>`)。
2. 重現(`probe/p3.py`):`lumos drift ack Issues/K 3 --kind c2 --reason "等 Map<K,V> 泛型那支修好再結案"` → rc 2,`擋下:--reason 裡還留著提示的佔位字「<K,V>」——換成真的內容再跑`。理由裡寫泛型、HTML 標籤(`<br>`)或 `a<b 且 c>d`,都會被擋,錯誤訊息還說使用者照抄了提示。
3. `_drift_ack_args_err` 把這道檢查也加到原本就有的 `lumos drift ack` 上,所以這是新版對既有指令收緊了輸入,不只影響新的 fix。

## F5 兩格新測試沒有真的釘住修法:把家節點的比對拔掉,c1/c5 照樣全綠;⑭ 在 macOS 走不到被測分支,也沒有前置斷言

severity: minor
blocking: 否
引句:「"deps": _drift_deps(cx, [_guard_pass_home(cx["env2"], cx["lines"])[0]]),」
file: `scripts/lumos:27824`
file: `scripts/lumos:28081`
file: `scripts/test_lumos.py:54013`
file: `scripts/test_lumos.py:54019`

1. ⑬ 直接呼叫 `_drift_fix_write`,deps 是手做的,只證明「有給 deps 時會比對」。`_drift_fix_c1`、`_drift_fix_c5` 真的有沒有把家節點放進 deps,沒有任何一格測到。改壞實驗(`mutA`,已清 `__pycache__`):兩處都改成 `"deps": [],` 之後,`-k drift_fix` 125 passed、`-k guard_settle` 38 passed,沒有一格翻紅。第 1 輪併發 F6 的修法(鎖內比家節點)等於沒有測試釘住。
2. ⑭:macOS 的檔案系統不分 NFC/NFD。本機實測 NFD 檔名建檔之後,用 NFC 路徑 `exists()` 回 True,所以 `_drift_phys` 第一行就提早回傳,逐層找的迴圈根本沒跑。docstring 承認「本機測不紅」,可是這一格沒有前置斷言(例如先確認 NFC 路徑 `exists()` 是 False,不成立就跳過),照樣在本機記一個 ✓。CI 跑在 ubuntu-latest(`.github/workflows/ci.yml`),推上去之後會真的測到;但推送前的閘在本機跑出來的綠,是「走不到被測分支」的那種綠(見下面鏡頭判定〈測試假綠形態〉)。

## F6 NFD 檔名修了「打開哪支檔」,沒修「印給人貼的 git 指令」:Linux 上照貼 git add / git checkout 會報 pathspec 對不到

severity: minor
blocking: 否
引句:「path = _drift_phys(env.vault, rel)」
file: `scripts/lumos:27764`
file: `scripts/lumos:28236`
file: `scripts/lumos:28164`

1. `_drift_phys` 只用在開檔。`cx["repo_rel"]` 還是索引鍵(NFC),成功訊息 `git add … {repo_rel}`、驗證失敗與記帳失敗的 `git checkout -- {repo_rel}` 都拿它印。乾淨檢查另外有 `_guard_raw_git_path` 換成 git 裡的真實拼法,這三行指令沒有換。
2. 輸入:Linux、檔案以 NFD 拼法被追蹤。修完照貼 `git add governance/drift-fixes.jsonl <NFC 路徑> && git commit` 時,git 的 pathspec 是逐位元組比對,會報 `pathspec … did not match any files`,`&&` 後面的 commit 也不會跑;照貼 checkout 想退回也一樣退不了。⚠ macOS 不分 NFC/NFD,本機跑不出來;這是讀程式碼推的,和第 1 輪 intake 採信外家 F6 的根據一樣。

## F7 --keep 預覽與表態成功訊息的 related 清單沒過 _esc_clean(同一行的 rel 過了)

severity: minor
blocking: 否
引句:「x[:-3] for x in rec['related']」
file: `scripts/lumos:27488`
file: `scripts/lumos:27500`

1. 這一輪新加的預覽行把 `rel` 和 `reason` 都包了 `_esc_clean`,但後面「當時連著 …」的已收尾計劃清單直接用 `x[:-3]` 拼。那是計劃的檔名,來自投稿者。✓ 成功那一行的 `rel` 和 related 也都沒包。
2. 輸入:已收尾計劃的檔名含 ESC 序列(git 允許),`drift fix --kind c2 --keep --dry-run` 或 `drift ack` → 逃逸碼直接進終端。和第 1 輪資安 F2 同一類(縱深防禦)。

## 已試過、沒找到洞的(不算 finding)

- `_drift_sh`:`\w` 認得中文;`$(…)`、空白、`;`、`~`、`*`、`!` 都會加引號;shlex.split 切回來還是同一個節點。`startswith("-")` 那條分支沒作用,因為 shlex.quote 不會替 `-x` 加引號;不過節點一定帶資料夾前綴,碰不到。
- `_drift_jsonl_parse` 改只在 `\n` 切:兩本帳的讀取端只有 `_drift_load_acks`、`_drift_jsonl_rows`(兩支都已改走它),加上 `_jsonl_append_verified` 的逐行讀(文字模式逐行讀只在 `\n` 切,不在 U+2028 切),沒有漏網的讀取端。
- `_drift_seq_ok`:舊帳沒有 seq、seq 是 0、負數、bool、字串,都不算已表態;修復帳的 `_drift_fix_last_sha` 仍然用 `_drift_ack_seq`,全是 0 號時取檔內最後一筆,行為合理。
- 帳檔路徑提前檢查、記帳前在鎖內再比一次磁碟、筆記是符號連結或還有別的硬連結就擋、c4 只列證據時略過乾淨檢查:逐條走過路徑,沒找到會出錯的輸入;⑦⑧⑨⑩ 各格的現場都成立(第 1 輪 intake 有還原翻紅的紀錄)。
- 真實圖譜 `drift scan`:c2 有 17 筆沒表態的重新列出,和防線計劃表格下面補的那句說明一致。

## 圖譜鏡頭固定席逐條判定

- Systems/guard-kill(rc 優先序、--json 輸出純度):diff 沒碰 guard kill 的 rc 與輸出路徑。不影響。
- Systems/lumos-cli-read(search 預設排除 superseded):diff 沒碰 search。不影響。
- Systems/lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 之間):沒碰。不影響。
- Systems/bound-tests-gate(固定席合約綁的測試逐支真跑):沒改閘的程式;新測試 `t_drift_fix_review_r1_edges` 只加進家節點的 TEST: 清單,沒有綁到任何 ★INVARIANT★ 行。不影響。
- Systems/授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT、主程式檔頭 SPDX 與 MIT 全文):diff 沒碰檔頭,也沒碰複製清單。不影響。
- Systems/測試假綠形態(還原翻紅釘要配前置斷言,證明現場成立):**有牴觸**。⑭ 列在 docstring 的翻紅釘清單裡(「_drift_phys 拿掉逐層找(Linux 上)→ ⑭紅」),卻沒有前置斷言,在 macOS 上是這條合約點名的第④型(現場走不到被測分支);⑬ 有走到被測的函式,但 c1/c5 接線那一層改壞了照樣全綠。見 F5。
- Systems/design-loop(處置閘第五步):沒碰。不影響。
- Systems/pitfalls-code-loop(★RISK★):這一輪沒改簿記檔名單(`_BOOKKEEPING_FILES` 在 53b6389c 就加了修復帳);混版會多審的取捨已經寫進家節點,附了回頭條件。不影響。

最高等級:major
