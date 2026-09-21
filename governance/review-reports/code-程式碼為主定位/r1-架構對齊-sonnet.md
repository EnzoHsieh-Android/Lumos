severity: major

## F1 新版「先讀程式碼」入口規矩沒同步進 SessionStart hook 與 lumos-project-notes skill,同一次對話會同時收到兩套互斥的「第一步」指示

severity: major
blocking: yes

觀察到什麼:這批把 `scripts/templates/graph-discipline.md`(單一來源,注入 CLAUDE.md/AGENTS.md)的核心規矩從「第一個工具呼叫是 lumos,不是 grep」整段改成「先讀程式碼、系統會主動推筆記給你」,並且把舊版結尾那兩行「不確定該敲哪個指令 → 讀索引:`lumos-project-notes` skill 的 `commands/INDEX.md`」整段刪掉、沒有替代。但同一套「入口規矩」還有兩份獨立的字面副本,這批完全沒動:

引句:「1. **先讀程式碼**：自己讀懂現況、得出改法，照程式實際的行為寫。」

這是新版 CLAUDE.md/AGENTS.md/graph-discipline.md 三份都改成的第一條。但:

- `scripts/hooks/claude/lumos-entry-hook.py:286` 這個 SessionStart hook,**每次開新對話都會印**:「本專案用 lumos 知識圖譜。動既有系統的第一個工具呼叫是 lumos search / context,不是 grep / Read」——原字面保留,完全沒改。
- `skills/lumos-project-notes/commands/INDEX.md:42`「三條不變的規矩」第一條:「任何任務的第一個工具呼叫是 `lumos`(search 或 context),不是 grep / Read / Explore。」
- `skills/lumos-project-notes/commands/01-進場查脈絡.md:3`:「規矩:**第一個工具呼叫就是這裡的指令**,grep/Read 是之後印證用。」

怎麼重現:任何裝了這套紀律的專案,開一個新 Claude session。輸入=SessionStart hook 觸發、CLAUDE.md 被當 system prompt 注入。輸出=同一輪脈絡裡同時出現「先讀程式碼」(CLAUDE.md 正文)與「第一個工具呼叫必須是 lumos,不是 grep/Read」(hook 注入的 additionalContext)兩條字面互斥的「第一步」指示;如果之後又觸發 `lumos-project-notes` skill(CLAUDE.md 自己的 skill 觸發表就指到它),裡面的 INDEX.md/01-進場查脈絡.md 再重申一次舊規矩。三處在同一個決策點上互相矛盾,agent 該先做哪件事沒有唯一答案。

為什麼是 bug 而不是風格偏好:這正是本專案自己歷史記錄過、判定為「問題」的同一種形狀——`docs/lumos-toolchain-knowledge/Systems/slim-install-安裝器.md` 記過 Task 9 的裁定:「兩套規則並存本身是問題……接手者的 Claude 會先讀到它、照著撲空」,當時的處置是整段替換、不留並存。這批只改了三份檔案裡的其中一份「來源」文字,卻漏了同一層(agent 操作規矩)另外兩處獨立硬編的字面副本,造成的正是同一種「兩套規則並存」的架構問題重演一次,而且其中一份(SessionStart hook)是機械保證每次對話都會被印出來的,不是「可能被讀到」而是「一定被讀到」。這會讓 agent 的實際行為在「查圖譜優先」與「讀 code 優先」之間漂移,不是措辭好不好看的問題。

---

## F2 兩篇新開的 Projects 計劃筆記缺 `lands_in`,送進處置閘會直接 FAIL(不是理論上、已機械重現)

severity: major
blocking: yes

觀察到什麼:這批新增兩篇 `type: project`、`status: doing` 的計劃筆記:

引句:「+type: project」
引句:「+status: doing」

