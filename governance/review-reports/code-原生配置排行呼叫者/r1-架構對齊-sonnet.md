severity: minor

我沒讀到 python-idioms 的內容;這份 diff 只動 SQL、測試和筆記,也沒有可套用的 Python 慣例,所以不影響判斷。鎖檔 `…cf3c8a.json.warming` 檢查時不存在,沒有東西要處理。

**1. 分層與依賴方向**
新碼放的層和鄰居一樣,沒有跨層。
- 查詢規則改在 `scripts/templates/android-stability-native.sql` 的 `caller_step`。對照的 `libart.so` 跳過、ERROR 偽框架判斷都在這同一支檔(file: `scripts/templates/android-stability-native.sql:63`、`:57`、`:71`)。
- 測試放在 `scripts/test_lumos.py` 的 `t_android_native_query_caller` 後面,透過 `_ms_native` 假表跑同一個範本,沒有繞過範本(file: `scripts/test_lumos.py:18605`、`:18484`)。
- 驗證紀錄放 `Verification/`,並由 `Systems/android-stability-collector.md` 和 `Systems/macrobenchmark-adapter.md` 的 `verified_by` 指到它,跟既有紀錄的掛法相同。
- 逃逸帳新增一列,手動記的 `"stage": "實作"` 在帳裡已有 8 筆,是既有做法(file: `docs/.escape-log.jsonl`)。

**2. 命名與錯誤處理**
測試命名 `t_android_native_query_caller_jni_trampoline` 符合 `t_android_native_query_<主題>` 的慣例。
- SQL 的空值處理 `coalesce(f.fname, '') != ''` 和同檔既有的 `coalesce(fname, '') != '' as sym` 寫法一致(file: `scripts/templates/android-stability-native.sql:45`)。
- PITFALL 行的鍵順序「出處、根因、修法、test」和同節點既有的一樣。
- 驗證紀錄用「怎麼跑、結果、沒驗到的」,在 `Verification/` 底下有多篇同標題(file: `docs/lumos-toolchain-knowledge/Verification/2026-09-11_代碼審資安席落地.md:32`),欄位也齊。
- 只有下面的 finding 2 這條不一致。

**3. 第二種做法**
- 沒有引入另一套假呼叫鏈工具,新測試仍走 `_ms_native`。
- 判斷「是不是 ART 框架」變成兩種準則並存:既有的按 .so 名,新增的按函式名。不過同一支查詢的配置器判斷已經是 .so 加函式名單並用(file: `scripts/templates/android-stability-native.sql:40-44`),所以結構上有先例。詳見 finding 1。

1. 「是不是 ART 框架」現在有兩種判法並存
severity: minor
blocking: 否
引句:「  where not s.unknown and f.so != 'libart.so' and coalesce(f.fname, '') != 'art_jni_trampoline' group by s.leaf」
file: `scripts/templates/android-stability-native.sql:63`(同檔 `:42-44` 的配置器判斷也是 .so 加函式名單並用)
代價:ART 的框架一半按 .so、一半按單一函式名。之後再碰到 boot.oat 裡的別的 ART 跳板,又得再補一個函式名,不像「按 boot.oat 路徑」那樣一次涵蓋。⚠ 判不準是否算第二種做法:同檔配置器有先例,所以我只記 minor。

2. 新測試自己宣告區域路徑常數、手拼整條呼叫鏈,沒用檔頭的 `_MS_*` 常數和 `_ms_jni`
severity: minor
blocking: 否
引句:「    boot = "/data/misc/apexdata/com.android.art/dalvik-cache/arm64/boot.oat"」
file: `scripts/test_lumos.py:18477-18481`(檔頭 `_MS_*` 常數)和 `:18517`(`_ms_jni` 組跳板鏈)
代價:`boot.oat` 與 `.vdex` 路徑只存在這一支測試裡,下一支測試要重複造一份。鄰居的做法是把路徑放模組層常數、再用輔助函式組鏈。

3. 驗證紀錄的標題用詞和最近三篇的同節不同
severity: minor
blocking: 否
引句:「## 沒驗到的」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-24_效能判定規則實機評測.md:42`(標題是「## 沒驗的」)
代價:同一個 Android 系列的紀錄用詞不統一,搜尋標題時會漏。不過 `沒驗到的` 在 `2026-09-11` 等多篇也有(同上 file 清單),兩種寫法都是既有的,所以只算很輕的 minor。

不對齊共 3 條,其中會擋推送的 0 條
