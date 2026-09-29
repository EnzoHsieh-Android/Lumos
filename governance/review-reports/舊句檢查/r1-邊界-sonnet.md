severity: major

審查鏡頭:邊界與輸入。實驗在 `os-r1/bsn/`(shared clone + 直接載入 `scripts/lumos` 與參考實作 `old_sentence_exp.py` 跑怪輸入),未改 repo。

## F1 路徑類的「檔名」沒有消失判準,字面照做會把仍存在的同名檔當成消失
severity: major
blocking: 是
引句:「這次被刪或改名的 Python 檔的舊路徑,和它的檔名」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:557-563`
1. 〈做法〉1 說路徑類抽「舊路徑和它的檔名」,但〈消失判準〉只寫「路徑=終點樹裡沒有這個路徑」。「檔名」(basename,例 `util.py`、`__init__.py`、`conftest.py`)不是樹裡的路徑,字面判準對它永遠成立(除非該檔在 repo 根)。
2. 輸入:刪掉 `pkg_a/util.py`、終點還有 `pkg_b/util.py`。字面照做:`util.py` 判為消失,筆記裡所有提到 `util.py` 的行(指的可能是 `pkg_b/util.py`)都列成 `m1`,而且路徑類不受形狀過濾(`.py` 一律放行)。
3. 參考實作有一道 spec 沒搬的條件:basename 只有在終點樹沒有任何同名檔時才算消失(`if bn not in tip_bases`)。實驗的 16/65 等成績是含這道條件量的,spec 少寫它,〈驗收以 P4r2 數字為準〉會對不上。
4. 建議:補寫 basename 的判準(終點樹任何位置都沒有同名檔才算),並在 S1 加一個「兩處同名檔只刪一處不列」的例。

## F2 表態指令的 `--name --旗標` 用 argparse 走不通,旗標類的名稱印出的指令照貼就回 2
severity: major
blocking: 是
引句:「`lumos drift ack <節點> <行號> --kind m1 --name <名稱> [--name <名稱>…] --reason "…"`」
file: `scripts/lumos:37581-37585`
1. 旗標類名稱長得像 `--dry-run`。`drift ack` 是 argparse,`--name --dry-run` 會被當成 `--name` 少了值,實測 `error: argument --name: expected one argument`、rc 2;同理名稱以 `-` 開頭一律不行。
2. 只有 `--name=--dry-run` 才過。spec 的提示範本與 S4 的例句都寫空白分隔,旗標類的 m1(spec 明列的三類名稱之一)一筆發現的提示就是壞指令。
3. 一筆的名稱集合若同時含旗標,提示要整條改成 `--name=<名稱>` 形式,而且 S4 要有一個「名稱以 `--` 開頭」的案例;否則測試只驗定義名、上線後才踩到。

## F3 提示指令被 `_esc_clean(x, 300)` 截斷,名稱多的那一行印出的是被截掉的指令
severity: minor
blocking: 否
引句:「`_drift_report_must` 那行通用 ack 句與 `_drift_print_hints` 的去重鍵都改成從同一處產生、去重鍵帶名稱集合」
file: `scripts/lumos:27672`
1. `_drift_print_hints` 每條指令都過 `_esc_clean(x, 300)`,超過 300 字補「…」。`m1` 的指令長度隨名稱集合變長:固定部分約 80 字、每個名稱約 25 字,約 9 個名稱就超過。
2. 輸入:筆記一行寫「改名對照:a_x、b_x、…(十幾個)」,那些名稱全消失。一筆 = 一行 = 十幾個名稱,印出的 ack 指令尾巴被截斷、少了 `--reason`,不能直接貼。
3. spec 只提「去重鍵帶名稱集合」沒提長度。建議 m1 提示不受 300 上限、或名稱過多時印「用 `--name` 列全部(見上列名稱)」。

## F4 `_drift_config` 現有的提早 return 會讓只寫 `old_sentence` 的設定被靜默忽略
severity: major
blocking: 是
引句:「多回 `old_sentence` 的值(同一支讀同一個鍵,不另開第二支」
file: `scripts/lumos:28196-28219`
1. 現行 `_drift_config` 有六個提早 return(檔不存在、壞 JSON、沒有 `drift_check`、`drift_check` 不是物件、`gate` 為 null、`gate` 值不合法),每個都直接回預設 gate。`old_sentence` 若只加在最後一個 return,以下設定被忽略且無警告:`{"drift_check": {"old_sentence": "block"}}`(沒寫 gate,走 `g is None` 那個 return)。
2. 這正是 spec 規畫的收尾動作:兩週後把 `m1` 轉 block,人最自然的寫法就是只寫 `old_sentence`。結果轉了也不擋,而 REVISIT 的判讀看不出來(帳上 kind 還是 `old-sentence-warned`)。同理 `gate` 拼錯時 `old_sentence` 也一起失效。
3. `old_sentence` 自己寫了不合法的值(例 `"on"`)spec 沒定,既有慣例是警告 + 用預設,要寫進 S3。
4. 另:回傳從三元組變四元組,既有呼叫端 `scripts/lumos:28420`(doctor,解三個)與測試 `scripts/test_lumos.py:51580` 都會 `ValueError: too many values`;spec 沒列這兩處。
5. 建議:`old_sentence` 與 `gate` 各自獨立解析(先取 `dc` 再各驗各的),S3 加「只寫 old_sentence」「gate 壞值 + old_sentence 好值」兩個組合。

## F5 Python 檔非 UTF-8 時,spec 的「剖不動」例外組接不到解碼錯誤
severity: minor
blocking: 否
引句:「剖不動(語法錯誤、合併衝突殘留、記憶體或遞迴過深——沿用 `_drift_py_names` 的例外組)」
file: `scripts/lumos:26795-26801`
1. `_drift_py_names` 的 except 只包 `ast.parse`。spec 又說「utf-8-sig 讀檔」,而解碼發生在剖之前。帶 `# -*- coding: latin-1 -*-` 的舊 Python 檔(位元組不是合法 UTF-8)在字面實作下 `UnicodeDecodeError` 直接往外拋。
2. 這支判定接在 pre-push 與 CI 裡、〈控制流〉明說 warn 不影響回傳碼;例外沒接住會讓行程以非 0 結束,warn 模式也擋推送。
3. 建議把解碼失敗併進「剖不動」(起點版不判、終點版走文字比對時也要能讀,讀不了就當還在)。⚠ 實作多半會順手用 `errors="replace"`,但 spec 沒寫、S1 也沒有測試點。

