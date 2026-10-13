severity: minor

整體結論:拿掉 `--compare-rules` 後,程式與手冊都沒有殘留。我用 grep 掃過 `scripts/lumos`、`scripts/test_lumos.py`、`skills/`、README 和 Systems 節點,都沒有 `compare-rules` 或 `_QUOTE_COMPARE_*`。舊測試名 `t_quote_full_span_compare_and_event` 在非卷證處也已清乾淨。

在我的實驗複本上跑的結果:
- 六篇節點(計劃、`loop-convergence-recording`、三篇 Issue、Verification)`lumos lint` 都是 0 問題。
- `lumos doctor` 只報 1 個 issue,是與本次無關的 Y 項(`效能檢核目錄.md` 的 `OpenAsync` 查無符號)。
- S1–S8 八個綁定測試名都存在,`-k quote_full_span` 是 82 條全綠。
- ★INVARIANT★ 節點的綁定測試沒被動到。

**1. 計劃正文還寫著「與比較模式同一規則」**
severity: minor
blocking: 否
引句:「寫側求 `kind` 那一次與比較模式同一規則(r2 架構對齊席)」
file: `docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md:72`
- 比較模式已在第 4 輪後拿掉,這句成了指向不存在機制的描述。
- Systems 節點那條 MemoryError 規則已改成「處置閘與寫側兩處」,計劃第 72 行沒跟上,兩邊不一致。
- 同類的小殘骸:`quote-check --spec` 的說明還寫「一般模式必填」(`scripts/lumos` 的 `add_argument("--spec"...)`),現在只剩一種模式。

**2. Verification 的斷言數與變異清單是第 4 輪的舊數字**
severity: minor
blocking: 否
引句:「代碼審四輪修補後 `-k quote_full_span` 是八支 95 條斷言」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-13_引句判準第一階段推送前驗證.md:26`
- 我實跑是 82 條,不是 95。拿掉比較模式的測試後少了 13 條。
- 同篇第 27 行的變異清單仍寫「比較模式路徑與讀檔與大小上限」。這些防線和測試都已刪除,又沒補上第 5 輪新改處的變異紀錄。這篇 Verification 是 `valid_under` 第一階段的依據,數字應該要能重現。

**3. 第 5 輪的兩處修補沒有翻紅釘(變異後測試仍全綠)**
severity: minor
blocking: 否
引句:「sha12 = report_sha[:12]」
file: `scripts/lumos:25840`
- 變異 A:把兩處呼叫的 `_validated_sha.get("--report")` 傳成 `None`(退回重讀檔)。`-k quote_full_span_block` 25 條全綠,存活。
  - 這是 r4 資源席的 TOCTOU 修補,「用寫側驗過的那份位元組的指紋」沒有任何測試釘住。
  - 現有測試只在檔案沒被換掉時比對 `report_sha`,兩種寫法的結果完全一樣。
  - 需要一支測試:在驗證與擋下之間換掉報告,斷言 `report_sha` 仍是驗過那份的指紋。
- 變異 B:把處置閘診斷的 `len(x) > 1000` 分支改成 `False`。`-k quote_full_span` 82 條全綠,存活。
  - 計劃第 72 行明寫了「超過 1000 字改印說明」,但測試只測了控制字元(tab)那一支,過長路徑沒有測試。
- 附帶:`_QUOTE_MALFORMED_CAP` 用在 `rtext.find(..., op + 2 + _QUOTE_MALFORMED_CAP)` 的掃描上限,拿掉後輸出不變,存活。那只是效能上限,沒有行為斷言;若要守住,需要一支超長單行未閉合的耗時測試。

其餘變異都翻紅:診斷行 `[disposal]` 前綴、`_kill_esc` 跳脫(連帶 3 條斷言)、`quote` 欄 200 字上限與截斷標記、`_QUOTE_WRITE_RULE` 預設值、`kind=unknown` 記法。

我已刪掉自己的實驗目錄。

總結:最高等級 minor,blocking 共 0 條
