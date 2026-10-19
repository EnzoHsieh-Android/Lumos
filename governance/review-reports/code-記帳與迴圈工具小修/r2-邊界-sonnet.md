severity: major

範圍:邊界與輸入鏡頭,修補鏡頭(修前 d2da0e8c,修後 f791d8ba)。實驗都在 `/tmp/lumos-seat-work/code-記帳與迴圈工具小修/邊界-sonnet/`,用修前、修後兩份 `scripts/lumos` 對同一個輸入各跑一次。修後的 `scripts/lumos` 與 f791d8ba 逐字相同(已用 diff 比對)。

## Findings

**1. `--regression-set none` 在發現清單有叫 `none` 的 id 時行為翻轉:第一輪死路,之後的輪次記錯資料**
severity: major
blocking: 是
歸因:有證據的修復回歸
- 變更:修補把 `--regression-set` 的 none 判法改成跟 `--folded-set` / `--accepted-set` 共用的 `_set_or_none`。這支規定,發現清單裡有叫 `none` 的 id 時,none 要照字面當 id。
- 資料基礎:計劃與帳上確有這種真實 id,真帳有 5 筆 `findings_set=['none']`。
- 計劃矛盾:計劃第 2 節寫的是「`--regression-set` 照舊整串 none=空清單」,修補跟它不一致。
- 重現(`e6.py`、`e7.py`):載體帶 `--findings-set none --folded-set none --tier standard --regression-set none`。

| 情境 | 修前 | 修後 |
|---|---|---|
| 第一輪 | rc0,`regression_set=[]` | rc2,訊息「這是第一輪…--regression-set 只能寫 none」,自相矛盾 |
| 第二輪 | rc0,`regression_set=[]` | rc0,帳上寫成 `['none']`,等於宣稱 id「none」是上一輪修補造成的 |

- 第一輪的出路:只剩寫 `None`(大寫 N)繞過。`None` 因為跟字面 id `none` 不同(`items[0] not in _f_ids` 比對區分大小寫)才被當空集合。這個出路沒有任何訊息或文件提到。
- 第二輪的影響:帳本只進不出,寫進去就撤不掉。
- 缺的測試:`t_canary_record_regression_set_code_only` 與 `t_canary_regression_set` 沒有「發現清單含 `none` id」的案例,所以全綠。
- 修法:`--regression-set` 的 none 不吃「發現清單有 none 就當 id」這條,或對這種情況給明確的出路。
引句:「rg = sorted(set(_set_or_none(regression_set)))   # none 的判法與切法跟折入、放行同一支(代碼審 r1 通才 3)」

**2. 擋下訊息裡的示意指令,對長編號與含控制字元的編號會給出另一個編號**
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前這兩種輸入給的是原字串)
- 變更:`q = _shlex.quote(_esc_clean(str(loop), 80))`。`_esc_clean` 會把控制字元(換行、Tab)換成空格,超過 80 字就截斷並加 `…`。
- 重現(`e2.py`):
  - 編號 `code-` 加 100 個「長」,第一筆沒帶 `--round`。修前示意指令是完整編號。修後是 `'code-長…(80字)…'`,結尾帶 `…`。照抄會開出另一個迴圈。
  - 編號 `code-a\nb\tc`。修前示意指令是原字串(換行與 Tab 原樣)。修後變成 `'code-a b c'`,也是另一個編號。
- 好的部分:`code-x'; touch /tmp/p #`、`code-$(id)`x``、中文加空白,引號都正確,沒有注入。
- 缺的測試:沒有任何測試覆蓋超過 80 字或含控制字元的編號。
- 建議:引號只對沒被改過的原字串做;被改過就不印可貼的指令。
引句:「q = _shlex.quote(_esc_clean(str(loop), 80))」

**3. 帳整本不是 UTF-8 時,`--orchestrator` 路徑仍會冒出 UnicodeDecodeError 堆疊,修補新增的友善訊息走不到**
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後都一樣;修補動到這行但保留了會丟例外的退路)
- 重現(`e9.py`):帳裡有一列含 `\xff`,執行 `canary record none --loop code-e9 --round r1 --orchestrator <編排者> --tier standard`。修前與修後都是 rc1,輸出 `UnicodeDecodeError`。
- 原因:`_recs = _lrows if _lerr is None else _loop_records(env, loop)`。帳壞時退回 `_loop_records`,它遇到整本非 UTF-8 會重丟例外。修補要擋下的就是這種帳,但這條路在輪次規則檢查之前就炸了。
引句:「_recs = _lrows if _lerr is None else _loop_records(env, loop)」

