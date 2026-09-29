# r1 收貨紀錄(code-最低python版本改3-14)

凍結材料:4990a90a..605b0a65 的 git diff -U10,3384 行,超過 1800 行,拆成五份(每份指紋見 r1-dispatch.json 同目錄的 patch 檔):
- r1-snapshot-a.patch(scripts/lumos,797 行)、r1-snapshot-b.patch(scripts/test_lumos.py,808 行)、r1-snapshot-c.patch(圖譜筆記,567 行)、r1-snapshot-d1.patch(掛鉤、安裝腳本、設定、CI,845 行)、r1-snapshot-d2.patch(README 類文件,252 行);整份 r1-snapshot.patch 留作記帳的審材。
分級:pitfalls --diff 判 standard(有程式檔、沒命中風險型樣)。這批改的是推送閘本身,多派了資安與外家兩席。
5 席:單 reviewer 兩席分段(核心 opus 審 a+b、掛鉤與安裝 sonnet 5.5 審 d1+d2+c);架構對齊 sonnet、資安 sonnet 審 a+d1;外家 Codex(gpt-5.6-sol xhigh,唯讀沙盒)審 a+d1。

## 席位收貨

- 5 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 5 份都已是正規化格式;quote-check 5 份全錨定;refcheck 只有一條「不存在」(核心席寫的是它自己臨時目錄裡的路徑 docs/proj-knowledge/Systems,不是 repo 的檔)。
- 發現 13 條(核心 5、掛鉤與安裝 3、架構對齊 1、資安 2、外家 2);major 4(核心 F1、核心 F2、架構對齊 F1、外家 F1),其餘 minor。
- 多席獨立報到的同一件:doctor 會執行別人的掛鉤(核心 F1、資安 F1);找不到時的候選清單丟掉不存在的(核心 F5、外家 F2)。
- 本輪有 major,accepted 必須是空的,13 條全折。

## 機械重現(在審的那一版 605b0a65 上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 核心 F1 / 資安 F1(doctor 執行別人的掛鉤) | 臨時 HOME 的 settings.json 註冊一支寫標記檔的 notify.sh 與一條 shell 條件式,跑 `lumos enforcement --json` | HIT:標記檔多一行 `RAN -c` |
| 核心 F2(升級注意印不出) | 讀 _vendor_toolchain 與 _pull_source_or_abort:拉新在同一個行程裡做,之後才走到升級注意的判斷 | HIT:讀碼確認,執行的是拉新前載入的程式 |
| 核心 F3(doctor 測試 ③ 不會紅) | `grep -n "return 1 if strict else 0" scripts/lumos` | HIT:不加 --strict 回傳碼恆為 0 |
| 核心 F4(註解矛盾) | 讀 python-floor begin 那行與 gate begin 那行 | HIT |
| 核心 F5 / 外家 F2(候選清單不全) | `env -i PATH=/definitely-missing HOME=/tmp LUMOS_PYTHON_SEARCH_DIRS=/definitely-missing /usr/bin/python3 scripts/lumos --version` | HIT:「找過的候選」只列 uv 一行 |
| 外家 F1(shell 第一步不認 LUMOS_PYTHON) | `env -i PATH=/definitely-missing HOME=/tmp LUMOS_PYTHON=/opt/homebrew/bin/python3.14 LUMOS_PYTHON_SEARCH_DIRS=/definitely-missing /bin/bash install.sh` | HIT:rc=2,「找不到任何 python」 |
| 掛鉤 F3(只推刪除也擋) | 臨時 repo 放 lumos 與 pre-push,餵一行 (delete),`LUMOS_PYTHON=/nonexistent` | HIT:rc=1;另讀 pre-push:錨點檢查不看 ref、每次都叫 lumos |
| 架構對齊 F1(兩份清單沒比對) | 讀 t_python_launcher_blocks_agree:只讀七支 shell 腳本 | HIT:讀碼確認;席位附的改壞實驗(11 passed)沒有重跑 |
| 掛鉤 F1(CI 只守語法) | 讀 ci.yml 的 3.9 守衛步驟:只有 ruff E9 | HIT:讀碼確認;席位附的 tomllib 實驗沒有重跑,修完用同一個改壞做翻紅 |
| 掛鉤 F2(漏講 Codex 要重新信任) | `grep -n "命令列變了才要" scripts/lumos`;讀升級注意與 README | HIT |
| 資安 F2(Windows 先搜目前目錄) | 本機是 macOS,不能實跑;讀 _py_probe:裸指令名直接交給 subprocess | 採信(推論):3.14 以前的 Windows shutil.which 與 CreateProcess 都先看目前目錄 |

## 處置

- 全部折進程式、測試與筆記(細節在計劃〈實作時的決定〉與〈審計修正紀錄〉代碼審 r1 段):
  - 核心 F1、資安 F1:只看「第二段是 lumos 自家掛鉤檔、第一段像 python」的命令;測試加一格,別的工具的掛鉤不列、不執行。
  - 核心 F2:觀察對,判準改——這次升級第一個專案一定是舊程式在跑 update,新程式裡怎麼改都補不到。改成失敗現場自己講:CI 環境找不到 3.14 時,說明多一行 setup-python 設 3.14;升級注意留給新程式執行 update 的情況(同一台機器第二個專案起);條款 [S9] 照實改寫,測試說明寫明前提。
  - 核心 F3:改比對收尾那行的問題數。
  - 核心 F4:註解改成「只剝呼叫檢查的三行」。
  - 核心 F5、外家 F2:每個候選都列結果,不存在的併成一行;uv 分「沒有這個指令」與「找不到 3.14」。
  - 外家 F1:七份 shell 共用段第一步先認 LUMOS_PYTHON(設了而且能執行)。
  - 架構對齊 F1:測試讀 lumos 的 _py_candidates、_py_fixed_candidates,逐項比對 shell 那份的版本號名稱、預設固定目錄、最後兩個名字。
  - 掛鉤 F1:[S7] 測試加一格,版本檢查之前只准 import 清單上的 3.9 標準庫模組。
  - 掛鉤 F2:升級注意、README 兩份、doctor Q 段的建議都補「Codex 要再開一次互動 codex 審過」。
  - 掛鉤 F3:觀察對,判準不成立——席位說刪除時後段檢查全跳過,但錨點檢查每次都叫 lumos,所以擋下是對的;把理由寫進 pre-push 的註解,行為不改。
  - 資安 F2:新增 _py_which,Windows 上落在目前目錄底下的不收、改用絕對路徑執行;找直譯器、問 uv、挑 Windows 包裝啟動指令都走它。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):拿掉自家掛鉤篩選 → doctor 測試 ⑥ 紅;改 lumos 版本號名稱順序 → 清單比對 ⑧ 紅;shell 不認 LUMOS_PYTHON → 掛鉤測試 ⑦ 紅;檔頭加 import tomllib → 3.9 守衛最後一格紅;拿掉 Windows 目前目錄判斷 → ⑤b 紅;說明丟掉不存在的候選 → ⑤ 紅;doctor 提醒改成計進問題數 → ③ 紅。
- refuted 無;accepted 無。
