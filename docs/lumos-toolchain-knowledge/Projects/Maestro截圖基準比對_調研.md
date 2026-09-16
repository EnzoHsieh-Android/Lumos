---
type: project
status: doing
created: 2026-09-10
updated: 2026-09-10
aliases:
  - assertScreenshot
  - 視覺回歸
  - 截圖基準圖比對
  - QA 驗收基準圖
related:
  - "[[Projects/Android側UI測試綁圖譜工作流_計劃]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Verification/2026-09-10_maestro-assertScreenshot實跑]]"
  - "[[Projects/截圖基準驗收流程_計劃]]"
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  KEY:調研問題(2026-09-10 Enzo)=「Maestro 看得到座標與截圖,能不能做成『基準圖 vs 測試結果圖相符』的自動流程」,目的是改善 QA 驗收流程;★結論:能,而且是 Maestro 原生指令,不用接第三方★——`assertScreenshot`(2.2.0 加入,本機 2.6.1 已有,最新 2.10.0):把當下畫面(或 cropOn 切到的單一元件)跟一張既有 PNG 逐像素比,相符率低於 thresholdPercentage(預設 95)就讓 flow 失敗,並在基準圖旁產一張紅框 diff 圖
  KEY:★外部查證說「2.6.1 沒有原生截圖比對,要接 Percy/Applitools/ImageMagick」是錯的★(2026-09-10 Enzo 帶進來的第二來源);三個獨立證據:①官方 CHANGELOG 2.2.0「Add a new assertScreenshot command for visual regression testing」②本機 ~/.maestro/lib 裡有 maestro/orchestra/AssertScreenshotCommand.class、ScreenshotMatch.class 與依賴 image-comparison-4.4.0.jar ③iPad Pro 13 模擬器上實跑,pass 與 fail 兩條路都走到(見 [[Verification/2026-09-10_maestro-assertScreenshot實跑]]);★對方沒開原始碼也沒跑,只憑「核心斷言靠 view hierarchy」的印象推論——同 [[positive-assertions-need-verification]] 那條:「沒有 X」跟「有 X」一樣要打開看★
  KEY:演算法(讀 ScreenshotMatch.kt,2.6.0 起為單一真相源):同尺寸→逐像素算 RGB 歐氏距離,距離平方 > (0.1×√(255²×3))² ≈ 1951 的算「不同」,相符率 = 1 − 不同像素/總像素;★尺寸不同直接 SizeMismatch 失敗(不是相符率低)★;像素容差 0.1 寫死不可調;★沒有遮罩/忽略區域,只有 cropOn 單一元件★;diff 圖用 romankh3 image-comparison 畫紅框(線寬 10、最小框 40);實際截圖不留在基準圖旁,但失敗當下的截圖會存到 ~/.maestro/tests/<時間戳>/screenshot-❌-….png
  KEY:★預設門檻 95 對 QA 驗收太鬆★——實測 iPad「設定」app 左欄選項換掉、右側整個內容面板換掉,相符率仍 96.2%(畫面大半是白底,3.8% 像素變動就是一整個面板),預設門檻判「相符」;門檻 99.9 才翻紅。建議畫面級 99.5–99.9,並把狀態列排除:cropOn 到 app 根容器,或用 `xcrun simctl status_bar <udid> override --time 9:41` 把時間/電量釘死(Apple 自家工具,實測可用)
  KEY:★基準圖不會自動建★(2.6.1 缺檔=斷言失敗「Screenshot file not found」;早期 PR #2078 的「缺檔就存成基準」沒進正式版);更新基準圖沒有 CLI 旗標,慣用形=同一支 flow 用環境變數切「takeScreenshot(更新)/assertScreenshot(驗收)」兩條 runFlow;★實測坑:flow 檔頭 env: 的預設值會蓋掉命令列 -e★(2.6.1),所以檔頭別放預設,未定義變數在 `== 'true'` 判斷下就是 false,三種組合實測都照預期
  KEY:★2.10.0 重驗(2026-09-10 晚,本機已升)★——①takeScreenshot 改寫進「該次執行的產物目錄」(<test-output-dir>/<時間戳>/<flow>/takeScreenshot/<path>),不再寫在 flow 旁;assertScreenshot 找圖順序=該次產物目錄→flow 相對路徑,所以「這次拍、下次比」要自己把圖搬進 repo ②門檻吃變數(`-e THRESHOLD=99.5` 可;未定義→「Invalid thresholdPercentage: undefined」;用 evalScript 給預設值要整行加引號,YAML 會把 `? :` 當語法) ③diff 圖改寫在基準圖旁 ④缺基準圖仍不自動建 ⑤★檔頭 env 仍蓋掉命令列 -e★ ⑥失敗截圖在 <產物目錄>/<flow>/screenshots/step-NNN-assertScreenshot.png ⑦setOrientation 在 iOS 模擬器可用但截圖尺寸永遠是直立畫格;★Android 平板 PORTRAIT=自然橫向 2560×1600,LANDSCAPE_* 反而變直向加黑邊★
  KEY:2.6.1 的 diff 圖路徑有 bug:相對路徑被拼兩次,寫到「基準圖資料夾/基準圖資料夾/<名>_diff.png」(實測 baseline/baseline/settings_main_diff.png);2.8.0 改用 resolveSibling 修掉、門檻改吃變數;2.9.0 加 setDarkMode(深色模式驗收要它)。★MCP 的 cheat_sheet 已列 setDarkMode 但 2.6.1 CLI 拒收「Invalid Command」——寫 flow 前以 `maestro --version` 為準,不以 cheat sheet 為準★
  KEY:iOS 模擬器實跑要點:①MCP list_devices 列不出 iOS 模擬器(今天 iPad 開著仍只列 Android/chromium),命令列 `maestro --device <UDID> test` 可以 ②截圖是裝置直立畫格(2064×2752),app 橫向跑時圖是躺的;基準與實測都躺所以比對不受影響,但人看 diff 圖要轉 90° ③cropOn 在 iOS 可用:hierarchy 的 bounds 是點(pt),截出來是像素(「一般」標籤 71×29pt → 142×58px),基準與驗收兩邊要同一個 cropOn ④text 選擇器吃語系(英文 "General" 在中文模擬器找不到,要用「一般」),QA flow 用 accessibility id 或 point 較穩 ⑤同一台機型+OS+方向+外觀+語系+字級,任一不同尺寸就對不上
  KEY:世界怎麼解(同層與不同層;2026-09-10 下午逐一開文件/原始碼確認):畫面級 E2E=Maestro assertScreenshot(本篇)/Playwright toHaveScreenshot(官方文件:mask 疊粉色框、maxDiffPixelRatio、maxDiffPixels、threshold 用 YIQ 色差、animations 預設 disabled——web 面比 Maestro 完整);元件級=iOS swift-snapshot-testing 1.19.4(2026-07-28;原始碼 UIImage.swift:precision=必須相符的像素比例、perceptualPrecision=單一像素要多像才算相符,預設都 1;in-process XCTest 不用跑模擬器互動)、Android Roborazzi(README:changeThreshold,0.01=准 1% 差異)/Paparazzi;自建管線=odiff(SIMD,最快)/pixelmatch/ImageMagick compare;雲端=Percy/Applitools/LambdaTest SmartUI(有 Maestro 整合,但付費且截圖外送)
  PRIOR-ART:①最小解在既有層——消費專案已採用 Maestro(Android 通道 [[Projects/Android側UI測試綁圖譜工作流_計劃]]),assertScreenshot 是同一支工具的原生指令,flow 檔照樣用 `[test:maestro:<name>]` 綁節點([[Systems/test-profile-multiplatform]]),★零新依賴★ ②世界解過=上一條 KEY ③裁定=**borrow-design**(用 Maestro 原生,不接雲端服務;要遮罩再考慮自寫比對——本篇已用 PIL 重現 Maestro 的相符率到小數第 14 位,證明可自建儀器,但 PIL 非標準庫,進 lumos 要純 python 讀 PNG,另案裁)
  KEY:★對 QA 驗收流程的建議形狀(本篇只到調研,要不要做、做在哪個專案由 Enzo 裁)★——①人看畫面點頭的那一刻=跑 flow 帶 UPDATE_BASELINE=true 存基準圖進 repo(基準圖就是驗收紀錄)②之後每次改動跑同一支 flow 不帶變數→過=畫面沒變;不過=看 diff 圖裁「回歸 or 預期改版」,預期改版就回①更新 ③flow name 綁功能節點,驗證筆記引用基準圖路徑;前置沿用既有慣例(只准對標可自動的 flow 自動跑、狀態列釘死、裝置 ready 定義寫成可檢查前置)
  KEY:★Android 模擬器與真 app 補測(2026-09-10 下午,Pixel Tablet/Android 15/2560×1600;iPad 上的 PosTerminal 示範 app)★——同一套行為:Android「設定」開一個項目仍 98.33% 相符、預設 95 照樣放行;同畫面隔 60 秒重拍 99.986%(時鐘沒釘,漂移只有 0.014%);Android demo mode 廣播能把時鐘釘在 12:00(截圖確認);PosTerminal 重開同畫面 100%、切一個分類讓商品格 15→3 張只動 2.4%(97.58%);環境變數切換範本在 Android 也照預期。★三平台的「已知改版」96.2/98.3/97.6 與「同畫面」≥99.98 中間有一大段空隙,門檻 99.5 落在其中★——SOP 見 [[Projects/截圖基準驗收流程_計劃]]
  KEY:★天花板★①版面一改就要重錄基準(同 Android 計劃「UI flow 對畫面長怎樣敏感」)②動態內容(時間、單號、頭像)沒遮罩,只能 cropOn 或把資料固定 ③相符率是像素比例,語意上「差一個字」跟「差一整塊留白」權重一樣,★門檻不是通用常數,要按畫面留白比例定★ ④Maestro Cloud 是否支援 assertScreenshot 沒查(搜尋只找到第三方 maestro-runner 有 --update-screenshots,官方 Cloud 文件沒提)
verified_by:
  - "[[Verification/2026-09-10_maestro-assertScreenshot實跑]]"
---
# Maestro 截圖基準比對調研（2026-09-10）

> 白話：Enzo 問「Maestro 既然看得到座標又能截圖，能不能自動比『基準圖』和『這次跑出來的圖』」，目的是讓 QA 驗收少靠人眼。答案是**可以，Maestro 自己就有這個指令**，叫 `assertScreenshot`。本篇把它的行為在模擬器上實際跑過一遍，記下哪裡會踩雷、門檻該怎麼定、跟既有的「flow 檔綁圖譜」設計怎麼接。本篇只到調研，**要不要做、做在哪個專案，等 Enzo 裁**。

## 為什麼要先糾正一個外部結論

Enzo 同日帶來另一份查證，說 2.6.1 版沒有原生截圖比對，得接 Percy、Applitools 或自己用 ImageMagick 寫比對。那份結論是錯的，錯在只憑「Maestro 的斷言靠 view hierarchy」這個印象推論，沒開原始碼也沒跑。本篇三個獨立證據都指向「有」：官方變更紀錄、本機安裝目錄裡的 class 檔、模擬器實跑（見驗證紀錄）。

## 這個指令做什麼、怎麼做

- **拿當下畫面跟一張既有的 PNG 比**：路徑相對 flow 檔；可用 `cropOn` 把畫面切到某一個元件再比（基準圖也要用同一個 cropOn 拍）。
- **比法是逐像素**：兩張圖尺寸必須一樣，不一樣直接判「尺寸不符」失敗。每個像素算 RGB 顏色距離，超過固定容差（約 44 個色階）算「不同」。相符率 = 不同像素佔全部的比例反過來。
- **門檻是相符率**：`thresholdPercentage` 預設 95，低於它就失敗。失敗時在基準圖旁邊產一張畫了紅框的 diff 圖；失敗當下的實際截圖存在 Maestro 的 debug 目錄，不在基準圖旁。
- **沒有遮罩**：不能說「這一塊不要比」。只能靠 cropOn 切到單一元件、或把會動的東西釘死。

## 實跑學到的六件事

1. **預設門檻 95 太鬆**。在 iPad 的「設定」app 上，點另一個左欄項目、右側整個面板換掉，相符率仍有 96.2%，預設門檻會放行。原因是畫面大半是白底，換一整個面板也只動了 3.8% 的像素。門檻 99.9 才翻紅。
2. **基準圖要自己先拍**。缺檔就是失敗，不會自動建。更新基準圖也沒有旗標，要在 flow 裡用環境變數切兩條路。
3. **flow 檔頭的 `env:` 預設值會蓋掉命令列的 `-e`**。所以檔頭不要放預設；變數沒定義時 `== 'true'` 就是 false，行為正好是「預設驗收、加旗標才更新」。
4. **2.6.1 的 diff 圖路徑會多一層資料夾**（`baseline/baseline/xxx_diff.png`）。2.8.0 修了。
   REVISIT:2026-10-10 Maestro 升到 2.8.0 以上後，重驗 diff 圖路徑與「檔頭 env 蓋掉 -e」是否仍如本篇所記，不是就改 KEY 行
5. **狀態列的時鐘可以釘死**：Apple 的 `simctl status_bar override` 實測可用，比 cropOn 省事。
6. **cheat sheet 比安裝的 CLI 新**：MCP 的 cheat sheet 列了 `setDarkMode`，2.6.1 的 CLI 拒收。寫 flow 前看 `maestro --version`。

## 建議的 QA 驗收 flow 形狀

    appId: com.example.app
    name: checkout_screen_visual
    ---
    - launchApp
    - waitForAnimationToEnd
    - runFlow:
        when:
          true: ${UPDATE_BASELINE == 'true'}
        commands:
          - takeScreenshot:
              path: ./baseline/checkout_main
              cropOn:
                id: root_container
    - runFlow:
        when:
          true: ${UPDATE_BASELINE != 'true'}
        commands:
          - assertScreenshot:
              path: ./baseline/checkout_main.png
              thresholdPercentage: 99.5
              cropOn:
                id: root_container

人看畫面點頭的那一刻，跑一次帶旗標的更新（基準圖就是驗收紀錄，進 repo）：

    maestro --device <UDID> test -e UPDATE_BASELINE=true checkout_screen_visual.yaml

之後每次改動跑同一支不帶旗標；失敗就看 diff 圖決定是回歸還是預期改版。跑之前把狀態列釘死：

    xcrun simctl status_bar <UDID> override --time 9:41 --batteryLevel 100 --batteryState charged

綁圖譜照既有做法：flow 的 `name:` 用 `[test:maestro:checkout_screen_visual]` 綁到功能節點，指令是 `lumos guard bind`（見 [[Systems/test-profile-multiplatform]]）。

## 跟既有設計的關係

- [[Projects/Android側UI測試綁圖譜工作流_計劃]] 已經把「flow 檔是可重放的驗收資產」立為方向，本篇只是在那條路上多一種斷言：除了「畫面上出現什麼字」，還能斷言「畫面長得跟核可過的一樣」。
- [[Systems/pitfalls-code-loop]] 的 UI 層驗收慣例目前靠 agent 開頁看一眼、留一次性截圖；基準圖比對可以把「看一眼」變成機械判定，但門檻與動態內容的處理要照本篇 KEY 行來，否則就是綠燈但沒在驗。

## 下午補查的（2026-09-10）

- **Android 模擬器跑過了**，行為跟 iOS 一致：預設門檻一樣放行、diff 路徑一樣多一層、環境變數切換一樣可用。Android 用 demo mode 廣播釘時鐘，實測有效。
- **真 app 也量了**：PosTerminal 示範 app 切一個分類、商品格從十幾張變三張，只動 2.4% 像素。這是「畫面級門檻要 99.5 起跳」最直接的證據。
- **替代方案的參數都開了文件或原始碼確認**：Playwright 有 mask 與 maxDiffPixelRatio；swift-snapshot-testing 有 precision 與 perceptualPrecision；Roborazzi 有 changeThreshold。
- 流程本身寫在 [[Projects/截圖基準驗收流程_計劃]]。

## 還是沒查的

- Maestro Cloud 跑 assertScreenshot 的行為（官方 Cloud 文件沒提；只看到第三方 maestro-runner 有 --update-screenshots 旗標）。
- 真機。
