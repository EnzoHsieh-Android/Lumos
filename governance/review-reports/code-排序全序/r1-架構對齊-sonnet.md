severity: minor

# 架構對齊審查:固定席排序抽成 `_sort_pins`

判準只看「跟既有做法一不一樣」,不判排序邏輯本身對不對。逐項對照如下。

## 發現一:抽成具名函式的形狀、docstring 寫法對齊既有「唯一實作」前例

這支專案對「同一件事只准一個實作」確實有既有紀律,只是最貼切的前例不在 `scripts/lumos` 本檔,而在
`governance/eval/retrieval_eval.py` 的 `_edit_orders`(`governance/eval/retrieval_eval.py:436`)與
`collect_unjudged`(`governance/eval/retrieval_eval.py:238`)。`_edit_orders` 的 docstring 開頭就是
「★edit 面三條排法的唯一實作★」,接著寫根因(誰複製了一份、複製時怎麼抄錯)、再寫「往下游的殺傷力」、
結尾一句「改這裡就是同時改兩邊」——這正是 `_sort_pins` 的 docstring 套用的同一種四段式(唯一實作宣告→
根因→下游殺傷力→不要在別處再寫一份)。抽取位置也對齊:`_edit_orders` 緊貼在呼叫它的 `eval_edit` 之前,
`_sort_pins` 同樣緊貼在呼叫它的 `cmd_impact` 之前。這一項是照既有前例做的,沒有引入新形狀。

引句:「★改這裡就是改所有固定席的呈現順序★,不要在別處再寫一份。」

severity: clean
blocking: 否——抽取手法、docstring 結構、放置位置都對齊本 repo 既有的「唯一實作」寫法前例,沒有另立一套。

## 發現二:排序鍵末項改成「一律用節點名」,反而是把 pins 排序拉回本檔其餘排序的既有慣例

`scripts/lumos` 裡候選排序幾乎全部收斂成「score 為主鍵、其餘輔鍵、末項一律是節點名斷同分」這一種形狀,
而且末項的節點名從不是條件式的。同一支 `cmd_impact` 函式裡,`free`、`dropped`、`lane_raw` 三處排序
用的都是同一把鍵:

- `scripts/lumos:23301`:`free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))`
- `scripts/lumos:23331`:`dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))`
- `scripts/lumos:23340`:`lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))   # 同 free/rescued 三鍵慣例`(註解自己點名這是共用慣例)

改動前的 `_sort_pins`(home 分支)末項寫成 `r["node"] if r.get("home") else ""`——只有一部分列有節點名可斷、
其餘拿空字串,等於局部放棄全序,這才是跟上面三處慣例不一致的地方。這次的修法把末項改成無條件的
`r["node"]`,是把 pins 排序拉回跟 free/rescued/lane 同一種「末項一律是真實節點名」的形狀,不是另發明第二種。

引句:「-r["score"] if r.get("home") else 0.0, r["node"]))」

severity: clean
blocking: 否——修法方向是修正既有的局部偏離,讓 pins 排序跟同檔 free/rescued/lane 三處的既有三鍵慣例對齊,不是引入新的排序哲學。

## 發現三:新函式沒有掛上 `cmd_impact` 私有輔助函式一致使用的 `_impact_` 字首

在 `_sort_pins` 前後同一個區塊裡,支援 `cmd_impact` 的私有函式一共 16 支,全部都用 `_impact_` 開頭
(逐一核對 `scripts/lumos:22406,22419,22487,22530,22591,22636,22712,22731,22795,22822,22861,22889,22904,22911,22976,23460,23472`,
例如 `scripts/lumos:22822` 的 `_impact_mark_home`、`scripts/lumos:22861` 的 `_impact_mark_about`、
緊鄰在 `_sort_pins` 正上方的 `scripts/lumos:22976` `_impact_load_config`)。這個字首在這一段是 100% 一致
的命名慣例,等於是「屬於 cmd_impact 這組」的命名空間標記,方便之後用 `_impact_` 一次搜出所有相關輔助函式。
新函式取名 `_sort_pins`,不帶 `_impact_` 字首,是這一段裡唯一的例外——不是「命名喜好」這種可換可不換的
美感差異,而是這一段既有的、看得出規則性的分組慣例被跳過了一次。

