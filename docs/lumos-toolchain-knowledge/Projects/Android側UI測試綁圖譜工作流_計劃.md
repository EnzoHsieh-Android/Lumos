---
type: project
status: todo
created: 2026-08-11
updated: 2026-08-11
related:
  - "[[test-layers軟提醒_計劃]]"
  - "[[Systems/pitfalls-code-loop]]"
tags:
  - type/project
  - status/todo
  - scope/governance
summary: |-
  FLOW:功能完成→除單元測試外,用 maestro 建該功能的 UI flow 檔→以檔案形式實跑通過→用 [test:] 綁回該功能的圖譜節點→之後重測/重驗直接跑檔
  KEY:★缺口是三重的,且都很精確(對照既有 [[Systems/pitfalls-code-loop]] 的「UI 層驗收慣例」2026-08-05)★—①**時機**:既有慣例掛在 code-loop 終審(審查時派 agent 去看一眼),使用者要的是**功能完成當下** ②**產物**:既有留截圖+console 存 review-reports/<loop>/ui-evidence/,那是**一次性證據**;要的是 flow 檔=**可重放資產**。⚠既有慣例自己寫著「證據可重放非口頭」——★但截圖其實不可重放,flow 檔才是★ ③**棧**:既有只點名 Playwright MCP / claude-in-chrome,兩者都是 web;**Android 沒有通道**
  KEY:★綁定機制已經存在,不必新造★—合約鏈的 `[test:測試方法名]` 現在指 JUnit 方法名;讓它**也能指 flow 檔路徑**(如 `[test:.maestro/smoke-05-manual-discount-over-100.yaml]`)就接上了。指令面 `lumos guard bind <node> "<KEY子字串>" <測試名>` 是現成的;`.lumos/test-layers.json` 的 layer/cmd/when 也已能宣告 maestro 指令(mOrangePos 2026-08-11 已實測會印提醒)
  KEY:★實戰要求一:斷言重點是「使用者看到什麼」,不是「有沒有被擋」★—mOrangePos 2026-08-11 實機抓到的缺陷:折扣超過 100% 的提示誤用 `R.string.input_err`(登入頁的「請輸入員工編號!」)。★單元測試斷言的回傳值 `Result.OutOfRange` 一直是對的,錯的是 UI 拿它去換哪一句話★——這一型單元測試結構上測不到,也正是 UI flow 唯一無可取代的價值。故 flow 的斷言必須含「畫面上出現什麼字」,只斷言「流程有沒有被擋」等於白做
  KEY:★實戰要求二:「寫了 flow」≠「flow 會跑」★—inline 跑通不代表寫成檔案跑得通(runFlow 相對路徑、optional 步驟、共用子流程都可能出錯)。★工作流必須要求以檔案形式實跑通過一次才算完成★,同 [test:] 綁定後要真跑一次的精神(信任階梯:真跑>機械查>LLM 判官>自報)
  KEY:★實戰要求三:裝置前置是這條路線的真實成本,沒文件化第二次就沒人跑得起來★—mOrangePos 實測撞到四關:①首次使用授權閘(要算挑戰碼)②複製設定★務必改裝置名★(否則兩台產生重複單號,踩既有事故)③一人登入開著時重裝沒登出會被擋(要 logo 連點解鎖)④**別台機器編的 APK 簽章不同,要換版本得先移除、設定全掉**。工作流要把「裝置 ready 的定義」寫成可檢查的前置,不能當常識
  KEY:★四個會讓腳本「沉默地做錯事」的坑(不是報錯,是回報成功但做錯)★—①同畫面兩個鍵盤共用同一組 resource-id→用 text/id 選會打到另一個且不報錯 ②Maestro 的 `text:` 是**全字串正則**,`tapOn:"."` 匹配任意字元(實測點到「1」,把 3.25 打成 3125)③某些欄位點選付款方式會自動帶值,再自己輸入反而錯 ④SeekBar 要 swipe 不能 tap,起點落在元件外會靜默無效。★這類「綠燈但做錯」比紅燈危險,產生 flow 的 agent 必須被明確警告★
  PRIOR-ART:①最小解在既有層—`[test:]` 合約鏈 + `lumos guard bind` + `.lumos/test-layers.json` 三個都已存在,只需讓 [test:] 接受 flow 檔路徑並補 Android 通道,**不造新機制、不新增治理層** ②世界解過—**Serenity BDD / Cucumber 的 living documentation**:把驗收條件變成可執行測試、再由測試結果產出活文件,核心價值=**同一份東西同時是規格與測試,兩者不會漂移**;**Maestro** 本身則提供 YAML flow(無編譯循環)、CI 整合、每次執行留影片/log/flake 偵測 ③裁定=**borrow-design**(借「規格與測試不分家」的意圖,原生實作;零依賴家規排除 adopt)
  KEY:★與 Serenity/Cucumber 的刻意偏離★—它們引入 Gherkin + step definitions 這一層**翻譯層**,規格與程式之間多一組要維護的膠水。本設計**不做翻譯層**:敘述本來就在圖譜節點裡、可執行步驟本來就在 flow 檔裡,★只需要一個指標把兩者綁起來★。不新增第三種產物
  KEY:★天花板(先寫明,免得被當成全覆蓋)★—①UI flow 對「畫面長怎樣」敏感,版面一改就要重錄(mOrangePos 的折扣面板因 id 衝突只能用座標點擊,改版必壞)②只驗走得到的路徑,取不到裝置/起不了環境時仍是「明記未驗+原因」,不得靜默跳過 ③不取代單元測試:規則面仍歸單元測試,UI flow 守的是接線與呈現
  DECISION:[2026-08-11]先擴既有 [test:] 與 test-layers,不新造機制;Android 通道補在既有「UI 層驗收慣例」之下而非另立
