severity: major

# 設計審第 2 輪 正確性-opus

席名:正確性-opus。審材:r2-snapshot.md(78 行,逐節讀完)。對照 repo:negguard 的 shared clone(HEAD 5f8c84ff)。
實驗做法:在自己的臨時目錄把 scripts/lumos 照 spec 字面改一份(S1 範本 `--new` 改待填;S4 kill-add 開頭「`--old`/`--new` 含兩個待填字樣之一就回 2」;guard kill 在分組前 `recipes = [{**r, "_rid": _kill_recipe_id(str(rel), r)} ...]`、`--json` 濾掉 `k.startswith("_")`、結果行在判定後插 `id=<_rid 前 12>`、合約片段先 `str()` 再截),再跟原版在合成 repo 上對照跑。實驗腳本:`fx-r2-work-正確性-opus/patch.py`、`exp.py`、`exp3.py`、`exp4.py`。

## F1 S4 用「含」比對會擋掉合法配方:程式本身就含待填字樣時(lumos 自己的範本那一行)寫不進去,跟「合法配方不會含」的宣稱相反
severity: major
blocking: 是
引句:「kill-add 多擋的是範本待填字樣(合法配方不會含),不擋推送或提交」
file: `scripts/lumos:13496`
1. S1 落地後,`_kill_add_template` 那一行的原始碼會變成 `"--new", "'<照新原文改寫的壞法>'"`;S4 的檢查本身也會把兩個待填字樣寫成字面。這個 repo 本來就對 scripts/lumos 宣告殺傷力配方(`docs/lumos-toolchain-knowledge/Systems/canary-audit.md:91` 那條 `"file": "scripts/lumos"`),替 S1 那條行為(範本 `--new` 是待填)寫配方時,最自然的原文錨點就是這一行。
2. 實驗 1(合成 repo:prod.py 有一行 `return ["--new", "'<照新原文改寫的壞法>'"]`,測試斷言它):kill-add `--old "\"'<照新原文改寫的壞法>'\"" --new "repr(new)"`。原版 rc0 寫入、guard kill 判 killed;照 spec 字面實作 → rc2「擋下:範本的待填欄還沒填」。也就是說,一條真的殺得掉的合法配方被擋了,而且訊息講錯原因。
3. S4 的測試只驗「含字樣就擋」,這個誤擋不會被任何條款抓到;〈實務隱患〉的已排除段還寫明「合法配方不會含」,接手的人會照這句認定沒有誤擋面。
4. 反過來看繞過面:只差空白、全形括號、刪掉半截(`'<照現在的程式填原文'`)都能繞過「含」比對,但那些都表示人已經動過那一欄;S4 要防的事故是「範本原樣貼上、忘了填」,而原樣貼上時整個值就等於待填字樣。改了一半的 `--new` 跟任何亂寫的壞法一樣會被判「殺得掉」,那是 guard kill 本來就有的限制,不是 S4 擋得了的。
5. 建議擇一:(a) 改成「`--old`/`--new` 去掉前後空白後**整個等於**待填字樣才擋」,原樣貼上照擋、合法配方不誤擋;條款 S4 補一句反向:「原文只是含待填字樣(程式本身就有這串字)時照常寫入」,配一個測試。(b) 保留「含」比對,就把已排除段那句改成實話(程式本身含這串字時會被擋,要換一個不含整串待填字樣的錨點),並在擋下訊息裡講這種情況怎麼繞過。

## F2 S4 擋 `--old` 待填字樣違反既有的「宣告不擋、跑時擋」原則,spec 沒有交代;要同步的文件也漏了 kill-add 與 guard kill 輸出
severity: minor
blocking: 否
引句:「`--old` 沒填雖然會被判配方漂移,一起擋比較一致」
file: `scripts/lumos:13231`
1. 程式註解與圖譜都把這條寫成刻意的取捨:`_kill_add_warn` 的說明寫「★只提醒、照舊寫入★(保留「宣告不擋、跑時擋」…)」,`Systems/guard-kill.md:34` 的 WHY 行也是同一句。`--old` 填待填字樣,本質上就是在宣告時寫入一條失配的配方,也就是這條原則刻意放行的那一類。spec 改成宣告時就擋,卻沒有提這條原則,也沒記這次為什麼開例外(理由「一起擋比較一致」並沒有回應原則本身)。
2. 已查過:現有測試沒有用待填字樣當 `--old`(在 scripts/test_lumos.py 搜尋兩個待填字樣都是 0 筆),不會弄紅測試,所以只算 minor。不過下一個讀到 WHY 行的人會以為 kill-add 從來不擋失配配方。
3. 〈要同步的文件〉只列了 kill-rm 的用法、範本與 HELP_WHEN。S4 改的是 kill-add 的行為,`Systems/guard-kill.md` 的 kill-add 段(第 68 行用法、第 95 行「kill-add」那段)、guard kill 人讀輸出多了 `id=` 這件事、`commands/06-代碼審與推送.md` 的 kill-add 那一列,都應該補進同步清單;guard-kill.md 第 34 行的 WHY 也要補一句「待填字樣是例外,宣告時就擋」。