引句:「def _sort_pins(pins, home_on):」

severity: minor
blocking: 否——只影響用字首搜尋輔助函式時的可發現性,不造成重複實作或行為分岔;之後任何一次改名都能無痛補上,不是結構性風險。

## 發現四:新測試改用「直接呼叫私有函式 + 手造字典 + 洗牌驗全序」,跟同一批 pins 排序既有測試的 CLI 子行程慣例不同,但在本檔裡各有前例

`scripts/test_lumos.py` 裡管「pins 順序」這件事本來就有一支既有測試
`t_impact_pins_order_incident_home_rest`(`scripts/test_lumos.py:38621`),走的是「先用 `_nh_repo`/`_nh_node`
真的建 git 版控節點與檔案,再呼叫 `_home_impact`(`scripts/test_lumos.py:38530`,內部是 `subprocess.run` 起
一個真的 `GRAPHCTL impact --json` 子行程)拿到 JSON 結果去斷言順序」。這條路徑上其餘管 pins/home 的測試
(`t_impact_home_is_additive_only`、`t_impact_home_knob_off_is_old_behavior`、`t_impact_pins_order_incident_home_rest`
等)清一色是這種「真 fixture + CLI 子行程」形狀。

新測試 `t_impact_pins_order_is_total`(`scripts/test_lumos.py:11729`)不建任何 vault/git fixture、不起子行程,
而是 `m = _load_lumos_inproc()` 之後直接呼叫私有函式 `m._sort_pins(...)`,輸入是測試自己手造的 dict 列表。
就「這一支 pins 排序測試專屬的既有慣例」而言,這是不同的做法。

但把範圍放大到全檔,直接呼叫 `scripts/lumos` 私有函式(包含帶 `_impact_` 字首的)在測試裡並非首例:
`t_impact_home_uses_nodehome_definition`(`scripts/test_lumos.py:38903`)一樣用 `_load_lumos_inproc()`
之後直接呼叫 `m._nodehome_side`、`m._nodehome_homes`、`m._impact_home_map`、`m._home_confirmed`、
`m._nodehome_top_dirs` 這些私有函式(只是那支測試仍搭配真實建出的 git fixture,不是純手造字典)。而「手造
合成資料 + 直接呼叫私有排序函式 + 用固定種子洗牌驗證全序不受輸入序影響」這個更具體的形狀,在
`governance/eval/retrieval_eval.py` 那條姊妹線已經有現成前例:`t_eval_edit_orders_single_source` 直接
呼叫 `m._edit_orders(res)`、`res` 是測試手打的 dict 列表;同檔 `scripts/test_lumos.py:27458` 也有
`_rnd.Random(99).shuffle(_l)` 這種固定種子洗牌驗證順序穩定性的寫法。新測試等於是把這個已存在但目前只
出現在 `governance/eval` 那條線的形狀,第一次搬進 `scripts/lumos` 自己的 `t_impact_*` 測試群,跟這一批
既有的「CLI 子行程」寫法並存,而不是取代或刪掉舊測試。

引句:「return [r["node"] for r in m._sort_pins(list(rows), True)]」

severity: minor
blocking: 否——直接呼叫私有函式在本檔測試裡(`t_impact_home_uses_nodehome_definition` 等)與姊妹檔 `governance/eval/retrieval_eval.py` 的測試裡都有前例,不是無中生有的第二套測試哲學;新測試與舊測試 `t_impact_pins_order_incident_home_rest` 並存,沒有互相取代或製造行為判定衝突,只是把驗證全序穩定性這個更適合單元隔離的性質,挑了本檔目前較少用、但確有先例的測試形狀。

## 總結

抽成具名函式的手法與排序鍵慣例都對齊既有前例,找到的兩點落差(命名字首缺口、測試改用直接呼叫)
分別在本檔與姊妹檔裡都能找到可對照的前例,不涉及重複實作或跨層破壞既有邊界,都不需要卡住這次改動。

全篇最高等級:輕微;阻塞項:0 條。
