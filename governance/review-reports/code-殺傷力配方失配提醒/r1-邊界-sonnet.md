severity: minor

邊界-sonnet 第 1 輪報告。方法:在 `--shared` clone 裡對約 90 個邊界各自「同一份筆記同時跑判斷函式與真跑 `lumos guard kill --json`」比對,另跑 kill-add / kill-rm / doctor 端到端。
實跑確認沒問題的格子(不另列 finding):file 為空 / `.` / `..` / 絕對 / `./x` / `a//b` / `sub/../x` / 不存在名字再 `..` / 結尾斜線 / 資料夾 / 空白檔名 / 中文檔名 / 檔名含反斜線 / glob 字元 / 前導 `-` / NFD;old 為空字串(判 hits,與 guard kill 同為 N+1 次;空檔 + 空 old 判 ok 也一致)、跨行、含 `\r\n`(判 0 次,與 guard kill 同)、檔含 BOM、檔為 CRLF;old 非字串 / None、file None、元素非物件 → malformed;設定檔壞 JSON / 空檔 / BOM / 最外層是陣列、字串、null、平台根 null、根不存在、根是檔、根不在 git、預設平台不存在、兩平台無預設 → kill-add 各印一行「沒驗原文」、照舊寫入、rc 0;kill-rm 的 `--id` 大小寫(不分)、剛好 8 字、完整 64 字、前後空白(被 strip 接受)、7 字 / 非十六進位 / 空字串 / `0x` 前綴 / 零命中 → rc 2 筆記不變;重複配方一起移除;格式壞配方(字串、陣列、None、欄位型別錯)移得掉;`kill_recipes` 為 inline / 多行縮排 / 後面還有別的欄位,移除後檔案形狀正常;`[kill: recipes]`(帶空白)標記也能被拿掉;筆記 frontmatter 沒收尾 / CRLF / BOM → kill-add 與 kill-rm 都擋下 rc 2 筆記不變。
`prod.py/.`、`../wt/prod.py` 兩格判 ok 而 guard kill 回 error(revert 失敗):測試的對應表明文把「還原失敗也算套用了壞法」記為相符(`_krc_match` 的 reverted_fail),不當 bug 報。

## F1 配方缺 `new`、或 `new` 不是字串時,判斷函式與 P2 說「對得上」,真跑 guard kill 卻崩潰 rc 1
severity: minor
blocking: 否
引句:「    if not isinstance(r, dict) or not isinstance(r.get("file"), str) or not isinstance(r.get("old"), str) \」
file: `scripts/lumos:13816`(cmd_guard_kill 的 `src.replace(r["old"], r["new"], 1)` 與其前的 `r["new"]`)
1. 重現(臨時 repo,配方只缺 `new`,其餘正常、原文恰好一次):判斷函式回 `ok`,`lumos doctor` P2 印「✓ 殺傷力配方的原文都對得上」,`lumos guard kill Systems/Limit --json` 以 `KeyError: 'new'` 崩潰 rc 1;`new` 為 None / 7 時同樣是 `TypeError: replace() argument 2 must be str`、rc 1。
2. `test` 缺、`test` 名含空白分號(guard kill 判 error「test 名不合法」)、`test` 為整數(survived)也都是 P2 全綠。計劃把 malformed 明定為 file/old/platform/invariant 四欄,所以程式與計劃字面相符、是計劃範圍問題;但 S5 本意是「判定與 guard kill 對得上」,這幾格是 P2 的假安心。只有手改筆記才會出現,故降為 minor;若收貨端依「判斷與 guard kill 結果對不上=major」字面,可升級。
3. 建議:要嘛把 `new` 為字串納入 malformed 判定,要嘛在 P2 標題/計劃的〈範圍外〉明寫「不驗 new/test 欄」。

