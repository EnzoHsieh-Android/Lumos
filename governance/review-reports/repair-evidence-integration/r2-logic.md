severity: major

logic-F1

severity: major

blocking: 是

觀察：S1 與 S2 對同一種「索引內容變更後恢復」的 ABA 軌跡規定相反結果。S1 要求以捕獲樹裁判，原始合法來源應通過；S2 卻要求設定、宣告或模式途中改回時撤回額外證據。固定樹與結尾樹相同時，實作者無法同時滿足兩條驗收測試。

獨立判準：同一輸入時序必須只有一個預期結果。設計必須明定二選一：

- 捕獲樹是權威快照，恢復至相同樹的 ABA 不撤證；或
- 任何觀測到的中途變動都撤證，即使最後恢復。

具體場景：捕獲時索引 A 內的測試內容、設定、安家宣告及模式全部合法；檢查途中索引變成非法 B，之後完整恢復成 A。結尾樹碼仍等於捕獲樹碼。S1 要合法來源通過；S2 要撤回額外證據。若該變更必須依靠額外測試路由，兩者分別導致 rc0 與拒收，會讓 `t_nodehome_optional_test_index_aba` 和 `t_nodehome_optional_test_input_snapshots` 的裁判互相衝突。

引句:「當暫存區途中改动又還原時，home檢查的額外測試路由應只用捕獲樹及起點作證；非法來源仍拒收，合法來源仍通過。」

引句:「當捕獲失敗、來源設定或宣告或模式途中改回、工作樹變動時，額外測試路由應保守撤回且不更改正式程式退路及逐提交核對。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:39`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:40`

逐項覆蓋／未驗邊界：

- 已覆蓋固定樹捕獲、ABA、捕獲失敗、輸入快照、工作樹競態、正式 index 路徑保留、來源留存、五份計劃及指定現行函式。
- 真 spec 與凍結副本位元一致，SHA-256 均為 `eb0bf3f6531bed5c1c20c808512d72f40781cc1d93200a845b8d878ea61ffe8c`。
- 未讀其他席、前輪報告或作者修復因果結論；未將待實作內容當作現況；未執行專案或外部程式。
- 未驗未來實作與動態測試結果；判定只針對凍結 spec 的內部正確性。

實際閱讀帳：

- `r2-materials.md`：唯一行 1–1194；因工具截斷補讀時重疊 1039–1040，實讀出現 1196 行。
- 唯一真 spec：1–76，共 76 行。
- 凍結副本：1–76，共 76 行。
- `lumos-design-loop/SKILL.md`：1–79，共 79 行。
- 行數、雜湊及一致性輸出：8 行。
- 內容合計 1435 行；連同可見工具標頭與截斷提示保守計 1441 行，未超過 1800 行。搜尋輸出 0 行。

最高級：major；blocking 數：1。