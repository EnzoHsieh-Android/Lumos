severity: major

# r1 資源併發-sonnet(鏡頭:資源、併發、時序、中途失敗)

白話:這份設計把「收工作樹」全押在 finally 上,但「被殺」才是這個指令最常見的結局(跑 5–15 分鐘,對話裡的工具逾時只有 2–10 分鐘);被殺時 finally 不跑,垃圾與孤兒測試會留下,而且沒有任何掃殘骸的機制。另外「驗的是哪個提交」在長時間執行中沒有被鎖住。

實驗環境:`git clone --shared` 出來的 repo(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/fg-r1-work-資源併發-sonnet/repo`),只跑 `-k` 小測試與自寫探針,未跑全套。

## F1 行程被殺(SIGTERM/SIGKILL/工具逾時)時 finally 不跑,工作樹與 `.git/worktrees` 登記殘留,設計沒有掃殘骸
severity: major
blocking: 是
引句:「放在 finally 裡一定收;主工作目錄不動」
file: `scripts/lumos:14202`(`tempfile.mkdtemp(prefix="lumos-kill-")`)與 `scripts/lumos:14311-14321`(guard kill 的 finally 收法);全檔 grep 無 `signal.signal`、`atexit`,也沒有掃 `lumos-kill-*` 殘骸的程式
1. 「一定收」只對正常結束與 Python 例外成立。Python 預設收到 SIGTERM 直接死,不跑 finally;SIGKILL 更不用說。編排者在對話裡跑 `lumos loop fix-check`,工具逾時(預設 120 秒、上限 600 秒)被殺是設計自己估的時間(2–10 分鐘、再加受波及合約約 4 分鐘)下的常態。
2. 實測(未改任何 repo 檔):自寫探針仿 guard kill 的收法(mkdtemp → `git worktree add --detach` → finally 裡 `worktree remove --force`、rmtree、`prune`),跑 4 秒後送 SIGTERM。結果 rc=-15,`git -C repo worktree list` 多出一行 `…/T/fgprobe2-xxxx/wt  (detached HEAD)`,`$TMPDIR/fgprobe2-xxxx` 目錄還在(整個 209MB 級的檢出;本 repo 檢出一次約 209MB、2 秒)。
3. 一次 fix-check 開兩個樹,被殺一次就留約 420MB 加兩筆 `.git/worktrees/<名>`;重複被殺會累積。guard kill 自己也有同樣缺口,但它是人手動跑、不會每輪都撞;fix-check 是每輪派下一輪前必跑,被殺機率高很多。
4. 設計的條款 S4 只驗正常結束後 `git worktree list` 沒殘留,沒有任何「被殺後下次跑要回收」的條款;「實務隱患」節也沒提。下次 fix-check 起跑時沒有「先掃 `lumos-fixcheck-*` 與孤兒 worktree」的步驟,殘骸只能靠人。
5. 另外,被殺時治理帳事件在「跑完逐項驗之後」才寫(〈記帳與跳過〉),所以被殺這件事在帳上完全看不見:`gov --stats` 的耗時與跳過比例會少算最慢、最容易被殺的那幾輪,偏向樂觀(RETIRE-IF 的「耗時中位數超過 15 分鐘」是用這本帳判的)。

## F2 Ctrl-C 時測試子行程是孤兒:`_kill_run` 開新 session,終端的 SIGINT 到不了它,finally 又把它的工作目錄刪掉
severity: major
blocking: 是
引句:「跑測試時把 `TMPDIR` 指到修正關卡自己的暫存資料夾,跟工作樹一起刪」
file: `scripts/lumos:13976-14000`(`_kill_run`:`Popen(..., start_new_session=True)`,只在 `TimeoutExpired` 才 `killpg`,沒有 `KeyboardInterrupt` 處理)
1. 設計「照 guard kill」,測試經 `_kill_run` 跑。它用 `start_new_session=True`,所以終端 Ctrl-C 只送給 lumos 本體,測試行程組留著。
2. 實測:探針 import `_kill_run` 跑 `sleep 77`,另一支 driver 對探針送 SIGINT:探針 rc=-2,traceback 停在 `Popen.wait`;之後 `pgrep -fl "sleep 77"` 仍看到 `sleep 77`。也就是 lumos 退出、finally 把工作樹與 TMPDIR 刪了,測試行程還活著。
3. 後果:孤兒測試在已被 `worktree remove --force` 刪掉的目錄裡繼續跑(可能重建檔案,讓 rmtree 後又長出半個目錄),或繼續佔 CPU 與 `TMPDIR` 底下的檔;「TMPDIR 跟工作樹一起刪」這句假設測試已經停了,被中斷時不成立。若是紅那邊(base 的測試檔疊到舊樹)的測試卡住,孤兒甚至拖到整台機器變慢。
4. 設計要求的 finally 因此需要「先殺行程組、等它真的死、再刪樹」的順序,這在設計裡沒有;只寫「逾時」會 killpg,「被中斷」沒寫。

## F3 第 2 步的時間預算超過對話裡能跑的上限,而且「2–10 分鐘」只對第 1 步成立
severity: major
blocking: 是
引句:「第 2 步殺傷力重跑每個測試指令先跑一次 baseline(逾時上限 600 秒)再每條配方各跑一次」
file: `.lumos/config.json:1-10`(本專案 run_cmd = `{python} scripts/test_lumos.py -k {method}`);實測 `-k t_gov_stats_gate_drift` 2.6 秒、`-k stop_block` 2.7 秒、worktree 檢出 2.0 秒
1. 第 1 步的估計站得住:每支測試(含匯入整支 3 萬行測試檔)約 3 秒,3–10 支 × 兩邊 ≈ 20–60 秒,兩個樹檢出 ≈ 4 秒,時間主要是受波及合約約 4 分鐘(設計自己引的 59 支)。
2. 第 2 步:壓力指令預設逾時 300 秒、每條都跑;殺傷力重跑的 baseline 逾時上限 600 秒、每條配方再跑一次。任何一項吃到上限,單次 fix-check 就超過 10 分鐘;三項疊加可到 20 分鐘以上。對話裡的 Bash 工具上限 10 分鐘,專案規則(CLAUDE.md)也明寫超過十分鐘的測試不在對話裡跑、交給閘與 CI。
3. 設計沒有:整次的總時間上限、分段(先紅後綠 / 合約 / 壓力 / 殺傷力)可單獨重跑的旗標、或「放背景跑並讀結果」的用法。於是第 2 步上線後編排者要嘛 10 分鐘被殺(落入 F1 殘骸)、要嘛用 `LUMOS_SKIP_FIX_CHECK=1` 跳過(RETIRE-IF 的「跳過比例超過三成」會被這個設計自己推高)。
4. 此外 `loop next` 的提醒只認 `passed` 事件(sha256 對得上);被殺沒有事件,所以編排者被提醒要跑、跑不完、又不能留下「跑到哪」,等於每次重頭來。

## F4 長時間執行中「現在的提交」沒有被釘住:合約測試在主工作目錄真跑數分鐘,中途被別的會談改檔或提交,事件記的 head 與實際驗的不同
severity: major
blocking: 是
引句:「修正提交不另記欄位:`fix-check` 驗的就是跑的當下那個提交,治理帳記它。」
file: `scripts/lumos:1147-1175`(`_gate_event_build`:`head_sha` 沒給時由 `_gate_event` 在寫帳那一刻 `rev-parse HEAD`;見 `scripts/lumos:1190-1215`)、`scripts/lumos:38606-38660`(`_run_bound_tests` 在傳入的 repo 根真跑,沒有鎖樹)
1. 先決條件只在開頭檢查一次「沒有未提交的程式與測試改動」。接著先紅後綠兩個樹用 `base` 與「現在的提交」建,這兩個是起跑時解析的 sha;第 5 項卻是在主工作目錄真跑——整個跑約 4 分鐘以上。全域 CLAUDE.md 與記憶都說同一個 repo 常有別的 Claude 會談同時在做事,這 4 分鐘內別人改檔、`git checkout`、`git commit` 都會發生。
2. 結果:第 5 項驗到的是「先紅後綠驗的那個提交 + 別人當下的未提交改動」的混合物,不是「跑的當下那個提交」。設計的說法「驗的就是跑的當下那個提交」就此不成立,而它還以此為由不記提交欄位。
3. 治理帳事件的 `head_sha` 由寫帳那一刻的 HEAD 決定(約在 5 分鐘之後),不是起跑時驗的那個 sha。起跑後 HEAD 若被別的會談移動,事件會把「通過」記在一個沒被驗過的提交上。`loop next` 的提醒又只比對修正紀錄 sha256(不比對提交),所以同一份修正紀錄通過一次後,之後再動程式(同一輪補折一條晚到的發現)也不再提醒。這在只提醒的階段是漏提醒;設計寫的「轉成擋」會直接沿用這個比對,就變成放錯。
4. 設計要補:起跑時 `rev-parse HEAD` 一次、整次都用這個 sha(合約測試也該在第三個工作樹或同一個「現在」的樹跑,或結束時再比一次 HEAD 與 `git status`,變了就作廢重跑);事件 `extra` 加 `verified_head`,`loop next` 比對要連同它。

## F5 `-k {method}` 是子字串比對:先紅那邊會被同前綴的兄弟測試誤判成紅
severity: major
blocking: 是
引句:「非 0 結束,而且 `_ran_count` 讀得到跑了至少一支、沒有全被跳過 → 紅,過;」
file: `scripts/test_lumos.py:31909-31910`(`tests = [t for t in tests if _args.keyword in t.__name__]`);`.lumos/config.json:5`(run_cmd);實測 `-k t_gov_stats_gate_drift` 輸出 `5 passed`
1. 本 repo 的 run_cmd 是 `… -k {method}`,而 runner 用 `keyword in t.__name__` 篩。一支測試名通常是別支的前綴(實測:一個測試名篩出 5 支)。
2. 場景:紀錄寫 `t_foo`,同一次修正還新寫了 `t_foo_edge`(沒登進紀錄,或也在紀錄裡但在 base 疊上的新測試檔中對舊程式必紅)。先紅那邊 `-k t_foo` 跑到兩支;`t_foo` 在 base 本來就會綠、`t_foo_edge` 紅 → 整體非 0、`_ran_count`=2 → 判「紅,過」。而 `t_foo` 其實沒守住這次問題,這正是先紅關要抓的「修之前就通過」,被漏掉。
3. 反向也成立:綠那邊兄弟測試紅會把紀錄裡本身綠的測試判不過,錯誤訊息還指向錯的測試名。
4. 設計寫了「去重」但去的是紀錄裡的測試名,不是實際跑到的測試集合。要嘛 run_cmd 對 python profile 要求精確名(例如 runner 增加完整比對旗標、或在輸出裡驗跑到的名單恰為所指),要嘛先紅關改看「該測試名」的逐支結果而不是整體退出碼。未實測整條 fix-check(尚未實作),依據是上述 runner 讀碼加單一名稱篩出多支的實驗。

## 實務隱患逐類(資源、併發、時序、中途失敗)

- 兩個會談同時跑 fix-check:已讀、已實測,無 finding。`mkdtemp` 名稱唯一;8 路並行 `git worktree add --detach <各自目錄>/wt HEAD`(目錄尾巴都叫 `wt`)全數成功,git 自動編成 `wt`…`wt7`,無互撞。fix-check 與 guard kill 同時跑同理(它們的樹各自獨立);但 `git worktree prune` 在別人樹「已刪目錄、未 remove」的瞬間沒有搶佔問題,也不會誤傷尚在的樹。
- 測試在樹裡跑的寫入面:已讀,無 finding。測試檔用 `Path(GRAPHCTL).resolve().parent.parent` 定位自己的 repo,所以 `.lumos/test-cache*.json` 寫進樹自己的 `.lumos/`(`.gitignore:30` 已忽略),樹刪了就沒了;`__pycache__` 同樣在樹內(`.gitignore:2`);runner 的 `gctl-run-` 根在 `TMPDIR` 下,設計讓 TMPDIR 隨樹刪是對的(前提見 F2)。第 5 項在主工作目錄跑則會更新主目錄的 `.lumos/test-cache.json`——這是推送前閘本來就有的行為,不是新風險。
- 治理帳併發追加:已讀,無 finding。`_gate_event` 以 `open(..., "a")` 單次寫一行,同機並行追加不會撕裂;`docs/.governance-log.jsonl` 在 git 追蹤中,工作目錄常是 modified,不影響先決條件(帳本不是程式檔)。
- 讀端成本:已實測,無 finding。16.1MB、10.1 萬行的治理帳,以字串預篩 `"fix-check"` 掃一遍 0.10 秒、全量 `json.loads` 0.27 秒;`lumos loop next` 整體啟動約 0.7 秒。預篩做法合理,`loop next` 不會明顯變慢;帳本長到十倍才需要再看。
- 磁碟滿:`_gate_event_or_warn` 寫不進會在 stderr 講一句、不改判定(`scripts/lumos:1234-1243`),夠用。建樹時磁碟滿會讓 `git worktree add` 失敗,設計沒寫「建第二個樹失敗時第一個要收」——但若確實把兩個樹的建立都放在同一個 try/finally 內就會收;屬實作細節,不另列。
- 時間預算:第 1 步 2–10 分鐘合理(見 F3 第 1 點);第 2 步不合理(F3)。

最高等級:major,blocking 共 5 條