## F2 路徑含換行時 kill-add 的提醒變成兩行,違反 S1「恰好一行」
severity: minor
blocking: 否
引句:「msg = f"{f} 讀不到({res['detail']});guard kill 跑到它會判 drifted 或讀檔出錯。{fix}"」
file: `scripts/lumos:13203`(新 `_kill_add_warn`,同段 outside/hits 分支同樣直接內插 `{f}`)
1. 重現:`lumos guard kill-add Systems/Limit 上限恆為5 --file $'a\nb.py' --old LIMIT --new Z`,標準錯誤非空行數 = 2(`⚠ 提醒:a` / `b.py 讀不到(不存在);…修法:…`),rc 0、照舊寫入。
2. P2 的逐條文字(`{res['file']}` 內插)有同樣形狀,會把一條拆成兩行。
3. 影響很小(要刻意寫換行檔名),但「恰好一行」是 S1 的字面條款、且測試 `_kr_err_lines` 以行數驗,日後有人把含換行路徑放進測試會誤判。建議顯示時對 file 做 `repr` 或把控制字元替換成空白。

## F3 doctor 遇到「讓 load_platforms 丟例外」或「最外層不是物件」的設定檔,在 P2 之前就崩潰,P2 對應的 S4 字面走不到
severity: minor
blocking: 否
引句:「warn_soft([f"設定檔讀不了:{_p2['cfg_err']}"],」
file: `scripts/lumos:4552`(load_platforms:`plats = cfg.get("platforms")` 對 list/str/null 設定直接 AttributeError;另 `預設平台 'q' 不在平台清單裡`、`兩平台沒寫 default_platform`、`root: null` 都是 ValueError/TypeError)
1. 重現:設定檔為 `[1,2]`、`"x"`、`null`、`{"default_platform":"q","platforms":{"a":{…}}}`、兩平台無預設、`root: null` 時,`lumos doctor` rc 1 並丟 traceback(出在 [T] 段呼叫 load_platforms),輸出裡根本沒有 P2 標題。我把基底 51f83721 的 `scripts/lumos` 拿來跑同一組設定,結果完全相同——是既有崩潰,不是這次引入。
2. 後果:S3「doctor 一般與 --strict 回傳碼都不受影響」、S4「內容讓 load_platforms 丟例外時印設定檔讀不了」在 doctor 端只有壞 JSON / 空檔 / BOM 三種走得到(那三種 load_platforms 不丟錯);P2 裡針對例外與「最外層要是物件」的分支(`_kill_cfg_load` 後半)只有 kill-add 路徑會用到。測試若是行程內直接呼叫 `_kill_p2_scan` 就看不出這件事。
3. 建議:在計劃〈實作紀錄〉註明這個既有前置崩潰,或另立 Issue;P2 本身不需改。

## F4 P2 對「格式不對」的配方印出空欄位的「::」,讀起來像壞掉
severity: minor
blocking: 否
引句:「st["items"].append(([stem], f"{rel} → {res['plat']}:{res['file']}:{detail}"」
file: `scripts/lumos:13261`(`_kill_p2_one` 對 malformed 與 invariant 為非字串的配方)
1. 重現:`kill_recipes` 為 `[1,2]`(或元素缺 file、invariant 為整數)時 doctor P2 印 `Systems/Limit.md → ::配方欄位格式不對(合約片段:;修法:lumos guard kill-rm Systems/Limit --id c8fe07417869)`。平台、檔名、合約片段三處都是空字串,留下 `::`、`合約片段:;`。
2. 功能無誤(身分與修法都對、kill-rm 也移得掉),只是 S3 要求「含原因」時讀者看到的是空欄。可在 plat/file 皆空時省略前綴。

## F5 kill-rm 的 `--id` 超過 64 字時回的錯誤訊息說「至少 8 個」,方向反了
severity: minor
blocking: 否
引句:「if not re.fullmatch(r"[0-9a-f]{8,64}", pre):」
file: `scripts/lumos:13458`(cmd_guard_kill_rm 的同一段 print)
1. 重現:貼完整 64 字身分多帶一個字元(65 字),rc 2、筆記不變(行為正確),訊息卻是「--id 要給至少 8 個十六進位字元的配方短身分(收到 '…65 字…')」,使用者會困惑「我給的已經超過 8 個」。7 字、非十六進位、`0x` 前綴都適用這句,唯獨過長不適用。
2. 純文字問題,S6 只規定「不到 8 個十六進位字元 → 擋下回 2」,過長沒規定;列為提醒。

最高等級:minor
