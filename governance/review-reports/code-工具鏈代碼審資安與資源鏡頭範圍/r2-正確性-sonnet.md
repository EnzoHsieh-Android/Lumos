severity: minor

只有一條 minor finding:計劃筆記做法 10 還留著舊的 `loop next` 輸出字串,跟範本不一致。其餘修補我讀過、也實跑過,沒有改壞上一輪對的東西。我在乾淨 clone 的 2afc3177 上跑了三組測試。`-k lens_scope`(76 項)、`-k loop_next`(125 項)、`-k templates`(124 項)全部通過,另外 `-k toolchain` 和 `-k rm_literal` 也過。全套測試沒跑(超過 2 分鐘上限)。

severity: minor
blocking: 否 — 只是計劃筆記裡一句過期引文;現行指令來源是範本與產品碼,沒有測試會因它而紅,也不會讓人照錯的字串操作
引句:「工具鏈本 repo(`loop next` 印了『鏡頭範圍: 工具鏈本 repo』;跨 repo 派工時看被審 repo 的根)派工時」
問題:這輪把 `loop next` 那一行改成「鏡頭範圍: 帳本所在 repo 是工具鏈本 repo——被審分支也在這個 repo 時……」。範本 §3 須知同步改成「印了『鏡頭範圍』那一行」,測試⑤也改成斷言 `『鏡頭範圍』那一行`。但計劃做法 10 的引文沒跟著改,仍是舊字串「鏡頭範圍: 工具鏈本 repo」。那個字串現在在程式輸出、範本、測試三處都已不存在。同一篇計劃的做法 5、S1 和範本裡的同一句都已同步。同一篇的做法 1 還留著舊說法「不補測試」,計劃第 228 行有交代「原文不追改,以範本為準」,所以那條算有意保留。做法 10 這處沒有同樣的交代。
具體失敗情境:下一個 session 依計劃做法 10 把 §3 須知逐字比對或重建,拿「印了『鏡頭範圍: 工具鏈本 repo』」去 grep `loop next` 輸出,會 0 筆,誤判成工具鏈判別失效,或把範本改回舊字串。測試⑤只對範本字串斷言,不會抓到計劃的漂移。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:160`,對照 file: `skills/lumos-design-loop/templates.md:142`

已讀,無 finding:
- **消費專案輸出逐字不變**:`scripts/lumos` 只改了一個常數字串,判別邏輯沒動。`t_loop_next_lens_scope_toolchain_vs_consumer` 的⑤(拿掉那一行後兩份輸出完全相同、退出碼相同)仍綠,JSON 的 `lens_scope` 欄位不變。
- **〈消費專案六類〉原文**:`_SEC_SIX_CLASSES_ORIG` 比對通過,圍欄裡的「不報」DoS 句還原為原句,「工具鏈」字樣只留在填空裡,測試③③b 通過。
- **三邊字串一致**:`scripts/lumos:16154`、`scripts/test_lumos.py:96400` 的 `_LENS_SCOPE_LINE`、計劃做法 5 與 S1、pitfalls-code-loop 筆記四處的 `loop next` 那一行完全一致。
- **新測試與守衛**:
  - `.is_file()` 對應的「SKILL.md 是目錄」情境若改成 `exists()` 就會紅。
  - 壞符號連結、`--repo` 不存在兩種情境對 `is_file`/`exists` 都不辨別,只釘現況,不是缺陷。
  - 刪檔規則測試加了 §3.1 與 §9 兩份派工詞,標籤數、前置斷言和各自的變異點名都成立。
  - 工具鏈三類與範圍外的逐句斷言字串都能在範本裡找到。
- **範本說法對得上程式**:
  - 判別只看根目錄那一支一般檔。帳本根沒有 `.git` 時,`_vault_repo_root` 退回 `vault.parent`,判成消費專案,方向是多審,跟範本寫的一致。
  - `--finding-kind` 有給就要求每條發現各標一個,缺漏會被擋,對得上。
  - 修正關卡在有 `finding_kinds` 時只看 code 類,process 類免填修正紀錄,對得上。
- **anchor-baseline**:登記的 `scripts/test_lumos.py` 雜湊與 2afc3177 的檔案相符。
- **暫存**:測試的暫存目錄由測試跑道自己清,沒有殘留。我的臨時 clone 已刪。

最高等級 minor,blocking 0 條。
