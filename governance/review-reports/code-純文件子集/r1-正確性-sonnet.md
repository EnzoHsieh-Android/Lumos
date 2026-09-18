severity: major

## F1 `_docs_only_file` 的副檔名比對大小寫敏感,`governance/`、`docs/` 底下的程式檔只要副檔名大小寫不同就被誤判成 docs,推送前與 CI 都只跑文件子集

severity: major
blocking: yes

觀察到什麼:`_docs_only_file` 判「這支檔是不是程式檔」時呼叫既有的 `_nodehome_code_kind(path)`,而那支函式的副檔名比對是大小寫敏感的字串相等(`("." + stripped.rsplit(".", 1)[1]) in _NODEHOME_CODE_EXTS`,`_NODEHOME_CODE_EXTS` 只收小寫如 `.py`/`.sh`)。當一支檔的路徑落在白名單目錄(`governance/`、`docs/`…)底下,而副檔名跟清單裡的拼法只有大小寫不同(例如 `.PY`、`.SH`、`.Py`),`_nodehome_code_kind` 回 `None`(既不是 `"ext"` 也不是 `"shebang?"`);而 `_docs_only_file` 對 `None` 的處理是「`kind != "shebang?"` 就直接當文件」,於是把一支真正的程式檔判成純文件。

引句:「    kind = _nodehome_code_kind(path)
    if kind == "ext":
        return False
    if kind != "shebang?":
        return True」

怎麼重現(已在乾淨臨時 repo 對這份凍結 patch 的內容實跑過,不是紙上推演):
```
mkdir governance && echo "x = 1" > governance/Tool.PY && git add -A && git commit -qm base
echo "x = 2" > governance/Tool.PY && git add -A && git commit -qm change
python3 scripts/lumos pitfalls --diff HEAD~1..HEAD --no-lint --json --repo . \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('suite'), d.get('suite_reason'))"
```
輸出:`docs 改到的只有 README、docs、assets 這類文件(沒碰程式與 skills)`——但這次改動實際上是改了 `governance/Tool.PY` 這支 Python 檔的內容,`suite` 卻回 `docs`。同樣手法對 `docs/run.SH`(相對 `docs/run.sh`)也一樣中招,親自用 `_nodehome_code_kind`/`_docs_only_file` 對照驗證過:

```
governance/tool.py -> kind= ext   docs_only=False   (正確:程式檔)
governance/tool.PY -> kind= None  docs_only=True    (誤判:文件)
docs/run.sh        -> kind= ext   docs_only=False   (正確:程式檔)
docs/run.SH        -> kind= None  docs_only=True    (誤判:文件)
```

為什麼是 bug 而不是風格:這批的核心賣點就是「純文件推送才跳過全套」,commit 訊息與程式內註解反覆強調「保守方向是多跑,不是少跑」「★白名單不是『非程式檔』★」。但這裡漏了一個方向:白名單目錄底下的程式檔只要副檔名大小寫跟清單拼法不同,就會被歸類成文件,推送前掛鉤與 CI 都只跑文件子集(191/1021 支,實測 `--list --suite docs` 數字),真正動到的程式碼完全沒被跑到、直接溜進 main,正是這個鏡頭要盯的「該跑全套卻判成 docs」那一型錯誤,不是風格偏好。

file: `scripts/lumos:5640-5644`(共用的 `_nodehome_code_kind`/`_is_code_file`,副檔名比對只認小寫)
file: `scripts/lumos:22289-22299`(`_docs_only_file` 沿用同一支函式判斷)


## F2 `_test_suite_for_range` / `_affected_test_keys` 對三點範圍(`a...b`)算錯 base,用左端點取代 merge-base,刪除的程式檔可能被誤判成純文件

severity: major
blocking: yes

觀察到什麼:兩支新函式都用 `base = diff_range.split("..")[0] if diff_range and ".." in diff_range else None` 算「範圍起點」,再拿這個 `base` 去 `git show base:path` 讀刪除檔在起點的內容決定它有沒有 shebang。這行字串切法對 `a...b`(三點,merge-base 語意)得到的 `base` 是 `a` 本身,不是 `git diff a...b` 實際使用的 `merge-base(a, b)`。三點語意下,`a` 這個 ref 在分岔之後可能還有自己的後續提交,`a` 當下的內容跟真正的分岔點內容不是同一份。

引句:「    base = diff_range.split("..")[0] if diff_range and ".." in diff_range else None」

怎麼重現(乾淨臨時 repo,實跑過):
1. `base` 分支建一支有 shebang 的無副檔名腳本 `governance/run`(`#!/bin/sh`),這是 merge-base。
2. `feature` 分支從這裡分岔,把 `governance/run` 刪掉。
3. `main`(即三點語法左端 `a`)繼續往前走,把 `governance/run` 改寫成沒有 shebang 的純文字(同一路徑、不同內容)。
4. `git diff main...feature --name-status` 正確算出 `D governance/run`(相對 merge-base,這是一支被刪掉的程式檔,應該判 full)。
5. `python3 scripts/lumos pitfalls --diff "main...feature" --no-lint --json --repo .` 卻回 `suite=docs`,原因印的是「改到的只有 README、docs、assets 這類文件」——因為 `_docs_only_file` 拿 `base="main"`(而不是 merge-base)去讀 `governance/run` 的內容,讀到 main 當下已經沒有 shebang 的版本,誤判成文件。

