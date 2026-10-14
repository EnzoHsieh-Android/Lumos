severity: major

整合面共 9 條 finding,其中 2 條 blocking。我沒建任何實驗檔,所以沒有暫存要刪。

**已讀,無 finding 的節**
- 舊計劃那條「不選」WHY 行照舊成立,推翻字樣不用收回。
  - 舊計劃的 WHY 行維持原文,`LUMOS-REPO` 與 `LUMOS-SPEC` 在 lens-repo(含 docs/、skills/、scripts/、codex-harness、hook信任邊界、design-loop)裡沒有任何「推翻」「被取代」字樣。
  - r1 當時規劃要標作廢,但沒落地。
  - 只剩本計劃自己的審計紀錄有殘留(見 F9)。
- 計劃的 PRIOR-ART 說「代碼審已經是這樣」屬實:`skills/lumos-design-loop/templates.md:109` 與 `skills/lumos-code-loop/SKILL.md:32` 都要求寫完整提交編號、不寫 HEAD。

severity: major
blocking: 是 — 要一起改的說法沒列全,留下幾份各自講舊版的指令手冊
引句:「`lumos-design-loop` 的 `templates.md` 在 `LUMOS-SPEC:` 那一行旁邊寫明」
問題:r1 版的做法 8 把要改的地方列全了(SKILL、reference、05、06、project-notes reference、design-loop 節點、掛鉤 FAIL_NOTE 與檔頭)。現在的做法 4 縮成只改 `templates.md` 一處,但 `LUMOS-SPEC` 在 lens-repo 的出現處遠不止這裡。
- 以下幾處照舊只寫 `<計劃筆記.md>`,或明講「從工作樹讀」:
  - `skills/lumos-design-loop/SKILL.md:26`
  - `skills/lumos-design-loop/reference.md:513`
  - `skills/lumos-project-notes/reference.md:83`
  - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:31`
  - `docs/lumos-toolchain-knowledge/Systems/design-loop.md:52`
  - `skills/lumos-design-loop/templates.md:335`(§7.6 架構席那格)
- `scripts/lumos` 裡還有兩處:`--spec` 的 argparse 說明「從工作樹讀」(53069 行),以及 `cmd_dispatch_lens_spec` 的 docstring。
- 掛鉤檔頭(`scripts/hooks/claude/dispatch-lens-hook.py:1-19`)寫「其餘判斷全在 lumos 端」,`FAIL_NOTE` 也只講範圍。
- 還有一處計劃完全沒列:`Systems/codex-harness.md:42` 的 WHY 行逐一列舉六個 `lens_fail` 代碼。r1 計劃原本要補,這版沒了,但 `lands_in` 還留著 codex-harness。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:29` 目前說的是代碼審,可能不用改。
具體失敗情境:編排者照 SKILL.md 步驟 3 派席,只會寫 `LUMOS-SPEC: <計劃筆記.md>`,不知道有提交編號寫法;下一個 session 的 AI 讀 05 指令表也學到「從工作樹讀」。新機制上線後仍沒人用,RETIRE-IF 的 8 週零使用條件會自己觸發。這正是「散落同步要守衛」那條老問題。
佐證:file: `skills/lumos-design-loop/SKILL.md:26`、file: `scripts/lumos:53069`、file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:42`

severity: major
blocking: 是 — 做法 1 說掛鉤不解析,做法 3 與 5 卻要掛鉤分辨寫法,與掛鉤薄殼的既有裁定衝突
引句:「只把值原樣交給 lumos;掛鉤自己不解析、不跑 git。」
問題:同一份計劃的做法 3 要求「值不是提交編號寫法時」才加繞法,做法 5 要求「用到提交編號寫法時」才記 `spec_rev`。掛鉤得自己判斷值是不是 7–40 碼十六進位加冒號,等於在掛鉤複製一份文法。
- 掛鉤檔頭與 `Projects/派工鏡頭注入_計劃` 的既有裁定是「hook 只做三件事,其餘全住 lumos」,`scripts/lumos:48750` 附近的註解也引用了這條。
- 兩邊各一份正規式,日後只改一邊就會分歧。
- 正解是讓 lumos 在 JSON 裡帶欄位(例如 `spec_rev: true`,或把失敗代碼分成「提交寫法的 spec_missing」與「路徑寫法的 spec_missing」),掛鉤只查表。計劃沒這樣寫,S3 與 S6 的測試也沒覆蓋。
具體失敗情境:實作者照做法 3 在掛鉤加正規式;日後 lumos 放寬到 40 碼以外(例如 sha256 的 64 碼),掛鉤沒跟著改,提交寫法被當成路徑,說明行亂給「先提交」繞法,事件記帳也漏記。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:8-14`、file: `scripts/hooks/claude/dispatch-lens-hook.py:250-264`(`_fail_note` 只認 `rng`)

