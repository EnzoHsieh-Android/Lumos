---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑥——roster 對帳測試齊全但治理帳 0 呼叫;[S1] --disposal 輸出自動附「當輪」對帳(僅最新輪,對齊 disposal 語意)[S2 修訂] --roster 保留為回放/手動觀測旗標(真正比照 panel 先例的祖父語意,r1 抓到原「退場」與援引先例不一致),skill 三處(非兩處)改寫
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

> 白話:席位對帳功能是好的但沒人記得敲。v2(r1 五條 major 折入後):問閘輸出自動附「當輪」對帳;旗標不硬退、降級為回放用途——這才是真的比照 panel 退場先例(它有祖父條款,我原案沒有)。

## 條款(v2)

- **[S1] 併入(當輪)**:`loop status <id> --disposal` 輸出尾端自動附**最新一輪**的 roster 對帳(復用 _roster_observe 邏輯但限定當輪 rid——對齊 disposal「只判最新輪」語意,不逐輪重印歷史);恆 advisory 不影響 PASS/FAIL。
- **[S2] 旗標降級為回放/手動觀測**(修訂,原「退場指路」與 panel 先例不一致):`--roster` 保留現行為(全輪、四模式可用)——舊 panel 回放與手動全史觀測的唯一通道;說明文字標「回放/手動觀測用;問閘當輪對帳已自動附於 --disposal」。
- **[S3] skill 三處改寫**(r1 實數):design-loop reference:235 與 code-loop reference:379 的裸 --roster 範例補「回放/全史觀測」語境;code-loop SKILL:21 缺席轉述句改為「--disposal 問閘會自動轉述當輪缺席」。
- 邊界:編制表/lens 值域不動;--panel/--light/--settle 模式行為與測試全不動(f-3 解法=旗標不退)。

## 行為斷言

--disposal 輸出含當輪對帳行且**只有當輪**(多輪 fixture 驗不重印歷史);--disposal rc 與未附對帳前完全一致(對照基準=--roster 旗標仍在,f-2 解);--roster 全部 17 條既有測試零改動照綠;skill 三處 grep 新語境字樣。

## 實務隱患

- 守衛面擦邊:動輸出不動判定,rc 一致釘鎖住;已升級完整迴圈(light 誤判)。已排除:金流/對外/不可逆。

## 審計修正紀錄

**r1(light 單席,5 條 major 全折→觸發 light 誤判升級)**:f-1 全歷史膨脹→[S1] 限當輪;f-2 對照基準消失→[S2] 旗標不退;f-3 三模式無替代→同上;f-4 三處非兩處+語境不可機械替換→[S3] 實數列點;f-5 panel 先例有祖父條款→[S2] 全面對齊先例改「降級回放用途」。
