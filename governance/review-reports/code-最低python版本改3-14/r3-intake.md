# r3 收貨紀錄(code-最低python版本改3-14)

凍結材料:r3-snapshot.patch(r2 折入的修正差異 57314d47..b0eff2af,git diff -U10,排除卷證目錄與治理帳;939 行,sha256 edb64a63…)。只審修正差異,4 席全新:單 reviewer opus、架構對齊 sonnet、資安 sonnet(Sonnet 5.5)、外家 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。這是審查上限(standard 3 輪)的最後一輪。

## 席位收貨

- 4 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 4 份都已是正規化格式;quote-check 3 份全錨定,資安席 clean、報告裡沒有引句。
- 發現 8 條(單 reviewer 2、架構對齊 2、資安 0、外家 4);major 3(架構對齊 F1、外家 F1、外家 F2),其餘 minor。
- 同一件事被兩席報到的:uv 非零退出一律說成找不到(單 reviewer F1、外家 F3)。
- 本輪有 major,accepted 必須是空的,8 條全折。
- 上限處置:第 3 輪仍有 major,編排者停下來問人;Enzo 2026-09-29 裁「修完再破例審一小輪」(只審這次修正差異)。

## 機械重現(在審的那一版 b0eff2af 上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家 F2(符號連結繞過目前目錄判斷) | 席位附的 mock 指令:os.name 暫改 nt、shutil.which 回 /repo/python3.14.exe、realpath 把它解到 /repo/tools/evil.exe,呼叫 `_py_which` | HIT:回 /repo/python3.14.exe |
| 外家 F1(假 python3.14 讓閘假放行) | 讀 b0eff2af 的 pre-commit python-314 段:python-path 回什麼就拿什麼當 LUMOS_PY,不驗 | HIT:讀碼確認;修完用一支印 /usr/bin/true 的假 python3.14 釘測試 ①b |
| 架構對齊 F1(Codex 那半沒測試) | 讀 t_doctor_flags_stale_hook_python:假設定全是手寫的 Claude 形狀 | HIT:讀碼確認;席位附的改壞實驗(9 passed)沒重跑,修完用同一個改壞做翻紅 ⑩ |
| 架構對齊 F2(變數撞名) | 讀 `_hook_python_problems`:外層 d 是設定字典、內層 d 被改成目錄字串 | HIT |
| 外家 F4(後綴比對收進別人的 .claude/hooks) | 讀那行 `d.endswith("/.claude/hooks")` | HIT:讀碼確認 |
| 單 reviewer F1 / 外家 F3(uv 出錯說成找不到) | 本機 `uv python find --system --no-python-downloads ">=3.99"` | 對照:沒找到時 rc=2、stderr 是 `error: No interpreter found for Python >=3.99 …`;席位附的壞 uv.toml 也是 rc=2,只能靠訊息分 |
| 單 reviewer F2(LUMOS_PYTHON 被略過卻沒講) | 讀 b0eff2af 共用段:找到別支就 return 0,`_LUMOS_ANY_NOTE` 沒人印 | HIT:讀碼確認 |

## 處置

- 全部折進程式、測試與筆記(細節在計劃〈實作時的決定〉〈誠實界線〉與〈審計修正紀錄〉代碼審 r3 段):
  - 外家 F2:只解析「所在目錄」那一層再比(同一個目錄的兩種寫法都認得),檔案本身不解析;測試 ⑤f 在目前目錄放一個指進子目錄的符號連結。
  - 外家 F1:pre-commit/pre-push 驗 python-path 回的路徑是絕對路徑、執行起來是 3.14 以上的 python 才拿來跑閘;安裝腳本與 post-commit 仍信任 PATH 上的 python,寫進〈誠實界線〉(改動前拿 PATH 上的 python3 也一樣)。
  - 架構對齊 F1、外家 F4:目錄照合併程式實際寫出的形狀,兩家分開精確比對;測試 ⑩ 拿合併程式真的寫出的 Claude 與 Codex 設定來餵,⑧ 加別人家目錄底下的 .claude/hooks。
  - 架構對齊 F2:內層改名 hook_dir。
  - 單 reviewer F1、外家 F3:非零退出時看 uv 的錯誤訊息,`No interpreter found` 才算找不到,其他記執行失敗並帶最後一行;測試 ⑤e。
  - 單 reviewer F2:四支安裝腳本在 `_LUMOS_ANY_NOTE` 有值時先印到 stderr。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):位置改回整條解析 → ⑤f 紅;uv 非零一律說找不到 → ⑤e 紅;Codex 目錄判斷拿掉 → ⑩ 紅;改回後綴比對 → ⑧ 紅;不驗 python-path 回的路徑 → ①b 紅。
- refuted 無;accepted 無。
