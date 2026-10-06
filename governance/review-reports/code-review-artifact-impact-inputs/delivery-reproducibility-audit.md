# 第三輪卷證與修正關卡乾淨下載重驗核對

核對日期：2026-10-06  
分支：`fix/review-artifact-impact-inputs`  
角色：唯讀 `lumos_reviewer_code`

## 結論

**不能完整按照既有規格重驗。**

可重驗的部分：

- 第三輪凍結材料、正式席報告、prompt 與帳面指紋完整。
- 四份有引句的報告執行 `quote-check` 全部 rc 0、`miss=0`。
- correctness、architecture 兩個正式席執行 `seat-check` 都是 `unreported=[]`、`out_of_scope=[]`。

不足的部分：

- `r3-fix.json` 需要的基準提交 `9a6e21e…` 不存在於這份乾淨、非 shallow clone，因此 fresh `fix-check` 會在測試前失敗。
- 原席報告的未釘版 `file:line` 已漂到修正後內容；現有 `refcheck` 的 rc 0 只能證明「現在那一行存在」，不能證明原引句仍在該行。
- 唯一改成 `path@commit:line` 的 UTF-8 正式報告，反而因 `9a6e21e…` 缺失而 `refcheck` rc 1。

帳上既有的 r3 pass 可能仍可被讀側沿用，但那不是乾淨環境重新執行修正關卡。

## Findings

### A-1 — severity: blocker；blocking: 是

**第三輪 fix-check 的必要 base commit 沒有隨發布分支可達。**

逐字引句：

> `"base": "9a6e21e49a96677db09286a63beaf38f381a0104"`

佐證：

- `governance/review-reports/code-review-artifact-impact-inputs/r3-fix.json:2` 將修正前基準釘在 `9a6e21e…`。
- `r3-dispatch.json:2` 的 `base_commit`、`:56` 的 repair-check head，以及 `r3-materials.json:3` 的 frozen head 都是同一提交。
- `scripts/lumos:12709-12713` 先解析 base；失敗時逐字輸出：

  > `擋下:修正紀錄的 base ... 轉不成這個 repo 裡存在的提交`

- `git rev-parse --is-shallow-repository` 輸出 `false`。
- `git cat-file -e 9a6e21e…^{commit}` 為 rc 128。
- `46ec9e7…`、`77ad08f…`、`ca6701b…` 也不存在；main `56f38db…`、修正通過版本 `532b32d…` 與 HEAD `b15b16d…` 存在。
- CLI 到 `scripts/lumos:12732` 才計算 `base..head`，`:12738` 才建立隔離工作樹，`:12803-12880` 才跑測試與合約。因此它會在所有實質重驗之前硬退出。
- `r3-fix.json` 列出的八個唯一測試名目前都存在於 `HEAD:scripts/test_lumos.py`；阻塞點是 Git 基準物件，不是測試遺失。

影響：

- 無法重算修正範圍。
- 無法在隔離工作樹重跑 r3 測試與受波及合約。
- `r3-dispatch.json` 和 `r3-materials.json` 雖保存 patch 與指紋，仍不能從 Git 還原當時提交。

最小補法：

1. 不修改已綁 hash 的原始報告、intake、snapshot 或 canary 帳列。
2. 讓 `9a6e21e…` 成為待發布 branch 的可達祖先。只保存 loose object 或 tag 不夠：`scripts/lumos:27961-27975` 還要求釘版提交被本地／遠端追蹤 branch 包含，而且接手流程使用 `--no-tags`。
3. 若要保留整理後的樹，最小 Git 形狀是加入一個「樹不變、第二父為 `9a6e21e…`」的歷史承載 merge。
4. 在新的最終程式 HEAD 重跑 r3 `fix-check`，再只追加既有慣例的 `chore(lumos): 記錄代碼審通過` 帳本提交。
5. 重新以 `--no-local --single-branch --no-tags` clone，確認 `git cat-file -e 9a6e21e…^{commit}` 與正式 `fix-check` 都是 rc 0。

若另外三個舊提交不是 `9a6e21e…` 的祖先，也需讓它們透過可抓取 branch 歷史保留下來；否則相關舊版本比較只能說由 patch／指紋支持，不能宣稱可由 Git 物件重驗。

### A-2 — severity: major；blocking: 是

阻擋範圍：原始 `file:line` 精確重播；不阻擋 snapshot 引句錨定。

**原報告的未釘版行號已漂移，但 refcheck 仍會回 rc 0。**

逐字引句：

> `引句:「一般改名仍取新路徑；只有簿記終點被排除時，不能把舊程式刪除一起藏掉。」`
>
> `file: scripts/lumos:24432`

佐證：

- 上述內容位於 `r3-correctness.md:7-9`。
- `r3-architecture.md:7-9` 同樣引用未釘版的 `scripts/lumos:24433`。
- 現在 `scripts/lumos:24432-24435` 已是修正後內容：

  > `# 一般改名仍取新路徑；簿記終點未確認是程式時，保留舊側角色證據。`
  >
  > `if (new in _BOOKKEEPING_FILES or new.startswith(_BOOKKEEPING_DIRS))`

- 實跑 correctness `refcheck` 為 rc 0，但 excerpt 是上述修正後文字；architecture 的 `24433` excerpt 只剩 `out += ...`。
- `r3-orchestrator-utf8-draft.md:7-8` 引用 `candidates = ...`，卻指到 `scripts/lumos:41345`；目前該行逐字是：

  > `return 2`

  該 draft 的 `refcheck` 仍為 rc 0。
