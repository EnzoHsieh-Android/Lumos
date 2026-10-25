severity: minor

## F1 兩支範本「一字不差」只比了判斷式的尾段,守衛與筆記說的比實際強
severity: minor
blocking: 否
file: `scripts/test_lumos.py`(t_android_e2e_preflight_stability_tools 末段)、`docs/lumos-toolchain-knowledge/Systems/android-e2e-acceptance.md`(該條 WHY)
失敗場景:測試只檢查 `cond = '.get("test_data") or {}).get("value")'` 這段子字串有出現在兩個檔案裡。收集腳本實際寫的是 `bool((st.get("test_data") or {}).get("value"))`,e2e 範本寫的是 `((cfg.get("stability") or {}).get("test_data") or {}).get("value")`,兩邊前半段本來就不同。把收集腳本改成 `test_data = not bool((st.get("test_data") or {}).get("value"))`(語意相反,字面仍含那段)時,這條比對照綠。
但這個改壞不會漏出整體:收集腳本自己的 t_android_memstab_collect_test_data_gate 會紅。所以影響是文字說得比守衛強,不是保護缺口。
歸因:有證據的原有漏查(這條比對是上輪修補新加的,修前不存在;修後才第一次有這句承諾)。
- 修後:在 after 副本改收集腳本成 `not bool(...)`,跑 `-k android_e2e_preflight`,結果 18 passed,0 failed(照綠)。
- 同一改壞跑 `-k collect_test_data_gate`,結果 10 passed,5 failed,會紅。
- 修前:沒有這條比對,無對照。

引句:「    # 兩邊的判斷式要一字不差,只改一邊這條就紅」
筆記同一處寫「同一句判斷式(測試比對兩邊一字不差)」,與實際只比片段不符。

## F2 README 回傳碼表仍把「少了工具」當成回 1 記沒判完的例子,但這次改動之後最常見的缺工具會回 2
severity: minor
blocking: 否
file: `README.md` 與 `README.en.md` 的回傳碼表
失敗場景:e2e 段開了 stability 且沒有 trace_processor 時,新的開跑前檢查在動 App 前就回 2,不寫紀錄。表上卻寫「1:有一塊沒跑成(例如少了工具,會記成沒判完)」,2 的清單也沒列缺工具。照 README 預期的人會預期有紀錄,實際沒有。整套跑與 `--preflight` 都一樣。
歸因:有證據的修復回歸(這次主題改動使例子過期,文件同一個提交裡沒對上)。
- 修後行為:after 副本跑 `-k android_e2e_preflight`,「開了穩定性、缺 trace_processor」兩種模式都是 rc=2,訊息為「找不到 trace_processor…」。
- 修前:before 副本(4f2d4fab)同案例也是 rc=2,只是訊息句式不同。所以 rc=2 這件事是首輪主題改動帶來的,不是第二輪修補造成的。
- 驗證紀錄表格 lab-full-1、lab-full-2 的「回傳 1」是修前實測,有註明是當天事後才加檢查,可讀懂。

引句:「| 1 | 紀錄寫好了，但有一塊沒過，或有一塊沒跑成（例如少了工具，會記成」

## 三問

① 原問題的修復效果:
- 修復點是補「只有最外層 stability、e2e 段沒開」的案例、整套跑也驗放行、擋下訊息改為「找不到 <工具>」句式、補判斷式比對。
- 修前的程式本來就用 e2e.get("stability") 當開關。before 副本用 after 的測試跑,紅的只有 4 條,都是訊息句式斷言;最外層案例本身修前就會過。所以「讀最外層」是補測試封住,不是修掉一個真缺陷。
- 我在 after 副本把開關改壞成 cfg.get("stability"),新案例紅 2 條(`-k android_e2e_preflight`:16 passed,2 failed),證明這個新案例能抓到那個改壞。

② 修補處的正常、錯誤與相鄰呼叫路徑:
- 條件與環境變數(TP、JAVA_HEAP_DUMP,預設值 trace_processor、java_heap_dump)和收集腳本一致。收集腳本讀 cfg["stability"] 最外層的 test_data.value;e2e 範本同樣讀最外層,不讀 e2e 段。
- 設定型別怪的情況:這段的型別穿透(stability 非物件、test_data 非物件)被前面的 `lumos macrobench --check-config`(`_e2e_cfg_err`、test_data 形狀檢查)先擋,所以不會走到 `.get` 丟 AttributeError。
- 順序:先查 ADB、MAESTRO,再查這兩支,最後才是 judge --precheck。擋下時沒碰 App,測試有斷言(installed.apk、maestro.log 不存在)。
- 整套跑的放行也有斷言(installed.apk 存在)。

③ 新發現的同一案例修前修後:
- F1:修前沒有該比對;修後「收集腳本語意改反」測試照綠,另一支收集腳本測試會紅(見上)。
- F2:rc=2 前後一致;文件例子的過期是首輪主題改動造成,不是第二輪修補造成。

## 圖譜鏡頭

- 測試假綠形態(INVARIANT:還原翻紅釘須配前置斷言證明現場成立):本次新增的案例有前置斷言(「擋下時沒碰 App」「整套跑時開跑前檢查放行」要求 installed.apk 存在),且我以改壞確認會紅,不影響。
- test-quality-handbook、arch-alignment-lens:不影響,新測試有獨立判準(各案例預期值寫死,不是把實作重寫一次)。F1 的字面子字串比對只是較弱的輔助守衛。
- lumos-cli-read、bound-tests-gate、canary-audit、guard-kill、lumos-cli-lifecycle:本次沒動它們各自合約綁定的行為,只是 scripts/test_lumos.py 被改動而列為牽連檔。不影響。
- anchor-baseline.json 的簽章更新:雜湊值變動符合 test_lumos.py 被改動,未發現不對。

已驗範圍:`-k android_e2e_preflight` 在修前、修後各跑一次;兩個改壞實驗(收集腳本判斷式反轉、開關改讀最外層)。未驗:全套測試、真機、HUP 或中斷路徑(不在本次改動內)。

兩條都是文字與守衛精度的小問題,程式本身的條件、環境變數與兩種模式的行為都與收集腳本一致。