## F6 形狀過濾的「大小寫混合」字面上放進所有首字大寫的英文單字
severity: minor
blocking: 否
引句:「形狀過濾:定義名要 4 個字以上、而且含底線或大小寫混合」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:279-283`
1. 參考實作的 `_shape_ok` 是「有任一大寫且有任一小寫」,`Note`、`Plan`、`Result`、`Config` 都過。整字比對又是區分大小寫、且用 ASCII 邊界,句首的英文單字 `Note:`、標題 `Result` 都命中。
2. 輸入:重構時刪掉 `class Result`(整個 repo 沒有第二個),範圍內任何筆記寫到 `Result` 的行都成 `m1`。中文為主的圖譜實驗沒踩到(英文散文少),英文圖譜的專案會踩。
3. 建議明寫:大小寫混合指「小寫後接大寫」(CamelCase 內部有轉折),或把首字大寫的單字排除。

## F7 撤除節判準的否定只認緊鄰的「未」,「未被取代」「沒有作廢」「撤除條件」都會被當成宣告
severity: minor
blocking: 否
引句:「但「尚未/還沒/未 + 撤除…」不算——整節連同子節不看」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:260-292`
1. 實測 `_is_banner`:`> 這條規則未被取代` = True(「被取代」是撤除字樣、否定式只列「未取代」不含「未被取代」)、`> 沒有作廢` = True、`> 尚未被撤除` = True、`> 撤除條件:連續 N 週零觸發` = True。
2. 本 repo 的鐵則要求 RULE 寫 `[retire:條件]`、`RETIRE-IF:` 這類「撤除條件」句,常寫成引用區塊;其中一句落在小標題底下,②會把「那行到節尾(含子節)」整段隱形;在一級標題底下則是「那行到整篇尾」。
3. 這是漏報方向(不是誤報)、誠實界線已承認②在一級標題的風險,但沒承認「否定式沒涵蓋」;REVISIT 那天「被②豁免的行數」計數也不會把這種假宣告與真宣告分開。
4. 建議:字眼判準改成「行內有撤除字樣且前 3 字內沒有未/沒有/不/尚」,或至少 REVISIT 計數時把含「撤除條件」的引用行分開列。

