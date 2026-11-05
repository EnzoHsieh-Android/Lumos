severity: minor

沒有會擋的問題。有一條 minor 的邊界發現(下面 finding),其餘邊界我都驗過、行為合理。

**驗證方式。** 我在 `/tmp` 建了一個臨時 repo(遠端 Lumos、本機 `refs/remotes/Lumos/main`、分支 feat 改了 `scripts/a.py`)。接著用 push-subset 的 `scripts/lumos pitfalls --diff main..HEAD --no-lint --json --pushed-ref <ref>` 逐一跑。沒有走完整掛鉤(掛鉤迴圈的行為只讀程式推論,沒有實跑)。

| `--pushed-ref` | `pushed_mainline` |
|---|---|
| `refs/heads/feat`、`feature/main`、`main2`、`trunk`、`develop`、`refs/heads/HEAD`、`refs/heads/a b` | false |
| `refs/heads/main`、`master` | true |
| `refs/tags/v1`、`refs/notes/x`、`refs/remotes/Lumos/main`、空字串、`refs/heads/` | true(偏保守,照全套) |

- 以上每一種輸出都帶 `suite_computed: true`。
- 遠端 HEAD 指向 `Lumos/trunk` 後,`refs/heads/trunk` 變成 true。
- 主線集合不看遠端名,遠端叫 Lumos 也能認出 main。

**其他邊界(程式推論)**
- 探測 `grep -q -- 'dest="pf_pushed_ref"' "$GRAPHCTL" 2>/dev/null`:符號連結會被跟隨;不存在或不可讀時 grep 回 2,`_PF_PR` 維持 0,結果是不帶旗標、照全套,方向安全。
- `"pushed_mainline": *false` 的 grep:輸出是單行 JSON,字串裡的引號都被跳脫成 `\"`。檔名或分支名裡就算寫了 `"suite_computed": true`,也湊不出連續的 `"suite_computed":`,不會誤中。
- 10 秒預算逾時時,`_note_reread_mainline_names` 只剩固定的 main、master。推 main 照樣 true,不會被降級;只有非標準主線名會受影響(見 finding)。
- 刪除分支(本機 sha 全 0)被迴圈跳過;新分支首推走原本的範圍推導,`suite_computed` 為 false 時照全套。
- 多 ref:標籤 ref 回 true,所以「功能分支加標籤」會全套;「功能分支加 main」在計劃 [S3] 有綁測試。
- 範圍算不出來時 `computed` 為 false,不降級,方向安全。

**manifest 的 3131 筆 lint 全是 `scripts/test_lumos.py` 的既有存量。** 我沒逐筆對行號,只看到檔案與規則分布;diff 在該檔只有兩個 hunk(80228 的一行、125261 起的 182 行新測試),沒看到 diff 範圍內有新增的真隱患。判誤報。

**圖譜鏡頭。** 讀了 diff 與計劃 [S1]–[S8],沒有逐篇 `lumos show` 那 8 篇固定席節點,也沒對 INVARIANT 逐條比對。以下只是依 diff 範圍的判斷:
- diff 只改測試範圍的挑選;tier=high 的代碼審守衛(`pitfalls-code-loop`、`code-loop守衛main-direct盲區`)、`doctor`、`note-shape`、`spec-gate` 這幾道在迴圈裡原樣保留。降級發生在它們之後,而且只動 `_suite_this`,所以這幾道不受影響。
- `bound-tests-gate`:改的是測試範圍選擇,但沒核對它的 INVARIANT 原文。

---
severity: minor
blocking: 否
標題:遠端 HEAD 沒設且預設分支不叫 main/master 時,直接推預設分支會被降成功能分支
引句:「分支短名在 _note_reread_mainline_names 的集合裡(永遠含 main、master,再加主線候選指到的分支名,不看遠端名)→ true;其他 → false。」
`scripts/lumos` 約 61995 行(`_pitfalls_pushed_mainline`)。
失敗場景:repo 預設分支叫 `trunk` 或 `develop`,`refs/remotes/<遠端>/HEAD` 沒設(`git init` 加 `remote add` 的 repo 常見,clone 則會設),推 `refs/heads/trunk` 時我實跑得到 `pushed_mainline: false`。掛鉤因此降成文件子集加關鍵字子集,並印「合併一律走 PR」。但 CI 的 push 事件只認 main 與 tag,`trunk` 直推既不跑本機全套、也沒有 CI 兜底。
本 repo 是 main,不受影響,所以降為 minor。⚠ 我不確定這個掛鉤有沒有被消費專案沿用,沒有證據可判。
