severity: major

這輪新寫的內容有 5 條 major、3 條 minor。「9 條驗收條款能不能寫成先紅的測試」這一項,我沒有跑實驗,只讀了 `lens-repo` 的 `scripts/test_lumos.py` 和 `scripts/hooks/claude/dispatch-lens-hook.py` 來判斷。我沒建暫存實驗目錄,沒有東西要刪。

## 做法 1(標記文法、圍欄與引用塊)

severity: major
blocking: 是 — 「寫歪」判定的範圍太寬,把正常的派工詞也整份擋下,審查席因此拿不到任何鏡頭。
引句:「一行裡出現 `LUMOS-REPO` 字樣卻不合上面的格式」
問題:判定只看「出現 `LUMOS-REPO` 字樣」。設計審的派工詞習慣整份貼進計劃全文,這份計劃本身就有很多行含這個字樣,例如「`LUMOS-REPO: <絕對路徑>`:單獨一行」和「派工詞照抄一行 `LUMOS-REPO: …`」。這些行不在圍欄或引用塊裡,整行又不合 `^LUMOS-REPO:` 格式,全會判成 `repo_malformed`。判成 `repo_malformed` 後「不算、只附說明」。計劃沒寫「寫歪」是否限於整行只含標記的行。圍欄規則也沒寫:`~~~` 圍欄、4 個以上反引號、縮排圍欄、沒關閉的圍欄(之後整份都略過還是都計入),以及 `>` 要不要先去掉前面的縮排,這些實作者都得猜。
失敗情境:在這個 repo 派一席審本計劃的設計審,派工詞貼了計劃全文並附 `LUMOS-SPEC:`。掛鉤在計劃正文的說明行上判 `repo_malformed`,該席沒拿到固定席節點。這個失敗在計劃自己的文字上就會踩到,之後每個討論這個功能的計劃都會踩。
佐證:``file: `scripts/hooks/claude/dispatch-lens-hook.py:178` ``(現有 `find_marker` 對每行 `strip()` 後整行比對,沒有「含字樣」這種寬判定可沿用)

## 做法 4(沒過:仍取角色卡與架構段)

severity: major
blocking: 是 — 計劃要掛鉤「用會談目錄叫一次 lumos 只取角色卡與架構段」,但 lumos 沒有這種呼叫方式,照字面做會拿到錯的 repo 的內容。
引句:「但仍用會談目錄叫一次 lumos 只取角色卡與架構段」
問題:`dispatch-lens` 沒有「只算角色與架構、跳過圖譜」的旗標。
- 角色段由 `_dispatch_lens_role_text` 對 `--repo` 目錄解析範圍後,對那個 repo 算 diff。範圍屬於目標 repo,在會談 repo 裡 sha 解析不到,角色段會是空字串,S8 的紅綠就看不出意義。
- 若範圍在兩個 repo 都存在,角色卡會用錯的 repo 算。
- 掛鉤收到 rc=0 時會把 `data["text"]`(會談 repo 算出的圖譜段)附上,那正是第 4 點要避免的「用錯的樹」。
- `--role-cards` 只在 `LUMOS-IMPACT` 那條路傳(`rng and wants_role_cards`),`LUMOS-SPEC` 路徑不傳角色旗標,所以 S8 對設計審路徑不成立,計劃沒講。
- 被拒路徑傳什麼 argv(要不要 `--deadline`、要不要吃 `text`)計劃沒定。
失敗情境:實作者只能自己決定新增 `--cards-only` 旗標,或直接丟掉 `text`,兩種做法驗收條款都沒綁。照字面做,錯樹的圖譜段會被當成成功附上。
佐證:``file: `scripts/lumos:48734` ``(`_dispatch_lens_role_text`);``file: `scripts/hooks/claude/dispatch-lens-hook.py:480` ``(`rng and wants_role_cards`);``file: `scripts/hooks/claude/dispatch-lens-hook.py:513` ``(rc=0 時取 `text` 附上)

## 做法 2(允許清單:工作樹)