(`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 與 `docs/lumos-toolchain-knowledge/Projects/審查評測集_計劃.md` 的新增 frontmatter 各自逐字都有這兩行;兩篇皆同形狀)兩篇 frontmatter 全文都沒有 `lands_in:` 欄位。CLAUDE.md 鐵則 5 本身就寫明「計劃寫 `lands_in`(現況落在哪幾篇或新開哪一篇)」,而且這不是沒人守的軟規矩——`scripts/lumos` 的 `_disposal_landing_step`([S21],`scripts/lumos:16998-17040`)是處置閘機械檢查的第六步,`type: project` 且在 Projects/ 底下、首筆審查帳晚於 2026-09-12 的計劃,`lands_in` 空的一律 FAIL。同層對照:同一批(2026-09-17~18)新開的其他計劃筆記 `雙向門放行_計劃.md`、`規格落成可驗收條件_計劃.md`、`收工點名問版本控制_計劃.md`、`逃逸自動記_計劃.md` **全部**有 `lands_in:` 欄位,這兩篇是最近一批裡唯二缺的。

怎麼重現(已在 `/tmp/seat-架構對齊-sonnet` 唯讀 worktree 實跑,非推測):對這批凍結內容裡真實提交的 `docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md`,用 `lumos canary record none` 造一筆最小審查帳(loop id `repro-lands-in-check`),再跑:

```
python3 scripts/lumos loop status repro-lands-in-check --disposal --spec docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md --repo .
```

輸出:

```
[disposal] 落點: ✗ — 計劃沒寫 lands_in(現況會寫進哪幾篇、或新開哪一篇);節點長成一篇包全部,就是因為落點從來沒被審過
    lumos append <計劃> lands_in Systems/<名>
⛔ DISPOSAL GATE FAIL (repro-lands-in-check 輪 r1: 落點)
```

rc=1,其餘六步(G3 hash、處置集合、留痕、quote-check、canary 觀測、條款綁定)全部 ✓ 或 skip,只有「落點」這一步 FAIL,拖垮整個處置閘判定。

為什麼是 bug 而不是風格偏好:這不是「筆記寫得不夠漂亮」,是繞過了本專案自己為「每支檔有家 / 計劃要交代落點」立的既有寫入口(`lumos append <計劃> lands_in Systems/<名>`)——鐵則 5 明講計劃筆記要用這個欄位交代「現況落在哪幾篇」,機械閘也真的照這個欄位判,同層對照的四篇最近計劃筆記全部照做,只有這批新開的兩篇沒有。這兩篇本身就在計劃筆記正文裡記了大量「這一批已改、尚未提交」「續接順序」之類需要走完整 design-loop 才會收斂的內容,照本專案自己的鐵則,這正是該走處置閘的東西,現在卻會被自己的閘擋下。

---

## 已驗過但判斷乾淨的路徑

- `governance/autonomous_loop/replay_weekly.py` 的 `FULL_SWEEP_SECONDS` 常數寫法(模組層具名常數、行內註解交代由來與退場)跟同層 `governance/autonomous_loop/lens_weekly.py`(`--budget` 預設值、註解引用 replay_weekly 的 BUDGET_SECONDS)、`backlog.py`(`INIT_SCORE` 模組常數)慣例一致,不是新的第二種做法。全庫 grep 過 `FULL_SWEEP_SECONDS`/「夠快就全」/60 秒門檻相關字串,確認沒有第二份沒同步的門檻邏輯拷貝。
- `governance/eval/review-evalset/{README.md,v1.json}` 的形狀(README.md + 版本化 json)跟同目錄 `governance/eval/hook-intercept/`、`governance/eval/lens-utilization/` 既有子目錄慣例一致。
- `governance/eval/ablation_lumos_first.py` 沒有重刻 `RULE_HEAD`/`RULE_END`/`strip_lumos_first_rule` 的判斷邏輯,而是 `sys.path.insert` 後直接 `from scenario_probe import LIMIT_RE, LUMOS_CALL_RE`,單一實作來源守住,這批沒有在這裡引入第二份實作。
- `Systems/autonomous-iteration-loop.md` 新加的 `responsibility:` 欄位、`about_code` 新增一行,格式跟同批其他六篇已用 `responsibility:` 欄位的 Systems 節點(`多詞評測.md`、`記憶過期清掃.md`、`每支檔有家.md`、`規格閘.md`)一致;`replay_weekly.py` 沒有被其他節點同時列為 about_code(單一家,不衝突)。
