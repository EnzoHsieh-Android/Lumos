severity: minor

我沒找到不刻意混淆、也不在〈範圍〉裡的寫法能讓這支掛鉤放行真繞閘。「只認判斷當下的事實」確實有縫:同一條指令把已存在的暫存目錄換成指向真 repo 的連結。我判斷它屬於有心改寫,但〈範圍〉沒列,且與 d3 的「封閉」說法矛盾,所以列為 minor。

## Findings

1. 判斷當下存在的暫存目錄,在同一條指令裡被換成指向真 repo 的連結,仍然放行。

   - 輸入(cwd 為真 repo,`E` 是判斷當下已存在的暫存實驗 repo):
     - `rm -rf E && ln -s <真repo> E && git -C E commit --no-verify -m x` → `[]`
     - `mv E E.old && ln -s <真repo> E && git -C E commit --no-verify -m x` → `[]`
     - `cd 已存在的空暫存目錄 && ln -s <真repo>/.git .git && git commit --no-verify -m x` → `[]`
     - 對 `echo 'gitdir: <真repo>/.git' > P/.git && git -C P commit -n -m x` 也是 `[]`(P 為已存在的暫存空目錄)。
     - `git -C 暫存空目錄 config core.hooksPath /dev/null` 也放行。
   - 對照:`mkdir W/newdir && ln -s … && git -C W/newdir commit -n`,目錄是同指令新建的,所以回 `['commit-n']`。
   - 走到的程式:`_not_real_repo` 先看 `_existing_temp_dir(eff)`,再用 git 查共用目錄。查的是執行前的狀態,指令真正執行時已被換掉。
   - 我的判斷:要連做兩步才成立,屬於〈範圍〉承認的「有心改寫」,不是一般代理「順手繞」。但有兩點與文件不符:
     - d3 選項②當年被否決的理由是「仍擋不住刪掉重建成連結」,出貨版同樣擋不住,所以 d3 的「攻擊面收成封閉」不成立。
     - 程式註解與計劃說「git 明說不在 repo 裡,之後建的只會是新的」。這個推論本身就被上面的 gitfile 與連結寫法推翻,而 d3 說要拿掉的正是這類推論。
   - 應該是:要嘛在〈範圍〉明列這一類(同指令改寫判斷當下已存在的暫存目錄)並改寫 d3 的「封閉」說法,要嘛判斷時對同一條指令裡出現 `ln`、`mv`、`rm` 或寫 `.git` 的情形不給豁免。
   - 歸因:有證據的原有漏查。修前版本(4e87b682)與修後版本同一組輸入都回 `[]`。
   - 查證命令:用 `SourceFileLoader` 載入兩版的 `bypass_reasons(cmd, 真repo)`,輸出見上。
   - 引句:「而且共用 git 目錄也在暫存根底下;或 git 明說它不在任何 repo 裡。不靠同一條指令裡的推論」
severity: minor
   - blocking: 否

2. commit 與 `git config` 的拋棄式豁免只看共用 git 目錄在不在暫存根底下,沒看是不是真遠端的工作副本。

   - 輸入:`/tmp/.../realclone` 是 `git init` 後 `remote add origin git@github.com:EnzoHsieh-Android/Lumos.git` 的工作副本,cwd 設在這個目錄。
     - `git commit --no-verify -m x` → `[]`
     - `git config core.hooksPath /dev/null` → `[]`
     - `LUMOS_SKIP_X=1 git commit -m x` → `[]`
     - 同一目錄的 `git push --no-verify origin main` → `['no-verify']`,推送端有擋。
   - 與文件的關係:計劃〈量測〉自己說暫存目錄裡有真工作副本,例如 `/tmp/lumos-readme-oct-audit` 一週 5 次一般推送。推送端因此改查推送位址,commit 與 config 端沒有對應檢查。
   - 影響:提交端的閘在這類目錄裡被繞過時不會問。後續的一般 `git push` 也不帶旗標,所以不會補問。如果那個副本裝了 Lumos 的提交前閘,這就是真繞閘。我沒驗證 `/tmp` 工作副本實際有沒有裝閘,⚠ 交編排者判斷。
   - 應該是:要嘛承認並寫進〈範圍〉,要嘛 commit 與 config 的豁免多查 `remote get-url`(網路位址就不豁免),或至少為這個取捨補一條說明。
   - 歸因:有證據的原有漏查。修前修後同為 `[]`。
   - 引句:「+        return _not_real_repo(eff)」
severity: minor
   - blocking: 否

## 已驗正向主張

甲(閘被擋、使用者在催的代理,正常寫法)

- 真 repo 裡下面這些都回對應代號,都會問:
  - 順序或位置變化:`git push --no-verify`(旗標在前或在後)、`git push origin HEAD --no-verify`、`git commit -nm`、`git commit --amend -n`
  - 縮寫、全域選項與前綴:`--no-verif`、`git --no-pager push --no-verify`、`git -C . push --no-verify`、`command`、`sudo`、`env`、`timeout` 等前綴
  - 括號與迴圈:`( … )`、`{ …; }`、`if … then`、`for … do`
  - 管線與導向:管線、`>/dev/null`、`2>&1`
  - 引號與反斜線:`g"i"t`、`$'--no-verify'`、`--no-ve''rify`、反斜線續行
  - 設定改寫:`-c core.hooksPath=`、`--config-env=`、`GIT_CONFIG_*`、`export` 後再提交、各種 `git config` 寫法(`--add`、`--unset`、`--worktree`、`-f`、`--file=` 等)
  - 環境變數:`LUMOS_SKIP_*` 前綴、`env` 前綴
