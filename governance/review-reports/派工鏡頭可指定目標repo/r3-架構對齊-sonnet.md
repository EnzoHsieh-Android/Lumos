severity: major

severity: major
blocking: 否 — 只要計劃補一句「直接借用哪個既有函式」就能收掉,不用改設計方向。
引句:「超過 1MB 不讀,跟工作樹那條路的上限同值;沒有上限就補一個」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:31152`(`_nodehome_cat_blobs_capped`:先問大小、超過上限的不讀進記憶體,註解寫明「上限放在批次讀取這一層,不另起查法」)。另見 `lumos:23941`(註解寫明用專案既有的 `git show` 包裝,第三輪另寫一套 `cat-file` 被架構席點過)。
判定理由:專案已經有「讀提交裡的檔、帶大小上限」的現成做法,而且註解明說不准另起查法。計劃卻自己組一套「`cat-file -s` 先查大小,再 `show`」,等於在 `_nodehome_cat_blobs_capped` 旁邊多一種有上限的讀法。計劃也沒說借哪個:`_nodehome_cat_blobs_capped` 內部直接起 `subprocess`、不走 `_lens_git`,跟 S5「假的 `_lens_git` 記錄每次呼叫的工作目錄」的測試法衝突。計劃需要明講取捨,二選一:(a) 沿用 `_lens_git show` 加一個共用的小上限包裝,並說明為何不用 `_nodehome_cat_blobs_capped`;(b) 用 `_nodehome_cat_blobs_capped` 並改 S5 的測法。

severity: major
blocking: 否 — 屬於模組邊界沒切清楚,補一句「由 lumos 在 JSON 回報」就能解。
引句:「只把值原樣交給 lumos;掛鉤自己不解析、不跑 git。」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:250`(`_fail_note` 只查 lumos 印的固定字彙 `lens_fail`,不自己判斷輸入形狀),`dispatch-lens-hook.py:54`(`LENS_FAIL_REASONS` 查表);`lumos:48752`(`_dispatch_lens_fail` 註解:新增原因加代碼,不加鍵)。
判定理由:做法 3 要求「值不是提交編號寫法」才加繞法,做法 5 要求「用到提交編號寫法時」才記 `spec_rev`。這兩處都得靠掛鉤自己判斷值的文法,跟「掛鉤不解析」自相矛盾。這樣 `<提交>:<路徑>` 的文法會在 lumos 和掛鉤各有一份正規式,日後會漂移。既有邊界是:判斷在 lumos,掛鉤只讀 lumos 回的固定字彙 JSON 再貼說明。所以該由 lumos 在 `--json` 輸出帶出「這次用了提交寫法」以及失敗代碼,掛鉤只依這個欄位附說明和記 note。另外,`_fail_note` 現在對 spec 路徑直接回空字串(`why = ... if rng else None`),計劃沒交代怎麼改這個簽名。

severity: minor
blocking: 否 — 措辭與事實不符,不影響設計方向。
引句:「路徑先做跟工作樹那條路相同的檢查」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49011`(`cmd_dispatch_lens_spec` 的工作樹路徑只有 `resolve().relative_to(root)` 與 `is_file()`,沒有「不得含 `..` 段」、沒有「要在 `docs/*-knowledge/` 底下」的檢查)。另外 `spec_missing`、`spec_outside_repo`、`no_knowledge` 三個代碼在 `scripts/lumos` 與 `LENS_FAIL_REASONS` 都不存在。
判定理由:計劃說兩條路檢查相同,實際提交那條會比工作樹那條嚴,結果同一個參數有兩套路徑規則。計劃也把這三個代碼寫成「沿用」,但它們是新增的(後文自己也承認「現在不印」)。建議改成明說「提交路徑較嚴」,或讓兩條路共用一個檢查函式;三個代碼改寫成新增,並列入要改 `LENS_FAIL_REASONS` 與 `_dispatch_lens_fail` 說明裡的種數。

severity: minor
blocking: 否 — 只是漏了指名既有函式。
引句:「確認提交存在,再 `show <提交>:<路徑>` 讀計劃內容」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:47401`(`_lens_full_sha`:`rev-parse --verify -q --end-of-options X^{commit}`,並驗是完整 sha)、`lumos:27825`(`_path_at_pin` 用 `cat-file -e sha:path` 判檔存在)、`lumos:30805`(`_NODEHOME_COMMIT_RE`,7 到 40 碼十六進位)。
判定理由:提交解析、檔存在判斷、十六進位正規式都已有現成實作。計劃只寫裸的 `rev-parse` 與 `cat-file -e`,沒說要借用,實作時容易再寫第二份,而且少了 `--end-of-options` 的防護。計劃要說明借用 `_lens_full_sha` 與 `_path_at_pin` 的泛化版,以及提交文法的正規式放哪一處。

severity: minor
blocking: 否 — 屬於讀取點重複的風險。
引句:「讀的計劃內容換成從提交讀到的那份,宣告與節點照現在從 HEAD 讀。」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:49137`(`_dispatch_lens_spec_with_arch` 在 `cmd_dispatch_lens_spec` 之外,自己重新算 root、重新讀一次計劃檔)。
判定理由:現在讀計劃就有內外各一份。計劃只寫「換成從提交讀」,沒說讀取收斂到哪裡。若各自解析 `<提交>:<路徑>`,同一個文法會有兩個解析點,也會多跑一輪 git。建議抽成一個「讀計劃內容」的共用函式,內外都呼叫它。

severity: minor
blocking: 否 — 記帳慣例的延伸,計劃已自述是有限鬆綁。
引句:「掛鉤事件 note 在用到提交編號寫法時記」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/_hookevent.py:111`(`mark` 的設計用途是「吞掉的逾時或失敗自己講一聲」,沒講的才算 ok);`dispatch-lens-hook.py:260`、`:484`、`:520` 的既有 note 都是中文說明句,類別是 `error` 或 `timeout`。
判定理由:成功時也呼叫 `mark` 是新用法,`spec_rev <代碼>` 這種機器字首跟既有的說明句格式不同。計劃沒說失敗時事件類別用 `error` 還是 `ok`。建議講清楚,並說明「成功不用 mark」這條既有慣例為何要破例。

總結:不對齊共 6 條,其中 major 2 條(自組有上限的提交讀法,與掛鉤和 lumos 對提交寫法文法的邊界重複);整體做法(在會談 repo 用 `_lens_git` 讀提交、不新增信任機制)與專案既有走向一致,沒有跨層直呼的問題。
