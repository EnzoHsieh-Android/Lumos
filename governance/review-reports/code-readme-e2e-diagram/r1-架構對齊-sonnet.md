severity: minor

## 1. 分層與依賴方向
新碼全落在 `assets/readme-diagrams/generate.py` 的 `android_acceptance_scene` 和 `validate_android_acceptance` 裡,和鄰居放的層一樣,沒有跨層直呼。

- 場景函式回傳 `title, 高, b, desc`,`SCENES` 登記不變。
- 檢查函式仍由 `validate()` 在同一處掛上,跟 `validate_android` 並排:``generate.py: `643-644` ``。
- 新增的 `badge(...)`、`rect`、`text`、`path`、`arrow` 都是現成輔助函式。
- 分支用珊瑚色虛線加 `arrow(...,"coral")`,和既有 `memory-shortcut` 同一種畫法:``generate.py: `520` ``。
- 工具標籤的 badge 位置(528,寬 180)沿用 `android-layer` 的 `badge(562,y+20,tag,c,146)` 做法:``generate.py: `516` ``。
- 文件三處同步:`assets/readme-diagrams/README.md` 的場景清單、README 兩版、`Systems/README圖產生器.md` 的 WHY 行。這和既有圖的更新方式一致。

沒有不對齊。

## 2. 命名與錯誤處理
- 屬性名 `data-kind="android-e2e-outcome"` 加 `data-outcome="pass"/"dig"`,和同圖已有的 `android-e2e-step` 加 `data-step` 同型,也像 `android-layer` 加 `data-layer`。
- 檢查用「屬性值依序比對清單」的寫法,和既有 `data-step`、`data-layer` 的 assert 一樣:``generate.py: `611` ``、``generate.py: `603` ``。
- 沒有 assert 訊息,但鄰居的清單式 assert 也沒有。只有迴圈內的計數 assert 帶 `, kind`,新增的迴圈沿用了這一點。

## A1 圖上的指令名跟正文、desc 不一致
severity: minor
blocking: 否

新的 `badge(528,614,"lumos judge","green",180)` 把判定步驟標成 `lumos judge`。同一圖的 desc 和 README 正文寫的都是完整指令 `lumos android-e2e judge`。

鄰居的標籤用的是真實指令名(`lumos macrobench`)。新的 alt text 也同步改成 `lumos judge`:``README.md: `80` ``。這是縮寫還是指令確實存在,我沒有核對,所以標 ⚠ 交編排者:如果 CLI 沒有 `lumos judge` 這個頂層指令,圖上的標籤和 alt text 就跟專案慣用的真實指令名不一致。

引句:「    b+=badge(528,614,"lumos judge","green",180)+'</g>'」

## 3. 第二種做法
沒有引入新做法。

- 場景專屬檢查仍是獨立函式加 `validate()` 掛接,沒另起一種。
- 元件全部重用既有輔助函式。
- 圖上分支用既有的珊瑚虛線語彙。
- README 的結果說明從表格改成條列,符合「少用表格、用條列講結果」的章節慣例。

不對齊共 1 條,其中 major 0 條
