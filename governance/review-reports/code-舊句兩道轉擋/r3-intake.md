# r3 收貨、重現與處置

## 材料與編制

- 修補鏡頭:修前 88322e46 → 修後 59f8f92b(`r3-repair-binding.json`,祖先關係 rc0,區間只有一個修補提交)。修補差異依區塊拆三段,每席必讀自己那段(lumos 618 行、測試 545 行、文件 456 行),同塊完整改動當上下文;架構對齊席讀 lumos 與測試兩段。四席皆全新 Claude Sonnet,派工詞禁止讀 r1-*、r2-* 卷證。
- 完整快照 `r3-snapshot.patch` 範圍 69ac44b2..a4d42fea。
- 配對案例:上一輪修補前已列,另存 `r3-behavior-cases.md`(不含上一輪結論)給新席。

## 收貨

- 四份報告從子代理逐字稿抽最後一則正式報告存檔,都不含跳脫字;都已是正規化格式。
- `quote-check`:
  - 架構對齊席全數錨定。
  - 正確性主程式席零 finding、沒有引句(報告是 clean)。
  - 測試假綠席 #3、文件一致席 #3 錨不到,見下表 T3、D3(機械重現 HIT)。
- `refcheck`:missing 0、out_of_range 0。

## 重現(編排者機械重現)

finding 編號:架構對齊席 A1–A4;測試假綠席 T1–T4(報告 F1–F4);文件一致席 D1–D3(報告 F1–F3)。正確性主程式席零 finding。

| finding | 重現 | 說明 |
|---|---|---|
| A1 | HIT | 臨時 repo 把 `governance` 做成指到 repo 外的符號連結:`_repo_path_unsafe(root, "governance/reread-verdicts", dirs=True)` 回 `('symlink', …/governance)`;`_note_reread_wt_verdicts` 的判斷 `d.is_dir() and not d.is_symlink()` 在同一路徑是 True/False,照樣走訪。寫端 `_note_audit_write_verdict` 走共用守衛,讀端沒走 |
| A2 | 採信 | 席位附對照 file:line:`_note_audit_config`、`_drift_config_text_parts` 只接 `(ValueError, UnicodeDecodeError)`,13 萬層設定檔實測丟 RecursionError;專案多處慣例就地接 RecursionError |
| A3 | HIT(讀碼) | `_note_reread_add_cmd` 自己 `shlex.quote`;既有 `_sh_quote`(印給人貼的指令參數)做同一件事 |
| A4 | 採信 | 測試 ③ 換掉 `sys.modules["json"]`,全檔沒有先例;綁死被測函式內部 import 寫法 |
| T1 | 採信 | 席位改壞實驗 C1、C2:設定檔與報告兩個呼叫端改回 `json.loads`,`-k t_reread_block`、`-k t_note_audit_reread` 照綠 |
| T2 | 採信 | 席位改壞實驗 H1–H4:skipped、none、covered、undecidable 四種帳不傳 head_sha,測試照綠;只有「有東西」那筆有測 |
| T3 | HIT | 引句在 `scripts/test_lumos.py` 的 `t_runner_drops_inherited_skip_env` 說明,快照裡被換行切成兩行所以錨不到;席位改壞 M30(寫死三個名單)照綠 |
| T4 | 採信 | 席位改壞 M36:來源欄寫死 ci,測試照綠;只驗 ci 一邊 |
| D1 | HIT | `Projects/守檔筆記對照改動_計劃.md` 第 106 行仍寫 `git add governance/reread-verdicts && git commit` |
| D2 | HIT | `Projects/舊句兩道轉擋_計劃.md` 第 67 行仍寫「detail 記兩層各幾篇…」,沒提 `layer1_fps` 與 skipped 帶 state |
| D3 | HIT | `Systems/reversibility-governance-ledger.md` 第 29 行寫 `_gate_event_fit` 由兩種帳共用,回頭重讀已是第三個使用者;這篇本分支沒改過,所以引句不在快照裡 |

## 修補因果(regression)

