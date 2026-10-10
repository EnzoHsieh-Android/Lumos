# r3 收貨、重現與處置(上限輪)

## 材料與編制

- 修補鏡頭:修前 2494971e → 修後 cbb854a0(`r3-repair-binding.json`,祖先關係 rc0,區間一個修補提交)。修補差異 334 行;完整快照 `r3-snapshot.patch` 範圍 8e648f3d..daff730e。
- 兩席全新 Claude Sonnet,派工詞禁止讀 r1-*、r2-* 與輕量迴圈卷證。
- 本迴圈第一筆帳沒帶 `--tier`,帳上定錨分級顯示「沒指定」;編排者照 `loop next --tier standard` 的 3 輪上限自律,本輪即上限輪。

## 收貨

- 兩份報告從子代理逐字稿抽存,都是正規化格式、引句全數錨定。
- 正確性席交回完整報告(F1–F4)後,背景還有它自己開的監看任務,之後又送了幾則同結論的訊息(把 F4 改列為未判定、只留三條 finding);卷證存的是第一次完整交回的那份,本表照它編號。

## 重現(編排者機械重現)

finding 編號:正確性席 C1–C4(報告 F1–F4);架構對齊席 A1–A3。

| finding | 重現 | 說明 |
|---|---|---|
| C1 | 採信 | 席位改壞:替 spec-gate 的 `add_parser` 加舊說法的 `description`,`spec-gate --help` 印舊說法、新測試照綠;`_fill_help_when` 只在沒有 description 時灌入 |
| C2 | HIT(讀碼) | `scripts/hooks/pre-commit` 跑 `note-shape --staged`,rc1 就擋;指令參考把它放在「只列出、不擋」區塊沒講它會擋 |
| C3 | 採信 | 席位附 `_drift_close_summary_untouched`:觸發是狀態改成收尾值且摘要逐字沒變,「待定」只影響排序 |
| C4 | 採信 | 席位附 `cmd_spec_gate` 在句式/綁定/相依回歸/風險低兩向判定擋下時提前 return,不寫 spec-gate-run |
| A1 | HIT | 新測試讀 argparse 私有屬性 `_choices_actions`,全檔僅此一處 |
| A2 | HIT | 開關表中文寫「同上，受總開關管」、英文只寫 `(same)`;表內其他列每列自足 |
| A3 | HIT | 英文 README 寫 `, in Chinese)`,同檔其他處是 `(Chinese)` |

## 修補因果(regression)

- 有證據屬上一輪修補造成:C1(測試改寫縮小守衛面)、C3、A1、A2、A3(上一輪新寫的字)。
- 原有漏查:C4。
- 未判定:C2(修前同區塊是 `git commit`,同樣會被擋)。這輪帳不帶 `--regression-set`。

## 處置

- 本輪最高 minor,上限輪新 minor 照規矩附理由放行,不觸發新一輪:C1–C4、A1–A3。
- 使用者裁定:放行後另修措辭再推,不再開審查輪。照做的文字修正:C2、C3、C4、A2、A3(各附於提交訊息);C1、A1 是測試寫法,不在「只修措辭」範圍,照放行理由留著,最後回報列出。
