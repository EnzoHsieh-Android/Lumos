severity: clean

我沒找到會擋的問題,也沒找到小問題。以下是我驗過的和沒驗的。

**1. 推送行的本機 ref 與遠端 ref 組合**

- **掛鉤只看遠端 ref。** 判主線用的是 `_rref`。`_lref` 只被讀進來,不參與判斷。
- **`_pitfalls_pushed_mainline` 的實跑結果。** 我在 `/tmp` 造了小 git repo,用 `python3.14 -I` 載入 lumos 直接呼叫它:

  | 遠端 ref | 結果 |
  |---|---|
  | `refs/heads/main`、`refs/heads/master` | true |
  | `refs/heads/feat` | false |
  | `refs/heads/` | true |
  | `refs/heads` | true |
  | `refs/tags/v1` | true |
  | 空字串 | true |
  | `refs/for/main` | true |
  | `HEAD` | true |
  | `main` | true |
  | `refs/remotes/origin/main` | true |
  | `refs/heads/main/x`、`refs/heads/feat/main` | false |
  | `refs/heads/Main` | false |
  | 帶非 ASCII 字元的分支名 | false |
  | 5000 字長的分支名 | false |
  | 結尾帶空白的 `refs/heads/main ` | false |

  不是 `refs/heads/` 開頭的一律 true,保守照全套。`Main` 大小寫不同判 false,遠端是 GitHub 就區分大小寫,不算洞。
- **刪除行。** 掛鉤對 `local_sha` 全零的行直接 `continue`,不會進到判斷。
- **混推。** 其中一個 ref 是 main 就整次推送照全套。`_SUITE_BRANCH_DOWN` 即使被前一個功能分支設成 1,降級說明也要求最終模式是 light 才印。
- **新補的兩個不同名案例前置成立。** 我把掛鉤複製到臨時目錄,把 `--pushed-ref "$_rref"` 改成 `"$_lref"`,再跑 `t_prepush_feature_branch_mixed_with_main`。結果 `FAILED(2 條斷言)`,`feat:main` 和 `main:feat` 兩條都翻紅。所以它們真的在守「看遠端不看本機」。這兩條放在同一個 repo、同一份改動裡配成對照組,`main:feat` 能證明這份改動原本會降成子集,`feat:main` 的「照全套」不是因為場景本身就算不出範圍。
- **`_down` 新值 `spec_light` 與 `feature_branch`。** 掛鉤裡 `_down` 只做 `-n` 判空,沒有任何字串比較。測試檔裡沒有引用它。

**2. 呼叫點拆包**

- **`_ppfb_harness` 多回 `kg` 之後。** `scripts/test_lumos.py` 裡 7 個呼叫點全都改成 5 值拆包。其中只有 `ppfb-light` 那支用到 `kg`,其他用 `_kg`。`ppfb-uncomputed` 那支先前拆成 `_a2`,現在是 `_kg`,沒有撞名。
- **測試實跑。** 在 push-subset 跑 `-k prepush_feature_branch` 得 `22 passed, 0 failed`,跑 `-k pitfalls_pushed_mainline` 得 `9 passed, 0 failed`。

**3. 圖譜鏡頭,逐篇判**

這 8 篇我只讀了硬合約行(`★INVARIANT★`)和與推送閘有關的行,沒有逐篇讀全文。

1. `Issues/code-loop守衛main-direct盲區`:講的是 tier 判斷用 merge-base 範圍。這份 diff 沒碰 code-loop check 的範圍算法,只加降級,不影響。
2. `Systems/pitfalls-code-loop`:`pitfalls --json` 只新增欄位(`pushed_mainline`、`suite_computed`),沒動分級與 lint 路徑,不影響。
3. `Systems/bound-tests-gate`:合約是「綁定測試逐支真跑,紅或懸空就擋」。這份 diff 沒碰 `code-loop check`。本機推功能分支少跑全套,由 PR 的 CI 補,合約本身不受影響。
4. `Systems/lumos-cli-read`:合約是 `search` 預設排除 superseded。與這份 diff 無關,不影響。
5. `Systems/design-loop`:合約是處置閘的條款綁測試。這份 diff 沒碰,不影響。
6. `Systems/guard-kill`:合約是 `guard kill` 的 rc 優先序與 JSON 純度。這份 diff 沒碰,不影響。
7. `Systems/lumos-cli-lifecycle`:合約是 re-inject 不動 sentinel 外內容。無關,不影響。
8. `Systems/測試假綠形態`:合約要求還原翻紅的測試要有前置斷言證明現場成立。新補的 `main:feat` 對照案例就是這個前置,我上面的變異實驗證明兩條會翻紅。

另外我用 grep 找舊句「CI 會跑全套當後盾」、「CI 會兜底」、「嫌久可」。程式、README、ARCHITECTURE 都已無殘留,只剩計劃筆記在引述舊句。

**修補鏡頭三問**

- **原問題的修復效果,有何行為證據?** 有。修前(判主線看本機 ref)的行為我用變異版掛鉤重現,兩個不同名案例都翻紅。修後的行為是 22 條測試全綠。
- **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。同名的功能分支、推 main、混推、舊版 lumos、算不出範圍都在 22 條裡。
- **新發現的同一案例,修前、修後各是什麼結果?** 本輪沒有新 finding。

**未驗範圍**

- 沒在真的遠端 repo 實跑。
- 沒跑全套測試。
- 沒驗遠端預設分支是 `develop` 這類主線候選的路徑。`t_pitfalls_pushed_mainline` 有一條「遠端 HEAD 指的 trunk」,我只確認它在 9 條裡通過。

過程中有一個小意外:我收尾時用 `pkill -f 'until ! pgrep -f'` 想停自己的等待迴圈,這個模式可能也比對到別的會談的程序。我沒有證據它真的打到別人。

清理:我的臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/邊界-sonnet` 和變異實驗留下的 `/private/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-run-b2ez2xcz` 都已刪除。刪之前 `lsof` 確認沒有程序開著。
