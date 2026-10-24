preflight-4: ran

# code-readme-android-e2e r4 收貨

人裁加的一輪(2026-10-25 Enzo,cap-decision extra-round,跑滿回顧已記)。
審材:主線 17a0d393 到 0aa3adbb 的完整改動 r4-snapshot.patch(343 行),加最近一次修補 r4-repair.patch(f3b5876f → 0aa3adbb)。
兩席全新:單審(sonnet,只看最近一次修補改過的每一句、逐句對出處)、架構對齊(sonnet),都交回後才一起存檔。單審引句全錨;架構對齊乾淨、0 條。
修補因果:F1 是上一輪新加的結構檢查帶出的脆弱點(以標題字串觸發);F2 的「每條」是上一輪修補改寫時擴大的說法;F3 是既有句子,上一輪把清單主詞改成「判七件事」後更容易被讀成七項全部。

## 機械重現

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | minor | 讀產生器:場景與 validate 各寫一份標題字串;席位改壞實驗只改標題時結構檢查整段不跑 | HIT | 折:標題抽成 ANDROID_TITLES 常數,場景與 validate 共用 |
| F2 | minor | 讀 android-receipt-rerun.sh:expect 為 - 的查詢 continue,不跑不比 | HIT | 折:中英兩版改成「重跑每條標了預期結果的查詢」 |
| F3 | minor | 讀 SKILL L0 第 8 步:只有 native_unreachable、java_growth、instances、peak_vitals 直達 L3,要有 test_data 宣告;frozen 走 L1;exits、strictmode 看紀錄檔 | HIT | 折:中英兩版改成前四項(記憶體類)才直達 L3、要先宣告,畫面卡住走 L1,閃退與 StrictMode 看結束紀錄與日誌 |

折 3、放行 0、駁回 0。
