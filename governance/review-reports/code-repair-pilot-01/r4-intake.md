# 使用者授權例外第4輪

沿code-repair-pilot-01及試行第1案，三輪歷史不重置。使用者聽取三個具體缺口與「再一輪」範圍後明確說繼續；授權記於試行計劃23:53:17事件。不改三輪機械規則、不新增名額。

## 修前根因／改變／保持

| id | 根因 | 要改 | 必須保持 | 配對基線 |
|---|---|---|---|---|
| r3 correctness F1 | 缺合法id的已發呼叫被略過，誤當完整零呼叫 | 畸形id形成unknown，不進有效分母 | 合法完成正證據present；完整零呼叫absent；有正證據仍優先 | 637989b1（code=4a60b231） |
| r3 boundary R3-B1 / security 1 | 清定位環境卻保留Git設定注入與使用者設定來源 | _git_env去command-scope config並封閉global/system設定來源 | PATH等非Git環境保留；副本自己的local hooksPath仍有效；兩runner一致 | 同上 |
| r3 security 2 | 只验来源gitdir，複製的絕對間接路徑可指回來源 | rsync後、任何Git寫入前驗副本gitdir、commondir及worktree實際落點 | 普通clone與安全的相對內部gitfile可用；拒絕時來源byte-equal、臨時副本清掉 | 同上 |

先補三組測試跑紅；涉及Git實驗只在臨時fixture，無網路、真模型或真push。前兩組屬既有4個修復根因组，第三組是本輪首次修復的Git間接路徑根因，第5組；同一缺陷双席不重算。新finding若出現按同例修前後分類，正式只加r4。

結果與收货欄待完成再填，入帳前凍結；不追加已綁定r3材料。
