severity: minor

我只找到 1 條 finding,是 minor、不擋。其餘極端輸入都實跑或對著代碼走了一遍,沒有出錯。

## Finding

severity: minor
blocking: 否。提示文字誤導,但不會判錯、不會壞帳;找不到會擋下或會做出錯行為的路徑,所以是 minor。

引句:「原因是 `時限不夠` 時同一行接「;合併要先量齊 N 支基準,約需 M 秒,剩 R 秒;要合併請帶 --max-seconds X」」

file: `scripts/lumos:29083`(`_kill_merge_ready` 時限門,diff 裡 `need = len(uniq) * ...` 那段)與 `scripts/lumos:29000` 前後(`_kill_merge_base` 的 `len(lane) < 2`)。

守的測試只有 1 支時,時限門仍然會擋下並建議帶大 `--max-seconds`。照建議重跑,仍會走到 `_kill_merge_base` 的 `len(lane) < 2`,印「合併道不足 2 支」而不合併。所以那個 X 對 1 支的情況永遠無效。這條還在 `_kill_merge_ready` 裡擋,不會走到 `_kill_merge_base`,時限門必定先於「合併道少於 2 支」那道判斷,因為這份 diff 把時限門排到最後。

重現:用假現場呼叫 `_kill_merge_ready`,`run_cmd` 是 `./gradlew :app:testDebugUnitTest --tests '*{method}'`,剩下時限 10 秒,測試只有 1 支:

```
⚠ kotlin:這次不合併(時限不夠),照逐支跑;合併要先量齊 1 支基準,約需 15 秒,剩 9 秒;要合併請帶 --max-seconds 100
```

修法:在 `_kill_merge_ready` 加一道「`len(uniq) < 2` 就記 `合併道不足 2 支`」,排在時限門之前。

另外,「剩 9 秒」是 10 秒被 `int()` 無條件捨去(`int(max(mg.remaining(), 0))`)的結果,純顯示。

## 逐項邊界(實跑或對著代碼走過,都沒出錯)

- **合併失敗名單**:用真的 `_choice_merge_classify` 加 JUnit XML 實跑。
  - 各案名單:

| 輸入 | 名單 |
|---|---|
| 一般失敗 | `['aCase']` |
| 巢狀類別 `p.K$Inner::aCase(int)` | `['Inner.aCase']` |
| 空 classname | `['aCase']` |
| 參數化 `aCase[1]` 失敗、`aCase[2]` 通過 | `['aCase']` |
| 兩個類別同名 `aCase` | `['aCase']` |
| 全部測試都失敗 | 全進名單,順序等於原順序 |
| 失敗的是 `xaCase`(只是字尾像) | `[]`,走原順序 |

  - 名單用 `endswith("." + m)`,所以 `xaCase` 不會誤中。名單空時 `_kill_merge_failed_first` 走原順序。
- **名單裡有合併道外的名字**:名單只從 `names`(合併道)篩,不可能出現道外的名字。
- **時限 X**:實跑 `_kill_merge_ready`,時限剩 10、0、負 50、0.4 且已花 250 秒、30 秒這幾種都沒出錯。
  - 負數有 `max(…, 0)` 擋住。
  - 已花很多秒時 X 照樣進位到百(已花 250 秒給 400)。
  - 這個 X 偏大,但無害。
  - `inf` 與 `nan` 的 `--max-seconds` 走不進提示分支,不會 OverflowError。
- **斷路器剛好第 5 次**:`_kill_merge_breaker` 先累計原因再判 `>= breaker`,所以第 5 次也記進 `unclean`,跳開那行帶最後一次原因。
  - 夾「有失敗」或「編不過」(`counts=False`)時不累計。
  - 原因字串都是固定字串,來源是 `_choice_merge_facts` 與 classify,鍵數有界。
- **single_runs**:`_single` 只在真的跑了單支那一行設,`--json` 輸出有過濾,kill log 是挑欄位寫的,不會漏進去。
  - 略過列、基準不綠的 abort 列、合併判存活的列不計入。
  - 還原失敗那條路會漏計一次,但那是 `break` 的作廢路徑,不影響判定。
- **merge_kind 跨平台**:`kinds[(plat, group)]` 與 `judged` 用的 `survived` 同一把鍵,所以 judged 為 merged 時所有平台都是 pass。
  - 沒跑快篩的平台組記 `none`。
  - 還原失敗(`break`)與快篩被中斷這兩種,快篩其實跑過但記成 `none`,屬標記精度,不影響判定。
- **舊帳與錯型別帳**:`_gov_row` 對缺欄位的舊帳給空字典或 0。型別錯的帳整行會被 `_gov_event_types_ok` 丟掉,這是既有行為,新欄位沿用,不是新問題。
- **平台名**:`off`、`unclean`、`kinds` 都以平台名為鍵,迴圈裡一個平台名只出現一次,不會互相覆蓋。
- **測試名含空白、中文、引號**:合併道的名稱檢查走既有的 `_test_name_ok`,不過就記 `名稱檢查沒過`,`_choice_merge_fullname` 純字串處理。

## 圖譜鏡頭

這次沒附固定席節點(鏡頭計算超時),所以沒有節點可逐條判,不下結論。

最高 severity 是 minor,blocking 條數為 0。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點變異加速第二段/邊界-sonnet` 已用字面絕對路徑刪除。
