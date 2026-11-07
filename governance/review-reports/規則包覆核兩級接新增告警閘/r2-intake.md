# r2 收貨(2026-11-08,四席 sonnet 新席:通才、正確性、整合、架構對齊)

四席報告全數存檔、正規化、引句全錨定。全輪 27 條(major 5、minor 22)。id:tc 通才、co 正確性、ig 整合、ar 架構對齊,加報告裡的 F 序號。整合席在 /tmp/lumos-seat-work 裝 ast-grep 0.51.1 做端到端實驗,目錄已由編排者刪除。

## 判讀

做 6(分級不數放行過的命中)是 r1 為了解 co1 新加的機制,r2 三席從三個方向打它:指紋算法對不上(ar1、co1、tc9)、自動路徑本來就帶 `--no-lint` 所以前提不成立(co2、ig1,整合席實測 `--no-lint` 時分級是 standard)、讀被審分支自己的放行檔會讓它自己逃審(tc1)。照「折入要新增機制時先寫不加它的最小解」:前提不成立,最小解就是不做,整條拿掉。提示級接閘推翻規則包有效的 RULE(tc3)照專案 CLAUDE.md 第 3 條不自行推翻,這版只接覆核級。

## 先查世界

- PRIOR-ART: 新規則先 Monitor 再 Block——Semgrep 規則模式(https://semgrep.dev/docs/semgrep-code/policies );誤報高的規則不擋——Google 靜態分析經驗(有效誤報壓在一成以下,https://cacm.acm.org/magazines/2018/4/226371-lessons-from-building-static-analysis-tools-at-google/pdf )。採用:提示級先量誤報、一成以下才接。
- PRIOR-ART: 白名單用真實路徑比同一支檔——本 repo `_lint_wt_allow` 判目錄已用 `os.path.samefile` 救 macOS 大小寫。採用同一做法判 `sgconfig.yml`,不用檔名黑名單。
- PRIOR-ART: 工具版本釘死——規則包 CI 已釘 ast-grep 0.51.1;範本跟著釘。

## 逐條去向(全部折入)

| id | 一句 | 去向 | 重現 |
|---|---|---|---|
| tc1 | 做 6 讓被審分支自放行就逃審 | 折:做 6 拿掉 | HIT:讀碼 `_lint_waivers_load` 讀工作目錄 |
| tc2 | 換版本靠 CI 紅做不到 | 折:範本釘 0.51.1;天花板 3 照實寫看不到消費專案 | HIT:讀碼 CI 釘 0.51.1 |
| tc3 | 提示級接閘推翻有效 RULE | 折:這版只接覆核級(做 4、d2) | HIT:讀 kotlin規則包 RULE 欄位齊全、型錄 CO-17 標誤報多 |
| tc4 | d1 留舊目錄名 | 折:d2 取代 d1 | HIT:讀 frontmatter |
| tc5 | about_code 不收目錄 | 折:不補 about_code(yml 不是程式檔),檔案節正文寫 | HIT:讀碼 about_code 擋目錄 |
| tc6 | 規則目錄全空測試會紅 | 折:做 2 寫明要改那段迴圈並簽名 | HIT:讀碼 test_lumos 只刪三目錄 |
| tc7 | 收工黑名單沒處理根因 | 折:做 5 改白名單只准 sgconfig.yml | HIT:讀碼 `_lint_wt_allow` |
| tc8 | SARIF 自檢沒驗目標規則 | 折:做 3 指定兩條規則、驗 ruleId | HIT:讀第二版做 3 |
| tc9 | 做 6 指紋雜湊與搬動行 | 折:做 6 拿掉 | HIT:同 ar1 |
| tc10 | 預算不夠是擋不是略過 | 折:做 4 範本說明照實寫、實務隱患加一條 | HIT:讀碼 undone budget 判擋 |
| tc11 | 20 筆門檻是散文 | 折:拿掉門檻,只量測記錄;回頭看寫進 REVISIT | HIT:讀第二版實務隱患 |
| co1 | `_lint_new_key` 不是放行檔指紋 | 折:做 6 拿掉 | HIT:讀碼 sha256 在 `_lint_new_diff_claims` |
| co2 | 自動路徑本來就 --no-lint | 折:做 6 拿掉、不做清單寫理由 | HIT:讀碼 pre-push、CI、code-loop 分級都帶 --no-lint |
| co3 | 做 6 從哪個清單拿掉不明 | 折:做 6 拿掉 | HIT:同 co2 |
| co4 | 收工比對方式不明 | 折:做 5 用 samefile 比同一支檔 | HIT:讀碼既有 samefile 救濟 |
| co5 | 全空測試與 review_ids | 折:做 2 寫明擴 review_ids、改迴圈 | HIT:同 tc6 |
| ig1 | 做 6 前提講過頭 | 折:同 co2 | HIT:整合席實測 --no-lint 分級 standard |
| ig2 | 收工黑名單 | 折:同 tc7 | HIT:同 tc7 |
| ig3 | 文字同步清單沒列齊 | 折:做 6 列齊 yml 註解、樣本註解、check.py 第三處、兩篇計劃與條款 | HIT:整合席主線 git grep |
| ig4 | 全空測試 | 折:同 tc6 | HIT:同 tc6 |
| ig5 | (b) 類沒有型錄標法與升級路徑 | 折:做 6 定義「不接(rules-unwired)」;做 1 不限嚴重度 | HIT:讀型錄第 11 行 |
| ig6 | 預算不夠是擋 | 折:同 tc10 | HIT:同 tc10 |
| ig7 | 舊專案沒有入口、重複宣告沒人偵測 | 折:不做清單寫明不偵測;範本只兩條、不再叫人另加提示級 | HIT:整合席實測字串不同才重複 |
| ig8 | 量測輸入沒定義 | 折:實務隱患寫明開 include_test_paths 與推送範圍;RETIRE-IF 寫明靠人看 | HIT:讀碼 include_test_paths 預設空 |
| ar1 | 做 6 指紋另寫一套 | 折:做 6 拿掉 | HIT:同 co1 |
| ar2 | 收工黑名單 | 折:同 tc7 | HIT:同 tc7 |
| ar3 | 做 6 過濾位置 | 折:做 6 拿掉 | HIT:同 co2 |

修補因果:tc1、tc9、co1、co3、ar1、ar3 是 r1 新加做 6 造成的(6 條);tc7、ig2、ar2、co4 是 r1 新加做 5 的寫法問題(4 條);其餘是 r1 前就有或 r1 沒看到的角落。
