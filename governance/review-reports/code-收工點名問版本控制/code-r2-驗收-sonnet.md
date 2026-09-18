severity: blocker

# 代碼審 r2 驗收報告(全新一席,sonnet)

## 新發現

### 1. 任意指令執行的修法沒堵住同一支檔裡的另一條路,而且這批改動把那條路的觸發面變寬了

severity: blocker
blocking: 是

`_git()` 把 `core.fsmonitor=` 關掉,確實擋住了 `_git_status_entries` 與 `_head_shebang` 這兩個新呼叫點(已實測驗證,見下方「驗收結果」)。但同一支檔的閘門 3 在圖譜被動過時會呼叫 `_impact_missing()`,那個函式用 `subprocess.run` 另外起了一個 `lumos impact --diff HEAD --sync-check` 子行程(`scripts/hooks/claude/check-graph-sync.py:747`),而 `scripts/lumos` 內部對應的 `cmd_impact_diff`(`scripts/lumos:25233`)呼叫 `git diff --name-only` 時只帶了 `-c core.quotePath=false`,**沒有**帶 `-c core.fsmonitor=`。我對這條路做了端到端實測:造一個惡意 `core.fsmonitor` 設定的 repo,工作樹上有一支未提交的程式碼檔 `scripts/keep.py` 和一篇未提交的圖譜筆記 `docs/t-knowledge/Systems/s.md`,直接跑真正的 `check-graph-sync.py`(`LUMOS_STOP_BLOCK_OFF=1`,不影響這條路徑),證據檔被建出來、內容是攻擊者指定的字串:
```
proof exists AFTER running the real hook end-to-end: True
proof content: pwned
```
更嚴重的是,這批改動本身把閘門 3 的觸發條件從「這一輪透過工具動過圖譜」放寬成「工作樹上有任何未提交的圖譜筆記」(`scripts/hooks/claude/check-graph-sync.py:989`),換句話說這條沒堵住的路,被這次的修改客觀上變得更容易踩到——只要工作樹上剛好留著一篇沒 commit 的筆記(常態,不是特例),`_impact_missing` 就會被呼叫。

引句:「這支檔其他地方的版本控制呼叫沒有走這條路,是否要一併收攏另案處理。」

這句誠實聲明本身沒錯(承認了缺口存在),但把它定性成「另案處理」低估了風險——它跟 blocker #2 是同一種漏洞(任意指令執行),而且透過這次擴大的閘門 3 觸發條件,實測上比修復前**更容易**被踩到,不應該留到下一批。

### 2. 收工點名的「去重」機制在 decision:block 那一輪不存檔,同一批未提交檔實際要講兩次才會被抑制

severity: minor
blocking: 否

`_save_printed(sid_for_dup, printed_key)` 只出現在函式最後的 stderr 分支(`scripts/hooks/claude/check-graph-sync.py:1073-1074`),`stop_block_decision` 為真、真的印出 `decision:block` 那條路徑在函式中途就 `return 0`(`scripts/hooks/claude/check-graph-sync.py` 的 `if stop_block_decision(...): ... return 0` 區塊),不會走到底部存檔。實測同一個 session 連續三次呼叫、工作樹狀態不變:第 1 次印 `decision:block`(不存檔)、第 2 次印 stderr 提醒(這才存檔)、第 3 次才被抑制——不是設計註解說的「同一批檔第二次就不再講」,而是第三次才不講。因為 `decision:block` 本來就受另一道 session 標記檔保護、一個 session 只擋一次,這個落差只會讓 stderr(模型看不到的除錯日誌)多印一次,不影響模型看到的內容,故列 minor。

引句:「同一批檔第二次就不再講(清單已經不限這一輪,不抑制會變成每輪刷屏)」

## 驗收結果(四條逐條)

**1. 中文檔名(轉義成八進位)**:**修好了**。直接呼叫 `_git_status_entries` 對含中文檔名 `scripts/收工點名.py` 的新檔查詢,回傳的相對路徑就是原樣中文、`(root / p).exists()` 為真。另外查了這支檔裡所有會呼叫版本控制的地方(`grep subprocess.run`),`_head_shebang` 走同一個 `_git()` 共用函式所以也在保護範圍內;`_impact_missing` 呼叫的外部 `lumos` CLI 本身在自己的 git 呼叫上早就有 `-c core.quotePath=false`(`scripts/lumos:25233` 那行本身就帶,一併確認過),所以「還有沒有別的路徑吐出轉義檔名」這題本身答案是「沒有」——中文檔名這條修得完整。

**2. 任意指令執行**:**修了但有新問題**。`_git()` 對它保護的兩個呼叫點(`_git_status_entries`、`_head_shebang`)確實擋住了——實測：先用未加 `-c core.fsmonitor=` 的裸 `git status --porcelain -uall` 對惡意設定的 repo 查一次,證據檔被建出來;再用 `_git_status_entries`(帶防護)查同一個 repo,證據檔不會被建出來、查詢結果仍正常回傳。但如上面新發現 #1,同一支檔的閘門 3(`_impact_missing`)完全沒有這層防護,而且是本批改動自己把它的觸發條件變寬——這條「已知會執行指令的設定項」實際上沒有被真正堵死,只是換了個入口繼續開著。「純 clone 不會帶到該設定」這句誠實聲明本身查證屬實(`git clone` 後 `core.fsmonitor` 確實是空的,已實測)。

**3. 模型那條訊息(交集→完整清單)**:**修好了**。直接呼叫 `stop_block_reason` 傳入用 shell 改出來的檔案清單,產出的 reason 文字裡確實列出了檔名(不再是空交集)。措辭本身量過長度:典型情況(1–2 支檔)整段落在 300–400 字元,遠低於 1500 字元上限,不會被截斷;句子偏長但語意完整,沒發現會讓模型誤解成「不用補筆記」的明顯歧義用詞。

**4. 排除規則對刪除的檔失效**:**修好了,沒找到新的誤判**。用 `_entry_is_code` 對「`dist/bundle.js` 被刪除」重跑,正確判定排除(`False`);同時刻意造了兩個容易誤傷的邊界案例——`mydist/file.js`(路徑含 `dist` 但不是真的 `dist/` 目錄)、`a/dist/deep.js`(巢狀在子目錄底下的真 `dist/`)——前者正確判為「仍是程式碼」(`True`)、後者正確判為「排除」(`False`),跟未刪除檔案原本的 `is_code_file` 邏輯行為一致,沒有發現這個改法引入新的誤判。

## 第一輪留痕抽查(三條)

- **#7 死碼**(`touched_graph_via_cli` 沒人呼叫):**屬實**。`grep -n "touched_graph_via_cli"` 全檔只剩函式定義本身(`scripts/hooks/claude/check-graph-sync.py:444`),測試檔裡也沒有任何呼叫,確實是「留著但沒人用」。
- **#5 三個時機表第一列同步**:**屬實**。`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md` 的「三個時機」表第一列已改寫成「工作樹上還沒提交什麼」語意,並補了整段「★2026-09-18 起:第一個時機的清單改成問版本控制★」說明,跟程式碼現況(問版本控制而非列舉工具名)一致。
- **#9 抽出共用函式 `_git()`**:**屬實**。`_git_status_entries`(`status --porcelain -uall`)與 `_head_shebang`(`show HEAD:<path>`)確實共用同一個 `_git()`,而且兩處分別正確使用 `text=True`(預設)/`text=False`,沒有發現參數混用導致行為跑掉的問題。

## 總結

最嚴重等級:blocker(1 條,新發現 #1)。blocking 共 1 條。
