severity: minor

repair5-F1  
severity: minor  
blocking: 否  
引句:「回顧含孤立代理字元:--check 判型別不合格;retro-stats(含 --json)與 doctor 只標那一個、不炸。」  
觀察：測試宣稱壞回顧會被標出，但 `retro-stats` 只要求 rc 0、沒有 Traceback、輸出含健康迴圈 `cry`；完全沒要求壞迴圈 `crx` 存在且狀態為 `stale`。doctor 更只驗沒有 Traceback。FIFO 案例同樣只驗不卡住，未驗 `--check` 失敗或統計標成過期。  
判準：若實作捕捉讀檔錯誤後直接從 stats/doctor 隱去 `crx`，這些測試仍會通過，與 docstring 的「只標那一個」內部不一致。  
具體輸入路徑：`crx/cap-retro.json` 含 JSON 跳脫的孤立 surrogate，另有健康的 `cry`；或把 `crx/cap-retro.json` 換成 FIFO。錯誤實作可只輸出 `cry=recorded`、doctor 不列 `crx`。  
file: `scripts/test_lumos.py:72350`  
file: `scripts/test_lumos.py:72353`  
file: `scripts/test_lumos.py:72410`  
建議：明確斷言 `crx == stale`、`cry == recorded`、doctor 的跑滿回顧段含 `crx`；FIFO 的 `--check` 應非零且 stats 應標過期。  
修補候選：壞的 `crx` 必須可見且 fail-closed。保留候選：健康的 `cry` 仍須維持 recorded；兩者應分開斷言。  
命令未實跑：唯讀環境禁止建立自己的 temp；原始輸出如下，未以此冒稱翻紅：
```text
mktemp: mkdtemp failed on /tmp/repair5-review.J5zQHG: Operation not permitted
```
未能做 mutation 翻紅，因此按要求不升 major。

repair5-F2  
severity: minor  
blocking: 否  
引句:「提示不再印 `--template > 檔` 的重導向(照貼會先清空已寫好的回顧);--template --write 只在檔不存在時建。」  
觀察：手冊檢查包在 `if f.exists()`；任一 `_CR_MANUALS` 或 `templates.md` 被刪除、改名、漏進交付包時，該項零斷言而靜默略過。  
判準：此測試宣稱所有列出的手冊都不再教危險重導向，則「檔案存在」本身也是必要前置斷言，不能當可選項。  
具體輸入路徑：從臨時版本移除 `skills/lumos-code-loop/SKILL.md`，其餘程式與手冊維持原樣；目前迴圈會略過該檔，仍可能全綠。  
file: `scripts/test_lumos.py:72284`  
file: `scripts/test_lumos.py:72286`  
建議：先逐檔斷言存在，再讀取並驗證沒有 `--template >` 且含 `--template --write`。  
修補候選：移除舊的破壞性指令。保留候選：每份既有手冊仍存在且繼續提供安全的 `--template --write` 指令。  
命令未實跑；同一個 temp 建立步驟 rc 1，原始輸出：
```text
mktemp: mkdtemp failed on /tmp/repair5-review.J5zQHG: Operation not permitted
```

三問結論：

- 修復：未判定。選定 `t_cap_retro_template_write_no_clobber` 為修補候選，但指定 patch 只有測試，沒有可獨立歸因的實作 hunk；也沒有同案例載入 `f6787629…` 與 `95735eff…` 的實跑證據。
- 保留：未判定。選定「沒有人裁紀錄時既有七步處置閘判定不變」為保留候選；只有靜態測試碼，未取得兩版本、同 fixture、同預期的實跑結果。
- 新發現：2 條，皆為新增測試的假綠缺口；未證明當前產品行為已實際失敗，也不歸因其他共同變更。

固定合約逐條回答：

- design-loop `.md` 審材與條款綁定：指定 hunk 未直接修改實作；行為未實跑，未判定不影響。
- search 排除 superseded、不排 stale：未修改相關實作；未實跑，未判定。
- bound-tests fail-closed：未修改相關實作；未實跑，未判定。
- guard-kill rc 優先序：未修改相關實作；未實跑，未判定。
- guard-kill JSON 純度：未修改相關實作；未實跑，未判定。
- LICENSE/COPYING/NOTICE 不得進 vendored 清單：未修改相關實作；未實跑，未判定。
- `scripts/lumos` SPDX/MIT 與複製檔授權：未修改相關實作；未實跑，未判定。
- 修 bug 測試須有現場前置斷言：本片段新增大量測試，但 F1/F2 顯示部分承諾沒有被結果斷言完整釘住；無 mutation 實跑，整體未判定。

`r3-pitfalls.json` 沒有 claim 落在本片段新增來源行 71578–72506；未把 manifest 當成兩版本新增告警判定。`r3-test-layers.txt` 為空。

已讀材料：

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-segments/repair-5.patch`：937 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 個邏輯行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 必讀合計：1440 行；固定 HEAD 已核對為 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff`。

額外上下文：

- `AGENTS.md`：97 行。
- `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md`：70 行。
- `scripts/test_lumos.py` 定點展開：438 行，範圍為 155–178、446–485、9798–9822、34525–34562、34935–35085、37035–37062、71545–71585、72490–72535、74594–74638。
- 另有 `rg` 符號索引輸出，未展開完整巨型 CLI。

額外定點正文 438 行已超過 340 行上限；依派工規則，本席不能宣告全片收斂，未覆蓋角落與三問正向結論均維持未判定，應拆新席重新限額覆核。

最高級：minor  
阻擋數：0  
三問未判定範圍：實作修復是否成立、既有行為是否保留、未讀角落是否另有回歸；均缺同案例兩版本來源與實跑證據。