為什麼是 bug:`--diff` 的說明字串本身沒限定只能給 `a..b`(參數只印範例「如 main..HEAD」,沒擋三點格式),`git diff a...b --name-only` 在函式一開頭就直接把整個 `diff_range` 原封傳給 `git`,git 自己會正確處理三點語意去算檔案清單;只有這裡另外算的 `base`(供 shebang 讀取用)沒有跟著用 merge-base,兩處語意不一致。結果是：對於「合併語意」下刪除的程式檔,`_docs_only_file` 用了錯誤提交點的內容做判斷,可能把「該跑全套」的改動判成 docs。這條是新函式自己的邏輯錯誤(雖然同一種字串切法在既有的 `_pitfall_tier` 也這樣寫,但那是既有函式不在這次審查範圍內;這次新增的 `_test_suite_for_range`/`_affected_test_keys` 沿用了同一個有瑕疵的算法,而且用途更關鍵——直接決定要不要跑全套)。

file: `scripts/lumos:22314-22333`(`_test_suite_for_range`)
file: `scripts/lumos:22335-22359`(`_affected_test_keys`,同一行 base 算法)

補充:目前實際會呼叫 pitfalls 的自動化路徑(`scripts/hooks/pre-push` 用 `$_rsha..$_lsha` 或 `$_EMPTY_TREE..$_lsha`、`.github/workflows/ci.yml` 用 `$BEFORE..$SHA`)都是兩點格式,不會踩到這條;三點格式只有人手動下 `lumos pitfalls --diff a...b` 才會碰到,所以這條對「自動閘」沒有立即風險,但工具本身允許任何 `--diff` 格式進到這兩支函式,一旦有人（或以後的自動化)改成三點語意呼叫,就會安靜地少跑該跑的測試。


## 其餘看過但沒收進發現的路徑(避免被誤會沒查)

- 白名單比對邏輯(`path == w or (w.endswith("/") and path.startswith(w))`)、簿記白名單交互(`_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 跟 `_DOCS_ONLY_PATHS` 的重疊)、`--no-renames` 對搬移/改名的兩筆拆解、空樹起點(`_EMPTY_TREE..sha`)——都跑過乾淨臨時 repo 的等價情境,行為跟測試釘的一致,沒找到問題。
- `affected_keys` 的正則(`async def`、縮排 `def`、hunk 標頭是 `class` 不是 `def` 的情況)——hunk 標頭是 class 時確實抓不到函式名,但函式一律會把檔名(去副檔名)加進 keys 當底線,實測不會導致 0 命中退化成沒有任何後備關鍵字。
- `_keys_suite_select` 對 `-` 名字(如 `spec-gate`)的整字比對——lookbehind/lookahead 只認 `[A-Za-z0-9_]`,不含 `-`,會對「同時被其他非字母數字字元包住的更長字串」過寬(例如 `get-spec-gate-info` 也會命中 `spec-gate`),但方向是多選不是漏選,不是這個鏡頭要抓的那一型。
- `_docs_suite_select` 的 docs/governance 二次過濾(`rx_generic` 配 `rx_real`)——方向同樣是「寧可多挑」,沒發現會漏挑真正該挑的文件測試。
- `--suite`/`--shard`/`--ff`/`--seed`/`-k` 的先後順序——讀 `scripts/test_lumos.py` 的 `main()`,`--suite` 選取先於 `--shard`,`--shard` 先於 `--ff`/`--seed`/`-k`,順序正確(子集先挑好、分片才不會分到空);用本 repo 實測 `--list --suite docs` 得 191/1021 支,4 片預設分片不會出現「某片剩 0 支」的假紅。
- `--suite keys` 沒配 `--keys`、`--keys` 沒配 `--suite keys` 各自 rc2;`--suite` 選中 0 支真跑 rc3、`--list` 0 支 rc0——都對照 `-k` 既有的 rc1(選中 0 支當失敗)行為看過,兩套 rc 語意不同是刻意設計(`--suite` 的呼叫端要分得出「沒對到」跟「有紅」以便退回全套),不是不一致。
- pre-push 對 `_suite_this`/`_SUITE_FULL`/`_SUITE_LIGHT`/`_SUITE_KEYS` 的多 ref 彙總、CI 那邊 `BEFORE` 全零/`cat-file -e` 失敗/`pitfalls` 出錯時的 fallback——讀過整段邏輯,任一 ref 為 full 就整體 full、light 蓋過 docs,fallback 一律往 full 倒,沒發現漏洞。
