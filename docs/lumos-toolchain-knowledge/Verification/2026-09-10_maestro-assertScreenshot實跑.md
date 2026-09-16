---
type: verification
status: pass
date: 2026-09-10
valid_under: 主體證明 Maestro 2.6.1(晚上另用 2.10.0 重跑關鍵幾條,差異記在正文「2.10.0 重驗」)在 iPad Pro 13-inch (M5)/iOS 26.5 模擬器(Apple「設定」app 與 PosTerminal 示範 app)與 Pixel Tablet/Android 15 模擬器(Android「設定」app)上的行為;沒在真機或 mOrangePos 跑過;Maestro Cloud 沒跑
revalidate_when: Maestro 升版(尤其 ≥2.8.0,diff 路徑與門檻吃變數都改了)、換模擬器機型或 OS、或第一次把 assertScreenshot 放進真 QA flow
tags:
  - type/verification
  - status/pass
  - scope/stack-knowledge
plan_refs:
  - "[[Projects/Maestro截圖基準比對_調研]]"
summary: |-
  TEST:七支 flow 實跑——A 缺基準圖、B 先拍後比、D 換畫面用嚴門檻、F cropOn、H 環境變數切換(四種組合)、S 狀態列釘死;卷證與重跑用的 flow/log/diff 圖/重算腳本都在 governance/review-reports/maestro-visual-baseline-2026-09-10/
  VERIFY:★預設門檻 95 放過「整個內容面板換掉」(相符 96.195%),門檻 99.9 才翻紅★;用 PIL 照原始碼重算同兩張圖得 96.19545545452497,與 Maestro 回報位位相同,代表演算法讀對了、也代表可自建儀器
  VERIFY:缺基準圖=斷言失敗不自動建;截圖 2064×2752;diff 寫到 baseline/baseline/(相對路徑拼兩次);cropOn 在 iOS 可用(71×29pt 的標籤截成 142×58px);★flow 檔頭 env 預設值蓋掉命令列 -e★;`simctl status_bar override --time 9:41` 釘時間可用
  VERIFY:★下午補跑 Android(Pixel Tablet/Android 15/2560×1600,「設定」app)與 iPad 上的 PosTerminal 示範 app★——Android 開一個設定項目 98.33%(預設 95 放行)、同畫面隔 60 秒 99.986%、demo mode 釘時鐘 12:00 截圖確認、環境變數切換範本照預期、diff 一樣寫到 baseline/baseline/;PosTerminal 重開同畫面 100%、切分類讓商品格 15→3 張 97.575%(門檻 99.5 翻紅);卷證在同目錄 android/ 與 pos-terminal/
  VERIFY:★2.10.0 重驗(升版後同一台 iPad 模擬器)★:缺基準仍失敗;takeScreenshot 落在 <產物目錄>/<時間戳>/<flow>/takeScreenshot/…,搬進 repo 後 assert 通過;換面板 95.97% 翻紅、diff 在基準圖旁;`-e THRESHOLD=99.5` 通過、未定義報 Invalid;檔頭 env 仍蓋掉 -e;setOrientation 可用(iPad LANDSCAPE_LEFT 跟原基準 100%、RIGHT 93%);Android 平板 PORTRAIT 才是 2560×1600
  VERIFY:副作用已還原——那台模擬器原本就有狀態列覆寫(時間釘在 12:30),實驗中的 clear 把它清掉,事後已用 override --time 12:30 補回;其他覆寫欄位(電量等)原值不明,沒法補
---
# 2026-09-10 Maestro assertScreenshot 實跑

> 白話：這篇證明「Maestro 2.6.1 真的有截圖比對斷言，而且我把它的每條路都跑過一次」。跑在 Enzo 開著的 iPad Pro 13 模擬器上，拿 Apple 內建的「設定」app 當對象，所以不碰任何 Enzo 的 app。

## 跑了什麼、看到什麼

| flow | 做什麼 | 結果 | 關鍵輸出 |
|---|---|---|---|
| A | 基準圖不存在就 assert | 失敗（預期） | `Screenshot file not found` ，明講要先建檔 |
| B | 同一畫面先 takeScreenshot 再 assertScreenshot，門檻 95 | 通過 | 基準圖 2064×2752 |
| C2 | 點另一個左欄項目後 assert，門檻 95 | **通過（不該過）** | 右側整個面板換了仍過 |
| D | 同上，門檻 99.9 | 失敗（預期） | `threshold not met, current: 96.195…%`；diff 圖寫到 `baseline/baseline/settings_main_diff.png` |
| F | takeScreenshot 與 assertScreenshot 都 cropOn 到「一般」標籤，門檻 99.9 | 通過 | 截出 142×58 px |
| H1'/H2'/H3' | 檔頭不放 env；`-e UPDATE_BASELINE=true` / `=false` / 不給 | 三組都照預期 | 給 true 只拍；false 或不給只比 |
| H4 | 檔頭放 `env: UPDATE_BASELINE: "false"` 再 `-e …=true` | **檔頭贏** | 只比不拍，命令列旗標沒生效 |
| S | `simctl status_bar override --time 9:41` 後截圖 | 通過 | 狀態列顯示 9:41 AM（見 strips.png 中間那條） |

