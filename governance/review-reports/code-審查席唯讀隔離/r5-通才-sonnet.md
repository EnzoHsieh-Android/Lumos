severity: minor

# 第 5 輪通才審(只審 r4 修正差異)

驗證:臨時複本 /tmp/lumos-seat-work/code-審查席唯讀隔離/r5w/c(git clone --shared,HEAD 01dd1f2f)。`claude plugin test mods/claude/lumos-guard` 90 支全綠;`python3.14 scripts/test_lumos.py -k guard_plugin_files` 25 支全綠。repo 根沒動。

### F1 存回每格都有上限,但派工改成等整條佇列,卡住時第 k 個派工等 k 倍上限
severity: minor
blocking: 否 — 只在 `$.state` 存回整個卡住時發生,派工最終仍會回來,不影響守衛判斷
引擎卡住時才會碰到;計劃 S7 寫的「存回卡住時派工照常回傳」在多席同時派時只剩「最終回傳」。
引句:「saving = saving.then(() => Promise.race([job(), io.sleep(SAVE_MS)]))」
引句:「          await save()」
位置:`mods/claude/lumos-guard/hooks/register.ts` 的 `save` 與 `onSpawn`(`await save()`)。
成因:r3 時派工自己 `Promise.race([save(), sleep])`,上限固定一格;r4 把上限搬進佇列每一格,派工改成直接 `await save()`,等的是整條串。每個卡住的存回各占一格 SAVE_MS(2 秒),後面的派工要排在它們後面。
重現(臨時複本 `hooks/r5.test.ts`,綠=行為如下):saveSeats 永不回傳、sleep(SAVE_MS) 手動放行,同時派 3 席:第 1 席要等第 1 格放行才回,第 2 席要等第 2 格,第 3 席要等第 3 格(三席各自回傳的時間依序差一格)。同時派 8 席最後一席約等 16 秒。
連帶:`release` 在 `finally`,所以「啟動中」計數也跟著撐 k 格,期間非審查席子代理的工具呼叫各自最多多等 5 秒(已有上限)。
建議:派工那頭保留自己的上限(`Promise.race([save(), sleep(SAVE_MS)])`),佇列的每格上限留給 `end` 與後續存回;或讓卡住的格在逾時後不再占佇列。補一支多席同時卡住的測試(現有 r4 測試只測會談結束)。

### 逐 hunk 判過、不成立的項目(不標)
- `end(keep)` 提前回傳:`/clear`、`resume` 不遞增 endGen、不清 pending,派工途中的席回來照常登記;`reason` 型別檔 ExitReason 含 'clear'|'resume',接線一致。
- `release(session, p)`:`pending.get(session) === p` 才刪,舊派工不扣新計數;測試覆蓋。
- `version ?? 0`:型別檔寫「沒寫過的值是 undefined、版本 0」,帶條件寫 0 合理;`makeIo` 版本非數字才會走到,代價是撞版三次後跳提示,屬設計取捨。
- `SEAT_LOOSE_RE` 兩支:連字號寫法不論冒號都算、底線空白要冒號;`clean` 的 NFKC 已把全形冒號轉半形,`LUMOS SEAT：` 能判 bad。`lumos−seat`(U+2212)這類 NFKC 不轉成連字號的寫法仍判 none,是 r3 前就有的覆蓋範圍,不是這輪引入。
- Glob:`pat.split(/[/,{}]/).includes('..')` 與巢狀大括號檢查跟舊的逐組檢查不衝突;絕對路徑選項仍掃非巢狀組。
- Python 端釘接線:去註解後用 `count == 1` 比,`find` 找不到時 `live[-1:]` 只會讓檢查變紅,不會變綠;實跑綠。
- 筆記:計劃做法節第 23 行「會談結束清掉對應與啟動中清單」沒寫 clear/resume 例外,但回退節、誠實界線與 lumos-guard 筆記已寫明,不影響行為判斷。

### 圖譜鏡頭
圖譜沒有釘到節點,備援段(受影響測試、共改、呼叫者皆 0)不逐條答。表態記錄 `py-eventloop na` 與本輪差異無關(差異沒有碰探針腳本)。

總結:最嚴重 minor,blocking 0 條
