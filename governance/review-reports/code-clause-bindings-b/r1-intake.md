# code-clause-bindings-b r1 — 收貨與編排者機械重現(驗收前編號 r3 折入)

preflight-4: n/a(code 迴圈)

★換編號緣由★:前編號 `code-clause-bindings` r3 是上限輪,折入 6 條沒有席位再驗;本編號只驗那批 delta(381 行)。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ✅ 全數錨定 | ok 5 | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok 13 | 觀測 |
| 外家否決-codex(sol/xhigh) | ✅ 全數錨定 | ok | 觀測 |

前編號 r3 的 h1–h6:單reviewer 判 h1/h3/h4/h5/h6 修好、h2 引入倒退;架構席全對齊(前輪 major 已折平);外家席 h3/h5 修好、h1/h2/h4 各有殘洞。

## 編排者自己重現的

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| i1 `a. [S1]`/`一、[S1]` 前面有「詞」→ 當散文靜默跳過(r3 之前是硬擋,倒退) | 單 blocker | 純函式餵 → listlike False → skip | **HIT** → 短編號進定義行白名單;像清單的判定也認短編號(iii. 之類白名單外的仍擋) |
| i2 雙反引號/未閉合反引號可把 `[manual:]` 藏進真條款 | 外家 #1 | 餵 ``- [S1] 甲 ``[manual:人看一次]`` `` → manual | **HIT** → 雙反引號 span 先剝;未閉合反引號之後一律不信 |
| i3 `~~~` 圍欄沒遮 | 外家 #2 | 餵 ~~~ 區塊 → S1 untagged | **HIT** → 改在唯一那份 `_visible_lines`(search 一起變,圖譜 lumos-cli-read 記) ;四反引號套三反引號的巢狀是逐行切換設計的既有邊界,不動 |
| i4 像清單的未知前綴只在零條款時查 → 加一條合法條款就繞過 | 外家 #3 | 餵兩行 → ok | **HIT** → 一律擋 |
| i5 `<!-- [S1] -->` 被當未知清單擋 | 外家 #4 | 餵 → fail | **HIT** → 單行 HTML 註解剝掉 |
| i6 handoff 人讀沒印重複數 | 外家 #5 minor | 讀碼 | HIT → 印 |
| i7 docstring「下一個 [SN] 之前」過時 | 外家 #6 minor | 讀 | HIT → 改 |
| i8 spec-trace 重複編號印 ⚠ 不是 ✗ | 單 minor | 讀 | HIT → ✗ |
| i9 自踩:像清單的判定拿整行判,「…詳見 [S2]」被判像清單 | 我(折 i4 時測試翻紅) | cg-p 紅 | HIT → 只看該行第一個 [SN] |

翻紅釘六個全翻紅:不認字母/中文編號(5)/ listlike 退回只認符號(2)/ 只在零條款時查(2)/ 不剝 HTML 註解(4)/ 未閉合反引號後照信(4)/ ~~~ 不算圍欄(2)。折完 clause 80、disposal 109、handoff 55、search 130、fence 10 全綠。

## 折入(9 條)

i1(單 blocker)/ i2(外家 #1)/ i3(外家 #2)/ i4(外家 #3)/ i5(外家 #4)/ i6(外家 #5)/ i7(外家 #6)/ i8(單 minor)/ i9(自踩)。

## 誠實記

- 這是同一個解析器第四輪被打穿。每一輪都是 Markdown 的另一種寫法。現在的規則已縮到:只認幾種定義行前綴、一行一條、看得見的字沿用專案唯一實作、看不懂就擋、純引用跳過但印出來。★再有殘洞應該是「認不得→擋」而不是「認不得→放行」,這才是這輪真正要守住的方向。★
- `_visible_lines` 加 `~~~` 是動了全檔共用的實作,search 的可見行也跟著變;測 search/fence/refcheck 子集全綠,圖譜記了。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet(全錨、算人數、最高 blocker)。

## 處置

9 條全部折入,accepted 為空(輪內有 blocker)。r2 派全新席只驗這批 delta。

(本檔在此之後不再修改。)
