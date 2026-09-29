severity: major

# 代碼審第 3 輪 正確性-opus(審材 r3-snapshot.patch,429b109f..e7112c53)

實驗環境:`git clone --shared` 到本席自己的臨時目錄(HEAD e7112c53),直譯器 /opt/homebrew/bin/python3(3.14.6),標準 YAML 讀法用 PyYAML 6.0.3。repo 根沒動。

## F1 c4 的標準 YAML 檢查用 Python 的 \s 拆「換完那一項」,換成全形空白或不斷行空白就照樣寫入,標準 YAML 讀出的是字串或整段讀不了

severity: major
blocking: 是
引句:「m = _DRIFT_VU_ITEM_RE.match(after)」
file: `scripts/lumos:27971`
file: `scripts/lumos:27964`
file: `scripts/lumos:380`

1. 根因:這輪把檢查改成「只看換完的結果」,但拆那一行用的 `_DRIFT_VU_ITEM_RE`(`^(\s*-\s+|valid_under:\s*)(.*)$`)是 Python 的 `\s`,會把 U+3000(全形空白)、U+00A0(不斷行空白)、U+2000–U+200A 當成空白;標準 YAML 只認半形空白與 tab。`_drift_c4_text_err` 的 `t = new.strip()` 也是 Python 的 strip,開頭是 U+3000 的 --new 不算「- 或 # 開頭」。結果檢查拿到的「那一項」是工具的讀法切出來的,不是 YAML 的讀法——跟這條 PITFALL 自己寫的「用自己的讀法驗證驗不出壞掉」是同一個毛病,只是換到空白字元上。
2. 輸入甲(清單項):`valid_under:` 底下 `  - 本工作樹(未提交)`、`  - 乙`,跑 `lumos drift fix Verification/U1 5 --kind c4 --old " 本工作樹(未提交)" --new "　已提交 abc"`(--old 開頭是半形空白,--new 開頭是 U+3000)。走到 `_drift_c4_yaml_err`:換完那行是 `  -　已提交 abc`,正則的 `\s+` 吃掉 U+3000、item=「已提交 abc」過 `_yaml_plain_ok`;工具自己的 `LIST_ITEM_RE`(同樣是 `\s`)讀成兩項清單、只差一項 → 寫入,回 0。標準 YAML:`-` 後面接 U+3000 不是清單記號,valid_under 變成單一字串 `'-　已提交 abc - 乙'`。
3. 輸入乙(開頭欄位那一行):`valid_under: 本工作樹(未提交)`(rtb 三篇真實的 c4 都是這種寫法),`--old " 本工作樹(未提交)" --new "　已提交 abc"` → 換完 `valid_under:　已提交 abc`,正則的 `valid_under:\s*` 與 `TOP_KEY_RE` 都照認 → 寫入,回 0。標準 YAML 整段開頭欄位讀不了(ScannerError),Obsidian 的屬性面板整篇壞掉。
4. 輸入丙(不用框到空白):`--old "本工作樹(未提交)" --new " 已提交 abc"`(--new 開頭 U+00A0)→ 換完 `  - \xa0已提交 abc`,寫入;標準 YAML 讀出 `'\xa0已提交 abc'`,工具讀出「已提交 abc」,值不同。`_yaml_plain_ok` 本來有 `v == v.strip()` 要擋這種,但正則先把空白吃掉了,輪不到它。
5. 重現(臨時 clone 內,`python3 ../work/repro1.py`,用 test_lumos 的 `_df_repo`/`_df_fix`/`_df_commit` 建專案、每格跑完 git checkout 還原):
   ```
   before U1: ['本工作樹(未提交)', '乙'] | U2: 本工作樹(未提交)
   U1 '　' rc= 0 ✓ drift fix c4:Verification/U1.md 第 5 行——valid_under 第 1 項換掉了還沒提交的說法
      file line: '  -　已提交 abc'
      standard YAML valid_under: '-　已提交 abc - 乙'
   U2 '　' rc= 0 ✓ drift fix c4:Verification/U2.md 第 4 行——valid_under 第 1 項換掉了還沒提交的說法
      file line: 'valid_under:　已提交 abc'
      standard YAML valid_under: 'YAML 讀不了:ScannerError'
   U1 '\xa0' rc= 0 ✓ drift fix c4:Verification/U1.md 第 5 行——valid_under 第 1 項換掉了還沒提交的說法
      file line: '  - \xa0已提交 abc'
      standard YAML valid_under: ['\xa0已提交 abc', '乙']
   ```
   三格都回 0、檔案已改,預期應回 2。
