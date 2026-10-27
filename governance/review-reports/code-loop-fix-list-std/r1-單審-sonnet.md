severity: minor

審查結果:找到一處流程指向不準和兩處用詞問題,三處都不會讓流程跑不下去,也沒有測試斷言這段文字。我對照了 `rN-intake.md` 的寫入時機(收貨後、記帳前,入帳後不再動)、範本第6步和手冊其他段落。

### C1 `rN-repro.txt` 與第6步 `before`／`after` 的對應在時序上對不起來
severity: minor
blocking: 否
引句:「它就是本節第6步 `before`／`after`「連到原始輸出」指向的那份,不另開第二個落點」
- 新規則把 `rN-repro.txt` 說成第6步 `before`／`after` 指向的那份。第6步是下一輪收貨時,針對新席每條 finding 填證據紀錄。`rN-repro.txt` 則是修的這一輪、「先紅後綠」時產出的輸出。
- 兩者產生的輪次和對象都不同,「就是」說得太滿。接手者可能以為只存一份 `rN-repro.txt` 就滿足第6步,或者反過來把第6步輸出塞進 `rN-repro.txt`。
- 兩份文件對「當輪」的指法不一致。範本第2步把修補差異存成「下一輪的 `rN-repair.patch`」,新規則的 intake 和 repro 卻都寫「當輪」,沒說明 N 指哪一輪。
- 新規則另說「intake 只寫結論與指向」。既有收貨紀錄的格式是「重現命令+輸出摘錄+HIT/MISS」,`--refuted-set` 也要 intake 重現表有 HIT/MISS 字樣。接手者若把摘錄整段搬進 `rN-repro.txt`,可能漏掉 HIT/MISS 結論列,記帳被擋。
- file: `skills/lumos-design-loop/templates.md:223`
- file: `skills/lumos-design-loop/templates.md:329`
- file: `skills/lumos-code-loop/reference.md:131`

### C2 「修補與拆小分開提交」沒交代推前要壓成一個、留痕綁版本
severity: minor
blocking: 否
引句:「修補提交和為了複雜度上限做的拆小分開提交(拆小照下方〈分開驗修補與重構〉當非必要重構)」
- 單源下方一條說「中間點可用暫時本機提交;推前仍按一功能一提交整理」。同一個範本、專案 CLAUDE.md、`skills/lumos-code-loop/SKILL.md:13` 也都說壓提交後留痕失效。
- 新句和兩處指路句(`skills/lumos-code-loop/SKILL.md` 第5步、`06-代碼審與推送.md`)只寫「分開提交」,沒說是暫時的本機提交。照字面做的人可能把兩個提交都推上去,或壓掉後失去「判不出是不是修補造成」要保的區間。
- 兩條規則其實能共存,只是沒寫出來。建議加半句「推前壓成一個,兩端提交碼照 `rN-repair-binding.json` 保存」。
- file: `skills/lumos-design-loop/templates.md:229`
- file: `skills/lumos-code-loop/SKILL.md:13`

### C3 「複雜度上限」是全 repo 沒定義過的詞,指路句裡的「拆小」又有歧義
severity: minor
blocking: 否
引句:「動手修前先列同一問題的全部出處（同族函式、各處說法、新守衛的反向案例）、修補與拆小分開提交、重現輸出另存」
- 我在 `skills/` 下搜過,「複雜度上限」只出現在這一處新增文字,沒有定義。接手者不知道是哪個上限、誰判定「為了它拆小」。
- 手冊別處的「拆小」另有所指。`scripts/lumos:17104` 的熔斷提示和 reference 的「重估是否拆案」,指的是把整個改動拆小或拆案。
- 兩份指路句只留「拆小」兩個字,沒有單源那句括號說明。接手者可能把它讀成「拆案」,或誤以為要拆成更多個提交。
- 建議指路句帶上「(為複雜度上限做的拆小)」,並在單源指明是哪個 lint 或規則。
- file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:118`
- file: `skills/lumos-code-loop/SKILL.md:50`

### 其他查證結果
- **寫入時機**:新規則沒有跟 intake 的寫入規則打架。`skills/lumos-code-loop/SKILL.md` 的順序是第3步收貨、第5步修、第6步記帳,修前寫 intake 發生在入帳前;`reference.md:127` 也寫「動手前在當輪尚未入帳的 intake」。「席報告收齊前不落地」管的是席報告,不管 intake。
- **單源一致性**:用詞和檔名(`rN-intake.md`、`rN-repro.txt`)在三處一致。圖譜 WHY 行的出處檔 `governance/review-reports/code-e2e-by-feature/cap-retro.json` 存在。
- **機械守衛**:`scripts/test_lumos.py` 裡沒有任何測試斷言新段落的字串。我沒找到會因這段文字紅的守衛,但也沒有守衛護著這條新規則。
- **新增檔案**:`rN-repro.txt` 是新增的檔名,沒有程式會掃描或要求它,也沒有把 `.txt` 視為違規的規則。

共 3 條,其中 major 0 條
