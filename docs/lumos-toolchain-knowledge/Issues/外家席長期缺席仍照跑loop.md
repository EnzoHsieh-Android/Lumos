---
type: issue
status: open
created: 2026-08-20
updated: 2026-08-20
aliases: []
tags:
  - type/issue
  - status/open
  - priority/P2
  - scope/loop-engineering
summary: |-
  FLAG:DECISION
  KEY:maker≠checker 是整套驗證的地基,而跨家族審查席已連續缺席數週:Codex 帳號不支援可用模型、Gemini pro 免費額度 limit=0、flash 逾時
  KEY:2026-08-20 gov-stats 案三輪 panel 九席全為 claude 家族;處置是在文件加一句「收斂宣稱要講小」,★缺席未被當成 blocker 處理★
  DECISION:[2026-08-20]立案,未處置——需裁「地基缺席時 loop 還能不能算數」
---
# 外家席長期缺席仍照跑loop

> 白話:整套驗證哲學建立在「做的人不能是驗的人」。跨家族審查席就是為此存在的。**它壞了好幾週,我們照跑,只在文件上加一句但書。**

## 可數事實(2026-08-20 實測)

| 外家管道 | 實測狀態 |
|---|---|
| Codex CLI | 帳號不支援任何可用模型(400 invalid_request:`gpt-5.6-sol`/`gpt-5.2-codex` 皆退回) |
| Gemini pro 系 | 429 配額用盡,錯誤訊息明寫 `limit: 0`(免費層) |
| Gemini flash 系 | 連線逾時(60s 無回應) |

**結果**:[[Projects/閘觸發帳統計_計劃]] 三輪對抗審計、九個審查席,**全部同一家族**。

## 為什麼這是問題

`lumos-design-loop` 的席次編制把外家否決席列為 `note-if-absent`——缺席**不擋收斂**,只要求「收斂宣稱要講小」。

★這條設計在「偶發缺席」下是合理的,在「長期缺席」下就變成了**地基缺席還繼續蓋樓,然後在牆上貼一張紙寫『本樓地基缺席』**★。

而且:**沒有任何機制會告訴你這個狀態持續多久了。** 每一輪各自寫一句但書,沒有人統計「連續幾輪沒有外家」。

## 與既有紀錄的關係

- memory `retrieval-v1-and-codex` 早已記載「Codex 到期,外家現役=Gemini API」——★該記載已過時,Gemini 也不可用★。
- `lumos-design-loop` 的能力宣告制原語意=「有就用,沒有就講小」;本單主張這個語意需要一個**時間維度的補充**。

## ✅ 管道已恢復(2026-08-20 當日)

- Enzo 換付費 key → **gemini-3-flash-preview 可用**(實測 200、serviceTier=standard、12s 級延遲)。★pro 系(gemini-3.1-pro-preview)本 key 額度仍=0,勿當預設★。
- 呼叫固定成 `scripts/external-seat.sh`(單發無狀態;歷來手打 curl 連摔逾時的教訓收進腳本註解)。
- **首跑實戰驗收**:對剛收斂的 gov-stats spec 當否決席,5 條 findings——**1 條真洞折入**(動態閘名逃逸字面值掃描,前三輪九個同門席皆未抓,已加測試釘)、1 條被 spec 既有定義駁掉、2 條措辭歧義補明。★單次樣本不足下品質結論,但「同門三輪漏、外家一發中」與本單立案動機一致★。

**未解的部分**:「連續幾輪無外家」仍無人統計、歷史已收斂 loop 的家族純度仍未盤;本單不關,降 P2。

## 待裁

- [ ] 連續 N 輪無外家席 → 要不要升級成 blocker 或至少警示?
- [ ] 要不要換管道?(付費 API / 本地模型 / 其他家族)——這是成本問題,不是技術問題。
- [ ] 已收斂的歷史 loop 裡有多少是單一家族?未統計。
