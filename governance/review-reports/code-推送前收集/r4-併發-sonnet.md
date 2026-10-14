severity: minor

併發與資源席第四輪報告。主要發現:修補把「槓桿」放對了(各片自成群組、整組送 TERM),但只送一次,留下一類修補沒蓋到的殘留。實驗目錄已刪(只刪了自己建的 `cr-ppc4-併發`),收尾 `ps` 看無孤兒(沒有 ppid=1 的 sleep / 測試殘片)。

**finding 1**

severity: minor
blocking: 否 — 單人單機、只在送訊號撞上片剛開始起子行程的幾十毫秒內才發生,殘留是會睡到被收的閒置子行程,不會污染結果或讓推送誤放行。
引句:「for _p in $_j; do kill -TERM -- "-$_p" 2>/dev/null || kill -TERM "$_p" 2>/dev/null; done」

問題:`_pp_kill_jobs` 對群組只送「一次」TERM。作者說剩下 1 次殘留的成因是「片在 setpgid 之前收到訊號的空窗」,我實測不是這個:那個空窗是安全的(此時片還只是 Python 本人,沒起任何孫行程,退回只殺本人就夠)。真正的殘留來自「送訊號當下群組成員正好在 fork 子行程」:訊號是逐一投遞給群組現有成員,正在 fork 的父行程被殺的同時,剛生出來的孩子已繼承群組卻沒收到這一發。這個孩子之後沒人再送,變成 ppid=1 的孤兒,群組本身還在(組號不會被重用)。

具體失敗情境(/bin/bash 3.2.57、macOS,我自己重現,孫行程為 `sleep 7777`):
- 穩態:片是個每 3 毫秒就起一個背景子行程的迴圈,150 毫秒後對群組送一次 TERM,60 次中 4 次留下孤兒;同樣流程、片的領頭行程結束後再補送一次整組 TERM,60 次 0 次殘留。
- 啟動:片是起來就立刻起兩個孫行程的 bash 腳本,用完整掛鉤模擬(主殼、兩個子殼、各 4 片),掛鉤啟動後 20–45 毫秒送 TERM 100 次中 27 次殘留;4–12 毫秒送 100 次 0 次殘留(那段還在 Python 啟動、沒有孫行程)。所以作者實測的 4–12 毫秒視窗(1600 次殘留 1 次)剛好落在「最安全」的一段,沒量到容易漏的那一段。真正的測試程式起子行程比我的最小腳本晚,實際機率較低,但機制在全套測試跑的八分鐘內一直存在(測試持續起 git 等子行程)。
- 補一次就消失:在每一片 `wait` 回來之後再對 `-$_p` 送一次 TERM(群組還有成員時組號仍有效,沒有成員會 ESRCH/EPERM,要吞掉),上述兩種情境都降到 0/40~0/60。注意補掃要放在訊號路徑的陷阱裡(`_pp_kill_jobs` 內短等一下再送第二發),因為被 TERM 時子殼是 `exit 143` 直接離開,不會走到 `wait` 之後。

佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:304`(`_pp_kill_jobs`)

**finding 2**

severity: minor
blocking: 否 — 掛鉤本來就為單人 macOS 環境維護,Windows 路徑是否真的走到全套測試這一支沒有證據;屬可移植性退步。
引句:「_PP_OWN_PGRP='import os, sys; os.setpgid(0, 0); os.execv(sys.argv[1], sys.argv[1:])'」

問題:啟動器沒有退路。`os.setpgid` 在 Windows 的 Python 不存在,會 AttributeError 離開碼 1,每一片都被判紅、整支推送被擋;而掛鉤的 `$PY` 找法明確收 `C:\...` 絕對路徑(`_lumos_py314` 的 case),表示 Windows(Git Bash)被當成支援平台。此外 `setpgid` 只要因任何原因失敗(例如不允許換群組的環境)也會整片紅,而不是退回「不換群組直接跑」。建議包 `hasattr`/try,失敗就照舊直接 exec,代價只是退回舊的收片行為。(我沒有 Windows 環境,以上由 API 可用性推出,沒有實跑。)

佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:818`(定義處,約在 `run_group` 之前)

**已讀,無 finding**
- 對整組送訊號會不會打到不該打的行程:子殼 S 不是群組組長,`kill -- -S` 會 ESRCH,走 fallback 只殺 S;S 活著時沒有別的群組能用同一組號;片的群組只含自己與其後代,不含掛鉤、主殼與 S。已結束且未收的工作其 pid 重用需要整個 pid 空間繞一圈,威脅模型下略。
- 片在 setpgid 前收到訊號:Python 啟動中無孫行程,fallback 只殺本人即可,實測 4–12 毫秒送 TERM 150 次 0 殘留,送 HUP 150 次 0 殘留(用「片是 Python、起兩個 sleep」的模擬,掛鉤與子殼結構照抄)。作者的 TERM/HUP 低殘留數字方向可重現,完整 1600/800 次沒有重跑(時間上限),pty Ctrl-C 沒有重現。
- 終端機掛斷時各片不再直接收到 SIGHUP(因為已離開前景群組),全靠掛鉤的 HUP 陷阱;`wait` 會被陷阱打斷,所以這條路徑成立,未發現缺口。

最高等級 minor,blocking 0 條。
