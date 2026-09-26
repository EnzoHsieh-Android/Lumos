preflight-4: ran

# r1 前掃(便宜 agent 固定清單,2026-09-26)

前掃報 4 條,編排者重現後:

1. 「cap-reached 已實現,不是永遠到不了」、2.「委派舊閘是 rc=1、流程會繼續到 cap」——**重現不成立(MISS)**:
   `lumos loop next code-記憶索引大小守衛 --spec governance/review-reports/code-記憶索引大小守衛/r4-snapshot.patch` 直接取退出碼 = 2,印「擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」;loop next 判定段 rc==2 時直接 return 2,到不了 cap。計劃的說法成立,不改。
   (前一次在舊編號 intake 裡用管線 `| head` 取 $?,拿到的是 head 的退出碼;這次直接取。)
3. 處置閘還沒有 cap 報告、4. spec 優先序還沒改——這是計劃要做的,不是錯,不處置。

①②③ 無命中。沒有動到核心裁定。
