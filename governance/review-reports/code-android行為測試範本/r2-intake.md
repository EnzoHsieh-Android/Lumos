# r2 收貨紀錄(code-android行為測試範本)

## 收貨

- 第 2 輪,standard,修訂輪。修補差異 d30d7ee90..cea727087(2028 行)拆兩包:範本審看 r2-repair-範本.patch(1410 行)、其他審與架構對齊看 r2-repair-其他.patch(618 行);整份凍結 r2-snapshot.patch。三席全 sonnet;外家預設不派。
- 引句:範本審、架構對齊各有 1 句引的是修補差異以外、但同一版本的既有行(對整份 r2-snapshot.patch 全錨),兩席留痕以整份為快照;其他審 1 句(刪除行)錨不到,不採信那句,所屬條目(二其6:Systems/test-quality-cli 沒記這輪改動)由編排者以 `git diff d30d7ee90..cea727087 -- docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md` 為空重現,HIT。
- 席位沒改 repo;臨時目錄已清。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 二範1 | 範本審 F1 | FakeProfileRepository.save 加 delay(100),正確 VM 兩支新寫法誤紅 | HIT(席位實跑;r1 舊寫法同 fake 綠) |
| 二範2 | 範本審 F2 | API-31 改成 `inflight ?: …` 永久快取 | HIT:照綠 |
| 二架2 | 架構 F2 | check.py 新 `_outside_fences` 與 lumos `_fence_regions` 口徑分岔 | HIT(讀碼:縮排 4 格與收尾長度規則不同) |
| 二其6 | 其他審 F6 | Systems/test-quality-cli 本輪無改動 | HIT |

refuted: none

## 先查世界

- PRIOR-ART: 二範1 是上一輪修補(Turbine 讀法)自己帶進的退步:範本〈怎麼用〉寫了「先推到靜止」,兩支漏做。照官方 Flow 測試頁「advanceUntilIdle」用法(https://developer.android.com/kotlin/flow/test )補上,並在守衛測試裡機械檢查「每個 `cancelAndConsumeRemainingEvents()` 之前同一個 test 區塊有推進呼叫」。
- PRIOR-ART: 二架2 剝圍欄——lumos `_fence_regions` 是全檔唯一判定(CommonMark 圍欄規則:縮排最多 3 格、收尾圍欄字元相同且長度不短於開頭、收尾行不帶 info string,https://spec.commonmark.org/0.31.2/#fenced-code-blocks )。check.py 零依賴不能 import lumos,所以照同一套規則實作並寫明刻意另一份,加一支測試對同一組輸入比對兩份判定一致(機械防漂移)。

## 逐條去向

全部折入(16 條:範本審 5、其他審 7、架構對齊 4)。
