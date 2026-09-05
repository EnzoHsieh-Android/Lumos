# code-readme-five r3 intake(2026-09-05,末輪:delta回歸-sonnet / 外家finder-codex)
收貨:兩席引句機驗見上方。delta 席自己註明快照已落後 live HEAD(外家先到、修法先落),其 major 與外家同題。
## 外家 1 major:控制字元檔名的八進位跳脫沒解 → git show 找不到 → 放行 HIT(重現 \x01) → `\"` 手解後整串 printf %b;五種怪檔名實測全擋;測試加一案。
## delta 1 major(同上)+ 1 minor:`${path:1:${#path}-2}` 對單一引號假輸入 set -u 吐錯(真 git 輸出到不了)HIT → 加長度 ≥2 守衛。(a)(d)(e) 驗收皆過;bash 3.2/5.3 同行為。
★達上限★:standard 3 輪到頂,r3 仍出 major(已折);修法之後沒有再派席。攤人:REVISIT 2026-09-08 併 [[Projects/Codex行為精修_計劃]] 同日那條一起裁要不要補一輪。intake 到此為止。
