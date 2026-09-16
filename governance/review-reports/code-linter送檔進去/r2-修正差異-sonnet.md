severity: major

以下是對 r2-snapshot.patch(修正上一輪八條發現的那份差異)本身的獨立複審。實驗全部在 `/tmp/lumos-r2-review`(用 `git -C` 開出的臨時 worktree,checkout 到 `2b4cb7ce`)裡做,repo 根目錄本身沒有被改動;每個實驗做完都把檔案還原,收工時 `git diff --stat` 確認乾淨。

## 發現 1:c2 的退路鎖,同一個程序巢狀拿鎖會自己把自己鎖死

`_vault_write_lock`(`scripts/lumos:11130`)的「可重入」快路徑是這樣判的:進函式先算出 `lock`(固定指向 `~/.cache/lumos/vault-lock/<key>.lock` 這條「主要」路徑)、`k = str(lock)`,然後檢查 `_VAULT_LOCK_HELD.get(k)`——這段計算在「這個路徑信不信任」的判斷★之前★。r2 加的退路只在判斷之後把 `lock`/`k` 改指到筆記庫自己裡面(`fallback = Path(vault) / f".lumos-vault-{key}.lock"`),但可重入檢查用的是判斷前算出來的那個 `k`(主要路徑),不是退路的 `k`。

引句:「退路選筆記庫自己:要寫的就是它、使用者一定擁有它,兩個程序算出來的路徑一樣,」(`governance/review-reports/code-linter送檔進去/r2-snapshot.patch:80`)

後果:一旦主要鎖目錄不可信(觸發退路),同一個程序裡「外層已經拿著鎖、內層再呼叫一次 `_vault_write_lock` 對同一個筆記庫」這種巢狀呼叫,不會被判成可重入——因為外層存進 `_VAULT_LOCK_HELD` 的鍵是退路鍵,內層檢查用的卻是主要路徑的鍵(查不到),於是內層照樣往下走、又一次算出同一個退路鎖檔、對「自己這個程序已經拿著的同一支鎖檔」發起 `_excl_lock_try`——那支鎖檔的 PID 就是自己,不會過期接手,結果內層卡滿 60 秒後拋 `RuntimeError("等了 60 秒還輪不到寫入…")`,而訊息講的「別的程序在寫」是假的,是自己卡自己。這正是函式自己文件裡講的「第四輪:原本自己卡自己 60 秒」那個舊坑,在退路分支重新出現。

重現(記憶體內、8 秒鬧鐘代替真等 60 秒,不動 repo):
```
home = 一個假 $HOME,其中 .cache/lumos 是指到別處的 symlink(讓信任檢查失敗、走退路)
vault = 一個真實資料夾
with m._vault_write_lock(vault):
    print("outer lock acquired")
    with m._vault_write_lock(vault):     # 巢狀,同一個 vault
        print("inner lock acquired")
```
外層印出 `outer lock acquired` 後,內層在 8 秒鬧鐘觸發前完全沒有進展——確認是卡死,不是單純變慢(真實情境會卡到 60 秒才拋例外)。

新加的測試 `t_vault_lock_falls_back_instead_of_giving_up`(`scripts/test_lumos.py:10863`)在最後一段寫著「巢狀允許」,但實際寫法是兩個★不重疊★的 `with` 區塊(先進出一次,再進出一次),不是「外層還沒退出、內層就進來」的真巢狀——所以這條回歸完全沒被新測試釘住,測試名字與註解讓人以為巢狀已經驗過了。

severity: major
blocking: 是

## 發現 2:c3 收緊收尾圍欄判定,把「收尾圍欄帶垃圾尾巴」的既有情境從「看得見」變成「看不見到檔尾」

`_visible_lines`(`scripts/lumos:2841`)這次加的條件是 `s[run:].strip() == ""`——收尾圍欄後面必須只剩空白,否則不算收尾。這修對了 r1 講的「巢狀範例裡 `~~~python` 提前關掉外層圍欄」那個方向,但條件本身比「不准帶語言標記」更寬:任何非空白尾巴都會讓那一行失去收尾資格,不管是語言標記還是純粹的錯字/多餘字元。而這支函式的既有語意是「圍欄沒關上=整份剩下的內容全部隱形」(函式自己的文件講得很白:「①假設圍欄成對:未閉合的圍欄看不見…幽靈圖譜邊、假合約佐證」)。

