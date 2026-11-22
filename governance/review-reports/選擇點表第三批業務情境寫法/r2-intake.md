# 選擇點表第三批業務情境寫法 r2 收貨

席位:正確性、邊界、整合、資源併發、回滾、架構對齊,全 sonnet,全新代理,派工詞寫明不讀 r1- 開頭的檔;各自只讀凍結快照 r2-snapshot.md(spec_commit 25d5dcef…)。六份收齊後才一次從逐字稿存檔;收齊前沒動計劃真檔與工作目錄。
收貨三道:六份都已是正規化格式;引句全數錨定;refcheck 只有架構對齊席一條 `configs/ast-grep/kotlin-choice/../kotlin-android/check.py:1394` 判 missing——那是繞一圈的相對寫法,實際檔 `configs/ast-grep/kotlin-android/check.py` 第 1394 行是 `CHOICE_ANCHORS`,內容對,照收。
reflog 只有編排者自己的提交;席位沒留 worktree;這一輪臨時目錄收齊後已刪。

發現共 28 條:正確性 c1–c3、邊界 b1–b6、整合 i1–i7、資源併發 r1–r3、回滾 rb1–rb6、架構對齊 a1–a3。blocking 4 條(c1、r1、rb1、rb2)。

## 重現表

| id | 席 | 等級 | 編排者重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 | major | HIT(讀規則語意):命中是作用域識別字,`inside` 只能從子協程往外找,數不出「兩個」;席位與邊界席 b1 各自實跑 has 加 precedes 才寫得出 | 折:範圍 2 寫明往下 has、precedes 配對、迴圈那一支與固定鏈 |
| b1 | 邊界 | minor | HIT:同 c1 | 折:同 c1 |
| r1 | 資源併發 | major | HIT:編排者實跑「命中每個 launch、往上 inside 到作用域」的寫法,6.5KB 平鋪 300 個 `launch` 輸出 16,958,900 位元組;同一條規則外包 `not: {not: …}` 輸出 136,950 位元組,命中都是 300 處。(從作用域識別字往下 has 的寫法同一檔 71KB——輸出量看寫法,計劃原文「用 inside」字面上指向會爆的那種) | 折:範圍 2 強制雙重否定、S9 合成輸入測試 |
| c2 | 正確性 | minor | HIT:同 r1 | 折:同 r1 |
| b4 | 邊界 | minor | HIT:同 r1 | 折:同 r1 |
| i4 | 整合 | minor | HIT:同 r1(規則包 PITFALL 第 99、102 行) | 折:同 r1,範圍 2 引用那兩條 PITFALL |
| a3 | 架構對齊 | minor | HIT:同 r1 | 折:同 r1 |
| rb1 | 回滾 | major | HIT(讀測試):`t_choice_points_batch2_stable` 只釘第一版六支樣本檔、用正規式排除第二批語法行;計劃 r1 折入要求另釘 `choice-batch2.kt` | 折:S7 改回照第二批做法、只釘第一版樣本 |
| rb2 | 回滾 | major | HIT(讀程式):`_render_gov_choice` 依列號只印計數;沒有取消放行的子指令 | 折:回退第 3 項改成從治理帳篩列號、手改放行檔,寫 REVISIT;補殺掉外溢 |
| rb3 | 回滾 | minor | HIT(讀 `_choice_kill_pick` 對已處置行直接 done) | 折:RETIRE-IF 補計數偏少的說明 |
| rb4 | 回滾 | minor | HIT(讀計劃範圍 1、6) | 折:回退第 2 項逐一列出要改回的文件 |
| rb5 | 回滾 | minor | HIT(讀條款綁定) | 折:拆出 S10 綁 `t_choice_samples_batch2` |
| rb6 | 回滾 | minor | HIT(計劃日期 2026-11-21 加兩個月) | 折:REVISIT 改 2027-02-28,範圍 6 補上線當天改日期 |
| i5 | 整合 | minor | HIT:同 rb6 | 折:同 rb6 |
| i1 | 整合 | minor | HIT(讀 `_choice_iv_cover` 收位元組位移) | 折:乾節點覆蓋不改、寫明理由;只有 ERROR 判斷依錨點分流 |
| a1 | 架構對齊 | minor | HIT(讀 `_choice_file_points`) | 折:範圍 3 寫明這是第一個依錨點分流的覆蓋判斷與理由 |
| a2 | 架構對齊 | minor | HIT(讀計劃〈用詞〉原則) | 折:`_choice_also` 條件改看列的「需補的 import」欄 |
| i2 | 整合 | minor | HIT(讀 test-templates.md:FLOW-23、FLOW-24、API-8 有對得上的範本) | 折:實務隱患與 REVISIT 改正範本清單 |
| i3 | 整合 | minor | HIT(讀母計劃〈範圍〉API 條目、型錄統計括號) | 折:範圍 6 補兩處同步 |
| i6 | 整合 | minor | HIT(型錄表頭沒有原寫法欄) | 折:S6 寫明原寫法取自候選欄的另一個名稱 |
| i7 | 整合 | minor | HIT(讀 `_choice_err_cover` docstring) | 折:天花板第 3 條寫明 |
| b2 | 邊界 | minor | HIT(讀〈用詞〉只數個數) | 折:實務隱患改說法、天花板第 3 條寫明互斥分支 |
| b3 | 邊界 | minor | HIT(席位實跑) | 折:天花板第 3 條補巢狀迴圈、do-while、完整套件名 |
| b5 | 邊界 | minor | HIT(讀型錄表頭與 check.py) | 折:欄位名改成「為什麼行為不同」 |
| b6 | 邊界 | minor | HIT(非空型別接 `?:` 是 USELESS_ELVIS 警告;席位標未實編,編排者也沒實編) | 折:實務隱患編不過那條補 toIntOrNull 三列 |
| c3 | 正確性 | minor | HIT(讀範圍 1 前後兩條) | 折:改寫 single 兩列的理由、說明段同步補觸發字表兩格 |
| r2 | 資源併發 | minor | HIT(現象,席位實測巢狀 300 層 26 秒) | 折:實務隱患記數字與既有行為 |
| r3 | 資源併發 | minor | HIT(讀 `_LINT_SARIF_MAX_BYTES` 64MB) | 折:實務隱患寫清 64MB 與 16MB 的關係、鏈長數字改成實測 |

