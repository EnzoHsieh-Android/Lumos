# r2 收貨紀錄(最低python版本改3-14)

## 席位收貨

- 凍結材料:r2-snapshot.md(106 行,sha256 e1302f43…),工作副本放編排者暫存區;7 席全新:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet(Sonnet 5.5);外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。派工詞告知這是第 2 版修訂稿、新增段落要同等嚴格、不准讀第 1 輪席報告。
- 7 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的提交,席位沒動 repo。
- 架構對齊席第一次交的報告用「問 1–問 4」段落、沒有逐條 `## F<n>` 標題與獨立 severity、引句行,機器數出 0 條。沒有改它的報告;請同一席只改格式、不改判斷與內容重交(續談只問它自己講過的話),重交後 3 條、引句全錨定。
- report-normalize 7 份;quote-check 7 份全錨定。
- 發現 53 條(正確性 14、接手 13、邊界 8、外家 7、回滾 5、併發 3、架構對齊 3;機器數 `## F<數字>` 標題),major 29(正確性 7、外家 7、邊界 6、接手 5、回滾 2、併發 1、架構對齊 1)。
- 多席獨立報到的同一件:`LUMOS_PYTHON` 指到包裝腳本無限重跑(正確性、邊界、接手、併發、外家)、get.sh 的 `--pull` 解不了舊複本(正確性、邊界、接手)、`{python}` 代入點不齊與引號(正確性、架構對齊、接手、外家)、Windows 包裝挑到商店替身(正確性、邊界、外家)、`git config lumos.python` 寫入時機(正確性、邊界、併發)。
- 有 major,accepted 為空,全折。

## 機械重現(編排者在 clone-314 讀碼或實跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 接手 F1 / 正確性 F3 / 邊界 F2(get.sh --pull 在 source 之後才生效) | `grep -n "pull\|bootstrap" get.sh` | HIT:`--pull` 只放進 ARGS 轉給 bootstrap(第 25、44 行),拉新發生在 bootstrap 裡 |
| 外家 F3(post-commit 只找 python3/python) | `grep -n "command -v" scripts/hooks/post-commit` | HIT:第 95 行 `command -v python3 \|\| command -v python` |
| 正確性 F5 / 邊界 F6 / 外家 F4(lumos.cmd 只看名字在不在) | 讀 scripts/lumos 的 _install_windows_shim | HIT:`next((c for c in ("python3", "python") if _shutil.which(c)), "python")` |
| 接手 F10(精簡版生成器帶走模組層語句) | 讀 scripts/slim-gen.py 開頭說明 | HIT:「root 集合必須含 module-level 語句與 class body」 |
| 正確性 F7 / 接手 F11(消費專案 CI 範例不存在) | `grep -n "setup-python\|runs-on" scripts/lumos`;讀第 24290 行附近 | HIT:沒有完整 workflow 範本,只有 doctor 提醒裡印的單一 `run:` 步驟(筆記形狀擋、存量漂移、筆記內容審三處) |
| 正確性 F1 / 邊界 F1 / 併發 F1 / 接手 F2 / 外家 F2(包裝腳本無限重跑) | 讀修訂稿第 2 點的條件(版本低於 3.14 或 `LUMOS_PYTHON` 不是目前這一支,都比 realpath) | HIT:包裝腳本啟動的真正路徑與設定的路徑永遠不同,條件恆成立;防重跑變數只攔「版本仍舊」 |
| 外家 F1(舊版更新程式漏發新共用檔) | 讀 scripts/lumos 的 _VENDORED_TREE_FILES 用法(行程啟動時載入的精確名單) | HIT:更新程式照自己記憶體裡的名單複製,不認得新版才加的檔 |
| 其餘 | 讀碼核對各席引的 file:line(refcheck 全在) | 採信;席位附的實測(併發 F1 的 200 次重跑 11.8 秒、邊界 F3 的 perl 回 0、正確性 F12 的 0.22 秒)沒有逐條重跑 |

## 處置

- 全部折入。同一類問題(r1 為了補洞新加的機制又冒 major)連兩輪,換形狀、整類拿掉,細節寫在計劃〈審計修正紀錄〉r2 一段:找 3.14 只留 lumos 裡一份並新增 `lumos python-path`;拿掉掛鉤共用 shell 檔、`git config lumos.python`、perl 逾時、`LUMOS_PYTHON` 在本體生效。
- 因機制拿掉而不再成立的發現,仍逐條列進 folded(處置=拿掉那個機制),不列 refuted。
- refuted 無;accepted 無。
