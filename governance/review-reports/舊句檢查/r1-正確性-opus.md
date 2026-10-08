severity: major

# 設計審 r1:正確性-opus(舊句檢查_計劃,凍結審材 r1-snapshot.md)

實驗環境:`git clone --shared` 到 `…/82c93a23…/scratchpad/osr1c`(與審材同一提交 8969cee9);rtb 用實驗報告指的唯讀複製 `…/scratchpad/ose/rtb`。
對照法:寫了 `osr1c/governance/eval/drift-exam/old-sentence/spec_variant.py`,匯入參考實作後只替換一處「照 spec 字面」的偏差,跑同一組 9 題 + rtb 182 個程式提交 + 工具鏈 300 個提交,跟未替換的基線逐筆比。基線重現了 P4r2(rtb 91 筆、要處理 20;工具鏈 1 筆只列出;9 題擋 7),可信。結果在 `…/scratchpad/osr1out/*.json`,比對器 `osr1out/cmp.py`。

| 變體(只改這一處) | 9 題 | rtb 182 | 工具鏈 300 |
|---|---|---|---|
| 程式檔判定只用 `_drift_probe_is_py`(不排除 docs/、governance/) | 同 | 同 | **1 → 6 筆;要處理 0 → 1** |
| 抽定義改用 `_drift_py_names` + 類別層(照 spec) | 同 | 同 | 同 |
| 路徑只看 Python 檔、檔名免形狀過濾 | 同 | 同 | 同 |
| 同上 + 檔名照字面「終點樹沒有這個路徑」 | 同 | 同 | 同 |
| 句子只用句號分號切(不切 !?) | 同 | 同 | 同 |
| 撤除字樣少 "Superseded" | 同 | 同 | 同 |
| 家只認終點樹 / 家只認 Python 檔 | 同 | 同 | 同 |

