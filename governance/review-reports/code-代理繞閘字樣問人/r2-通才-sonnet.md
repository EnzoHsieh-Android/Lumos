severity: minor

審的是程式組全份加掛鉤全文(載入 `bypass-ask-hook.py` 實測,修前版本用 b5be3aad 存到臨時目錄對照)。沒找到 blocker 或 major。主要的繞過路徑(`--no-verify` 與縮寫、`-n` 短旗標組、`-c`/`--config-env`/`GIT_CONFIG_*`、`git config` 寫入與拆除、`LUMOS_SKIP_*` 的各種前綴)正常寫法都會問。四個新加規則各有一條縫,另有一條新增的誤問。

## Findings

1. 新規則「lumos 在段裡任何位置都認」造成誤問(修補引入的回歸)
severity: minor
   blocking: 否
   - 引句:「lk = next((k for k in range(i, len(seg)) if _lumos_at(seg, k)), None)」
   - `_skip_before` 用 `_SKIP_ASSIGN.match(w) for w in seg[:end]` 掃 lumos 詞之前的每個詞,不限賦值位置。所以 `grep -n "LUMOS_SKIP_NOTE_SHAPE=1" scripts/lumos` 或 `rg "LUMOS_SKIP_X=1" scripts/lumos` 會被判成設了跳過。這個 repo 常用這類 grep 查跳過旗標。
   - 預期放行,實際回 `['lumos-skip']`。
   - 歸因:有證據的修復回歸。
     - 修前版本同一條指令回 `[]`。
     - 修後版本回 `['lumos-skip']`。
     - `grep -rn LUMOS_SKIP_X=1 docs scripts/lumos`、`grep -c "LUMOS_SKIP_X=" scripts/lumos` 同樣如此。
     - `cat scripts/lumos | grep LUMOS_SKIP_X=1` 兩版都放行(lumos 在另一段)。
   - 應該只認「賦值出現在命令前綴」的詞,或把 lumos 詞限定為被執行的那個詞(直譯器之後的第一個非旗標參數)。

2. 「推送看推送位址」:省略使用者名的 scp 式位址在暫存目錄會被當成本機路徑
severity: minor
   blocking: 否
   - 引句:「if "://" in url or re.match(r"^[^/]+@[^/]+:", url):」
   - 只有 `user@host:path` 被排除。`aliashost:Org/Repo.git` 或 `github.com:Org/Repo.git` 這種靠 ssh config 補使用者的寫法,會被 `os.path.join(eff, url)` 接在暫存目錄後面,判成暫存根底下。
   - 重現:`git -C r1 remote add aliasr aliashost:EnzoHsieh-Android/Lumos.git`,`r1` 在 `/tmp/lumos-seat-work/...`。
     - `bypass_reasons("git push --no-verify aliasr main", r1)` 回 `[]`,等於放行。
     - 同樣的位址換成 `user@example.com:a/b.git` 回 `['no-verify']`。
   - 這正是計劃〈量測〉裡說暫存目錄有真工作副本對真遠端推送的情形。
   - 歸因:有證據的原有漏查。修前版本同輸入也回 `[]`,不是這輪造成的。
   - 另一個窄縫:`git remote set-url --add origin /tmp/x` 只加一個位址,推送仍會送到原本的真位址,但掛鉤用 `added[origin]=/tmp/x` 豁免。
   - 同理 `git remote add origin /tmp/b; git push ...`:`origin` 已存在時 add 會失敗,掛鉤仍當 origin 是暫存。

3. 「同指令建過」與「`$(mktemp -d)` 直接當目標」各有縫:都放行,真實目錄上的提交會漏問
severity: minor
   blocking: 否
   - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
   - 3a. 只看指令替換內文的第一個詞:
     - `cd $(mktemp -d && echo <真repo>) && git commit -n` 回 `[]`。
     - `cd $(mktemp -d; cd <真repo>; pwd) && git commit -n` 回 `[]`。
     - 這兩條寫法不自然。
   - 3b. `mktemp -d -p <真repo>`、`mktemp -d ./scratch.XXXX`、`mktemp -d --tmpdir=<真repo>` 建在 repo 工作樹裡的新目錄,仍被當暫存而豁免。`D=$(mktemp -d ./scratch.XXXX) && cd $D && git commit -n` 回 `[]`,但 `$D` 其實在真工作樹裡。
   - 3c. `mkdir /tmp/a && ln -s <真repo> /tmp/a/x && cd /tmp/a/x && git commit -n` 回 `[]`:「同指令建過」的目錄底下被放了符號連結。
   - 歸因:有證據的原有漏查。3a、3b 修前同輸入結果一樣。

4. 匯出的 `GIT_DIR`、`GIT_WORK_TREE` 不被追蹤
severity: minor
   blocking: 否
   - 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
   - 只認同段內聯的賦值。
   - `export GIT_DIR=<真repo>/.git; cd /tmp; git commit -n` 回 `[]`。`GIT_WORK_TREE` 同樣。
   - 先 `cd` 到 mktemp 目錄再 `export GIT_DIR=...` 也回 `[]`。
   - 歸因:有證據的原有漏查。修前版本結果相同。
   - 計劃〈做法〉只寫了同段賦值,所以這是文件與實作一致但有縫,不是不一致。

