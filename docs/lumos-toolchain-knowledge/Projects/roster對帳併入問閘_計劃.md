---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑥(v4,r2 七條再折後大幅瘦身)——[S1] 只掛 --disposal、只在 rid 為真 rN 時對帳;異常集合=明確列舉五種(external_missing/單家族/兼任/unknown/席數短缺),抑制四種常印診斷;hedge 刪「低共識」條件(無資料源);異常觸發寫 loop 目錄輕量留痕檔供兩季覆核;settle 誠實除外(記錄結構恆 round-less 無 rid 可對,明說做不到+Issue 觀察,不假裝覆蓋)
  KEY:★light 誤判實錘★:r1 單席冒 5 條 major,依鐵則升級 roster-merge-std 完整迴圈,乾淨輪不洗回
  DEP:[[Projects/建了沒人跑批次裁定_計劃]]
status: done
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/done
---

# roster對帳併入問閘_計劃

> 白話:v4(三輪 31 條教訓後的瘦身版):只做能做乾淨的那一塊——disposal 問閘、真實輪次、異常才開口、開口就留痕。settle 那條路的資料模型根本沒有輪次可對,直說做不到,不端假菜。

## 條款(v4)

- **[S1] 範圍=--disposal 且 rid 為真 rN**:`cmd_loop_status` 把 `roster` 布林傳進 `_loop_status_disposal`(加參數,r2 d-f1 管線補明);disposal 判定完成後(★出口清單以實作當下逐一點名為準,r3 e-f2:rid 綁定後除 PASS/FAIL 終點外還有三個 return 2 提前中止路(G3 spec 讀不到/一輪多處置帳/findings 壞值)——這三路=帳面異常優先於席位對帳,刻意不掛對帳、註解寫明;共用收尾只掛 PASS/FAIL 兩終點前★,包 try/except——炸=一行降級警告,rc 不變),以 disposal 自己的 rid 為唯一輸入呼叫 `_roster_observe(only_rid=rid, anomalies_only=True)`(參數化單一實作,only_rid 同時抑制內部 dispatch glob 補漏);rid 為 `__seqN` 合成鍵→跳過(round-less 無派工快照可對);使用者同帶 `--roster`→尾端跳過(全史已印)。
- **[S1b] anomalies_only 涵蓋對照表(r2 d-f5 補)**:★印★六種(r3 e-f1 拆名):external_missing、單家族、真兼任(同名 ≥2 必要外家席)、命名歧義(名字撞兩家關鍵字表——與真兼任分開命名,log 種類欄各自標)、unknown 降級、席數短缺 shortfall;★抑制★=逐輪摘要行、kind/tier/entry 診斷行、conditional 席提示、無快照提示四種。外家未派措辭(hedge 簡化,刪無資料源的「低共識」條件,r2 d-f6):「外家席本輪未派(編制=<requirement 值>;辯方是否該派屬編排當場判斷,本行僅轉述編制對照,不裁決)」。
- **[S1c] 異常留痕(r2 d-f7;r3 e-f3 顆粒度)**:先收集全部異常種類、印完全部異常行,**最後一次性** append 單行到 `governance/review-reports/<loop>/roster-alerts.log`(ts+rid+種類清單)——log 寫入失敗只損失留痕不吞異常輸出(寫入自身再包一層 try,失敗印一行「留痕失敗」);兩季覆核有檔可查。
- **[S2] 旗標全保留**:--roster 現行為(全史、四模式)與 argparse help 更新同 v3;測試帳(r3 e-f4 行號更正):t_loop_status_roster_check 16 條中 14 條零改動,**22508-22514** 的 rc 對照與零 diff 兩條依「同帶跳過」語意重寫(22475-22480 屬 t_loop_next_roster,不動)。
- **[S3] skill 三處精確句子**:同 v3,但 settle 相關句改為誠實形:「settle 結清模式的席位對帳需手動 loop status <id> --roster(其記錄結構無輪次欄,自動對帳做不到——詳 [[Issues/settle路徑席位對帳無輪次可對]])」。
- **[S4] settle 誠實除外(r2 d-f2/d-f3 取代 v3 的假補掛)**:settle 記錄結構恆 round-less(帶 round 會在入口被 rc2 擋),無 rid 與派工快照可機械對——**明說做不到**,立 Issue 列觀察(若日後 settle 記錄格式演進出輪次概念再回頭);高風險 spec 走 settle 時的席位核對=skill 指路手動 --roster。
- 邊界:編制表/lens 值域/--panel/--light 不動;PASS/FAIL 布林零改動。

## 行為斷言

異常 fixture(真 rN+外家缺)→ --disposal 輸出含轉述行且 roster-alerts.log 多一行;健康 fixture → 零 roster 行且 log 無新行;__seqN fixture → 零 roster 行;同帶 --roster → 尾端跳過(全史照印無重複);打樁 raise → rc 不變+降級警告;雙輪編制不同 fixture → 附的是 disposal rid 那輪(交叉斷言);settle fixture → 零自動對帳行(誠實除外);印/抑制對照表逐種驗(五印四抑)。

## 實務隱患

- 守衛面:動輸出不動判定;try/except+打樁斷言鎖 rc。已排除:金流/對外/不可逆。
- 必要性(ext-f1 挑戰入檔):異常才發聲+留痕檔;回頭條件=2026-11-26 查 roster-alerts.log,零出現→連旗標一併重審退場(掛本案 Verification revalidate_when,判準有檔可查)。
- REVISIT:2026-11-26 查 roster-alerts 真實出現數(零→--roster 重審退場;上行條款)
- settle 除外=已知缺口誠實化:高風險 spec 的席位核對仍靠人記得(skill 指路);Issue 掛觀察。

## 審計修正紀錄

**r1(light 誤判升級)/std-r1(19 條)**:見 v2/v3 紀錄。
**std-r2(delta 席 7 條全折)**:d-f1 參數管線補明;d-f2/d-f3 settle 假補掛撤除→[S4] 誠實除外+Issue(blocker:自己的跳過規則吃掉自己的補掛=比漏接更隱蔽);d-f4 單家族併入異常集合;d-f5 印/抑制對照表明列;d-f6 hedge 刪無資料源條件;d-f7 異常留痕檔。
**std-r3(delta 席 4 條全折,cap 輪)**:e-f1 兼任一名兩義拆開;e-f2 出口清單寫全(三個 return 2 路刻意不掛+註解);e-f3 log 一次性寫入+雙層 try 顆粒度;e-f4 測試行號更正(22508-22514 非 22475-22480)。四條皆文書精度級無設計反轉——cap 內收斂,實作代碼審接手。
