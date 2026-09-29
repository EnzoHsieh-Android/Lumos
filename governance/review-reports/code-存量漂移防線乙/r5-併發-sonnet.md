severity: clean

## 併發與資源鏡頭:已看,無 finding

已看 _DriftNames 逐支建集合:texts 與 _DriftProbeTree._text 是同一批字串物件的參照,沒有另外複製全文;集合逐支 update,不再先接成一大段再整批切,尖峰記憶體確實下降。
引句:「+        for t in texts:」

已看 .text 屬性改成每次存取才 join:實測 50 支共 6MB、100 次存取 join 合計 0.02 秒,成本可忽略。同場景 100 條非識別字名稱的正則掃描要 7.9 秒,那是這份差異之前就有的成本(r3 只把純識別字名稱改查集合),不是這份差異引入的,也沒讓它變差。
引句:「+        return "\n".join(self.texts)」

已看 names_in 的快取與 partial:快取鍵仍是「樹上有的路徑排序後的 tuple」,每棵樹一份;partial 只多一個布林,不多佔記憶體;讀不出的檔不進 texts,沒有重複讀取,預算檢查(_read 回 False 回 None)保留。
引句:「+            texts = [self._text[p] for p in key if self._text[p] is not None]」

已看 _drift_list 認 64 碼:_DRIFT_LS_CACHE 與 _DRIFT_OID_CACHE 的上限 8 與同步清除邏輯沒動(file: `scripts/lumos:26541`);64 碼只讓 SHA-256 repo 進同一個有上限的快取,不改變上限,也不會讓非提交編號的字串進快取。
引句:「+    if not (isinstance(where, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", where)):」

已看拿掉 _drift_py_too_deep:3.14 以上 ast.parse 的深度失敗是可接的 MemoryError/RecursionError,except 已涵蓋;拿掉後不再對大檔多跑一次斷詞(省約 0.5 秒),沒有新增行程或迴圈。
引句:「except (SyntaxError, ValueError, MemoryError, RecursionError):」

已看 _drift_row_unread:每條判不了的行只走該行的條件與 bad_paths,成本是行數乘讀不出的檔數,且只在判不了分支呼叫,不在熱路徑;沒有新的 git 行程、沒有繞過預算。
引句:「+                    out.update(q for q in t.bad_paths() if (q == path if path else _drift_probe_code_path(q)))」

最嚴重等級 clean,blocking 共 0 條。
