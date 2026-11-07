# code-android寫法回合結束檢查 r5 收貨(2026-11-07)

範圍:第四輪修正差異 `ffce2c71a..adf857791`,排除卷證目錄(r5-repair.patch,1609 行),七席都看整份、不拆包。第四輪處置閘已過;照代碼審手冊步驟 5 加開這一輪(cap-decision extra-round、回顧已補 r4)。修正關卡 r4 通過。

## 收貨三道

- 正規化:正確性席把等級寫在清單項裡,用 `report-normalize --write` 純格式搬成獨立行(改 2 處,不改等級與引句);其餘六份已是正規化格式。
- quote-check:正確性、邊界、通才、資安、架構對齊全數錨定;資源 clean、沒有引句;合約席 4 句有 1 句(F4)錨不到——引的是這輪沒改到的 `--worktree-nofilter` 說明文字,編排者在現檔 `scripts/lumos:76897` 機械重現,HIT。
- 合約席說共用暫存區有 973 份 `gctl-run-*`、分不出是誰的,依規定沒有整批刪;編排者也不整批刪(可能有別的會談的)。

## 前輪驗收

- 第四輪折入 16 條:各席核對皆修好(資源 2100 支候選 1.25 秒、55MB;Counter 最壞輸入 0.15 秒;資安五支鉤子 × 四種 PATH 二十組都回可信 lumos;合約四個邊界改壞皆紅;正確性子目錄、CR、換行、16 種怪檔名皆對)。放行兩條(四約1、四資源3)沒有被推翻。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 五邊1、五通1 | 席位實跑:`CLAUDE_PROJECT_DIR=<repo>/sub`,鉤子拿 repo 根相對路徑接到子目錄,筆記改了仍擋收工、無副檔名腳本漏點;用主線 7eaad22 舊版鉤子跑同情境輸出相同(既有問題) | HIT |
| 五通2、五正2 | 席位實跑:`impact --worktree-nofilter --repo <子目錄>` 在入口被「找不到 git 專案」擋下 rc2 | HIT |
| 五正1 | 席位實跑:sparse-checkout 排除的檔報 D、skip-worktree 改過的檔報 M,`git status --porcelain` 皆空 | HIT |
| 五安1 | 席位實跑:`PATH=":/usr/bin:/bin"`、repo 根放可執行 `git`,`ci-status-hook.py`、`stop-lint-hook.py` 都造出標記檔 | HIT |
| 五約1 | 席位改壞:拿掉 `S_ISREG` 守衛相關子集全綠;FIFO 情境卡在 open 20 秒 | HIT |
| 其餘 minor | 讀碼、席位實跑與改壞實驗 | HIT |

## 先查世界

PRIOR-ART:照 PATH 找程式第三次被打穿(r3 ast-grep、r4 `_trusted_lumos`、r5 裸名 `git`)——同類第三次,不再逐支工具解路徑,改成程序一開始把 PATH 的空項、`.` 與相對項清掉(只留絕對路徑項),之後所有子程序都吃乾淨的 PATH;既有的逐支解析保留當縱深。POSIX 規定 PATH 的空項(開頭、結尾或連續冒號)等於目前目錄,這正是被利用的成因(出處由修補代理查官方文件補進計劃〈依據來源〉)。
PRIOR-ART:sparse-checkout 與 skip-worktree——git 官方 `git ls-files -t` 會標出 skip-worktree(`S`)等狀態(https://git-scm.com/docs/git-ls-files );採用:讀旗標、整支略過,跟 `git status` 一致。
PRIOR-ART:子目錄專案——同上一輪:`git status --porcelain` 的路徑從 repo 根算起;鉤子入口先把專案根換成 `--show-toplevel`,下游接路徑就一致。這是主線原本就有的問題,這輪一起收。

## 分組與去向(輪內有 major;14 條全折,不放行)

- L1 子目錄專案端到端:五邊1、五通1、五通2(major);五正2(minor)
- L2 sparse-checkout 與 skip-worktree:五正1(major)
- L3 PATH 換形狀:五安1(major)
- L4 測試補洞:五約1(major);五約2、五約3(minor)
- L5 查詢文字順序:五通3、五約4(minor)
- L6 架構小項:五架1、五架2、五架3(minor)

修補派給乾淨的修補代理,臨時目錄 `/tmp/lumos-seat-work/乙線修補r5/`。
