preflight-4: ran

# code-規格閘半套-v2 r2 收貨紀錄

- 審材 r2-delta-snapshot.patch(r1 折入 delta,87 行,指紋 9f0ebc4da7e48962);兩席全新;外家缺席留痕。單席引句全數錨定;架構席第 2 句引了兩行(while 迴圈),機械錨不到,由編排者重現。

## 編排者重現
- **U1**:`_clause_grammar("當甲,系統反應")` 回 (True…)——缺應判斷用字元比對 → HIT。
- **U2**:`_clause_grammar("當甲成立,在為順應法規要求後,則系統應調整")` 回 (True…)——「順」不在表 → HIT。
- **U3**:`_shall_index("客服問答應於24小時內完成回覆")` 回 -1 → HIT(反方向誤傷)。
- **U4**:`_shall_index` 是手寫 while+find,本檔同類問題一律 lookbehind 正則 → HIT。

## 去重對照(U1–U4;全折)
| id | 內容 | 席 | 嚴重度 | 型 | 折法 |
|---|---|---|---|---|---|
| U1 | 缺應判斷沒跟著跳複合詞 | 單F1 | major | code | 兩處改用 `_shall_index`;測試 ⑩ |
| U2 | 複合詞表不齊(順應/理應/照應/接應/自應) | 單F2 | major | code | 補進;測試 ⑩ |
| U3 | 「問答應於…」的應被跳過 | 單F3 | minor | code | 表拿掉「答」;測試 ⑩ |
| U4 | 手寫 while 找應、字元集用字串 | 架構§3(major)、§1(minor) | major | code | 改成 `_SHALL_RE` 負向 lookbehind 一次搜,常數收進正則 |