## F8 「句」的切法在括號巢狀、英文句點、括號不成對時的行為 spec 沒定
severity: minor
blocking: 否
引句:「在括號裡只看括號內,在括號外剝掉括號內容,再用句號、分號切」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:401-431`
1. 巢狀括號:括號外剝除只剝最內層,`現況:foo_bar_x 還在用(含 (內) 曾改過)` 剝完剩 `還在用(含 \0\0\0 曾改過)`,外層括號裡的「曾」還在句裡 → 判成歷史句不列(實測 True)。但同一句若名稱在括號內只看內層,兩個位置規則不對稱。
2. 「句號」spec 沒寫是 `。` 還是也含 `.`;參考實作只切 `。;;!?!?`,英文句點不切(名稱與路徑常含 `.` 所以不能直接切)。輸入 `old style removed. foo_bar_x is used now`:`removed` 在前一句卻算同一句,被放過。
3. 不成對:行首有孤立的 `(`(例 `(1 現況:foo_bar_x…`),參考實作把「從 `(` 到行尾」當括號內容,行頭到 `(` 的部分不看。實測不會誤放也不會誤列,但跟「括號外剝掉括號內容」的字面不同,S2 沒有不成對的案例。
4. 建議:S2 加巢狀與孤立括號的釘;spec 寫明「句號 = `。`,英文句點不切」。

## F9 定義名的抽法對條件式、元組、動態定義的覆蓋跟 spec 的「條件式」說法不一致
severity: minor
blocking: 否
引句:「模組層與類別層的指派名(擴充 `_drift_py_names`,加一個參數開類別層指派,既有呼叫端不變)」
file: `scripts/lumos:26802-26813`
1. spec 寫「所有 `def`/`class` 名(含巢狀與條件式)」——對 `ast.walk` 成立。但指派名沿用 `_drift_py_names` 只走 `tree.body`。實測:`try: MAX_RETRY = 3 except …: MAX_RETRY = 4`、`if a: OTHER_X = 1`、`A_ONE, B_TWO = 1, 2` 三種都抽不到(回傳的指派集合是空的)。
2. 輸入:起點是模組層 `MAX_RETRY = 3`、終點把它包進 `try/if`。終點端抽不到 → 名稱判為消失 → 筆記裡講 `MAX_RETRY` 的現況句被誤列。參考實作(`_assigns` 遞迴 If/Try、拆 tuple)沒這個問題,spec 只說「擴充」沒說要遞迴。
3. 動態產生的定義(`globals()[n] = …`、`setattr`):終點改成動態註冊時,靜態的 def 消失、名稱仍在,會誤列。起點端動態的從來不進候選,所以這是單向誤報。旗標同理:`add_argument(FLAG)` 用變數、`add_argument(*names)`、改用 click/typer、只接 `node.args` 的字串常數(參考實作就是如此)。
4. 這些是既有的取捨(誠實界線只寫「只看 Python」),但 spec 沒承認,而且回頭條件(REVISIT)只看準度,量不出這類誤報是哪種造成的。建議明寫「動態定義與非 argparse 旗標不認」並在準度抽判時分類。

## F10 「起點是空樹」的兩個括號說法跟現行 clamp 行為對不上,有上線點時新分支首推會判整段歷史
severity: minor
blocking: 否
引句:「起點是空樹(新分支找不到主線、或截到上線點前)時 `m1` 這次不判」
file: `scripts/lumos:24138-24150`
1. `_lens_push_base` 找不到主線時回空樹,但 `_nodehome_clamp_base` 在有上線點標記時把「空樹」直接換成上線點提交(`return gl`)。所以「截到上線點前」不會產生空樹;沒有上線點標記時才是空樹、`_note_audit_resolve` 回 `base=None`。
2. 輸入:消費專案有上線點標記、新分支找不到主線(rtb 的情境)。實際範圍是「上線點..頂端」,可能整段歷史,不是空樹 → `m1` 會判、候選名稱多、耗時長,而且「先加後刪」(誠實界線寫的)在這種範圍最常發生。spec 描述的行為(不判)只在沒有上線點標記時成立。
3. 建議改成「`_note_audit_resolve` 回 `base=None` 時不判」並註明有上線點的新分支照判。
4. 順帶:SHA-256 的 repo 空樹編號不同於 `_EMPTY_TREE_SHA`(`_drift_empty_tree` 有註解),`base=None` 的判斷要跟著 `_note_audit_resolve` 的實際回值,不要自己比常數。

## F11 掃描時間只在「每篇筆記前」檢查,名稱多時一次比對可以很慢,block 模式會變成無出路
severity: minor
blocking: 否
引句:「每剖一支檔前、每掃一篇筆記前檢查;剖檔在行程內不可中斷,最壞多出一支檔的時間。」
1. 實測(`t2.py`,本 repo 圖譜 3.7 MB、6 萬行):把消失名稱做成一個交替式正則,1000 名 4.8 秒、5000 名 28 秒、20000 名 98 秒,跟名稱數線性。單一筆記比對的耗時不算「一支檔」,但一篇筆記通常很小,所以逾時檢查有效;問題在總量,大型刪除(整個模組被刪、快取上限 20000 筆)一次推送就超過 60 秒預算。
2. warn 模式只印「沒跑完」;block 模式照 spec 算「要處理」(判不了),而 `drift ack` 只能綁具體的行、對「沒跑完」沒有出路,只剩 `LUMOS_SKIP_DRIFT_CHECK=1`。這是大型重構那一次推送的必然狀況,不是稀有輸入。
3. 只改文件、沒有改到 Python 檔的推送也走同一條路徑:spec 沒寫「範圍裡沒有 Python 檔就不建終點整 repo 的定義集合、不掃筆記」,字面上可以每次都組一遍;〈零筆也記帳〉又讓純文件推送每次都寫一筆 `old-sentence-clean`,REVISIT 的分母被灌水。
4. 建議:候選名稱為空(或範圍沒有 Python 檔)時直接短路並記 `old-sentence-clean`(或不記)、寫明;名稱數超過某個數(例 3000)時分批比對、每批前查時間。

## F12 筆記讀取路徑沒指定,BOM 筆記與無法解碼的筆記行為不同;終點「整個 repo」沒說排除目錄
severity: minor
blocking: 否
引句:「掃圖譜筆記的正文、摘要(summary)、決策欄(`_notelines_regions` 的 body/summary/decisions);圍欄內不掃(`_visible_lines`);開頭欄位(about_code、related…)不掃。」
file: `scripts/lumos:24693-24716`
1. 實測 `_notelines_regions`:帶 BOM 的筆記(`﻿---`)`split_frontmatter` 切不出開頭欄位,整篇每一行都判成 `body`;開頭欄位(about_code、related)被當成散文掃、摘要行不再是 `summary`(分層變成「只列出」)、`about_code` 讀不到家。CRLF 的筆記沒問題(`\r` 被 strip 掉)。
2. 現行 `_drift_tree_env` 用 `utf-8-sig` 解碼,所以沿用它讀筆記就沒事;但 spec 只寫「掃圖譜筆記」沒指定,自己 `cat-file` 再 `decode("utf-8")` 的實作會踩。同一支函式對不能解碼的筆記另有 `env.unreadable`,核心判定把它算「判不了」,`m1` 若沒沿用會靜默略過那篇。
3. 終點「整個 repo 的所有 Python 檔」沒寫排除目錄(參考實作排除 `docs/`、`governance/` 與 `_DELGUARD_EXCLUDE_DIRS`:`node_modules/`、`build/` 等)。字面照做,`node_modules`、`build/`、已提交的 `.venv` 裡同名定義會讓消失的名稱被判成還在(漏報),或反過來讓那些目錄的檔改動也產生候選。本 repo 目前 `governance/*.py` 與 `scripts/lumos` 同名的形狀合格名稱只有 4 個,影響不大,但消費專案不一定。
4. 建議:明寫沿用 `_drift_tree_env` 的解碼與 `unreadable` 處理、以及要排除的目錄清單。

## 各鏡頭逐項結論(規則要求「判不影響也寫為什麼」)

- 中文/Unicode 名稱:`ast` 接受 `def 計算_總額`,形狀過濾要底線才過;整字比對用 ASCII 邊界,中文名稱在中文字旁邊也算命中,子字串式命中(`重計算_總額`)照列。spec 沒定義中文名的「整字」,無失敗場景,列入 F10 之外的已讀。
- 名稱是另一名稱的子字串:`get_user` 對 `get_user_id`、`my_get_user`、`get_user2` 都不命中(實測),旗標 `--dry-run` 對 `--dry-run-x` 不命中,行為正確。路徑 `tests/util.py` 前面有 `/` 不命中 `util.py`,只影響召回。
- 測試檔與正式檔同名定義:整個 repo 比,同名就不列,方向是漏報,不出錯。
- `__init__` 等雙底線名:形狀過濾放行(有底線、長度 ≥ 4),但整個 repo 幾乎必有第二處同名,實務上不會成為候選,不出錯。
- 檔案改名同時改內容:不論 `-M` 或 `--no-renames`,終點整個 repo 比對讓移到新檔的定義不算消失,舊路徑另列,行為正確;唯一問題是 F1 的檔名。
- 空 repo:`_note_audit_resolve` 終點找不到回 2,在 `m1` 之前擋下,不影響本功能。
- 範圍裡只有非 Python 檔:spec 寫明印一行不判;行為見 F11 第 3 點的記帳問題。
- CRLF:筆記端不影響分區與撤除節(實測);表態原文比對用 `.strip()` 去掉尾端 `\r`。
- 「動到核心裁定的六組」:A(判定另開函式)可行,`cmd_drift_check` 的結構撐得住;B 見 F4;C 見 F2、F3;D 不在本鏡頭出問題;E 見 F1、F9、F10;F 見 F7、F8。

最高等級:major;blocking 共 3 條
