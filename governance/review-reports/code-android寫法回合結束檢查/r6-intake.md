# code-android寫法回合結束檢查 r6 收貨(2026-11-07)

範圍:第五輪修正差異 `adf857791..eb555321f`,排除卷證目錄(r6-repair.patch,1783 行),七席都看整份。第五輪處置閘已過;照代碼審手冊步驟 5 加開這一輪(cap-decision extra-round、回顧已補 r5)。修正關卡 r5 通過。

## 收貨三道

- 正規化:七份皆已是正規化格式。
- quote-check:六份全數錨定;資源 clean、沒有引句。

## 前輪驗收

- 第五輪 14 條:各席核對皆修好(正確性 skip-worktree、assume-unchanged 與 git status 一致,入口收子目錄;邊界子目錄專案筆記動過靜默放行、無副檔名腳本點得到;資安九個 Python 入口 × 五種 PATH 零命中、對照組命中;合約第五輪 F1–F4 改壞重做皆紅、`t_r5*` 新測試抽查非等價改壞全紅;資源洗 PATH 10 萬項 0.016 秒)。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 六正1、六邊1、六通1、六約1 | 四席各自實跑:子目錄專案根 `sub/`,兄弟目錄 `other/b.py` 刪除,收工點名列出 `other/b.py(已刪除)`,同時有 `sub/` 改動時擋停;改 `other/b.py` 或新增 `other/c.py` 不點名(活檔有專案範圍判斷、刪除分支沒有);主線舊版同樣不判(既有問題,子目錄路徑接對之後才碰得到) | HIT |
| 六安1 | 席位實跑:`PATH=":/usr/bin:/bin"`、repo 根放 `python3.14`,`pre-push` 執行了 `./python3.14`;放 `bash` 時第一行 `#!/usr/bin/env bash` 就解到 `./bash` | HIT |
| 其餘 minor | 讀碼與席位實跑 | HIT |

## 先查世界

PRIOR-ART:PATH 空項第四次(r3 ast-grep、r4 `_trusted_lumos`、r5 Python 入口裸名 git、r6 shell 掛鉤)——POSIX:PATH 的空項等於目前目錄(https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap08.html ,上一輪已補進計劃)。天花板:PATH 有空項時,使用者自己在那個目錄打的 `git`、掛鉤第一行的 `env bash`、AI 用 Bash 跑的任何指令都可能解到目前目錄——這是環境層缺口,工具只能保證自己不再多開一條路。採用:三支 shell 掛鉤開頭同樣濾 PATH、找到的 python 不是絕對路徑就不用;第一行 `#!/usr/bin/env bash` 不改(改成 `/bin/bash` 會在 bash 不在 `/bin` 的系統壞掉,而且第一行在任何程式碼前就被解析),寫進天花板。若下一輪仍只抓到這種環境層變形,停下攤給人裁,不再逐輪追。
PRIOR-ART(使用者提醒「收斂不了就上網找印證方式」後補查;前幾輪只查了指令用法、沒查整類解法):
- PATH 類方向印證——Go 1.19 起 os/exec「will not resolve a program using an implicit or explicit path entry relative to the current directory」,解析結果相對於目前目錄就回 ErrDot(https://pkg.go.dev/os/exec );CWE-427 防護建議「Remove or restrict all environment settings before invoking other programs」、只用完整路徑,並寫明濾掉危險項「might not be a complete solution」(https://cwe.mitre.org/data/definitions/427.html )。結論:方向對(入口清 PATH + 拒相對解析結果 = 這兩條),錯在沒一次套到所有入口;shell 掛鉤是最後一類入口,第一行 env bash 屬 CWE 寫明的不完整面,記天花板。
- 子目錄類形狀更正——prek:專案根不一定等於 git 根,掛鉤只看自己專案的檔、檔名相對專案(https://prek.j178.dev/monorepos/ )。結論:要換形狀——在唯一出口 `_git_status_entries` 整批濾掉專案外條目,不在下游各分支逐處判(r4、r5、r6 連三輪逐處補正是這個症狀)。已通知修補代理改做。

## 分組與去向(輪內有 major;9 條全折)

- M1 刪除檔專案範圍:六正1、六邊1、六通1(major);六約1(minor)
- M2 shell 掛鉤 PATH:六安1(major)
- M3 小項:六安2、六通2、六架1、六架2(minor,說明與天花板)

修補派給乾淨的修補代理,臨時目錄 `/tmp/lumos-seat-work/乙線修補r6/`。
