severity: minor

# r3fix 驗收:合約與圖譜一致鏡頭

立場:三個月後接手的人,預設文件與現實對不上,逐句拿程式與測試核。

## 已核對、對得上的(摘要)

- 四篇筆記的每句規則逐句對過 `scripts/lumos`:值判準(字元集、200 字、反引號包裹)、`_NODEHOME_TAG_NAME_RE` 單一識別字、test-gone 要是上一版綁著的 test、比對去平台前綴、空白規則(前有正文且後接空白或行尾連前空白一起拿、前只有縮排改拿後空白、前有空白後緊接字就留)、整行不算與多出空行不算、核取方塊保留(`_NOTELINES_BARE_LIST_RE` 本身會吃 `- [ ]`,靠 `"[" not in line` 擋住,筆記說法與程式一致)、`_ns_tr_guard` 不豁免、提交前 tip=None 只查工作目錄索引、判定用到才建且只建一次。全部與程式一致。
- 條款對格(`scripts/test_lumos.py`):
  - S1 在 `t_nodehome_test_tag_only_edit_is_not_write_back`:換新名 ①、逗號清單與大寫鍵全形冒號與刪綁定 ②、test-gone ③ 與帶前綴 ⑤d、測試改名 ⑨、散文字 ⑥、指不到真測試(英文句子、不存在名稱、反引號英文句子)④、test-gone 非上一版綁過 ⑤、非識別字形狀四種 ⑤b、@ 後非提交編號 ⑤c、中文值 ⑦、空 `[test:]` ⑧、行內程式碼舉例 ⑪。
  - S2 在 `t_nodehome_diff_test_tag_only_edit_is_not_write_back` ①②。
  - S3 在第一支的 ⑩。
  - S4 在 `t_nodehome_test_tag_strip_edges`:跨三行 ①、落單反引號 ②、圍欄 ③、別欄位值 ④、單獨成行 ⑤(夾空行 ⑪)、參數化 ⑥、空白值 ⑦、反引號中文 ⑧、超 200 ⑨、沒收尾 ⑩、全形與縮排 ⑫、插在兩字中間 ⑫b、核取方塊 ⑫c、縮排 ⑬、圍欄空行 ⑭、CRLF ⑮。
  - S5 在 `t_slot_parse_unchanged_after_scan_refactor`。
  - S6 在 `t_nodehome_tag_only_new_names_must_be_real_tests`:①②③ 合約行假綁定、④ 真測試、④b 未提交測試改動、⑤ 非簽出版本。
- 實跑:`-k test_tag` 39 passed、`-k scan_refactor` 2 passed、`-k tag_only` 28 passed、0 failed。
- 綁的 `[test:]` 名稱 11 個(四篇與每支檔有家_計劃相關)逐一 `grep '^def'` 都恰存在一次;全圖譜 grep 沒有綁到舊名(`_nodehome_tag_exempt` 與舊測試名零命中)。
- TEST 計數:`grep -c '^def t_nodehome_'` = 61、`t_doctor_nodehome_` = 5,與筆記一致。
- `lumos lint Projects/只換測試綁定不算寫說明_計劃` 0 問題;`lint Systems/每支檔有家` 0 問題;`doctor` 圖譜健康 0 issues(662 篇;另有的提醒段落不屬本案);`contracts Systems/每支檔有家` 回「沒有登記任何合約」。
- 其他筆記:`Projects/每支檔有家_計劃.md` 的內容有變定義、S12、誤擋三處已補例外;`Systems/補新語言SOP.md`、`Projects/漂移防治路線圖_計劃.md`、`Verification/2026-09-11_每支檔有家落地.md` 提到的是歷史事件或不同情境,沒有因這輪變成假話。`Projects/交接2026-10-03_計劃.md` 的 D2 條目與 REVISIT:2026-10-15 還沒標完成,但計劃〈做法〉5 明寫上線後才關,目前不是假話(上線後要記得關)。

## Findings

severity: minor
blocking: 否 + 判準:筆記字面比程式窄或鬆但程式方向是更保守(多擋不少擋),沒有放過說明的路,不影響合約判定。
問題:筆記把「`@` 後面只認提交編號」寫在 test-gone 那一句裡,程式其實對兩種鍵的每個值都套(`_nodehome_test_tag_value_ok` 不看鍵),且正則只收小寫十六進位。後果:`[test:類別@x]` 這種值不會被拿掉(換名或刪除都算內容有變),`[test-gone:x@1A2B3C4]` 大寫提交編號也不豁免。方向是誤擋,不是漏放,但三個月後的人照筆記讀會以為只管 test-gone、大小寫都行。測試也沒有覆蓋 `[test:]` 帶 @、大寫編號這兩格。
引句:「`@` 後面只認 7 到 40 碼十六進位的提交編號」
引句:「_NODEHOME_COMMIT_RE = re.compile(r"[0-9a-f]{7,40}")」
file: `/Users/enzo/harness/lumos-rtb3/scripts/lumos:26901`

severity: minor
blocking: 否 + 判準:測試格與條款字面對得上但該格把多個情境併成一個斷言,翻紅力度比條款顯示的弱,不影響現行行為正確性。
問題:[S4] 條款把「標記在行首、前面是全形空白、在縮排後面」列為回 0 的三種寫法,測試 ⑫ 把三處修改塞進同一次 try_body、一個 check。任一處壞掉會紅,但三處之中壞兩處互相抵銷或哪一處壞了看不出;另外 tab 當前空白(筆記與 `_SLOT_STRIP_WS` 都寫了 tab)完全沒有測試格。
引句:「⑫標記在行首、前面是全形空白、在縮排後面 → rc0」
file: `/Users/enzo/harness/lumos-rtb3/scripts/test_lumos.py:47139`

## clean 面的證據引句

引句:「新的 `[test:]` 名稱要是單一識別字(可帶平台前綴;帶點號、::、#、空白的不豁免」——對照 `_NODEHOME_TAG_NAME_RE` 與測試 ⑤b,一致。

總結:全份最高等級 minor
