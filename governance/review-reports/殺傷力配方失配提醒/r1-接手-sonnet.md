severity: major

## F1 提醒叫人「改寫原文再宣告」,但工具沒有改寫或刪除配方的路,舊的失配配方會留著
severity: major
blocking: 是
引句:「先照現在的程式改寫原文再宣告」
file: `scripts/lumos:12886-12960`(cmd_guard_kill_add 判重段:配方身分含 old,old 一變就是新配方、append;同身分且 new 不同時回「先把舊的那條手動拿掉」)
1. 看到 kill-add 提醒的人照字面做:用新的 `--old` 再跑一次 kill-add。因為配方身分是 (筆記, invariant, file, old),old 變了就被當成另一條,舊的失配配方原封不動留在 `kill_recipes`。
2. 結果是 P2 段每次 doctor 照樣列舊的那條,而且 guard kill 對舊條仍判 drifted。spec 沒有任何一處說要手動刪舊條,也沒有「刪」的指令(程式裡查無 kill-remove 類指令,只能手改 frontmatter 的單行 JSON)。
3. P2 的每一條列項、kill-add 的提醒,都只說「對不上」,沒給下一步(改哪個欄位、新原文怎麼挑、舊條要不要刪、手改時 `kill_recipes` 是 `|-` 後單行 compact JSON 且改完要自己維持)。沒脈絡的下一個會談只能猜,rtb 那 10 條存量(REVISIT 的驗收對象)就清不掉。
4. 建議:提醒與 P2 的 `warn_soft` 都帶 `advice=`(該函式本就支援),寫明「新增新原文那條後,手動刪掉舊條;或手改該節點 kill_recipes 的 old」;或在〈做法〉明列「改寫配方」的標準步驟並寫進 skill 文件。

## F2 RETIRE-IF 裡「寫入時那道提醒一次都沒印過」無處可量
severity: major
blocking: 是
引句:「而且寫入時那道提醒這段期間一次都沒印過」
file: `scripts/lumos:12886`(cmd_guard_kill_add 只用 print 到 stderr,spec 的新提醒同樣只寫標準錯誤,沒有任何留痕)
1. 提醒只印到 stderr,不寫帳(沒有 log、不進 `.governance-log`、不進 `.kill-log.jsonl`),事後無法得知 8 週內印過幾次。
2. 因此撤除條件的後半段無法照字面量:接手者只能「相信沒印過」,條件永遠不會被驗證成立或不成立。
3. 「連續 8 週」要的是 doctor P2 逐週結果,也沒有地方記每週 P2 的列出數(doctor 本身不留歷史,`--verbose` 輸出也不落盤)。要嘛加留痕(哪個檔、什麼格式),要嘛把撤除條件改成能量的(例如「rtb 與工具鏈兩邊,各抽一次 `lumos doctor --verbose` P2 為零,間隔 8 週」並說誰、何時抽)。

## F3 REVISIT 2026-10-15 依賴「請 rtb 會談回報」,沒有留下可執行的步驟與判斷門檻
severity: minor
blocking: 否
引句:「還有剩就照剩下的數字決定再等兩週或攤給人裁」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:28`(同行 REVISIT)
1. 到期日接手的會談要自己找 rtb 會談,但 rtb 是另一個專案,沒說怎麼聯絡、回報貼哪裡(哪篇筆記/Issue)、基準數字是 10 條(其中 Mock-DSP 1 條是出現 4 次,屬另一種修法)。
2. 「照剩下的數字決定」沒有門檻(剩 1 條算不算全修完?剩多少再等?),兩週後再等的次數也沒上限,可能無限延後。
3. 建議:寫明回報落點與一個數字門檻(例如剩 0 條開另案、剩 ≤3 條等一次、其他攤給人),REVISIT 另開一行帶日期給 doctor 唸。

## F4 落點交代不全:路線圖、skill 文件、guard-kill 要寫什麼沒講
severity: minor
blocking: 否
引句:「revert 實作提交即可:doctor 少一段、kill-add 少一行提醒;筆記與配方都沒被改過。」
file: `docs/lumos-toolchain-knowledge/Projects/漂移防治路線圖_計劃.md:35`(1a 列「在做」連到本計劃)與 `skills/lumos-project-notes/reference.md:530,594`(kill-add 說明)
1. `lands_in` 只列 Systems/guard-kill,但 spec 沒說要在該節點補什麼(新增 P2 段、kill-add 新提醒、不改 guard kill 的 WHY 行?),也沒說完成後把路線圖 1a 列由「在做」改成什麼。
2. 實作會改變 kill-add 的使用者可見輸出與 doctor 輸出,但 skill 文件(reference.md 的 kill-add 說明、commands/06 的那列、doctor 段落)沒被列為要同步的文件;下個會談讀 skill 會不知道有這個提醒、也不知道失配後怎麼修(與 F1 同根)。
3. 對比既有併發計劃有列出要同步的文件清單(含 reference.md 與參數說明字串),本案沒有,容易漏。
4. 建議:新增〈落點〉小節列出 guard-kill 節點、路線圖 1a 狀態、reference.md/commands 06 要補的句子。

## F5 doctor 讀的是工作目錄,kill-add 與 guard kill 的修法順序沒說,修完立刻 P2 轉綠但 guard kill 仍可能 drifted
severity: minor
blocking: 否
引句:「讀的是工作目錄的檔(包含沒提交的改動);guard kill 讀的是隔離工作樹裡檢出的提交版本」
file: `scripts/lumos:13143`(cmd_guard_kill 以提交版本建隔離工作樹)
1. 誠實界線有提差異,但沒告訴修配方的人後果:改了程式與配方、尚未提交時,P2 全綠,跑 guard kill 還是 drifted。接手者看到「P2 綠了 guard kill 卻紅」不知道原因。
2. 建議提醒文字或 skill 補一句「配方與程式要先提交再跑 guard kill」(併發計劃已有同類補救順序可引用)。