引句:「if ch == fence[0] and run >= fence[1] and s[run:].strip() == "":」(`governance/review-reports/code-linter送檔進去/r2-snapshot.patch:23`)

重現(離線,不動 repo):
```python
txt = "開頭\n```\n程式碼\n``` 這是打錯字加在後面\n真的重要的合約行在這裡\n"
seen = [ln for _no, ln in m._visible_lines(txt.split("\n"))]
```
r2(HEAD)結果:`seen == ["開頭"]`——「真的重要的合約行在這裡」消失。
還原成 r1 的寫法(只看字元與長度,不看尾巴)重跑同一段文字:`seen == ["開頭", "真的重要的合約行在這裡", ""]`——原本看得見。

也就是說,這次修法把「收尾圍欄後面帶任何東西(不只是語言標記)」全部判定為「還沒收尾」,而不是只針對 CommonMark 定義的「語言標記」這個子情況去修。任何一行不小心在收尾 ``` 後面多打一個字(常見的手滑,例如貼錯、多敲一鍵),就會讓★該行之後到檔尾的所有內容★(包含合約行、severity 宣告、[SN] 條款——這支函式在 `scripts/lumos:4607`、`scripts/lumos:5428`、`scripts/lumos:5460` 等多處被用來抽這些東西)整段隱形,而且沒有任何提示。這正是函式文件裡「一個縮排的 ``` 就能把某節點的鐵則警告靜默關掉」講的同一類危險,換了個觸發方式重新出現。

patch 自己的「改之前先量過影響面」只掃了圖譜現有的 537 篇筆記,量的是「這批既有內容會不會變」,沒有涵蓋「未來任何人不小心打錯收尾圍欄」這種新輸入的健壯性——新加的測試 `t_closing_fence_must_not_carry_a_language_tag`(`scripts/test_lumos.py:10970`)也只覆蓋「語言標記」這一種尾巴(`~~~python`),沒有覆蓋「非語言標記的任意尾巴」這個更寬的觸發面。

severity: major
blocking: 是

## 發現 3:c6 的「語法樹檢查」docstring 宣稱擋得住「拿變數繞」,實測擋不住

`t_lint_files_substitution_has_one_implementation`(`scripts/test_lumos.py:11041`)的機械保證用 `ast.walk` 找 `.replace(...)`/`.sub(...)` 呼叫,並檢查呼叫的參數裡是否★直接★出現 `_LINT_NEW_FILES_TOKEN` 這個名字或 `"{LINT_FILES}"` 這個字面值。

引句:「if isinstance(sub, _ast.Name) and sub.id == "_LINT_NEW_FILES_TOKEN":」(`governance/review-reports/code-linter送檔進去/r2-snapshot.patch:606`)

這支檢查只看「呼叫的參數表達式本身」,不追資料流。實測寫一個先把 token 存進區域變數、再用那個變數呼叫 `.replace` 的「第二份實作」:
```python
def _dummy_bypass_style_replace(cmd, files):
    tok = _LINT_NEW_FILES_TOKEN
    return cmd.replace(
        tok, " ".join(files))
```
把這段插進 `scripts/lumos`(在別的位置,離題,不影響其他函式)後,重新對整份檔案跑同一套 AST 判斷邏輯:只找到既有的 `_lint_cmd_with_files` 一處,插入的第二份「變數間接」實作完全沒被抓到——`subs == [('_lint_cmd_with_files', 17861)]`,長度仍是 1,測試會照樣判定通過。

