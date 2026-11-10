# code-簡報審查抓到的機制缺口 r1 收貨

分級 light(pitfalls:改動裡沒有程式檔),只派一席架構對齊。完整凍結材料 r1-snapshot.patch 2494 行超過 1800,席位審的是排除設計審卷證、replay 與兩本帳的 r1-pack-arch.patch(547 行)。

## 機械收貨

- report-normalize:已是正規化格式,不用改。
- quote-check(對 r1-snapshot.patch):2 句引言全數錨定。
- refcheck:佐證 8 處全部對得上(missing 0、out_of_range 0)。
- seat-check:派工單形狀沒被認出要查的材料,vacuous 豁免(不判漏查或出界)。
- 收貨時 repo 只有治理帳與這個卷證資料夾有變動,席位沒動 repo。

## 判讀(觀察與判準分開驗)

| id | 席位等級 | 觀察重現 | 判準 | 去向 |
|---|---|---|---|---|
| a1 | major | HIT:`scripts/test_lumos.py` 的 `_KTSEC_CASES` 有選填第五欄「預期報在哪幾行」,`t_kotlin_rulepack_security_rules` 逐列核對;規則本體的改壞列在 docstring 翻紅釘、不寫成測試程式。新測試另從 `// BAD` 記號算預期行、直讀 state.yml、在測試裡改壞規則本體,三處都是專案原本沒有的做法 | 架構對齊錨:引入第二種做法 = major,成立 | 折 |
| a2 | minor | HIT:計劃 S1 綁 `t_kotlin_rulepack_samples`,那支只驗壞例至少兩處命中、好例零命中;S1 後半「Fragment、ProcessLifecycleOwner、Activity 照報」它守不到 | 綁定比條款弱,minor 成立 | 折 |

編排者機械重現不到的:無(refuted none)。

## 先查世界

PRIOR-ART: 逐例表(table-driven test)每列寫死自己的預期值,是 Go 社群與 CockroachDB 測試指南的建議做法;預期值跟實作分開、不從同一個來源算出來,讀的人看列就知道這例在驗什麼。來源:https://skills.sh/cockroachdb/cockroach/table-driven-test 、https://dev.to/usapopopooon/should-test-expected-values-come-from-the-same-place-as-the-implementation-1lnk 。採用:正好是專案 `_KTSEC_CASES` 既有形狀,不另立一套。
PRIOR-ART: ProcessLifecycleOwner 官方類別說明:「You can consider this LifecycleOwner as the composite of all of your Activities」,用途是 App 回到前景或進到背景時反應。來源:https://developer.android.com/reference/androidx/lifecycle/ProcessLifecycleOwner 。採用:照報的理由從「查不到放行依據」改成正面理由(它的 STARTED 就是 App 有畫面在前景,正是這條規則管的情況);這點是面試簡報第三輪看圖審查指出「依據不足」論證薄弱後回頭查的。

## 修法

- a1:Service 例外的七種情況寫成 `_KTSEC_CASES` 新列 C227~C233(完整 kt 檔、第五欄寫死預期行號),刪掉 `t_kotlin_rulepack_lifecycle_service_scope`;改壞規則的手法照既有慣例寫進 `t_kotlin_rulepack_security_rules` 的翻紅釘。
- a2:計劃 S1 改綁 `t_kotlin_rulepack_security_rules`,主詞改成「規則包逐例表」;`Systems/kotlin規則包` 的 WHY 行 `[test:]` 跟著改。
- 順手:壞例樣本與 WHY 行裡 ProcessLifecycleOwner 照報的理由改成上面查到的官方說法。

## 翻紅釘(編排者在工作目錄改壞 state.yml、跑 `-k kotlin_rulepack_security_rules`、還原;腳本在 scratchpad,不進卷證)

```
M1 has 往類別本體裡找(加 stopBy: end): 紅的新列 ['C233'] | 431 passed, 2 failed
M2 名字換成不存在: 紅的新列 ['C227', 'C228', 'C229', 'C230', 'C233'] | 423 passed, 10 failed
M3 拿掉 media3 前綴: 紅的新列 ['C228'] | 431 passed, 2 failed
M4 外層 inside 拿掉 stopBy: 紅的新列 ['C227', 'C228', 'C229', 'C230', 'C233'] | 423 passed, 10 failed
M5 regex 名字出現就算(拿掉 ^ 與建構子括號): 紅的新列 ['C231'] | 431 passed, 2 failed
restored True
```

修後 `-k kotlin_rulepack` 491 passed, 0 failed。
