1. **blocker**  
引句:「乾淨→進實作；乾淨明定為該輪 panel 閘 PASS，照 panel 語意 K=1 只看最後一輪」  
問題：repo 現行 panel 並非 K=1。2026-08-06 後建立的 loop 會啟用 K=2；只有最後一輪合格時仍明確 FAIL，必須連續兩輪合格才 PASS。照 spec 字面用「單輪乾淨」放行實作，與真正的機械閘直接矛盾；若實作者照 repo 執行，則 spec 宣稱的放行條件根本無法成立。  
查證：`/tmp/node-restore-sop-v2-r2.md:186`；`scripts/lumos:3750-3756`；`scripts/lumos:3897-3910`；`scripts/lumos:3931-3934`

2. **major**  
引句:「蓋章時 lumos lint 的 J-c 已驗過 [src:]/[git:] 指針存在性」  
問題：這句對 `[git:]` 宣稱過頭。shallow clone 中若 commit 物件不存在，J-c 不驗存在性，也不擋；它只發 soft warning「驗證跳過」，lint 仍可成功。SOP 卻把這一步當已完成的存在性核對，會讓 shallow clone 的懸空 git 指針帶著假綠進入 agent 語意審查。應改成「full clone 才驗過；shallow-skip 必另補驗」。  
查證：`/tmp/node-restore-sop-v2-r2.md:138`；`scripts/lumos:2558-2572`；`scripts/lumos:2511-2514`

3. **major**  
引句:「報告級引用可用 refcheck 掃——只認 path[:行號] 格式」  
問題：`path[:行號]` 並不是 refcheck 的充分格式。實作只掃 Markdown inline-code span，還要求 token 含 `/`，且第一段必須是 repo 當下存在的非隱藏頂層目錄；正文裸寫的 `scripts/lumos:2508` 即使形狀完全符合 `path:行號`，沒有反引號仍會被靜默略過。這個簡化會讓執行者以為「格式對就有掃到」，實際得到零 claims 的假綠。  
查證：`/tmp/node-restore-sop-v2-r2.md:138`；`scripts/lumos:10752-10775`

4. **major**  
引句:「金流/對外送出/不可逆的功能，禁止在生產環境跑會踩到情境；只准測試/沙盒環境」  
問題：第二條紅線只隔離「環境名稱」，沒有要求切斷真實外部端點、使用假帳號/測試憑證，或確認沙盒資料可重置。照字面可在連著真 webhook、郵件、簡訊或共享 staging 資料的「測試環境」真的送出或做不可逆操作。repo 自己對 scenario sandbox 的既有安全標準反而是拔 remote、假 hook、假身分三層切斷；此處標準更弱。  
查證：`/tmp/node-restore-sop-v2-r2.md:118`；`scripts/scenario_probe.py:80-89`

最嚴重 severity：blocker
