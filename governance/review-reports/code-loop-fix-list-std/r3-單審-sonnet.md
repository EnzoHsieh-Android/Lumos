severity: minor

四個指路段落都在、真的在下方,也講同一件事。「下方 guard kill 那條」是 `skills/lumos-design-loop/templates.md:232`,「下方〈分開驗修補與重構〉」是同檔 228 行。我沒找到照字面做會做錯的地方。`scripts/test_lumos.py` 沒有任何斷言釘住這幾段字串,也沒有程式檢查 `rN-repro.txt` 這個檔名。`*intake*.md` 的 glob 只收 .md,不會誤抓 .txt。

### C1 同一輪修補產出的檔,N 的口徑不一致
severity: minor
blocking: 否
引句:「N 跟同一輪的 `rN-intake.md` 相同」
這句只把 `rN-repro.txt` 對到 `rN-intake.md`。第2、3步卻要求把 `rN-repair.patch` 和 `rN-repair-binding.json` 存成「下一輪」的 N。
- 同一次修補會產出 r1-repro.txt 加 r2-repair.patch,中間沒有任何一句說明這兩個 N 為什麼不同。
- 「當輪 `rN-intake.md`」也沒講是剛收完貨的那一輪,還是下一輪。
- 字面照做能做完,但編排者可能把 repro 存成 r2。這會讓下一輪新席「連到這份」時找不到。
file: `skills/lumos-design-loop/templates.md:223`、`skills/lumos-design-loop/templates.md:234`

### C2 修補結論寫進 intake,可能漏給新席
severity: minor
blocking: 否
引句:「intake 只寫重現命令、摘錄與結論並指向這份」
派工詞追加段的「配對案例入口」可以指向 intake 的案例來源段(templates.md:255)。同一個 intake 的該組底下,現在被要求寫「修前紅、修後綠」的結論。這和同段「不讀上輪席報告或作者的因果結論」互相拉扯。只給案例來源段就能同時遵守,但新規則沒寫「結論段不給新席」。
file: `skills/lumos-design-loop/templates.md:255`

### C3 HIT/MISS 的限縮和 intake 收貨定義是兩套說法
severity: minor
blocking: 否
引句:「HIT/MISS 字樣只用在核對席位宣稱的重現表，修補自己的驗證寫修前紅、修後綠」
- 收貨規則寫的是 intake「每條格式=重現命令+輸出摘錄+HIT/MISS 結論」(templates.md:329)。同一行還說前掃語意類修正「逐條記這裡」,新限縮沒處理這條。
- 席位宣稱的重現和修補的「修前紅」往往是同一條命令,編排者得在同一個檔裡寫兩列。
- `--refuted-set` 只認重現表同一列的 id 加 HIT/MISS,新規則沒有破壞它,所以不是 blocking。

### C4 repro 檔既叫原始輸出又要遮罩,且沒說進不進 binding
severity: minor
blocking: 否
引句:「修補這一輪重現與改壞驗證的原始輸出另存 `rN-repro.txt` 進卷證」
- 後半句又要「只留必要非敏感內容、先遮罩秘密」,所以存下來的不是原始輸出。
- 被引用的 guard kill 那條末句是「不能安全保留可核對證據就未判定」。遮罩不乾淨時,修補自己的「修前紅」也會變成未判定,新規則沒交代這種情況。
- 第5步規定產生的 log 要在 binding 逐檔列 `archive_only`,新規則沒說 repro 檔屬不屬於。如果派工單 `materials` 把它列進去,會吃掉 1800 行額度。
file: `skills/lumos-design-loop/templates.md:239`

修補鏡頭三問:
- 有沒有修對:修對了。上一版把拆函式寫成「暫時本機提交加兩端提交碼存進 binding」,和〈分開驗修補與重構〉重複又略有出入,現在改成單源指路。
- 有沒有讓原本對的說法變錯或丟掉資訊:沒有變錯。丟了「完整原始輸出」(現在改成遮罩後的必要內容),也丟了中間提交碼存放位置的明文。這兩處只是精度下降。
- 有沒有帶進新問題:有,就是 C1 到 C4,都只是 minor。

共 4 條,其中 major 0 條
