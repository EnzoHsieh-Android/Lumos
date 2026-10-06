severity: clean

1. 分層與依賴方向：對齊。方案由既有 `cmd_home_check` 負責固定版本的編排，再把樹碼交給既有 `_nodehome_list`、`_nodehome_reader`、`_nodehome_changes` 等 Git reader；沒有跨層直呼或新增快照層。

引句:「索引模式先用write-tree捕獲固定樹。可捕獲時，改動清單、設定、圖譜與分類讀同一樹」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-snapshot.md:31`

必要佐證：`r1-materials.md:778`、`r1-materials.md:812`、`r1-materials.md:846`、`r1-materials.md:877`

2. 命名與錯誤處理：對齊。捕獲失敗仍回到既有正式檢查及 fail-open 邊界；沒有另立例外模型、回傳型態或日誌通道。

引句:「捕獲失敗不借額外證據，保留原正式程式檢查退路，不修改安家集合、每提交規則或fail-open政策」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-snapshot.md:31`

必要佐證：`r1-materials.md:925`、`r1-materials.md:928`、`r1-materials.md:979`

3. 第二種做法：未發現。固定樹明確沿用既有 Git reader；來源留存、修補配對、1800 行與因果判讀也擴充既有共用範本 §3.1，沒有建立平行裁判或另一套快照格式。

引句:「沿用現有Git reader而不自建快照引擎」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-snapshot.md:26`

必要佐證：`r1-materials.md:1016`、`r1-materials.md:1033`、`r1-materials.md:1040`

4. 落點責任：對齊。CLI 固定樹歸 `Systems/每支檔有家`，修補及來源證據流程歸 `Systems/每輪修補差異派工`，測試假綠與 ABA 控制歸 `Systems/測試假綠形態`，未見責任外溢。

引句:「落點 Systems/每輪修補差異派工、Systems/每支檔有家、Systems/測試假綠形態」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-snapshot.md:24`

未驗邊界：

- 固定樹尚未實作；本席只依待實作方案判讀，沒有宣稱行為已驗。
- 材料未提供三個落點節點的現有行數、KEY 數與管檔數，因此容量是否已大到需要拆節點維持未判定；目前沒有第二種做法或越權證據，故不列 finding。
- 各計劃的既有綠筆記與驗證入口未被當作本次整合已通過的證明。

實際閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行。
- 真 spec：67 行。
- snapshot：以 SHA-256 證實與真 spec 完全相同，未重複讀取 67 行。
- `r1-materials.md`：完整 1185 行；因首次輸出截斷，補讀 120–360，共重讀 241 行。
- 行數及雜湊盤點輸出：7 行。
- 合計：1579 行。
- 未讀其他席、前輪報告或作者修復因果結論；未執行外部代碼，未修改 repo、帳號或 git。

不對齊共 0 條，其中 major 0 條。

最高級：clean；blocking 數：0