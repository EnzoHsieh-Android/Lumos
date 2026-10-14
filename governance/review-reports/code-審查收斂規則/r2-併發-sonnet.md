severity: minor

我讀了程式、實測了大圖譜的耗時與記憶體,也用奇怪的 `[residual:]` 指標灌過寫索引那段。效能、寫索引的原子性、鎖都沒有問題;主要發現是 git 逾時或失敗時退路的方向不一致。

**實測用的資料**
- 副本是 932 篇筆記加 20MB 治理帳,另外灌了 1200 條帶殘留的合約。
- `_residual_scan` 約 0.18 秒。
- `_residual_index_entries` 約 0.1 秒。
- `_residual_index_write` 約 0.26 秒。
- `_doctor_residual_lines` 約 0.28 秒。
- 記憶體尖峰約 176MB。
- 空圖譜下 `guard residual --reindex` 約 1.2 秒。
- 整個 `doctor` 要 24 秒、尖峰 1.5GB,但那是既有的基線,殘留這段只占 0.3 秒。
- 實驗副本已刪除。

severity: minor
blocking: 否 — 只發生在 git 本身失敗或逾時,退回的是改動前的分級,不是新增的放行路徑
引句:「    except (OSError, subprocess.TimeoutExpired):」
問題:`_residual_tier_hits` 裡 git 失敗時的退路方向不一致。
- `_residual_diff_touches` 在 git 逾時或回傳非 0 時回 True,也就是寧可多升 high。
- 同一支函式裡的 `git diff --name-only`(逾時或非 0)直接 `return out`,命中檔案清單是空的,等於放行。
- `_residual_index_read_at` 對起點版本的 `git show`:逾時 20 秒回 "bad",非 0 一律回 "missing"。起點索引因此變成空集合,`removed`(拿掉殘留)判斷和起點索引裡守的檔都一起失效。
具體失敗情境:
- 起點版本在淺層 clone 裡不存在,或大範圍 diff 逾時。
- 起點索引被當成空的,拿掉殘留的推送不會被點名。
- 名單命令逾時,`files` 的命中清單為空。
- 結果就是分級退回沒有殘留機制之前的樣子,沒有任何訊息。
- 頂端索引壞掉有 `head_bad`,起點讀不到卻沒有對應的旗標。
建議:`git show` 逾時或非 0 且不是「檔案不存在」時回 "bad",並新增 `base_bad` 之類的旗標;`--name-only` 失敗也比照 `_residual_diff_touches` 當成碰到。
佐證:``file: `scripts/lumos:44396` ``、``file: `scripts/lumos:44472` ``

severity: minor
blocking: 否 — 重跑會自癒,doctor 會抓出索引過期
引句:「            _residual_reindex_tail(env, "沒有這個標記")」
問題:`--remove` 在「沒有這個標記」這條路上,補索引成功時什麼都沒印,仍回 2。使用者看不出索引已經補好了。
另外,`_residual_index_write` 只接 `ValueError`、`RuntimeError`、`OSError`。合約行寫完後,若 `Env` 載入或 `_residual_index_entries` 丟出其他例外,會出現 traceback 而不是「合約行已寫、索引沒更新」。
我用 10 種怪指標(含 NUL、5000 字元、`..`、全形)試過,沒有一個丟例外,所以這是防禦性的觀察。
在合約行寫完、索引寫入前按 Ctrl-C,也只會留下過期索引。重跑 `--add` 的「已經有了」路徑,或 `--reindex`,都能補好。
佐證:``file: `scripts/lumos:19195` ``、``file: `scripts/lumos:19107` ``

已讀,無 finding:
- 鎖的範圍:`--reindex` 與 add/remove 都在 `_vault_write_lock` 內,巢狀可重入。
- 索引用 `_write_lf` 的暫存檔加 `os.replace`,中斷時會清掉暫存檔,不會寫一半。
- 每次 `guard residual` 重建整份索引的成本,在上面的規模下可以接受。
- `_residual_diff_touches` 的整字比對:1200 個名字掃 10 萬行約 0.09 秒。
- doctor 與 pitfalls 的時間、記憶體在大圖譜下沒有問題。

最高等級 minor,blocking 0 條。
