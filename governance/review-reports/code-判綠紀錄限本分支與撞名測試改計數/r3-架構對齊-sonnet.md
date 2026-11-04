severity: minor

我對照的是 `git show fe97022786221eec968fff5f614b1c135866e11a:scripts/lumos`,存成 `/private/tmp/claude-501/lumos-fe97.py`,下面的行號都是這份的。我審查時,工作目錄裡的 `scripts/lumos` 比 fe97022 多了一處未提交改動:`_drift_born_env_err` 那行被改回舊寫法。這不是我改的,我沒有碰。

**一、分層與依賴方向**

新增的 `_git_partial_clone` 放在 `_git_is_shallow` 正下方(`scripts/lumos:12022`、`scripts/lumos:12035`),跟鄰居放同一區。它走 `_lens_git_dl` 這條共用的 git 呼叫層,跟 `_gov_ledger_ignored`(`scripts/lumos:1775`)一樣。呼叫它的是 `_drift_born_env_err` 和 `_redbase_on_branch`,兩邊都沒反過來依賴。

判祖先的寫法內聯在 `_redbase_on_branch`,跟 `_note_reread_own_fps`(`scripts/lumos:52858`)、`_codeloop_missing_commit` 同一種做法。專案裡沒有共用的判祖先函式,13 個以上的位置各自內聯,所以這不算新做法。

`_TG_CONST_PAT` 抄了一份 `_TG_LIT_PAT` 的三引號段並註明出處。專案原本就是這樣對待 `_C_STRIP_PAT`(`scripts/lumos:6786`)與 `_TG_LIT_PAT`,做法一致。

有一處跨區直呼:`_redbase_branch_name` 呼叫了回頭重讀區的 `_note_reread_branch`(`scripts/lumos:53356`)。`_note_reread_branch` 的說明綁在回頭重讀那份計劃,簽名帶推送用的 `pushed_ref`,新碼傳 `None` 去用它。專案裡別區呼叫回頭重讀私有函式有兩個先例:
- `_metric_gate_off` 呼叫 `_note_reread_config`(`scripts/lumos:4681`)。
- drift ack 共用 `_note_reread_wt_verdicts`(`scripts/lumos:56170`),那支的說明明寫「走訪只有這一份」。

`_note_reread_branch` 沒有這種共用標示。我判為 minor、標 ⚠:兩個區是對等的功能區而不是上下層,而且已有先例。照最嚴的讀法也可以算 major。

severity: minor
blocking: 否
引句:「ref = _note_reread_branch(rr, None)」
佐證:`scripts/lumos:53356`(函式本身)、`scripts/lumos:56170`(明寫共用的先例)

**二、命名與錯誤處理**

命名跟鄰居一致:
- `_REDBASE_ANC_BUDGET_SEC` 對應 `_NOTE_REREAD_BUDGET_SEC`(`scripts/lumos:51723`)與 `_SECEV_BUDGET_SEC`(`scripts/lumos:8595`)。
- `_REDBASE_ANC_CAP` 對應 `_NS_TR_GREP_CAP`(`scripts/lumos:47593`)。
- 截止時間用 `import time as _t; _t.monotonic() + budget`,跟 `scripts/lumos:11022` 和 `scripts/lumos:33876` 一樣。

說明一律印到 stderr、帶 `[spec-gate]` 前綴,跟同函式群一致。逾時走 `_lens_git_dl` 加 `_git_timeout`,逾時回 None,跟 `_gov_ledger_ignored` 同款。

有一處不一致。`_git_partial_clone` 回三態(True、False、None),`_redbase_on_branch` 把 None 當判不了。但 `_drift_born_env_err` 把這行改寫成直接 `if _git_partial_clone(root):`,None 被當成非部分複製。同一函式裡,4 行前的淺層檢查是把 git 逾時當判不了,回「git 跑不起來」(`scripts/lumos:55677` 前後)。`_drift_born_env_err` 的呼叫端 `_drift_born_annotate` 的說明明寫「每一步有一點不確定就判不了」。所以同一個三態值,兩個呼叫端處理方向相反,新舊兩個判法函式的失敗訊號也不同:`_git_is_shallow` 用丟 `TimeoutExpired`,`_git_partial_clone` 用回 None。舊行為(`_lens_git` 回 None 就放行)也是這樣,但這次 diff 動了那一行,又把三態收掉,所以我列為 minor。

severity: minor
blocking: 否
引句:「if _git_partial_clone(root):」
佐證:`scripts/lumos:55674`(`_drift_born_env_err` 的淺層檢查把逾時當判不了)、`scripts/lumos:12022`(`_git_is_shallow` 用丟例外)

測試端的寫法與鄰居一致:`_gb_repo`、`_gb_red` 的前綴與 `_ig_sg_repo`、`_rb_sg_repo` 同類。`_tqg_module()` 是同批 redbase 測試共用的載入法,例如 `scripts/test_lumos.py:123545`。換掉模組函式再 finally 換回,以及 `contextlib.redirect_stderr`,都跟專案現有寫法相同。

**三、第二種做法**

我沒有找到鄰居已有同功能、diff 卻另寫一套的情形。

- 目前分支名:專案裡本來就有多種寫法,`_codeloop_git_branch`(`scripts/lumos:64692`)、三處內聯的 `symbolic-ref -q --short`(`scripts/lumos:42133`、`scripts/lumos:43674`、`scripts/lumos:65200`)、`_note_reread_branch`。這次沒有再寫第五套 git 呼叫,是薄包 `_note_reread_branch`,說明裡講了不用 `--short` 與不用 `_codeloop_git_branch` 的理由(同名 tag 與分離 HEAD)。
- 寫進帳的 `ref` 欄位:其他閘多半寫 `_codeloop_git_branch` 的值(分離 HEAD 寫字面 HEAD,同名 tag 時可能寫 `heads/名`),規格閘寫去掉前綴的分支名、分離 HEAD 就不寫。這個差異有寫理由。
- 讀取 `ref` 的只有新的 `_redbase_on_branch`(`scripts/lumos:14464`);其他讀 `ref` 的位置(`scripts/lumos:24572` 簽核帳、`scripts/lumos:16507`)是別本帳的欄位,不衝突。所以目前不構成第二種做法。
- 部分複製偵測:新函式取代了 `_drift_born_env_err` 裡舊的單一設定檢查,`scripts/lumos` 裡已沒有其他獨立的部分複製偵測。
- 淺層判法:`repo_kind` 沿用 `_git_is_shallow` 加 `TimeoutExpired`,沒有另寫淺層判法。

不對齊共 2 條,其中 major 0 條
