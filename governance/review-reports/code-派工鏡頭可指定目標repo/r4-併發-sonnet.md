severity: clean

這輪修補沒有資源類問題,以下是實測結果。

**上限 5000 加兩種寫法的耗時**
- 實驗用 `_spec_commit_present` 直接呼叫,放在掛鉤 30 秒預算內跑。
- 5000 個候選在提交裡都存在,每個候選用帶重音字母(NFC 與 NFD 寫法不同),實際送出 10000 行,耗時約 3.1 秒。
- 候選全不存在時約 2.3 秒。
- 候選給到 2 萬個時,耗時不變(3.18 秒),只會多回報「超過上限」,沒有隨候選數增長。
- 在本 repo 這種大 repo 上查 5000 個不存在的候選,約 1.0 秒。
- 最壞情況用掉的時間遠低於 `_LENS_SPEC_BUDGET`(30 秒)。

**命中後的 ls-tree**
- 每批 200 個路徑,命中 5000 個約 25 批,每批前都會檢查 `deadline`。
- 剩餘不到 1 秒時回 None,呼叫端當成「算到一半」,不會把誠實的操作擋掉。

**逾時收子行程**
- `_nodehome_cat_sizes` 用 `subprocess.run(timeout=)`,逾時會殺掉 git 子行程,沒有孤兒行程。
- `_lens_git` 的作法相同。
- 輸入走 stdin 由 `communicate` 處理,10000 行不會卡死。

**`_nodehome_cat_sizes` 擴充對原用途的影響**
- 唯一改動是多接 `ValueError`(路徑字串有編不回去的代理字元時),這種情況原本會直接崩潰,現在回 None。
- 耗時與行為對節點認家那些呼叫點沒有變化。
- 呼叫點在 `scripts/lumos`:32635、36606、38596。
- 呼叫端 36606 有 `or [None]*len(...)` 接 None,38596 另有逾時預算,都吃得下 None。

**記憶體**
- 候選最多 5000 個,擴成 10000 個指令字串,量很小。

已讀範圍:`scripts/lumos` 的 `_nodehome_cat_sizes`、`_spec_commit_cands_norm`、`_spec_commit_present`、呼叫端 `cmd_dispatch_lens_spec`,以及 `_lens_git`。其餘部分,包括字元集重構、`_vault_node_check`、`_spec_commit_rev_ok` 與符號連結訊息,也已讀,無 finding。

實驗目錄已刪除。

最高等級 clean,blocking 0 條。
