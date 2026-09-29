severity: major

# 正確性鏡頭:scripts/lumos 與 scripts/test_lumos.py(最低 Python 改 3.14,r1)

凍結 patch 跟 clone-314 的 HEAD(605b0a65)對 4990a90a 的 diff 逐字相同,已先核對。

## F1 doctor 的 Q 段和 enforcement 把「命令裡有 hooks/」的每一條掛鉤都當成 Python 直譯器:不但誤報,還會用 `-c <探針>` 實際執行使用者自己的掛鉤腳本
severity: major
blocking: 是 — 維護者自己機器上的真實設定就會永遠誤報,而且每次 Claude 開場都會執行非 lumos 的掛鉤腳本
引句:「exes.add(_shlex.split(cmd)[0])」
file: `scripts/lumos:19901`
file: `scripts/hooks/claude/lumos-entry-hook.py:256`

1. `_hook_python_problems` 過濾掛鉤只看一個條件:命令字串裡有沒有 `hooks/`。有就拿 `shlex.split(cmd)[0]` 當直譯器,交給 `_py_probe` 執行 `<那個東西> -c <版本探針>`。第三方掛鉤很常見的形狀都會被收進來,例如 `if [ -f ~/.orca/agent-hooks/… ]; then …`、`bash "$HOME/.claude/hooks/x.sh"`,或是直接寫絕對路徑的 `/…/.claude/hooks/notify.sh`。
2. 在這台機器的真實設定上重現(唯讀):`/opt/homebrew/bin/python3 scripts/lumos enforcement --json` 的 python 那列輸出 `…claude 掛鉤 if(沒有這個指令);codex 掛鉤 if(沒有這個指令);重跑 lumos install 修正`。第一個字 `if` 來自 Orca 的掛鉤,可是重跑 lumos install 根本修不掉它,所以 doctor 的 Q 段在這台機器上會永遠亮著。
3. 用臨時 HOME 重現誤報:settings.json 放三條命令,一條是 lumos 的 `/opt/homebrew/bin/python3 "${HOME}/.claude/hooks/lumos-entry-hook.py"`,一條是 `if [ -f "$HOME/.orca/agent-hooks/claude-hook.sh" ]; then …`,一條是 `bash "$HOME/.claude/hooks/notify.sh"`。`HOME=$T lumos doctor` 印出:
   `[Q] … • claude 的掛鉤註冊的是 bash:執行失敗(回傳碼 2,可能是 Windows 商店替身)` / `• claude 的掛鉤註冊的是 if:沒有這個指令`。在 macOS 上,訊息還會說是「Windows 商店替身」。
4. 用臨時 HOME 重現副作用:建 `$T/.claude/hooks/notify.sh`,內容是 `echo "RAN $1" >> $T/side-effect.log`,再在 Stop 事件註冊它的絕對路徑。跑 `HOME=$T lumos enforcement --json`(或 `lumos doctor`)之後,`side-effect.log` 多一行 `RAN -c`,表示使用者的掛鉤腳本被實際執行了。`lumos enforcement --json` 由 lumos-entry-hook 在每次 Claude SessionStart 呼叫(見上面的 file 行),所以每開一個 session 都會用怪參數執行一次使用者的掛鉤腳本。
5. 做法第 9 點要查的只有「lumos 自己註冊的那幾支」。可以判定的特徵現成就有:merge-claude-settings.py 寫的命令形狀固定是「`<直譯器> "<…>/hooks/<已知的 .py 檔名>"`」。只認第二個 token 指到 `hooks/<lumos 自家的檔名>.py` 的命令,就能排除第三方掛鉤。現行測試 t_doctor_flags_stale_hook_python 的 fixture 只放了 lumos 形狀的命令,碰不到這種情況。

## F2 升級注意在標準的 `lumos update` 流程裡永遠不會印出來:跑 update 的是 pull 之前就載進記憶體的舊程式
severity: major
blocking: 是 — [S9] 在主要路徑上不成立,而計劃說消費專案的 CI 回 2 只能靠這段注意來提醒;測試是「現場走不到被測分支」型的假綠
引句:「if _py314_upgrade and "scripts/hooks/pre-commit" in healed:」
file: `scripts/lumos:17657`
file: `scripts/test_lumos.py:51609`