severity: major
blocking: 是 — 會談目錄是工作樹時,「共用資料夾」要怎麼找沒寫;而且清單只涵蓋會談 repo 的工作樹,使用者原本的問題沒被涵蓋。
引句:「讀會談 repo 的 git 共用資料夾底下 `worktrees/*/gitdir` 檔」
問題:
- 全域規則要求每份工作開獨立工作樹,所以會談目錄常常就是工作樹。這時 `<會談>/.git` 是一個檔案。要找共用資料夾得先讀 `gitdir:`,再讀 `commondir`。計劃只在被廢棄的舊版做法 2 寫過這個流程,新版沒寫。
- 現有的 `_events_main_trusted(root, main_root)` 要呼叫端先給 `main_root`,並且直接拼 `main_root/.git/worktrees`。它是「給定 root 判可否信」,不是「列出清單」,也不處理 `.git` 是檔案的情形。照它寫會在會談是工作樹時整份清單落空。
- `gitdir` 檔內容是 `<工作樹>/.git`,允許清單要的是它的父目錄,計劃沒寫要取父目錄。
- 會談目錄若是 repo 的子資料夾、或根本不是 repo,怎麼辦計劃沒寫。「不在目標路徑跑任何 git」沒說會談目錄能不能跑,而 `git rev-parse --git-common-dir` 是最簡單的做法。
- 已被刪掉但記錄還在的工作樹(prunable)要不要排除也沒寫。
失敗情境:使用者的會談在 lumos 工具鏈,審的是另一個 repo 的工作樹。計劃寫的清單涵蓋的是「會談 repo」的工作樹,不是目標 repo 的,這個情境會被 `repo_not_registered` 擋下。
佐證:``file: `scripts/lumos:27051` ``(`_events_main_trusted`)

severity: major
blocking: 是 — 登記制登記的是專案根,沒說登記專案的其他工作樹算不算,而示範情境(目標專案的獨立工作樹)正是這個缺口。
引句:「把那個專案的根(realpath)追加進使用者層的 `~/.config/lumos/projects.txt`」
問題:`lumos init` 與 `lumos update` 的 root 是 `find_vault(Path.cwd())` 的上兩層,在工作樹裡跑就登記到那個工作樹。登記到的工作樹日後被 `git worktree remove`,清單裡留著不存在的路徑。反過來,在主 checkout 登記過的專案,它的新工作樹不在清單裡。允許清單的第一條只涵蓋「會談 repo」自己的工作樹,對目標專案沒有對應規則。
失敗情境:使用者的會談在 lumos 工具鏈,審 `Backend_improve` 專案的新工作樹。該專案主 checkout 早登記過,新工作樹卻不在清單裡,被拒;計劃的「在那個專案跑一次 `lumos update`」叫人到那個工作樹裡 update,下次換工作樹又被拒。
佐證:``file: `scripts/lumos:24307` ``(`cmd_update` 取 `vault.parent.parent`)

## 登記清單的寫入點

severity: major
blocking: 是 — 計劃指定 `install.sh` 要登記專案,但它沒有專案可登記;其餘寫入細節也沒定。
引句:「`lumos init`、`lumos update` 與 `install.sh` 跑完時,把那個專案的根(realpath)追加進」
問題:
- `install.sh` 只是 `exec ... scripts/lumos install --force` 的薄殼,裝的是全域 lumos 與使用者層 skills,不在任何專案裡跑。「那個專案的根」在 install 時不存在,實作者得猜:跳過、登記來源 repo、還是登記 cwd。
- `~/.config` 不存在時要不要建、建出的權限是什麼沒寫。
- `XDG_CONFIG_HOME` 沒提。`~/.config/lumos/projects.txt` 寫死,與 XDG 預設路徑只是巧合一致。
- 清單的「資料夾屬於自己、非 group/other 可寫」檢查要求的是「檔與它的資料夾」,但 `~/.config` 預設 umask 0755 沒問題,若建成 0775 就會被自己的檢查判成「當清單是空的」,導致每次都被拒。
- 寫入要原子還是 append 沒寫。
- 專案裡已有 `_trusted_private_dir(d, *rel_segments)`,同樣處理「家目錄底下的私有資料夾,逐層拒 symlink」。計劃的〈先找既有〉寫的是 `_trusted_lumos` 的 `_ok`,沒提這支,有重複造輪子與漏掉 symlink 檢查的風險。
- 登記失敗要不要擋 `init`/`update` 也沒寫。
失敗情境:實作者在 `install.sh` 一步卡住,只能憑猜決定,S7 只涵蓋 `init`/`update`,`install.sh` 與 `XDG_CONFIG_HOME` 沒有任何測試。
佐證:``file: `install.sh:63` ``;``file: `scripts/lumos:48003` ``(`_trusted_private_dir`)

## 驗收條款與測試搭法(HOME 暫存化)