severity: minor
blocking: 否 — 代碼表與事件記帳的措辭互相矛盾,實作時才會撞到,不影響方向
引句:「提交裡沒有這個路徑 `spec_missing`(沿用)」
問題:有三處說法對不上現況。
- `spec_missing`、`spec_outside_repo`、`no_knowledge` 不是「沿用」。掛鉤的 `LENS_FAIL_REASONS` 只有六個範圍類代碼,`cmd_dispatch_lens_spec` 失敗時只印 stderr、rc 2 或 3,不印 `lens_fail`。同一段括號又自己說「現在不印」,前後矛盾。
- `scripts/lumos:48753` 的 docstring 與 48756 行的「六個」,以及測試 `t_dispatch_lens_fail_reason_json` / `t_dispatch_lens_hook_fail_reason_notice`(`scripts/test_lumos.py:42070`、42123 起)都要跟著改。
- 做法 3 讓工作樹路徑的設計審失敗也會附說明行,`_fail_note` 現行會 `_mark("error", …)`,事件 kind 從 ok 變 error。這與 S6「沒用到這個寫法時 note 跟現在一樣」、S3「行為應與現在相同」衝突。計劃也沒寫提交寫法失敗時 kind 該用 ok 還是 error(r1 版曾明寫被拒用 ok)。
具體失敗情境:實作者照 S3 保持行為不變,工作樹路徑失敗就不附說明;照做法 3 又得附。測試寫法分歧後,必有一條紅。
佐證:file: `scripts/lumos:48752-48760`、file: `scripts/hooks/claude/_hookevent.py:111-125`

