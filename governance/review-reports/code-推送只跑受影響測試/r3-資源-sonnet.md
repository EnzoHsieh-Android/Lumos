severity: minor

這輪修補只動了測試、一個內部變數名稱和說明文件。pre-push 的子程序處理、逾時、預算都沒動,不是這輪的變更面。

severity: minor
**
**blocking: 否**
測試成本:`t_prepush_feature_branch_mixed_with_main` 餘裕只剩 2 倍
引句:「r2, calls2 = push([("refs/heads/feat", head, "refs/heads/main", base)])」
`scripts/test_lumos.py:125880` 附近。這輪多加兩次真掛鉤推送,每次約 20 秒。
- 我在前景實測,最慢段 82.6 秒,上限 180 秒,輸出標 `⚠ 餘裕不足 3 倍`。
- 慢機器或磁碟忙時,超過約 2.2 倍就會撞上限,屆時是這支測試紅,不是掛鉤出錯。
- 作者在 `t_prepush_feature_branch_already_light` 的 docstring 裡已經拆過一次這種超時,這支現在是同樣處境。
- 歸因:有證據的修復回歸。修前只有一次混推,修後多兩次。查證命令是上面那條 `-k` 指令,只跑了修後;修前未量,未判定。
- 加兩次推送本身是合理的,守著「判主線看遠端 ref」這個必要行為。要降風險,可把 `main:feat` 與 `feat:main` 兩例拆成獨立測試。

**鏡頭回答**
1. **子程序殘留**:修補沒碰 pre-push 的程序管理。檔內仍有 EXIT 清暫存、INT/TERM/HUP 呼叫 `_pp_kill_jobs` 的 trap(`scripts/hooks/pre-push:339-344`、`957-958`)。測試端用 `_sp.run` 前景等待,沒有背景程序。我跑完測試後,`/tmp` 下沒有 `gctl-run` 殘留。
2. **時間預算**:掛鉤本身沒有新增逾時,只有測試的 180 秒上限(見上面那條)。
3. **大檔與二次方**:修補沒有新增讀大檔或巢狀迴圈。`_down` 改名只是字串。測試每次推送只做幾次 grep 和一次 python 取關鍵字。
4. **測試成本**:見上面那條 finding。
5. **pitfalls manifest**:這輪沒有內建題,不適用。
6. **圖譜鏡頭**:我沒有逐篇讀 8 個節點(沒跑 `lumos show`),原因是這輪修補面只有測試與變數更名,範圍太窄。
   - 逐篇判斷未做,也不宣稱這 8 篇的合約沒受影響。
   - 讀到的修補差異裡,`ARCHITECTURE.md` 與 `bound-tests-gate.md` 有文字更新,只改說明,沒動行為。

**三問**
- **原問題的修復效果**:本輪針對的「判主線看遠端 ref 而非本機分支名」,有 `feat:main` 與 `main:feat` 兩個對照案例,同一測試實跑 4 項全過。修前沒有這兩例,**修前行為未判定**。我沒另外做「把掛鉤改成看本機 ref,該例是否紅」的變異實驗,所以測試能不能抓到這種改壞,未驗。
- **相鄰路徑**:`_ppfb_harness` 回傳多了一個 `kg`,所有呼叫端都已改成 5 元素解包。`already_light` 改成直接用 `kg / "Systems" / "Home.md"`,沒有搜尋路徑的歧義。我沒有另外跑其他五支 `t_prepush_feature_branch_*`,這幾支未驗。
- **新發現的修前修後差異**:唯一發現是測試耗時,修前未量。

**未驗範圍**:其他五支 feature_branch 測試、變異實驗、固定席 8 篇節點。
