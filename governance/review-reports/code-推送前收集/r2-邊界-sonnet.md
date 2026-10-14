severity: minor

## Finding 1：孤兒檢查的等待窗口只有 0.3 秒，機器一忙，翻紅釘就失效

severity: minor
blocking: 否 — 只是守衛測試在負載下會假綠；掛鉤本身的行為沒錯。
引句:「_time.sleep(max(0.0, 5.0 - (_time.monotonic() - t0)))」

問題：⑥、⑦兩條要證明「孤兒各片已被收掉」。它們靠假全套測試睡 4 秒後寫下 `SUITE-END` 來偵測孤兒。但等待是從 Popen 起算固定到 5.0 秒，不是從假全套開始跑起算。掛鉤起動、跑完各道閘的假 lumos 呼叫、再到起全套，這段時間在空閒機器上約 0.7 秒。孤兒的 `SUITE-END` 會在約 4.7 秒寫下，檢查在 5.0 秒讀，餘裕只有約 0.3 秒。

具體失敗情境：
- 我把 `run_group` 裡新加的 `trap ... exit 143` 那行拿掉，等於把 r1 併發席的孤兒缺陷放回去。
- 空閒時 ⑥、⑦ 都紅，翻紅釘有效。
- 在背景放 2 倍 CPU 核心數的忙迴圈再跑同一個子集，⑥ 變綠（孤兒存在卻沒被抓到），只剩 ⑦ 紅（見下一條）。
- 推送前閘就是分片並行跑 `test_lumos.py`，這條測試正好跑在這種負載下。
- 同一組用 `took < 3.5` 的斷言（⑤、⑦）在負載下反方向會假紅，也是同一個固定時鐘的問題。

這是 r1 併發席那條缺陷的唯一回歸守衛，失效後再被改壞不會有人發現。

建議：等待窗口改成從假全套寫下 `SUITE` 那一刻起算（輪詢 `argv.log` 出現 `SUITE` 後再等 4.5 秒以上）。`took` 的上限也同樣要放寬。

佐證：``file: `scripts/test_lumos.py`（t_prepush_interrupt_stops_every_gate 的 ⑥⑦ 段）``。我在 scratchpad 的副本上拿掉 trap 重現，副本已刪。

## 已讀，無 finding

- **版本探測**：`grep -q -- '"--keep-going"' "$GRAPHCTL"`。
  - 現行 `scripts/lumos` 只有一處，在 `check` 子命令的 argparse 註冊裡，歷史上也只有 a9362d4c 加過，沒有別的子命令會誤判成新版。
  - 檔案讀不到、很大或當二進位檔都安全：`2>/dev/null` 加 `-q` 會退成舊路徑，只記一筆，不會放行。
  - 字樣若改成單引號，探測會靜默退化，但 ⑧ 測試守著。
- **重導向包組**：`{ printf ... >> f; } 2>/dev/null || true`，開檔失敗的雜訊確實被擋。
- **tee 的 `>&2 2>/dev/null`**：輸出照印，留底檔寫不進去也不噴錯。
- **`LUMOS-BLOCKS:` 壞形狀**：下列情況都落到通用句或只記一筆，不會放行，也不會把 glob 展開。
  - 沒有那一行、空行、未知種類。
  - 逗號後有空白、空元素。
  - 兩行時取最後一行。
  - 沒有空格的 `LUMOS-BLOCKS:review`。
- **`push-summary` 照換行切**：U+2028、U+2029、U+0085 的 ref 名不會被切斷。補一點：Python 端的 `.strip()` 會吃掉欄位頭尾的 Unicode 空白，但只影響顯示。
- **漂移測試抽表**：
  - 抽出的表與 `scripts/lumos` 一致。
  - 抽 `reason_kind` 的正則沒有漏抽或誤抽。我逐一核對了 `.get("reason_kind")`、`reason_kind=reason_kind` 等寫法，都不會被誤抽。
  - 抽不到或對不上時是紅，不是靜默綠。
  - 只有「同一種類在掛鉤寫兩次且句子不同」這種人為情境會讓 dict 去重蓋掉差異。
- **逃逸 elif、`pp_keep_log`、log 搬進 `$_PP_TMP`**：邏輯與測試相符。
- **新測試**：`push_summary`、`prepush_cl_reason`、`prepush_escape_records`、`prepush_block_kinds`、`prepush_test_logs`、`prepush_mixed`、`prepush_plain_summary` 七組在空閒機器上都 rc=0。

最高等級 minor，blocking 0 條。
