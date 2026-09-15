severity: major

# t_impact_pins_order_is_total 測試品質審查

## 做了什麼

把 `scripts/lumos`、`scripts/test_lumos.py` 複製一份到 `/tmp/mut_sort_test`(不動 repo),對 `_sort_pins` 逐條做變異測試:拆掉某段邏輯 → 清 `__pycache__` → 跑 `python3 test_lumos.py -k <關鍵字>` → 看翻不翻紅 → 還原比對。每次還原後都重新確認整支測試轉綠,再進下一條。

## 發現一:測試問的是產品的具名實作,不是自己複製一份

`_order` 直接呼叫 `m._sort_pins(list(rows), True)`,不是重寫一份排序邏輯自己算。把修法唯一改動的那一行(排序鍵末項)還原成舊寫法 `r["node"] if r.get("home") else ""` 之後重跑,結果如下表。

| 植入 | 跑哪支 | 實際輸出 | 判定 |
|---|---|---|---|
| 排序鍵末項改回 `r["node"] if r.get("home") else ""`(patch 描述的翻紅釘) | `t_impact_pins_order_is_total` | `★餵順序不同的同一批固定席,排出來要一樣★` 翻紅,原序排出 P00/P01/P02…,打亂後排出 P05/P06/P04…;其餘 5 條仍綠 | 守得住 |

引句:「return [r["node"] for r in m._sort_pins(list(rows), True)]」

severity: clean
blocking: 否——查的是產品端具名實作,不是自算一遍,拆掉修法本身該翻紅的那條真的翻紅。

## 發現二:「單一來源」那條檢查本身守不住——它只查名字在不在,不查是不是真的只有一份

`hasattr(m, "_sort_pins")` 這條檢查自己的說明寫著「兩處各寫一份=會無聲漂移」,但它能查到的只有「這個名字的函式存在」,查不到「排序邏輯是不是真的只寫了這一份」。回頭看這次審的 commit(798ce9f3)本身:`cmd_impact`(排 `--file` 模式的必推名單)確實改成呼叫 `_sort_pins`,但 `cmd_impact_diff`(排 `--diff` 模式的必推名單)在同一支檔案裡自己另外寫了一份幾乎同義的排序鍵——`key=(lambda v: (v["kind"] != "incident", not v.get("home", False), -v["score"], v["node"])) if _home_on else (lambda v: (-v["score"], v["node"]))`,完全沒有呼叫 `_sort_pins`(`scripts/lumos:23629`,HEAD 798ce9f3)。也就是說,「兩處各寫一份」這個檢查自己點名要防的情況,在它要保護的這次提交裡本來就已經存在——只是這份獨立複本剛好沒踩到這次修的那個特定 bug(它的末項本來就恆定用 `v["node"]`),所以目前輸出不會分岔,但兩份實作各自維護、日後任一邊改了排序規則(例如再加一層優先序)另一邊不會跟著動,`hasattr` 這條檢查對此完全沒有偵測力。

