# esc r1 邊界席
B-1|major:desc 換行不消毒,--list 一行一筆合約被打穿(週報 grep 載重)。
引句:「[{r.get('severity','?')}@{r.get('stage','?')}] {r.get('desc','')}」
B-2|major:ANSI 控制碼原樣進終端(cat -v 實證)。
B-3|major:歸因守衛無 NFC 正規化——NFD 貼上形被擋且錯誤訊息肉眼無解。
引句:「if loop_id not in known:」
B-4|minor:canary 帳壞行靜默吞(與 escape 帳警告不對稱)。
B-5|minor:壞行警告逐行重複無行號,50 壞行=50 條相同噪音。
B-6|minor:--list 靜默丟棄 positional 編號,像按迴圈過濾其實不是。
B-7|major:「最重」單筆 fixture 測不到權重表——改壞權重 7 條全綠實證。
引句:「check("--list 讀得回(按迴圈分組+最重等級)"」
抑噪:併發 400 筆實測無撕裂;5 萬字 desc 落盤完整。
severity: major
