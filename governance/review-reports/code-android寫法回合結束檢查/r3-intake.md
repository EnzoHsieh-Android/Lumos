# code-android寫法回合結束檢查 r3 收貨(2026-11-07)

範圍:修補差異 `a1456f8f6..8717114b0`(r3-repair.patch,3044 行),拆四包:甲=主程式(1051)、乙=鉤子(258)、丙=測試(1026)、丁=筆記與修正紀錄(709);甲乙、乙丁兩份合包。資安席看整份。high 上限第 3 輪。修正關卡 r2 通過(補了三組同類重犯的說明後重跑)。

## 收貨三道

- 正規化:七份皆已是正規化格式。
- quote-check:正確性(甲)、邊界(乙)、資源(甲)、通才(乙丁)、資安(整份)全數錨定。合約席對它那包(丙)有 2 句錨不到——引的是主程式與鉤子的碼,對整份 r3-repair.patch 全數錨定,記帳時這一席快照填整份。架構對齊席 F4 的第二句引句「n = 1」不到 10 字,同條第一句錨得到,不影響採信。
- 資源席 r3 第一次派工卡在一個 50 支 5MB 大檔的實驗上約一小時沒有回應(程序已結束、結果沒回傳),編排者停掉後續談,要它用已量到的結果交報告;報告裡該實驗標「未跑完」並附預期值。

## 前輪驗收

- 第二輪 25 條:各席核對自己那幾條。正確性 F1(fsmonitor)修好、過濾器名字大小寫與含點都沒漏;邊界 F1–F2 實測修好(21 組訊號時機零孤兒);資源 F2、F3 實測修好,F1 程式已改、大檔實測未跑完;合約 F1–F9 改壞重做皆翻紅;通才 F1–F3 修好;架構對齊 F1–F5 照方向修;資安 F1(嵌套 repo)修好,F2(ast-grep 照 PATH)處置不夠——見本輪三安3。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 三安1 | 席位實跑:過濾器名字含非 UTF-8 位元組,`git config --get-regexp` 列不到,`_lint_wt_git status` 造出記號檔 | HIT |
| 三安2 | 席位實跑:真檔 `check-graph-sync.py` 收工點名的 `git status --porcelain -uall` 與 `git diff HEAD` 在 racy 檔上執行 clean 過濾器 | HIT |
| 三正1 | 席位實跑:HEAD 檔內容寫成 garbage,`rev-parse --verify -q HEAD` 回 128,`_lint_wt_unready` 回 deliberate | HIT |
| 三正2 | 席位實跑:非工作樹路徑 70MB 合法 SARIF 回 ([], False) → env-unavailable 自動放行 | HIT |
| 三約1 | 席位改壞:鉤子插第二個 `_trusted_lumos` 定義,`-k hooks_never_run` 46 過 0 敗 | HIT |
| 三通1 | 席位實跑:`_unchecked_kind({"unchecked_kind": ["x"]})` 丟 TypeError | HIT |
| 三資源1 | 席位實跑:假工具一直吐資料,暫存 SARIF 3 秒長到 3.7GB | HIT |
| 其餘 minor | 讀碼、席位實跑與改壞實驗 | HIT |

## 先查世界

PRIOR-ART:過濾器防護第三次被打穿(r1 嵌套 repo 前的 clean filter、r2 fsmonitor 與嵌套 repo、r3 非 UTF-8 名字與鉤子層)——同一個判讀連輪被打穿,整類拿掉、改不靠名字清單的做法。git 官方:`git hash-object --no-filters`「Hash the contents as is, ignoring any input filter that would have been chosen by the attributes mechanism, including the end-of-line conversion」(https://git-scm.com/docs/git-hash-object );`git ls-files -s` 只輸出索引的「mode bits, object name and stage number」(https://git-scm.com/docs/git-ls-files )。採用:工作樹模式與收工點名不跑 `git status`/`git diff` 對工作樹,改成索引物件編號對工作樹不套過濾器的雜湊;`_git_untrusted_c` 拿掉過濾器列舉,只留固定鍵。代價:用真過濾器(LFS、autocrlf)的專案會多查一些檔(多查不漏查)。排除:再補「名字非 UTF-8 就整次不查」的字表規則(第三次補字表,下一輪同類會再被打穿)。
PRIOR-ART:鉤子共用安全邏輯——`Systems/hook信任邊界`:安全邊界的共用邏輯照逐字複本加守衛(鉤子不能匯入主程式);照用。
PRIOR-ART:失效記成成功第三次出現(r2 通才 F1、r3 正確性 F1、通才 F2)——同類換形狀:判定層不補預設、每條出口明寫種類、沒寫的一律落 failed(fail closed)。

## 分組與去向(輪內有 major;原報 major 全折,原報 minor 三條附理由放行)

- J1 換形狀不靠過濾器名字:三安1、三安2(major);三架3(minor)
- J2 git 出錯不當刻意不查:三正1(major)
- J3 SARIF 上限只管工作樹模式:三正2(major)
- J4 守衛擋重複定義:三約1(major)
- J5 失效分類收成一處:三通1、三通2、三架1(minor)
- J6 鉤子輸入與其他:三邊1、三安3、三資源1、三約2、三約3、三約4、三通3、三架2、三架4(minor)
- 放行:三正3(超大檔縮到上限以下時舊告警當新增——修補刻意取捨、已寫在略過說明,情境窄)、三資源2(64MB 上限下主程式記憶體約 0.9GB,有界、不無限長)、三架5(`_nodehome_cat_*` 沒帶 GIT_OPTIONAL_LOCKS——cat-file 不寫索引、不拿選用鎖,無實害)。

修補派給乾淨的修補代理,臨時目錄 `/tmp/lumos-seat-work/乙線修補r3/`。
