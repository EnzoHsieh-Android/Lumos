# code-簡報審查抓到的機制缺口-std r2 收貨

兩位全新席,審修補後整包 r2-pack.patch(543 行)加修補差異 r2-repair-review.patch(238 行);修補來源 r2-repair-binding.json(修前 3beebb94 → 修後 0f2989d0)。

## 機械收貨

- 架構對齊席報告已是正規化格式。正確性席報告最後一行原寫「max severity: minor」,格式檢查擋下;退回該席只改最後一行重交(內容一字未改),重交後正規化通過。兩份 quote-check 對 r2-snapshot.patch 全數錨定;refcheck 正確性 3 處、架構對齊 12 處全對。
- 兩席沒動 repo;正確性席的臨時目錄收齊後用字面路徑刪除(lsof 確認沒有程序在用)。
- 上一輪修正關卡(fix-check r1):修正前 3beebb94 → 修正後 cafa1a3e 全部通過(219.8 秒;c3、c4、a1、a2、a3 記成 spec/process 不用修正紀錄)。之後 0f2989d0 只把測試說明裡會觸發 Python 無效跳脫警告的字樣改成白話、計劃加一行紀錄。

## 判讀(id:正確性席 d、架構對齊席 e)

| id | 席位等級 | 觀察重現 | 歸因 | 去向 |
|---|---|---|---|---|
| d1 | minor | HIT:前綴放寬成任意套件、括號前允許任意字元,兩種改壞逐例表照綠 | 原有漏查(規則兩版沒變) | 折:補 C240(com.acme.LifecycleService 照報)、C241(Listener 介面委派照報) |
| d2 | minor | HIT:README 80 場那句寫「四組都接近滿分」,原始紀錄 H04 有一格 3/5;也沒寫只測 Haiku | 原有漏查(README 兩版沒變) | 折:中英兩版改「只測 Haiku」「大多接近滿分」,計劃範圍 2 與依據同步 |
| d3 | minor | HIT:壞例樣本 ProcessLifecycleOwner 那句沒限定非 Service 類別 | 未判定(修前修後都在) | 折:併 e5 改寫 |
| e1 | minor | HIT:預期值表三列條款欄寫成「S1 代碼審補」,一格來源只寫「同上」 | 修復回歸(r1 折入時新寫的列) | 折:條款欄只寫 S1,「代碼審補」移到來源格;「同上」改成完整來源 |
| e2 | minor | HIT:審計修正紀錄放在回退與天花板前面 | 修復回歸(r1 折入時新加的節) | 折:搬到最後 |
| e3 | minor | HIT:輪次寫成「-std r1」,鄰居寫「std r1」 | 修復回歸(r1 折入時新寫) | 折:計劃與測試註解改成 std r1、std r2 |
| e4 | minor | HIT:兩份新計劃的 c1、b1 等編號在席報告裡查不到 | 原有漏查(設計審時就這樣寫) | 折:寫明那是收貨紀錄的流水號與對照位置 |
| e5 | minor | HIT:壞例樣本註解帶筆記連結,沒用鄰居的 `// case:` 寫法,描述的內部 Service 情形樣本裡沒有 | 修復回歸(r1 折入 a5 時改的那句) | 折:四段都改成 `// case:` 寫法,不帶連結,內容照樣本實際寫法 |

編排者機械重現不到的:無(refuted none)。修復回歸集合:e1、e2、e3、e5(都是 r1 折入時新寫的格式與命名,不涉及規則行為)。

## 先查世界

PRIOR-ART: 正規式變異沿用 r1 的 Stryker Weapon regeX 做法;本輪補「前綴放寬成任意套件」與「括號前允許任意字元」兩種,鄰居 architecture.yml 的 Application 排除就是 `(\w+\.)*` 寬鬆寫法,這次刻意不放寬,所以要有一例守住。

## 翻紅釘

```
M0 不改(基準): 紅的列 [] | 449 passed, 0 failed
M10 前綴放寬成任意套件: 紅的列 ['C240'] | 447 passed, 2 failed
M11 括號前允許任意字元: 紅的列 ['C241'] | 447 passed, 2 failed
restored True
```

修後 `-k kotlin_rulepack` 507 passed, 0 failed;三份計劃 lint 0 問題。
