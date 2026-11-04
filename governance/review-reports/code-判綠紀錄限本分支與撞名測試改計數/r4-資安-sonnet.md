severity: clean

這輪沒有可利用的洞。我讀完整份 r4-snapshot.patch,並到 repo 查證 `_lens_git`、`_lens_git_dl`、`_gov_rows_at`、`_gate_event_build`、`_LENS_SHA_RE`、`_note_reread_show`。

本案提示的三點結論如下。

- **`git config -z` 的解析**:`_git_partial_clone` 把輸出切成每筆以 NUL 結尾、鍵與值以換行分隔,裸鍵沒有換行。值不由外來文字拼進指令,只拿來判真假。
  - 鍵名用固定的正規式,`git config` 只讀不寫,不會執行任何東西。
  - `int(v, 0)` 遇到壞值丟 ValueError,被接住後當真。判不了時一律往「小心」那邊走:判成部分複製,或判不了而照舊留。
  - 沒有任何一種怪值能讓它誤判成「不是部分複製」,進而去連遠端。
- **帳被忽略時讀整本工作目錄的帳**:`_gov_rows_at(rr, None, …)` 先擋符號連結與非一般檔,才讀檔。
  - 這條路徑本來就讀工作目錄那份,不是新增的讀取面。
  - 讀進來的 `head_sha` 要先過 `_LENS_SHA_RE.fullmatch`(只收 40 或 64 位小寫十六進位),才會被當參數交給 `merge-base --is-ancestor` 與 `cat-file -e`。
  - 因此帳裡的自由字串不可能被當成 git 旗標,也沒有 shell 插值。
  - `ref` 欄位只做字串相等比對,不進指令。
- **測試改寫 `.git/config`**:只寫在 `mkvault()` 與 `_gb_repo` 建的暫存 repo,測試裡的 `remote.origin.uploadpack` 指到測試自己寫的記號腳本。路徑來自 `tempfile`,沒有外部輸入。測試沒有走網路,也沒有看起來真能用的憑證。

① 提示注入:已看,無。
- 新增寫進治理帳的 `ref` 是分支名,先過 `_note_reread_show`(去控制字元、截 1000 字)。
- 讀回來只做相等比對。唯一另一個讀 `d.get("ref")` 的地方是簽核帳 `.signoff-log.jsonl`,與治理帳是不同的檔。
- 新增的 stderr 訊息只印筆數(整數)與常數字串,沒有外來自由文字進入派工詞或 hook 附加段。

② 讀寫與執行越界:已看,無。
- 新增的 git 呼叫是 `config -z --get-regexp`、`merge-base --is-ancestor`、`cat-file -e`、`rev-parse --is-shallow-repository`。
  - 這四個都不會觸發 `core.fsmonitor`、hook 這類會執行 repo 內設定的路徑。
  - 都走既有的 `_lens_git` 的 `git -C <repo>`,逾時有上限。
- 讀工作目錄帳時擋符號連結。沒有新寫檔路徑,沒有跟著外來路徑寫。
- `_redbase_prev_doc` 讀紅燈版的路徑檢查是既有行為,這輪沒有改。
- 沒有新增下載來源、環境變數覆蓋的網址、密鑰或信箱。我對筆記與文件部分的新增行掃過 `@`、`http`、`token`、`secret`、`curl`、`eval`、`shell=True`、`LUMOS_SKIP`、`PYTHONPATH`。唯一命中是 PRIOR-ART 行裡的 git 官方文件網址,屬於引用,不是下載來源。

③ 非刻意、一步就能繞過的守衛:已看,無。我逐一想了這輪新增的走過路徑,每條判不了時都落在原本的行為,沒有多出一個能被意外走過的缺口。
- 部分複製或淺複製:`_redbase_on_branch` 整批不問 git、照舊留。這比過濾前的行為沒有更鬆,且是計劃天花板三已列的取捨,不是新缺口。
- 帳被忽略但 `.git/config` 壞掉、git 逾時、過了截止時間或超過 200 筆:都是「判不了、照舊留、印一句幾筆」。
- 「判不了」這個方向本身:被留下的判綠紀錄會讓該測試不存紅燈版,這是新增過濾之前就有的行為。所以沒有「照平常操作一步就讓原本會擋的守衛放行」的新路徑。
- 部分複製且帳進版控:`_redbase_branch_rows` 回 `[]`,不再有判綠觀測。結果是紅燈版多存、不會少存,方向偏嚴,不是繞過。
- 沒有新增任何 `LUMOS_SKIP_*` 之類環境變數讀取。
- 分支名過濾的碰撞:截斷或清洗後同名只會把兩條分支當成同一條而照留,方向偏安全。

最嚴重等級是 clean,blocking 共 0 條。
