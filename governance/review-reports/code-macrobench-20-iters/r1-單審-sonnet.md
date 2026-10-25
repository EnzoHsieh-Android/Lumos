severity: major

## F1 cv 算出無限大時,寫進基準的檔自己讀不回來,整份基準被鎖死
severity: major
blocking: 是
引句:「cv = {}」不在 diff;原文為 `return statistics.pstdev(runs) / abs(mean) if mean else None`
file: `scripts/lumos:39495`(`_macrobench_cv`)、`scripts/lumos:39661`(`_macrobench_entry_ok` 新增的 cv 檢查)
場景:
- 某個啟動類指標的 runs 是有限數,例如 `[1e300,-1e300,5e-324,5e-324,5e-324]`。平均是 5e-324,不是 0,所以不走 `else None`。
- 母體標準差約 6e299,相除得 `inf`。`_macrobench_iterations` 把 inf 當 cv 記下。
- `_write_lf` 的 `json.dumps` 寫出 `Infinity`。
- 下一次讀基準時,`_macrobench_entry_ok` 用 `_macrobench_num` 驗 cv,拒收非有限數,所以整份基準被判讀不了。
- 我在暫存 repo 實跑。`--update-baseline` 印「基準已更新」,隨後 `--json` 得到 `baseline_unreadable: true`、`checked: 0`。
- 此後 `--update-baseline` 也拒絕覆蓋,要人手動 `rm`。寫端產出的東西,讀端自己不收。
- 這違反 S4 寫的「含非有限數時那一項不記,照樣能比、能存」。
- 另一條相關路徑:runs 是 `[1e308,1e308]` 時,`statistics.fmean` 丟 `OverflowError: intermediate overflow in fsum`。`_macrobench_collect` 的 `except Exception` 接住後,整個結果檔被當讀不了。改動前這個檔能讀。
建議:
- `_macrobench_cv` 內包 try/except OverflowError,回 None。
- 算完後 `math.isfinite` 檢查,不是有限數就回 None。
- 補一條測試,餵 `[1e300,-1e300,5e-324,...]` 與 `[1e308,1e308]`,斷言檔案仍讀得進來,且基準寫出後 `baseline_unreadable` 為 false。

## F2 平均為 0 的保護沒有測試守著
severity: major
blocking: 否
引句:「return statistics.pstdev(runs) / abs(mean) if mean else None」
file: `scripts/lumos:39495`;測試 `scripts/test_lumos.py` 新增的 `t_macrobench_baseline_records_iterations`
場景:
- 啟動類指標 runs 全是 0,例如 `[0,0,0]`,平均為 0,應不記 cv。
- 我把 `if mean else None` 拿掉後跑 `-k macrobench`,179 條通過。2 條失敗是我的複本缺 governance fixture,與這個改動無關。
- 拿掉後的行為是 `ZeroDivisionError`,整個結果檔被當讀不了。
- 新測試只有平均 100 與平均不為 0 的情境,沒有平均為 0,也沒有平均為負數取 `abs` 的情境。
- 這是 S4「算 cv」的必要邊界,改壞測試抓不到。
建議:在 `t_macrobench_baseline_records_iterations` 加兩個情境。runs `[0.0,0.0,0.0]` 要照樣存進基準、`cv` 不含該指標、`iterations` 是 3。runs 平均為負時,cv 要大於 0。

## F3 --update-baseline 存下少於 20 輪的基準時完全沒有提醒
severity: minor
blocking: 否
引句:「for x in res.get("low_iterations", []):」
file: `scripts/lumos:40202` 之後 `return _macrobench_update(...)`(約 `scripts/lumos:40206`)
場景:
- `res["low_iterations"]` 在 `if update_baseline: return _macrobench_update(...)` 之前就算好,但那條路徑直接 return,不呼叫 `_macrobench_print`。
- 專案用 5 輪結果 `--update-baseline` 時沒有任何「輪數不足」提示。
- 這份基準之後會讓 20 輪規則永遠不啟用,而使用者第一次看到提醒要等到下一次比對。
- S3 寫的是「現況少於 20 輪時,文字輸出應印一行提醒」,字面上沒限定模式。
- 測試也只在比對模式驗。
建議:`_macrobench_update` 之後同樣印 low_iterations 提醒,或在 S3 明寫只在比對模式提醒,並補一條 `--update-baseline` 的測試。

## F4 S3 提醒測試的第⑤條判準太鬆
severity: minor
blocking: 否
引句:「line = [l for l in t.stdout.splitlines() if "pkg.S#coldStartup" in l and "20" in l]」
file: `scripts/test_lumos.py`(`t_macrobench_low_iterations_notice` ⑤)
場景:
- 篩選條件的「20」只因提醒句固定寫著「iterations 設 20」才會中。
- 判準「`"5" in l`」是子字串比對。把輸出的輪數寫成 15 或 25 仍然通過。
- 輪數印錯(例如寫成基準的輪數)時,若數字字串裡剛好含 5,測試抓不到。
建議:改成比對完整片段「只跑了 5 輪」。

## F5 條款 S4 與實作對「那一項」的範圍有出入
severity: minor
blocking: 否
引句:「結果檔的 runs 缺、不是清單或含非有限數時那一項不記,照樣能比、能存」
file: `scripts/lumos:39511-39522`(`_macrobench_iterations`)、計劃筆記 S4
場景:
- 同一情境有兩個啟動類指標,其中一個 runs 壞掉。實作整個情境不記 `iterations`,但好的那個指標的 `cv` 照記。
- 「那一項」可讀成指標,也可讀成情境,字面不明。測試 ⑤b 只驗 `iterations` 不記,沒有驗 `cv`。
- 若日後有人改成情境不記 `cv`,或指標也記,沒有測試會紅。
建議:把 S4 改寫成「情境不記輪數、好的指標仍記 cv」,並在 ⑤b 加一條對 cv 的斷言。

## 沒有問題的項目
- `low_iterations` 鍵在 `res` 初始化就固定帶上。`_macrobench_without_results` 走 `dict(res, ...)` 輸出時是 `[]`,與基準缺失路徑一致。
- 舊基準(沒有 `iterations`)走 `isinstance(e.get("iterations"), int)` 為 False,所以 `mag_only` 為 False,判定照舊。
- 舊版程式讀新基準不檢查多出的欄位,所以不受影響。
- bool、0、負數的 iterations 在 `_macrobench_entry_ok` 被擋,測試 ⑦⑧⑨ 有守。
- `ignore_metrics` 在讀端與 iterations 計算端一致排除。
- 固定席節點(design-loop、guard-kill、lumos-cli-read 等 INVARIANT)只牽連 scripts/lumos 與測試總檔,這份 diff 沒有動到它們各自宣稱的行為。

總結:全篇最高為 major
