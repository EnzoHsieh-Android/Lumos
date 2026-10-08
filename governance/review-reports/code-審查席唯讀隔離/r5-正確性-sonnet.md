severity: minor

### F1 派工改成直接等 save(),卡住時 k 個並行派工最後一個等 k×SAVE_MS
severity: minor
blocking: 否 — 只拖慢派工回傳,不影響守衛判斷(席在記憶體裡先登記完了),且要 $.state 存回真的卡住才發生
引句:「saving = saving.then(() => Promise.race([job(), io.sleep(SAVE_MS)]))」
引句:「          await save()」
位置:`mods/claude/lumos-guard/hooks/register.ts` save() 與 spawn 內 `await save()`(原本是 `Promise.race([save(), io.sleep(SAVE_MS)])`)。
走法:存回永遠不回(`saveSeats` 不 resolve),同一會談並行派 3 席。每次 save 都接在前一格後面,每格各等 SAVE_MS;第 k 個 spawn 的 `await save()` 要等前面 k-1 格逾時加自己這格。
重現(臨時複本 /tmp/r5w/g,未改 repo):`sleep` 在 SAVE_MS 時 200ms 後 resolve、`saveSeats` 永不 resolve,並行 spawn 3 席,三個派工回傳耗時 [202, 403, 605] ms,即線性成長;真值 SAVE_MS=2000 下是 2/4/6 秒。設計審常一次並行派 7、8 席,最後一席約 14~16 秒才回傳。
副作用:`release(session, p)` 在 finally,要等 `await save()` 做完,啟動中計數也跟著撐久,同會談非審查席子代理的工具呼叫會多等並可能撞 WAIT_MS 逾時。
這跟計劃 S7「存回卡住時派工照常回傳」的字面不完全相符(單席成立,多席不成立)。測試「存回卡住時會談結束照樣回來」只派一席,守不到。
建議方向:派工那頭仍用自己的上限(或讓排隊總等待有上限),不要讓每格各自累加。

### F2 Glob 的 `..` 檢查擋不到由大括號選項拼出來的 `..`
severity: minor
blocking: 否 — 沒有證據顯示 Glob 實作會展開成跨上層的遍歷,且最多只到席位 cwd 的上一層
引句:「if (pat.split(/[/,{}]/).includes('..') || /\{[^{}]*\{/.test(pat)) return null」
位置:`register.ts` searchBase 的 Glob 段。
走法:pattern 為 `.{.,x}/y`(單層大括號、選項各是 `.` 與 `x`):以 `[/,{}]` 切完是 `.`、`.`、`x`、``,沒有任何一段等於 `..`;大括號沒巢狀、選項不以 `/` 開頭;固定段迴圈第一段含 `{` 就 break。於是 `searchBase` 回席位 cwd 加上 path 的結果,放行。若 Glob 引擎真的先展開大括號,展開後就有 `../y`。
重現:臨時複本加 `chk({ tool: 'Glob', pattern: '.{.,x}/y' })`,結果 `null`(放行)。展開後引擎會不會真的走上層我沒實測(未能重現實際讀取),所以只列 minor。
類別:跟 r4 修的「`..` 在萬用字元前後」同族,r4 這次改成逐段比字串,仍沒處理「段由大括號拼出」。

### 圖譜鏡頭
- 固定席筆記沒有附在材料尾端,只有「圖譜沒有釘到節點」備援段(受影響測試、共改、呼叫者皆 0),無逐條可判。
- 計劃與 Systems/lumos-guard 的文字跟 diff 行為對得上(/clear 與 resume 不算結束、release 用自己那份、版本 0、撞版提示、SEAT_LOOSE_RE 底線要接冒號)。唯一差異是 F1:計劃寫「存回每一格都有時間上限、卡住不拖住派工」,多席並行時累加沒有被這句涵蓋。
- 測試改名 S4→S7 與計劃條款歸屬一致。「90 支」我沒逐支數,未驗。

### 已走過、判定沒問題
- release(session, p):會談結束後同編號新派工建立新 p,舊派工回來只扣舊 p,且只在 `pending.get(session) === p` 時刪,新 p 不被誤刪;舊 p 的等待者被 wake。
- end(keep) 直接回:endGen 不增、pending 不清,/clear 中途的派工回來照登記。reason 為 clear 或 resume 以外(exit、logout、-p 結束)照舊清。
- `version ?? 0`:撞版比對由 store 版本決定,缺值帶 0 不會退成無條件寫。
- SEAT_LOOSE_RE 第二支:`LUMOS_SEAT: ...`、`LUMOS SEAT：` 判壞;`Lumos seat guard` 一般句子不誤擋。底線或空白寫法不接冒號會判 none(即不隔離),這是文件寫明的取捨。
- Cf 剝除只用來判「是不是空行、是不是想寫標記」,合格比對仍用原文逐字,標記中間夾格式字元判壞;與計劃一致。

總結:最嚴重 minor,blocking 0 條
