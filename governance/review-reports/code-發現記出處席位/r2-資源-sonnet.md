severity: minor

## 結論
修補差異裡我沒找到會讓正常操作失敗的資源問題,只有一條 minor。固定席節點這次沒附(鏡頭計算超時),圖譜鏡頭無固定席可逐條判。就修補碰到的檔,我只能說:`_seat_noise_name`、`_finding_seat_event`、`_loop_next_hints` 的改動都在 `scripts/lumos` 內,不改帳格式、不改既有欄位語意,對其他節點應不影響。

## Finding 1:`_seat_noise_name` 的去尾數字正規式在超長席名上是二次方時間
severity: minor
blocking: 否

引句:「bare = re.sub(r"(?:(?<=[^\x00-\x7f])r)?\d+$", "", role)」

- 位置:file: `scripts/lumos:18058`(修補新增的 `_seat_noise_name`)。
- 原因:這條 `re.sub` 沒有錨定開頭。角色名是「一長串數字,最後接一個非數字字元」時,每個起點都吃到數字尾端、發現 `$` 對不上、再逐位退回。總工作量是 O(n²)。
- 輸入:帳上載體的 `finding_seats` 席名,角色段為 `"1"*n + "_"`,後面再接 `-x`。
- 量測(`python3.14` 直接跑修補新增的兩條正規式):

| n | 耗時 |
|---|---|
| 5000 | 0.106 秒 |
| 20000 | 1.68 秒 |

- 同一個席名在每個「條數」都會被重算一次(`for nm in dict.fromkeys(_seat_noise_name(n) ...)` 在 `for i, names in ...` 內),所以耗時乘上條數。
- 修前版本 `_SEAT_ROUND_MARK_RE` 是帶 `(?=-[A-Za-z][\w.]*$)` 的版本,我沒另外跑。因此這條只能說是修補新增的程式路徑,「修前沒有」不確定。
- 可信度:真實席名都很短,而且這是單人威脅模型。20000 字元的席名不會正常出現,所以降為 minor。
- 做法建議:在角色上加長度上限,或把 `\d+$` 改成 `re.search(r"\d+$", role)` 後再切片。
- 歸因:未判定。我沒有替修前版本跑同一輸入,只確認了新程式碼本身會二次方。
- 重現命令:
```
python3.14 -c 'import re,time;t=time.time();re.sub(r"(?:(?<=[^\x00-\x7f])r)?\d+$","","1"*20000+"_");print(time.time()-t)'
```

## 其他逐項判定(不報)
- `_SEAT_SPLIT_RE = ^(.*?)-(?=[A-Za-z])(.*)$` 錨在開頭,只有一個起點,線性。我量了 `"-"*20000+"1"` 和 `"a"+"-1"*20000+"z"`,都是 0.0 秒。
- `_seat_noise_carriers` 是單趟掃帳,以 `(loop, round)` 為鍵的 dict 只留最後一筆,記憶體跟載體列數成正比。新加的 `and r.get("loop")` 只多一次取值,沒有新迴圈。
- `_finding_seat_event` 裡的 `re.sub(r"\s+"," ",...)` 是線性的,且只在擋下事件時跑一次。
- `cmd_canary` 新增的 `if not loop` 提前擋下,不增加讀帳工作。
- `_finding_seat_required_block` 的 `_loop_ts_key` 是對該迴圈帳逐列各算一次,線性。`_finding_seat_since_key` 多一個 `_DAY_RE.fullmatch`,常數時間。
- 子程序與執行緒:修補沒新增任何子程序、執行緒、檔案句柄或暫存檔,所以「逾時、Ctrl-C 沒被收掉」這條不適用。
- 新測試執行時間:`python3.14 scripts/test_lumos.py -k finding_seat` 共 54 案例通過,總計約 40 秒,遠低於單支 180 秒上限。

## 三問回答
1. 子程序或執行緒在逾時、Ctrl-C、例外時沒被收掉:沒有。修補沒有新增子程序或執行緒。
2. 時間預算在大輸入或慢機器上擋下正常操作或放行:沒有硬性預算。`_SEAT_NOISE_DAYS=56` 只是窗口,不是計時器。
3. 把整份大檔、整本帳或深層巢狀一次讀進記憶體,或做二次方工作(含正規式回溯):整本帳的處理是線性單趟。二次方只出現在 Finding 1 的超長席名上。

最嚴重等級 minor
