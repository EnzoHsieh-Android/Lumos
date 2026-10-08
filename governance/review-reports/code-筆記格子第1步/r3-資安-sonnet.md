severity: minor

**第 3 輪資安審查(R3S):1 條 minor,0 條 blocking。** 我只讀碼,沒有實際跑出終端畫面。對照了 r2 資安報告,也讀了 `_ns_check_line`、`_esc_clean` 和 `_note_shape_report` 的現行碼。

**R3S-1 路徑已清控制字元,同一行的 `frag` 和同類的 `errs` 還是原樣回印**
severity: minor
blocking: 否 — 只能污染終端顯示,拿不到權限或資料;而且是這批修正漏掉同一行的另一個欄位,縱深防禦層級。

引句:「shown = "; ".join(f"{_esc_clean(p, 200)}:{n} {rule} {frag}" for p, n, rule, frag, _f in viol[:10])」

1. 攻擊路徑(推論):
   - 攻擊者在 PR 或別人的分支裡,於筆記摘要區寫一行 `FACT: <ESC 序列…>`,不帶 `[來源:…]`。
   - 維護者或 CI 跑 `lumos note-shape --diff` 或 `lumos doctor` 時,`_ns_check_line` 會回傳 `("現況描述沒寫來源", text.strip()[:60], …)`。
   - 這個 `frag` 是筆記原文前 60 字,`strip()` 去不掉 ESC(0x1b)。
   - 它被原樣印到 stderr:`_note_shape_report` 的 `print(f"  {_esc_clean(p, 200)}:{n}  {rule} {frag}:{fix}", …)`,以及 doctor 的 `shown`。這兩處的 `frag` 都沒走 `_esc_clean`。
   - 拿到的東西:偽造終端畫面,例如用游標移動或清行把「擋下」訊息蓋掉。
   - 不確定的一點:被審 diff 沒顯示 `context_marker_warnings` 會不會預先濾掉含控制字元的行。
2. 同一類殘留:`errs.append(f"{p}:這篇筆記不是 UTF-8 文字,檢查不了——轉成 UTF-8 再提交")` 的路徑 `p` 沒清,再由 `for e in errs: print(f"  {e}")` 印出。
   - 位置是 `scripts/lumos:26125` 和 `scripts/lumos:27694`。
   - 檔名可以夾 ESC,這正是 r1 資安席要補的那一類。
   - 本輪只補了 `viol` 的 `p` 和 doctor 的路徑,沒補這條。
3. 修法:在 `_note_shape_report` 把 `frag` 和 `e` 都包 `_esc_clean`。doctor 的 `shown` 也同樣處理 `frag`。

**逐類**

1. **不可信輸入流到危險操作:已看,無。**
   - 新增的三個正規式 `_NS_SLOT_LINK_RE`、`_NS_SLOT_PUNCT_RE`、`_NS_PTR_SEP_RE` 沒有巢狀量詞。
   - `\[\[[^\[\]]*\]\]` 的字元類排除 `[`,所以連續 `[[[[` 或缺右括號的輸入不會多重重掃,是線性的。
   - `_ns_text_key` 的 lookbehind 和 lookahead 是單字元,也沒有回溯風險。
   - git 呼叫沒有變動:`cat-file --batch` 走 stdin,argv 固定,沒有 shell 插值、eval 或反序列化。
2. **登入與權限:已看,無。**
3. **密鑰與個資:已看,無。**
   - 治理帳新增的 `check` 是 `slots` 或 `shape+slots` 這兩個固定字串。
   - `slots_lines` 和 `slots_missing` 沿用 r2 的結論,是整數和程式內固定格名,筆記內容流不進帳本鍵。
4. **加密與傳輸:已看,無。**
5. **執行邊界:有 R3S-1。**
   - 逃生口 `LUMOS_SKIP_NOTE_SHAPE` 仍會留帳。
   - 子開關 `note_shape.slots` 可被同一提交關掉,這是計劃天花板第 4 項已承認的設計,不重報。
   - 「舊行」判定:r2 的修法把舊行比對拆成 `text`、`ptr`、`phys` 三桶。`ptr` 桶現在要求舊連結全含在新行裡,換連結和刪連結算新寫。這只會多擋,沒有放寬繞過路徑。續行改為只比整條,關掉了「在舊句後面接續行躲檢查」的繞過。
6. **行動端:不適用。**
7. **新依賴:無。**

**圖譜鏡頭(LUMOS-IMPACT):** 這批改動只動 `scripts/lumos` 的筆記格子檢查、`scripts/test_lumos.py` 和計劃筆記。我沒有找到被它破壞的資安合約。治理帳結構欄位只是加了固定值的 `check`,沒有放寬任何擋下條件。

最高嚴重度 minor,blocking 0 條
