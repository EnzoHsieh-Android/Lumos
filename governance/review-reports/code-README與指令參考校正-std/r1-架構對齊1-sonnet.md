severity: minor

整份 diff 沒有另起第二種做法，也沒有違反已定的規矩，以下 6 條都是輕微不一致。

核對過的對照：
- README 的章節順序。中英兩版標題、段落一一對應，英文版新增的「測試要有用」整節跟中文版 `README.md:71-93` 段落對應。
- 指令參考中英兩版的新增條目和「專案開關」表，逐列相同。
- `assets/readme-diagrams/generate.py` 只改既有 scene 的文字，沒有新增 scene 函式；SVG 也是跟著產生器一起改，`--check` 通過（22 張雙語 SVG）。
- 首屏四站地圖和三段式圖沒動；細節圖留在原位。
- 指令參考的「頂層命令數」仍用「八十多個 / more than eighty」這種約略說法，延續 `對外說明親和化改寫.md:1003` 定下的「不再寫死」。

沒核對的範圍：
- 各條說法是否符合程式實況（不屬這席）。
- SVG 的實際排版。
- 圖譜其他節點。
- `docs/心智模型.md` 和 `docs/mental-model.md` 沒有跟這次改動衝突，也沒有跟著補（grep 這次相關的說法皆無命中）。

圖譜鏡頭（固定席 `Systems/README圖產生器.md`）：
- **不影響。** 這次改動沒破壞該節點宣稱的行為或合約。
- **原因：** 它只管 `generate.py` 產圖，且要求不手改 SVG。這次改動走產生器，`--check` 全過。

## A1 家筆記新紀錄的目視驗證方式，跟同一篇筆記記載的做法不同
severity: minor
blocking: 否

引句:「用 qlmanage 轉圖目視確認字沒超出框」

對照 file: `docs/lumos-toolchain-knowledge/Systems/README圖產生器.md:19`：PITFALL 記載用 qlmanage 轉圖會截到動畫第一格，目視檢查要改用無頭 Chrome（加 `--virtual-time-budget`）。同一篇的 `:29` 也寫「目視用無頭 Chrome 截圖(見上面的坑),中英兩版都要看」。

新紀錄用的正是該 PITFALL 點名要避開的做法，沒有說明這兩張圖為什麼不受影響。這兩張圖若有動畫，目視結果就不可信。建議改用無頭 Chrome，或在紀錄裡寫明這兩張圖為何可用 qlmanage。

## A2 家筆記沒有在被改寫的舊紀錄上加指向新紀錄的註記
severity: minor
blocking: 否

引句:「evals-overview 改成「主要在 Lumos 自己的 repo 排程執行」、通知那格改「出問題時通知人」」

對照 file: `docs/lumos-toolchain-knowledge/Systems/README圖產生器.md:40`：10-01 的 drift-guard 紀錄被後來改寫時，在原紀錄加了註記「(這列 2026-10-09 起改成…見下方 2026-10-09 那條。)」。

`:39` 的 10-01 evals-overview 紀錄仍寫「退步或沒過通知人」和「推播漏網只留紀錄不通知」，這次已被 `:43` 的新紀錄改掉，但沒有加同樣的指向註記。只讀 `:39` 的人會當成現況。

## A3 更新清點改用另一種篩選口徑，標題範圍和內容對不上
severity: minor
blocking: 否

引句:「這份用「能不能從 main 追溯」篩，不用提交時間篩」

對照 file: `docs/updates/2026-10-07-readme-audit.md:4`：既有清點的口徑是「以 **committer 時間** 篩選 10/1 00:00 至盤點時間、且可從此 main 追溯的提交」。

新檔文件名和標題是「10/7–10/10」，完整清單卻從 10/03 起算。新檔在第 4 行解釋了原因（PR #48 的提交到 10/9 才合併），所以不算誤導。但這是同一個系列清點裡第二種篩選口徑，讀者要看到第 4 行才知道標題範圍不等於內容範圍。建議把標題或文件名標成「依合併進 main 的時點」，或在系列中統一口徑。

## A4 評測一節的情境探針條目寫成多句操作細節，且超出自己清點寫的處置
severity: minor
blocking: 否

引句:「Every run starts from a fresh copy of the same frozen snapshot, so nothing one run changes carries into the next.」

對照 file: `README.en.md:152`、`README.en.md:153`、`README.en.md:155` 這三條同層條目各一兩句。中文版同。

- 新增的情境探針條目有 5 句，包含事故停批、壞場次不計分、有效場次不到一半不下結論、用量帳。
- 新清點 `docs/updates/2026-10-10-readme-audit.md:15` 的處置寫的是「評測一節補一句保護說明」，實際不止一句。
- 這類執行細節比較適合留給心智模型文件，README 只保留結論與導向。

## A5 指令參考首次出現純說明的項目符號清單
severity: minor
blocking: 否

引句:「**These only list, they don't block; deal with them when you see them:**」

對照 file: `docs/command-reference.md:58`、`docs/command-reference.md:69`（含 `:91`）：既有條目一律是「一行簡介 + 帶註解的 code block」，說明用粗體段落。例如 `:56` 的「**Every one of these verifies its own write.**」。

新增的 6 個項目符號是指令參考裡第一批 `- ` 清單，內容多數沒有可敲的指令，而是自動行為的說明（例如「健康檢查列撤除候選時…」）。頁首說這份頁面是「look something up」的指令表，這些說明的位置和格式都偏離它。

## A6 專案開關另起一張表，跟既有散在各處的敘述式寫法並存
severity: minor
blocking: 否

引句:「| `note_audit.gate` | note content audit (`note-audit check`; blocks only when the pre-push hook calls that command, which this toolkit's own hook does not) | block / warn / off | block |」

對照 file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:9`、`skills/lumos-project-notes/commands/07-安裝維運.md:19`：既有的 `.lumos/config.json` 開關（`note_shape.test_refs`、`note_shape.slots`）都以敘述句寫在對應情境的指令說明裡。

新增的表是指令參考裡第一張表，也是第一個彙整的開關清單。它的格式本身沒有問題，但現在開關的預設值有三處說法：情境說明、指令參考表、README 的段落。這張表的 `note_shape.slots` 列又直接引用 07 的說法，之後要同步三處。建議在 07 或 06 補一句指向這張表，或說明這張表是唯一彙整來源。

最高等級:minor
