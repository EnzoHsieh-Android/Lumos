# code-簡報審查抓到的機制缺口-std r3 收貨

兩位全新席(最後一輪),審修補後整包 r3-pack.patch(551 行)加修補差異 r3-repair-review.patch(316 行);修補來源 r3-repair-binding.json(修前 0f2989d0 → 修後 771f6c11)。

## 機械收貨

- 兩份報告都已是正規化格式;quote-check 對 r3-snapshot.patch 全數錨定;refcheck 正確性 4 處、架構對齊 4 處全對。
- 兩席沒動 repo;兩席臨時目錄收齊後用字面路徑刪除(lsof 確認沒有程序在用)。

## 判讀(id:正確性席 h、架構對齊席 g)

| id | 席位等級 | 觀察重現 | 歸因 | 去向 |
|---|---|---|---|---|
| h1 | major | HIT:把規則的 launchIn 整段刪掉,`-k kotlin_rulepack_security_rules` 449 passed, 0 failed;逐例表的「不報」例沒有「同形狀在畫面類別裡會報」的對照,基底版測試檔對這條規則 0 處提及 | 原有漏查(規則偵測段三版相同) | 折:補 C242(Fragment 裡七種偵測寫法各一行,寫死第 5~11 行)、C243(四種已包生命週期的寫法不報),逐項重放十一種刪法 |
| g1 | minor | HIT:審計修正紀錄寫「代碼審 light r1」,預期值表與測試註解寫「代碼審 r1」;鄰居用「代碼審 r1」指沒尾碼的迴圈 | 修復回歸(r2 改輪次標籤時沒同步這兩行) | 折:改成「代碼審 r1(…,light)」 |
| g2 | minor | HIT:改了正反樣本,條款只綁逐例表那支;部分鄰居會另綁樣本自測 | 原有(條款在輕量審 r1 就改綁) | 折:加 [S5] 綁 t_kotlin_rulepack_samples,預期值表補一列 |

編排者機械重現不到的:無(refuted none)。修復回歸集合:g1。

## 先查世界

PRIOR-ART: 規則逐例測試除了驗「例外有效」,也要有「被保護的形狀本身會被認出」的正例,不然「不報」分不出是例外生效還是規則根本沒認出;這就是 Systems/測試假綠形態 那條合約要的前置斷言,也是變異測試(Stryker Weapon regeX)每個選項都要有測試殺得死的原則。本輪對規則原有的每個比對樣式與排除各做一種刪法。

## 翻紅釘

```
M12 拿掉 lifecycleScope.launch($$$): 紅的列 ['C242'] | 451 passed, 2 failed
M13 拿掉 $O.lifecycleScope.launch($$$): 紅的列 ['C242'] | 451 passed, 2 failed
M14 拿掉 launchIn(lifecycleScope): 紅的列 ['C242'] | 451 passed, 2 failed
M15 拿掉 launchIn($O.lifecycleScope): 紅的列 ['C242'] | 451 passed, 2 failed
M16 拿掉 collect($$$): 紅的列 ['C242'] | 451 passed, 2 failed
M17 拿掉 collectLatest { }: 紅的列 ['C242'] | 451 passed, 2 failed
M18 拿掉 collectLatest($$$): 紅的列 ['C242'] | 451 passed, 2 failed
M19 拿掉 repeatOnLifecycle 排除: 紅的列 ['C243'] | 451 passed, 2 failed
M20 拿掉 $L.repeatOnLifecycle 排除: 紅的列 ['C243'] | 451 passed, 2 failed
M21 拿掉 collect 分支的 flowWithLifecycle 排除: 紅的列 ['C243'] | 451 passed, 2 failed
M22 拿掉 launchIn 分支的 flowWithLifecycle 排除: 紅的列 ['C243'] | 451 passed, 2 failed
restored True
```

修後 `-k kotlin_rulepack` 511 passed, 0 failed;計劃 lint 0 問題、spec-trace 3 條款全標。