引句:「check("★排序有單一來源 _sort_pins★(兩處各寫一份=會無聲漂移)",」

file: `scripts/lumos:23629`(HEAD 798ce9f3,`cmd_impact_diff` 內的獨立排序鍵)

severity: major
blocking: 是——檢查的名稱與說明宣稱在守「單一來源」,但它只驗證名字存在,查不到「還有第二份」;而這次提交當下就真的有第二份獨立實作,這條檢查對此毫無偵測力。

## 發現三:「前置」斷言不是套套邏輯,翻紅釘的條號核對得上

`_rnd.Random(7).shuffle(_perm)` 後,先斷言 `_perm` 真的跟 `base` 不同序,再斷言排序結果應該一樣。用還原修法的變異測試檢查:翻紅的是「★餵順序不同的同一批固定席,排出來要一樣★」這一條,前置那條(打亂後確實不同序)仍然綠——因為打亂本身跟 `_sort_pins` 無關,不會被這個變異影響。docstring 寫「第 2 條翻紅」,如果不算最前面那條檢查 `hasattr` 的行(它查的是「有沒有具名實作」,跟排序行為本身是兩件事),往下數:①前置、②排出來要一樣、③不得增減候選……第 2 條正好是翻紅的那條。核對正確。

引句:「翻紅釘:把排序鍵末項改回 `r["node"] if r.get("home") else ""` → 第 2 條翻紅。」

severity: clean
blocking: 否——編號依直觀讀法核對得上實測結果。

## 發現四:「不得增減候選」「事故仍排最前」都真的在守,不是空跑

| 植入 | 跑哪支 | 實際輸出 | 判定 |
|---|---|---|---|
| `_sort_pins` 內 `out = list(pins)[:-1]`(拿掉一筆) | `t_impact_pins_order_is_total` | 「排序不得增減候選(只換順序)」翻紅,且後面 `got.index(...)` 因為節點不在清單裡直接丟例外 | 守得住 |
| 把首鍵改成常數 `False`(拿掉「事故永遠最前」) | `t_impact_pins_order_is_total` | 「事故仍排最前」翻紅,輸出變成 `['Systems/Z.md', 'Systems/A.md', 'Systems/M.md']` | 守得住 |

引句:「check("排序不得增減候選(只換順序)", sorted(_order(base)) == sorted(r["node"] for r in base), "")」

severity: clean
blocking: 否——兩條都在變異測試下準確翻紅。

## 發現五:「家仍排在非家之前」是假守衛——靠 fixture 給的分數巧合過關,拿掉真正的優先鍵測不出來

這條斷言用的 `mixed` fixture 裡,家節點的分數是 `0.9`(非零)。`_sort_pins` 的排序鍵是 `(kind != incident, not home, -score if home else 0.0, node)`。因為 fixture 裡家節點分數恆為正,第三鍵 `-score` 對家節點永遠是負值、對非家節點恆是 `0.0`,單靠第三鍵就已經能把家排到非家前面——第二鍵 `not home` 事實上完全沒被用到。

實測:把 `not r.get("home", False)` 改成常數 `False`(相當於拿掉「家優先」這一條規則本身),用測試自己的 fixture 重跑,六條斷言**全綠**,包括「家仍排在非家之前」;再跑整個 `-k impact` 套件(305 個案例),失敗數與未變異的基線一模一樣(都只有一支跟排序無關、因為 `/tmp` 精簡複製缺檔造成的 `t_prepush_computes_impact_once`)——也就是說,拿掉「家優先」這條規則,**全 repo 跟 impact 相關的測試沒有任何一條會翻紅**。

| 植入 | 跑哪支 | 實際輸出 | 判定 |
|---|---|---|---|
| 第二鍵 `not r.get("home", False)` 改成常數 `False` | `t_impact_pins_order_is_total`(用它自己的 fixture,家分數 0.9) | 6 條全綠,「家仍排在非家之前」照樣通過 | **守不住** |
| 同一植入 | `python3 test_lumos.py -k impact`(305 案例) | 305 passed(跟未變異基線失敗數相同,唯一失敗是環境缺檔的 `t_prepush_computes_impact_once`,跟排序無關) | **守不住** |
| 同一植入,改用分數為 0 的家節點手動呼叫 `_sort_pins`(不進測試檔,只是驗證機制本身) | 直接呼叫 `m._sort_pins` | 家節點排到非家之後(`['Systems/A.md', 'Systems/M.md', 'Systems/Z.md']`) | 證實第二鍵確實有實質作用,只是被 fixture 的非零分數蓋住了 |

而分數為 0 的家節點不是理論邊角案例——`_impact_mark_home` 自己的註解就寫明「還不是候選的 → 新增一項,種類 home、分數 0(必推不看分數決定去留)」,這是新確認家但原本沒進候選集時的常態路徑(`scripts/lumos:22827`,實際賦值在 `scripts/lumos:22856` 的 `"score": 0.0`)。只要這種分數 0 的家節點跟一個分數非零的非家候選同席,拿掉第二鍵就會把它排到非家後面,而現有的整套測試(含這支新測試跟既有的 `t_impact_pins_order_incident_home_rest`)都測不出來。

引句:「mixed = [{"node": "Systems/Z.md", "pinned": True, "kind": "contract", "score": 0.9, "home": True},」

file: `scripts/lumos:22827`
file: `scripts/lumos:22856`

severity: major
blocking: 是——這條斷言的名字說要守「家在非家之前」,但實測整個 impact 測試套件對這個具體回退零反應,是靠 fixture 分數巧合過關的假守衛,不是真的在守這條規則。

## 小結

這支測試對它最核心的目標——「固定席同分候選必須是全序,不能把順序交給不穩定的上游」——守得住:直接查產品具名實作、前置檢查不是套套邏輯、翻紅釘核對正確,拿掉修法本身會準確翻紅。「事故仍排最前」「排序不得增減候選」兩條回歸檢查也都用變異測試證實真的在守。

但有兩處守不住,而且都是這支測試自己的措辭在承諾要防的事:①「單一來源」那條檢查只查名字存在,查不到「還有第二份」——這次審的提交裡,`cmd_impact_diff` 就已經自己另外寫了一份幾乎同義的排序鍵,完全繞過 `_sort_pins`;②「家仍排在非家之前」那條斷言靠 fixture 給的非零分數巧合過關,把真正負責這條規則的排序鍵整個拔掉,不管是這支新測試單獨跑還是整個 impact 套件(305 案例)一起跑都不會翻紅,而分數為 0 的家節點在產品邏輯裡是常見情境而非邊角案例。

全篇最高等級為重大,阻塞項有兩條。
