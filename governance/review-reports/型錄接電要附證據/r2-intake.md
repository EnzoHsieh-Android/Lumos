# r2 收貨紀錄(型錄接電要附證據)

- 四席(通才二、正確性二、證據可信二、架構對齊二)交回後一次存檔,取自逐字稿;架構對齊二三行等級前縮排,report-normalize --write 只搬到行首;四份對 r2-snapshot.md 全數錨定。四席都沒建臨時目錄。編號:通才二 e、正確性二 f、證據可信二 g、架構對齊二 h。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| e1 | 通才二 | major | 「退回只標批一」會讓沒有規則包的列憑空多一個批一;字面也沒限定在宣稱接電的列 | HIT:python 讀 18 列通電批次,只有 API-9 有批一 | 折:改成只拿掉批四標籤,告警帶寫法值變空時寫「未接」,範圍限定在現在宣稱接電的列(H1) |
| e2 | 通才二 | major | 「取代」沒寫要刪什麼、舊測試怎麼改,比對對象是整格還是批四段沒寫 | HIT:check.py catalog_problems 呼叫 _batch4_problems;測試 t_kt_catalog_batch4_wiring、_kt_batch2_b4_problems 直接驗舊行為 | 折:寫明 _batch4_problems 換成新比對、只比告警帶寫法值裡的批四括號段、標籤順序固定,列出要改的兩支舊測試與口徑句斷言(H8) |
| e3 | 通才二 | minor | 新節放錯位置會被 main_rows 當主表列 | HIT:check.py main_rows 在「## 情境決策表」前截斷 | 折:新節放〈待查證〉之後(H9) |
| e4 | 通才二 | minor | 固定值沒列舉、擋不到列沒有合法的等級與出處、detekt 沒綁標籤 | HIT:讀快照範圍 3 | 折:列舉固定值、加理由欄、detekt 只准配推送前標籤(H9) |
| e5 | 通才二 | minor | 〔真跑〕只驗存在,可張冠李戴;pilot.md 不在卷證 | 前半 HIT(讀快照);後半 MISS:`git show --stat c6ac4eb0d` 列了 sweep/pilot.md | 折前半:樣本檔名要以該列編號開頭、內容要含壞例原文(H5);後半不成立 |
| f1 | 正確性二 | major | 候選定義是(標籤,規則碼),範圍 1 又說(列,標籤)一列就夠,兩條打架;32 列同標籤多候選 | HIT:python 數到 32 列 | 折:單位一律(列,標籤,檢查),每個候選都要一筆判定(H2) |
| f2 | 正確性二 | major | 同 e1 | HIT:同 e1 | 折:同 e1 |
| f3 | 正確性二 | major | 說要記版本但表裡沒有版本欄,版本漂移沒人偵測 | HIT:讀快照範圍 1 欄位 | 折:〈接電證據〉節開頭固定一行真跑環境版本,自檢驗格式;回頭條件綁 linter 精選目錄(H7) |
| f4 | 正確性二 | minor | 通電批次比對對象與舊值處理沒定義 | HIT:同 e2 | 折:同 e2 |
| f5 | 正確性二 | minor | 樣本檔路徑相對誰、detekt 與標籤搭配沒檢查 | HIT:讀快照 | 折:同 e4、e5 |
| g1 | 證據可信二 | major | 「清單裡讀不到判擋不到」會把資安包 17 條、navigation 5 條全判掉,因為清單沒載入那兩個套件 | HIT:registry-lint31.13.2.tsv 第四欄沒有 navigation 與資安包 | 折:改成全部真跑(H4);只在真跑樣本編不過時才讀頁,讀頁也不准用「清單讀不到」當擋不到的理由(H3) |
| g2 | 證據可信二 | major | 抽 30 筆只抽擋得到那邊、沒門檻,沒抽到的照當擋得到 | HIT:讀快照範圍 2 | 折:不抽樣,全部候選真跑(H4) |
| g3 | 證據可信二 | major | 樣本可以是改寫過的變體,S4 只驗存在 | HIT:pilot.md 的 UI-11、ARCH-28、UI-49、PERF-1「照抄不報、變體才報」 | 折:樣本要含壞寫法欄某個例子的原文,自檢機械比對(H5) |
| g4 | 證據可信二 | minor | 真跑設定跟「預設開」沒分清,先導用了 checkAllWarnings | HIT:pilot.md UI-80、TEST-25 | 折:真跑一律照範本設定(只開 warningsAsErrors、不開 checkAllWarnings),報出且讓建置失敗才算擋得到(H6) |
| g5 | 證據可信二 | minor | 天花板只寫多擋;androidx 檢查跟函式庫版本走,舊 BOM 會少擋 | HIT:pilot.md 版本表 | 折:天花板改成雙向,環境版本行記 androidx 各套件版本 |
| h1 | 架構對齊二 | minor | 欄名「列」對既有「編號」;節位置沒寫 | HIT:型錄〈待查證〉表頭 | 折:欄名用「編號」,位置同 e3 |
| h2 | 架構對齊二 | minor | 樣本副檔名與引用寫法沒對齊 samples/situation 的 .kt.txt | HIT:check.py situation_samples | 折:`samples/lint-wiring/<編號>.kt.txt`,出處只寫檔名 |
| h3 | 架構對齊二 | minor | 讀表沒寫照 _pending_table 骨架,錯誤訊息沒帶節名 | HIT:check.py _pending_table、pending_problems 訊息 | 折:寫明 |

--refuted-set none(e5 後半 MISS 併在 e5 那列,e5 前半成立照折)。--regression-set:e1、f2(r1 折入 G5 時寫「退回只標批一」造成)、f1(r1 折入 G2 的粒度寫法造成)、g1(r1 折入 G3 的「讀不到判擋不到」造成)、e2、f4(r1 寫「取代」沒展開)。

## 依根因分組

- H1 退回的目標值(e1、f2)
- H2 判定粒度(f1)
- H3、H4 讀不到與抽樣(g1、g2)——同一個根因:判定靠讀頁,所以要抽樣、要猜沒載入的套件;一起換成全部真跑
- H5 樣本對應(g3、e5、f5)
- H6 真跑設定(g4)
- H7 版本(f3、g5)
- H8 取代舊比對(e2、f4)
- H9 格式細節(e3、e4、h1、h2、h3)

## 先查世界

- PRIOR-ART:H3、H4、H6——Android Lint 的 lint 任務照專案的 lint 區塊跑,`warningsAsErrors = true` 讓 warning 升成 error、`abortOnError` 讓 error 擋建置;沒開 `checkAllWarnings` 時只跑預設開的檢查(https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint)。所以照範本設定真跑、看報告裡等級是 error 的筆,一次就同時驗了「會報」「預設開」「warning 以上」。採用:全部候選真跑,不抽樣。compose-rules 用 detekt-cli 加 compose-rules 外掛跑(本機快取有 detekt-cli 1.23.8;外掛從 Maven Central 下載,https://mrmans0n.github.io/compose-rules/detekt/)。資安包從 Google Maven 下載(com.android.security.lint:lint)。
- PRIOR-ART:H5——lint 自己的測試框架用「原始碼片段 → 預期輸出」(`lint().files(kotlin("..."))`,https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉),樣本就是要測的那段碼本身;採用:樣本必須含型錄壞寫法欄的例子原文。
- PRIOR-ART:H1——型錄既有值「未接」代表沒有任何檢查接上(型錄〈輸入與口徑〉通電批次欄的值);照用,不另創。
- PRIOR-ART:H2、H7、H8、H9——專案既有寫法(〈待查證〉節、samples/situation、_pending_table),沒有要另查的。
