severity: major

以下先答鏡頭要的逐項回滾結果,再列 finding。

回滾逐項(程式碼查證):
- **撤一列**:型錄、規則 id、樣本 HIT/MISS 標記、`已撤列號:` 四處要同動,漏任一處 check.py 與 `choice_tables` 都報「表壞」。`_choice_tables` 回傳原因後,`_choice_push_scan` 對有 Kotlin 改動的推送擋下(記 blocked「表壞」)。純文件推送不經這道,所以修復提交本身推得出去。退得掉。
- **撤作用域其中一列**:`不收(` 那行要加回被撤那列的原寫法。只有 S6 測試把關,check.py 不管這行。多列共用的樣本行(例 `// MISS C-38 C-39`)要改標記,否則 `choice_sample_mark_problems` 紅。
- **整批撤**:S5、S6 靠跳過條件不紅(見 rb1 的耦合例外)。範圍 3、4 的程式擴充留著,走不到,沒有風險。
- **撤到一半**:型錄撤了規則沒撤,或樣本檔刪了表裡還有列,都被 check.py 與既有 `t_choice_*`(含第一版 S23 的 `choice_sample_problems(...) == []`)抓到,紅是設計內的保護。真正的新洞在下面。
- **已記處置外溢**:`_choice_kill_pick` 對 killed、waived 的行直接 `done`、不重跑。`_choice_waived_keys` 的鍵只有 `choice:<檔>:<行指紋>`,不含列號。外溢範圍是同行之後挑到的任何壞法(見 rb2、rb3)。

## rb1 第三批 S7 把 choice-batch2.kt 釘進常數,第二批單列撤除從此會讓測試紅
severity: major
blocking: 是——第二批〈回退〉原本不碰 test_lumos.py,第三批新增的釘值使它必須改測試並先簽章,屬回滾路徑被新增段落破壞。
- spec 段落:範圍 4「第三批的 S7 要另把 `samples/choice-batch2.kt` 一起釘住」;S7 條款「只含第一、二批語法的既有樣本行 應 挑出跟加入前相同的壞法」。
- 查證:現有 `t_choice_points_batch2_stable` 的 `names` 只列 `arid.kt`、`chain.kt`、`choice.kt`、`error.kt`、`multibyte.kt`、`nested.kt`。測試還用 regex `\?\.|\?:|\blet\b|combine|LaunchedEffect|remember` 把第二批語法行排除在釘值之外。這是第二批刻意讓「撤第二批單列」不碰測試的設計。第三批要求釘 choice-batch2.kt,等於把這批被排除的第二批語法行釘進常數,釘值內含 `(檔, 行, 列, 樣板, new_sha)`。
- 失敗場景:第三批上線後,第二批 REVISIT 與第三批同日重看(2027-01-21)。依第二批〈回退〉第 1 項撤 C-3x 的任一列,要拿掉 choice-batch2.kt 裡那列的標記行,並讓該行挑到的列改變。第三批 S7 釘住的 (行號, 列, new_sha) 對不上,`t_choice_points_batch3_stable` 紅。紅的是 test_lumos.py 裡的測試,改它要先簽章。spec 的〈回退〉第 2、3 項都沒提這個耦合。
- file: `scripts/test_lumos.py:146596`、`scripts/test_lumos.py:146641`

引句:「第三批的 S7 要另把 `samples/choice-batch2.kt` 一起釘住」

## rb2 〈回退〉第 3 項指的「放行清單」不存在,「重看」也沒有可執行的出口,且只列放行漏列殺掉外溢
severity: major
blocking: 是——回退步驟指向一個程式不會印的輸出,而且就算列出來也沒有指令能把放行作廢。
- spec 段落:〈回退〉第 3 項「撤列提交時把那一列有放行的行列出來(`gov --stats` 依列號那段的放行清單),要不要重看由人決定」。
- 查證一:`_render_gov_choice` 的依列號段每列只印 `壞法 N、殺掉 N、存活 N、跑不出結果 N;放行 {標籤 數}`,只有計數,沒有 (檔, 行) 清單。
- 查證二:`lint-waive --list` 印的是放行檔的 key、file、rule、reason,不印列號。列號只存在治理帳的 `waived` 事件(欄位 `row`)裡。
- 查證三:程式裡沒有取消放行的指令(grep 無 unwaive、revoke 類的 lint-waive 子命令)。`_choice_disposition` 對 waived 一律優先於其他狀態,所以「重看」只能手改放行檔。
- 查證四:第 3 項第一句說被殺掉與存活(守的測試沒變)也會外溢,但要列的只有放行。killed 外溢更隱蔽:`_choice_kill_pick` 對 killed 且測試仍被條款綁的行直接 `done`、不重跑。撤列後新挑到的別列壞法被當成已殺掉,從沒實跑過。
- 失敗場景:RETIRE-IF 因「等價」放行偏多而撤列。撤列提交裡照 spec 找不到要列的行,同行的新壞法繼承「等價」放行,永遠不再被問。
- file: `scripts/lumos:18007`、`scripts/lumos:42607`、`scripts/lumos:78045`、`scripts/lumos:78322`

引句:「撤列提交時把那一列有放行的行列出來(`gov --stats` 依列號那段的放行清單),要不要重看由人決定」

