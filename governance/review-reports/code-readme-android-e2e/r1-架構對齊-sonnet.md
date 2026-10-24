severity: minor

整體判斷:新場景和 README 新章節在結構上都跟鄰居一致,沒有第二種做法。有兩處格式不齊,都是 minor。

## 1. 分層與依賴方向:對齊

- **場景寫法:** `android_scene` 只用既有的 `text`、`rect`、`path`、`arrow`、`badge`,沒有另一套繪圖元件。它回傳 `(title,h,body,desc)`,跟 `swiss_cheese_scene` 一樣(assets/readme-diagrams/generate.py:411-451)。
- **登記:** 它登記進 `SCENES`,放在 swiss-cheese 之後,一樣是 `名稱:(kicker, fn)` 的格式(generate.py:535-546)。`main()` 迴圈自動產出 `<name>-zh/en.svg`,沒有另開產出路徑,也沒手改 SVG。
- **README 章節:** 新章節是 H2,位置在「測試要有用」(README.md:264)與 drift(README.md:361)之間,結構是開場段落、置中圖、`<details>` 收細節。這跟 swiss-cheese 與 risk-review 章(README.md:181-262)一致。中英兩版逐段對應,圖用 `<p align="center"><a><img width="760">` 加連到完整 SVG,跟 README.md:257-259 同一格式。
- **家節點:** 只在既有的歷史清單末尾加一行,位置和寫法跟前面各條同形。

## 2. 命名與錯誤處理:大致對齊,有一處不齊

- **場景名與檔名:** `android-e2e` 是小寫連字號,產出 `android-e2e-zh.svg` 與 `android-e2e-en.svg`,放在 `assets/`,跟 `swiss-cheese`、`risk-review` 同形。
- **kicker:** `ANDROID / EVIDENCE BY LAYER` 沿用 `QUALITY / FIVE LAYERS` 的「領域 / 描述」格式,是對齊的。
- **data-kind:** `android-inputs`、`android-layer`、`memory-shortcut` 都是單一連字號詞,跟 `defence-layer`、`escape-ledger` 同形。唯獨 `android-evidence record` 中間有空白,詳見 A1。
- **替代文字:** 中英兩份 alt 都是一句話講完流程,跟鄰居長度與風格相近(README.md:68、191、258)。
- **錯誤處理:** 新場景沒有加進 `validate()` 的斷言。`swiss_cheese` 有專屬的 `data-kind` 數量斷言(generate.py:570-572),drift 沒有,所以這點不構成不一致。

## 3. 第二種做法:沒有引入,但有一份文件沒同步

- **沒有:** 沒有手改 SVG、沒有另一套繪圖元件,README 嵌圖格式與圖檔目錄都跟鄰居相同。
- **有一處沒同步:** 產生器的 README 沒跟著更新,詳見 A2。

## A1 data-kind 屬性值裡有空白
severity: minor
blocking: 否
引句:「b+='<g data-kind="android-evidence record">'+rect(38,642,684,82」
對照:鄰居的 `data-kind` 值都是單一連字號詞,例如 `escape-ledger`(generate.py:440)、`defence-layer`(generate.py:428)。`android-evidence record` 在 `data-kind` 這種單值識別欄位裡是兩個詞,讀取端若把它當單一 token 會比對不到。生成的 SVG 圖面沒有差別,但命名格式跟鄰居不同。

## A2 產生器 README 的場景數量與清單沒更新
severity: minor
blocking: 否
引句:「SCENES={"map":("00 / THE SYSTEM",map_scene),」(diff 內 SCENES 區塊,新增 `"android-e2e":("ANDROID / EVIDENCE BY LAYER",android_scene)`)
對照:
- assets/readme-diagrams/README.md:3 寫「Eleven bilingual scenes」,新增後實際是 12 個。
- 同檔第 14 行寫「reproduces all 22 assets exactly」,新增後是 24 個。
- 同檔「Scene roles」清單(第 38-48 行附近)逐一列出 Map、First change、Knowledge、Dispatch、Review、Write-back、Evals,沒有 Android 條目。
- 同檔結尾另有一段單獨說明 drift 概覽,android-e2e 沒有。

這份 diff 沒動這個檔,而這個檔就是要求「場景數量與清單隨之更新」的地方。家節點(`Systems/README圖產生器.md`)有補歷史行,但產生器 README 的靜態數字已經過期。

不對齊共 2 條,其中 major 0 條
