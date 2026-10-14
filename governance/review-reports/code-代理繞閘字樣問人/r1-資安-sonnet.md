severity: major

只有第 1 條發現成立,是一條繞過;其餘各類已看,無。

**1. `--git-dir=X`(黏著寫法)、`--git-dir X` 和 `GIT_DIR=X` 不會改變生效目錄,在暫存目錄裡可對真 repo 繞閘而不被問**
severity: major
blocking: 是

- 誰:被提示注入的代理,或是推送被擋、順手想繞閘的代理。
- 入口:Bash 指令先 `cd` 到暫存根底下(不存在的目錄或非 repo 的目錄),再用 `--git-dir` 或 `GIT_DIR` 指向真 repo 提交。
- 送什麼:`cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git --work-tree=/Users/enzo/real commit --no-verify -m x`
- 拿到什麼:`bypass_reasons` 回空清單,掛鉤放行,提交前閘被跳過而且沒有問人。
- 原因:`_parse_git` 只認 `-C` 來改生效目錄,黏著的 `--git-dir=X` 不是 `_GIT_VALUE_OPTS` 的成員,只被當成一個要跳過的旗標。`GIT_DIR=` 前綴也從不影響 `eff`。於是 `eff` 停在 `/tmp/nonexist`。`_exempt` 走 commit 分支,`_not_real_repo` 看到「目錄不存在」就回 True。
- 計劃的 S3 明列「`cd` 到暫存目錄後又 `git -C` 指回真目錄」要問人。`--git-dir` 是同一件事的另一種寫法,〈範圍〉沒列,所以不算已接受的漏洞。
- 應該是:只要出現 `--git-dir`、`--work-tree` 或 `GIT_DIR`/`GIT_WORK_TREE` 賦值,就不給拋棄式豁免,或把 `--git-dir` 也納入生效目錄的計算。

引句:「黏著的 `--git-dir=X` 不多吃。記下 `-C` 的目錄(可多次,後者相對前者)與 `-c` 的鍵值。」

最小重現(python3.14 用 SourceFileLoader 載入掛鉤,呼叫 `bypass_reasons`):

| 指令 | cwd | 輸出 |
|---|---|---|
| `cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git --work-tree=/Users/enzo/real commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && GIT_DIR=/Users/enzo/real/.git git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && git --git-dir /Users/enzo/real/.git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && env GIT_DIR=/Users/enzo/real/.git git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `git --git-dir=/Users/enzo/real/.git commit -n -m x` | `/tmp/lumos-seat-work` | `[]` |
| `cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git <推送> --no-verify origin` | `/Users/enzo` | `['no-verify']` |

最後一列(推送)有問人,因為 push 只看目標位址,不看目錄;提交、合併、config 這幾類才會漏。

## 逐類結果

**1. 不可信輸入流到危險操作:已看,無可利用的洞。**
- 選項注入:`git -C d` 的 `-C` 與 `d` 分成兩個參數,`d` 以 `-` 開頭也只會被當成目錄值。
- 遠端名稱:`_push_remote_arg` 取第一個不以 `-` 開頭的詞,所以名稱不會以 `-` 開頭。
- 惡意 repo 執行任意碼:我建了 repo,設了 `core.fsmonitor`、`core.sshCommand`,再實跑掛鉤會下的 `rev-parse --git-common-dir` 與 `remote get-url`,標記檔都沒生成。這兩個子指令不碰索引,也不連網。
- 被影響的資料:`remote get-url` 回的位址可被 `url.*.insteadOf` 影響,但真推送也用同一個改寫後的位址,所以判定與實際一致。
- 推論(minor,不阻擋):`get-url` 回的是 fetch 位址,不是 pushurl。真 repo 若設了 `remote.X.url=/tmp/...` 而 `pushurl` 指向真遠端,會被誤判成拋棄式。這需要攻擊者先能改 repo 設定,所以我不單獨立條。

**2. 輸出到使用者:已看,無。**
- 問人理由 `_reason_text` 只用固定字串與命中代號查表,沒有嵌入指令或路徑的原文。
- 存活事件只記 `mark("error", 例外型別名 + 前 120 字)`。例外字串可能含指令片段,但它寫進本機事件帳,不是給使用者看的輸出。

**3. 執行邊界:已看,無。**
- `sys.path.insert(0, 掛鉤自己所在目錄)`:目錄是掛鉤自己的,攻擊者要先能寫 `~/.claude/hooks/` 才有用,那時早已越界。
- `_hookevent` 缺席就退回空殼並照常運作(放行)。
- 安裝名單、錨點簽名、`enforcement` 列都是照既有 hook 的模式加,沒有新寫入面。
- `merge-claude-settings.py` 註冊 `Bash` matcher,並讓 `_codex_entries` 對 Codex 跳過。

**4. 繞過面:除第 1 條外,已看,無新的。**
- 〈範圍〉已列的寫法(別名、變數拼接、`bash -c`、`eval`、指令替換等)我沒有重報。

## 固定席節點逐條判

- `Issues/code-loop守衛main-direct盲區`、`Systems/guard-kill`:不影響。這份 diff 沒碰 `code-loop` 或 `guard kill` 的邏輯。
- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject 保留 sentinel 之外的內容):不影響。`merge-claude-settings.py` 與 `scripts/lumos` 的改動只加了 hook 名單與註冊項,沒有動 CLAUDE.md 的 sentinel 改寫路徑。
- `Systems/lumos-cli-read` ★INVARIANT★(search 排除 superseded):不影響,沒碰 search。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):這份 diff 不違反它。但第 1 條說明 S3 的測試沒涵蓋 `--git-dir` 這條路。
- `Systems/design-loop` ★INVARIANT★:不影響,只動代碼與計劃,沒碰處置閘。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★)與其餘只列名的節點:沒有看到會破壞其行為的改動。

最嚴重 severity: major,blocking 共 1 條。