- 有證據屬上一輪修補新增、而且沒守住:A4(修補新增的測試寫法)、T1、T2(修補新加的行為只測了一部分呼叫端)。
- 有證據的原有漏查:A1(修前兩份走訪都只看最後一層,修補合併時照搬)、A3(同區 `_note_reread_cmdline` 兩版都直接 shlex)、T4(修前寫死 ci 也照綠)、D1、D2。
- 未判定:A2(包裝是修補新增,兄弟閘沒接 RecursionError 是原有漏查,混在同一條)、T3(修前是 main() 清前綴的另一種寫法,沒有可比的測試)、D3(回頭重讀使用它早於修補,多鍵語意是修補新增)。

## 修前選例(本輪修補前列)

| 組 | repair(原問題要好) | preserve(既有正常行為不能壞) |
|---|---|---|
| 讀端路徑守門 | 上層資料夾(`governance`)是符號連結時,工作目錄紀錄不被讀進來,prepare 與 `drift ack --kind reread` 兩邊都一樣;測試要有「上層是連結」一組 | 資料夾本身是連結、單檔是連結、FIFO、太大、形狀壞照原本略過;正常未提交紀錄照算只差提交(`t_reread_wt_records_guarded`、`t_reread_block_layer1`) |
| 巢狀太深 | 設定檔與判定者報告兩個呼叫端各有一條深層巢狀測試;同一份 `.lumos/config.json` 的兄弟閘讀設定不再丟 RecursionError | 正常設定照讀;讀不成 JSON 的既有訊息與退回預設不變(`-k note_audit_config`、`-k drift_config`、`-k note_shape`) |
| 指令引號 | 給人貼的提交指令走既有 `_sh_quote` | 一般檔名印出來不變 |
| 測試寫法 | 行程內造 RecursionError 改用專案既有的替換寫法,不換 `sys.modules` | 原本「解析不接 RecursionError 就紅」照紅 |
| 帳欄位測試 | skipped、none、covered、undecidable 四種帳的 head_sha 各有斷言;來源欄本機記 hook 有斷言;清略過變數有一條觀察「整族」的斷言(例如子行程裡除了 `LUMOS_SKIP_CLAUDE_PLUGIN` 沒有任何 `LUMOS_SKIP_*`) | 原有 ① 到 ⑦ 斷言照綠 |
| 文件 | 三處文件與真碼一致 | 未改動的段落照舊 |

## 處置

- 本輪有存活 major(A1),code 迴圈 major 輪 accepted 必空,所以全部折入:A1–A4、T1–T4、D1–D3。
- 本輪是上限輪(standard 上限 3 輪)。折入後的修補差異沒有新席審過;要不要再開一輪交人裁(`loop cap-decision`)。

## 修補提交與驗收

- 40f871bf:六組一起修(修補代理,照上表修前選例;15 種改壞全數翻紅)。
  - T1、T2、T3、T4 修前就綠:產品行為本來對,缺的是測試;新測試靠改壞翻紅證明守得住。
  - G1 在 drift ack 那邊,上層連結時寫端守衛先擋下,端到端看不到讀端,另加一條行程內直接呼叫讀端的斷言。
  - 修補代理順手發現舊 ③ 的 drift ack 那一半傳空字串當筆記內容,只驗到一半;已改餵真內容並加前置斷言。
  - 沒改、超出範圍:筆記內容審讀工作目錄判定檔的 `_note_audit_load_verdicts`、`_note_audit_parse_verdict`(讀判定檔不是設定檔)、`_ci_config`(不是推送前閘)。
- 編排者驗收:抽看主程式改動(讀端改走 `_repo_path_unsafe`,在既有 OSError 保護內;指令引號改走 `_sh_quote`;兄弟閘就地接 RecursionError);自己重跑 `t_reread_wt_records_guarded` 28、`t_reread_deep_json_config_and_report` 2、`t_note_audit_and_drift_config_deep_nesting` 5、`t_reread_cmd_quote_shared` 4、`t_reread_ledger_head_sha_all_kinds` 7、`t_runner_drops` 4、`t_reread_block` 92、`t_command_index_complete` 14、`gate_event` 5,全綠。

## 記帳註記

- 各席 `--scope-lines` 記該席必讀的修補差異行數(主程式 618、測試 545、文件 456、架構對齊兩段共 1163)。
- 載體席選全數錨定的架構對齊席。A2、T3、D3 修補因果未判定(見上),依共用範本 §3.1 這輪帳不帶 `--regression-set`。
