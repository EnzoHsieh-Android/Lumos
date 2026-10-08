severity: major

範圍:架構對齊鏡頭(範圍解析選配參數、共用函式、範本載入、判定者模型、閘名、專案開關、掛鉤、CI、紀錄檔形狀)。已對 repo `scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml` 逐項核對。

## F1 紀錄資料夾在頂端樹裡不存在時,照既有讀法會被當成「git 失敗」,提醒永遠印不出來
severity: major
blocking: 是
引句:「看被推頂端提交的樹裡 `governance/reread-verdicts/` 有沒有「合第 3 節檔名正規式、而且以這個指紋開頭」的紀錄(只列目錄、不讀內容、不組 diff;`.tmp-wlf` 殘檔不合正規式、不算)」
file: `scripts/lumos:26052`
1. 既有做法 `_note_audit_load_verdicts` 用 `_nodehome_git(... "ls-tree", "-z", "--name-only", f"{where}:governance/note-verdicts")`,目錄不存在時 git 回 rc128(實測 `git ls-tree HEAD:governance/reread-verdicts` 印 fatal: Not a valid object name、rc128),`_nodehome_git` 把非零一律回 None,既有程式在這裡把 None 當成「沒有判定檔」。
2. spec 同時規定「git 失敗 → 印這次沒提醒、記 skipped、回 0」(第 4 節、S7)。兩條規則對同一個 None 沒有說怎麼分。
3. 新資料夾在上線後、第一份紀錄提交之前一定不存在(每個專案的初始狀態)。照 spec 字面(沿用既有 helper、git 失敗一律 skipped)實作,check 在每個專案的每次推送都走 skipped,永遠不會列出「沒對照」的候選,S6 的 reminded 路徑只有在資料夾已存在時才走得到;兩週量測的 `reminded` 會是 0,RETIRE-IF 第一條「提醒沒人用」會被誤判成立。反過來照既有慣例把 None 當空,又會把真的 git 失敗吞成「全部沒對照」。
4. spec 需要明寫:先分辨「資料夾不存在」(例如先查 `ls-tree <頂端>:governance` 或用 `git cat-file -e`/`ls-tree <頂端> -- governance/reread-verdicts` 的空輸出)與「git 真的失敗」,前者視為零紀錄、後者才 skipped;S6/S7 各補一個資料夾不存在的案例。

## F2 reread-prepare 沒有 --orchestrator 參數,但項目檔名、檔頭、判定者模型都靠它
severity: major
blocking: 是
引句:「`.lumos/note-audit/reread-<項目指紋>-<編排者>.md`」
file: `scripts/lumos:26342`
1. 既有 `note-audit prepare` 有必填 `--orchestrator claude|codex`(`scripts/lumos:39294` 附近的 argparse),判定者模型、檔名 `{fp}-{orchestrator}.md`、清單檔頭都由它決定。
2. spec 第 1 節寫兩個子指令都收 `--diff [--push-remote --pushed-ref]`,沒有 `--orchestrator`;第 6 節的操作串寫「`lumos note-audit reread-prepare --diff <範圍>`」;第 4 節要求 reread-check 印出「reread-prepare 指令(原樣帶這次的 `--diff`、`--push-remote`、`--pushed-ref`)」。
3. 但項目檔名、檔頭「編排者」、`_note_audit_judge_model` 加的新參數(claude→sonnet、codex→`_CODEX_SEAT_MODEL`)、「codex 編排時準度沒量過」的公告全都需要知道編排者。照字面實作,編排者從哪來沒有定義:要嘛寫死 claude(codex 編排者拿不到 codex 判定者,跟既有「判定者跟編排者同一家」的做法不同,等於引入第二種做法),要嘛實作者自行加參數,而 reread-check 印的指令因為不能猜編排者,貼上去會被 argparse 擋。
4. 建議:reread-prepare 沿用 `--orchestrator claude|codex` 必填(既有做法);reread-check 印的指令帶 `--orchestrator <claude|codex>` 佔位或兩行各一種;S1/S3 加測試。

