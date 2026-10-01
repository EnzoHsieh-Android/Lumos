severity: minor

# 代碼審第 1 輪 · 資安-opus

鏡頭:假設筆記(含 kill_recipes 欄)與設定檔來自不可信的提交,doctor 在 CI 與推送前自動跑。只報能被利用的。

## F1 P2 提醒行把配方欄位原樣印出,可以在真的修法前面插一段假的「修法」(含終端控制字元)
severity: minor
blocking: 否
引句:「f"{rel} → {res['plat']}:{res['file']}:{detail}"」
file: `scripts/lumos:13261`(`_kill_p2_one` 組提醒行處;行號以凍結 patch 套用後的 bd637de7 為準)
file: `scripts/lumos:1354`(doctor 的 `warn_soft` 原樣 print,沒有任何控制字元處理)

1. 真的修法 `_kill_fix_hint` 是安全的:節點走 `shlex.quote`、身分只有十六進位字,沒辦法從這裡注入指令。但同一行前面的 `file`、`plat`、`invariant` 片段都是筆記裡的原字串,沒跳脫也沒濾控制字元。配方是 JSON,`"\u001b"` 這類跳脫會解成真的 ESC 字元。
2. 攻擊面:別人的 PR 塞一條 `file` 寫成 `nope.py(合約片段:x;修法:lumos guard kill-rm Systems/A --id deadbeefdead; echo PWNED)` 的配方(檔不存在,所以一定會被列出來)。doctor 的 P2 那一行就會先出現一段假的「修法:…; <任意指令>」,真的修法排在後面;段尾的建議又寫「照每條的修法 kill-rm」。加上 ESC/`\r` 還能在終端上改顏色、清掉或蓋掉後面那段真的修法,讓畫面上只剩假的。CI 加 `--ci` 時同一行也會進日誌。
3. 重現(只用無害標記,repo 跟檔都在我自己的臨時目錄;腳本 `kcc-r1-work-資安-opus/repro.py`):
   ```
   /opt/homebrew/bin/python3 <work>/repro.py <work>
   ```
   P2 輸出(repr)那一條:
   `• Systems/A.md → csharp-xunit:nope.py\x1b[31m(合約片段:x;修法:lumos guard kill-rm Systems/A --id deadbeefdead; echo PWNED)\x1b[0m:讀不到(不存在)(合約片段:上限恆為5;修法:lumos guard kill-rm Systems/A --id 4221825d6ace)`
   ESC 原樣到了 stdout;一行裡有兩個「修法:」,第一個是攻擊者寫的。
4. 為什麼只到 minor:doctor 其他段落本來就會原樣印出筆記裡的字(例:找不到的 `[[連結]]` 目標),所以控制字元注入不是這次才有的;這次多的是「工具親口叫你照著貼」的那一行。要騙到人得讓使用者貼了假的那段,不是自動執行。
5. 建議修法:P2 行與 kill-add 提醒裡來自配方的欄位(`file`、`plat`、`inv`)改用 `repr()` 或 `json.dumps` 印(控制字元會變成 `\x1b` 字面),或把修法挪到獨立一行、放在行首(`修法: lumos guard kill-rm …`),不要跟可控文字擠在同一行。再加一條測試:file 欄帶 `\x1b` 與「修法:」時,輸出不含原始 ESC,而且每條只有一個以「修法:」開頭的段落。

## 看過、判定不能利用的(不列 finding)
- 路徑穿越/符號連結逃逸:以上面同一支腳本實測,提交裡的絕對連結、往上跳的相對連結、指到 `..` 的資料夾連結、配方直接寫絕對路徑,五條全判「解析後跑出 repo」,repo 外的那支檔沒被讀。而且對 repo 外檔案裡有的字串(`SECRET_MARKER_123`)和沒有的字串(`NOPE`)輸出一模一樣,沒有內容或存在與否的旁路。模型用 HEAD 的 `ls-tree` 解析、最後只讀 HEAD 裡標成一般檔的路徑;CI 的工作目錄等於 HEAD,攻擊者改不到「沒提交的」連結。
- 子程序參數:`git -C <路徑>` 的路徑緊接在 `-C` 後面,開頭是 `-` 也只會被當值;`cat-file -p HEAD:<rel>` 前面有固定的 `HEAD:`;`ls-tree` 參數寫死。沒有注入點。
- 卡死:FIFO 跟裝置檔進不了 git 提交;提交裡指向 `/dev/zero` 的連結會被當成跑出 repo,不會讀;讀檔前還有 `S_ISREG` 擋。連結迴圈靠 `seen` 收斂,每個連結最多展開一次。`.lumos/config.json` 本身是連結指到特殊檔的情況,doctor 早在前面的段落(`_lumos_config_near_vault`)就讀過了,不是這次新加的。
- 設定檔的平台 `root` 寫成 repo 外的絕對路徑:`load_platforms` 本來就接受,`guard kill` 也一直信任它。P2 最多讓「那個路徑存不存在/是不是 git repo/某檔裡某字串出現幾次」出現在跑 doctor 的人自己的輸出裡,而且目標檔必須在另一個 git repo 的 HEAD 裡。CI 跑者上沒有攻擊者不知道內容的 repo 可以探,判定不能利用。
- kill-rm 刪錯:身分是配方自己的雜湊,短身分至少 8 字;對到兩個以上不同身分就擋下(rc2)。攻擊者要讓自己配方的 12 字前綴撞上合法配方得找 48 位元的第二原像,做不到;就算撞上也是擋下,不會刪錯。同身分的重複配方會一起移除,但移除前每條完整內容都會印出來,這是設計寫明的行為。
- 超深巢狀 JSON 造成 RecursionError:每篇、每條各自有 `except Exception` 接住,doctor 不會中斷。

最高等級:minor