## F3 「`--json` 濾掉所有底線開頭的欄」會改掉既有輸出:配方裡手寫的底線欄原本會印出來,所以「各筆結果的欄位跟改動前相同」按字面不成立
severity: minor
blocking: 否
引句:「`--json` 輸出前濾掉所有底線開頭的欄(含既有 `_logged`),`--json` 內容與既有 `recipe_id` 欄都不變」
file: `scripts/lumos:13955`
1. 每筆結果都是 `{**原配方, …}`,配方裡任何手寫欄位都會原樣進 `--json`;現在的程式只濾 `_logged`。
2. 實驗 2:配方多一個手寫欄 `"_why": "手寫的備註欄"`。原版 `--json` 的那筆結果有 `_why`;照 spec 字面實作之後沒有了(兩版欄位集合差 `{'_why'}`)。S3 寫的「各筆結果的欄位跟改動前相同」按字面就不成立。repo 內沒有程式讀 guard kill 的 `--json`(已搜過 scripts/、hooks/、.github/),影響面小。
3. 建議:只濾明列的旁路欄 `{"_logged", "_rid"}`;或者照現在的濾法做,但把 S3 收窄成「kill-add 寫得出來的欄位與工具加的欄位不變」。
4. 同一個實驗順帶看到一個既有的洞:配方手寫 `"_logged": true` 時,kill-log 一行都不寫(兩版都是 0 行),等於從筆記就能讓這條配方的結果不進帳(背書計算讀的就是 kill-log)。這次本來就要在分組前做配方副本,做副本時順手把筆記帶進來的底線欄拿掉(`_rid` 照樣用原配方算)就能補上;不補的話,至少記進 F5 那篇 Issue。

## F4 「先截再跳脫」本身安全,但配方欄位帶落單的替身字元時,短身分那支函式就會崩潰:新做的列出跟著崩潰,kill-rm 也移不掉這條
severity: minor
blocking: 否
引句:「格式壞的配方(欄位缺、型別錯、不是物件)也應列出、不崩潰」
file: `scripts/lumos:12917`
1. 先講安全的部分(已實測):Python 截字串是照「字元」截,不會切斷多位元組字;JSON 裡成對的 `😀` 讀進來時已經合成一個字元,截字也不會把它拆開;落單的替身字元屬於 Cs 類,`_kill_esc` 會把它轉成看得見的 `\ud800`;因為先截再跳脫,也不會出現跳脫到一半被截斷的情形。實驗 4:`_kill_show(old[:30])` 印成 `"LIMIT = 5\ud800"`,沒有問題。只有組合字或 ZWJ 表情符號可能被截掉半個,那只是顯示問題。
2. 會出事的是身分計算:筆記的 JSON 寫 `"old": "LIMIT = 5\ud800"`(字串型別,不算「型別錯」),`_kill_recipe_id` 會走 `_kill_recipe_key`,它的 `json.dumps(...).encode("utf-8")` 丟 UnicodeEncodeError。實驗 4:原版 kill-rm、guard kill 都以 rc1 崩潰、印出錯誤追蹤;照 spec 實作的列出要逐條算身分,同樣會崩潰。結果是使用者既列不出身分,也移不掉這條。kill-add 寫不出這種配方(它在寫入前算 key 就先崩潰了),只會來自手改或不可信的提交。
3. 建議:身分雜湊改用 `.encode("utf-8", "surrogatepass")`(`_kill_recipe_key` 與 `_kill_recipe_id` 的格式壞分支都要改)。不含替身字元的字串編出來的位元組完全相同,所以既有配方、kill-log 的 recipe_id 一條都不會變。S2 的「不崩潰」把「字串帶落單替身字元」也列進去。不在這次修的話,就記進 F5 那篇 Issue。

