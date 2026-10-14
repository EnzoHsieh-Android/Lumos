severity: minor

本輪修補的核心路徑我沒找到會擋推送的洞,只有三條 minor,都不阻擋。

我實跑了三件事:
- 在複本上做行雜湊、原文掃描兩個突變,相關測試都會紅。
- 在工作樹實跑 `python3.14 scripts/test_lumos.py -k nogo`,281 過、0 敗。
- 拿 282 份 Projects 計劃筆記,比對舊的剝行內標記掃描與新的原文掃描,只有 4 份從無命中變成有命中,誤判面小。

臨時目錄與 `gctl-run-*` 現場都已刪,工作樹沒動。

severity: minor
blocking: 否 — 只影響「改了什麼才算同一行」的精確度,不會放行危險內容
引句:「s = "".join(ch for ch in unicodedata.normalize("NFC", vis) if unicodedata.category(ch)[0] in "LN")」
問題:行雜湊把標點、符號(含 emoji)、組合附加符號(類別 M)、零寬字元全部丟掉,所以不同內容會算出同一個雜湊。
具體失敗情境:
- 實測 `- 不做 🚫 退款` 與 `- 不做 ✅ 退款` 雜湊相同。
- 實測 `refund -1` 與 `refund 1` 雜湊相同,負號被丟掉。
- 實測 `不做 退\u200b款` 與 `不做退款` 雜湊相同。
- 泰文 `ก็` 與 `ก` 雜湊相同(組合附加符號被篩掉);這在單人、只用中英文的威脅模型外。
- 影響只在「審過的被略過行」與「現在的被略過行」被判成同一份:輕量審或 major 的綁定會涵蓋到只差符號的改動。
- 這與設計意圖「改標點不算改」一致,不會讓危險詞漏過,但符號承載語意時(負號、否定記號)會被當成沒改。
- 佐證:`scripts/lumos:8097-8103`(`_nogo_line_key`),`scripts/test_lumos.py`(`t_nogo_line_key_normalized`)

severity: minor
blocking: 否 — 屬威脅模型外的既有繞法,本輪沒讓它變糟
引句:「m = rx.search(ln)」
問題:席名在 r7 改成先做 NFKC,但關鍵字掃描只做原文比對,不做 NFKC,也不去零寬字元。
具體失敗情境:
- 計劃寫 `ｐａｙｍｅｎｔ` 或 `退\u200b款`,門判風險低(實測 `_door_keyword_hits` 回空)。
- 全形英文、零寬字元就能繞過四類關鍵字。
- 原文掃描修了反引號與圍欄的盲區,沒處理這一類。
- 與威脅模型(單人、AI 依序操作)衝突程度低,所以只列 minor。
- 佐證:`scripts/lumos:8148`(`_door_keyword_hits`),`scripts/lumos:9322`(`_nogo_is_arch_seat`)

severity: minor
blocking: 否 — 屬已知取捨,但文件沒量化
引句:「_DOOR_SCAN_RAW = True   # 關鍵字掃描看每一行的原文」
問題:原文掃描讓行內程式碼與網址裡的英文識別字也算命中。
具體失敗情境:
- `\bprod\b`、`\bsend\b`、`\bmail\b` 會命中 `https://x/send/ok`、`/send/`、`--prod`,這些都實測會命中。
- `send_message` 因底線是字元而不命中。
- 提到 `.canary-log.jsonl`、路徑裡的 `payment` 的計劃會被判高風險。
- 實測 282 份計劃裡有 4 份由低轉高,例如 `canary`、`遷移`、`prod`。
- 門判定規則版本 5 一升,舊的風險低留痕若碰到這類內容,推送前會判過期,需要重跑規格閘。
- 方向是多擋,屬設計意圖;只是文件沒提到 URL 與路徑誤判。

已讀,無 finding:
- `_under_root`:與舊兩處寫法(`is_absolute() or root is None` 才直接用,否則接在 root 底下)行為等價。處置閘、`_nogo_review_unbound`、`_nogo_snapshot_rows` 三處沿用同一語意,絕對路徑、`..`、符號連結(`resolve` 在呼叫端)的行為與舊版一致。`_vault_repo_root` 不回 None。非字串路徑已在呼叫端以 `isinstance` 擋掉。
- `_nogo_skipped_rows` 自算時用 `skip=()` 加 `only=nogo`:已排除行只在實務隱患節、不做清單只在不做節,兩者不重疊,結果與 `_door_judge` 傳入的一致。
- 測試強度:
  - 行雜湊改成只去空白,`-k nogo_line_key` 變 6 敗。
  - 原文掃描改回剝行內標記,`-k door_scans_raw` 變 5 敗。
  - `_under_root` 沒有獨立測試,靠 `spec_path` 的相對路徑情境(`cmd_canary` 會轉成 repo 相對路徑)間接覆蓋;相對的快照路徑沒有測試。

最高等級 minor,blocking 0 條。
