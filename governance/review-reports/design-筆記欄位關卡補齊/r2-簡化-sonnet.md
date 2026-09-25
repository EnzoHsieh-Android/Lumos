severity: blocker

## F1 S10 沒寫 cutoff,現存違規不是 10 篇是至少 141 篇,S12 過不了

`做法`第四節與 FACT 摘要都以「現存違規只有 10 篇」為前提(這正是 r1 用來否決「比上一版」複雜設計、改成「一律有違規就擋、當次修掉」的關鍵理由)。但這個 10 篇裡的 9 篇計劃,其實是用了摘要 FACT 行裡才出現的隱藏篩選條件「09-11 起建」:

引句:「09-11 起建、檔名以「_計劃」結尾卻沒寫落點 9 篇」

而條款 S10 本身完全沒有這個時間篩選,是對「所有」`_計劃`筆記一視同仁:

引句:「若名稱以「_計劃」結尾的專案筆記沒有 lands_in,或其中一項不是」

我機械數了一次(`docs/lumos-toolchain-knowledge/Projects/*_計劃.md`,frontmatter 沒有 `lands_in` 鍵):不分建立日期共 141 篇缺 lands_in,只有 9 篇是 `created >= 2026-09-11`。也就是說,若照 S10 字面實作(沒有 cutoff),這次改動要處理的不是文件裡講的 10 篇,而是至少 141 篇(還沒算「有 lands_in 但格式錯或指到不存在節點」的那些,只多不少)。

這會讓 S12 直接過不了:

引句:「當這次改動完成,本 repo 圖譜的每一篇筆記都應通過 lint」

同一批 141 篇裡的其餘 132 篇(例如 `docs/lumos-toolchain-knowledge/Projects/panel收斂判準改革_計劃.md`、`docs/lumos-toolchain-knowledge/Projects/工具分類_計劃.md` 等,machine 核對詳見上段)沒有出現在「四、同一次改動修掉現存的 10 篇違規」清單裡,S10 上線當下就會讓它們全部推送/CI 紅燈。

要嘛(a)把 S10 明文加上跟 `_ALIASES_CUTOFF`/`_ENUM_CUTOFF`(`scripts/lumos:4849`、`4869`)同款的 created-cutoff,並在做法與條款都寫清楚是哪一天、為什麼;要嘛(b)老實承認要修的是 141 篇不是 9 篇,重算「同一次改動」範圍。兩條路都會動搖 r1「現存違規只有 10 篇,直接修掉比較簡單」這個否決複雜設計的核心理由——這正是簡化鏡頭要抓的:少寫的那個 cutoff,本身就是一塊被藏起來的複雜度。

severity: blocker
blocking: yes

## 已讀、無 finding 的部分

- 推送前「筆記格式」段擋不擋看 `note_lint.gate`、看不懂當 warn(跟 `node_home.gate` 看不懂當 on 刻意不同)——查過 `scripts/lumos:21442-21444`,現有 `node_home.gate` 看不懂確實是退回 `on`,спec 這句「以程式碼為準」的對照沒問題。
- 「S9 about_code 要在版控索引裡,已加進提交但還沒提交的算」——查過 `_about_code_path`(`scripts/lumos:13652`)現在只驗磁碟 `is_file()`,不驗索引,跟摘要說的「寫入指令刻意維持只驗磁碟」一致;`git ls-files` 本來就含已 add 未 commit 的檔,S9 描述可行。
- 「推送前健檢讀的是工作目錄,這是健檢所有段落共同的限制」——查過 `run_doctor`(`scripts/lumos:995`)呼叫 `_nodehome_config` 沒帶 `from_snapshot=True`,doctor 本體確實讀工作目錄;快照式讀法(`from_snapshot=True`,`scripts/lumos:21400-21422`)只在獨立的「每支檔有家」推送前檢查指令裡用,不是 doctor 這條路徑,新段落沿用 doctor 既有限制、沒有比既有段落更差,不是新洞。
- 「S5 帶碰到清單跑,筆記格式段結果不變,且預告合約逾期段全擋不受影響」——查過 CI(`.github/workflows/ci.yml:97`)不帶 `--touched-from`、只有 pre-push 帶(`scripts/hooks/pre-push:179`),CI 全擋行為本來就不吃 touched list,S5 這句站得住。
- S11 responsibility 最短字數——查過 `cmd_set`/`_cmd_set_locked`(`scripts/lumos:13569`)目前對 `responsibility` 沒有任何長度檢查,只有 `cmd_new`(`scripts/lumos:15052`)在新開節點時呼叫 `_nodehome_resp_ok`,S11 描述屬實,而且可以直接重用同一支 helper,不必另寫一套——這正是簡化鏡頭想看到的重用,沒有可再砍的東西。
- 日期只擋加引號(S7 對照現況)——查過 `RULE3_RE`/相關 lint 行(`scripts/lumos:302`)現在只抓「日期加引號」,不驗格式,跟摘要說法一致。
- decisions `valid` 現在寫 no/0 會被當有效(S8 對照現況)——查過多處 `str(d.get("valid","true")).lower() != "false"` 的判法(如 `scripts/lumos:1816`),任何非字面 "false" 的值都算有效,跟摘要說法一致。
- lands_in 格式檢查（`Systems/<名>` 純字串、不帶 `.md`）與設計審落點那一步共用同一支 `_lands_in_bad`（`scripts/lumos:17910`)——這段重用沒問題;但「指到存在的節點」這半句跟設計審落點那一步**不是**同一套判法(見 F1 之外的補充:落點那一步 `_disposal_landing_step` 在 `scripts/lumos:17966-17967` 對不存在的節點是標「(新開)」直接判 ✓,不會擋,S10 卻要求存在才過)——因為已經合併進 F1 的論述裡,這裡不另開一條,只在此註記查證來源。
- lands_in 節點連結 `Systems/lumos-cli-write`、`Systems/lumos-cli-read` 存在(spec 自己的落點)——`ls` 確認兩篇都在。

---
最嚴重 severity:blocker;blocking 共 1 條。