## 分組(依根因)

- 作用域規則怎麼寫(c1、b1;r1、c2、b4、i4、a3):數「兩個」的結構與輸出量——第 1 輪 b2 之後第二次被打到,本輪有 major。
- 回退與撤列(rb1、rb2、rb3、rb4、rb5、rb6、i5):第 1 輪 rb1 之後第二次,本輪有 major。
- 覆蓋判斷與補 import 的分流(i1、a1、a2)。
- 規則漏判與天花板(b2、b3、i7)。
- 文件與說法(i2、i3、i6、b5、b6、c3)。
- 資源既有行為(r2、r3)。

## 先查世界

- PRIOR-ART:數「兩個」——ast-grep 關係規則文件列出 inside、has、follows、precedes 四種與 stopBy,沒有計數;`precedes` 是「目標在子規則節點之前」(https://ast-grep.github.io/guide/rule-config/relational-rule.html 、https://ast-grep.github.io/reference/rule.html )。採用:配對兩個含子協程的兄弟。
  方向:對 — 兩席各自用 has 加 precedes 寫出、樣本逐型核對一致;雙重否定是專案已驗過兩次的輸出修法(Systems/kotlin規則包 第 99、102 行 PITFALL),本輪編排者實跑命中集合不變、輸出降兩個數量級。來源:上面兩個 ast-grep 文件網址。
- PRIOR-ART:撤列後的處置重用——Stryker 增量模式以每個壞法為單位重用上次結果,被殺掉的要殺手測試還在且沒變、存活的要沒有新測試蓋到它且測試沒變(https://stryker-mutator.io/docs/stryker-js/incremental/ );回歸變異測試 ReMT 用靜態分析判哪些「壞法-測試」組合的結果能沿用(https://userweb.cs.txstate.edu/~rp31/papersSSE/regrMuteTest.pdf )。
  方向:要換(處置鍵)— 世界做法以壞法為單位重用、測試改了就作廢;本工具以行為單位是第一版的取捨,而且「處置鍵帶列號或壞法雜湊」在 Systems/規格閘 被否決過。這一批不換、照實寫進〈回退〉第 3 項與 REVISIT,要不要另開計劃改處置鍵攤給人裁(收尾報告時提)。
- 不加新機制的最小解:這輪沒有新增機制(S9、S10 是測試,REVISIT 是回頭條件);乾節點覆蓋判斷原本打算分流,改成不分流,少一個機制。
