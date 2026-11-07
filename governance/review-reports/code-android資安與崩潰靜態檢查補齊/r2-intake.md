# r2 收貨紀錄(code-android資安與崩潰靜態檢查補齊)

兩席新席(審查二、架構對齊二)全數交回後才寫進卷證;報告從逐字稿取最後一則。審查二初版 Finding 1 標 major 卻寫 blocking: 否(兩欄矛盾),退回該席自己重判,重交版改成 major/blocking: 是,其餘不動。兩份 quote-check 全數錨定。

編號:審查二 R4(major)、R5、R6(minor);架構對齊二 A4(minor,多行 ignores)、A5(major,兩套除錯判法)。

歸因(照修補鏡頭):R4 審查席判「未判定(修補新增程式自帶的覆蓋缺口)」;A5 是 r1 修補把除錯判斷再抄一份帶出的(有證據的修復回歸:r1 修補差異 r2-repair.patch 新增那段);R5、R6、A4 是原有漏查。

## 先查世界

- PRIOR-ART:A5:ast-grep 官方支援 sgconfig 的 `utilDirs` 放全域共用規則、規則用 `matches: <id>` 引用(https://ast-grep.github.io/guide/rule-config/utility-rule.html ),本機 0.51.1 在暫存區實跑可用;採用,同一包四條規則共用一份。判法沿用 r1 定案的「只認除錯旗標成立那一支」,另依審查二 ②實跑結果補「只用且接別的條件」也算除錯版(`if (BuildConfig.DEBUG && x)` 只在除錯版成立)。
- R4 R5 R6 A4:補案例與等價寫法,不查外部。

## 出處清單

- 認除錯旗標的規則:`grep -rn BuildConfig configs/ast-grep/kotlin-android/rules*/` → API-19(`kt-http-logging-body-unguarded`)、DATA-16(`kt-room-destructive-migration`)、API-40、API-41,四條全改用共用判斷。
- 讀 ignores 的位置:只有 `load_rules`;改後全規則包 22 條寫了排除的規則都讀得出非空清單(單行、多行兩種寫法)。

## 重現(修前紅、修後綠)

| id | 驗法 | 結果 |
|---|---|---|
| R4 | 共用判斷各拿掉 else、when、且、或子條件 | HIT:各自翻紅 C25/C07/C32、C26、C27、C28 |
| R5 | 新增 C29 不帶接收者的 setAllowFileAccessFromFileURLs | HIT:修前沒有案例;修後綠 |
| R6 | 新增 C30 `?.`、C31 屬性賦值 | HIT:修前規則不報;補寫法後報 |
| A4 | load_rules 讀多行 ignores | HIT:修前 4 處多行讀成空清單;修後全非空 |
| A5 | grep 兩套判法 | HIT:修後四條都只 `matches: kt-in-debug-only-branch` |

另:API-19 改用共用判斷後 `if (BuildConfig.DEBUG) Level.NONE else Level.BODY` 改前不報、改後報(C32);DATA-16 的 `if (!BuildConfig.DEBUG)` 改前不報、改後報(C34)。既有 API-19、DATA-16 的好例樣本照樣 0 命中、壞例照樣命中(`check.py --sg` 規則 211 條、0 個問題)。修後 `-k kotlin_rulepack` 99 passed、`-k kt_catalog` 48 passed。
