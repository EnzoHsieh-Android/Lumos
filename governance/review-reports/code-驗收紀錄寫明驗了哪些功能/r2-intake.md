# code-驗收紀錄寫明驗了哪些功能 r2 收貨紀錄(2026-10-03,standard:通才-sonnet+架構對齊-sonnet,只看 r1 修正與補修差異)

機械:兩份 report-normalize 已正規;quote-check --spec r2-snapshot.patch:通才席全錨定,架構對齊席 3 句有 1 句錨不到(該條內容由編排者讀碼重現,見下表)。

編號:g1 = r2-通才-sonnet.md F1;a1 = r2-架構對齊-sonnet.md F1。共 2 條,全 minor、blocking 0。另收通才席一條「觀察」(混在好項裡的空項被默默丟掉,非 finding),一併修。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅 t_doctor_check3_long_name_hint_intact:紀錄檔名 140 字,改法那行被 _esc_clean 截在引號中間,照貼參數為空 | HIT |
| a1 | 編排者讀碼:warn(cap=20) 不看 _verbose,warn_soft 在 --verbose/--ci 全列;先紅 t_doctor_check3_bad_entry_cap_verbose_and_mixed_empty ①② | HIT |
| 觀察 | 先紅同支 ③:["[[Systems/A]]", "", "#Systems/B"] 不報任何壞項 | HIT |

處置:2 條全折(另修觀察那條)。g1:說明照行長上限清、照貼指令只清控制字元不截斷;a1:warn 的 cap 在 --verbose/--ci 全列、結尾措辭同 warn_soft;觀察:全是空的才算「讀不出任何一項」,混在好項裡的照報空的項(判空收進 _system_ref_blank / _system_ref_item,判「驗了誰」那支複雜度回到門檻內)。突變:改法截到 60 字 → long_name 紅;空項當合格 → mixed ③ 紅。
回歸(上一輪修補造成的):g1(r1 改法加引號時一起截斷)、a1(r1 補修把封頂做進 warn 時沒看 _verbose)。
