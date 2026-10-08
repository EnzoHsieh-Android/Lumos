# code-測試綁定一行一支 r1 收貨

席報告 2 份(正確性 5 條,其中 2 條 major;架構對齊 2 條)。quote-check 全錨。收貨時看 git status 沒動 repo。

彙整 id:正確性 c1–c5、架構對齊 a1–a2。

## 根因分組

- 名稱從遮罩過的文字切、又先找字面 `[test:`:c1(大小寫與全形冒號漏)、c2(反引號名稱變 NUL、誤併)、a1(跟 test_refs/S20 切法分岔)。
- 印出的形狀:c3(名稱不設上限)、a2(第三欄型別變成 list)。
- 同一行只出一則:c4(數量先命中吞掉綁定)。
- 測試覆蓋:c5(綁定規則丟例外沒有釘子)。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | t_note_wording_binding_hint ⑤:`[Test:…]`、`[test：…]` | 修前沒提醒 | HIT |
| c2 a1 | 同上 ⑥:`[test:`k a`,`k b`]`;quiet 新增 I:`[test:`t_one`,t_one]` | 修前印出 NUL、I 被誤報 | HIT |
| c3 | 同上 ⑦:一行 12 支 | 修前 12 支全列 | HIT |
| a2 | 讀碼:emit 對 binding 用 len(tag)、join(tag) | 型別分流 | HIT |
| c4 | 同上 ⑧:同一行有數量句與兩支綁定 | 修前只出數量 | HIT |
| c5 | 新測試 t_note_wording_binding_isolated:替換 `_ns_wd_binding_hit` 丟例外 | 現況已能接住(這是補釘子) | HIT |

## 處置

全折(7 條):
- c1、c2、a1:綁定規則改吃原文(只遮掉引號),名稱切法整段交給 note-shape 與 S20 共用的 `slot_parse` + `_test_names_of`,拿掉字面 `[test:` 的前置過濾。
- c3、a2:綁定的第三欄改成組好的說明字串(跟數量的標記一樣是字串),名稱最多列 5 支、其餘講總數。
- c4:`_ns_wd_line_hit` 改回清單,數量與位置取第一個、綁定另外看,同一行可兩則都出;帳本 lines 改數不重複的行。
- c5:新增 t_note_wording_binding_isolated。
故意改壞五處(餵遮罩文字、綁定被吞、名稱不設上限、不遮引號、不看切點)全部翻紅。效能:3000 行 0.04 秒、一行 5000 支瞬間。
