severity: minor

**問 1 分層與依賴方向:結構大致對齊,圖放的位置與鄰居不同。**
- 新場景 `android_scene(en)` 回傳 `(title,h,body,desc)`,與既有場景函式同形(`assets/readme-diagrams/generate.py:453` drift_scene、`:411` swiss_cheese_scene)。
- 登記方式:`SCENES` 新增一項 `"android-e2e":("ANDROID / EVIDENCE BY LAYER",android_scene)`,格式與同表 `"swiss-cheese":("QUALITY / FIVE LAYERS",…)` 一致。
- 只用 stdlib,沒有另一套元件,全程用既有的 `rect`、`text`、`path`、`arrow`、`badge`。
- 我跑了 `python3 assets/readme-diagrams/generate.py --check`,24 張 SVG 驗過且逐位元組重現,所以不是手改 SVG。
- 新章節放在「測試要有用」之後、「怎麼防止筆記過期」之前,是平級的二級標題,中英位置一致(`README.md:302`、`README.en.md:302`)。
- 章內結構是導言,再接一張圖,再接 `<details>`。圖放在 `<details>` 外面,這點與多數鄰居不同(見 A1)。
- 說明檔 `assets/readme-diagrams/README.md` 的場景數(Twelve)、圖檔數(24)、Scene roles 都同步補了。

**問 2 命名:大致對齊,有兩處小差異。**
- 場景名 `android-e2e` 與檔名 `android-e2e-zh.svg`、`android-e2e-en.svg` 符合 `{name}-{lang}.svg` 的慣例。kicker 全大寫、用 `/` 分隔,與 `QUALITY / FIVE LAYERS`、`EVALS / FEEDBACK` 同形。
- data-kind 用小寫連字號單詞(`android-layer`、`android-inputs`、`android-record`、`memory-shortcut`),與 `defence-layer`、`escape-ledger` 同形。
- 替代文字照鄰居寫成一整句流程描述(`README.md:310`、`README.en.md:310`),中文用全形標點,與 `README.md:68` 一致。
- 說明檔的 Scene roles 條目用「Android: …」,形式與同列表其他項一致。
- 差異見 A2:英文 `<summary>` 的措辭,以及英文連結旁的語言標記。

**問 3 第二種做法:沒有引入第二種做法,但有一處文件與機檢沒同步。**
- 沒有手改 SVG、沒有另一套元件、沒有另一種嵌圖格式。圖同樣用 `<p align="center"><a><img width="760">` 嵌入並連到原圖。
- 新章節的 `[…](docs/lumos-toolchain-knowledge/Projects/…_計劃.md)` 連到圖譜計劃筆記,檔案存在。既有 README 只連 `skills/…` 與 `docs/updates/…`,這是新的連結目標類型,但只是普通連結,不算第二種做法。
- 家節點 `README圖產生器.md` 的新紀錄同步了場景、數量與用詞,沒有文件與實際脫節。
- `validate()` 對 swiss-cheese 場景有 `data-kind` 數量斷言(`generate.py:570-572`),新場景加了四種 data-kind 群組卻沒有對應斷言(見 A3)。

## A1 流程圖放在 details 外,與多數鄰居不同
severity: minor
blocking: 否
引句:「<a href="assets/android-e2e-en.svg">」
對照:`README.md:175`(graph-demo 圖在 `<details>` 內)、`:192`(risk-review)、`:223`(security-lane)、`:258`(swiss-cheese)、`:425`(evals-overview)。只有 `README.md:68`(map)與 `:389` 前後的 drift 圖放在外面或段中。

## A2 英文 summary 與語言標記措辭跟鄰居不同
severity: minor
blocking: 否
引句:「What each layer does, lab results, and limits」
對照:`README.en.md:41`、`:163`、`:188`、`:217`、`:269`、`:366`、`:414` 的 summary 多以 "See …" 開頭,中文 `README.md:315` 是「看…」。另外,新章英文連結旁寫 "(in Chinese)",既有英文章用 "(Chinese)"(`README.en.md:296`)。

## A3 新場景的結構沒有進 validate 斷言
severity: minor
blocking: 否
引句:「b+='<g data-kind="memory-shortcut">'+path(」
對照:`generate.py:570-572` swiss-cheese 場景對 `defence-layer`、`aligned-escape`、`escape-ledger` 有數量斷言。android 場景的 4 個 `android-layer`、1 個 `memory-shortcut`、`android-inputs`、`android-record` 沒有,說明檔也沒提到這些檢查。

不對齊共 3 條,其中重大 0 條
