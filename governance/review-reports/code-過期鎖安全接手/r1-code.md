severity: major

## C1：建鎖錯誤被事件帳記成成功

severity: major  
blocking: yes  
file: `scripts/hooks/claude/dispatch-lens-hook.py:363`  
引句:「if lock_status.get("lock_error") is True:」

此分支把錯誤說明注入派工詞後直接 `return 0`，卻沒有像逾時分支一樣呼叫 `_hookevent.mark(...)`。外層 `guard()` 因此會把每次建鎖失敗記成 `ok`，違反事件帳「內部吞掉的失敗不得算成功」的契約。若權限或路徑問題持續存在，`lumos enforcement` 仍會看到近期成功事件，形成守衛假綠。

最小重現已執行：以 mock 令 lumos 回 `rc=2` 與 `{"lock_error":true,"lock_path":"/tmp/x"}`，再用 mock `record()` 捕捉 `guard()` 寫入種類，得到：

```text
rc 0 event_kind ok
```

應在此分支回傳前記 `_mark("error", "lumos dispatch-lens 鎖無法建立...")`，並讓 hook 測試同時斷言事件種類為 `error`。

## C2：失敗清理把原本的 ABA 移到 lstat 與 unlink 之間

severity: major  
blocking: yes  
file: `scripts/lumos:33876`  
引句:「if (now.st_dev, now.st_ino) == identity:」

`lock.lstat()` 與下一行 `lock.unlink()` 不是同一個原子操作。若檔名在兩者之間被另一持有者換入，檢查仍拿到舊 inode，隨後卻會按路徑刪掉新持有者的鎖。這正是本案要消除的「先看身份，再按路徑操作」競態，只是從過期接手移到了寫入失敗的清理路徑；現有測試只在 `lstat` 前完成替換，未覆蓋這個窗口。

最小重現已執行：以無磁碟 fake lock 令 `lstat()` 先回本次 inode、回傳前把目前路徑切成 `other`，`unlink()` 記錄實際刪除對象；對 `os.write` 注入 `ENOSPC`，結果為：

```text
deleted= other
```

此形狀無法靠「再 stat 一次」關閉競態。安全修法需避免在失敗後按共享路徑清理，例如先完整寫好唯一暫存檔，再用具排他性的建立步驟發布；若維持現形，寧可留下可診斷的自身半成品，也不能刪除可能已換入的他人鎖。

## C3：S1 的跨程序測試只擋雙持，沒有驗兩方都拒絕接手

severity: minor  
blocking: no  
file: `scripts/test_lumos.py:54435`  
引句:「not (parent_acquired is True and result.get("acquired") is True)」

S1 寫的是兩個新版程序都應拒絕既有過期鎖並保留原鎖，但斷言只禁止 `True/True`。若某次修改讓其中一方取得、另一方失敗，這支測試仍會綠。S2 的單程序案例提供部分補網，因此列 minor。建議直接斷言父子結果皆為 `False`，並核對舊鎖內容與身份未變。

S1–S6 其餘核對：S1/S2 的主實作已停止 mtime/PID 接手；S3 有短寫迴圈與錯誤分流，但受 C2 阻擋；S4 的 60 秒上限、鎖位置與立即建鎖錯誤成立；S5 的 `lock_uncertain`、`lock_error`、hook JSON 接收與正常暖快取路徑成立，但 C1 使事件帳失真；S6 已誠實限定同版安全並把混版切換列成人工進場條件。

固定席圖譜：`canary-record未落盤事件`、`code-loop守衛main-direct盲區`、`deinit整夾刪使用者檔`、`hook卸載殘留註冊`、`init-force-slug誤用basename`、`vendored測試套件在消費端假紅`、`測試未隔離HOME刪掉真機Claude-hooks`、`known-pitfall-refresh-token`、`lumos-cli-lifecycle`、`lumos-cli-read` 已讀，未見本 patch 破壞；HOME 修改有 `finally` 復原。`bound-tests-gate` 的 S1 證據有 C3 的弱斷言；`design-loop` 的設計卷證與凍結判定存在；`測試假綠形態` 命中 C3。三篇落點 Systems 與 Issue 對「不自動接手、舊版不互通、人工復原」的說法一致；Verification 維持 `pending`，沒有把 S6 寫成已部署核可。

`py-eventloop` 表態 `na` 成立：新增的 `json.loads` 位於同步 hook，執行在同步 `subprocess.run` 返回後，沒有 asyncio/event-loop 路徑；未發現可反駁證據。

最重等級 major；blocking 2
