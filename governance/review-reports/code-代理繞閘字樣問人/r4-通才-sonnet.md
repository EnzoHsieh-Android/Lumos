severity: minor

我只找到一條問題,屬於「誤問」方向,而且是修補後新出現的。(甲)方向(代理用正常寫法讓掛鉤放行真繞閘)沒有找到,證據在最後。

## Finding

1. 指令裡只要有一個空字串參數(`''` 或 `""`),切詞就會當掉,整條指令退回「照字面看」的粗判。結果是不該問的指令被問,拋棄式豁免也一起失效。

引句:「k = min(t.index(c) for c in "<>" if c in t)   # `)>`、`;>`:前面是分隔、後面是導向」

severity: minor
blocking: 否

- 走到哪一行:`_tokens` 新增的 `elif all(c in "();<>|&\n" for c in t)` 分支。posix shlex 把 `''` 切成空字串 `""`,`all()` 對空字串為真,接著 `min()` 對空序列丟 `ValueError`。`bypass_reasons` 接住這個錯誤後改走 `_literal`,而 `_literal` 不看拋棄式、不看旗標位置。
- 重現,載入修後掛鉤,cwd 是真 repo:
  - `bh.bypass_reasons("sed -i '' 's/LUMOS_SKIP_X/LUMOS_SKIP_Y/' scripts/lumos", real)` 回 `['literal']`。
  - `sed -i '' 's/--no-verify/x/' docs/lumos-toolchain-knowledge/Projects/a.md` 和 `sed -i "" 's/hooksPath/x/' scripts/lumos` 同樣回 `['literal']`。
  - 實跑掛鉤主程式,stdin 給 PreToolUse 事件,`sed -i '' 's/hooksPath/x/' scripts/lumos` 輸出 `permissionDecision: "ask"`。
  - 對照:`git commit -m '' --author x` 回 `[]`,因為預篩沒命中,根本沒進分類器。
- 影響:macOS 上 `sed -i ''` 是慣用寫法。改 `scripts/lumos` 或這個 repo 的 docs 時,只要樣式裡有三個字樣之一(`--no-veri`、`hookspath`、`lumos_skip_`),就會被問。路徑有 "lumos" 就滿足 `_literal` 的 git/lumos 前提。另外,拋棄式 repo 裡 `git commit -n -m x --author ''` 也會被問。模擬第 1 次實驗:`git commit -m x -n --author ''` 修前回 `['commit-n']`,修後回 `['literal']`,在暫存目錄也會被問,拋棄式豁免沒起作用。
- 應該是:空字串詞要先排除。例如在 `_tokens` 對 `t == ""` 直接 `out.append("")`,或讓分支要求 `t` 非空。
- 歸因:有證據的修復回歸。修前版本(9b8ce146)的 `_tokens` 沒有這個分支。同一批指令:
  - sed 三條:修前 `[]`,修後 `['literal']`。
  - `git -C /tmp/lumos-seat-work/x commit --no-verify -m ''`:修前 `['no-verify']`,修後 `['literal']`。

## 三問

① 原問題(`)>`、`;>` 這類分隔符黏著導向)的修復效果,我沒有拿修前版本逐案對照,只驗了修後行為:
- `2>/dev/null`、`>/dev/null`、`2>&1`、`&>`、`|&`、`2>>log`、`<&-`、`1>&2` 接在 `git config core.hooksPath` 後面,全部回 `[]`(讀設定不誤問)。
- `git push --no-verify >/dev/null 2>&1` 回 `['no-verify']`。

② 修補處的相鄰路徑:只有上面那一條回歸。空字串詞也會讓 `git config core.hooksPath ''` 這類寫入退到 `literal`。它仍然問人,所以不是漏問,只是理由代號變粗。

③ 新發現同一案例,修前 `[]`、修後 `['literal']`,見上面的對照。

## (乙)日常指令誤問:已驗無誤問

