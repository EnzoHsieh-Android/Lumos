severity: clean

**第 2 輪資安審查(R2S):沒有可利用的洞,0 條 finding。**

審了 `/tmp/code1-r2.patch` 全文,另查了 `scripts/lumos` 裡批次讀 git 內容的 `_nodehome_cat_blobs` 和終端消毒用的 `_esc_clean`。我只讀碼,沒有實際構造輸入重現。第 1 輪報告在 `governance/review-reports/code-筆記格子第1步/` 底下找不到,所以修法是對照 diff 本身驗的,不是對照 r1 報告。

**逐類結果**

1. **不可信輸入流到危險操作:已看,無。**
   - 本輪新增的 git 呼叫在 `_ns_base_summary_lines`,它把 `f"{base_where}:{p}"` 這種規格一次餵給 `git cat-file --batch`。
   - 這是 stdin 批次讀,不經 shell;argv 是固定的 `["git","-C",repo,"cat-file","--batch"]`。
   - 路徑 `p` 來自別人分支的檔名,但 `_nodehome_cat_blobs` 開頭已有 `if any("\n" in s_ ...)  return None`,檔名夾換行無法在批次輸入裡再塞一條規格。
   - `base_where` 是推送範圍的起點 sha 或 ref,不是檔案內容。
   - 路徑裡有 `:`、開頭是 `-` 或帶 `..` 時,只會讓規格讀不到(回 None),不會讀到別的物件。
   - 新增的 `_ns_vault_rel` 只是把原本兩處各寫的圖譜選取邏輯合成一處,輸出一定是 `docs/<slug>`,slug 來自已變更路徑。
   - 沒有 eval、反序列化、模板或 shell 插值。
2. **登入與權限:已看,無。** 這個工具沒有認證面。
3. **密鑰與個資:已看,無。**
   - 治理帳新增的 `check`、`slots_lines`、`slots_missing` 是整數和固定的格名。
   - `slots_missing` 的鍵來自 `slot_check_keyed` 回傳的程式內固定格名,不再用正則從訊息字樣反推,所以筆記內容不會流進帳本鍵。
   - 另一個已存在的欄位 `nodes` 帶節點路徑,這次沒改。
4. **加密與傳輸:已看,無。** 沒有網路呼叫。
5. **執行邊界:已看,無可利用項。**
   - 終端控制字元:本輪把筆記路徑補上 `_esc_clean`(S1 的修法):格子缺漏的回印行有清,doctor 列「繞過掃描」的那行路徑也補了清。
   - `_esc_clean` 同時清掉 C0、DEL 和 C1(0x7f 到 0x9f),所以 8 位元的 ESC 變體也擋得住。
   - 核心一句的回印本來就走 `_esc_clean`。
   - 掛鉤範本這次不帶 `--slots`。合併中直接 `return None` 跳過檢查,條件是 `MERGE_HEAD` 存在,而這需要本機寫 `.git` 才做得到,遠端的 PR 做不到。
   - `LUMOS_SKIP_NOTE_SHAPE` 逃生口仍會留帳,這次沒變弱。
   - 計劃筆記已把「讀被推送版本的 `note_shape.slots` 設定、可被同一提交關掉」列在天花板第 4 項(S2),這是已知的既有設計,不重報。
   - 「舊行」判定放寬(去空白、只放連結的鍵帶連結集合、`pre2` 收上線前的行、續行接回)只會讓更多行被當舊行而放行。要利用它需要先有一行已存在的缺格舊句,而計劃的天花板第 7 項已承認這一點。這只是少擋,攻擊者拿不到額外權限,屬格子規則的完整性,不是資安洞,不報。
6. **行動端:不適用。**
7. **新依賴:無。** 只用既有的 `subprocess` 和標準庫。

最高嚴重度 clean,blocking 0 條
