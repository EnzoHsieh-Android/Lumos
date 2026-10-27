# code-loop-fix-list-std r1 收貨紀錄

preflight-4: ran(文件改動;前一個編號 code-loop-fix-list 為 light,抓到 major 後依規則改走本編號)

## 機械檢查
- 架構對齊-sonnet:正規化 ✓、引句全數錨定、refcheck 8/8。當處置清單載體。
- 單審-sonnet:正規化 ✓、refcheck 12/12;引句 3 句有 1 句錨不到(C1,引句內又包「」被截斷,且逗號寫成半形)。

## 錨不到的引句機械重現
| id | 做法 | 結果 |
|---|---|---|
| C1 | `grep -c '它就是本節第6步' governance/review-reports/code-loop-fix-list-std/r1-snapshot.patch` | HIT(1 筆,原文是全形逗號「，不另開第二個落點」);採信 |

## 處置(全折,修在同一個提交)
- A1、A2(手冊指路處複述了做法):06 與 SKILL.md 第5步的指路句縮成只指向〈先列出處清單再修〉。
- C1(rN-repro.txt 說成「就是」第6步證據):改寫成修補當輪的完整原始輸出,intake 照收貨格式寫重現命令、摘錄與 HIT/MISS;下一輪第6步可連到它,但證據仍由新席自己查證。
- C2(分開提交沒交代推前壓成一個):改成暫時本機提交,推前壓成一個,兩端提交碼存進下一輪的 rN-repair-binding.json。
- C3(「複雜度上限」沒定義):改寫成「推送前新增告警閘的函式複雜度」,「拆小」改成「拆函式」。
