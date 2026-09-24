severity: minor

## F1 兩邊合併信賴 remerge-diff,但淺層複製(shallow clone)缺父提交時會靜默給出錯誤結果(非誤擋而是可能漏擋)

severity: minor
blocking: no

這條不是 r2 這次新增的程式碼造成的(r2 只把 remerge-diff 限縮到 `len(parents) == 2`,沒有動 `_nodehome_merge_own_changes` 本體),但 r2 的圖譜筆記與 docstring 把「兩邊合併」定調成精確判法,值得記一筆殘留風險。

引句:「只算它自己多改的:兩邊合併用 git 的 remerge-diff(跟 git 自動合併會產生的結果比,兩邊都改過、git 自動合起來的」

實測(`/tmp/shallowsrc` 建一段有合併提交的歷史,再用 `git clone --depth 1 --no-single-branch file:///tmp/shallowsrc /tmp/shallowclone2` 造出只有合併提交本身、拿不到任何上一版物件的淺層複製):
```
git show --remerge-diff --format= --name-status -z HEAD
→ 退出碼 0,印出 "A f.txt"(不是 "M f.txt")
```
`git show --remerge-diff` 在缺父提交物件時**不會失敗、也不像章魚合併那樣印警告**,而是把整支檔判成新增(A),等於把合併提交裡「其實沒動、只是父提交讀不到」的檔也算進「自己改的」路徑集合——跟這次修的章魚合併問題同一種「靜默給錯結果、退出碼還是 0」形狀,只是這次方向可能是多算(誤擋)而非漏算。

不升級成 blocker/major 的原因:①`_nodehome_git` 只在 `returncode != 0` 時回 `None`(`scripts/lumos:21622`),這條路目前確實會被讀成「有結果」而非退回舊判法,但②`.github/workflows/ci.yml:16` 已設 `fetch-depth: 0`,CI 端跑不到這個情境;會踩到的只剩「人在本機用淺層複製跑 `lumos home check --diff`」這種罕見操作。建議之後有空順手补:remerge-diff 前先確認 `git rev-parse --is-shallow-repository` 是 false,是的話跟章魚合併一樣回 `None` 退回舊判法。

## F2 已驗過、沒問題的部分

引句:「rm = _nodehome_merge_own_changes(repo_root, sha) if len(parents) == 2 else None」

- 實跑新測試 `t_nodehome_octopus_merge_own_violation_still_blocked`:兩次(patch 原樣 / 把 `if len(parents) == 2` 條件拔掉還原成 r1 版本)對照,拔掉後第二個斷言翻紅(`提醒:src/a.py 改了...`,rc 從 1 變成非 1),證實這支測試真的測到「章魚合併退回舊判法」這條路,不是靠別的原因過。
- 直接在 `/tmp/octoexp` 造一個三個上一版的章魚合併、在合併提交裡順手多改一個檔,跑 `git show --remerge-diff --format= --name-status -z`:輸出只有 `diff: warning: Skipping remerge-diff for octopus merges.`(印到 stderr)、`--name-status` 本體是空的、退出碼 0——跟作者說法逐字對得上,`len(parents) == 2` 這個切法是必要且正確的防線。
- 額外測了幾種「重點攻擊」點名的情境,兩個上一版時 remerge-diff **都正常給出正確結果**(不是靜默空):
  - 二進位檔衝突(`/tmp/binconf`):`M` `b.bin` 正常列出。
  - 改名同時改內容衝突(`/tmp/renconf`):`M` `renamed.txt` 正常列出(用 `-M` 有抓到改名)。
  - `--allow-unrelated-histories`(`/tmp/unrelA` + `/tmp/unrelB`):`M` `a.txt` 正常列出。
  這三種都沒有重現「退出碼 0 但空結果」的問題,只有章魚合併(F2 驗過)與淺層複製(F1)兩種。
- 退回舊判法那條路(`per = [...]; paths = set.intersection(...)`,`scripts/lumos:21943-21950`)本身沒被這次 patch 改動,但用 `t_nodehome_octopus_merge_own_violation_still_blocked` 的現場核對它對章魚合併算得對:合併提交裡改的 `src/a.py` 跟 main/x/y 三個上一版都不一樣 → 交集裡有它 → 照擋,語意跟兩邊合併版一致。
