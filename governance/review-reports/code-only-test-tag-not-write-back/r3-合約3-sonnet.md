severity: minor

# 第 3 輪 合約與圖譜一致 審查

## 核對結論(逐項)

1. 四篇這次寫的句子逐句對程式:豁免條件(sig_t 一樣、新 `[test:]` 要 judge 回 yes、新 `[test-gone:]` 要是上一版 `[test:]`、拿掉不核對)、判定不可靠(judge 為 None 或 `_ns_tr_guard` 有回原因)就不豁免、空白規則(前有正文連前面空白拿,前只有縮排拿後面)、sig/sig_t/tag_names 的定義,全部對得上 `scripts/lumos` 的 `_nodehome_tag_only_change`、`_nodehome_tag_judge`、`_nodehome_strip_test_tags`、`_slot_strip_keys`、`_nodehome_parse_note`。值判準字元集與 200 字上限與計劃〈範圍〉第三條一致。判定器只在某篇 sig 不同、sig_t 相同、且有新 `[test:]` 名稱時才建,一次執行最多建一次(`_tj` 快取連 None 也快取),跟〈實務隱患〉效能一句一致。
2. 設計的測試格逐一對到實際測試:S1 對 t_nodehome_test_tag_only_edit_is_not_write_back ①~⑪、S2 對 t_nodehome_diff_test_tag_only_edit_is_not_write_back ①②、S4 對 t_nodehome_test_tag_strip_edges ①~⑮、S5 對 t_slot_parse_unchanged_after_scan_refactor、S6 對 t_nodehome_tag_only_new_names_must_be_real_tests ①~⑤,情境與計劃字句一致。我跑了 `-k test_tag`(30 passed)與 `-k scan_refactor`(2 passed)。
3. 筆記內綁的 `[test:]` 全部存在(上列加 t_nodehome_route_content_change_definition、t_nodehome_decisions_compared_by_value、t_nodehome_diff_route_per_commit、t_nodehome_diff_route_counts_content_per_commit、t_nodehome_gate_switch、t_nodehome_config_disk_read_skips_symlink 各 1 支)。舊名 t_nodehome_tag_exempt_hidden_sentence_caught_by_test_refs 在 repo 內只剩 0 處綁定(全圖譜與 scripts grep 無),`_nodehome_tag_exempt` 只出現在計劃〈審計修正紀錄〉的歷史敘述,有標明已刪。`t_nodehome_*` 61 支、`t_doctor_nodehome_*` 5 支與 TEST 行的機械數一致。
4. `lumos contracts Systems/每支檔有家`、`Systems/筆記內容閘` 都回「沒有登記任何合約」,無合約被動到;`lumos lint Projects/只換測試綁定不算寫說明_計劃` 0 問題;`lumos doctor` 圖譜健康 0 issues(其餘為既有提醒,N 段 11 個數字、P 段 43 條、Y 段 `OpenAsync` 都與本案無關)。
5. 其他筆記 grep「內容有變」「唯一合法」「簿記」「tag_exempt」「sig_t」:其他 Projects/Systems 沒有因這輪變成假話的講法;每支檔有家_計劃 的 S11 與 d 欄位「內容有變」用法仍成立。

引句(clean 部分):「只換、加、刪測試綁定也不算(2026-10-05 起;新出現的名稱要指得到真測試,見上面那行 WHY)」——對得上 `scripts/lumos` 的 `_nodehome_tag_only_change` 與兩處呼叫點。

## Findings

severity: minor
blocking: 否 + 不影響閘的判定行為,只是計劃筆記裡兩處陳述已被 r2 的改法取代、沒標過期;未造成誤擋或漏擋。
引句:「就把可拿掉的值收窄成「這個 repo 裡找得到的測試名」」
file: `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:27`
說明:RETIRE-IF 的收窄動作(新 `[test:]` 名稱要指得到真測試)r2 之後已經實作成 `_nodehome_tag_only_change` 的 judge 核對,這條撤除條件第一半寫的是已經做完的事。三個月後的人讀到會以為「有人藏句子就要再收窄」是待辦,其實剩下的洞只有〈天花板〉1(句子剛好是真測試名)。

severity: minor
blocking: 否 + 只影響後人重做翻紅驗證時的對照,不影響現行測試與閘。
引句:「拿掉值判準 → [S1] ⑥⑦ 與 [S4] ⑦⑧⑨ 紅」
file: `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:89`
說明:這是 r2 之前的實作紀錄,r2 加了真測試核對後對照已失效:現行 [S1] ⑥ 是「換綁定同時改一個散文字」,跟值判準無關;[S4] ⑧(反引號中文)、⑨(201 個 a)就算拿掉值判準,拿掉的名稱也過不了 judge,照樣 rc1,不會翻紅。同一段的「五條驗收測試」「265/267/198 條全綠」也是當時的數,現在有 S1~S6。該段沒標「r2 前」。要驗值判準守不守得住,現在只有 [S4] ⑦(只有空白的值)會紅。

severity: minor
blocking: 否 + 屬綁定覆蓋缺口,行為本身(`_ns_tr_guard` 的既有路徑)程式碼上成立,只是這條新用法沒有測試釘。
引句:「簽出的不是終點、工作目錄有沒提交的測試或設定改動就不豁免」
file: `scripts/lumos:30001`
說明:Systems/每支檔有家 的 WHY 綁了 t_nodehome_tag_only_new_names_must_be_real_tests,但該測試 ⑤ 只釘「簽出的不是終點」;「工作目錄有沒提交的測試或設定改動」這半句在本案的呼叫路徑(`_nodehome_tag_judge`)沒有任何測試守,拿掉 `_ns_tr_guard` 呼叫只有 ⑤ 會紅、這半句本身沒有獨立測試。此外這句在提交前路徑(tip=None)不適用(不呼叫 guard),句子緊接「推送時再到終點版本找」所以讀得出是推送限定,但沒有明寫。⚠ 這半句在原筆記測試綁定要存在那邊的測試是否間接守到,我沒逐一核對。

總結:全份最高等級 minor