- 暫存目錄實驗 repo,remote 指向另一個本機裸庫:`push --no-verify origin HEAD`、`-u`、`-f`、`--repo=`、直接給 bare 路徑、`../bare.git` 相對路徑、`-C` 加子目錄,全部放行。
- 暫存目錄的 `commit -n`、`cd 實驗目錄 && 多段 git 鏈`、`gctl-run-1/r` 這種路徑,全部放行。
- 只有網路 remote 或沒有 remote 的 repo 才問,方向正確。
- 回真 repo 的第二段仍會問:`cd exp && commit -n && cd real && commit -n` 的第二個 `commit -n` 回 `['commit-n']`。
- `grep`、`rg` 搜 `--no-verify`、`core.hooksPath`、`LUMOS_SKIP_*`,以及 `grep -rn ... 2>/dev/null | head`,放行。
- commit 訊息裡提到 `--no-verify`、`-n`、`LUMOS_SKIP_X`、`core.hooksPath`,包括 `$(cat <<'EOF'...)` 的 heredoc 訊息,放行。
- `-S<keyid含n>`、`-m "-n"`、`--author 'A -n'`、`-- -n`,放行。
- `git config --get`、`--get-all`、`--list`、`--show-origin`、`--type=path core.hooksPath`、`--get remote.origin.url`,放行。
- 完整掛鉤(含預篩)實跑,耗時約 0.06 到 0.12 秒。

## (甲)真繞閘:未找到放行寫法

- 已攔住的正常寫法:
  - `--no-verify` 放在任何位置、`-n`、`-an`、`-sn`、`-nm`、`--amend -n`。
  - `-c`、`--config-env`、`GIT_CONFIG_KEY_n`、`GIT_CONFIG_PARAMETERS`、`export` 各種形式。
  - `git config core.hooksPath` 的各種寫入、`--unset`、`--add`、`-f`、`--worktree`、`set` 新語法。
  - `LUMOS_SKIP_*` 作前綴,或搭配 `env`、`/usr/bin/git`、`export`。
  - `(cd exp && true); git commit -n`(子殼層 cd)仍會問。
  - 同一條指令先 `remote set-url` 或 `remote add` 再推送,不給豁免。
- 縮寫 `--no-ve`、`--no-ver` 不是繞法。我在實驗 repo 實測,git 回 129 拒絕這些縮寫,`-ccore.hooksPath=` 也是 `unknown option`。
- ⚠ 以下是小的攔不到點,計劃〈範圍〉沒明列,交編排者判斷是否補進範圍,我不認為是 blocking:
  - `set -a; LUMOS_SKIP_X=1; git push` 回 `[]`。
  - `export LUMOS_SKIP_X=1; unset LUMOS_SKIP_X; lumos doctor` 會誤問,因為 `unset` 沒處理。
  - 用 Bash 對 `scripts/hooks/pre-push` 做 `chmod -x`、`rm`、`sed -i`。〈範圍〉只承認 Edit/Write 這類非 Bash 工具改閘檔,且事後 `anchor verify` 抓得到。

## 固定席節點

- `Issues/code-loop守衛main-direct盲區`、`Systems/lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`:不影響。
  - 這輪我讀的程式組只有 `bypass-ask-hook.py` 和 `_hookevent.py`,沒碰 search 濾網、re-inject sentinel、處置閘、guard kill 的 rc 優先序與 `--json` 純淨度。
  - `_hookevent.py` 本身的 diff 我只在檢視全檔時看過,沒對 hunk 逐行比對。
- `測試假綠形態` 的「前置斷言證明現場成立」:上面這個空字串回歸顯示現有測試沒有覆蓋空字串參數。補紅測試時,要在斷言前先證明走的是 `_tokens` 分支,而不是 `_literal`。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(`scripts/lumos`):這組程式沒改到,不影響。

未驗範圍:併發與資源(他席負責)、`scripts/lumos` 與 `merge-claude-settings.py` 的註冊,以及測試文件組。

最嚴重等級:minor,blocking 共 0 條。

所有實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/通才-sonnet/`,請編排者刪。
