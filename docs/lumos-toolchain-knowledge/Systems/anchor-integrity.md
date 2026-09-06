---
type: system
status: done
created: 2026-07-02
updated: 2026-07-28
self_audit: sonnet/2026-08-21
about_code_stamp: batch-2026-08-23/2026-08-23/be1575ecbbcb
tags:
  - type/system
  - status/done
  - risk/守衛面
verified_by:
  - "[[Verification/2026-07-02_anchor-integrity]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-09-03_派工鏡頭注入驗收]]"
  - "[[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]"
summary: |-
  FLOW:anchor approve --note→6錨點(runner×2+git hooks×3+claude hook×1:dispatch-lens-hook.py,2026-09-03 新類別「會改寫子代理輸入的 hook」) sha256→anchor-baseline.json(checked-in)+治理帳 anchor-approve 事件｜anchor verify→逐錨點比對→mismatch/缺檔 rc1(pre-push 擋、自主 loop 每輪入口硬擋含 missing baseline)
  KEY:守「驗證器本身被悄悄改成一律通過」——測試綠/hook 放行的前提(批改程式沒被動過)從盲信變成可機械核對宣稱;外部實證=八大評測被 conftest 鉤子破
  KEY:刻意不守 scripts/lumos 本體(天天迭代→盲簽疲勞);分層=baseline 守驗證器、測試守被驗物
  KEY:loop 入口比 pre-push 嚴——missing baseline 視同失敗(無人看顧無人眼兜底);pre-push 維持 rc0+警示(漸進採用)
  KEY:[2026-07-28]調研 gap 候選(arXiv 2607.05743:「檢查時刻vs使用時刻」分離=agent 執行安全通病)——anchor verify 在 pre-push 本機驗、測試實跑在稍後雲端 CI,中間空窗無人看;候選解=CI 端跑測試前自算受護檔雜湊寫入該次執行紀錄、放行時比對「當時真正跑的是哪一版把關程式」;未排程(與既有天花板「真解留 future CI」同向,此為具體形狀)
  KEY:誠實天花板——同 repo 守衛悖論:決意繞過者可連守衛一起改;買到的是無痕篡改被封死(必留 baseline diff/缺 approve 事件/bypass 軌跡其一),非不可繞。baseline 自身無自我保護(手改 json 靠對帳抓,v1 人工);core.hooksPath 一行可指走整個 hooks 層(loop 入口 shell 直呼=第二條路,真解留 future CI)
  DEP:[[lumos-refcheck]](vault-free 同型)｜_append_governance_log(寫者宣稱已改:doctor --ci + anchor approve)
  TEST:t_anchor 14 checks(無 baseline 警示/approve 建檔+留痕/gov 顯示 note/改檔+缺檔 rc1/--json/重簽容缺/repo 解析 rc2)
  VERIFY:[[2026-07-02_anchor-integrity]]
decisions:
  - content: 方案 A baseline hash+顯式 approve;否決 RHB 環境硬化(方案 B)與純 diff 標記送審(方案 C)
    id: d1
    context: 本機單人工作流沒有 agent 摸不到的執行面,硬寫隔離=自欺;marker 對 agent 零成本自貼、無內容 hash 底線
    why_chosen: 機械、確定性、零依賴;無痕篡改被封死到只剩「連守衛一起改」,人 review 有明確紅旗;B 留 future 真 CI(baseline 屆時直接複用)
    decided: 2026-07-02
    valid: true
  - content: 錨點集合 v1 固定列舉 5 檔,不含 scripts/lumos 本體
    id: d2
    context: lumos 是自主 loop 天天迭代對象,收進 baseline=每天 approve→盲簽疲勞,守衛立刻形同虛設
    why_chosen: 分層——baseline 守驗證器(runner+hooks),測試守被驗物(lumos 行為);改壞 lumos 由 test_lumos.py 抓,前提「runner 沒被動」正是 baseline 守的
    decided: 2026-07-02
    valid: true
about_code:
  - governance/autonomous-loop.sh
  - scripts/hooks/pre-push
  - scripts/lumos
related:
  - "[[Projects/派工鏡頭注入_計劃]]"
---
# anchor-integrity

`lumos anchor verify/approve`——**錨點完整性守衛**(vault-free):測試 runner 與把關 hooks 的 sha256 baseline + 顯式 approve 留痕。

## 動機
方法論最底層退路「CI 跑真測試、綠才算數」把測試結果當不可造假真值,但 runner/評分器本身可被悄悄改寫(外部實證:八大權威評測被 conftest 鉤子全破)。lumos 自主 loop 的 agent 摸得到整個 repo,同樣風險。

