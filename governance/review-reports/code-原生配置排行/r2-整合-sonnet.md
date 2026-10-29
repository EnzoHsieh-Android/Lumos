severity: minor

我逐句對照了兩份 patch 與程式(版本 07642d8e)。沒有 blocker 或 major。文件裡的設定鍵名、`"@default"`、環境變數名、檔名、失敗原因字樣和印出字樣都對得上程式。`[test:]` 綁的測試名全部存在於 `scripts/test_lumos.py`,我用腳本逐一核對過。但有 5 條文件與實作沒對齊的小地方。

1. 收集腳本「回 2」的清單沒跟上修補新增的兩條擋下路徑
severity: minor
blocking: 否 因為只是清單不完整,照文件做不會做錯東西(只影響排查時的預期)。
引句:「其餘情況都寫出結果檔並回 0」
file: `scripts/templates/android-stability-collect.sh:406-408`(少了範本就 `die`)、`:675`(`LUMOS_STABILITY_STEP_BUDGET_S` 不合法就 `die`)、同檔檔頭 `:13-14` 的回傳碼註解
歸因:有證據的修復回歸。修前 84b487f2 沒有這兩條 `die`,修後新增了。兩處舊句子(`Android記憶體與穩定性驗收_計劃.md` 第 2 步、檔頭註解)都沒改。
場景:接手的人讀到「其餘都回 0」。他把 `LUMOS_STABILITY_STEP_BUDGET_S=abc` 設在環境裡,或只抄了收集腳本,而且 `native_retained` 有列出該情境。結果收集腳本回 2,而且不寫結果檔。這和文件說的相反。第一種情形下,即使這次情境沒打開 `native_retained`,也會被擋下。

2. `native_run` 的 docstring 還是舊的停 App 順序
severity: minor
blocking: 否 因為是程式註解與計劃的措辭不一致,行為沒錯。
引句:「停 App → 讀結束紀錄 → 啟動 → 讀 pid → 暖機 W 輪」
file: `scripts/templates/android-stability-collect.sh:589`(docstring 寫「停 App → 啟動 → 讀結束紀錄與 pid」)、`:481-488`(`fresh_launch` 實際是停、讀結束紀錄、啟動)
歸因:有證據的修復回歸。修前程式本身就是「停、啟動、讀結束紀錄」,docstring 與程式相符。修後計劃和程式都改成先讀結束紀錄再啟動,docstring 沒跟著改。
場景:三個月後的人拿 docstring 對照計劃,會以為停 App 那筆結束紀錄會被算進「前」的快照,於是懷疑 S7 的「第二段期間 App 結束」判法。

3. skill L0 新增的「照抄進收據的提醒」沒有規格依據,「前幾名」與「提醒」都沒定義
severity: minor
blocking: 否 因為是未定義的詞,AI 照做時只是格式不確定,不會做出會擋推送的結果。
引句:「把前幾名照抄進收據的提醒」
file: `skills/lumos-android-evidence/reference.md:5-50`(manifest 欄位只有 `layers`、`gaps`、`contract_refs`,沒有「提醒」欄位);`docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md` 的「打算怎麼做」第 7 步與 S19 只寫「L0 的往下條件不變」和 L3 那段,沒有「L0 通過時照抄排行」這條。
歸因:有證據的修復回歸。`git show 84b487f25d` 的 SKILL.md L0 句子沒有這段,`23c0d065` 才加進去。
場景:AI 在 L0 通過時照這句做,但收據裡沒有「提醒」欄位可寫,「前幾名」也沒有數字。lumos 印 20 個,`--json` 帶 200 個,AI 可能抄 3 筆也可能抄 200 筆。計劃的 S19 只管 L3 那一半,L0 這一半沒有條款也沒有測試。

4. skill L3 把「結果檔沒有 native_retained 段」放在 `enabled` 是 true 的括號裡
severity: minor
blocking: 否 因為兩種情況的處置相同(都手動錄),只是描述不精確。
引句:「reason 寫了為什麼,包括」
file: `scripts/lumos:40075`,結果檔沒有這段時回的是 `_macrobench_native_off(...)`,`enabled` 是 false(`:40052`)。
歸因:有證據的原有漏查。修補沒碰這句,修前修後文字相同。
場景:讀者找不到「enabled 是 true 而 reason 是結果檔沒有這段」這種組合,因為實際上不會出現。這和計劃第 7 步把它單獨列出來的寫法也不一致。

5. 驗收計劃的結果檔欄位清單漏了第二段實際寫的欄位
severity: minor
blocking: 否 因為是精度問題,不影響判定。
引句:「ok 時加 main_process_only 與 sites,沒打開時 enabled 是 false」
file: `scripts/templates/android-stability-collect.sh:622-623`,`native_run` 還寫入 `pids`、`driver`、`exits_new`(`sec.update(pids=..., driver=..., exits_new=new)`)。`原生記憶體增長提示_計劃` 的「打算怎麼做」第 3 步有說這些欄位寫在新段落裡,但這份欄位清單沒列。
歸因:有證據的原有漏查。修補沒碰這句。
場景:有人依欄位清單寫結果檔驗證或第三方讀取,會以為段落裡只有 `enabled`、`status`、`reason`、`main_process_only`、`sites`。

**三問**

① 原問題的修復效果:修補範圍內的四項文件宣稱,都找到程式上的對應。
- 預算的三條規則:`:582-585` 的預估公式,`:669-675` 擋 nan/inf/0/負數/非數字,`:676` 與 `:591-593` 的 `deadline` 和 `left()` 扣 180 秒。
- 少範本擋下:`:406-408`。
- 長名字與超大整數不會把「還留著多少」截掉:`scripts/lumos:40105-40108` 的三段各自截、整數算 MiB。
- ERROR 偽框架:SQL 的呼叫者與並列排序規則,和計劃相符。

這些是靜態對照,我沒有實際執行測試。

② 修補處的正常、錯誤與相鄰路徑:
- 原生配置排行沒打開的路徑沒變:`native_on` 為 false 時,`preflight` 不查範本也不查兩個新檔名的 git 忽略。
- 第二段共用 `fresh_launch` 後,第一段的順序沒變。
- 退回四種版本錯配的說法,與程式對得上。舊版 lumos 的 `_macrobench_stab_cfg_err` 只驗已知鍵,因此忽略 `native_retained`。舊收集腳本配新 lumos 時,`_macrobench_native_off` 回「結果檔沒有 native_retained 段」。
- 新收集腳本單獨抄進消費專案時,錯誤訊息教人 `lumos update`。`lumos update` 確實會把 `_VENDORED_TREE_FILES` 補進專案(`scripts/lumos:32256`),範本也已登記在 `:31980-31981`。
- 這條路徑上唯一偏離的是第 1 條:新增的 rc 2 路徑沒進清單。

③ 新發現在修前和修後各是什麼結果:
- 第 1 條:修前 `die` 只有舊的幾種,文件清單與程式相符。修後多了兩種,清單沒改,所以不一致是修補造成的。
- 第 2 條:修前 docstring 與程式順序相符,修後不符。
- 第 3 條:修前 SKILL L0 沒有照抄這句,修後才有。
- 第 4、5 條:修前修後文字相同,是原本就有的問題。

總結:最嚴重為 minor,blocking 0 條。