但這支測試自己的註解(`scripts/test_lumos.py:11085` 前後)明講它買到什麼——原文用引號列了四種它擋得住的繞法:換行、換縮排、換成 re.sub,以及拿變數繞。r1 架構席原始發現點名的五種繞法之一正是用變數間接(`tok = _LINT_NEW_FILES_TOKEN; cmd.replace(tok, ...)`),而這正是實測沒被擋下的那一種——註解宣稱擋住的四件事裡,有一件其實沒擋住。也就是說,這次修法把「純字串比對」升級成「語法樹比對」,擋住了拆行、換縮排、`re.sub`、`str.replace(cmd, TOKEN, …)` 這種★直接引用★token 的寫法,但對「先賦值給變數再用」這個 r1 明確示範過的繞法沒有防住,而註解卻宣稱防住了——跟 c6 原始發現的性質(「機械保證」名不副實)是同一件事,只是換了一層更難察覺的包裝。目前程式裡只有一處真的在替換(現狀乾淨),這條測試買到的保證比它自稱的窄。

severity: minor
blocking: 否

---

## c1–c8 逐條核對表

| id | 一句話 | 核對結果 |
|---|---|---|
| c1 | 降級只套用在推送閘接得住的宣告 | 修對了。`_push_gate_covers` 標記的判斷條件(`_LINT_NEW_FILES_TOKEN in cmd`)跟推送閘實際的略過條件(`scripts/lumos:18432` 的 `if _LINT_NEW_FILES_TOKEN not in cmd`)逐字對得上;標記只存在函式內部,`for c in lint_claims: c.pop("_push_gate_covers", None)`(`scripts/lumos:21019`)在組出 `out["claims"]` 之前清掉,不外流;`_tier_claims` 在清掉之前就已經算完,清除動作不影響已經算好的分級。用還原測試驗過:退回舊寫法,新加的 t8 案例確實翻紅。 |
| c2 | 不可信就換地方鎖,不乾脆不鎖 | 主線(單次拿鎖、互斥仍成立)修對了,但引進新回歸——見發現 1:退路重新引入「巢狀拿鎖自己卡自己」這個文件裡講明已經修過一次的舊坑,新測試沒真的測到巢狀情境。 |
| c3 | 收尾圍欄不准帶語言標記 | 對 r1 舉的「語言標記」案例修對了,但條件下得比題目寬,新增了「任意非空白尾巴都會讓收尾失敗、隱形到檔尾」的回歸面——見發現 2。 |
| c4 | 冒煙沒檔時回報「沒驗到」而非「跑不動」 | 修對了。回傳值改成可能是 `None`,唯一呼叫端(`scripts/lumos:17358`)已跟著判斷 `if ready is None`;沒有其他呼叫端遺漏(`grep` 確認全檔只有這一處呼叫)。 |
| c5 | 呼叫端明寫只要命令、加斷言釘住迭代順序與去重 | 修對了。第三個呼叫端(`_lint_new_cmd_targets`,`scripts/lumos:17968` 的 `list(_lint_stacks_for_diff(...))`)本來就是靠 dict 迭代語意剛好相容,這次沒改邏輯只補了注解跟測試;新測試(`scripts/test_lumos.py:9579` 起)確實把「直接迭代拿到命令、first-seen 順序、同一命令只出現一次」釘成明文案例。 |
| c6 | 改用語法樹檢查,擋住拆行/縮排/re.sub | 部份修對:確實擋住了字串比對版本擋不住的那幾種繞法(拆行、換縮排、`re.sub`、直接引用 token 的函式型寫法),但 docstring 宣稱連「拿變數繞」都擋得住,實測不成立——見發現 3。 |
| c7 | 呼叫端數量改成四個 | 修對了。`grep -n "_lint_cmd_with_files(" scripts/lumos` 排除定義行後正好 4 個呼叫端(`17329`/`17558`/`18447`/`20978`),跟改後的 docstring 一致,也跟 `_lint_cmd_with_files` 自己 docstring 講的「三個地方各寫一次…第四個地方」對得上。 |
| c8 | 兩處 JSON 擷取寫法統一 | 修對了,範圍如約定:r1 指出的是「這份原始 diff 自己改了 `data` 卻沒改 `data6`」這兩處不一致,r2 把 `data6`(`scripts/test_lumos.py:10687`)也改成 `next(...)` 跟 `data` 一致。同一支函式裡 `data3`/`data4`/`data5` 仍是舊式 `[...][0]` 寫法,但那三處是這份原始 diff之前就存在、未被那份 diff 觸碰的既有寫法,不在「兩處統一」的承諾範圍內,不算沒修好。 |