6. 同一類第三次(r1 邊界 F2 → r2 正確性 F1 → 這裡):換完那一項要用 YAML 的空白定義切(只認 ` ` 與 `\t`),或直接要求換完那行的「- 」/「valid_under: 」後面第一個字元不是任何 `str.isspace()` 的字元、而且 --old/--new 都不含非 ASCII 空白。前一輪收貨時本類 rated major(r2-intake:正確性 F1、外家否決 F1),這裡照同一個標準。

## F2 計劃收尾的「看:」那行只加了引號、沒套 ./,- 開頭的節點印出的指令跑不起來

severity: minor
blocking: 否
引句:「print(f"      看:lumos context {_esc_clean(_drift_sh(p[:-3]), 300)}")」
file: `scripts/lumos:26461`

1. 輸入:圖譜根目錄有 `-x.md`(open 的 Issue)連到 `Projects/Open_計劃`,跑 `lumos set Projects/Open_計劃 status done`。
2. 印出 `看:lumos context -x`;照貼跑 → rc 2「擋下:少了必須要給的 note」。同一篇用 `lumos context ./-x` 跑得出來(rc 0)。
3. 這輪的修正把 `_drift_sh` 從「- 開頭一律加引號」改成「只有 node=True 才補 ./」,drift fix 那幾處都傳了 node=True,這一處新接上 `_drift_sh` 卻沒傳——正是「只修了報上來的那個輸入」的形狀。重現:臨時 clone 內 `python3 ../work/repro2.py` 前半段。

## F3 _drift_fix_target 把 ./ 剝掉後改用檔名猜,./-x 碰到同名就擋,提示印的指令沒有任何寫法能指到那一篇

severity: minor
blocking: 否
引句:「a = a[2:] if a.startswith("./") else a」
file: `scripts/lumos:27734`
file: `scripts/lumos:27738`

1. 輸入:圖譜根目錄的 `-x.md` 與 `Issues/-x.md` 都是 open 的 Issue、都連到已收尾計劃。`lumos drift scan` 對根目錄那篇印 `lumos drift fix ./-x 3 --kind c2 …`。
2. 照貼跑:剝掉 ./ 之後 "-x" 沒有斜線,走 `env.by_stem` → 兩篇 → 回 2「同名筆記有 2 篇(-x、Issues/-x),給完整路徑」。可是 `./-x` 本來就是完整路徑,`./-x.md` 也被剝成同一個,沒有別的寫法能指到根目錄那篇。
3. 修正的本意是「./ 開頭 = 圖譜內路徑」,剝完應該照「給了路徑就只認那一篇」那條走(`a + ".md" in env.notes`),不該退回檔名猜。重現:`repro2.py` 後半段輸出 `fix ./-x rc 2 擋下:同名筆記有 2 篇(-x、Issues/-x),給完整路徑`。

## F4 git 指令改用原樣路徑的三處接線沒有測試,三處全部改回索引鍵測試照綠

severity: minor
blocking: 否
引句:「_drift_git_arg 改回索引鍵 → ⑦紅」
file: `scripts/lumos:28184`
file: `scripts/lumos:28217`
file: `scripts/lumos:28256`

1. ⑦只直接呼叫 `_drift_git_arg` 驗函式本身;`_drift_fix_verify` 的 git checkout 提示、`_drift_fix_record` 的「要退就」、`cmd_drift_fix` 成功時的 git add 三處有沒有真的用它,沒有任何測試看。
2. 改壞:把三處 `{_drift_git_arg(cx)}` 全改回 `{_esc_clean(_drift_sh(cx['repo_rel']), 300)}`,清 `__pycache__` 後跑 `python3 scripts/test_lumos.py -k drift_fix_review` → `39 passed, 0 failed`。
3. 跟第 2 輪收貨處理的 deps 接線(正確性 F5)同一種假綠:函式對了、呼叫端改回去沒人發現。要驗接線,可以在同程序裡替換 `_guard_raw_git_path` 回 NFD 拼法、跑 `cmd_drift_fix`,看印出的 git add 那一行。

## 逐 hunk 其他查證(沒有發現,附理由)

