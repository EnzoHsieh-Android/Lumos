# r1 收貨、重現與處置

## 開輪依據與材料

- 同一批改動先開了輕量迴圈 `code-README與指令參考校正`(第一個提交 bd1a1bba 只有文件;一席架構對齊報 7 條 minor,6 條折入第二個提交 0221bd2e、探針細節那條當時保留)。第二個提交改到 README 圖產生器 `assets/readme-diagrams/generate.py`,`lumos pitfalls --diff 8e648f3d..HEAD` 改判 standard、`spec-gate --push-check` 沒判成 light,所以另開本迴圈從頭審整條分支。輕量迴圈的帳與卷證照留,不併進本迴圈。
- 凍結審材 `r1-snapshot.patch` 範圍 8e648f3d..0221bd2e,1022 行;架構對齊席讀不含 SVG 的 `r1-part-text.patch`(926 行)。沒有適用的棧別題(`stack_questions_applicable` 空)。
- 兩席全新 Claude Sonnet,派工詞禁止讀 `governance/review-reports/`。

## 收貨

- 兩份報告從子代理逐字稿抽最後一則存檔,都是正規化格式、引句全數錨定。

## 重現(編排者機械重現)

finding 編號:正確性席 F1–F7;架構對齊席 A1–A6。

| finding | 重現 | 說明 |
|---|---|---|
| F1 | HIT | `python3.14 scripts/lumos spec-gate "Projects/探針判準對齊程式碼為主_計劃"` → rc=1,5 條綁定測試都綠、印「沒標 keeps 的是新行為,測試現在就該紅」;`cmd_spec_gate` 在風險低且兩向判定不過時 return 1。`spec-gate --help` 與子命令總表都寫「印紅綠(不擋)」,指令參考照抄 |
| F2 | 採信 | 席位附 `refresh_labels.py` 的 `signal` 與 `retrieval_eval.py` 的 `collect_unjudged`:分母是計分觸及的(題目, 候選筆記)組數 |
| F3 | 採信 | 席位附 `_lint_new_config(repo_root)` 讀工作目錄 |
| F4 | HIT(讀碼) | `note_shape` 的 negation、tag_hints、close_summary、wording 四個 warn/off 開關,表上沒列 |
| F5 | 採信 | 席位附 `replay_weekly.py` 的 `build_msg` 也通知「舊帳凍不了」 |
| F6 | 採信 | 席位附 `dispatch-lens-hook.py` 的 `FAIL_NOTE` 只認固定原因碼,範圍格式寫錯不講 |
| F7 = A1 | HIT | `Systems/README圖產生器.md` 的 PITFALL 記 qlmanage 會截到動畫第一格,新紀錄卻寫用 qlmanage 目視 |
| A2 | HIT | 同篇 10/01 evals-overview 紀錄沒加指向 10/10 新紀錄的註記 |
| A3 | 採信 | 新清點用「能從 main 追溯」篩,10/07 那份用提交時間篩,標題範圍與內容對不上 |
| A4 | 採信 | README 探針條目 5 句,清點寫「補一句」 |
| A5 | HIT | 指令參考第一批 `- ` 清單;既有條目是一行簡介加帶註解的指令區塊 |
| A6 | 採信 | 開關表是第一份彙整,情境說明另在 skill 手冊 06、07 |

## 修補因果(regression)

- 首輪,不適用。

## 修前選例

| 組 | repair | preserve |
|---|---|---|
| 規格閘說明 | `spec-gate --help` 與總表講到風險低紅綠是放行條件(新測試 `t_spec_gate_help_says_low_risk_blocks` 修前紅) | `-k spec_gate` 既有 101 條照綠 |
| 文件說法 | README、指令參考、清點、圖說的通知條件、開關表、派工掛鉤、探針說明與程式一致 | `--suite docs` 736 條照綠;`generate.py --check` 照綠 |

## 處置

- 本輪有存活 major(F1),code 迴圈 major 輪 accepted 必空,13 條全部折入:F1–F7、A1–A6(F7 與 A1 同一處)。
- 修補提交:082a5d7d(文件、圖、說明文字、家筆記)、b53500e2(新測試修前紅、修後綠,綁進 `Systems/規格閘`)。
- 圖改產生器重產;四張圖用無頭 Chrome(`--virtual-time-budget=10000`)完整轉圖目視,中英字都在框內。
- 編排者驗收:`-k spec_gate` 101、`-k help` 8、`-k subcommand` 1、`-k command_index` 14、`--suite docs` 736,全綠。
