# r4 收貨、重現與處置

## 開輪依據與材料

- 第三輪到 standard 上限,處置閘已過但三輪都有 major、第三輪修補沒有新席審過;使用者裁定破例再一輪(`loop cap-decision extra-round`),只審第三輪修補。跑滿回顧已記(`cap-retro.json`)。
- 修補鏡頭:修前 a4d42fea → 修後 40f871bf(`r4-repair-binding.json`,祖先關係 rc0,區間只有一個修補提交)。完整快照 `r4-snapshot.patch` 範圍 69ac44b2..a36b9633。
- 照 standard 編制派兩席全新 Claude Sonnet:正確性席讀完整修補差異 736 行(兼改壞實驗),架構對齊席讀主程式與測試兩段 553 行。派工詞禁止讀 r1–r3 卷證與回顧。
- 配對案例:第三輪修補前已列,另存 `r4-behavior-cases.md`。

## 收貨

- 兩份報告從子代理逐字稿抽最後一則正式報告存檔,不含跳脫字;都已是正規化格式。
- `quote-check`:兩份全數錨定。
- `refcheck`:正確性席兩處 missing 是 `governance/note-verdicts` 資料夾名(它描述的情境用的路徑,repo 裡沒有這個資料夾),不是檔案引用。

## 重現(編排者機械重現)

finding 編號:架構對齊席 A1;正確性席 C1–C3(報告 F1–F3)。

| finding | 重現 | 說明 |
|---|---|---|
| A1 | HIT | 臨時 repo 把 `governance` 做成指到 repo 外的連結:`_repo_path_unsafe(root, "governance/note-verdicts", dirs=True)` 回 `('symlink', …/governance)`;`_note_audit_load_verdicts` 只判 `d.is_dir()`。席位另附 `_drift_load_acks` 讀到外面帳的實測 |
| C1 | HIT | 同 A1 的筆記內容審那一支(兩席獨立點到同一處);席位附修前修後兩版都讀到外部判定檔 |
| C2 | 採信 | 席位附重現腳本:13 萬層判定檔提交後 `note-audit check` 印 RecursionError 堆疊;`_note_audit_parse_verdict` 只接 `(ValueError, UnicodeDecodeError)`,讀碼相符 |
| C3 | 採信 | 席位改壞 M14:外層 `except OSError` 改成別的例外,`-k reread_wt_records_guarded` 28 條、`-k reread_block_layer1` 12 條照綠;產品行為 chmod 000 實測回空 |

## 修補因果(regression)

- 四條都有兩版證據屬原有漏查:A1、C1、C2 的函式在 a4d42fea 與 40f871bf 完全相同(席位 diff 為空);C3 修前版做同樣改壞也照綠。沒有 finding 有證據屬修補回歸,所以這輪帶 `--regression-set none`。
- 正向主張:上層連結、深層設定、四種帳 head_sha、整族清除、來源欄兩邊、指令引號的 repair 與 preserve 都有席位兩版證據(見兩份報告的三問段);指令引號那組是 preserve(`_sh_quote` 就是 `shlex.quote`),不是 repair。

## 處置

- 本輪最高 minor,四條都附理由放行,不在這條分支改:
  - A1、C1:修補前就有的同族讀端,屬於筆記內容審與漂移表態帳兩個別的功能;推送前檢查只認已提交的樹,不會讓閘被繞過。
  - C2:筆記內容審讀判定檔的解析,那道閘沒接進推送前掛鉤與 CI,只影響手動跑。
  - C3:產品行為對,缺的是測試。
- 四條記進 `Issues/工作目錄治理資料讀端未走共用路徑守衛`(症狀、根因、怎麼繞、什麼算修好,REVISIT 2026-11-09 另開改動一次掃完)。
- 這輪沒有修補,不需要修正紀錄與修正關卡。