## F3 專案開關的鍵名與值域另立一套,錯誤處理也沒定義
severity: major
blocking: 是
引句:「`.lumos/config.json` 的 `note_reread.mode`:`warn`(預設)/`off`,從被檢查的頂端版本讀」
file: `scripts/lumos:25783`
1. 既有三道閘(`note_audit.gate`、`drift_check.gate`、`note_shape.gate`)一律是「<閘名>.gate」、值域 block/warn/off(`_NOTE_AUDIT_GATE_VALUES`、`_DRIFT_GATE_VALUES`、`_NOTE_SHAPE_GATE_VALUES`),各自有一支讀取函式並且對「設定檔讀不成 JSON」「鍵不是物件」「值不合法」「null」各印一句提醒、照預設(`_note_audit_config`、`_drift_gate_config`)。
2. spec 用 `mode`(不是 `gate`)且只有 warn/off,是同一個專案設定檔裡的第二種寫法。使用者照既有慣例寫 `{"note_reread": {"gate": "off"}}` 會被靜默忽略、提醒照常印(spec 沒說未知鍵怎麼處理);而 spec 自己「轉擋另案」時要多一個 block 值,必然要再改鍵名或值域,等於現在就種下第二次遷移。
3. spec 也沒有定義四種壞設定(JSON 壞、note_reread 不是物件、值不在 warn/off、null)各自的預設與提醒句;既有兩支讀取函式都有,S13 只測 off。
4. 建議:鍵名用 `note_reread.gate`,值域先收 block/warn/off(block 這一版當 warn 處理並提醒,或直接拒收並提醒),讀取函式照 `_note_audit_config` 的四種壞設定分支寫,S13 補案例。

## F4 「改到的檔」取自 `_nodehome_changes`(一律 NFC),又要求 pathspec 用 git 原樣路徑,兩條互相打架
severity: major
blocking: 是
引句:「用 `_nodehome_changes`(起點與頂端兩邊的樹、帶改名偵測)取全部改動」
file: `scripts/lumos:23900`
1. `_nodehome_changes` 對每個路徑都做 `nfc()`(`scripts/lumos:23919`、`23922`),沒有 `norm=False` 選項;`norm=False` 只存在於 `_nodehome_name_status`(`scripts/lumos:23931`),且吃的是 `diff-tree --name-status -z` 的原始輸出,不是 `_nodehome_changes` 的回傳。
2. 第 0 節規定「要拿去問 git 的路徑(pathspec、`cat-file`)一律用 git 原樣路徑(`_nodehome_name_status` 的 `norm=False` 那條)」,第 2 節 diff 的 pathspec 與第 1 節取起點/頂端 blob 都要用它。但候選的「改到的檔」清單來源是 `_nodehome_changes`,回來的已是 NFC。
3. 在 NFD 樹(macOS 建立的檔名、`core.precomposeunicode` 沒生效的 repo,這個 repo 自己就有筆記形狀擋驗收輪的實例)裡,程式檔或測試檔檔名含中文時,拿 NFC 路徑去做 `git diff -- <pathspec>` 與 `cat-file` 查不到:diff 變成空、指紋把該檔記成「已刪」、S2 的 diff 少了那支檔,而且不報錯(填「(無)」)。
4. spec 需要明寫第 1 節的改動清單怎麼同時拿到 NFC(比對)與原樣(問 git)兩份,例如改用 `_nodehome_name_status(norm=False, codes=…)` 對同一個範圍再跑一次 `diff-tree`/`diff --name-status -z -M`,或替 `_nodehome_changes` 加一個回原樣路徑的選配參數(同「第二種做法」的風險要說明);S1 已有 NFD 案例,S2 也要有 NFD 程式檔案例。