## rb3 上線方向的反向外溢讓第三批列的統計失真,RETIRE-IF 該撤的列會讀不到數
severity: minor
blocking: 否——只影響第三批自己的度量準度,不破壞回退本身。
- spec 段落:〈回退〉第 3 項只寫撤列方向的外溢;RETIRE-IF 與〈範圍 7〉的「每列命中次數」。
- 查證:`_choice_disposition` 與 `_choice_kill_pick` 只看 (檔, 行指紋),不看列號。第三批上線前,第二批挑到的壞法已被放行或殺掉的行,上線後改挑第三批的列(例 `x.firstOrNull { … } ?: d`)。這時該行直接 `done`,不產生新的 choice-kill 事件,也不進依列號的壞法計數(`row_mut` 只由事件寫入)。
- 失敗場景:RETIRE-IF 要求「至少 5 個壞法」才判跑不出結果,「至少 5 筆放行」才判等價。重疊行越多,第三批列計到的壞法與放行越少,該撤的列因分母不足而不被撤。Verification 的「每列命中次數」也量不出這種被外溢吃掉的命中。spec 只在撤列方向承認外溢。
- file: `scripts/lumos:17943`、`scripts/lumos:78322`

引句:「被殺掉、放行、存活(守的測試沒變)的紀錄,都會外溢給同一行之後挑到的別列壞法」

## rb4 整批撤的清單漏掉本計劃自己新增的文件改動
severity: minor
blocking: 否——不會讓閘紅,只是留下與型錄不符的說明,下一個人照字面讀會被誤導。
- spec 段落:〈回退〉第 2 項只列 `about_code` 與「第三批那條 WHY 行」。
- 查證:範圍 1 說明段同步另外改了「錨點從六種改成七種」「API 列是換成的方法名」改寫、〈統計〉列數。範圍 6 還新增了 Systems/規格閘 WHY「第三批的 RETIRE-IF 也讀這一段」、錨點列舉補「整個呼叫」、母計劃〈天花板〉第 1 條指向這份,以及 kotlin規則包正文那句改寫。
- 查證:目前 check.py 與測試沒有任何一處比對說明段的「六種/七種」與 `CHOICE_ANCHORS` 的數量。〈回退〉第 1 項(單列撤)也沒說要更新「第三批翻案」那一行。
- 失敗場景:整批撤後型錄仍寫「七種」與已不存在的第三批來源,規格閘 WHY 仍說第三批的 RETIRE-IF 讀依列號段,而那批列已沒了。這些筆記都是線索級,不會有機器擋。

引句:「改掉 Systems/kotlin規則包 的 `about_code`(拿掉 `choice-batch3.kt`)與第三批那條 WHY 行」

## rb5 「撤列後 batch2 測試不紅」的條款綁在不相干的測試上
severity: minor
blocking: 否——只是條款綁定錯位,不影響現行行為。
- spec 段落:S6 條款與預期值表 S6 第四列(缺 HIT 時 `t_choice_samples_batch3` 紅、`t_choice_samples_batch2` 不紅)。
- 查證:S6 綁的是 `t_choice_table_batch3`,但條款描述的是 `t_choice_samples_batch2` 該只看 C-32 到 C-37,以及它不會被第三批缺口弄紅。`t_choice_table_batch3` 不可能驗這件事。
- 失敗場景:日後有人把 batch2 的篩選改回「不在 C-1 到 C-31」,第三批任何列缺 HIT 都會讓第二批測試紅,沒有任何綁定測試會翻紅。這正是回退保護(撤列或缺口不外溢到別批測試)的唯一承載條款。

引句:「`t_choice_samples_batch2` 應 只看 C-32 到 C-37 [test:t_choice_table_batch3]」

## rb6 REVISIT 日期早於 RETIRE-IF 的兩個月起算點
severity: minor
blocking: 否——只是提醒提早響,決策仍可延後。
- spec 段落:RETIRE-IF「上線日(寫進第三批的 Verification)起滿兩個月」;REVISIT:2027-01-21。
- 查證:計劃寫於 2026-11-21,今天是 2026-11-22,仍在設計審 r2,之後還有實作、簽章與範圍 7 實測才上線。上線日必然晚於 2026-11-21,2027-01-21 一定不滿兩個月。
- 失敗場景:doctor 在 2027-01-21 唸這條回頭提醒,依列號的數據還不夠兩個月。人依提醒決定留列或撤列,等於用不足的樣本判回退。

引句:「REVISIT:2027-01-21 第三批上線滿兩個月前後,連同第二批的 REVISIT 一起看第三批各列的殺掉率」

實務隱患鏡頭(本功能碰的風險類):
- **併發與交易**:範圍外,單人單機依序操作。
- **金流與對外送出**:無,只改型錄、規則與壞法產生程式,掃描在本機。
- **不可逆**:治理帳逐筆追加、撤列不改舊帳,是 rb2、rb3 外溢的來源。此外 `已撤列號:` 守住列號不重用(`_choice_retired_problems` 查過會擋)。
- **守衛面**:所有 Kotlin 推送被「表壞」擋住的路徑已確認存在,spec 的〈回退〉要一次做齊並先跑 check.py 與實際行為一致。

圖譜節點:
- **Systems/kotlin規則包**:不影響。其 WHY 與 about_code 只需照 rb4 同步,沒有合約行會被破壞。
- **Systems/規格閘**:不影響其 WHY「有效處置以 (檔, 行指紋) 為鍵」與「放行不存行號」這兩條,本設計沿用而不改。但 rb2、rb3 顯示該 WHY 的外溢取捨在撤列與上線兩個方向都放大,第三批的〈回退〉第 3 項說法要依程式現況改正。

臨時目錄:本席未建立任何臨時目錄,無需刪除。

總結:最高嚴重度 major,blocking 共 2 條
