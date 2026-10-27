severity: minor

整體判斷:新規則和手冊其他段落沒有互相矛盾到讓人無法照做的地方,但有三處照字面做會繞路或留下風險。我沒找到會走錯到出事的地方。

查證結果:
- 「推送前新增告警閘的函式複雜度」在 repo 裡有對應。`skills/lumos-code-loop/SKILL.md` 第13行寫「這次改動帶進新的告警」。`.lumos/lint.json` 的 ruff 設定是 `C901` 加 `max-complexity = 10`。
- `scripts/test_lumos.py` 裡沒有測試斷言這次改動的字串。我 grep 了「先列出處」「rN-repro」「暫時本機提交」「修與釘」「分開驗修補」「第0步」,都沒有。
- 唯一碰到 `templates.md` 和 `SKILL.md` 的守衛是 `t_design_loop_manuals_spec_freeze_wording` 與角色卡檢查,它們看的是別的字串,不會因此失效。
- 「推前壓成一個」跟既有的「中間點可用暫時本機提交；推前仍按一功能一提交整理」一致。`SKILL.md` 第8步也是壓成一個功能提交後才凍結、留痕。所以和「壓提交後留痕失效」不衝突。
- 第2步 `rN-repair.patch`、第6步 `before`／`after` 的「下一輪」命名,新規則沿用了原有慣例,沒有矛盾。

### C1 binding 的步驟引用指錯了
severity: minor
blocking: 否
引句:「兩端提交碼照本節第2步存進下一輪的 `rN-repair-binding.json`」
- `rN-repair-binding.json` 是第3步〈留來源〉建的。第2步是產生 `rN-repair.patch`,第1步才是固定兩端。
- 第3步還有一句「squash/rebase前保存仍可取回的兩端完整來源」,管的是壓提交之後那兩個提交碼還取不取得回來。照字面只看第2步的人可能漏掉這一句。
- 這條規則正好要求推前壓提交,所以提交碼取不回的風險比平常大。
- 另一處小問題:同一句話裡,「當輪 rN-intake.md」和「下一輪 rN-repair-binding.json」的 N 指不同輪。有「同輪」「下一輪」字樣可以救,但容易誤讀。
- file: `skills/lumos-design-loop/templates.md:223`(修補後版本;binding 在第237行)

### C2 「完整原始輸出」和遮罩秘密的規定沒對齊
severity: minor
blocking: 否
引句:「修補這一輪重現與改壞驗證的完整原始輸出另存同輪的 `rN-repro.txt` 進卷證」
- 同一節第6步寫「環境紀錄只留相關非秘密資訊，不抄整份環境變數」。`guard kill` 那條也寫「命令與輸出只保留必要非敏感內容，保存前遮罩秘密／個資…不能安全保留可核對證據就未判定」。
- 新規則說「完整」,沒提遮罩。卷證會進 git 並被推上去。
- 另外,intake 的 HIT／MISS 在原定義裡是「命令能否重現席位宣稱的結果；MISS＝佐證不採信、finding 退回或降級」。
- 新規則要求在 intake 為修補的重現也寫 HIT／MISS。修後「改壞驗證」若寫 MISS,意思是「已修好」,和原定義打架。
- 記帳時 `--refuted-set` 用「id 在 intake 同一列整字出現並有 HIT/MISS 字樣」來認列,這樣寫也容易被誤認為被反駁。
- file: `skills/lumos-design-loop/templates.md:232`(遮罩規定)、`skills/lumos-design-loop/templates.md:329`(HIT/MISS 與 intake 定義)

### C3 兩個暫時提交,但 binding 只有「兩端」
severity: minor
blocking: 否
引句:「修補和為了過推送前新增告警閘的函式複雜度而做的拆函式，先各用一個暫時本機提交分開」
- 這樣會有三個點:修前、修補後、拆函式後。
- 第1步的終點是「修補已提交後的完整提交碼」。binding 只有 `before_commit`／`after_commit`,拆函式後那個點沒有欄位可記。
- 拆函式提交落在 `rN-repair.patch` 之外,新席只能靠完整改動快照看到它。
- 「每個點留完整提交、涵蓋組與第6步證據指標」(分開驗修補與重構那條)沒說放在哪。
- 「推送前新增告警閘的函式複雜度」措辭偏窄:閘擋的是任何新告警,複雜度只是 `C901`(上限10)這一項。
- 另外,告警指紋含函式名,拆函式會產生新名稱,可能又被當成新告警。`.lumos/lint-waivers.json` 裡有好幾筆這種案例。規則沒提這點。
- file: `skills/lumos-design-loop/templates.md:235`(第1步)、`.lumos/lint.json:3`

### 修補鏡頭三問
1. **有沒有把要修的說法修對?** 有。上一版寫「修補與拆小分開提交」,和「一功能一提交」衝突,現在改成暫時本機提交加推前壓成一個。`rN-repro.txt` 原先寫「就是第6步指向的那份」,會讓新席拿作者的輸出頂替自己的查證;現在明寫新席仍須自己查證,不以這份代替。
2. **有沒有讓原本對的說法變錯、或丟掉資訊?** 沒有變錯。`SKILL.md` 第5步和 `06-代碼審與推送.md` 精簡成只指路,「分開提交」和「`rN-repro.txt`」只剩 `templates.md` 一處有,符合單源,不算丟失。
3. **有沒有帶進新問題?** 有,就是上面 C1(新加的步驟引用指錯)、C2(「完整」與遮罩的落差,HIT／MISS 語意)、C3(三點對兩欄)。

共 3 條,其中 major 0 條
