severity: minor

**①提示注入**

已看,無。新寫進帳的分支名(`ref` 欄位)只在讀取端做字串相等比對(新碼 `ref != name`),不進任何給 AI 的派工詞、hook 附加段或指令。新增的 stderr 說明只印筆數與常數 `_REDBASE_ANC_CAP`,沒有回顯分支名或 `head_sha`。我另外找了別處讀 `d.get("ref")` 的地方:`scripts/lumos:24548` 讀的是簽核帳,`scripts/lumos:16968` 讀的是 verdict 紀錄,都不是規格閘留痕的 `ref`,也沒有把它當成 git ref 去用。`_gate_event_build` 的 `ref` 本來就會原樣進 JSON(`scripts/lumos:1619`),`json.dumps` 會跳脫,沒有換行注入。

**②讀寫與執行越界**

已看,無。

- git 命令注入:餵給 `merge-base --is-ancestor` 與 `cat-file -e` 的 `sha` 都先過 `_LENS_SHA_RE.fullmatch`(只收 40 或 64 位十六進位)才進命令。帳本欄位寫成以 `-` 開頭或帶 `;` 的字串,進不了這兩個 git 呼叫。命令用 list 形式,沒有 shell 插值(`scripts/lumos:65221`)。
- 路徑:新碼不新增任何寫檔,只讀帳與跑 git 讀取命令。
- 新測試的 uploadpack 腳本:`remote.origin.uploadpack` 只設在 `pc` 這個測試用複製上。腳本、記號檔 `gbf-fetched`、`gbf-shallow`、`gbf-partial` 都放在 `d.parent`。`d` 來自 `mkvault().parent.parent / tag`,而 `mkvault` 用 `tempfile.mkdtemp(prefix="gctl-test-")` 建私有目錄(`scripts/test_lumos.py:183`)。所以腳本與記號都在測試自己的私有暫存內,不碰共用 `/tmp`,也沒有可預測的共用路徑可被搶先放符號連結。腳本內容是 `touch '<記號>'` 加 `exit 1`,路徑來自 mkdtemp,不含外來字串。腳本只在 `pc` 內由 git 在查不到的提交上呼叫;測試最後也斷言新碼沒有去連遠端。
- 密鑰與信箱:沒有新增。`t@t` 是既有測試慣例的假值。
- 另一個可能的洞:有一個 git 的設定若被改寫,git 讀取命令可能去連遠端或跑程式。這個洞要靠有人改 `.git/config` 才成立,而這在「打開陌生 repo 時 git 本身就會讀它」這條既有基線上,沒有因本次 diff 變大,所以不報。

**③非刻意、一步就能繞過的守衛**

1. 治理帳被 git 忽略時,壓提交或 rebase 之後,自己這條分支的判綠紀錄被丟掉,紅燈版存成實作後的內容。
severity: minor
blocking: 否
   - 誰:使用者本人或照常操作的 AI。
   - 從哪:先跑一次規格閘讓測試判綠,留下帶 `head_sha` 的判綠紀錄;之後一個平常的 `git commit --amend`、`git rebase -i` 壓提交或 `rebase main`。
   - 送什麼:改寫後的 HEAD。判綠時的 `head_sha` 不再是祖先,`_redbase_on_branch` 在完整 repo 判成 False 並丟棄。
   - 拿到什麼:這支測試之後再跑出紅時,「判綠過就不存紅燈版」的守衛被意外走過,紅燈版存成實作後的測試內容。推送時 `tq/redbase-weakened` 就拿這份已改過的版本當基準,比對力道變弱。
   - 備註:這是計劃「做法 1」刻意接受的取捨,並已寫進 `_TG_LIMITS` 與使用說明的「抓不到」清單,只在帳被忽略時發生,影響的是作弊偵測強度。依範圍規則,不列 blocker。
   - 引句:「治理帳被 git 忽略的專案,壓過或 rebase 過的分支上舊的判綠紀錄不算」

2. 部分複製只靠 `extensions.partialClone` 判斷;缺這個設定而有承諾遠端(promisor)的 repo 會被當成完整 repo。
severity: minor
blocking: 否
   - 推論:寫不出完整的攻擊路徑,所以標推論。照一般 `git clone --filter` 或 `git fetch --filter`,git 會同時寫 `extensions.partialClone` 與 `remote.<名>.promisor`,正常操作走不到這個缺口。只有手改 `.git/config` 只留 `remote.*.promisor=true`,而沒有 extension 那行時,對本機沒有的 `head_sha` 做 `merge-base` 或 `cat-file` 才會自動連遠端。要有人先動 `.git/config`,而那本來就能直接設 `core.fsmonitor` 之類執行程式,所以沒有新的攻擊面。
   - 縱深防禦:判祖先的子程序可以帶 `GIT_NO_LAZY_FETCH=1`,或改成「`remote.*.promisor` 任一為 true 也當部分複製」。
   - 引句:「pc = _lens_git_dl(rr, "config", "--get", "extensions.partialClone", deadline=deadline)」

最嚴重等級是 minor,blocking 共 0 條。