---
# Android 側 UI 測試綁圖譜工作流_計劃

**Goal:** 讓 Android 功能完成時，除了單元測試，也產出一支**可重放的 maestro flow**，並綁回該功能的圖譜節點——之後任何人要重測或重驗，跑一個檔就行。

> **狀態：待評估與拍板。** 由 mOrangePos 2026-08-11 實跑一輪 smoke 後就地寫回。
> 進實作前依家規需過 `lumos-design-loop`。

---

## 缺口在哪（不是「沒有 UI 驗收」，是三個維度都差一點）

既有的 UI 層驗收慣例（[[Systems/pitfalls-code-loop]]，2026-08-05）長這樣：

> test-layers 宣告 layer 含「UI 驗收」的棧被 diff 命中時，終審驗收＝agent 以 Playwright MCP／claude-in-chrome 真開頁執行驗收條款，截圖+console 證據存 `review-reports/<loop>/ui-evidence/`

對照使用者要的：

| | 既有慣例 | 要的 |
|---|---|---|
| **時機** | code-loop **終審**時 | **功能完成當下** |
| **產物** | 截圖 + console（一次性證據） | **flow 檔（可重放資產）** |
| **棧** | Playwright / claude-in-chrome（**都是 web**） | **Android** |

第二列值得特別講：那條慣例自己寫著「**證據可重放非口頭**」——立意完全正確，**但截圖其實不可重放**。要重驗還是得再派一次 agent、再點一遍。flow 檔才真的可重放，而且下一個人跑它不需要理解當初為什麼那樣點。

## 綁定機制不用新造

合約鏈的 `[test:測試方法名]` 現在指 JUnit 方法名。讓它**也能指 flow 檔路徑**就接上了：

```
KEY:★INVARIANT★ 手動折扣百分比不得超過 100% [test:ManualDiscountValidatorTest.百分比超過100必須擋下]
                                              [test:.maestro/smoke-05-manual-discount-over-100.yaml]
```

`lumos guard bind` 是現成指令；`.lumos/test-layers.json` 的 `{layer, cmd, when}` 也已經能宣告 maestro 指令（mOrangePos 2026-08-11 已實測會印提醒）。

## 三條從實戰得到的設計要求

### 一 · 斷言重點是「使用者看到什麼」，不是「有沒有被擋」

mOrangePos 這次抓到的缺陷：折扣超過 100% 的提示誤用了 `R.string.input_err`，而那是登入頁的「請輸入員工編號!」。擋是擋住了，但店員看到一句與折扣無關的話。

**單元測試斷言的回傳值 `Result.OutOfRange` 一直是對的**——錯的是 UI 拿它去換哪一句話。這一型單元測試**結構上**測不到，也正是 UI flow 唯一無可取代的價值。

所以產生 flow 的 agent 必須被要求：斷言要含「畫面上出現什麼字」。只斷言「流程有沒有被擋」等於白做。

```yaml
- assertVisible: "折扣超過上限。.*"
- assertNotVisible: "請輸入員工編號.*"   # 回歸釘：不可再退回誤用的字串
```

### 二 · 「寫了 flow」不等於「flow 會跑」

