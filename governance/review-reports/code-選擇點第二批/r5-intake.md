# r5 收貨紀錄

第五輪代碼審(tier high,上限三輪跑滿後人裁第二次加開的一輪,cap-decision extra-round 與更新後的跑滿回顧在第四輪帳本提交):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r5-snapshot.patch`(範圍 `6857e3d60..c261a1547`,1855 行,資安席整份、不拆),另附修補鏡頭 `r5-repair.patch`(修前 59c41038 → 修後 c261a154)、`r5-repair-binding.json`、`r5-behavior-cases.md`。派工詞只放標記行加一句「先讀完 scratchpad 裡自己那份完整派工詞照做」,完整派工詞由 mk_b2_seats_r5.py 產生;七席都照完整派工詞的格式交回。

## 收貨

- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔(合約席後來又交兩則補充:子集測試 `-k choice` 408 passed、等待迴圈結束,結論不變,存的是它的主報告)。
- report-normalize:七份都已是正規化格式。quote-check:七份全數錨定(對 `r5-snapshot.patch`)。refcheck:邊界席一處 missing 是它寫明「沒讀」的 `governance/residual-index.json`,只是提到檔名、不拿來當證據,其餘全對。seat-check:派工單材料欄沿用前幾輪格式,工具判 vacuous 豁免。
- 圖譜鏡頭:鏡頭備份 `lens-r5.txt` 派工當下還在背景產生(第一次用 `timeout` 指令,macOS 沒有這支、rc127 空檔,改成背景重跑,派工後約一分鐘才寫完)。通才席讀到空檔、架構對齊席沒讀,兩席照實寫固定席未判定;正確性、邊界、資源、資安讀了備份逐條判固定席;合約席依 diff 判不影響、未對照備份。
- 記帳材料:正確性、邊界、通才三席派工材料是 `r5-repair-code.patch` 加 `r5-repair-tests.patch`(派工單 153 行),記帳的 `--snapshot` 填兩份原樣串接的 `r5-repair-codetests.patch`(`cat` 程式那份再接測試那份,153 行,內容不增不減)。載體選邊界席:quote-check 對這份全錨;正確性席有一句引的是第二輪就在的 `regex: '^[-+]'` 那行(只在 `r5-snapshot.patch` 錨得到),通才席是 clean、沒有引句,兩席都不能當載體(在 `git clone --shared` 副本上試記,工具在寫帳前擋下)。
- 席位臨時目錄:正確性、通才、資源、資安自己刪了;邊界、合約、架構對齊收貨後由編排者刪(刪前 lsof)。合約席留下兩支等待迴圈 `until ! pgrep -f "test_lumos.py -k choice"`——迴圈自己的指令列含那串字,pgrep 永遠找到自己、不會結束;確認是本會談子代理開的(輸出寫在本會談任務目錄)後只停這兩個程序。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| b1 c2 | 複本把 api.yml C-34 `value-used` 最後一個 `all` 的 `nthChild: {…, ofRule: {matches: code}}` 換成 `nthChild: {position: 1, reverse: true}`,跑 `choice_sample_problems` | `[]`(照綠);另用第四輪掃描腳本的拿法(regex 只吃到第一個 `}`)拿同一個選項:回「選擇點規則掃樣本跑不起來」——第四輪腳本把這種改壞 YAML 的變異當成翻紅,漏了它 | HIT |
| c1 | scratchpad r5_mutsweep.py(新增 regex 頭尾錨點、`\s*`、或的每一支各改一次)+ r5_diff.py(原規則與變異規則各掃一次語料 r5corpus/corpus.kt 加樣本目錄,比命中) | `let$`→`let`:多命中 `x.letX { it }`;`combine$`:多命中 `a.combineLatest(b)`;`^LaunchedEffect`:多命中 `MyLaunchedEffect(k)`;`^remember`:多命中 `myremember(k)`;`^Unit`、`Unit$`:少命中 `LaunchedEffect(distanceUnit)`、`LaunchedEffect(UnitX)`;樣本核對全照綠 | HIT |
| c3 | 同上,拿掉 literal-arg 的 `kind: prefix_expression` | 少命中 `LaunchedEffect(-k + 1)`、`LaunchedEffect(+k * 2)`;第四輪把它判等價,錯 | HIT |
| c4 | 同上 | 拿掉 `\?\.` 那支:少命中 `a?.combine(b)`;拿掉 `\s*`:少命中 `a . combine(b)`;完整套件名 regex 拿掉 `\s*`:多命中跨行的 `kotlinx.coroutines` / `.flow.combine(a, b)` | HIT |
| b2 | 測試總檔 `t_choice_table_batch2` 的列號案例 | 沒有 `C-0`、`A-0`;check.py 列號判斷改成收 `0` 後 20 條照綠 | HIT |
| (編排者擴掃) | 同 c1 的掃描與差異比對 | 另見:`finally` 區塊裡的 `.let`(拿掉 `kind: catch_block` 後被當值多命中)、`x . let` 點號前後空白、沒有呼叫的 `x.let`(拿掉 `kind: call_expression` 多命中)、加標註的常數 `@Suppress("x") 1`(拿掉 `regex: '^[-+]'` 少命中——變異反而更對,見處置);另外第四輪腳本把 C-37 規則本體五項誤標成「literal 區,有一致性比對守」(往回看 30 行找 literal 字樣,範圍太粗) | HIT |

## 分組

1. **變異掃描有盲點,樣本守不住規則子句**(c1 major、c2 major、c3 major、b1 major、c4 minor,另編排者擴掃):第四輪的全面掃描三個洞——改壞 YAML 的變異算成翻紅(stillborn 當 kill)、只有刪行與拿掉整個選項沒有改一部分(錨點、`\s*`、或的一支、只拿種類留 regex)、等價判斷靠人看(c3 判錯);另有 literal 區範圍標錯。C-34 這一族連五輪(r1 c1、r2 g1、r3 c1、r4 c1、r5 b1 c2)、C-36 字面值連四輪。
2. **列號零沒有測試**(b2 minor):程式已擋 `C-0`、`A-0`,測試沒釘。

## 先查世界

- 第 1 組:PRIOR-ART: 變異測試工具與研究一致把「改完編不過、跑不起來」的變異(stillborn / invalid)排除在分子分母外,不算 kill——Stryker 的 mutant states 文件把 CompileError、RuntimeError 列為 invalid、不進 mutation score(https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ );GateTruth(https://arxiv.org/pdf/2608.12635 )實例:某基準把編譯失敗算成 kill,重算後 100% 掉到 86.7%–94.4%。等價變異判定:人工判斷不可靠、等價不可判定,實務上用 Trivial Compiler Equivalence 這類機械比較(原版與變異版產物相同才判等價,保守、只會少判不會錯判)(https://orbilu.uni.lu/bitstream/10993/20289/1/ICSE15.pdf )。regex 變異運算子(MutRex,https://foselab.unibg.it/mutrex )按程式員常犯錯誤設計(前綴加字、量詞改、字元類改等),對應本案「錨點、`\s*`、或的一支」。採用:①掃描把跑不起來的變異另列無效、不算翻紅;②加 regex 頭尾錨點、`\s*`、或的每一支、行內鍵逐一拿掉(括號配對、不弄壞 YAML)的變異;③等價判定改成機械差異比對——原規則與變異規則各掃同一份語料加樣本,命中完全相同才列等價候選,有差的那一行就是要補的樣本(TCE 的思路:比產物不比人的判斷)。不採:把樣本核對改成 Semgrep 式「沒標的命中也算失敗」——理由同第四輪(既有樣本 236 個命中 128 個沒標,要重標第一批樣本、範圍超出這條分支)。
  方向:對 — 判法照舊看語法樹、樣本照舊只看有標記的行;五輪的發現都是同一族「掃描涵蓋面不夠」,這輪換的是掃描本身的形狀(無效變異不算、機械判等價),不是規則判法(上面 Stryker、GateTruth、ICSE15 三個網址)。
- 第 2 組:文件與既有判法,不需外部依據(撤號那一行早就只認 `[1-9]` 開頭)。

## 等價存活(修後重掃 api.yml 200 項變異:照綠 47、無效 45;照綠的差異比對語料上沒差 45 項)

- 掃描與差異比對的完整輸出在本目錄 `r5-mutsweep.txt`(語料檔在編排者 scratchpad,`.kt` 不放進卷證以免被推送閘當產品碼掃);沒差的 45 項分三類:
  - 父節點種類本來固定的限定(navigation_suffix 的父節點是 navigation_expression、value_arguments 的父節點是 call_suffix、call_suffix 的父節點是 call_expression、control_structure_body 只掛在 if/when_entry/迴圈底下,依此類推)、`kind: statements`、外層呼叫的 `nthChild: 1` 與 `kind: simple_identifier`(呼叫的第一個子節點就是被呼叫的名字)。
  - `regex: '^(\?\.|\.)…'` 與 nul.yml `'^\?\.'` 的頭錨點:navigation_suffix 的文字一定從 `.` 或 `?.` 開頭;完整套件名 regex 的尾錨點:它比對的 navigation_expression 一定以 `.combine` 結尾。
  - literal-arg 的 `stopBy: end`、內層 `nthChild`、`kind: value_argument`;C-37 literal 區(由 C-36 與 C-37 literal-arg 一字不差的比對測試守,C-36 那份同一變異都已翻紅)。
- 有差的 2 項都在 C-37 literal 區(`- kind: prefix_expression` 刪行、`reverse: true`),C-36 同位置的變異已被新樣本翻紅,一致性比對守住 C-37。
- nul.yml 13 項變異:照綠 2、無效 8,照綠 2 項差異比對沒差(頭錨點同上;`inside: {not: {kind: navigation_expression}}` 第四輪已判)。
- 語料只是語料:沒差只證明這份語料分不出來,不證明等價;語料涵蓋的寫法(各控制結構的條件與區塊、finally、標註、具名引數、展開運算子、原始字串、巢狀樣板、呼叫鏈上的同名方法、頂層與接收者寫法)。

## 處置

| id | 去向 | 種類 | 改了哪裡 |
|---|---|---|---|
| c1 c2 c4 b1 | 折 | code | 樣本 choice-batch2.kt 補 C-34 五行(if 區塊最後一個陳述後接註解 HIT、finally MISS、`x.letX` MISS、`x . let` HIT、沒有呼叫的 `x.let` MISS)、C-35 五行(`a?.combine` HIT、`combineLatest` MISS、`a . combine` HIT、跨行完整套件名 MISS、`my.kotlinx…combine` HIT)、C-36 四行(`MyLaunchedEffect` MISS、`distanceUnit` HIT、`UnitX` HIT、`-k + 1` HIT)、C-37 兩行(`myremember` MISS、`distanceUnit` HIT) |
| c3 | 折 | code | 同上補 `-k + 1`;另外 C-36、C-37 literal-arg 兩份一起拿掉 `regex: '^[-+]'`(只留 `kind: prefix_expression`):差異比對顯示拿掉後只差在標註加常數 `@Suppress("x") 1` 改成算常數,這才對(全是常數的 key 換掉必然等價),而且規則註解本來就寫「看結構不看文字開頭」;補 `LaunchedEffect(@Suppress("x") 1)` MISS 一行;計劃〈範圍〉2 字面值說明同步 |
| b2 | 折 | code | `t_choice_table_batch2` 補 `C-0` 與乾節點表 `A-0`(check.py 列號判斷改成收 0 時這兩條紅,修後 22 passed) |

修補因果:c1 c2 c4 b1 是第四輪掃描的盲點沒掃到的原有子句(兩席修前修後同結果);c3 的子句從第二輪就在,第四輪等價判斷錯;b2 原有。無回歸。
