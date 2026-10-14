severity: major

## 範圍與方法

我讀了材料全文、前掃修正 p1 到 p9、掛鉤全檔,以及 lumos 的 `_lens_git`、`_dispatch_lens_graph` 和 `cmd_dispatch_lens_spec`。我另外在臨時目錄做了實驗,實驗目錄已刪。實驗證實了 F1 和 F3。F5 的「一路到 git 之前」部分沒有實跑,是從程式推的。

「不重報」的 p1 到 p9 我都沒有重報。F1、F2 與 p3 的修法有關,但是 p3 沒有涵蓋的缺口。

## Finding

severity: major
blocking: 是 — 做法 2 的信任檢查能被繞過,繞過後 git 會在別人可寫的設定下執行任意指令,而這正是這份計劃要擋的事。
引句:「找它的 git 資料夾,不跑 git:`<路徑>/.git` 是資料夾就是它;是檔案(工作樹)就讀裡面的 `gitdir:` 那一行,再讀那個資料夾裡的 `commondir` 檔」
問題:只有 `.git` 是檔案時才讀 `commondir`。git 本身對任何 gitdir 都會讀 `commondir`,連 `.git` 是資料夾時也一樣。所以 `<路徑>/.git` 是自己擁有、755 的資料夾,裡面放一個 `commondir` 指到別處,檢查看到的是「資料夾」,就不去追共用目錄。實際生效的設定來自 `commondir` 指到的那個目錄,而那個目錄從沒被檢查。
具體失敗情境:
- 輸入:`b/r/.git/commondir` 內容是 `ev/common`。`ev/common` 是 chmod 777,它的 `config` 帶 `core.fsmonitor = touch …/PWNED`。派工詞寫 `LUMOS-REPO: …/b/r`。
- 結果:`.git` 是資料夾,路徑與父目錄也屬於自己,所以前三條都過。
- 實測:對 `b/r` 跑 `git status`,`PWNED` 檔被建立,任意指令真的執行了。
- 所以 S3「別人可寫就一次 git 都不跑」在這條路上不成立。
- 修法:不分 `.git` 是檔案或資料夾,只要 gitdir 裡有 `commondir` 就解析並驗證。
- `commondir` 是相對路徑時,要以 gitdir 為基準解析。實測工作樹的 `commondir` 內容就是 `../..`,材料沒寫這點。
- `gitdir:` 也可能是相對路徑,要以 `.git` 檔所在目錄為基準。
- 解析結果也要走一次同樣的擁有者與可寫檢查。
- 佐證:`/private/tmp/claude-501/.../scratchpad/lr-r1-正確性/b/r/.git/commondir` 的實驗,已刪。

severity: minor
blocking: 否 — 只在檔案層級的設定被人改過時才出事,單人威脅模型下機率低,但檢查的名目和實際不符。
引句:「這個資料夾、它的父目錄、它的 git 資料夾(工作樹時連共用的那個)都屬於目前使用者,而且都不是 group/other 可寫」
問題:檢查只看資料夾本身的權限。git 讀的是裡面的 `config`、`config.worktree`、`hooks/` 這些檔案。在自己擁有的 755 資料夾裡,一個 o+w 的 `config` 仍然可被別人改。資料夾權限擋不住改既有檔案的內容。
具體失敗情境:`.git/config` 被 `chmod o+w`,別的使用者寫入 `core.fsmonitor`。資料夾檢查全過,git 照跑。
修法:一併驗 `config` 和 `config.worktree`(若存在)的擁有者與可寫位元。計劃要嘛補上,要嘛把宣稱縮小成「資料夾層級」。

severity: major
blocking: 是 — 成功通過檢查後,派工詞不說這批節點是從哪個 repo、哪個提交算出來的,與設計審 `LUMOS-SPEC:` 組合時會靜默附上錯的節點,審查席無從察覺。
引句:「路徑必須是 lumos 專案的根,而且指錯時附上的節點會跟審材明顯對不上,席位照範本本來就要逐條判。」
問題:這個「明顯對不上」只在兩個 repo 毫不相干時成立。計劃要服務的主情境正好是同一個 repo 的多個工作樹:相同的 `docs/x-knowledge/Projects/a_計劃.md` 相對路徑、相同的 Systems 節點名。`LUMOS-REPO:` 若被寫錯,或被派工詞裡貼進來的材料帶進一行,lumos 會:
- 在另一個工作樹讀到那份舊版或不同版本的計劃。
- 算出看起來完全合理的 `codex-harness` 之類節點。
- 全部成功,rc=0,沒有任何說明行。

做法 4 與做法 5 的說明行只覆蓋失敗。成功路徑沒有「本次在 `<realpath>`、HEAD 為 `<sha前8>` 算出」這種可核對的標示。同樣道理,貼進派工詞的審查材料裡若恰好有單獨一行 `LUMOS-REPO: /abs/path`(例如被審的計劃或範本本身,本計劃就含這一行格式),第一行或唯一一行就會生效,不會有任何提示。
修法:成功時在附加文字開頭固定印一行來源,例如 `LUMOS-LENS: 於 <repo realpath> @ <短 sha> 計算`。同時考慮要求標記行前後不能是引用區塊,或只認派工詞最後一段。
具體失敗情境:
- 輸入:派工詞貼了一份計劃全文,裡面有一行範例 `LUMOS-REPO: /Users/x/other-worktree`;另有 `LUMOS-SPEC: docs/x-knowledge/Projects/a_計劃.md`。
- 結果:該工作樹裡有一份舊版計劃,掛鉤靜默附上舊版的連結節點。

