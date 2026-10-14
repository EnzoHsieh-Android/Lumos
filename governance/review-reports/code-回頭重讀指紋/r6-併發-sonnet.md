severity: minor

回報範圍:這輪修補(批次排除超過 32MB 或大小缺漏的檔、已算過的不再收)。我在 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp` 的測試夾具上實測了四組。實驗目錄 `cr-rf6-資源/` 已刪。

實測結果:
- **作者數字重現**:8 組各 40MB 的新增檔,檢查總耗時 1.1 秒(作者寫 1.6)。逐檔 diff 只問 1 次、只帶 8 支小檔,8 支大檔全被判「太大」退回舊版,沒有進批次。
- **改上千支一般大小檔**:5 篇筆記共管 1500 支(每支約 20KB),總耗時 1.9 秒,只問 1 次 git diff,5 篇都用新版指紋。30 秒預算綽綽有餘。
- **批次邊界與重算**:要求順序與批次順序相反,路徑參數上限壓小,N=100 時 5 次呼叫,N=300 時 13 次。路徑總數剛好 N+1,每支只 diff 一次,沒有二次方重算。
- **Q0 對照**:Q0 管一支小的新增檔加所有 f 檔,它的結果是新版(101 篇全 v2),這是我自己的情境。

severity: minor
blocking: 否 — 不是這輪修補造成的,而且「一條分支同時改上百篇有關聯筆記」在單人本機工具裡不常見。
引句:「往後收一批(_note_reread_fp_diff_batch)——兩邊大小合計不超過 _NOTE_REREAD_FP_DIFF_BATCH」
問題:這輪修補把檔案那一側的耗時壓平了,但指紋這一步其餘的耗時是跟「改動筆記數」成正比的:每篇筆記各開一次 git 子行程(`_note_reread_diff_once` 每篇約 20ms,另有 `_nodehome_side`)。逐檔 diff 批次只有 1 次,批次化沒有碰到這一塊。
具體失敗情境:300 篇各管 1 支 20KB 檔且各改一行,檢查要 13 到 17 秒。1000 篇要 27 秒,碰到 30 秒減 3 秒預留的上限,其中 685 篇退回「逾時」,只有 315 篇用新版。受影響的是誠實的操作,而且會被判舊版後照擋。修補在逐檔 diff 這一步沒有退步,耗時卡在批次化碰不到的地方。作者的測試只量檔數、沒有量筆記數,所以看不出來。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:37022` ``(`_note_reread_diff_once`,cProfile 顯示 300 次呼叫累計 6.07 秒,另有 `_nodehome_side` 2 次累計 6.29 秒,其餘為子行程等待)。

已讀,無 finding:
- `_note_reread_fp_diff_batch` 的 `wanted` 過濾與 `fpfile` 的 done 檢查。
- `order.index` 與切片在批次數小於等於 N 時是線性。
- `asked` 清單的包含判斷成本可忽略。
- `_diff_git_starts` 與截斷改用 `pairwise` 沒有記憶體放大。
- 單批 64MB 上限下,原始輸出加解碼文字只存一份,與前幾輪相同。

最高等級 minor,blocking 0 條。