## F5 「整支崩潰、另記 Issue」列的配方種類不齊,崩潰的回傳碼又跟 survived 一樣;RETIRE-IF 拿「那類已修」當撤除前提,會照不全的清單判
severity: minor
blocking: 否
引句:「guard kill 遇到格式壞到整支崩潰的配方(不是物件、file/old/new 是數字)也不在這次修,記成 Issue」
file: `scripts/lumos:13877`
1. 實驗 3(照 spec 實作之後):`缺 new` 而且 old 對得到 → `src.replace(r["old"], r["new"], 1)` 丟 KeyError,一行結果都沒印;`platform` 是陣列 → 分組 `groups.setdefault` 丟 TypeError(不能當字典鍵);另外照程式讀:缺 old 而目標檔是空檔時 `"".count("") == 1`,接著 `r["old"]` 會丟 KeyError;用位置參數過濾合約、配方的 invariant 又不是字串時,`in` 會丟 TypeError;F4 的替身字元也是一種。這幾種都不在括號列的「不是物件、file/old/new 是數字」裡。
2. 這些崩潰的行程回傳碼是 1(未接住的例外),跟「有配方 survived」的 rc1 撞在一起,hook 或 CI 會把崩潰讀成「稻草人證據」。這是既有行為,但開 Issue 時應該寫進去。
3. S3 用「有印出結果行時」限定範圍,條款本身仍然寫得出測試、也一致(實驗 3:缺 old → 印出 `⚠ drifted   id=3884bd1f926c …`,拿這個 id 跑 kill-rm 回 rc0;invariant 是數字 → 改成先 `str()` 再截之後照常印出 `id=271b06675fb9`,拿去 kill-rm 也回 rc0)。所以這條只影響 Issue 的範圍和 RETIRE-IF 的判斷,算 minor。建議把括號改成「不是物件、欄位型別讓 guard kill 丟例外(file/old/new 是數字、缺 new、platform 不能當鍵…)」,或改寫成「guard kill 印不出結果行的那幾類」,並附實驗清單。

## 各節核對紀錄

- **開頭/依據/PRIOR-ART/RETIRE-IF**:已讀,無 finding。核對「短身分用既有的 `_kill_recipe_id`(P2、kill-add 提醒、kill-rm 共用)」:`_kill_recipe_id` 在 scripts/lumos:12935,`_kill_fix_hint`(13226)與 kill-rm(13545)都用它,而且同樣以 `str(rel)` 當 node,guard kill 的 `rel` 也來自同一個 `env.find`,三處的身分會一致。
- **範圍**:F1(已排除段的宣稱)、F5(不做清單)。
- **做法・範本**:核對「`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`」。現況(13496)是 `val("new", "'<壞法>'")`;改了之後,完整內容那一行(`_kill_rm_show` 13574)照樣印舊壞法。無 finding。
- **做法・kill-add 擋待填字樣**:F1、F2。
- **做法・kill-rm 不帶 --id**:核對「有給(含空字串)照既有驗證與移除(空字串照舊擋下回 2)」。argparse 現在是 `required=True`(40735),dispatch 傳 `args.gkr_id`(41676);改成選填之後預設是 None,用 `is None` 分流就正確;空字串會進既有的 `re.fullmatch` 而回 2。逐欄格式、重複合成一行、不是物件的元素用 `_kill_recipe_id` 的格式壞分支(可移除性已由既有 t_guard_kill_rm ④ 證過):除 F4 外無 finding。
- **做法・guard kill 人讀輸出**:核對「後面 9 個組結果的地方 `{**r, …}` 自然帶上,不必逐處補」。實數 cmd_guard_kill 裡的 `{**r` 正好 9 處(平台不在設定、worktree 失敗、test 名不合法、baseline 非綠、路徑逃逸、開檔失敗、漂移、revert 失敗、正常結果)。副作用逐一查過:kill-log 寫的是明列欄位(13945–13951),不會帶出 `_rid`;背書計算讀的是 kill-log(39411 起),不讀結果字典;位置參數的合約過濾(13755)用 `r.get("invariant")`,不碰 `_rid`,先算身分或先過濾結果都一樣;既有測試對結果行只用子字串比對,沒有斷言「判定緊接著合約片段」;這個 repo 也沒有比對 guard kill 輸出的 golden 檔。實驗在原配方上算 `_rid`,印出的 id 拿去 kill-rm 對得到。只有 F3 的 `--json` 濾法是問題。
- **條款**:S1、S2、S4 照字面都寫得出測試;S3 在「有印出結果行時」的範圍內寫得出測試,而且實驗通過(見 F5 第 3 點)。S4 缺一條反向條款(F1)。
- **回退**:已讀,無 finding。核對「kill-add 不擋待填字樣;筆記與配方都沒被這次改動自動改過」:S4 只擋輸入、不改既有資料,revert 之後回得去。
- **實務隱患**:F1(已排除段)、F2(同步清單)。「別在函式體內新增 `"verdict": "…"` 字面」這一點,照 spec 的做法不會碰到。
- **審計修正紀錄**:已讀,無 finding。核對「短身分改在分組前一次算好、`--json` 濾掉所有底線開頭欄」與做法段一致;濾法本身的問題見 F3。

最高等級:major;blocking 共 1 條
