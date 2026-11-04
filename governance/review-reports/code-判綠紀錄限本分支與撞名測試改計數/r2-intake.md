# r2 收貨紀錄(代碼審第二輪,7 席;審修前 409ab14f → 修後 6e10ae5b)

收齊後一次寫進卷證;席報告從逐字稿存。七席 quote-check 全錨定、refcheck 全 0 缺。整合席交卷時背景的 `-k spec_gate` 還在跑,之後補報 404 綠 1 紅(t_round_valid_ignores_spec_gate,單獨重跑修前修後都綠,判斷是三組同時跑的負載造成;編排者本輪子集另跑一次核對)。

## 發現、歸因與去向(全折)

| id | 席 | 原報 | 一句 | 席位歸因 | 去向 |
|---|---|---|---|---|---|
| b1 | 邊界 | major | 只寫 remote.origin.promisor 的新式部分複製沒被認出,照樣連遠端 | 有證據的原有漏查(修前兩種都連) | 折:共用 `_git_partial_clone` 認三個設定,回頭條件那支一起換 |
| r2 | 資源 | minor | 同 b1 | 原有漏查 | 折(同 b1) |
| s2 | 資安 | minor | 同 b1(推論) | — | 折(同 b1) |
| a3 | 架構對齊 | minor | 部分複製與淺複製判法把回頭條件那支再抄一份 | — | 折:抽成共用 `_git_partial_clone`,兩處都叫它 |
| r1 | 資源 | minor | 帳被忽略時仍算分岔點、讀那一版的帳,部分複製會觸發自動抓取、60 秒卡住 | 原有漏查(三版相同) | 折:帳被忽略時不算分岔點、直接讀整本工作目錄的帳 |
| g1 | 通才 | minor | 部分複製整批不過濾,修前在這種 repo 反而濾得對 | 有證據的修復回歸(修前 kept 0、修後 1) | 折:寫進天花板三(部分複製沒有這道過濾、GIT_NO_LAZY_FETCH 只有新版 git 有) |
| i1 | 整合 | minor | S6、S8 條款與天花板三沒跟上部分複製的行為 | 有證據的修復回歸(文件漂移) | 折:S6、S8、天花板三改寫 |
| c1 | 正確性 | minor | HEAD 解不出、分支名取不到兩道守衛沒測試 | 原有漏查 | 折:補還沒有提交的 HEAD、分離 HEAD 兩案 |
| g2 | 通才 | minor | 同 c1 分離 HEAD 那半 | 原有漏查 | 折(同 c1) |
| i3 | 整合 | minor | 判不了帳有沒有被忽略就不過濾,沒測試 | 原有漏查 | 折:補 unknown 案例 |
| b2 | 邊界 | minor | S6 同名重開缺前置斷言 | 未判定 | 折:補前置(判綠寫進帳、記分支名、重開後不是祖先) |
| r4 | 資源 | minor | 同 b2 | 原有漏查 | 折(同 b2) |
| i2 | 整合 | minor | 從另一條功能分支切出延續同計劃,舊判綠被丟 | 原有漏查 | 折:寫進天花板五 |
| r3 | 資源 | minor | 大 repo 沒有 commit-graph 時 10 秒問不完 | 未判定 | 折:寫進天花板三(附 git commit-graph write) |
| s1 | 資安 | minor | 帳被忽略的專案壓提交後自己的判綠被丟,比對起點變弱 | — | 折:天花板一補代價一句 |
| a1 | 架構對齊 | minor | deadline=None 的意思跟鄰居相反(自己起算) | — | 折:改成 budget 秒數參數,deadline 語意回到鄰居慣例 |
| a2 | 架構對齊 | minor | 判祖先第三份內聯 | — | 折:註解寫明三處判不了的方向各不同、不抽共用 |
| a4 | 架構對齊 | minor | 取分支名又多一種寫法 | — | 折:改借回頭重讀的 `_note_reread_branch` |

## 根因分組(修前)

1. 部分複製的認法與讀舊版本的時機(b1、r2、s2、a3、r1、g1、i1):一條規則——讀任何舊版本或問不在本機的提交之前,先用同一支判斷認部分複製(三個設定);帳被忽略時根本不讀舊版本。出處清單:`_redbase_on_branch` 的 repo 種類、`_redbase_branch_rows` 的分岔點與讀帳、`_drift_born_env_err`;文件:計劃做法 1 d、S6、S8、天花板三。
2. 判斷路徑沒有改壞會紅的案例(c1、g2、i3、b2、r4):每道守衛補一案。出處清單:`_redbase_on_branch` 的 head、name 兩道;`_redbase_branch_rows` 的 ignored 判定三態;S6 gb3。
3. 天花板沒寫齊(i2、r3、s1):照實補進計劃。
4. 寫法跟鄰居對齊(a1、a2、a4)。

## 修前先查世界

- git 的部分複製設計文件寫明承諾遠端由三個設定各自認定(extensions.partialClone、remote.<名>.promisor、remote.<名>.partialCloneFilter),而且後來的 git 允許多個承諾遠端,只看 extension 不夠。https://www.kernel.org/pub/software/scm/git/docs/technical/partial-clone.html 、https://github.com/git/git/blob/649b59bd8eea1ed7fdf8de2312d27b99f4a2f863/Documentation/technical/partial-clone.txt
- 部分複製整批不過濾(g1)不改:沒有不觸發自動抓取又能問「提交在不在本機」的舊版 git 指令;GIT_NO_LAZY_FETCH 只有新版有(見 r1 收貨紀錄)。寫成天花板。

## 修後逐條改壞(本輪新補 10 條,全紅)

J1 部分複製只認舊式設定、J2 帳被忽略照算分岔點、J3 分離 HEAD 也比分支名、J4 HEAD 解不出照問、J5 判不了是否被忽略也過濾、J6 回頭條件那支不認部分複製、H2 部分複製照問、H1 淺複製回不是祖先當真、H4 分支名用 --short、G1 不比分支名。原始輸出在 r2-repro.txt。

## 重現表

| id | 重現 | 判定 |
|---|---|---|
| b1 | 只設 remote.origin.promisor 的複製,cat-file 查不存在的提交觸發留記號的遠端抓取腳本(新測試前置斷言) | HIT 採信 |
| r1 | 帳被忽略時呼叫過濾,記錄分岔點函式被叫了幾次(修前 1 次以上,J2 改壞紅) | HIT 採信 |
| g1 | 部分複製設定下別分支判綠照留(新測試「部分複製:照留」即此行為) | HIT 採信 |
| c1 | 還沒有提交的 HEAD 拿掉 head 守衛 → TypeError(J4) | HIT 採信 |
