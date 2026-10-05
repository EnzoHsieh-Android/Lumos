# code r2 收貨紀錄(code-only-test-tag-not-write-back)

八席齊了才動工作目錄。report-normalize 八份都合格(派工詞先要求總結行不寫 severity,這輪沒有退件);quote-check 七份全錨,合約2 席 6 句錨不到 1 句(#6,引的是 Projects/每支檔有家_計劃 的 [S12] 補句——那篇在 r2-delta.patch 裡、不在 r2-snapshot.patch;編排者重現:`git show dbaa2fe1:docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md | grep -c` 原句 → 1,HIT(第一次誤用 81a4907c——那是補檔前、只有卷證的版本,回 0;改用補檔後的 dbaa2fe1));refcheck 全對得上。
圖譜鏡頭:同 r1,本機 main 不含範圍起點,hook 沒附;派工詞改成直接點名三篇相關筆記請席位讀。

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| g1 | 通才2 | blocker | 席附 probe.py 實跑:`[test-gone:一句英文]`(帶不帶 @提交、拆成多個)每支檔有家 rc0、筆記形狀擋 rc0;編排者寫成 t_nodehome_tag_only_new_names_must_be_real_tests ②③,在 dbaa2fe1(第一輪修正)版本、夾具加開 test_refs=block 讓豁免打開時紅 | HIT 採信,折:豁免自己核對,新的 test-gone 要是上一版綁過的 [test:] |
| x1 | 正確性2 F1 | major | 同 g1(rc0/rc0 對 rc0/rc1) | HIT 採信,折(同 g1) |
| y1 | 邊界2 F1 | major | 同 g1,另加合約行與條款行的 [test:] 那道直接放行(`_ns_tr_test_viol`);編排者寫成同一支測試 ①(合約行新寫 [test:英文句子]),在 dbaa2fe1 加開豁免時紅 | HIT 採信,折:新的 [test:] 名稱自己核對真測試(共用 _NsTrJudge) |
| z1 | 設定路徑 F1 | minor | 席附探針:設 LUMOS_SKIP_NOTE_SHAPE=1 時兩道一起放過 | HIT 採信,折:豁免不再看那道,跳過那道不影響 |
| z2 | 設定路徑 F2 | minor | 席附探針:推送終點不是簽出版本時那道降成提醒、豁免照開 | HIT 採信,折:判定不可靠(_ns_tr_guard)就不豁免,同一支測試 ⑤ |
| s1 | 資安 | minor | 同 z1、z2 的推論 | HIT 採信,折(同 z1、z2) |
| k1 | 合約2 F1 | minor | 同 z1、z2(筆記沒講那道會降級) | HIT 採信,折:筆記改寫豁免條件 |
| x2 | 正確性2 F2 | minor | 新格 [S4] ⑬(只改縮排)⑭(圍欄裡少一個空行)在 dbaa2fe1 加開豁免時回 0(紅) | HIT 採信,折:不再整行壓平 |
| y2 | 邊界2 F2 | minor | 同 x2 | HIT 採信,折(同 x2) |
| p1 | 規格符合2 多做 | minor | 空行收斂寫在圍欄判斷外,圍欄裡也收 | HIT 採信,折:只收拿掉標記行留下的那個空行(圍欄外) |
| x3 | 正確性2 F3 | minor | 新格 [S4] ⑮(整篇 CRLF)在 dbaa2fe1 加開豁免時回 1(紅,多出假的內容有變) | HIT 採信,折:sig_t 每行去尾端空白 |
| k2 | 合約2 F2 | minor | 「連同前面空白」沒測試守 | HIT 採信,折:[S4] ⑫ 涵蓋行首、縮排後、全形空白前三種 |
| k3 | 合約2 F3 | minor | Projects/每支檔有家_計劃 第 97 行與第 193 行沒跟著改,[S12] 補句沒綁新測試 | HIT 採信,折 |
| a1 | 架構對齊2 | minor | cfg 事後塞鍵、兩條傳法 | HIT 採信,折:整個設定耦合刪掉,兩處都用 tag_judge 參數 |

輪內有 blocker → accepted 一條都不帶;refuted 0。

翻紅方法更正:第一次拿 81a4907c 的主程式對照,但那個提交是補檔前的版本,主程式跟最原始的 718d32bd 一樣,對照無效;改用 dbaa2fe1,並在夾具暫加 note_shape.test_refs=block 讓第一輪版本的豁免打開——不加的話第一輪版本一律不豁免,該擋的格子會因為「本來就擋」而綠,證明不了新測試抓得到洞。
