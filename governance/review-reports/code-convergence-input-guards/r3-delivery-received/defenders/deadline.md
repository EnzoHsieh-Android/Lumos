severity: major  
裁決: evidence（現象成立，但不是 `60ad34cb..c09d1203` 這批新增）

- 現象：HIT。`scripts/lumos:46928` 建立 20 秒期限；`scripts/lumos:46868-46871` 把當下剩餘時間傳入 `_codeloop_record_valid_ex`。後者在 `scripts/lumos:46970` 固定成 `_to`，再由 `merge-base`（`:46976-46977`）與 `diff`（`:46992-46993`）依序各使用完整 `_to`。第一支若接近期限才完成，第二支仍可再等待相同時間，整段確實可能接近 40 秒。
- 判準「呼叫端承諾整段截止」：HIT。`docs/lumos-toolchain-knowledge/Projects/合併進主線認合進來那側的留痕_計劃.md:41` 明訂整段共用 `_DISP_BUDGET`，每次 Git 只能使用剩餘時間；`scripts/lumos:46805-46809` 的 helper 註解與計算也一致。
- 判準「由本批新增」：MISS。固定基準 `60ad34cb` 已有完全相同案例：`scripts/lumos:46740-46764` 傳剩餘時間，`scripts/lumos:46858-46886` 又讓兩個子程序各用同一 timeout。到 `c09d1203` 僅因前文增加 107 行而移至上述新行號；`_DISP_BUDGET`、`_merge_side_left`、`_codeloop_merge_side`、`_codeloop_merge_side_lookup`、`_codeloop_record_valid_ex` 的實際函式內容逐字相同。設計計劃檔在兩版的 blob 也相同。
- 上游：審查留痕路徑由 `scripts/lumos:47578-47587` 同步呼叫，沒有外層計時器會在 20 秒強制中止。
- 下游：若差異包含需讀首行的簿記檔，`scripts/lumos:47067-47068` 還會把同一 timeout 傳給批次讀取；其大小與內容兩趟在 `scripts/lumos:29312-29335` 未收到 deadline 時也各自使用完整 timeout，因此問題不只理論上的兩趟上限。

未判定：沒有宣稱實測得到恰好 40 秒。唯讀沙箱拒絕建立指定 `/tmp/lumos-seat-work/...`，故未改到其他位置做延遲注入；結論來自兩個固定提交的實際 Git 物件與完整上下游來源比較。未讀其他席報告或 staging。