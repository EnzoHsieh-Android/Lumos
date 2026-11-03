severity: clean

被審材料:`r1-snapshot.patch` 全部 17 個檔。實質程式改動在 `scripts/lumos` 與 `scripts/test_lumos.py`,其餘是筆記、卷證與一份技能文件。我對照 repo 現況查過所有會碰 git 子程序、帳本欄位與正規式的位置。

## ① 提示注入(自由文字進派工詞、hook 附加段或指令)

已看,無。

- 新增的輸出只有三句,內容都是計數、常數與 `_gov_ledger_ignored` 回來的規則字串。規則字串早就過 `_out_clean`(`file: `scripts/lumos:1786``)。
- 這三句沒有回顯帳本裡的 `ref`、`head_sha`、`loop` 這類外來文字。`ref` 與 `head_sha` 只拿來比對與丟給 git。
- 本案新增的 `ref` 欄位內容來自 `git symbolic-ref --short -q HEAD`。git 本身禁止分支名含控制字元,所以這個值寫進帳本再被讀回也不帶換行或 ANSI 序列。
- 讀 `ref` 的新位置只有 `_redbase_on_branch`,它只做字串比較。`spec-gate-record` 的讀者(`_spec_gate_gov_index`,`file: `scripts/lumos:15401``)用 `dict(e)` 帶進 `ref`,但沒有任何位置把它印進派工詞或給 AI 的文字。

## ② 讀寫與執行越界

已看,無。

- 分支名以 `-` 開頭的問題(提示一)不成立,有兩個原因:
  - git 不允許分支名以 `-` 開頭。
  - 分支名完全沒進 git 參數。`name` 只拿來跟帳本的 `ref` 做 `!=` 比對,`_redbase_branch_name` 的回傳值也沒有傳給任何 git 子程序。
- 帳本欄位 `head_sha` 會被當成 git 參數,但先過 `_LENS_SHA_RE.fullmatch`,見 `file: `scripts/lumos:64670``。
  - 該正規式只收 40 或 64 位小寫十六進位,所以不可能以 `-` 開頭。
  - 帳本裡帶尾端換行的值,`fullmatch` 也不會放過。
  - 通過後 `merge-base --is-ancestor <sha> <head>` 與 `cat-file -e <sha>^{commit}` 的參數都是純十六進位。
  - `head` 來自 `_lens_full_sha`,它已用 `--end-of-options`(`file: `scripts/lumos:65221``)。
- `_lens_git` 用的是 list 形式的 `subprocess.run`,沒有 shell 插值,參數含 NUL 時回 `None`(`file: `scripts/lumos:65203``)。
- 新碼沒有新增寫檔、沒有跟著捷徑寫、沒有 hook 或安裝腳本、沒有網址或環境變數覆蓋點。
  - 治理帳寫入沿用 `_gate_event`。
  - `extra` 現在排除 `ref`,不會蓋掉 `_gate_event` 自己帶進去的 `ref`(`file: `scripts/lumos:1595``)。
- 新寫進程式、範本或文件的密鑰與信箱:已掃新增行的 token、key、password、`@` 信箱樣式,沒有命中。
  - 測試裡的 `t@t` 是 fixture 用的假值,不報。
  - 測試用 `--no-verify` 提交,只發生在 `_gb_repo` 建的暫存 repo 內。
  - `git clone --no-local` 的來源與目的地也都在測試暫存目錄,不涉及外部位置。

## ③ 非刻意、一步就能繞過的守衛

已看,無。

- 這次的判綠過濾只在治理帳被 git 忽略時啟動,而且判不了的一律照舊留下。偏差方向是多存一份紅燈版,不是少存。
- 平常操作可能讓過濾誤丟自己分支的判綠紀錄:壓提交、rebase、`--amend`、`git branch -m`、淺複製。
  - 這些情況會多存一份「實作後內容」的紅燈版,讓比對工具多保護或誤報,不會讓守衛失效。
  - 反方向(該丟卻留)是從判綠後的提交開新分支,那一筆仍是祖先、照舊被算進來。這是計劃已寫明的粒度天花板,行為等同改動前,不是新增的洞。
  - 所以「誰、從哪、送什麼、拿到什麼」四件填不出任何守衛被意外走過的路徑。
- 環境殘留:新碼沒有讀任何 `LUMOS_SKIP_*` 或 `PYTHONPATH`,也沒有新的環境變數入口。
  - 沿用的 git 子程序繼承環境,是既有行為。
- 三引號正規式(提示三):`_TG_CONST_PAT` 加入的 `"""[^"]*+(?:"(?!"")[^"]*+)*+"""` 與 `_TG_LIT_PAT` 同一段。
  - 這段正規式只用在 `fullmatch` 判「是不是常值斷言」,判成常值只會讓檢查多列候選。
  - 所以它放寬的是漏報,不會製造新的放行。
  - 效能面(沒收尾的三引號可能逐位置掃到尾)歸資源席,不報。
- `t_name_collision_scales` 改用計數器加 60 秒安全網。這只影響測試的紅綠,不涉及外部輸入。

## 總結

最嚴重等級是乾淨,blocking 共 0 條。
