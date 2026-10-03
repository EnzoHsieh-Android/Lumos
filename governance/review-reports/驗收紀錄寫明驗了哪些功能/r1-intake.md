preflight-4: ran

# 驗收紀錄寫明驗了哪些功能 r1 前掃與收貨紀錄(2026-10-03)

前掃(sonnet 代理,固定清單四類;只讀)命中後直接改進計劃,不算 findings。語意類逐條前→後:

| 類 | 修改前 | 修改後 | 依據(讀碼) |
|---|---|---|---|
| ④ | `LINK_KEYS`(連結欄位寫法檢查) | 只進 `LIST_KEYS`,不加 `LINK_KEYS`、`_KNOWN_FRONTMATTER_KEYS` | `LINK_KEYS` 只給 lint 已知鍵聯集與 `_delguard_purelink`(假同步判定)用,沒有寫法檢查;`LIST_KEYS` 已併入 lint 已知鍵 |
| ④ | 沒有這個鍵 → 照舊從正文與開頭欄位的所有連結推 | 開頭欄位只算「整個值恰為單一連結」且不是區塊寫法的項 | `_note_from_text` 的 fm_targets 用 `_SINGLE_WIKILINK_RE.fullmatch`、排除 block_keys |
| ④ | 不接圖譜連線(typed edge) | 不接具名連線;但 `system_refs` 每項照通則進 `n.targets`、一般圖譜邊照算,明寫是既有行為 | `TYPED_EDGE_FIELDS` 寫死三欄;`n.targets` 收所有單一連結欄位 |
| ③ | `system_refs` 指到不存在或不是 Systems 的節點時 3/4 列出 | 只列存在但不是 Systems 的;不存在的由 2/4 報 | doctor 2/4 對 `n.targets` 全部報壞連結 |
| ④ | 3/4 另列問題項,跟漏寫 verified_by 同一段 | 另用一個 `warn`、另一個標題 | `warn` 的標題數字專指 missing,混進去會對不上 |
| ④ | 失敗照既有寫法提醒 | 另給 `lumos append … system_refs` 補法;`NEW_HINT` 補一句 | 既有提醒叫人跑 `sync-verified-by --apply`,它補不到 `system_refs` |
| ④ | 跳過 stale/fail/superseded 留在呼叫端 | 收進共用函式(回 None),兩邊不再各寫 | 跳過集合原本在 doctor、sync 各寫一份 |
| ① | 指路連結、doctor 3/4 沒定義 | 白話段補定義 | — |
| ② | skill 檔名沒路徑;slim 副本沒提 | 寫路徑;註明精簡版沒有這節、不用同步 | `slim/skills/lumos-project-notes/reference.md` 沒有欄位那節 |
| ② | 條款測試名不存在 | 條款區註明預先宣告、實作時新增 | — |

## 四席收貨(r1)

機械:四份 report-normalize 已正規;quote-check --spec r1-snapshot.md 四份全錨定;refcheck 正確性、邊界、架構對齊全 ok,整合席 1 處引用的檔不存在(佐證行,不影響該條判讀)。

編號:c1–c6 = r1-正確性-opus.md F1–F6;b1–b6 = r1-邊界-sonnet.md F1–F6;i1–i6 = r1-整合-sonnet.md F1–F6;a1–a2 = r1-架構對齊-sonnet.md F1–F2。共 20 條,blocking 8(c 2、b 3、i 3)。

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 / i1 | 兩席實驗:lumos remove 拿掉 system_refs 最後一項,鍵一起刪掉,doctor 回到從正文推 | HIT(兩席獨立一致) |
| c2 / b1 / b2 / b3 / i2 | 三席實驗:空值、全形括號、區塊寫法、純量多連結、純文字路徑、連結後多一句 → 鍵存在、解出來空或只剩最後一項,2/4 與 lint 都不報 | HIT(三席獨立一致) |
| c3 / i3 | 兩席讀碼:new --systems 只驗存在,Projects 也會寫進 system_refs;本 repo 42 篇計劃帶 verified_by | HIT |
| b4 | 席位實驗:resolve 路徑找不到改用檔名找,[[Projects/A]] 被救成 Systems/A | HIT |
| b5 | 讀碼:status 只 strip 沒 lower | 採信 |
| c4 | 讀碼:3/4 只查紀錄那側缺登記,不查功能那側多掛 | 採信 |
| c5 / i5 | 讀碼:孤兒推薦仍從正文推並建議跑 sync | 採信 |
| c6 / i6 | 讀碼:revert 後與舊版 lumos 對 system_refs 的行為 | 採信(i6 判不準部分改寫成相容句) |
| i4 | 編排者查:slim reference.md 有 plan_refs 欄位那節;commands/04 沒有 3/4 段;SKILL.md、reference.md 的同步錨點 | HIT(前掃寫錯精簡版那句) |
| b6 / a1 / a2 | 讀碼核對 | 採信 |

處置:20 條全折。同一個根(有鍵就只看它 → 寫壞默默關檢查)換形狀:每項嚴格判、任何寫壞形狀都報 issue;沒驗任何功能改寫 `無 <理由>`。其餘照補,詳見計劃審計修正紀錄 r1。
