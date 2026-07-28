---
type: verification
status: pass
date: 2026-07-28
feature: testmap
valid_under:
  - "LandmarkMember@驗收當日 HEAD(兩層金標 5+5)"
  - "testmap v1 常數(conf 0.9/0.5/0.8 封頂、stem≥4、200KB、cochange support≥3)"
revalidate_when:
  - "Landmark 測試佈局大改(新測試專案/命名慣例換)→ 金標重抽"
  - "testmap 判定/剝離規則異動 → t_testmap_* 全綠+金標重跑"
plan_refs:
  - "[[Projects/檔案測試依賴地圖_計劃]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:t_testmap_build/t_testmap_affected/t_testmap_rc 68 檢查全綠;全套 1577 passed 0 failed;anchor 重批訖
  VERIFY:[[Projects/檔案測試依賴地圖_計劃]] 全案落地+[S4] Landmark 轉正閘 PASS
  KEY:Landmark 真庫——edges=371(content 347/cochange 12/雙源 9/naming+content 3)、src=549、tests=68;金標兩層各 5 對分層 recall:單元層 5/5、整合層 5/5(較低層 1.0 ≥0.7 → 轉正);噪音度=每 src 建議條數 中位 1、p95 11(advisory 可受)
  KEY:cochange support 門檻裁值——擋 32 邊(全 support=2);金標無一死於門檻 → 維持 3
  KEY:抽樣誠實帳——整合層第 5 席首抽誤猜 TicketService(不存在),改讀測試自身註解定真主題 NotificationRepository 後判 ✓;程序=先定主題再查邊,非反向湊
---
# Verification: testmap 落地＋Landmark 轉正（2026-07-28）

驗證對象：[[Projects/檔案測試依賴地圖_計劃]]——`lumos testmap build/affected` 實作＋[S4] 成效裁決。

## 機械正確性（[S3] TDD）

- `t_testmap_build`／`t_testmap_affected`／`t_testmap_rc`（rc 矩陣獨立函式防吞斷言）共 **68 檢查全綠**；全套 **1577 passed 0 failed**。
- 覆蓋 [S3] 全 25 項：naming 各型（含點分 basename 去尾點、`_spec` 直剝、`Foo_TESTS` 底線不敏感、同名唯一 `__tests__/Button`、dunder 擋）、content（I+stem 雙指、短 stem、200KB）、cochange（support 3 建/2 擋、封頂 0.8）、確定性、affected 全語意（自證/去重/刪檔兩路/uncovered）、陳舊三訊號（非祖先 sha／build 後 commit／未提交＋未追蹤）、map 三級守衛、fail-open×json、CJK、rc 矩陣。

## [S4] Landmark 轉正閘：**PASS（轉正）**

| 層 | 金標（測試 ↔ 主題 src） | recall |
|---|---|---|
| 單元（LandmarkMember.Tests） | PointAccrual／VoucherRedeemPolicy／SqlDateBoundary（鏡像命名）＋HmacSignature↔HmacService、SmsTokenInvariant↔SmsTokenService（主題類，import 佐證） | **5/5** |
| 整合（IntegrationTests，情境命名） | RedeemIdempotency↔VoucherService、VoidConcurrencyDoubleRefund↔PointService、PointsNegativeBatchPosApi↔PointService、VoucherBatchLedger↔VoucherService、TicketHistoryFolding↔NotificationRepository | **5/5** |

- 裁決＝較低層 recall 1.0 ≥ 0.7 → **轉正**。
- 整合層全靠 content/cochange 訊號接住（naming 盲區實證如 spec 預期；`I`+stem 介面慣例是關鍵補刀）。
- 噪音度：每 src 建議條數中位 1、p95 11（advisory 可受，不設硬閘照 spec）。
- support 門檻：擋 32 邊全為 support=2，金標零傷 → 維持 3。
- 抽樣誠實帳：整合層第 5 席首抽誤猜不存在的 `TicketService`——修正程序＝讀測試自身註解定真主題再查邊；教訓記入：金標主題判定須以測試內文為準，不得憑檔名腦補。

## toolchain 自庫（天花板如實）

`test_lumos.py` 單檔巨測（>200KB 跳 content）＋`scripts/lumos` 無副檔名不入候選——自庫僅驗機械正確性，不當成效證據（spec 明文）。
