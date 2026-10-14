severity: minor

我實測了三處,都在單人使用的威脅模型下不會直接放行壞東西,所以沒有 major。三條 finding 都是 minor。

severity: minor
blocking: 否 — 只多花時間,而且批次讀整批的記憶體有 64MB 上限,指紋結果不受影響。
引句:「base["blobs"] = blobs = _note_reread_fp_prefetch(scan, base, oid)」
問題:`_note_reread_fp_prefetch` 的讀取順序是候選 about_code 鍵的全域排序(`blob_order`),但指紋實際走的順序是候選篇的順序,再加每篇內的排序鍵。兩個順序不一致時,每支缺檔都會換掉整批,再從它起讀下一個 64MB。
失敗情境:我造了 120 支約 0.96MB 的檔,合計 109MB。
- 照順序走:2 批、0.1 秒。
- 反序走(候選 A 列到排序靠後的檔,候選 B 列到靠前的檔):120 批、7.5 秒,每批約 64MB。
- 檔案更多時耗時線性增加。時間會耗到推送前檢查的 30 秒上限,後面的篇被判逾時。這一條接到第三條:逾時的篇不擋。
- 記憶體沒爆,仍是一批約 64MB 再乘兩三倍。
- 觸發條件是頂端內容合計超過 64MB 且單支在 1MB 以下,約 70 支以上的 1MB 檔,或幾百支 100KB 的檔。
佐證:``file: `scripts/lumos:36575-36620` ``(實驗腳本已刪)

severity: minor
blocking: 否 — 只發生在單檔接近 32MB 上限的病態輸入,而且只多花時間與記憶體。
引句:「lines = data.split(b"\n", mx)[:mx]」
問題:縮排鏈的計算沒有檢查截止時間。對 32MB 以內的檔(單檔上限 `_NOTE_REREAD_FP_MAX`),`data.split` 會一次切出全部行,再用純 Python 迴圈掃到最大的起點行。
失敗情境:我直接呼叫 `_note_reread_hunk_tags`,hunk 放在檔尾。
- 32MB 的純空行:2.6 秒,峰值 RSS 約 600MB。
- 32MB 的 `x\n`:3.5 秒。
- 31MB 的 ` x\n`:5.4 秒,累計峰值 RSS 約 1.5GB。
- 1MB 的單行、1MB 的 tab 前綴、1400 層階梯縮排加 1399 段改動:都在 0.01 秒內,沒問題。
- 批次讀取的結果已在手上時,這段計算完全不碰 git,所以不受 `deadline` 約束。幾支這樣的檔就能讓推送前檢查的 30 秒軟上限失效。
- 檢查 deadline 的位置也沒到這裡,每支檔之間沒有檢查,只靠 git 呼叫。
佐證:``file: `scripts/lumos:36633-36700` ``

severity: minor
blocking: 否 — 這是設計取捨,原作者已明講;但逾時判定的位置讓它的觸發面比文件寫的大。
引句:「late = set(res.get("late") or ())」
問題:`late` 是 `why == "逾時"` 的所有篇,也就是 `_note_reread_blocking` 內所有因逾時沒算出新版指紋的篇都豁免。
- 豁免的來源不只是文件說的「指紋這一步花掉約 27 秒」。
- `_note_reread_fp_base` 的 `--raw` diff 或查大小逾時,會讓所有候選的 `why` 都是「逾時」,整個第一層變成不擋。
- 第一條的反序讀取、第二條的大檔掃描,都會把原本算得出的篇推進逾時,於是被豁免。
失敗情境:大改動加慢速磁碟,或只是多幾支大檔,第一層的擋就整個變成提醒。第二層 `must` 不受影響。帳上有 `late` 欄可事後查。
佐證:``file: `scripts/lumos:37673-37686` ``

已讀,無 finding:
- `_nodehome_cat_blobs_capped` 的 `sizes` 參數。傳入 None 的那一支不讀;`start` 單支不超過 1MB,所以一定進得了總量上限內,不會空轉。
- 縮排堆疊與雜湊 memo。深度最多約 1400 層,共用外層只算一次。
- `inf` 邊界與 CRLF 空行。
- 順序一致時的批次數,是 2 批。

最高等級 minor,blocking 0 條。
