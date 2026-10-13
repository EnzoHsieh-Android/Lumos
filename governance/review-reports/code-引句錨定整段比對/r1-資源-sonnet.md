severity: minor

併發與資源這一鏡頭沒有找到 major 以上的問題。我實際跑過這些項目:
- 寫側的順序是對的:擋下事件先落帳,再印訊息、回 rc2。擋下時沒有寫帳,所以不會有帳寫了而事件沒寫的情況。
- `_gate_event_or_warn` 失敗時只在 stderr 警告,不改判定。`_gate_event` 本身也接住了 `OSError` 和 `UnicodeEncodeError`。
- `rec["quote_rule"]` 只在 `findings_set` 和 `--snapshot` 都有給的區塊裡才寫,也就是只蓋在載體那一列,這是對的。
- `KeyboardInterrupt` 和 `SystemExit` 沒有被 `except Exception` 吞掉。
- full-span-v1 對 14MB 的對抗輸入跑起來都是線性時間:未閉合、深巢狀、單一巨大引句、2M 個落單收尾引號。14MB 混合輸入峰值約 2GB,但真實報告只有幾百 KB,不構成問題。
- 對真實帳本跑 `--compare-rules` 約 25 秒、峰值 1.35GB,下面第 2 條就是這個。

1. 比較模式讀到帳上的路徑含 NUL 字元時,整個指令 traceback 中止
severity: minor
blocking: 否
引句:「return (Path(rel) if Path(rel).is_absolute() else root / rel).read_text(encoding="utf-8")」
file: `scripts/lumos:26698`
- 輸入:帳列的 `report_path` 是 `"a\u0000b.md"`。`json.dumps` 允許這種字串,手改或壞帳都可能出現。
- 走到哪:`_read` 呼叫 `read_text`,丟出 `ValueError: embedded null byte`。外面只接 `UnicodeDecodeError` 和 `OSError`。
- 壞在哪:我實跑是 traceback 收場,前面已經算好的統計一個都沒印。
- 這跟指令自己的設計不一致。「讀不到」「非 UTF-8」「壞行」都是計數後略過,唯獨這一類會讓整個唯讀統計失效。
- 建議在 `_read` 外把 `ValueError` 也算進 `unread`,或在取出路徑時先擋掉含 NUL 的值。

2. 比較模式對同一份快照,每份報告都重新正規化兩次,時間和記憶體都被放大
severity: minor
blocking: 否
引句:「a = _quote_rows(rtext, stext, rule="legacy")」
file: `scripts/lumos:26719`
- 輸入:真實帳本有 953 份快照,最大一份 72MB。
- 走到哪:每份報告各呼叫 legacy 和 v1 一次。兩版內部都會對整份快照做 `_quote_norm`,也就是 `split`、`join` 和去空白三種大副本。
- 壞在哪:同一份快照下有 N 份報告,就正規化 2N 次。實測 `quote-check --compare-rules` 約 25 秒、峰值 1.35GB,指令本身的基線是 247MB。
- 「同時只留一份快照」只限制了原文,沒有限制正規化後的副本。
- 這是只在人手動跑時才會碰到的唯讀指令,不會卡閘,所以只列 minor。

3. ⚠ 處置閘用 `except Exception` 接判準例外,連記憶體不足也當成判準失敗
severity: minor
blocking: 否
引句:「rows = _quote_rows(_rtext_q, _stext_q, rule=_qrule)」
file: `scripts/lumos:26521`
- `MemoryError` 是 `Exception` 的子類,會被這個 `except Exception` 接住。
- 計劃文字明說這是要「判失敗、回放報邏輯漂移」。所以週跑子程序在大快照上暫時 OOM 時,會報成「引句判準丟例外」的漂移。
- 手動 `loop replay --freeze` 對 rc1 照樣凍結,計劃已承認這是既有設計。所以暫時性 OOM 可能被凍成一份判失敗的黃金判定。
- 我沒有實際讓 OOM 發生,只讀程式與計劃文字,所以標 ⚠。
- 建議把 `MemoryError` 單獨放行重丟,或在訊息裡標明是資源不足而非判準問題。

我建的實驗目錄已刪除。

總結:最高等級 minor,blocking 共 0 條
