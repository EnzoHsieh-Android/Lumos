severity: minor

# 合約與圖譜一致鏡頭 r1(code-only-test-tag-not-write-back)

固定席:派工說明本次沒附固定席節點(鏡頭計算超時),未補算。自己跑 contracts 補查:
- `lumos contracts Systems/每支檔有家`、`lumos contracts Systems/筆記內容閘` 皆回「這篇沒有登記任何動了會壞的合約」,兩篇都沒有 ★INVARIANT★,本次改動沒有合約語意被改。
- 兩篇 `lumos lint` 都 0 問題。
- 實跑 `-k test_tag`、`-k slot_parse`、`-k nodehome`:265 passed, 0 failed(新三支測試與既有 t_nodehome_* 含 route_content_change_definition 都綠)。

逐句核對結論:
- 筆記內容閘 WHY 的「slot_parse 與新的 _slot_strip_keys 都走 _slot_scan」與程式一致。
- 每支檔有家 WHY 的「提交前與推送前共用同一個 sig」:兩邊都經 `_nodehome_parse_note` 的 sig(scripts/lumos:27301 逐提交、27397 提交前),屬實。
- 「拿掉後只剩清單符號的行整行不算」「圍欄、行內程式碼、別的欄位值裡的不拿」「中文、空白、超過 200 字、跨行不拿」都與程式一致。
- 兩行改過的現況句(KEY 推送前逐提交、KEY node_home.gate)與程式一致。

## F1
severity: minor
blocking: 否 + 只是脈絡文字漂移,不影響閘的行為,也沒有綁定測試被改語意
被改行為後變假的舊講法:每支檔有家_計劃對「內容有變」的定義沒跟著改。
引句:「+  KEY:推送前逐提交看寫回:改程式的那個提交裡、那篇的內容(摘要、決策、正文)是在這個提交改的才算寫回」
file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:97`(「內容有變:摘要、決策、正文三者任一不同…其他開頭欄位…的變動算簿記」)與 `:123`([S12],綁 t_nodehome_route_content_change_definition)。
現在摘要與正文先拿掉測試綁定標記才比,這兩處沒提例外。計劃屬歷史設計文件,但 [S12] 的條款字面與現況不符;三個月後的人讀 [S12] 會以為換 [test:] 也算內容有變。對照:程式 `_nodehome_parse_note` 的 sig 已改。修法是在 [S12] 末尾補一句指到新計劃。

## F2
severity: minor
blocking: 否 + 只是描述精確度,行為與測試都對
筆記內容閘 WHY 對 `_slot_strip_keys` 的描述與程式有一處不符。
引句:「新的 `_slot_strip_keys`(拿掉指定鍵的欄位、其他字原樣)」
程式實際會連同標記前面的半形空白與 tab 一起拿掉(`out[-1] = out[-1].rstrip(" \t")`,見 diff 的 `_slot_strip_keys`,其 docstring 寫得對)。例:`x [test:a] y` 拿掉後是 `x y`,不是 `x  y`。對 sig 比對沒有害處,但筆記說「其他字原樣」是假話。

## F3
severity: minor
blocking: 否 + 守衛強度的落差,不是現有行為錯誤
筆記內容閘 WHY 的核心句「掃描規則只有一份」綁的測試只守到一半。
引句:「[test:t_slot_parse_unchanged_after_scan_refactor]」
該測試只比 slot_parse 輸出跟舊實作一致;`_slot_strip_keys` 若改回自己另寫掃描器,這支不會紅(只有 t_nodehome_test_tag_strip_edges 的邊界案例可能抓到,但它沒綁在這篇)。把 t_nodehome_test_tag_strip_edges 也掛到那條 WHY,或在行文裡說清楚這條測試只守 slot_parse 不變。

## F4
severity: minor
blocking: 否 + 舊帳漂移加上本次未補綁
每支檔有家新改的兩行現況句只綁舊測試,新行為的測試只綁在 WHY 那一行;另外 TEST 計數行仍寫舊數字。
引句:「只換、加、刪測試綁定標記也不算(2026-10-05 起)」
該行綁的是 t_nodehome_diff_route_per_commit 與 t_nodehome_diff_route_counts_content_per_commit,不含 t_nodehome_diff_test_tag_only_edit_is_not_write_back(只在 WHY 行綁)。node_home.gate 那行同理。TEST 行「t_nodehome_* 42 支」,實數 `grep -c "^def t_nodehome_" scripts/test_lumos.py` 為 60(本次加 2、舊帳早已漂移 16),file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:40`。

## 其他筆記掃描
grep 「內容有變」「寫回」「唯一合法」「簿記」「sig」:Systems 底下其他「簿記」都是治理帳白名單意義,無關;「唯一合法」只在每支檔有家 node_home.gate 那行(已改)。唯一漂移是 F1。

總結:全份最高等級 minor
