# 威脅類別表 v1 雙家協定卷證

依 [[Projects/資安風險提問分階段_計劃]] d5:威脅類別表的核可由 Claude 與 Codex 兩家各自獨立審、意見一致才核可。v1 走了三輪:初審兩家都「修改後可核可」→ 合併定稿 → 第一次確認兩家都不可核可(4 條必改已改)→ 第二次確認 Codex 可核可、Claude 1 條必改已改 → 增量確認兩家都「可核可」。

- 原草案:`threat-table-v1.md`;改前留底:`threat-table-v1-final-r2.md`;定稿:`threat-table-v1-final.md`(sha256 48e5c0ef33c3d8a456c32b0c1b609e57dc6e446496945d907243ce3d5aaa70c4;〈定稿表〉那一節是 Systems/資安威脅類別表 的正本內容)。
- 派工詞:`threat-review-prompt.md`、`threat-confirm-prompt.md`、`threat-confirm2-prompt.md`、`threat-confirm3-prompt.md`。
- Claude 報告(整份):`threat-review-claude.md`、`threat-confirm-claude.md`、`threat-confirm2-claude.md`、`threat-confirm3-claude.md`。
- Codex 報告:原檔是整段執行紀錄(每份 100–470KB),**已截取結論段**——只存每份最後一個以「結論: 」開頭的行到檔尾,檔名前加 `codex-`。原檔不進 repo,sha256 記在下表供對照:

| 原檔 | 原檔 sha256 | 原檔位元組 | 截取起始行/總行數 | 截取檔 |
|---|---|---|---|---|
| threat-review-codex.md | 04c132c89663090689601f879adae799668260385ce7840e7ba4b9c7ac6bff5b | 337334 | 1733/1914 | codex-threat-review-codex.md |
| threat-confirm-codex.md | 4c30962549f402ec3fd5f410ae93b76f76931b7e6496e4a0a1e063f42e04ed5c | 473557 | 2667/2706 | codex-threat-confirm-codex.md |
| threat-confirm2-codex.md | 82228ca2acb1068d38a6a06536a08ae1b7c38d7486a9e3ce18a04833cfb4f84a | 391822 | 1909/1931 | codex-threat-confirm2-codex.md |
| threat-confirm3-codex.md | 10a507a5e5b19ad6a7a8690ac320d9be96c9f58c0ac481eb37c1db35f6dd6829 | 96450 | 465/472 | codex-threat-confirm3-codex.md |

核可範圍:表核可只代表類別對照定稿,不代表閘門已完成連動,也不代表任何消費專案通過資安驗收;「單人專案作者無法自審、需非作者的人審」仍是未解待辦。
