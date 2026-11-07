severity: major

審的是第 2 版 r2-snapshot.md。對照的程式碼是 `scripts/test_lumos.py` 的 `main()` 與 `_fanout_wanted`、`scripts/hooks/pre-push`、`scripts/lumos` 的合約測試閘。全程沒有跑任何測試,只讀碼與 grep。

## F1 `--lf` 沒有大小上限,也沒有「選完再判」,紀錄一大就退成全套
severity: major
blocking: 是(`--lf` 是第 2 版新開的豁免出口,而且正好卡在本席被要求檢查的位置;要讓 `--lf` 在任何狀況都不退成全套才算做完)
spec 段落:範圍、做 2 與做 5;驗收條款 S5。
問題:
- 做 2 的「選完再判」只列了關鍵字與 `--suite keys`,沒有 `--lf`。
- 做 1 又把 `args.lf` 當成「有帶條件」。所以 `--lf` 一帶就同時繞過兩道門。
- 「上次紅過」紀錄是執行器既有的 `.lumos/test-cache*.json`,每次執行都會覆寫。
  - 大面積紅(沙盒壞掉、環境問題)時,`failed` 可以列上千支甚至近全部。
  - 此時 `--lf` 等於全套,而且是單一程序跑,不會切片。
- spec 只定義「沒有紀錄回 2」,其餘兩種情況沒定義:
  - 紀錄存在但名字全是已刪除的測試:`tests` 變成 0 支。現有程式只有「帶 `-k` 而 0 支」才判紅,所以 `--lf` 會印「0 案例」並放行,疑似假綠 ⚠。
  - 紀錄是 `failed: []`(上次全綠):是算「沒有紀錄」,還是退成全套,spec 沒說。
  - 紀錄檔壞掉:`except (OSError, ValueError): pass` 把它吞成空串列,效果同上,要靠實作剛好寫成 rc 2。
- S5 只測「紅 2 支」與「完全沒紀錄」兩種,這兩種之外的邊界都沒釘。
引句:「沒有紀錄時印一行並回 2,不退成全套」
引句:「關鍵字篩選或 `--suite keys` 選完之後,選中支數超過全部測試的三成就擋」
佐證:
- file: `scripts/test_lumos.py:49745-49752` 讀 `test-cache*.json` 時用 `+=` 合併,沒有筆數上限,讀壞了就靜默吞掉。
- file: `scripts/test_lumos.py:49803-49806` 只對 `-k` 選中 0 支判紅。
- 建議:把 `--lf` 併進選完再判的同一條規則(超過三成就擋)。紀錄為空、全過期、讀壞都明確回 2。S5 補這三案。

## F2 `-k t_ --shard i/4` 輪流跑四片,每片都在三成以內,合起來就是全套
severity: major
blocking: 是(順手寫出「大半全套」的路徑,而且 CI 重現片的正當寫法會在同一處被誤擋或誤放)
spec 段落:做 1 與做 2;S3;天花板 4。
問題:
- 現有 `main()` 先做分片切割、後做 `-k` 篩選。做 2「接在測試清單篩選完」,此時 `tests` 已經是分片後的一片。
- 分母「全部測試」是切片前還是切片後,spec 沒寫。
  - 分母取切片前:`-k t_ --shard 1/4` 選中約 25%,不擋。連跑四次就是全套,每次約 2 分鐘,正好壓在工具上限邊緣。
  - 分母取切片後:正當的 `-k foo --shard 1/4` 反而可能被誤擋。
- 天花板 4 只提「多個關鍵字各跑一次」,沒提「分片輪流」。
- S1 的「只帶 `--shard`」擋得住,但 `--shard` 配任何關鍵字就變成豁免。
引句:「選中三成以內但很大的子集(例:多個關鍵字各跑一次)擋不到」
佐證:
- file: `scripts/test_lumos.py:49700-49740` 分片在上,`if _args.keyword:` 在 `49775` 附近,篩選順序確認。
- 建議:
  - 對話裡把 `--shard` 也當「要被量」的旗標,分母固定取切片前的全部測試數。
  - 或對話裡配了 `--shard` 就一律走逃生門。

## F3 三成的門檻不等於時間,spec 自己舉的證據就反駁了它
severity: minor
blocking: 否(不會讓全套溜過,但三成的設計目的沒達成)
spec 段落:做 2。
問題:
- 選中支數 ≤ 30% 約等於 1100 支以上。`-k` 路徑不切片,單一程序跑,仍會超過 spec 開頭自己說的「對話工具上限」。
- 支數與秒數不成比例:`_docs_suite_select` 註解寫過一支測試最慢 136 秒,209 支要 234 秒。
- 擋下訊息把 `--suite docs` 當成建議指令列出來,但 spec 自己承認它「約四分鐘」,也超過對話上限。
- `--suite docs` 在對話裡不分改動類型都能用,對想多跑的 AI 就是一條合法的大子集。
引句:「`--suite docs`(文件子集,約兩百支、約四分鐘)不套這條」
佐證:file: `scripts/test_lumos.py:49656-49660` 是 `--suite docs` 的說明。
建議:門檻改看預估秒數(耗時表已存在),或至少把 `--suite docs` 與大子集寫進天花板。