## 接線
- `scripts/hooks/pre-push`:環境檢查後、vault 閘門前(repo 層,無 vault 也跑);rc1 擋 push,訊息三選一(還原/approve/--no-verify 留痕)。
- `governance/autonomous-loop.sh`:每輪 gap 派 orchestrator 前(污染可能發生在當天中途);errexit-safe;missing baseline 硬擋。
- 改錨點的合法路徑=`lumos anchor approve --note`(重算寫回 + 治理帳 `anchor-approve` 事件,note 進 `lumos gov` 顯示)。

## 相關
- 設計稿:`docs/design/2026-07-02-anchor-integrity.md`(design-loop 3 輪、R1 missed 作廢、R2+R3 收斂;qwen endorsed;辯方 4 次全駁倒假 major)。
- 實作計畫:`docs/superpowers/plans/2026-07-02-anchor-integrity.md`。

## 第六個錨點(2026-09-03,新類別)

`scripts/hooks/claude/dispatch-lens-hook.py` 是第一支被錨的 Claude Code hook。理由:它用 `updatedInput` 改寫子代理的派工詞,與提示注入技術同構、差別只在善意——[[Verification/2026-09-03_派工攔截點實測]] 定為硬約束。其餘四支 claude hook 只注入上下文、改不了輸入,維持不錨。★錨點只罩 repo 裡那份★,`lumos install` 複製到 `~/.claude/hooks/` 的副本在機制外(能改家目錄的人本來就能做任何事)。`ANCHOR_FILES` 與 baseline 鍵集合由 `t_anchor_files_match_baseline` 交叉互證(之前兩者從無測試互證)。

## ★簽名檔本身沒提交,是這道守衛的天生破口(2026-09-06 實際被 CI 咬到)★

**發生什麼**:折完一輪代碼審要推,推送前的閘擋我「把關檔改過沒簽名」。我簽了名、也把改動提交了——但只提交了知識庫那個資料夾,而**簽名檔放在治理資料夾底下**,沒進去。推送過了,CI 紅。

**為什麼會這樣**:兩道閘看的東西不一樣。

- 推送前的那道拿**工作目錄現在的樣子**驗:你剛簽完名,檔案就在那裡,所以綠。
- CI 拿**已經推上去的內容**驗:簽名檔沒進版控,推上去的還是舊的,對不起來,所以紅。

**最坑的地方**:CI 的錯誤訊息會叫你「重新核可並留理由」——照做也沒用,因為問題根本不是沒簽名,是簽了沒提交。訊息把人指向錯的方向,而這種紅燈又特別像「守衛壞了」。

**怎麼修的**:推送前的閘多一道——簽名檔如果處在「改過但沒提交」的狀態就擋下,訊息直接講「沒提交」並給提交指令,不叫人再簽一次。守衛配的是**行為測試不是字串比對**:真的搭一個小 repo、真的把簽名檔弄髒、真的跑那支 hook;而且反向驗過——把這道擋拿掉,兩條斷言翻紅。

## ★清單從 6 個變 10 個,而且多一條「集合要相等」(2026-09-07)★

**發現什麼**:這道守衛原本只逐條比對「清單裡有的檔」。而版控裡 `scripts/hooks` 底下有 8 個檔,清單只列 4 個——**另外四支會自動執行的 hook,內容被改了、或偷偷多一支,守衛一句話都不說**。

四支補進清單(進場提醒、改檔前推合約、收工查圖譜、推送後回報 CI),並加一條:**清單裡的 hook 檔集合,必須等於實際存在的 hook 檔集合**。偷加一支會被點名。

**★這條買到什麼、沒買到什麼——要講清楚,不然會被當成防線★**

- **買到**:「無聲新增/刪除一支 hook」變成**必留一種痕跡**。
- **沒買到**:它不是防線。真正的攻擊者在你 checkout 的那一刻,那支碼**就已經跑過了**。防那一刀的是另一件事——hook 不執行你手邊資料夾裡的碼(見 [[Systems/hook信任邊界]])。

**做的時候踩到一個,值得記**:集合檢查第一版拿版控清單當真相來源,但逐檔比對那半看的是檔案系統。**兩個來源混用會互相打架**——「hook 檔存在但沒 git add」時會誤報成「登記過但檔案不在了」。改成都看檔案系統,而且這樣才對:**沒進版控的 hook 照樣會自動跑,它才是這條要盯的東西**。
