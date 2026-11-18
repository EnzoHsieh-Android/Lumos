severity: clean

這一輪沒有 finding,下面照派工詞逐項交代驗過什麼、沒驗什麼。

## 圖譜鏡頭固定席逐條判

- `Systems/kotlin規則包.md`(家)不受影響。修補只動 `api.yml` 的字面值判斷、`choice-batch2.kt` 樣本、`test_lumos.py` 與計劃筆記,`check.py` 在修前修後之間沒有差異。
  - 該節點的說明沒有講「字面值要以 `-`、`+` 開頭」這種句子。
  - 全 repo 搜「正負號、前綴運算式、`^[-+]`」,只在 `api.yml` 的註解與計劃範圍 2 那一行出現,兩處與新程式一致。
- `Systems/bound-tests-gate.md` 的 ★INVARIANT★ 不受影響。修補沒有碰 `scripts/lumos` 的綁定測試閘。我在臨時副本跑 `-k t_bound_tests_g`,結果 16 passed, 0 failed。
- `Systems/guard-kill.md`、`Systems/lumos-cli-lifecycle.md`、`Systems/測試假綠形態.md`、`Systems/lumos-cli-read.md` 的 ★INVARIANT★ 都不受影響。修補沒有改到 `scripts/lumos`,這幾條合約的綁定測試沒有動。
- `Systems/pitfalls-code-loop.md`、`Systems/loop-convergence-recording.md`(★RISK★)不受影響,理由同上。
- 超出上限只列名的節點,我沒有逐篇讀。修補沒有碰 `scripts/lumos`,我判這些節點不受影響。
- 「這次新增的殘留」段寫著算不出來(派工鏡頭時間預算用完),我也沒有展開。
  - 修補差異沒有動 `governance/residual-index.json`。
  - 我沒有核對治理帳的 residual-ask 列,所以那段的必答題(殘留問答有沒有換編號或改字重問、第二個代理是不是另一個代理)我答不出,標為未判定。

## 鏡頭 1 到 3

- **鏡頭 1(指令與語意):** 這次改動的文件(`r6-repair-docs.patch` 與計劃範圍 2)沒有新增任何「lumos 會做 X」或指令敲法的句子,所以沒有可對照的指令旗標或預設值。
- **鏡頭 2(計劃、條款、型錄與實作):**
  - 計劃新句說「不比對開頭是不是 `-`、`+`;`@Suppress("x") 1` 也是前綴運算式、算常數;`-k + 1` 是二元運算、不算」。
  - 對照 `api.yml`:兩份 `literal-arg` 都改成只留 `kind: prefix_expression` 加「最後一個子節點是數字常數」,與句子一致。
  - 兩份改動逐行相同,「C-36、C-37 的 literal-arg 兩份一字不差」仍成立。
  - 〈統計〉列數、`Systems/kotlin規則包` 與 `Systems/規格閘` 的改句這輪沒有動;修補沒有新增列,所以列數不變。`check.py` 型錄檢查是「規則 228 條,問題 0 個」。
  - 計劃筆記 `lumos lint` 0 問題。
- **鏡頭 3(合約):** 改到的筆記裡沒有 ★INVARIANT★ 行被動到。

## 修補鏡頭三問

**① 原問題的修復效果**
- claim:`LaunchedEffect(@Suppress("x") 1)` 應該不命中(標註加常數仍是常數),`LaunchedEffect(-k + 1)` 仍要命中。
- input:`choice-batch2.kt` 第 118、119 行,各用兩版 `api.yml` 掃。
- expected:修後只有第 118 行命中。
- before(c261a154 的規則加修後樣本):第 118 行與第 119 行都命中 C-36,`@Suppress` 那行被誤命中,整份樣本共 33 個命中。
- after(8333987a):只有第 118 行命中 C-36,整份共 32 個命中。
- comparison:修補消掉了 `@Suppress` 那行的誤命中,`-k + 1` 沒有被誤收。
- 翻紅釘:我把修後的 `api.yml` 裡的 `kind: prefix_expression` 全部刪掉,`t_choice_samples_batch2` 翻成 32 passed, 1 failed。紅的是 C-36 第 112、118 行的 HIT 樣本。判這條測試抓得到這個改壞。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 修後版本跑下列測試全綠:`choice_points_compose` 7、`kt_catalog` 320、`choice_table_batch2` 22、`choice_samples_batch2` 33、`t_bound_tests_g` 16。
- 沒有逐支跑 `t_choice_points`、`t_choice` 兩組,只信 r6-behavior-cases.md 寫的「跑過一次全綠」,這部分算未驗。
- 相鄰寫法 `!true`:不在數字清單裡,所以仍是命中。這是原本 `^[-+]` 時就有的行為,不是這次修補造成的,我也不判它是缺陷。
- `C-0` 與 `A-0` 的測試案例:`check.py` 在修前修後沒有差異,擋它的是 `check.py` 的 `[CA]-[1-9][0-9]*`,所以這兩條測試只是把原有行為補上釘子,不是行為變更。
- preserve:修前就有的 `-1`、`-1L`、`-0x1F`、`+2.5` 不命中,`-1.coerceAtLeast(k)`、`-k` 命中,這幾行在修後 `t_choice_samples_batch2` 全過。

**③ 新發現**
- 沒有新發現,所以沒有修前修後對照。
- 附帶看到一點,不構成 finding:樣本 `my.kotlinx.coroutines.flow.combine(a, b)` 標 HIT。我讀它是保守的「只認整串完整套件名」寫法,看不出具體失敗場景。

歸因:無 finding,不適用。

未驗範圍:
- 變異掃描與差異比對(r5-mutsweep)沒有重跑。
- 括號包住的常數 key 照樣命中、引數層層巢狀的輸出平方成長這兩條沒有自動測試,我也沒補。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/合約-sonnet` 已用字面絕對路徑刪除,刪前 `lsof +D` 確認沒有程序開著。

最嚴重:clean;blocking 共 0 條
