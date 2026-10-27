severity: clean

零 finding。本輪只有一個修補:`scripts/lumos` 的 `_e2e_note_gaps` 把正文提到路徑的後邊界從 `[A-Za-z0-9_-]` 擴成 `[A-Za-z0-9_/-]`,另在測試補一個例子。

## 已驗主張

**repair 案例:正文寫 `.maestro/login.yaml/x`。**
- 預期:不算提到,`login.ok` 要列進 `cases_without_notes`。
- 修前:在乾淨 clone 的 9c28eb9e 加上修後的 `scripts/test_lumos.py`,執行 `python3.14 scripts/test_lumos.py -k cases_without_notes`。結果是 `✗ … 流程是 .maestro/login.yaml/x → login.ok 照列`,`cases_without_notes` 只有 `['other.x']`,測試 FAILED。這證明修前把它誤判成有提到。
- 修後:同一個命令在 `e2e-case-note-link` 的 73cfe068 上執行,`-k android_e2e_coverage` 共 50 passed、0 failed。
- 歸因:有證據的修復。

**preserve 案例:仍算提到。**
- 我另外直接拿新舊兩條 regex 各跑一次。
- `.maestro/login.yaml。`、`` `./.maestro/login.yaml` ``、`(.maestro/login.yaml)`、行尾(有換行和沒換行)、`.maestro/login.yaml.`、`.maestro/login.yaml、…` 這幾種,新舊都是命中。
- 加入測試的負例 `old/`、`.bak`、`x.` 前綴,新舊都不命中。
- 修前 9c28eb9e 的測試裡這幾個 preserve 例(`` `./…` ``、`。`、`(…)`)都通過,只有 `/x` 那條紅。修後全綠。

**相鄰行為。**
- 路徑後面接 `/` 的字串(`.maestro/login.yaml/`、`.maestro/login.yaml/ok`、中文緊貼 `…yaml/再`)修前算命中,修後不算,與規格「結尾邊界」一致。
- 前綴邊界、`./` 開頭、中文緊貼的行為沒變。

**目錄型 flows 沒有回歸。**
- 我找過「flows 填目錄、筆記寫 `dir/`」會不會因為後面多了斜線而被誤判成沒提到。
- 對照表的 flow 名是「相對路徑去副檔名」,`_e2e_norm` 先去掉尾端 `/`,設定也要求檔案路徑。所以 flows 裡不會有目錄型條目,這個疑慮不成立。
- 就算有目錄型條目,修前的 regex 對 `dir/login.yaml` 也不會命中,所以不是修補造成的。

## 三問

1. 原問題有修好嗎:有。`/x` 例在修前紅、修後綠。
2. 修補處的正常、錯誤與相鄰路徑還成立嗎:成立。preserve 例與負例都沒變。唯一的行為差異是「後接斜線」改成不算提到,這是預期的修改。
3. 同一案例在修前、修後各是什麼:`.maestro/login.yaml/x` 修前不列(誤判成有提到),修後會列。其他 preserve 例修前修後都不變。

## 未驗範圍

- 沒有重審第 1、2 輪的其他 hunk。圖譜鏡頭與角色卡(未附卡)沒有逐題展開。
- 本輪修補沒有碰 `_platform_name_files` 與 `_residual_test_files`,所以那部分只依賴既有測試通過,我沒有另外驗證。
- 圖譜鏡頭那邊,修補的筆記改動只是計劃筆記多一行修正紀錄,沒有改合約行。
- 清理:我刪了自己跑修前測試留下的現場 `gctl-run-rgn830ft` 和臨時 clone。`/var/folders/tc/…/T/` 底下還有很多不是我建的 `gctl-run-*`,我沒碰。第二次重跑修前測試時也可能留了一個,但無法確認是哪一個,所以沒刪。

共 0 條,其中 major 0 條
