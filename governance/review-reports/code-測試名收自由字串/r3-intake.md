# code-測試名收自由字串 r3 收貨與處置

七席收齊後一次存檔;report-normalize 只做格式搬移。兩份退回或補正格式:架構對齊席首交的引句是自己的歸納、多一組等級宣告,退回原席照格式重交(判斷未改);資源席首交那條沒有獨立 severity 行,退回重交(內容未改)。整合席那份是編排者存檔工具從第一個 severity 行截取,切掉了開頭總述與 F1 標題,改存全文再由 report-normalize 補檔級行(工具已改成存全文;其餘已存報告逐份檢查,第二行都不是 blocking,沒有同樣被切的)。共 15 條(正1–3、邊1–3、資1、整1–3、通1–3、架1–2;資安 clean 0 條):major 1 條(正1),其餘 minor。引句全數錨定。上限輪(3/3),照使用者裁定「代碼審跑滿上限時折完就合併」:全部折入,駁回 0 條,折完不再派新席,cap-decision 記 accept-risk 並寫跑滿回顧。

## 根因分組與編排者裁定(交作者照做)

- G1 拼名撞名跨檔誤判(正1,major):describe 加測試的拼名只在同一支檔裡配對(標題帶來源檔,group 與 test 同檔才拼);補「不同檔不算撞名、同檔照算」兩支測試,用真檔案經 _raw_test_titles 跑。
- G2 撞名判斷與實際選取不一致(正3、邊3、通2,含 @tag 結尾的名字;正2 describe 結尾整字邊界沒測試):統一規則——撞名一律用執行器實際會用的那條篩選式去比每個標題(regex_tail 就拿 `\s<跳脫後>(?:\s@\S+)*$` 對標題做 search),不再先剝標題 tag 再字面比;補 `login @smoke` 對 `login @smoke @slow`、`x login @smoke`、describe `XFoo` 加 test `Bar` 對名字 `Foo Bar` 三支測試。
- G3 撞名迴圈重算(資1):每個平台的標題預處理只做一次,不隨綁定名重算;tag 尾巴樣式改成不回溯的寫法;補 1000 名 × 22000 標題的耗時測試。
- G4 頭尾空白標題(通1):「頭尾有空白的標題不收」只用在錨定比對的平台(Playwright 的 regex_tail);Jest/Vitest/Flutter 照修前收修剪後的名字。各補一支。
- G5 Windows 引號(邊1):`{method}` 在 Windows 上改用跟 `{python}` 同一套的雙引號寫法(`list2cmdline`),不用 shlex 單引號;補一支模擬 win32 的測試看展開形狀。
- G6 多行字串分支記憶體(邊2):三引號與 `@"` 分支改成不推重複狀態的寫法(展開式或逐段 find),補一支 8MB `"""` 後接大量孤立引號的記憶體測試,拿掉修法要紅。
- G7 測試只比字串(通3):Playwright 錨定測試補「用 Python re 對真實標題字串 search」的行為斷言(帶 tag 選得到、relogin 選不到)。
- G8 文件與訊息(整1、整2、整3、架1、架2):S50、bound-tests-gate、`_name_filter_escape` docstring 的舊錨改成現行;file_name_match 補進計劃做法 5、test-profile-multiplatform、reference.md 的覆蓋欄位清單;Android 兩篇舊計劃剩下的識別字說法加「已被取代」註;spec-gate tests-exist 與 bad-name 那兩處擋下訊息改用 `_TEST_NAME_RULE_ZH`;`_TEST_NAME_RULE_ZH` 的 200 與 Windows 字元改由 `_TEST_NAME_MAX`、`_WIN_CMD_SPECIAL` 組出,不手寫。