- 以下被放行,與〈範圍〉承認的一致:`sh -c '…'`、`$(…)` 內的指令、`!git`(感嘆號黏著)、`echo $((git push --no-verify))`。
- 目錄追蹤:真 repo cwd 下,`cd 暫存目錄 && cd 真repo` 之類的組合(`&&`、`||`、`;`、子殼層、`$HOME`、`~`、`git -C 真repo`)都回 `commit-n`,不誤放行。
- `--git-dir`、`--work-tree` 與 `remote set-url`、`add`、`rename`、`config remote.*`、`config url.*` 都使豁免失效,回報 `['no-verify']` 或 `['commit-n']`。唯讀的 `git remote -v` 不影響豁免。
- 暫存目錄 `E` 的 `.git/config` 被 `sed -i` 或 `echo >>` 改成指向真遠端後再推送,仍回 `[]`。這是〈範圍〉已承認的「直接改 `.git/config`」,不重報。

乙(日常不該問的指令)

- 以下全部回 `[]`,沒有誤問:
  - 審查席在已存在的暫存 repo 裡的實驗:`git -C E commit --allow-empty --no-verify`、`cd E && git commit -n`、`git config core.hooksPath` 寫入、帶遠端名稱的 `push --no-verify`(遠端指向暫存裸 repo)、`gctl-run-*` 的子目錄提交。
  - 搜尋與讀值:`grep`、`rg` 搜尋這些旗標名、`git config core.hooksPath` 讀值、`--get`、`--local`。
  - 一般提交推送與 `git log -n`:Claude 慣用的 `git commit -m "$(cat <<'EOF' … EOF)"` 含撇號、`--no-verify`、`-n`、`LUMOS_SKIP_` 字樣的訊息,`git commit -F - <<'EOF'`,以及 `git log -n`、`git diff -n`、`git push -n/--dry-run`、`git push -u`、`--no-edit`、`--no-gpg-sign`。
- 沒加引號的 `echo git push --no-verify` 會問,這是文件承認的誤問。
- 小的誤問(不另列 finding):
  - 旗標值剛好是 `--no-verify`:`git commit -m --no-verify`、`git push --push-option --no-verify` 會問。
  - `cd W/exp && git push --no-verify` 沒寫遠端,保守地問。
  - `cd $TMPDIR && …` 目錄判不出,會問。
- 效能與巢狀:
  - 輸入:1.9 萬字、各 3000 層巢狀 `$(` 或 `(`、2000 個 `cd`、800 個 heredoc,不論有無結束字。
  - 結果:最慢 0.016 秒,沒有退化。超過 2 萬字走 `literal`,長度夠但沒有可疑字樣的指令回 `[]`。
- `_hookevent._trim` 修補驗證:
  - 20 萬行的檔修剪後剩 2000 行,權限保持 `0640`。
  - 超過一分鐘的殘留 `*.trim` 暫存檔被清掉,新的暫存檔保留。
  - 經 `record()` 觸發的修剪正常。
  - 單行超過 `MAX_BYTES/2` 時整檔會變成只剩換行。`record` 把 note 截在 200 字,實務上不會發生,不報。

## 三問

1. 原問題修復效果:新規則下,同指令新建目錄、`mktemp`、同指令動遠端設定這幾類都回對應代號,舊版(4e87b682)放行,例如 `mkdir nd && git -C nd init && git -C nd commit --no-verify` 舊 `[]`、新 `['no-verify']`。對判斷當下已存在目錄的同指令改寫,新舊都放行(finding 1)。
2. 相鄰路徑:已存在的暫存 repo 實驗、`gctl-run` 子目錄、讀值、搜尋、heredoc 提交訊息都沒被誤問(見乙)。
3. 新發現的修前修後:兩條都是新舊同結果,屬原有漏查,不是修補引入的回歸。

## 固定席節點逐條判

- `Issues/code-loop守衛main-direct盲區`:不影響。該事故講守衛盲區,這次兩個掛鉤檔不碰那條路徑。
- `Systems/lumos-cli-read`(含 ★INVARIANT★ search 排除 superseded):不影響。改動沒碰 `search` 或讀取邏輯。
- `Systems/lumos-cli-lifecycle`(含 ★INVARIANT★ re-inject 保留 sentinel 外內容):不影響。程式組只動掛鉤與 `_hookevent`,沒碰 re-inject。`scripts/lumos` 與 `merge-claude-settings.py` 的改動屬測試文件組,我沒逐 hunk 讀。
- `Systems/design-loop`(處置閘第五步)、`Systems/測試假綠形態`(還原翻紅釘要前置斷言)、`Systems/guard-kill`:不影響程式組。測試是否帶前置斷言屬 `test_lumos.py`,不在我的分組。
- `Systems/pitfalls-code-loop`、`Systems/reversibility-governance-ledger`(★RISK★):不影響。程式組沒碰 pitfalls 分級或帳本。
- 超出上限只列名的節點:`Systems/bound-tests-gate`、`Systems/slim-install-安裝器`、`Systems/lumos-deinit` 等,與程式組無關,沒逐條判。

總結:最嚴重等級 minor,blocking 共 0 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/_hookevent.py`
- 我的實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/通才-sonnet/`,請編排者刪除。