inline 跑得通，不代表寫成檔案跑得通——`runFlow` 的相對路徑、`optional` 步驟、共用子流程都可能出錯。工作流必須要求**以檔案形式實跑通過一次**才算完成。

同 `[test:]` 綁定後要真跑一次的精神：**真跑 > 機械查 > LLM 判官 > 自報**。

### 三 · 裝置前置是真實成本

mOrangePos 實測撞到四關，任何一關沒文件化，第二次就沒人跑得起來：

1. 首次使用授權閘（要算挑戰碼）
2. 複製設定時**務必改裝置名**（否則兩台產生重複單號，直接踩既有事故）
3. 一人登入開著時，重裝沒登出會被「此帳號已被登入」擋死
4. **別台機器編的 APK 簽章不同** → 要換版本得先移除，**設定全掉**

工作流要把「裝置 ready 的定義」寫成可檢查的前置，不能當常識。

## 四個會讓腳本「沉默地做錯事」的坑

這類**綠燈但做錯**比紅燈危險——maestro 回報成功，實際做的是別的事。產生 flow 的 agent 必須被明確警告：

| 坑 | 症狀 |
|---|---|
| 同畫面兩個鍵盤共用同一組 `resource-id` | 用 `text:`/`id:` 選會打到另一個，**不報錯**，只是輸入進錯地方 |
| Maestro 的 `text:` 是**全字串正則** | `tapOn: "."` 匹配任意單一字元（實測點到「1」，把 3.25 打成 3125） |
| 選付款方式會自動帶入金額 | 再自己輸入反而算錯 |
| SeekBar 要 `swipe` 不能 `tap` | 起點落在元件外會靜默無效 |

## 世界怎麼解的（PRIOR-ART ②）

**Serenity BDD / Cucumber 的 living documentation**：把驗收條件變成可執行測試，再由測試結果產出活文件。核心價值＝**同一份東西同時是規格與測試，兩者不會漂移**。

**Maestro** 本身提供 YAML flow（無編譯循環）、CI 整合、每次執行留影片／log／flake 偵測。

**刻意偏離**：Serenity／Cucumber 引入 Gherkin + step definitions 這一層**翻譯層**，規格與程式之間多一組要維護的膠水。本設計**不做翻譯層**——敘述本來就在圖譜節點裡，可執行步驟本來就在 flow 檔裡，**只需要一個指標把兩者綁起來**，不新增第三種產物。

（註：翻譯層的維護成本是設計考量，非本次檢索所得的引用——搜尋結果只涵蓋其優點，未涵蓋缺點，此處不冒充有出處。）

出處：[Serenity BDD — Living Documentation](https://serenity-bdd.github.io/docs/reporting/living_documentation)、[Maestro Docs](https://docs.maestro.dev/)

## 天花板（先寫明，免得之後被當成全覆蓋）

- UI flow 對「畫面長怎樣」敏感，**版面一改就要重錄**。mOrangePos 的折扣面板因 id 衝突只能用座標點擊，改版必壞。
- 只驗走得到的路徑。取不到裝置／起不了環境時仍是「**明記未驗＋原因**」，不得靜默跳過。
- **不取代單元測試**：規則面仍歸單元測試，UI flow 守的是接線與呈現。

## 參考實作（已落地，可直接看）

mOrangePos `8f239db`：

```
.maestro/common-login.yaml                        啟動→登入，內建一人登入解鎖
.maestro/smoke-01-cash-checkout.yaml              最重要的回歸（關帳閘沒擋到最常見路徑）
.maestro/smoke-05-manual-discount-over-100.yaml   含「使用者看到什麼」的斷言
.maestro/README.md                                裝置前置 + 四個坑 + 座標對照表
.lumos/test-layers.json                           kt → UI 驗收層
```

## 待辦

- [ ] `[test:]` 接受 flow 檔路徑：解析、`guard bind` 支援、doctor Check T 判定（檔案存在即算綁上？還是要求跑過？）
- [ ] Android 通道補進「UI 層驗收慣例」：maestro MCP 的 `list_devices` → `inspect_screen` → `run`，與既有 Playwright 通道並列
- [ ] 「裝置 ready」的可檢查前置清單（各專案自填，如 `.maestro/README.md`）
- [ ] 產 flow 的 agent prompt：要求斷言含「畫面上出現什麼字」＋四個坑的警告＋必須以檔案形式實跑通過
- [ ] 決定要不要在功能完成時**硬要求**產 flow，還是只軟提醒（傾向後者：不是每個功能都有 UI 面）
