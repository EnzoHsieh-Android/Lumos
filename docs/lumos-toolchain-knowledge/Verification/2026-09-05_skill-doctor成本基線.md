---
type: verification
status: pass
date: 2026-09-05
valid_under: Claude Code 2.1.261 的 /skill-doctor(Stats 分頁),Enzo 本機,量的是 2026-08-29~09-05 這 7 天
revalidate_when: 代碼審/設計審席位編制改了、或 skill 說明文字改了之後,再跑一次 /skill-doctor 對照;REVISIT:2026-10-05 重量一次看趨勢
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/loop數據收集_計劃]]"
---
# 2026-09-05_skill-doctor成本基線

> 白話:Claude Code 2.1.261 新增了一個指令,會列出每支 skill「每回合掛在系統提示上花多少字」和「這 7 天總共燒了多少 token」。這是第一次有機器量出來的 lumos 流程成本,記下來當基線,以後改了審查編制可以對照。截圖由 Enzo 手機翻拍終端機,數字人工抄錄。

KEY:量法=`/skill-doctor`(2.1.261 起併進 /plugins 的 Stats 分頁);「context」=該 skill 在系統提示清單裡那一行的 token 數,每回合都付;「7d tokens」=近 7 天歸給該 skill 的 session token(它自己的定義,含被叫起之後那一段對話;子代理算不算沒查)。
KEY:lumos 五支的掛載成本合計約 420 token/回合(code-loop ~90、design-loop ~110、project-notes ~90、core-knowledge ~70、pitfalls-gapfill ~60),占整份 skill 清單(約 1800)兩成多——★不值得砍字★:說明文字是刻意塞觸發詞的,情境探針量的就是命中率,要縮先跑探針([[Projects/修法A_lumos先行ablation_計劃]] 的儀器)。
KEY:★真正的成本在迴圈★——7 天:lumos-code-loop 930 萬 token / 49 次(平均約 19 萬一次)、lumos-design-loop 300 萬 / 56 次(約 5 萬一次)、lumos-project-notes 130 萬 / 239 次(約 5 千一次)。代碼審一次≈設計審四次≈查圖譜 35 次。這填的是 [[Issues/流程自產工作量未量測]] 一直缺的「總量」那格(--finding-kind 量的是「發現在修什麼」的比例,不是錢)。
KEY:同機器其他項(非 lumos,但影響 lumos 專案的每回合成本):csharp/kotlin/vue 三支慣例 skill 裝在全域、在本 repo 零次使用,每回合約 180 token;unity-cli 一行約 220 是單一最大項;context7/playwright 兩個 plugin 50~86 天沒用且本 session 開頭連線超時。

## 誠實界線
- 數字是從手機翻拍的截圖抄的,沒有機器匹配的原始檔(/skill-doctor 不落檔、stdout 也不給對話);抄錯風險存在,但每格都對過兩次。
- 「7d tokens」怎麼歸因(含不含子代理、含不含 hook 注入)官方沒寫,我沒查;所以 930 萬只能當「代碼審是大戶」的相對訊號,不能拿去算美元。
- 只量了一台機器、一週;那週剛好有 Codex 接入的四階段+精修共 8 場代碼審,偏高。REVISIT 2026-10-05 再量一次才知道常態。