- 正式 `r3-orchestrator-utf8.md:8` 已使用正確形狀 `scripts/lumos@9a6e21e…:41342`，但因 A-1 缺物件，`refcheck` 為 rc 1、`missing=1`。
- `scripts/lumos:23860-23875` 的 `_validate_repo_ref` 只判檔案存在與行號範圍；`scripts/lumos:40066-40078` 也只在 missing 或 out-of-range 時回 rc 1，不比對引句與 excerpt。

仍可成立：

- 兩段改名引句存在 `r3-source.patch:20,46`。
- UTF-8 引句存在 `r3-source.patch:247`。
- 完整 snapshot 對應位置為 `r3-snapshot.patch:23753,23779,23980`。
- 四份報告對 snapshot 的 `quote-check` 都是 rc 0、`miss=0`。

因此可以重驗「引句確實來自凍結審材」，不能重驗「原 Git 版本的該行正是這句」。

最小補法：

1. 保持 ledger 綁定的原始報告不變，避免破壞 `report_sha256`。
2. 在同一卷證目錄新增一份非席位、非新輪次的 reproduction manifest，把每條原引用寫成 `path@9a6e21e…:line`。
3. 完成 A-1 後，對 reproduction manifest 跑 `refcheck`；原報告繼續對 snapshot 跑 `quote-check`。兩項都通過才足以證明引句與 Git 座標。

## 重驗矩陣

| 項目 | 結果 | 實證 |
| --- | --- | --- |
| source／graph／snapshot 完整性 | 可成立 | SHA-256 與 708／358／24441 行均吻合 |
| prompt 完整性 | 可成立 | 兩個 SHA-256 均吻合 dispatch |
| 正式席報告完整性 | 可成立 | correctness／architecture hash 均吻合 canary 帳 |
| 引句是否在凍結 snapshot | 可成立 | 四份 quote-check 均 rc 0、miss 0 |
| 正式席是否觸及派工材料 | 可成立 | 兩份 seat-check 均無 unreported/out_of_scope |
| UTF-8 編排者報告 seat-check | 不當成正式席判定 | 它不是獨立 seat；實跑會列兩份 material unreported |
| 原始 Git file:line 精確對應 | 不足 | 未釘引用已漂；釘版引用因缺物件 rc 1 |
| r3 fix-check fresh rerun | 不成立 | base 9a 無法解析，會在測試前 rc 2 |
| 帳上既有 r3 pass 沿用資料 | 足夠，但非 fresh rerun | 532 commit 存在、record hash 相符、其後僅純簿記提交 |

## 實際命令與退出碼

| 命令 | rc | 摘要 |
| --- | ---: | --- |
| `pwd` | 0 | 位於指定乾淨 clone |
| `git status --short --branch` | 0 | 正確分支，未列工作樹改動 |
| `git rev-parse HEAD refs/remotes/origin/main refs/remotes/origin/fix/review-artifact-impact-inputs` | 0 | `b15b16d…`／`56f38db…`／`b15b16d…` |
| `git rev-parse --is-shallow-repository` | 0 | `false` |
| `git cat-file -e <sha>^{commit}` 驗 9a／56f／46ec／77ad／ca67／b15 | 1（彙總） | 9a、46ec、77ad、ca67 個別 rc 128；56f、b15 個別 rc 0 |
| `git cat-file -e 532b32d…^{commit}; git cat-file -t 532b32d…; git rev-parse HEAD^` | 0 | 532 是 HEAD 第一父 |
| `git show -s --format=... HEAD refs/remotes/origin/main` | 0 | 確認 HEAD、main 與父提交 |
| `git show --format=... --name-only HEAD` | 0 | HEAD 只含治理帳與 r3 卷證 |
| `git show 9a6e21e…:scripts/lumos >/dev/null` | 128 | 無法取出舊 source |
| `shasum -a 256 r3-source.patch r3-graph.patch r3-snapshot.patch; wc -l ...` | 0 | hash 與行數全符 materials manifest |
| 報告、snapshot、prompt 的 `shasum -a 256` | 0 | 全符 dispatch／canary 帳列 |
| `refcheck r3-architecture.md --repo . --json` | 0 | 4 ok，但 excerpt 是目前內容 |
| `refcheck r3-correctness.md --repo . --json` | 0 | 4 ok，但行號已指向修正後內容 |
| `refcheck r3-intake.md --repo . --json` | 0 | 0 claims |
| `refcheck r3-orchestrator-utf8-draft.md --repo . --json` | 0 | 41345 被判 ok，實際是 `return 2` |
| `refcheck r3-orchestrator-utf8.md --repo . --json` | 1 | pinned 9a claim missing 1 |
| 四份報告各自執行 `quote-check --spec r3-snapshot.patch --json` | 全部 0 | 全部 miss 0 |
| correctness／architecture 各自執行 `seat-check --dispatch r3-dispatch.json --json` | 全部 0 | unreported/out_of_scope 皆空 |
| 兩份 UTF-8 報告執行同一 seat-check | 全部 0 | 各列兩份 material unreported；CLI 此檢查為觀測性 rc 0 |
| `git show HEAD:scripts/test_lumos.py \| rg '^def <測試名>\('`，逐一核對八個測試 | 0 | 八個測試名全存在 |
| 查 `docs/.canary-log.jsonl` 的本 loop 帳列 | 0 | 找到 r1–r3 與 r3 三筆收貨資料 |
| 查 `docs/.governance-log.jsonl` 的 fix-check 事件 | 0 | 找到 r3 warned 與 532 passed |
| `shasum -a 256 r3-fix.json` | 0 | `478e4c…`，與 532 passed 事件相同 |

## 未執行事項

- 未執行 `lumos loop fix-check`，避免寫治理帳。
- 未執行第四輪代碼審或重跑功能測試。
- 未讀其他本機工作目錄或 archive refs。
- 未 checkout、fetch、reset、commit 或操作 remote。
- 未修改專案內容。