severity: major
blocking: 是 — 計劃要把 `HOME` 指到暫存資料夾,但沒說掛鉤怎麼找得到 lumos,照寫會讓測試在掛鉤開頭就 `return 0`,綠燈是假的。
引句:「測試把 `HOME` 指到暫存資料夾(登記清單寫在那裡)」
問題:掛鉤的 `_trusted_lumos` 先用 `shutil.which("lumos")`,找不到就退到 `$LUMOS_HOME`,再退到 `Path.home()/harness/lumos-toolchain/scripts/lumos`。測試把 `HOME` 換掉後,在沒有全域 `lumos` 的 CI 上這個退路就落空,`_find_lumos_script` 回 None,掛鉤 `main()` 在跑 subprocess 之前直接 return 0。
- S1/S2/S3/S8/S9 都會因此以「沒附說明、沒附節點」的樣子出現,實作者可能把紅當成自己的 bug,或把綠當成成功。
- 計劃沒說要同時設 `LUMOS_HOME` 或 patch `_find_lumos_script`。
- 現有測試 `t_dispatch_lens_hook_fail_reason_notice` 就是靠真實 HOME 找到 lumos,另一個把 `HOME` 換掉的測試是 `lumos` 這邊的 `cmd_dispatch_lens` 單元測試(它不經掛鉤)。
- S1 要「用 `git worktree add` 造工作樹」並「算出固定席節點」,但計劃同時說測試用假的 `subprocess.run` 依 argv 分派、lumos 那次回 JSON。這樣只能驗 `--repo` 傳了什麼,驗不了「真的在那個工作樹算」,S1 的「掛鉤應在那個工作樹算」就只剩參數檢查,條款和測試搭法不一致。
- S7 兩個命令(init、update)共用一支測試名 `t_lumos_update_registers_project`,又只寫「跑完」,`install.sh` 沒有對應條款。
佐證:``file: `scripts/hooks/claude/dispatch-lens-hook.py:330` ``(`_trusted_lumos` 的 `Path.home()` 退路);``file: `scripts/test_lumos.py:42122` ``(現有掛鉤測試的搭法)

## 原因代碼的判定順序

severity: minor
blocking: 否 — 順序沒定只影響顯示哪個代碼,不會讓審查席拿到錯的樹;但測試條款要綁固定輸出,實作者得猜。
引句:「原因代碼是掛鉤自己的四個(`repo_not_absolute`、`repo_not_registered`、`repo_duplicate`、`repo_malformed`,每個一句固定話)」
問題:四個代碼同時成立時以哪個為準沒寫。例如兩行不同值而且其中一個是相對路徑,是 `repo_duplicate` 還是 `repo_not_absolute`?有 `- LUMOS-REPO:` 寫歪的行,同時另一行合格,算 `repo_malformed` 還是照合格的算?路徑含 NUL、讀不到、空字串各歸哪個?`repo_not_registered` 的說明叫人「在那個專案跑一次 `lumos update`」,但路徑根本不存在(`samefile` 丟例外)時這句話是誤導。
失敗情境:S2、S5 的測試只能憑猜測選期望值,日後改順序測試不會紅。
佐證:無(純文字規格缺口)

## 其餘小項

severity: minor
blocking: 否 — 用詞不一致,實作者可自行統一,但驗收時容易兩邊各讀成不同意思。
引句:「通過記 `repo_marker pass same_as_session=0|1`」
問題:`same_as_session` 比對的是「通過的路徑」對「會談目錄」。會談目錄若是 repo 的子資料夾,或標記路徑與會談 repo 工作樹根是同一個 repo 的不同寫法,結果為 0 還是 1 沒寫。RETIRE-IF 用的是「`LUMOS-REPO:` 都等於會談目錄」,這個欄位才是量測依據。
佐證:無

severity: minor
blocking: 否 — 會談目錄一律在允許清單裡的前提若不成立,只是多了一個被拒的特例,不是安全洞。
引句:「(會談目錄本身也在允許清單裡,寫了不會壞)」
問題:這句話只對「會談目錄是 repo 根」成立。會談目錄是子資料夾時,工作目錄 `samefile` 對不到根;會談目錄不是 repo 時更沒有條目。範本一律叫人寫 `LUMOS-REPO:`,這些會談在範本照做後反而被拒(`repo_not_registered`),比不寫更差。
佐證:無

做法 3(過了)、做法 6(預算)、做法 12(`-c core.fsmonitor=false`)已讀,無 finding。做法 12 補充一點:`_lens_git` 現有的 `-c` 只在 `quote=True` 時加,實作者要讓 fsmonitor 設定對所有呼叫都生效,這點計劃有寫「一律帶」,與現狀不衝突。

總結:最高等級 major,共 6 條 major finding,其中 6 條 blocking;另有 2 條 minor(non-blocking)。
