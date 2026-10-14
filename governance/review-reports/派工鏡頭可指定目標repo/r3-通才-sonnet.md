severity: major

## 1. 提交編號怎麼取、跟凍結快照沒有綁在一起

severity: major
blocking: 是 — 折入之後計劃變了,舊提交編號仍然通過,席位拿到的固定席節點對的是過期版本,而且沒有任何訊號。
引句:「先把計劃提交,寫 `LUMOS-SPEC: <完整提交編號>:<計劃路徑>`」
問題:計劃只說「寫完整提交編號」,沒說編排者怎麼取得。設計審的流程是把工作樹上的計劃複製成 rN-snapshot.md、派席、折入、再提交。固定席節點卻是從提交裡的那份算的。快照與提交裡的 blob 之間沒有任何綁定:lumos 不印 blob 雜湊,範本不要求兩者相同,dispatch.json 也不記提交編號。
具體失敗情境:
- 第 1 輪提交 A,折入後計劃改了,第 2 輪編排者沿用 A,或在會談目錄跑 `git rev-parse HEAD` 拿到主工作樹的提交。lumos 會成功算出節點,席位審的卻是快照。
- 計劃把一個新檔加進範圍,固定席卻看不到它。「附加段開頭加印提交編號前 12 碼」對席位沒用,因為席位不知道期望值。
建議做法:
- 讓快照直接由 `git show <sha>:<path> > rN-snapshot.md` 產生,兩者就不可能不一致。
- 在 rN-dispatch.json 記下提交編號。
- 讓 lumos 在輸出裡印 blob 的 sha。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/skills/lumos-design-loop/templates.md:40` ``(現行範本只叫人「原樣留一行」,沒有取編號的步驟)。

## 2. 沒提交的計劃不支援,但流程原本不要求先提交,更好的退路也沒考慮

severity: major
blocking: 是 — 前提寫錯,而且強制先提交會與提交前檢查衝突;計劃也沒有評估能避開這兩件事的做法。
引句:「不讀工作樹裡沒提交的改動(凍結快照本來就要先提交)」
問題:設計審現行是先複製快照、派席、折入,最後才提交,所以「凍結快照本來就要先提交」不是現行事實。這條會把流程改成每輪派工前都要提交一次。草稿計劃在這一步會遇到:
- pre-commit 的 lint 與「改 code 沒動圖譜」檢查;
- 錨點簽名;
- 專案規則不准 `--no-verify`,記憶裡也有這條。
每輪還會多一個 WIP 提交,最後得壓回一個。
更好的退路:
- 用暫存 index 做「不上分支的提交」:`GIT_INDEX_FILE=tmp git add <計劃> && git write-tree && git commit-tree`。結果是不經過任何 hook、不動分支、也不污染歷史的懸空提交,物件庫共用,會談目錄讀得到。
- 做成 `lumos` 的一個子命令,編排者拿到的編號就是 40 碼,同時解掉第 1 條。
- 另一個選項是只讀檔案、不跑 git:從 `git worktree list` 比對出已註冊的工作樹,用名字而不是任意路徑去讀計劃檔。
懸空提交約兩週後才會被 gc,而設計審的迴圈只跑一晚,時間夠用。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/skills/lumos-design-loop/SKILL.md:26` ``(派工詞與凍結快照的現行順序)。

## 3. 接受 7–40 碼,與代碼審那條路的完整提交編號不一致

severity: minor
blocking: 否 — 多半會失敗成 `spec_rev_missing`,不是靜默錯;但規則本身不一致。
引句:「是 7–40 碼十六進位,冒號後是 repo 根起算的相對路徑、不以 `/` 開頭」
問題:計劃的 PRIOR-ART 說「照代碼審同一個道理」,範本也寫「完整提交編號」。但文法收縮寫,而 lumos 現有的 `_LENS_SHA_RE` 只收 40 或 64 碼。物件庫是所有工作樹共用的,縮寫碼隨提交增加會變得模稜兩可,同一個縮寫今天能解、明天就報 ambiguous。本地若剛好有叫 hex 的 ref,`rev-parse` 還可能解到別處。64 碼的 sha256 repo 也沒被計劃涵蓋。
建議:標記只收 `_LENS_SHA_RE` 的形狀,並用 `--end-of-options` 加 `^{commit}` 解析,與 `_lens_full_sha` 同一套。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:47148` ``、``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:47158` ``。

