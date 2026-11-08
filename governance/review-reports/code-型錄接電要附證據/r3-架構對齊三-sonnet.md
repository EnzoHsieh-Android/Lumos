severity: minor

我只看了 patch 與對照檔,沒有改任何檔,也沒有重跑 lint。判斷依據是 patch 內容加 `scripts/test_lumos.py` 與 `skills/kotlin-idioms/checks-catalog.md` 的既有寫法。

## 1. 分層與依賴方向

沒有不對齊。這輪只動五類東西:樣本檔 `.kt.txt`、型錄判定表與計數、`t_kt_catalog_batch4_evidence` 的改壞例、計劃筆記、`governance/anchor-baseline.json`。沒有新增函式、模組或跨層呼叫。測試只透過既有的 `mutate(...)` 與 `setcol(...)` 驅動 `catalog_problems`,依賴方向沒變。anchor 重簽的 note 沿用上一筆的「…;使用者授權原話:「你自己簽核」」格式。

引句:「+    mutate("UI-24 通電批次沒有告警帶寫法只有批四", lambda ls: setcol(ls, 9, "批四(" + lint + ")", main24), "UI-24", "只准寫在")」
對照:`scripts/test_lumos.py:129186`,同函式的 r1 改壞例走同一條 `mutate` 路徑。

## 2. 命名與寫法

主體與鄰居一致,有兩處小出入。

- 新增的兩支改壞例,命名、參數順序和註解前綴都照 `scripts/test_lumos.py:129186` 與 `:129187` 的寫法。
- ARCH-72 樣本把 manifest 片段放在 `/* AndroidManifest.xml 的 application 內(…):` 區塊註解裡。這跟 `configs/ast-grep/kotlin-android/samples/lint-wiring/ARCH-71.kt.txt` 一致,與 ARCH-73 的 `<!-- 以下放進 AndroidManifest.xml … -->` 也是同一系。

**finding 1**:計劃筆記〈審計修正紀錄〉新增的代碼審 r2 這一行,少了鄰居都有的兩樣東西。
- r1 那行寫了席名(`4 席:審查、架構對齊、樣本甲、樣本乙`)和 `卷證 `governance/review-reports/code-型錄接電要附證據/``。
- 設計審 r1 到 r3 的行也有卷證指向或「卷證同上」。
- r2 這行寫成 `3 席`,沒有席名,也沒有卷證指向。

引句:「代碼審 r2(2026-11-08,3 席):13 條/blocking 3/位置檢查另兩個條件沒有改壞例」
對照:`docs/lumos-toolchain-knowledge/Projects/型錄接電要附證據_計劃.md:123`(代碼審 r1)與 `:121`(設計審 r3,「卷證同上」)。
severity: minor
blocking: 否

**finding 2**:ARCH-25 的 CI 範本判定列,「擋不到」這一列的備註少了「原本 <等級>」。
- 同類的「擋不到」列,鄰居寫的是 `原本 Error;…沒報;依賴:…`,例如 ARCH-40、ARCH-41。
- ARCH-25 改成 `沒報 | 沒報:這條只在 DialogFragment 裡檢查…`,沒有寫原本的 Warning。
- 同一輪的 UI-54 CI 列有補「(原本 Error)」,所以 ARCH-25 在 patch 內部也不一致。

引句:「+| ARCH-25 | CI 範本:Android Lint | UseGetLayoutInflater | 擋不到 | 沒報 | 沒報:這條只在 DialogFragment 裡檢查(反編譯確認),壞寫法欄寫的是一般 Fragment,樣本照寫;依賴 fragment 1.8.9」
對照:同 patch 內被刪掉的舊列 `-| ARCH-40 | CI 範本:Android Lint | MissingKeepAnnotation | 擋不到 | 沒報 | 原本 Warning;樣本沒有 enum 參數,沒報;依賴:navigation-compose 2.9.5`。
severity: minor
blocking: 否

## 3. 第二種做法

沒有。這輪沒有為了同一件事另寫一套機制:
- 改壞例用既有的 `mutate`。
- 判定欄位仍是「擋得到、擋不到、沒報」三種固定值。
- 樣本重跑沿用既有的「真跑」出處標記。
- 計數行 `接電證據:248 筆(擋得到 172、擋不到 76` 的 166+6=172、82-6=76 加總仍是 248。

引句:「+- 接電證據:248 筆(擋得到 172、擋不到 76;2026-11-08 真跑)」
對照:`skills/kotlin-idioms/checks-catalog.md`,同一格式的上一版是「擋得到 166、擋不到 82」。

不對齊共 2 條,其中 major 0 條。
