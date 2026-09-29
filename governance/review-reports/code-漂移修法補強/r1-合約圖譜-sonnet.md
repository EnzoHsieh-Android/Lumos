severity: minor

## F1 lumos help 裡 drift fix 那句一行說明沒跟著改
severity: minor
blocking: 否
引句:「c3 `--status <值> [--by <節點>] [--reason "…"]`(`--reason` 選填,接在補的那一行最後;要新版工具,消費專案先 `lumos update`)」
file: `scripts/lumos:36820`
1. 這批 diff 把 commands/04 說明頁的 c3(加 --reason)與 c4(只列證據、給範本與預填 set 指令、不進修復帳)都改寫了,argparse 的 `--reason` help 也改了。
2. 但 `scripts/lumos:36820` 的 `"drift fix"` 一行說明(`lumos help` 類的指令總表)仍寫「c3 改狀態加一行、c4 換掉還沒提交的前提」:沒提 c3 可帶 --reason,且 c4 已不是「換掉」而是只列證據由人走 lumos set。該行不在 patch 內(未被修改),重現:`grep -n '"drift fix":' scripts/lumos`。
3. 影響僅是說明文字過時(c4 那半句在本批之前就已偏),不影響行為與合約。

## 圖譜鏡頭逐條判定
- 授權與歸屬 ★INVARIANT★(授權檔不得進 _VENDORED_TOOLKIT):不影響。diff 只在刪除守衛「讀」`_VENDORED_ALL` 當跳過清單,沒改 `_VENDORED_TOOLKIT` 或 deinit 的 unlink 邏輯;跳過清單只讓更多路徑被略過,不會刪任何檔。
- guard-kill 兩條 ★INVARIANT★(rc 優先序、--json 純度):不影響。改動只在 `_guard_settle_missing_say` 的措辭與回傳(原本無回傳,現回清單;settle 兩個呼叫端維持預設 say=True、仍印到 stdout,與原本相同),guard kill 的 rc 判定與 JSON 路徑沒被碰。guard-kill 新增的 WHY 行帶出處與 [test:t_drift_fix_c1_missing_message](測試存在),舊 FACT 行改成 WHY 符合前綴規則。
- 測試假綠形態(還原翻紅釘要配前置斷言):不影響既有綁定;新測試我未逐支跑翻紅,不在本席範圍,未提 finding。
- bound-tests-gate / lumos-cli-read / lifecycle / design-loop:不影響。沒改這些節點宣稱的閘、search 濾網、re-inject、處置閘。
- 圖譜筆記與 commands 頁一致性:delguard(vendored-skip 記帳、純路徑、工具鏈照抽)、lumos-cli-write(<卷證>、<sha> 佔位字)、存量漂移守衛(c4 兩來源、c3 --reason、TEST 清單含新測試,「見下面 c4 那條 PITFALL」指的 PITFALL 存在)與程式一致;commands 03/04/08 與程式行為一致,03 的三個佔位字與 `_SET_COND_SLOTS` 相同。
- 筆記前綴規則:新增行皆為 WHY/PITFALL 型帶出處與測試,沒有無來源的 FACT/FLOW/DEP,沒有寫別人家的檔路徑(delguard 節點的「消費專案跳過…」節用自然語言,未貼別檔反引號路徑)。delguard 的 REVISIT 行緊鄰原句,符合鐵則 4。

最高等級:minor
