# r4 收貨紀錄(6 席全新,人裁破例第 4 輪)

席位與編號:正確性 C1–C10、邊界 B1–B11、接手的人 H1–H7、簡化 S1–S7、回滾 R1–R7、架構對齊 A1–A5(A6 是「已讀,無 finding」不計)。共 47 條。

## 引句錨定狀況

quote-check:接手的人、簡化、回滾、架構對齊四席全數錨定(載體選回滾);正確性 4 句、邊界 1 句錨不到——都是引句跨行或抄到行尾被截(正確性 #1 #3 的引句延伸到下一行、#2 #4 抄到行尾帶出反引號外文字)與一句短於 10 字的「原文」示範(邊界 #3),內容逐條在下表重現。

## 機械重現表

| 群 | 涵蓋 finding | 重現命令/查證 | 結果 |
|---|---|---|---|
| 全域堆疊被前面落單開引號吃掉 | C1 B1 | scratchpad `proto_pair.py`:攻擊字串前加 `他提到「某規則 還沒結束` 換行 → 全域堆疊落單位置 `[]`(放行);不加 → `[27]`;改成每條尾段各自數 → 三種前文都數到 1 | HIT(兩席獨立實測,邊界席另掃帳上 22/3034 份有留到結尾未配對的開引號) |
| 設定區塊與降級路徑 | S1 C2 B2 B11 A3 H5 C6 R6 | 讀 r4-snapshot〈判準版本蓋在帳上〉:設定壞值退回 legacy、`write_rule: legacy` 可讓寫側放行後半編造;〈回退〉自承改設定要走推送閘 | HIT |
| 永久比較指令旗標過多、口徑未定 | S2 B5 C5 B7 B10 | 讀 r4-snapshot〈量測與留痕〉;邊界席實測帳上 226 組多列、80 組載體與非載體並存;3271 組 legacy 全跑 12.9 秒、尖峰 1.65 GB | HIT |
| 文件改動不分階段 | H1 R3 | 讀 r4-snapshot〈兩階段上線〉「行為上等於沒改」與〈同步改的地方〉無階段標註 | HIT(兩席獨立一致) |
| 第二階段放行無門檻、REVISIT 取數做不到 | H2 H3 B6 C9 | 讀 r4-snapshot 兩行 REVISIT;`lumos gov --since 3 --full` 實測會逐筆印 note,可 grep 出 `quote-rule:` 與 `kind=`;被擋報告不進帳、可能被覆寫 | HIT |
| 新判準丟例外的止血 | B3 R4 R5 | `scripts/lumos` 處置閘引句步只包 `(OSError, UnicodeDecodeError)`;`replay_weekly.py` 只認紅燈字眼 | HIT |
| v1 誤放行無撤銷、凍結入口不看綠 | R1 R2 | 讀 `cmd_loop_replay` 凍結只擋 rc2;`governance/replay` 305 份有 5 份 rc1 | HIT(凍結接受非綠是回放既有設計,不屬本計劃;本計劃補程序與釘版測試) |
| 既有測試替身會被 `rule=` 打壞 | A4 C4 B4 | `scripts/test_lumos.py` 約 27411 行 `def quote_rows(*args)` 注入 `cmd_canary`,改成關鍵字呼叫後丟 TypeError | HIT |
| S7 條款字面與帳被動機制 | C3 R7 | 讀 `cmd_loop_replay`:帳被動由逐列 sha 比對決定,與判準無關 | HIT |
| 第二階段會紅的測試不只一支 | A5 H6 C6 B8 | grep `t_quote_full_span_rule_stamped_on_ledger` 無設定檔段、`t_quote_full_span_manual_commands_repo` bare 根段 | HIT |
| 其餘細節 | A1 A2 C7 C8 C10 B9 H4 H7 S3 S4 S5 S6 S7 | 逐條讀 r4-snapshot 對應段與 `scripts/lumos`、`scripts/test_lumos.py`、`docs/methodology/圖譜即合約.md` 對應行 | HIT(規格未定義、措辭或測試缺口) |

## 處置

- 折入 44 條,寫進第五版。主軸:落單判定改成每條尾段各自數;拿掉 `.lumos/config.json` 設定區塊,寫側判準改由程式常數 `_QUOTE_WRITE_RULE` 決定(回退=還原第二階段提交,經推送閘與代碼審、git 有痕);比較指令縮成只剩全帳掃描;文件同步、Issue 與立案清單結案全部移到第二階段提交;第二階段放行門檻;擋下事件帶出問題引句片段;新判準丟例外時處置閘判失敗不 traceback(回放因而報邏輯漂移);v1 判定釘版測試與誤放行處置程序。
- 放行 3 條:
  - A1(並存第二套判定版本機制,⚠):取捨已寫在 PRIOR-ART 並以 decision-add 記決策,推進 `_REPLAY_ENGINE_REV` 會讓 305 個黃金抽查全部跳過重算。
  - S3(拿掉事件的 kind):H3 證明擋下那一刻是唯一確定讀得到報告原文的時候,事後重算常因報告被覆寫做不到;kind 留在寫側算,改成連問題引句片段一起記。
  - S7(第二階段預先宣告不派審):分級由 `pitfalls --diff` 機械判,計劃不能預先宣告;照它判的走。
- refuted:無。
