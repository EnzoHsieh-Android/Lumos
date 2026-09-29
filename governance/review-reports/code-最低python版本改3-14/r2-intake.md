# r2 收貨紀錄(code-最低python版本改3-14)

凍結材料:r2-snapshot.patch(r1 折入的修正差異 605b0a65..57314d47,git diff -U10,排除卷證目錄與治理帳;1047 行,sha256 85cfdf10…)。只審修正差異,4 席全新:單 reviewer opus(正確性與邊界)、架構對齊 sonnet、資安 sonnet(Sonnet 5.5)、外家 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。

## 席位收貨

- 4 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的提交與 amend,席位沒動 repo。
- report-normalize 4 份都已是正規化格式;quote-check 3 份全錨定,資安席 clean、報告裡沒有引句;refcheck 全部對得上。
- 發現 9 條(單 reviewer 4、架構對齊 2、資安 0、外家 3);major 1(外家 F1),其餘 minor。
- 同一件事被兩席報到的:shell 第一步認 LUMOS_PYTHON 的缺口(外家 F1 看「不驗是不是 python」、單 reviewer F3 看「略過時不講原因」)。
- 本輪有 major,accepted 必須是空的,9 條全折。

## 機械重現(在審的那一版 57314d47 上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家 F1(shell 收任意可執行檔) | 取 57314d47 的 install.sh 共用段 source,`LUMOS_PYTHON=/usr/bin/true` 呼叫 `_lumos_any_python` | HIT:selected=/usr/bin/true |
| 單 reviewer F1 / 外家 F2(自家掛鉤篩選) | 57314d47 的 lumos 載入後,臨時 HOME 註冊 `/nonexistent/python3.14t "${HOME}/.claude/hooks/impact-hook.py"` 與 `/usr/bin/python3 /opt/other/lumos-entry-hook.py`,呼叫 `_hook_python_problems` | HIT:3.14t 那條沒列;/opt/other 那條被當成自家掛鉤列成問題 |
| 單 reviewer F2(目前目錄防護擋整棵子樹) | 同一份 lumos,目前目錄設 /、os.name 暫改 nt,`_py_which("python3")` | HIT:回 None(/opt/homebrew/bin/python3 明明在) |
| 單 reviewer F3(略過不講原因) | 讀 57314d47 共用段:條件不成立直接往下找,訊息是固定字串 | HIT:讀碼確認 |
| 單 reviewer F4(lumos.cmd 缺回頭條件) | 讀計劃〈實作時的決定〉那句 | HIT:旁邊沒有 REVISIT 行 |
| 架構對齊 F1(認自家掛鉤的第三種寫法) | 讀 enforcement_status 的檔名列舉與 _hook_python_problems | HIT:讀碼確認兩處各自列舉 |
| 架構對齊 F2(get.ps1 沒有目前目錄防護) | 讀 get.ps1 的 Get-Command 迴圈 | 觀察屬實;判準不成立——PowerShell 不執行目前目錄裡沒寫路徑的指令,不受同一風險(席位自己標了 ⚠ 沒實測) |
| 外家 F3(uv 逾時說成找不到) | 讀 57314d47 的 _py_uv_find:逾時、執行失敗、沒找到都回同一個 None | HIT:讀碼確認;修完用卡住的假 uv 釘測試 |

## 處置

- 全部折進程式、測試與筆記(細節在計劃〈實作時的決定〉與〈審計修正紀錄〉代碼審 r2 段):
  - 外家 F1、單 reviewer F3:共用段第一步只收絕對路徑、而且實際執行印得出記號的 LUMOS_PYTHON;不合格記下原因往下找,找不到任何 python 時說明第一行講出來。七份一起改、逐字一致。
  - 單 reviewer F1、外家 F2:正規式收結尾的 t;第二段要放在 `~/.claude/hooks` 或 Codex 的 hooks 目錄。
  - 單 reviewer F2:只擋目前目錄本身(Windows)與 PATH 相對路徑項(各平台),不擋整棵子樹。
  - 單 reviewer F4:計劃補上 lumos.cmd 那層的現況與 REVISIT 行。
  - 架構對齊 F1:自家掛鉤檔名單抽成一支 `_own_hook_scripts`,測試守 enforcement 各列找的檔名都在名單裡。
  - 架構對齊 F2:觀察對、判準不成立;把「PowerShell 不需要這道防護」的理由寫進 get.ps1 註解,行為不改。
  - 外家 F3:_py_uv_find 回 (路徑, 說明),逾時、執行失敗、找不到分開講。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):共用段改回只看能不能執行 → ⑦b 紅;正規式拿掉 t → ⑦⑧ 紅;目前目錄判斷改回擋子樹 → ⑤c 紅;uv 逾時改回說找不到 → ⑤d 紅。
- refuted 無;accepted 無。