severity: minor
blocking: 否 — lands_in 有缺漏也有殘留,不擋方向,但違反「改到的每支檔的家要列」
引句:「Systems/hook信任邊界」
問題:`lands_in` 對不上這次的改動。
- `Systems/hook信任邊界` 是 r1 加信任機制時留下的。現在計劃自己說「不新增信任機制」,這篇的 about_code 雖有 `scripts/lumos`,內容卻是 `_trusted_lumos` 的找法,與讀提交無關。
- 計劃要改 `skills/lumos-design-loop/templates.md`,它的家是 `Systems/每輪修補差異派工`(about_code 列了它),不在 `lands_in`。專案鐵則 5 要求「改了程式要寫說明就寫進改到那支檔的家」。
- `Systems/design-loop.md:52` 講 `LUMOS-SPEC` 落點,若手冊要同步也該列。
- 計劃本文沒有 `decisions:` 或 `WHY:` 行。「不讓派工詞指定 repo、改走提交編號」的否決理由只在散文裡;鐵則 2 要求用 `lumos decision-add` 記,而且這正是下一個 AI 最需要的「被否決的方案」。
具體失敗情境:實作時 pre-commit 發現 `templates.md` 的家沒被計劃指到,或處置閘第六步的落點看起來不對。三輪後有人想重提 `LUMOS-REPO`,圖譜裡查不到結構化的否決紀錄。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md`(about_code 列 templates.md)

severity: minor
blocking: 否 — 做法 2 對現況的兩句描述不實,實作時才會發現
引句:「路徑先做跟工作樹那條路相同的檢查:不得含 `..` 段、不得是絕對路徑、要在 `docs/*-knowledge/` 底下」
問題:`cmd_dispatch_lens_spec` 的工作樹路徑現行做法是接受絕對路徑,只檢查 resolve 後在 repo 內;既有測試正是這樣(`scripts/test_lumos.py:41610`、41627 起),沒有「要在 `docs/*-knowledge/`」的限制,也沒有 `..` 段檢查。「跟工作樹那條路相同」不成立。上限也一樣:計劃說「跟工作樹那條路的上限同值」,但工作樹路徑是無上限的 `read_text`。
具體失敗情境:實作者把新檢查也加到工作樹路徑,舊測試(絕對路徑、非 knowledge 目錄的計劃)紅;或不加,兩條路的規則不一致卻被計劃說成相同。
佐證:file: `scripts/lumos:48999-49025`

severity: minor
blocking: 否 — 「先提交」被當成既有慣例其實沒有出處,而且沒防範用到舊輪的提交
引句:「不讀工作樹裡沒提交的改動(凍結快照本來就要先提交)」
問題:設計迴圈手冊裡找不到「派工前先提交計劃」的規定。`SKILL.md:57` 只說 gate PASS 之後卷證 commit,範本給席的是 `/tmp/<id>-rN.md` 工作副本。所以提交編號寫法會新增一個強制步驟,而且計劃沒有驗證那個提交裡的計劃內容與這一輪凍結快照(`--reviewed` 的 sha256)是同一份。
具體失敗情境:r3 折完沒提交,編排者沿用 r2 的提交編號貼進 `LUMOS-SPEC`。鏡頭用 r2 版計劃算固定席,漏掉 r3 新加的檔,席位看起來「附了節點」,實際是舊的。附加段加印前 12 碼只說明版本,不攔錯版。
佐證:file: `skills/lumos-design-loop/SKILL.md:26`、file: `skills/lumos-design-loop/SKILL.md:57`

severity: minor
blocking: 否 — Codex 編排的影響沒講清楚,範圍外的決定本身合理
引句:「Codex 編排的 `--arm` 不在範圍內。」
問題:`--arm` 只收 `<base>..<head>` 範圍,`dispatch-lens` 對設計審的 `--spec` 沒有武裝路徑;Codex 當編排者時,派工訊息對掛鉤是密文,設計審本來就拿不到任何 `LUMOS-SPEC` 鏡頭。所以這個決定不新增問題。
- 但做法 4 的範本指示是無條件的:Codex 編排者照範本寫提交編號寫法,什麼也不會發生,而且不會有說明行。
- r1 版曾要求範本標明「只對 Claude 編排有效」,這版沒有。
- `Systems/codex-harness` 的「天生限制」第 2 點(派工訊息密文)是它的家,但做法沒提要補一句。
具體失敗情境:Codex 編排的設計迴圈照新範本做,以為補了跨工作樹的鏡頭,實際跟以前一樣什麼都沒附,也沒人知道。
佐證:file: `skills/lumos-design-loop/templates.md:122-124`、file: `scripts/lumos:53475`

severity: minor
blocking: 否 — 分支新節點只列名,怎麼判、怎麼讀沒講清楚,「主線」一詞也不準
引句:「計劃直接連結的節點照現在從會談 repo 的圖譜讀」
問題:現行 `linked` 是用工作樹 `is_file` 判節點存不存在;節點只在分支上新開、會談樹沒有時,現況會直接被丟掉。
- 計劃說要「列名並標主線還沒有這篇」,但沒說怎麼從那個提交知道連結到的節點存在。要用 `cat-file -e <提交>:<vault>/<節點>.md`,還要保證 S4 的 rc 0。
- 「主線」其實是會談 repo 目前的 HEAD,不一定是 main。
- 兩邊都有但內容不同的節點(分支改過的 Systems)一律讀會談樹的舊版,席位看到的合約行可能與計劃要審的版本不同。
- 目標架構段也一樣,宣告與節點讀會談 repo 的 HEAD。
具體失敗情境:計劃新開 `Systems/新節點` 並自己 `[[連結]]`。實作者沿用 `linked` 邏輯,S4 的節點被靜默略掉,測試只能靠新增判斷才紅;措辭上又誤把會談分支當主線。
佐證:file: `scripts/lumos:49047-49052`、file: `scripts/lumos:49137-49156`

severity: minor
blocking: 否 — 審計紀錄殘留與目前決策相反的句子,下個 AI 讀了會誤判
引句:「舊裁定兩處加會談 codex-harness 標作廢」
問題:`審計修正紀錄` 的 r1 前掃那一行,寫的是「舊裁定兩處加會談 codex-harness 標作廢」;r1 那行還寫「舊裁定照字面作廢會把還有效的決策一起作廢」與「只作廢被推翻的那一格」。本計劃現在是「不推翻舊裁定」,這幾句不是被後續覆蓋,而是仍躺在計劃裡,讀的人會以為還要去標作廢。r2 那行只講「整類拿掉」,沒明講這幾個動作都撤銷。
具體失敗情境:實作者讀到 r1 紀錄,去把舊計劃的 WHY 行標成 `[status:superseded]`,與「舊裁定照舊成立」相反。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭跨repo不再靜默_計劃.md:16`(WHY 行目前沒有作廢標記,這樣才對)

最高等級 major,blocking 共 2 條(F1 範本與手冊沒列全、F2 掛鉤自述不解析卻要分辨寫法)。
