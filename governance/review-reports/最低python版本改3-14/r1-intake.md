preflight-4: ran

# r1 收貨紀錄(最低python版本改3-14)

## 前置掃描(首輪,派一席 Sonnet 5.5 唯讀掃四類)

- 結果:①存在類 1、②0、③語意類 3、④語意類 8(另存在類 1 與①同一件)。沒有一條動到「核心裁定」(Enzo 2026-09-29 的四項:找不到擋下、自動找並重跑、安裝器不替人裝、只清擋路的),全部由編排者直接修進計劃;下面逐條列修改前→後,席位可覆核推翻。
- 修改前的整份計劃另存在編排者暫存區(plan314-before-preflight.md),〈做法〉〈條款〉兩節前後差異 32 行。

| 前掃項 | 類 | 修改前原句(摘) | 修改後(摘) |
|---|---|---|---|
| ①/④-3 共用檔沒登記工具自裝檔名單 | 存在 | 「shell 那份放在 `scripts/hooks/` 底下一支新的共用檔(git 掛鉤會跟著被複製進消費專案,安裝腳本也 source 它)」 | 「新共用檔要登記進工具自裝檔的精確名單(跟 `t_vendored_file_list_matches_what_install_ships` 一起改)」 |
| ③-1 五支安裝腳本 vs 兩處實作(get.ps1 是 PowerShell) | 語意 | 「五支安裝腳本改用共用清單;找不到就報錯並附安裝指令」 | 「安裝入口不各自找直譯器……找 3.14 與找不到時的說明全交給第 2 點(lumos 開頭)……PowerShell 也不用再寫一份」;[S4] 改成「連任何 python 都找不到」才由安裝入口報錯 |
| ③-2 Windows `.cmd` 包裝與精簡版測試的交界 | 語意 | 「Windows 另加 `py -3.14`。」(沒說寫進哪裡) | 「`py -3.14` 是 lumos 開頭那份的 Windows 候選;`lumos.cmd` 包裝照舊寫指令名不寫死路徑,版本交給 lumos 開頭,所以跟精簡版共用的包裝候選順序不動」 |
| ③-3 「只回退擋下」會不會退回 3.9 | 語意 | 「把 git 掛鉤找不到 3.14 時改成印提醒並放行(第 3 點),其餘保留」 | 「放行是整道檢查不跑,★不是改用 3.9 跑★」 |
| ④-1 post-commit 現況寫錯 | 語意 | 「`post-commit` 擋不了提交,找不到時印一行提醒就結束。」(當成現況的延伸) | 「現況找不到 python 時會執行空字串指令出錯,改成 source 共用檔、找不到就印一行提醒後正常結束」;第 3 點補寫兩支掛鉤的現況(沒 python 放行、有 3.9 就拿 3.9 跑) |
| ④-2 merge-claude-settings 不只 lumos 一個入口 | 語意 | 「它由 lumos 啟動,經過第 2 點一定是 ≥3.14」 | 「它自己開頭也加同一個版本檢查(低於 3.14 就報錯回 2、不寫設定),因為使用者也可能直接用 `python3` 手動跑它」;[S5] 同步 |
| ④-4 get.sh 舊安裝複本沒有新共用檔 | 語意 | 「安裝腳本也 source 它」 | 安裝入口一律不 source 共用檔(同 ③-1 的修法) |
| ④-6 既有測試只盯兩支掛鉤 | 語意 | 「`t_hooks_python_fallback` 這類斷言『掛鉤寫 `command -v python3`』的測試改成斷言走共用清單」 | 「(現在只盯 post-commit 與 pre-push……)改成斷言三支掛鉤都 source 共用檔」 |
| ④-7 CI 其他兩道會在 3.14 重跑 | 語意(補充) | (沒提) | 第 6 點加「編譯全部檔」與「SyntaxWarning 歸零」兩道在 3.14 重跑、新警告一起清 |
| ④-8 頂層版本檢查被 import 時誤觸 | 語意 | 「檔案最前面(任何 3.10 以上才有的寫法之前)檢查版本……`os.execv` 用它重跑同一組參數」 | 「版本檢查放在 `if __name__ == "__main__":` 那段、進 `main()` 之前(被測試用 import 載入時不觸發)……重跑 `__file__` 加原本的參數」;[S2] 加「被 import 載入時不應觸發」 |
| ④-9 Windows 的 execv 拿不到回傳碼 | 語意 | (沒提) | 「Windows 的 execv 不會真的取代行程……改成子行程跑完再用它的回傳碼結束」;[S2] 加「回傳它的回傳碼」 |
| ④-10 沒有守「scripts/lumos 仍可被 3.9 解析」 | 語意 | 〈誠實界線〉只用 REVISIT 承認 | 新增 [S7] `t_lumos_parses_under_old_grammar`;〈誠實界線〉改寫成「[S7] 守語法、守不到載入時呼叫新版標準庫」 |
| ④-12 CHANGELOG 自己規定只記發版 | 語意 | 「CHANGELOG 記一條給消費專案看的升級說明」 | 「不寫 CHANGELOG……升級注意寫在 README,由下次發版的人帶進去」;README.en 另一處 3.9+ 一併列入 |

