# r1 收貨紀錄(選擇點變異常駐切換最小實驗)

preflight-4: ran

## 前掃(便宜代理,固定清單四項;直接修真檔,不算 findings)

- ①未定義詞:壞法、守的測試、殺/存活、PIT、Robolectric、第四段、T68、卷證、AI 自定 → 正文補定義與連結(第四段連到 [[Projects/選擇點變異加速第四段_計劃]];T68 改寫成實際原因;卷證寫明目錄)。
- ②壞引用:Robolectric 架構文件舊網址已搬家 → 換成 https://robolectric.org/architecture 。
- ③範圍矛盾:停手條件「不到一半」與第二步「過一半」在剛好 50% 都不涵蓋 → 改成「小於 50% 否決;50% 含以上做第二步」。第二步「同 5 個」沒指定 → 寫明從第一步 10 個裡挑同一支檔的 5 個、不夠就補。

## 語意類命中(修改前 → 後)

- METFORD:前「每個壞法仍重開一次測試程序(真機或模擬器上重裝重跑),省的只有編譯」→ 後「app 只裝一次、每個壞法仍各跑一次測試,省的是建置與安裝,執行那段沒變」。依據:論文原文只推送安裝一次 app、模擬器不可用時才重啟(https://arxiv.org/html/2501.02875v2 )。〈跟舊否決差在哪〉的論證改成「我們的時間是不是大半在 Gradle 啟動與 Robolectric 初始化,待量」。PRIOR-ART 行同步改。
- 平均秒數:前「批 4a 實測一個壞法平均約 30 秒」(沒出處)→ 後「2026-11-27 批 4a 正式重跑 80 個壞法共 3681 秒,平均約 46 秒」。預期值表 S5 的例子同步改 46 秒。
- 量法:前「Gradle `--profile` 給編譯與設定時間,第四段初始化腳本的測試事件給初始化與測試時間」→ 後「實驗自帶初始化腳本印各段牆上時間(毫秒)」。依據:`--profile` 官方文件沒寫分項;第四段腳本只設 events、不帶時間,且只掛合併呼叫(scripts/lumos 的 _CHOICE_MERGE_INIT 與 _choice_merge_cmd)。
- PIT:前「測試程序常駐不重開」→ 後「壞法保存在記憶體換位元組碼、不寫入磁碟,也不必重開 JVM」(照 https://pitest.org/faq/ 原文)。

沒有動到核心裁定(重開與停手條件的方向不變)。

## 收貨

四席(正確性、邊界、整合、架構對齊)全數交回後才一次從逐字稿存檔,四份都已是正規化格式、引句全數錨定。另一份計劃(選擇點挑法易混淆寫法優先)的整合席退回改一行引句格式的期間,本計劃已開始改寫;那一席審的是另一份計劃的凍結快照,沒有讀到本計劃改過的內容。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | 停手分子漏掉編譯,常駐一次編譯能省的那段沒算 | 折:改成「可省 = 總時間 − 測試時間」,編譯、設定、JVM 啟動、首次沙盒都算可省 |
| c2 | 正確性 F2 | major | 四段量法量不出它說的四段 | 折:改成只切兩份(T 與 Σt),用官方 afterTest 時間 |
| c3 | 正確性 F3 | minor | 50% 門檻跟 RETIRE-IF 的快一倍互相矛盾 | 折:門檻改 0.6(理論上限 2.5 倍) |
| c4 | 正確性 F4 | major | 5:5 取樣與「平均」定義會偏掉停手判斷 | 折:定義十次合計比(總和比);明寫不外推到 choice-kill 母體 |
| c5 | 正確性 F5 | major | 開關失效時判定會假一致 | 折:每次呼叫讀屬性、正控制(已知被殺要紅)、壞寫法 diff 對照、判定三種 |
| c6 | 正確性 F6 | major | 原型平均秒數沒定義攤提 | 折:一次性成本與邊際時間分開記 |
| c7 | 正確性 F7 | minor | 數字出處與〈不做〉表位置不對 | 折:改指〈依據來源〉那列與 PRIOR-ART 排除句 |
| b1 | 邊界 B1 | major | 現行每個壞法不是單次 Gradle 呼叫 | 折:量測不經 choice-kill,〈用詞〉定義一次呼叫 |
| b2 | 邊界 B2 | major | 平均對雙峰分布與 50% 邊界沒規則 | 折:每個壞法 3 次取中位數、用總和比、門檻 0.6 |
| b3 | 邊界 B3 | major | 冷啟動污染第一個樣本 | 折:做法第 0 步暖機兩次丟掉、量測期間不跑別的 Gradle |
| b4 | 邊界 B4 | major | 同一支檔挑 5 個可能湊不齊 | 折:10 個取自最多兩支檔、第二步至少 2 殺 2 存活、補進來的也拆帳 |
| b5 | 邊界 B5 | major | 常駐原型裡壞法掛住沒死亡處理 | 折:每個壞法限時、逾時就結束原型另起 JVM |
| b6 | 邊界 B6 | minor | S3 兩邊結果格式不同 | 折:轉成「類別.方法 → 結果」清單比 |
| b7 | 邊界 B7 | minor | 只改一處否決會留下矛盾 | 折:〈落點〉寫明否決改兩處、值得則另開計劃處理兩篇 |
| b8 | 邊界 B8 | minor | 回退沒涵蓋臨時工作樹與治理帳 | 折:回退寫明刪臨時工作樹、不經 choice-kill 不寫帳 |
| i1 | 整合 I1 | major | 46 秒在圖譜查不到出處 | 折:改引第四段計劃的實測 FACT(142 個 14197 秒),實驗自己量基準 |
| i2 | 整合 I2 | major | Robolectric 每支測試前都初始化,不是一次性 | 折:每支測試的初始化算進省不掉的 Σt |
| i3 | 整合 I3 | major | 同一個 JVM 掛住會卡死 | 折:同 b5 |
| i4 | 整合 I4 | major | 對照與平均口徑沒定 | 折:同 c4、c6 |
| i5 | 整合 I5 | minor | 〈不做〉表位置寫錯 | 折:同 c7 |
| i6 | 整合 I6 | major | 要寫回的筆記清單不全 | 折:〈落點〉補驗證紀錄、FACT 寫法、通知挑法計劃、兩篇舊否決的處理 |
| i7 | 整合 I7 | minor | 逐測試覆蓋出處標錯、程式化 JUnit 是換執行引擎 | 折:數字整句換掉;〈不做〉寫明換執行引擎要另開計劃人裁 |
| i8 | 整合 I8 | minor | 自帶腳本只能塞進 run_cmd | 折:量測不經 choice-kill、run_cmd 不動 |
| i9 | 整合 I9 | minor | METFORD 是真機儀器測試,類比沒寫出來 | 折:〈跟舊否決差在哪〉寫明真機儀器測試與 JVM 本機測試的差 |
| a1 | 架構對齊 A1 | major | 實驗結果放審查卷證是第二種做法 | 折:改寫成 Verification 筆記 |
| a2 | 架構對齊 A2 | minor | 總時間來源沒說 | 折:不經 choice-kill,T 由外層取時間、Σt 由 afterTest |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| c1 | 讀做法第 1 步與停手條件:分子只取兩段,第 2 步原型確實省掉編譯 | HIT |
| c2 b1 i4 | scripts/lumos 的 _choice_merge_cmd 只在合併呼叫插初始化腳本;第四段計劃寫逐支重跑 | HIT |
| i1 | 全 repo 搜 3681 只中雜湊;第四段計劃 FACT 是 142 個 14197 秒 | HIT |
| i2 | Robolectric 官方架構頁原文 before each test(整合席取回) | HIT |
| a1 | 第四段的實測寫在 Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md | HIT |
| 其餘 | 讀快照與對照檔即可確認現象 | HIT |

## 先查世界

- PRIOR-ART:量測拆帳(c1 c2 b1 i2 i4)——Gradle 官方 TestResult 的 getStartTime、getEndTime 是毫秒,Lucene 建置腳本用 afterTest 算每支測試時間 https://docs.gradle.org/current/kotlin-dsl/gradle/org.gradle.api.tasks.testing/-test-result/get-start-time.html 、https://apache.googlesource.com/lucene-solr/+/refs/heads/LUCENE-9670/gradle/testing/slowest-tests-at-end.gradle 。採用:只切 T 與 Σt 兩份,不自己切 Robolectric 初始化。
- PRIOR-ART:掛住處理(b5 i3)——PIT 另開子 JVM 跑測試,能砍掉掛住的子程序 https://pitest.org/faq/ 。採用:逾時就結束原型,不在同一 JVM 硬撐。
- PRIOR-ART:常駐 Robolectric 的每支測試成本(i2)——Robolectric 官方:每支測試前有大量環境初始化 https://robolectric.org/architecture 。採用:算進省不掉的那份。
