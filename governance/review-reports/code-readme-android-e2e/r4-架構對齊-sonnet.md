severity: clean

**1. 分層與依賴方向**
對齊。
- **場景函式**:`android_scene(en)` 回傳 `title, 高, body, desc` 四元組,和 `drift_scene` 結尾的 `return title, 710, b, desc` 同一形狀。它只用既有的 `text`、`rect`、`path`、`arrow`、`badge`(generate.py:19-43),沒有自己另寫元件。
- **登記方式**:在 `SCENES` 表加一列 `"android-e2e":("ANDROID / EVIDENCE BY LAYER",android_scene)`,和 `swiss-cheese` 等既有列同格式。
- **斷言位置與寫法**:在 `validate()` 裡,緊接 swiss-cheese 那段。兩段都是「用標題比對,再用 `data-kind` 計數」(generate.py:559-562 對 diff 新增行)。新段多了一個 `data-layer` 順序比對,屬於同一種做法。
- **README 章節位置**:放在測試品質章(README.md:264)與 drift 章(README.md:361)之間,是頂層 `##` 章。章首圖在 `<details>` 外,內文在 `<details>` 內並用粗體小標,這和 drift、評估章一樣。中英兩版位置一致(都是第 302 行)。
- **跨層**:沒有。

**2. 命名**
對齊。
- **場景名與檔名**:`android-e2e` 的格式和 `drift-guard`、`swiss-cheese` 一樣,輸出為 `android-e2e-en.svg` 和 `android-e2e-zh.svg`,與 `drift-guard-en.svg`、`drift-guard-zh.svg` 同樣用 `-en` 和 `-zh` 後綴。
- **data-kind**:`android-inputs`、`android-layer`、`memory-shortcut`、`android-record` 的格式與 `defence-layer`、`aligned-escape`、`escape-ledger` 同為小寫連字號;`data-layer` 屬性也沿用 swiss 的寫法。
- **summary 措辭**:「See what each layer does, lab results, and limits」和既有的「See the three checks and their configuration」、「See the four evaluations…」同為 "See …" 句型。
- **替代文字**:長句說明流程,和 drift 圖的替代文字同類。
- **語言標記**:連到中文圖譜筆記的連結結尾標 `(Chinese)`,和 README.en.md:296 既有的寫法一致。
- **說明檔條目**:`assets/readme-diagrams/README.md` 的 Scene roles 新增 Android 一條,場景數同步改為 Twelve、素材數改為 24。
- 這條 Android 條目比鄰居長,多寫了斷言內容,這是粒度差異,不算命名不一致。

**3. 第二種做法**
沒有。
- 新圖由產生器產出,Systems 家節點的紀錄也寫明「重產、沒手改 SVG」。
- 嵌圖格式是既有的 `<p align="center"><a><img width="760"></a></p>`。
- 沒有新元件、新依賴或另一套斷言寫法。
- 文件與實作同步:場景數 12 與素材數 24 在 README 裡一致,`return title,746,...` 的高度也沒有和其他地方矛盾。
- 字級用 `17 if en else 20` 這種條件式,swiss 場景同時有 `en and 19 or 21` 和條件式兩種寫法,所以新寫法不算引入第二種。

不對齊共 0 條,其中重大 0 條
