---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑥(v3,std-r1 五席 19 條全折)——[S1] 異常才發聲:問閘(--disposal 與 --settle 兩路徑)收尾以閘判定的 rid 唯一輸入呼叫參數化 _roster_observe(only_rid 含抑制內部 glob 補漏;anomalies_only;__seqN 合成鍵跳過不印;兩出口皆包 try/except),健康輪零輸出、異常行轉述式含辯方條件 hedge;[S2] --roster 旗標全保留(advisory 不加機械擋),同帶時尾端附加自動抑制;[S3] 三處 skill 精確句子(兩 reference 同句)
  KEY:★light 誤判實錘★:r1 單席冒 5 條 major,依鐵則升級 roster-merge-std 完整迴圈,乾淨輪不洗回
  DEP:[[Projects/建了沒人跑批次裁定_計劃]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# roster對帳併入問閘_計劃

> 白話:v3(升級完整審 19 條折入後):對帳不再「每輪必印」,改成**有異常才開口**——外家該在沒在、席位對不上編制,問閘時自動跳警示;一切健康就閉嘴。旗標原樣保留給回放跟手動全史。

## 條款(v3)

- **[S1] 異常才發聲(兩條問閘路徑)**:`_roster_observe` 加參數 `only_rid=None, anomalies_only=False`(比照 _panel_round_conjuncts 的 quiet= 參數化先例,**單一實作禁抄改**;only_rid 同時抑制函式內部的 dispatch glob 補漏——只認該 rid);`--disposal` 與 `--settle` 兩條問閘(settle 收最高風險 spec,r1 抓到漏接)各自在**兩個出口(PASS/FAIL)前**呼叫、**比照既有呼叫點包 try/except**(炸=降級一行警告,rc 不變);rid=**閘自己判定的 rid 唯一輸入**(不得由 roster 重算);rid 為 `__seqN` 合成鍵(round-less:light/循序 code-standard)→ **跳過對帳不印**(無真實派工快照可對,沉默勝過錯誤示警);對帳無異常(席數足、家族齊、無兼任、無 unknown)→ **零輸出**。
- **[S1b] 異常措辭改造**:轉述式非裁決式;外家未派的訊息帶條件 hedge:「外家席本輪未派——若本輪有存活 major 低共識條目則屬缺席(處置=收斂結論降級+留痕註記,2026-08-22 裁);無則屬正常未觸發」——消除與 PASS 並排的互斥觀感,也修正「辯方=條件觸發、roster 檢=無條件」的語意落差。
- **[S2] 旗標全保留**:--roster 現行為(全史、四模式)不動——理由=**advisory 不該加機械擋**(panel 的 cutoff 是給會動 rc 的閘用的,此處不援引);同帶 `--disposal --roster` 時尾端附加**自動抑制**(全史已含當輪,不重複);說明文字落點=argparse help 更新(「全史觀測/回放用;問閘異常轉述已自動附於 --disposal/--settle」),不加執行期 banner。
- **[S3] skill 三處精確句子**:design-loop reference:235 與 code-loop reference:379 **同句**:「本段散文為解說,漂移以 roster 為準;問閘(--disposal/--settle)偵測到席位異常會自動轉述,--roster 供全史回放」;code-loop SKILL:21 改:「外家缺席的轉述由問閘自動附出(異常才印,含條件觸發 hedge);全史核對用 loop status --roster」。
- 邊界:編制表/lens 值域不動;--panel/--light 模式不動;PASS/FAIL 判定布林零改動。

## 行為斷言

異常 fixture(外家缺)→ --disposal 與 --settle 輸出各含轉述行(hedge 字樣);健康 fixture → 兩閘輸出零 roster 行;__seqN(round-less fixture)→ 零 roster 行;同帶 --roster → 尾端附加抑制(全史區塊照印、無重複當輪段);打樁讓對帳段 raise → 兩閘 rc 與無附加時一致且輸出含降級警告;雙輪編制刻意不同 fixture → 附的是閘判定 rid 那輪(交叉斷言 rid 相等);既有 16 條 roster 測試(機械數,原誤記 17):14 條零改動照綠、22475-22480 那組 2 條依「同帶抑制」語意重寫。

## 實務隱患

- 守衛面:動輸出不動判定;try/except+打樁斷言鎖 rc。已排除:金流/對外/不可逆。
- 必要性(外家 ext-f1 的挑戰誠實入檔):零呼叫可能=零需求。異常才發聲把成本壓到「健康=零噪音」;回頭條件=下次動 _TIER_ROSTER 或 _roster_observe 時回顧異常轉述有無真實出現過,兩季(2026-11-26)仍零出現→連旗標一併重審退場(寫入本案 Verification revalidate_when)。

## 審計修正紀錄

**r1(light 單席 5 條 major→誤判升級,見 v2 紀錄)**
**std-r1(2026-08-26,五席 19 條全折零放行:ext 4[1b]+s1 3+s2 4[1b]+s3 5+arch 3;ext 引句格式本輪合規)**:
- 異常才發聲取代恆印(ext-f1 必要性挑戰+輸出量);互斥裁決觀感→轉述式+hedge(ext-f2/s3-f5)。
- rid=閘判定唯一輸入+交叉斷言(ext-f3);only_rid 參數化含 glob 抑制(s1-f1/arch-f1);__seqN 跳過(s1-f2);兩出口+try/except(s1-f3)。
- settle 路徑補掛(s3-f3);同帶抑制(s2-f4/arch-f2/s3-f2);驗法改打樁 raise(s2-f2);雙輪 fixture(s2-f3);測試帳實數 16=14+2(s2-f1,第七次數數教訓)。
- 說明文字落點明定(s3-f1);三處精確句子且兩 reference 同句(s3-f4);「全面對齊先例」措辭撤換為「advisory 不加機械擋」(arch-f3)。
