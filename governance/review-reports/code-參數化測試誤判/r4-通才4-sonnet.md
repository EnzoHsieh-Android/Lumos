severity: blocker

## F1 機械守衛用正則掃「解構寫法」,只認得一種寫法,常見的括號解構/星號解構/連鎖賦值/續行/存進 dict 都會讓它假綠

severity: blocker
blocking: yes

這支新守衛(`t_platform_index_consumers_all_unpack_same_arity`)存在的唯一理由,是防「`_platform_test_index` 加了第 6 個回傳值,消費端漏改解構,少收一個值」這族錯誤以後不靠人記得,而是機器抓。它靠兩條正則去掃原始碼行:一條認「直接解構呼叫」,一條認「先存成一個變數(holder),之後才解構」。

引句:「mm = _re.match(r"^\s*([\w, ]+?)\s*=\s*(?:m\.)?_platform_test_index\(", ln)」
引句:「holders = set(_re.findall(r"^\s*(\w+)\s*=\s*(?:m\.)?_platform_test_index\(", src, _re.M))」

兩條正則都假設解構是「一行、逗號分隔的裸識別字,等號右邊直接接呼叫或 holder 名字」。只要消費端换一種同樣合法、同樣常見的寫法,兩條正則都比對不到,守衛就會在「明明少收一個值」的情況下印綠。

**怎麼重現(已實際跑過,不是推論)**:把 `scripts/lumos`、`scripts/test_lumos.py` 複製到暫存目錄(不動原 repo),在複製出來的 `scripts/lumos` 裡,緊接著 `return pdata, split, default, methods_for, hay_for, loose_for` 那行之後,加入以下 5 個「真的漏收一個值」的消費函式(每個都只收 5 個而不是該有的 6 個):

```python
def _dummy_consumer_paren_bug(repo_root):
    (pdata, split, default, methods_for, _hay) = _platform_test_index(repo_root)
    return pdata

def _dummy_consumer_star_bug(repo_root):
    pdata, split, default, *rest = _platform_test_index(repo_root)
    return pdata

def _dummy_consumer_chain_bug(repo_root):
    pidx = idx = _platform_test_index(repo_root)
    pdata, split, default, methods_for, _hay = idx
    return pdata

def _dummy_consumer_backslash_bug(repo_root):
    pidx = _platform_test_index(repo_root)
    pdata, split, default, methods_for, _hay = \
        pidx
    return pdata

def _dummy_consumer_dict_bug(repo_root):
    store = {"idx": _platform_test_index(repo_root)}
    pdata, split, default, methods_for, _hay = store["idx"]
    return pdata
```

再跑 `python3 scripts/test_lumos.py -k platform_index_consumers_all_unpack_same_arity`(在複製出來的暫存目錄裡跑,`GRAPHCTL` 會自動指到同目錄下的 `scripts/lumos`)。結果:

```
lumos 測試(1 案例)
  ✓ ① 找得到那支索引的回傳行
  ✓ ② 每一處解構的個數都對得上
2 passed, 0 failed
```

5 個貨真價實漏收一個值的消費者,守衛全部沒看到,②照樣綠。（另外用模擬同一組正則對 lambda 包裝一次呼叫的寫法也做了推演,同一根因會失手,但這條沒有逐一實跑,列為推論,不算入「已驗證」數量。）

**為什麼是 bug 不是風格問題**:守衛的 docstring 明講「翻紅釘:把任一處解構改回五個 → ②紅」,等於作者自己宣稱這支守衛能擋住「解構個數不對」這整族錯誤。但它只擋得住『逗號分隔、單行、裸識別字』這一種寫法,而括號解構、星號解構、連鎖賦值、續行、存進容器再取用全部是日常會寫出來的合法 Python,不是刁鑽edge case。反諷的是,同一批 diff 裡 `_py_declared_methods` 的 docstring 才剛好白紙黑字警告過「不要用放寬的正則去掃」、要用真語法樹(`ast.parse`)——因為正則抓不住字串/縮排這類語法變化;而這支守衛自己犯了同一種錯:用正則去抓「解構」這種一樣有多種合法語法形狀的東西。只要日後有人（或審查員自己）用上面任一種寫法補一個新消費點又漏改,守衛不會紅,會安靜地绿,回到 r1-r3 想解決的「人數漏」問題,只是把「人數漏」換成「守衛掃漏」。

## F2 守衛硬寫死只掃兩個檔,任何第三個消費檔——即使用最直白的逗號解構——完全不在掃描範圍內

severity: blocker
blocking: yes

引句:「src = Path(GRAPHCTL).read_text(encoding="utf-8")」
引句:「tst = Path(__file__).read_text(encoding="utf-8")」

守衛只讀這兩份原始碼字串(`scripts/lumos` 本體 + `scripts/test_lumos.py` 自己),整支函式沒有第三個讀檔來源,也沒有機制去發現「repo 裡還有沒有別的檔在呼叫 `_platform_test_index`」。今天 repo 裡確實只有這兩處在用它(已用 `grep -rn "_platform_test_index" --include="*.py" .` 核對過,結果只落在 `scripts/lumos` 與 `scripts/test_lumos.py` 兩檔,查證見 `scripts/lumos` 全檔 grep,無第三檔),但守衛的設計是「機械掃,不靠人記得」,而它掃描的檔案清單本身就是靠人手寫死的兩個路徑,一旦日後有第三個消費者(例如另一支腳本、plugin、或另一支測試檔匯入 lumos 模組後自己解構),它完全落在守衛的視野之外。

**怎麼重現(已實際跑過)**:同上暫存目錄,再加一個全新檔案 `scripts/other_consumer.py`,內容是最普通、教科書等級的直接逗號解構,一樣漏收一個值(收 5 個不是 6 個):

```python
def third_party_consumer(repo_root):
    pdata, split, default, methods_for, _hay = lumos_mod._platform_test_index(repo_root)
    return pdata
```

再跑同一支測試,結果一樣是「② 每一處解構的個數都對得上」印綠、`2 passed, 0 failed`——即使這個消費者用的正是守衛在自己兩個檔內部完全認得出來的那種寫法(直接逗號解構,無括號無星號無 holder),只因為它住在第三個檔案,就被完全略過。

**為什麼是 bug 不是風格問題**:F1 討論的是「同一批被掃的檔案裡,換個寫法就躲過」;這條討論的是「掃描範圍本身就沒把整個 repo 包進去」,兩者是獨立的失守面。守衛的 docstring 說「翻紅釘:把任一處解構改回五個 → ②紅」,沒有加註「僅限這兩個檔」這個前提,而這個前提對「以後由機器抓,不靠人記得」這句設計初衷是致命的——只要漏改發生在第三個檔案,不管改法多老實,守衛都不會紅。

## 其餘已驗過、判定沒問題的路徑(附在此,不佔用發現欄位)

- **回傳行改寫成別的形狀(換行/加註解/改名)時,守衛是紅還是綠**:實測把 `return pdata, split, default, methods_for, hay_for, loose_for` 那行尾巴加一句行內註解,①（「找得到那支索引的回傳行」)直接失敗、整支測試印紅、不是靜默跳過,行為正確,不算發現。
- **前三輪折入的東西這輪有沒有被改壞**:`grep -n "_spec_gate_declared(" scripts/lumos` 核對三個呼叫點(`5768`、`5803`、`6172`),全部餵的是 `loose_for(plat)` 不是舊的 `methods_for(plat)`,沒有退回 r1 blocker 描述的「錨在欄位 0、漏看類別裡測試」那個舊洞。