## F4 逃生門的名稱沒印,但只要讀一次執行器原始碼就知道,理由 10 字隨手湊得出
severity: minor
blocking: 否(天花板 2 已承認可設環境變數,並留下理由與計數;這裡補的是「不印名字」並未達成隱藏)
spec 段落:做 4、做 6;天花板 2。
問題:
- 擋下後 AI 的下一步通常是讀 `test_lumos.py` 找擋的來源,`LUMOS_ALLOW_FULL_SUITE` 就在原始碼和圖譜筆記裡。
- 只驗「去空白後 10 字」,「為了驗證全套是否通過」就過。
- RETIRE-IF 用「逃生門放行次數超過擋下次數」判成敗,但被繞過的情況會讓逃生門次數變多,守衛反而被撤掉。這個度量在被繞過時方向相反。
引句:「**訊息不印逃生門的變數名**,逃生門只寫在 [[Systems/測試執行器]]。」
佐證:
- file: `scripts/test_lumos.py:49391-49400` 的 `_FANOUT_CHILD_ENV` 同型常數都明寫在原始碼裡。
- 建議:RETIRE-IF 改成看「放行理由是否真的對應 CI 重現等正當情境」,不只看次數比。

## F5 直接手跑推送前掛鉤會帶出 `LUMOS_PUSH_ATTEMPT`,全套被整套豁免,天花板沒列
severity: major
blocking: 是(全域 CLAUDE.md 要求「推送前跑完專案的推送前掛鉤」,所以這是 AI 自然會做的動作,不是刻意偽造)
spec 段落:做 1 的豁免、不做最後一條、天花板 2 與 5。
問題:
- `scripts/hooks/pre-push` 在跑測試前就 export `LUMOS_PUSH_ATTEMPT`。
- AI 在對話裡「為了預檢」直接呼叫 hook 腳本,就會用豁免身分拿到分片全套,不經過逃生門,也不留紀錄。
- spec 只談 `git push` 觸發的閘,以及手設環境變數(刻意偽造)。直接呼叫 hook 這條路沒被分類。
- ⚠ 我沒有真的跑 hook,所以不確定 hook 在沒有 stdin 的 ref 列表時是否提早退出。這需要實作端確認。
引句:「不擋對話裡 `git push` 觸發的推送前閘全套:那是規定的跑法」
佐證:file: `scripts/hooks/pre-push:393` 的 `export LUMOS_PUSH_ATTEMPT=...` 在 hook 前段就設定。
建議:把「直接呼叫 hook」寫進天花板,並確認 hook 在無 stdin 時是否提早結束。或讓豁免多驗一個 `GIT_*` 環境變數(只有真的 git push 才有,但 `main()` 開頭會把它們清掉,所以要在清之前判斷)。

## F6 擋下訊息與 pre-push 提示在消費專案裡指向永遠失敗的 `--lf`
severity: minor
blocking: 否(誤導但不會繞過)
spec 段落:做 4、做 5。
問題:
- 現有程式只在 `_is_src` 為真(來源 repo)時才讀寫 `.lumos/test-cache*.json`。
- 消費專案裡 `--lf` 永遠「沒有紀錄」回 2,但擋下訊息仍把它列為可用指令。
- spec 的「消費專案」隱患只說會被擋,沒提這個。
引句:「消費專案**:測試總檔會被安裝進消費專案(工具自裝檔),那邊在對話裡不帶條件跑也會被擋」
佐證:file: `scripts/test_lumos.py:49740-49746`,`_is_src` 判斷。
建議:訊息在非來源 repo 時省略 `--lf`。

## F7 `--list` 與選完再判的先後沒定義
severity: minor
blocking: 否
spec 段落:做 2、做 3。
問題:`--list -k t_` 是查詢,不跑測試;但做 2「接在測試清單篩選完、開始跑之前」若放在 `--list` 之前,會把純查詢誤擋。現有程式的 `--list` 在 `49775` 附近的篩選後立刻 return,中間沒有可插「選完再判」的位置,實作者得自己選。
引句:「第 2 條接在測試清單篩選完、開始跑之前」
建議:明寫「`--list` 不套選完再判」,並補一案。

## 固定席逐條判

以下節點的牽連檔都只有 `scripts/scenario_probe.py`,本案只動 `scripts/test_lumos.py` 與 pre-push 的兩行提示,對它們都不影響。

- `Systems/codex-harness`:不影響。`scenario_probe.py` 原本就在開巢狀 Claude 前拿掉 `CLAUDECODE`,本案沒有改它。
- `Systems/測試假綠形態`(★INVARIANT★):不影響。該條要求還原翻紅釘搭配前置斷言;S4 的前置(拿掉 `CLAUDECODE` 時回 None)符合,但 F1 的「0 案例放行」疑似是新的假綠形態,值得補一案。
- `Systems/bound-tests-gate`(★INVARIANT★):不影響。合約測試閘用 `.lumos/config.json` 的 `{python} scripts/test_lumos.py -k {method}` 逐支跑,過濾探針用不存在的假名,兩者都帶 `-k` 且選中很少,不會被擋。見 file: `scripts/lumos:72737-72800`。
- `Systems/lumos-cli-lifecycle`、`lumos-cli-read`:不影響。它們不呼叫測試執行器。
- `Systems/design-loop`、`canary-audit`:不影響。它們不呼叫測試執行器。
- `Systems/guard-kill`(★INVARIANT★):不影響。guard kill 與合約測試閘共用同一個 `run_cmd`,帶 `-k`,不碰擋下判斷。

## 實務隱患鏡頭

- 對話裡正當用法被擋:
  - `lumos` 自己起執行器都帶 `-k`,不受影響。
  - CI 片重現(`--shard 2/4`)被擋,走逃生門;見 F2。
  - 推送前閘紅了之後的補救改成 `--lf -x`;見 F1 與 F6。
- 繞過路徑:F1、F2、F5。
- 天花板完整性:缺 F2(分片輪流)、F5(直接呼叫 hook)、F1(`--lf` 紀錄)三條。

總結:最高等級為 major,blocking 共 3 條。
