severity: minor

# 第 2 輪 合約與圖譜一致 審查報告

做法:逐句拿 `scripts/lumos` 與 `scripts/test_lumos.py` 對筆記;合約用 lumos contracts 查;第 2 項的測試我沒能跑(沙盒擋了測試執行),只確認八支綁定測試名都各有一支定義,效力靠讀碼判斷。

## 逐句核對結果(對的)

- TEST 支數:`grep -c '^def t_nodehome_' scripts/test_lumos.py` 得 61,`t_doctor_nodehome_` 得 5,與筆記「61 支、5 支」一致。
引句:「t_nodehome_* 61 支、t_doctor_nodehome_* 5 支」
- 「豁免什麼時候開」:`_nodehome_tag_exempt` 取 `_note_shape_config` 的總開關再丟 `_ns_test_refs_mode(gate, cfg_text, False)`,回 block 才開。總開關 warn/off 或 test_refs 為 warn/off/沒設都不開,與筆記「總開關與 test_refs 都是 block」一致。程式預設 test_refs 是 warn,所以「沒設就不開」成立。本 repo 的 `.lumos/config.json` 確有 `note_shape.test_refs: block`。
- 「sig 與 sig_t」:`_nodehome_parse_note` 兩個鍵並存,兩處比對(提交前 `_nodehome_evaluate`、推送前 `_nodehome_mark_note_content`)都用同一個 `tag_exempt` 選鍵,只有一個入口(`cmd_home_check`)設它。說法屬實。
引句:「sig=(摘要, 解析後的決策, 正文)、sig_t=同上但拿掉測試綁定標記」
- 合約:contracts Systems/每支檔有家、Systems/筆記內容閘兩篇都回「沒有登記任何合約」,這輪沒動到合約。

## Finding 1
severity: minor
blocking: 否 — 只是筆記說法比程式實際保證寬,不是程式違反合約;程式與計劃〈天花板〉都已寫「判不了或被跳過」的大意。
問題:Systems/每支檔有家 的 WHY 與 KEY 把豁免說成「推送時會擋就開」,但 `_nodehome_tag_exempt` 只看設定,不看那道當次實際擋不擋。Projects/筆記測試綁定要存在_計劃〈做法〉5 與 [S16] 寫明:推送時目前簽出的提交不是推送終點、已追蹤測試檔或 `.lumos/config.json` 有沒提交的改動時,這組只提醒不擋;[S15] 的新測試檔、LUMOS_SKIP_NOTE_SHAPE=1(整道跳過)也一樣。這些情況豁免照開、核對沒擋,「單行英文說明包成 `[test:…]`」就放行。另外 INVARIANT 合約行上的測試名本來就不被那道驗存在(只由 Check T 與合約測試閘管),也是缺口。
引句:「專案的「筆記測試綁定要存在」推送時會擋(note_shape 總開關與 test_refs 都是 block,`_nodehome_tag_exempt`)時」
file: `docs/lumos-toolchain-knowledge/Projects/筆記測試綁定要存在_計劃.md:65`(〈做法〉5 保險)與 `:91`([S16])
與被讀那篇宣稱的行為有衝突:是「窄衝突」,不是「那道在所有推送都擋」。〈天花板〉1 的「那道判不了或被跳過」應點名這三種保險情況與 SKIP 環境變數,Systems 兩篇則應加一句「保險情況下那道只提醒,豁免仍開」。

## Finding 2
severity: minor
blocking: 否 — 守衛強度說法過頭,不影響行為正確。
問題:筆記內容閘 WHY 寫 `_slot_strip_keys` 會「連同欄位前面的半形空白與 tab」一起拿掉,並綁 `t_slot_parse_unchanged_after_scan_refactor`。該測試新增的比對是「兩邊都去掉所有空白後相等」,故意不看空白;而 `_nodehome_strip_test_tags` 之後本來就把每行空白壓平。所以刪掉 `out[-1].rstrip(" \t")` 那行,兩條路都不會紅,這句話沒有任何測試守。(我沒改檔做突變,是讀碼判斷;要確認請在 worktree 拿掉該行跑 `-k slot_parse_unchanged` 與 `-k test_tag`。)
引句:「連同欄位前面的半形空白與 tab;其他字原樣」
引句:「_slot_strip_keys 拿掉全部鍵後去掉空白 = slot_parse 的核心一句去掉空白」
file: `scripts/lumos:4195`(rstrip 那行)

## Finding 3
severity: minor
blocking: 否 — 不是這輪新增的假話,是這輪沒順手改到的鄰句。
問題:Projects/每支檔有家_計劃 只改了 [S12],沒動兩處相關句:定義段仍寫「其他開頭欄位…的變動算簿記」且說內容有變是「三者任一不同」(未提豁免,`:97`);〈誤擋〉處置寫「唯一的解法是把檔加進對的那篇」(`:193`),豁免開時多了「只換綁定」這條不用加檔的路。[S12] 的補句自己也只綁舊的兩支測試,新行為沒有條款綁新測試(守它的是 Systems 與新計劃那邊的綁定)。
引句:「簿記欄位的變動不算(2026-10-05 補:專案的筆記測試綁定要存在推送時會擋時」
file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:97` 與 `:193`

## 其他筆記掃描
grep 「內容有變」「唯一合法」「寫回落點」:Systems/每支檔有家 的 KEY 行 29、35 已同步改。Projects/推筆記認家_計劃 `:87` 的「越界唯一合法寫法是寫明文」講的是 regen 節點,與豁免無關,不算假話。沒有別篇的 sig 或 note_shape.test_refs 講法被這輪弄成假話。

## 綁定測試存在性
`t_nodehome_test_tag_only_edit_is_not_write_back`、`t_nodehome_diff_test_tag_only_edit_is_not_write_back`、`t_nodehome_test_tag_strip_edges`、`t_nodehome_tag_exempt_hidden_sentence_caught_by_test_refs`、`t_slot_parse_unchanged_after_scan_refactor`、`t_nodehome_gate_switch`、`t_nodehome_config_disk_read_skips_symlink`、`t_nodehome_route_content_change_definition`、`t_nodehome_decisions_compared_by_value` 各有一支定義。新測試對「設定是 warn、gate warn、沒設」三種都斷言 rc1,守到「豁免開關」那句;守不到的是 Finding 2 的空白句與 Finding 1 的保險情況。

總結:全份最高等級 minor
