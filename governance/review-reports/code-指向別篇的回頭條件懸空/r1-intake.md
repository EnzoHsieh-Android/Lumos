# code-指向別篇的回頭條件懸空 r1 收貨

席報告 2 份(正確性 4 條 minor、架構對齊 1 條 major + 3 條 minor),都是新席。兩份都從逐字稿抽原始最後回覆存檔(子代理完成通知會把 < > 轉成跳脫字)。quote-check:正確性席全錨;架構對齊席 A4 的引句跨兩行、錨不到,不當載體。

彙整 id:正確性 c1–c4、架構對齊 a1–a4。載體:正確性席。輪內有 major → 全折、不放行任何一條。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 | 讀碼:`_revisit_ref_dates` 與 `_revisit_lines` 同一條流水線(可見行→剝行內程式碼→`_revisit_split`→`_probe_parse`),只差不跳過已結案 | 兩份 | HIT |
| a2 | 讀碼:S17 用 `env.resolve(link_target(ref))`,S21 直接 `env.resolve(tgt)` | 少一道正規化 | HIT |
| a3 | 讀碼:同一區塊 `_RREF_DATE_RE` 與 `_RREF_AFTER_DATE_RE` 各寫一次日期形狀 | 兩份 | HIT |
| a4 | 讀碼:S17、S19、S20 皆 `sorted(env.notes)`,S21 `for rel in env.notes` | 未排序 | HIT |
| c1 | 測試格:`見 [[Systems/結案X]] 的 REVISIT 2026-11-08`、`回頭條件見 [[Systems/改成X]]` | 修前不列 | HIT |
| c2 | 測試格:`REVISIT：2026-11-08`(全形冒號) | 修前不列 | HIT |
| c3 | 測試格:一行三萬組 `` `a` [[Systems/X]] REVISIT 2026-11-08 `` | 修前 34.8 秒 | HIT |
| c4 | 測試格:`…再量;另外把 Y 改成 Z。` | 修前不列 | HIT |

## 處置(依根因分組,全折)

- 第二套做法(a1 a2 a3):讀回頭條件行抽成 `_revisit_all_lines`(含已結案、帶結案旗標),`_revisit_lines` 改成濾掉已結案的那一層、對外不變,S21 用全部;解析連結先過 `link_target`;日期形狀只寫一次(`_RREF_AFTER_DATE_RE` 由 `_RREF_DATE_RE.pattern` 組)。
- 範圍邊界(c1 c4):待辦詞範圍扣掉連結本身(`_rref_window`);句尾認「。!?;」與半形 !?;(英文句點不算,路徑與版本號裡有)。
- 輸入格式(c2):冒號認半形與全形。
- 效能(c3):判「在不在行內程式碼裡」改二分(區段由左到右不重疊)。
- 輸出穩定(a4):`sorted(env.notes)`。

先紅後綠:新增 5 格(S1 ⑧、S3 ⑧⑨⑩⑪)修前紅;修後 26 條全綠。翻紅:範圍不扣連結→⑧⑨紅;句尾只認。→⑩紅;不認全形冒號→S1⑧紅;線性掃區段→⑪紅(36 秒);共用讀法漏結案→S1④、S2③紅。`_revisit_lines` 的其他使用者:`-k revisit` 115、`-k closing` 12、`-k drift_fix` 161 全綠。a4 沒有測試格:`Env.from_texts` 本身就排序,測試搭不出未排序的情形。

## 修補因果(regression-set)

首輪,沒有上一輪修補。
