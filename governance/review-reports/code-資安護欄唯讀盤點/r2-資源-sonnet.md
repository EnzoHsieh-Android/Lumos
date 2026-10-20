severity: major

# 資源席報告(r2-資源-sonnet)

這份報告只改了格式,內容照前一版。三條 finding 都定為 major、blocking 是。F2、F3 維持 major,理由寫在各條判準裡。

共用派工詞當時缺檔,我先依資源.txt、`r2-repair-binding.json` 與 `r2-intake.md` 工作,後來才補讀〈輸出格式〉。

表態查證:py-memory 寫「沒有會成長的模組狀態,沒有無上限快取」,依 F1 實測不成立。

## 總結

這輪修復的資源面主張有實測證據,可以成立。但有一個耗盡記憶體的洞,另有兩個二次方熱點,三個都是修前就有的原有漏查。

白話講:64MiB 的總量上限只管「讀進來多少」。壞資料產生的錯誤清單沒有上限,幾 MB 的輸入就能把機器記憶體吃光。

## Findings

### F1 錯誤清單沒有數量上限,8MB 輸入吃掉 5GB 記憶體

severity: major
blocking: 是

判準:輸入上限(單檔 2MiB、總量 64MiB)被設計成資源的天花板,但輸出端的錯誤數量沒有上限,輸入 8MB 就能讓輸出放大約 100 倍、記憶體放大約 600 倍,所以擋。

歸因:有證據的原有漏查(修前 7.3GB、修後 5.25GB,修復只縮小了單則大小,沒碰數量)

引句:「errors.append(_vault_issue("invalid_record", rel, line=line, id=safe, detail="; ".join(probs)))」

佐證 file: `scripts/lumos:7106`(版本 aadf6b07)。`_secinv_collect` 內,每個畸形控制項各記一筆,`errors` 沒有數量上限,JSON 與文字模式都完整輸出。`_secinv_blocks` 裡每個畸形圍欄也各記一筆,同樣不封頂。

失敗場景:
- 輸入:4 篇各約 2MiB 的 Systems 筆記,內容是 `{"schema_version":1,"controls":[{},{},…]}`,每篇約 52 萬個空物件。
- 指令:`lumos --vault … security list --json`。
- 預期:輸入約 8.4MB,輸出與記憶體都在同量級,或錯誤被截斷。
- 實際:279 萬筆 `invalid_record`,輸出 813MB,峰值 RSS 5.25GB,耗時 24 秒,rc=2。推到 31 篇(64MiB 上限內)約需 40GB,等於 OOM。
- 同一類:31 篇各約 2MiB 的 `` ```lumos-security-v1 ``(尾端帶空白)畸形圍欄,得 250 萬筆 `malformed_block`、輸出 455MB、RSS 2.9GB。
- 同一類:帶前綴的 `> ```lumos-security-v1` 變體行,得 283 萬筆、輸出 448MB、RSS 2.8GB。
- 文字模式(同一個畸形圍欄 vault):輸出 357MB、耗時 44 秒、RSS 2.8GB。

兩版查證(同一案例):
- 修前 `20293afe`:空物件案例 4 檔,279 萬筆、輸出 1.18GB、RSS 7.30GB、16.6 秒。
- 修後 `aadf6b07`:同案例,279 萬筆、輸出 813MB、RSS 5.25GB、24.4 秒。
- 畸形圍欄案例 31 檔:修前 RSS 2.90GB、8.7 秒,修後 RSS 2.90GB、13.3 秒。
- 修後變慢,是因為新加的 `_json_text_escaped` 要多掃一遍輸出。
- 單一 `{}` 的 detail 修前 245 字,修後被 `_secinv_names` 截短,但筆數照舊。

建議:每個節點最多記 N 筆錯誤,超出的併成一筆「另有 M 筆同類」;或每塊控制項在跑 schema 前先設個數上限。

### F2 inventory 的 assets/surfaces 重複檢查是二次方

severity: major
blocking: 是

判準:單一 1.8MB 的合法登記檔(在單檔上限內)就讓指令跑 17 秒,且隨項目數成平方成長,沒有任何上限保護;我維持 major,因為它跟 G7 已修的 `_secinv_check_links` 是同一類,修復漏掉這一處。

歸因:有證據的原有漏查(修前修後都是二次方)

引句:「if it["id"] in ids:」

佐證 file: `scripts/lumos:7127`(版本 aadf6b07)。`ids` 是 list,每項都線性掃一遍;G7 只把 `_secinv_check_links` 的集合改成預先建好,漏掉這一處。

失敗場景:
- 輸入:一份約 1.8MB(5.5 萬個 asset)的 inventory 區塊。
- 預期:秒內完成。
- 實際:`security list` 跑 16.95 秒,RSS 約 300MB。

兩版查證:

| 項目數 | 修前 | 修後 |
|---|---|---|
| 5000 | | 約 +0.3 秒 |
| 10000 | | 約 +1.2 秒 |
| 20000(asset 與 surface 各一份) | 4.64 秒 | 4.85 秒 |
| 55000 asset | | 16.95 秒 |

扣掉啟動基準 0.7 秒,每加倍約 4 倍。cProfile 顯示 `_secinv_inv_items` 佔 3.87 秒。

建議:同時維持一個 set 做成員檢查,list 只留給輸出順序。

### F3 決策引用每條控制項都重新解析整篇決策

severity: major
blocking: 是