同一畫面隔八分鐘再拍一張（H1' 的基準）跟 B 的基準比，相符率 100.0%——因為那台模擬器的時鐘本來就被釘在 12:30，所以這個數字**不能**拿來當「時鐘漂移很小」的證據。

## 下午補跑：Android 模擬器與 PosTerminal 示範 app

| 平台／app | flow | 做什麼 | 結果 | 關鍵數字 |
|---|---|---|---|---|
| Android 設定 | B | 先拍後比，門檻 95 | 通過 | 截圖 2560×1600 |
| Android 設定 | D | 點開一個項目後比，門檻 99.9 | 失敗（預期） | 相符 98.330%；預設 95 會放行 |
| Android 設定 | T | 同畫面隔約 60 秒重拍 | 只拍 | 跟基準相符 99.986%，時鐘沒釘 |
| Android 設定 | S | demo mode 廣播後截圖 | 只拍 | 狀態列時鐘 12:00（android_strips.png 第三條） |
| Android 設定 | H | 環境變數切換範本，帶旗標／不帶 | 兩組都照預期 | 帶旗標只拍、不帶只比且過 99.5 |
| PosTerminal | P1 | 先拍後比，門檻 99.5 | 通過 | 主畫面：左側分類、中間商品格、右側訂單欄 |
| PosTerminal | P2 | 重開 app 同畫面 | 只拍 | 相符 100.0%（狀態列本來就釘在 12:30） |
| PosTerminal | P3 | 點「套餐」分類後比，門檻 99.5 | 失敗（預期） | 相符 97.575%；商品格 15→3 張只動 2.4% 像素 |

Android 模擬器是我為了這次實驗開的，跑完已關掉。

## 2.10.0 重驗（同日晚上，本機升版後）

| 項目 | 2.6.1 | 2.10.0 |
|---|---|---|
| 缺基準圖 | 失敗、不自動建 | 同 |
| takeScreenshot 寫到哪 | flow 旁（`./baseline/x.png`） | **該次執行的產物目錄**（`<test-output-dir>/<時間戳>/<flow>/takeScreenshot/baseline/x.png`）；assert 先找該次產物目錄、再找 flow 相對路徑 |
| diff 圖 | `baseline/baseline/x_diff.png`（多一層） | `baseline/x_diff.png` |
| 門檻吃變數 | 否 | 是；未定義報 `Invalid thresholdPercentage: undefined`；evalScript 預設值要整行加引號 |
| 檔頭 env vs `-e` | 檔頭贏 | 檔頭仍贏 |
| 失敗截圖 | `screenshot-❌-<時間>.png` | `<flow>/screenshots/step-NNN-assertScreenshot.png` |
| 換面板相符率 | 96.2% | 95.97% |
| setOrientation | 未測 | iPad LANDSCAPE_LEFT 跟原基準 100%、RIGHT 93.1%；Android 平板 PORTRAIT=2560×1600、LANDSCAPE_*=1600×2560 |

卷證：`governance/review-reports/maestro-visual-baseline-2026-09-10/v210/`。

## 重算腳本

`maestro-matchpct.py`（PIL）照 ScreenshotMatch.kt 的規則逐像素算，對 D 那兩張圖算出 96.19545545452497，跟 Maestro 印的一模一樣。重跑：

    python3 governance/eval/maestro-matchpct.py <基準圖> <實測圖>

## 環境

- Maestro CLI 2.6.1（`~/.maestro/bin/maestro`），最新版 2.10.0。
- Xcode 26.6；在這個 shell 裡 `xcrun` 要帶 `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`，因為 xcode-select 指向 CommandLineTools。
- 模擬器 UDID EA712A4B-485E-4B04-876E-4618F4895DB2，Maestro 的 MCP `list_devices` 列不出它，命令列 `--device` 可以。

## 沒驗的

- Android 模擬器、真機、Maestro Cloud。
- 門檻在「留白少的畫面」（例如商品格子塞滿的 POS 頁）該定多少——本篇的 96.2% 是「設定」app 的留白比例，換畫面數字會不同。
