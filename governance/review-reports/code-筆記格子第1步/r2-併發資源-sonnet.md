severity: clean

併發與資源鏡頭:沒有找到能重現的新問題,第 1 輪的 K1(起點版本逐篇各開一次 git)已確實修掉。我在乾淨 clone `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/r2k` 重量了一次,對照組是 r1 版本的 `c5fc9870:scripts/lumos`(同一個 clone、同一批提交)。方法是在 PATH 前面放一個 git 包裝腳本,每次呼叫都記一行,再用 `/usr/bin/time -l` 量時間與記憶體。

**量測結果(舊版 = 第 1 輪審的 c5fc9870,新版 = 本輪 440af7a4)**

| 場景 | 舊版 | 新版 |
|---|---|---|
| 推送,300 篇只改正文 | 301 次 `git show`,12.5 秒 | 1 次 `git show`,2.6 秒 |
| 推送,240 篇各新寫一行缺格子的 WHY | 約 334 次 git,13.6 至 16.8 秒 | 34 次 git(其中 `cat-file` 2 次),2.6 至 3.2 秒 |
| 大範圍推送,615 檔、約 11.8 萬行新增,格子上線點在範圍最後(對應 pre2 最壞情況) | 615 次 `git show`,31.6 秒,248 MB | 約 40 次 git,6.1 秒,258 MB |
| 提交時單次跳過,暫存 436 篇 | 436 次 `git show`,17.1 秒 | 約 18 次 git,1.8 秒 |
| doctor 完整事後掃描,112 個提交 | 21.1 秒,342 次 `show` | 11.8 秒,12 次 `show` |

- **起點版本批次讀取。** `_ns_base_summary_lines` 只讀「摘要有新寫行」的那幾篇,用 `_nodehome_cat_blobs` 一次讀完。呼叫次數不再隨筆記數成長。
- **doctor 剩下的時間。** 11.8 秒大部分是原有的逐提交 `diff` 與 `diff --name-status`,各 112 次;那是 `_notelines_range_added` 本來的行為,不在這次 diff 裡,而且受 200 個提交的上限(`_NS_DOCTOR_SCAN_CAP`)限制。
- **pre2 的代價。** 新增約 10 MB 記憶體(248 MB 到 258 MB),時間可忽略。pre2 只收範圍內、格子還沒上線的提交所寫的行,範圍有界。
- **單次跳過前的計算。** 436 篇暫存只多一次 `cat-file`,新增 `MERGE_HEAD` 的判斷只是一次 `rev-parse`。
- **子集測試。** `python3.14 scripts/test_lumos.py -k slots` 在 rw 上 99 項全過,最慢的 `t_slots_push_old_lines` 約 10 秒。

**排查過、判不影響的項目**
- 治理帳的 `slots_missing` 鍵來自 `slot_check_keyed` 回傳的格名,而格名來自 `_SLOT_KEYS` 白名單(`slot_parse` 只認白名單鍵),所以鍵數有界,不會因亂寫的鍵無限長大。
- 輸出量有上限:格子違規最多印 20 條(`_NS_SLOT_SHOW`),doctor 最多列 10 處。
- 批次讀取失敗(逾時、或路徑含換行)回 None,整段格子檢查跳過並印一句。我造了路徑含換行的筆記試過,它不在圖譜清單裡,不會把其他缺格子行一起放過。
- 只放連結行的舊行比對(`_ns_is_old`)是 O(新行數 × 舊行數)。實測 3000 乘 3000 約 0.5 秒;真實規模(幾百到幾千條)不構成問題。
- `_ns_deleted_summary_lines` 接續行用 `out[-1] +=` 串接,理論上是二次方。實測要連續 2 萬行縮排刪除行才到 0.5 秒,實務上不會碰到。
- `old_by` 與 `pre2` 的行有重疊(`lines` 裡會重複算),只是多算一次比對,沒有失敗場景,不標。

**圖譜鏡頭(固定席)**
- 計劃〈效能〉(`docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:185`)寫「一批起點版本讀取」。實作現在照做,上一輪我標的 K1 與計劃不一致的地方已消除。
- `lumos impact --diff` 列出的 `★INVARIANT★` 家(`lumos-cli-read`、`lumos-cli-lifecycle`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`節點範圍與索引守衛` 等):本鏡頭看的是資源與時序,這次 diff 沒有改它們管的行為,對併發與資源面不影響。
- 計劃〈天花板〉第 7 條新增的敘述(整行複製缺格舊句也算舊行)只涉及判定語意,不涉及資源面。
- 這次沒發現哪句筆記跟程式對不上,不需要另立 Issue。

最高嚴重度 clean,blocking 0 條