**4. 最後一列壞掉且沒有換行時,寫側不擋,新記錄黏在壞列後面**
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後輸出相同,不是修補造成)
- 重現(`e3.py`、`e4.py`):帳內容是 `{"loop":"code-e3","rou`(沒有換行),再記一筆 `code-e3` 的帶輪次記錄。修前修後都是 rc2「落盤自驗失敗」,但帳多了 504 位元組,新記錄黏在壞列後面。這筆記不上,帳裡多一行永遠讀不了的黏合列。
- 原因:`_canary_ledger_rows` 靜默略過壞列,所以寫側的「帳讀不懂」只認得非 UTF-8 與輪次非字串兩種。使用者看得到失敗訊息,資料沒有被悄悄弄壞,所以只列 minor。

## 已驗主張(無問題)
- **`--round` 純空白**:`"\t"` 與 `"  "` 修前 rc0,帳上 `round` 寫成 Tab 或空白。修後 rc2 並走「每筆要帶輪次」,修補有效。
- **`--regression-set` 空值判法**:`\t`、`,`、`""` 全部 rc2(`\t` 修前 rc0,是修補修好的)。`None`、`NONE `、` none ` 都得到 `[]`。`none,none`、`a1,none` 在發現清單沒有 none id 時 rc2。非 code- 編號 rc2。
- **結局帳排除**:
  - 同編號只有結局帳時再記帶輪次的席,修前 rc2(把結局帳算成不帶輪次),修後 rc0。
  - 帶輪次的迴圈加結局帳,`loop next` 修前 rc2 混用,修後正常。
  - `loop status --panel` 修前 rc2,修後正常。
  - 副作用:結局帳不再算進循序舊迴圈的輪數。`legacy+outcome` 的 `loop status` 從「跑了 2 輪」變成「1 輪」,`loop next` 從「接下來第 3 輪」變成「第 2 輪」。這是設計意圖,也避免結局帳被當成乾淨輪而假收斂。
  - 小副作用:只有結局帳的編號,`loop next` 現在報「全新編號、沒有任何記錄」。
- **帳壞範圍**:非 UTF-8 只在別的編號的列時,任何編號都擋,訊息講「整本判不了」,符合修補宣稱。輪次非字串只擋自己的編號,別的編號放行(`e3.py` 已驗)。
- **其他邊界**:空帳、只有一列、缺 `loop` 欄的合法 JSON 列、`loop` 為 null 或 list 的列、CRLF 帳,都跟修前行為一致且不誤擋。
- **局部測試**:`-k outcome`、`round_format`、`regression_set`、`set_none` 四組全綠(16、15、15、5)。

## 未驗與觀察
- `--round` 為 `r 1` 或全形 `ｒ１` 時,修前修後都原樣寫進帳。這是原有行為,不是修補造成,也沒有被 `_review_rows` 影響。
- 驗收條款 S17、S18 照字面可以寫成會紅的測試,但沒有條款涵蓋「發現清單含 none id 時的 regression-set」,這正是 finding 1 漏掉的原因。
- 沒有逐條核對 r1-fix.json 的配對案例。沒有跑全套測試。

## 三問
1. **原問題的修復效果**:
   - 有行為證據的:結局帳排除、`--round` 純空白、regression-set 空值判法、帳壞範圍,都在修前修後各跑一次,結果如上。
   - 其餘「共用讀帳」「型別說明」「出口訊息」,我只做了邊界輸入的觀察,沒有逐項獨立驗證修復效果。
2. **修補處的正常、錯誤與相鄰路徑**:大部分成立。例外是 finding 1(regression-set 的相鄰路徑翻轉)與 finding 2(訊息出口對長編號與控制字元)。
3. **新發現在修前修後各是什麼結果**:
   - Finding 1 修前正確、修後錯誤,是回歸。
   - Finding 2 修前給原字串、修後給改過的字串,是回歸。
   - Finding 3、4 修前修後相同,不是回歸。

最嚴重 severity:major。blocking 共 1 條(finding 1)。
