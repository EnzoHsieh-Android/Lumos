---
type: verification
status: pass
date: 2026-11-01
valid_under: detekt 1.23.8(Homebrew)、JBR 17.0.14、kotlinx-coroutines-core-jvm 1.8.1 與 kotlin-stdlib 1.9.20 當 classpath、macOS 本機最小樣本;Android 官方三頁依 2026-11-01 讀到的版本(架構建議 2026-10-05、UI 事件 2026-05-18、狀態還原 2026-10-07、Flow 測試 2026-09-24)
revalidate_when: detekt 升到 2.x、共用 detekt 設定或 kotlin-idioms 機檢接線範例改動、Android 官方 UI 事件頁或架構建議頁改寫一次性事件的建議時
tags:
  - type/verification
  - status/pass
  - scope/stack-knowledge
plan_refs:
  - "[[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]]"
---
# 2026-11-01_Kotlin慣例對齊官方與detekt實測

> 白話:這篇記的是兩件事的證據——①Kotlin 慣例手冊與審查題改成跟 Android 官方一致之後,四支條款測試實作前全紅、實作後全綠;②detekt 1.23.8 在「只給 --input」的命令列跑法下,哪些規則根本不會報。

## 條款測試紅綠(規格閘留痕)

- 實作前(把三支實作檔換回主線 8b1a1cfb0 版本、測試檔留新版):`lumos spec-gate` 印 S1–S4 全紅,判 PASS(風險低)。
- 實作後:S1–S4 全綠。
- 兩道原本就綠、沒經過「先紅」的檢查各注入一次故障:審查鏡頭條號範圍改回 R1–R18 → S3 紅;洩漏題觸發字偷加 `AndroidViewModel` → S2 紅;還原後兩支都綠,檔案跟注入前一字不差。

## detekt 1.23.8 實測

最小樣本各跑一次,命中的規則名用報告行尾的 `[規則名]` 計數:

| 情況 | 會報的(本計劃關心的規則) | 不報的 |
|---|---|---|
| 照 kotlin-idioms 舊版〈機檢接線〉範例 | 整次失敗,退出碼 3:「Property 'coroutines>CoroutineLaunchedInTestWithoutRunTest' is misspelled or does not exist」 | 全部 |
| 拿掉那一行、只給 `--input` | `GlobalCoroutineUsage`(import 後寫 `GlobalScope.launch`) | `ForbiddenMethodCall`、`InjectDispatcher`、`RedundantSuspendModifier`、`SuspendFunWithFlowReturnType`、`SleepInsteadOfDelay`、`CouldBeSequence`、`SuspendFunSwallowedCancellation`;寫完整套件名的 `kotlinx.coroutines.GlobalScope.launch` 也不報 |
| 帶 `--classpath`(協程與標準庫 jar)與 `--jdk-home` | 上一列不報的前六條都報 | `SuspendFunSwallowedCancellation` 對 `try/catch(Exception)`、`catch(Throwable)` 包 `delay` 都不報,只報 `runCatching { delay(…) }` |
| `ForbiddenImport` 擋 `kotlinx.coroutines.runBlocking`、只給 `--input` | 報(import 那一行) | — |

另以 `detekt --generate-config` 產的 1.23.8 預設設定核對規則名與預設開關:`SuspendFunWithFlowReturnType`、`InjectDispatcher`、`SleepInsteadOfDelay`、`RedundantSuspendModifier` 預設開;`SuspendFunSwallowedCancellation`、`GlobalCoroutineUsage`、`ForbiddenMethodCall`、`CouldBeSequence` 預設關;`CoroutineLaunchedInTestWithoutRunTest` 不在裡面。

## 沒驗到的

- 沒有裝了 detekt Gradle 外掛的 Android 專案可以實跑型別解析任務的 SARIF 輸出;回頭條件記在 [[Systems/linter精選目錄]]。
- 只在 macOS 本機跑過,沒在 CI 上跑;CI 沒有 detekt 時 S4 那支印「沒驗到」、只驗範例存在。

## 代碼審 r1 之後

正確性席指出 S4 那支只排除退出碼 3:設定的 YAML 少一個右大括號時,detekt 1.23.8 以退出碼 1 整次失敗,舊判準照綠。改成樣本放一行 import 之後的 `GlobalScope.launch`,斷言退出碼 2 而且報出 `[GlobalCoroutineUsage]` 那一行。改完注入兩種故障各跑一次:範例少一個右大括號 → 退出碼 1、紅;範例加回 `CoroutineLaunchedInTestWithoutRunTest` → 退出碼 3、紅;還原後綠。同一輪另修:R22 的官方範例補上 `UnconfinedTestDispatcher(testScheduler)`(漏了會讀到初始值)、手冊新節標明只有 Android 專案適用並每條補依據行、測試守門改用既有的 `_need_src`。