- `_plan_file_exists` 改用 `_nfc_child`:原本 `any(nfc(q.name) == want for q in parent.iterdir())`,OSError 回 False;現在 `_nfc_child` 在 try 裡用 `next(...)` 走同一個產生器,iterdir 或走訪時的 OSError 都回 None → False,找到回 Path → True。parent 不是目錄的判斷還在前面。行為一模一樣。
- `_phys_path` 對照原本 `_drift_phys`:唯一差別是某一層 iterdir 丟 OSError 時,舊版立刻回整條原路徑,新版把這一層照原拼法接下去、繼續往下找。只有「前面幾層已經換成 NFD 拼法、後面某層沒權限列目錄」才會回不同的路徑,兩種路徑都打不開,呼叫端都是報「打不開」或讀不到;沒有會改變結果的輸入。
- `_drift_sh` 拿掉非節點參數的「- 開頭就加引號」:剩下的非節點呼叫端是範本句(一定是「提交 」開頭、含空白會加引號)與 `_drift_git_arg`(repo 相對路徑,以圖譜目錄名開頭);實際跑不到 - 開頭。
- 結案橫幅正則:對工具鏈 Issues 裡全部真實橫幅(`> ## ✅ 已結案(`、`> ✅ **已結案(`、`> ★已結案(`、`**★已結案(`、`已結案(`)逐一比過都認得;rtb 用的是正文裡的 `## 結案` 段落,不是第一段橫幅,照設計會加橫幅。「已結案通知功能…」照樣不算。
- 佔位字正則:對照所有會印進 --reason/--new 的提示(`<為什麼算解決,…>`、`<為什麼還沒解決>`、`<為什麼照留>`、`<原片段>`、`<新片段>`、`<sha>`、`<卷證>`)都涵蓋;c3 的 `<a/b/…>` 在 --status,本來就被列舉值擋。
- c4 誤擋:這輪新增「跨行的值」「行內清單」都改成擋。工具鏈與 rtb 兩份圖譜裡真實的 c4(`valid_under: 僅 Phase 14 … 本工作樹(未提交、…)` 三篇、工具鏈兩篇引號寫法)都是單行純量或單行引號項,不受影響;兩份圖譜沒有區塊純量或行內清單寫法的 c4。
- 新測試格有沒有走到被測分支:r2 ①五格在 r1 版會寫入(舊版只看換之前的引號、Q4 放行行內清單),現行版分別走到「頭尾」「標準 YAML」「行內清單」三個分支,訊息關鍵字對得上;⑤、c5 ② 有 `seen`/`deps` 非空的前置;⑭ 在 macOS 上先斷言現場不成立就跳過並印出,Linux 才跑。⑦ 見 F4。

## 圖譜鏡頭固定席

- Systems/guard-kill(rc 優先序、--json 純度):diff 沒碰 guard kill 的判定與輸出路徑,只新增 drift fix 相關函式與改 settle 共用的提示;不影響。
- Systems/lumos-cli-read(search 預設排除 superseded):diff 沒碰 search 與濾網;不影響。
- Systems/lumos-cli-lifecycle(re-inject 只改 sentinel 之間):diff 沒碰 inject/CLAUDE.md 寫入;不影響。
- Systems/bound-tests-gate(code-loop check 逐支真跑綁定測試):diff 沒碰閘本身;家節點 TEST 清單加了 t_drift_fix_review_r2_edges,這支存在於 test_lumos.py(本席實跑綠),不會變成懸空;不影響。
- Systems/授權與歸屬(_VENDORED_TOOLKIT 不含授權檔、主程式檔頭 SPDX+MIT):diff 沒動檔頭與白名單,只在檔中段加函式;不影響。
- Systems/測試假綠形態(還原翻紅釘要有前置斷言):⑭ 這輪補了前置斷言(現場不成立就跳過並印出),符合;⑦ 用替身讓現場成立、函式本身的翻紅釘有效,但三處呼叫端沒釘,見 F4——不算違反這條合約(合約講的是釘子要證明現場成立),是接線沒釘。
- Systems/design-loop(處置閘第五步):diff 沒碰處置閘;不影響。
- Systems/pitfalls-code-loop(★RISK★):diff 沒碰 pitfalls 分級;不影響。
- 超出上限只列名的節點:diff 碰到的共用函式只有 `_plan_file_exists`(逃逸自動記)、`_issue_close_revisits` 與新增的 `_nfc_child`/`_phys_path`;`_plan_file_exists` 行為逐行對過一致(見上一節),其餘只列名的節點本席沒逐篇讀,不下判斷。
- 角色卡:派工詞尾端只有 `LUMOS-ROLE-CARDS: on` 一行,沒有附角色卡內容,無從逐張回應。

最高等級:major