## 4. 「相同的檢查」不屬實

severity: minor
blocking: 否 — 屬於規格與實作不符,實作時就會發現,但驗收條款 S2 會因此寫歪。
引句:「路徑先做跟工作樹那條路相同的檢查:不得含 `..` 段、不得是絕對路徑、要在 `docs/*-knowledge/` 底下」
問題:現行工作樹那條路沒有「要在 docs/*-knowledge 底下」的檢查,只檢查在 repo 內,也沒有 1MB 上限。`vault_rel` 取的是 `slugs[0]`。repo 有多個 knowledge 資料夾時,提交裡的計劃路徑可能在第二個資料夾,節點卻用第一個資料夾去對。
建議:重寫成「提交路徑新增的檢查」,並把多個 slug 的情況寫清楚。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49005-49055` ``。

## 5. 程式檔存在判斷改了,但後面的步驟仍讀會談目錄

severity: minor
blocking: 否 — 結果是範圍偏小或說明誤導,不會附錯計劃。
引句:「計劃提到的程式檔「存不存在」改用 `cat-file -e <提交>:<檔>` 判(檔在那個提交裡存在才算),impact 照現在在會談 repo 的主線算。」
問題:現況是 `impact --file f --repo root` 子行程讀會談目錄的工作樹,不是「主線」。`_nodehome_landing_sizes`(落點大小)也讀會談工作樹。於是計劃新增或改名的檔,在提交裡存在、在會談目錄不存在,impact 空手而回。輸出會寫成「沒牽到任何家、合約或事故的節點」,席位以為真的沒有。S1 只測得到「檔兩邊都有」的情境。
建議:這種情況要單獨標示為「這個檔在會談 repo 沒有」,並補一條驗收條款。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49075-49085` ``。

## 6. S5 的守衛測試抓不到繞過 `_lens_git` 的 git 呼叫

severity: minor
blocking: 否 — 只是驗收的涵蓋範圍不足。
引句:「假的 `_lens_git` 記錄每次呼叫的工作目錄,全部等於會談 repo 根」
問題:這條只替換 `_lens_git`。`cmd_dispatch_lens_spec` 的 impact 是直接 `_sp.run` 起子行程,`_codeloop_git_*` 等也直接用 `subprocess`。測試綠燈不能證明「只在會談 repo 跑 git」,這正是計劃拿來主張安全的核心。
建議:像舊 S3 那樣,改假 `subprocess.run` 依 argv 分派並記錄工作目錄。

## 7. 「掛鉤不解析」與記帳、繞法說明互相矛盾

severity: minor
blocking: 否 — 實作時會自己發現,但會讓「掛鉤不碰新文法」的承諾失效。
引句:「掛鉤自己不解析、不跑 git。」
問題:做法 3 要求「值不是提交編號寫法時」才加繞法,做法 5 要求記 `spec_rev`。兩者都需要掛鉤辨識文法。要嘛掛鉤重複一份正規式(兩份文法會漂移),要嘛由 lumos 的 JSON 回報 `mode`,計劃沒寫。
其他缺口:
- 新代碼 `spec_rev_missing` 需要進掛鉤的 `LENS_FAIL_REASONS` 白名單,新 lumos 配舊掛鉤時是否靜默,計劃沒寫(做法 2 只提到種數要改)。
- 超過 1MB 沒有失敗代碼。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:27` ``、``file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:54` ``。

## 已讀,無 finding

- 緣起與舊裁定不推翻的論述。
- 回退。
- 守衛面「最壞是指到會談 repo 的別的提交」:不新增跑 git 的目錄,這個判斷成立。

最高等級 major,共 7 條,blocking 2 條(第 1、2 條)。
