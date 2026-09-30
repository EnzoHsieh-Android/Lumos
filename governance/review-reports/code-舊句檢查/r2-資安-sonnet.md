severity: minor

# 資安席(sonnet)r2:舊句檢查 m1 第 1 輪修正

審材:r2-snapshot.patch(以 scripts/lumos 部分為主)。實驗都在 `git clone --shared` 的臨時目錄、HOME 換成假目錄跑;重現腳本用測試檔自己的 `_nh_repo`、`_m1_note`、`_m1_run` 組專案,在 /private/tmp/claude-501/sec-r2-x/(e_long.py、e_pad.py、e_cache.py、e_path.py、e_dos.py、e_dos2.py)。

## F1 單行上限成了旁路:一句舊句補到超過 20000 字,block 模式 rc 0,而且結論行說「沒有還在講的」
severity: minor
blocking: 否
引句:「        if len(ln) > _DRIFT_M1_LINE_MAX:」
佐證行:file: `scripts/lumos:_drift_m1_scan_note`(超長行 `continue` 之後不進任何發現、也不影響 rc);`scripts/lumos:_drift_m1_conclusion`(結論只看 handle、listed 筆數)
敘述:
1. 設定 `drift_check.old_sentence=block`。起點 `src/a.py` 定義 `old_func_x`,終點刪掉;筆記 `Systems/B.md`(about_code 列 src/a.py)寫一行 `這裡呼叫 \`old_func_x\` 做事。` 後面接 20000 個空白。
2. 跑(e_pad.py):`_m1_run(root, base..tip)` 輸出 `(0, '舊句檢查:這次消失 1 個名稱,筆記裡沒有還在講的\n  1 行超過 20000 字沒掃\n')`。同一句不補空白(e_long.py 的 A.md)同批回 rc 1、列為要處理。
3. 壞在哪:超長行只計數印一行、不算「判不了」,所以 block 不擋;結論行同時宣稱「筆記裡沒有還在講的」,跟下一行「1 行沒掃」互相矛盾,CI 上看結論行的人會被誤導。CI 也走同一條路,不能靠 CI 補位。
4. 邊際能力:這條旁路不比句內歷史字眼(在句子裡加「原本」)更便宜,所以只評 minor;但那條是設計上的取捨、這條是實作副作用,超長行至少該當成「判不了」(block 擋)或把結論行的「沒有還在講的」改成「沒掃完」。
5. 時間上限本身有效:我試 3 萬個名稱、200 行 x 1000 個名稱(每行約 16000 字):2.5 秒(e_dos.py);6 萬個路徑型名稱、30 行 x 1000 個:6.9 秒(e_dos2.py,路徑型走 `others` 那條逐分支正則,最慢)。都在 30 秒預算內,r1 的 DoS 已收。

## F2 group_ok 放寬後,群組可寫的快取目錄裡,同群組者只用改名就能讓 m1 讀到別的 blob 的定義集合
severity: minor
blocking: 否
引句:「+    if not _mkdir_trusted_under_home(".cache", "lumos", "drift-defs", group_ok=True):」
佐證行:file: `scripts/lumos:_trusted_private_dir`(patch 內 `st.st_mode & (_stat.S_IWOTH if group_ok else ...)`);`scripts/lumos:_lens_cache_read`(只查檔案擁有者是自己、檔不可群組寫、TTL,不查「這個檔是為哪個 blob 寫的」)
敘述:
1. 擁有者檢查是有的:同群組者放不進自己擁有的檔(`_lens_cache_read` 驗 st_uid),也建不出擁有者是你的檔。符號連結:目錄與各層父目錄逐層擋,`.cache/lumos` 被換成他人建的目錄會因擁有者不符被擋。
2. 放不掉的是「改名」:目錄群組可寫時,同群組者不用擁有檔案,就能把 V 自己寫的 `<key>.json` 互相改名。快取鍵是 sha256(內容編號|schema|Python 版本),攻擊者推的提交,自己算得出 base 版、tip 版兩個 blob 的鍵。
3. 重現(e_cache.py):先跑一次寫出兩筆快取(目錄 0700);`chmod 770` 模擬群組可寫;`os.replace(tip 版項目, base 版項目)`;再跑同一段範圍:第一次 `擋下:… 消失了 1 個名稱 … 要處理 1 筆`,改名後 `(0, '舊句檢查:這次改到 1 支程式檔,沒有名稱消失')`——起點版讀到終點版的定義集合,消失的名稱整批被吃掉。
4. 對照:同一個 0770 目錄,`_trusted_private_dir(d, …)`(未帶 group_ok)回 False、快取整個不用,帶 `group_ok=True` 回 True(實測)。放寬前這條攻擊不成立。
5. 限制:目錄要是群組可寫才成立,而 `_home_cache_write` 每次寫入都 `chmod 0700`、新建層明給 0700,所以只有全命中的唯讀跑(不觸發寫入)之前,由管理者或 ACL 把 leaf 目錄設成群組可寫才會留著;.cache 與 .cache/lumos 那兩層群組可寫只造成快取用不了,改不到內容。m1 本身是 advisory(預設 warn),所以評 minor。修法方向留給實作者;要不要接受這個殘餘,請照 `_mkdir_trusted_under_home` docstring 的「誠實邊界」補一句(目前 group_ok 註解只提 umask 002)。
6. 漏記痕跡 `ledger-miss.jsonl`:`O_NOFOLLOW` 加開檔後查擁有者,擋得住他人預建的普通檔;他人預建的 FIFO 會讓 `os.open(O_WRONLY)` 卡住,但要漏記發生且 drift-m1 目錄群組可寫兩個條件同時成立,我沒能自己造出第一個條件,不報。

