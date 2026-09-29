severity: minor

## F1 同一句判不了說明裡,只有讀不出的檔名被消毒,筆記路徑與行文字仍原樣印到終端
severity: minor
blocking: 否 — 只影響終端顯示被污染,不改變放行或擋下的判定
引句:「路徑來自被推送的內容,印之前把控制字元換成空格(r4 資安席;借逃逸帳的 _esc_clean)。」
1. 攻擊路徑(推論,未實際重現):有推送權限的人在圖譜資料夾建一篇檔名含 ESC 序列(如 `Systems/a\x1b[2K.md`)的筆記,筆記內寫一行條件式回頭條件並讓它判不了(例如指到讀不出的程式檔)。
2. 走到 `_drift_probe_check` 與 `_drift_probe_candidates` 組 unknown 字串時,用的是 `f"{p}:{no} 的條件判不了(" ...`,p 是筆記路徑,沒經過 `_esc_clean`。
3. `_drift_check_print` 再把 unknown 原樣 `print(..., file=sys.stderr)`;`_drift_scan_print` 也把 `p` 與 `t[:70]`(行原文)原樣印出。ESC 序列進到別人的終端。
4. 這份差異只把 `_drift_bad_note` 的檔名消毒,同一句字串前半的 p 沒補;「_esc_clean 涵蓋所有印出點」沒成立。⚠ 是否真的能建出含控制字元的筆記檔名、且筆記載入器不先濾掉,我沒有跑,所以只標推論。
file: `scripts/lumos:27184-27190`
file: `scripts/lumos:27278-27282`

## 已看,無 finding:partial 判定與點名邏輯能否被構造成靜默放行
引句:「return True if hit else (None if names.partial else False)」
1. 讀不出的檔只會把「找不到」升成判不了(None,block 模式下算要處理),不會把「找到」降成放行;攻擊者放一支非 UTF-8 檔只會造成多擋,不會繞過。
2. hit 為 True 時照走候選、之後由 judge 判定,沒有跳過判定的路徑。

## 已看,無 finding:_drift_row_unread 點名範圍
引句:「out.update(q for q in t.bad_paths() if (q == path if path else _drift_probe_code_path(q)))」
1. 點名只影響說明文字,不影響 verdict;status 的 rel 來自 env.resolve,最後都過 `_drift_bad_note` 的 `_esc_clean`,且有 200 字截斷。

## 已看,無 finding:64 碼提交編號快取
引句:「re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", where)」
1. 只放寬到合法的 SHA-256 提交編號,鍵仍是完整編號,沒有引入可被構造的快取碰撞。

最嚴重等級 minor,blocking 共 0 條。