5. 未閉合 `$(` 的效能退步,〈做法〉宣稱的「2 萬字最壞 0.11 秒」不成立
severity: minor
   blocking: 否
   - 引句:「def _match_paren(text: str, i: int) -> int:」
   - `_replace_cmdsubs` 對每個沒配對的 `$(` 呼叫 `_match_paren`,每次掃到尾,所以是平方時間。
   - 重現:`"$("*9000 + " git commit -n"`(約 18000 字)耗時約 2.5 秒。2 萬字上限內純 `"$("*9990` 約 3.1 秒。
   - 修前版本同輸入約 0.01 秒。
   - 結果仍正確(`commit-n`)。掛鉤預算是 5 秒,慢機或有負載時可能超時,超時就放行。
   - 歸因:有證據的修復回歸(兩版耗時如上)。
   - 修法:`_replace_cmdsubs` 一次預算配對表,或第一次找不到配對就停止再找。

## 已驗的正向主張

以下都在修後版本實測,輸入與預期都符合:

- 縮寫:`--no-verif` 與 `--no-verify` 命中。`--no-ver`、`--no-ve`、`--no-v` 在 git 2.39 都不被接受(實測印出用法說明),所以預篩從 `--no-veri` 起算沒有漏。
- `-n` 判斷:
  - `-qn`、`-anm`、`-m x -S -n`、`-F msg -n`、`--amend -C HEAD -n`、`-C . commit -n` 命中。
  - `-m "x" -- -n`、訊息裡的 `-n`、`git log -n 5 && git commit -m x` 不誤問。
- 設定與環境變數:
  - `-c core.hooksPath=` 的大小寫、引號、空值、`--config-env=` 命中。
  - `GIT_CONFIG_KEY_0=core.hooksPath` 與 `GIT_CONFIG_PARAMETERS` 命中。
  - `git config` 的 `--get`、只給鍵、`-l`、`grep` 不誤問。
  - `--unset`、`--unset-all`、`--add`、`--replace-all`、`--worktree`、`--global` 寫入命中。
- 包裝與前綴:`env`、`sudo`、`timeout`、`command`、`\git`、`/usr/bin/git`、子殼層、`&&`、管線、續行都能找到 git。
- `LUMOS_SKIP_*`:前綴、`export`(含分行)、`env -i` 命中;`bash -c`、`lumos-foo`、`lumos.sh` 不誤問。
- 暫存放行:
  - `/tmp` 實驗 repo 裡的 `git commit -n`、`git config core.hooksPath`、`git -C <暫存repo> commit -n`、`mktemp -d && git init && commit -n` 都放行。
  - 這個 repo 的審查席暫存目錄也放行。
  - `cd` 回真 repo、`cd ..`、`cd -`、`pushd`、`$OLDPWD`、不存在的目錄、`--git-dir`、`--work-tree`、`-C <真repo>`(含 `~`、`$HOME`)都仍問。
- 暫存目錄裡的 clone:
  - 對真遠端 `git push --no-verify` 仍問。
  - 只在 clone 內提交放行。
- 一般的 `git push origin HEAD`、`git commit -m` 在預篩就停,不誤問。
- heredoc 內文與引號內的字樣不誤問;`echo git push --no-verify` 會問,屬計劃明載的刻意誤問。

## 配對案例(修前、修後)

| 案例 | 修前 | 修後 |
|---|---|---|
| `grep -n "LUMOS_SKIP_X=1" scripts/lumos` | `[]` | `['lumos-skip']`(finding 1,新增誤問) |
| 未閉合 `$(` 約 18000 字 | 約 0.01 秒 | 約 2.5 秒(finding 5) |
| `aliasr` 推送到 scp 式遠端 | `[]` | `[]`(finding 2,未變) |
| `export GIT_DIR=...; cd /tmp; git commit -n` | `[]` | `[]`(finding 4,未變) |
| `LUMOS_SKIP_X=1 timeout 5 lumos doctor`、`... sudo lumos doctor` | `[]` | `['lumos-skip']`(正向改善,屬 lumos 任何位置都認的預期效果) |

## 對三問的回答

1. 原問題的修復效果:
   - 「lumos 任何位置都認」修了 `timeout`、`sudo` 前綴漏問,見上表第 5 列。
   - 「推送看推送位址」,pushurl 與 fetch 位址不同的情形我沒有另建案例驗,未判定。
2. 修補處的相鄰呼叫路徑:正常、錯誤與相鄰路徑仍成立,例外是上面 finding 1 與 5。
3. 新發現的同一案例修前修後的結果:見上表。

## 固定席節點

- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill` 的 ★INVARIANT★:判不影響。這些 INVARIANT 都是關於 `scripts/lumos` 的 search、re-inject、處置閘、測試假綠與 guard kill,本輪程式組只新增獨立掛鉤與 `_hookevent.py` 的修剪暫存檔改為獨立名字(`tempfile.mkstemp`),沒碰這些行為。我沒有逐條驗證 INVARIANT 的綁定測試。
- `Issues/code-loop守衛main-direct盲區`:這輪改動沒有碰 main 直推守衛,判不影響。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★,牽連 `scripts/lumos`):程式組沒改 `scripts/lumos`,判不影響。
- 其餘「超出上限只列名」的節點:我沒有逐篇讀。

## 未驗範圍

- `test_lumos.py` 新增的測試沒有逐條跑,也沒有確認它們是否涵蓋 finding 1 與 5。
- 文件註冊組沒讀。
- Windows 路徑、`safe.directory` 造成 rev-parse 失敗被誤當「不在 repo」的情形沒測。

最嚴重等級 minor,blocking 共 0 條(5 條 finding 都是 blocking:否)。
