preflight-4: ran

# code-android-ui-kind r2 收貨

審材:r2-snapshot.patch(703 行,2bdefa2da714976d1bfa9f0c15e9e55066682e71..46773fe6fed99c46625941a749229c15804186fe);修補差異 r2-repair.patch(391 行,f96ffe70 → 46773fe6);來源 r2-repair-binding.json(含 r1 fix-check 結果指紋,passed、沒有未執行項);配對案例 r2-behavior-cases.json;pitfalls 清單 r2-manifest.json(5 條內建隱患題)。
七席全新:正確性、資源、邊界、整合、通才、架構對齊、資安,全部 sonnet;七席都交回後才一起存檔(從各席逐字稿取原文)。這輪派工詞把最後一行改成「總結:最高嚴重度」,七份都已是正規化格式,沒有要更正的。
引句:邊界席 2 句有 1 句錨不到(引的是重跑腳本裡的一行,那支檔這次沒改、不在凍結 patch 裡),照規定機械重現(見下表 R2B2);其餘全錨。
正確性席報告末尾自述「曾短暫把審查用的工作樹切成 detached HEAD、隨即切回」,違反派工詞「git 一律 `git -C <臨時目錄>`」;收貨時核對:分支仍是 EnzoHsieh-Android/android-ui-kind、HEAD 46773fe6、git status 只有我的帳本與卷證、範本檔指紋跟 HEAD 版本相同,reflog 只多兩筆 checkout。沒有造成改動,記錄在案。
圖譜鏡頭:固定席有附,七席都逐條答;「授權與歸屬」的 ★INVARIANT★ 判不受影響(反向改壞驗紅)。

## 逐條重現與去向

| id | 席 | 嚴重度 | 重現 | 結果 | 組 | 去向 |
|---|---|---|---|---|---|---|
| R2C1 | 正確性 | minor | 範本把 `ORDER BY SUM(self_ns) DESC, name` 的 `, name` 拿掉,`-k android_ui_attribution` 照綠(席位報 47 passed) | HIT | G2-test | 折 |
| R2B1 | 邊界 | minor | sqlite3:幀 10ms → measure(dur -1)→ Compose:a 3ms,輸出 other 10、compose 0;我另算多一層已收尾 traversal 5ms 時四類加總仍是 10(席位說「多層時會超過幀長」不成立) | HIT(現象成立;加總超過的推論 MISS) | G2-test | 折:不改邏輯,補測試釘住「沒收尾區段底下的時間留給最近一個已收尾的祖先、四類加總等於幀長」,範本與計劃寫明 |
| R2B2 | 邊界 | minor | 範本整份貼進 queries.sql,`LC_ALL=C PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` 跑收據的 rerun.sh → `UnicodeEncodeError: 'ascii' codec can't encode characters`;預設環境回 `OK  Q1` | HIT | G2-enc | 折 |
| R2G1 | 通才 | minor | 讀 t_license_headers_travel_with_vendored_files:前置斷言要求複製清單裡有 .sql 範本;計劃 RETIRE-IF 撤掉範本時這條會紅,授權守衛本身沒壞 | HIT | G2-test | 折 |
| R2I1 | 整合 | minor | 計劃第 22 行的 WHY 仍寫「draw」(修補後只認框架的 draw 與 draw-VRI);SKILL.md L1 第 2 步 pipeline 名單少了 Record View#draw()、postAndWait、draw-VRI | HIT | G2-doc | 折 |
| R2I2 | 整合 | minor | 計劃「這三條與 draw 只認框架名稱…各有測試釘住」那行沒有測試名;`grep -rn receipt_rerun docs skills` 沒有命中 | HIT | G2-doc | 折 |
| R2I3 | 整合 | minor | 驗收紀錄 valid_under 寫「歸因查詢範本本次版本」,範本在驗收後改了 draw 規則,命中它自己的 revalidate_when | HIT | G2-doc | 折:用現行範本在實驗室真實 Trace 重算三種注入的 L1,更新紀錄 |
| R2S1 | 資安 | minor | 讀範本與 SKILL.md:`__PROCESS__` 的格式只由 skill 文字要求(推論,無直接攻擊路徑) | HIT | — | 放行:trace_processor 唯讀、只對指定 Trace 查詢;Android 套件名本身只允許英數字、底線與點;skill 已要求先確認、不合就停下問人 |

資源席、架構對齊席:clean。

## 根因分組與統一修法

- G2-test(3 條):測試釘住的是「現在剛好如此」而不是規則。修法:同分決勝補案例;沒收尾區段補案例並寫明規則;授權守衛的前置改成直接拿假檔名驗「照類型認註解符號」的判斷,不依賴真實清單有沒有 .sql。
- G2-enc(1 條):收據重跑腳本讀寫檔沒指定編碼,範本帶非 ASCII 字之後在非 UTF-8 環境崩潰。修法:重跑腳本所有開檔一律指定 utf-8(同一支檔一次掃完);收據重跑測試另在 LC_ALL=C 下再跑一次。
- G2-doc(3 條):修補改了規則,散落各處的說明沒有一起改。修法:計劃 WHY、skill 名單、測試名、驗收紀錄同一輪改齊;驗收紀錄用現行範本重算。

## 三問(席位回答的核對)

- 原問題修復:七席都以修前修後兩版各跑同一批輸入,r1 的 16 條都有行為證據(收據重跑修前 BAD Q1 rc1 → 修後 OK;NULL 名稱修前 other 4 → 修後加總等於幀長;draw、負數、授權守衛反向改壞都紅)。
- 相鄰路徑:正確性席 20 種改壞抓到 18 種(沒抓到的是同分決勝 R2C1,與 Perfetto 不會出現的形狀);資源席 30 萬區段修前修後同速。
- 未驗:七席都沒有 trace_processor,真實 Perfetto 上只靠我在實驗室 Trace 上跑的結果。

## 修補因果

regression_set:R2G1、R2I1、R2I2、R2I3(席位以兩版比對指出:前置斷言、計劃那行、驗收紀錄沒跟著改,都是 r1 修補新增或連帶造成);R2C1、R2B1、R2B2、R2S1 修前修後行為相同,屬原有漏查。
