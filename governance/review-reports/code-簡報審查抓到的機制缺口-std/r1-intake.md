# code-簡報審查抓到的機制缺口-std r1 收貨

light 編號第一筆抓到 major,light 永久失效,照規則改開這個編號走 standard:一位找錯審查員加一席架構對齊。兩席審的是排除卷證、replay 與三本帳的 r1-pack.patch(525 行)。

## 機械收貨

- 兩份報告都已是正規化格式;quote-check 對 r1-snapshot.patch 全數錨定;refcheck 正確性 10 處、架構對齊 15 處全對。
- 收貨時 repo 只有治理帳與這個卷證資料夾有變動,兩席沒動 repo。
- 兩席留在 /tmp/lumos-seat-work/ 的實驗目錄,收齊、存進卷證後已用字面路徑刪除(刪前 lsof 確認沒有程序在用)。

## 判讀(id:正確性席 c、架構對齊席 a)

| id | 席位等級 | 觀察重現 | 判準 | 去向 |
|---|---|---|---|---|
| c1 | major | HIT:拿掉 `androidx\.lifecycle\.|` 後 C227~C233 照綠;逐例表沒有一例寫 androidx.lifecycle. 前綴 | 規則包 WHY 規定每個正規式選項要有例子變紅;被保護的是計劃範圍 1 寫明的行為 → major 成立 | 折:補 C234 |
| c2 | minor | HIT:只拿掉 `^` 時七例全綠;docstring 把 ^ 歸給 C231 | 測試說明與實際不符,且 ^ 沒有守 | 折:補 C235(自寫基底 BaseLifecycleService 照報),docstring 改成逐項 |
| c3 | minor | HIT:LifecycleService 子類別裡用 ProcessLifecycleOwner 收,規則零命中;S1 與 WHY 寫成無條件照報 | 條款對這個輸入兩句互相矛盾 | 折:定為「外圍是 Service 一律不報」,補 C236,計劃範圍 1、S1、WHY 寫明優先順序 |
| c4 | minor | HIT:Issue 的 repro 帶 `# noqa: BLE001`,照做沒有告警可放行 | repro 照字面做不出現象 | 折:repro 改成不加 noqa、寫明要先接 ruff 與 BLE |
| a1 | minor | HIT:計劃依據來源第 4 列只有未提交的工作樹路徑,規格閘判不合 | 會讓規格閘回 1 | 折:補節點連結;另加 ProcessLifecycleOwner 官方依據一列 |
| a2 | minor | HIT:計劃沒有審計修正紀錄節 | 鄰居跑過審查的計劃都有 | 折:補設計審兩輪與代碼審三筆 |
| a3 | minor | HIT:預期值表第 4、6 列在逐例表找不到對應;代碼審補的例子沒標 | 表與測試對不上 | 折:預期值表每列標對應的 C 編號;補 C237(Fragment 裡 PLO)、C238(同檔 Service 旁的 Fragment);代碼審補的另標 |
| a4 | minor | 同 c1 | 同 c1 | 折(併 c1) |
| a5 | minor | HIT:壞例樣本註解指向逐例表編號 C233 | 鄰居樣本註解引用計劃節點,不引用測試編號 | 折:改指計劃節點 |

編排者機械重現不到的:無(refuted none)。

## 先查世界

PRIOR-ART: 正規式的變異測試:Stryker 的 Weapon regeX 專門改壞正規式的錨點、字元類別、次數等,要求測試抓得到,抓不到的算存活變異或等價變異。來源:https://npmjs.com/package/weapon-regex 、https://index-dev.scala-lang.org/stryker-mutator/weapon-regex 。採用:正規式每個選項、錨點、括號各做一種改壞,逐項重放;跟規則包 WHY「每個正規式選項與錨點都要有例子變紅,否則記成等價改壞」一致。括號前的 `\s*` 原本沒有例子,與其記成等價改壞,補一例 C239 成本更低。

## 翻紅釘(編排者在工作目錄改壞 state.yml、跑 `-k kotlin_rulepack_security_rules`、還原;腳本在 scratchpad,不進卷證)

```
M0 不改(基準): 紅的列 [] | 445 passed, 0 failed
M1 has 往類別本體裡找: 紅的列 ['C233'] | 443 passed, 2 failed
M2 名字換成不存在: 紅的列 ['C227', 'C228', 'C229', 'C230', 'C233', 'C234', 'C236', 'C238', 'C239'] | 427 passed, 18 failed
M3 拿掉 media3 前綴: 紅的列 ['C228'] | 443 passed, 2 failed
M4 外層 inside 拿掉 stopBy: 紅的列 ['C227', 'C228', 'C229', 'C230', 'C233', 'C234', 'C236', 'C238', 'C239'] | 427 passed, 18 failed
M5 拿掉 ^ 與建構子括號: 紅的列 ['C231', 'C235'] | 441 passed, 4 failed
M6 拿掉 androidx.lifecycle 前綴: 紅的列 ['C234'] | 443 passed, 2 failed
M7 只拿掉 ^: 紅的列 ['C235'] | 443 passed, 2 failed
M8 只拿掉括號前的空白: 紅的列 ['C239'] | 443 passed, 2 failed
M9 只拿掉建構子括號: 紅的列 ['C231'] | 443 passed, 2 failed
restored True
```

修後 `-k kotlin_rulepack` 503 passed, 0 failed。規格閘:規則檔暫時換回主線版跑 S1 紅、PASS(風險低)留痕,之後換回。