1. 全域 `lumos` 是指向來源 clone 裡 `scripts/lumos` 的符號連結。`cmd_update` → `_vendor_toolchain` 會先在同一個行程裡 `git pull` 來源,再複製檔案。來源 clone 還停在舊版時,執行 update 的是 pull 之前的舊程式,裡面沒有這段判斷。舊程式會把新的 pre-commit 複製過去,但不印注意。到了下一次 update,pre-commit 裡已經有 `python-path`,條件不成立,一樣不印。所以單一專案的使用者永遠看不到;多專案的使用者,第一個 update 的專案看不到。計劃〈做法〉第 1 點「★為什麼不讓 shell 自己找 3.14★ ①舊版的更新程式在啟動時已把…讀進記憶體」講的就是這個機制,這裡又踩了一次。
2. 重現(全部在 mktemp 的臨時目錄裡做,HOME 和 CODEX_HOME 都指向臨時目錄):
   `git clone -q <clone-314> $T/src && git -C $T/src reset -q --hard 4990a90a`;在 `$T/proj` 執行 `git init`、建 `docs/proj-knowledge/Systems`,再放進 4990a90a 的 `scripts/hooks/pre-commit`(`grep -c python-path` 得 0)。
   `cd $T/proj && HOME=$T/home CODEX_HOME=$T/home/.codex LUMOS_HOME=$T/src python3.14 $T/src/scripts/lumos update | grep '升級注意\|結尾自癒'`
   第一次:來源被 pull 到 605b0a65,自癒清單裡有 `scripts/hooks/pre-commit`,沒有「升級注意」。第二次:`✓ 結尾自癒檢查:工具組完全對齊`,仍然沒有「升級注意」。
3. t_update_prints_python314_notice_and_slim_strips_floor 用 `_load_lumos_mod` 載入新版,直接呼叫 `mod._vendor_toolchain(src, root, …, no_pull=True)`,等於把「執行 update 的已經是新程式」當成前提,所以真實路徑上這一格一定是綠的。專案合約〈測試假綠形態〉要求翻紅釘要附「現場成立」的前置斷言,這條沒有做到。這個提示得從新程式自己一定會跑到的地方觸發。例如新 lumos 在專案裡第一次執行時,發現沒有留過「看過升級注意」的標記就印;或 update 在 pull 之後重新 exec 一次自己。