severity: minor
blocking: 否 — 兩行以上一律拒絕會被正常內容觸發,但失敗方向是「沒附」,不是附錯,且有說明行。
引句:「同一份派工詞出現兩行以上,視為不合格(原因 `repo_duplicate`),照做法 4 處理——不去任何地方算、只附說明。」
問題:派工詞裡貼上計劃或範本全文本來就常見,內容含 `LUMOS-REPO:` 的說明或範例時,真正的標記加上範例就湊成兩行。結果是原本能算的情形變成算不出來,而且 `repo_duplicate` 的提示讓人誤以為自己寫重了。
具體失敗情境:派工詞貼了本計劃的「做法 1」那一行,加上編排者自己的一行,兩行都符合正規式,拒絕。
修法:只在派工詞最後一個非空白行或獨立標記區塊找,或對「與第一行不同值」才算重複。

severity: minor
blocking: 否 — 失敗方向是拒絕,不會讓不該信任的目錄被執行,但原因代碼會騙人。
引句:「結果要等於 `realpath`(要指 repo 根,不收子資料夾,免得同一個 repo 有多種寫法;不等於也是 `repo_not_root`)。」
問題:大小寫不分的檔案系統上,`os.path.realpath` 不會把大小寫還原成磁碟上的真實寫法,但 `git rev-parse --show-toplevel` 會。實測:`git -C /USERS/ENZO/… rev-parse --show-toplevel` 回 `/Users/enzo/…`,而 `os.path.realpath('/USERS/ENZO/…')` 回 `/USERS/ENZO/…`,兩者不等。
具體失敗情境:`LUMOS-REPO:` 寫了大小寫不同的合法路徑 → 比對失敗 → 報 `repo_not_root`。說明行讀起來像「你給的是子資料夾」,實際只是大小寫不同。
修法:比對改用 `os.path.samefile`,或兩邊都過 `os.path.realpath` 再加 `normcase` 與 Unicode 正規化比較。另外要明寫「傳給 `--repo` 的是 realpath 還是原字串」。計劃寫「傳這個路徑」,有歧義。

severity: minor
blocking: 否 — 影響範圍限於明確加了 `LUMOS-REPO:` 的情形,方向是更保守,但會讓人學會不寫標記。
引句:「前四條都過了,才跑 `git -C <路徑> rev-parse --show-toplevel`」
問題:父目錄「不是 group/other 可寫」這條,在以下常見位置會誤殺:
- `/tmp` 或 `/private/tmp`:sticky 加 other 可寫,所有放在那裡的合法 repo 都會被拒。
- 預設 umask 002 的 Linux:使用者建的工作目錄常是 group 可寫。

沒寫標記時,會談目錄反而完全不檢查。結果是同一個 repo 寫標記會被拒,不寫標記卻能算,誘因是不寫。這不是新危險,但「把原本附得上的情形變成附不上」只針對有標記的路徑,仍值得在計劃裡寫明這個取捨,或對 sticky 目錄(`S_ISVTX`)放寬父目錄檢查。

severity: minor
blocking: 否 — 理由是計劃已把這類殘餘風險寫進實務隱患並接受,這裡只補一個它沒有點到的差別。
引句:「這一類在會談目錄也一樣擋不住(會談目錄沒有任何檢查),而且使用者自己在那個資料夾裡敲 `git status` 就會觸發,不是本計劃新開的口」
問題:兩者可執行的範圍不同。會談目錄是使用者在 Claude 的信任提示下主動打開的那一個。`LUMOS-REPO:` 允許派工詞指向磁碟上任何自己擁有、結構正確的 repo,其中包含使用者下載了、卻從未打開也從未信任的 repo。「使用者自己敲 `git status` 也會觸發」只對他實際進入的目錄成立。派工詞可被注入正是計劃自己承認的威脅,注入者只要知道一個這樣的路徑就能觸發。
具體失敗情境:使用者之前 `git clone` 了一個陌生 repo 放在 `~/Downloads/x`,從沒進去過,裡面 `.git/config` 帶 `core.fsmonitor`;派工詞被注入一行 `LUMOS-REPO: /Users/u/Downloads/x`,路徑加父目錄加 `.git` 都屬於自己且為 755,檢查全過,git 執行。
修法:列為已知殘餘風險時把這個差別寫清楚。可選的緩解是掛鉤以 `-c core.fsmonitor=false -c core.hooksPath=/dev/null` 之類跑 `rev-parse`,或把允許的 repo 限制在曾被 lumos 登記過的清單。

## 已讀,無 finding

- 做法 3 到 8 的流程編排:`--repo` 傳遞、設計審 `spec_missing` 等三個代碼、說明行分兩版、Codex 不在範圍。
- 符號連結:`os.path.realpath` 會解開 `<路徑>` 本身的連結,實測 `ln -s` 後 git 的 toplevel 與 realpath 一致。
- `..`:`realpath` 會正規化 `..`。
- 工作樹的 `gitdir:` 與 `commondir` 本身:實測存在,`commondir` 內容是相對路徑 `../..`,計劃需要明寫以 gitdir 為基準解析,這已併入 F1。
- 設計審 `cmd_dispatch_lens_spec` 的邊界檢查:絕對路徑與穿越 `..` 都在 `resolve().relative_to(root)` 擋住。
- `LUMOS-ROLE-CARDS` 與 `LUMOS-ARCH-TARGET` 的傳遞,與新標記無互動。

最高等級 major,共 2 條 blocking(F1、F3)。
