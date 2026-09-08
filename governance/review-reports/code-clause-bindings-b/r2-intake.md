# code-clause-bindings-b r2 — 收貨與編排者機械重現

preflight-4: n/a(code 迴圈)

三席驗收 -b r1 的 9 條折入(delta 368 行)。三席都判 i1–i9 各自修好,但 i1/i2/i3 各引入新洞——全部在我上一輪新加的正則與遮蔽規則上。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ✅ 全數錨定 | ok | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok 14 | 觀測 |
| 外家否決-codex(sol/xhigh) | ✅ 全數錨定 | ok | 觀測 |

## 編排者自己重現的

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| j1 三條行內可見規則散在解析器裡=第二份實作 | 架 major | 讀 INLINE_CODE_RE 旁的叢與我的三行 | **HIT** → 收成 `_strip_inline_markup`,跟 `_visible_lines` 配對 |
| j2 反引號在 [SN] 前面 → 條款消失 → 閘印「未啟用」放行 | 單 A blocker、外家 #1 | 餵 `` `[S1] 沒標 `` → rows 空、skip | **HIT** → 原始行像條款(lead 或 listlike)且遮完看不到 → 當認不得擋 |
| j3 cf./vs. 兩字母縮寫被當編號 → 假重複定義 | 單 B | 餵 `cf. [S1]` → defined | **HIT** → 字母編號限單字母且必帶分隔符 |
| j4 「詳見:[S9]」「注:[S1]」「Q:[S2]」被當像清單誤擋 | 單 C、外家 #4 | 餵 → listlike | **HIT** → listlike 只認符號與帶分隔符的短編號,拿掉冒號與任意短詞 |
| j5 ``` 與 ~~~ 共用一個 toggle,交錯會反轉可見性 | 外家 #2 | 餵交錯範例 → 假證據露出、真條款被吞 | **HIT** → 圍欄各自配對(改在 `_visible_lines`) |
| j6 ① 圈號不算清單也不算像清單 → 靜默 | 外家 #3 | 餵 → prose skip | **HIT** → 納入定義行與 listlike |
| j7 已定義的編號再出現在認不得的清單行被遮掉 | 外家 前輪3 | 餵 → ok | **HIT** → listlike 一律記,已定義的當重複擋 |
| j8 跨行 HTML 註解裡的 [S1] 被當條款 | 外家 前輪4 | 餵 → untagged | **HIT** → `_visible_lines` 整段不看 |
| j9 註解說「未閉合反引號剝不掉」與碼相反 | 外家 #5 minor | 讀 | HIT → 改 |

翻紅釘五個全翻紅:反引號在前照放行(2)/ 已定義編號再出現不擋(2)/ 圍欄不配對(2)/ 跨行註解不看(2)/ listlike 退回認任意短詞+冒號(4)。折完 clause 89、disposal 115、search 130、fence 10、refcheck 14、lint 174、guard 308 全綠。

## 折入(9 條)

j1(架 major)/ j2(單 A、外家 #1)/ j3(單 B)/ j4(單 C、外家 #4)/ j5(外家 #2)/ j6(外家 #3)/ j7(外家 前輪3)/ j8(外家 前輪4)/ j9(外家 #5)。

## 誠實記

- 動了 `_visible_lines`(全檔共用):圍欄配對、跨行註解——search/refcheck/fence 子集全綠,圖譜 lumos-cli-read 記了;但這是「順手改了搜尋看得見什麼」,不是本案設計審過的範圍。
- 這是解析器第五輪被打穿。規則現在只剩:定義行前綴白名單(含短編號)、一行一條、看得見的字沿用兩份唯一實作、認不得就擋、詞/詞+冒號開頭是散文。★下一輪(-b r3,上限)若仍有 blocking,就停、攤給 Enzo——不再自己開 -c。★

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet(全錨、算人數、最高 blocker)。

## 處置

9 條全部折入,accepted 為空(輪內有 blocker)。

(本檔在此之後不再修改。)