判準:耗時是「控制項數 × 該節點決策量」,上限內的最壞情況(單篇 2MiB 決策加數萬條控制項)會跑幾十分鐘以上,等於可被輸入拖垮;我維持 major,因為跟 G7 已修的 `_secinv_claim_counts` 是同一族,修復漏掉這一處。

歸因:有證據的原有漏查(`_secinv_decision_problem` 修補前後都沒變)

引句:「ds = [d for d in _node_decisions(env, node) if str(d.get("id", "")).strip() == did]」

佐證 file: `scripts/lumos:6973`(版本 aadf6b07)。`_secinv_decision_problem` 每次呼叫都對該節點整份 frontmatter 重跑 `parse_decisions`,沒有快取;來源與例外各呼叫一次。

失敗場景:
- 輸入:一篇有 N 條決策的節點,被 M 條控制項的 `decision_ref` 引用。
- 預期:解析一次、重複使用。
- 實際:

| 決策數 | 控制項數 | 耗時 |
|---|---|---|
| 1000 | 1000 | 修前 5.64 秒、修後 5.65 秒 |
| 3000 | 3000 | 46 秒 |
| 3000 | 10000 | 151 秒(當時有其他席同時佔 CPU) |

相鄰路徑(次要):`_pq_decision_target` 在沒給 cache 時,只要 `decision_ref` 大小寫對不上,就會對每一條控制項重建一次整庫的小寫路徑索引。實測 1000 條控制項、4000 篇筆記是 +1.2 秒;更大規模會變成分鐘級,但我沒跑極端值。

建議:在 `_secinv_build` 裡建一個 per-run 的決策表與路徑索引快取,跟 `cache` 同生命週期。

## 已驗的正向主張

| 主張 | 輸入 | 預期 | 修前結果 | 修後結果 | 比較 |
|---|---|---|---|---|---|
| G7 覆蓋與入口索引(1.2 萬條控制項、4000 個入口) | 8 檔 | 同結果、更快 | 20.02 秒 | 1.48 秒 | 修復成立。`records` 的 id、`unmapped`、各入口 `mapped_control_ids` 逐項相同 |
| G7 合約宣稱快取(3000 條 invariant 來源) | 3 檔 | 同結果、更快 | 13.13 秒 | 0.95 秒 | 修復成立,同上逐項相同 |
| 總項目數上限(12 萬個 `.txt` 加 1 個 `.md`) | 單目錄 | 擋下 | 讀完、rc0、391MB | rc2、`enumeration_failed`、0.94 秒、321MB | 成立;但 `scope.files` 變 0,大型含附件圖譜整份拒讀 |
| 單檔上限先看 `fstat` | 6GiB 稀疏檔加 FIFO | 不讀內容 | | `file_too_large` 加 `special_file`,0.76 秒、306MB | 成立 |
| 總量 64MiB | 33 檔,約 65MB | 能讀完 | | 1.70 秒、428MB、無錯誤 | 成立 |
| 檔數上限 | 9900、10100 個 `.md` | 擋第 10001 個 | 9900 個 1.31 秒 | 9900 個 1.41 秒;10100 個 `too_many_files` | 成立 |
| 正常路徑 | 本 repo 圖譜(907 篇) | 輸出不變 | 0.87 秒、305MB | 0.94 秒、305MB;`records`、`errors`、`unclassified`、`unregistered` 全相同 | 沒有回歸 |
| `_json_special_re` 與逐字元舊法 | 全部 0x110000 個碼位 | 一致 | | 0 筆不一致,建表 0.12 秒;1800 萬字乾淨文字 0.2 秒 | 成立 |

這些案例都是修前沒有選例,修後補的。兩版都跑過的我都附了修前結果。

## 回答三問

1. **原問題的修復效果:** 資源面的 G7 與列舉上限,行為證據齊全(見上表)。不成立的是「資源已受控」這個整體說法,因為 F1 到 F3 都在。
2. **修補處的正常、錯誤與相鄰路徑:**
   - fd 管理:`load_vault_safe` 在三種情況下檢查,fd 數前後都是 4 對 4。
   - 情況一:深度 50/150/300 的目錄,和 800 層觸發 RecursionError,都正確回報。
   - 情況二:`RLIMIT_NOFILE=60` 製造 EMFILE。
   - 情況三:`os.read` 與 `scandir` 注入 KeyboardInterrupt、EIO、MemoryError。
   - 上限是讀之前先擋:單檔看 `fstat`,讀入量最多 `min(單檔, 剩餘)+1`。
   - 新增行為提醒(非缺陷):含超過 5 萬個非 `.md` 附件的圖譜現在整份拒讀(rc2)。
3. **新發現的同一案例在修前、修後各是什麼結果:** 見各 finding 的兩版查證。F1 到 F3 修前修後都成立,所以都歸為原有漏查,不是修復造成的回歸。

## 未驗範圍

- 文字模式 F1 只在畸形圍欄案例實測,空物件案例沒另跑。
- 31 檔的空物件案例我沒實跑(預估 40GB 會把機器拖垮),F1 的大數字是外推。
- F3 的極端規模(2MiB 決策加 10 萬條控制項)沒跑到完。
- `references_valid` 等新欄位對輸出大小的影響只量了小規模。
- 不考慮併發寫入,依派工。

## 清理

我的臨時目錄與 before/after 兩個 worktree 都已用字面絕對路徑刪除。

最嚴重 severity: major,blocking 共 3 條。
