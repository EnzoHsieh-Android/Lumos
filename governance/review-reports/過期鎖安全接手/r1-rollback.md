severity: blocker

# 回退席

## k1：舊版與新版共存仍可雙持

severity: blocker
blocking: 是
引句:「當兩個不同 PID 在舊鎖與新鎖交錯時，`_excl_lock_try` 應至多讓一人取得主鎖」
file: `scripts/lumos:33861`
file: `scripts/lumos:33868`
新版持有鎖且工作超過舊版門檻時，舊版仍會按 mtime 搬走它；新舊程序同時自認持鎖。審查席以 901 秒舊鎖實測舊版 `old_version_acquired=True`。需界定混版窗口與進場條件，不可把 S1 擴稱跨版本保證。

## k2：鎖內沒有背景 PID，人工復原無法只靠它核對

severity: major
blocking: 是
引句:「遇到殘留鎖，先從錯誤訊息提供的位置核對使用該筆記庫的程序與派工鏡頭背景工作是否仍在執行」
file: `scripts/lumos:33904`
file: `scripts/lumos:33907`
鎖記短命派工者 PID，未保存 Popen 背景 PID。派工者退出後背景仍活時，操作者若只看鎖內 PID 就誤刪，下一次再派第二支。需具體可執行的查核方式或保留無法判定的鎖。

## k3：回退會恢復已確認的雙持

severity: major
blocking: 是
引句:「回退程式不得把治理帳新寫者接上舊自動接手邏輯；S1 會重新翻紅時須停止推送」
file: `scripts/lumos:33861`
file: `scripts/test_lumos.py:54432`
上線後直接 revert 新鎖原語會帶回舊 ABA；文內沒有可恢復服務的安全回退。需明列 roll-forward 或停用入口的做法、跨版本進場條件。

PRIOR-ART、RETIRE-IF、實務隱患其餘已讀，無 finding。

總結：最嚴重 severity: blocker；blocking 3 條。
