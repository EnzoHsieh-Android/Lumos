severity: major

白話:這輪把截止時間傳進了核可鏈驗章和多數 git 呼叫,也把鏈長改成超過就擋。這幾處我都實測過,行為正確。但提交樹快照的一個迴圈沒有檢查截止時間,實測超過 60 秒預算。這個迴圈修補前就有,不是這輪造成的。

## 1. 快照裡每個符號連結 .md 都另起一次 git,迴圈不看截止時間
severity: major
blocking: 是

引句:「def _secev_tree_mode_link(tree, path):」

這段在修補差異裡只是上下文,函式本身沒改。

- **失敗場景**:被推的提交樹在 `docs/x-knowledge/Systems/` 下有 N 個符號連結的 `*.md`。`_secev_snap_md` 對每個符號連結呼叫一次 `_secev_tree_mode_link`,而它每次都跑 `git ls-tree`。這個迴圈沒有 `deadline` 檢查,內部的 `_nodehome_git` 用預設的 20 秒逾時,也沒吃整道預算。
- **現象**:`_secev_evaluate` 宣稱每個 ref 只有 60 秒預算,並在逾時時回 `evaluation_timeout`。這個迴圈只能等它自己跑完,中間不會被截止。
- **重現**:用 `git fast-import` 造 3000 個符號連結 `.md`,再用 `SourceFileLoader` 載入 `scripts/lumos` 後呼叫:

```
_secinv_snapshot_tree(repo, sha, "docs/x-knowledge", deadline=time.monotonic()+60)
```

結果:
- 修後版 7655a12d:耗時 80.45 秒,errors 為 3000 筆 `symlink_rejected`,maxrss 346MB。
- 修前版 b99f52c8:耗時 76.69 秒,結果相同。
- 單次 `git ls-tree` 約 20 毫秒。
- 放大到 10000 筆約 500 秒(⚠ 外推,沒實跑);檔數上限 `_VAULT_SAFE_ENTRIES_MAX` 是 50000,更久。
- 最後還是擋(`symlink_rejected` 在 `_SECINV_READ_KINDS` 內)。問題只在 pre-push 卡住,沒有逾時回報。

歸因:有證據的原有漏查。修前修後的兩版查證命令與耗時都在上面。修補沒碰這個迴圈,但修補宣稱的「截止時間傳到每個外部呼叫與每個迴圈」在這裡不成立。

## 回答三問

**①原問題的修復效果有何行為證據?**
- **驗章截止時間**:`_secapr_verify` 傳入 `deadline=now+1.0` 驗 2000 筆鏈,1.00 秒時丟出 `_SecevTimeout`。逾時後 `pgrep ssh-keygen` 沒有殘留行程,因為 `subprocess.run` 逾時會殺掉子行程並等它結束。
- **鏈長上限**:`_secapr_parse` 對 40000 行的輸入直接丟 `_SecaprTooLong`(0.06 秒,不是默默截斷)。呼叫端 `_secev_stage_chain` 把它轉成 `read_incomplete` 擋下。
- **單檔過大**:設定檔、核可鏈、工具清單超過單檔上限時走 `read_status`,回 `too_large` 後擋下,不再當成沒有這支檔。
- **巢狀深度**:`_secev_loads` 對 8M 層的 list 與 dict 都丟 `RecursionError`,0.02 秒,被當成壞行。
- **快照檔數上限**:60000 個 `.md` 時 1.97 秒,errors 是 `too_many_files`,它在 `_SECINV_READ_KINDS` 內,所以 `read_complete` 為 false 而擋。
- **整棵樹**:`_SecevTree` 列 40 萬檔耗時 0.59 秒、maxrss 299MB。

**②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- **核可鏈 2000 筆全走 ssh-keygen 驗章**:17.25 秒,maxrss 50MB,在 60 秒預算內。程式註解寫「約 13 秒」,本機實測約 17 秒,數字偏舊但不影響結論。
- **主線版與推送版分岔**:只有主線第一筆有效時才會分岔,而分岔會在驗完主線後立刻返回,所以兩條鏈不會各驗 2000 筆。實測 16.53 秒。
- **相鄰仍成立**:`_secapr_verify_sig` 先查快取再查截止時間,快取命中不受影響。逾時時先丟 `_SecevTimeout`,不被當成驗章失敗。

**③新發現的同一案例在修前、修後各是什麼結果?**
- 發現 1 修前 76.69 秒,修後 80.45 秒,結果相同,歸因為原有漏查。

## 已驗與未驗範圍

**備註(不另立 finding,沒有具體失敗場景)**:
- 一行 16MB 的寬 JSON 解析後 maxrss 達 814MB(約 50 倍放大),3.1 秒。這在單檔上限內,沒有失敗,只是峰值偏高。
- `_git_is_shallow(timeout=20)` 沒有取剩餘預算,可能超出 60 秒預算至多 20 秒。逾時時 `TimeoutExpired` 沒被它自己接住,會落到 `evaluation_error` 而擋下。
- `_SECAPR_MAX_ENTRIES` 降到 2000 後,鏈滿 2000 筆就不能再追加,也沒有收尾或壓縮的路徑。

**未驗**:
- 沒有跑端到端的 `_secev_evaluate`,只直接呼叫內部函式量測。
- 多程序併發不審。
- `_secev_depth` 在 git 失敗時回 -1,被 `ctx.depth` 的 `max(..., 0)` 吞成 0,我沒構造出可重現的壞場景。

最嚴重 severity:major,blocking 共 1 條

暫存已清:兩個 detached worktree 和 `/private/tmp/lumos-seat-work/code-安全證據閘與資安格子/資源-sonnet` 都用字面絕對路徑刪除。
