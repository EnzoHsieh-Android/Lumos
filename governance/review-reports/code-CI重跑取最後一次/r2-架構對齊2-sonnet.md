severity: major

## F1 複本守衛從 `ast.walk`(全樹)退成 `tree.body`(只掃頂層),巢狀定義會被靜默漏比

severity: major
blocking: yes

r1(改動前)的複本比對用的是 `_ast.walk(tree)`,會遞迴走整棵語法樹,不管 `_ci_latest_attempts` 定義在檔案的哪個層級都找得到:

引句:「        for n in _ast.walk(tree):」

r2 把它換成只看模組頂層敘述:

引句:「        for n in tree.body:」

這一改動就是把巢狀函式定義排除在掃描範圍外。實測驗證(在 /tmp 用兩行程式碼比對):對

```python
def outer():
    def _ci_latest_attempts(rows):
        return rows
```

`tree.body` 掃到的結果是空清單,`ast.walk(tree)` 才找得到那個函式。也就是說:如果之後有人(不管是不是惡意)把某一份複本的 `_ci_latest_attempts` 包進另一個函式裡、或者藏進 `if TYPE_CHECKING:` 之類的區塊,r2 這版守衛會直接把那一份從 `bodies` 字典裡漏掉,不會報「① 現場成立」失敗(因為 `{"lumos", "ci-status-hook.py"}` 這兩份仍在頂層、仍找得到),也不會被 diff 比對出不一致——等於守衛安靜地退化成「只比原本那兩份」,新增或被動過手腳的第三份完全不在比對範圍內。這正好是派工單「重點攻擊」點名要驗的情境:「如果有人把函式改成巢狀定義或改名,守衛會不會安靜變成只比一份」——會。

跟本檔既有的兩組同類複本守衛比對,這個做法是退步、不是跟進:
- 信任邊界守衛(`scripts/test_lumos.py:15653`)用的是 `_re.search(r"def _trusted_lumos\(\):.*?\n    return None\n", txt, _re.S)`——對整段原始文字做正則,不管函式定義在第幾層縮排都抓得到。
- 逾時預算守衛(`scripts/test_lumos.py:16091`)一樣是對整段原始文字用 `_re.search(r"_BUDGET_RATIO = .*?\n    return max\(_BUDGET_FLOOR,.*?\n", _txt, _re2.S)`。

這兩組既有守衛都是「不管巢狀層級,直接對文字/整棵樹找」,不會因為縮排層級被漏掉。r2 這支新守衛反而換成只看 `tree.body`(等同「只比對頂層定義」),跟本檔自己另外兩組同類守衛的既有寫法不一致,而且弱化的方向剛好命中派工單指名要防的那個攻擊面。

現況說明:目前 repo 裡兩份 `_ci_latest_attempts`(`scripts/lumos`、`scripts/hooks/claude/ci-status-hook.py`)都定義在模組頂層,所以這支測試現在不會漏抓、也不會假綠——這是「守衛本身變弱」的問題,不是「現在就漏抓」的問題,但既然這輪的宣稱就是「掃全部,不寫死清單」(且註解明講是吸取代碼審 r1 教訓才改的),守衛的掃描範圍不該比它取代的舊版本、也不該比同檔案裡的姊妹守衛更窄。

修法建議(供參,不強制採用哪種):把 `for n in tree.body:` 改回 `for n in _ast.walk(tree):`(注意這樣找到的 `FunctionDef` 可能不止一個匹配名稱的節點,需要處理多個候選或報錯的情況),或跟信任邊界/逾時預算兩組守衛一致,改用整段文字的正則截取後再 `_ast.parse` 那一段。

## 已驗過、沒問題

- `rid = str(rid)` 與紅燈判定 `red = (...) in ("failure", "timed_out", "startup_failure")` 兩份複本逐字相同,且字面值跟 `scripts/lumos:24368` 的 `_CI_RED` 與 `scripts/hooks/claude/ci-status-hook.py:26` 的 `RED` 一致,不是憑空編出新清單。
- 掃描範圍從「寫死兩個路徑」改成 `[base / "lumos"] + sorted((base / "hooks").rglob("*.py"))`:`rglob` 是遞迴掃描,即使之後 `scripts/hooks/` 底下真的冒出 Codex 專用子目錄,也會被掃到(不像信任邊界那組守衛只鎖 `hooks/claude` 這一層),跟「掃全部、不寫死清單」的宣稱方向一致,沒有發現遺漏子目錄的問題。
- `reds_const` 只抓模組頂層的 `_CI_RED` / `RED` 賦值(`isinstance(n, _ast.Assign)` 且在 `tree.body` 內),跟 F1 用的是同一個「只看頂層」範圍,兩者範圍一致,不是各自標準不一致造成的問題;F1 的風險點在於「函式本身」被藏進巢狀層級會漏比對,不在常數判定這段。