## F3 t_doctor_flags_stale_hook_python 的 ③ 永遠不會翻紅:doctor 不加 --strict 時,不論有幾個 issue 都回 0
severity: minor
blocking: 否 — 現在的行為是對的,只是它宣稱的翻紅釘不生效;Q 段不在 --ci 路徑上,退化後的實際影響只有 --strict 的回傳碼和「N issues」那行
引句:「check("③軟提醒不計 issues(回傳碼跟沒問題時一樣)", r_bad.returncode == r_fine.returncode,」
file: `scripts/lumos:3110`

1. run_doctor 的結尾是 `return 1 if strict else 0`,測試卻跑不帶 --strict 的 `doctor`,所以兩邊恆為 0。
2. 翻紅實驗:在臨時 clone 裡把 Q 段的 `warn_soft(_hp, …` 改成 `warn(_hp, …`(計進 issues),清掉 __pycache__,再跑 `python3.14 scripts/test_lumos.py -k t_doctor_flags_stale_hook_python`,結果是 `6 passed, 0 failed`。另外直接量:壞設定的那一邊印 `⚠ 發現 1 個 issue`、rc=0;好設定的那一邊是 `✓ 圖譜健康 — 0 issues`、rc=0。
3. docstring 寫的「計進 issues → ③紅」不成立。要改成比對 stdout 收尾行的 issue 數,或改跑 `doctor --strict`。

## F4 版本檢查段開頭的註解說精簡版「剝掉這一段」,跟結尾的註解與生成器的實際行為矛盾
severity: minor
blocking: 否 — 只是註解寫錯,不影響執行;但下一個照註解改生成器的人會把整段剝掉
引句:「精簡版生成器會剝掉這一段——見 Systems/python直譯器選擇」
file: `scripts/slim-gen.py:302`

1. 同一段的內層註解寫「精簡版生成器只剝這三行…上面的函式留著無害」。slim-gen.py 的 `_FLOOR_GATE_BEGIN` 找的也只是 `python-floor gate begin`,計劃〈實作時的決定〉同樣寫「只剝呼叫版本檢查那三行」。外層 `python-floor begin` 那行的說法是舊的。

## F5 找不到 3.14 時的說明:「沒有任何一個存在」這個分支永遠走不到,而且沒裝 uv 也會被列成「找過的候選」
severity: minor
blocking: 否 — 只影響說明文字,但它跟同一支函式「不存在的候選不列」的規則互相矛盾
引句:「lines.append("找過的候選:" + ("" if tried else "沒有任何一個存在"))」
file: `scripts/lumos:179`

1. `_py_resolve` 會把「不存在」「沒有這個指令」的候選濾掉不列,但 uv 那格不論 uv 在不在,都一律 `tried.append((desc, "沒有 uv,或 uv 找不到 3.14"))`。所以只要沒設 LUMOS_PYTHON,`tried` 一定非空,`沒有任何一個存在` 永遠印不出來。
2. 重現:`env -i HOME=/tmp/nohome PATH=/usr/bin:/bin LUMOS_PYTHON_SEARCH_DIRS=/nonexist /usr/bin/python3 scripts/lumos --version` 印出 `找過的候選:` / `  uv python find:沒有 uv,或 uv 找不到 3.14` / `  python3:版本 3.9.6,低於 3.14`。PATH 上沒有 uv,它卻被列成「找過」。

## 已看,無 finding 的部分
- 3.9 能不能讀進來、重跑或報錯:在 `/usr/bin/python3`(3.9.6)上實跑。`python-path` 會找到並 exec `/opt/homebrew/opt/python@3.14/bin/python3.14`,rc 0,耗時 0.7 秒。PATH 被縮短、找不到 3.14 時印完整說明、rc 2,沒有追蹤訊息。拿 3.9 的 runpy 以非主程式身分載入時不會觸發檢查(測試 ⑤ 綠)。ruff 檢查 F821/F811,結果跟改動前一樣,沒有新的未定義名稱。
- 候選順序、找到就停、單一 5 秒與總共 15 秒的逾時、uv 的 `--system --no-python-downloads`(本機 uv 0.11.19 實跑合法)、LUMOS_PYTHON 只收絕對路徑而且合格、LUMOS_REEXEC_PYTHON 防重跑的比法、版本夠時不因 LUMOS_PYTHON 重跑、Windows 用子行程取回傳碼:已看,無 finding。
- `python-path` 的回傳碼:在沒有圖譜的 /tmp 下跑回 0;LUMOS_PYTHON 指到 3.9 時回 2 並印說明;3.9 加上合格的 LUMOS_PYTHON 會重跑之後回 0。已看,無 finding。
- `_run_cmd_expand`:三個代入點都改了,拿掉 `import shlex` 之後函式裡沒有殘留的引用。路徑含空白時加引號可以執行(測試 ② 綠)。已看,無 finding。
- `_pick_windows_launcher`、doctor 三處 CI 提示接上 `_CI_PY314_NOTE`、enforcement 的狀態維持 active、HELP_WHEN 與子指令註冊:已看,無 finding(enforcement 讀到的內容問題併在 F1)。
- 新增的 10 支測試都在本機用 3.14 跑綠。除了 F2 和 F3,其他宣稱的翻紅釘對照程式路徑看過,走得到被測分支。

最嚴重等級 major,需要擋下的共 2 條(F1、F2),另有 3 條不擋的 minor。
