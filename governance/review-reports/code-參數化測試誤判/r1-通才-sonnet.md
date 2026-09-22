severity: blocker

## F1 declared-count 靠的是「掃不到縮排/類內方法」的既有天花板,真撞名會被誤判成參數化而放綠

severity: blocker
blocking: yes

觀察到什麼:新判準的核心邏輯是「N≥2 時,再看程式裡宣告了幾支名字對得上的測試(declared);只有一支就當成參數化、照常判紅綠,兩支以上才判測試名要唯一」。

引句:「            # 只宣告了一支、卻收集到好幾個案例 → 同一支測試的多組輸入,一起跑全綠才算過」
引句:「    return sum(1 for nm in methods if m in str(nm))」

`declared` 的來源是 `methods_for(plat)`,也就是 `discover_test_methods()` 用 `method_re` 對原始碼做**靜態行首錨掃描**得到的名字集合。python profile 的 `PYTHON_TEST_RE` 是 `(?m)^def (t_[A-Za-z0-9_]+)\s*\(`(`scripts/lumos:3826`),`^` 錨死在欄位 0——這條規則本身在同一支檔案裡被明講是已知天花板:「Python:行首錨(欄位 0)——排除巢狀/類內/縮排 def…無框架註冊標記可錨=誠實天花板」(`scripts/lumos:3824-3825`),`python` profile 的 `attr_hint` 也寫著「行首 def t_*/def test_*(名字錨非框架註冊——無斷言 helper 也會被認,天花板)」(`scripts/lumos:4000`)。

問題是:這條**已知會漏掃類內/縮排方法**的靜態掃描,在這次改動之前只影響 real/dangling 判定(綁定存在性),風險有限;這次改動把它拿來**當「要不要豁免測試名不唯一檢查」的守門依據**,而真正跑測試時的過濾是子字串比對(`{method}` 佔位符餵給 `pytest -k` 之類的指令),**子字串過濾不管縮排、不管在不在 class 裡**——於是「靜態掃描漏看的第二支測試」會被 pytest 真的選中、真的一起跑,但 `declared` 卻只算到 1,新判準就把它當成「同一支測試的參數化」放行,不再印「測試名要唯一」。這正是派工單鏡頭③要打的「把其實撞名誤判成參數化而放行」,而且是全部三個呼叫點(`_spec_gate_run_clauses`/`_spec_gate_regress`/`_spec_gate_push_one`)共用同一支 `_spec_gate_declared`,三處全部會中。

怎麼重現(實際跑出來,不是推論):

1. 建立 `/tmp/sg-repro/tests/test_x.py`:
```python
def test_alpha():
    assert True


class TestGroup:
    def test_alpha_variant(self):
        assert True
```
這是兩支完全不相干、各自獨立宣告的測試(不是同一支測試的參數化),只是名字撞了子字串。

2. 用本機找得到的 pytest 驗證「真的跑會選到兩支」:
```
$ /private/tmp/audit-c-copy/.venv/bin/python -m pytest -k test_alpha -q
..                                                                       [100%]
2 passed in 0.01s
```
確實選到、跑了 2 支,不是 1 支參數化出來的 2 個 case。

3. 用改動後的 `discover_test_methods` 直接查這個 repo 的靜態掃描結果:
```
>>> methods = discover_test_methods("/tmp/sg-repro")
>>> methods
{'test_alpha'}
>>> _spec_gate_declared("test_alpha", methods)
1
```
`test_alpha_variant` 因為縮排在 class 裡,完全沒被掃進 `methods` 集合——`declared` 只算出 1。

4. 走完整的 `lumos spec-gate`(`.lumos/config.json` 的 `test.run_cmd` 指到上面那支 pytest,`[S1]` 綁 `[test:test_alpha]`):
```
[spec-gate] 跑: S1 綠(test_alpha)
[spec-gate] 匯總: 條款 1/綁了 1/靠人 0/紅 0/綠 1/弱證據 0/相依回歸 0 支綠
```
完全沒有「篩選匹配到 2 支」或「測試名要唯一」的字樣——判定直接是乾淨的綠,跟改動前(任何 N≥2 一律 weak)行為相反。

為什麼是 bug 而不是風格:這條規格閘本身的職責是「風險低的計劃才不派審,直接放行」(`[spec-gate] PASS(風險低):直接實作,不派審`)。這裡示範的是**兩支互不相干的真測試,一支綁對、一支意外被子字串選中**——這正是「測試名要唯一」這條檢查原本要擋的情境(要求換更長、不互為子字串的名字),而不是這次要修的「同一支測試參數化」情境。改動前,任何 N≥2 都無條件判弱證據,這種撞名一定會被攔下;改動後,只要撞到的那支恰好落在靜態掃描的既有盲區(縮排/類內方法,官方自己承認的「天花板」),就會被誤判成參數化、悄悄放行成綠,而不會印出任何提示要求改名。這不是把「用例數」改成更準的「宣告數」的單純改進,而是把判準的安全邊界建立在一個本檔自己都承認會漏掃的訊號上,漏掃時反而把本來該擋的情境變得比改動前更寬鬆(從「必攔」變「可能悄悄放行」)。且風險低的規格閘一旦判綠會直接跳過設計審,這個誤判沒有下游補救。

補充驗證(鏡頭①②④⑤,沒發現問題):
- ①三支以上/名字互相包含:`_spec_gate_declared` 用 `m in str(nm)` 純子字串比對(不是正則),沒有正則特殊字元或 ReDoS 疑慮;`declared` 只要不等於 1(0、2、3…或 None)一律落入「測試名要唯一」分支,不是只防兩支,對 3+ 撞名一樣有效(讀 `scripts/lumos:5667-5674` 邏輯即可確認,是 `if declared == 1: pass else: return weak`,沒有另外對 declared 的其他數值分案例)。
- 空字串/底線名字:`method` 為空字串或全空白時 `_spec_gate_declared` 直接回 `None`(`if not m: return None`),回退成跟改動前一樣「不知道就當要防」的保守路徑,沒有被新分支繞過。
- ②多平台/方法集抓不到東西:`methods_for(plat)` 回空集合時 `_spec_gate_declared` 一樣回 `None`(`if not methods: return None`),`declared is None` 不等於 1,一樣落回「測試名要唯一」保守分支,不會因為某平台方法集是空的就被誤放行——這條路徑本身安全,危險的是「方法集非空但漏掃其中一支」(即 F1)。
- ④三個呼叫點傳的平台是否正確:`_spec_gate_run_clauses` 用迴圈變數 `plat`(來自 `_run_bound_tests` 回傳的每筆結果自帶的平台)、`_spec_gate_regress` 用迴圈變數 `plat`(同樣來自 `rres` 逐筆結果)、`_spec_gate_push_one` 用迴圈變數 `pl`——三處都是拿「這一筆測試結果自己所屬的平台」去查 `methods_for`,沒有寫死成 `default` 或誤用另一個變數,`grep -n "_spec_gate_declared(" scripts/lumos` 三處呼叫逐一核對過,平台變數跟同一行迴圈解包出來的平台一致。
- ⑤跟「N==0/被跳過=弱證據」的互動:`_spec_gate_verdict` 判斷順序是「N≥2 先判」→「N==1 且 skipped」→「no-cmd/unproven 或 N==0」→「N is None」;N==0 或 N==1 都不會進入 N≥2 分支,`declared` 對這兩種情況完全不生效,讀 `scripts/lumos:5667-5678` 順序確認過,不會有「宣告了一支但案例數是 0,被 declared 誤判成綠」這種交互。
