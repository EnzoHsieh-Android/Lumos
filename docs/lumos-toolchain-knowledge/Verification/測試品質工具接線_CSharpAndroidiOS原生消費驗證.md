---
type: verification
status: pass
date: 2026-10-08
valid_under: 可信本機合成案例；SDK9.0.117/xUnit/VSTest/JUnit logger4.1.0；AGP8.13.2/Kotlin2.2.21/Gradle8.13/API35獨立模擬器；Xcode26.6/iOS26.5/XCTest/xcbeautify3.2.1
revalidate_when: JUnit歸因、reporter/framework/SDK或橋接脚本改動時，重跑對應原生紅綠及零選中／編譯錯控制
tags:
  - type/verification
  - status/pass
  - scope/evals
plan_refs:
  - "[[Projects/測試品質工具接線_計劃]]"
system_refs:
  - "[[Systems/test-quality-cli]]"
  - "[[Systems/test-quality-multilang]]"
---
# 測試品質工具接線_CSharpAndroidiOS原生消費驗證

## 原生範圍與卷證

獨立消費專案 /Users/enzo/lumos-test-quality-lab-20261008 的csharp/android/ios，可由根目錄run_experiment.py選棧重跑；可信本機原生命令與平台啟動要求見README。原始卷證歸檔 governance/eval/results/test-quality-three-platforms-20261008；source附件用.txt不可變資料，原始xcresult壓成zip，搬移不是重跑。

[S6] C# run-e20xop57：SDK9.0.117/net9.0、xUnit2.9.2、VSTest17.12.0、adapter2.8.2、JUnit logger4.1.0。基準3／還原3／重構3全綠，價格回0故障2個目標assertion紅。原始TRX、JUnit、退出碼、鎖版與來源快照齊。
[S6] Android run-f1kw9ly6：AGP8.13.2/Gradle8.13/Kotlin2.2.21/JDK17、JUnit4、SDK36編譯/API35独立模擬器。3個Local unit與2個裝置instrumentation基準及還原5綠；故障2價格+1平台儲存目標紅。裝置前置驗app包名，清私有preferences，驗新store可讀90及負數拒絕理由／沒有儲存副作用。兩命令原始XML各自保留後匯整。
[S6] iOS run-bd7n9ned：Xcode26.6 build17F113/iOS26.5模擬器、XCTest、XcodeGen2.46.0、xcbeautify3.2.1。3價格+2平台UserDefaults基準及還原5綠，故障2價格+1儲存目標紅。suite為test-only，setup/teardown清除；負數驗領域錯誤與不寫入。保留.xcresult、formatter及xcodebuild退出碼；原生65轉共同非零1不構成assertion歸因證明。
[S7] 每棧zero-selected與compile-error均invalid。C# runtime-error-krunqagf/capture有真實InvalidOperationException失敗，但check回invalid，未計detected。核心22控制／相關子集2passed 0failed，包含一般例外訊息提斷言名稱不作歸因。
三棧Semgrep掃描各列1自比候選；copiedAlgorithm反例未由有限規則檢出，不依零候選放行。Node run-ko7n2ab7與Laravel run-ydr022x1原生回歸仍detected／not_assessed，未改來源判準界線。

## 重構範圍核對

原先amount*9/10雖測試綠，固定寬度整數中間乘法有溢位風險，不能宣稱對所有非負100倍數等價。原始refactor階段保留為當時實驗，不拿它授予等價資格；補跑refactor-safe使用(amount/10)*9，check-safe核對新卷證。對非負100倍數，整數除10先為整數q，原式10q-q=9q，中間9q不超過原值，避開乘法溢位。工具標green-reported-equivalence-unreviewed；推導另列，不由綠燈自動判等價。

REVISIT:[when-file:scripts/test_quality.py][by:2026-11-08] 變更報告歸因或framework/reporter時重跑typed與抹型別正反例，以及原生零選中／編譯錯與還原。

## 外推邊界

只授予本次固定合成案例的部分原生驗證，不授予整棧synthetic-verified或project-verified。C#不推論ASP.NET/NUnit/MSTest；Android不推論UI/Compose/生命週期或其他API/真機；iOS不推論Swift Testing/UI/真機/其他destination與reporter版本。全部oracle是declared、verdict not_assessed；沒有模型呼叫或代碼審收斂輪數改善量測。報告可偽造，一致性核對不是執行真實性認證。

refactor-safe三棧均實跑綠，check-safe.json均detected／not_assessed；原先不安全的refactor原始卷證不覆寫。Node run-_ldjjq_z、Laravel run-xfpefp10另重跑先除再乘版本均detected，保留在node-safe-compatibility/laravel-safe-compatibility。C#全部5測試綠；Android與iOS的兩個故意反例也在原生runner綠，只證明它們不能由綠燈視為合格。

AGP instrumentation XML也可能沒有type/message，只把首個java.lang.AssertionError及JUnit斷言stack放正文；用原生樣本補認首個例外與Assert frame，不從nested cause提到斷言名作歸因，正反例各留一個控制。

收工交叉審計：乾淨agent唯讀圖譜×程式×原生卷證核對無finding，manifest729項hash一致，三棧check-safe用當前CLI均detected/not_assessed。相關子集2passed/0failed；22個收證控制通過。doctor全圖譜0issues／786篇；30段386條既有提醒屬全圖譜健檢。獨立模擬器已關閉，重跑按README啟動。

原生驗收當時五消費專案vendor收證模組與當時本機來源hash一致，所有implementation目前hash對回各自restored快照，未殘留故障或重構實作。