## F3 名稱正規化擋得完整,但同一行提示裡的路徑與說明只過 _esc_clean:U+202E、零寬字元原樣印到終端,docstring 的「印提示都過這一支」講過頭
severity: minor
blocking: 否
引句:「    也不帶非 UTF-8 位元組留下的替身字元。列出、印提示、寫表態、比對表態都過這一支,照貼提示印的名稱一定表態得掉」
佐證行:file: `scripts/lumos:_drift_fix_hint`(路徑走 `_drift_sh`,只擋 shell 特殊字元);`scripts/lumos:_esc_clean`(只換 C0 與 0x7f–0x9f,U+202E、U+200B 通過)
敘述:
1. 名稱側我掃了整個 Unicode:`_drift_m1_name_canon` 擋掉 Cc、Cf、Cs、Zl、Zp,剩下通過的只有隱形但無終端副作用的類別(Cn、Co、Mn、Zs 在名稱中間、U+3164 等填充字元、U+FFFD)。名稱不會帶出終端控制或方向覆寫;shell 注入用 `x';id;'` 等實跑,整段單引號包住(見 e_path.py 輸出 `'Systems/q'"'"'; id; '"'"''`),安全。
2. 有一處沒對上:docstring 說也擋「非 UTF-8 位元組留下的替身字元」,實作只擋 Cs(路徑無損解碼的替身);內容解碼走 `_drift_decode(errors="replace")` 留下的 U+FFFD 是 So,`m._drift_m1_name_canon("ab_�cd")` 回名稱本身。後果無害(列出與表態兩側用同一支,貼得過),只是宣稱與行為不一致。
3. 路徑側(重現 e_path.py):git 索引放 `docs/kg-knowledge/Systems/bidi<U+202E>evil.md` 與 `zw<U+200B>x.md` 的筆記,drift check 印出 `lumos drift ack 'Systems/bidi<U+202E>evil' 8 --kind m1 --name=old_func_x --reason "…"`——U+202E 原樣在終端,雙向重排會把它後面整段指令顯示成倒的;零寬那條看起來與正常檔名一樣。ESC 序列(`x\x1b[31m.md`)有被換成空格。貼上的實際位元組仍是正確的、指令也帶不進額外參數,所以只算顯示層的混淆,評 minor。同一筆在治理帳裡走 JSON 轉義,沒問題。
4. 非 UTF-8 檔名(`se\xf1or.md`):終端印成 `se\udcf1or`(stderr 的 backslashreplace,不當機),帳裡是替代字元 `se�or`(e_path.py 實跑,rc 1、帳寫成功)。但提示裡貼的路徑是 `'Systems/se\udcf1or'` 這串字面反斜線,貼上去找不到檔、表態不掉,只能改筆記。這不是安全問題,是 block 模式下這一筆只能靠改筆記或整批略過的可用性缺口;每次改路徑名稱後要重驗:第一個真的遇到非 UTF-8 筆記檔名的專案(macOS 檔案系統本來就建不出來,只有 Linux 檔系統會遇到)出現時。

## 兜底 error 會不會讓 block 放行(不算 finding)
- `_drift_m1_guarded`:第一次例外 → `_drift_m1_report(new_res("error"))`:`st in _DRIFT_M1_UNKNOWN` 使 busy 為真,block 模式 rc 1、warn rc 0;第二次也丟例外 → 最後一行 `return 1 if mode == "block" else 0`。三層都是 block 擋、warn 放,跟 warn 本來的語意一致,沒有「讓例外把 block 變成放行」的路徑。
- 攻擊者要用例外做的事只有拖慢或擋掉自己的推送(能造成例外的輸入本來就是自己推的內容),沒有讓別人放行。`except Exception` 不吃 KeyboardInterrupt、SystemExit,所以使用者中斷仍然中斷。
- 表態(ack)在 error 狀態不會被讀:`res["handle"]` 為空,ack 不影響 rc。

## 其他角度的結論
- 快取目錄與檔:擁有者檢查、路徑逐層驗、`os.replace` 原子寫都在;缺口只有 F2 那一條(改名)。
- 名稱表態比對 `_drift_m1_split_acked`:表態檔裡的名稱與發現的名稱都過 `_drift_m1_name_canon`;非字串、帶控制字元的表態名稱被丟掉、不涵蓋任何名稱,方向對(寧可判成沒表態)。
- 推送內容自帶表態(ack 檔隨提交進 repo)是既有設計,不是新洞。

## 圖譜鏡頭逐條判定
- Systems/lumos-cli-read(★INVARIANT★ search 預設排除 superseded):diff 不碰 search,不影響。
- Systems/bound-tests-gate(★INVARIANT★ 綁定測試真跑):diff 不碰 code-loop check;新測試進了測試檔但不改綁定測試的跑法,不影響。
- Systems/guard-kill:不碰 guard kill,不影響。
- Systems/授權與歸屬(授權檔不得入白名單、主程式檔頭 SPDX 與 MIT):diff 沒動 `_VENDORED_TOOLKIT` 也沒動檔頭,不影響。
- Systems/測試假綠形態:本席不做覆蓋度判定;F2 顯示「快取信任放寬」目前沒有對應的翻紅測試(e_cache.py 可當雛形),已在 F2 寫明。
- Systems/lumos-cli-lifecycle、Systems/design-loop、Systems/pitfalls-code-loop:diff 不碰,不影響。
- 「只列名」的其餘節點:`_trusted_private_dir`、`_mkdir_trusted_under_home`、`_home_cache_write` 三支共用函式多了 `group_ok` 參數,預設 False;既有呼叫端(派工鏡頭快取等)行為不變,只有舊句檢查兩處(快取、漏記痕跡)走 True,影響面僅限 F2。

最高等級:minor
