# 防刷 r1 架構席
A-1|major:rev 記在散文=同一版本化機制的第二種弱實作(考卷 rev=labels 內容 sha 自動算、換尺自動偵測);escape schema 無 rev 欄。
引句:「規則:改判準必升 rev」
B-1|minor:鹽分派演算法抄對 split_of,但 held 名單落地物(frontmatter/索引檔/散文)未定。
引句:「鹽分派=按 sha256(報告路徑+固定鹽字串)決定 train/held 歸屬」
C-1|major:人工 grep 審計=「蓋好沒人跑」八次教訓型;家內更強同形=t_precommit_whitelist_drift_guard(清單+grep 做成機械測試)。
引句:「審計時 grep 三帳檔名/記號在 scripts 與 orchestrator-prompt 的引用點」
抑噪:鹽分派非第二種做法;C 手動 grep 風格與 ★圖譜攔截★ 週看同款;誠實天花板已自承審計型。
severity: major