## F1 m1 的表態提示遇到旗標類名稱時,照貼就失敗
severity: major
blocking: 是
引句:「確定照留就 `lumos drift ack <節點> <行號> --kind m1 --name <名稱> [--name <名稱>…] --reason "…"`」
file: `scripts/lumos:37581`
1. 三類名稱裡有一整類是旗標(`--restore` 這種;P4r 報告〈5〉#4 的觸發名就是 `--restore`)。提示照字面印成 `--name --restore`。
2. `drift ack` 用的是一般 argparse(`scripts/lumos:37581` 起的 `dra` 子解析器)。實測:`--name --restore` → argparse 把 `--restore` 當成另一個選項,`error: argument --name: expected one argument`,rc 2;只有 `--name=--restore` 才解析得到。
3. 所以旗標類的每一筆,照提示貼都拿到 rc 2;block 模式下使用者在這一步卡住,只剩 `LUMOS_SKIP_DRIFT_CHECK=1`(連 c1–c5 一起跳)。`_drift_sh` 加引號也沒用(shell 拿掉引號後 argparse 看到的一樣)。
4. 改法:提示一律印成 `--name=<名稱>`;[S4] 加一個旗標名稱照貼提示能成功表態的案例。

## F2 撤除節第②種在現在的工具鏈圖譜上多半誤觸發,約 480 行被靜默跳過
severity: major
blocking: 是
引句:「節內任何一行獨立的引用區塊(`>` 開頭)含撤除字樣時,從那一行到節尾(含子節)不看」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:333`
1. 拿參考實作的 `Note.ret_full2` 減掉 `ret_full`,數現在工具鏈圖譜「只因第②種才不看」的非空行:10 篇、603 行(rtb 0 篇)。逐篇看觸發行:
   - 真的在宣告「以下是歷史」的只有 2 篇:`Systems/記憶過期清掃` L32(107 行,就是拿來設計這條規則的那篇)、`Verification/2026-08-22_受波及合約測試真跑閘落地` L15(「這篇已失效」,15 行)。
   - 其他 8 篇都不是宣告,是引用區塊裡剛好出現撤除字樣的子字串:`Projects/code側刪除傳播守衛_計劃` L71「golden **已凍結**」→ 139 行;`Projects/派工時自動補清單_計劃` L61「當舊主張**撤掉**」→ 88 行;`Verification/2026-08-22_成本欄接上與撤除兩階段` L24「**撤除** hook 一刀刪炸掉…」→ 80 行;`Projects/送審前impact鏡頭機械化_計劃` L29 講的是**另一篇**計劃「(已結案,status: superseded)」→ 60 行;`Projects/主session鏡頭利用率_計劃` L47「硬約束**撤掉**兩次」→ 56 行;`Projects/精簡版update指令_計劃` L22、`Systems/convergence-evidence-gate` L70、`Projects/公開精簡版_計劃` L91 各因「作廢」觸發。
2. 照 spec 實作,這 8 篇從觸發行到節尾(多半就是一級標題底下的整篇後半)的舊句一律漏掉,而且被跳過的句子不記帳,兩週帳看不到。〈誠實界線〉寫「P4r2 重跑報告點名、還沒踩到」,現況已經踩到:單篇超過 100 行的已有一篇是誤觸發(139 行)。
3. 根因:第①種(小標題後第一行)用這組字樣是合理的訊號;第②種放在節中任意位置,「撤除/撤掉/作廢/已凍結」大多是描述動作的動詞,不是宣告。另外 `NOT_YET` 只認「未」緊接動詞,「未被取代」「沒有作廢」照樣算撤除(同一組字樣,①②都受影響)。
4. 改法擇一:第②種只認帶指向詞的宣告(例:引用區塊同時含「以下/下面/後面/這篇/本節」與撤除字樣),或第②種只用「已失效、不是現況、歷史紀錄、superseded」這些名詞性字樣、不收動詞;或照報告自己寫的回頭條件,收窄到「只到下一個任何層級的標題」。無論選哪個,[S2] 加一個反例:引用區塊寫「golden 已凍結」的節,後面的舊句照列。

## F3 定義快取鍵只有 blob 雜湊,抽法改版或換 Python 後會一直拿到過期結果
severity: major
blocking: 是
引句:「每個 blob 的定義集合以 blob 雜湊為鍵」
file: `scripts/lumos:26790`
1. 快取放在 `git-common-dir`,多個工作樹共用、跨 lumos 版本常駐,20000 筆照最近用過的順序留(常用的 blob 永遠不會被丟掉)。鍵裡沒有「抽法版本」,也沒有 Python 版本。
2. 失敗場景一:之後修抽法(例:照 F6 補上 tuple 拆包指派或條件式裡的模組層指派),沒改過的 blob 照樣命中舊快取、拿到舊集合 → 「終點整個 repo 的定義」漏掉新抽法才認得的名稱 → 別的檔刪掉同名定義時被誤判成消失;錯誤一直留著,直到那個 blob 被改掉。
3. 失敗場景二:本 repo 慣用多個工作樹(lumos-gvc 等),兩個工作樹的 lumos 版本不同時共用同一份快取,誰後寫誰算,結果看推送順序而定。
4. 失敗場景三:「剖不動」如果也進快取,用 3.14 剖不動、換成新版 Python 能剖的檔會一直被當成剖不動(反過來也一樣)。
5. 改法:鍵改成 `(抽法版本常數, sys.version_info[:2], blob 雜湊)`,或檔頭存版本、版本不同就整份丟掉;[S5] 加「版本常數變了就不命中」的案例。附帶一提:時間到沒跑完的那次要不要把已經剖好的寫回快取,spec 沒寫;不寫回的話,冷快取剖不完的大 repo 每次推送都從頭來、永遠跑不完。

## F4 程式檔範圍照 spec 字面會跟參考實作不一樣,工具鏈的驗收數字對不上
severity: major
blocking: 是
引句:「範圍裡改到的每支 Python 檔(`_drift_probe_is_py` 判定)」
file: `scripts/lumos:26784`
1. `_drift_probe_is_py` 只看副檔名或首行,**不排除** docs/、governance/;參考實作 `Code.kind` 先過 `_excluded`(docs/、governance/、建置目錄、lock 檔)(`old_sentence_exp.py:121`)。既有的 `_drift_probe_code_path`(`scripts/lumos:26777`)才有排除,但 spec 只點名 `_drift_probe_is_py`。
2. 實驗(只換這一處):9 題、rtb 182 個提交逐筆相同;工具鏈 300 個提交從 1 筆變 6 筆、要處理 0 → 1。多出來的:
   - 0cbc5549 改了 `governance/eval/sync-nudge/probe_sync.py`,`tool_use` 被判消失 → 4 篇筆記裡講 Claude 逐字稿「tool_use 區塊」的行被列出(誤報;那是訊息格式的名字,不是那支程式的定義)。
   - 1474d5d2 從 `governance/eval/retrieval_eval.py` 拿掉 `_macro_on`,`Systems/retrieval-ranking` 摘要行還寫「新增 `_macro_on`」→ 要處理(查過終點與現在的 HEAD 都沒有這個定義,**是真舊句**)。
3. 所以兩種讀法各有得失,但 spec 同時寫了「實作的驗收以 P4r2 那份數字為準」:照字面實作,工具鏈那一欄驗收過不了;為了對上數字而排除 governance/,又跟〈做法〉1 的字面不符。實作者兩邊都會被審。
4. 改法:明寫程式檔判定 = `_drift_probe_code_path` 且 `_drift_probe_is_py`(與參考實作同範圍);要不要把 governance/ 下的評測腳本納進來另外決定,決定了就重跑驗收數字。

## F5 共用 60 秒預算讓 block 模式的 m1 被前一段拖到必擋
severity: major
blocking: 是
引句:「`m1` 用 drift check 同一個截止時間(`_DRIFT_BUDGET_SEC` 起算,前面那段用掉的就少了)」
file: `scripts/lumos:28258`
1. spec 自己的〈實務隱患・效能〉記了:rtb 新分支首推,前面 c1–c5/probe 就用掉 67 秒(預算 60 秒)。那種推送輪到 `m1` 時一秒都不剩。
2. warn 模式只印「沒跑完」,沒問題;但 `old_sentence=block` 時照 spec「時間到算要處理」,結果是:`drift_check.gate=warn` 的專案,因為**另一段檢查**太慢,這次推送被 `m1` 擋下。這一筆不能用 ack 解掉,只能 `LUMOS_SKIP_DRIFT_CHECK=1`,而那個開關連 c1–c5 一起跳過。
3. 這跟 [S3]「`drift_check.gate` 為 off 或 block 都不改變 `m1` 的行為與回傳碼」相衝突:gate 是 off 時 m1 有整整 60 秒,gate 是 warn/block 時前段會吃掉 m1 的時間 → gate 的值實際上會改變 m1 的回傳碼。
4. RETIRE-IF 轉擋的條件只看準度與筆數,沒看「沒跑完」的比例;兩週後轉 block,rtb 新分支首推就會固定被擋。
5. 改法擇一:m1 保底自己的預算(例:m1 另給固定秒數、不從前段剩下的算);或把「沒跑完的比例」加進 RETIRE-IF 的轉擋條件;[S3]/[S6] 加「前段用完預算、m1=block」的案例並寫明期望。

## F6 定義抽法照 spec 擴充 `_drift_py_names`,跟參考實作的集合不同
severity: minor
blocking: 否
引句:「模組層與類別層的指派名(擴充 `_drift_py_names`,加一個參數開類別層指派,既有呼叫端不變)」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:200`
1. 參考實作的 `_assigns` 會認:tuple 拆包的指派(`A, B = …`)、模組層 `if`/`try` 裡的指派、沒給值的型別標註(`x: int`,資料類別的欄位)。`_drift_py_names` 只認模組層直接的 `Name` 指派,型別標註還要有值(`scripts/lumos:26790` docstring)。spec 只說「加一個參數開類別層指派」。
2. 在 rtb 頂端量:參考實作認得、照 spec 抽不到的合格名稱有 279 個(例 `INTENT_CORRECT`、`EXIT_BLOCK` 是 tuple 拆包;rtb 類別層沒給值的型別標註有 1315 個)。歷史重放 182/300 個提交**沒有差別**,所以目前只是 spec 跟參考實作不一致:這類名稱被改名或刪掉時會漏掉。
3. 改法:明寫類別層也收「沒給值的型別標註」與 tuple 拆包;要不要收條件式模組層,跟參考實作對齊或寫明不收。

## F7 路徑類的判準寫得不夠,照字面有兩處跟參考實作不同
severity: minor
blocking: 否
引句:「路徑=終點樹裡沒有這個路徑」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:569`
1. 檔名的「消失」沒寫判準。參考實作是「終點沒有任何檔叫這個檔名」;照字面拿「終點樹裡沒有這個路徑」去比檔名,檔名幾乎永遠不等於一條完整路徑 → 刪掉 `pkg_a/__init__.py` 時 `__init__.py` 被判消失,即使別的套件還有 `__init__.py`,每一行提到 `__init__.py` 的筆記都被列出。
2. 「旗標與路徑不受這條限制」:參考實作 `_shape_ok` 只放過含 `/` 或結尾 `.py` 的名稱,沒副檔名的 Python 腳本檔名(`lumos`、`pre-push`)照樣要過形狀過濾。照 spec,刪掉或改名一支沒副檔名的 Python 腳本,檔名以整字比對會命中大量筆記(工具鏈裡「lumos」幾乎每篇都有)。
3. 參考實作的路徑迴圈跑的是**所有**程式檔(含 .sh/.js),spec 限定 Python。
4. 「整字」對路徑的邊界沒寫;參考實作 `_mk_rx` 把 `/ . -` 當成非邊界,所以 `foo.py` 不會命中 `other/foo.py`;照一般 `\b` 會命中。
5. 歷史重放(py 限定 + 檔名免過濾;再加字面檔名判準)兩版都 0 差別,所以是規格精度問題:把檔名判準、沒副檔名的檔名要不要過濾、比對邊界照參考實作寫進 spec。

## F8 切句字元與撤除字樣表,spec 的文字跟參考實作少了一些
severity: minor
blocking: 否
引句:「在括號外剝掉括號內容,再用句號、分號切」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:420`
1. 參考實作切的是 `。;;!?!?`,spec 只寫句號、分號。
2. spec 列的 `RETIRE_WORDS` 有 11 個,參考實作多一個大寫的 `Superseded`(`old_sentence_exp.py:260`);照 spec 列表做、而且大小寫敏感比,「> Superseded by …」這種旗標就認不到。
3. 「尚未/還沒/未 + 撤除…」的「…」沒展開;參考實作是固定正則 `NOT_YET`(`:262`),而且只要命中就整行不算旗標(同一行另有真的撤除宣告也一樣)。
4. 歷史重放 0 差別;照參考實作把三樣逐字寫進 spec(或寫「逐字搬 `RETIRE_WORDS`、`NOT_YET`、切句字元」),測試逐項釘。

## F9 分層的「家」沒寫看哪一棵樹、算不算非 Python 程式
severity: minor
blocking: 否
引句:「這次任何一支改到的程式檔的家」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:598`
1. 參考實作 `homes_any`:起點樹與終點樹兩邊的 about_code 都算,改名時新舊兩條路徑都算,而且是所有程式檔(不只 Python)。
2. spec 只寫「about_code 列了它」。最常見的情況是:刪掉一支檔,同一個提交順手把 about_code 那一項也刪掉、正文沒改。只看終點樹的話,那篇就不算家 → 舊句從要處理掉到只列出,block 模式擋不到。
3. 歷史重放(只看終點樹 / 只看 Python)0 差別;照參考實作寫明「起點與終點兩棵樹、新舊路徑、所有程式檔」。

## F10 「通用 ack 句」要改的地方其實碰不到 m1
severity: minor
blocking: 否
引句:「`_drift_report_must` 那行通用 ack 句與 `_drift_print_hints` 的去重鍵都改成從同一處產生」
file: `scripts/lumos:28293`
1. 同一節又寫「`m1` 的要處理不進既有 `must` 清單,自己印、自己記帳」。`_drift_report_must` 的通用 ack 句只對 `must` 裡的種類印(`for k in sorted(kinds)`),m1 永遠不會出現在那裡。
2. 照字面,要嘛改了一段對 m1 沒作用的程式,要嘛實作者為了讓它有作用把 m1 塞回 `_drift_report_must`,反而違反「不進 must」。寫明:m1 自己印表態句,用同一個產生器(並照 F1 印成 `--name=`)。

## F11 名稱集合的「涵蓋」是單筆還是多筆聯集,沒寫清楚
severity: minor
blocking: 否
引句:「一筆發現的名稱集合**全部**被同路徑同原文的 `m1` 表態涵蓋才算已表態」
file: `scripts/lumos:27404`
1. 「仿 c2/c3」的既有做法是只看 seq 最大的那幾筆,要它們各自涵蓋(`_drift_split_acked`)。這一行提到 A、B 兩個名稱,作者先 `--name A`、再另外 `--name B` 表態:照 c2/c3 讀法只看最後那筆 {B} → 沒涵蓋 → 照列;照聯集讀法 → 已表態。兩種實作都符合字面,[S4] 分不出來。
2. 寫明選哪一種,[S4] 加上「分兩次表態」的案例。

## F12 沒起點時 block 模式的回傳碼沒寫
severity: minor
blocking: 否
引句:「起點是空樹(新分支找不到主線、或截到上線點前)時 `m1` 這次不判」
file: `scripts/lumos:25801`
1. 治理帳的 kind 把「時間到」與「沒起點」併成 `old-sentence-incomplete`;時間到在 block 模式算要處理。實作者很自然會寫成「incomplete + block → 回 1」,結果 block 專案的第一次推送(找不到主線)永遠被 m1 擋,而且沒辦法 ack。
2. 另外,括號裡的「或截到上線點前」跟程式對不上:`_nodehome_clamp_base` 碰到空樹起點會改成上線點,所以截過之後不會是空樹;只有找不到主線、而且也沒有上線點才會是空樹。
3. 寫明:沒起點不論模式都回 0、只印;括號改成跟程式一致的說法。

## F13 終點剖不動的文字比對寫法太窄,也沒說整個 repo 的其他剖不動檔怎麼辦
severity: minor
blocking: 否
引句:「那支檔裡有 `def 名`、`class 名`、`名 =` 或 `"--旗標"` 字樣就當它還在」
file: `scripts/lumos:26816`
1. `"--旗標"` 只認雙引號,`add_argument('--foo')` 單引號的寫法認不到;`名 =` 認不到 `名=1` 與 `名: int = 1`。這幾種情況名稱會被當成消失。既有的 `_drift_py_def_re` 已經處理了這些寫法,應該沿用。
2. 「那支檔」指的是範圍裡改到的檔。頂端**沒改到**但剖不動的檔,它的定義不會進入「整個 repo 的定義」,別處刪掉同名定義時會被誤判成消失。spec 沒說這些檔也要做文字比對。
3. 兩個 repo 目前的頂端都是 0 支剖不動(實測工具鏈 46 支、rtb 277 支),所以現在還沒發生;寫明沿用 `_drift_py_def_re`、比對範圍含頂端所有剖不動的 Python 檔即可。

## F14 轉擋門檻跟同一道閘既有的 RULE 不一致 ⚠
severity: minor
blocking: 否
引句:「準度低於 60%、或任一次推送超過 30 筆 → 不轉擋、留在提醒」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:20`
1. 同一道閘(治理帳 gate 都是 `drift-check`)的既有 RULE 寫:預設改 block 要考卷正例全對、工具鏈最近 100 個提交重放每筆要處理都判成真、每次要處理 ≤5。m1 另開一個開關,門檻降到準度 60%、≤30 筆。
2. 那條 RULE 沒寫 `[confirmed:]`,照 CLAUDE.md 算線索、不算依據,所以標 ⚠。不過 spec 應該明講 m1 的開關不受那條 RULE 管、理由是什麼,不然日後有人照那條 RULE 審,會把轉擋判成違規。

## 六組核心裁定逐組驗(正確性鏡頭)
- A 另開判定函式、不進 must:做得出來;`_drift_check_core`、考試都沒有用到 `_DRIFT_KINDS`(grep 只有 4 處:`_drift_load_acks`、`_drift_ack_args_err`、`_drift_scan_print`、argparse 的 choices),加 m1 不會動到考試與噪音基準。唯一不一致見 F10。
- B 兩個開關的控制流:做得出來,但 `cmd_drift_check` 在 gate=off 時現在是直接 return(`scripts/lumos:28257`),要改結構;`_drift_config` 現在回 3 個值,有兩個呼叫端(`:28254`、`:28420`)要一起改;沒寫 `gate`、只寫 `old_sentence` 的設定,現在會走提早回傳的分支,擴充時要先讀 `old_sentence`。`old_sentence` 寫了不合法的值怎麼辦沒寫(建議同 gate:照預設並提醒)。gate 的值實際會透過預算改變 m1 的結果,見 F5。
- C 表態名稱集合:旗標名稱照提示表態會失敗(F1);涵蓋的語意有兩種讀法(F11)。
- D 時間到 warn/block:warn 做得對;block 會被前段拖到必擋(F5);沒起點的回傳碼沒寫(F12)。
- E 三類消失判準與終點剖不動:定義名全 repo 比對跟參考實作一致;範圍(F4)、路徑(F7)、文字比對(F13)有落差。
- F 字眼表 P4r2:`HIST_WORDS` 逐字核對 25 個 + 3 個詞組,跟參考實作一致;切句字元與撤除字樣見 F8;撤除節第②種見 F2。

## 合約行(★INVARIANT★)逐條
- `Systems/guard-kill` L20(guard kill 的 rc 優先序)、L21(`--json` 模式 stdout 只有一行 JSON):m1 只動 `drift check`/`drift ack`,不碰 guard kill 的程式路徑與輸出,不影響。
- `Systems/lumos-cli-write`:沒有 ★INVARIANT★ 行。
- `Systems/存量漂移守衛`:沒有 ★INVARIANT★ 行;L22 那條 RULE(開關讀頂端提交)spec 已經在〈實務隱患・守衛面〉照搬;L20 那條見 F14。
- `Systems/lumos-cli-read` 的 d1(讀指令不寫帳):m1 只在 `drift check`(閘)寫帳,`drift scan` 不跑 m1,不違反。

## 實務隱患(正確性鏡頭逐類)
- 不可逆:無。只讀程式與筆記、只印與記帳;快取在 git 目錄,刪掉即可。
- 金流/對外送出:無。本機命令列,不打外部服務。
- 守衛面:碰到。F1(照提示表態會失敗)、F2(大片區塊被靜默跳過)、F5(被前段拖到必擋)都會讓人更傾向直接用 `LUMOS_SKIP_DRIFT_CHECK`。
- 快取正確性:碰到,見 F3。
- 資安:`--name` 走一行檢查、印出前過 `_esc_clean`,正確性鏡頭沒看到新洞;`--name ""` 空字串會通過 `_drift_one_line`,建議順手擋掉(不算 finding)。

## 各節
- 開頭欄位與白話段:已讀,無 finding。
- PRIOR-ART/RETIRE-IF/REVISIT:F4、F14;REVISIT 的 grep 字串跟 `_gate_event` 的輸出格式(`json.dumps`,預設分隔字元)對得上。
- 範圍:已讀,無另外的 finding。
- 做法 1:F3、F4、F6、F7、F12、F13。
- 做法 2:F2、F8、F9。
- 做法 3:F1、F5、F10、F11。
- 條款:[S1]–[S6] 缺的案例已經分別寫在 F1、F2、F3、F5、F11。
- 回退:已讀,無 finding(`_drift_load_acks` 會濾掉不認得的種類,查過屬實)。
- 誠實界線:F2(「還沒踩到」跟現況不符)。

最高等級:major;blocking 共 5 條
