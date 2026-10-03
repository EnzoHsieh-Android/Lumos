severity: minor

**S1 開頭欄位淨差異表仍以 NFC 當鍵,同名撞鍵沒套 r1 的整組不配**
severity: minor
blocking: 否 — 縱深防禦,要同時送兩個 NFC/NFD 同名篇,且只影響開頭欄位其他欄的新寫判定
引句:「self._m = {} if dn is None else {nfc(q): {n for n, _t in rows} for q, rows in _notelines_parse_added(dn).items()}」
1. file: `scripts/lumos:27528`。這是 diff 的上下文行,r1 的 `_ns_append_nfc_clash` 沒蓋到它。
2. 誰、從哪裡:筆記作者在同一次推送送出兩篇 NFC 與 NFD 寫法不同的同名筆記 A 和 B。
3. 送什麼:字典推導式遇到同一個 NFC 鍵時,後來的覆蓋先來的。A 的「淨新增行號集合」被 B 的取代。
4. 拿到什麼:A 開頭欄位其他欄的新寫行,若行號不在 B 的集合裡,就被當成舊行而漏查。
5. 我沒有實際重現。依據是讀碼:`net.lines(nfc(p))` 取值,見 `scripts/lumos:27493`。
6. 修法:把 `_ns_append_nfc_clash` 的結果也套到這張表,或在撞鍵時回空集合並讓 `failed` 為真,這樣就整次照嚴格查。

**S2 申訴不分範圍:只判句尾的申訴可以換掉同編號的整行重判定**
severity: minor
blocking: 否 — 推論,威脅模型明寫「只防疏忽、不防存心繞過」,且作者本來就能自己寫判定檔
引句:「k = (d["disputes"], r["id"])」
1. 同一內容編號可能在不同範圍下各有判定:整行的 `(id, None)` 和只判句尾的 `(id, tail)`。
2. `_note_audit_fold_scoped` 的 `c = disputes.get((name, r["id"]), c)` 會把被指名檔案裡同編號的每種範圍都換成申訴結果,不管輕重。
3. 路徑:用較新的起點範圍 prepare,舊句已存在,項目變成只判句尾,申訴判成 CONTEXT。這份申訴指名一份舊的整行 CODE 判定檔。同一個編號在整行範圍的 CODE 就被換成 CONTEXT,沒有來源對、上下文不變的核對。
4. 寫不出具體的外部攻擊者,只有筆記作者自己。所以標推論。
5. 補強:申訴要換掉整行判定時,要求申訴那一列的範圍(tail)跟被換的那一列一致,或只准往重的方向換。

**已看,無**
- **1 不可信輸入流到危險操作**
  - `_ns_relaxed_seen` 的 `LUMOS_PUSH_ATTEMPT` 只進 sha256,記號檔名固定是 `lumos-relaxed-seen`,放在 `rev-parse --absolute-git-dir` 回的目錄,沒有路徑注入。
  - 批次讀的規格是 `f"{tip_spec}:{b}"` 或 `f"{base_where}:{b}"`。`b` 來自 diff,必須以 `.md` 結尾,且在 vault_rel 底下,所以不會以 `/` 或 `0:` 開頭而變成別的物件。含換行的路徑會在 `_nodehome_cat_blobs` 被整批拒掉,對應 `scripts/lumos:26511`。
  - 去重是寫記號在先、記帳在後。記帳寫失敗時同一次推送的重試不再記,只是少記帳,不是洞。
- **2 繞過守衛**
  - r1 的 NFC/NFD 撞名在配對表(`_notelines_append_pairs`)這條路上修好了,S1 是漏掉的另一處同形狀。
  - 大小寫不同的路徑鍵本來就不同,不撞。改名被 `a != b` 排除。符號連結、子模組(`.md` 結尾的 gitlink)不會讓一篇的舊行扣到另一篇。
  - 「現況描述沒寫來源」永遠不扣,借舊行的債帶過新的現況句這條路堵住了。「程式行號引用」「釘版本不合法」以片段為鍵,舊行的債不能換成新的行號引用。其他整行規則照規則名計數,最多抵銷數量相同的同名違規,不能放行新增的種類。
  - `tail` 欄要 16 碼十六進位。內容編號涵蓋整行文字,所以換一段尾巴就是新編號,判定蓋不到。
- **3 提示注入**
  - 範本新段說「規則 6 仍適用整個條目,含舊句」。這比 r1 前更嚴:舊句裡對判定者說話的文字,現在也會被標 CODE。
  - 清單多印的「舊句」「只判這次補在句尾的」兩行來自筆記原文,屬同一個不可信面,已被規則 6 蓋住。
- **4 密鑰與個資、執行邊界**
  - 記號檔只含 16 碼雜湊。
  - 治理帳新欄位 `pairs`、`rules` 是路徑與規則名,`_gate_event_fit` 把整行壓在 4096 位元組內。
  - 新的擋下訊息只印常數與上限,沒印使用者內容。
- **5 加密與傳輸、行動端**:已看,無。

**固定席節點**
- `reversibility-governance-ledger`、`pitfalls-code-loop`:只多了一種 `relaxed` 事件和一個去重記號檔,不碰可逆性帳的欄位與寫入邏輯,不影響。
- `lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`測試假綠形態`、`design-loop`:diff 沒動這些節點宣稱的行為(search 過濾、綁定測試真跑、kill 的 rc、授權白名單、還原翻紅釘、處置閘),不影響。

最高嚴重度 minor,blocking 0 條