## F5 選配參數收「原因」之後,`_note_audit_resolve` 其他兩路輸出的去向沒定義
severity: minor
blocking: 否
引句:「呼叫端給一個空清單時,它把提早結束的原因(淺層 clone、刪除分支、頂端已在主線、沒有圖譜、讀不到檔案清單)寫進清單、★自己不寫治理帳★」
file: `scripts/lumos:26099`
1. 既有函式在提早結束的路徑上同時 `print` 到 stderr(淺層、刪除分支、起點說明)或 stdout(沒有圖譜)、並寫 `_gate_event_or_warn`;另外每次都無條件印一行「起點——…」說明到 stderr。spec 只說事件不寫,沒說原本的 print 是停掉還是保留。
2. 若保留:reread-check 印一次、resolve 又印一次,同一原因兩行,且部分走 stderr,跟「所有輸出走標準輸出」衝突(掛鉤丟掉 stderr,CI 看得到雜訊)。若停掉:既有呼叫端不變只靠「不給參數行為照舊」保證,實作者需知道兩種行為都要測。
3. 也沒說 `rc2` 的「擋下:…」兩個 print(範圍格式、終點找不到)在 reread-check 先自己驗證後是否還可能走到。理由放行:reread 會先自己驗、不會走到;但請在 S7 加一句「原因不重複印」以免雙印。

## F6 LUMOS_SKIP_REREAD_CHECK 沒有記帳,跟既有兩道閘的略過慣例不同
severity: minor
blocking: 否
引句:「`LUMOS_SKIP_REREAD_CHECK=1` 單次不跑(只管本機)。」
file: `scripts/lumos:26512`
1. 既有 `LUMOS_SKIP_NOTE_AUDIT`、`LUMOS_SKIP_DRIFT_CHECK` 都是「只認 1、印一句、記 `skipped-env`」;spec 對 reread 只說不跑,沒說記帳,而 S7 的 `skipped` 也沒涵蓋它。
2. 兩週量測用 `skipped` 算「提醒被跳過的比例」;不記帳時環境變數略過會看起來像「沒有那次推送」,分母偏小。理由放行:這是只提醒版,影響量測分母而不影響放行。

## 已讀,無 finding
- 共用函式 `_notes_touched_in_range`:抽自 `_notes_status_flipped` 現有的 `git log --format= --name-only -z -M` 那段,回路徑清單、失敗回 None,做法與既有一致(既有函式本來就經模組全域 `_ns_git`)。
- 範本載入共用:既有 `_note_audit_prompt` 剝 `# SPDX-` 行與開頭 `<!-- -->` 的邏輯與 spec 描述一致;改一次掃描替換對正常輸入輸出不變。
- 判定者模型函式加參數:既有兩個呼叫點(`scripts/lumos:26247`、`26390`)靠預設值不變,做法沿用。
- 閘名 `note-reread` 與 `_KNOWN_GATES`:登記方式(單一元組加註解)照既有;`skipped` 前綴會被 gov 統計辨認。
- `_BOOKKEEPING_DIRS`:單一常數、無其他寫死副本,加一項即覆蓋所有消費者。
- 掛鉤:接在存量漂移那段之後、`pp_stop_if_signaled`、獨立上線標記行,寫法沿用;`note-audit reread-check` 不含 `note-audit check`、也不含漂移標記 `drift check`,標記互不干擾。
- CI:接在 drift check 之後、沿用 `if: github.event_name == 'push'` 與 origin/HEAD 補設;`continue-on-error` 是本檔第一次使用、跟 `|| true` 重複,屬風格,不列。
- 紀錄檔與項目檔形狀:檔名正規式自成一套、用 `_write_lf`、項目檔用 `_note_audit_work_dir` 與 `---本文---` 分隔,沿用既有;不同於 `note-verdicts` 的檔名前綴是有意的,且 spec 說明了不互讀。
- `_lens_git` 單次逾時 20 秒、reread-check 30 秒總上限:spec 已說每次 git 呼叫前看截止時間,最壞多出一次呼叫的時間,屬量級說明,不列。

最高等級:major;blocking 共 4 條
