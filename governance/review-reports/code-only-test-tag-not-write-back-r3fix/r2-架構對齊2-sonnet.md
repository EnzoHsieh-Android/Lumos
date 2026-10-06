severity: minor

# 架構對齊審查(r2 修正差異)

確認:上一輪點名的第二份平台前綴正則已刪。delta 裡 `_NODEHOME_TAG_PREFIX_RE` 與 `bare()` 都被拿掉,test-gone 改成跟上一版 `[test:]` 整串比對;scripts/lumos 現存的前綴正則只剩 `_NODEHOME_TAG_NAME_RE` 內嵌的一段(形狀檢查,不是去前綴)。

## 1. 分層與依賴方向
clean。改動都在 `_slot_strip_keys`、`_nodehome_tag_only_change` 內部,沒有新的跨層呼叫;`_nodehome_tag_only_change` 仍透過傳入的 judge 判定,沒有直呼別層。
引句:「old_tests = {nm for k, nm in b["tag_names"] if k == "test"}」
既有碼佐證:file: `scripts/lumos:29690`(`_NS_TR_PREFIX_RE` 仍是筆記測試綁定要存在那邊自己的前綴判法,這次沒有再去重複它)

## 2. 命名與錯誤處理
有一條不一致。`_slot_strip_keys` 用 `str.isalnum()` 判「後一個字元是不是字」。專案判這件事的既有寫法有兩種:正則 `[^\W_]`(file: `scripts/lumos:6786`、`scripts/lumos:6691`、`scripts/lumos:7117`,明講「底線不算實字」)和 `(?<!\w)`/`(?!\w)` 邊界(file: `scripts/lumos:9376`,註解寫明為了 CJK id 也要有效)。`isalnum` 逐字判在專案只有 `scripts/lumos:33754` 一處,而且那處是判副檔名字元,不是判「字 vs 標點」。兩者行為幾乎一致(isalnum 對 CJK 也回真),差別只在底線:`\w` 把 `_` 當字,`isalnum` 不當,所以「a [k:v]_x」會吃掉前面空白。結構對、語意差一個字元,屬 minor。
severity: minor
blocking: 否 — 命名/判法不一致但結構對,沒有引入第二套邏輯,也沒有跨層。
引句:「if b >= len(line) or not line[b].isalnum():」

## 3. 第二種做法
大致 clean。前綴去除的第二份正則已刪(見上方確認),test-gone 比對退回「整串一致」,跟 file: `scripts/lumos:29746` 附近的 `_NS_TR_PREFIX_RE` 並存的只是形狀檢查,不是第二套去前綴機制。⚠ `_NODEHOME_TAG_NAME_RE` 內嵌的 `(?:[A-Za-z0-9_-]+:)?` 與 `_NS_TR_PREFIX_RE` 是兩份各自寫的前綴形狀,但這是上一輪就存在、這次沒動,且用途不同(一個放行、一個拆名),不列為不對齊。
引句:「# test-gone 要跟上一版的 [test:] 整串一致——不去平台前綴」

總結:不對齊共 1 條,其中 major 0 條
