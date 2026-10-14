severity: major

這輪只找到一個洞。修補把「用遠端舊值算分岔點」只套在推主線,其他分支名仍照本機追蹤 ref 算。補償用的 CI 只提醒、不擋。

我也試了其他幾條路,都沒繞過,列在最後。

## Finding 1:推到主線以外的分支名時,偽造本機追蹤 ref 仍能讓指紋看不到藏起來的改動

severity: major
blocking: 是 — 推功能分支時,第三輪的偽造追蹤 ref 攻擊原樣有效,回頭重讀提醒整段失效,之後走網站合併進主線時沒有任何會擋的檢查

引句:「分支名不在 _note_reread_mainline_names 裡(功能分支:rebase 後強推」

攻擊步驟(輸入 → 結果):
1. 在 attack 分支先提交一個藏了改動的提交 E(改 `src/a.py` 第 5 行),再提交正常改動和筆記追加。
2. 把 `refs/remotes/origin/main` 本機偽造成 E。
3. 這時 `reread-prepare` 不帶推送參數,分岔點落在 E。指紋看不到 E 的改動,記成「已對照」的紀錄。
4. 真正推送時給 `--diff <真主線 base>..HEAD --pushed-ref refs/heads/feat`(或 `release`、`refs/tags/v1`,任何不在 main/master 和遠端 HEAD 之列的名字)。
   - `_note_reread_push_old` 因分支名不在主線名單而直接返回,`push_old` 維持 None。
   - 分岔點又吃本機追蹤 ref(偽造值),指紋與紀錄相符。
   - 結果:`--gate` 放行,`rc=0`。
5. 之後在 GitHub 網站合併進 main,不經過本機 pre-push。

補償機制名存實亡。引句旁的註解說「功能分支這條由 CI 用 fetch 下來的真遠端主線重算補驗」,但 CI 那一步 `.github/workflows/ci.yml:264` 寫的是:
- 不帶 `--gate`
- 尾巴 `|| true`
- 步驟本身 `continue-on-error: true`

所以 CI 只印提醒、永遠不擋。補丁附帶的文件也寫明「不帶 `--gate` 時它在任何情況都回 0」。

實驗證據(用 `_rfp_forged` 夾具,偽造 origin/main 為 E,在 forged 範圍記好紀錄,再以 `--gate` 檢查):

| `--pushed-ref` | 結果 |
|---|---|
| `refs/heads/main` | rc=1,擋下 |
| `refs/heads/feat` | rc=0,「1 篇守檔筆記都對照過這一版程式了」 |
| `refs/heads/release` | rc=0,同上 |
| `refs/tags/v1` | rc=0,同上 |

- 修補只擋住「直接推 main」這一種寫法,偽造追蹤 ref 這個根因還在。
- 代價比 r3 小,因為多了合併進主線這一步。但這步在網站上做,正好是單人 AI 編排者常用的流程。
- 建議方向:不論推到哪個分支名,分岔點都不要信本機追蹤 ref,改用遠端舊值。新建分支時沒有舊值,就改問遠端實際的主線,例如 `ls-remote`。CI 那步也要有能擋的版本。
- 佐證:`scripts/lumos:37780`(`_note_reread_push_old` 在分支名不在主線名單時直接返回)、`scripts/lumos:36423`(只在 `push_old` 有值時才用遠端舊值)、`.github/workflows/ci.yml:264`。

## 試過但沒繞過的

- **其他 git 設定讓指紋讀到不同差異**:在 `.git/config` 或環境變數設了這些,逐檔 diff 輸出逐位元組相同。
  - 試過的設定:`diff.noprefix`、`mnemonicPrefix`、`relative`、`context`、`srcPrefix`、`core.whitespace`、`ignoreSubmodules`、`algorithm`、`renames`、`autocrlf`、`safecrlf`、`textconv`、`xfuncname`、`GIT_CONFIG_COUNT/KEY/VALUE`。
  - `core.bigFileThreshold=1` 或 `.git/info/attributes` 的 `* -diff` 會讓輸出變成 `Binary files differ`。這時指紋改記 index 行的新 blob 編號,仍隨內容變,只會多報、不會漏報。
- **主線名不是 main/master**:試了預設分支叫 `trunk`,設或拿掉 `origin/HEAD` 都被擋。拿掉 `origin/HEAD` 後指紋退回 v1,對不上 v2 紀錄,屬保守方向。
- **惡意檔名搞亂一次 diff 切檔頭**:檔名帶 ` b/`、只改 mode 的檔,讀程式推演後的結果如下。
  - `_note_reread_split_diff` 會把它誤判成別的名字,但同名會被丟掉,單檔重問後也對不上。
  - 結果是退回 v1(更嚴),沒有改動被併進另一支或被丟掉。這條只靠讀程式推演,沒另外造檔實測。
- **偽造 pre-push stdin、直接呼叫 reread-check**:呼叫它不會替任何筆記產生「已對照」的紀錄,不構成繞過。

臨時目錄:我建的實驗 repo 與暫存已刪。`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下還有 `gctl-run-*` 目錄,不是我建的,我沒碰。

最高等級 major,blocking 1 條。
