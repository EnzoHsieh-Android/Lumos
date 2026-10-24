severity: clean

我跑了 `python3.14 assets/readme-diagrams/generate.py --check`,結果是「24 bilingual SVGs: validated, reproducible, static fallback and reveal order checked」。SVG 是產生器重產的,沒有手改。

**1. 分層與依賴方向:對齊。**
- `android_scene(en)` 的回傳形狀是 `return title,746,b,desc`,跟 `swiss_cheese_scene`(`generate.py:411`)和 `drift_scene`(`generate.py:453`)一樣。
- 它定義在 `drift_scene` 之後、`SCENES` 之前,用 `rect`、`text`、`path`、`arrow`、`badge` 這些既有元件,沒有另起一套。
- `SCENES`(`generate.py:533`)多一筆 `"android-e2e":("ANDROID / EVIDENCE BY LAYER",android_scene)`。鍵名是小寫連字號,kicker 是大寫加斜線,跟 `"swiss-cheese":("QUALITY / FIVE LAYERS",…)` 同格式。
- 只用標準庫,沒加依賴。
- README 新章是一個 `##` 標題,後面接開場段、置中的 `<p align="center"><a><img width="760">`,再接 `<details>`。這跟 `README.md:257` 的 swiss-cheese 和 `README.md:389` 的 drift-guard 同型。中英兩版逐行對應(`README.md:309` 對 `README.en.md:309`)。
- 章節位置在「測試品質」章之後、「drift」章之前,同層 `##`,沒有塞進別章的 `<details>`。

**2. 命名與錯誤處理:對齊。**
- 檔名 `android-e2e-zh.svg` 和 `android-e2e-en.svg` 是 `<scene>-<lang>.svg`,跟 `swiss-cheese-zh.svg`、`drift-guard-zh.svg` 一樣。
- `data-kind` 有 `android-inputs`、`android-layer`(帶 `data-layer`)、`memory-shortcut`、`android-record`,都是單詞連字號。`android-layer` 對應 `defence-layer`(`generate.py:428`),`android-record` 對應 `escape-ledger`。
- 替代文字描述了圖的內容,不是檔名,這點跟 `README.md:257` 一致。
- `generate.py` 的寫法緊湊,`=` 兩邊不留空白,`en and 19 or 21` 和 `19 if en else 21` 兩種條件式並存,跟 `swiss_cheese_scene` 同風格。`evals_scene` 用有空白的寫法,倉內本來就兩種並存,不算不對齊。
- 說明檔 `assets/readme-diagrams/README.md` 的數字都對上了:場景數 11 改 12、圖檔數 22 改 24。`SCENES` 實際有 12 筆,`assets/` 下有 24 個 SVG。
- 場景條目寫成 `- Android: …`,跟 `- Evals: …` 同格式。
- 家節點 `README圖產生器.md` 補了日期紀錄,寫明沒手改 SVG,並記下前一輪的 `data-kind` 改正。

**3. 第二種做法:沒有。**
- 沒有手改 SVG,也沒有新的嵌圖格式。
- 圖用產生器加 `--check` 驗證,文件與實際同步:場景數、圖檔數和場景清單都跟產生器對得上。
- 新增的 `memory-shortcut` 虛線沿用既有的 `path(...,"coral",2,"6 6",True)` 加 `arrow`。這個畫法跟 `aligned-escape`(`generate.py:418`)的虛線同源,不算另一套。

不對齊共 0 條,其中重大 0 條