- 屬實、不用改的:④-5 `_toml_loads` 代解分支、④-7 CI 與 lint 現值、④-11 F65 的出處。前掃另外實測:系統 python3.9 目前還解析得了 scripts/lumos(沒有 3.10 以上語法)。

## 席位收貨

- 凍結材料:r1-snapshot.md(81 行,sha256 8ebb7774…),工作副本放編排者暫存區;7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet(Sonnet 5.5);外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。
- 7 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的動作,席位沒動 repo。
- report-normalize 7 份;quote-check 6 份全錨定,架構對齊席 1 句「lands_in」不到 10 字、不採信(那條 F3 的判斷改用它的敘述與開頭欄位核對);refcheck 兩處「不存在」是正規表示式(`scripts/hooks/(pre-commit|pre-push|post-commit)`)與指令加參數(`scripts/lumos --version`),不是路徑,不影響。
- 發現 51 條(正確性 13、邊界 9、接手 9、外家 7、併發 5、回滾 5、架構對齊 3;機器數各報告「## F<數字>」標題與獨立的 severity 行,扣掉檔首那一行),major 33(正確性 9、外家 6、接手 6、邊界 5、併發 3、回滾 3、架構對齊 1)。更正:最初手數成 52 條/major 28,是把架構對齊報告的「## Findings」段落標題當成一條、major 目測少算。多席獨立報到的同一件:錨點清單(接手、正確性、外家)、防重跑變數繼承(併發、正確性、邊界、接手)、路徑很短的環境(邊界、正確性、接手)、安裝入口只試 python3(邊界、正確性、外家、接手)、註冊路徑沒引號(邊界、外家、正確性)、CHANGELOG 矛盾(正確性、外家、接手)。
- 有 major,accepted 為空,全折。

## 機械重現(編排者在 clone-314 與本機跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1(檢查在檔尾,載入期就炸) | `/usr/bin/python3 -c "def f(x: int \| None): pass"` | HIT:`TypeError: unsupported operand type(s) for \|` |
| 正確性 F2 / 接手 F2(feature_version 放過 PEP 701) | 3.14 上 `ast.parse('f"{d["a"]}"', feature_version=(3,9))`;同一行給 3.9 compile;ruff E9 py39 / py314 | HIT:ACCEPTED;3.9「f-string: unmatched '['」;ruff py39 報 1 條、py314 全過 |
| 接手 F3(ruff py314 多出的告警) | 同一組規則對 scripts/lumos 與 test_lumos.py 比 py39 與 py314 | HIT:B905 +10、RUF007 +1 |
| 邊界 F1 / 正確性 F7 / 接手 F5(路徑很短) | `env -i PATH=/usr/bin:/bin bash -c 'command -v python3.14; python3 -c …'` | HIT:沒有 python3.14、python3 是 3.9;而 /opt/homebrew/bin/python3.14 存在 |
| 外家 F5(uv 會觸發下載) | `uv python find --help` | HIT:有 `--no-python-downloads` 與 `--system`,計劃沒用 |
| 邊界 F4 / 外家 F4 / 正確性 F11 第 3 點(註冊沒引號) | 讀 scripts/merge-claude-settings.py 的 _hook_cmd | HIT:POSIX 與 Codex 非 Windows 分支 `{_PY}` 沒引號,只有 Windows 分支有 |
| 其餘 | 讀碼核對各席引的 file:line(refcheck 全在) | 採信;席位附的實測(正確性 F11 的 uv .venv、併發 F2 的毫秒數、回滾 F4 的 _equivalent)沒有逐條重跑 |
